""" functions to deal with the dispense cokelog, primarily to parse and determine usernames and membership type of paid members """
import re
from datetime import datetime
from django.conf import settings

from .payments import log

COKELOG = getattr(settings, "COKELOG_PATH", None)
if COKELOG is None:
    log.warning("COKELOG_PATH is not defined, cannot sync payment status from dispense to DB")

ALL_REGEX = r"^(?P<date>[A-Za-z]{3}\s+\d+\s[\d:]{8})\s(\w+)\sodispense2:\sdispense '([^']+)' \((?P<item>(coke|pseudo|snack|door):(\d{1,3}))\) for (?P<for>\w+) by (?P<by>\w+) \[cost\s+(\d+), balance\s+(\d+)\]$"
MEMBERSHIP_REGEX = r"^(?P<date>[A-Za-z]{3}\s+\d+\s[\d:]{8})\s(\w+)\sodispense2:\sdispense '(membership [^']+)' \((?P<item>(pseudo):(\d{1,3}))\) for (?P<for>\w+) by (?P<by>\w+) \[cost\s+(\d+), balance\s+(\d+)\]$"

class CokeLog:
    regex = ALL_REGEX

    # dictionary (keyed by username) of lists of dispense records (by-user, and date)
    dispenses = {}
    filename = COKELOG
    file = None
    last_offset = 0

    def __init__(self, **kwargs):
        if "filename" in kwargs:
            self.filename = kwargs.pop("filename")
        if "regex" in kwargs:
            self.regex = kwargs.pop("regex")
    
    def is_loaded(self):
        return self.file is not None

    def open(self):
        """ loads the cokelog, trying to avoid parsing the whole thing again """
        if not self.is_loaded():
            # open the logfile if we haven't already
            self.file = open(self.filename, 'r')
        self.parse()

    def reload(self):
        if not self.is_loaded():
            return None
        self.parse()

    def parse(self):
        """ read the cokelog, starting where we left off """
        pat = re.compile(self.regex)
        year = datetime.now().year

        # set file offset
        self.file.seek(self.last_offset)

        while True:
            line = self.file.readline()
            
            if line == '':
                # EOF
                break

            m = pat.match(line)
            if m is not None:
                data = {
                    'by': m.group("by"),
                    'date': datetime.strptime(m.group("date"), "%b %d %H:%M:%S").replace(year=year),
                    'item': m.group("item"),
                }
                user = m.group("for")

                if user in self.dispenses:
                    self.dispenses[user] += [data]
                else:
                    self.dispenses[user] = [data]
                #log.debug("got dispense item for user %s, item %s on date %s" % (user, data['item'], data['date']))
        # remember the latest file offset
        self.last_offset = self.file.tell()
    
    def get_last_dispense(self, username, item_code=None, dispense_by=None):
        if self.dispenses is None or not username in self.dispenses:
            return None

        for r in reversed(self.dispenses[username]):
            if item_code is not None and r["item"] != item_code:
                continue
            if dispense_by is not None and r["by"] != dispense_by:
                continue
            return r
        return None

# create a "static" instance of cokelog
member_cokelog = CokeLog(regex=MEMBERSHIP_REGEX)

def try_update_from_dispense(membership):
    """
    updates the membership with payment details from dispense, if found
    Note: this WILL overwrite any existing payment information
    """

    if membership.member.username == '' or membership.member.username is None:
        # can't do anything with empty usernames
        return False

    # check if anything has happened since last time
    if member_cokelog.is_loaded():
        member_cokelog.reload()
    else:
        member_cokelog.open()
    
    # look for entries like "dispense 'membership ...' (pseudo:..) for <user> by <user> ..."
    ms_disp = member_cokelog.get_last_dispense(membership.member.username)

    if ms_disp is not None:
        if ms_disp['item'] != membership.get_dispense_item():
            log.warn("user '%s': paid incorrect item '%s', not '%s' in dispense." % (
                membership.member.username, ms_disp['item'], membership.get_dispense_item()
            ))
        else:
            membership.date_paid = ms_disp['date']
            membership.payment_method = 'dispense'
            log.debug("user '%s': paid in cokelog" % membership.member.username)
            return True
    else:
        log.info("user '%s': no paid membership in cokelog" % membership.member.username)

    return False
    

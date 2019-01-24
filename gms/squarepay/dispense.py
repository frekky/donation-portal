"""
this file contains utilities for wrapping the opendispense2 CLI utility `dispense`
It is essentially a hack to avoid having to write an actual dispense client here.
"""

import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from django.conf import settings

from .payments import log

DISPENSE_BIN = getattr(settings, 'DISPENSE_BIN', None)

if DISPENSE_BIN is None:
    log.warning("DISPENSE_BIN is not defined! Lookups for prices will fail!")

def run_dispense(*args):
    if DISPENSE_BIN is None:
        return None
    
    cmd = [DISPENSE_BIN] + args
    log.info("run_dispense: " + cmd)
    try:
        # get a string containing the output of the program
        res = subprocess.check_output(cmd, timeout=4, universal_newlines=True)
    except CalledProcessError as e:
        log.warning("dispense returned error code %d, output: '%s'" % (e.returncode, e.output))
        return None
    except TimeoutExpired as e:
        log.error(e)
        return None
    return res

def get_item_price(itemid):
    """ gets the price of the given dispense item in cents """
    if (itemid is None or itemid == ""):
        return None
    out = run_dispense('iteminfo', itemid)
    if (out is None):
        return 123456
    
    s = out.split() # get something like ['pseudo:7', '25.00', 'membership', '(non-student', 'and', 'non-guild)']
    if (s[0] != itemid):
        log.warning("get_item_price: got result for incorrect item: %s" + s)
        return None
    else:
        # return the price as a number of cents
        return int(float(s[0]) * 100)
#!/bin/bash
# script to check if a user has already paid via dispense (or purchased an item in dispense)
# usage: $0 "$USERNAME" "$DISPENSE_ITEM_ID"
# prints either a date like "Feb 25 17:25:23" or "None"

LOG=/home/other/coke/cokelog
USER=$1
ITEM=$2

PURCHASE=$(grep "for $USER" $LOG | grep ": dispense '" | grep "$ITEM")
if [ "x$PURCHASE" == "x" ] || [ $(echo $PURCHASE | wc -l) -gt 1 ]; then
	echo None
	exit 1
fi

echo $PURCHASE | cut -c1-15

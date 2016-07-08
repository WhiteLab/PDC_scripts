#!/bin/sh
#
# This is a wrapper script to be called by cron to initiate a bionimbus web bridge transfer to the bionimbus web site. This is being wrapped to help create a more dynamic method to # be able to change the log file destination.

NOW=$(date +"%y%m%d")
cd /home/mbrown/core_xfer_configs && ../PDC_scripts/bionumbus_web_bridge_loader.py -j faber_core.json 2>> logs/$NOW'_faber_sync.log' >> logs/$NOW'_faber_sync.log' &

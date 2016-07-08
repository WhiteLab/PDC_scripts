#!/bin/sh
#
# This is a wrapper script to be called by cron to generate symlinks for files transfered by partner cores. This is being wrapped to help create a more dynamic method to # be able to change the log file destination.

NOW=$(date +"%y%m%d")
cd /filestore/LOGS && ../PDC_scripts/fudge_it_JS.py -d /filestore/RSYNC_SHARE/segal_data -m FLOWCELLID 2>> $NOW'_segal_link.log' >> $NOW'_segal_link.log' &

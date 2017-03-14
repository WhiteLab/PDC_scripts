#!/bin/sh
#
# This is a wrapper script to be called by cron to generate symlinks for files transfered by partner cores. This is being wrapped to help create a more dynamic method to # be able to change the log file destination.

NOW=$(date +"%y%m%d")
cd /filestore/LOGS && ../PDC_scripts/fudge_it_PF.py -d /filestore/SFTP_SHARE/pfaber/pfaber_data -l /filestore/RSYNC_SHARE/faber_core_sync 2>> $NOW'_faber_link.log' >> $NOW'_faber_link.log' &

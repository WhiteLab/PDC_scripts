#!/usr/bin/env python

import argparse
import json
import sys
import subprocess
import re
import time
import os


def date_time():
    cur = ">" + time.strftime("%c") + '\n'
    return cur


def get_source_list(user, server, directory, log):
    rsync_cmd = 'rsync --list-only -r ' + user + '@' + server + ':' + directory
    try:
        seqfiles = []
        flist = subprocess.check_output(rsync_cmd, shell=True)
        for item in flist.split('\n'):
            if re.search('\S+\.sequence\.txt\.gz$', item):
                # split on white space just to get dir/file
                info = item.split()
                seqfiles.append(info[-1])
        return seqfiles

    except:
        log.write('Getting source file list failed for' + ' '.join((user, server, directory)) + '\n')
        log.flush()
        exit(1)


def search_and_desync(sf, dest, log, user, server, directory, new_dir_list):
    cur = dest + sf
    if not os.path.isfile(cur):
        log.write(date_time() + 'Syncing file ' + sf + '\n')
        log.flush()
        # check to see if directory exists first!
        check_dir = dest + os.path.dirname(sf)
        if not os.path.isdir(check_dir):
            os.mkdir(check_dir, mode=0o755)
            new_dir_list.append(check_dir)
            log.write('Made dir ' + check_dir + '\n')
        rsync_cmd = 'rsync -rtv ' + user + '@' + server + ':' + directory + sf + ' ' + dest + sf
        check = subprocess.call(rsync_cmd, shell=True)
        if check == 0:
            log.write(date_time() + ' File transfer successful!\n')
            log.flush()
            return new_dir_list
        else:
            log.write(date_time() + 'File transfer failed using command: ' + rsync_cmd + ' FIX IT\n')
            log.flush()
            exit(1)


def synergize(config_file):
    config_data = json.loads(open(config_file, 'r').read())
    (source_user, source_server, source_dir, dest_dir, log_dir) = (config_data['source-user'], config_data['source-ip'],
    config_data['source-dir'], config_data['destination-dir'], config_data['log-dir'])
    log = open(log_dir + config_file[:-5], 'a')
    log.write(date_time() + 'Getting source file list\n')
    source_list = get_source_list(source_user, source_server, source_dir, log)
    if len(source_list) < 1:
        log.write('Sequencing files found...eject!\n')
        log.flush()
        return 0
    else:
        new_dir_list = []
        log.write('Searching destination for found sequencing files\n')
        for seqfile in source_list:
            new_dir_list = search_and_desync(seqfile, dest_dir, log, source_user, source_server, source_dir,
                                             new_dir_list)
    for dirs in new_dir_list:
        final_file_cmd = 'touch ' + dirs + '/import.me ' + dirs + '/sync.me'
        subprocess.call(final_file_cmd)
    log.write(date_time() + 'File transfer completed!\n')
    log.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Check file source for new files and sync to destination')
    parser.add_argument('-j', '--json', action='store', dest='config_file', help='.json configuration file with source'
                        ' and destination login info as well as source directory to search sub folders and'
                                                                                 ' destination directory')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    synergize(args.config_file)

if __name__ == '__main__':
    main()
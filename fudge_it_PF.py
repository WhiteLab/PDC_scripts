#!/usr/bin/env python
import argparse
import os
import sys
import re
import subprocess
import time


def date_as_int():
    return time.strftime("%y%m%d")


def get_year():
    return str(time.strftime("%Y"))


def fudge_it_pf(dirname, links):
    # helper function to create symbolic link with correctly named file
    # see if it matches this format: 2016-337_GTGAAAC_160512_D00422_0315_AHMLHHBCXX_L002_R1_001.fastq.gz
    find_cmd = 'find ' + dirname + ' -name \'*.fastq.gz\''
    flist = []
    try:
        flist = subprocess.check_output(find_cmd, shell=True)
    except:
        sys.stderr.write('There was an error executing the find command.  Ignoring\n')
    flist = flist.rstrip('\n')
    year = get_year()
    for fn in flist.split('\n'):
        test = re.search('\w+[-|_](\d+-\d+)[_|-](\d{6}[_|-]\w+[_|-]\d+[_|-]\w{10})_S\d+_L00(\d)_R(\d)_\d+\.fastq'
                         '\.gz$', fn)
        try:
            # 2016-1019_ATCACGA_L002_R2_001.fastq.gz
            (bid, run, lane, end) = (test.group(1), test.group(2), test.group(3), test.group(4))
            run = run.replace('-', '_')
            sys.stderr.write('trying regex 1 ok for ' + fn + ' checking for existing link\n')
            run_path = links + '/' + run
            if not os.path.isdir(run_path):
                os.mkdir(run_path, 0o755)
            symlink = run_path + '/' + '_'.join((bid, run, lane, end)) + '_sequence.txt.gz'
            if not os.path.isfile(symlink):
                mklink = 'ln -s ' + fn + ' ' + symlink
                subprocess.call(mklink, shell=True)
                sys.stderr.write('Creating link for ' + fn + ' ' + mklink + '\n')

        except:
            try:
                sys.stderr.write('Normal format failed.  Trying NextSeq format ' + fn + '\n')
                test = re.search('\w+[-|_](\d+-\d+)[_|-](\d{6}[_|-]\w+[_|-]\d+[_|-]\w{10})_S\d+_R(\d)_\d+\.fastq'
                                 '\.gz$', fn)
                (bid, run, end) = (test.group(1), test.group(2), test.group(3))
                run = run.replace('-', '_')
                sys.stderr.write('trying regex 2 ok for ' + fn + ' checking for existing link\n')
                run_path = links + '/' + run
                if not os.path.isdir(run_path):
                    os.mkdir(run_path, 0o755)
                symlink = run_path + '/' + '_'.join((bid, run, '1', end)) + '_sequence.txt.gz'
                if not os.path.isfile(symlink):
                    mklink = 'ln -s ' + fn + ' ' + symlink
                    subprocess.call(mklink, shell=True)
                    sys.stderr.write('Creating link for ' + fn + ' ' + mklink + '\n')
            except:
                sys.stderr.write('Regex 2 failed for ' + fn + ' Moving on\n')


def main():
    parser = argparse.ArgumentParser(
        description='Searches for sequence files that aren\'t "HGAC compatible" and creates symlinks correctly'
                    ' formatted')
    parser.add_argument('-d', '--dir', action='store', dest='dirname', help='directory to search')
    parser.add_argument('-l', '--links', action='store', dest='links', help='directory to create symlinks in')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    fudge_it_pf(args.dirname, args.links)

if __name__ == '__main__':
    main()
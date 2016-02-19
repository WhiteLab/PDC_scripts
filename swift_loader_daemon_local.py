#!/usr/bin/env python
import argparse
import json
import logging
import os
import subprocess
import sys

'''
Deamon version of swift loader.

Provide details for access to remote location in .json
also contains base file-path info
also contains desired swift project name and file location
Do this only on newly available files 
add logging

e.g.  swift stat PANCAN RAW/2015-1234/2015-1234_sequence.txt.gz

typical swift call:
  swift upload --object-name RAW/2015-1234/2015-1234_sequence.txt.gz \
      PANCAN 2015-1234_sequence.txt.gz
  
for larger files, do in 1G segments:
  swift upload --object-name RAW/2015-1235/2015-1235_sequence.txt.gz \
      PANCAN -S 1073741824 2015-1235_sequence.txt.gz
modified version of J Grunstad's to run locally.  copy not required

'''


class Loader():
    ONE_GB = 1073741824
    FIVE_GB = 5368709120

    def __init__(self, json_config, novarc):
        self.json_config = json_config
        self.novarc = novarc
        self.parse_config()

        self.source_novarc()
        # relocate our operations to the cinder volume
        os.chdir(self.config_data['local-dir'])

        logfile = self.config_data['project'] + ".log"
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='[%Y-%m-%d %H:%M:%S %p]')

        self.check_environment()
        self.get_swift_filelist()
        self.get_local_filelist()

        if len(self.remote_files) < 1:
            logging.info("No new files to transfer, exiting")
            sys.exit(0)

        logging.info("Preparing to transfer %i new files" % len(self.remote_files))
        [self.process_file(f) for f in self.remote_files]
        logging.info("Complete")

    def source_novarc(self):
        with open(self.novarc, 'r') as f:
            for line in f:
                k, v = line.rstrip().split('=')
                k = k.replace('export ', '')
                v = v.replace('"', '')
                os.environ[k] = v

    def check_environment(self):
        if not os.environ.get('OS_TENANT_NAME'):
            logging.critical("OS_TENANT_NAME not set, forgot to load " + \
                             "~/.novarc?  Trying again")
            self.source_novarc()
            #sys.exit(1)
        # if os.environ.get('http_proxy') or os.environ.get('HTTP_proxy'):
        #     logging.critical("http_proxy environmental variables need to be " + \
        #                      "unset.  Exiting")
        #     sys.exit(1)

    def process_file(self, filename):
        self.swift_load(filename)

    def parse_config(self):
        self.config_data = json.loads(open(self.json_config, 'r').read())

    def get_swift_filelist(self):
        logging.info("Gathering swift files")
        self.swift_files = list()
        logging.info(['swift', 'list',
                      self.config_data['project'], '--prefix',
                      self.config_data['subdirectory']])
        p = subprocess.Popen(['swift', 'list',
                              self.config_data['project'], '--prefix',
                              self.config_data['subdirectory']], stdout=subprocess.PIPE)
        for line in p.stdout.read().splitlines():
            self.swift_files.append(line.split('/')[-1])

    def get_local_filelist(self):
        logging.info("Gathering new remote files")
        self.remote_files = list()
        cmd = 'find %s -iname *.gz' % self.config_data['remote-dir']
        logging.info([cmd])
        try:
            p = subprocess.check_output(cmd, shell=True)
        except:
            logging("Directory for " + self.config_data['remote-dir'] + " not found! Peacing out!")
            exit(1)
        for line in p.splitlines():
            remote_filename = line
            if remote_filename not in self.swift_files:
                logging.info("transfer remote_filename: " + remote_filename)
                self.remote_files.append(remote_filename)


    def swift_load(self, filename):
        logging.info("loading to swift: " + filename)
        file_basename = os.path.basename(filename)
        bid = file_basename.split('_')[0]
        os.system('swift upload --skip-identical --object-name ' + \
                  '%s/%s/%s %s -S %s %s' % (self.config_data['subdirectory'],
                                            bid, file_basename, self.config_data['project'],
                                            self.ONE_GB, filename))


def main():
    parser = argparse.ArgumentParser(
        description='Copy files from afar, stage in cwd, and load into Swift.')
    parser.add_argument('-j', '--json', action='store', dest='config_file',
                        help='.json config file, contains file locations and access credential details')
    parser.add_argument('-n', '--nova', action='store', dest='novarc', help='.novarc file with swift openstack auth')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    subprocess.call('. ' + args.novarc, shell=True)

    loader = Loader(args.config_file, args.novarc)


if __name__ == '__main__':
    main()

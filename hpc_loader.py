#!/usr/bin/env python
import argparse
import json
import logging
import os
import subprocess
import sys

'''
HPC daemon version of swift loader.

Provide details for access to remote location in .json
also contains base file-path info
also contains desired project name and file location
Do this only on newly available files 
'''


class Loader:

    def __init__(self, json_config, chown):
        self.json_config = json_config
        self.config_data = json.loads(open(self.json_config, 'r').read())
        self.remote_user = self.config_data['remote-user']
        self.remote_server = self.config_data['remote-ip']
        self.remote_dir = self.config_data['remote-dir']
        self.project_dir = self.config_data['project-dir']
        self.sub_dir = self.config_data['subdirectory']
        self.password_file = self.config_data['password-file']
        self.chown_flag = chown
        if self.chown_flag == 'y':
            self.user = self.config_data['f_owner']
            self.group = self.config_data['f_group']
        self.local_files = list()
        self.remote_files = list()
        # relocate our operations to the cinder volume
        os.chdir(self.config_data['log-dir'])

        logfile = self.config_data['project'] + ".log"
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='[%Y-%m-%d %H:%M:%S %p]')
        self.get_local_filelist()
        self.get_remote_filelist()

        if len(self.remote_files) < 1:
            logging.info("No new files to transfer, exiting")
            sys.exit(0)

        logging.info("Preparing to transfer %i new files" % len(self.remote_files))
        [self.process_file(f) for f in self.remote_files]
        logging.info("Complete")

    def process_file(self, filename):
        self.local_load(filename)

    def get_local_filelist(self):
        logging.info("Gathering local files")
        find_cmd = 'find ' + self.project_dir + '/' + self.sub_dir + ' -name *.gz'
        logging.info(find_cmd)
        p = subprocess.check_output(find_cmd, shell=True)
        for line in p.splitlines():
            self.local_files.append(line.split('/')[-1])

    def get_remote_filelist(self):
        logging.info("Gathering new remote files")
        # module set on remote, in this case remote-dir is actually the module name
        list_cmd = 'rsync --list-only -r --password-file=' + self.password_file + ' ' + self.remote_user + '@' \
                   + self.remote_server + '::' + self.remote_dir
        logging.info(list_cmd)
        p = ''
        try:
            p = subprocess.check_output(list_cmd, shell=True)
        except:
            logging.info("Directory for " + self.remote_dir + " not found! Check configs!")
            exit(1)
        for line in p.splitlines():
            # appending only the gzipped names
            remote_filename = os.path.basename(line)
            if remote_filename[-2:] == 'gz':
                remote_filename = remote_filename.split()[-1]
                if remote_filename not in self.local_files:
                    logging.info("transfer remote file: " + line)
                    # output has extensive file info, only need last part
                    self.remote_files.append(line.split()[-1])

    def local_load(self, filename):
        logging.info("syncing to local: " + filename)
        file_basename = os.path.basename(filename)
        bnid = file_basename.split('_')[0]
        file_dir = self.project_dir + '/' + self.sub_dir + '/' + bnid
        if not os.path.isdir(file_dir):
            create_dest = 'mkdir -p ' + file_dir
            if self.chown_flag == 'y':
                create_dest += '; chown ' + self.user + ':' + self.group + ' ' + file_dir
            logging.info("Creating missing destination directory " + create_dest)
            subprocess.call(create_dest, shell=True)
        get_cmd = 'rsync -rtvP --password-file ' + self.password_file + ' ' + self.remote_user + '@' \
                  + self.remote_server + '::' + self.remote_dir + '/' + file_basename + ' ' + file_dir + '/' \
                  + file_basename
        if self.chown_flag == 'y':
            get_cmd += '; chown ' + self.user + ':' + self.group + ' ' + file_dir + '/' + file_basename
        logging.info(get_cmd)
        subprocess.call(get_cmd, shell=True)


def main():
    parser = argparse.ArgumentParser(
        description='rsync project-specific files using modules between local and remote.')
    parser.add_argument('-j', '--json', action='store', dest='config_file',
                        help='.json config file, contains file locations and access credential details')
    parser.add_argument('-c', '--chown', action='store', dest='chown',
                        help='Change user:group flag with \'y\'')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    Loader(args.config_file, args.chown)


if __name__ == '__main__':
    main()

import argparse
import json
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

'''

class Loader():

  ONE_GB = 1073741824
  FIVE_GB = 5368709120

  def __init__(self, json_config):
    self.json_config = json_config
    self.parse_config()
    self.get_swift_filelist()
    self.get_remote_filelist()
    [self.process_file(f) for f in self.remote_files]


  def process_file(self, filename):
    self.copy_file_from_remote(filename)
    self.swift_load(filename)
    os.remove(filename)


  def parse_config(self):
    self.config_data = json.loads(open(self.json_config, 'r').read())


  def get_swift_filelist(self):
    print "Gathering swift files"
    self.swift_files = list()
    p = subprocess.Popen(['swift', 'list', 
          self.config_data['project'], '--prefix', 
          self.config_data['subdirectory']], stdout=subprocess.PIPE)
    for line in p.stdout.read().splitlines():
      self.swift_files.append(line.split('/')[-1])


  def get_remote_filelist(self):
    print "Gathering new remote files"
    self.remote_files = list()
    remote_acct = "%s@%s" % (self.config_data['remote-user'],
        self.config_data['remote-ip'])
    remote_find_cmd = 'find %s -iname "*.gz"' % self.config_data['remote-dir']
    p = subprocess.Popen(['ssh', remote_acct, remote_find_cmd], 
        stdout=subprocess.PIPE)
    for line in p.stdout.read().splitlines():
      remote_filename = line.split('/')[-1]
      if remote_filename not in self.swift_files:
        print "transfer remote_filename: " + remote_filename
        self.remote_files.append(remote_filename)

  
  def copy_file_from_remote(self, filename):
    try:
      print "copying remote file: " + filename
      os.system('scp -o ForwardAgent=yes "%s@%s:%s/%s" .' % 
          (self.config_data['remote-user'],
           self.config_data['remote-ip'], 
           self.config_data['remote-dir'],
           filename))
    except Exception as e:
      print >>sys.stderr, "ERROR: copy_file_from_remote"
      raise
      sys.exit(1)


  def swift_load(self, filename):
    print "loading to swift: " + filename
    bid = filename.split('_')[0]
    os.system('swift upload --skip-identical --use-slo --object-name ' + \
        '%s/%s/%s %s -S %s %s' %(self.config_data['subdirectory'],
          bid, filename, self.config_data['project'], 
          self.ONE_GB, filename))
      

def main():
  parser = argparse.ArgumentParser(
      description='Copy files from afar, stage in cwd, and load into Swift.')
  parser.add_argument('-j', '--json', action='store', dest='config_file', 
      help='.json config file, contains file locations and access credential details')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()

  loader = Loader(args.config_file)


if __name__ == '__main__':
  main()


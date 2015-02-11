import argparse
import json
import os
import sys
'''
Provide details for access to remote location in .json
also contains base file-path info
alson contains desired swift project name and file location
  
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

  def __init__(self, json_config, filename):
    self.json_config = json_config
    self.filename = filename
    self.parse_config()
    self.process_file()

  
  def parse_config(self):
    self.config_data = json.loads(open(self.json_config, 'r').read())


  def copy_file_from_remote(self, filename):
    try:
      os.system('scp "%s@%s:%s/%s" .' % (self.config_data['remote-user'],
                                         self.config_data['remote-ip'], 
                                         self.config_data['remote-dir'],
                                         filename))
    except Exception as e:
      print >>sys.stderr, "ERROR: copy_file_from_remote"
      raise

  def swift_load(self, filename):
    bid = filename.split('_')[0]
    size = os.path.getsize(filename)
    print "%s - %s" % (filename, size)
    if(size > self.FIVE_GB):
      print "it's a big one, %s" % bid
      os.system('swift upload --object-name RAW/%s/%s %s -S %s %s' %
          (bid, filename, self.config_data['project'], self.ONE_GB, filename))
    else:
      os.system('swift upload --object-name RAW/%s/%s %s %s' %
          (bid, filename, self.config_data['project'], filename))


  def process_file(self):
    self.copy_file_from_remote(self.filename)
    self.swift_load(self.filename)
    os.remove(self.filename)
      

def main():
  parser = argparse.ArgumentParser(
      description='Copy files from afar, stage in cwd, and load into Swift.')
  parser.add_argument('-l', '--list', action='store', dest='file_list',
      help='contains only filenames')
  parser.add_argument('-j', '--json', action='store', dest='config_file', 
      help='.json config file, contains file locations and access credential details')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
  args = parser.parse_args()

  loader = Loader(args.config_file, args.file_list)


if __name__ == '__main__':
  main()


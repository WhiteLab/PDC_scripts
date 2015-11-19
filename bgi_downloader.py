#/usr/bin/env python
import argparse
import os
import subprocess
import sys

CMD = ["python", "/home/ubuntu/BGI-cli/bgionline.py"]


def parse_creds(filename):
  with open(filename, 'r') as f:
    line = f.readline()
    creds = line.rstrip().split(':')
    return creds


def login(user, password):
  output = subprocess.check_output(CMD + ["login", "-u", user, "-p", password])
  print output


def get_project_id(user, project):
  output = subprocess.check_output(CMD + ["list_user_projects", user])
  print output
  for line in output.split('\n'):
    if project in line:
      return line.split('\t')[0]

def list_project_files(project):
  files_output = subprocess.check_output(CMD + ["list_project_files", project])
  file_dict = dict()
  for line in files_output.split('\n'):
    if '-' in line:
      print line
      toks = line.split('\t')
      file_dict[toks[0]] = toks[2]
  return file_dict


def download_from_link(link, filename):
  output = subprocess.check_output(['wget', link, "-O", filename])
  print output


def process_download_links(file_dict):
  link_dict = dict()
  for file_id in file_dict:
    filename =  file_dict[file_id]
    if not os.path.isfile(filename):
      output = subprocess.check_output(CMD + ["get_download_link", file_id])
      link = output.split('\n')[1]
      download_from_link(link, filename)
    else:
      print "Skipping: %s" % filename


def set_environmentals():
  os.environ["PYTHONIOENCODING"] = "UTF-8"
  os.environ["BGIONLINE_SERVER_HOST"] = "beta.bgionline.com"

def main():
  parser = argparse.ArgumentParser(description='Download project data ' + \
      'from BGI-online')
  parser.add_argument('-p', '--project', action='store', dest='project',
      required=True, help='BGI project name')
  parser.add_argument('-c', '--creds', action='store', dest='credentials_file',
      required= True, help='Credentials file. Contents:  username:password')
  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()
  set_environmentals()
  (USER, PASSWD) = parse_creds(args.credentials_file)
  
  login(USER, PASSWD)
  project_id = get_project_id(USER, args.project)
  project_files = list_project_files(project_id)
  process_download_links(project_files)

if __name__ == '__main__':
  main()

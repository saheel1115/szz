#!/usr/bin/env python

import argparse

import os
import os.path 
from os import listdir
import sys

import logging

from DbChange import DbChange

sys.path.append("../util")
import Log
import Util
from Config import Config

import xmlReadSoup


def dump_db(xml_file, database):

  commit_list = xmlReadSoup.parse_xml(xml_file)
  for co in commit_list:
    database.dump_change(co)

  database.commit_db()

  


  

def genDiff(projPath, isSnapshot, config):

  if isSnapshot == True:
    process_project_snapshot(projPath, config, isThread=False)
  else:
    process_project(projPath, config)

def main():

  print "Tool to populate all_changes database by parsing xml log"

  parser = argparse.ArgumentParser(description='Tool to evaluate cross entropy difference')

  #project specific arguments
  parser.add_argument('-p', dest="proj_dir", help="the directories containing xml logs")

  parser.add_argument('-f', dest="xml_file", help="xml_file in case loneproj is True")

  parser.add_argument('--loneproj',dest='loneproj',action='store_true')


  #logging and config specific arguments
  parser.add_argument("-v", "--verbose", default = 'w', nargs="?", \
                          help="increase verbosity: d = debug, i = info, w = warnings," \
                          "e = error, c = critical.  " \
                          "By default, we will log everything above warnings.")
  parser.add_argument("--log", dest="log_file", \
                      help="file to store the logs, by default it will be stored at log.txt")

  parser.add_argument("--conf", dest="config_file", default='config.ini', \
          help="configuration file, default is config.ini")


  args = parser.parse_args()

  log_file = args.log_file
  proj_dir = args.proj_dir
  xml_file = args.xml_file
  is_loneproj = args.loneproj


  if is_loneproj is False:
    if not os.path.isdir(args.proj_dir):
      print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
      sys.exit()

    print "Going to process project %s" % (args.proj_dir)
  

  print log_file

  Util.cleanup(log_file)
  Log.setLogger(args.verbose, log_file)
  
  cfg = Config(args.config_file)
  db = DbChange(cfg)
  db.clean_db()

  if is_loneproj:
    dump_db(xml_file, db)
  else:
    for f in sorted(listdir(proj_dir)):
      file_path = os.path.join(proj_dir,f)
      print file_path
      dump_db(file_path, db)



if __name__ == '__main__':
    main()

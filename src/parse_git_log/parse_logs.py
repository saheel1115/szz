#!/usr/bin/env python
import sys
import re
import os
from os.path import isfile
import fnmatch
import argparse
import csv
import re
from datetime import datetime, timedelta
import sys
from parseLog import parseLog

import xmlWrite

def populateJiraDB(csv_file):

  jiraDB = {}

  with open(csv_file, 'r') as csvf:
      reader = csv.reader(csvf, delimiter=',')
      for row in reader:
        project, sha, issue = row[0], row[1], row[2]
        project = project.lower()
        jiraDB[(project, sha)] = issue
  
  return jiraDB

def log_parse_langs(project, no_merge_log, no_stat_log, out_dir, bug_only, jira_db):
    file_name  = project.split(os.sep)[-1]
    out_file = out_dir + os.sep + file_name + ".xml"
    print ">>>>>>>" , out_file
    if os.path.exists(out_file):
        return
    pl = parseLog(project, no_merge_log, no_stat_log, out_file, jira_db)
    pl.parse(bug_only)


def parse_dir(top, out_dir, bug_only, jira_db):
    
    proj_dirs = listdirs(top)
    proj_dirs = set(proj_dirs)

    for proj in proj_dirs:
        print proj
        noMerge_log = proj + os.sep + 'no_merge_log.txt'
        noStat_log  = proj + os.sep + 'no_stat_log.txt'
        if not os.path.exists(noMerge_log):
            print "!!! " + noMerge_log + " does not exist"
        if not os.path.exists(noStat_log):
            print "!!! " + noStat_log + " does not exist"

        log_parse_langs(proj, noMerge_log, noStat_log, out_dir, bug_only, jira_db)
   

def listdirs(folder):
    return [ d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
        if os.path.isdir(d)]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Tool to dump subject and body from parsing git log')
    parser.add_argument('--version', action='version', version='ParseLogs 2.0')
    parser.add_argument('-i',dest="lang_dir", help="the directories containing original git log")
    parser.add_argument('-d',dest="out_dir", help="the output directories to dump the logs")  
    parser.add_argument('-f',dest="csv_file", default='jiraclassification.csv',
        help="Jira bug classifier")   
    parser.add_argument('--all', action='store_true', default=False, 
        help="whether to dump all logs or bugfix only logs")

    args = parser.parse_args()

    lang_dir  = args.lang_dir
    out_dir   = args.out_dir
    bug_only  = not args.all
    csv_file  = args.csv_file

    print csv_file

    jira_db = populateJiraDB(csv_file)

    '''
    for k,v in jira_db.items():
      print k, v

    print "---------------------"
    '''

    if lang_dir is None or not os.path.exists(lang_dir):
        print "!! Please provide a valid log file"
        sys.exit()

    if out_dir is None:
        print "!! Please provide a valid csv file to store output"
        sys.exit()

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    parse_dir(lang_dir,out_dir,bug_only,jira_db)

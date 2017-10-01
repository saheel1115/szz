#!/usr/bin/python
import sys
import os
import os.path
import argparse
import re

#import datetime
#import pytz
#import logging


import glob,os.path
import fnmatch
from bs4 import BeautifulSoup as Soup



from commit import commit


def parse_xml(xml_file):

  print("===> processing %s" % str(xml_file))

  commit_list = []

  co = None

  handler = open(xml_file).read()
  soup = Soup(handler, 'lxml')

  for entry in soup.findAll('commit'):
      #print entry
      #print "------------------"
      sha = entry.sha.string
      project = entry.project.string

      co = commit(project, sha)
      co.committer   = entry.committer.string if not  entry.committer is None else ""
      co.commit_date = entry.commit_date.string if not  entry.commit_date is None else ""
      co.author      = entry.author.string if not  entry.author is None else ""
      co.author_date = entry.author_date.string if not  entry.author_date is None else ""
      co.isbug       = entry.bug.string if not entry.bug is None else ""
      co.subject     = entry.subject.string if not entry.subject is None else ""
      co.body        = entry.body.string if not entry.body is None else ""

      changes        = entry.findAll('change')

      for ch in changes:
          add       = ch.add.string if not ch.add is None else ""
          delete    = ch.delete.string if not ch.delete is None else ""
          file_name = ch.file.string if not ch.file is None else ""
          language  = ch.language.string if not ch.language is None else ""
          co.addChange(add, delete, file_name,language)

      commit_list.append(co)

  return commit_list


def dump_change(xml_file):
  commit_list = parse_xml(xml_file)
  for co in commit_list:
    co.dumpStr()








#=============================================================================================
#=============================================================================================


def test():

  #parse_xml(sys.argv[1])
  dump_change(sys.argv[1])







if __name__ == "__main__":

  '''
  Usage: run from root, for example: ~/bitbucket/err_corr
         python src_icse14/svn_blame/process_blame.py -p /biodata/githubrepos/ -v d --log blame.log
  '''
  test()


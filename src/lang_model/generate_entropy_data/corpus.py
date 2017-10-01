#!/usr/bin/env python

import argparse
import os
import sys
from os import listdir
import threading
import time
from sets import Set

#sys.path.append("src/util")
sys.path.append("../../util")
import Util
import langModel
import fnmatch

testTotrain = {}

def get_files(input_dir, suffix):
  print input_dir, suffix
  files_list = []
  pattern = '*.' + suffix

  for root, dirs, files in os.walk(input_dir):
    for filename in fnmatch.filter(files, pattern):
      filename = os.path.join(root,filename)
      files_list.append(filename)

  return files_list
'''
def get_files(project_dir, suffix = ""):

  files_list = []
  file_dir = os.path.join(project_dir)
  for file in os.listdir(file_dir):
    if file.endswith(suffix):
      files_list.append(os.path.join(file_dir, file))

  return files_list
'''

def get_files_wrapper(projectDir, isAppend, isReverse):
  if isReverse and isAppend:
    suffix = 'code.tokens.reverse.append'
  elif isReverse and not isAppend:
    suffix = 'code.tokens.reverse'
  elif not isReverse and isAppend:
    suffix = 'code.tokens.append'
  elif not isReverse and not isAppend:
    suffix = 'code.tokens'

  files_list = get_files(projectDir, suffix)
  return files_list



def process(projectDir, outputDir,
            isAppend, isReverse,
            cacheMinOrder, cacheBackoffWeight):

  print "---- process -----"
  print "projectDir = " , projectDir

  if isReverse:
    output_dir = outputDir + os.sep + "suffix"
  else:
    output_dir = outputDir + os.sep + "prefix"

  print "outputDir = " , output_dir

  if os.path.isdir(output_dir):
    print("%s directory exists, deleting ..." % output_dir)
    Util.cleanup(output_dir)

  Util.create_dir(output_dir)

  #global_lang_model = os.path.join(projectDir, 'project.train.10grams')

  all_train_files = get_files_wrapper(projectDir, isAppend, isReverse)
  print len(all_train_files)
  all_test_files = get_files_wrapper(projectDir, False, isReverse)

  print len(all_test_files)
  lm = langModel.LangModelAll(projectDir, output_dir, all_train_files, all_test_files)

  ret = lm.train()
  if ret == False:
    print "Nothing to learn; returning"
    return

  lm.test(cacheMinOrder, cacheBackoffWeight)


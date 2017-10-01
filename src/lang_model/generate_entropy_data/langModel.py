#!/usr/bin/env python

import argparse
import os
import sys
from os import listdir
import threading
import time
from sets import Set

#sys.path.append("src/util")
import Util
import random
import math
from sets import Set

run = os.system

CHUNK_NO = 10

class LangModel(object):
  """docstring for ClassName"""


  def __init__(self, lmSetting, inputDir, outputDir, inputFiles, testFiles):
    self.lm_setting  = lmSetting
    self.input_dir   = inputDir
    self.output_dir  = outputDir
    self.input_files = inputFiles #use for training data
    self.test_files  = testFiles
    self.isCache     = False #by default

    self.input_files_chunk = []


  '''
  cache_min_order is the minimum n-gram order upto which we will BACKOFF
  cache_backoff_weight is the weight when BACKOFF
     - 1 for decrease weight
     - 1 for increase weight
     - 0 for no weight
  '''
  def initCacheModel(self, cacheMinOrder, cacheBackoffWeight):
    self.isCache              = True
    self.cache_min_order      = cacheMinOrder
    self.cache_backoff_weight = cacheBackoffWeight

    self.cache_dir = os.path.join(self.output_dir, 'cache')
    if os.path.exists(self.cache_dir):
      Util.cleanup(self.cache_dir)

    Util.create_dir(self.cache_dir)


  def chunkList(self, fileList, chunkNo=CHUNK_NO):

    #print len(fileList)
    n = int(math.floor(len(fileList)/chunkNo)) + 1 # number of files per chunk
    #print "n = ", n
    file_to_chunk = {}
    count = 0
    for i in xrange(0, len(fileList), n):
      for f in fileList[i:i+n]:
        file_to_chunk[f] = count
      self.input_files_chunk.append(fileList[i:i+n])
      count += 1

    #for i in self.input_files_chunk:
    #  print i
    #print file_to_chunk
    #sys.exit()
    return file_to_chunk


  def getCoreFileName(self, fileName, suffix='.code'):
    core_name = os.path.basename(fileName)
    return core_name.split(suffix)[0]


  def testWithCacheModel(self, train_model, test_file):

    # print "--->"
    print train_model, test_file

    options  = '-ENTROPY -BACKOFF -TEST -CACHE -MAINTENANCE -CACHE_ORDER 10 -CACHE_DYNAMIC_LAMBDA -FILE_CACHE -FILES'
    options += ' -CACHE_MIN_ORDER %d -CACHE_BACKOFF_WEIGHT %d' % (self.cache_min_order, self.cache_backoff_weight)

    output_file = os.path.join(self.cache_dir , 'output.txt')
    log_file = os.path.join(self.cache_dir , 'log.txt')

    run('./completion %s -NGRAM_FILE %s -NGRAM_ORDER 10 -INPUT_FILE %s -OUTPUT_FILE %s > %s'
      % (options, train_model, test_file, output_file, log_file))

    run('mv %s.file.measures %s' % (test_file, self.cache_dir))

    #cmd = 'mv `find %s -name "*.sentence.entropies"` %s' % (self.input_dir, self.cache_dir)
    #print cmd
    #run(cmd)



class LangModelAll(LangModel):
  """docstring for ClassName"""
  def __init__(self, inputDir, outputDir, trainFiles, testFiles):

    super(LangModelAll, self).__init__(Util.LMSetting.All, inputDir, outputDir, trainFiles, testFiles)

    self.train_dir   = os.path.join(self.input_dir, 'trainAll')
    self.file_to_lm  = {}
    self.lm_files    = []
    self.train_files = []

  def createTrainData(self):

    if os.path.isdir(self.train_dir):
      print("%s exists!!\n Deleting..." % (self.train_dir))
      Util.cleanup(self.train_dir)

    Util.create_dir(self.train_dir)
    random.shuffle(self.input_files)
    print len(self.input_files)
    file_to_chunk = self.chunkList(self.input_files)

    ''' associte chunk to each file '''
    for file_name, chunk in file_to_chunk.items():
      tf = os.path.join(self.train_dir, str(chunk) + ".train")
      core_name = self.getCoreFileName(file_name)
      self.file_to_lm[core_name] = tf

    print len(self.input_files)
    chunk_nos = [i for i in range(len(self.input_files_chunk))]

    print len(chunk_nos)

    ''' create train files '''
    train_files_set = Set()

    for i in range(len(self.input_files_chunk)):
      tf = os.path.join(self.train_dir, str(i) + ".train")
      train_files_set.add(tf)
      this_chunk = Set()
      this_chunk.add(i)
      rest = Set(chunk_nos) - this_chunk
      # print("this_chunk = %r" % this_chunk)
      # print("rest = %r" % rest)
      for chunk in rest:
        flist = self.input_files_chunk[chunk]
        for f in flist:
          #print f
          run('cat %s >> %s' % (f, tf))

    #print self.file_to_lm
    return list(train_files_set)

  def train(self):

    retVal = True
    self.train_files = self.createTrainData()

    if len(self.train_files) == 0:
      retVal = False

    for tf in self.train_files:
      tf_model = tf + '.project.train.10grams'
      run('./bin/ngram-count -text %s -lm %s.wb.o10.lm.gz -order 10 -wbdiscount -unk' % (tf, tf))
      run('./bin/ngram -lm %s.wb.o10.lm.gz -unk -order 10 -write-lm %s' % (tf, tf_model))
      self.lm_files.append(tf_model)

      temp_file = tf + ".wb.o10.lm.gz"

      if not os.path.isfile(temp_file):
        print("%s does not exist!!" % temp_file)
        continue
      else:
        run('rm %s' % temp_file)

    return retVal

  def test(self, cacheMinOrder, cacheBackoffWeight):

    self.initCacheModel(cacheMinOrder, cacheBackoffWeight)

    self.lm_to_testFile = {}

    for tf in self.test_files:
      core_name = self.getCoreFileName(tf)
      lm = self.file_to_lm.get(core_name)
      # print "core_name = " , core_name
      # print "lm = " , lm

      if not self.lm_to_testFile.has_key(lm):
        self.lm_to_testFile[lm] = Set()
      self.lm_to_testFile[lm].add(tf)

    #print self.lm_to_testFile
    for lm, test_file_list in self.lm_to_testFile.items():
      temp_file = '%s.test' % (str(lm))
      #print "=========", temp_file
      #print test_file_list
      print >> open(temp_file, 'w'), '\n'.join(test_file_list)
      self.testWithCacheModel(lm, temp_file)

    #cmd = 'cat `find . -name "*.test.file.measures"`  >> %s/all.test.file.measures' % (self.cache_dir)
    #print cmd
    #run(cmd)

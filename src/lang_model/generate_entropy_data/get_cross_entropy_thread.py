#!/usr/bin/env python

import argparse
import os
import sys
from os import listdir

import threading
import time

import corpus
import Util

run = os.system


class myThread (threading.Thread):

  def __init__(self, threadID, name, inputDir, \
               outputDir, isAppend, isReverse, \
               cacheMinOrder, cacheBackoffWeight
	       ):

    threading.Thread.__init__(self)
    self.threadID    = threadID
    self.name        = name
    self.input_dir   = inputDir
    self.output_dir  = outputDir
    self.append      = isAppend
    self.reverse     = isReverse
    self.cache_min_order = cacheMinOrder
    self.cache_backoff_weight = cacheBackoffWeight


  def run(self):
    print "Starting " + self.name + "\n"
    corpus.process(self.input_dir, self.output_dir, \
                   self.append, self.reverse, self.cache_min_order, self.cache_backoff_weight)

    print "Exiting " + self.name + "\n"



def main():

  parser = argparse.ArgumentParser(description='Tool to evaluate cross entropy')

  #project specific arguments
  parser.add_argument('-p', dest="proj_dir", help="the directories containing corpus with annotated directories")
  parser.add_argument('-d', dest="out_dir", help="directories to dump the processed files")

  parser.add_argument('--snapshot',dest='snapshot',action='store_true')
  parser.add_argument('--no-snapshot',dest='snapshot',action='store_false')
  parser.set_defaults(snapshot=False)

  parser.add_argument('--reverse',dest='reverse',action='store_true')
  parser.add_argument('--append' ,dest='append' ,action='store_true')

  parser.set_defaults(reverse=False)
  parser.set_defaults(append=False)

  parser.add_argument('-b', dest="cache_backoff_weight", default="3",
    help="cache_backoff_weight is the weight when BACKOFF : -1 for decrease weight, 1 for increase weight, 0 for no weight")
  parser.add_argument('-c', dest="cache_min_order", default="0", help="minimum n-gram order upto which we will BACKOFF")

  args = parser.parse_args()

  if not os.path.isdir(args.proj_dir):
    print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    sys.exit()

  print "Going to process project %s" % (args.proj_dir)

  proj_dir             = args.proj_dir
  is_snapshot          = args.snapshot
  is_append            = args.append
  is_reverse           = args.reverse
  cache_min_order      = int(args.cache_min_order)
  cache_backoff_weight = int(args.cache_backoff_weight)
  lm_setting           = 1 #args.lm_setting


  proj = os.path.basename(proj_dir)
  print "---->" , proj
  if is_snapshot == True:
    threads = []
    #snapshots = listdir(proj_dir)
    #snapshots    = filter(lambda f: os.path.isdir(f), listdir(proj_dir))
    snapshots    = [ name for name in os.listdir(proj_dir) if os.path.isdir(os.path.join(proj_dir, name)) ]
    print snapshots
    tid = 0
    for s in snapshots:
      snap_dir = os.path.join(proj_dir, s)
      out_dir = args.out_dir + os.sep + proj + os.sep + s #+ os.sep + "result"
      print out_dir

      threads.append(myThread(tid, s, snap_dir, out_dir, is_append, is_reverse, cache_min_order, cache_backoff_weight))
      tid += 1


    for t in threads:
      t.start()

    for t in threads:
      t.join()

  else:
    out_dir = proj_dir + os.sep + "result"
    corpus.process(proj_dir, out_dir, is_append, is_reverse, cache_min_order, cache_backoff_weight)


if __name__ == '__main__':
  main()

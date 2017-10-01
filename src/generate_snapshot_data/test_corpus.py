#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
from git import *
import fnmatch
import glob


from projDB import DbProj
#from GitRepo import GitRepo


sys.path.append("src/util")
sys.path.append("src/changes")
from Config import Config
from OutDir import OutDir

import Log
from Util import cd
import Util
from datetime import datetime
from datetime import timedelta
import ntpath, pickle


#--------------------------------------------------------------------------------------------------------------------------
def fetchCommitCount(cfg, projectPath, language, snapshot1, snapshot2):

    db_config = cfg.ConfigSectionMap("Database")
    logging.debug("Database configuration = %r\n", db_config)

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    snapshot_temp = snapshot1.rstrip(os.sep)
    snapshot1 = snapshot_temp.split(os.sep)[-1]

    snapshot_temp = snapshot2.rstrip(os.sep)
    snapshot2 = snapshot_temp.split(os.sep)[-1]

    logging.debug("project = %r\n", project_name)

    proj = DbProj(project_name, language)
    proj.connectDb(db_config['database'], db_config['user'], db_config['host'], db_config['port'])
    commit_no = proj.countCommitBetweenDates(db_config['table'], snapshot1, snapshot2)
    return commit_no




#=============================================================================================
#=============================================================================================

def parseCorpusDir(corpus_dir, config_file, log_file, verbose):

    Util.cleanup(log_file)

    Log.setLogger(verbose, log_file)

    cfg = Config(config_file)

    filesDepth1 = glob.glob(corpus_dir + os.sep + '*')
    projDirs    = filter(lambda f: os.path.isdir(f), filesDepth1)

    projDirs = sorted(projDirs)

    for i in range(len(projDirs)-1):
      snapshot = projDirs[i]
      next_snapshot = projDirs[i+1]
      test_new = snapshot + os.sep + 'test/new/'
      test_old = snapshot + os.sep + 'test/old/'
      file_count = len(os.listdir(test_new))
      file_count_old = len(os.listdir(test_old))
      commit_count = fetchCommitCount(cfg, corpus_dir, 'java', snapshot, next_snapshot)

      print (',').join((
          snapshot, next_snapshot,
          str(file_count_old),
          str(file_count),
          str(commit_count)
          ))
      assert(file_count == commit_count)




def test():
    parser = argparse.ArgumentParser(description='Utility to test corpus dump')

    #project specific arguments
    parser.add_argument('-p',dest="corpus_dir", help="the directory containing corpus directory")

    #logging and config specific arguments
    parser.add_argument("-v", "--verbose", default = 'w', nargs="?", \
                            help="increase verbosity: d = debug, i = info, w = warnings, e = error, c = critical.  " \
                            "By default, we will log everything above warnings.")
    parser.add_argument("--log", dest="log_file", default='log.txt', \
    					help="file to store the logs, by default it will be stored at log.txt")
    parser.add_argument("--conf", dest="config_file", default='config.ini', help="configuration file, default is config.ini")


    args = parser.parse_args()

    if not os.path.isdir(args.corpus_dir):
        print "!! Please provide a valid directory, given: %s" % (args.corpus_dir)
    	sys.exit()

    print "Going to parse corpus for project %s" % (args.corpus_dir)
    parseCorpusDir(args.corpus_dir, args.config_file, args.log_file, args.verbose)

def test_ec_data():

  config = 'src/generate_snapshot_data/config.ini'
  log    = 'test.log'

  print "snapshot1, snapshot2, file_count_old, file_count_new,commit_count"

  parseCorpusDir('/biodata/ec_data/corpus/atmosphere/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/derby/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/elasticsearch/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/facebook-android-sdk/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/lucene/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/netty/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/openjpa/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/presto/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/qpid/',config, log, 'd')
  parseCorpusDir('/biodata/ec_data/corpus/wicket/',config, log, 'd')





if __name__ == "__main__":
  #python src/generate_snapshot_data/test_corpus.py -p /biodata/ec_data/corpus/facebook-android-sdk/ --conf src/generate_snapshot_data/config.ini
  #test()
  test_ec_data()



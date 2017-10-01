#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
import datetime


from Config import Config
from Corpus import Corpus

sys.path.append("src/util")
import Log
import Util



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Tool to dump commit history for given project')

    #project specific arguments
    parser.add_argument('-p',dest="proj_dir", help="the directories containing src code")
    parser.add_argument('-l',dest="lang", default='java', help="languages to be processed")
    parser.add_argument('-d',dest="out_dir", default='out_dir', help="directories to dump the processed files")


    #logging and config specific arguments
    parser.add_argument("-v", "--verbose", default = 'w', nargs="?", \
                            help="increase verbosity: d = debug, i = info, w = warnings, e = error, c = critical.  " \
                            "By default, we will log everything above warnings.")
    parser.add_argument("--log", dest="log_file", default='log.txt', \
    					help="file to store the logs, by default it will be stored at log.txt")
    parser.add_argument("--conf", dest="config_file", default='config.ini', help="configuration file, default is config.ini")



    args = parser.parse_args()

    if not os.path.isdir(args.proj_dir):
        print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    	sys.exit()

    print "Going to process project %s for %s" % (args.proj_dir, args.lang)

    print "Creating output directory at %s" % (args.out_dir)

    Util.cleanup(args.log_file)

    #od = OutDir(args.out_dir)
    #od.create_out_dir(args.out_dir)

    Log.setLogger(args.verbose, args.log_file)

    cfg = Config(args.config_file)

    corpus = Corpus(args.proj_dir, args.lang, args.out_dir, cfg)
    logging.debug(corpus)
    corpus.dump()


    #print corpus.printSnapshots()
    #1. Fetch one line changes of a given project for a given language from the database
    #edits = fetchEdits(cfg, args.proj_dir, args.lang)

    #2. build the test corpus based on each edit
    #createTrainingCorpus(args.proj_dir, args.lang, args.out_dir, edits)
    #createTestCorpus(args.proj_dir, args.lang, od, edits)









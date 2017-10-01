#!/usr/bin/env python
import sys
import re
import os
from os.path import isfile
import fnmatch
import argparse
import csv

import xmlReadSoup
import classify

from xmlWrite import xmlWrite
import util



def dump_xml(commit_list, out_file):

    xmlFile = xmlWrite(out_file)

    for co in commit_list:
        if co is None:
            continue
            
        xmlFile.setCommit(co.sha)
        xmlFile.setProject(co.project)

        xmlFile.setCommitter(co.committer, co.commit_date)
        xmlFile.setAuthor(co.author, co.author_date)
        
        xmlFile.setIsBug(co.isbug)
        xmlFile.setSubject(co.subject)
        xmlFile.setBody(co.body)

        for ch in co.changes:
            insertion, deletion, file_name, tag = ch.get() 
            xmlFile.setChanges(insertion, deletion, file_name, tag)

    xmlFile.dump()

def parse_xml(log_file):

    commit_list = xmlReadSoup.parse_xml(log_file)
    return commit_list




#--------------------------------------------------------------------------------#
# If training is None, do 1:3
#--------------------------------------------------------------------------------#

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Tool to dump subject and body from parsing git log')
    parser.add_argument('--version', action='version', version='ParseLogs 2.0')
    parser.add_argument('-tr',dest="train_dir", default = None, help="the directories contaning train xmls of git logs")
    parser.add_argument('-t',dest="test_dir", help="the directories contaning test xmls of git logs")
    parser.add_argument('-o',dest="out_dir", help="the output directories to dump the logs")
    parser.add_argument('-l',dest="lang", default='java',   help="language")

    args = parser.parse_args()

    train_dir = args.train_dir
    test_dir = args.test_dir
    out_dir = args.out_dir
    lang = args.lang

    
    if train_dir is None or not os.path.exists(train_dir):
        print "!! Please provide a valid train dir"
        sys.exit()
    

    if test_dir is None or not os.path.exists(test_dir):
        print "!! Please provide a valid test dir"
        sys.exit()

    if out_dir is None:
        print "!! Please provide a valid csv file to store output"
        sys.exit()

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for root, dirnames, filenames in os.walk(train_dir):
        for filename in fnmatch.filter(filenames, '*.xml'):

            #learning phase            
            train_file = os.path.join(root, filename)
            print "train_file = " , train_file
            train_commit_list = parse_xml(train_file)
            train_features    = classify.extractFeature(train_commit_list)

            #prediction phase  
            test_file = os.path.join(test_dir, filename)
            print "test_file = " , test_file
            test_commit_list = parse_xml(test_file)
            test_features = classify.extractFeature(test_commit_list)
            
            #dumping the output
            out_file = os.path.join(out_dir, filename)
            test = classify.runClassifier(train_features,test_features,'svm')
            dump_xml(test, out_file)
        
        
            
            



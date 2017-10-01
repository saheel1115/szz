#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
import datetime
import ntpath
import codecs

from GitRepo import GitRepo
from OutDir import OutDir

sys.path.append("src/util")
import Log
from Util import cd
import Util

# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

class SnapShot:

    def __init__(self, projPath, snapshot, outDir, debug=False):

        self.src_path = projPath + os.sep + snapshot
        self.out_path = outDir + os.sep + snapshot
        self.debug    = debug
        self.git_repo = GitRepo(self.src_path)
        self.date     = datetime.datetime.strptime(snapshot, '%Y-%m-%d').date()

        self.out_dir = None
        self.edits = []
        self.test_files = set()
        self.train_files = set()

    def __str__(self):

        retStr = str(self.date) + "\n"
        retStr += "========\n"

        for e in self.edits:
            retStr += str(e)
        return retStr

    def addEdit(self, edit):

        if self.out_dir is None:
            self.out_dir = OutDir(self.out_path)
            self.out_dir.create_out_dir(self.out_path)

        self.edits.append(edit)


    def getTestFiles(self):

        for e in self.edits:
            self.test_files.add(e.file_name)
        return self.test_files


##    def dumpTestFiles(self):
##
##        if self.out_dir is None:
##            # no edits corr to this snapshot
##            return
##
##        print('Dumping files in test dir for ' + path_leaf(self.src_path))
##        test_dirs = self.out_dir.get_test_dirs()
##
##        for e in self.edits:
##            files = self.git_repo.fetchFiles(e.file_name, e.sha)
##            for i, sha in enumerate(files):
##                self.git_repo.checkFile(e.file_name, sha)
##                src_file = self.git_repo.repo_path + os.sep + e.file_name
##
##                if not os.path.exists(src_file):
##                    print "!!! " , src_file , " does not exist"
##                    continue
##                
##                file_name = e.file_name.replace(os.sep, Util.SEP)
##
##                file_name, extn = os.path.splitext(file_name)
##
##                # Condition to filter out all files except C source files. Added on 2014-09-25 by Saheel.
##                # Changed on 2015-01-30 by Saheel to consider C++ files as well.
##                if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
##                    continue
##
##                file_name = file_name + Util.SEP + e.sha + extn
##
##                dest_file = test_dirs[i] + os.sep + file_name
##                #print src_file, dest_file
##                shutil.copyfile(src_file, dest_file)



    def dumpTestFiles(self):


        if self.out_dir is None:
            # no edits corr to this snapshot
            return

        print('Dumping files in test dir for ' + path_leaf(self.src_path))
        test_dirs = self.out_dir.get_test_dirs()

        for e in self.edits:
            files = self.git_repo.fetchFiles(e.file_name, e.sha)
            for i, sha in enumerate(files):

              #copy_content = self.git_repo.showFile(e.file_name, sha)

              file_name = e.file_name.replace(os.sep, Util.SEP)
              file_name, extn = os.path.splitext(file_name)

              if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
                continue

              file_name = file_name + Util.SEP + e.sha + extn
              dest_file = test_dirs[i] + os.sep + file_name
              #print file_name, dest_file
	      self.git_repo.dumpFile(e.file_name, sha, dest_file)
              #copy_content = self.git_repo.showFile(e.file_name, sha)
	      #with codecs.open(dest_file, "w", encoding="utf-8") as f:
	      #   f.write(copy_content)



    def getTrainFiles(self):

        return self.train_files


    def dumpTrainFiles(self):

        if self.out_dir is None:
            return

        print('Dumping files in learn and change dirs for ' + path_leaf(self.src_path))
        self.getTestFiles()
        # self.git_repo.git.stash('-u')

        #all files under snapshot except test files
        for root, dirs, files in os.walk(self.src_path):
            for f in files:
                src_file = os.path.join(root, f)
                file_name = src_file.split(self.src_path)#[1].strip(os.sep)

                if len(file_name) < 2:
                    logger.error(file_name)
                    continue

                file_name = file_name[1].strip(os.sep)

                # Condition to filter out all files except C source files. Added on 2014-09-25 1:32PM PDT by Saheel.
                # Changed on 2015-02-01 by Saheel to consider C++ files as well.
                file_name_without_extn, extn = os.path.splitext(file_name)
                if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
                    continue

                if file_name in self.test_files:
                    dest_file = self.out_dir.changed_dir + os.sep + file_name.replace(os.sep, Util.SEP)
                    shutil.copyfile(src_file, dest_file)
                    continue

                self.train_files.add(file_name)

                dest_file = self.out_dir.learn_dir + os.sep + file_name.replace(os.sep, Util.SEP)
                shutil.copyfile(src_file, dest_file)

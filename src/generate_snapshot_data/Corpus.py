#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
import datetime


from Config import Config
from DbEdits import DbEdits
from GitRepo import GitRepo
from OutDir import OutDir
from SnapShot import SnapShot

sys.path.append("src/util")
import Log
from Util import cd
import Util



class Corpus:

    def __init__(self, projectPath, language, outDir, configFile, debug=True):

        self.src_path = projectPath
        self.language = language
        self.out_path = outDir
        self.cfg      = configFile
        self.debug    = debug

        proj_path = self.src_path.rstrip(os.sep)
        self.project_name = proj_path.split(os.sep)[-1]
        logging.info("project = %s\n", self.project_name)

        self.snapshots = []
        self.changed_files_per_date = {} #commit_date -> set(file_name)
        self.edit_to_snapshot = {}
        self.snapshot2edit = {}

        #self.initEdits()
        self.edits = self.fetchEdits()
        self.initSnapshots()

    def __str__(self):
        retStr = "project : " + self.project_name + "\n"
        retStr += "SnapShots : \n"

        for s in self.snapshots:
            retStr += str(s) + " "

        return retStr

    def printSnapshots(self):

        for s in self.snapshots:
            print s

    def initEdits(self):

        self.edits = self.fetchEdits()

        # for e in self.edits:

        #     #print e.file_name, e.sha, e.commit_date
        #     file_name = e.file_name.replace(os.sep,'_')

        #     if not self.changed_files_per_date.has_key(e.commit_date):
        #         self.changed_files_per_date[e.commit_date] = set()

        #     self.changed_files_per_date[e.commit_date].add(file_name)

        # if self.debug:
        #     for key in sorted(self.changed_files_per_date):
        #         print key, self.changed_files_per_date[key]


    def fetchEdits(self):

        logging.info("Going to fetch edits for project : %s", self.project_name)

        db_config = self.cfg.ConfigSectionMap("Database")
        logging.debug("Database configuration = %r\n", db_config)

        db_edits = DbEdits(self.project_name, self.language)
        db_edits.connectDb(db_config['database'], db_config['user'], db_config['host'], db_config['port'])
        db_edits.fetchEditsFromTable(db_config['table'])

        #logging.debug(db_edits)

        return db_edits.edits

    @staticmethod
    def minKey(commitDate, snapshot):

        if commitDate >= snapshot.date:
            return (commitDate - snapshot.date).days
        else:
            return 9999

    def mapEditToSnapshot(self):

        for e in self.edits:
            cd = e.commit_date
            snap = min(self.snapshots, key=lambda sd : self.minKey(cd,sd))
            if cd < snap.date:
                print("---> skipping: commit_date %s: snapshot %s" % (cd, snap.date))
                continue

            self.edit_to_snapshot[e] = snap
            snap.addEdit(e)

        logging.debug("mapEditToSnapshot : <edit> : <snapshot>")
        for key in self.edit_to_snapshot:
            logging.debug("%s:%s" % (key, self.edit_to_snapshot[key]))

    def initSnapshots(self):

        snaps = [snap for snap in os.listdir(self.src_path)]
        # 'ss_sha_info.txt' is not a snapshot directory, hence can be removed
        # ...it actually contains some metadata about the commit SHAs of each snapshot
        # ...which is used by `src/generate_asts_and_type_data/gather_typedata_into_csv.py`
        snaps.remove('ss_sha_info.txt')
        snaps.sort()

        for snap in snaps:
            s = SnapShot(self.src_path, snap, self.out_path)
            self.snapshots.append(s)

        self.mapEditToSnapshot()


    def dump(self):

        Util.cleanup(self.out_path + "/*")
        for snap in self.snapshots:
            snap.dumpTestFiles()
            snap.dumpTrainFiles()



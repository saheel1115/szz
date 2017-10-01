#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
from git import *


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
def pathLeaf(path):
    """
    Returns the basename of the file/directory path in an _extremely_ robust way.
    
    For example, pathLeaf('/hame/saheel/git_repos/szz/abc.c/') will return 'abc.c'.
    
    Args
    ----
    path: string
        Path to some file or directory in the system

    Returns
    -------
    string
        Basename of the file or directory
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#--------------------------------------------------------------------------------------------------------------------------
def getProjName(projectPath):

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    return project_name

#--------------------------------------------------------------------------------------------------------------------------
def dumpSnapShots(srcPath, destPath, ss_interval_len, commitDateMin, commitDateMax):

    print srcPath, destPath, commitDateMin, commitDateMax

    repo = Repo(srcPath)
    branch = repo.active_branch

    print branch

    project_name = getProjName(srcPath)

    start_date = commitDateMin + timedelta(days=1)

    while start_date <= commitDateMax:
        #snapshot = destPath + os.sep + project_name + os.sep + project_name + "_" + str(start_date)
        snapshot = destPath + os.sep + project_name + os.sep + str(start_date)
        print snapshot

        if not os.path.isdir(snapshot):
            Util.copy_dir(srcPath,snapshot)
            git_command = "git checkout `git rev-list -n 1 --no-merges --before=\"" + str(start_date) + "\" " +  str(branch) + "`"
            with cd(snapshot):
                os.system("git reset --hard")
                #os.system("git checkout")
                os.system(git_command)

        start_date = start_date + timedelta(days=ss_interval_len*30)

    #snapshot = destPath + os.sep + project_name + os.sep + project_name + "_" + str(commitDateMax)
    start_date = commitDateMax
    snapshot = destPath + os.sep + project_name + os.sep + str(start_date)

    print snapshot
    if not os.path.isdir(snapshot):
        Util.copy_dir(srcPath,snapshot)
        git_command = "git checkout `git rev-list -n 1 --no-merges --before=\"" + str(start_date) + "\" " +  str(branch) + "`"
        with cd(snapshot):
            os.system("git reset --hard")
            #os.system("git checkout")
            os.system(git_command)




#--------------------------------------------------------------------------------------------------------------------------
def fetchCommitDates(cfg, projectPath, language):

    db_config = cfg.ConfigSectionMap("Database")
    logging.debug("Database configuration = %r\n", db_config)

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    logging.debug("project = %r\n", project_name)

    proj = DbProj(project_name, language)
    proj.connectDb(db_config['database'], db_config['user'], db_config['host'], db_config['port'])
    proj.fetchDatesFromTable(db_config['table'])

    logging.debug(proj)

    print proj

    print proj.projects

    assert(len(proj.projects) == 1)

    _ , _ , commit_date_min, commit_date_max = proj.projects[0]

    return (commit_date_min, commit_date_max)




#=============================================================================================
#=============================================================================================


# Utility to take snapshots of git repositories at 6 months interval
# 1. First, retrieve the 1st commit date from SQL server
# 2. Copy the projects to directories: project_date1, project_date2, .... in each 6 months interval
# 3. For each copy checkout the dump upto that date

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Utility to take snapshots of git repositories at specified (in months) interval')

    #project specific arguments
    parser.add_argument('-p',dest="proj_dir", help="the directory containing original src code")
    parser.add_argument('-d',dest="out_dir", default='out_dir', help="directories to dump the snapshots")
    parser.add_argument('-l',dest="lang", default='java', help="languages to be processed")
    parser.add_argument('-m',dest="ss_interval_len", default='6', help="duration of interval (in months) between two snapshots")

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

    print "Going to take snapshot for project %s" % (args.proj_dir)

    print "Creating output directory at %s" % (args.out_dir)


    Util.cleanup(args.log_file)

    Log.setLogger(args.verbose, args.log_file)

    cfg = Config(args.config_file)

    #1. First, retrieve the 1st commit date from SQL server
    commit_dates = fetchCommitDates(cfg, args.proj_dir, args.lang)

    #2. Snapshot
    dumpSnapShots(args.proj_dir, args.out_dir, int(args.ss_interval_len), commit_dates[0], commit_dates[1])

    project_name = pathLeaf(args.proj_dir)
    ss_dir = os.path.abspath(args.out_dir)
    ss_names = os.listdir(ss_dir + '/' + project_name)
    ss_names.sort()
    ss_paths = [ss_dir + '/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]

    ss_name_to_sha = {}
    for ss_index, ss_path in enumerate(ss_paths):
        repo = Repo(ss_path)
        ss_sha = repo.git.log('--format=%H', '-n', '1')
        ss_name_to_sha[ss_names[ss_index]] = ss_sha

    with open(ss_dir + '/' + project_name + '/ss_sha_info.txt', 'wb') as out_file:
        pickle.dump(ss_name_to_sha, out_file)


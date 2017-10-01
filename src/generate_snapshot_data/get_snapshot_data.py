"""
This module contains the function -- getSSData() -- that dumps the snapshots for a given project or the all-commits changes per snapshot, depending on the arguments it receives. Run `pydoc get_snapshot_data.printUsage` for more info.
"""

import os, sys

def printUsage():
    """
    Usage: python get_snapshot_data.py <data_root> <language> <project_name> <script_to_run> <interval>

    Sample usage: python get_snapshot_data.py data/ cpp bitcoin dump 3
    """
    pass

def getSSData(args):
    """
    Calls the `dump.py` (dumps snapshots data) or `run.py` (dumps commit changes per snapshot) scripts written by Baishakhi Ray. For usage info, run `pydoc get_snapshot_data.printUsage`. 

    Args to be provided as a list!

    Args
    ----
    data_root: string
        Path to the directory that contains the `projects`, `snapshots`, and `corpus` directories. For each project (linux, bitcoin, libgit2, xbmc, etc.), `projects` contains a dump of its latest version; `snapshots` contains N directories for N snapshots; `corpus` will hold (for each snapshot!) the changes data that is dumped by the `run.py` script
    language: string
        can be "c", "cpp", or "java"
    project: string
        Name of the project to be processed
    script_to_run: string
        "dump" or "run" -- this argument decides which script will be executed. "dump" runs the dump.py script that dumps the snapshots. "run" runs the run.py script that generates the corpus data (i.e. change, learn, test folders for each snapshot). The `snapshot_interval_in_months` argument will be ignored in case of "run".
    interval: string
        Snapshots of the project will be taken every `snapshot_interval_in_months` months
    """
    if len(args) != 6 or not os.path.isdir(args[1]) or not args[2] in ['c', 'cpp', 'java'] or not args[4] in ['dump', 'run']:
        print(printUsage.__doc__)
        sys.exit()
    
    DATA = args[1]
    PROJECTS_DIR = DATA + '/projects/'
    SNAPSHOTS_DIR = DATA + '/snapshots/'
    CORPUS_DIR = DATA + '/corpus/'
    
    LANGUAGE = args[2]
    PROJECT = args[3]
    DUMP_OR_RUN = args[4]
    INTERVAL = args[5]
    
    if DUMP_OR_RUN == 'dump':
        if not os.path.isdir(PROJECTS_DIR) or not os.path.isdir(SNAPSHOTS_DIR):
            print("\nYour data folder (" + DATA + ") does not contain directories called `projects`, `snapshots`.")
            print("These directories are required for dumping the snapshots. Aborting...")
            sys.exit()
    
        os.system('rm -rf ' + SNAPSHOTS_DIR + PROJECT + '/*')
        os.system('python src/generate_snapshot_data/dump.py -p ' + PROJECTS_DIR + PROJECT + ' -v d -d ' + SNAPSHOTS_DIR + ' --conf src/generate_snapshot_data/config.ini -l ' + LANGUAGE + ' -m ' + str(INTERVAL))
    elif DUMP_OR_RUN == 'run':
        if not os.path.isdir(PROJECTS_DIR) or not os.path.isdir(SNAPSHOTS_DIR) or not os.path.isdir(CORPUS_DIR):
            print("\nYour data folder (" + DATA + ") does not contain directories called `projects`, `snapshots`, `corpus`.")
            print("These directories are required to dump the change history for each snapshot. Aborting...")
            sys.exit()
    
        os.system('mkdir -p ' + DATA + '/logs/')
        os.system('python src/generate_snapshot_data/run.py -p ' + SNAPSHOTS_DIR + PROJECT + ' -d ' + CORPUS_DIR + PROJECT + ' -v d -l ' + LANGUAGE + ' --log ' + DATA + '/logs/' + PROJECT + '_log.txt --con src/generate_snapshot_data/config.ini')
    
if __name__ == "__main__":
    getSSData(sys.argv)

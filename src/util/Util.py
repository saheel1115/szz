import os
import sys
import os.path
import errno
import shutil

SEP = '__'

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



#Generic create directory function
def create_dir(path):

    try:
    	# print path
        os.makedirs(path)

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise

def copy_file(src, dst):
    try:
        shutil.copyfile(src, dst)
    except OSError as exc: # python >2.5
        raise

def cleanup(path):

    if os.path.isdir(path):
        # print "!!! Cleaning up " , path
        shutil.rmtree(path)

		# var = raw_input("Path %s exists; do you want to delete it?" % (path))
		# print "you entered", var
		# if var.lower().startswith('y'):
		# 	print "!!! Cleaning up " , path
		# 	shutil.rmtree(path)

    elif os.path.isfile(path):
        # print "!!! Removing " , path
        os.remove(path)

def enum(**enums):
    return type('Enum', (), enums)

LMSetting = enum(All=1, NonIssueOnly=2, NonIssuePlus=3)

import os
import sys
import os.path
import errno
import shutil

sys.path.append("src/util")
import Util

class OutDir(object):



    def __init__(self,path):
        self.root = path
        self.learn_dir = self.root + os.sep + "learn"
        self.changed_dir = self.root + os.sep + "change"
        self.test_new = self.root  + os.sep + "test" + os.sep + "new"
        self.test_old = self.root  + os.sep + "test" + os.sep + "old"

    def __str__(self):
        return self.root

    def create_out_dir(self,path):

        Util.cleanup(path)
        # self.learn_dir = path + self.learn_dir
        # self.test_new = path + self.test_new
        # self.test_old = path + self.test_old

        for p in {self.learn_dir, self.test_new, self.test_old, self.changed_dir}:
            try:
                os.makedirs(p)

            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def get_test_dirs(self):
        return (self.test_new, self.test_old)

    def get_learn_dir(self):
        return self.learn_dir

    def get_new_test_dir(self):
        return self.test_new

    def get_old_test_dir(self):
        return self.test_old

    def get_change_dir(self):
        return self.changed_dir



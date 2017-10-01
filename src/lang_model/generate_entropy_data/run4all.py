#!/usr/bin/env python

import sys
import os

sys.path.append("src/util")
from Util import cd
#import Util


def main():
  print "Run the run.py for all git corpus inside to directory"

  if len(sys.argv) < 2:
    print "Pass a top level corpus directory"
    sys.exit()

  proj_dir = sys.argv[1]
  print "corpus directory :" , proj_dir

  if not os.path.isdir(proj_dir):
    print "Not a valid directory, please pass a top level corpus directory"
    sys.exit()

  output_dir = sys.argv[2]
  print "output directory :" , output_dir

  cache_min_order = sys.argv[3]
  cache_backoff_weight = sys.argv[4]
  #lm_setting = sys.argv[5]

  curr_path = os.path.dirname(os.path.realpath(__file__))
  projects = os.listdir(proj_dir)

  for prj in projects:
    print "echo \"============= " , prj , " =============\""
    p = proj_dir + os.sep + prj

    run_command_plm = "nohup python get_cross_entropy_thread.py -p " + p \
                  + " -d " + output_dir  + " --snapshot --append " \
                  + " -b "  + cache_backoff_weight + " -c " + cache_min_order \
		  + " > " + prj + ".out 2> " + prj + ".err &"

    run_command_slm = "python get_cross_entropy_thread.py -p " + p \
                  + " -d " + output_dir  + " --snapshot --reverse --append " \
                  + " -b "  + cache_backoff_weight + " -c " + cache_min_order \
		  + " > " + prj + "_r.out 2> " + prj + "_r.err &"

    with cd(curr_path):
      print run_command_plm
      #os.system(run_command_plm)
      print run_command_slm
      #os.system(run_command_slm)

  print "run4all done!!"

if __name__ == "__main__":
  main()





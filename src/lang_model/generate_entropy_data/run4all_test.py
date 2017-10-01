#!/usr/bin/env python

import sys
import os

sys.path.append("src/util")
import Util


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

  for cache_backoff_weight in [-1,0,1]:

    for cache_min_order in [5]:

      #print cache_min_order, cache_backoff_weight

      if cache_backoff_weight == -1:

        temp_dir = "n" + str(cache_min_order)  + "d"
      elif cache_backoff_weight == 1:
        temp_dir = "n" + str(cache_min_order)  + "i"
      else:
        temp_dir = "n" + str(cache_min_order)

      output_dir1 = output_dir + temp_dir

      curr_path = os.path.dirname(os.path.realpath(__file__))
      projects = os.listdir(proj_dir)

      for prj in projects:
        print "echo \"============= " , prj , " =============\""
        p = proj_dir + os.sep + prj

        run_command_plm = "python get_cross_entropy_thread.py -p " + p \
                      + " -d " + output_dir1  + " --snapshot --append " \
                      + " -b "  + str(cache_backoff_weight) + " -c " + str(cache_min_order)

        run_command_slm = "python get_cross_entropy_thread.py -p " + p \
                      + " -d " + output_dir1  + " --snapshot --reverse --append " \
                      + " -b "  + str(cache_backoff_weight) + " -c " + str(cache_min_order)

        with Util.cd(curr_path):
          print run_command_plm
          os.system(run_command_plm)
          print run_command_slm
          os.system(run_command_slm)

  print "run4all done!!"

if __name__ == "__main__":
  main()





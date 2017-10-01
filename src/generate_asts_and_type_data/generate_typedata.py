#----------------------------------------------------------------------------------
import os, sys, ntpath, shlex
from pprint import pprint
from parse_srcML import parseSrcmlForTypedata
from extract_C_files import extractAndCopyCFiles
from subprocess import Popen, PIPE
from multiprocessing import Pool

#----------------------------------------------------------------------------------
# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def pathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#----------------------------------------------------------------------------------
def Popen_and_print(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, close_fds=True)

    stdout, stderr = process.communicate()
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)

    return process.returncode

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 5 or not os.path.isdir(sys.argv[2]) or not os.path.isfile(sys.argv[3]):
        print("Usage: python generate_type_data.py <project_name> <path_to_data_dir> <path_to_src2srcml_exe> <num_of_cores> [<old> <new> <learn>]")
        print("\nSample usage: python generate_type_data.py libgit2 data/ bin/src2srcml 4 old learn\n")
        raise IOError("Invalid arguments...")
    
    if len(sys.argv) > 5:
        for item in sys.argv[5:]:
            if item not in ['old', 'new', 'learn']:
                print("Usage: python generate_type_data.py <project_name> <path_to_data_dir> <path_to_src2srcml_exe> <num_of_cores> [<old> <new> <learn>]")
                print("\nSample usage: python generate_type_data.py libgit2 data/ bin/src2srcml 4 old learn\n")
                raise IOError("Invalid arguments...")
    
    project_name = pathLeaf(sys.argv[1])
    data_root = sys.argv[2]
    srcml_exe = sys.argv[3]
    num_of_cores = sys.argv[4]

    options = sys.argv[5:]
    process_old = 'old' in options
    process_new = 'new' in options
    process_learn = 'learn' in options

    ss_names = [ss_name for ss_name in os.listdir(data_root + '/snapshots/' + project_name + '/') if os.path.isdir(data_root + '/snapshots/' + project_name + '/' + ss_name)]
    ss_names.sort()
    
    ss_corpus_paths = [data_root + '/corpus/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]
    ss_paths = [data_root + '/snapshots/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]
    ss_c_paths = [data_root + '/snapshots_c_cpp/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]
    ss_srcml_paths = [data_root + '/snapshots_srcml/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]
    
    cmds = []
    for index, ss_corpus_path in enumerate(ss_corpus_paths):
        print("\nGenerating typedata for " + ss_corpus_path + "...")

        cmd = "python src/generate_asts_and_type_data/generate_typedata_helper.py " \
              + ss_corpus_path + " " \
              + ss_c_paths[index] + " " \
              + ss_names[index] + " " \
              + ss_paths[index] + " " \
              + ss_srcml_paths[index] + " " \
              + srcml_exe + " " \
              + str(process_old) + " " \
              + str(process_new) + " " \
              + str(process_learn) + " "
        cmds.append(shlex.split(cmd))
    
    pool = Pool(int(num_of_cores))
    return_codes = pool.map(Popen_and_print, cmds)
    
#----------------------------------------------------------------------------------

# NOTE: This script assumes that type data has been generated using generate_typedata.py script
# If that's not the case, don't worry yourself with modifying this script; writing your own will be easier.
#----------------------------------------------------------------------------------
import os, sys, pickle, ntpath, psycopg2, csv, subprocess, shlex
from pprint import pprint
from time import sleep

#----------------------------------------------------------------------------------
# Some custom functions that improve the readibility and debuggability.
# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def pathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#----------------------------------------------------------------------------------
# Given a list, we first delete its last element (unless it is the only element in the list). Then, we return a list of length 5 consisting of either the 1st five elements of the modified list or by appending empty strings (as many as necessary) to the modified list to make it of length 5
def getFirstFive(mylist):
    if len(mylist) != 1:
        mylist = mylist[:-1]        # Remove the 'root' parent
    if len(mylist) >= 5:
        return mylist[:5]
    else:
        return mylist + ['']*(5 - len(mylist))
    
#----------------------------------------------------------------------------------
# If mode == 'learn', given a string of the form "/path/to/project/corpus/learn_srcml/s1__s2__s3.c.xml.data", it returns ['s1/s2/s3.c', -1]
# If mode == 'old' or 'new', given a string of the form "/path/to/project/corpus/test/old_srcml/s1__s2__s3__SHA.c.xml.data", it returns ['s1/s2/s3.c', SHA]
# If mode == 'ss', given a string of the form "/path/to/project/snapshots_srcml/s1__s2__s3__SHA.c.xml.data", it returns ['s1/s2/s3.c', 0]
# NOTE: Since the s_i's represent the location of the file in the project directory structure, 'i' is not fixed...
#         we may have just s1 and s2. Or we may have s1 through s4.
def getFilenameAndSHA(myname, mode, ss_sha_info = None, ss_name = None):
    if mode == 'learn':
        return [pathLeaf(myname)[:-9].replace('__', '/'), -1]
    elif mode == 'ss':
        return [pathLeaf(myname)[:-9].replace('__', '/'), ss_sha_info[ss_name]]
    elif mode in ['old', 'new']:
        filename_parts = pathLeaf(myname)[:-9].split('__')     # ['s1', 's2', 's3', 'SHA.c']
        SHA_and_extension = filename_parts[-1].split('.')       # ['SHA', 'c']
        return ['/'.join(filename_parts[:-1]) + '.' + SHA_and_extension[1], SHA_and_extension[0]]

#----------------------------------------------------------------------------------
# Gather type data from all the .data files in learn and test/old folders of all the snapshots of the given project...
#   and dump them in a PostgreSQL table.
# Schema for the table:
#   [project, snapshot, file_name, sha, line_num, line_type, parent1, parent2, parent3, parent4, parent5, parents_all, hasChanged]

if __name__ == "__main__":
    if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
        print('\nUsage: python gather_and_store_data.py <path_to_data_dir> <project_name>')
        print('Sample usage: python gather_and_store_data.py data/ libgit2\n')
        raise IOError
    
    data_root = sys.argv[1]
    project_name = pathLeaf(sys.argv[2])
    corpus_path = data_root + "/corpus/" + project_name
    project_ss_path = data_root + "/snapshots/" + project_name
    if not os.path.isdir(corpus_path) or not os.path.isdir(project_ss_path):
        print("Corpus path or Snapshot path inferred from given data directory and project name is invalid. Please check the input.")
        print("The paths that I have are:")
        print("Corpus path: " + corpus_path)
        print("Snapshot path: " + project_ss_path)
        raise ValueError
    
    ss_names = [ss_name for ss_name in os.listdir(corpus_path) if os.path.isdir(corpus_path + '/' + ss_name)]
    ss_names.sort()

    ss_sha_info_filepath = project_ss_path + "/ss_sha_info.txt"
    if not os.path.isfile(ss_sha_info_filepath):
        raise ValueError("Inferred path to the `ss_sha_info.txt` file is invalid. I have:\n" + ss_sha_info_filepath)

    with open(ss_sha_info_filepath, 'rb') as ss_sha_info_file:
        ss_sha_info = pickle.load(ss_sha_info_file)

    corpus_ss_paths = [corpus_path + '/' + ss_name + '/' for ss_name in ss_names]
    ss_srcml_paths = [data_root + '/snapshots_srcml/' + project_name + '/' + ss_name + '/' for ss_name in ss_names]
    
    csv_file_ss = open(corpus_path + '/ss_typedata.csv', 'w')
    csv_file_new = open(corpus_path + '/new_typedata.csv', 'w')
    csv_file_old = open(corpus_path + '/old_typedata.csv', 'w')
    csv_file_learn = open(corpus_path + '/learn_typedata.csv', 'w')
    
    csv_writer_ss = csv.writer(csv_file_ss)
    csv_writer_new = csv.writer(csv_file_new)
    csv_writer_old = csv.writer(csv_file_old)
    csv_writer_learn = csv.writer(csv_file_learn)
    
    print("\nI hope you have run the `generate_typedata.py` script before running this script! If not, you have 5 seconds to interrupt.")
    sleep(5)
    
    for index, ss_name in enumerate(ss_names):
        corpus_ss_path = corpus_ss_paths[index]
    
        learn_srcml_path = corpus_ss_path + "learn_srcml/"
        old_srcml_path = corpus_ss_path + "test/old_srcml/"
        new_srcml_path = corpus_ss_path + "test/new_srcml/"
        ss_srcml_path = ss_srcml_paths[index]
        if not os.path.isdir(learn_srcml_path) or not os.path.isdir(old_srcml_path) or not os.path.isdir(ss_srcml_path):
            print("\nOne of the `learn_srcml`, `old_srcml`, or `snapshots_srcml` directories for the snapshot " + ss_names[index] + " is invalid.")
            print("The paths that I have are:\n" + learn_srcml_path + "\n" + old_srcml_path + "\n" + ss_srcml_path)
            print("Skipping this snapshot for now.\n")
            continue
    
        # ss_data will contain the type data for each line in each file for this particular snapshot
        # new_data will contain the type data for each line in each file for this particular snapshot's `test/new` folders
        # old_data will contain the type data for each line in each file for this particular snapshot's `test/old` folders
        # learn_data will contain the type data for each line in each file for this particular snapshot's `learn` folders
        ss_data = []
        old_data = []
        new_data = []
        learn_data = []
        print('\nNow gathering srcML data for `' + ss_name + '` snapshot for `' + project_name + '` project...')
    
        learn_data_filepaths = [os.path.join(learn_srcml_path, filename) for filename in next(os.walk(learn_srcml_path))[2] if filename.endswith('.data')]
        old_data_filepaths = [os.path.join(old_srcml_path, filename) for filename in next(os.walk(old_srcml_path))[2] if filename.endswith('.data')]
        new_data_filepaths = [os.path.join(new_srcml_path, filename) for filename in next(os.walk(new_srcml_path))[2] if filename.endswith('.data')]
        ss_data_filepaths = [os.path.join(ss_srcml_path, filename) for filename in next(os.walk(ss_srcml_path))[2] if filename.endswith('.data')]
        
        for learn_data_filepath in learn_data_filepaths:
            line_type_dict = {}
            line_parents_type_dict = {}
            with open(learn_data_filepath, 'r') as data_file:
                line_type_dict = pickle.load(data_file)
                line_parents_type_dict = pickle.load(data_file)
            
            for line_num in line_type_dict.keys():
                learn_data.append([project_name, ss_name] +
                                  getFilenameAndSHA(learn_data_filepath, 'learn') +
                                  [line_num, line_type_dict[line_num]] +
                                  getFirstFive(line_parents_type_dict[line_num]) +
                                  ['-'.join(line_parents_type_dict[line_num][:-1])] +
                                  [-1])
    
        # Write back the `learn` data for this ss
        csv_writer_learn.writerows(learn_data)
    
        for old_data_filepath in old_data_filepaths:
            line_type_dict = {}
            line_parents_type_dict = {}
            with open(old_data_filepath, 'r') as data_file:
                line_type_dict = pickle.load(data_file)
                line_parents_type_dict = pickle.load(data_file)
            
            for line_num in line_type_dict.keys():
                old_data.append([project_name, ss_name] +
                                getFilenameAndSHA(old_data_filepath, 'old') +
                                [line_num, line_type_dict[line_num]] +
                                getFirstFive(line_parents_type_dict[line_num]) +
                                ['-'.join(line_parents_type_dict[line_num][:-1])] +
                                [0])
    
        # Write back the `old` data for this ss
        csv_writer_old.writerows(old_data)
    
        for new_data_filepath in new_data_filepaths:
            line_type_dict = {}
            line_parents_type_dict = {}
            with open(new_data_filepath, 'r') as data_file:
                line_type_dict = pickle.load(data_file)
                line_parents_type_dict = pickle.load(data_file)
            
            for line_num in line_type_dict.keys():
                new_data.append([project_name, ss_name] +
                                getFilenameAndSHA(new_data_filepath, 'new') +
                                [line_num, line_type_dict[line_num]] +
                                getFirstFive(line_parents_type_dict[line_num]) +
                                ['-'.join(line_parents_type_dict[line_num][:-1])] +
                                [1])
    
        # Write back the `new` data for this ss
        csv_writer_new.writerows(new_data)
    
        for ss_data_filepath in ss_data_filepaths:
            line_type_dict = {}
            line_parents_type_dict = {}
            with open(ss_data_filepath, 'r') as data_file:
                line_type_dict = pickle.load(data_file)
                line_parents_type_dict = pickle.load(data_file)
            
            for line_num in line_type_dict.keys():
                ss_data.append([project_name, ss_name] + 
                               getFilenameAndSHA(ss_data_filepath, 'ss', ss_sha_info, ss_name) +
                               [line_num, line_type_dict[line_num]] +
                               getFirstFive(line_parents_type_dict[line_num]) +
                               ['-'.join(line_parents_type_dict[line_num][:-1])] + 
                               [-2])
    
        # Write back the `learn`, `test/old`, and `ss` data for this ss; no need to wait for the processing of `new` data
        csv_writer_ss.writerows(ss_data)
        print('Done gathering typedata for snapshot ' + ss_name)
    
    csv_file_ss.close()
    csv_file_new.close()
    csv_file_old.close()
    csv_file_learn.close()

#----------------------------------------------------------------------------------

#----------------------------------------------------------------------------------
import os, sys, ntpath, shlex
from pprint import pprint
from parse_srcML import parseSrcmlForTypedata
from extract_C_files import extractAndCopyCFiles

#----------------------------------------------------------------------------------
# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def pathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#----------------------------------------------------------------------------------
def generate_type_data_for_snapshot(ss_corpus_path, ss_c_path, ss_name, ss_path, ss_srcml_path, srcml_exe, process_old, process_new, process_learn):
    learn_corpus_path = ss_corpus_path + 'learn/'
    old_corpus_path = ss_corpus_path + 'test/old/'
    new_corpus_path = ss_corpus_path + 'test/new/'
    
    if not os.path.isdir(ss_path):
        raise ValueError('Given `ss` path is invalid. Skipping this ss completely. I was given: ' + ss_path)

    learn_valid = True
    if not os.path.isdir(learn_corpus_path):
        learn_valid = False
        print('Given `learn` path is invalid. Skipping this dir. I was given: ' + learn_corpus_path)
    else:
        learn_filepaths = [os.path.join(learn_corpus_path, filename) for filename in next(os.walk(learn_corpus_path))[2] if filename.endswith(('.c', '.cpp', '.cc'))]

    old_valid = True
    if not os.path.isdir(old_corpus_path):
        old_valid = False
        print('Given `old` path is invalid. Skipping this dir. I was given: ' + old_corpus_path)
    else:
        old_filepaths = [os.path.join(old_corpus_path, filename) for filename in next(os.walk(old_corpus_path))[2] if filename.endswith(('.c', '.cpp', '.cc'))]

    new_valid = True
    if not os.path.isdir(new_corpus_path):
        new_valid = False
        print('Given `new` path is invalid. Skipping this dir. I was given: ' + new_corpus_path)
    else:
        new_filepaths = [os.path.join(new_corpus_path, filename) for filename in next(os.walk(new_corpus_path))[2] if filename.endswith(('.c', '.cpp', '.cc'))]

    # Extract the .c and .cpp files in the snapshots
    # -- and copy them to `ss_c_path` as defined above
    extractAndCopyCFiles(ss_path, ss_c_path)

    learn_srcml_path = ss_corpus_path + 'learn_srcml/'
    old_srcml_path = ss_corpus_path + 'test/old_srcml/'
    new_srcml_path = ss_corpus_path + 'test/new_srcml/'
    ss_srcml_path = ss_srcml_path
    os.system("mkdir -p " + learn_srcml_path + " " + old_srcml_path + " " + new_srcml_path + " " + ss_srcml_path)
    os.system("rm -rf " + learn_srcml_path + "/* " + old_srcml_path + "/* " + new_srcml_path + "/* " + ss_srcml_path + "/*")

    ss_filepaths = [os.path.join(ss_c_path, filename) for filename in next(os.walk(ss_c_path))[2]]

    # Processing `test/old` directory
    if old_valid and process_old == 'True':
        for old_filepath in old_filepaths:
            old_filename = pathLeaf(old_filepath)
            srcml_filepath = old_srcml_path + old_filename + '.xml'
    
            os.system(srcml_exe + " " + old_filepath + " > " + srcml_filepath)
            parseSrcmlForTypedata(srcml_filepath)

    # Processing `test/new` directory
    if new_valid and process_new == 'True':
        for new_filepath in new_filepaths:
            new_filename = pathLeaf(new_filepath)
            srcml_filepath = new_srcml_path + new_filename + '.xml'

            os.system(srcml_exe + " " + new_filepath + " > " + srcml_filepath)
            parseSrcmlForTypedata(srcml_filepath)

    # Processing `learn` directory
    if learn_valid and process_learn == 'True':
        for learn_filepath in learn_filepaths:
            learn_filename = pathLeaf(learn_filepath)
            srcml_filepath = learn_srcml_path + learn_filename + '.xml'
    
            os.system(srcml_exe + " " + learn_filepath + " > " + srcml_filepath)
            parseSrcmlForTypedata(srcml_filepath)
    
    # Processing the snapshots per se
    for ss_filepath in ss_filepaths:
        ss_filename = pathLeaf(ss_filepath)
        srcml_filepath = ss_srcml_path + ss_filename + '.xml'

        os.system(srcml_exe + " " + ss_filepath + " > " + srcml_filepath)
        parseSrcmlForTypedata(srcml_filepath)

#----------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 10:      
        raise ValueError("Invalid number of args provided to `generate_typedata_helper`. 9 args needed.")

    ss_corpus_path = sys.argv[1]
    ss_c_path = sys.argv[2]
    ss_name = sys.argv[3]
    ss_path = sys.argv[4]
    ss_srcml_path = sys.argv[5]
    srcml_exe = sys.argv[6]
    process_old = sys.argv[7]
    process_new = sys.argv[8]
    process_learn = sys.argv[9]

    try:
        generate_type_data_for_snapshot(ss_corpus_path, ss_c_path, ss_name, ss_path, ss_srcml_path, srcml_exe, process_old, process_new, process_learn)
        print("Done generating typedata for snapshot " + ss_name + ".")
    except Exception as e:
        sys.stderr.write(str(e))

#----------------------------------------------------------------------------------

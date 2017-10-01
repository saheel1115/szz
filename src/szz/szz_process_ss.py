#--------------------------------------------------------------------------------------------------------------------------
import os, sys, ntpath, subprocess, shlex, re, pickle
from pprint import pprint
from subprocess import Popen, PIPE

try:
    from git import Repo
except ImportError as e:
    raise e
    
#--------------------------------------------------------------------------------------------------------------------------
def dismemberFilename(myname, mode):
    """ 
    Breaks down a complicated filename and returns a 2-element list consisting of the filename-component and the SHA-component
    
    If mode == 'learn', given a string of the form "s1__s2__s3.c", it returns ['s1/s2/s3.c', -1]
    If mode == 'old', given a string of the form "s1__s2__s3__SHA.c", it returns ['s1/s2/s3.c', SHA]

    NOTE: Since the s_i's represent the location of the file in the project directory structure, 'i' is not fixed. Thus, we may have just s1 and s2. Or we may have s1 through s4.
    
    Args
    ----
    myname: string
        Full name of a file in the `learn` or `test/old` directories of some project corpus
    mode: string
        A string indicating whether `myname` comes from `learn` or `test/old` directories.
    """
    if mode == 'learn':
        return [pathLeaf(myname).replace('__', '/'), -1]
    elif mode == 'old':
        filename_parts = myname.split('__')     # ['s1', 's2', 's3', 'SHA.c']
        SHA_and_extension = filename_parts[-1].split('.')       # ['SHA', 'c']
        return ['/'.join(filename_parts[:-1]) + '.' + SHA_and_extension[1], SHA_and_extension[0]]

#--------------------------------------------------------------------------------------------------------------------------
def pathLeaf(path):
    """Returns the basename of the file/directory path in an _extremely_ robust way. For example, pathLeaf('/hame/saheel/git_repos/szz/abc.c/') will return 'abc.c'."""
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#--------------------------------------------------------------------------------------------------------------------------
def szz_reverse_blame(ss_path, sha_to_blame_on, buggy_line_num, buggy_file_path_in_ss, buggy_SHA):
    """Reverse-blames `buggy_line_num` (added in `buggy_SHA`)  onto `sha_to_blame_on`."""
    ss_repo = Repo(ss_path)
    ss_name = pathLeaf(ss_path)
    try:
        # If buggy_SHA equals sha_to_blame_on, then git-blame-reverse fails.
        # In our code buggy_SHA and sha_to_blame_on are never equal, but just to be safe...
        if sha_to_blame_on != buggy_SHA:
            curr_blame_info = ss_repo.git.blame('--reverse', '-w', '-n', '-f', '--abbrev=40', \
                                                '-L' + buggy_line_num + ',+1', \
                                                '--', buggy_file_path_in_ss, \
                                                buggy_SHA + '..' + sha_to_blame_on,
                                                stdout_as_string = False)
            curr_buggy_line_num = curr_blame_info.split('(')[0].split()[-1]
            curr_buggy_file_path_in_ss = ' '.join(curr_blame_info.split('(')[0].split()[1:-1])
            return [ss_name, curr_buggy_file_path_in_ss, sha_to_blame_on, curr_buggy_line_num]

        else:
            return [ss_name, buggy_file_path_in_ss, sha_to_blame_on, buggy_line_num]

    except Exception as e:
        sys.stderr.write("\nError in reverse-blame! Continuing with next line_num...\n" + str(e))
        return None

#--------------------------------------------------------------------------------------------------------------------------
def szz_process_file(old_file_SHA, old_file_path_in_ss, old_files_path, old_file_fullname, new_files_path,
                     ss_path, ss_SHA):
    """Returns buggy tuples corresponding to the lines deleted in `old_file_path_in_ss`"""

    ss_repo = Repo(ss_path)
    all_buggy_tuples_in_ss_files = []
    bugfix_SHA = old_file_SHA
    this_ss_name = pathLeaf(ss_path)

    # Get the line numbers of lines deleted from old_file; these are our buggy lines!
    diff_command = 'diff -N -w -E -B --unchanged-line-format="" ' \
                   + '--old-line-format="%dn " --new-line-format="" ' \
                   + old_files_path + old_file_fullname + ' ' \
                   + new_files_path + old_file_fullname
    process = Popen(shlex.split(diff_command), stdout=PIPE, close_fds=True)
    line_nums = process.communicate()[0].split()

    project_snapshots_dir = os.path.dirname(os.path.dirname(ss_path))
    ss_sha_info_filename = os.path.join(project_snapshots_dir, 'ss_sha_info.txt')
    ss_sha_info_dict = pickle.load(open(ss_sha_info_filename, 'rb'))
    all_ss_names = sorted(ss_sha_info_dict.keys())
    this_and_prev_ss_names = all_ss_names[:all_ss_names.index(this_ss_name)] + [this_ss_name]

    # Blame each buggy line to get the bug-introducing `buggy_sha`
    # Then, reverse-blame each buggy line to find buggy lines present in various snapshots
    for line_num in line_nums:
        try:
            blame_info = ss_repo.git.blame('-w', '-M', '-C', '-C', '-n', '-f', '--abbrev=40', \
                                           '-L' + line_num + ',+1', \
                                           bugfix_SHA + '^', \
                                           '--', old_file_path_in_ss, \
                                           stdout_as_string = False)
        except Exception, e:
            print("\nError! Continuing with next line_num...\n" + str(e))
            continue

        buggy_line_num = blame_info.split('(')[0].split()[-1]
        buggy_SHA = blame_info.split()[0][-40:]
        buggy_file_path_in_ss = ' '.join(blame_info.split('(')[0].split()[1:-1])

        buggy_SHA_date = str(ss_repo.git.log('-n', '1', '--format="%ad"', '--date=short', buggy_SHA))
        buggy_SHA_date = buggy_SHA_date.replace('"', '')

        project_snapshots_dir = os.path.dirname(os.path.dirname(ss_path))
        for ss_name in this_and_prev_ss_names:
            if buggy_SHA_date < ss_name:
                ss_sha = ss_sha_info_dict[ss_name]
                ss_path = project_snapshots_dir + '/' + ss_name + '/'

                # `buggy_tuple_ss` is the info of the buggy line mapped to this snapshot
                buggy_tuple_ss = szz_reverse_blame(ss_path, ss_sha, buggy_line_num, buggy_file_path_in_ss, buggy_SHA)
                if buggy_tuple_ss:
                    # Add info on where the buggy line originated
                    buggy_tuple_ss += [buggy_SHA, buggy_file_path_in_ss, buggy_line_num]
                    all_buggy_tuples_in_ss_files.append({(old_file_path_in_ss, old_file_SHA, line_num): buggy_tuple_ss})

    return all_buggy_tuples_in_ss_files

#--------------------------------------------------------------------------------------------------------------------------
def szz_process_ss(ss_name, ss_path, ss_changes_path, bugfix_SHAs_filename):
    bugfix_SHAs = [SHA for SHA in open(bugfix_SHAs_filename).read().splitlines()]
    all_buggy_lines_fixed_in_ss = []

    # Git repo for current ss
    try:
        ss_repo = Repo(ss_path)
    except Exception as e:
        sys.stderr.write("\nApparently, " + ss_path + " is not a valid git repo. Skipping this snapshot...")
        sys.stderr.write(str(e))
        return

    ss_SHA = ss_repo.git.log('--format=%H', '-n', '1')

    # Get metadata on the files in ss/test/old and ss/test/new in order to process the buggy lines
    old_file_paths_in_ss = []
    old_file_SHAs = []
    
    # Path to ss/test/old and ss/test/new; used to diff old and new files
    old_files_path = ss_changes_path + 'test/old/'
    new_files_path = ss_changes_path + 'test/new/'
    if not os.path.isdir(old_files_path) or not os.path.isdir(new_files_path):
        sys.stderr.write("`test/old/` or `test/new/` path invalid for the snapshot `" + ss_name + "`. Skipping this snapshot...")
        return

    old_file_fullnames = [filename for filename in os.listdir(old_files_path) if filename.endswith(('c', 'cpp', 'cc', 'java'))]
    old_file_fullnames.sort()
    for old_file_fullname in old_file_fullnames:
        # Example of old_file_fullname = src__oid__b7c891c629d298f2d82310d8ced2ee2e48084213.c
        name_SHA_pair = dismemberFilename(old_file_fullname, 'old')
        old_file_paths_in_ss.append(name_SHA_pair[0])
        old_file_SHAs.append(name_SHA_pair[1])

    # Start processing the ss/test/old files
    for old_file_index, old_file_path_in_ss in enumerate(old_file_paths_in_ss):
        old_file_SHA = old_file_SHAs[old_file_index]
        if old_file_SHA in bugfix_SHAs:
            temp = szz_process_file(old_file_SHA, old_file_path_in_ss,
                                    old_files_path, old_file_fullnames[old_file_index],
                                    new_files_path, ss_path, ss_SHA)
            all_buggy_lines_fixed_in_ss += temp

    with open(ss_changes_path + '/ss_mappedOntoSSOnly.bugdata', 'wb') as ss_bugdata_outfile:
        pickle.dump(all_buggy_lines_fixed_in_ss, ss_bugdata_outfile)

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("Invalid input args to szz_process_ss.py. Aborting this snapshot.")
    
    print('\nProcessing snapshot ' + sys.argv[1])
    szz_process_ss(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print("Processing done for snapshot " + sys.argv[1])

#--------------------------------------------------------------------------------------------------------------------------

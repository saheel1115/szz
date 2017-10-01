#--------------------------------------------------------------------------------------------------------------------------
import os, sys, ntpath, subprocess, shlex, re, pickle, csv
from subprocess import Popen, PIPE
from collections import defaultdict
from pprint import pprint

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
def szz_reverse_blame(ss_path, sha_to_map_onto, buggy_linums, buggy_file_path, buggy_SHA):
    """Reverse-blames `buggy_linums` (added in `buggy_file_path` in `buggy_SHA`)  onto `sha_to_map_onto`."""
    ss_repo = Repo(ss_path)
    # If `buggy_SHA` equals `sha_to_map_onto`, then git-blame-reverse fails.
    if sha_to_map_onto != buggy_SHA:
        blame_options = []
        for linum in buggy_linums:
            blame_options.append('-L' + linum + ',+1')
        blame_options += [buggy_SHA + '..' + sha_to_map_onto, '--', buggy_file_path]
        
        try:
            blame_infos = ss_repo.git.blame('--reverse', '-w', '-n', '-f', '--abbrev=40', \
                                            stdout_as_string = False, *blame_options)
        except Exception as e:
            print('Error while reverse-blaming! Skipping this (buggy_SHA, buggy_file_path) pair...') 
            print(str(e))
            return None

        buggy_tuples = []
        blame_infos = blame_infos.splitlines()
        if len(blame_infos) != len(buggy_linums):
            print('Minor error... something weird happened while reverse-blaming. Please check!')
            return None

        for index, blame_info in enumerate(blame_infos):
            mapped_buggy_line_num = blame_info.split('(')[0].split()[-1]
            mapped_buggy_file_path = ' '.join(blame_info.split('(')[0].split()[1:-1])
            buggy_tuples.append([sha_to_map_onto, mapped_buggy_file_path, mapped_buggy_line_num, \
                                 buggy_SHA, buggy_file_path, buggy_linums[index]])
            
        return buggy_tuples

    else:
        return [[sha_to_map_onto, buggy_file_path, linum, buggy_SHA, buggy_file_path, linum] for linum in buggy_linums]

#--------------------------------------------------------------------------------------------------------------------------
def szz_process_file(old_file_SHA, old_file_path_in_ss, old_files_path, old_file_fullname, new_files_path,
                     ss_path, ss_SHA, mapped_commits):
    """Returns buggy tuples corresponding to the lines deleted in `old_file_path_in_ss`"""

    ss_repo = Repo(ss_path)
    mapped_buggy_tuples = []
    bugfix_SHA = old_file_SHA
    this_ss_name = pathLeaf(ss_path)

    # Get the line numbers of lines deleted from old_file; these are our buggy lines!
    diff_command = 'diff -N -w -E -B --unchanged-line-format="" ' \
                   + '--old-line-format="%dn " --new-line-format="" ' \
                   + old_files_path + old_file_fullname + ' ' \
                   + new_files_path + old_file_fullname
    process = Popen(shlex.split(diff_command), stdout=PIPE, close_fds=True)
    line_nums = process.communicate()[0].split()

    # Blame the deleted lines so as to know which commit(s) added them
    blame_options = []
    for line_num in line_nums:
        blame_options.append('-L' + line_num + ',+1')
    blame_options += [bugfix_SHA + '^', '--', old_file_path_in_ss]

    # Blame the buggy lines to get the bug-introducing `buggy_sha`
    # Then, reverse-blame them to find buggy lines...
    # ...present in various commits between the buggy and bugfixing commit
    try:
        blame_infos = ss_repo.git.blame('-w', '-n', '-f', '--abbrev=40', \
                                        stdout_as_string = False, \
                                        *blame_options)
    except Exception, e:
        print("\nError! Continuing with next line_num...\n" + str(e))
        return None

    # This dictionary maps (buggy_SHA, buggy_file_path_in_ss) to the list of line numbers...
    # ...of the buggy lines added in `buggy_file_path_in_ss` in `buggy_SHA`
    linums_in_sha_file_pair = defaultdict(list)
    buggy_SHAs = set()
    for blame_info in blame_infos.splitlines():
        buggy_SHA = blame_info.split()[0][-40:]
        buggy_file_path_in_ss = ' '.join(blame_info.split('(')[0].split()[1:-1])
        buggy_line_num = blame_info.split('(')[0].split()[-1]
        linums_in_sha_file_pair[(buggy_SHA, buggy_file_path_in_ss)].append(buggy_line_num)
        buggy_SHAs.add(buggy_SHA)

    shas_to_map_onto = defaultdict(list)
    for buggy_SHA in buggy_SHAs:
        # Get SHAs of all commits _between_ `buggy_SHA` and `bugfix_SHA`
        all_inbetween_commits = ss_repo.git.log('--reverse', '--ancestry-path', '--format=%H', '--abbrev=40', \
                                                buggy_SHA + '..' + bugfix_SHA) 
        all_inbetween_commits = set(all_inbetween_commits.split()[:-1]) # <-- slicing removes `bugfix_SHA` from the list 
        relevant_commits = set.intersection(all_inbetween_commits, mapped_commits)
        shas_to_map_onto[buggy_SHA] += list(relevant_commits)

    for bsha, fpath in linums_in_sha_file_pair.keys():
        for sha_to_map_onto in shas_to_map_onto[bsha]:
            linums = linums_in_sha_file_pair[(bsha, fpath)]
            buggy_tuples = szz_reverse_blame(ss_path, sha_to_map_onto, linums, \
                                             fpath, bsha)
            if buggy_tuples is not None:
                mapped_buggy_tuples += [buggy_tuple + ['1', this_ss_name, old_file_SHA, old_file_path_in_ss, linums[index]] \
                                        for index, buggy_tuple in enumerate(buggy_tuples)]

    return mapped_buggy_tuples

#--------------------------------------------------------------------------------------------------------------------------
def szz_process_ss(ss_name, ss_path, ss_corpus_path, bugfix_SHAs_filename):
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
    old_files_path = ss_corpus_path + 'test/old/'
    new_files_path = ss_corpus_path + 'test/new/'
    if not os.path.isdir(old_files_path) or not os.path.isdir(new_files_path):
        sys.stderr.write("`test/old/` or `test/new/` path invalid for the snapshot `" + ss_name + "`. Skipping this snapshot...")
        return

    old_file_fullnames = [filename for filename in os.listdir(old_files_path) if filename.endswith(('c', 'cpp', 'cc', 'java'))]
    old_file_fullnames.sort()
    for old_file_fullname in old_file_fullnames:
        name_SHA_pair = dismemberFilename(old_file_fullname, 'old')
        old_file_paths_in_ss.append(name_SHA_pair[0])
        old_file_SHAs.append(name_SHA_pair[1])

    # Read in the commits onto which we will map each buggy line
    # Note: `mapped_commits.txt` is created by szz.py before calling szz_process_ss.py
    if not ss_corpus_path.endswith('/'):
        ss_corpus_path += '/'
    project_corpus_path = os.path.dirname(os.path.dirname(ss_corpus_path)) + '/'
    with open(project_corpus_path + 'mapped_commits.txt', 'rb') as infile:
        mapped_commits = [commit.strip() for commit in infile.readlines() if commit.strip()]

    # Start processing the ss/test/old files
    for old_file_index, old_file_path_in_ss in enumerate(old_file_paths_in_ss):
        old_file_SHA = old_file_SHAs[old_file_index]
        if old_file_SHA in bugfix_SHAs:
            print(old_file_path_in_ss)
            temp = szz_process_file(old_file_SHA, old_file_path_in_ss,
                                    old_files_path, old_file_fullnames[old_file_index],
                                    new_files_path, ss_path, ss_SHA, mapped_commits)
            if temp is not None:
                all_buggy_lines_fixed_in_ss += temp

    with open(ss_corpus_path + '/ss_mappedOntoSSOnly.bugdata', 'wb') as ss_bugdata_outfile:
        csv_writer = csv.writer(ss_bugdata_outfile)
        csv_writer.writerow(['sha', 'file_name', 'line_num', 'bi_sha', 'bi_file_name', 'bi_line_num', 'is_bug', 'bf_ss', 'bf_sha', 'bf_file_name', 'bf_line_num'])
        csv_writer.writerows(all_buggy_lines_fixed_in_ss)

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("Invalid input args to szz_process_ss.py. Aborting this snapshot.")
    
    print('\nProcessing snapshot ' + sys.argv[1])
    szz_process_ss(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print("Processing done for snapshot " + sys.argv[1])

#--------------------------------------------------------------------------------------------------------------------------

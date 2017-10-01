#--------------------------------------------------------------------------------------------------------------------------
import os, sys, shlex, subprocess, csv, ntpath
from collections import defaultdict

try:
    from git import Repo
except ImportError as e:
    print('Required library `gitpython` not found in system. Please install using `sudo pip install gitpython`.')
    raise

#--------------------------------------------------------------------------------------------------------------------------
def pathLeaf(path):
    """Returns the basename of the file/directory path in an _extremely_ robust way. For example, pathLeaf('/hame/saheel/git_repos/szz/abc.c/') will return 'abc.c'."""
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 5 or not os.path.isdir(sys.argv[1]) or not os.path.isfile(sys.argv[3]) or not os.path.isfile(sys.argv[4]):
        print("\nUsage: python get_deleted_line_numbers.py <data_dir> <project_name> <path_to_showlinenum_script> <bf_shas_file>")
        print("\nSample usage: python get_deleted_line_numbers.py data/ libuv bin/showlinenum.awk data/bf_shas/libuv.oneyear\n")
        raise ValueError('Please provide correct arguments, as described above.')

    data_dir = sys.argv[1] + "/"
    project_name = sys.argv[2]
    path_to_showlinenum_script = os.path.abspath(sys.argv[3])
    bf_sha_filepath = os.path.abspath(sys.argv[4])

    # Getting the list of bugfix-shas for this project
    bf_shas = []
    with open(bf_sha_filepath, "r") as bf_sha_file:
        bf_shas = bf_sha_file.read().splitlines()
    if len(bf_shas) == 0:
        raise ValueError("No SHAs of bugfix commits were found! I checked this file: " + bf_sha_filepath)
    else:
        print("\n" + str(len(bf_shas)) + " bugfix commits found. Now getting the lines that were deleted in each of them...")
    
    # Looking for the git repository for the project
    project_repo_path = data_dir + "/projects/" + project_name
    try:
        project_repo = Repo(project_repo_path)
    except Exception as e:
        raise ValueError("No Git repository found at '" + project_repo_path + "'!")

    # `deleted_lines_info` will contain (bf_sha, bf_file_name, bf_line_num, bi_file_name, bi_line_num) tuples
    # -- note that the `bf_file_name` and `bf_line_num` got Fixed in `bf_sha`
    # -- and were Introduced in `bi_sha` at `bi_file_name` and `bi_line_num`
    deleted_lines_info = []

    erroneous_bf_shas = set()
    for index, bf_sha in enumerate(bf_shas):
        if (index % 100) == 0:
            print('Currently on bf_sha #' + str(index + 1))

        # Use the git-diff command to see what was deleted and added in bf_sha
        diff_out = project_repo.git.diff("-U0", "-w", bf_sha, bf_sha + "^", stdout_as_string=False)

        # Use the `showlinenum.awk` bash script to prepend line numbers to `diff_out`
        p = subprocess.Popen(shlex.split(path_to_showlinenum_script + " show_header=0"), 
                             stdout = subprocess.PIPE, 
                             stdin = subprocess.PIPE, 
                             stderr = subprocess.STDOUT)
        p_stdout = p.communicate(input = diff_out)[0]

        # Extract the info on deleted lines only 
        # -- deleted lines appear with a `+` sign in `p_stdout` because of the way we ran `showlinenum` above
        # -- see relevant section in `../../NOTES.txt` for details
        p_stdout_lines = p_stdout.splitlines()

        filename_to_lines_dict = defaultdict(list)
        for line in p_stdout_lines:
            # A typical diff `line` looks like this:
            # src/unix/linux-core.c:472:+  if (model_idx == 0) {
            line_splits = line.split(":")

            # Get `bf_file_name` and `bf_line_num`
            try:
                if line_splits[2].startswith("+"):
                    bf_file_name = line_splits[0]
                    bf_line_num = line_splits[1]
                    filename_to_lines_dict[bf_file_name].append(bf_line_num)

            except Exception as e:
                # Problems occus when given `bf_sha` is a "bad object" (which happens rarely)
                # print('Error while processing ' + bf_sha)
                # print(str(e))
                erroneous_bf_shas.add(bf_sha)
            
        deleted_lines_info_curr_sha = []
        for bf_file_name in filename_to_lines_dict:
            linums = filename_to_lines_dict[bf_file_name]
            blame_options = ['-L' + linum + ',+1' for linum in linums]
            blame_options += [bf_sha + '^', '--', bf_file_name.replace(' ', '\ ')]

            try:
                blame_infos = project_repo.git.blame('-w', '-n', '-f', '-M', '-C', '--abbrev=40', \
                                                    stdout_as_string = False, *blame_options)
            except Exception as e:
                print(str(e))
                print((bf_sha, bf_file_name))
                continue
        
            for blame_info in blame_infos.splitlines():
                try:
                    bf_line_num = blame_info.split(')')[0].split()[-1]
                    bi_line_num = blame_info.split('(')[0].split()[-1]
                    bi_sha = blame_info.split()[0][-40:]
                    bi_file_name = ' '.join(blame_info.split('(')[0].split()[1:-1])
                    curr_tuple = (project_name, bf_sha, bf_file_name, bf_line_num, bi_sha, bi_file_name, bi_line_num)
                    deleted_lines_info_curr_sha.append(curr_tuple)

                except Exception as e:
                    print(str(e))
                    print((bf_sha, bf_file_name))
                    print('Skipping this `bf_file_name` in this `bf_sha`...')
                    break

        deleted_lines_info += deleted_lines_info_curr_sha
        
    out_dir = data_dir + 'lines_deleted_in_bf_shas/'
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    out_file_name = out_dir + pathLeaf(bf_sha_filepath) + ".buggylines"
    with open(out_file_name, 'wb') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow(('project', 'bf_sha', 'bf_file_name', 'bf_line_num', 'bi_sha', 'bi_file_name', 'bi_line_num'))
        csv_writer.writerows(deleted_lines_info)
        

    if len(erroneous_bf_shas) > 0:
        print("\nErrors encountered while processing the following " + str(len(erroneous_bf_shas)) + " bugfix commits. Skipped.")
        print(erroneous_bf_shas)

    print("\nOutput written to '" + out_file_name + "'. Done.")
#--------------------------------------------------------------------------------------------------------------------------

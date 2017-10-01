import sys
import os

sys.path.append("../util")
import Util


def listdirs(folder):
    return [ d for d in (os.path.join(folder, d1) for d1 in os.listdir(folder))
        if os.path.isdir(d)]

#input the proj-dir containing all the projects
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "!! Please give a proj_dir to pass"
        print "Example: ../../projects/"
        sys.exit()

    proj_dir = sys.argv[1]
    top_proj = listdirs(proj_dir)

    for proj in top_proj:
        with Util.cd(proj):
            dir_name = proj.split(os.sep)
            project = dir_name[-1:][0]
            print project
            git_cmd1 = "git log --no-merges --numstat --pretty=\">>>>>>>>>>>> %H <<|>> " \
                    + project + " <<|>> %cn <<|>> %cd <<|>> %an <<|>> %ad <<|>>\"" \
                    + " --diff-filter=M -- '*.java' > no_merge_log.txt"

            git_cmd2 = "git log --no-merges --pretty=\">>>>>>>>>>>> %H <<|>> " \
                    + project + " <<|>> %s <<|>> %b <<|>>\"" \
                    + " --diff-filter=M -- '*.java' > no_stat_log.txt"

            os.system(git_cmd1)
            os.system(git_cmd2)

import sys
import os

sys.path.append("../util")
from Util import cd

def getProjName(projectPath):

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    return project_name

def resetSnapShots(projPath):

    print projPath

    #repo = Repo(projPath)
    #branch = repo.active_branch

    #print branch
    #project_name = getProjName(projPath)
    snapshots = os.listdir(projPath)
    
    for s in snapshots:
        snap_dir = os.path.join(projPath,s)
        if os.path.isdir(snap_dir):
	   print snap_dir
           with cd(snap_dir):
#             os.system("git reset --hard HEAD")
             os.system("git clean -f")


def main():
    print "Run the run.py for all git repositories inside to directory"

    proj_dir = sys.argv[1]
    print "Project directory :" , proj_dir

    if not os.path.isdir(proj_dir):
        print("%s is not a valid directory" % proj_dir)
        sys.exit()

    projects = os.listdir(proj_dir)

    for prj in sorted(projects):
        proj_path = os.path.join(proj_dir,prj)
        print prj, proj_path
        resetSnapShots(proj_path)


if __name__ == "__main__":

    main()





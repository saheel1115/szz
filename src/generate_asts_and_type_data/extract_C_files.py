"""Recursively walks the given directory and copies the .c and .cpp and .cc files to output directory."""
# -------------------------------------------------------------------------------------------
import os, sys, shlex
from subprocess import Popen, PIPE
from multiprocessing.dummy import Pool

# -------------------------------------------------------------------------------------------
def isCFile(filename):
    """Returns True if `filename` ends in .c, .cpp, .cc"""
    return filename.endswith(".c") or filename.endswith(".cpp") or filename.endswith(".cc")

# -------------------------------------------------------------------------------------------
def Popen_and_print(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, close_fds=True)

    stdout, stderr = process.communicate()
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)

    return process.returncode

#--------------------------------------------------------------------------------------------------------------------------
def printUsage():
    """
    Usage: python extract_C_files <path_to_input_dir> <path_to_output_dir>
    Run `pydoc path/to/extract_C_files` for more info
    """
    print(printUsage.__doc__) 

# -------------------------------------------------------------------------------------------
def extractAndCopyCFiles(in_dir, out_dir):
    """Recursively walks the `in_dir` directory and copies the .c and .cpp and .ccfiles to `out_dir`

    Args
    ----
    in_dir: string
        Path to the directory from which C files need to be extracted
    out_dir: string
        Path to the directory where C files need to be copied
    """
    if not os.path.isdir(in_dir):
        print(in_dir + " is not a valid directory")
        print(printUsage.__doc__)
        raise IOError
    else:
        in_dir = os.path.abspath(in_dir)

    if not os.path.isdir(out_dir):
        print("Creating output directory for extracted .c, .cpp, and .cc files.")
        cmd = "mkdir -p " + out_dir
        Popen(shlex.split(cmd))
    else:
        print("Emptying the possibly non-empty output directory for extracted .c, .cpp, and .cc files.")
        cmd = "rm -rf " + out_dir + '/*'
        Popen(shlex.split(cmd))
        out_dir = os.path.abspath(out_dir)

    cmds = []
    for root, dirs, files in os.walk(in_dir):
        for nextFile in files:
            if(isCFile(nextFile)):
                fullpath = os.path.join(root, nextFile)
                outfile = "__".join(filter(None, root.partition(in_dir)[2].split('/')) + [nextFile])
                cmd = "cp " + fullpath + " " + out_dir + "/" + outfile
                cmds.append(shlex.split(cmd))

    # Create a maximum of 16 `cp` threads at a time. 16 seems small enough to not stall the system :-/
    pool = Pool(16)
    return_codes = pool.map(Popen_and_print, cmds)

# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(printUsage.__doc__)
        raise IOError
    else:
        extractAndCopyCFiles(sys.argv[1], sys.argv[2])

# -------------------------------------------------------------------------------------------

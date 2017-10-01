import os
import sys
import os.path
import logging
import shutil
import codecs

from git import *

sys.path.append("src/util")
from Util import cd
import Util

class GitRepo:

  def __init__(self, repoPath):
    self.repo_path = repoPath
    repo = Repo(repoPath)
    logging.debug(repo)
    assert (repo.bare == False) #make sure a git repo exists


    self.git = repo.git

  def fetchFiles(self, fileName, sha):

    try:
      shas = self.git.rev_list('-n 2', sha,'--remove-empty','--', fileName)
      #print shas
      return shas.split('\n')
    except Exception as e:
      print('Most likely, %s commit does not exist... Skipping related files.'
            % (sha) )
      logging.debug('Most likely, %s commit does not exist... Skipping related files.'
            % (sha) )
      return []

  def checkFile(self, fileName, sha):
    
    try:
      self.git.checkout(sha,'--', fileName)
    except Exception, e:
      # print("!!Error in checking out %s, %s\n%s" % (fileName, sha, str(e)))
      logging.debug("A renamed/deleted file couldn't be checked out: %s, %s" % (fileName, sha))
   

  def showFile(self, fileName, sha):
    
    try:
      file_content = self.git.show(sha + ":" + fileName)
      #file_content = str = unicode(self.git.show(sha + ":" + fileName), errors='ignore') 
      return file_content
    except Exception, e:
      print e
      print('file= %s, sha= %s does not exist.' % (fileName, sha))
      logging.debug('file= %s, sha= %s does not exist.' % (fileName, sha))
  
  #calls git show from command line
  # this removes unicode error
  def dumpFile(self, fileName, sha, destination):
    
    with cd(self.repo_path):   
      try:
	command = 'git show ' + sha + ":" + fileName + " > " + destination
	os.system(command)
      except Exception, e:
	print fileName, sha, destination, e

def test():
  print "Testing GitStuff"
  #gs = GitRepo("/Users/bray/top_projects/ActionBarSherlock/")
  #file_name = 'test/app/src/com/actionbarsherlock/tests/app/Issue0002.java'
  #sha = 'bffb56869b3ad224fe9d56ca5120b5d6d5a326fb' 
  #first_sha = '4b1ed196e5f2a919ace59354e00e7c1b62242161'

  gs = GitRepo("/biodata/ec_data/snapshots/openjpa/2009-04-29")
  #gs = GitRepo("/biodata/ec_data/projects/openjpa")
  file_name = 'openjpa-persistence-jdbc/src/test/java/org/apache/openjpa/persistence/query/TestSubquery.java'
  sha = '35ef9efaecb177d32d24a064bcbd40ae0578f6d5'

  for i,f_sha in enumerate(gs.fetchFiles(file_name, sha)):
    temp_file = "test"
    print "----->" , f_sha
    copy_file = temp_file + "_" + f_sha + ".java"
    gs.dumpFile(file_name,f_sha,copy_file)
    '''
    copy_content = gs.showFile(file_name,f_sha)
    print copy_file
    with open(copy_file, "w") as text_file:
      text_file.write("%s" % copy_content)
    #with codecs.open(copy_file, "w", encoding="utf-8") as f:
    #  f.write(copy_content)
    '''


if __name__ == '__main__':

  test()

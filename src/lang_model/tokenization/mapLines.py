#!/usr/bin/env python
import argparse
import os, sys
import os.path
import re
import codecs
import fnmatch
from subprocess import Popen, PIPE
import shlex

sha = "[0-9a-f]{5,40}"
start_delim = "<a>"
end_delim   = "</a>\n"

def isBlankLine(line, isMapped):
  retVal = False
  if line in ['\n', '\r\n']:
    retVal = True
  elif isMapped == True:
    if line == start_delim + end_delim:
      retVal == True
  return retVal
      
def comment_remover(text):
  def replacer(match):
    s = match.group(0)
    if s.startswith('/'):
      return ""
    else:
      return s

  pattern = re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
      re.DOTALL | re.MULTILINE
  )

  return re.sub(pattern, replacer, text)
    

def mapFileLines(inFile, outFile):

  if not os.path.isfile(inFile):
    print("!! %s file does not exist" % (inFile))
    return
  
  if not os.path.isfile(outFile):
    print("!! %s file does not exist" % (outFile))
    return  

  inf = codecs.open(inFile, "r", "iso-8859-1")
  inf_lines = inf.readlines()
  inf.close()

  temp_inFile = inFile+'.tmp'
  inf_lines1 = []
  with codecs.open(temp_inFile,'w',"iso-8859-1") as inf_temp:
    for l in inf_lines:
      l = comment_remover(l)
      l = l.replace(" ", "")
      inf_lines1.append(l)
      inf_temp.write(l)

  temp_outFile = outFile+'.tmp'
  of_lines1 = []
  of = codecs.open(outFile, "r", "iso-8859-1")
  of_lines = of.readlines()
  of.close()

  with codecs.open(temp_outFile, "w", "iso-8859-1") as of_temp:
    for l in of_lines:
      l = l.strip(start_delim).rstrip(end_delim)
      l = l.replace(" ", "")
      of_lines1.append(l)
      of_temp.write(l + '\n')
  
  diff_command = 'diff --minimal -N -B -b -w -E --unchanged-line-format="" ' \
                   + '--old-line-format="%dn " --new-line-format="" ' \
                   + temp_inFile + ' ' \
                   + temp_outFile
  
  process = Popen(shlex.split(diff_command), stdout=PIPE, close_fds=True)
  ignored_lines = process.communicate()[0].split()
  ignored_lines = set([int(i) for i in ignored_lines])
 
  #print ignored_lines
  os.remove(temp_inFile)
  os.remove(temp_outFile)
  
  last_ml = -1
  map_file = inFile + ".map"
  mf = open(map_file,'w')
  
  mf.write("toke_line,mapped_line\n")
  
  for ol in xrange(0,len(inf_lines1)):
    org_line = inf_lines1[ol].strip()
    if((ol + 1) in ignored_lines):
      #print "..ignoring %d , %s" % ((ol + 1),org_line)
      continue
   
    #print str(ol+1), org_line
    
    for ml in xrange(last_ml+1,len(of_lines1)):
      map_line = of_lines1[ml]
      #print "\t---->", str(ml+1), map_line
      if org_line == map_line:
        last_ml = ml
        write_line = ",".join((str(ml+1), str(ol+1))) + '\n'
        mf.write(write_line)
        break

  mf.close()  
      

'''
 walk directories and do some pre-processing.

 1. filename = Find src code with language extension
 2. token_file = tokenize noc_file
 4. map lines of token_file to original file 

'''

def walk_dir(input_dir, language):

  #print input_dir, language
  files_list = []
  pattern = '*.' + language 

  for root, dirs, files in os.walk(input_dir):
    for filename in fnmatch.filter(files, pattern):
      filename = os.path.join(root,filename)
      name , extension = os.path.splitext(filename)#[1][1:]
      
      noc_file = name + '.code.tokens'  #output file without any comments      
      mapFileLines(filename, noc_file)
  
def main():
  parser = argparse.ArgumentParser(
    description='Module generate tokens from source code')

  parser.add_argument('-p',dest="proj_dir", \
                      help="the directories containing src code")
  parser.add_argument('-l',dest="lang", default='java', \
                      help="languages to be processed")
 
  args = parser.parse_args()
  #print args

  if not os.path.isdir(args.proj_dir):
    print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    sys.exit()

  walk_dir(args.proj_dir, args.lang)

def test():
  #filename = '/biodata/ec_data/snapshots/facebook-android-sdk/2010-05-11/facebook/src/com/facebook/android/Facebook.java'
  #noc_file = '/biodata/ec_data/snapshots/facebook-android-sdk/2010-05-11/facebook/src/com/facebook/android/Facebook.code.tokens'
  filename = 'test/StreamingServiceGWTClientImpl.java'
  noc_file = 'test/StreamingServiceGWTClientImpl.code.tokens'
  mapFileLines(filename, noc_file)

if __name__ == "__main__":
  main()
  #test()

#!/usr/bin/env python
import argparse
import os, sys
import os.path
import fnmatch
from numpy import loadtxt
from collections import defaultdict

def read_entropy(entropy_file, reverse_entropy_file, map_file):
  if not os.path.isfile(map_file):
    print "!! %s does not exist" % map_file
    return

  if not os.path.isfile(entropy_file):
    print "!! %s does not exist" % entropy_file
    return
  
  if not os.path.isfile(reverse_entropy_file):
    print "!! %s does not exist" % reverse_entropy_file
    return
  
  keyValue = loadtxt(map_file, delimiter=",",skiprows=1,ndmin=2)
  mapDict = { int(token):int(orig) for token,orig in keyValue }

  keyValue = loadtxt(entropy_file, delimiter=",",skiprows=0,ndmin=2)
  entrDict = { int(line):float(entr) for line,entr in keyValue }
  
  #if not ((len(mapDict) == len(entrDict)) or len(mapDict) == len(entrDict)-1):
  #  print '!! potential error in ' , map_file  
  
  keyValue = loadtxt(reverse_entropy_file, delimiter=",",skiprows=0,ndmin=2)
  #mapping the reverse line back 
  rentrDict = { max(entrDict)-int(rline)+1:float(rentr) for rline,rentr in keyValue } 

  assert(len(entrDict) == len(rentrDict))
  
  dd = defaultdict(list) 

  for d in (mapDict, entrDict, rentrDict): 
      for key, value in d.iteritems():
              dd[key].append(value)

  return dd

      
'''
 walk directories and do some pre-processing.

 1. filename = Find src code with language extension
 2. token_file = tokenize noc_file
 4. map lines of token_file to original file 

'''

def walk_dir(input_dir, language, project_name):

  #print input_dir, language
  pattern = '*.' + language 

  for root, dirs, files in os.walk(input_dir):
    for filename in fnmatch.filter(files, pattern):
      filename = os.path.join(root,filename)
      name , extension = os.path.splitext(filename)
      entropy = name + '.code.tokens.sentence.entropies'        
      reverse_entropy = name + '.code.tokens.reverse.sentence.entropies'
      map_file = filename + ".map"
      merged = read_entropy(entropy, reverse_entropy, map_file)
      tmp = filename.split(input_dir)[1]
      snapshot , filename_frm_root = tmp.split(os.sep,1)
      out_file = filename + ".entropy.csv"

      of = open(out_file, 'w')
      
      for key, value in merged.iteritems():
        if (len(value) < 3):
	  print_line = (',').join((project_name, snapshot, filename_frm_root, str(key),'-1', str(value[0]),str(value[1])))
	else:
	  print_line = (',').join((project_name, snapshot,filename_frm_root, str(key), str(value[0]),str(value[1]),str(value[2])))
	  
	of.write(print_line + '\n')
      
      of.close()
  
def main(): 

  parser = argparse.ArgumentParser(
    description='Module generate tokens from source code')

  parser.add_argument('-n',dest="proj_name", \
                      help="name of the project")
  parser.add_argument('-p',dest="proj_dir", \
                      help="the directories containing src code")
  parser.add_argument('-l',dest="lang", default='java', \
                      help="languages to be processed")
 
  args = parser.parse_args()
  #print args

  if not os.path.isdir(args.proj_dir):
    print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    sys.exit()

  walk_dir(args.proj_dir, args.lang, args.proj_name)

def test():
  proj_dir = '/biodata/ec_data/snapshots/facebook-android-sdk/2015-07-08/facebook/src/com/facebook'
  proj_name = 'facebook-android-sdk'
  lang = 'java'

  walk_dir(proj_dir, lang, proj_name)

if __name__ == "__main__":
  main()
  #test()

#!/usr/bin/env python
import argparse
import os, sys
import os.path
import re
import codecs
import threading
import fnmatch

start_delim = "<a> "
end_delim   = " </a>\n"


class myThread (threading.Thread):

  def __init__(self, threadID, name, inputDir, \
               outputDir, isAppend, isReverse, cache_min_order, cache_backoff_weight):
    
    threading.Thread.__init__(self)
    self.threadID    = threadID
    self.name        = name
    self.input_dir   = inputDir
    self.output_dir  = outputDir
    self.append      = isAppend
    self.reverse     = isReverse
    self.cache_min_order = cache_min_order
    self.cache_backoff_weight = cache_backoff_weight


  def run(self):
    print "Starting " + self.name + "\n"
    corpus.process(self.input_dir, self.output_dir, \
                   self.append, self.reverse, self.cache_min_order, self.cache_backoff_weight)
    print "Exiting " + self.name + "\n"






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

def copyWoComments(inFile, outFile):

  if not os.path.isfile(inFile):
    return

  #print inFile
  #print outFile

  inf = codecs.open(inFile, "r", "iso-8859-1")

  file_lines = ""
  for line in inf:
    org_line = line.strip()
    file_lines += line
  inf.close()

  no_comments = comment_remover(file_lines)

  #print no_comments

  of = codecs.open(outFile, "w", "iso-8859-1")
  of.write(no_comments)
  of.close()

def split(name):

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    return s2.replace('_', ' ')


def appendDelim(inFile, outFile):

  if not os.path.isfile(inFile):
    print("!! %s does not exist" % inFile)
    return

  inf = codecs.open(inFile, "r", "iso-8859-1")
  file_lines = ""

  for line in inf:
    org_line = line.strip()

    tokens = org_line.split(" ")
    '''
    conv_tokens = []
    for t in tokens:
        conv_tokens.append(split(t))

    org_line = ' '.join(conv_tokens)
    '''

    org_line = ' '.join(tokens)
    org_line = start_delim + org_line + end_delim
    file_lines += org_line
  inf.close()

  of = codecs.open(outFile, "w", "iso-8859-1")
  of.write(file_lines)
  of.close()


def write_single_line(input_file, output_file=None):

  if not os.path.isfile(input_file):
    return

  if output_file == None:
    output_file = input_file + ".append"

  words = []

  fin = open(input_file)
  fout = open(output_file, 'w')

  while 1:
    try:
      line = fin.next().strip()
    except StopIteration:
      break

    words.extend(line.split())

    if len(words) > 40000:
      print >> fout, ' '.join(words)
      words = []

  if len(words) > 0:
    print >> fout, ' '.join(words)

  fin.close()
  fout.close()
  #os.system('mv %s.tt %s' % (input_file, input_file))
  return output_file


def reverse_file(file_name):

  inf = codecs.open(file_name, "r", "iso-8859-1")
  file_lines = inf.readlines()
  inf.close()

  rev_file = file_name + ".reverse"

  #print "outfile = ", rev_file

  #outf = open(rev_file, 'w')
  outf = codecs.open(rev_file, "w", "iso-8859-1")

  rev_lines = file_lines[::-1]

  for l in rev_lines:
    revword = " ".join(l.split()[::-1])
##    print "------"
##    print l
##    print revword
    outf.write(revword + "\n")

  outf.close()
  return rev_file


'''
 walk directories and do some pre-processing.

 1. filename = Find src code with language extension
 2. noc_file = Remove comments from
 3. token_file = tokenize noc_file
 4. Append delimeter after each line
 5. Append all the lines to one line
 6. Reverse the file for suffix based LM

'''

def walk_dir(input_dir, language, is_reverse, is_append):

  print input_dir, language, is_reverse, is_append

  files_list = []
  pattern = '*.' + language

  for root, dirs, files in os.walk(input_dir):
    for filename in fnmatch.filter(files, pattern):
    
      filename = os.path.join(root,filename)
      name , extension = os.path.splitext(filename)
      #print filename
      noc_file = name + '.code'  #output file without any comments

      '''
      if os.path.isfile(noc_file):
        #skip if file exists
        print "skipping.."
        continue
      '''

      #print filename
      #print noc_file
      copyWoComments(filename, noc_file)
      
      if language == "java":
        #print "java"
        os.system('java -jar src/lang_model/lexer/LexJava-1.0.jar \'%s\'' % noc_file)
      else:
        #print "c"
        os.system('java -jar src/lang_model/lexer/LexC-1.0.jar \'%s\'' % noc_file)

      token_file = noc_file + ".tokens"
      appendDelim(token_file,token_file)

      try:
        os.system('rm ' + noc_file)
      except e:
        print e

      if is_append:
        write_single_line(token_file)

      if is_reverse:
        rev_file = reverse_file(token_file)
        if is_append:
          write_single_line(rev_file)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(
      description='Module generate tokens from source code')

    parser.add_argument('-p',dest="proj_dir", help="the directories containing src code")
    parser.add_argument('-l',dest="lang", default='java', help="languages to be processed")
    parser.add_argument('--reverse',dest='reverse',action='store_true')
    parser.add_argument('--append',dest='append',action='store_true')

    parser.set_defaults(reverse=False)
    parser.set_defaults(append=False)

    args = parser.parse_args()
    print args

    if not os.path.isdir(args.proj_dir):
        print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    	sys.exit()


    walk_dir(args.proj_dir, args.lang, args.reverse, args.append)



#!/usr/bin/env python

import os
import sys


def cross(input_file, fold_num, options):
    pipes = [os.pipe() for i in xrange(fold_num)]
    
    for i in xrange(fold_num):
        pid = os.fork()
        if pid == 0:
            os.close(pipes[i][0])
 
            train_file = '%s.fold%d.train' % (input_file, i)
            test_file = '%s.fold%d.test' % (input_file, i)           
            print './completion %s -NGRAM_FILE %s.3grams -NGRAM_ORDER 3 -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, test_file, test_file, test_file)
            os.system('./completion %s -NGRAM_FILE %s.3grams -NGRAM_ORDER 3 -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, test_file, test_file, test_file))

            sys.exit()
        else:
            os.close(pipes[i][1])
    
    for p in pipes:
        os.wait()
    

if __name__ == '__main__':
    input_file = sys.argv[1]
    fold_num = int(sys.argv[2])
    options = ' '.join(sys.argv[3:])
    
    cross(input_file, fold_num, options)

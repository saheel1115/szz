#!/usr/bin/env python

import os
import sys


def cross(project, fold_num, order, options):
    pipes = [os.pipe() for i in xrange(fold_num)]

    for i in xrange(fold_num):
        pid = os.fork()
        if pid == 0:
            os.close(pipes[i][0])
 
            train_file = '%s.train' % (project)
            test_file = '%s.fold%d.test' % (project, i)           
            print './completion-entropy %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, test_file, test_file, test_file)
            os.system('./completion-entropy %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, test_file, test_file, test_file))


            sys.exit()
        else:
            os.close(pipes[i][1])
    
    for p in pipes:
        os.wait()
   
 
if __name__ == '__main__':
    project = sys.argv[1]
    fold_num = int(sys.argv[2])
    order = int(sys.argv[3])
    options = ' '.join(sys.argv[4:])
    
    cross(project, fold_num, order, options)


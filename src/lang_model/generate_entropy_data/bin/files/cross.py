#!/usr/bin/env python

import os
import sys


def cross(input_file_dir, fold_num, options, order):
    pipes = [os.pipe() for i in xrange(fold_num)]
    
    for i in xrange(fold_num):
        pid = os.fork()
        if pid == 0:
            os.close(pipes[i][0])
 
            train_file = '%s/fold%d.train' % (input_file_dir, i)
            test_file = '%s/fold%d.test' % (input_file_dir, i)
            scope_file = '%s/fold%d.scope' % (input_file_dir, i)
            print './completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, test_file)
            os.system('./completion %s -NGRAM_FILE %s.%dgrams -NGRAM_ORDER %d -SCOPE_FILE %s -INPUT_FILE %s -OUTPUT_FILE %s.output | tee %s.log' % (options, train_file, order, order, scope_file, test_file, test_file, test_file))

            sys.exit()
        else:
            os.close(pipes[i][1])
    
    for p in pipes:
        os.wait()
    

if __name__ == '__main__':
    input_file_dir = sys.argv[1]
    order = int(sys.argv[2])
    fold_num = 10
    options = ' '.join(sys.argv[3:])
    
    cross(input_file_dir, fold_num, options, order)

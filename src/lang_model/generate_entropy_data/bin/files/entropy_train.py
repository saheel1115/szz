#!/usr/bin/env python

import os
import sys

def split(input_file_dir, fold_num, suffix):
    files_list = []
    file_dir = os.path.join(input_file_dir, 'files')
    for file in os.listdir(file_dir):
        if file.endswith(suffix):
            files_list.append((int(file[:file.find('.')]), os.path.join(file_dir, file)))

    files_list.sort()
    files_list = [file for id, file in files_list]

    files_number = len(files_list)

    part_files_number = files_number/fold_num
    left_files_number = files_number%fold_num

    part_files_list = []

    # multi-process
    last_end = 0
    for i in xrange(fold_num):
        start = last_end
        last_end = start + part_files_number
        if i < left_files_number:
            last_end += 1
        
        part_files_list.append(files_list[start:last_end])

    return part_files_list


def create_fold(input_file_dir, fold_num):
    part_files_list = split(input_file_dir, fold_num, '.tokens')
    method_files_list = split(input_file_dir, fold_num, '.scope')
    
    for i in xrange(fold_num):
        train_files = []
        for j in xrange(fold_num):
            if j != i:
                train_files.extend(part_files_list[j])
        
        print >> open('%s/fold%d.test' % (input_file_dir, i), 'w'), '\n'.join(part_files_list[i])
        print >> open('%s/fold%d.scope' % (input_file_dir, i), 'w'), '\n'.join(method_files_list[i])
        os.system('cat %s > %s/fold%d.train' % (' '.join(train_files), input_file_dir, i))


def train(input_file_dir, fold_num, max_order):
    create_fold(input_file_dir, fold_num)
    
    pipes = [os.pipe() for i in xrange(fold_num)]

    
    for i in xrange(fold_num):
        pid = os.fork()
        if pid == 0:
            os.close(pipes[i][0])

            for order in xrange(1, max_order+1):
                train_file = '%s/fold%d.train' % (input_file_dir, i)
                os.system('./bin/ngram-count -text %s -lm %s.kn.lm.gz -order %d -unk -kndiscount' % (train_file, train_file, order))
                os.system('./bin/ngram -lm %s.kn.lm.gz -unk -order %d -write-lm %s.%dgrams' % (train_file, order, train_file, order))
                os.system('rm %s.kn.lm.gz' % train_file)
                
            sys.exit()
        else:
            os.close(pipes[i][1])
    
    for p in pipes:
        os.wait()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print './files_train.py input_file_dir ngram_order'
        sys.exit(1)

    input_file_dir = sys.argv[1]
    order = int(sys.argv[2])
    fold_num = 10
    
    train(input_file_dir, fold_num, order)

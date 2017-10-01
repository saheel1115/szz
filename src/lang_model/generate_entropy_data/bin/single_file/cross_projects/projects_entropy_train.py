#!/usr/bin/env python

import os
import sys

def write_single_line(input_file):
    words = []

    fin = open(input_file)
    fout = open(input_file+'.tt', 'w')
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
    
    os.system('mv %s.tt %s' % (input_file, input_file))


def split(input_file, fold_num):
    items = os.popen("wc -l %s" % input_file).read().split()
    line_num = int(items[0])
    
    part_line_num = line_num / fold_num
    
    fin = open(input_file, 'r')
    part_file_id = 0
    line_count = 0
    fout = open('%s.part%d' % (input_file, part_file_id), 'w')
    
    while True:
        try:
            line = fin.next().strip()
        except StopIteration:
            break
        
        print >> fout, line
        
        line_count += 1
        if part_file_id != fold_num-1 and line_count == part_line_num:
            part_file_id += 1
            line_count = 0
            fout = open('%s.part%d' % (input_file, part_file_id), 'w')

    fout.close()


def create_fold(input_file, fold_num):
    split(input_file, fold_num)
    
    for i in xrange(fold_num):
        os.system('mv %s.part%d %s.fold%d.test' % (input_file, i, input_file, i))
        write_single_line('%s.fold%d.test' % (input_file, i))


def create_projects_fold(cur_project, projects):
    train_files = []
    for project in projects:
        if project != cur_project:
            train_files.append(project)
    os.system('cat %s > %s.train' % (' '.join(train_files), cur_project))
    write_single_line('%s.train' % cur_project)
    

def train(cur_project, project_file, fold_num):
    projects = [project.strip() for project in open(project_file).readlines()]
    project_num = len(projects)

    create_projects_fold(cur_project, projects)
    create_fold(cur_project, fold_num)

    train_file = '%s.train' % (cur_project)
    for order in xrange(1, 11):
        os.system('./ngram-count -text %s -lm %s.kn.o%d.lm.gz -order %d -unk -kndiscount' % (train_file, train_file, order, order))
        os.system('./ngram -lm %s.kn.o%d.lm.gz -unk -write-lm %s.%dgrams -order %d' % (train_file, order, train_file, order, order))
        os.system('rm %s.kn.o%d.lm.gz' % (train_file, order))
    

if __name__ == '__main__':
    cur_project = sys.argv[1]
    project_file = sys.argv[2]
    fold_num = int(sys.argv[3])
    
    train(cur_project, project_file, fold_num)

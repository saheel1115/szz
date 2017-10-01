#import xml.etree.cElementTree as ET
#from lxml import etree as ET
from lxml import etree as ET
from commit import commit
import sys
import os

import nltk

import util
import classify

def dump_xml(commit_list,out_file):

    xmlFile = xmlWrite(out_file)

    for c in commit_list:
        xmlFile.setCommitAll(c.sha, c.tag, c.project, c.committer, c.commit_date, c.author, c.author_date, c.subject, c.body, c.isbug, c.bug_type)

    xmlFile.dump()


def parse_xml_by_bug_type(xml_doc, bug_type):
    buggy_list = []
    commit_list = parse_xml_all(xml_doc)

    for co in commit_list:
        if bug_type == co.getBugType():
            buggy_list.append(co)

    return buggy_list

def parse_xml(xml_doc, lang='java'):
    print "---> parse_xml_all"
    context = ET.iterparse(xml_doc, events=("start", "end"))

    file_name = os.path.basename(xml_doc)
    file_name = os.path.splitext(file_name)[0]
    project = ""

    commit_list = []

    co = None

    add = None
    delete = None
    file_name = None

    count = 0
    for event, element in context:
        if event is "start":
            if element.tag == 'commit':
                if not co is None:
                    commit_list.append(co)
                co = None
                add = None
                delete = None
                file_name = None
                count += 1

            if element.tag   == "sha":
                co             = commit(project, element.text)
                #co.sha = element.text
            elif element.tag == "tag":         co.tag         = element.text
            elif element.tag == "project":     co.project    = element.text
            elif element.tag == "committer":   co.committer   = element.text
            elif element.tag == "commit_date": co.commit_date = element.text
            elif element.tag == "author":      co.author      = element.text
            elif element.tag == "author_date": co.author_date = element.text
            elif element.tag == "bug":         co.isbug       = element.text
            elif element.tag == "bug_type_root":      co.bug_type_root   = element.text
            elif element.tag == "bug_type_impact":    co.bug_type_impact = element.text
            elif element.tag == "bug_type_component":    co.bug_type_comp    = element.text
            elif element.tag == "subject":     co.subject     = element.text
            elif element.tag == "body":        co.body        = element.text
            elif element.tag == "add":         add            = element.text
            elif element.tag == "delete":      delete         = element.text
            elif element.tag == "file":        file_name      = element.text
            elif element.tag == "language":    language       = element.text

        if event is "end" and element.tag == "change":
                co.addChange(add, delete, file_name,language)

    commit_list.append(co)

    return commit_list

'''
def parse_xml(xml_doc, lang):
    if lang is None:
        return parse_xml_all(xml_doc)

    context = ET.iterparse(xml_doc, events=("start", "end"))

    file_name = os.path.basename(xml_doc)
    file_name = os.path.splitext(file_name)[0]

    commit_list = []

    co = None

    add = None
    delete = None
    file_name = None

    count = 0
    for event, element in context:
        if event is "start":
            if element.tag == 'commit':
                if not co is None:
                    if co.tag is lang:
                        commit_list.append(co)
                co = None
                add = None
                delete = None
                file_name = None
                count += 1

            if element.tag   == "sha":
                co             = commit(project, element.text)
                cp.sha = element.text
            elif element.tag == "tag":         co.tag         = element.text
            elif element.tag == "project":     co.project    = element.text
            elif element.tag == "committer":   co.committer   = element.text
            elif element.tag == "commit_date": co.commit_date = element.text
            elif element.tag == "author":      co.author      = element.text
            elif element.tag == "author_date": co.author_date = element.text
            elif element.tag == "bug":         co.isbug       = element.text
            elif element.tag == "bug_type_root":      co.bug_type_root   = element.text
            elif element.tag == "bug_type_impact":    co.bug_type_impact = element.text
            elif element.tag == "bug_type_component":    co.bug_type_comp    = element.text
            elif element.tag == "subject":     co.subject     = element.text
            elif element.tag == "body":        co.body        = element.text
            elif element.tag == "add":         add            = element.text
            elif element.tag == "delete":      delete         = element.text
            elif element.tag == "file":        file_name      = element.text
            elif element.tag == "language":    language       = element.text

        if event is "end" and element.tag == "change":
                co.addChange(add, delete, file_name,language)

    if co.tag is lang:
        #print "------"
        commit_list.append(co)

    return commit_list
'''


if __name__ == "__main__":
    print (sys.argv[1])

    commit_list = parse_xml(sys.argv[1], None)
    featuresets = []

    for c in commit_list:
        '''
        print c.sha
        print c.body
        print c.subject
        print c.bug_type
        '''
        bugRootType = c.getBugRootType()
        bugImpactType = c.getBugImpactType()

        logStr = c.getLog()

        features = classify.dialogue_act_features(logStr)
        featuresets.append((features, bugRootType))

        features1 = classify.dialogue_act_features(logStr)
        featuresets.append((features, bugImpactType))

    for f in featuresets:
        print f




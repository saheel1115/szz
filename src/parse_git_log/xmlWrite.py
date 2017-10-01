#import xml.etree.cElementTree as ET
#from lxml import etree as ET
from lxml import etree as ET
import os

class xmlWrite:

    def __init__(self, out_file):

        self.xmlFile = out_file
        #print ">>>>>>>>>>>>>>", self.xmlFile

        if os.path.exists(out_file):
            tree = ET.parse(out_file)
            root = tree.getroot()
            self.root = root
        else:
            self.root = ET.Element("root")
        

    def setCommit(self, sha):

        self.commit = ET.SubElement(self.root, "commit")

        field = ET.SubElement(self.commit, "sha")
        #field.set("name", "sha")
        field.text = sha

    def setAuthor(self, author, author_date):

        field1 = ET.SubElement(self.commit, "author")
        field1.text = author
        field2 = ET.SubElement(self.commit, "author_date")
        field2.text = author_date

    def setCommitter(self, committer, commit_date):

        field1 = ET.SubElement(self.commit, "committer")
        field1.text = committer

        field2 = ET.SubElement(self.commit, "commit_date")
        field2.text = commit_date

    def setProject(self, project):
        field = ET.SubElement(self.commit, "project")
        field.text = project

    def setProjInfo(self, tag, project):
        field = ET.SubElement(self.commit, "language")
        field.text = tag


        field = ET.SubElement(self.commit, "project")
        field.text = project

    def setSubject(self, subject):
        field = ET.SubElement(self.commit, "subject")
        field.text = subject

    def setBody(self, body):

        field = ET.SubElement(self.commit, "body")
        field.text = body

    def setIsBug(self, is_bug):

        field = ET.SubElement(self.commit, "bug")
        if is_bug is True:
            field.text = "Yes"
        else:
            field.text = "No"

    def setIsBugFinal(self, is_bug):

        field = ET.SubElement(self.commit, "bug")
        field.text = str(is_bug)

    def setBugType(self, bug_class, bug_type):
        if bug_type is None:
            return
        bt = (' | ').join(bug_type)

        #print " >>>>>>>>> bt :" , bt
        field = ET.SubElement(self.commit, bug_class)
        field.text = bt

    def setBugTypeStr(self, bug_class, bug_type):
        if bug_type is None:
            return

        #print " >>>>>>>>> bt :" , bt
        field = ET.SubElement(self.commit, bug_class)
        field.text = bug_type


    def setChanges(self, add, delete, file_name, tag):

        change = ET.SubElement(self.commit, 'change')

        field = ET.SubElement(change, "add")
        field.text = add

        field = ET.SubElement(change, "delete")
        field.text = delete

        field = ET.SubElement(change, "file")
        field.text = file_name

        field = ET.SubElement(change, "language")
        field.text = tag

    def setCommitAll(self, sha,  tag,  project, committer, commit_date, author, author_date, subject, body, is_bug, bug_type_root,bug_type_impact):
        self.setCommit(sha)
        self.setProject(project)
        self.setCommitter(committer, commit_date)
        self.setAuthor(author, author_date)
        self.setIsBugFinal(is_bug)
        #self.setIsBug(is_bug)
        #self.setBugType(bug_type)
        #self.setBugTypeStr("bug_type_root",  bug_type_root)
        #self.setBugTypeStr("bug_type_impact", bug_type_impact)

        self.setSubject(subject)
        self.setBody(body)


    def dump(self):
        #print ">>>>>>>>>>>>>>", self.xmlFile
        tree = ET.ElementTree(self.root)
        tree.write(self.xmlFile, pretty_print=True)



if __name__ == "__main__":
    xml = xmlWrite("foo.xml")

    xml.setCommit("abcdefg")
    xml.setSubject("foo")
    xml.setCommit("abcdefg")
    xml.dump()

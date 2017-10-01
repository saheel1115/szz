from collections import namedtuple

Change = namedtuple('Change', 'add delete filename')

class change:
    def __init__(self, add, delete, file_name, tag = None):
        self.add = add
        self.delete = delete
        self.file_name = file_name
        self.tag = tag

    def get(self):
        return (self.add, self.delete, self.file_name, self.tag)

BugType = namedtuple('BugType', 'root impact component')

class BugType:
    def __init__(self, root, impact, component):
        self.root = root
        self.impact = impact
        self.component = component

    def get(self):
        return (self.root, self.impact, self.component)

class commit:
    def __init__(self, project, sha,
            tag = None,
            committer = None, commit_date = None,
            author = None, author_date = None,
            isbug = False,
            subject = None, body = None
            ):
        self.project = project
        self.sha = sha
        self.tag = tag
        self.committer = committer
        self.commit_date = commit_date
        self.author = author
        self.author_date = author_date
        self.isbug = isbug
        #self.bug_type = BugType(bug_type,bug_type,bug_type)
        self.bug_type_root = "OTHER"
        self.bug_type_impact = "OTHER"
        self.bug_type_comp = "OTHER"
        self.subject = subject
        self.body = body
        self.changes = []

    def addChange(self, add, delete, file_name, tag):
        if file_name is None:
            return
        elif add is None:
            add = '0'
        elif delete is None:
            delete = '0'

        ch = change(add, delete, file_name, tag)
        self.changes.append(ch)

    def getLog(self):
        logStr = ""

        if self.subject != None:
            logStr += self.subject

        if self.body != None:
            logStr += "\n" + self.body

        return logStr

    

    def getBugType(self, bug_type_str):
        if self.isbug is False:
            return None

        if not bug_type_str is None:
            return bug_type_str.strip(" |").strip()
        else:
            return "OTHER"

    def getBugRootType(self):
        return self.getBugType(self.bug_type_root)

    def getBugImpactType(self):
        return self.getBugType(self.bug_type_impact)

    def getBugCompType(self):
        return self.getBugType(self.bug_type_comp)

    def __str__(self):
        retStr = "\n-----------------------"

        retStr += "\nproject : " + str(self.project)
        retStr += "\nlang : " + str(self.tag)
        retStr += "\nsha : " + str(self.sha)
        retStr += "\nauthor : " + str(self.author)
        retStr += "\nauthor_date : " + str(self.author_date)
        retStr += "\nsubject : " + str(self.subject)
        retStr += "\nbody : " + str(self.body)
        retStr += "\nisBug : " + str(self.isbug)
        #retStr += "\nbug_type : " + str(self.getBugType())
        for c in self.changes:
            retStr += '\n' + c.add + "\t" + c.delete + "\t" + c.file_name

        return retStr

    def dumpStr(self):

        retStr = ""
        
        for c in self.changes:
          retStr = (',').join((
                      str(c.tag), 
                      str(self.project), 
                      str(c.file_name), 
                      str(self.sha), 
                      str(self.author), 
                      str(self.author_date), 
                      str(self.isbug),
                      str(c.add), 
                      str(c.delete)
                    ))
          print retStr

import sys

import logging
from collections import namedtuple

sys.path.append("src/util")
from DatabaseCon import DatabaseCon


proj = namedtuple('proj', ['language', 'project', 'commit_date_min', 'commit_date_max'])

class proj(namedtuple('proj', ['language', 'project', 'commit_date_min', 'commit_date_max'])):
    __slots__ = ()

    def __repr__(self):
        return "%s|%s|%s|%s\n" % (self.language, self.project, self.commit_date_min, self.commit_date_max)


class DbProj:

	def __init__(self, proj=None, lang=None):
		self.project = proj
		self.language = lang
		self.projects = []

	def __str__(self):

		print_str = ""

		for p in self.projects:
			print_str += str(p)

		return print_str

	def connectDb(self, db, dbUser, dbHost, dbPort):

		self.dbCon = DatabaseCon(db, dbUser, dbHost, dbPort)

	def fetchDatesFromTable(self, table):

		sql_command = "SELECT tag, project, min(commit_date), max(commit_date)"
		sql_command +=  " FROM " + table + " Where tag like \'" + self.language + "\'"
		sql_command +=  " and project = \'" + self.project + "\' group by tag, project"

		print sql_command

		rows = self.dbCon.execute(sql_command)

		for row in rows:
			language, project, commit_date_min, commit_date_max = row
			p = proj(language, project, commit_date_min, commit_date_max)
			self.projects.append(p)

	def countCommitBetweenDates(self, table, snapshot1, snapshot2):

            snapshot1 = "'" + snapshot1 + "'"
            snapshot2 = "'" + snapshot2 + "'"

            sql_command = "SELECT distinct file_name, sha"
            sql_command +=  " FROM " + table + " Where tag like \'" + self.language + "\'"
            sql_command +=  " and project = \'" + self.project + "\' and commit_date >= " \
                               + snapshot1 + " and commit_date < " + snapshot2

            #print sql_command
            rows = self.dbCon.execute(sql_command)
            return len(rows)


	def printCommitDates(self):

		for p in self.projects:
			print p

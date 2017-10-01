import sys

import logging
from collections import namedtuple

sys.path.append("src/util")
from DatabaseCon import DatabaseCon


sha = namedtuple('proj', ['language', 'project', 'file_name', 'sha', 'author', 'author_date',
    'is_bug', 'insertion', 'deletion'])

class sha(namedtuple('proj', ['language', 'project', 'file_name', 'sha', 'author', 'author_date',
    'is_bug', 'insertion', 'deletion'])):
    __slots__ = ()

    def __repr__(self):
        return "%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (self.language, self.project, self.file_name, self.sha,
                self.author, self.author_date, self.is_bug, self.insertion, self.deletion)


class DbAll_changes:

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

		sql_command = "SELECT language, project, min(commit_date), max(commit_date)"
		sql_command +=  " FROM " + table + " Where language iLike \'" + self.language + "\'"
		sql_command +=  " and project = \'" + self.project + "\' group by language, project"

		print sql_command

		rows = self.dbCon.execute(sql_command)

		for row in rows:
			language, project, commit_date_min, commit_date_max = row
			p = proj(language, project, commit_date_min, commit_date_max)
			self.projects.append(p)


	def printCommitDates(self):

		for p in self.projects:
			print p

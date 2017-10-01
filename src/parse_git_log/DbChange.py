import sys, os
import psycopg2
import logging
import codecs

sys.path.append("../util")
sys.path.append("../change")

from DatabaseCon import DatabaseCon
from Config import Config
import Util
from commit import commit


class DbChange:
  def __init__(self, config):

    self.cfg = config
    
    self.connect_db()
    #self.clean_db()


  def connect_db(self):
    self.db_config = self.cfg.ConfigSectionMap("Database")
    logging.debug("Database configuration = %r\n", self.db_config)
    self.dbCon = DatabaseCon(self.db_config['database'], self.db_config['user'], \
                             self.db_config['host'], self.db_config['port'])


  def clean_db(self):
    schema = self.db_config['schema']
    response = raw_input("Deleting database %s ?" % (self.db_config['schema'] + '.' \
      + self.db_config['table']))
    #response = 'y'
    if response.lower().startswith('y'):
      for table in [self.db_config['table']]:
        tab = schema + "."  + table
        print("Deleting from table %r \n" % table)
        sql_command = "DELETE FROM " + tab
        self.dbCon.insert(sql_command)


    self.dbCon.commit()

  def commit_db(self):
    self.dbCon.commit()


  def insert_change_table(self, valueStr):

    schema = self.db_config['schema']
    table = schema + "." + self.db_config['table']

    #print table

    #logging.debug("table = %r" % table)

    sql_command = "INSERT INTO " + table + \
                "(language, project, file_name, sha, author, author_date, is_bug, " + \
                  "insertion, deletion)" + \
                  "VALUES (" + valueStr + ")"
    
    #print sql_command
    #logging.debug(sql_command)
    self.dbCon.insert(sql_command)

  def close(self):
    self.dbCon.close()

  @staticmethod
  def toStr(text):
    try:
      text1 = str(text).encode('iso-8859-1')
      temp_text = text1.replace("\'","\"")
      return "\'" + str(temp_text) + "\'"
    except:
      print type(text)
      return None
    #text = str(text).encode('utf-8')


  def dump_change(self, this_commit):

    author_date = this_commit.author_date.split(" ")[0]

    for c in this_commit.changes:
      insert_str = (',').join((
                  self.toStr(c.tag), 
                  self.toStr(this_commit.project), 
                  self.toStr(c.file_name), 
                  self.toStr(this_commit.sha), 
                  self.toStr(this_commit.author), 
                  self.toStr(author_date), 
                  self.toStr(this_commit.isbug),
                  self.toStr(c.add), 
                  self.toStr(c.delete)
                ))
      
      self.insert_change_table(insert_str)

  
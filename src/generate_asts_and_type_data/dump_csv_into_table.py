# Fetches the CSV file (containing type data) from the given project folder and writes it to the common typedata table in database
#----------------------------------------------------------------------------------
import os, sys, psycopg2, csv, ntpath

#----------------------------------------------------------------------------------
# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#----------------------------------------------------------------------------------
if len(sys.argv) != 4 or not os.path.isfile(sys.argv[1]) or not sys.argv[3] in ['learn', 'old', 'new', 'ss']:
    print('\nUsage: python dump_csv_into_table.py <path_to_csv_file> <project_name> <old_or_new_or_learn_or_ss>\n')
    print('Sample usage: python dump_csv_into_table.py data/corpus/libgit2/learn_old_ss_typedata.csv libgit2 old')
    print('Sample usage: python dump_csv_into_table.py data/corpus/libgit2/new_typedata.csv libgit2 new\n')
    raise IOError

csv_filename = sys.argv[1]
project_name = sys.argv[2]
old_or_new_or_learn_or_ss = sys.argv[3]

# PostgreSQL table names cannot have hyphens, apparently
table_name = "err_corr_c.typedata_" + project_name + "_" + old_or_new_or_learn_or_ss
table_name = table_name.replace('-', '_')

# Establish a connection to PostgreSQL
con = None
csv_file = None

try:
    con = psycopg2.connect(database='saheel', user='saheel')
    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS ' + table_name)
    cur.execute('CREATE TABLE ' + table_name + ' (project varchar(25), \
                                                  snapshot varchar(12), \
                                                  file_name text, \
                                                  sha varchar(42), \
                                                  line_num integer NOT NULL, \
                                                  line_type varchar(12), \
                                                  parent1 varchar(12), \
                                                  parent2 varchar(12), \
                                                  parent3 varchar(12), \
                                                  parent4 varchar(12), \
                                                  parent5 varchar(12), \
                                                  parents_all text, \
                                                  is_new integer)')

    csv_file = open(csv_filename, 'r')
    cur.copy_from(csv_file, table_name, sep=",")

    con.commit()

except Exception, e:
    if con:
        con.rollback()
    raise e

finally:
    if con:
        con.close()
    if csv_file:
        csv_file.close()      
#----------------------------------------------------------------------------------

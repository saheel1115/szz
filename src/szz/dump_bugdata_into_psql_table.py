#--------------------------------------------------------------------------------------------------------------------------
import os, sys, psycopg2, csv
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
def dump_bugdata_ss_in_psql(bugdata_ss, project_name):
    # PostgreSQL table names cannot have hyphens, apparently
    project_name = project_name.replace('-', '_')

    bugdata_ss_table_name = "err_corr_c.bugdata_" + project_name + "_ss"
    typedata_ss_table_name = "err_corr_c.typedata_" + project_name + "_ss"
    merged_ss_table_name = "err_corr_c.bug_typedata_" + project_name + "_ss"

    try:
        con = psycopg2.connect(database="saheel", user="saheel") 
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS " + bugdata_ss_table_name)
        cur.execute("CREATE TABLE " + bugdata_ss_table_name + " (project varchar(25), \
                                                                  file_name text, \
                                                                  sha varchar(42), \
                                                                  line_num integer NOT NULL, \
                                                                  is_new integer, \
                                                                  is_buggy smallint, \
                                                                  bf_ss varchar(12), \
                                                                  bf_file_name text, \
                                                                  bf_sha varchar(42), \
                                                                  bf_line_num integer NOT NULL)")

        query = "INSERT INTO " + bugdata_ss_table_name + " (project, file_name, sha, line_num, is_new, is_buggy, bf_ss, bf_file_name, bf_sha, bf_line_num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(query, bugdata_ss)
        con.commit()
        

    except Exception, e:
        if con:
            con.rollback()
        raise e

    finally:
        if con:
            con.close()

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
        print("\nUsage: python calc_metrics.py <path_to_data_dir> <project_name>")
        print("Sample: python calc_metrics.py data/ libgit2\n")
        raise IOError
    
    data_dir = sys.argv[1]
    project_name = sys.argv[2]

    corpus_path = data_dir + "/corpus/" + project_name + "/"

    bugdata_path = corpus_path + "/ss_bugdata.csv"
    with open(bugdata_path, 'rb') as bugdata_file:
        csv_reader = csv.reader(bugdata_file)
        bugdata_ss = []
        for row in csv_reader:
            bugdata_ss.append(tuple(row))

    dump_bugdata_ss_in_psql(bugdata_ss, project_name)

#--------------------------------------------------------------------------------------------------------------------------

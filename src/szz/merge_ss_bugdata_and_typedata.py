#--------------------------------------------------------------------------------------------------------------------------
import os, sys, psycopg2, csv
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
        print("\nUsage: python calc_metrics.py <path_to_data_dir> <project_name>")
        print("Sample: python calc_metrics.py data/ libgit2\n")
        raise IOError
    
    data_dir = sys.argv[1]
    project_name = sys.argv[2]

    # PostgreSQL table names cannot have hyphens, apparently
    project_name = project_name.replace('-', '_')

    bugdata_ss_table_name = "err_corr_c.bugdata_" + project_name + "_ss"
    typedata_ss_table_name = "err_corr_c.typedata_" + project_name + "_ss"
    merged_ss_table_name = "err_corr_c.bug_typedata_" + project_name + "_ss"

    try:
        con = psycopg2.connect(database="saheel", user="saheel") 
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS " + merged_ss_table_name)
        cur.execute("SELECT typeT.*, COALESCE(bugT.is_buggy, 0) as is_buggy, bugT.bf_ss, bugT.bf_file_name, bugT.bf_sha, bugT.bf_line_num \
                     INTO " + merged_ss_table_name + " \
                     FROM " + bugdata_ss_table_name + " as bugT \
                         RIGHT JOIN " + typedata_ss_table_name + " as typeT \
                             ON (bugT.project = typeT.project AND \
                                 bugT.sha = typeT.sha AND \
                                 bugT.file_name = typeT.file_name AND \
                                 bugT.line_num = typeT.line_num)")
        con.commit()

    except Exception, e:
        if con:
            con.rollback()
        raise e

    finally:
        if con:
            con.close()

#--------------------------------------------------------------------------------------------------------------------------

"""
This script adds a specific column to the `bug_typedata_projectname_ss` tables. The added column contains the nesting depth (>=0) of each line. (BT stands for bug_type)
"""
import os, sys, psycopg2, ntpath, traceback, subprocess
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
def get_BT_data(project_name):
    BT_ss_table_name = "err_corr_c.bug_typedata_" + project_name + "_ss"
    BT_ss_table_name = BT_ss_table_name.replace('-', '_')

    BT_data = []
    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("SELECT file_name, sha, line_num, parents_all FROM " + BT_ss_table_name)
        BT_data = list(cur.fetchall())
        
    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    if con:
        con.close()
        
    # Make it a list of lists instead of list of tuples
    for index, BT_tuple in enumerate(BT_data):
        BT_data[index] = list(BT_tuple)
        
    return BT_data
#--------------------------------------------------------------------------------------------------------------------------
def dump_BT_prime_table(BT_data, project_name):
    BT_prime_table_name = "err_corr_c.BT_prime_" + project_name
    BT_prime_table_name = BT_prime_table_name.replace('-', '_')

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS " + BT_prime_table_name + " ")
        query = """
                CREATE TABLE """ + BT_prime_table_name + """ (file_name text,
                                                              sha varchar(42),
                                                              line_num integer, 
                                                              parents_all text,
                                                              depth integer)
                """
        cur.execute(query)

        query = "INSERT INTO " + BT_prime_table_name + " (file_name, sha, line_num, parents_all, depth) VALUES (%s, %s, %s, %s, %s)"
        cur.executemany(query, BT_data)

        con.commit()
        
    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
def join_BT_ss_and_BT_prime(project_name):
    BT_ss_table_name = "err_corr_c.bug_typedata_" + project_name + "_ss"
    BT_ss_table_name = BT_ss_table_name.replace('-', '_')

    BT_prime_table_name = "err_corr_c.BT_prime_" + project_name
    BT_prime_table_name = BT_prime_table_name.replace('-', '_')

    BT_merged_table_name = "err_corr_c.bug_typedata_" + project_name + "_ss_wd"
    BT_merged_table_name = BT_merged_table_name.replace('-', '_')

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()
        
        cur.execute("ALTER TABLE " + BT_ss_table_name + " DROP COLUMN IF EXISTS depth")
        query = """
                SELECT ss.*, prime.depth
                INTO """ + BT_merged_table_name + """
                FROM """ + BT_ss_table_name + """ as ss
                    JOIN """ + BT_prime_table_name + """ as prime
                        ON (ss.file_name = prime.file_name AND
                            ss.sha = prime.sha AND
                            ss.line_num = prime.line_num)
                """
        cur.execute(query)
        con.commit()
        
        cur.execute("DROP TABLE " + BT_prime_table_name)
        cur.execute("DROP TABLE " + BT_ss_table_name)
        cur.execute("ALTER TABLE " + BT_merged_table_name + " RENAME TO " + BT_ss_table_name.split('.')[1])
        con.commit()

    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python add_depth_to_BT_table.py <project_name>")
        print("\nSample usage: python add_depth_to_BT_table.py libgit2")
        raise ValueError("Incorrect input arguments. Aborting...")
    
    project_name = sys.argv[1]
    
    # depth_dict = get_depth_data(project_name)
    # if not depth_dict:
    #     raise ValueError("`get_depth_data` returned an empty `depth_dict` dictionary. Aborting...")

    print("\nNow fetching BT_ss_data...")

    # BT_data is a list of lists; each element list = [file_name, sha, line_num, parents_all]
    BT_data = get_BT_data(project_name)
    if not BT_data:
        raise ValueError("`get_BT_data` returned an empty `BT_data` list. Aborting...")

    print("\nNow creating BT_prime_data, i.e., table with `depth` appended to BT_ss_data...")

    # We will add `depth` attribute to each row in BT_data
    error_count = 0
    for index, BT_tuple in enumerate(BT_data):
        # `depth` = number of parents as given in `parents_all` column of BT table
        depth = BT_tuple[3].count('-') + 1
        if BT_tuple[3] == '':
            BT_data[index].append(0)
        else:
            BT_data[index].append(depth)

    print("\nNow dumping the temporary table BT_prime. This may take approx. 3-4 min per million LOC...")
    dump_BT_prime_table(BT_data, project_name)

    print("\nNow joining BT_ss and BT_prime to get desired table. This takes about 2 min per million LOC...")
    join_BT_ss_and_BT_prime(project_name)

#--------------------------------------------------------------------------------------------------------------------------

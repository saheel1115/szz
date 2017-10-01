"""
This script adds a specific column to the `bug_type_entropy_projectname_old` tables. The added column contains the nesting depth (>=0) of each line.
"""
import os, sys, psycopg2, ntpath, traceback, subprocess
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
def get_BTE_data(project_name):
    BTE_old_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old"
    BTE_old_table_name = BT_old_table_name.replace('-', '_')

    BTE_data = []
    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("SELECT file_name, sha, line_num, parents_all FROM " + BTE_old_table_name)
        BTE_data = list(cur.fetchall())
        
    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    if con:
        con.close()
        
    # Make it a list of lists instead of list of tuples
    for index, BTE_tuple in enumerate(BTE_data):
        BTE_data[index] = list(BTE_tuple)
        
    return BTE_data
#--------------------------------------------------------------------------------------------------------------------------
def dump_BTE_prime_table(BTE_data, project_name):
    BTE_prime_table_name = "err_corr_c.BTE_prime_" + project_name
    BTE_prime_table_name = BTE_prime_table_name.replace('-', '_')

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS " + BTE_prime_table_name + " ")
        query = """
                CREATE TABLE """ + BTE_prime_table_name + """ (file_name varchar(100), 
                                                              sha varchar(42),
                                                              line_num integer, 
                                                              parents_all varchar(144), 
                                                              depth integer)
                """
        cur.execute(query)

        query = "INSERT INTO " + BTE_prime_table_name + " (file_name, sha, line_num, parents_all, depth) VALUES (%s, %s, %s, %s, %s)"
        cur.executemany(query, BTE_data)

        con.commit()
        
    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
def join_BTE_old_and_BTE_prime(project_name):
    BTE_old_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old"
    BTE_old_table_name = BTE_old_table_name.replace('-', '_')

    BTE_prime_table_name = "err_corr_c.BTE_prime_" + project_name
    BTE_prime_table_name = BTE_prime_table_name.replace('-', '_')

    BTE_merged_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old_wd"
    BTE_merged_table_name = BTE_merged_table_name.replace('-', '_')

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()
        
        cur.execute("ALTER TABLE " + BTE_old_table_name + " DROP COLUMN IF EXISTS depth")
        query = """
                SELECT old.*, prime.depth
                INTO """ + BTE_merged_table_name + """
                FROM """ + BTE_old_table_name + """ as old
                    JOIN """ + BTE_prime_table_name + """ as prime
                        ON (old.file_name = prime.file_name AND
                            old.sha = prime.sha AND
                            old.line_num = prime.line_num)
                """
        cur.execute(query)
        con.commit()
        
        cur.execute("DROP TABLE " + BTE_prime_table_name)
        cur.execute("DROP TABLE " + BTE_old_table_name)
        cur.execute("ALTER TABLE " + BTE_merged_table_name + " RENAME TO " + BTE_old_table_name.split('.')[1])
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
        print("\nUsage: python add_depth_to_BTE_table.py <project_name>")
        print("\nSample usage: python add_depth_to_BTE_table.py libgit2")
        raise ValueError("Incorrect input arguments. Aborting...")
    
    project_name = sys.argv[1]
    
    # depth_dict = get_depth_data(project_name)
    # if not depth_dict:
    #     raise ValueError("`get_depth_data` returned an empty `depth_dict` dictionary. Aborting...")

    print("\nNow fetching BTE_old_data...")

    # BTE_data is a list of lists; each element list = [file_name, sha, line_num, parents_all]
    BTE_data = get_BTE_data(project_name)
    if not BTE_data:
        raise ValueError("`get_BTE_data` returned an empty `BTE_data` list. Aborting...")

    print("\nNow creating BTE_prime_data, i.e., table with `depth` appended to BTE_old_data...")

    # We will add `depth` attribute to each row in BTE_data
    error_count = 0
    for index, BTE_tuple in enumerate(BTE_data):
        # `depth` = number of parents as given in `parents_all` column of BTE table
        depth = BTE_tuple[3].count('-') + 1
        if BTE_tuple[3] == '':
            BTE_data[index].append(0)
        else:
            BTE_data[index].append(depth)

    print("\nNow dumping the temporary table BTE_prime. This may take approx. 3-4 min per million LOC...")
    dump_BTE_prime_table(BTE_data, project_name)

    print("\nNow joining BTE_old and BTE_prime to get desired table. This takes about 2 min per million LOC...")
    join_BTE_old_and_BTE_prime(project_name)

#--------------------------------------------------------------------------------------------------------------------------

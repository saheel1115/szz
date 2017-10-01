"""
This script adds a specific column to the `bug_type_entropy_projectname_old` tables. The added column contains the number of lines deleted in the SHA in which each file was modified. 

But there's a catch. The column equals -1 if the line that was modified is a bug (because since it's a buggy line, it is going to be deleted -- note that this table records the `old` versions of the files committed), otherwise it equals the number of lines deleted in that file in that commit. This is done to fulfill the needs of a specific experimental setup.
"""
import os, sys, psycopg2, ntpath, traceback, subprocess
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
def get_deletion_data(project_name):
    everything_table_name = "err_corr_c.everything"

    deletion_tuples = []
    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("SELECT sha, sum(deletion) FROM " + everything_table_name + " WHERE project = '" + project_name + "' AND isbug=1 GROUP BY sha")
        deletion_tuples = cur.fetchall()
        
    except Exception as e:
        print(traceback.print_exc())
        print(str(e))
        raise e

    finally:
        if con:
            con.close()
        
    return dict(deletion_tuples)

#--------------------------------------------------------------------------------------------------------------------------
def get_BTE_data(project_name):
    BTE_old_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old"

    BTE_data = []
    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("SELECT file_name, sha, line_num, is_buggy FROM " + BTE_old_table_name)
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

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS " + BTE_prime_table_name + " ")
        query = """
                CREATE TABLE """ + BTE_prime_table_name + """ (file_name varchar(100), 
                                                              sha varchar(42),
                                                              line_num integer, 
                                                              is_buggy integer, 
                                                              num_of_del integer)
                """
        cur.execute(query)

        query = "INSERT INTO " + BTE_prime_table_name + " (file_name, sha, line_num, is_buggy, num_of_del) VALUES (%s, %s, %s, %s, %s)"
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
    BTE_prime_table_name = "err_corr_c.BTE_prime_" + project_name
    BTE_merged_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old_wd"

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()
        
        cur.execute("ALTER TABLE " + BTE_old_table_name + " DROP COLUMN IF EXISTS num_of_del")
        query = """
                SELECT old.*, prime.num_of_del
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
        print("\nUsage: python add_num_of_deletions_to_BTE_table.py <project_name>")
        print("\nSample usage: python add_num_of_deletions_to_BTE_table.py libgit2")
        raise ValueError("Incorrect input arguments. Aborting...")
    
    project_name = sys.argv[1]
    
    deletion_dict = get_deletion_data(project_name)
    if not deletion_dict:
        raise ValueError("`get_deletion_data` returned an empty `deletion_dict` dictionary. Aborting...")

    print("\nNow fetching BTE_old_data...")

    # BTE_data is a list of lists; each element list = [file_name, sha, line_num, is_buggy]
    BTE_data = get_BTE_data(project_name)
    if not BTE_data:
        raise ValueError("`get_BTE_data` returned an empty `BTE_data` list. Aborting...")

    print("\nNow creating BTE_prime_data, i.e., table with `num_of_del` appended to BTE_old_data...")

    # We will add `num_of_del` attribute to each row in BTE_data
    error_count = 0
    for index, BTE_tuple in enumerate(BTE_data):
        # If line is buggy, assign -1; else, the actual number of lines deleted in that file in that bugfix commit
        if BTE_tuple[3] == 1:
            try:
                BTE_data[index].append(deletion_dict[BTE_tuple[1]])
            except Exception as e:
                BTE_data[index].append(0)
                error_count += 1
                print("!!! deletion_dict look-up failed for this line:")
                pprint(BTE_tuple)

        else:
            BTE_data[index].append(-1)

    # BTE_data = [tuple(curr_list) for curr_list in BTE_data]
    print("\n" + str(error_count) + " errors occurred while processing a total of " + str(len(BTE_data)) + " rows")

    print("\nNow dumping the temporary table BTE_prime. This may take approx. 3-4 min per million LOC...")
    dump_BTE_prime_table(BTE_data, project_name)

    print("\nNow joining BTE_old and BTE_prime to get desired table. This takes about 2 min per million LOC...")
    join_BTE_old_and_BTE_prime(project_name)

#--------------------------------------------------------------------------------------------------------------------------

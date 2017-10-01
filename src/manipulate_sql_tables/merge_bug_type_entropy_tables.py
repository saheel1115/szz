#--------------------------------------------------------------------------------------------------------------------------
import os, sys, psycopg2
import traceback

#--------------------------------------------------------------------------------------------------------------------------
def merge_tables_for_new(project_name):
    bug_typedata_new_table_name = "err_corr_c.bug_typedata_" + project_name + "_new"
    entropydata_new_table_name = "err_corr_c.entropydata_" + project_name + "_new"
    merged_new_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_new"

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        print("Database connection established.\nNow merging the `new` tables for " + project_name + "...")
        cur.execute("DROP TABLE IF EXISTS " + merged_new_table_name)
        query = """
                SELECT bug.project, entr.*, bug.line_type, bug.parent1, bug.parent2, bug.parent3, bug.parent4,
                    bug.parent5, bug.parents_all, COALESCE(bug.is_buggy, 0) as is_buggy
                INTO """ + merged_new_table_name + """
                FROM """ + bug_typedata_new_table_name + """ as bug 
                    JOIN """ + entropydata_new_table_name + """ as entr 
                    ON (entr.file_name = bug.file_name AND
                        entr.sha = bug.sha AND
                        entr.line_num = bug.line_num AND
                        entr.is_new = bug.is_new)
                """
        cur.execute(query)
        con.commit()

    except Exception as e:
        if con:
            con.rollback()
        print(traceback.format_exc())
        raise e

    try:
        cur.execute("GRANT ALL ON " + merged_new_table_name + " TO PUBLIC")
        con.commit()

    except Exception as e:
        if con:
            con.rollback()
        print(traceback.format_exc())
        raise e

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
def merge_tables_for_old(project_name):
    bug_typedata_old_table_name = "err_corr_c.bug_typedata_" + project_name + "_old"
    entropydata_old_table_name = "err_corr_c.entropydata_" + project_name + "_old"
    merged_old_table_name = "err_corr_c.bug_type_entropy_" + project_name + "_old"

    try:
        con = psycopg2.connect(database='saheel', user='saheel')
        cur = con.cursor()

        print("Database connection established.\nNow merging the `old` tables for " + project_name + "...")
        cur.execute("DROP TABLE IF EXISTS " + merged_old_table_name)
        con.commit()
        query = """
                SELECT bug.project, entr.*, bug.line_type, bug.parent1, bug.parent2, bug.parent3, bug.parent4,
                    bug.parent5, bug.parents_all, COALESCE(bug.is_buggy, 0) as is_buggy
                INTO """ + merged_old_table_name + """
                FROM """ + bug_typedata_old_table_name + """ as bug 
                    JOIN """ + entropydata_old_table_name + """ as entr 
                    ON (entr.file_name = bug.file_name AND
                        entr.sha = bug.sha AND
                        entr.line_num = bug.line_num AND
                        entr.is_new = bug.is_new)
                """
        cur.execute(query)
        con.commit()

    except Exception as e:
        if con:
            con.rollback()
        print(traceback.format_exc())
        raise e

    try:
        cur.execute("GRANT ALL ON " + merged_old_table_name + " TO PUBLIC")
        con.commit()

    except Exception as e:
        if con:
            con.rollback()
        print(traceback.format_exc())
        raise e

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python this_script.py <project_name>\n")
        print("\nSample usage: python this_script.py libgit2\n")
        raise ValueError("Please provide correct arguments.")

    project_name = sys.argv[1]

    merge_tables_for_new(project_name)
    merge_tables_for_old(project_name)

#--------------------------------------------------------------------------------------------------------------------------

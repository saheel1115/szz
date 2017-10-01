#--------------------------------------------------------------------------------------------------------------------------
import os, sys, psycopg2, pickle
from pprint import pprint

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
        print("\nUsage: python calc_metrics.py <path_to_data_dir> <project_name>")
        print("\nSample usage: python calc_metrics.py data/ libgit2\n")
        raise IOError
    
    data_dir = sys.argv[1]
    project_name = sys.argv[2]
    corpus_path = data_dir + '/corpus/' + project_name
    results_file_path = data_dir + '/ast_node_bugginess_results/' + project_name + '.data'
    ss_names = [ss_name for ss_name in os.listdir(corpus_path) if os.path.isdir(corpus_path + '/' + ss_name)]
    ss_names.sort()

    parent_types = ['do', 'while', 'for', 'if', 'else', 'switch', 'function']

    # Algo:
    # 1. Get #buggy_lines/#total_lines for each (parent_type, ss_name) pair
    # 2. Then aggregate it over all snapshots to get project-level ast-node-bugginess

    # Step 1:
    num_of_buggy_lines_per_ss_type_pair = {}
    num_of_total_lines_per_ss_type_pair = {}
    for parent_type in parent_types:
        print("Processing type: " + parent_type + "...")
        for ss_name in ss_names:
            try:
                con = psycopg2.connect(database='saheel', user='saheel')
                cur = con.cursor()
                
                table_name = "err_corr_c.bug_typedata_" + project_name + "_ss"
                table_name = table_name.replace('-', '_')
                query = "SELECT count(*) \
                         FROM " + table_name + " \
                         WHERE snapshot='" + ss_name + "' \
                               AND is_buggy='1' \
                               AND parent1='" + parent_type + "'"
                cur.execute(query)
                # Indexing transforms each result of the form `[(40L,)]` into `40`
                num_of_buggy_lines_per_ss_type_pair[(ss_name, parent_type)] = cur.fetchall()[0][0] 

                query = "SELECT count(*) \
                         FROM " + table_name + " \
                         WHERE snapshot='" + ss_name + "' \
                               AND parent1='" + parent_type + "'"
                cur.execute(query)
                # Indexing transforms each result of the form `[(40L,)]` into `40`
                num_of_total_lines_per_ss_type_pair[(ss_name, parent_type)] = cur.fetchall()[0][0] 

            except Exception as e:
                raise e

            finally:
                if con:
                    con.close()

    # Step 2:
    num_of_buggy_lines_per_type = {}
    num_of_total_lines_per_type = {}
    for parent_type in parent_types:
        num_of_buggy_lines_per_type[parent_type] = 0
        num_of_total_lines_per_type[parent_type] = 0

    for key in num_of_buggy_lines_per_ss_type_pair:
        ss_name, parent_type = key
        num_of_buggy_lines_per_type[parent_type] += num_of_buggy_lines_per_ss_type_pair[key]
        num_of_total_lines_per_type[parent_type] += num_of_total_lines_per_ss_type_pair[key]

    type_bugginess = {}
    for p_type in parent_types:
        if num_of_total_lines_per_type[p_type] != 0:
            type_bugginess[p_type] = num_of_buggy_lines_per_type[p_type]*1.0 \
                                     /num_of_total_lines_per_type[p_type]
        else:
            type_bugginess[p_type] = -1


    with open(results_file_path, 'wb') as out_file:
        pickle.dump(type_bugginess, out_file)

#--------------------------------------------------------------------------------------------------------------------------

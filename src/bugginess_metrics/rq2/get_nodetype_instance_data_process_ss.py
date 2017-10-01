#--------------------------------------------------------------------------------------------------------------------------
import os, sys, psycopg2, csv, pandas, ntpath

#--------------------------------------------------------------------------------------------------------------------------
def pathLeaf(path):
    '''Returns the basename of the given path, e.g. pathLeaf('/hame/saheel/git_repos/szz/abc.c/') will return "abc.c"'''
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#--------------------------------------------------------------------------------------------------------------------------
def getProperFilepath(myname):
    '''Given a string of the form "s1__s2__s3.c", it returns "s1/s2/s3.c"'''
    return myname.replace('__', '/')

#--------------------------------------------------------------------------------------------------------------------------
def get_instance_data_for_ss(project_name, ss_name, nt_instances_data_file_path, out_data_dir):
    # Postgres connection stuff
    table_name = 'err_corr_c.bug_typedata_' + project_name + '_ss'
    table_name = table_name.replace('-', '_')
    con = psycopg2.connect(database="saheel", user="saheel") 
    cur = con.cursor()

    colnames = ['project', 'snapshot', 'file_name', 'node_type', 'start_linum', 'end_linum', 'id', 'method', 'method_count']
    instance_locations_data = pandas.read_csv(nt_instances_data_file_path, names=colnames, header=None, dtype='object')
    
    # Fetch the bug data for the current c_cpp_file from the database
    # ...and convert it into a pandas DataFrame for quick per-file processing
    cur.execute("SELECT file_name, line_num, is_buggy, bf_sha FROM " + table_name + " WHERE snapshot='" + ss_name + "'")
    results = list(cur.fetchall())
    ss_bug_data = pandas.DataFrame(results, columns = ['file_name', 'line_num', 'is_buggy', 'bf_sha'], dtype='object')

    # pandas DataFrame containing the locations for all instances in this snapshot
    ss_instance_locations_df = instance_locations_data[instance_locations_data.snapshot==ss_name]
    c_cpp_file_names = ss_instance_locations_df.file_name.unique()
    ss_instance_bugdata = []
    for c_cpp_file_name in c_cpp_file_names:
        node_types = ['do', 'while', 'for', 'if', 'else', 'switch']
        file_bug_data = ss_bug_data[ss_bug_data.file_name == c_cpp_file_name]
        for nt in node_types:
            # `instances` of `nt` in `c_cpp_file_names` in `ss_name`...
            # ...is just a list of start_linum and end_linum couples
            instances_df = ss_instance_locations_df[(ss_instance_locations_df.file_name==c_cpp_file_name) \
                                                    & (ss_instance_locations_df.node_type==nt)][['start_linum', 'end_linum']]
            instances = [(int(start), int(end)) for index, start, end in instances_df.itertuples()]
            for start_linum, end_linum in instances:
                # Record bug data for this particular instance
                instance_bug_data = file_bug_data[(file_bug_data.line_num >= start_linum) \
                                              & (file_bug_data.line_num <= end_linum) \
                                              & (file_bug_data.is_buggy == 1)]
                num_of_buggy_lines = len(instance_bug_data.index)
                num_of_total_lines = end_linum - start_linum + 1
                frac_of_buggy_lines = 1.0*num_of_buggy_lines/num_of_total_lines
                num_of_bugs = len(instance_bug_data.bf_sha.unique())

                # Record bug data for all instances in this snapshot in `ss_instance_bugdata`
                # ...we will later merge `ss_instance_bugdata` with `ss_instance_locations_df`
                ss_instance_bugdata.append([getProperFilepath(c_cpp_file_name), nt,
                                            str(start_linum), str(end_linum),
                                            str(num_of_buggy_lines), str(num_of_total_lines),
                                            str(frac_of_buggy_lines), str(num_of_bugs)])

    # Join `ss_instance_bugdata` and `ss_instance_locations_df`
    colnames = ['file_name', 'node_type', 'start_linum', 'end_linum', 'num_buggy_lines', 'num_total_lines', 'frac_buggy_lines', 'num_distinct_bugs']
    ss_instance_bugdata_df = pandas.DataFrame(ss_instance_bugdata, columns=colnames, dtype='object')
    joined_df = pandas.merge(ss_instance_locations_df, ss_instance_bugdata_df, on=['file_name', 'node_type', 'start_linum', 'end_linum'])
    ss_instance_data_file_path = out_data_dir + ss_name + '.csv'
    ss_instance_locs_data_file_path = out_data_dir + ss_name + '.locs.csv'
    joined_df.to_csv(ss_instance_data_file_path, mode='wb', index=False)

    # ss_instance_locations_df.to_csv(ss_instance_locs_data_file_path, mode='wb')
    # with open(out_data_dir + ss_name + '.bug.csv', 'wb') as ss_instance_data_file: 
    #     csv_writer = csv.writer(ss_instance_data_file)
    #     header = ['project', 'snapshot', 'file_name', 'node_type',
    #               'start_linum', 'end_linum',
    #               'num_buggy_lines', 'num_total_lines',
    #               'frac_buggy_lines', 'num_distinct_bugs']
    #     csv_writer.writerow(header)
    #     csv_writer.writerows(ss_instance_bugdata)

    if con:
        con.close()
#--------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("Error! Invalid args to get_nodetype_instance_data_process_ss.py. Aborting this snapshot.")
    
    print('Processing ' + sys.argv[1] + ':' + sys.argv[2])
    get_instance_data_for_ss(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print("Instance data collected for snapshot " + sys.argv[2] + "\n") # sys.argv[1] is ss_name

#--------------------------------------------------------------------------------------------------------------------------

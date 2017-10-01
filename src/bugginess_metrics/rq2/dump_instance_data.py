import os, sys, psycopg2, csv, pandas

#--------------------------------------------------------------------------------------------------------------------------
def printUsage():
    '''
    Usage: python dump_instance_data.py <path_to_data_dir>
                                        <project_name>

    E.g.:  python get_instances_of_AST_nodes.py data/ bitcoin
    '''
    print(printUsage.__doc__)

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
        printUsage()
        raise ValueError('Insufficient arguments provided to the script.')

    data_dir = sys.argv[1] + '/'
    project_name = sys.argv[2]
    instance_data_dir = data_dir + 'ast_node_instances/' +  project_name + '/'
    csv_file_names = [filename for filename in os.listdir(instance_data_dir) if filename.endswith('.csv')]
    csv_file_names.sort()
    csv_file_paths = [instance_data_dir + csv_file_name for csv_file_name in csv_file_names]
    
    # PostgreSQL table names cannot have hyphens, apparently
    table_name = "instance_data." + project_name
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
                                                      node_type varchar(15), \
                                                      start_linum integer, \
                                                      end_linum integer, \
                                                      id text, \
                                                      method text, \
                                                      method_count integer, \
                                                      num_buggy_lines integer, \
                                                      num_total_lines integer, \
                                                      frac_buggy_lines float, \
                                                      num_distinct_bugs integer)')
        
        SQL_STATEMENT = """COPY %s FROM STDIN WITH
                               CSV
                               HEADER
                               DELIMITER AS ','
                        """
    
        for csv_file_path in csv_file_paths:
            with open(csv_file_path, 'rb') as csv_file:
                cur.copy_expert(sql=SQL_STATEMENT % table_name, file=csv_file)
                con.commit()
        
    except Exception as e:
        if con:
            con.rollback()
        raise
    
    finally:
        if con:
            con.close()

#--------------------------------------------------------------------------------------------------------------------------

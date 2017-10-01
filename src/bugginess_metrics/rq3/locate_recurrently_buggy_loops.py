#--------------------------------------------------------------------------------------------------------------------------
import os, sys, pandas, psycopg2

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python locate_recurrently_buggy_loops.py <data_dir> <project_name>')
        raise ValueError('Error! Project name not given. Insufficient args.')

    data_root = sys.argv[1]
    project_name = sys.argv[2]
    outfile_name = data_root + '/ast_node_instances/' + project_name + '.loops.bugdata.csv'
    table_name = 'instance_data.' + project_name 
    table_name = table_name.replace('-', '_')

    con = psycopg2.connect(user='saheel', database='saheel')
    cur = con.cursor()

    node_types = ['for', 'while', 'do']

    dfs = []
    for nt in node_types:
        query = """
                SELECT foo.file_name, foo.method, foo.id, AVG(num_total_lines), SUM(num_distinct_bugs) 
                FROM """ + table_name + """ AS foo, 
                     (SELECT file_name, method 
                      FROM (SELECT DISTINCT file_name, method, method_count 
                            FROM """ + table_name + """ 
                            WHERE node_type='""" + nt + """' 
                            GROUP BY file_name, method, method_count) AS tmp 
                      GROUP BY file_name, method 
                      HAVING COUNT(*) = 1) AS bar 
                WHERE foo.node_type='""" + nt + """' 
                      AND foo.file_name = bar.file_name 
                      AND foo.method = bar.method 
                GROUP BY foo.file_name, foo.method, foo.id
                """
        cur.execute(query)
        res = list(cur.fetchall())

        cols = ['file_name', 'method', 'id', 'avg_loc', 'num_overall_bugs']
        df = pandas.DataFrame(res, columns=cols)
        df['node_type'] = [nt]*len(df.file_name)
        dfs.append(df)

    recurrently_buggy_loops_data = pandas.concat(dfs)
    with open(outfile_name, 'wb') as outfile:
        recurrently_buggy_loops_data.to_csv(outfile, index=False)

    if con:
        con.close()

#--------------------------------------------------------------------------------------------------------------------------
        # # Following code between the START and END tags tells what percentage of loops are 'trackable'
        # # Code kept for record purposes
        # # <START>
        # cols = ['file_name', 'method', 'id']
        # cur.execute("select distinct file_name, method, id from instance_data." + project_name + " where node_type='" + nt + "' and num_distinct_bugs>0")
        # res = list(cur.fetchall())
        # foo = pandas.DataFrame(res, columns=cols)
        
        # cols2 = ['snapshot', 'file_name', 'method', 'id', 'method_count', 'num_distinct_bugs']
        # cur.execute("select snapshot, file_name, method, id, method_count, num_distinct_bugs from instance_data." + project_name + " where node_type='" + nt + "'")
        # res = list(cur.fetchall())
        # bar = pandas.DataFrame(res, columns=cols2)
    
        # same = 0
        # diff = 0
        # for index, a, b, c in foo.itertuples():
        #     bar_data = bar[(bar.file_name==a) & (bar.method==b) & (bar.id==c)]
        #     counts_len = len(set(bar_data.method_count))
        #     if counts_len == 1:
        #         same += 1
        #     else:
        #         diff += 1
        
        # if (same+diff) != 0:
        #     print((nt, same, diff, 100.0*same/(same+diff)))
        # else:
        #     print((nt, same, diff))
        # # <END>
#--------------------------------------------------------------------------------------------------------------------------

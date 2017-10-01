#----------------------------------------------------------------------------------
import os, sys, shutil
from shlex import split as format_cmd
from subprocess import Popen, PIPE, STDOUT, call

#----------------------------------------------------------------------------------
def printPopenOutput(process):
    stdout, stderr = process.communicate()
    if stdout:
        sys.stdout.write(stdout)

    if stderr:
        sys.stderr.write(stderr)

#----------------------------------------------------------------------------------
def printUsage():
    '''
Usage: python main.py <path_to_output_data_dir> 
                      <project_name> 
                      <github_clone_url> 
                      <project_language>
                      <interval_between_ss_in_months> 
                      <num_of_parallel_cores>
                      [--steps <N1> <N2> <N3>...]

If the optional `--steps` arg is provided, the numbers after `--steps` indicate steps that will be executed.
If `--steps` is not provided, all the steps will be executed. Your options for those numbers are:
    
    1. Clone the latest version of given project
    2. Dump the snapshots (aka snapshot data)
    3. Dump the history of all commit changes
    4. Get list of bug-fixing commits
    5. Extract bug data (SZZ)
    6. Store CSV files with bug data into SQL tables
    7. Generate ASTs and parse them for type data
    8. Gather extracted AST-type data into CSV files
    9. Store CSV files with AST-type data into SQL tables
    10. Merge bugdata and typedata tables to get bug_typedata table
    11. Calculate bugginess of each AST node type using the bug_typedata
    12. Add 'Nesting Depth' column to bug_typedata tables
    13. Locate instances of each AST nodetype
    14. Collect data for the located AST nodetype instances
    15. Plot Lorenz Curves for nodetype instances for each snapshot
    16. Dump the CSV files with nodetype instance into Postgres
    17. Identify distinct loops and get bug data on recurrently buggy ones
        
For example: python main.py data/ libgit2 https://github.com/libgit2/libgit2.git c 3 16 --steps 1 2 3 4 5
Above command will generate CSV files with bug data for the libgit2 project.

Another example: python main.py data/ bitcoin https://github.com/bitcoin/bitcoin.git cpp 3 16 --steps 5 6 7 8
Above command will generate CSV files with bug data, CSV files with type data, dump all of them in PostgreSQL, and merge the dumped tables. 
It will NOT modify the snapshots and history of commit changes

    '''
    print(printUsage.__doc__)

#----------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) == 7:
        all_steps = True
        options = []
    elif len(sys.argv) < 7:
        printUsage()
        raise ValueError('7 or more args expected. ' + str(len(sys.argv) - 1) + ' given.')
    elif len(sys.argv) > 7 and not sys.argv[7] == '--steps':
        printUsage()
        raise ValueError('Expected arg `--steps` not given.')
    else:
        all_steps = False
        options = sys.argv[8:]
        for option in options:
            if not option.isdigit():
                printUsage()
                raise ValueError('Args after `--steps` must be numeric. Please try again.')

    data_root_path = os.path.abspath(sys.argv[1])
    if not os.path.isdir(data_root_path):
        os.mkdir(data_root_path)
    project_name = sys.argv[2]
    git_url = sys.argv[3]
    language = sys.argv[4]
    num_of_intervals = sys.argv[5]
    num_of_cores = sys.argv[6]

    # Relevant directories to store our data
    projects_dir = data_root_path + '/projects/'
    project_dir = projects_dir + project_name + '/'

    ss_dir = data_root_path + '/snapshots/'
    project_ss_dir = ss_dir + project_name + '/'

    ss_c_cpp_dir = data_root_path + '/snapshots_c_cpp/'
    project_ss_c_cpp_dir = ss_c_cpp_dir + project_name + '/'

    ss_srcml_dir = data_root_path + '/snapshots_srcml/'
    project_ss_srcml_dir = ss_srcml_dir + project_name + '/'

    corpus_dir = data_root_path + '/corpus/'
    project_corpus_dir = corpus_dir + project_name + '/'

    bf_shas_dir = data_root_path + '/bf_shas/'
    project_bf_shas_file_path = bf_shas_dir + project_name
    
    entropy_results_dir = data_root_path + '/entropy_results/'
    project_entropy_results_dir = entropy_results_dir + project_name + '/'

    ast_node_bugginess_results_dir = data_root_path + '/ast_node_bugginess_results/'

    # TODO parse output of each command for error string

#----------------------------------------------------------------------------------
    if '1' in options or all_steps:
        # 1. Clone the latest version of given project
        msg = '---------------------------------------------------- '
        msg += '1. Clone the latest version of given project '
        msg += '----------------------------------------------------\n'
        print(msg)

        cmd = format_cmd('mkdir -p ' + projects_dir)
        call(cmd)
    
        cmd = format_cmd('rm -rf ' + project_dir)
        call(cmd)
    
        cmd = format_cmd('mkdir -p ' + project_dir)
        call(cmd)
    
        cmd = format_cmd('git clone ' + git_url + ' ' + project_dir)
        call(cmd)
    
#----------------------------------------------------------------------------------
    if '2' in options or all_steps:
        # 2. Dump the snapshots
        msg = '---------------------------------------------------- '
        msg += '2. Dump the snapshots '
        msg += '----------------------------------------------------'
        print(msg)
                
        cmd = format_cmd('python src/generate_snapshot_data/get_snapshot_data.py ' + data_root_path + ' ' + language + ' ' \
                          + project_name + ' dump ' + num_of_intervals)
        call(cmd)

#----------------------------------------------------------------------------------
    if '3' in options or all_steps:
        # 3. Dump the history of all commit changes
        msg = '---------------------------------------------------- '
        msg += '3. Dump the history of all commit changes '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/generate_snapshot_data/get_snapshot_data.py ' + data_root_path + ' ' + language + ' ' \
                          + project_name + ' run ' + num_of_intervals)
        call(cmd)

#----------------------------------------------------------------------------------
    if '4' in options or all_steps:
        # 4. Get list of bug-fixing commits from PostgreSQL
        msg = '---------------------------------------------------- '
        msg += '4. Get list of bug-fixing commits from PostgreSQL '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('mkdir -p ' + bf_shas_dir)
        call(cmd)
    
        cmd = format_cmd('python src/szz/get_list_of_bugfix_SHAs.py ' + project_name + ' ' \
                          + project_bf_shas_file_path)
        call(cmd)
    
#----------------------------------------------------------------------------------
    if '5' in options or all_steps:
        # 5. Run SZZ
        msg = '---------------------------------------------------- '
        msg += '5. Run SZZ to get bug data '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/szz/szz.py ' + project_corpus_dir + ' ' \
                          + project_ss_dir + ' ' + project_bf_shas_file_path + ' ' + num_of_cores)
        call(cmd)
    
#----------------------------------------------------------------------------------
    if '6' in options or all_steps:
        # 6. Dump the CSV files with bug data into PostgreSQL tables
        msg = '---------------------------------------------------- '
        msg += '6. Dump the CSV files with bug data into PostgreSQL tables '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/szz/dump_bugdata_into_psql_table.py '
                          + data_root_path + ' ' + project_name)
        call(cmd)
        
#----------------------------------------------------------------------------------
    if '7' in options or all_steps:
        # 7. Generate AST-type data
        msg = '---------------------------------------------------- '
        msg += '7. Generate AST-type data '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/generate_asts_and_type_data/generate_typedata.py ' \
                          + project_name + ' ' + data_root_path + ' bin/src2srcml ' + num_of_cores)
        call(cmd)
        
#----------------------------------------------------------------------------------
    if '8' in options or all_steps:
        # 8. Gather generated AST-type data into CSV files
        msg = '---------------------------------------------------- '
        msg += '8. Gather generated AST-type data into CSV files '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/generate_asts_and_type_data/gather_typedata_into_csv.py ' \
                          + data_root_path + ' ' + project_name)
        call(cmd)
        
#----------------------------------------------------------------------------------
    if '9' in options or all_steps:
        # 9. Dump the CSV files with AST-type data into PostgreSQL tables
        msg = '---------------------------------------------------- '
        msg += '9. Dump AST-type data into PostgreSQL '
        msg += '----------------------------------------------------'
        print(msg)

        for item in ['new', 'old', 'learn', 'ss']:
            cmd = format_cmd('python src/generate_asts_and_type_data/dump_csv_into_table.py ' \
                             + project_corpus_dir + '/' + item + '_typedata.csv ' + project_name + ' ' + item)
            call(cmd)
              
#----------------------------------------------------------------------------------
    if '10' in options or all_steps:
        # 10. Merge bugdata table with typedata table to get bug_typedata table
        msg = '---------------------------------------------------- '
        msg += '10. Merge bugdata table with typedata table to get bug_typedata table '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/szz/merge_ss_bugdata_and_typedata.py ' + data_root_path + ' ' + project_name)
        call(cmd)
    
#----------------------------------------------------------------------------------
    if '11' in options or all_steps:
        # 11. Calculate defect density of each AST node type using the bug_typedata dumped above
        msg = '---------------------------------------------------- '
        msg += '11. Calculate defect density of each AST node type '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('mkdir -p ' + ast_node_bugginess_results_dir)
        call(cmd)
    
        cmd = format_cmd('python src/bugginess_metrics/calc_defect_density_per_nodetype.py ' + data_root_path + ' ' + project_name)
        call(cmd)

#----------------------------------------------------------------------------------
    if '12' in options or all_steps:
        # 12. Add Nesting Depth column to bug_typedata tables
        msg = '---------------------------------------------------- '
        msg += '12. Add Nesting Depth column to bug_typedata tables '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/manipulate_sql_tables/add_depth_to_BT_table.py ' + project_name)
        call(cmd)
#----------------------------------------------------------------------------------
    if '13' in options or all_steps:
        # 13. Locate instances of each AST nodetype
        msg = '---------------------------------------------------- '
        msg += '13. Locate instances of each AST nodetype '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/bugginess_metrics/rq2/locate_nodetype_instances.py ' + data_root_path + ' ' + project_name)
        call(cmd)
#----------------------------------------------------------------------------------
    if '14' in options or all_steps:
        # 14. Collect data for the located AST nodetype instances
        msg = '---------------------------------------------------- '
        msg += '14. Collect data for the located AST nodetype instances '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/bugginess_metrics/rq2/get_nodetype_instance_data.py ' \
                         + data_root_path + ' ' + project_name + ' ' + num_of_cores)
        call(cmd)
#----------------------------------------------------------------------------------
    if '15' in options or all_steps:
        # 15. Plot Lorenz Curves for nodetype instances for each snapshot
        msg = '---------------------------------------------------- '
        msg += '15. Plot Lorenz Curves for nodetype instances for each snapshot '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('Rscript src/bugginess_metrics/rq2/plot_lorenz_curves.r ' \
                         + data_root_path + ' ' + project_name)
        call(cmd)
#----------------------------------------------------------------------------------
    if '16' in options or all_steps:
        # 16. Dump the CSV files with nodetype instance into Postgres
        msg = '---------------------------------------------------- '
        msg += '16. Dump the CSV files with nodetype instance into Postgres '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/bugginess_metrics/rq2/dump_instance_data.py ' \
                         + data_root_path + ' ' + project_name)
        call(cmd)
#----------------------------------------------------------------------------------
    if '17' in options or all_steps:
        # 17. Identify distinct loops and get bug data on recurrently buggy ones
        msg = '---------------------------------------------------- '
        msg += '17. Identify distinct loops and get bug data on recurrently buggy ones '
        msg += '----------------------------------------------------'
        print(msg)

        cmd = format_cmd('python src/bugginess_metrics/rq3/locate_recurrently_buggy_loops.py ' \
                         + data_root_path + ' ' + project_name)
        call(cmd)
#----------------------------------------------------------------------------------
    # if '18' in options or all_steps:
    #     # 18. Plot Lorenz curve for ALL buggy loops
    #     msg = '---------------------------------------------------- '
    #     msg += '18. Plot Lorenz curve for ALL buggy loops '
    #     msg += '----------------------------------------------------'
    #     print(msg)

    #     cmd = format_cmd('Rscript src/bugginess_metrics/rq3/plot_lorenz_curve.r ' \
    #                      + data_root_path + ' ' + project_name)
    #     call(cmd)
#----------------------------------------------------------------------------------
    msg = '---------------------------------------------------- '
    msg += 'main.py DONE for ' + project_name + ' '
    msg += '----------------------------------------------------'
    print(msg)


#----------------------------------------------------------------------------------

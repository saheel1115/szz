#--------------------------------------------------------------------------------------------------------------------------
import os, sys, pickle, shlex, pandas
from subprocess import Popen, PIPE, STDOUT, call
from multiprocessing.dummy import Pool

#--------------------------------------------------------------------------------------------------------------------------
def printUsage():
    '''
    Usage: python calc_defect_density_per_nodetype_instance.py <path_to_data_dir>
                                                               <project_name>
                                                               <num_of_parallelizable_cores>

    E.g.:  python get_instances_of_AST_nodes.py data/ bitcoin 16
    '''
    print(printUsage.__doc__)

#--------------------------------------------------------------------------------------------------------------------------
def call_cmd(cmd):
    return call(cmd, close_fds=True)

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 4:
        printUsage()
        raise ValueError('Insufficient args provided.')

    data_dir = sys.argv[1] + '/'
    if not os.path.isdir(data_dir):
        raise ValueError('Given path to data directory is invalid. I was given:\n' + data_dir + '\n')

    project_name = sys.argv[2]
    num_of_cores = int(sys.argv[3])
    
    # nt = AST node type, viz. `for`, `if`, `switch`, etc.
    ast_nt = 'for'
    out_data_dir = data_dir + '/ast_node_instances/' + project_name + '/'
    if not os.path.isdir(out_data_dir):
        os.mkdir(out_data_dir)

    # TODO get ss_names via query to instance locations table
    data_file_path = data_dir + 'ast_node_instances/' + project_name + '.locations.csv'
    colnames = ['project', 'snapshot', 'file_name', 'node_type', 'start_linum', 'end_linum', 'id', 'method', 'method_count']
    data = pandas.read_csv(data_file_path, names=colnames, header=None)
    ss_names = data.snapshot.unique()
    del data

    # Wait for processes to complete
    pool = Pool(num_of_cores)
    processes = []
    cmds = []
    ss_names.sort()
    for ss_name in ss_names: # skip last snapshot since we do not have bug data for it
        process_ss_cmd = "python src/bugginess_metrics/rq2/get_nodetype_instance_data_process_ss.py " \
                         + project_name  + ' ' \
                         + ss_name + ' ' \
                         + data_file_path + ' ' \
                         + out_data_dir
        cmds.append(shlex.split(process_ss_cmd))

    return_codes = pool.map(call_cmd, cmds)
    print('get_nodetype_instance_data.py for ' + project_name + ' DONE!')
#--------------------------------------------------------------------------------------------------------------------------

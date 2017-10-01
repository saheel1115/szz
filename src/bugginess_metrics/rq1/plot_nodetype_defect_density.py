#-------------------------------------------------------------------------------
import os, sys, pickle
import matplotlib as mpl
mpl.use('agg')
import pylab

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print('Expecting 1 argument.')
        print('Usage: python plot_ast_node_bugginess.py <path_to_results_dir>')
        print('Sample usage: python plot_ast_node_bugginess.py data/ast_node_bugginess_results/')
        raise ValueError

    results_dir = sys.argv[1]
    result_file_names = os.listdir(results_dir)
    result_file_paths = [results_dir + '/' + result_file_name for result_file_name in result_file_names]
    result_files = [open(result_file_path, 'rb') for result_file_path in
                    result_file_paths if '.data' in result_file_path]

    parent_types = ['do', 'while', 'for', 'if', 'else', 'switch', 'function']
    parent_type_bugginess_values = {}
    for parent_type in parent_types:
        parent_type_bugginess_values[parent_type] = []

    for result_file in result_files:
        result = pickle.load(result_file)
        result_file.close()
        for parent_type in parent_types:
            parent_type_bugginess_values[parent_type].append(result[parent_type])
        
    # A list of lists, each of which represents values for one parent_type
    data_to_plot = []
    for parent_type in parent_types:
        data_to_plot.append(parent_type_bugginess_values[parent_type])

    pylab.boxplot(data_to_plot)
    pylab.xticks(range(1, len(parent_types) + 1), parent_types)
    pylab.ylim(-0.01, 0.04)
    pylab.ylabel('#BuggyLOC/#TotalLOC avg over snaps')
    pylab.xlabel('AST Node Type')
    pylab.savefig(results_dir + 'boxplot.png', bbox_inches='tight')

#-------------------------------------------------------------------------------

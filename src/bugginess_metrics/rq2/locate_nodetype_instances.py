#--------------------------------------------------------------------------------------------------------------------------
from __future__ import generators
import os, sys, ntpath, re, csv
from lxml import etree
from collections import defaultdict

#--------------------------------------------------------------------------------------------------------------------------
# ********************************* Some global variables ********************************* 
node_types = ['do', 'while', 'for', 'if', 'else', 'switch']
srcml_tags = {'do': '{http://www.sdml.info/srcML/src}do',
              'while': '{http://www.sdml.info/srcML/src}while',
              'for': '{http://www.sdml.info/srcML/src}for',
              'if': '{http://www.sdml.info/srcML/src}if',
              'else': '{http://www.sdml.info/srcML/src}else',
              'switch': '{http://www.sdml.info/srcML/src}switch',
              'root': '{http://www.sdml.info/srcML/src}root',
              'function': '{http://www.sdml.info/srcML/src}function'}
err_count = 0
total_count = 0

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
def printUsage():
    '''
    Usage: python get_instances_of_AST_nodes.py <path_to_data_dir>
                                                <project_name>

    E.g.:  python get_instances_of_AST_nodes.py data/ bitcoin
    '''
    print(printUsage.__doc__)

#--------------------------------------------------------------------------------------------------------------------------
def getStartTagLineNums(iterator):
    start_tag_line_nums = {}
    for nt in node_types:
        start_tag_line_nums[nt] = []
    for node in iterator:
        for nt in node_types:
            if node.tag.endswith('src}' + nt):
                start_tag_line_nums[nt].append(node.sourceline - 1)
                break
    return start_tag_line_nums

#--------------------------------------------------------------------------------------------------------------------------
def getEndTagLineNums(srcml_file_path):
    srcml_file_lines = [line.strip() for line in open(srcml_file_path, 'r').readlines()]
    end_tag_line_nums = {}
    for nt in node_types:
        end_tag_line_nums[nt] = []
    for index, line in enumerate(srcml_file_lines):
        for nt in node_types:
            num_of_end_tags_on_this_line = re.findall('</' + nt + '>', line)
            end_tag_line_nums[nt].extend([index]*len(num_of_end_tags_on_this_line))

    return end_tag_line_nums

#--------------------------------------------------------------------------------------------------------------------------
def addToRows(rows, project_name, ss_name, c_cpp_file_name, nt,
              method_inst_starts, method_inst_ends, instance_ids,
              method_name, method_instances_count):
    # Instead of calling append() on `rows` N times, we call append() on...
    # ...`temp_rows` N times followed by 1 extend() on `rows`
    # Because `rows` can be huge, we want to avoid multiple edits to it
    temp_rows = []
    for index, method_inst_start in enumerate(method_inst_starts):
        temp_rows.append((project_name, ss_name, c_cpp_file_name, nt,
                          str(method_inst_start), str(method_inst_ends[index]), str(instance_ids[index]),
                          method_name, str(method_instances_count)))

    rows.extend(temp_rows)

#--------------------------------------------------------------------------------------------------------------------------
def getStartEndNTMatches(start_tag_line_nums, end_tag_line_nums):
    matches = []
    if len(start_tag_line_nums) != len(end_tag_line_nums):
        print('Error! #start_tags != #end_tags')
        return []

    if len(start_tag_line_nums) == 1:
        matches.append((start_tag_line_nums[0], end_tag_line_nums[0]))
    elif len(start_tag_line_nums) > 1:
        open_instances = [start_tag_line_nums[0], start_tag_line_nums[1]]
        curr_start_tag_index = 1
        curr_end_tag_index = 0
        while curr_end_tag_index < len(end_tag_line_nums):
            if end_tag_line_nums[curr_end_tag_index] < open_instances[-1]:
                matches.append((open_instances[-2], end_tag_line_nums[curr_end_tag_index]))
                curr_end_tag_index += 1
                open_instances.pop(-2)
            elif curr_start_tag_index == len(start_tag_line_nums) - 1:
                open_instances.reverse()
                for start_tag_line_num in open_instances:
                    matches.append((start_tag_line_num, end_tag_line_nums[curr_end_tag_index]))
                    curr_end_tag_index += 1
            else:
                curr_start_tag_index += 1
                open_instances.append(start_tag_line_nums[curr_start_tag_index])

    matches.sort()
    return matches

#--------------------------------------------------------------------------------------------------------------------------
def getInstanceIDs(instance_depths):
    # Stores the number of instances found at each depth, pre-initialized to 0
    depth_counts = defaultdict(int) 

    IDs = []
    for depth in instance_depths:
        depth_counts[depth] += 1

        id = []
        for i in range(1, depth + 1):
            id.append(str(depth_counts[i]))

        IDs.append('.'.join(id))
    
    return IDs

#--------------------------------------------------------------------------------------------------------------------------
def parseMethod(method_elem, nt):
    instance_starts = []
    method_instances = []
    instance_depths = []

    prev_action = 'start'
    curr_depth = 0
    context = etree.iterwalk(method_elem, events=('start', 'end'), tag=srcml_tags[nt])
    for action, elem in context:
        if action == 'start':
            instance_starts.append(elem.sourceline - 1)
            method_instances.append(elem)
            if prev_action == 'start':
                curr_depth += 1
            instance_depths.append(curr_depth)

        elif action == 'end':
            if prev_action == 'end':
                curr_depth -= 1

        prev_action = action

    return (method_instances, instance_starts, instance_depths)

#--------------------------------------------------------------------------------------------------------------------------
def getMethodInstanceEnds(method_elem, nt, srcml_file_path):
    instance_ends = []
    next_elem = method_elem.getnext()
    if next_elem is not None:
        method_start = method_elem.sourceline
        method_end_approx = next_elem.sourceline
        srcml_file_lines = [line.strip() for line in open(srcml_file_path, 'r').readlines()]
        method_lines = srcml_file_lines[(method_start - 1):method_end_approx]
        for index, line in enumerate(method_lines):
            num_of_end_tags_on_this_line = re.findall('</' + nt + '>', line)
            instance_ends.extend([index + method_start - 1]*len(num_of_end_tags_on_this_line))
        
    return instance_ends
    
#--------------------------------------------------------------------------------------------------------------------------
def getEnclosingMethod(nt_elem):
    # Get the `function` AST node (and the function name)...
    # ...in which this instance resides 
    method_found = False
    method_elem = None
    method_name = ''
    for parent in nt_elem.iterancestors():
        if parent.tag.endswith('src}function') \
           or parent.tag.endswith('src}constructor') \
           or parent.tag.endswith('src}destructor'):
            method_elem = parent
            method_found = True
            break
        elif parent.tag.endswith('src}macro'):
            method_elem = parent
            method_found = True

    if method_found:
        # Function nodes have <type> as 1st child and <name> as 2nd child.
        # Constructor and Destructor nodes have no <type> child, thus <name> is their 1st child.
        # <name> node itself may have some children.
        if method_elem.tag.endswith('src}function'): 
            method_name_child = method_elem[1]
        else:
            method_name_child = method_elem[0] 

        # Get method_name
        if method_name_child.text: method_name += method_name_child.text
        for child in method_name_child.getchildren():
            if child.text: method_name += child.text
            if child.tail: method_name += child.tail
    
    return (method_elem, method_name)
#--------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # ******************************* Initialization/Error-checking **********************************
    if len(sys.argv) != 3:
        printUsage()
        raise ValueError('Insufficient args provided.')

    data_dir = sys.argv[1] + '/'
    if not os.path.isdir(data_dir):
        raise ValueError('Given path to data directory is invalid. I was given:\n' + data_dir + '\n')

    project_name = sys.argv[2]
    srcml_project_dir = data_dir + '/snapshots_srcml/' + project_name + '/'
    if not os.path.isdir(srcml_project_dir):
        raise ValueError('Inferred path to snapshots_srcml directory is invalid. I have:\n' + srcml_project_dir + '\n')

    c_cpp_project_dir = data_dir + '/snapshots_c_cpp/' + project_name + '/'
    if not os.path.isdir(c_cpp_project_dir):
        raise ValueError('Inferred path to snapshots_srcml directory is invalid. I have:\n' + srcml_project_dir + '\n')

    ss_names = os.listdir(srcml_project_dir)
    ss_names.sort()

    ss_srcml_dirs = [srcml_project_dir + name + '/' for name in ss_names if os.path.isdir(srcml_project_dir + name)]
    ss_c_cpp_dirs = [c_cpp_project_dir + name + '/' for name in ss_names if os.path.isdir(c_cpp_project_dir + name)]
    if len(ss_srcml_dirs) != len(ss_c_cpp_dirs):
        raise ValueError('Different number of directories found in' \
                         ' snapshots_srcml and snapshots_c_cpp directories. Aborting!')

    # ******************************* Parsing each file in each snapshot **********************************
    # TODO Mention algo here
    rows = []
    print('\nLocating instances of each block-level AST nodetype for:')
    for ss_index, ss_name in enumerate(ss_names):
        print(project_name + ' -- ' + ss_name)

        c_cpp_file_names = [each for each in os.listdir(ss_c_cpp_dirs[ss_index])]
        c_cpp_file_names.sort()

        for c_cpp_file_name in c_cpp_file_names:
            # print(c_cpp_file_name)
            if 'test' in c_cpp_file_name or 'tests' in c_cpp_file_name:
                continue
            srcml_file_name = c_cpp_file_name + '.xml'
            srcml_file_path = ss_srcml_dirs[ss_index] + srcml_file_name

            if not os.path.isfile(srcml_file_path):
                continue
            
            p = etree.XMLParser(huge_tree=True)
            tree = etree.parse(srcml_file_path, parser=p)
            iterator = tree.iter()
            next(iterator)      # to skip the xmlns header

            instance_starts_forall_nt = getStartTagLineNums(iterator)
            instance_ends_forall_nt = getEndTagLineNums(srcml_file_path)
            matches = {}
            for nt in node_types:
                matches[nt] = getStartEndNTMatches(instance_starts_forall_nt[nt], \
                                                   instance_ends_forall_nt[nt]) 

            for nt in node_types:
                nt_instances_parsed = []
                nt_instances = tree.findall('//' + srcml_tags[nt])
                for nt_instance in nt_instances:
                    if nt_instance not in nt_instances_parsed:
                        method_elem, method_name = getEnclosingMethod(nt_instance)
                        # TODO handle nt==function instances separately?
                        if method_elem == None:
                            # TODO do we handle the case when method_elem is returned None?
                            # ...this happens about 1% times when the parent is a macro,
                            # ...or src2srcml AST-generator fails magnificently 
                            total_count += 1
                            err_count += 1
                            # print(ss_name, c_cpp_file_name, nt, nt_instance.sourceline)
                            continue

                        method_instances, \
                            method_inst_starts, \
                            instance_depths = parseMethod(method_elem, nt)
                        total_count += len(method_inst_starts)

                        start_indices = [instance_starts_forall_nt[nt].index(start_linum) \
                                         for start_linum in method_inst_starts]
                        method_inst_ends = [instance_ends_forall_nt[nt][start_index] \
                                              for start_index in start_indices]

                        instance_ids = getInstanceIDs(instance_depths)
                        method_instances_count = len(method_instances)

                        nt_instances_parsed.extend(method_instances)
                        addToRows(rows, project_name, ss_name, getProperFilepath(c_cpp_file_name), nt,
                                  method_inst_starts, method_inst_ends, instance_ids,
                                  method_name, method_instances_count)

    print(str(err_count) + '/' + str(total_count) + ' = ' +
          str(err_count*100.0/total_count) + '% instances were skipped due to errors.')

    # ******************************* Writing output to CSV file **********************************
    outfile_path = data_dir + '/ast_node_instances/' + project_name + '.locations.csv'
    print('Writing output to ' + outfile_path)
    with open(outfile_path, 'wb') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerows(rows)

    print('locate_nodetype_instances.py for ' + project_name + ' Done!')

#--------------------------------------------------------------------------------------------------------------------------

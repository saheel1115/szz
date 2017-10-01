"""
This module contains the `parseSrcmlForTypedata` function

The `parseSrcmlForTypedata` function takes a srcML file `srcML_file_name` as input and for each line in the file extracts its parent's nodetype and 'depth' in the AST. Output is written to `srcML_file_name.data` in the specified `out_dir` directory. Run `pydoc path/to/parseSrcmlForTypedata.py` for more info.

See the docs for `printUsage` function for usage information.
"""
# -------------------------------------------------------------------------------------------
from __future__ import generators
from lxml import etree
from pprint import pprint
import os, sys, re, pickle

# -------------------------------------------------------------------------------------------
def printUsage():
    """Usage: python parseSrcmlForTypedata <path_to_srcML_file>"""
    print(printUsage.__doc__)

def KnuthMorrisPratt(text, pattern):
    '''
    Helper function. Performs Knuth-Morris-Pratt string matching and yields all starting positions of copies of the `pattern` in the `text`. 

    Calling conventions are similar to string.find, but its arguments can be lists or iterators, not just strings, it returns all matches, not just the first one, and it does not need the whole text in memory at once. Whenever it yields, it will have read the text exactly up to and including the match that caused the yield.

    By: David Eppstein, UC Irvine, 1 Mar 2002
    From: http://code.activestate.com/recipes/117214/
    '''
    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos-shift]:
            shift += shifts[pos-shift]
        shifts[pos+1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos
# -------------------------------------------------------------------------------------------
def parseSrcmlForTypedata(srcML_file_path):
    """For each line in `srcML_file_path`, this function extracts its parent's nodetype and 'depth' in the AST. This typedata is written to `srcML_file_path.data`.

    Run `pydoc path/to/parseSrcmlForTypedata.py` for more info.

    Args
    ----
    srcML_file_path: string
        Path to the srcML file to be processed
        
    Returns
    -------
    None, if something goes wrong; True, otherwise
    """
    if not os.path.isfile(srcML_file_path):
        print(printUsage.__doc__)
        return

    # -------------------------------------------------------------------------------------------
    parent_types = ['do', 'while', 'for', 'if', 'else', 'switch', 'root', 'function', 'error', 'block']

    # NOTE: 'label' and 'macro' could have been parent_type; I chose not to have them as such
    # NOTE: Comments have 'root' as their parent
    # NOTE: The parent 'block' refers to block expressions about which we don't have sufficient information
    #       For ex. they may be macro-expanded function blocks, but since macros are not expanded in srcML,
    #           we don't have this info. Thus, we simply put them in 'block' category
    
    get_line_parents_type_dict = {'src}unit'        : 'root',
                                  'src}asm'         : 'asm',
                                  'src}do'          : 'do',
                                  'src}for'         : 'for',
                                  'src}if'          : 'if',
                                  # 'src}then'      : 'if',
                                  'src}else'        : 'else',
                                  'src}switch'      : 'switch',
                                  'src}while'       : 'while',
                                  'src}function'    : 'function',
                                  'src}catch'       : 'error',
                                  'src}throw'       : 'error',
                                  'src}try'         : 'error'
                                  # 'src}block'       : 'block'
    }
    
    # -------------------------------------------------------------------------------------------
    line_types = ['do', 'while', 'for', 'if', 'else', 'macro', 'switch', 'decl', 'others', 'none', 'function', 'error', 'expr-call', 'expr-assign', 'expr-others', 'continue', 'break', 'return', 'goto']
    
    get_line_type_dict = {'src}asm'                 : 'decl',
                          'src}block'               : 'block',
                          'src}break'               : 'break',
                          'src}case'                : 'switch',
                          'src}comment'             : 'none',
                          # 'src}condition'           : '',
                          # 'src}constraint'          : '',
                          'src}continue'            : 'continue',
                          'src}decl'                : 'decl',
                          'src}decl_stmt'           : 'decl',
                          'src}default'             : 'switch',
                          'src}do'                  : 'do',
                          'src}else'                : 'else',
                          'src}empty_stmt'          : 'none',
                          'src}enum'                : 'decl',
                          # 'src}expr'                : '',
                          'src}expr_stmt'           : '',
                          'src}extern'              : 'decl',
                          'src}for'                 : 'for',
                          'src}goto'                : 'goto',
                          'src}if'                  : 'if',
                          # 'src}incr'                : '',
                          # 'src}index'               : '',
                          # 'src}init'                : '',
                          'src}label'               : 'others',
                          'src}macro'               : 'macro',
                          # 'src}name'                : '',
                          'src}namespace'           : 'others',
                          'src}range'               : 'others',
                          'src}requires'            : 'others',
                          'src}switch'              : 'switch',
                          'src}template'            : 'decl',
                          'src}then'                : 'if',
                          # 'src}type'                : '',
                          'src}typedef'             : 'decl',
                          'src}using'               : 'others',
                          'src}while'               : 'while',
                          'src}elseif'              : 'else',
                          # 'src}argument'            : '',
                          # 'src}argument_list'       : '',
                          'src}call'                : 'expr-call',
                          'src}function'            : 'function',
                          'src}function_decl'       : 'decl',
                          # 'src}param'               : '',
                          # 'src}parameter_list'      : '',
                          'src}return'              : 'return',
                          # 'src}specifier'           : '',
                          # 'src}lambda'              : '',
                          'src}class'               : 'others',
                          'src}class_decl'          : 'decl',
                          'src}constructor'         : 'others',
                          'src}constructor_decl'    : 'decl',
                          'src}destructor'          : 'others',
                          'src}destructor_decl'     : 'decl',
                          'src}friend'              : 'others',
                          # 'src}member_list'         : '',
                          'src}private'             : 'others',
                          'src}protected'           : 'others',
                          'src}public'              : 'others',
                          'src}super'               : 'others',
                          'src}struct'              : 'others',
                          'src}struct_decl'         : 'decl',
                          'src}union'               : 'others',
                          'src}union_decl'          : 'decl',
                          'src}catch'               : 'error',
                          'src}throw'               : 'error',
                          'src}throws'              : 'error',
                          'src}try'                 : 'error',
                          'cpp}define'              : 'macro',
                          'cpp}directive'           : 'macro',
                          'cpp}elif'                : 'macro',
                          'cpp}endif'               : 'macro',
                          'cpp}error'               : 'macro',
                          'cpp}file'                : 'macro',
                          'cpp}if'                  : 'macro',
                          'cpp}else'                : 'macro',
                          'cpp}ifdef'               : 'macro',
                          'cpp}ifndef'              : 'macro',
                          'cpp}include'             : 'macro',
                          'cpp}line'                : 'macro',
                          'cpp}pragma'              : 'macro',
                          'cpp}undef'               : 'macro',
                          'cpp}number'              : 'macro',
                          'cpp}pragma'              : 'macro',
                          'cpp}region'              : 'macro',
                          'cpp}endregion'           : 'macro',
                          'cpp}macro'               : 'macro',
                          'cpp}value'               : 'macro',
                          # 'src}decltype'            : 'macro'
                          # 'typename'                : ''
                          'src}escape'              : 'others'
    }
    
    # -------------------------------------------------------------------------------------------
    srcML_file_handle = open(srcML_file_path, 'r')
    srcML_file_lines = [line[:-1] for line in srcML_file_handle.readlines()]
    
    len_C_file = len(srcML_file_lines) - 2 # AST file has 2 additional lines; here, we want the number of LOC in the C file 
    srcML_file_handle.close()
    
    # Dictionary of type of each line...
    #   each line has exactly one type
    line_type_dict = {}
    for i in range(1, len_C_file + 1):
        line_type_dict[i] = ''
    
    # Dictionary of parents of each line...
    #   each line has a list of parents
    line_parents_type_dict = {}
    for i in range(1, len_C_file + 1):
        line_parents_type_dict[i] = []
    # -------------------------------------------------------------------------------------------
    # Get type for each line. Read the comments below for high-level algo and other implementation quirks.
    
    p = etree.XMLParser(huge_tree=True)
    tree = etree.parse(srcML_file_path, parser=p)
    iterator = tree.iter()
    
    # To skip the <?xml version=...> and <unit ...> nodes 
    next(iterator)                  
    line_num = 2
    
    # Iterate over all the start nodes in the XML file
    for node in iterator:
        # This condition makes sure we only check the nodes that occur at the beggining of each line...
        #   because those are the ones that determine the type of the line (most of the times, anyway)
        if node.sourceline >= line_num:
            line_num = node.sourceline + 1
    
            # Algo for finding the type for a given line:
            #   First, classify the expr_stmts as expr-assign, expr-call, and expr-others
            #   Else, look-up the tag in line_type_dict to get the type for the line
            #   Else, go up the ancestors till you get a match in the line_type_dict
            tag = node.tag.split('/')[4]
            if tag == 'src}expr_stmt':
                if re.search('[^=]=[^=]', srcML_file_lines[node.sourceline - 1]):
                    line_type_dict[node.sourceline - 1] = 'expr-assign'
                elif '<call>' in srcML_file_lines[node.sourceline - 1]:
                    line_type_dict[node.sourceline - 1] = 'expr-call'
                else:
                    line_type_dict[node.sourceline - 1] = 'expr-others'
            elif tag in get_line_type_dict.keys():
                line_type_dict[node.sourceline - 1] = get_line_type_dict[tag]
            else:
                # This _mostly_ indicates that this line belongs to a broken statement...
                #   i.e. statement for which developers decided to use > 1 lines in the code
                # Thus we will have to look up in this node's ancestors to get this line's type
                # For example:
                #     mctx.input.tip_context = (eflags & REG_NOTBOL) ? CONTEXT_BEGBUF
                #                              : CONTEXT_NEWLINE | CONTEXT_BEGBUF; (<---- 
                #                                                                        \
                #                         this is the line we are examining right now ----
                for ancestor in node.iterancestors():
                    if ancestor.tag.split('/')[4] == 'src}expr_stmt':
                        if re.search('[^=]=[^=]', srcML_file_lines[ancestor.sourceline - 1]):
                            line_type_dict[node.sourceline - 1] = 'expr-assign'
                        elif '<call>' in srcML_file_lines[ancestor.sourceline - 1]:
                            line_type_dict[node.sourceline - 1] = 'expr-call'
                        else:
                            line_type_dict[node.sourceline - 1] = 'expr-others'
                        break
                    elif ancestor.tag.split('/')[4] in get_line_type_dict.keys():
                        line_type_dict[node.sourceline - 1] = get_line_type_dict[ancestor.tag.split('/')[4]]
                        break
    
            # This condition should not occur actually, since by now the type should've been assigned
            #   but anyway, just put it in 'others' for now and throw a warning
            if line_type_dict[node.sourceline - 1] == '':
                print('Woah! Check why line #' + str(node.sourceline) + ' in file ' + srcML_file_path + ' is being assigned type "others"')
                print('\nPlease notify Saheel!\n')
                line_type_dict[node.sourceline - 1] = 'others'
            
            # Now, we will find the parents of each line i.e. all the block-level statements that contain this line
            # The different types of block-level statements are listed in parent_types
            # For lines that don't have an XML node on them, parents are recorded below
            for ancestor in node.iterancestors():
                if ancestor.tag.split('/')[4] in get_line_parents_type_dict.keys():
                    parent = get_line_parents_type_dict[ancestor.tag.split('/')[4]]
                    try:
                        line_parents_type_dict[node.sourceline - 1].append(parent)
                    except:
                        # Whenever a C file ends with a macro, the XML file is only 1 line shorter than the C file (otherwise it is 2 lines shorter)...
                        #   resulting in a KeyError
                        # This discrepancy happens in < 1% of the files, so no big deal. We handle it simply by adding another key to the dict.
                        line_parents_type_dict[node.sourceline - 1] = [parent]
    
    # -------------------------------------------------------------------------------------------
    # Now, we have to assign types (and parents) to those lines that didn't have a start node
    # These can be end-of-block lines, comments, or empty lines
    
    unaccounted_line_nums = [line_num for line_num in line_type_dict.keys() if line_type_dict[line_num] == '']
    for unaccounted_line_num in unaccounted_line_nums:
        # First, try to match for end-of-block lines and assign a type accordingly.
        end_tags = re.findall("</[a-zA-Z]*>", srcML_file_lines[unaccounted_line_num]) # result is a list
        if len(end_tags) >= 1:
            for end_tag in end_tags:
                end_tag = end_tag[2:-1]
                if line_type_dict[unaccounted_line_num] == '' and 'src}' + end_tag in get_line_type_dict.keys():
                    line_type_dict[unaccounted_line_num] = get_line_type_dict['src}' + end_tag]
    
                # Simultaneously, also record its parents (which gets a little hacky -- see below)
                if 'src}' + end_tag in get_line_parents_type_dict.keys():
                    line_parents_type_dict[unaccounted_line_num].append(get_line_parents_type_dict['src}' + end_tag])
    
            # A hack for handling lines with only ending tags, e.g. "</block></switch>"
            # -- in these cases, we look at the parents of the previous line 
            # -- and add some of them to the parents of this line
            index = 0
            if not line_parents_type_dict[unaccounted_line_num] == []:
                for temp in KnuthMorrisPratt(line_parents_type_dict[unaccounted_line_num - 1], line_parents_type_dict[unaccounted_line_num]):
                    index = temp
                    break
            line_parents_type_dict[unaccounted_line_num] = line_parents_type_dict[unaccounted_line_num - 1][index:]
    
        # Else, it's a comment or empty line -- in both cases, its type is 'none'
        else:
            line_type_dict[unaccounted_line_num] = 'none'
            line_parents_type_dict[unaccounted_line_num] = ['root']
            
    # -------------------------------------------------------------------------------------------
    # We need to clean up some 'else if' stuff in line_parents_type_dict
    for key in line_parents_type_dict.keys():
        indices = [i + 1 for i, x in enumerate(line_parents_type_dict[key]) if x == 'else'] 
        line_parents_type_dict[key][:] = [ item for i, item in enumerate(line_parents_type_dict[key]) if i not in indices ]
    # -------------------------------------------------------------------------------------------
    # # Uncomment these lines for some output
    # pprint(line_type_dict)
    # pprint(line_parents_type_dict)
    
    fout = open(srcML_file_path + '.data', 'wb')
    pickle.dump(line_type_dict, fout)
    pickle.dump(line_parents_type_dict, fout)
    fout.close()
    return True

# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('\nIncorrect number of args given.')
        print(printUsage.__doc__)
    else:
        if not parseSrcmlForTypedata(sys.argv[1]):
            print("Something went wrong in the call to `parseSrcmlForTypedata`...")
# -------------------------------------------------------------------------------------------

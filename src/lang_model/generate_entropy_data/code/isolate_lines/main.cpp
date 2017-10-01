#include <iostream>

#include "suggestion.h"

using namespace std;

string copy_right = "\n\
=========================================================\n\
Author: Zhaopeng Tu\n\
 Email: tuzhaopeng@gmail.com\n\
  Date: 2013-11-18\n\
  Note: A Caching LM-based Code Suggestion Tool V0.3\n\
=========================================================\n";

string help_info = "\n\
you should enter the following parameters:\n\
the necessary parameters: \n\
---------------------------------------------------------------\n\
 -INPUT_FILE  \t\t the input file\n\
 -NGRAM_FILE  \t\t the ngrams file\n\
 -NGRAM_ORDER \t\t the value of N (order of lm)\n\
---------------------------------------------------------------\n\
\n\
the optional parameters:\n\
---------------------------------------------------------------\n\
-ENTROPY      \t\t calculate the cross entropy of the test file\n\
              \t\t rather than providing the suggestions\n\
-TEST         \t\t test mode, no output, no debug information\n\
-FILES        \t\t test on files or not, default on a single file\n\
-DEBUG        \t\t output debug information\n\
-OUTPUT_FILE  \t\t the output file\n\
---------------------------------------------------------------\n\
-BACKOFF      \t\t use the back-off technique\n\
-CACHE        \t\t use the cache technique \n\
              \t\t (types: WINDOW_CACHE, SCOPE_CACHE)\n\
              \t\t (default is cache window of 1000 words)\n\
-CACHE_ONLY   \t\t only use the cache technique without ngrams\n\
-CACHE_ORDER  \t\t the maximum order of ngrams used in the cache (default: 3)\n\
-CACHE_MIN_ORDER  \t\t the minimum order of ngrams used in the cache (default: 3)\n\
-CACHE_SMOOTH  \t  use smoothing technique for cache probability estimation\n\
-CACHE_DYNAMIC_LAMBDA \t dynamic interpolation weight for -cache (H/(H+1)), default option\n\
-CACHE_LAMBDA \t\t interpolation weight for -CACHE\n\
-WINDOW_CACHE \t\t build the cache on a window of n tokens (default n=1000)\n\
-WINDOW_SIZE  \t\t the size of cache, default: 1000 tokens\n\
-FILE_CACHE  \t\t build the cache on a file or related files\n\
-SCOPE_FILE   \t\t the scope file for scope cache on TYPE or METHOD\n\
-RELATED_FILE \t\t when using cache on file scope, build the cache on the related files\n\
              \t\t FILE_DIR should be given\n\
-FILE_DIR     \t\t the directory that stores all files\n\
-REST_FILE    \t\t when using cache on file scope, build the cache on the rest files\n\
              \t\t except the curret test file\n\
-MAINTENANCE  \t\t maintenance mode, build cache on the current file except the current line\n\
-SUFFIX       \t\t use suffix (tokens after) rather than the prefix (tokens before) \n\
---------------------------------------------------------------\n\
-TYPE        \t\t use the class model that exploits type information\n\
-TYPE_FILE   \t\t the type file\n\
-TYPE_CACHE  \t\t use the cache technique for the choice of words given a type\n\
-LEXEME_CACHE      \t\t use the cache built on the lexemes (diff from -CACHE for type model)\n\
-TYPE_CACHE_ONLY   \t\t only use the type cache technique without type file\n\
-TYPE_CACHE_LAMBDA \t\t interpolation weight for -type_cache, default value: 0.5\n\
-TYPE_CACHE_DYNAMIC_LAMBDA \t dynamic interpolation weight for -type_cache (H/(H+1)),\n\
                           \t if not set, the weight of type_cache will be default value 0.5\n\
---------------------------------------------------------------\n\
";
//-FILE_CACHE_TYPE \t the type of scope cache (FILE, TYPE, or METHOD)\n\
//-FILE_CACHE_TYPE \t the type of scope cache (FILE, TYPE, or METHOD)\n\


int main(int argc, const char* argv[])
{
    cout << copy_right << endl;
    
    if (argc < 9)
    {
        cerr << "read parameters err, please check your parameter list" << endl;
        cout << help_info << endl;
        return 1;
    }

    if (!Data::ReadConfig(argc, argv))
    {
        cout << help_info << endl;
        return 1;
    }

    cout << "here" << endl;

    Suggestion suggestion;
    suggestion.Process();
        
	return 0;
}


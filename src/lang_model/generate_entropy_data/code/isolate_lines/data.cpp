#include "data.h"

//the necessary parameters
string Data::INPUT_FILE;
string Data::NGRAM_FILE;
string Data::OUTPUT_FILE;
int Data::NGRAM_ORDER = 3;

//the optional parameters
bool Data::TEST = false;
bool Data::FILES = false;
bool Data::ENTROPY = false;

bool Data::USE_BACKOFF = false;
bool Data::USE_CACHE = false;
int Data::CACHE_ORDER = 10;
bool Data::USE_WINDOW_CACHE = false;
int Data::WINDOW_SIZE = 1000;
bool Data::USE_FILE_CACHE = false;
string Data::SCOPE_FILE;
bool Data::USE_RELATED_FILE=false;
string Data::FILE_DIR;
bool Data::USE_REST_FILE=false;
float Data::CACHE_LAMBDA = 0.0;
bool Data::CACHE_DYNAMIC_LAMBDA = false;
bool Data::CACHE_SMOOTH = false;
bool Data::USE_CACHE_ONLY = false;
int Data::CACHE_MIN_ORDER = 3;

int Data::BEAM_SIZE=10;

bool Data::DEBUG = false;
bool Data::MAINTENANCE = false;
bool Data::SUFFIX = false;

bool Data::USE_TYPE = false;
string Data::TYPE_FILE;
bool Data::USE_TYPE_CACHE = false;
bool Data::USE_TYPE_CACHE_ONLY = false;
float Data::TYPE_CACHE_LAMBDA = 0.5;
bool Data::TYPE_CACHE_DYNAMIC_LAMBDA = false;
bool Data::USE_LEXEME_CACHE = false;

Ngram* Data::NGRAM;
Cache Data::CACHE;
Cache Data::LEXEME_CACHE;
Type* Data::TYPE;
TypeCache Data::TYPE_CACHE;


bool Data::ReadConfig(const int &argc, const char* argv[])
{ 
	int i = 1;
    string scope_cache_type;

	while (i < argc)
	{
        if (strcmp(argv[i], "-INPUT_FILE") == 0)
        {
            INPUT_FILE = argv[i+1];
            i += 2;
        }
        else if (strcmp(argv[i], "-NGRAM_FILE") == 0)
        {
            NGRAM_FILE = argv[i+1];
            i += 2;
        }
        else if (strcmp(argv[i], "-NGRAM_ORDER") == 0)
        {
            NGRAM_ORDER = atoi(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-OUTPUT_FILE") == 0)
        {
            OUTPUT_FILE = argv[i+1];
            i += 2;
        }
        else if (strcmp(argv[i], "-BACKOFF") == 0)
        {
            USE_BACKOFF = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-TEST") == 0)
        {
            TEST = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-FILES") == 0)
        {
            FILES = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-ENTROPY") == 0)
        {
            ENTROPY = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-CACHE") == 0)
        {
            USE_CACHE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-CACHE_ORDER") == 0)
        {
            CACHE_ORDER = atoi(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-CACHE_MIN_ORDER") == 0)
        {
            CACHE_MIN_ORDER = atoi(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-CACHE_ONLY") == 0)
        {
            USE_CACHE_ONLY = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-WINDOW_CACHE") == 0)
        {
            USE_WINDOW_CACHE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-WINDOW_SIZE") == 0)
        {
            WINDOW_SIZE = atoi(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-FILE_CACHE") == 0)
        {
            USE_FILE_CACHE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-RELATED_FILE") == 0)
        {
            USE_RELATED_FILE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-FILE_DIR") == 0)
        {
            FILE_DIR = argv[i+1]; 
            i += 2;
        }
        else if (strcmp(argv[i], "-REST_FILE") == 0)
        {
            USE_REST_FILE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-SCOPE_FILE") == 0)
        {
            SCOPE_FILE = argv[i+1]; 
            i += 2;
        }
        else if (strcmp(argv[i], "-CACHE_LAMBDA") == 0)
        {
            CACHE_LAMBDA = atof(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-CACHE_DYNAMIC_LAMBDA") == 0)
        {
            CACHE_DYNAMIC_LAMBDA = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-CACHE_SMOOTH") == 0)
        {
            CACHE_SMOOTH = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-TYPE") == 0)
        {
            USE_TYPE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-TYPE_FILE") == 0)
        {
            TYPE_FILE = argv[i+1];
            i += 2;
        }
        else if (strcmp(argv[i], "-TYPE_CACHE") == 0)
        {
            USE_TYPE_CACHE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-LEXEME_CACHE") == 0)
        {
            USE_LEXEME_CACHE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-TYPE_CACHE_ONLY") == 0)
        {
            USE_TYPE_CACHE_ONLY = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-TYPE_CACHE_LAMBDA") == 0)
        {
            TYPE_CACHE_LAMBDA = atof(argv[i+1]);
            i += 2;
        }
        else if (strcmp(argv[i], "-TYPE_CACHE_DYNAMIC_LAMBDA") == 0)
        {
            TYPE_CACHE_DYNAMIC_LAMBDA = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-DEBUG") == 0)
        {
            DEBUG = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-MAINTENANCE") == 0)
        {
            MAINTENANCE = true;
            i += 1;
        }
        else if (strcmp(argv[i], "-SUFFIX") == 0)
        {
            SUFFIX = true;
            i += 1;
        }
        else
        {
            cerr << "read parameters err, please check your parameter list" << endl;
            cerr << "wrong parameter: " << argv[i] << endl;
            return false;
        }
	}


    if (!Check())
    {
        cerr << "Cannot pass the parameters" << endl;
        return false;
    }

    Show();
   
    // loading ngrams
    if (ENTROPY)
    {
        NGRAM = new Ngram(NGRAM_FILE, NGRAM_ORDER);
    }
    else
    {
        NGRAM = new Ngram(NGRAM_FILE, NGRAM_ORDER, BEAM_SIZE);
    }
    // CACHE.SetMinOrder(NGRAM_ORDER < CACHE_ORDER? NGRAM_ORDER : CACHE_ORDER);
    CACHE.SetMinOrder(CACHE_MIN_ORDER);
    LEXEME_CACHE.SetMinOrder(CACHE_MIN_ORDER);

    CACHE.SetSmooth(CACHE_SMOOTH, NGRAM_ORDER);
    
    if (USE_TYPE)
    {
        if (TYPE_FILE.empty())
        {
            cerr << "TYPE FILE not given" << endl;
            return false;
        }

        TYPE = new Type(TYPE_FILE, BEAM_SIZE*2);

        TYPE_CACHE.SetBeamSize(BEAM_SIZE);
    }

    return true;
}

bool Data::Check()
{
    if (INPUT_FILE == "" || NGRAM_FILE == "" || NGRAM_ORDER == 0)
    {
        cerr << "At least one of the necessary options is not given." << endl;
        return false;
    }

    if (OUTPUT_FILE == "")
    {
        TEST = true;
    }

    if (TEST)
    {
        DEBUG = false;
    }

    if (USE_WINDOW_CACHE && USE_FILE_CACHE)
    {
        cerr << "you can use only kind of cache: window cache or scope cache" << endl;
        return false;
    }
    
    /*
    2013-12-17  delete this for lexeme cache on type model
    if (USE_CACHE_ONLY || USE_WINDOW_CACHE || USE_FILE_CACHE)
    {
        USE_CACHE = true;
    }
    */
    if (MAINTENANCE || SUFFIX)
    {
        USE_FILE_CACHE = true;
    }

    if (USE_TYPE_CACHE_ONLY)
    {
        USE_TYPE_CACHE = true;
        USE_CACHE = true;
        USE_RELATED_FILE = false;
        USE_TYPE = false;
        USE_TYPE_CACHE = false;
        USE_LEXEME_CACHE = false;
    }

    if (USE_TYPE_CACHE)
    {
        USE_TYPE = true;
    }

    if (USE_TYPE_CACHE && !USE_TYPE_CACHE_ONLY)
    {    
        if (TYPE_FILE.empty())
        {
            cerr << "type file should be given when you use type cache." << endl;
            cerr << "if you use the option '-USE_TYPE_CACHE_ONLY'), it can be absent." << endl;
            return false;
        }

    }

    if (USE_CACHE)
    {
        if (!(USE_WINDOW_CACHE || USE_FILE_CACHE ))
        {
            // USE_WINDOW_CACHE = true;
            USE_FILE_CACHE = true;
        }
    }

    if (!CACHE_DYNAMIC_LAMBDA && CACHE_LAMBDA < 0.000001)
    {
        CACHE_DYNAMIC_LAMBDA = true;
    }

    if (USE_RELATED_FILE)
    {    
        /*
        if (!USE_FILE_CACHE)
        {
            cerr << "related files are only available when you use scope cache on file" << endl;
            return false;
        }
        */

        if (FILE_DIR.empty())
        {
            cerr << "file directory should be given when you build file cache on related files" << endl;
            return false;
        }

        if (SCOPE_FILE.empty())
        {
            cerr << "scope file should be given when you use scope cache" << endl;
            return false;
        }

    }
    
    /*
    if (USE_REST_FILE)
    {
        if (!USE_FILE_CACHE)
        {
            cerr << "rest files are only available when you use scope cache on file" << endl;
            return false;
        }
    }
    */

    if (USE_RELATED_FILE && USE_REST_FILE)
    {
        cerr << "you can use only kind of other files: related files or rest files" << endl;
        return false;
    }



    return true;
}

void Data::Show()
{
    cout << "Parameters:" << endl;
    cout << "Input File: " << INPUT_FILE << endl;
    cout << "Output File: " << OUTPUT_FILE << endl;
    cout << "Ngram File: " << NGRAM_FILE << "\t Order: " << NGRAM_ORDER << endl;
    cout << "Back-off: " << USE_BACKOFF << endl;
    cout << "Test Mode: " << TEST << endl;
    cout << "Test on Files: " << FILES << endl;
    cout << "Type Information: ";
    if (USE_TYPE)
    {   
        cout << TYPE_FILE;
        cout << "\t Interpolation weight: ";
        if (TYPE_CACHE_DYNAMIC_LAMBDA)
        {
            cout << "DYNAMIC" << endl;
        }
        else
        {
            cout << CACHE_LAMBDA << endl;
        }
        cout << "Lexeme Cache: " << USE_LEXEME_CACHE << endl;
    }
    else
    {
        cout << USE_TYPE << endl;
    }


    if (ENTROPY)
    {
        cout << "Entropy Mode" << endl;
    }
    cout << "Cache: " << USE_CACHE << ", Order: " << CACHE_ORDER << ", Minimum Order: " << CACHE_MIN_ORDER <<  ", " << endl;
    if (USE_CACHE)
    {
        if (USE_WINDOW_CACHE)
        {
            cout << "WINDOW CACHE";
        }
        else
        {
            cout << "FILE CACHE";
            if (!SCOPE_FILE.empty())
            {
                cout << ", RELATED_FILE: " << USE_RELATED_FILE;
                if (USE_REST_FILE)
                {
                    cout << ", Scope file: " << SCOPE_FILE;
                }
                // cout << ", REST_FILE: " << USE_REST_FILE;
            }
        }

        cout << ", Smooth: " << CACHE_SMOOTH << ", Interpolation weight: ";
        if (CACHE_DYNAMIC_LAMBDA)
        {
            cout << "DYNAMIC" << endl;
        }
        else
        {
            cout << CACHE_LAMBDA << endl;
        }
    }
    else
    {
        cout << endl;
    }

    cout << "Debug: " << DEBUG << endl;
    cout << "\n\n" << endl;

}

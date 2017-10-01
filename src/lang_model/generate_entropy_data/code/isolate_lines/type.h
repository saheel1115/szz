#ifndef __CLASS_H__
#define __CLASS_H__
#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>

#include "utility.h"
#include "ngram.h"

using namespace std;

class Type
{
public:	
    /**
    * update the cache with the record (type_name, token)
    * @param type_name  the previous (n-1) tokens
    * @param token    the current token
    **/
    Type(const string& typeFile, const int beam_size)
    {
        ifstream fin(typeFile.c_str());
        /**
        
        the type file is in the following format:
        type_name  token   prob

        **/

        cout << "=================================================" << endl;
        cout << "Reading type-vocabulary dictionary..." << endl;

        string line;
        vector<string> items;
        vector<Word> words;
        string type_name, last_type_name;
        while (getline(fin, line))
        {
            Split(line, "\t", items);
            type_name = items.at(0);

            Word word;
            word.m_token = items.at(1);
            word.m_prob = atof(items.at(2).c_str());

            if (type_name == last_type_name)
            {
                words.push_back(word);
            }
            else
            {
                if (!words.empty())
                {
                   // sort the words according to their probabilities
                   sort(words.rbegin(), words.rend());
                   if ((int)words.size() > beam_size)
                   {
                       words.resize(beam_size);
                   }
                   m_words.insert(make_pair(last_type_name, words));
                }

                last_type_name = type_name;
                words.clear();
                words.push_back(word);
            }
        }

        if (!words.empty())
        {
           // sort the words according to their probabilities
           sort(words.rbegin(), words.rend());
           if ((int)words.size() > beam_size)
           {
               words.resize(beam_size);
           }
           m_words.insert(make_pair(last_type_name, words));
        }
    }

	bool GetCandidates(const string& type_name, vector<Word>& candidates)
    {
        candidates.clear();

        map<string, vector<Word> >::iterator iter = m_words.find(type_name);
        if (iter != m_words.end())
        {
            candidates = iter->second;
            return true;
        }
        else
        {
            return false;
        }
    }

private:
    // the map that contains the records given a (sequence) of type_name (e.g., Ci or Ci-2Ci-1Ci)
    // when using only the current type name, then the choice of word is independent from the context
    // which means that given a type name, the same choices are always made
    // this can be improved in the future
    map<string, vector<Word> > m_words;
};
#endif


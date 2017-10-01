#ifndef __CLASSCACHE_H__
#define __CLASSCACHE_H__
#include <list>

#include "cache.h"
#include "data.h"

using namespace std;

const int BEAM_SIZE = 20;

class TypeRecord:public Record
{
public:
    TypeRecord()
    {
        m_count = 0;
        m_beam_size = BEAM_SIZE;
    }

    TypeRecord(const int beam_size)
    {
        m_count = 0;
        m_beam_size = beam_size;
    }

    TypeRecord(const string& token)
    {
        m_count = 1;
        m_beam_size = BEAM_SIZE;
        m_recent_tokens.push_back(token);
    }

    TypeRecord(const int beam_size, const string& token)
    {
        m_count = 1;
        m_beam_size = beam_size;
        m_recent_tokens.push_back(token);
    }

    void Update(const string& token)
    {
        m_recent_tokens.push_back(token);

        if ((int)m_recent_tokens.size() > m_beam_size)
        {
            m_recent_tokens.pop_front();
        }

        m_count = (int)m_recent_tokens.size();
    }

    void GetTokenCounts(map<string, int>& token_counts)
    {
        list<string>::iterator iter;
        for (iter=m_recent_tokens.begin(); iter!=m_recent_tokens.end(); ++iter)
        {
            map<string, int>::iterator miter = token_counts.find(*iter);
            if (miter != token_counts.end())
            {
                miter->second += 1;
            }
            else
            {
                token_counts.insert(make_pair(*iter, 1));
            }
        }
    }
private:
    // new element of TypeRecord, only keep the latest BEAM_SIZE tokens for each class
    list<string> m_recent_tokens;
    int m_beam_size;
};


class TypeCache:public Cache
{
public:
    TypeCache()
    {
        m_beam_size = BEAM_SIZE;
    }

    void SetBeamSize(const int beam_size)
    {
        m_beam_size = beam_size;
    }

    void Build(const string& input_file)
    {
        ifstream fin(input_file.c_str());
        string line, token;

        vector<string> elems;

        while (getline(fin, line))
        {
            stringstream ss(line);

            while (ss >> token)
            {
                Split(token, "<=>", elems);

                Update(elems.at(0), elems.at(1));
            }
        }
    }

    /**
    * update the cache with the record (prefix, token)
    * @param prefix  the previous (n-1) tokens
    * @param token    the current token
    **/
    void Update(const string& prefix, const string& token)
    {
        map<string, TypeRecord>::iterator iter = m_records.find(prefix);
        if (iter != m_records.end())
        {
            iter->second.Update(token);
        }
        else
        {
            TypeRecord record(m_beam_size, token);
            m_records.insert(make_pair(prefix, record));
        }
    }

    void Clear()
    {
        m_records.clear();
    }

    void UpdateCandidates(const string& prefix, const float cache_lambda, const bool cache_dynamic_lambda, vector<Word>& candidates)
    {
        int cache_count = GetCount(prefix);
        if (cache_count != 0)
        {
            float cache_discount = cache_lambda;
            if (cache_dynamic_lambda)
            {
                //P(cnd) = 1/(cache_count+1)*P(lm) + cache_count/(cache_count+1)*P(cache)
                cache_discount = (float)cache_count/(cache_count+1);
            }
            float ngram_discount = 1-cache_discount;

            // found cache records of the prefix
            map<string, int> token_counts;
            GetTokenCounts(prefix, token_counts);

            // update the information of candidates get by the ngrams
            map<string, int>::iterator iter;
            for (int i=0; i<(int)candidates.size(); ++i)
            {
                // discount the probability first
                candidates.at(i).m_prob *= ngram_discount;

                iter = token_counts.find(candidates.at(i).m_token);
                if (iter != token_counts.end())
                {
                    candidates.at(i).m_prob += cache_discount * ((float)iter->second/cache_count);
                    candidates.at(i).m_debug += ", in cache: " + to_string1(iter->second) + "/" + to_string1(cache_count);
                    token_counts.erase(candidates.at(i).m_token);
                }
            }

            // add the left records in the cache to te candidates
            for (iter=token_counts.begin(); iter!=token_counts.end(); ++iter)
            {
                Word candidate(iter->first, cache_discount * ((float)iter->second/cache_count));
                candidate.m_debug += "only in cache: " + to_string1(iter->second) + "/" + to_string1(cache_count);
                candidates.push_back(candidate);
            }

            // sort the candidates, because the scores are changed
            sort(candidates.rbegin(), candidates.rend());
        }
    }

    void GetTokenCounts(const string& prefix, map<string, int>& token_counts)
    {
        token_counts.clear();

        map<string, TypeRecord>::iterator iter = m_records.find(prefix);
        if (iter != m_records.end())
        {
            iter->second.GetTokenCounts(token_counts);
        }
    }

    int GetCount(const string& prefix)
    {
        map<string, TypeRecord>::iterator iter = m_records.find(prefix);
        if (iter != m_records.end())
        {
            return iter->second.GetCount();
        }
        else
        {
            return 0;
        }
    }
private:
    // the map that contains the records given a prefix (e.g., wi-2 wi-1)
    map<string, TypeRecord> m_records;
    int m_beam_size;
};
#endif


#include "suggestion.h"

void Suggestion::Process()
{
    // initilize the statistics
    m_total_number = 0;
    m_mrr = 0.0;
    m_top1_correct = 0;
    m_top5_correct = 0;
    m_top10_correct = 0;
    m_total_prob = 0.0;

    if (Data::DEBUG)
    {
        m_fout.open(Data::OUTPUT_FILE.c_str());
    }

    if (Data::FILES)
    {
        DealFiles();
    }
    else
    {
        DealFile(Data::INPUT_FILE);
    }

    cout << "Total tokens: " << m_total_number << endl;
    if (Data::ENTROPY)
    {
        cout << "Entropy: " << -m_total_prob/m_total_number << endl;
    }
    else
    {
        cout << "Mean reciprocal rank: " << m_mrr/m_total_number << endl;
        cout << "Total top1 accuracy: " << (float)m_top1_correct/m_total_number << endl;
        cout << "Total top5 accuracy: " << (float)m_top5_correct/m_total_number << endl;
        cout << "Total top10 accuracy: " << (float)m_top10_correct/m_total_number << endl;
    }
}

void Suggestion::DealFiles()
{
    vector<string> input_files;
    ifstream fin(Data::INPUT_FILE.c_str());
    string line;
    while (getline(fin, line))
    {
        input_files.push_back(line);
    }
    fin.close();

    ifstream fin_list(Data::INPUT_FILE.c_str());

    ofstream fout_file_measures((Data::INPUT_FILE+".file.measures").c_str());

    ifstream fin_scope_list;
    if (Data::USE_RELATED_FILE)
    {
        fin_scope_list.open(Data::SCOPE_FILE.c_str());
    }

    string file_name;
    string scope_file_name;
    int count = 0;
    while (getline(fin_list, file_name))
    {
        ifstream fin(file_name.c_str());
        getline(fin_scope_list, scope_file_name);
        ReadScope(scope_file_name);

        if (Data::MAINTENANCE || Data::SUFFIX)
        {
            Data::CACHE.Build(file_name, Data::CACHE_ORDER, Data::USE_TYPE, false);
        }

        if (Data::USE_RELATED_FILE)
        {

            for (int i=0; i<(int)m_related_files.size(); ++i)
            {
                Data::CACHE.Build(Data::FILE_DIR + "/" + m_related_files.at(i), Data::CACHE_ORDER, Data::USE_TYPE, false);

                if (Data::USE_TYPE && Data::USE_LEXEME_CACHE)
                {
                    // build cache on the lexeme sequence for type model
                    Data::LEXEME_CACHE.Build(Data::FILE_DIR + "/" + m_related_files.at(i), Data::CACHE_ORDER, Data::USE_TYPE, true);
                }

                if (Data::USE_TYPE_CACHE)
                {
                    Data::TYPE_CACHE.Build(Data::FILE_DIR + "/" + m_related_files.at(i));
                }

                /*
                if (Data::DEBUG)
                {
                    cout << "related file: " << Data::FILE_DIR + "/" + m_related_files.at(i) << endl;
                    cout << "cache: " << Data::CACHE.m_records.size() << endl;
                }
                */
            }
        }
        /*
        else if (Data::USE_REST_FILE)
        {
            for (int i=0; i<(int)input_files.size(); ++i)
            {
                if (i != count)
                {
                    Data::CACHE.Build(input_files.at(i), Data::CACHE_ORDER, Data::USE_TYPE, true);

                    if (Data::USE_TYPE_CACHE)
                    {
                        Data::TYPE_CACHE.Build(Data::FILE_DIR + "/" + m_related_files.at(i));
                    }
                }
            }
        }
        */

        count += 1;

        DealFile(file_name);

        if (Data::USE_FILE_CACHE)
        {
            Data::CACHE.Clear();

            if (Data::USE_TYPE && Data::USE_LEXEME_CACHE)
            {
                Data::LEXEME_CACHE.Clear();
            }
        }

        Data::TYPE_CACHE.Clear();

        if (Data::ENTROPY)
        {
           fout_file_measures << file_name << "," << -m_file_prob/m_file_total_number << endl;
        }
        else
        {
            fout_file_measures << m_file_mrr/m_file_total_number << " ||| "
                               << (float)m_file_top1_correct/m_file_total_number << " ||| "
                               << (float)m_file_top5_correct/m_file_total_number << " ||| "
                               << (float)m_file_top10_correct/m_file_total_number << endl;
        }
    }

}

void Suggestion::DealFile(const string& input_file)
{
    // initilize the statistics for each file
    m_file_total_number = 0;
    m_file_mrr = 0.0;
    m_file_top1_correct = 0;
    m_file_top5_correct = 0;
    m_file_top10_correct = 0;
    m_file_prob = 0.0;

    ifstream fin(input_file.c_str());
    ofstream fout((input_file+".sentence.entropies").c_str());
    string line, item;
    int line_count = 0;

    while (getline(fin, line))
    {
        line_count += 1;
        vector<string> items;

        stringstream ss(line);

        while (ss >> item)
        {
            items.push_back(item);
        }

        vector<string> tokens;
        vector<string> lexemes;
        tokens.push_back("<s>");
        lexemes.push_back("<s>");

        for (int i=0; i<(int)items.size(); ++i)
        {
            if (Data::USE_TYPE)
            {
                vector<string> elems;
                Split(items.at(i), "<=>", elems);
                lexemes.push_back(elems.at(0));
                tokens.push_back(elems.at(1));
            }
            else
            {
                tokens.push_back(items.at(i));
                lexemes.push_back(items.at(i));
            }
        }


        // analysis the tokens
        // common usage
        string prefix, cache_prefix, lexeme_cache_prefix;
        string debug_info;
        int start;

        // for predicting task
        vector<Word> candidates;
        int rank;

        // for calculating the cross entropy
        float prob;
        float sentence_prob = 0.0;

        for (int i=1; i<(int)tokens.size(); i++)
        {
            start = i-(Data::NGRAM_ORDER-1)>0? i-(Data::NGRAM_ORDER-1) : 0;
            Join(tokens, start, i-1, prefix);

            /*
            cout << "prefix: ";
            if (i > 1)
            {
                cout << tokens.at(i-2) << " ";
            }
            cout << tokens.at(i-1) << ", token: " << tokens.at(i) << ", lexeme: " << lexemes.at(i) << endl;
            */

            if (Data::USE_CACHE)
            {
                // generate new prefix for cache
                start = i-(Data::CACHE_ORDER-1)>0 ? i-(Data::CACHE_ORDER-1) : 0;
                Join(tokens, start, i-1, cache_prefix);
            }

            if (Data::USE_TYPE && Data::USE_LEXEME_CACHE)
            {
                Join(lexemes, start, i-1, lexeme_cache_prefix);
            }

            // 2014-01-28 maintenance
            if (Data::MAINTENANCE || Data::SUFFIX)
            {
                Data::CACHE.Delete(cache_prefix, tokens.at(i));
            }

            if (Data::ENTROPY)
            {
                // to do next
                // add the cache of the type-lexeme cache
                prob = GetProbability(prefix, cache_prefix, tokens.at(i), debug_info);
                sentence_prob += prob;
                m_file_prob += prob;

                /*
                if (Data::DEBUG)
                {
                     m_fout << "<bead>" << endl;
                     m_fout << "<ref>" << lexemes.at(i) << "</ref>" << endl;
                     m_fout << "<type>" << tokens.at(i) << "</type>" << endl;
                     m_fout << "<prob>" << prob << " ||| " << debug_info << " </prob>" << endl;
                     m_fout << "</bead>" << endl;
                }
                */
            }
            else
            {
                GetCandidates(prefix, cache_prefix, candidates);

                if (Data::USE_TYPE)
                {
                    // the results stored in the candidates, now we need to get the lexemes
                    GetLexemes(candidates);
                }

                if (Data::USE_TYPE && Data::USE_LEXEME_CACHE)
                {
                    // update the candidates according to the lexeme cache
                    Data::LEXEME_CACHE.UpdateCandidates(lexeme_cache_prefix, Data::CACHE_LAMBDA, Data::CACHE_DYNAMIC_LAMBDA, candidates);
                    // Data::LEXEME_CACHE.UpdateCandidates(lexeme_cache_prefix, Data::CACHE_LAMBDA, true, candidates);
                }

                // for calcuting accuracy
                rank= GetRank(candidates, lexemes.at(i));
                if (rank > 0)
                {
                    m_file_mrr += 1/(float)rank;
                }
                m_file_top1_correct += Is_in(candidates, lexemes.at(i), 1);
                m_file_top5_correct += Is_in(candidates, lexemes.at(i), 5);
                m_file_top10_correct += Is_in(candidates, lexemes.at(i), 10);

                if (Data::DEBUG)
                {
                    m_fout << "<bead>" << endl;
                    m_fout << "<ref>" << lexemes.at(i) << "</ref>" << endl;
                    for (int j=0; j<(int)candidates.size(); j++)
                    {
                        m_fout << "<cand id=" << j+1 << "> "
                               << candidates.at(j).m_token << " ||| " << candidates.at(j).m_prob
                               << " ||| " << candidates.at(j).m_debug
                               << " </cand>" << endl;
                    }
                    m_fout << "</bead>" << endl;
                }
            }

            // 2014-01-28 maintenance
            if (Data::MAINTENANCE)
            {
                Data::CACHE.Update(cache_prefix, tokens.at(i));
            }

            // update the prefix cache
            if (Data::USE_CACHE && !(Data::MAINTENANCE || Data::SUFFIX))
            {
                // 2013-12-13
                // here, even for type model, we build cache on the tokens not on the lexemes
                // we can improve this later, then we will first get the lexemes and then update the caches in GetCandidates
                if (Data::USE_WINDOW_CACHE)
                {
                    Data::CACHE.Update(cache_prefix, tokens.at(i), Data::WINDOW_SIZE);
                }
                else
                {
                    Data::CACHE.Update(cache_prefix, tokens.at(i));
                }
            }

            if (Data::USE_TYPE && Data::USE_LEXEME_CACHE)
            {
                // 2013-12-17
                // add the caches built on the lexemes for type model
                if (Data::USE_WINDOW_CACHE)
                {
                    Data::LEXEME_CACHE.Update(lexeme_cache_prefix, lexemes.at(i), Data::WINDOW_SIZE);
                }
                else
                {
                    Data::LEXEME_CACHE.Update(lexeme_cache_prefix, lexemes.at(i));
                }
            }


            if (Data::USE_TYPE_CACHE)
            {
                Data::TYPE_CACHE.Update(tokens.at(i), lexemes.at(i));
            }
        }

        int num = (int)tokens.size() - 1;

        if (Data::ENTROPY && num > 0)
        {
            fout << line_count << "," << -sentence_prob/num << endl;
        }

        m_file_total_number += num;
    }

    m_total_number += m_file_total_number;

    if (Data::ENTROPY)
    {
        // calcuting the cross entropy
        m_total_prob += m_file_prob;
    }
    else
    {
        // calcuting accuracy
        m_mrr += m_file_mrr;
        m_top1_correct += m_file_top1_correct;
        m_top5_correct += m_file_top5_correct;
        m_top10_correct += m_file_top10_correct;
    }
}



void Suggestion::GetCandidates(const string& prefix,
                               const string& cache_prefix,
                               vector<Word>& candidates)
{
    if (!Data::USE_CACHE_ONLY)
    {
        // n-gram word candidates
        Data::NGRAM->GetCandidates(prefix, Data::USE_BACKOFF, candidates);
        if (Data::DEBUG)
        {
            for (int i=0; i<(int)candidates.size(); ++i)
            {
                candidates.at(i).m_debug = "ngram prob: " + to_string1(candidates.at(i).m_prob);
            }
        }
    }
    else
    {
        candidates.clear();
    }

    if (Data::USE_CACHE)
    {
        // update the candidates according to the cache
        Data::CACHE.UpdateCandidates(cache_prefix, Data::CACHE_LAMBDA, Data::CACHE_DYNAMIC_LAMBDA, candidates);
    }
}


void Suggestion::GetLexemes(vector<Word>& candidates)
{
    vector<Word> type_candidates = candidates;
    candidates.clear();

    vector<Word> lexeme_candidates;
    for (int i=0; i<(int)type_candidates.size(); ++i)
    {
        string current_type = type_candidates.at(i).m_token;

        if (!Data::USE_TYPE_CACHE_ONLY)
        {
            Data::TYPE->GetCandidates(current_type, lexeme_candidates);
        }

        if (Data::USE_TYPE_CACHE)
        {
            // update the candidates according to the type cache
            Data::TYPE_CACHE.UpdateCandidates(current_type, Data::TYPE_CACHE_LAMBDA, Data::TYPE_CACHE_DYNAMIC_LAMBDA, lexeme_candidates);
        }

        // update the probabilities of lexeme candidates by mutiplying the corresponding type probability
        for (int j=0; j<(int)lexeme_candidates.size(); ++j)
        {
            lexeme_candidates.at(j).m_prob *= type_candidates.at(i).m_prob;
            // add the lexeme candidates to the candidates
            candidates.push_back(lexeme_candidates.at(j));
        }
    }

    // sort the candidates
    sort(candidates.rbegin(), candidates.rend());
}


float Suggestion::GetProbability(const string& prefix,
                                 const string& cache_prefix,
                                 const string& token,
                                 string& debug_info)
{
    float prob = 0.0;
    debug_info.clear();

    if (!Data::USE_CACHE_ONLY)
    {
        prob = Data::NGRAM->GetProbability(prefix, token, Data::USE_BACKOFF);
        if (Data::DEBUG)
        {
            debug_info = "ngram prob: " + to_string1(pow(2, prob));
        }
    }

    if (Data::USE_CACHE)
    {
        int cache_count = Data::CACHE.GetCount(cache_prefix);
        if (cache_count != 0)
        {
            int valid_order = Data::CACHE.GetValidOrder(cache_prefix);
            float cache_discount = Data::CACHE_LAMBDA;
            if (valid_order > 2 && Data::CACHE_DYNAMIC_LAMBDA)
            {
                //P(cnd) = 1/(cache_count+1)*P(lm) + cache_count/(cache_count+1)*P(cache)
                cache_discount = (float)cache_count/(cache_count+1);
            }


            if (Data::CACHE_SMOOTH && Data::NGRAM_ORDER>1)
            {
                // smoothing discount
                float smooth_discount = 1.0;
                if (valid_order < Data::NGRAM_ORDER)
                {
                    for (int i=Data::NGRAM_ORDER; i>valid_order; i--)
                    {
                        smooth_discount *= (float)1/i;
                    }

                    if (valid_order > 1)
                    {
                        smooth_discount *= (float)(valid_order-1)/valid_order;
                    }
                }
                else
                {
                    smooth_discount *= (float)(Data::NGRAM_ORDER-1)/Data::NGRAM_ORDER;
                }

                cache_discount *= smooth_discount;
            }

            float ngram_discount = 1-cache_discount;

            int ngram_count = Data::CACHE.GetCount(cache_prefix, token);
            prob = ngram_discount * pow(2, prob) + cache_discount * ((float)ngram_count/cache_count);
            debug_info += ", in cache: " + to_string1(ngram_count) + "/" + to_string1(cache_count);

            if (prob > 0.0)
            {
                prob = log2(prob);
            }
            else
            {
                prob = Data::NGRAM->m_unk_prob;
            }
        }
    }

    return prob;
}


int Suggestion::GetRank(const vector<Word>& candidates, const string& ref)
{
    for (int i=0; i<(int)candidates.size(); i++)
    {
        if (candidates.at(i).m_token == ref)
        {
            return i+1;
        }
    }

    return 0;
}

int Suggestion::Is_in(const vector<Word>& candidates, const string& ref, const int top_n)
{
    int end = top_n < candidates.size() ? top_n : candidates.size();
    for (int i=0; i<end; i++)
    {
        if (candidates.at(i).m_token == ref)
        {
            return 1;
        }
    }

    return 0;
}

void Suggestion::ReadScope(const string& scope_file_name)
{
    m_class_scope_begins.clear();
    m_class_scope_ends.clear();
    m_method_scope_begins.clear();
    m_method_scope_ends.clear();
    m_related_files.clear();

    ifstream fin(scope_file_name.c_str());
    string line;

    vector<string> items;

    while (getline(fin, line))
    {
        /*
        if (startswith(line, "<class>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</class>"))
                {
                    break;
                }

                Split(line, items);
                m_class_scope_begins.insert(atoi(items.at(0).c_str()));
                m_class_scope_ends.insert(atoi(items.at(1).c_str()));
            }
        }
        if (startswith(line, "<method>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</method>"))
                {
                    break;
                }

                Split(line, items);
                m_method_scope_begins.insert(atoi(items.at(0).c_str()));
                m_method_scope_ends.insert(atoi(items.at(1).c_str()));
            }
        }
        */
        if (startswith(line, "<file>"))
        {
            while (getline(fin, line))
            {
                if (startswith(line, "</file>"))
                {
                    break;
                }

                m_related_files.push_back(line);
            }
        }
    }
}

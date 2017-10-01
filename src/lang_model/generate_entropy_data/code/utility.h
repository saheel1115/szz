#ifndef __UTILITY_H__
#define __UTILITY_H__

#include <map>
#include <vector>
#include <stack>
#include <time.h>
#include <string>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <math.h>

using namespace std;

const float LOG_E_10 = 2.30258509299405f;
const float LOG_2_10 = 3.32192809488736f;
const float NATURAL_LOG = (float)2.718;

inline void Split(const string &line, const string separator, vector<string> &items)
{
    items.clear();

    int start, end;

    int sep_size = separator.size();

    start = 0;
    end = line.find(separator);

    while (end != string::npos)
    {
        items.push_back(line.substr(start, end-start));

        start = end + sep_size;
        end = line.find(separator, start);
    }

    items.push_back(line.substr(start, line.size()-start));
}

inline void Split(const string &line, vector<string> &items)
{
    items.clear();

    stringstream ss(line);
    string word;

    while (ss >> word)
    {
        items.push_back(word);
    }
}

inline void Split(const string &line, vector<double> &items)
{
    items.clear();

    stringstream ss(line);
    string word;

    while (ss >> word)
    {
        items.push_back(atof(word.c_str()));
    }
}

inline int CountWords(const string &str)
{
	vector<string> items;
	Split(str, items);

	return items.size();
}

inline void Join(const vector<string> &items, string &joined_str)
{
    //assert(items.size() > 0);

    joined_str = "";

    for (int i = 0; i < items.size()-1; i++)
    {
        joined_str += items.at(i) + " ";
    }
    joined_str += items.back();
}

inline void Join(const vector<string> &items, const int &start, const int &end, string &joined_str)
{
    //assert(0 <= start <= end < items.size());

    joined_str = "";

    if (start > end)
    {
        return;
    }

    for (int i = start; i < end; i++)
    {
        joined_str += items.at(i) + " ";
    }
    joined_str += items.at(end);
}

inline void GetFirstNWords(const string &str, const int &n, string &first_words)
{
    if (n == 0)
    {
        first_words = "";
        return;
    }

	int pos = str.find(" ");
	int count = 0;

	while (++count < n && pos != string::npos)
	{
		pos = str.find(" ", pos+1);
	}

	if (count < n)
	{
		first_words = str;
	}
	else
	{
		first_words = str.substr(0, pos);
	}
}

inline void GetLastNWords(const string &str, const int &n, string &last_words)
{
    if (n == 0)
    {
        last_words = "";
        return;
    }

	int pos = str.rfind(" ");
	int count = 0;

	while (++count < n && pos != string::npos)
	{
		pos = str.rfind(" ", pos-1);
	}

	if (count < n)
	{
		last_words = str;
	}
	else
	{
		last_words = str.substr(pos+1, str.size()-pos-1);
	}
}

inline void count_time(int flag, string inf)
{
	static stack<int> stflags;
	static stack<clock_t> stclocks;
	static stack<string> stinfs;

	if (flag > 0)
	{
		stflags.push(flag);
		stclocks.push(clock());
		stinfs.push(inf);
		cout << "---------------------------------------" << '\n';
		if (inf != "NULL")
		{
			cout << "(start - " << inf << ")" << endl;
		}
	}
	else
	{
		if (stflags.empty() || stflags.top() + flag != 0
			|| flag == 0)
		{
			cerr << "flag error!" << endl;
		}
		else
		{
			double tsecond = (clock() - stclocks.top()) / (double)CLOCKS_PER_SEC;
			int h = (int)(tsecond / (60 * 60));
			int m = (int)((tsecond - h * 60 * 60) / 60);
			double s = tsecond - h * 60 * 60 - m * 60;

			if (stinfs.top() != "NULL")
			{
				cout << "(finish - " << stinfs.top() << "): ";
			}
			cout << h << " hour " << m << " min " << s << " second " << '\n';
			cout << "---------------------------------------" << '\n';
			stclocks.pop();
			stflags.pop();
			stinfs.pop();
		}
	}
}

inline bool startswith(const string &str, string prefix)
{
	if (prefix.size() > str.size())
	{
		return false;
	}
	else
	{
		// return strncmp(str.c_str(), prefix.c_str(), prefix.size()) == 0;
		return str.compare(0, prefix.size(), prefix) == 0;
	}
}

inline bool endswith(const string &str, string suffix)
{
	if (suffix.size() > str.size())
	{
		return false;
	}
	else
	{
		return str.compare(str.size()-suffix.size(), suffix.size(), suffix) == 0;
	}
}


inline string to_string1(double m)
{
	char r[64];
	int		i;
	int		j;
	int		len;

	r[len = sprintf(r, "%.12f", m)] = '\0';
	for (i = 0; i < len && r[i] != '.'; ++i)
	{
		NULL;
	}
	for (j = len - 1; j >= 0 && j > i && r[j] == '0'; r[j--] = '\0')
	{
		NULL;
	}
	if (i == j)
	{
		r[i] = '\0';
	}

	return string(r);
}

inline string to_string1(int m)
{
	return to_string1((double)m);
}
#endif


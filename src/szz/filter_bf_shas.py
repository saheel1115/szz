#--------------------------------------------------------------------------------------------------------------------------
import os, sys, pandas
from git import Repo

#--------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage: python script.py <data_dir> <project_name> <min_date> <max_date>')
        sys.exit()

    data_dir = sys.argv[1] + '/'
    project_name = sys.argv[2]
    min_date = sys.argv[3]
    max_date = sys.argv[4]
    
    lines_deleted_data_filename = data_dir + 'lines_deleted_in_bf_shas/' + project_name + '.buggylines'
    csvdata = pandas.read_csv(lines_deleted_data_filename, index_col=False)

    bf_bi_shas = csvdata[['bf_sha', 'bi_sha']] # extract these 2 columns
    bf_bi_shas_tuples = [(tuple[1], tuple[2]) for tuple in bf_bi_shas.itertuples()] # DataFame to list of couples
    bf_bi_shas_tuples_unique = pandas.unique(bf_bi_shas_tuples)

    bf_shas_relevant = []
    project_repo = Repo(data_dir + 'projects/' + project_name)
    for bf_sha, bi_sha in bf_bi_shas_tuples_unique:
        bf_sha_date = str(project_repo.git.log('-n', '1', '--format="%ad"', '--date=short', bf_sha))
        bf_sha_date = bf_sha_date.replace('"', '')

        bi_sha_date = str(project_repo.git.log('-n', '1', '--format="%ad"', '--date=short', bi_sha))
        bi_sha_date = bi_sha_date.replace('"', '')

        if bi_sha_date < max_date and bf_sha_date > min_date:
            bf_shas_relevant.append(bf_sha)

    bf_shas_relevant = pandas.unique(bf_shas_relevant)
    bf_shas_outfile_name = data_dir + 'bf_shas/' + project_name + '.' + min_date + '.' + max_date
    with open(bf_shas_outfile_name, 'wb') as outfile:
        outfile.write('\n'.join(bf_shas_relevant))

#--------------------------------------------------------------------------------------------------------------------------

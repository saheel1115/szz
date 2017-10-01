import pandas, sys

data_dir = sys.argv[1] + '/'
project_name = sys.argv[2]
deleted_lines_filename = data_dir + 'lines_deleted_in_bf_shas/' + project_name + '.buggylines'

df = pandas.read_csv(deleted_lines_filename)
df = df[['bf_sha', 'bi_sha']]
grouped = df.groupby(['bf_sha', 'bi_sha'])
index = [gp_keys[0] for gp_keys in grouped.groups.values()]
unique_df = df.reindex(index)

result_filename = data_dir + 'lines_deleted_in_bf_shas/' + project_name + '.pairs'
unique_df.to_csv(result_filename, columns=['bf_sha', 'bi_sha'], index=False)

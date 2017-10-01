library('ineq')
args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 2) {
    print('Usage: Rscript plot_lorenz_curve_for_defect_densities.r <path/to/data_dir> <project_name>')
    print('E.g. : Rscript plot_lorenz_curve_for_defect_densities.r data/ bitcoin')
} else if (length(args) == 2) {
    data_dir <- args[1]
    project_name <- args[2]

    instance_data_dir <- paste(data_dir, 'ast_node_instances', project_name, sep='/')
    if (!dir.exists(instance_data_dir)) {
        print(paste('Error! Instance data for project `', project_name, '` not found. Aborting!', sep=''))
        break
    }

    csv_file_names = list.files(instance_data_dir, pattern='csv$')
    csv_file_paths = paste(instance_data_dir, csv_file_names, sep='/')

    ## node_types = c('do', 'while', 'for', 'if', 'else', 'switch', 'root', 'function', 'error', 'block')
    node_types = c('do', 'while', 'for', 'if', 'else', 'switch', 'root', 'function')
    for (nt in node_types) {

        plots_dir_1 <- paste('plots', 'num_bugs_vs_num_lines_lorenz', project_name, nt, sep='/')
        if (!dir.exists(plots_dir_1)) {
            dir.create(plots_dir_1, recursive=TRUE)
        }
        
        plots_dir_2 <- paste('plots', 'frac_buggy_lines_lorenz', project_name, nt, sep='/')
        if (!dir.exists(plots_dir_2)) {
            dir.create(plots_dir_2, recursive=TRUE)
        }

        for (i in seq(1, (length(csv_file_paths)))) {
            csv_data = read.csv(csv_file_paths[i])
            csv_data_nt_only = csv_data[which(csv_data$node_type==nt & csv_data$num_buggy_lines>0, ),
                                        c('num_distinct_bugs', 'num_total_lines', 'frac_buggy_lines')]

            png(paste(plots_dir_1, '/', csv_file_names[i], '.png', sep=''))
            plot(Lc(x=csv_data_nt_only$num_distinct_bugs, n=csv_data_nt_only$num_total_lines), col='darkred', lwd=2)
            foo = dev.off()

            png(paste(plots_dir_2, '/', csv_file_names[i], '.png', sep=''))
            plot(Lc(x=csv_data_nt_only$frac_buggy_lines), col='darkred', lwd=2)
            foo = dev.off()

            # gini = ineq(dds$dd, type='Gini')
        }
    }
}

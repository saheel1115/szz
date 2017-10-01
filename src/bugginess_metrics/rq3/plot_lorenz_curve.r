library('ineq')
library('ggplot2')
args <- commandArgs(trailingOnly = TRUE)

if (length(args) != 2) {
    print('Usage: Rscript plot_lorenz_curve_for_defect_densities.r <path/to/data_dir> <project_name>')
    print('E.g. : Rscript plot_lorenz_curve_for_defect_densities.r data/ bitcoin')
} else if (length(args) == 2) {
    data_dir <- args[1]
    project_name <- args[2]

    instance_data_dir <- paste(data_dir, 'ast_node_instances', sep='/')
    if (!dir.exists(instance_data_dir)) {
        print(paste('Error! Instance data for project `', project_name, '` not found. Aborting!', sep=''))
        break
    }

    csv_file_path = paste(instance_data_dir, '/', project_name, '.loops.bugdata.csv', sep='')
    csv_data = read.csv(csv_file_path)

    node_types = c('do', 'while', 'for')
    for (nt in node_types) {

        plots_dir <- paste('plots', 'rq3', project_name, sep='/')
        if (!dir.exists(plots_dir)) {
            dir.create(plots_dir, recursive=TRUE)
        }
        
        csv_data_nt_only = csv_data[which(csv_data$node_type==nt & csv_data$num_overall_bugs>0, ), c('avg_loc', 'num_overall_bugs')]

        png_file_name = paste(plots_dir, '/', nt, '.png', sep='')

        lc = Lc(x=csv_data_nt_only$num_overall_bugs, n=csv_data_nt_only$avg_loc)
        diagonal = data.frame(x=seq(0, 1.0, length.out=length(lc$p)), y=seq(0, 1.0, length.out=length(lc$p)))

        ggplot(data.frame(lines_covered=1-lc$p, bugs_encountered=1-lc$L), aes(x=lines_covered, y=bugs_encountered)) + geom_line(color='darkred') + geom_line(aes(x=diagonal$x, y=diagonal$y))
        ggsave(png_file_name)

        # gini = ineq(dds$dd, type='Gini')
    }
}

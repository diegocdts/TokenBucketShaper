from analysis.data_analysis import Analysis
from analysis.data_visualization import Visualization
from helpers.outputs import Metric


def run(experiment_name, metric):
    analysis = Analysis()
    analysis.load_data(experiment_name, metric)
    best = analysis.best_distribution()
    analysis.sort_distributions_by_aic()

    visualization = Visualization(analysis.data, metric)
    visualization.histogram(best, True)


run('flows_100|y_100|rho_12.80KB|sigma_12.80KB|SLA_0.01s|rate_128.03MBps', Metric.occupancy)

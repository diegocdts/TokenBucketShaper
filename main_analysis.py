from analysis.data_analysis import Analysis
from analysis.data_visualization import Visualization
from helpers.outputs import Metric


def run(file_name, metric):
    analysis = Analysis()
    analysis.load_data(file_name)
    best = analysis.best_distribution()
    analysis.sort_distributions_by_aic()

    visualization = Visualization(analysis.data, metric)
    visualization.histogram(best, True)

run('flows_50|y_100.0|rho_128.00KB|sigma_1.28KB|SLA_0.01s|rate_7.24MBps', Metric.occupancy)

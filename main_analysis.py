from analysis.data_analysis import Analysis
from analysis.data_visualization import Visualization
from helpers.outputs import Metric


def run(experiment_name, node, metric):
    analysis = Analysis()
    analysis.load_data(experiment_name, node, metric)
    best = analysis.best_distribution()
    analysis.sort_distributions_by_aic()

    visualization = Visualization(analysis.data, metric)
    visualization.histogram(best, True)


run('rate_12.75MBps|flows_100|lambda_1010|rho_128.00KB|sigma_384B|SLA_0.01s', 0, Metric.occupancy)

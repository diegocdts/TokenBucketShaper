import os

from analysis.data_analysis import Analysis
from analysis.data_visualization import Visualization
from helpers.outputs import Metric


def run(experiment_name, node, metric):
    analysis = Analysis()
    analysis.load_data(experiment_name, node, metric)
    analysis.score_distributions()
    sorted_distributions = analysis.sort_distributions_by_aic()

    visualization = Visualization(analysis.data, metric)
    visualization.histogram(experiment_name, sorted_distributions[:3], True)


scenarios = [scenario for scenario in sorted(os.listdir('outputs/')) if scenario.startswith('rate')]

for scenario in scenarios:
    run(scenario, 0, Metric.occupancy)

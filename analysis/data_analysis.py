import os

import numpy as np
from scipy import stats


class Analysis:

    def __init__(self):
        self.data = []
        self.distributions = [
            stats.norm,         # Normal
            stats.expon,        # Exponential
            stats.pareto,       # Pareto
            stats.lognorm,      # Log-normal
            stats.gamma,        # Gamma
            stats.weibull_min,  # Weibull Min
            stats.weibull_max,  # Weibull Max
            stats.genextreme,   # GEV
            stats.rayleigh,     # Rayleigh
        ]
        self.aic_values = []
        self.distributions_map = []

    def load_data(self, experiment_name, node, metric):
        path = f'outputs/{experiment_name}/node_{node}/{metric.value}'
        files = os.listdir(path)
        files = [file for file in files if file.endswith('.csv')]

        for file in files:
            data = np.loadtxt(f'{path}/{file}', delimiter=',', ndmin=1).tolist()
            self.data = self.data + data
        self.data = np.array(self.data)

    def score_distributions(self):
        for distribution in self.distributions:
            print(distribution.name)
            data = np.array(self.data)
            if distribution.name == 'poisson':
                params = np.mean(data)
                log_likelihood = np.sum(stats.poisson.logpmf(data, params))
                num_params = 1
            else:
                params = distribution.fit(data)
                log_likelihood = distribution.logpdf(data, *params).sum()
                num_params = len(params)
            aic = 2 * num_params - 2 * log_likelihood
            self.aic_values.append(aic)
            distribution_info = [distribution, aic, params]
            self.distributions_map.append(distribution_info)

    def sort_distributions_by_aic(self):
        self.distributions_map = np.array(self.distributions_map, dtype=object)
        indexes = np.argsort(self.distributions_map[:, 1])
        sorted_distributions = self.distributions_map[indexes]
        return sorted_distributions

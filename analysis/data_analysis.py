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
            stats.poisson,      # Poisson
            # stats.beta,        # Beta
        ]
        self.aic_values = []

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

    def sort_distributions_by_aic(self):
        sorted_distributions = []
        place = 1
        for index in np.argsort(self.aic_values):
            sorted_distributions.append(self.distributions[index])
            print(place, self.distributions[index].name)
            place += 1
        return sorted_distributions

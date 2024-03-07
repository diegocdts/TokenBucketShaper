import os.path

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from helpers.outputs import Metric

outputs_analysis = 'outputs_analysis'


def create_outputs_analysis():
    if not os.path.exists(outputs_analysis):
        os.mkdir(outputs_analysis)


class Visualization:

    def __init__(self, data, metric: Metric):
        """
        Generates a data visualization from a data set
        :param data: the data set
        :param metric: label of the data
        """
        self.metric = metric
        self.data = data
        create_outputs_analysis()

    def histogram(self, experiment_name, distributions, plot_distribution_curve=False):
        """
        Generates histogram visualization
        """
        if self.metric == Metric.latency:
            num_bins = self.bins_for_latency()
        else:
            num_bins = np.arange(min(self.data), max(self.data) + 2) - 0.5

        weights = np.ones(len(self.data)) / len(self.data) * 100

        counts, bins, _ = plt.hist(self.data, bins=num_bins, density=False, weights=weights)

        if plot_distribution_curve:
            for distribution in distributions:
                params = distribution.fit(self.data)
                print(params)

                x_min, x_max = min(self.data), max(self.data)
                x = np.linspace(x_min, x_max, 1000)
                pdf = distribution.pdf(x, *params)

                # pdf normalization
                area_total_hist = np.sum(np.diff(bins) * counts)
                area_total_pdf = np.trapz(pdf, x)
                pdf *= area_total_hist / area_total_pdf
                plt.plot(x, pdf, label=distribution.name)

            plt.title(f'{self.metric.value.capitalize()} histogram\n'
                      f'Best distribution: {distributions[0].name}')
            plt.legend(loc='best')
        plt.xlabel(self.metric)
        plt.ylabel('Frequency (%)')
        plt.savefig(f'{outputs_analysis}/{experiment_name} - {self.metric.value}.png')
        plt.close()

    def qq_plot(self):
        """
        Generates QQ-Plot visualization
        """
        plt.figure(figsize=(8, 6))
        stats.probplot(self.data, dist="norm", plot=plt)
        plt.title("QQ-Plot")
        plt.show()

    def statistics(self):
        mean = np.mean(self.data)
        median = np.median(self.data)
        minimum = np.min(self.data)
        maximum = np.max(self.data)
        std_dev = np.std(self.data)
        variance = np.var(self.data)

        print("Mean:", mean)
        print("Median:", median)
        print("Minimum:", minimum)
        print("Maximum:", maximum)
        print("Standard Deviation:", std_dev)
        print("Variance:", variance)

    def bins_for_latency(self):
        max_latency_str = str(max(self.data)).replace('.', '')
        for char in max_latency_str:
            if char != '0':
                return int(char) + 1
        return 10

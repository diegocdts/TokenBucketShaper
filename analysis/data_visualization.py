import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from helpers.outputs import Metric


class Visualization:

    def __init__(self, data, metric: Metric):
        """
        Generates a data visualization from a data set
        :param data: the data set
        :param metric: label of the data
        """
        self.metric = metric
        self.data = data

    def histogram(self, distribution, plot_distribution_curve=False):
        """
        Generates histogram visualization
        """
        if self.metric == Metric.latency:
            num_bins = self.bins_for_latency()
        else:
            num_bins = np.arange(min(self.data), max(self.data) + 2) - 0.5

        if distribution.name == 'lognorm' or 'rayleigh':
            self.data = self.data + 0.001

        plt.hist(self.data, bins=num_bins, weights=np.ones(len(self.data)) / len(self.data) * 100)

        if plot_distribution_curve:
            params = distribution.fit(self.data)
            print(params)
            x = np.arange(min(self.data), max(self.data) + 1)
            pdf = distribution.pdf(x, *params)
            percentual_frequency = pdf / np.sum(pdf) * 100
            plt.plot(x, percentual_frequency, 'r-')
            plt.title(f'Histogram\nBest distribution: {distribution.name}')
        plt.xlabel(self.metric)
        plt.ylabel('Frequency (%)')
        plt.show()

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

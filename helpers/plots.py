import os
import sys

import numpy as np
import matplotlib.pyplot as plt

from helpers.outputs import Metric, build_rate_file_name, OutputPath


def log(timestamp, occupancy, received, forwarded, tb_emptying_shaper):
    space = '  -  '
    message = (f'timestamp: {timestamp:.4f}{space}'
               f'occupancy: {occupancy} packets{space}'
               f'packets received: {received}{space}'
               f'packets forwarded: {forwarded}{space}'
               f'TB emptying shaper: {tb_emptying_shaper}\n')
    sys.stdout.write('\r' + message)
    sys.stdout.flush()


def samplings_as_csv(file_name, occupancy=None, latencies=None):
    occupation_file_path = f'{OutputPath.occupancy}/{file_name}.csv'
    latency_file_path = f'{OutputPath.latency}/{file_name}.csv'
    if occupancy is not None and latencies is not None:
        with open(occupation_file_path, 'a') as file_occupancy:
            file_occupancy.write(f'{occupancy}\n')
        with open(latency_file_path, 'a') as file_latency:
            file_latency.writelines('\n'.join(map(str, latencies)))
            file_latency.write('\n')
    else:
        with open(occupation_file_path, 'w'):
            pass
        with open(latency_file_path, 'w'):
            pass


def samplings_as_png(begin_window, sampling_interval, file_name, sla):
    occupancy_path = f'{OutputPath.occupancy}/{file_name}.csv'
    latency_path = f'{OutputPath.latency}/{file_name}.csv'

    plot(begin_window, sampling_interval, occupancy_path, file_name, Metric.occupancy)
    plot(begin_window, sampling_interval, latency_path, file_name, Metric.latency, delay_sla=sla)


def plot(begin_window, sampling_interval, file_path, file_name, metric, delay_sla=None):
    data = np.loadtxt(file_path, delimiter=',', ndmin=1)

    plt.figure(figsize=(10, 6))

    if metric == Metric.latency:
        x = np.arange(1, len(data) + 1)
        plt.ylabel(f'{metric} (seconds)')
        plt.xlabel('Packet')
        # plt.axhline(y=delay_sla, color='r', linestyle='--')
    else:
        x = np.linspace(int(begin_window)+sampling_interval, int(begin_window)+(sampling_interval * len(data)),
                        len(data))
        plt.ylabel(f'{metric} (packets)')
        plt.xlabel('Timestamp (s)')

    plt.plot(x, data, label=file_name)

    plt.legend(loc=5)

    plt.savefig(file_path.replace('csv', 'png'))
    plt.close()

    histogram(data, file_name, metric)
    cdf(data, file_name, metric)


def export_plot_rates(args, rates_list: np.array):
    file_name = build_rate_file_name(args)
    path = f'{OutputPath.rate}/{file_name}'
    np.savetxt(f'{path}.csv', rates_list, delimiter=',', fmt='%.2f')

    plt.figure(figsize=(10, 6))
    x = np.linspace(1, len(rates_list), len(rates_list))
    y = [rate/(1000 ** 3) for rate in rates_list]
    plt.plot(x, y, label=file_name)

    plt.xticks(x, x)
    plt.xlabel('Iteration')
    plt.ylabel('Transmission rate (GBps)')
    plt.legend(loc=5)

    plt.savefig(f'{path}.png')
    plt.close()


def token_buckets_shaper_occupation(token_buckets, file_name):
    occupations = sorted([tb.max_occupancy_observed for tb in token_buckets])
    shapers = list(range(1, len(occupations)+1))

    if max(occupations) > 0:
        plt.figure(figsize=(10, 6))
        plt.vlines(shapers, ymin=0, ymax=occupations, colors='b', linewidth=2, label=file_name)

        plt.legend(loc=5)

        plt.xlim(1, len(occupations))
        plt.ylim(0, max(occupations) + (0.05 * max(occupations)))

        plt.xlabel('Token bucket shaper')
        plt.ylabel('Max occupation observed')

        plt.savefig(f'{OutputPath.shaper}/{file_name}.png')
        plt.close()


def cdf(data, file_name, metric):
    data = sorted(data)
    cdf_data = np.arange(1, len(data) + 1) / len(data)

    plt.figure(figsize=(10, 6))
    plt.plot(data, cdf_data, marker='o', linestyle='-', label=file_name)

    if metric == Metric.latency:
        plt.xlabel('Latency')
    else:
        plt.xlabel('Occupancy')
    plt.ylabel('Cumulative Probability')
    plt.legend(loc=5)
    plt.grid(True)

    plt.savefig(f'{OutputPath.cdf}/{file_name}_{metric}.png')
    plt.close()


def histogram(data, file_name, metric):
    plt.figure(figsize=(10, 6))
    num_bins = 25
    hist, bins = np.histogram(data, bins=num_bins, density=True)
    percentual_frequency = hist / np.sum(hist) * 100

    plt.bar(bins[:-1], percentual_frequency, width=(bins[1] - bins[0]), alpha=0.7, color='blue', label=file_name)

    for i, freq in enumerate(percentual_frequency):
        if freq > 0:
            plt.text(bins[i], freq + 1, f'{freq:.2f}%', ha='center', va='bottom', fontsize=10)

    plt.legend(loc=5)

    plt.xlabel(metric)
    plt.ylabel('Frequency (%)')

    plt.savefig(f'{OutputPath.histogram}/{file_name}_{metric}.png')
    plt.close()


def full_histogram(file_name: str):
    end_index = file_name.find('[')
    file_prefix = file_name[:end_index]

    roots = [f'{OutputPath.occupancy}', f'{OutputPath.latency}']
    metrics = [f'{Metric.occupancy}', f'{Metric.latency}']
    for root, metric in zip(roots, metrics):
        files = os.listdir(f'{root}/{file_prefix}')
        files = [file for file in files if file.endswith('.csv')]

        all_data = []

        for file in files:
            data = np.loadtxt(f'{root}/{file_prefix}/{file}', delimiter=',', ndmin=1).tolist()
            all_data = all_data + data

        histogram(all_data, f'{file_prefix}full', metric)

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

from helpers.outputs import Metric, Extension, format_bytes


def log(timestamp, occupancy, biggest_burst, num_bursts, received, forwarded, buckets_status):
    space = '  -  '
    message = (f'timestamp: {timestamp:.4f}{space}'
               f'max occupancy: {occupancy} packets{space}'
               f'biggest burst: {biggest_burst} packets{space}'
               f'num bursts: {num_bursts} packets{space}'
               f'packets received: {received}{space}'
               f'packets forwarded: {forwarded}{space}\n'
               f'buckets status: {buckets_status}\n')
    sys.stdout.write('\r' + message)
    sys.stdout.flush()


def samplings_as_csv(simulation_info, occupancy=None, latencies=None):
    occupancy_file_path = simulation_info.get_file_metric_path(Metric.occupancy, Extension.csv)
    latency_file_path = simulation_info.get_file_metric_path(Metric.latency, Extension.csv)
    if occupancy is not None and latencies is not None:
        with open(occupancy_file_path, 'a') as file_occupancy:
            file_occupancy.write(f'{occupancy}\n')
        with open(latency_file_path, 'a') as file_latency:
            file_latency.writelines('\n'.join(map(str, latencies)))
            file_latency.write('\n')
    else:
        with open(occupancy_file_path, 'w'):
            pass
        with open(latency_file_path, 'w'):
            pass


def samplings_as_png(begin_window, sampling_interval, simulation_info):
    occupancy_path = simulation_info.get_file_metric_path(Metric.occupancy, Extension.csv)
    latency_path = simulation_info.get_file_metric_path(Metric.latency, Extension.csv)
    scenario_name = simulation_info.scenario_name

    plot(begin_window, sampling_interval, occupancy_path, scenario_name, Metric.occupancy, simulation_info)
    plot(begin_window, sampling_interval, latency_path, scenario_name, Metric.latency, simulation_info)


def plot(begin_window, sampling_interval, file_path, scenario_name, metric, simulation_info):
    data = np.loadtxt(file_path, delimiter=',', ndmin=1)

    plt.figure(figsize=(10, 6))

    if metric == Metric.latency:
        x = np.arange(1, len(data) + 1)
        plt.ylabel(f'{metric} (seconds)')
        plt.xlabel('Packet')
    else:
        x = np.linspace(int(begin_window)+sampling_interval, int(begin_window)+(sampling_interval * len(data)),
                        len(data))
        plt.ylabel(f'{metric} (packets)')
        plt.xlabel('Timestamp (s)')

    plt.plot(x, data, label=scenario_name)
    plt.suptitle(simulation_info.current_file_name)

    plt.legend(loc=5)

    plt.savefig(file_path.replace('csv', 'png'))
    plt.close()

    histogram(data, scenario_name, metric, simulation_info)
    cdf(data, scenario_name, metric, simulation_info)


def export_plot_rates(simulation_info, rates_list: np.array):
    np.savetxt(simulation_info.get_file_metric_path(Metric.rate, Extension.csv), rates_list, delimiter=',', fmt='%.2f')

    plt.figure(figsize=(10, 6))
    x = np.linspace(1, len(rates_list), len(rates_list))
    y = [rate for rate in rates_list]
    plt.plot(x, y, label=simulation_info.rate_file_name)

    plt.xticks(x, x)
    plt.xlabel('Iteration')
    plt.ylabel('Transmission rate (Bytes per sec)')
    plt.legend(loc=5)

    plt.savefig(simulation_info.get_file_metric_path(Metric.rate, Extension.png))
    plt.close()


def token_buckets_shaper_occupation(token_buckets, simulation_info):
    occupations = sorted([tb.max_shaper_occupancy for tb in token_buckets])
    [tb.__setattr__('max_shaper_occupancy', 0) for tb in token_buckets]
    shapers = list(range(1, len(occupations)+1))

    if max(occupations) > 0:
        plt.figure(figsize=(10, 6))
        plt.vlines(shapers, ymin=0, ymax=occupations, colors='b', linewidth=2, label=simulation_info.scenario_name)

        plt.legend(loc=5)

        plt.xlim(1, len(occupations))
        plt.ylim(0, token_buckets[0].shaper_capacity + 1)

        plt.xlabel('Token bucket shaper')
        plt.ylabel('Max occupation observed')
        plt.suptitle(simulation_info.current_file_name)

        plt.savefig(simulation_info.get_file_metric_path(Metric.shaper, Extension.png))
        plt.close()


def cdf(data, scenario_name, metric, simulation_info, is_full=False):
    data = sorted(data)
    cdf_data = np.arange(1, len(data) + 1) / len(data)

    plt.figure(figsize=(10, 6))
    plt.plot(data, cdf_data, marker='o', linestyle='-', label=scenario_name)

    if metric == Metric.latency:
        plt.xlabel('Latency')
    else:
        plt.xlabel('Occupancy')
    plt.ylabel('Cumulative Probability')
    plt.suptitle(simulation_info.current_file_name)
    plt.legend(loc=5)
    plt.grid(True)

    if is_full:
        extra = f'Full {metric}'
        plt.suptitle(extra)
    else:
        extra = f'{metric} - '

    plt.savefig(simulation_info.get_file_metric_path(Metric.cdf, Extension.png, extra=extra))
    plt.close()


def histogram(data, scenario_name, metric, simulation_info, is_full=False):
    plt.figure(figsize=(15, 7))
    if metric == Metric.latency:
        num_bins = 15
    else:
        num_bins = np.arange(min(data), max(data) + 2) - 0.5

    hist, bins, patches = plt.hist(data, bins=num_bins, weights=np.ones(len(data)) / len(data) * 100,
                                   label=scenario_name)

    plt.ylim(min(hist) - 1, max(hist) + 1)

    delta = (bins[1] - bins[0]) / 2
    for i, freq in enumerate(hist):
        if freq > 0:
            absolute = round(freq * len(data) / 100)
            absolute_str = f' ({absolute})'
            height = min(hist) + 1
            plt.text(bins[i] + delta, height, f'{freq:.4f}%{absolute_str}', ha='center', va='bottom', fontsize=10,
                     rotation=90)

    plt.legend(loc=1)

    plt.xlabel(metric)
    plt.ylabel('Frequency (%)')
    plt.suptitle(simulation_info.current_file_name)

    if is_full:
        extra = f'Full {metric}'
        plt.suptitle(extra)
    else:
        extra = f'{metric} - '

    plt.savefig(simulation_info.get_file_metric_path(Metric.histogram, Extension.png, extra=extra))
    plt.close()


def full_histogram_cdf(args, simulation_info):
    paths = [simulation_info.get_metric_path(Metric.occupancy), simulation_info.get_metric_path(Metric.latency)]
    metrics = [Metric.occupancy, Metric.latency]
    for path, metric in zip(paths, metrics):
        files = os.listdir(path)
        files = [file for file in files if file.endswith('.csv')]

        all_data = []

        for file in files:
            data = np.loadtxt(f'{path}/{file}', delimiter=',', ndmin=1).tolist()
            all_data = all_data + data

        histogram(all_data, f'{simulation_info.scenario_name}', metric, simulation_info, is_full=True)
        cdf(all_data, f'{simulation_info.scenario_name}', metric, simulation_info, is_full=True)

        if metric == Metric.occupancy:
            max_occupation = max(all_data)
            save_max_occupation(args, simulation_info, max_occupation)


def save_max_occupation(args, simulation_info, max_occupation):
    file = simulation_info.parameters_analysis_file
    with open(file, 'a') as file_writer:
        file_writer.write(f'{args.rho}, {args.sigma}, {max_occupation}\n')


def plot_parameters_analysis(simulation_info):
    files = os.listdir(simulation_info.parameters_analysis_path)
    files = [file for file in files if file.endswith('.csv')]
    for file in files:
        data = np.loadtxt(f'{simulation_info.parameters_analysis_path}/{file}', delimiter=',', ndmin=1)
        parameters = ['rho', 'sigma']
        for index, parameter in enumerate(parameters):
            if data.ndim > 1:
                fixed_parameter = np.unique(data[:, index])
                for unique in fixed_parameter:
                    file_name = file.replace(f'.{Extension.csv.value}', '')
                    flows = file_name.replace('_', ' = ')
                    file_name = f'{file_name}_fixed_{parameter}_{unique}'
                    indices = np.where(data[:, index] == unique)
                    variable_parameter = sorted(data[:, 1 - index][indices])
                    max_occupations = data[:, 2][indices]
                    plt.figure(figsize=(10, 6))
                    plt.plot(variable_parameter, max_occupations, label=file_name)
                    plt.scatter(variable_parameter, max_occupations)
                    for i, value in enumerate(max_occupations):
                        plt.text(variable_parameter[i], value + 0.5,
                                 f'occupation = {value}\n{parameters[1 - index]} = {variable_parameter[i]}', fontsize=7,
                                 ha='center', va='bottom')
                    plt.ylabel('Max occupation')
                    plt.xlabel(parameters[1 - index])
                    plt.suptitle(f'Fixed {parameter} = {format_bytes(unique)}\n{flows}')
                    plt.savefig(f'{simulation_info.parameters_analysis_path}/{file_name}.{Extension.png}')

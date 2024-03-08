import os

import numpy as np
import matplotlib.pyplot as plt

from helpers.outputs import Metric, Extension, format_bytes

fontsize = 12


def samplings_as_csv(simulation_info, queue_nodes):
    for node in queue_nodes:
        occupancies = np.array(node.occupancies)
        occupancy_file_path = simulation_info.get_file_metric_path(Metric.occupancy, Extension.csv, node_id=node.id)
        np.savetxt(occupancy_file_path, occupancies, delimiter=',')

        latencies = np.array(node.latencies)
        latency_file_path = simulation_info.get_file_metric_path(Metric.latency, Extension.csv, node_id=node.id)
        np.savetxt(latency_file_path, latencies, delimiter=',')


def samplings_as_png(args, simulation_info, queue_nodes):
    for node in queue_nodes:
        print(f'Preparing the plots for Node {node.id}')
        occupancy_path = simulation_info.get_file_metric_path(Metric.occupancy, Extension.csv, node_id=node.id)
        latency_path = simulation_info.get_file_metric_path(Metric.latency, Extension.csv, node_id=node.id)
        scenario_name = simulation_info.scenario_name

        occupancy_data = np.loadtxt(occupancy_path, delimiter=',')
        latency_data = np.loadtxt(latency_path, delimiter=',')

        max_occupation = max(occupancy_data)
        max_latency = max(latency_data)
        save_max_observation(args, simulation_info, max_occupation, max_latency, node.id)

        plot(args, occupancy_data, occupancy_path, scenario_name, Metric.occupancy, simulation_info, node_id=node.id)
        plot(args, latency_data, latency_path, scenario_name, Metric.latency, simulation_info, node_id=node.id)


def plot(args, data, file_path, scenario_name, metric, simulation_info, node_id):

    plt.figure(figsize=(10, 6))
    x = np.arange(1, len(data) + 1)

    if metric == Metric.latency:
        plt.ylabel(f'{metric} (seconds)', fontsize=fontsize)
        plt.xlabel('Packet', fontsize=fontsize)
    else:
        plt.ylabel(f'{metric} (packets)', fontsize=fontsize)
        plt.xlabel('Sample', fontsize=fontsize)

    plt.plot(x, data, label=scenario_name)
    plt.suptitle(simulation_info.scenario_name)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    plt.legend(loc=5, fontsize=fontsize)

    plt.savefig(file_path.replace('csv', 'png'))
    plt.close()

    histogram(data, scenario_name, metric, simulation_info, node_id)
    cdf(data, scenario_name, metric, simulation_info, node_id)


def export_plot_rates(simulation_info, rates_list: np.array):
    print('Preparing the rate plot')
    np.savetxt(simulation_info.get_file_metric_path(Metric.rate, Extension.csv), rates_list, delimiter=',', fmt='%.2f')

    plt.figure(figsize=(10, 6))
    x = np.linspace(1, len(rates_list), len(rates_list))
    y = [rate for rate in rates_list]
    plt.plot(x, y, label=simulation_info.rate_file_name)

    for i, rate in enumerate(y):
        plt.text(x[i], rate + 1, format_bytes(rate, 5), va='bottom', ha='left', rotation=45, fontsize=fontsize)

    y_ticks = np.linspace(min(rates_list), max(rates_list), 10)
    y_ticks_labels = [format_bytes(y_tick) for y_tick in y_ticks]
    plt.yticks(y_ticks, y_ticks_labels, fontsize=fontsize)
    plt.xticks(x, x, fontsize=fontsize)
    plt.xlabel('Iteration', fontsize=fontsize)
    plt.ylabel('Transmission rate (Bytes per sec)', fontsize=fontsize)
    plt.legend(loc=2, fontsize=fontsize)

    plt.suptitle(simulation_info.scenario_name)

    plt.savefig(simulation_info.get_file_metric_path(Metric.rate, Extension.png))
    plt.close()


def token_buckets_shaper_occupation(token_buckets, simulation_info):
    print('Preparing the token buckets shaper occupation plot')
    occupations = sorted([tb.max_shaper_occupancy for tb in token_buckets])
    [tb.__setattr__('max_shaper_occupancy', 0) for tb in token_buckets]
    shapers = list(range(1, len(occupations)+1))

    if max(occupations) > 0:
        plt.figure(figsize=(10, 6))
        plt.vlines(shapers, ymin=0, ymax=occupations, colors='b', linewidth=2, label=simulation_info.scenario_name)

        plt.legend(loc=5)

        plt.xlim(1, len(occupations))
        plt.ylim(0, token_buckets[0].shaper_capacity + 1)

        plt.xlabel('Token bucket shaper', fontsize=fontsize)
        plt.ylabel('Max occupation observed', fontsize=fontsize)
        plt.suptitle(simulation_info.scenario_name)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)

        plt.savefig(simulation_info.get_file_metric_path(Metric.shaper, Extension.png))
        plt.close()


def cdf(data, scenario_name, metric, simulation_info, node_id):
    data = sorted(data)
    cdf_data = np.arange(1, len(data) + 1) / len(data)

    plt.figure(figsize=(10, 6))
    plt.plot(data, cdf_data, marker='o', linestyle='-', label=scenario_name)

    if metric == Metric.latency:
        plt.xlabel('Latency', fontsize=fontsize)
    else:
        plt.xlabel('Occupancy', fontsize=fontsize)
    plt.ylabel('Cumulative Probability', fontsize=fontsize)
    plt.suptitle(simulation_info.scenario_name)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.legend(loc=5, fontsize=fontsize)
    plt.grid(True)

    extra = f'{metric} - '

    plt.savefig(simulation_info.get_file_metric_path(Metric.cdf, Extension.png, node_id=node_id, extra=extra))
    plt.close()


def histogram(data, scenario_name, metric, simulation_info, node_id):
    plt.figure(figsize=(15, 7))
    if metric == Metric.latency:
        num_bins = 15
    else:
        num_bins = np.arange(min(data), max(data) + 2) - 0.5

    plt.hist(data, bins=num_bins, weights=np.ones(len(data)) / len(data) * 100, label=scenario_name)

    """
    delta = (bins[1] - bins[0]) / 2
    for i, freq in enumerate(hist):
        if freq > 0:
            absolute = round(freq * len(data) / 100)
            absolute_str = f' ({absolute})'
            height = min(hist) + 1
            plt.text(bins[i] + delta, height, f'{freq:.4f}%{absolute_str}', ha='center', va='bottom', fontsize=10,
                     rotation=90)
    """

    plt.legend(loc=1, fontsize=fontsize)

    plt.xlabel(metric, fontsize=fontsize)
    plt.ylabel('Frequency (%)', fontsize=fontsize)
    plt.suptitle(simulation_info.scenario_name)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    extra = f'{metric} - '

    plt.savefig(simulation_info.get_file_metric_path(Metric.histogram, Extension.png, node_id=node_id, extra=extra))
    plt.close()


def save_max_observation(args, simulation_info, max_occupation, max_latency, node_id):
    file = simulation_info.parameters_analysis_file
    with open(file, 'a') as file_writer:
        file_writer.write(f'{args.rho}, {args.sigma}, {simulation_info.rate}, {node_id}, {max_occupation}, '
                          f'{max_latency}\n')


def plot_parameters_analysis(simulation_info):
    files = os.listdir(simulation_info.parameters_analysis_path)
    files = [file for file in files if file.endswith('.csv')]
    for file in files:
        data = np.loadtxt(f'{simulation_info.parameters_analysis_path}/{file}', delimiter=',', ndmin=1)
        parameters = ['RHO', 'SIGMA']
        for index, parameter in enumerate(parameters):
            if data.ndim > 1:
                fixed_parameter = np.unique(data[:, index])
                for unique in fixed_parameter:
                    file_name = file.replace(f'.{Extension.csv.value}', '')
                    flows = file_name.replace('_', ' = ')
                    file_name = f'{file_name}_fixed_{parameter}_{unique}'
                    indices = np.where(data[:, index] == unique)
                    aux_data = data[indices]
                    aux_data = aux_data[np.argsort(aux_data[:, 1 - index])]
                    variable_parameter = aux_data[:, 1 - index]
                    rates = aux_data[:, 2]
                    node_ids = aux_data[:, 3]
                    max_occupations = aux_data[:, 4]
                    max_latencies = aux_data[:, 5]
                    plot_observations(variable_parameter, max_occupations, rates, parameters, parameter, index,
                                      node_ids, unique, flows, simulation_info, file_name, Metric.occupancy)
                    plot_observations(variable_parameter, max_latencies, rates, parameters, parameter, index,
                                      node_ids, unique, flows, simulation_info, file_name, Metric.latency)


def plot_observations(variable_parameter, observations, rates, parameters, parameter, index, node_ids, unique,
                      flows, simulation_info, file_name, metric):
    if metric == Metric.occupancy:
        text_observation = 'OCC'
        unit = 'packets'
    else:
        text_observation = 'LAT'
        unit = 'seconds'
    plt.figure(figsize=(10, 6))
    plt.plot(variable_parameter, observations, label=file_name)
    plt.scatter(variable_parameter, observations)
    for i, value in enumerate(observations):
        plt.text(variable_parameter[i], value,
                 f'{text_observation} = {value}\n'
                 f'RT = {format_bytes(rates[i])}ps\n'
                 f'{parameters[1 - index]} = {format_bytes(variable_parameter[i])}\n'
                 f'NODE = {int(node_ids[i])}', fontsize=fontsize,
                 ha='center', va='bottom')
    locs, labels = plt.xticks()
    xticks = [format_bytes(float(value.get_text())) for value in labels]
    plt.xticks(locs, xticks)
    plt.ylabel(f'Max {metric.value} ({unit})')
    plt.xlabel(f'{parameters[1 - index]}')
    plt.suptitle(f'Fixed {parameter} = {format_bytes(unique)}\n{flows}')
    plt.savefig(f'{simulation_info.parameters_analysis_path}/{file_name} - {metric.value}.{Extension.png}')
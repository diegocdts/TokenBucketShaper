import os
from enum import Enum


def node_directory(node):
    return f'node_{node}'


def set_file_name(args):
    return f'[{args.max_time}s]'


class SimulationInfo:
    def __init__(self, args, rate):
        self.rate = rate
        self.scenario_name = build_scenario_name(args, rate)
        self.file_name = set_file_name(args)
        self.rate_file_name = build_rate_file_name(args)
        self.scenario_path = self.get_scenario_path()
        self.parameters_analysis_path, self.parameters_analysis_file = get_parameters_analysis_path(args.flows,
                                                                                                    args.lambda_param)
        self.build_metric_paths(args)

    def get_scenario_path(self):
        base_dir = 'outputs'
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        scenario_path = f'{base_dir}/{self.scenario_name}'
        if not os.path.exists(scenario_path):
            os.mkdir(scenario_path)
        return scenario_path

    def build_metric_paths(self, args):
        for node in range(args.num_queue_nodes):
            # creates one directory per node
            node_path = f'{self.scenario_path}/{node_directory(node)}'
            if not os.path.exists(node_path):
                os.mkdir(node_path)
            for metric in Metric.__members__.items():
                name, value = metric
                if value == Metric.rate or value == Metric.shaper:
                    # creates the rate and shaper directories inside the scenario directory
                    metric_path = f'{self.scenario_path}/{value.value}'
                else:
                    # creates the other metric directories inside the node directory
                    metric_path = f'{node_path}/{value.value}'
                if not os.path.exists(metric_path):
                    os.mkdir(metric_path)

    def get_file_metric_path(self, metric, extension, node_id='', extra=''):
        if metric == Metric.latency or metric == Metric.occupancy:
            return f'{self.scenario_path}/{node_directory(node_id)}/{metric}/{self.file_name}.{extension}'
        elif metric == Metric.histogram or metric == Metric.cdf:
            return f'{self.scenario_path}/{node_directory(node_id)}/{metric}/{extra}{self.file_name}.{extension}'
        else:
            return f'{self.scenario_path}/{metric}/{self.file_name}.{extension}'


class Metric(Enum):
    occupancy = 'occupancy'
    latency = 'latency'
    rate = 'rate'
    shaper = 'shaper'
    cdf = 'cdf'
    histogram = 'histogram'

    def __str__(self):
        return self.value


class Extension(Enum):
    csv = 'csv'
    png = 'png'

    def __str__(self):
        return self.value


def build_scenario_name(args, rate):
    return (f'flows_{args.flows}|'
            f'y_{args.lambda_param}|'
            f'rho_{format_bytes(args.rho)}|'
            f'sigma_{format_bytes(args.sigma)}|'
            f'SLA_{args.delay_sla}s|'
            f'rate_{format_bytes(rate)}ps')


def build_rate_file_name(args):
    return (f'flows_{args.flows}|'
            f'rho_{format_bytes(args.rho)}|'
            f'sigma_{format_bytes(args.sigma)}|'
            f'SLA_{args.delay_sla}s')


def get_parameters_analysis_path(num_flows, lambda_param):
    base_dir = 'outputs'
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    path = f'{base_dir}/parameters_analysis'
    if not os.path.exists(path):
        os.mkdir(path)
    file = f'{path}/flows_{num_flows}|y_{lambda_param}.{Extension.csv}'
    with open(file, 'a'):
        pass
    return path, file


def format_bytes(value):
    kilobytes_limit = 1000  # 1 KB
    megabytes_limit = 1000 ** 2  # 1 MB
    gigabytes_limit = 1000 ** 3  # 1 GB

    if value >= gigabytes_limit:
        return f"{value / gigabytes_limit:.2f}GB"
    elif value >= megabytes_limit:
        return f"{value / megabytes_limit:.2f}MB"
    elif value >= kilobytes_limit:
        return f"{value / kilobytes_limit:.2f}KB"
    else:
        return f"{value}B"

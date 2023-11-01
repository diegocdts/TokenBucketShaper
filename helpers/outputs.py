import os
from enum import Enum


class SimulationInfo:
    def __init__(self, args, begin_window, rate):
        self.rate = rate
        self.scenario_name = build_scenario_name(args, rate)
        self.current_file_name = build_file_name(args, begin_window)
        self.rate_file_name = build_rate_file_name(args)
        self.scenario_path = self.get_scenario_path()
        self.parameters_analysis_path = get_parameters_analysis_path(args.flows)
        self.build_metric_paths()

    def get_scenario_path(self):
        base_dir = 'outputs'
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        scenario_path = f'{base_dir}/{self.scenario_name}'
        if not os.path.exists(scenario_path):
            os.mkdir(scenario_path)
        return scenario_path

    def build_metric_paths(self):
        for metric in Metric.__members__.items():
            name, value = metric
            path = f'{self.scenario_path}/{value.value}'
            if not os.path.exists(path):
                os.mkdir(path)

    def get_file_metric_path(self, metric, extension, extra=''):
        if metric == Metric.rate:
            return f'{self.scenario_path}/{metric}/{self.rate_file_name}.{extension}'
        else:
            if 'Full' in extra:
                return f'{self.scenario_path}/{metric}/{extra}.{extension}'
            else:
                return f'{self.scenario_path}/{metric}/{extra}{self.current_file_name}.{extension}'

    def set_current_file_name(self, args, begin_window):
        self.current_file_name = build_file_name(args, begin_window)

    def get_metric_path(self, metric):
        return f'{self.scenario_path}/{metric}/'


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


def build_file_name(args, begin_window):
    return f'[{begin_window}s-{begin_window + args.sampling_window}s]'


def build_rate_file_name(args):
    return (f'flows_{args.flows}|'
            f'rho_{format_bytes(args.rho)}|'
            f'sigma_{format_bytes(args.sigma)}|'
            f'SLA_{args.delay_sla}s')


def get_parameters_analysis_path(num_flows):
    base_dir = 'outputs'
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    path = f'{base_dir}/parameters_analysis'
    if not os.path.exists(path):
        os.mkdir(path)
    file = f'{path}/flows_{num_flows}.{Extension.csv}'
    with open(file, 'a'):
        pass
    return path


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

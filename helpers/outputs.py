import os
from enum import Enum


class OutputPath(Enum):
    outputs = 'outputs'
    occupancy = 'outputs/occupancy'
    latency = 'outputs/latency'
    rate = 'outputs/rate'
    shaper = 'outputs/shaper'
    cdf = 'outputs/cdf'
    histogram = 'outputs/histogram'

    def __str__(self):
        return self.value


class Metric(Enum):
    occupancy = 'occupancy'
    latency = 'latency'
    rate = 'rate'
    shaper = 'shaper'
    cdf = 'cdf'
    histogram = 'histogram'

    def __str__(self):
        return self.value


def create_base_output_paths():
    """
    create the directories to save files into
    """
    for output in OutputPath.__members__.items():
        name, value = output
        if not os.path.exists(value.value):
            os.mkdir(value.value)


def create_output_path(path):
    for output in OutputPath.__members__.items():
        name, value = output
        _path = f'{value.value}/{path}'
        if value != OutputPath.outputs and value != OutputPath.rate and not os.path.exists(_path):
            os.mkdir(_path)


def build_file_name(args, begin_window, rate):
    """
    returns the name of the files to be generated for queue occupancy and latency
    :param args parsed arguments
    :param begin_window: the moment a new file name is created
    :param rate transmission rate
    :return: file name
    """
    path = (f'flows_{args.flows}|'
            f'y_{args.lambda_param}|'
            f'rho_{format_bytes(args.tokens)}|'
            f'sigma_{format_bytes(args.bucket_capacity)}|'
            f'SLA_{args.delay_sla}s|'
            f'rate_{format_bytes(rate)}ps')
    file = f'[{begin_window}s-{begin_window + args.sampling_window}s]'
    create_output_path(path)
    return f'{path}/{file}'


def build_rate_file_name(args):
    return (f'flows_{args.flows}|'
            f'rho_{format_bytes(args.tokens)}|'
            f'sigma_{format_bytes(args.bucket_capacity)}|'
            f'SLA_{args.delay_sla}s|')


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

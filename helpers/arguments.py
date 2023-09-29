import argparse


def arguments():
    parser = argparse.ArgumentParser(description='Arguments to be used in Flow, TokenBucket and '
                                                 'TransmissionQueue objects')

    parser.add_argument('--seed',
                        type=int,
                        default=123,
                        help='Seed for random values')

    parser.add_argument('--flows',
                        type=int,
                        default=10,
                        help='Total number of flows')

    parser.add_argument('--lambda_param',
                        type=float,
                        default=100,
                        help='The lambda parameter for the expovariate random time inter packets')

    parser.add_argument('--tokens',
                        type=int,
                        default=128000,
                        help='Number of tokens to be created per second')

    parser.add_argument('--bucket_capacity',
                        type=int,
                        default=12800,
                        help='Max capacity of the bucket (also burst size) in bytes')

    parser.add_argument('--max_queue_occupancy',
                        type=int,
                        default=999999999999999999999999,
                        help='Max capacity of the queue in bytes')

    parser.add_argument('--delay_sla',
                        type=float,
                        default=0.01,
                        help='The SLA delay')

    parser.add_argument('--max_time',
                        type=float,
                        default=2000,
                        help='Maximum program execution time (in seconds)')

    parser.add_argument('--mtu',
                        type=int,
                        default=128,
                        help='Maximum Transmission Unit')

    parser.add_argument('--rate_percentage',
                        type=float,
                        default=100,
                        help='The percentage of the calculated rate to be used')

    parser.add_argument('--sampling_interval',
                        type=float,
                        default=0.001,
                        help='The sampling interval')

    parser.add_argument('--sampling_window',
                        type=float,
                        default=200,
                        help='Window to create a new set of sampling files')

    return parser.parse_args()

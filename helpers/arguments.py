import argparse


def arguments():
    parser = argparse.ArgumentParser(description='Arguments to be used in Flow, TokenBucket and '
                                                 'QueueNode objects')

    parser.add_argument('--seed',
                        type=int,
                        default=1,
                        help='Seed for random values')

    parser.add_argument('--flows',
                        type=int,
                        default=100,
                        help='Total number of flows')

    parser.add_argument('--lambda_param',
                        type=int,
                        default=1000,
                        help='The lambda parameter for the expovariate random time inter packets')

    parser.add_argument('--rho',
                        type=int,
                        default=1000,
                        help='Number of packets equivalent to the number of tokens generated per second. This value '
                             'will be multiplied by mtu, as 1 byte consumes 1 token.')

    parser.add_argument('--sigma',
                        type=int,
                        default=3,
                        help='The burst size and the bucket capacity, in packets. This value will be multiplied by mtu '
                             'since 1 byte consumes 1 token')

    parser.add_argument('--queue_capacity',
                        type=int,
                        default=9999999999999999,
                        help='Max capacity of the queue in packets')

    parser.add_argument('--delay_sla',
                        type=float,
                        default=0.01,
                        help='The SLA delay')

    parser.add_argument('--mtu',
                        type=int,
                        default=128,
                        help='Maximum Transmission Unit')

    parser.add_argument('--rate_percentage',
                        type=float,
                        default=100,
                        help='The percentage of the calculated rate to be used')

    parser.add_argument('--max_time',
                        type=float,
                        default=15,
                        help='Maximum program execution time (in seconds)')

    parser.add_argument('--num_queue_nodes',
                        type=int,
                        default=1,
                        help='The total of QueueNodes to instantiate')

    parser.add_argument('--uflows_node',
                        type=str,
                        default='0_0',
                        help='The number of uncontrolled flows per queue node in the form '
                             '\'numberOfFlows_queueNodeIndex\'. Use a comma to specify the number for multiple nodes. '
                             'Ex: \'2_0,0_1,2_2\' where there are 2 flows for node 0, no flow for node 1, and 2 flows '
                             'for node 2.')

    parser.add_argument('--uflow_lambda_param',
                        type=float,
                        default=100,
                        help='The lambda parameter for the expovariate random time inter packets of the uncontrolled '
                             'flows')

    args = parser.parse_args()

    args.rho = args.rho * args.mtu

    args.sigma = args.sigma * args.mtu

    args.queue_capacity = args.queue_capacity * args.mtu

    return args

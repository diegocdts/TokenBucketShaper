import numpy as np

from components.Flow import Flow
from components.TokenBucket import TokenBucket
from components.QueueNode import QueueNode
from helpers.outputs import SimulationInfo
from helpers.plots import export_plot_rates


def get_flows(args, env, token_buckets):
    flow = Flow(env=env,
                num_flows=args.flows,
                lambda_param=args.lambda_param,
                mtu=args.mtu,
                tokens_per_second=args.rho,
                bucket_capacity=args.sigma,
                token_buckets=token_buckets)
    return flow


def get_token_buckets(args, env, queue_node):
    token_buckets_list = []

    for index in range(args.flows):
        token_bucket = TokenBucket(env=env,
                                   identifier=f'TB_{index}',
                                   mtu=args.mtu,
                                   tokens_per_second=args.rho,
                                   bucket_capacity=args.sigma,
                                   queue_node=queue_node)
        token_buckets_list.append(token_bucket)

    return token_buckets_list


def get_transmission_queue(args, env):
    current_rate = net_calc_4_rate(args)
    rates_list = [current_rate]

    new_rate = None

    while new_rate != current_rate:
        current_rate = new_rate

        new_rate = net_calc_4_rate(args, current_rate)
        rates_list.append(new_rate)

    new_rate = round(new_rate * (args.rate_percentage / 100))

    simulation_info = SimulationInfo(args, new_rate)
    queue_node = QueueNode(env=env,
                                   rate=new_rate,
                                   mtu=args.mtu,
                                   queue_capacity=args.queue_capacity)

    export_plot_rates(simulation_info, rates_list)

    return queue_node, simulation_info


def net_calc_4_rate(args, current_rate=None):
    """
    returns the transmission rate obtained through network calculus
    :param args: parsed arguments
    :param current_rate: current transmission rate
    :return: the new transmission rate
    """
    if current_rate:
        fixed_latency = args.mtu / current_rate
    else:
        fixed_latency = 0.0
    flows = args.flows
    rho = np.full(flows, args.rho)
    sigma = np.full(flows, args.sigma)

    foi = 0  # foi = flow of interest
    s = sigma[foi]  # s = foi burst
    # Preparation
    rhoy = np.concatenate([rho[0:foi], rho[foi + 1:]])
    rhoy = sum(rhoy)
    sigmay = np.concatenate([sigma[0:foi], sigma[foi + 1:]])
    sigmay = sum(sigmay)
    # Capacity estimation based on the SLA
    delay_sla = args.delay_sla
    transm_rate = -(s + sigmay - fixed_latency*rhoy + delay_sla*rhoy +
                    (fixed_latency**2*rhoy**2 - 2*fixed_latency * delay_sla*rhoy**2 - 2*fixed_latency*rhoy*s +
                     2*fixed_latency*rhoy*sigmay + delay_sla**2*rhoy**2 + 2*delay_sla*rhoy*s - 2*delay_sla*rhoy*sigmay +
                     s**2 + 2*s*sigmay + sigmay**2)**(1/2))/(2*(fixed_latency - delay_sla))

    return transm_rate

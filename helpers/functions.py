import numpy as np

from components.Flow import Flow
from components.TokenBucket import TokenBucket
from components.TransmissionQueue import TransmissionQueue
from helpers.outputs import build_file_name
from helpers.plots import export_plot_rates, samplings_as_csv, log, token_buckets_shaper_occupation, samplings_as_png


def get_flows(args, env, token_buckets):
    flows = []

    for token_bucket in token_buckets:
        flow = Flow(env=env,
                    lambda_param=args.lambda_param,
                    mtu=args.mtu,
                    token_bucket=token_bucket)
        flows.append(flow)

    return flows


def get_token_buckets(args, env, transmission_queue):
    token_buckets_list = []

    for index in range(args.flows):
        token_bucket = TokenBucket(env=env,
                                   identifier=f'TB_{index}',
                                   mtu=args.mtu,
                                   tokens_per_second=args.rho,
                                   bucket_capacity=args.sigma,
                                   transmission_queue=transmission_queue)
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

    file_name = build_file_name(args, env.now, new_rate)
    transmission_queue = TransmissionQueue(env=env,
                                           rate=new_rate,
                                           mtu=args.mtu,
                                           queue_capacity=args.queue_capacity,
                                           file_name=file_name)

    export_plot_rates(args, rates_list)

    return transmission_queue


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


def plot_results(env, args, transmission_queue, token_buckets):
    begin_window = env.now
    while True:
        samplings_as_csv(transmission_queue.file_name)
        yield env.timeout(args.sampling_window)
        samplings_as_png(begin_window, args.sampling_interval, transmission_queue.file_name, args.delay_sla)
        token_buckets_shaper_occupation(token_buckets, transmission_queue.file_name)
        begin_window = env.now
        transmission_queue.file_name = build_file_name(args, begin_window, transmission_queue.rate)


def sampling_transmission_queue(env, sampling_interval, transmission_queue):
    while True:
        yield env.timeout(sampling_interval)
        occupancy = transmission_queue.max_queue_occupancy
        latencies = transmission_queue.latencies
        transmission_queue.restart_samplers()
        samplings_as_csv(transmission_queue.file_name, occupancy, latencies)


def show_log(env, sampling_interval, transmission_queue, token_buckets):
    while True:
        yield env.timeout(sampling_interval)
        tb_emptying_shaper = len([tb for tb in token_buckets if tb.is_emptying_shaper])
        log(env.now, transmission_queue.max_queue_occupancy, transmission_queue.received, transmission_queue.forwarded,
            tb_emptying_shaper)

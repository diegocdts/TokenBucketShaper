import random
import time

import simpy

from helpers.arguments import arguments
from helpers.functions import get_transmission_queue, get_token_buckets, get_flows
from helpers.plots import samplings_as_png, token_buckets_shaper_occupation, plot_parameters_analysis
from helpers.processes import refill_tokens, sampling

if __name__ == "__main__":
    # arguments parse
    args = arguments()

    random.seed(args.seed)

    # creates a simpy environment
    env = simpy.Environment()

    # instantiates the token_buckets and flows lists and the transmission queue using the parsed arguments
    transmission_queue, simulation_info = get_transmission_queue(args, env)
    token_buckets = get_token_buckets(args, env, transmission_queue)
    flows = get_flows(args, env, token_buckets)

    # refill tokens
    env.process(refill_tokens(env, mtu=args.mtu, tokens_per_second=args.rho, token_buckets=flows.pre_token_buckets))
    env.process(refill_tokens(env, mtu=args.mtu, tokens_per_second=args.rho, token_buckets=token_buckets))

    # samples information from transmission_queue
    env.process(sampling(env, args, simulation_info, transmission_queue))

    env.run(until=args.max_time)

    time.sleep(1)
    samplings_as_png(args, simulation_info)
    token_buckets_shaper_occupation(token_buckets, simulation_info)
    time.sleep(1)
    plot_parameters_analysis(simulation_info)

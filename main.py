import random
import time

import simpy

from helpers.arguments import arguments
from helpers.functions import sampling_transmission_queue, instances, show_log, plot_results
from helpers.outputs import create_base_output_paths
from helpers.plots import samplings_as_png, token_buckets_shaper_occupation, full_histogram

if __name__ == "__main__":
    # arguments parse
    args = arguments()

    random.seed(args.seed)

    # creates a simpy environment
    env = simpy.Environment()

    # creates the output directories
    create_base_output_paths()

    # instantiates the token_buckets and flows lists and the transmission queue using the parsed arguments
    flows, token_buckets, transmission_queue = instances(args, env)

    # plot results
    env.process(plot_results(env, args, transmission_queue, token_buckets))

    # process log
    env.process(show_log(env, args.sampling_interval, transmission_queue, token_buckets))

    # samples information from transmission_queue
    env.process(sampling_transmission_queue(env, args.sampling_interval, transmission_queue))

    env.run(until=args.max_time)

    time.sleep(1)
    samplings_as_png(args.max_time - args.sampling_window, args.sampling_interval, transmission_queue.file_name,
                     args.delay_sla)
    token_buckets_shaper_occupation(token_buckets, transmission_queue.file_name)
    time.sleep(1)
    full_histogram(transmission_queue.file_name)

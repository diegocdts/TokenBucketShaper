from helpers.plots import samplings_as_csv, log


def sampling(env, args, simulation_info, queue_node):
    samplings_as_csv(simulation_info)
    while True:
        print('timestamp: {:.3f}'.format(env.now))
        yield env.timeout(args.sampling_interval)
        occupancy = queue_node.max_queue_occupancy
        latencies = queue_node.latencies
        queue_node.restart_samplers()
        samplings_as_csv(simulation_info, occupancy, latencies)


def refill_tokens(env, mtu, tokens_per_second, token_buckets):
    while True:
        yield env.timeout(mtu / tokens_per_second)
        for token_bucket in token_buckets:
            token_bucket.new_tokens()


def show_log(env, sampling_interval, queue_node, token_buckets):
    while True:
        yield env.timeout(sampling_interval)
        buckets_status = '|'.join(str(token_bucket.bucket) for token_bucket in token_buckets)
        log(env.now, queue_node.max_queue_occupancy, queue_node.biggest_burst,
            queue_node.num_bursts, queue_node.received, queue_node.forwarded, buckets_status)

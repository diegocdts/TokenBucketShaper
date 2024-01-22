from helpers.plots import samplings_as_csv, log


def sampling(env, args, simulation_info, transmission_queue):
    samplings_as_csv(simulation_info)
    while True:
        print('{:.3f}'.format(env.now))
        yield env.timeout(args.sampling_interval)
        occupancy = transmission_queue.max_queue_occupancy
        latencies = transmission_queue.latencies
        transmission_queue.restart_samplers()
        samplings_as_csv(simulation_info, occupancy, latencies)


def refill_tokens(env, mtu, tokens_per_second, token_buckets):
    while True:
        yield env.timeout(mtu / tokens_per_second)
        for token_bucket in token_buckets:
            token_bucket.new_tokens()


def show_log(env, sampling_interval, transmission_queue, token_buckets):
    while True:
        yield env.timeout(sampling_interval)
        buckets_status = '|'.join(str(token_bucket.bucket) for token_bucket in token_buckets)
        log(env.now, transmission_queue.max_queue_occupancy, transmission_queue.biggest_burst,
            transmission_queue.num_bursts, transmission_queue.received, transmission_queue.forwarded, buckets_status)

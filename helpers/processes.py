from helpers.plots import samplings_as_csv


def sampling(env, args, simulation_info, queue_nodes):
    for node in queue_nodes:
        samplings_as_csv(node.id, simulation_info)
    while True:
        print('timestamp: {:.3f}'.format(env.now))
        yield env.timeout(args.sampling_interval)
        for node in queue_nodes:
            occupancies = node.occupancies
            latencies = node.latencies
            node.restart_samplers()
            samplings_as_csv(node.id, simulation_info, occupancies, latencies)


def refill_tokens(env, mtu, tokens_per_second, token_buckets):
    while True:
        yield env.timeout(mtu / tokens_per_second)
        for token_bucket in token_buckets:
            token_bucket.new_tokens()

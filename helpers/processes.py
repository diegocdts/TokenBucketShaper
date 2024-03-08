from helpers.outputs import Metric, Extension


def refill_tokens(env, mtu, tokens_per_second, token_buckets):
    while True:
        yield env.timeout(mtu / tokens_per_second)
        for token_bucket in token_buckets:
            token_bucket.new_tokens()


def sampling_by_time(env, sampling_interval, simulation_info, queue_nodes):
    while True:
        yield env.timeout(sampling_interval)
        print(f'{round(env.now, 4)}')
        for node in queue_nodes:
            occupancy = len(node.queue)
            occupancy_file_path = simulation_info.get_file_metric_path(Metric.occupancy, Extension.csv, node_id=node.id,
                                                                       extra='by time')
            with open(occupancy_file_path, 'a') as file_writer:
                file_writer.write(f'{occupancy}\n')

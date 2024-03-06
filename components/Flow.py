import random

from components.TokenBucket import PreTokenBucket


class Packet:
    def __init__(self, size, now):
        self.size = size
        self.created_at = now
        self.entered_queue_at = None
        self.left_queue_at = None

    def queue_latency(self):
        if self.entered_queue_at and self.left_queue_at:
            return self.left_queue_at - self.entered_queue_at


class Flow:
    def __init__(self, env, num_flows, lambda_param, mtu, bucket_capacity, token_buckets):
        self.env = env
        self.num_flows = num_flows
        self.lambda_param = lambda_param
        self.mtu = mtu
        self.pre_token_buckets = [PreTokenBucket(env, mtu, token_bucket, bucket_capacity)
                                  for token_bucket in token_buckets]
        self.action = env.process(self.send_packet())

    def send_packet(self):
        while True:
            inter_packet_interval = random.expovariate(self.lambda_param * self.num_flows)
            flow = random.randint(0, self.num_flows - 1)
            yield self.env.timeout(inter_packet_interval)

            packet = Packet(size=self.mtu, now=self.env.now)
            self.pre_token_buckets[flow].shaping(packet)


def dictionary_uflow_node(uflows_node):
    keys = uflows_node.split(',')
    dictionary = {}
    uflow = 0
    for key in keys:
        split = key.split('_')
        number_of_uflows = int(split[0])
        node = int(split[1])
        for _ in range(number_of_uflows):
            dictionary[uflow] = node
            uflow += 1
    return dictionary


class UncontrolledFlow:
    def __init__(self, env, uflows_node, uflow_lambda_param, mtu, queue_nodes):
        self.env = env
        self.dictionary = dictionary_uflow_node(uflows_node)
        self.lambda_param = uflow_lambda_param
        self.mtu = mtu
        self.queue_nodes = queue_nodes

        self.num_uflows = len(self.dictionary)
        self.action = env.process(self.send_packet())

    def send_packet(self):
        if self.num_uflows > 0:
            while True:
                inter_packet_interval = random.expovariate(self.lambda_param * self.num_uflows)
                uflow = random.randint(0, self.num_uflows - 1)
                node_index = self.dictionary.get(uflow)
                yield self.env.timeout(inter_packet_interval)

                packet = Packet(size=self.mtu, now=self.env.now)
                self.queue_nodes[node_index].queuing_packet(packet)

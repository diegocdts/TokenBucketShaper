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
    def __init__(self, env, num_flows, lambda_param, mtu, tokens_per_second, bucket_capacity, token_buckets):
        self.env = env
        self.num_flows = num_flows
        self.lambda_param = lambda_param
        self.mtu = mtu
        self.pre_token_buckets = [PreTokenBucket(env, mtu, tokens_per_second, token_bucket, bucket_capacity)
                                  for token_bucket in token_buckets]
        self.action = env.process(self.send_packet())

    def send_packet(self):
        while True:
            inter_packet_interval = random.expovariate(self.lambda_param * self.num_flows)
            flow = random.randint(0, self.num_flows - 1)
            yield self.env.timeout(inter_packet_interval)

            packet = Packet(size=self.mtu, now=self.env.now)
            self.pre_token_buckets[flow].shaping(packet)

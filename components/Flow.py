import random


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
    def __init__(self, env, lambda_param, mtu, tokens_per_second, token_bucket):
        self.env = env
        self.lambda_param = lambda_param
        self.mtu = mtu
        self.pre_token_bucket = PreTokenBucket(env, mtu, tokens_per_second, token_bucket)
        self.action = env.process(self.send_packet())

    def send_packet(self):
        while True:
            inter_packet_interval = random.expovariate(self.lambda_param)
            yield self.env.timeout(inter_packet_interval)

            packet = Packet(size=self.mtu, now=self.env.now)
            self.pre_token_bucket.shaping(packet)


class PreTokenBucket:
    def __init__(self, env, mtu, tokens_per_second, token_bucket):
        self.env = env
        self.mtu = mtu
        self.tokens_per_second = tokens_per_second
        self.token_bucket = token_bucket
        self.shaper = []
        self.action = env.process(self.send_burst())

    def shaping(self, packet):
        self.shaper.append(packet)

    def send_burst(self):
        while True:
            burst = self.shaper
            self.shaper = []
            self.token_bucket.handle_burst(burst)
            yield self.env.timeout(self.mtu / self.tokens_per_second)

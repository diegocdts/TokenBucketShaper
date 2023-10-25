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
    def __init__(self, env, lambda_param, mtu, token_bucket):
        self.env = env
        self.lambda_param = lambda_param
        self.mtu = mtu
        self.token_bucket = token_bucket
        self.action = env.process(self.send_burst())

    def send_burst(self):
        while True:
            inter_packet_interval = random.expovariate(self.lambda_param)
            yield self.env.timeout(inter_packet_interval)

            packet = Packet(size=self.mtu, now=self.env.now)
            self.token_bucket.handle_packet(packet)

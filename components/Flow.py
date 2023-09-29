import random


class Packet:
    def __init__(self, flow, size, now):
        self.flow = flow
        self.size = size
        self.created_at = now
        self.entered_queue_at = None
        self.left_queue_at = None

    def queue_latency(self):
        if self.entered_queue_at and self.left_queue_at:
            return self.left_queue_at - self.entered_queue_at


class Flow:
    def __init__(self, env, num_flows, lambda_param, mtu, token_buckets):
        self.env = env
        self.num_flows = num_flows
        self.lambda_param = lambda_param * num_flows
        self.mtu = mtu
        self.token_buckets = token_buckets
        self.action = env.process(self.send_burst())

    def send_burst(self):
        while True:
            flow = random.randint(0, self.num_flows - 1)
            inter_packet_interval = random.expovariate(self.lambda_param)
            yield self.env.timeout(inter_packet_interval)

            packet = Packet(flow=flow, size=self.mtu, now=self.env.now)
            self.token_buckets[flow].handle_packet(packet)

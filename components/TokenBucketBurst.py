def split_burst(burst, bucket):
    burst_bytes = sum(packet.size for packet in burst)
    if burst_bytes > bucket:
        return int(len(burst) * bucket / burst_bytes)
    else:
        return len(burst)


class TokenBucket:
    def __init__(self, env, identifier, mtu, tokens_per_second, bucket_capacity, transmission_queue):
        self.env = env
        self.identifier = identifier
        self.mtu = mtu
        self.tokens_per_second = tokens_per_second
        self.bucket_capacity = bucket_capacity
        self.bucket = bucket_capacity
        self.transmission_queue = transmission_queue

        self.shaper = []
        self.shaper_occupancy = 0
        self.shaper_capacity = tokens_per_second
        self.max_shaper_occupancy = 0

        self.is_emptying_shaper = False

        self.action = env.process(self.new_tokens())

    def new_tokens(self):
        while True:
            self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
            self.empty_shaper()
            yield self.env.timeout(self.mtu / self.tokens_per_second)

    def empty_shaper(self):
        if self.shaper and self.bucket >= 0:
            split = split_burst(self.shaper, self.bucket)
            self.forward(self.shaper[:split])
            self.shaper = self.shaper[split:]

    def handle_burst(self, burst):
        split = split_burst(burst, self.bucket)
        self.forward(burst[:split])
        self.shaping(burst[split:])

    def shaping(self, burst):
        self.shaper += burst
        if len(self.shaper) > self.max_shaper_occupancy:
            self.max_shaper_occupancy = len(self.shaper)

    def forward(self, burst):
        self.bucket -= sum(packet.size for packet in burst)
        self.transmission_queue.queuing(burst)

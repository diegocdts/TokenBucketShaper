def split_burst(burst, bucket):
    burst_bytes = sum(packet.size for packet in burst)
    if burst_bytes > bucket:
        return int(len(burst) * bucket / burst_bytes)
    else:
        return len(burst)


class PreTokenBucket:
    def __init__(self, env, mtu, tokens_per_second, token_bucket, bucket_capacity):
        self.env = env
        self.mtu = mtu
        self.tokens_per_second = tokens_per_second
        self.token_bucket = token_bucket
        self.bucket_capacity = bucket_capacity
        self.bucket = bucket_capacity
        self.shaper = []
        self.shaper_capacity = int(tokens_per_second / mtu)
        self.action = self.env.process(self.new_tokens())

    def new_tokens(self):
        while True:
            self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
            self.send_burst()
            yield self.env.timeout(self.mtu / self.tokens_per_second)

    def shaping(self, packet):
        if self.shaper_capacity > len(self.shaper):
            self.shaper.append(packet)

    def send_burst(self):
        if self.shaper and self.bucket >= 0:
            split = split_burst(self.shaper, self.bucket)
            if split > 0:
                self.token_bucket.handle_burst(self.shaper[:split])
                self.shaper = self.shaper[split:]


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
        self.shaper_capacity = int(tokens_per_second / mtu)
        self.max_shaper_occupancy = 0

        self.action = env.process(self.new_tokens())

    def new_tokens(self):
        while True:
            self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
            self.empty_shaper()
            yield self.env.timeout(self.mtu / self.tokens_per_second)

    def empty_shaper(self):
        if self.shaper and self.bucket >= 0:
            split = split_burst(self.shaper, self.bucket)
            if split > 0:
                self.forward(self.shaper[:split])
                self.shaper = self.shaper[split:]

    def handle_burst(self, burst):
        if self.shaper or self.bucket == 0:
            self.shaping(burst)
        else:
            split = split_burst(burst, self.bucket)
            if split > 0:
                self.forward(burst[:split])
            self.shaping(burst[split:])

    def shaping(self, burst):
        if burst:
            split = self.shaper_capacity - len(self.shaper)
            burst = burst[:split]
            self.shaper += burst
            if len(self.shaper) > self.max_shaper_occupancy:
                self.max_shaper_occupancy = len(self.shaper)

    def forward(self, burst):
        self.bucket -= sum(packet.size for packet in burst)
        self.transmission_queue.queuing(burst)

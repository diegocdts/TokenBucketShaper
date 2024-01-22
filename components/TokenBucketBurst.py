def split_burst(burst, bucket):
    to_send = []
    while burst and bucket >= burst[0].size:
        to_send.append(burst.pop(0))
    to_keep = burst
    return to_send, to_keep


class PreTokenBucket:
    def __init__(self, env, mtu, tokens_per_second, token_bucket, bucket_capacity):
        self.env = env
        self.mtu = mtu
        self.token_bucket = token_bucket
        self.bucket_capacity = bucket_capacity
        self.bucket = bucket_capacity
        self.shaper = []
        self.shaper_capacity = int(tokens_per_second / mtu)

    def new_tokens(self):
        self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
        self.send_burst()

    def shaping(self, packet):
        if self.shaper_capacity > len(self.shaper):
            self.shaper.append(packet)

    def send_burst(self):
        if self.shaper and self.bucket >= 0:
            to_send, to_keep = split_burst(self.shaper, self.bucket)
            if to_send:
                self.token_bucket.handle_burst(to_send)
                self.shaper = to_keep


class TokenBucket:
    def __init__(self, env, identifier, mtu, tokens_per_second, bucket_capacity, transmission_queue):
        self.env = env
        self.identifier = identifier
        self.mtu = mtu
        self.bucket_capacity = bucket_capacity
        self.bucket = bucket_capacity
        self.transmission_queue = transmission_queue

        self.shaper = []
        self.shaper_capacity = int(tokens_per_second / mtu)
        self.max_shaper_occupancy = 0

    def new_tokens(self):
        self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
        self.empty_shaper()

    def empty_shaper(self):
        if self.shaper and self.bucket >= 0:
            to_send, to_keep = split_burst(self.shaper, self.bucket)
            if to_send:
                self.forward(to_send)
                self.shaper = to_keep

    def handle_burst(self, burst):
        if self.shaper or self.bucket == 0:
            self.shaping(burst)
        else:
            to_send, to_keep = split_burst(burst, self.bucket)
            if to_send:
                self.forward(to_send)
            self.shaping(to_keep)

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

def split_burst(burst, bucket):
    to_send = []
    while burst and bucket >= burst[0].size:
        packet = burst.pop(0)
        bucket -= packet.size
        to_send.append(packet)
    to_keep = burst
    return to_send, to_keep


class PreTokenBucket:
    def __init__(self, env, mtu, token_bucket, bucket_capacity):
        self.env = env
        self.mtu = mtu
        self.bucket = bucket_capacity
        self.bucket_capacity = bucket_capacity
        self.token_bucket = token_bucket
        self.shaper = []
        self.max_shaper_occupancy = 0

    def new_tokens(self):
        self.bucket = self.bucket + self.mtu
        self.send_burst()

    def shaping(self, packet):
        self.shaper.append(packet)
        if len(self.shaper) > self.max_shaper_occupancy:
            self.max_shaper_occupancy = len(self.shaper)

    def send_burst(self):
        to_send, to_keep = split_burst(self.shaper, self.bucket)
        if to_send:
            self.shaper = to_keep
            self.bucket -= sum(packet.size for packet in to_send)
            self.token_bucket.handle_burst(to_send)


class TokenBucket:
    def __init__(self, env, identifier, mtu, tokens_per_second, bucket_capacity, queue_node):
        self.env = env
        self.identifier = identifier
        self.mtu = mtu
        self.bucket_capacity = bucket_capacity
        self.bucket = bucket_capacity
        self.queue_node = queue_node

        self.shaper = []
        self.shaper_capacity = int(tokens_per_second / mtu)
        self.max_shaper_occupancy = 0

    def new_tokens(self):
        self.bucket = min(self.bucket + self.mtu, self.bucket_capacity)
        self.empty_shaper()

    def empty_shaper(self):
        to_send, to_keep = split_burst(self.shaper, self.bucket)
        if to_send:
            self.shaper = to_keep
            self.forward(to_send)

    def handle_burst(self, burst):
        if self.shaper or self.bucket < burst[0].size:
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
        self.queue_node.queuing_burst(burst)

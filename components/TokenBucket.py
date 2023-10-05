
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
        if self.shaper and self.bucket >= self.shaper[0].size:
            self.is_emptying_shaper = True
            packet = self.shaper.pop(0)
            self.forward(packet)
        else:
            self.is_emptying_shaper = False

    def handle_packet(self, packet):
        if self.shaper or self.bucket < packet.size:
            self.shaping(packet)
        else:
            self.forward(packet)

    def shaping(self, packet):
        if self.shaper_capacity - len(self.shaper) >= packet.size:
            self.shaper.append(packet)
            if len(self.shaper) > self.max_shaper_occupancy:
                self.max_shaper_occupancy = len(self.shaper)

    def forward(self, packet):
        self.bucket -= packet.size
        self.transmission_queue.queuing(packet)

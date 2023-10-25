class TransmissionQueue:

    def __init__(self, env, rate, mtu, queue_capacity, file_name):
        self.env = env
        self.rate = rate
        self.mtu = mtu
        self.queue_capacity = queue_capacity
        self.file_name = file_name

        self.received = 0
        self.forwarded = 0

        self.queue = []
        self.max_queue_occupancy = 0

        self.latencies = []

        self.action = env.process(self.un_queuing())

    def queuing(self, burst):
        [packet.__setattr__('entered_queue_at', self.env.now) for packet in burst]
        self.queue += burst
        self.update_max_queue_occupancy()
        self.received += 1
        if not self.action.is_alive:
            self.action = self.env.process(self.un_queuing())

    def un_queuing(self):
        while self.queue:
            packet = self.queue.pop(0)
            yield self.env.timeout(packet.size / self.rate)
            self.set_packet_latency(packet)
            self.forwarded += 1

    def set_packet_latency(self, packet):
        packet.left_queue_at = self.env.now
        self.latencies.append(packet.queue_latency())

    def update_max_queue_occupancy(self):
        if len(self.queue) > self.max_queue_occupancy:
            self.max_queue_occupancy = len(self.queue)

    def restart_samplers(self):
        self.max_queue_occupancy = 0
        self.latencies = []

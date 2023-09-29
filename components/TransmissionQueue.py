class TransmissionQueue:

    def __init__(self, env, rate, mtu, max_queue_occupancy, file_name):
        self.env = env
        self.rate = rate
        self.mtu = mtu
        self.max_queue_occupancy = max_queue_occupancy
        self.file_name = file_name

        self.received = 0
        self.forwarded = 0

        self.queue = []
        self.queue_occupancy = 0

        self.latencies = []

        self.action = env.process(self.un_queuing())

    def queuing(self, packet):
        if self.max_queue_occupancy - self.queue_occupancy >= packet.size:
            packet.entered_queue_at = self.env.now
            self.queue.append(packet)
            self.queue_occupancy += 1
            self.received += 1
            if not self.action.is_alive:
                self.action = self.env.process(self.un_queuing())

    def un_queuing(self):
        while self.queue:
            packet = self.queue.pop(0)
            self.prepare_to_forward(packet)
            yield self.env.timeout(packet.size / self.rate)
            self.queue_occupancy -= 1
            self.forwarded += 1

    def prepare_to_forward(self, packet):
        packet.left_queue_at = self.env.now
        self.latencies.append(packet.queue_latency())

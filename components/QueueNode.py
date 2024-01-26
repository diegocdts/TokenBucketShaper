class QueueNode:

    def __init__(self, identifier, env, rate, mtu, queue_capacity, next_node=None):
        self.id = identifier
        self.env = env
        self.rate = rate
        self.mtu = mtu
        self.queue_capacity = queue_capacity
        self.next_node = next_node

        self.queue = []
        self.biggest_burst = 0
        self.num_bursts = 0

        self.occupancies = []
        self.latencies = []

        self.action = env.process(self.un_queuing())

    def queuing_packet(self, packet):
        packet.entered_queue_at = self.env.now
        self.queue.append(packet)
        self.sample_queue_occupancy()
        if not self.action.is_alive:
            self.action = self.env.process(self.un_queuing())

    def queuing_burst(self, burst):
        [packet.__setattr__('entered_queue_at', self.env.now) for packet in burst]
        self.queue += burst
        self.sample_queue_occupancy()
        if not self.action.is_alive:
            self.action = self.env.process(self.un_queuing())

    def un_queuing(self):
        while self.queue:
            packet = self.queue.pop(0)
            yield self.env.timeout(packet.size / self.rate)
            self.set_packet_latency(packet)
            if self.next_node:
                self.next_node.queuing_packet(packet)

    def set_packet_latency(self, packet):
        packet.left_queue_at = self.env.now
        self.latencies.append(packet.queue_latency())

    def sample_queue_occupancy(self):
        self.occupancies.append(len(self.queue))

    def restart_samplers(self):
        self.biggest_burst = 0
        self.num_bursts = 0
        self.occupancies = []
        self.latencies = []

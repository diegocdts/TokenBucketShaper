class QueueNode:

    def __init__(self, identifier, env, rate, mtu, queue_capacity, next_node=None):
        self.id = identifier
        self.env = env
        self.rate = rate
        self.mtu = mtu
        self.queue_capacity = queue_capacity
        self.next_node = next_node

        self.received = 0
        self.forwarded = 0

        self.queue = []
        self.max_queue_occupancy = 0
        self.biggest_burst = 0
        self.num_bursts = 0

        self.latencies = []

        self.action = env.process(self.un_queuing())

    def queuing_packet(self, packet):
        self.queue.append(packet)
        self.update_max_queue_occupancy()
        self.received += 1
        if not self.action.is_alive:
            self.action = self.env.process(self.un_queuing())

    def queuing_burst(self, burst):
        [packet.__setattr__('entered_queue_at', self.env.now) for packet in burst]
        self.queue += burst
        self.update_biggest_burst(len(burst))
        self.update_max_queue_occupancy()
        self.received += len(burst)
        if not self.action.is_alive:
            self.action = self.env.process(self.un_queuing())

    def un_queuing(self):
        while self.queue:
            packet = self.queue.pop(0)
            yield self.env.timeout(packet.size / self.rate)
            self.set_packet_latency(packet)
            self.forwarded += 1
            if self.next_node:
                self.next_node.queuing_packet(packet)

    def set_packet_latency(self, packet):
        packet.left_queue_at = self.env.now
        self.latencies.append(packet.queue_latency())

    def update_max_queue_occupancy(self):
        if len(self.queue) > self.max_queue_occupancy:
            self.max_queue_occupancy = len(self.queue)

    def restart_samplers(self):
        self.max_queue_occupancy = 0
        self.biggest_burst = 0
        self.num_bursts = 0
        self.latencies = []

    def update_biggest_burst(self, burst_size):
        if burst_size > self.biggest_burst:
            self.biggest_burst = burst_size
        if burst_size > 1:
            self.num_bursts += 1

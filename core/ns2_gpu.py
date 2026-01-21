from dataclasses import dataclass
from typing import List, Deque
from collections import deque


@dataclass
class GPUFence:
    signaled: bool = False


@dataclass
class GPUCommand:
    name: str
    cost_cycles: int
    fence: GPUFence | None = None


class GPUQueue:
    def __init__(self, max_in_flight: int):
        self.queue: Deque[GPUCommand] = deque()
        self.in_flight: List[GPUCommand] = []
        self.max_in_flight = max_in_flight

    def submit(self, cmd: GPUCommand):
        self.queue.append(cmd)

    def tick(self):
        # Move commands into execution
        while self.queue and len(self.in_flight) < self.max_in_flight:
            self.in_flight.append(self.queue.popleft())

        # Execute commands
        finished: List[GPUCommand] = []
        for cmd in self.in_flight:
            cmd.cost_cycles -= 1
            if cmd.cost_cycles <= 0:
                finished.append(cmd)

        for cmd in finished:
            self.in_flight.remove(cmd)
            if cmd.fence:
                cmd.fence.signaled = True


class NS2GPU:
    """
    NS2-shaped GPU model:
    - graphics queue
    - async compute queue
    - fence-based synchronization
    """

    def __init__(self, max_in_flight: int):
        self.graphics = GPUQueue(max_in_flight)
        self.compute = GPUQueue(max_in_flight)

    def submit_graphics(self, name: str, cycles: int) -> GPUFence:
        fence = GPUFence()
        self.graphics.submit(GPUCommand(name, cycles, fence))
        return fence

    def submit_compute(self, name: str, cycles: int) -> GPUFence:
        fence = GPUFence()
        self.compute.submit(GPUCommand(name, cycles, fence))
        return fence

    def tick(self):
        self.graphics.tick()
        self.compute.tick()

class Scheduler:
    def __init__(self):
        self.cpu = 0
        self.gpu = 0

    def tick_cpu(self, n: int):
        self.cpu += n

    def tick_gpu(self, n: int):
        self.gpu += n

    def should_sync(self) -> bool:
        return abs(self.cpu - self.gpu) > 10_000

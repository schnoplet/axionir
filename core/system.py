from .cpu import CPUState, MMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import HotBlockProfiler, TraceCache
from .scheduler import Scheduler
from .gpu_ir import GPUCommandBuffer


class Dispatcher:
    def __init__(self, interp, opt, profiler, trace_cache):
        self.interp = interp
        self.opt = opt
        self.profiler = profiler
        self.trace_cache = trace_cache

    def run(self, block):
        key = block.hash()

        # Run existing trace if present
        if self.trace_cache.has(key):
            for b in self.trace_cache.get(key):
                self.interp.exec_block(b)
            return

        # Normal execution
        self.interp.exec_block(block)

        # Hot block → trace growth
        if self.profiler.record(block):
            optimized = self.opt.optimize(block)
            self.trace_cache.start_or_extend(key, optimized)


class AxionIRSystem:
    def __init__(self):
        self.mmu = MMU()
        self.cpu_state = CPUState()

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.optimizer = IROptimizer()

        self.profiler = HotBlockProfiler()
        self.trace_cache = TraceCache()

        self.dispatcher = Dispatcher(
            self.interp,
            self.optimizer,
            self.profiler,
            self.trace_cache,
        )

        self.scheduler = Scheduler()
        self.gpu = GPUCommandBuffer()

    def run_block(self, block):
        self.dispatcher.run(block)
        self.scheduler.tick_cpu(len(block))

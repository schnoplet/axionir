from .cpu import CPUState, ShadowMMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import HotBlockProfiler, TraceCache
from .scheduler import Scheduler
from .ns2_profile import NS2Profile
from .ns2_gpu import NS2GPU, GPUFence


class Dispatcher:
    def __init__(self, interp, opt, profiler, trace_cache, cpu_state, mmu):
        self.interp = interp
        self.opt = opt
        self.profiler = profiler
        self.trace_cache = trace_cache
        self.cpu_state = cpu_state
        self.mmu = mmu

    def run(self, block):
        key = block.hash()

        # speculative trace execution
        if self.trace_cache.has(key):
            snap = self.cpu_state.snapshot()
            self.mmu.begin_epoch()

            ok = True
            for b in self.trace_cache.get(key):
                if not self.interp.exec_block(b):
                    ok = False
                    break

            if ok:
                self.mmu.commit_epoch()
                return
            else:
                self.cpu_state.restore(snap)
                self.mmu.rollback_epoch()

        # normal execution
        self.mmu.begin_epoch()
        self.interp.exec_block(block)
        self.mmu.commit_epoch()

        # hot path → trace
        if self.profiler.record(block):
            optimized = self.opt.optimize(block)
            self.trace_cache.start_or_extend(key, optimized)


class AxionIRSystem:
    """
    3rd-class NS2 emulator:
    - NS2-shaped CPU/GPU/memory
    - async GPU
    - CPU↔GPU fence synchronization
    """

    def __init__(self, profile: NS2Profile | None = None):
        self.profile = profile or NS2Profile()

        # CPU + memory
        self.cpu_state = CPUState(
            reg_count=self.profile.cpu.registers
        )
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024
        )

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.optimizer = IROptimizer()

        self.profiler = HotBlockProfiler()
        self.trace_cache = TraceCache()

        self.dispatcher = Dispatcher(
            self.interp,
            self.optimizer,
            self.profiler,
            self.trace_cache,
            self.cpu_state,
            self.mmu,
        )

        self.scheduler = Scheduler()

        # NS2 GPU
        self.gpu = NS2GPU(
            max_in_flight=self.profile.gpu.max_in_flight_cmds
        )

        print("[AxionIR] Booted", self.profile.describe())

    def submit_gpu_work(self, name: str, cycles: int) -> GPUFence:
        return self.gpu.submit_graphics(name, cycles)

    def wait_for_fence(self, fence: GPUFence):
        """
        CPU stall until GPU fence is signaled.
        This is real console behavior.
        """
        while not self.gpu.is_fence_signaled(fence):
            self.scheduler.tick_cpu(1)
            self.gpu.tick()

    def run_block(self, block):
        self.dispatcher.run(block)
        self.scheduler.tick_cpu(len(block))
        self.gpu.tick()

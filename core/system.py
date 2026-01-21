from .cpu import CPUState, ShadowMMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import HotBlockProfiler, TraceCache
from .scheduler import Scheduler
from .gpu_ir import GPUCommandBuffer
from .ns2_profile import NS2Profile


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
    AxionIR bound to an NS2-shaped system profile.
    This is a 3rd-class emulator: hardware-shaped, firmware-free.
    """

    def __init__(self, profile: NS2Profile | None = None):
        self.profile = profile or NS2Profile()

        # CPU + memory shaped by NS2 profile
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
        self.gpu = GPUCommandBuffer()

        # Debug / introspection hook
        print("[AxionIR] Booted", self.profile.describe())

    def run_block(self, block):
        self.dispatcher.run(block)
        self.scheduler.tick_cpu(len(block))

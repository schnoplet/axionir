from .cpu import CPUState, ShadowMMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import HotBlockProfiler, TraceCache
from .scheduler import Scheduler
from .ns2_profile import NS2Profile, NS2Mode
from .ns2_gpu import NS2GPU, GPUFence
from .ns2_display import NS2Display, VSyncFence


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

        self.mmu.begin_epoch()
        self.interp.exec_block(block)
        self.mmu.commit_epoch()

        if self.profiler.record(block):
            optimized = self.opt.optimize(block)
            self.trace_cache.start_or_extend(key, optimized)


class AxionIRSystem:
    """
    3rd-class NS2 emulator:
    - docked / handheld modes
    - CPU/GPU/display behavior changes with mode
    """

    def __init__(self, profile: NS2Profile | None = None):
        self.profile = profile or NS2Profile()

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

        self.gpu = NS2GPU(
            max_in_flight=self.profile.gpu_in_flight()
        )
        self.display = NS2Display(
            refresh_hz=self.profile.refresh_hz()
        )

        print("[AxionIR] Booted", self.profile.describe())

    # -----------------------------
    # Mode control (REAL NS2 behavior)
    # -----------------------------

    def set_mode(self, mode: NS2Mode):
        if self.profile.mode == mode:
            return

        self.profile.mode = mode

        # Update GPU + display characteristics
        self.gpu = NS2GPU(
            max_in_flight=self.profile.gpu_in_flight()
        )
        self.display = NS2Display(
            refresh_hz=self.profile.refresh_hz()
        )

        print("[AxionIR] Switched to", self.profile.mode.value.upper())

    # -----------------------------
    # GPU / Display interaction
    # -----------------------------

    def submit_gpu_work(self, name: str, cycles: int) -> GPUFence:
        return self.gpu.submit_graphics(name, cycles)

    def wait_for_fence(self, fence: GPUFence):
        while not fence.signaled:
            self.scheduler.tick_cpu(1)
            self.gpu.tick()
            self.display.tick(1)

    def present_frame(self) -> VSyncFence:
        return self.display.present()

    def wait_for_vsync(self, fence: VSyncFence):
        while not fence.signaled:
            self.scheduler.tick_cpu(1)
            self.gpu.tick()
            self.display.tick(1)

    # -----------------------------
    # CPU execution
    # -----------------------------

    def run_block(self, block):
        self.dispatcher.run(block)

        # CPU time advances differently depending on mode
        cpu_cycles = len(block)
        if self.profile.mode == NS2Mode.HANDHELD:
            cpu_cycles *= 2  # lower freq → slower progress

        self.scheduler.tick_cpu(cpu_cycles)
        self.gpu.tick()
        self.display.tick(cpu_cycles)

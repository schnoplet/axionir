from .cpu import CPUState, ShadowMMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import HotBlockProfiler, TraceCache
from .scheduler import Scheduler
from .ns2_profile import NS2Profile, NS2Mode
from .ns2_gpu import NS2GPU, GPUFence
from .ns2_display import NS2Display, VSyncFence
from .elf_loader import ELF64Loader
from .arm64_cpu import ARM64CPU


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

        # Try speculative trace
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

        # Normal execution
        self.mmu.begin_epoch()
        self.interp.exec_block(block)
        self.mmu.commit_epoch()

        # Hot path → trace
        if self.profiler.record(block):
            optimized = self.opt.optimize(block)
            self.trace_cache.start_or_extend(key, optimized)


class AxionIRSystem:
    """
    REAL NS2 emulator core.
    This is no longer a simulator.
    It loads real ELF binaries and executes ARM64 instructions.
    """

    def __init__(self, profile: NS2Profile | None = None):
        self.profile = profile or NS2Profile()

        # Convert GB/s → bytes per frame slice (60 Hz)
        bandwidth_bytes = int(
            (self.profile.memory.bandwidth_gbps * 1e9) / 60
        )

        # -------------------------
        # CPU + Memory
        # -------------------------

        self.cpu_state = CPUState(
            reg_count=self.profile.cpu.registers
        )

        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=bandwidth_bytes,
        )

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.optimizer = IROptimizer()

        # ARM64 frontend
        self.arm64 = ARM64CPU(self.cpu_state, self.mmu)

        # -------------------------
        # Execution infrastructure
        # -------------------------

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

        # -------------------------
        # GPU + Display
        # -------------------------

        self.gpu = NS2GPU(
            max_in_flight=self.profile.gpu_in_flight()
        )

        self.display = NS2Display(
            refresh_hz=self.profile.refresh_hz()
        )

        # -------------------------
        # ELF loader
        # -------------------------

        self.elf = ELF64Loader(self.mmu)

        print("[AxionIR] Booted", self.profile.describe())

    # =====================================================
    # ELF LOADING (REAL SOFTWARE)
    # =====================================================

    def load_elf(self, path: str):
        entry = self.elf.load(path)
        self.cpu_state.pc = entry
        print(f"[AxionIR] ELF loaded, entry @ 0x{entry:x}")

    # =====================================================
    # ARM64 EXECUTION
    # =====================================================

    def step_arm64(self):
        """
        Fetch, decode, translate, execute ONE ARM64 instruction.
        """
        opcode = self.arm64.fetch()
        block = self.arm64.decode_to_ir(opcode)
        self.run_block(block)

    def run_arm64(self, max_steps: int = 1_000_000):
        """
        Execute ARM64 instructions until stopped or max_steps reached.
        """
        for _ in range(max_steps):
            self.step_arm64()

    # =====================================================
    # GPU / DISPLAY SYNC
    # =====================================================

    def submit_gpu_work(self, name: str, cycles: int) -> GPUFence:
        return self.gpu.submit_graphics(name, cycles)

    def wait_for_fence(self, fence: GPUFence):
        while not fence.signaled:
            self.scheduler.tick_cpu(1)
            self.gpu.tick()
            self.display.tick(1)
            self.mmu.reset_bandwidth()

    def present_frame(self) -> VSyncFence:
        return self.display.present()

    def wait_for_vsync(self, fence: VSyncFence):
        while not fence.signaled:
            self.scheduler.tick_cpu(1)
            self.gpu.tick()
            self.display.tick(1)
            self.mmu.reset_bandwidth()

    # =====================================================
    # IR EXECUTION
    # =====================================================

    def run_block(self, block):
        self.dispatcher.run(block)

        cpu_cycles = len(block)
        if self.profile.mode == NS2Mode.HANDHELD:
            cpu_cycles *= 2

        self.scheduler.tick_cpu(cpu_cycles)
        self.gpu.tick()
        self.display.tick(cpu_cycles)
        self.mmu.reset_bandwidth()

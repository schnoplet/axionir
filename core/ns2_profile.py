from dataclasses import dataclass, field


# =============================
# NS2 SYSTEM PROFILE
# =============================
# NS2-shaped hardware model.
# Firmware-free, legally clean.
# =============================


@dataclass
class NS2CPUProfile:
    arch: str = "ARMv8-A"
    cores: int = 8
    registers: int = 32
    base_freq_mhz: int = 1000      # handheld-ish
    docked_freq_mhz: int = 1800    # docked-ish


@dataclass
class NS2GPUProfile:
    queues: int = 2                # graphics + async compute
    unified_memory: bool = True
    max_in_flight_cmds: int = 64
    tile_based: bool = True        # important console assumption


@dataclass
class NS2MemoryProfile:
    total_mb: int = 12 * 1024      # 12 GB class
    cpu_gpu_shared: bool = True
    page_size: int = 4096
    bandwidth_gbps: int = 100      # simulated constraint


@dataclass
class NS2Profile:
    cpu: NS2CPUProfile = field(default_factory=NS2CPUProfile)
    gpu: NS2GPUProfile = field(default_factory=NS2GPUProfile)
    memory: NS2MemoryProfile = field(default_factory=NS2MemoryProfile)

    def describe(self) -> str:
        return (
            f"NS2Profile("
            f"CPU={self.cpu.cores}x{self.cpu.arch}@{self.cpu.base_freq_mhz}MHz, "
            f"GPU_queues={self.gpu.queues}, "
            f"RAM={self.memory.total_mb}MB"
            f")"
        )

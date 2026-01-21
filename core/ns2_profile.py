from dataclasses import dataclass


# =============================
# NS2 SYSTEM PROFILE
# =============================
# This file defines an NS2-shaped hardware model.
# It does NOT emulate firmware or proprietary behavior.
# It exists to give AxionIR a realistic console profile.
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
    tile_based: bool = True        # very important assumption


@dataclass
class NS2MemoryProfile:
    total_mb: int = 12 * 1024      # 12 GB class
    cpu_gpu_shared: bool = True
    page_size: int = 4096
    bandwidth_gbps: int = 100      # simulated constraint


@dataclass
class NS2Profile:
    cpu: NS2CPUProfile = NS2CPUProfile()
    gpu: NS2GPUProfile = NS2GPUProfile()
    memory: NS2MemoryProfile = NS2MemoryProfile()

    def describe(self) -> str:
        return (
            f"NS2Profile("
            f"CPU={self.cpu.cores}x{self.cpu.arch}@{self.cpu.base_freq_mhz}MHz, "
            f"GPU_queues={self.gpu.queues}, "
            f"RAM={self.memory.total_mb}MB"
            f")"
        )

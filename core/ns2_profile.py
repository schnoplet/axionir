from dataclasses import dataclass, field
from enum import Enum


class NS2Mode(Enum):
    HANDHELD = "handheld"
    DOCKED = "docked"


@dataclass
class NS2CPUProfile:
    arch: str = "ARMv8-A"
    cores: int = 8
    registers: int = 32
    handheld_freq_mhz: int = 1000
    docked_freq_mhz: int = 1800


@dataclass
class NS2GPUProfile:
    unified_memory: bool = True
    handheld_in_flight: int = 32
    docked_in_flight: int = 64
    tile_based: bool = True


@dataclass
class NS2MemoryProfile:
    total_mb: int = 12 * 1024
    cpu_gpu_shared: bool = True
    page_size: int = 4096
    bandwidth_gbps: int = 100


@dataclass
class NS2Profile:
    cpu: NS2CPUProfile = field(default_factory=NS2CPUProfile)
    gpu: NS2GPUProfile = field(default_factory=NS2GPUProfile)
    memory: NS2MemoryProfile = field(default_factory=NS2MemoryProfile)
    mode: NS2Mode = NS2Mode.HANDHELD

    def cpu_freq(self) -> int:
        return (
            self.cpu.docked_freq_mhz
            if self.mode == NS2Mode.DOCKED
            else self.cpu.handheld_freq_mhz
        )

    def gpu_in_flight(self) -> int:
        return (
            self.gpu.docked_in_flight
            if self.mode == NS2Mode.DOCKED
            else self.gpu.handheld_in_flight
        )

    def refresh_hz(self) -> int:
        return 60

    def describe(self) -> str:
        return (
            f"NS2Profile("
            f"mode={self.mode.value}, "
            f"CPU={self.cpu.cores}x{self.cpu.arch}@{self.cpu_freq()}MHz, "
            f"GPU_in_flight={self.gpu_in_flight()}, "
            f"RAM={self.memory.total_mb}MB"
            f")"
        )

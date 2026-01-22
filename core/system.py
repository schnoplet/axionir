from core.cpu import CPUState, ShadowMMU, IRInterpreter
from core.arm64_cpu import ARM64CPU
from core.elf_loader import ELF64Loader
from core.ns2_profile import NS2Profile
from core.service_manager import ServiceManager
from core.process_manager import ProcessManager
from core.vfs import VirtualFileSystem

from core.services.time_service import TimeService
from core.services.process_service import ProcessService
from core.services.fs_service import FileSystemService

from core.boot.boot_manager import BootManager
from core.boot.module_loader import ModuleLoader


class AxionIRSystem:
    def __init__(self, profile=None, fs_root="ns2_fs"):
        self.profile = profile or NS2Profile()

        self.cpu_state = CPUState()
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=0,
        )

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.arm64 = ARM64CPU(self.cpu_state, self.mmu)
        self.elf = ELF64Loader(self.mmu)

        self.vfs = VirtualFileSystem(fs_root)

        self.process_manager = ProcessManager()
        self.services = ServiceManager()

        self.services.register("time", TimeService())
        self.services.register("fs", FileSystemService(self.vfs))

        self.module_loader = ModuleLoader(self.elf, self.vfs)
        self.boot_manager = BootManager(self)

        print("[AxionIR] Booted", self.profile.describe())
        print("[AxionIR] FS root:", fs_root)

    def boot_ns2(self):
        self.boot_manager.boot_ns2()

    def run(self):
        # Execution loop placeholder — scheduler comes later
        pass

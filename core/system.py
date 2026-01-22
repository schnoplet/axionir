from core.cpu import CPUState, ShadowMMU, IRInterpreter
from core.arm64_cpu import ARM64CPU
from core.elf_loader import ELF64Loader
from core.ns2_profile import NS2Profile

from core.service_manager import ServiceManager
from core.process_manager import ProcessManager
from core.ipc import IPCMessage
from core.vfs import VirtualFileSystem

from core.services.time_service import TimeService
from core.services.process_service import ProcessService
from core.services.fs_service import FileSystemService

from core.boot.boot_manager import BootManager
from core.boot.module_loader import ModuleLoader

from core.display.framebuffer import Framebuffer
from core.display.host_window import HostWindow
from core.display.vi_service import VIService

from core.kernel.memory import VirtualMemoryManager
from core.kernel.abi import KernelABI


class AxionIRSystem:
    # existing SVCs
    SVC_IPC = 0x1000
    SVC_GET_SERVICE = 0x1001

    def __init__(self, profile=None, fs_root="ns2_fs"):
        self.profile = profile or NS2Profile()

        self.cpu_state = CPUState()
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=0,
        )

        self.interpreter = IRInterpreter(self.cpu_state, self.mmu)
        self.cpu = ARM64CPU(self.cpu_state, self.mmu)
        self.elf_loader = ELF64Loader(self.mmu)

        self.vfs = VirtualFileSystem(fs_root)

        self.process_manager = ProcessManager()
        self.services = ServiceManager()

        # kernel
        self.vmm = VirtualMemoryManager()
        self.kernel = KernelABI(self)

        # display
        self.framebuffer = Framebuffer()
        self.window = HostWindow(self.framebuffer)

        # services
        self.services.register("time", TimeService())
        self.services.register("fs", FileSystemService(self.vfs))
        self.services.register("vi", VIService(self.framebuffer))

        self.module_loader = ModuleLoader(self.elf_loader, self.vfs)
        self.boot_manager = BootManager(self)

        print("[AxionIR] Booted", self.profile.describe())
        print("[AxionIR] FS root:", fs_root)

    def run(self):
        while True:
            opcode = self.cpu.fetch()
            block = self.cpu.decode_to_ir(opcode)

            for ins in block.instructions:
                if ins.op.name == "SVC":
                    svc = self.cpu_state.read_reg(8)

                    # kernel ABI first
                    handled = self.kernel.handle(svc)
                    if handled is not False:
                        continue

                    # existing services
                    if svc == self.SVC_GET_SERVICE:
                        self.svc_get_service()
                        continue

                    if svc == self.SVC_IPC:
                        self.svc_ipc()
                        continue

                self.interpreter.exec(ins)

            self.window.update()

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


class AxionIRSystem:
    # SVC numbers (kernel ABI surface)
    SVC_IPC = 0x1000
    SVC_GET_SERVICE = 0x1001

    def __init__(self, profile=None, fs_root="ns2_fs"):
        # -------------------------
        # Hardware profile
        # -------------------------
        self.profile = profile or NS2Profile()

        # -------------------------
        # CPU + memory
        # -------------------------
        self.cpu_state = CPUState()
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=0,
        )

        self.interpreter = IRInterpreter(self.cpu_state, self.mmu)
        self.cpu = ARM64CPU(self.cpu_state, self.mmu)
        self.elf_loader = ELF64Loader(self.mmu)

        # -------------------------
        # Filesystem (user-provided dumps)
        # -------------------------
        self.vfs = VirtualFileSystem(fs_root)

        # -------------------------
        # Process + service managers
        # -------------------------
        self.process_manager = ProcessManager()
        self.services = ServiceManager()

        # -------------------------
        # Display pipeline (real surface)
        # -------------------------
        self.framebuffer = Framebuffer()
        self.window = HostWindow(self.framebuffer)

        # -------------------------
        # Core services (NS2 architecture)
        # -------------------------
        self.services.register("time", TimeService())
        self.services.register("fs", FileSystemService(self.vfs))
        self.services.register("vi", VIService(self.framebuffer))

        # -------------------------
        # Boot infrastructure
        # -------------------------
        self.module_loader = ModuleLoader(self.elf_loader, self.vfs)
        self.boot_manager = BootManager(self)

        print("[AxionIR] Booted", self.profile.describe())
        print("[AxionIR] FS root:", fs_root)
        print("[AxionIR] Services:", self.services.list_services())

    # ============================================================
    # Kernel service lookup (NS2-style)
    # ============================================================
    def svc_get_service(self):
        """
        X1 = service ID (temporary numeric mapping)
        returns handle in X0
        """
        service_map = {
            1: "time",
            2: "process",
            3: "fs",
            4: "vi",
        }

        sid = self.cpu_state.read_reg(1)
        name = service_map.get(sid, f"unknown_{sid}")

        proc = self.process_manager.system_process()
        if proc is None:
            raise RuntimeError("No system process available")

        handle = proc.new_handle(name)
        print(f"[AxionIR][SVC] get_service '{name}' → handle {handle}")

        self.cpu_state.write_reg(0, handle)

    # ============================================================
    # Kernel IPC handler
    # ============================================================
    def svc_ipc(self):
        """
        X0 = service handle
        X1 = command id
        X2 = message data (opaque for now)
        """
        proc = self.process_manager.system_process()
        if proc is None:
            raise RuntimeError("No system process available")

        handle = self.cpu_state.read_reg(0)
        cmd = self.cpu_state.read_reg(1)
        data = self.cpu_state.read_reg(2)

        service_name = proc.get_handle(handle)
        if service_name is None:
            raise RuntimeError(f"Invalid service handle {handle}")

        msg = IPCMessage(cmd, data)
        self.services.dispatch(service_name, msg)

        # success
        self.cpu_state.write_reg(0, 0)

    # ============================================================
    # NS2 boot entrypoint
    # ============================================================
    def boot_ns2(self):
        """
        Boot the real NS2 system module sequence.
        User must provide required ELFs.
        """
        self.boot_manager.boot_ns2()

    # ============================================================
    # Main execution loop
    # ============================================================
    def run(self):
        """
        Full system run loop:
        - CPU execution
        - SVC handling
        - display update
        """

        while True:
            # --- CPU step ---
            opcode = self.cpu.fetch()
            ir_block = self.cpu.decode_to_ir(opcode)

            for instr in ir_block.instructions:
                if instr.op.name == "SVC":
                    svc_num = self.cpu_state.read_reg(8)

                    if svc_num == self.SVC_GET_SERVICE:
                        self.svc_get_service()
                        continue

                    if svc_num == self.SVC_IPC:
                        self.svc_ipc()
                        continue

                self.interpreter.exec(instr)

            # --- Display ---
            self.window.update()

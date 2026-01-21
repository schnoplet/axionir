from core.cpu import CPUState, ShadowMMU, IRInterpreter
from core.arm64_cpu import ARM64CPU
from core.elf_loader import ELF64Loader
from core.ns2_profile import NS2Profile
from core.service_manager import ServiceManager
from core.process import Process
from core.ipc import IPCMessage
from core.vfs import VirtualFileSystem

from core.services.time_service import TimeService
from core.services.process_service import ProcessService
from core.services.fs_service import FileSystemService


class AxionIRSystem:
    SVC_IPC = 0x1000
    SVC_GET_SERVICE = 0x1001

    def __init__(self, profile: NS2Profile | None = None, fs_root: str = "ns2_fs"):
        self.profile = profile or NS2Profile()

        self.cpu_state = CPUState()
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=0,
        )

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.arm64 = ARM64CPU(self.cpu_state, self.mmu)
        self.elf = ELF64Loader(self.mmu)

        # Kernel objects
        self.process = Process(entry_point=0)
        self.services = ServiceManager()

        # Filesystem
        self.vfs = VirtualFileSystem(fs_root)

        # Core services
        self.services.register("time", TimeService())
        self.services.register("process", ProcessService(self.process))
        self.services.register("fs", FileSystemService(self.vfs))

        print("[AxionIR] Booted", self.profile.describe())
        print("[AxionIR] FS root:", fs_root)

    def get_service(self):
        service_map = {
            1: "time",
            2: "process",
            3: "fs",
        }

        sid = self.cpu_state.read_reg(1)
        name = service_map.get(sid, f"unknown_{sid}")
        handle = self.process.new_handle(name)

        print(f"[AxionIR] Service lookup '{name}' → handle {handle}")
        self.cpu_state.write_reg(0, handle)

    def handle_ipc(self):
        handle = self.cpu_state.read_reg(0)
        cmd = self.cpu_state.read_reg(1)
        data = self.cpu_state.read_reg(2)

        service_name = self.process.get_handle(handle)
        msg = IPCMessage(cmd, data)
        self.services.dispatch(service_name, msg)

        self.cpu_state.write_reg(0, 0)

    def run(self, max_steps=10_000_000):
        steps = 0
        while self.cpu_state.running and steps < max_steps:
            opcode = self.arm64.fetch()
            block = self.arm64.decode_to_ir(opcode)

            for ins in block.instructions:
                if ins.op.name == "SVC":
                    nr = self.cpu_state.read_reg(8)

                    if nr == self.SVC_GET_SERVICE:
                        self.get_service()
                        continue

                    if nr == self.SVC_IPC:
                        self.handle_ipc()
                        continue

                self.interp.exec(ins)

            steps += 1

        if steps >= max_steps:
            print("[AxionIR] Execution stopped (step limit)")

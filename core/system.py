from core.cpu import CPUState, ShadowMMU, IRInterpreter
from core.arm64_cpu import ARM64CPU
from core.elf_loader import ELF64Loader
from core.ns2_profile import NS2Profile
from core.service_manager import ServiceManager
from core.process import Process
from core.ipc import IPCMessage

from core.services.time_service import TimeService
from core.services.process_service import ProcessService


class AxionIRSystem:
    def __init__(self, profile: NS2Profile | None = None):
        self.profile = profile or NS2Profile()

        self.cpu_state = CPUState()
        self.mmu = ShadowMMU(
            size=self.profile.memory.total_mb * 1024 * 1024,
            bandwidth_bytes_per_tick=0,
        )

        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.arm64 = ARM64CPU(self.cpu_state, self.mmu)
        self.elf = ELF64Loader(self.mmu)

        # -------------------------
        # Kernel objects
        # -------------------------
        self.process = Process(entry_point=0)
        self.services = ServiceManager()

        # Register core services
        self.services.register("time", TimeService())
        self.services.register(
            "process",
            ProcessService(self.process)
        )

        # Give process service handles
        self.time_handle = self.process.new_handle("time")
        self.proc_handle = self.process.new_handle("process")

        print("[AxionIR] Booted", self.profile.describe())
        print("[AxionIR] Services ready")

    def handle_ipc(self):
        """
        Simplified IPC entry point.
        X0 = handle
        X1 = command id
        """
        handle = self.cpu_state.read_reg(0)
        cmd = self.cpu_state.read_reg(1)

        service_name = self.process.get_handle(handle)
        if not service_name:
            raise RuntimeError("Invalid service handle")

        msg = IPCMessage(cmd)
        resp = self.services.dispatch(service_name, msg)

        # Return success in X0
        self.cpu_state.write_reg(0, 0)
        return resp

    def run(self, max_steps=10_000_000):
        steps = 0
        while self.cpu_state.running and steps < max_steps:
            opcode = self.arm64.fetch()
            block = self.arm64.decode_to_ir(opcode)

            for ins in block.instructions:
                if ins.op.name == "SVC":
                    nr = self.cpu_state.read_reg(8)

                    # IPC syscall
                    if nr == 0x1000:
                        self.handle_ipc()
                        continue

                self.interp.exec(ins)

            steps += 1

        if steps >= max_steps:
            print("[AxionIR] Execution stopped (step limit)")

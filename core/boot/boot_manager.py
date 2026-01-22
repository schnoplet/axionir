from core.boot.ns2_boot_order import NS2_BOOT_SEQUENCE
from core.process_manager import ProcessManager


class BootManager:
    def __init__(self, system):
        self.system = system
        self.procman = system.process_manager
        self.loader = system.module_loader

    def boot_ns2(self):
        print("[AxionIR] Starting NS2 boot sequence")

        for module in NS2_BOOT_SEQUENCE:
            name = module["name"]
            desc = module["description"]

            print(f"[AxionIR][BOOT] Loading {name} — {desc}")

            entry = self.loader.load_module(module)

            proc = self.procman.launch(
                entry_point=entry,
                is_system=True,
            )

            print(
                f"[AxionIR][BOOT] {name} launched "
                f"(PID={proc.pid}, entry=0x{entry:x})"
            )

        print("[AxionIR] NS2 boot sequence complete")

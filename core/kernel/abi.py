class KernelABI:
    # syscall numbers (subset, real-world style)
    SVC_EXIT   = 0x01
    SVC_YIELD  = 0x02
    SVC_MMAP   = 0x03
    SVC_MUNMAP = 0x04
    SVC_GETPID = 0x05
    SVC_GETTID = 0x06

    def __init__(self, system):
        self.sys = system

    def handle(self, svc_num: int):
        cpu = self.sys.cpu_state
        proc = self.sys.process_manager.system_process()

        if svc_num == self.SVC_EXIT:
            code = cpu.read_reg(0)
            print(f"[AxionIR][KERNEL] Process exit code {code}")
            cpu.running = False
            return

        if svc_num == self.SVC_YIELD:
            # cooperative yield (single-thread for now)
            return

        if svc_num == self.SVC_MMAP:
            size = cpu.read_reg(0)
            addr = self.sys.vmm.mmap(size)
            cpu.write_reg(0, addr)
            return

        if svc_num == self.SVC_MUNMAP:
            addr = cpu.read_reg(0)
            self.sys.vmm.munmap(addr)
            cpu.write_reg(0, 0)
            return

        if svc_num == self.SVC_GETPID:
            cpu.write_reg(0, proc.pid)
            return

        if svc_num == self.SVC_GETTID:
            cpu.write_reg(0, 1)  # single-threaded kernel
            return

        return False

from .ir import IROp, IRInstr, IRBlock
import copy
import sys


class CPUState:
    def __init__(self, reg_count: int = 32):
        self.regs = [0] * reg_count
        self.pc = 0
        self.sp = 0x800000
        self.flags = {"Z": False}
        self.running = True

    def read_reg(self, idx: int) -> int:
        return self.sp if idx == 31 else self.regs[idx]

    def write_reg(self, idx: int, value: int):
        if idx == 31:
            self.sp = value
        else:
            self.regs[idx] = value


class ShadowMMU:
    def __init__(self, size: int, bandwidth_bytes_per_tick: int):
        self.mem = bytearray(size)
        self.next_free = 0x10000000  # start of user mappings

    def mmap(self, length: int) -> int:
        addr = self.next_free
        length = (length + 0xFFF) & ~0xFFF  # page align
        self.next_free += length
        return addr

    def read64(self, addr: int) -> int:
        return int.from_bytes(self.mem[addr:addr + 8], "little")

    def write64(self, addr: int, value: int):
        self.mem[addr:addr + 8] = value.to_bytes(8, "little")


class IRInterpreter:
    def __init__(self, state: CPUState, mmu: ShadowMMU):
        self.s = state
        self.m = mmu

    def exec_block(self, block: IRBlock) -> bool:
        for ins in block.instructions:
            if not self.exec(ins):
                return False
        return True

    def exec(self, ins: IRInstr) -> bool:
        if not self.s.running:
            return False

        if ins.op == IROp.NOP:
            return True

        if ins.op == IROp.MOV:
            self.s.write_reg(
                ins.dst,
                ins.imm if ins.imm is not None else self.s.read_reg(ins.src1)
            )
            return True

        if ins.op == IROp.ADD:
            self.s.write_reg(
                ins.dst,
                self.s.read_reg(ins.src1) + self.s.read_reg(ins.src2)
            )
            return True

        if ins.op == IROp.LOAD:
            self.s.write_reg(ins.dst, self.m.read64(self.s.read_reg(ins.src1)))
            return True

        if ins.op == IROp.STORE:
            self.m.write64(
                self.s.read_reg(ins.dst),
                self.s.read_reg(ins.src1)
            )
            return True

        if ins.op == IROp.JMP:
            self.s.pc = ins.imm
            return True

        if ins.op == IROp.SVC:
            return self.handle_syscall()

        return False

    def handle_syscall(self) -> bool:
        nr = self.s.read_reg(8)

        # exit
        if nr == 93:
            code = self.s.read_reg(0)
            print(f"[AxionIR] Program exited with code {code}")
            self.s.running = False
            return False

        # write(fd, buf, len)
        if nr == 64:
            fd = self.s.read_reg(0)
            buf = self.s.read_reg(1)
            length = self.s.read_reg(2)
            data = bytes(self.m.mem[buf:buf + length])

            if fd == 1:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()

            self.s.write_reg(0, length)
            return True

        # mmap(addr, length, prot, flags, fd, offset)
        if nr == 222:
            length = self.s.read_reg(1)
            addr = self.m.mmap(length)
            self.s.write_reg(0, addr)
            return True

        print(f"[AxionIR] Unhandled syscall {nr}")
        self.s.running = False
        return False

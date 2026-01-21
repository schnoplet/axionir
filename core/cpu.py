from core.ir import IROp, IRInstr
import sys


class CPUState:
    def __init__(self, reg_count: int = 32):
        self.regs = [0] * reg_count
        self.pc = 0
        self.sp = 0x800000
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

    def read64(self, addr: int) -> int:
        return int.from_bytes(self.mem[addr:addr + 8], "little")

    def write64(self, addr: int, value: int):
        self.mem[addr:addr + 8] = value.to_bytes(8, "little")


class IRInterpreter:
    def __init__(self, state: CPUState, mmu: ShadowMMU):
        self.s = state
        self.m = mmu

    def exec(self, ins: IRInstr) -> bool:
        if not self.s.running:
            return False

        if ins.op == IROp.NOP:
            return True

        if ins.op == IROp.MOV:
            self.s.write_reg(ins.dst, ins.imm)
            return True

        if ins.op == IROp.JMP:
            self.s.pc = ins.imm
            return True

        return True

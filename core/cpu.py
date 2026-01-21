from .ir import IROp, IRInstr, IRBlock
import copy


class CPUState:
    def __init__(self, reg_count: int = 32):
        self.regs = [0] * reg_count
        self.pc = 0
        self.sp = 0x800000  # initial stack pointer
        self.flags = {"Z": False}

    def read_reg(self, idx: int) -> int:
        if idx == 31:
            return self.sp
        return self.regs[idx]

    def write_reg(self, idx: int, value: int):
        if idx == 31:
            self.sp = value
        else:
            self.regs[idx] = value

    def snapshot(self):
        return copy.deepcopy(self)

    def restore(self, snap):
        self.regs = snap.regs
        self.pc = snap.pc
        self.sp = snap.sp
        self.flags = snap.flags


class ShadowMMU:
    def __init__(self, size: int, bandwidth_bytes_per_tick: int):
        self.mem = bytearray(size)
        self.bandwidth_limit = bandwidth_bytes_per_tick
        self.bandwidth_used = 0
        self.history = []

    def reset_bandwidth(self):
        self.bandwidth_used = 0

    def consume_bandwidth(self, bytes_used: int) -> bool:
        self.bandwidth_used += bytes_used
        return self.bandwidth_used <= self.bandwidth_limit

    def begin_epoch(self):
        self.history.append([])

    def rollback_epoch(self):
        if not self.history:
            return
        diffs = self.history.pop()
        for addr, old in reversed(diffs):
            self.mem[addr] = old

    def commit_epoch(self):
        if self.history:
            self.history.pop()

    def read64(self, addr: int) -> int:
        if not self.consume_bandwidth(8):
            raise RuntimeError("Memory bandwidth exceeded")
        return int.from_bytes(self.mem[addr:addr + 8], "little")

    def write64(self, addr: int, value: int):
        if not self.consume_bandwidth(8):
            raise RuntimeError("Memory bandwidth exceeded")

        if self.history:
            for i in range(8):
                self.history[-1].append((addr + i, self.mem[addr + i]))

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
        try:
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
                val = self.m.read64(self.s.read_reg(ins.src1))
                self.s.write_reg(ins.dst, val)
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

        except RuntimeError:
            return False

        return False

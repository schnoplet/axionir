from .ir import IROp, IRInstr, IRBlock
import copy


class CPUState:
    def __init__(self, reg_count: int = 32):
        self.regs = [0] * reg_count
        self.pc = 0
        self.flags = {"Z": False}

    def snapshot(self):
        return copy.deepcopy(self)

    def restore(self, snap):
        self.regs = snap.regs
        self.pc = snap.pc
        self.flags = snap.flags


class ShadowMMU:
    """
    Memory with write-diff tracking for rewind / rollback.
    """
    def __init__(self, size: int = 1024 * 1024):
        self.mem = bytearray(size)
        self.history = []  # list of (addr, old_value)

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
        return int.from_bytes(self.mem[addr:addr+8], "little")

    def write64(self, addr: int, value: int):
        if self.history:
            # record original bytes
            for i in range(8):
                self.history[-1].append((addr + i, self.mem[addr + i]))
        self.mem[addr:addr+8] = value.to_bytes(8, "little")


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
        r = self.s.regs

        if ins.op == IROp.NOP:
            return True

        if ins.op == IROp.MOV:
            r[ins.dst] = ins.imm if ins.imm is not None else r[ins.src1]
            return True

        elif ins.op == IROp.ADD:
            r[ins.dst] = r[ins.src1] + r[ins.src2]
            return True

        elif ins.op == IROp.SUB:
            r[ins.dst] = r[ins.src1] - r[ins.src2]
            return True

        elif ins.op == IROp.MUL:
            r[ins.dst] = r[ins.src1] * r[ins.src2]
            return True

        elif ins.op == IROp.LOAD:
            r[ins.dst] = self.m.read64(r[ins.src1])
            return True

        elif ins.op == IROp.STORE:
            self.m.write64(r[ins.dst], r[ins.src1])
            return True

        elif ins.op == IROp.CMP:
            self.s.flags["Z"] = (r[ins.src1] == r[ins.src2])
            return True

        return False

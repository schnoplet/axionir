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


class MMU:
    def __init__(self, size: int = 1024 * 1024):
        self.mem = bytearray(size)

    def read64(self, addr: int) -> int:
        return int.from_bytes(self.mem[addr:addr+8], "little")

    def write64(self, addr: int, value: int):
        self.mem[addr:addr+8] = value.to_bytes(8, "little")


class IRInterpreter:
    def __init__(self, state: CPUState, mmu: MMU):
        self.s = state
        self.m = mmu

    def exec_block(self, block: IRBlock) -> bool:
        """
        Executes a block.
        Returns True if execution was safe,
        False if speculation must be rolled back.
        """
        for ins in block.instructions:
            ok = self.exec(ins)
            if not ok:
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

        # Unsupported op → speculation failure
        return False

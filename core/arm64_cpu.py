import struct
from .ir import IRInstr, IROp, IRBlock


class ARM64CPU:
    def __init__(self, cpu_state, mmu):
        self.s = cpu_state
        self.m = mmu

    def fetch(self) -> int:
        pc = self.s.pc
        instr = struct.unpack_from("<I", self.m.mem, pc)[0]
        self.s.pc += 4
        return instr

    def decode_to_ir(self, opcode: int) -> IRBlock:
        block = IRBlock(label=f"pc_{self.s.pc:x}")

        # MOVZ
        if (opcode >> 23) & 0x1FF == 0b110100101:
            rd = opcode & 0x1F
            imm16 = (opcode >> 5) & 0xFFFF
            shift = ((opcode >> 21) & 0x3) * 16
            block.emit(IRInstr(IROp.MOV, dst=rd, imm=imm16 << shift))
            return block

        # ADD immediate (for stack)
        if (opcode >> 24) & 0x1F == 0b10001:
            rd = opcode & 0x1F
            rn = (opcode >> 5) & 0x1F
            imm12 = (opcode >> 10) & 0xFFF
            block.emit(IRInstr(IROp.MOV, dst=rd, src1=rn))
            block.emit(IRInstr(IROp.ADD, dst=rd, src1=rd, src2=rd))
            return block

        # LDR Xt, [Xn]
        if (opcode >> 22) & 0x3FF == 0b11111000010:
            rt = opcode & 0x1F
            rn = (opcode >> 5) & 0x1F
            block.emit(IRInstr(IROp.LOAD, dst=rt, src1=rn))
            return block

        # STR Xt, [Xn]
        if (opcode >> 22) & 0x3FF == 0b11111000000:
            rt = opcode & 0x1F
            rn = (opcode >> 5) & 0x1F
            block.emit(IRInstr(IROp.STORE, dst=rn, src1=rt))
            return block

        # B
        if (opcode >> 26) & 0x3F == 0b000101:
            imm26 = opcode & 0x03FFFFFF
            if imm26 & (1 << 25):
                imm26 |= ~0x03FFFFFF
            block.emit(IRInstr(IROp.JMP, imm=self.s.pc + (imm26 << 2)))
            return block

        # RET
        if opcode == 0xD65F03C0:
            block.emit(IRInstr(IROp.JMP, imm=self.s.read_reg(30)))
            return block

        block.emit(IRInstr(IROp.NOP))
        return block

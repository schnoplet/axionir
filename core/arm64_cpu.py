import struct
from .ir import IRInstr, IROp, IRBlock


class ARM64CPU:
    """
    ARM64 instruction fetch + decode + IR translation.
    This is REAL execution infrastructure.
    """

    def __init__(self, cpu_state, mmu):
        self.s = cpu_state
        self.m = mmu

    # =========================
    # FETCH
    # =========================

    def fetch(self) -> int:
        pc = self.s.pc
        instr = struct.unpack_from("<I", self.m.mem, pc)[0]
        self.s.pc += 4
        return instr

    # =========================
    # DECODE → IR
    # =========================

    def decode_to_ir(self, opcode: int) -> IRBlock:
        block = IRBlock(label=f"pc_{self.s.pc:x}")

        # ----------------------------------
        # MOVZ (Move Wide Immediate)
        # ----------------------------------
        # opcode[31:23] == 0b110100101
        if (opcode >> 23) & 0x1FF == 0b110100101:
            rd = opcode & 0x1F
            imm16 = (opcode >> 5) & 0xFFFF
            shift = ((opcode >> 21) & 0x3) * 16
            value = imm16 << shift

            block.emit(IRInstr(
                op=IROp.MOV,
                dst=rd,
                imm=value
            ))
            return block

        # ----------------------------------
        # ADD (register)
        # ----------------------------------
        # opcode[31:21] == 0b10001011000
        if (opcode >> 21) & 0x7FF == 0b10001011000:
            rd = opcode & 0x1F
            rn = (opcode >> 5) & 0x1F
            rm = (opcode >> 16) & 0x1F

            block.emit(IRInstr(
                op=IROp.ADD,
                dst=rd,
                src1=rn,
                src2=rm
            ))
            return block

        # ----------------------------------
        # Unknown instruction → NOP
        # ----------------------------------
        block.emit(IRInstr(op=IROp.NOP))
        return block

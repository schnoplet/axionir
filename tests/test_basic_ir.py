from core.ir import IRBlock, IRInstr, IROp
from core.system import AxionIRSystem

def test_basic_math():
    sys = AxionIRSystem()
    b = IRBlock()
    b.emit(IRInstr(IROp.MOV, dst=0, imm=6))
    b.emit(IRInstr(IROp.MOV, dst=1, imm=7))
    b.emit(IRInstr(IROp.MUL, dst=2, src1=0, src2=1))
    sys.run_block(b)
    assert sys.cpu_state.regs[2] == 42\n
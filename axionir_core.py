from core.ir import IRBlock, IRInstr, IROp
from core.system import AxionIRSystem

def main():
    sys = AxionIRSystem()

    block = IRBlock("demo")
    block.emit(IRInstr(IROp.MOV, dst=0, imm=6))
    block.emit(IRInstr(IROp.MOV, dst=1, imm=7))
    block.emit(IRInstr(IROp.MUL, dst=2, src1=0, src2=1))
    block.emit(IRInstr(IROp.ADD, dst=3, src1=2, src2=1))

    # run multiple times to trigger hot block logic
    for _ in range(10):
        sys.run_block(block)

    print("R2 =", sys.cpu_state.regs[2])
    print("R3 =", sys.cpu_state.regs[3])

if __name__ == "__main__":
    main()

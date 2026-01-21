# AxionIR Core - NS2 Emulator Entry
# Apache-2.0

from core.system import AxionIRSystem


def main():
    sys = AxionIRSystem()

    # future:
    # sys.load_elf("something.elf")
    # sys.run()

    # for now, just boot cleanly
    pass


if __name__ == "__main__":
    main()

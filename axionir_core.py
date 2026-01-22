# AxionIR - NS2 Emulator Entrypoint
# This file intentionally stays small.
# All real behavior lives in core/.

from core.system import AxionIRSystem


def main():
    # Create system with user-provided filesystem root
    sys = AxionIRSystem(fs_root="ns2_fs")

    # When you have a real ELF to test, uncomment:
    sys.launch_elf("test.elf", is_system=True)

    # Run the emulator
    sys.run()


if __name__ == "__main__":
    main()

import struct


ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1
EM_AARCH64 = 183

PT_LOAD = 1


class ELFError(Exception):
    pass


class ELF64Loader:
    """
    Minimal ELF64 loader for AArch64.
    Maps LOAD segments and returns entry point.
    """

    def __init__(self, mmu):
        self.mmu = mmu

    def load(self, path: str) -> int:
        with open(path, "rb") as f:
            data = f.read()

        # ---- ELF header ----
        if data[:4] != ELF_MAGIC:
            raise ELFError("Not an ELF file")

        ei_class = data[4]
        ei_data = data[5]

        if ei_class != ELFCLASS64:
            raise ELFError("Not ELF64")

        if ei_data != ELFDATA2LSB:
            raise ELFError("Not little-endian")

        (
            e_type,
            e_machine,
            e_version,
            e_entry,
            e_phoff,
            _,
            _,
            e_ehsize,
            e_phentsize,
            e_phnum,
        ) = struct.unpack_from("<HHIQQQIHHH", data, 16)

        if e_machine != EM_AARCH64:
            raise ELFError("Not AArch64")

        # ---- Program headers ----
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            (
                p_type,
                p_flags,
                p_offset,
                p_vaddr,
                _,
                p_filesz,
                p_memsz,
                _,
            ) = struct.unpack_from("<IIQQQQQQ", data, off)

            if p_type != PT_LOAD:
                continue

            segment = data[p_offset : p_offset + p_filesz]

            # Map segment
            for j in range(len(segment)):
                self.mmu.mem[p_vaddr + j] = segment[j]

            # Zero-fill BSS
            for j in range(p_filesz, p_memsz):
                self.mmu.mem[p_vaddr + j] = 0

        return e_entry

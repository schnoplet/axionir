import os


class ModuleLoader:
    def __init__(self, elf_loader, vfs):
        self.elf = elf_loader
        self.vfs = vfs

    def load_module(self, module):
        path = module["path"].lstrip("/")

        full_path = os.path.join(self.vfs.root, path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(
                f"Required NS2 module missing: {module['name']} ({path})"
            )

        entry = self.elf.load(full_path)
        return entry

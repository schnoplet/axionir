import os


class VirtualFile:
    def __init__(self, path: str):
        self.path = path
        self.fd = open(path, "rb")

    def size(self) -> int:
        self.fd.seek(0, os.SEEK_END)
        return self.fd.tell()

    def read(self, offset: int, size: int) -> bytes:
        self.fd.seek(offset)
        return self.fd.read(size)


class VirtualFileSystem:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.open_files = {}
        self.next_fd = 1

    def _resolve(self, path: str) -> str:
        full = os.path.abspath(os.path.join(self.root, path.lstrip("/")))
        if not full.startswith(self.root):
            raise RuntimeError("Path escape detected")
        return full

    def open(self, path: str) -> int:
        full = self._resolve(path)
        if not os.path.exists(full):
            raise FileNotFoundError(path)

        vf = VirtualFile(full)
        fd = self.next_fd
        self.open_files[fd] = vf
        self.next_fd += 1
        return fd

    def size(self, fd: int) -> int:
        return self.open_files[fd].size()

    def read(self, fd: int, offset: int, size: int) -> bytes:
        return self.open_files[fd].read(offset, size)

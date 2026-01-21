from core.ipc import IPCService, IPCMessage


class FileSystemService(IPCService):
    """
    Filesystem service backed by a host directory.
    """

    def __init__(self, vfs):
        self.vfs = vfs

    def handle(self, msg: IPCMessage):
        cmd = msg.command_id
        data = msg.data or {}

        # command 0: open(path)
        if cmd == 0:
            path = data.get("path", "")
            fd = self.vfs.open(path)
            msg.response = {
                "result": 0,
                "fd": fd
            }
            return msg

        # command 1: get size(fd)
        if cmd == 1:
            fd = data["fd"]
            size = self.vfs.size(fd)
            msg.response = {
                "result": 0,
                "size": size
            }
            return msg

        # command 2: read(fd, offset, size)
        if cmd == 2:
            fd = data["fd"]
            offset = data.get("offset", 0)
            size = data["size"]
            blob = self.vfs.read(fd, offset, size)
            msg.response = {
                "result": 0,
                "data": blob
            }
            return msg

        raise RuntimeError(f"Unknown FS command {cmd}")

from core.ipc import IPCService, IPCMessage


class FileSystemService(IPCService):
    """
    Minimal filesystem service stub.
    Enough to let system software proceed.
    """

    def handle(self, msg: IPCMessage):
        cmd = msg.command_id

        # command 0: open file
        if cmd == 0:
            # pretend file exists
            msg.response = {
                "result": 0,
                "file_handle": 1
            }
            return msg

        # command 1: get file size
        if cmd == 1:
            msg.response = {
                "result": 0,
                "size": 4096
            }
            return msg

        # command 2: read file
        if cmd == 2:
            msg.response = {
                "result": 0,
                "bytes_read": 0
            }
            return msg

        raise RuntimeError(f"Unknown FS command {cmd}")

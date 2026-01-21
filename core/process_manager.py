from core.process import Process


class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.system_pid = None

    def launch(self, entry_point: int, is_system=False) -> Process:
        proc = Process(entry_point)
        self.processes[proc.pid] = proc

        if is_system:
            self.system_pid = proc.pid

        return proc

    def get(self, pid: int) -> Process | None:
        return self.processes.get(pid)

    def system_process(self) -> Process | None:
        if self.system_pid is None:
            return None
        return self.processes[self.system_pid]

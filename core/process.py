class Process:
    _next_pid = 1

    def __init__(self, entry_point: int):
        self.pid = Process._next_pid
        Process._next_pid += 1

        self.entry = entry_point
        self.handles = {}
        self.next_handle = 1

    def new_handle(self, obj):
        h = self.next_handle
        self.handles[h] = obj
        self.next_handle += 1
        return h

    def get_handle(self, h):
        return self.handles.get(h)

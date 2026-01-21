from core.process import Process

p = Process(entry_point=0x1234)

obj = {"service": "fs"}
h = p.new_handle(obj)

print("PID:", p.pid)
print("Handle:", h)
print("Lookup:", p.get_handle(h))

.global _start
_start:
    mov x0, #4096      // size
    mov x8, #3         // mmap
    svc #0

    mov x8, #5         // getpid
    svc #0

    mov x0, #0
    mov x8, #1         // exit
    svc #0

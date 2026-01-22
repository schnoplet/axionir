# NS2 boot module order (architectural, not proprietary)

NS2_BOOT_SEQUENCE = [
    {
        "name": "kernel",
        "path": "/system/kernel.elf",
        "system": True,
        "description": "NS2 kernel / supervisor",
    },
    {
        "name": "sm",
        "path": "/system/sm.elf",
        "system": True,
        "description": "Service Manager",
    },
    {
        "name": "ldr",
        "path": "/system/ldr.elf",
        "system": True,
        "description": "Module Loader",
    },
    {
        "name": "pm",
        "path": "/system/pm.elf",
        "system": True,
        "description": "Process Manager",
    },
    {
        "name": "nvservices",
        "path": "/system/nvservices.elf",
        "system": True,
        "description": "NVIDIA system services",
    },
    {
        "name": "vi",
        "path": "/system/vi.elf",
        "system": True,
        "description": "Display compositor",
    },
    {
        "name": "am",
        "path": "/system/am.elf",
        "system": True,
        "description": "Applet Manager",
    },
    {
        "name": "home",
        "path": "/system/home.elf",
        "system": True,
        "description": "Home Menu",
    },
]

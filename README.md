# AxionIR

AxionIR is an emulator project for the **Nintendo Switch 2**.  
Its purpose is to run the real Switch 2 operating system, homescreen, and software on a PC using **files dumped by the user from their own console**.

AxionIR does not include any Nintendo code, firmware, keys, or assets.  
It only provides the execution environment.

---

## What AxionIR Is (Technical Explanation)

AxionIR implements the core components required to host the Nintendo Switch 2 system software:

- An ARM64 CPU execution pipeline
- An ELF loader for running real system binaries
- A kernel-style syscall (SVC) interface
- A process model with multiple system processes
- IPC (inter-process communication) and service routing
- A virtual filesystem backed by user-provided files
- A boot system that launches system modules in the correct order
- A framebuffer and display pipeline that system software can draw into

Rather than rewriting or replacing the Switch 2 operating system, AxionIR is designed so that **the original system binaries run unmodified**, as they would on real hardware.

The emulator behaves like the underlying console environment:
- system modules request services
- services communicate via IPC
- memory is allocated via kernel calls
- graphics output goes through the video interface into a framebuffer

---

## What AxionIR Is (Plain Explanation)

In simple terms:

AxionIR is a program that pretends to be a Nintendo Switch 2 so that the real Switch 2 software thinks it’s running on its own hardware — but it’s actually running on your PC.

When fully developed, the intended flow is:
1. You dump system files from your own Switch 2
2. You open AxionIR
3. You select the dumped files
4. AxionIR starts the Switch 2 operating system
5. The real homescreen appears in a window
6. Games and apps can then be launched

AxionIR itself does **not** contain any games or system software.

---

## About Dumping System Files

At the moment, there is **no publicly documented, stable method** for dumping Nintendo Switch 2 system software in the form required by emulators.
This means that you cannot currently use this emulator to actually play games or run official Nintendo Switch 2 software. Based on previous consoles, I expect this to change by the end of the year (around the start of November if I had to put a date on it).

This is expected for a new console. Historically, emulator development begins **before** reliable dumping methods are widely available. The emulator is built first, and support for real system files is added later as legal dumping methods become known.

AxionIR is being developed with this in mind:
- it does not assume a specific dump method
- it is designed to handle partial or incomplete dumps
- it will validate user-provided files when dumping becomes practical

No dumping tools or instructions are provided by this project.

---

## Current State of the Project

AxionIR is in **early development**, but the core foundations already exist.

Right now, AxionIR can:
- Execute real ARM64 binaries
- Load ELF files and jump to their entry points
- Provide a kernel-style syscall interface
- Create and manage system processes
- Route IPC calls to services
- Read real files from a user-selected directory
- Present a real framebuffer in a PC window
- Launch system modules in a defined boot order

At this stage, the emulator focuses on **infrastructure**, not end-user features.

---

## What Is Not Implemented Yet

The following parts are incomplete or missing:

- Full kernel syscall coverage
- IPC shared memory buffers
- GPU command processing
- Input handling
- Audio output
- Accurate timing and scheduling
- Shader translation and graphics acceleration
- JIT (dynamic recompilation)

These are expected for an emulator at this stage and are built incrementally on top of the existing structure.

---

## Project Roadmap (Estimated)

Dates are intentionally conservative.

### 2026
- Expand kernel ABI and syscall coverage  
- Implement IPC shared memory
- Bring up basic input and timing
- Improve error handling and logging
- Begin early GPU command decoding
- Basic system stability improvements
- First partial homescreen boot attempts
- Initial GPU output beyond framebuffer clears
- Service completeness improvements

### Beyond
- Interactive homescreen boot
- Early system UI rendering
- Continued GPU and IPC improvements
- Game compatibility work
- Performance optimization
- User-friendly UI and setup flow
- Packaging into a single executable

This timeline may change depending on complexity and available research.

---

## Legal Notice

AxionIR does not ship with:
- Nintendo firmware
- System modules
- Encryption keys
- Games or assets

To use AxionIR, users must legally obtain and dump files from their own Nintendo Switch 2.

AxionIR is an independent project and is not affiliated with Nintendo.

---

## Summary

AxionIR is a long-term emulator project aimed at running the real Nintendo Switch 2 software on a PC.

It is currently focused on building the correct low-level environment so that, when legal system dumps become available, the actual system software can run without modification.

Progress is measured in infrastructure and correctness rather than visible features.

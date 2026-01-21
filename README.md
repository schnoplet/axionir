# AxionIR

**AxionIR** is a next-generation emulator research core built around an **intermediate-representation–first architecture**, designed to explore high-performance, scalable emulation techniques for modern console-class systems.

AxionIR is not a consumer emulator. It is a **research framework** focused on CPU translation, GPU command abstraction, scheduling models, and memory systems, with an emphasis on correctness, experimentation, and long-term extensibility.

---

## Project Scope

AxionIR is intended as an early-stage research effort. It does **not** target any specific commercial console, firmware, operating system, or proprietary software.

The project exists to:
- explore emulator architecture and performance
- experiment with new execution and scheduling models
- provide a clean, modular foundation for future research
- remain legally clean and platform-agnostic

Only original code and original test programs are supported.

---

## Design Philosophy

AxionIR is built around a few core principles:

- **IR-first design**  
  All CPU execution flows through a custom intermediate representation, enabling optimization, caching, and future JIT compilation.

- **Translation over emulation**  
  Subsystems (especially GPU) are designed to translate intent into modern APIs rather than simulate hardware at a low level.

- **Deterministic correctness first**  
  Performance work is layered on top of a deterministic, testable core.

- **Modularity**  
  CPU, GPU, memory, and scheduling systems are cleanly separated and replaceable.

---

## Core Components

- **CPU Core**
  - Architecture-agnostic intermediate representation
  - Interpreter and cached block execution
  - Designed for future dynamic recompilation

- **Memory System**
  - Flat memory model with hooks for paging and permissions
  - Save-state and snapshot-friendly design

- **Scheduler**
  - Experimental CPU/GPU timing and synchronization models
  - Research-focused decoupling and predictive sync strategies

- **GPU Framework**
  - Command-buffer-based GPU IR
  - Backend-agnostic design (e.g. Vulkan, Metal, DirectX)

---

## Non-Goals

AxionIR explicitly does **not**:
- ship with firmware, BIOS, or ROMs
- run proprietary commercial software
- bypass DRM or security mechanisms
- replicate any specific console behavior verbatim

This project is focused on **emulator technology**, not content execution.

---

## Status

AxionIR is currently in **early development**.

The project is expected to evolve rapidly as new research directions are explored and evaluated.

Breaking changes are normal at this stage.

---

## License

AxionIR is licensed under the **Apache License, Version 2.0**.

This license was chosen to encourage open research, collaboration, and reuse while providing an explicit patent grant.

See the `LICENSE` file for full details.

---

## Disclaimer

AxionIR is an independent, open-source research project.

It is not affiliated with, endorsed by, or associated with Nintendo or any other console manufacturer.

All trademarks and brand names are the property of their respective owners.

# PPC2x86 — PowerPC ↔ x86/x64 ISA Translation Station

```
  ██████╗ ██████╗  ██████╗██████╗ ██╗  ██╗ █████╗  ██████╗
  ██╔══██╗██╔══██╗██╔════╝╚════██╗╚██╗██╔╝██╔══██╗██╔════╝
  ██████╔╝██████╔╝██║      █████╔╝ ╚███╔╝ ╚█████╔╝███████╗
  ██╔═══╝ ██╔═══╝ ██║     ██╔═══╝  ██╔██╗ ██╔══██╗██╔══██║
  ██║     ██║     ╚██████╗███████╗██╔╝ ██╗╚█████╔╝╚██████╔╝
  ╚═╝     ╚═╝      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚════╝  ╚═════╝
  PowerPC ↔ x86/x64 ISA Translation Station  v1.0.0
```

> **From the minds of IBM Bob & Daneyand**

---

## What Is This?

**PPC2x86** is a fully self-contained Python tool for translating PowerPC (PPC32 and PPC64) instruction mnemonics into their x86/x86-64 equivalents — and back again. It is the app you reach for when you are porting assembly, studying compiler output, writing a JIT, or just deeply curious about the bizarre and beautiful world of instruction set architecture.

It ships two front-ends that share exactly one brain:

- A **wxPython GUI** — a dark-themed, phosphor-green retro "ISA Museum" packed with lookup panels, a live-scrolling trivia ticker, an ISA Museum tab covering nine historic architectures, easter eggs, hidden panels, and enough compiler lore to keep you occupied for days.
- A **command-line interface** — single-shot lookups for scripts and shell pipelines, plus a full interactive REPL for exploratory sessions.

Everything is embedded in plain Python source files. No database. No network. No surprises.

---

## Version

**1.0.0** — Retro ISA Museum Edition

---

## Features

### Core lookup engine
- **423 PPC mnemonics** — PPC32 and PPC64 integer, load/store, branch, condition register, floating-point (double and single precision), AltiVec/VMX vector, system/privileged, and all extended mnemonics and simplified forms
- **524 x86/x64 mnemonics** — integer, x87 FPU, SSE, SSE2, SSSE3, SSE4.1, AVX, AVX2, BMI1/2, string, system, bit manipulation
- **273 PPC→x86 mappings** + **154 x86→PPC reverse mappings**, each with:
  - `DIRECT` — semantically equivalent, use it
  - `CLOSE` — equivalent with caveats (endianness, register model, operand order)
  - `SUGGESTION` — best approximation; not guaranteed equivalent; clearly flagged
- **Fuzzy fallback** — mistype `lzw` and it suggests `cntlzw` and `lmw`; mistype `addz` and it surfaces `addze`

### GUI (wxPython)
- Dark phosphor-green retro terminal theme — looks like a 1985 workstation fell forward in time
- **Lookup tab** — live-filtering searchable instruction list on the left; rich-text result panel on the right showing the source instruction, all analogues with confidence badges, and semantic notes
- **Direction toggle** — flip between PPC→x86 and x86→PPC with one click
- **Mode selector** — 32-bit or 64-bit, changes which instructions are shown and which mappings apply
- **Suggestion warning banner** — when a result is a suggestion rather than a direct or close match, a bright amber warning bar says so explicitly
- **ISA Museum tab** — click any of nine historic architectures in the sidebar and get a museum-placard-style panel with vendor, years active, bit width, endianness, register count, description, "Famous For" callout, and a custom-drawn timeline bar showing its lifespan from 1975 to 2025
- **Compare dialog** — side-by-side ISA comparison, pick any two and compare them
- **ISA Timeline dialog** — a full-window Gantt-style chart of all nine ISAs drawn in colour across fifty years
- **Scrolling ticker bar** — ISA trivia facts scroll continuously across the bottom of the window; right-click to filter by architecture
- **History Log tab** — every lookup is recorded with mnemonic, direction, and timestamp
- **Menu bar** — File, View, ISA Museum, Extras (ISA Timeline, Instruction Count Stats, Random ISA Fact, Benchmark Trivia), Help

### CLI
- Single-shot: `ppc2x86 --from ppc --instr fadd` — prints a formatted result card with ANSI colour codes, confidence badge, full instruction details, and notes
- Plain text output when not a TTY — safe for scripts and `grep`
- REPL: `ppc2x86` — full interactive session with command history via `readline`, all commands below
- `--mode 32|64` flag on both single-shot and REPL

### ISA Museum content
Nine architectures profiled and covered with trivia:

| ISA | Vendor | Years | Notes |
|-----|--------|-------|-------|
| **SPARC** | Sun Microsystems / Oracle | 1987–present | Register windows, SPARC64, delay slots |
| **Alpha AXP** | DEC / Compaq / HP | 1992–2004 | First mainstream 64-bit RISC; no byte load/store |
| **MIPS** | MIPS Technologies | 1985–present | RISC origin story, SGI workstations, branch delay slots |
| **PA-RISC** | Hewlett-Packard | 1986–2008 | HP's Precision Architecture, precursor to Itanium |
| **Itanium (IA-64)** | Intel / HP | 2001–2021 | EPIC architecture, bundle encoding, compiler-heavy, famous cautionary tale |
| **68k** | Motorola | 1979–present | Mac, Amiga, Atari ST, still alive in embedded systems |
| **VAX** | DEC | 1977–2000 | CISC pinnacle, VMS, 304 instruction modes |
| **PowerPC** | IBM / Motorola / Apple | 1992–present | POWER ISA, AltiVec, Cell/B.E., POWER10 |
| **x86 / x86-64** | Intel / AMD | 1978–present | The instruction set that ate the world |

### Easter eggs (spoilers — stop reading if you want to find them yourself)
<details>
<summary>Click to reveal all easter eggs</summary>

- **Konami Code** — with the window focused, press `↑ ↑ ↓ ↓ ← → ← → B A`. A full-screen ASCII art splash appears with a secret message
- **Title click** — click the window title label seven times; the ISA Graveyard panel appears, complete with hand-drawn tombstones for every dead ISA
- **Compiler Quotes** — after entering the Konami code, a new "Compiler Quotes" item appears in the Help menu revealing 23 quotes from Knuth, Patterson, Torvalds, Cutler, Keller, and friends
- **Status bar** — right-click anywhere on the status bar for a random compiler/ISA quote
- **About dialog** — click the `★` star three times to unlock the Hall of Fame credits panel
- **Ticker bar** — right-click the scrolling fact ticker for an ISA filter menu

</details>

---

## Install with pipx (recommended)

```bash
pipx install ppc2x86
ppc2x86 --from ppc --instr lwz     # single lookup
ppc2x86                            # interactive REPL
```

The CLI and REPL have no dependencies. For the retro ISA-museum GUI, add wxPython to the same
isolated environment, then launch it:

```bash
pipx inject ppc2x86 wxPython
ppc2x86 --gui
```

Upgrade with `pipx upgrade ppc2x86`; remove with `pipx uninstall ppc2x86`. If the command is not found,
run `pipx ensurepath` and open a new terminal.

---

## Requirements

- **Python 3.9+**
- **wxPython >= 4.2** (GUI mode only — CLI works without it)

```bash
pip install wxPython
```

That is the only external dependency. Everything else — all instruction data, all trivia, all ISA profiles — is embedded in the Python source.

---

## Installation

```bash
git clone https://github.com/007Style/PPC2x86.git
cd PPC2x86
pip install -e .              # CLI / REPL only
pip install -e '.[gui]'       # plus the wxPython GUI
ppc2x86 --help
```

Standard `src/` layout with `pyproject.toml`; nothing to compile.

---

## Usage

### GUI

```bash
ppc2x86 --gui
ppc2x86 --gui --mode 64
```

### Single-shot CLI

```bash
# PPC → x86
ppc2x86 --from ppc --instr lwz
ppc2x86 --from ppc --instr fadd --mode 64
ppc2x86 --from ppc --instr vaddubm
ppc2x86 --from ppc --instr fmadd        # suggestion — no SSE2 FMA

# x86 → PPC
ppc2x86 --from x86 --instr MOV
ppc2x86 --from x86 --instr PADDB
ppc2x86 --from x86 --instr SYSCALL --mode 64

# Pipe-friendly (no colour codes when stdout is not a TTY)
ppc2x86 --from ppc --instr add | cat
```

### Interactive REPL

```bash
ppc2x86           # enters REPL when no args are given
ppc2x86 --repl    # force REPL explicitly
```

REPL commands:

| Command | Description |
|---------|-------------|
| `lookup <mnemonic>` | Look up an instruction in the current direction/mode |
| `search <query>` | Search mnemonics, names, and descriptions |
| `set dir ppc\|x86` | Switch direction (PPC→x86 or x86→PPC) |
| `set mode 32\|64` | Switch 32-bit or 64-bit mode |
| `list categories` | Show all instruction categories for current ISA |
| `info <isa>` | Print a profile card for SPARC, alpha, mips, pahrisc, itanium, 68k, vax, ppc, x86 |
| `random fact` | Print a random ISA trivia fact |
| `help` | Show all commands |
| `quit` | Exit |

Example session:

```
$ ppc2x86

  PPC2x86 — ISA Translation Station  v1.0.0
  Direction: PPC → x86   Mode: 32-bit

ppc2x86[ppc/32]> lookup fmadd

  FMADD  [SUGGESTION]
  Floating-Point Multiply-Add

  → x86 analogues:
    VFMADD231SD   Fused Multiply-Add Scalar DP (231)
                  ⚠  Suggestion only — AVX FMA3 required; no SSE2 equivalent.

ppc2x86[ppc/32]> set dir x86
  Direction set to X86 → PPC

ppc2x86[x86/32]> lookup PADDB

  PADDB  [DIRECT]
  Add Packed Byte Integers

  ← PPC analogues:
    vaddubm   Vector Add Unsigned Byte Modulo

ppc2x86[x86/32]> info alpha
  ────────────────────────────────────────
  Alpha AXP
  Vendor  : Digital Equipment Corporation (DEC)
  Born    : 1992  Died: 2004
  ...

ppc2x86[x86/32]> random fact
  [MIPS — quirk]
  MIPS has a branch delay slot: the instruction immediately after every
  branch is always executed, even when the branch is taken. This quirk
  was a deliberate RISC pipeline optimisation that compilers learned
  to exploit — and that programmers learned to dread.

ppc2x86[x86/32]> quit
```

---

## Project Structure

```
PPC2x86/                    (packages below live in src/ppc2x86/)
├── src/ppc2x86/cli.py      ← Entry point — CLI single-shot, REPL, and GUI launch
├── pyproject.toml          ← packaging; wxPython is the optional [gui] extra
│
├── core/
│   ├── engine.py           ← InstructionEngine class — all lookup/search logic
│   └── fuzzy.py            ← Levenshtein distance + prefix-ranked fuzzy match
│
├── data/
│   ├── ppc_instructions.py ← 423 PPC mnemonic records (full metadata)
│   ├── x86_instructions.py ← 524 x86/x64 mnemonic records (full metadata)
│   ├── mappings.py         ← 273 PPC→x86 + 154 x86→PPC MappingEntry records
│   └── isa_trivia.py       ← 61 ISA facts, 9 profiles, 23 quotes, easter egg content
│
├── gui/
│   ├── app.py              ← PPC2x86App (wx.App) + MainFrame + menu + status bar
│   ├── main_panel.py       ← MainLookupPanel — search list + result panel + history
│   ├── mode_bar.py         ← Direction + mode toggle toolbar
│   ├── result_panel.py     ← Rich-text result display + suggestion warning banner
│   ├── isa_museum.py       ← ISA Museum tab, placard, timeline bar, compare dialog
│   ├── easter_eggs.py      ← EasterEggManager — Konami, graveyard, hidden menus
│   ├── theme.py            ← Colour palette, font helpers, apply_theme()
│   └── widgets/
│       ├── searchable_list.py  ← Live-filtering SearchCtrl + ListCtrl
│       ├── ticker_bar.py       ← Timer-driven scrolling trivia ticker
│       └── about_dialog.py     ← About dialog + hidden ★ click zone
│
├── LICENSE
└── README.md
```

---

## Architecture

```
ppc2x86/cli.py
    │
    ├── CLI path ──────────────────────────────────────────────────────────┐
    │   argparse → run_single_shot() or run_repl()                         │
    │                    │                                                  │
    │                    ▼                                                  │
    │             InstructionEngine (core/engine.py)                       │
    │                    │                                                  │
    │       ┌────────────┼────────────────┐                                │
    │       ▼            ▼                ▼                                │
    │   PPC_INSTRUCTIONS  X86_INSTRUCTIONS  PPC_TO_X86 / X86_TO_PPC       │
    │   (data/)           (data/)           (data/mappings.py)             │
    │                    │                                                  │
    │               fuzzy.py (fallback)                                    │
    │                                                                       │
    └── GUI path ───────────────────────────────────────────────────────── ┘
        PPC2x86App → MainFrame
            ├── ModeBar (direction + mode toggles)
            ├── AuiNotebook
            │     ├── MainLookupPanel
            │     │     ├── SearchableList ← InstructionEngine.search()
            │     │     └── ResultPanel   ← InstructionEngine.lookup()
            │     ├── ISAMuseumPanel
            │     │     ├── ISA sidebar (ListBox)
            │     │     ├── Museum placard (_TimelineBar painted via DC)
            │     │     └── Dialogs: Compare, ISA Timeline
            │     └── History Log tab
            ├── TickerBar (wx.Timer + ISA_FACTS)
            ├── StatusBar (right-click quotes)
            └── EasterEggManager
                  ├── Konami code detector
                  ├── Title click counter → ISA Graveyard
                  └── About ★ hidden zone
```

---

## Data Sources

All data is embedded in source files — no network access or external files required.

| Data | Source reference used |
|------|-----------------------|
| PPC instruction set | IBM POWER ISA v3.1 (OpenPOWER Foundation, public) |
| x86/x64 instruction set | Intel 64 and IA-32 Architectures Software Developer's Manual |
| x86-64 extensions | AMD64 Architecture Programmer's Manual |
| SPARC architecture | SPARC v8/v9 IEEE Std 1754, Sun/Oracle documentation |
| Alpha AXP | Digital/Compaq Alpha Architecture Reference Manual |
| MIPS | MIPS32/64 Architecture Reference Manuals (Wave Computing) |
| PA-RISC | HP PA-RISC 2.0 Architecture Reference Manual |
| Itanium (IA-64) | Intel Itanium Architecture Software Developer's Manual |
| 68k / 680x0 | Motorola M68000 Family Programmer's Reference Manual |
| VAX | DEC VAX Architecture Reference Manual |

---

## Confidence Levels

PPC2x86 uses three confidence levels for every mapping, displayed as colour-coded badges:

| Badge | Colour | Meaning |
|-------|--------|---------|
| `[DIRECT]` | Green | Semantically equivalent — same operation, same flags behaviour |
| `[CLOSE]` | Yellow | Functionally equivalent with noted caveats — endianness, register model, operand order, addressing differences |
| `[SUGGESTION]` | Orange | Best-effort approximation — the operation can be emulated but there is no direct analogue; always explained in the notes field |
| `[FUZZY]` | Dim | Your mnemonic was not found; these are the closest matches by edit distance |

When you see `[SUGGESTION]`, read the notes. Do not blindly copy the x86 mnemonic into your code.

---

## Notable Mappings Worth Knowing

| PPC | x86 | Confidence | Notes |
|-----|-----|------------|-------|
| `add` | `ADD` | DIRECT | PPC three-operand form maps via `LEA` when dest ≠ src |
| `lwz` | `MOV` | CLOSE | PPC is big-endian; x86 is little-endian — byte order differs |
| `lwarx` / `stwcx.` | `CMPXCHG` | SUGGESTION | Load-link/store-conditional ≠ compare-and-swap; semantics differ |
| `fmadd` | `VFMADD231SD` | SUGGESTION | No SSE2 FMA — requires AVX FMA3 (Intel Haswell 2013+) |
| `mfspr` / `mtspr` | `RDMSR` / `WRMSR` | SUGGESTION | SPR namespace ≠ MSR namespace; wildly different register IDs |
| `sc` | `SYSCALL` | DIRECT | Direct on Linux/macOS ABI; Windows uses `SYSCALL` differently |
| `sync` | `MFENCE` | DIRECT | Full memory barrier in both ISAs |
| `vperm` | `PSHUFB` | SUGGESTION | AltiVec `vperm` is a full 16-byte permute from two sources; `PSHUFB` permutes within one register using a different mask format |
| `cntlzw` | `LZCNT` | DIRECT | Note: `LZCNT` requires ABM or BMI1; older CPUs need `BSR` + adjustment |
| `blr` | `RET` | DIRECT | Both return to link register / return address on stack |

---

## Known Limitations

- **No binary encoding/decoding** — this is a mnemonic lookup tool, not an assembler or disassembler
- **No POWER10 / AMX / AVX-512** deep coverage — surface entries only
- **Condition register semantics** are simplified in the notes — CR field mapping to EFLAGS is architecture-deep and context-dependent; the suggestions in the CR category are starting points, not complete solutions
- **AltiVec → SSE2 mapping** is approximate — the vector models differ significantly in element ordering, saturation semantics, and permute operations
- **No Windows REPL color** — `readline` is stdlib on macOS/Linux; on Windows install `pyreadline3` for history support
- wxPython must be installed separately for the GUI; the CLI and data layer have zero external dependencies

---

## License

MIT — see [LICENSE](LICENSE).

---

## Credits

**From the minds of IBM Bob & Daneyand**

Built with Python 3, wxPython 4.2, and a deep love for instruction sets that most people have forgotten existed.

Special appreciation to the architects, engineers, and compiler writers whose work across five decades of CPU history made this project interesting enough to build.

*"The purpose of abstracting is not to be vague, but to create a new semantic level in which one can be absolutely precise."*  
— Edsger W. Dijkstra

---

> *From the minds of IBM Bob & Daneyand*

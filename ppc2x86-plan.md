# PPC2x86 — PowerPC ↔ x86/x64 Instruction Picker — Plan

## Top-Level Overview

Build a fully self-contained Python application that maps PowerPC (32-bit and 64-bit) instructions to their x86/x86-64 equivalents and vice-versa. When no direct analogue exists the tool suggests the closest approximations and marks them clearly as suggestions. All instruction data is embedded directly in Python source files — no external databases or network calls.

The project ships two front-ends that share a single core engine:

- **CLI mode** — single-shot (`ppc2x86 --from ppc --instr lwz`) and interactive REPL (run with no arguments).
- **GUI mode** — wxPython, elaborate "retro ISA museum" theme packed with easter eggs, hidden extras, and reference material about classic ISAs (SPARC, Alpha, MIPS, PA-RISC, Itanium, 68k, etc.).

The project lives at `/Users/daneyand/Documents/Bob/PPC2x86/`.

---

## Architecture Overview

```
PPC2x86/
├── ppc2x86.py              ← entry point (CLI + launches GUI)
├── core/
│   ├── __init__.py
│   ├── engine.py           ← lookup/suggestion logic
│   └── fuzzy.py            ← fuzzy / partial-match helpers
├── data/
│   ├── __init__.py
│   ├── ppc_instructions.py ← PPC 32 + 64 instruction table
│   ├── x86_instructions.py ← x86-32 + x86-64 instruction table
│   ├── mappings.py         ← PPC↔x86 mapping table (direct + suggested)
│   └── isa_trivia.py       ← historical ISA facts, quotes, Easter egg content
├── gui/
│   ├── __init__.py
│   ├── app.py              ← wx.App subclass, top-level frame
│   ├── main_panel.py       ← primary lookup panel
│   ├── mode_bar.py         ← PPC→x86 / x86→PPC / mode selector widget
│   ├── result_panel.py     ← instruction detail + analogue display
│   ├── isa_museum.py       ← "ISA Museum" bonus tab (SPARC, Alpha, etc.)
│   ├── easter_eggs.py      ← hidden interactions, konami code, etc.
│   ├── theme.py            ← colour palette, fonts, retro styling helpers
│   └── widgets/
│       ├── __init__.py
│       ├── searchable_list.py  ← filterable instruction list control
│       ├── ticker_bar.py       ← scrolling trivia ticker at the bottom
│       ├── about_dialog.py     ← credits + ISA timeline graphic
│       └── tooltip_rich.py     ← rich-text tooltip with opcode details
├── requirements.txt
└── README.md
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold & Entry Point

**Intent**
Create the directory tree, `requirements.txt`, and the main `ppc2x86.py` entry point that dispatches to CLI or GUI based on arguments. This gives a runnable skeleton before any data or logic exists.

**Expected Outcomes**
- `/Users/daneyand/Documents/Bob/PPC2x86/` directory exists with all sub-packages.
- `python ppc2x86.py --help` prints usage without error.
- `python ppc2x86.py --gui` prints "GUI not yet implemented" placeholder and exits cleanly.
- `python ppc2x86.py --from ppc --instr NOP` prints "Engine not yet implemented" placeholder and exits cleanly.
- `requirements.txt` lists `wxPython`.
- `README.md` has title, description, and usage skeleton.

**Todo List**
1. Create directory tree: `core/`, `data/`, `gui/`, `gui/widgets/` with `__init__.py` in each.
2. Write `requirements.txt` with `wxPython>=4.2`.
3. Write `ppc2x86.py` with `argparse` setup: flags `--gui`, `--from {ppc,x86}`, `--instr MNEMONIC`, `--mode {32,64}`, `--repl`.  When no args are given, launch REPL.  When `--gui` is given, launch GUI.  When `--from` + `--instr` are given, run single-shot lookup.
4. Write `README.md` stub with project title, one-paragraph description, requirements, and usage examples.

**Relevant Context**
- No sibling project conventions to follow — this is a Python project.
- Entry point must handle both CLI dispatch and GUI launch from the same file.

**Status** — `[ ] pending`

---

### Sub-Task 2 — PPC Instruction Data Table

**Intent**
Build the embedded PowerPC instruction database. This is the research-heavy sub-task. Every PPC integer, float, load/store, branch, condition register, vector (AltiVec/VMX), and 64-bit extended instruction gets a record.

**Expected Outcomes**
- `data/ppc_instructions.py` exports `PPC_INSTRUCTIONS: dict[str, dict]`.
- Each entry key is the canonical mnemonic (e.g. `"lwz"`, `"fmadd"`, `"stvx"`).
- Each value contains: `mnemonic`, `full_name`, `syntax`, `description`, `flags` (list of affected condition register bits or flags), `variants` (32-only / 64-only / both), `category` (one of: integer, float, load_store, branch, cr, vector, system, optional), `encoding` (brief binary format string).
- At least 300 distinct PPC mnemonics covered, spanning both PPC32 and PPC64 ISA.

**Todo List**
1. Research and compile PPC integer arithmetic/logical instructions (add, subf, mullw, divw, and, or, xor, neg, etc.) — include dot-form variants.
2. Research and compile PPC load/store instructions (lwz, lbz, lhz, stw, stb, sth, lwarx, stwcx, lmw, stmw, lfd, stfd, etc.).
3. Research and compile PPC branch and condition register instructions (b, bl, blr, bctr, bc, cmp, cmpi, cmpw, mfcr, mtcr, crand, etc.).
4. Research and compile PPC floating-point instructions (fadd, fsub, fmul, fdiv, fmadd, fabs, frsp, fctiw, fctiwz, etc.).
5. Research and compile PPC AltiVec/VMX vector instructions (vaddubm, vmuluwm, vperm, vsel, lvx, stvx, vcmpequw, etc.).
6. Research and compile PPC64-specific extended instructions (ld, std, ldarx, stdcx, mulld, divd, extsw, etc.).
7. Research and compile PPC system/privileged instructions (mtspr, mfspr, tlbie, rfi, sc, etc.).
8. Write `data/ppc_instructions.py` with the complete `PPC_INSTRUCTIONS` dict.

**Relevant Context**
- Sources: IBM PowerPC Architecture Book vols 1–3 (open), POWER ISA v3.1 (public).
- Mnemonics are case-insensitive in practice; store as lowercase.

**Status** — `[ ] pending`

---

### Sub-Task 3 — x86/x64 Instruction Data Table

**Intent**
Build the embedded x86 and x86-64 instruction database covering the instructions a compiler or programmer would realistically encounter as analogues for PPC code.

**Expected Outcomes**
- `data/x86_instructions.py` exports `X86_INSTRUCTIONS: dict[str, dict]`.
- Each entry contains: `mnemonic`, `full_name`, `syntax`, `description`, `flags` (EFLAGS bits affected), `variants` (32-only / 64-only / both), `category`, `encoding` (brief description), `sse_avx_extension` (None or extension name).
- At least 300 distinct x86/x64 mnemonics covering integer, floating-point (x87, SSE, SSE2), SIMD (SSE/AVX), string, bit manipulation, branch, system, and 64-bit-extended instructions.

**Todo List**
1. Compile x86 integer instructions (MOV, ADD, SUB, IMUL, IDIV, AND, OR, XOR, NOT, NEG, SHL, SHR, SAR, LEA, XCHG, CMPXCHG, etc.).
2. Compile x86 memory/addressing instructions (PUSH, POP, PUSHA/POPA, LOD/STO string variants, MOVSX, MOVZX, etc.).
3. Compile x86 branch/control instructions (JMP, Jcc family, CALL, RET, LOOP, INT, SYSCALL, SYSRET, etc.).
4. Compile x87 FPU instructions (FLD, FST, FADD, FSUB, FMUL, FDIV, FSIN, FCOS, FSQRT, FCOM, etc.).
5. Compile SSE/SSE2 instructions (MOVSS, ADDSS, MULSS, DIVSS, MOVAPS, ADDPS, MOVSD, ADDSD, PMULLW, etc.).
6. Compile x86-64 extensions (MOVSXD, CDQE, 64-bit REX-prefixed forms, SWAPGS, etc.).
7. Compile bit-manipulation and BMI instructions (BSF, BSR, BT, BTC, BTR, BTS, LZCNT, TZCNT, POPCNT, ANDN, etc.).
8. Write `data/x86_instructions.py` with the complete `X86_INSTRUCTIONS` dict.

**Relevant Context**
- Sources: Intel 64 and IA-32 Architectures Software Developer's Manual (public), AMD64 Architecture Programmer's Manual (public).

**Status** — `[ ] pending`

---

### Sub-Task 4 — PPC↔x86 Mapping Table

**Intent**
Build the authoritative mapping that connects PPC mnemonics to x86 mnemonics (and vice-versa). This is the intellectual core of the project. Each mapping entry records whether the relationship is direct or approximate, and why.

**Expected Outcomes**
- `data/mappings.py` exports:
  - `PPC_TO_X86: dict[str, MappingEntry]`
  - `X86_TO_PPC: dict[str, MappingEntry]`
- `MappingEntry` is a dataclass/dict with: `source`, `targets: list[str]`, `confidence` (`"direct"` | `"close"` | `"suggestion"`), `notes`, `mode` (`"32"` | `"64"` | `"both"`).
- Every PPC instruction from Sub-Task 2 has at least one mapping entry (even if confidence=`"suggestion"`).
- Every x86 instruction that is a known analogue for something in PPC has a reverse mapping.

**Todo List**
1. Map PPC integer arithmetic to x86 equivalents (add→ADD, subf→SUB, mullw→IMUL, divw→IDIV, etc.) — direct mappings.
2. Map PPC load/store to x86 MOV family (lwz→MOV, lbz→MOVZX, lha→MOVSX, lwarx→LOCK+MOV, stwcx→XCHG/CMPXCHG, etc.) — mostly direct with notes about addressing differences.
3. Map PPC branch/CR instructions to x86 Jcc, CALL, RET — note condition register differences.
4. Map PPC FP instructions to x87 and SSE/SSE2 (fadd→FADD or ADDSS/ADDSD, fmadd→no direct analogue → suggest FMA3 VFMADD, etc.).
5. Map PPC AltiVec to SSE/SSE2/AVX (vaddubm→PADDB, vmuluwm→PMULLD, vperm→PSHUFB suggestion, lvx→MOVDQU/MOVDQA, etc.).
6. Map PPC64 extensions to x86-64 equivalents (ld→MOV with 64-bit operand, mulld→IMUL 64-bit, etc.).
7. Map PPC system instructions — most are suggestions/no analogue (mtspr→MOV to CR4/MSR, sc→SYSCALL, etc.).
8. Build the reverse `X86_TO_PPC` dict by inverting and de-duplicating the forward table.
9. Write `data/mappings.py`.

**Relevant Context**
- Confidence levels matter for user trust — be conservative. When unsure, use `"suggestion"`.
- Notes field should explain semantic differences (register model, endianness, addressing mode).

**Status** — `[ ] pending`

---

### Sub-Task 5 — Historical ISA Trivia & Easter Egg Content

**Intent**
Populate `data/isa_trivia.py` with the rich content that feeds the GUI's easter eggs, ISA Museum tab, scrolling ticker, tooltips, and hidden panels. Covers SPARC, Alpha, MIPS, PA-RISC, Itanium (EPIC), Motorola 68k, VAX, and compiler/ISA history.

**Expected Outcomes**
- `data/isa_trivia.py` exports:
  - `ISA_FACTS: list[dict]` — at least 60 facts/trivia items, each with `isa`, `text`, `category` (`"history"` | `"design"` | `"quirk"` | `"compiler"` | `"benchmark"`).
  - `ISA_PROFILES: dict[str, dict]` — one profile per ISA: `name`, `vendor`, `year`, `bits`, `endian`, `registers`, `description`, `famous_for`, `died` (year or None).
  - `COMPILER_QUOTES: list[str]` — 20+ memorable quotes from ISA/compiler luminaries.
  - `KONAMI_UNLOCK_TEXT: str` — the secret message revealed by the Konami code.
  - `HIDDEN_MESSAGES: dict[str, str]` — keyed by trigger, value is revealed text.

**Todo List**
1. Research and write SPARC profile + 8 trivia items (register windows, SPARC64, Sun, Oracle).
2. Research and write Alpha profile + 8 trivia items (DEC, 64-bit pioneer, NT port, compaq, HP).
3. Research and write MIPS profile + 8 trivia items (RISC origin story, SGI, MIPS64, delay slots).
4. Research and write PA-RISC profile + 8 trivia items (HP Precision Architecture, Itanium transition).
5. Research and write Itanium profile + 8 trivia items (EPIC, IA-64, bundle format, compiler dependence, failure story).
6. Research and write 68k profile + 8 trivia items (Mac, Amiga, Atari ST, embedded longevity).
7. Research and write VAX profile + 5 trivia items (CISC pinnacle, VMS, DEC legacy).
8. Write 20+ compiler/ISA quotes (Patterson & Hennessy, Jim Keller, Dave Cutler, etc.).
9. Write Konami code reveal text, hidden ASCII art, and `HIDDEN_MESSAGES` entries.
10. Write `data/isa_trivia.py`.

**Relevant Context**
- Content should be factually accurate but written in an enthusiastic, retro-museum tone.
- Quotes should be attributed correctly.

**Status** — `[ ] pending`

---

### Sub-Task 6 — Core Lookup Engine

**Intent**
Write the `core/engine.py` lookup and suggestion engine that the CLI and GUI both call. No wxPython dependency — pure Python.

**Expected Outcomes**
- `core/engine.py` exports `InstructionEngine` class.
- `engine.lookup(mnemonic, direction, mode)` returns a `LookupResult` dataclass with: `source_instr`, `targets`, `confidence`, `notes`, `alternatives`.
- `engine.search(query, isa, mode)` returns a list of matching mnemonics (for the searchable list widget and REPL).
- `engine.list_categories(isa)` returns list of category names.
- `engine.get_isa_profile(isa_name)` returns profile dict from trivia data.
- All results correctly handle the 32/64-bit mode flag.
- `core/fuzzy.py` provides `fuzzy_match(query, candidates)` using simple edit-distance / prefix logic (no external lib).

**Todo List**
1. Define `LookupResult` dataclass in `engine.py`.
2. Implement `lookup()` — exact match first, then case-insensitive, then fuzzy fallback.
3. Implement `search()` — filters PPC or x86 instruction dict by substring/prefix on mnemonic, full_name, and description.
4. Implement `list_categories()`.
5. Implement `get_isa_profile()`.
6. Write `core/fuzzy.py` with `fuzzy_match()` using Levenshtein distance (implement from scratch, no `difflib` for correctness guarantee).
7. Write unit-level smoke tests inline as `if __name__ == "__main__"` block that exercises lookup for 10 known mappings.

**Relevant Context**
- Engine must be importable without wx installed (CLI-only environments).
- Confidence levels from mapping table must be passed through and exposed.

**Status** — `[ ] pending`

---

### Sub-Task 7 — CLI Front-End (Single-Shot + REPL)

**Intent**
Wire the entry point's CLI path to the engine. Deliver a polished terminal experience: colored output, suggestion warnings, and a full interactive REPL.

**Expected Outcomes**
- `python ppc2x86.py --from ppc --instr lwz --mode 32` prints a formatted result with mnemonic, analogue(s), confidence badge, and notes.
- `python ppc2x86.py --from x86 --instr MOV` prints PPC analogues.
- `python ppc2x86.py` (no args) enters REPL: prompts `ppc2x86> `, accepts commands, shows `help`, `quit`.
- REPL supports: `set mode 32|64`, `set dir ppc|x86`, `lookup <mnemonic>`, `search <query>`, `list categories`, `info <isa>`, `random fact`.
- Suggestions are flagged with a `[SUGGESTION]` badge in output.
- ANSI color used when stdout is a TTY; plain text otherwise.

**Todo List**
1. Write `cli/` module (or inline in `ppc2x86.py`) with `format_result()` — renders `LookupResult` to terminal with ANSI colors.
2. Implement single-shot path: parse args, call engine, print result, exit.
3. Implement REPL: `readline`-powered prompt loop, command dispatcher, `help` text.
4. Add `random fact` command that pulls from `ISA_FACTS`.
5. Add `info <isa>` command that prints an ISA profile card.
6. Ensure graceful "no match found, try fuzzy suggestions" fallback message.

**Relevant Context**
- Use `sys.stdout.isatty()` to detect color support.
- `readline` is stdlib on macOS/Linux; on Windows use `pyreadline3` as optional import.

**Status** — `[ ] pending`

---

### Sub-Task 8 — GUI Foundation (wxPython App + Theme)

**Intent**
Stand up the wxPython application shell with the retro ISA museum theme applied. No instruction data yet — just the frame, menu bar, status bar, colour palette, and the tab/panel scaffold.

**Expected Outcomes**
- `python ppc2x86.py --gui` opens a window titled "PPC2x86 — ISA Translation Station".
- Window has: menu bar (File, View, ISA Museum, Extras, Help), tab strip with "Lookup", "ISA Museum", "History Log" tabs, scrolling ticker bar at the bottom, status bar.
- Theme applied: dark background, green/amber phosphor-terminal color scheme, monospace font.
- Menu items exist (most not yet wired): About, Preferences, Konami Code hint in Help menu.

**Todo List**
1. Write `gui/theme.py` with color constants, font helpers, and `apply_theme(window)` utility.
2. Write `gui/app.py` with `PPC2x86App(wx.App)` and `MainFrame(wx.Frame)` — sets title, size, icon (text-art fallback if no image asset).
3. Write `gui/mode_bar.py` — direction toggle (PPC→x86 / x86→PPC) and mode selector (32-bit / 64-bit) as a toolbar-style panel.
4. Write `gui/widgets/ticker_bar.py` — `wx.Timer`-driven scrolling text ticker fed by `ISA_FACTS`.
5. Add tab strip with placeholder panels for Lookup, ISA Museum, History Log.
6. Wire menu File→Quit, Help→About (stub dialog).

**Relevant Context**
- wxPython 4.2 API — use `wx.Panel`, `wx.Notebook` or `wx.aui.AuiNotebook` for tabs.
- Theme must be applied before any child widgets are created to avoid flicker.

**Status** — `[ ] pending`

---

### Sub-Task 9 — GUI Lookup Panel

**Intent**
Build the primary lookup panel: searchable instruction list on the left, result detail panel on the right, direction/mode controls wired to the engine.

**Expected Outcomes**
- Left pane: filterable `wx.ListCtrl` showing all PPC (or x86) mnemonics with their category.
- Search box above the list filters in real-time as the user types.
- Selecting an instruction fires a lookup and populates the right pane.
- Right pane shows: source mnemonic + description, analogue(s) with confidence badge (direct/close/suggestion), notes, syntax.
- Suggestion results displayed with a yellow warning banner: "⚠ This is a suggested analogue, not a guaranteed equivalent."
- Direction toggle (PPC→x86 / x86→PPC) swaps the list source and re-runs the lookup.
- Mode toggle (32/64) re-runs the lookup with the new mode.

**Todo List**
1. Write `gui/widgets/searchable_list.py` — `wx.Panel` wrapping a `wx.SearchCtrl` + `wx.ListCtrl` with live filtering.
2. Write `gui/result_panel.py` — renders `LookupResult`; uses rich-text (`wx.richtext.RichTextCtrl`) for formatted output.
3. Write `gui/main_panel.py` — `wx.SplitterWindow` combining the list and result panel; connects events to engine calls.
4. Wire direction and mode toggles from `mode_bar.py` to `main_panel.py` via wx events or callbacks.
5. Add copy-to-clipboard button on the result panel.
6. Populate the "History Log" tab with each successful lookup (mnemonic, direction, timestamp).

**Relevant Context**
- `wx.richtext.RichTextCtrl` supports colored text and bold — use for confidence badge coloring.
- Keep engine calls synchronous (the engine is fast); no threading needed.

**Status** — `[ ] pending`

---

### Sub-Task 10 — ISA Museum Tab

**Intent**
Build the "ISA Museum" tab — a visually rich, browsable reference of historical architectures fed by `isa_trivia.py`. This is one of the main "fun extras" visible at all times.

**Expected Outcomes**
- Tab contains a left sidebar listing all ISAs (SPARC, Alpha, MIPS, PA-RISC, Itanium, 68k, VAX, PPC, x86).
- Selecting an ISA shows a "museum placard" style panel: name, vendor, years active, bit width, endianness, register count, description, "Famous For" section, and a timeline bar graphic.
- A "Random Fact" button shows a random trivia item for that ISA in a styled callout box.
- A "Compare" button opens a side-by-side ISA comparison sub-panel.
- Footer shows `ISA_PROFILES` count and total fact count.

**Todo List**
1. Write `gui/isa_museum.py` with `ISAMuseumPanel(wx.Panel)`.
2. Implement left sidebar as `wx.ListBox` populated from `ISA_PROFILES` keys.
3. Implement museum placard panel using `wx.StaticText` labels and custom-drawn timeline bar (`wx.PaintDC`).
4. Implement "Random Fact" button wired to `ISA_FACTS` filtered by selected ISA.
5. Implement side-by-side comparison sub-panel (two placards, auto-scrolling).
6. Style to match the retro theme from `theme.py`.

**Relevant Context**
- Timeline bar should span 1960–2010 and mark each ISA's birth/death year visually.

**Status** — `[ ] pending`

---

### Sub-Task 11 — Easter Eggs & Hidden Extras

**Intent**
Implement all the hidden and plain-sight fun extras: Konami code, ASCII art splash, hidden menu items, compiler quote ticker, click secrets, and the animated "ISA Graveyard".

**Expected Outcomes**
- Konami code (↑↑↓↓←→←→BA) detected globally in the window triggers a full-screen ASCII art splash with `KONAMI_UNLOCK_TEXT`.
- Clicking the title label 7 times reveals the "ISA Graveyard" panel (tombstones for dead ISAs).
- A "secret" menu item appears in Help after the Konami code is entered: "Show Compiler Quotes".
- The ticker bar cycles through ISA trivia facts; right-clicking the ticker reveals a context menu to filter by ISA.
- About dialog has a hidden clickable area that shows a scrolling credits panel with compiler luminaries.
- Status bar right-click shows a random `COMPILER_QUOTES` entry.
- "Extras" menu has visible items: ISA Timeline, Instruction Count Stats, Random ISA Fact, Benchmark Trivia.

**Todo List**
1. Write `gui/easter_eggs.py` with `EasterEggManager` that attaches key/click listeners to the main frame.
2. Implement Konami code detector as a key event chain tracker.
3. Implement title-click counter and ISA Graveyard panel (wx.Dialog with tombstone art drawn via `wx.DC`).
4. Implement "Show Compiler Quotes" secret menu item reveal.
5. Wire ticker right-click context menu for ISA filtering.
6. Implement About dialog hidden click zone.
7. Implement status bar right-click for random quote.
8. Wire all "Extras" menu visible items to their respective panels/dialogs.
9. Write `gui/widgets/about_dialog.py` with credits and hidden zone.

**Relevant Context**
- Use `wx.KeyEvent` at the frame level for Konami detection; accumulate key sequence in `EasterEggManager`.
- Keep all easter egg state in `EasterEggManager` — no globals.

**Status** — `[ ] pending`

---

### Sub-Task 12 — README & Polish

**Intent**
Write the full README, finalize `requirements.txt`, add a launch helper script, and do a final integration pass — ensure CLI and GUI both work end-to-end with real data.

**Expected Outcomes**
- `README.md` covers: project description, screenshots (ASCII art stand-ins), requirements, install steps, CLI usage with examples, GUI overview with feature list, easter egg hints section, architecture diagram, data sources list, and license.
- `requirements.txt` is complete and pinned to a minimum version.
- Running `python ppc2x86.py --from ppc --instr add` returns a correct result.
- Running `python ppc2x86.py --gui` opens the full GUI.
- No import errors, no bare exceptions swallowed silently.

**Todo List**
1. Write complete `README.md`.
2. Finalize `requirements.txt` (wxPython>=4.2).
3. Verify CLI single-shot path with 10 test mnemonics.
4. Verify REPL commands all work.
5. Verify GUI launches, tabs work, lookup works, ticker scrolls.
6. Verify Konami code and at least two other easter eggs fire correctly.
7. Fix any integration bugs found during verification.

**Relevant Context**
- This is the final integration sub-task — earlier sub-tasks should all be complete.

**Status** — `[ ] pending`

---

## Data Sources Reference

| Source | URL / Reference |
|--------|-----------------|
| POWER ISA v3.1 | IBM OpenPOWER Foundation (public PDF) |
| Intel SDM | intel.com/sdm (free download) |
| AMD64 APM | amd.com/en/support/tech-docs (free) |
| SPARC v8/v9 | sparc.com / IEEE Std 1754 |
| Alpha AXP ref | Digital/Compaq architecture manuals |
| MIPS32/64 ref | MIPS Technologies / Wave Computing |
| PA-RISC 2.0 | HP/Hewlett Packard Architecture reference |
| IA-64 ISA | Intel Itanium Architecture manuals |
| 68k / 680x0 | Motorola M68000 Family Programmer's Reference |
| VAX | DEC VAX Architecture Reference Manual |

---

## Non-Goals

- No assembler or disassembler — instruction lookup only.
- No binary encoding/decoding of actual machine code.
- No POWER10 / AMX / AVX-512 deep coverage (surface entries only).
- No network features, telemetry, or update checks.
- No macOS-app bundle / DMG packaging (plain Python script).

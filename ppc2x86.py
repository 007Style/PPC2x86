#!/usr/bin/env python3
"""
ppc2x86 — PowerPC ↔ x86/x64 Instruction Picker
================================================

Translate PowerPC mnemonics to their x86/x64 equivalents (and vice-versa),
or launch the retro ISA-museum GUI.

Usage examples
--------------
Single-shot lookup (PPC → x86):
    python ppc2x86.py --from ppc --instr lwz
    python ppc2x86.py --from ppc --instr fmadd --mode 64

Single-shot lookup (x86 → PPC):
    python ppc2x86.py --from x86 --instr MOV
    python ppc2x86.py --from x86 --instr PADDB --mode 64

Interactive REPL (no arguments, or force with --repl):
    python ppc2x86.py
    python ppc2x86.py --repl

Launch the wxPython GUI:
    python ppc2x86.py --gui
    python ppc2x86.py --gui --mode 64

REPL commands
-------------
    lookup <mnemonic>       Look up the current source ISA mnemonic
    search <query>          Full-text search across all instructions
    set dir ppc|x86         Switch source ISA direction
    set mode 32|64          Switch 32/64-bit mode
    list categories         List available instruction categories
    info <isa>              Show ISA profile card (sparc, alpha, mips, …)
    random fact             Display a random ISA trivia fact
    help                    Show this help text
    quit / exit             Exit the REPL
"""

import argparse
import sys
import os

# ---------------------------------------------------------------------------
# Colour helpers (ANSI; disabled when not a TTY)
# ---------------------------------------------------------------------------

_USE_COLOR = sys.stdout.isatty()

_C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[32m",
    "yellow": "\033[33m",
    "cyan":   "\033[36m",
    "red":    "\033[31m",
    "blue":   "\033[34m",
    "dim":    "\033[2m",
}


def _c(name: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{_C[name]}{text}{_C['reset']}"


# ---------------------------------------------------------------------------
# Engine import (lazy — avoids import cost when --gui branches early)
# ---------------------------------------------------------------------------

def _get_engine():
    """Import and return a shared InstructionEngine instance."""
    # Add the project root to sys.path so sub-packages resolve correctly
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    from core.engine import InstructionEngine
    return InstructionEngine()


# ---------------------------------------------------------------------------
# Result formatting
# ---------------------------------------------------------------------------

_CONF_COLOR = {
    "direct":     "green",
    "close":      "cyan",
    "suggestion": "yellow",
    "none":       "red",
    "fuzzy":      "dim",
}

_CONF_LABEL = {
    "direct":     "[DIRECT]",
    "close":      "[CLOSE]",
    "suggestion": "[SUGGESTION]",
    "none":       "[NO MATCH]",
    "fuzzy":      "[FUZZY]",
}


def format_result(result, direction: str) -> str:
    """Render a LookupResult to a multi-line terminal string."""
    lines = []
    conf = result.confidence
    color = _CONF_COLOR.get(conf, "dim")
    badge = _CONF_LABEL.get(conf, f"[{conf.upper()}]")

    src = result.source_mnemonic
    si = result.source_instr

    lines.append("")
    lines.append(_c("bold", f"  {src.upper()}") + "  " + _c(color, badge))
    if si:
        lines.append(_c("dim", f"  {si.get('full_name', '')}"))
        lines.append(f"  Syntax : {si.get('syntax', 'n/a')}")
        lines.append(f"  {si.get('description', '')}")

    if conf == "fuzzy":
        lines.append("")
        lines.append(_c("yellow", "  No exact match found.") + " Did you mean:")
        for mnem, score in result.alternatives:
            lines.append(f"    {_c('cyan', mnem):<20}  score={score:.2f}")
        lines.append("")
        return "\n".join(lines)

    if conf == "none":
        lines.append("")
        lines.append(_c("red", f"  {result.notes}"))
        lines.append("")
        return "\n".join(lines)

    arrow = "→" if direction == "ppc" else "←"
    dest_isa = "x86" if direction == "ppc" else "PPC"
    lines.append("")
    lines.append(_c("bold", f"  {arrow} {dest_isa} analogues:"))

    for i, tgt in enumerate(result.targets):
        ti = result.target_instrs[i] if i < len(result.target_instrs) else None
        fname = ti.get("full_name", "") if ti else ""
        syn = ti.get("syntax", "") if ti else ""
        desc = ti.get("description", "") if ti else ""
        lines.append(f"    {_c('bold', tgt):<22}  {fname}")
        if syn:
            lines.append(f"    {'':22}  Syntax: {syn}")
        if desc:
            lines.append(f"    {'':22}  {_c('dim', desc[:80])}")

    if result.notes:
        lines.append("")
        if conf == "suggestion":
            lines.append(_c("yellow", "  ⚠  " + result.notes))
        else:
            lines.append(_c("dim", "  ℹ  " + result.notes))

    lines.append("")
    return "\n".join(lines)


def format_isa_profile(profile: dict) -> str:
    """Render an ISA profile dict as a museum-placard style string."""
    lines = []
    w = 60
    lines.append("  " + "─" * w)
    lines.append(f"  {_c('bold', profile['name'])}")
    lines.append(f"  Vendor  : {profile['vendor']}")
    lines.append(f"  Born    : {profile['year']}  "
                 f"Died: {profile.get('died') or 'still alive'}")
    lines.append(f"  Bits    : {profile['bits']}-bit")
    lines.append(f"  Endian  : {profile['endian']}")
    lines.append(f"  Regs    : {profile['registers']} integer registers")
    lines.append("")
    desc = profile.get("description", "")
    # Word-wrap at ~58 chars
    import textwrap
    for line in textwrap.wrap(desc, width=58):
        lines.append(f"  {line}")
    lines.append("")
    lines.append(_c("dim", "  Famous for:"))
    for line in textwrap.wrap(profile.get("famous_for", ""), width=58):
        lines.append(f"  {line}")
    lines.append("  " + "─" * w)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppc2x86",
        description=(
            "PPC2x86 — PowerPC ↔ x86/x64 Instruction Picker.\n\n"
            "Translates PowerPC mnemonics to x86/x64 equivalents (and vice-versa). "
            "Run without arguments to enter the interactive REPL."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the wxPython GUI (requires wxPython>=4.2).",
    )
    parser.add_argument(
        "--from",
        dest="source_isa",
        choices=["ppc", "x86"],
        metavar="{ppc,x86}",
        help="Source ISA for a single-shot lookup.",
    )
    parser.add_argument(
        "--instr",
        dest="mnemonic",
        metavar="MNEMONIC",
        help="Instruction mnemonic to look up (e.g. lwz, MOV).",
    )
    parser.add_argument(
        "--mode",
        choices=["32", "64"],
        default="32",
        help="Target bit-mode: 32 (default) or 64.",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        help="Force interactive REPL.",
    )

    return parser


# ---------------------------------------------------------------------------
# Single-shot
# ---------------------------------------------------------------------------

def run_single_shot(args: argparse.Namespace) -> None:
    engine = _get_engine()
    result = engine.lookup(args.mnemonic, args.source_isa, args.mode)
    print(format_result(result, args.source_isa))
    sys.exit(0)


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

_REPL_HELP = """\
Commands
--------
  lookup <mnemonic>       Translate mnemonic (uses current dir/mode)
  search <query>          Full-text search instructions
  set dir ppc|x86         Switch direction
  set mode 32|64          Switch bit mode
  list categories         List instruction categories
  info <isa>              Show ISA profile (sparc, alpha, mips, pa-risc,
                          itanium, 68k, vax, ppc, x86)
  random fact [<isa>]     Random ISA trivia fact
  help                    Show this help
  quit / exit             Exit
"""


def _repl_banner() -> str:
    return _c("bold", "\n  PPC2x86 — ISA Translation Station  ") + _c("dim", "v1.0.0\n")


def run_repl(args: argparse.Namespace) -> None:
    engine = _get_engine()

    # Optional readline for history
    try:
        import readline  # noqa: F401
    except ImportError:
        try:
            import pyreadline3 as readline  # noqa: F401
        except ImportError:
            pass

    from data.isa_trivia import COMPILER_QUOTES
    import random

    direction = "ppc"
    mode = getattr(args, "mode", "32")

    print(_repl_banner())
    print(_c("dim", f"  Direction: {direction.upper()} → {'x86' if direction == 'ppc' else 'PPC'}   "
             f"Mode: {mode}-bit"))
    print(_c("dim", "  Type 'help' for commands, 'quit' to exit.\n"))

    # Random quote on start
    print(_c("cyan", f"  \"{random.choice(COMPILER_QUOTES)}\"\n"))

    try:
        while True:
            try:
                prompt = _c("green", f"ppc2x86[{direction}/{mode}]> ")
                line = input(prompt).strip()
            except EOFError:
                print()
                break
            if not line:
                continue

            parts = line.split(None, 1)
            cmd = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""

            if cmd in ("quit", "exit", "q"):
                break

            elif cmd == "help":
                print(_REPL_HELP)

            elif cmd == "lookup" and rest:
                result = engine.lookup(rest.strip(), direction, mode)
                print(format_result(result, direction))

            elif cmd == "search" and rest:
                isa = direction  # search in source ISA
                matches = engine.search(rest.strip(), isa, mode)
                if matches:
                    print(f"\n  {len(matches)} matches in {isa.upper()}:")
                    for m in matches:
                        print(f"    {_c('cyan', m)}")
                else:
                    print(_c("yellow", f"  No matches for '{rest.strip()}'."))
                print()

            elif cmd == "set":
                sub_parts = rest.lower().split()
                if len(sub_parts) == 2 and sub_parts[0] == "dir":
                    if sub_parts[1] in ("ppc", "x86"):
                        direction = sub_parts[1]
                        dest = "x86" if direction == "ppc" else "PPC"
                        print(_c("cyan", f"  Direction set to {direction.upper()} → {dest}\n"))
                    else:
                        print(_c("red", "  Usage: set dir ppc|x86\n"))
                elif len(sub_parts) == 2 and sub_parts[0] == "mode":
                    if sub_parts[1] in ("32", "64"):
                        mode = sub_parts[1]
                        print(_c("cyan", f"  Mode set to {mode}-bit\n"))
                    else:
                        print(_c("red", "  Usage: set mode 32|64\n"))
                else:
                    print(_c("red", "  Usage: set dir ppc|x86  OR  set mode 32|64\n"))

            elif cmd == "list" and rest.lower().startswith("cat"):
                cats = engine.list_categories(direction)
                print(f"\n  Categories ({direction.upper()}):")
                for cat in cats:
                    print(f"    {_c('cyan', cat)}")
                print()

            elif cmd == "info" and rest:
                isa_name = rest.strip().lower()
                profile = engine.get_isa_profile(isa_name)
                if profile:
                    print(format_isa_profile(profile))
                else:
                    avail = ", ".join(sorted(
                        ["sparc", "alpha", "mips", "pa-risc",
                         "itanium", "68k", "vax", "ppc", "x86"]
                    ))
                    print(_c("yellow", f"  Unknown ISA '{isa_name}'."))
                    print(_c("dim", f"  Available: {avail}\n"))

            elif cmd == "random" and rest.lower().startswith("fact"):
                parts2 = rest.split(None, 1)
                isa_filter = parts2[1].strip() if len(parts2) > 1 else None
                fact = engine.random_fact(isa_filter)
                if fact:
                    label = fact.get("isa", "").upper()
                    cat = fact.get("category", "")
                    print(f"\n  {_c('bold', label)}  {_c('dim', '[' + cat + ']')}")
                    import textwrap
                    for line in textwrap.wrap(fact["text"], width=70):
                        print(f"  {line}")
                    print()
                else:
                    print(_c("yellow", f"  No facts found for '{isa_filter}'.\n"))

            else:
                # Try interpreting the whole line as a mnemonic lookup
                result = engine.lookup(line, direction, mode)
                print(format_result(result, direction))

    except KeyboardInterrupt:
        print()

    sys.exit(0)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def run_gui(args: argparse.Namespace) -> None:
    """Launch the wxPython GUI."""
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    try:
        import wx  # noqa: F401
    except ImportError:
        print(
            "wxPython is not installed. Install it with:\n"
            "  pip install wxPython\n"
            "or visit https://wxpython.org/pages/downloads/"
        )
        sys.exit(1)
    try:
        from gui.app import PPC2x86App
    except ImportError:
        print("GUI not yet fully implemented.")
        sys.exit(0)
    app = PPC2x86App(initial_mode=args.mode)
    app.MainLoop()
    sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.gui:
        run_gui(args)
    elif args.repl:
        run_repl(args)
    elif args.source_isa and args.mnemonic:
        run_single_shot(args)
    elif args.source_isa and not args.mnemonic:
        parser.error("--from requires --instr MNEMONIC.")
    elif args.mnemonic and not args.source_isa:
        parser.error("--instr requires --from {ppc,x86}.")
    else:
        run_repl(args)


if __name__ == "__main__":
    main()

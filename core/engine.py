"""
engine.py — Core lookup and search engine for PPC2x86.

This module has NO dependency on wxPython and can be used in CLI-only
environments.

Public API
----------
LookupResult    dataclass returned by InstructionEngine.lookup()
InstructionEngine
    .lookup(mnemonic, direction, mode)  → LookupResult
    .search(query, isa, mode)           → list[str]
    .list_categories(isa)               → list[str]
    .get_isa_profile(isa_name)          → dict | None
    .random_fact(isa)                   → dict | None
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from data.ppc_instructions import PPC_INSTRUCTIONS
from data.x86_instructions import X86_INSTRUCTIONS
from data.mappings import PPC_TO_X86, X86_TO_PPC, MappingEntry
from data.isa_trivia import ISA_FACTS, ISA_PROFILES, COMPILER_QUOTES
from core.fuzzy import fuzzy_match


@dataclass
class LookupResult:
    """The result of a single instruction lookup."""
    source_mnemonic: str           # what the user asked for
    source_instr: dict | None      # full instruction record (or None if unknown)
    targets: list[str]             # matched destination mnemonics
    target_instrs: list[dict]      # full records for each target
    confidence: str                # "direct" | "close" | "suggestion" | "none" | "fuzzy"
    notes: str                     # explanation text
    mode: str                      # "32" | "64" | "both"
    alternatives: list[tuple[str, float]] = field(default_factory=list)
    # alternatives: (mnemonic, score) pairs when source wasn't found exactly


class InstructionEngine:
    """
    Stateless lookup engine.  Create once, call methods freely.
    """

    def __init__(self) -> None:
        self._ppc = PPC_INSTRUCTIONS      # lowercase keys
        self._x86 = X86_INSTRUCTIONS      # uppercase keys
        self._ppc_to_x86 = PPC_TO_X86
        self._x86_to_ppc = X86_TO_PPC

    # ------------------------------------------------------------------
    # Public: lookup
    # ------------------------------------------------------------------

    def lookup(
        self,
        mnemonic: str,
        direction: str = "ppc",  # "ppc" → x86, "x86" → ppc
        mode: str = "32",
    ) -> LookupResult:
        """
        Look up *mnemonic* in the given direction.

        Steps:
        1. Exact match (case-insensitive).
        2. Fuzzy fallback — returns top alternatives with confidence="fuzzy".
        """
        direction = direction.lower()
        if direction not in ("ppc", "x86"):
            raise ValueError(f"direction must be 'ppc' or 'x86', got {direction!r}")
        if mode not in ("32", "64", "both"):
            mode = "32"

        if direction == "ppc":
            return self._lookup_ppc(mnemonic, mode)
        else:
            return self._lookup_x86(mnemonic, mode)

    def _lookup_ppc(self, mnemonic: str, mode: str) -> LookupResult:
        key = mnemonic.lower()

        # --- exact match ---
        mapping: MappingEntry | None = self._ppc_to_x86.get(key)
        if mapping and self._mode_ok(mapping.mode, mode):
            source_instr = self._ppc.get(key)
            targets, target_instrs = self._resolve_x86_targets(mapping.targets)
            return LookupResult(
                source_mnemonic=mnemonic,
                source_instr=source_instr,
                targets=targets,
                target_instrs=target_instrs,
                confidence=mapping.confidence,
                notes=mapping.notes,
                mode=mapping.mode,
            )

        # Check if the mapping exists but wrong mode
        if mapping and not self._mode_ok(mapping.mode, mode):
            return LookupResult(
                source_mnemonic=mnemonic,
                source_instr=self._ppc.get(key),
                targets=[],
                target_instrs=[],
                confidence="none",
                notes=(
                    f"'{key}' exists but is only available in "
                    f"{mapping.mode}-bit mode (requested: {mode}-bit)."
                ),
                mode=mode,
            )

        # --- fuzzy fallback ---
        all_ppc_keys = list(self._ppc_to_x86.keys())
        alts = fuzzy_match(key, all_ppc_keys, max_results=6, threshold=0.35)
        return LookupResult(
            source_mnemonic=mnemonic,
            source_instr=None,
            targets=[],
            target_instrs=[],
            confidence="fuzzy",
            notes=f"No exact match for '{mnemonic}'. Did you mean one of these?",
            mode=mode,
            alternatives=alts,
        )

    def _lookup_x86(self, mnemonic: str, mode: str) -> LookupResult:
        key = mnemonic.upper()

        mapping: MappingEntry | None = self._x86_to_ppc.get(key)
        if mapping and self._mode_ok(mapping.mode, mode):
            source_instr = self._x86.get(key)
            targets, target_instrs = self._resolve_ppc_targets(mapping.targets)
            return LookupResult(
                source_mnemonic=mnemonic,
                source_instr=source_instr,
                targets=targets,
                target_instrs=target_instrs,
                confidence=mapping.confidence,
                notes=mapping.notes,
                mode=mapping.mode,
            )

        if mapping and not self._mode_ok(mapping.mode, mode):
            return LookupResult(
                source_mnemonic=mnemonic,
                source_instr=self._x86.get(key),
                targets=[],
                target_instrs=[],
                confidence="none",
                notes=(
                    f"'{key}' exists but is only available in "
                    f"{mapping.mode}-bit mode (requested: {mode}-bit)."
                ),
                mode=mode,
            )

        all_x86_keys = list(self._x86_to_ppc.keys())
        alts = fuzzy_match(key.lower(), [k.lower() for k in all_x86_keys],
                           max_results=6, threshold=0.35)
        # Restore original casing
        lower_to_orig = {k.lower(): k for k in all_x86_keys}
        alts = [(lower_to_orig.get(a, a), s) for a, s in alts]
        return LookupResult(
            source_mnemonic=mnemonic,
            source_instr=None,
            targets=[],
            target_instrs=[],
            confidence="fuzzy",
            notes=f"No exact match for '{mnemonic}'. Did you mean one of these?",
            mode=mode,
            alternatives=alts,
        )

    # ------------------------------------------------------------------
    # Public: search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        isa: str = "ppc",
        mode: str = "32",
    ) -> list[str]:
        """
        Full-text search across mnemonic, full_name, and description.
        Returns a list of matching mnemonics (up to 50).
        """
        isa = isa.lower()
        q = query.lower()
        table = self._ppc if isa == "ppc" else self._x86
        results: list[str] = []

        for mnemonic, record in table.items():
            variant = record.get("variants", "both")
            if not self._mode_ok(variant, mode):
                continue
            haystack = " ".join([
                record.get("mnemonic", ""),
                record.get("full_name", ""),
                record.get("description", ""),
                record.get("category", ""),
            ]).lower()
            if q in haystack:
                results.append(mnemonic)
            if len(results) >= 50:
                break

        return results

    # ------------------------------------------------------------------
    # Public: list_categories
    # ------------------------------------------------------------------

    def list_categories(self, isa: str = "ppc") -> list[str]:
        """Return sorted unique category names for *isa*."""
        table = self._ppc if isa.lower() == "ppc" else self._x86
        return sorted({r.get("category", "other") for r in table.values()})

    # ------------------------------------------------------------------
    # Public: get_isa_profile
    # ------------------------------------------------------------------

    def get_isa_profile(self, isa_name: str) -> dict | None:
        """Return the ISA profile dict, or None if not found."""
        return ISA_PROFILES.get(isa_name.lower())

    # ------------------------------------------------------------------
    # Public: random_fact
    # ------------------------------------------------------------------

    def random_fact(self, isa: str | None = None) -> dict | None:
        """
        Return a random fact from ISA_FACTS.
        If *isa* is given, restrict to that ISA's facts.
        Returns None if no facts are available.
        """
        pool = ISA_FACTS
        if isa:
            pool = [f for f in ISA_FACTS if f.get("isa") == isa.lower()]
        if not pool:
            return None
        return random.choice(pool)

    # ------------------------------------------------------------------
    # Public: get_compiler_quote
    # ------------------------------------------------------------------

    def get_compiler_quote(self) -> str:
        """Return a random compiler/ISA quote."""
        if not COMPILER_QUOTES:
            return ""
        return random.choice(COMPILER_QUOTES)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _mode_ok(entry_mode: str, requested_mode: str) -> bool:
        """True when *entry_mode* is compatible with *requested_mode*."""
        if entry_mode == "both":
            return True
        if requested_mode == "both":
            return True
        return entry_mode == requested_mode

    def _resolve_x86_targets(self, targets: list[str]) -> tuple[list[str], list[dict]]:
        instrs = [self._x86[t] for t in targets if t in self._x86]
        return targets, instrs

    def _resolve_ppc_targets(self, targets: list[str]) -> tuple[list[str], list[dict]]:
        instrs = [self._ppc[t] for t in targets if t in self._ppc]
        return targets, instrs


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    engine = InstructionEngine()

    TESTS = [
        # (mnemonic, direction, mode, expected_confidence_not_fuzzy)
        ("add",      "ppc", "32", True),
        ("lwz",      "ppc", "32", True),
        ("blr",      "ppc", "32", True),
        ("fadd",     "ppc", "32", True),
        ("vaddubm",  "ppc", "32", True),
        ("sc",       "ppc", "32", True),
        ("MOV",      "x86", "32", True),
        ("ADD",      "x86", "32", True),
        ("PADDB",    "x86", "32", True),
        ("SYSCALL",  "x86", "32", True),
        # fuzzy
        ("lwzz",     "ppc", "32", False),
        ("MOOOV",    "x86", "32", False),
    ]

    passed = 0
    failed = 0
    for mnem, direction, mode, expect_found in TESTS:
        r = engine.lookup(mnem, direction, mode)
        found = r.confidence != "fuzzy"
        ok = found == expect_found
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(
            f"[{status}] lookup({mnem!r}, {direction!r}, {mode!r}) → "
            f"conf={r.confidence!r} targets={r.targets}"
        )

    print(f"\n{passed} passed / {failed} failed out of {len(TESTS)} tests")

    # Search test
    results = engine.search("load", "ppc", "32")
    print(f"\nsearch('load', ppc, 32): {len(results)} results → {results[:5]}")

    # Categories
    print(f"\nPPC categories: {engine.list_categories('ppc')}")
    print(f"x86 categories: {engine.list_categories('x86')}")

    # ISA profile
    p = engine.get_isa_profile("alpha")
    print(f"\nalpha profile: {p['name']} ({p['year']}) — {p['famous_for'][:60]}…")

    # Random fact
    f = engine.random_fact("sparc")
    print(f"\nRandom SPARC fact: {f['text'][:80]}…")

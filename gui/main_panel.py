"""
main_panel.py — Primary lookup panel combining the searchable list and result panel.

Layout:
  [SearchableList (left)] | [ResultPanel (right)]

Wired to the engine via direction/mode callbacks.
"""

from __future__ import annotations

import datetime
import wx

from core.engine import InstructionEngine
from gui.theme import THEME, get_font
from gui.widgets.searchable_list import SearchableList, EVT_INSTR_SELECTED
from gui.result_panel import ResultPanel


class MainLookupPanel(wx.Panel):
    """Primary lookup view — splitter with list on left, result on right."""

    def __init__(self, parent: wx.Window,
                 direction: str = "ppc",
                 mode: str = "32") -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)

        self._engine = InstructionEngine()
        self._direction = direction
        self._mode = mode

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Top search bar (direct mnemonic entry)
        top_row = wx.BoxSizer(wx.HORIZONTAL)
        lbl = wx.StaticText(self, label="Mnemonic:")
        lbl.SetForegroundColour(THEME.FG_AMBER)
        lbl.SetFont(get_font(10, bold=True))
        top_row.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)

        self._mnem_entry = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._mnem_entry.SetBackgroundColour(THEME.BG_INPUT)
        self._mnem_entry.SetForegroundColour(THEME.FG_BRIGHT)
        self._mnem_entry.SetFont(get_font(12))
        self._mnem_entry.SetHint("Type mnemonic and press Enter…")
        top_row.Add(self._mnem_entry, 1, wx.EXPAND | wx.ALL, 6)

        btn_go = wx.Button(self, label="Look Up")
        btn_go.SetBackgroundColour(THEME.SEL_BG)
        btn_go.SetForegroundColour(THEME.FG_BRIGHT)
        btn_go.SetFont(get_font(10, bold=True))
        top_row.Add(btn_go, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        sizer.Add(top_row, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 4)

        # Splitter
        self._splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self._splitter.SetBackgroundColour(THEME.BG)
        self._splitter.SetSashGravity(0.28)
        self._splitter.SetMinimumPaneSize(180)

        # Left pane — searchable list
        self._instr_list = SearchableList(self._splitter)
        self._instr_list.SetBackgroundColour(THEME.BG_PANEL)

        # Right pane — result panel
        self._result_panel = ResultPanel(self._splitter)

        self._splitter.SplitVertically(
            self._instr_list, self._result_panel, sashPosition=260
        )
        sizer.Add(self._splitter, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self._populate_list()

        # Events
        self._instr_list.Bind(EVT_INSTR_SELECTED, self._on_instr_selected)
        self._mnem_entry.Bind(wx.EVT_TEXT_ENTER, self._on_entry_enter)
        btn_go.Bind(wx.EVT_BUTTON, self._on_entry_enter)

    # ------------------------------------------------------------------
    # Public — called by app.py on mode-bar changes
    # ------------------------------------------------------------------

    def set_direction(self, direction: str) -> None:
        self._direction = direction
        self._populate_list()

    def set_mode(self, mode: str) -> None:
        self._mode = mode

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _populate_list(self) -> None:
        """Fill the left list with all mnemonics for the current ISA."""
        if self._direction == "ppc":
            from data.ppc_instructions import PPC_INSTRUCTIONS
            items = [
                (m, r.get("category", ""))
                for m, r in sorted(PPC_INSTRUCTIONS.items())
            ]
        else:
            from data.x86_instructions import X86_INSTRUCTIONS
            items = [
                (m, r.get("category", ""))
                for m, r in sorted(X86_INSTRUCTIONS.items())
            ]
        self._instr_list.set_items(items)

    def _do_lookup(self, mnemonic: str) -> None:
        """Run a lookup and display the result."""
        result = self._engine.lookup(mnemonic, self._direction, self._mode)
        self._result_panel.show_result(result, self._direction)

        # Add to history
        frame = wx.GetTopLevelParent(self)
        if hasattr(frame, "add_history"):
            frame.add_history({
                "mnemonic":   mnemonic.upper(),
                "direction":  self._direction,
                "targets":    result.targets,
                "confidence": result.confidence,
                "time":       datetime.datetime.now().strftime("%H:%M:%S"),
            })
        if hasattr(frame, "set_status"):
            conf = result.confidence.upper()
            frame.set_status(
                f"Lookup: {mnemonic.upper()} [{conf}]  "
                f"→ {', '.join(result.targets) or '(no match)'}"
            )

    def _on_instr_selected(self, event) -> None:
        self._do_lookup(event.mnemonic)

    def _on_entry_enter(self, _event) -> None:
        mnem = self._mnem_entry.GetValue().strip()
        if mnem:
            self._do_lookup(mnem)

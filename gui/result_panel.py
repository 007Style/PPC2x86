"""
result_panel.py — Instruction detail and analogue display panel.

Shows the source instruction details and its x86/PPC analogues.
Uses wx.richtext.RichTextCtrl for coloured, formatted output.
Includes a "Copy to clipboard" button.
"""

from __future__ import annotations

import datetime
import wx
import wx.richtext

from gui.theme import THEME, get_font, confidence_colour
from core.engine import LookupResult


class ResultPanel(wx.Panel):
    """Right-pane instruction result display."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)

        self._current_result: LookupResult | None = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Suggestion warning banner (hidden by default) ---
        self._warn_panel = wx.Panel(self, style=wx.BORDER_NONE)
        self._warn_panel.SetBackgroundColour(THEME.WARN_BG)
        warn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._warn_label = wx.StaticText(
            self._warn_panel,
            label="⚠  This is a suggested analogue, not a guaranteed equivalent.",
        )
        self._warn_label.SetForegroundColour(THEME.WARN_FG)
        self._warn_label.SetFont(get_font(10, bold=True))
        warn_sizer.Add(self._warn_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        self._warn_panel.SetSizer(warn_sizer)
        self._warn_panel.Hide()
        sizer.Add(self._warn_panel, 0, wx.EXPAND)

        # --- Rich text result area ---
        self._rtc = wx.richtext.RichTextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE,
        )
        self._rtc.SetBackgroundColour(THEME.BG)
        self._rtc.SetForegroundColour(THEME.FG)
        self._rtc.SetFont(get_font(11))
        sizer.Add(self._rtc, 1, wx.EXPAND | wx.ALL, 4)

        # --- Copy button ---
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_copy = wx.Button(self, label="Copy to Clipboard")
        self._btn_copy.SetBackgroundColour(THEME.BG_SURFACE)
        self._btn_copy.SetForegroundColour(THEME.FG_DIM)
        self._btn_copy.SetFont(get_font(9))
        self._btn_copy.Bind(wx.EVT_BUTTON, self._on_copy)
        btn_row.AddStretchSpacer(1)
        btn_row.Add(self._btn_copy, 0, wx.ALL, 4)
        sizer.Add(btn_row, 0, wx.EXPAND)

        self.SetSizer(sizer)

        self._show_placeholder()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show_result(self, result: LookupResult, direction: str) -> None:
        """Render a LookupResult into the rich text control."""
        self._current_result = result
        rtc = self._rtc
        rtc.Clear()

        conf = result.confidence

        # Suggestion warning banner
        if conf == "suggestion":
            self._warn_panel.Show()
        else:
            self._warn_panel.Hide()
        self.Layout()

        # --- Source instruction header ---
        self._write_bold(f"{result.source_mnemonic.upper()}", size=14)
        self._write_color("  ", THEME.FG)  # spacer

        # Confidence badge
        badge_text = {
            "direct":     " [DIRECT] ",
            "close":      " [CLOSE] ",
            "suggestion": " [SUGGESTION] ",
            "none":       " [NO MATCH] ",
            "fuzzy":      " [FUZZY] ",
        }.get(conf, f" [{conf.upper()}] ")
        self._write_color(badge_text, confidence_colour(conf), bold=True)
        rtc.Newline()

        # Source instruction details
        si = result.source_instr
        if si:
            self._write_color(si.get("full_name", ""), THEME.FG_DIM)
            rtc.Newline()
            self._write_color("Syntax:  ", THEME.FG_AMBER, bold=True)
            self._write_color(si.get("syntax", "n/a"), THEME.FG)
            rtc.Newline()
            self._write_color("Category: ", THEME.FG_DIM)
            self._write_color(si.get("category", ""), THEME.FG)
            rtc.Newline()
            rtc.Newline()
            self._write_color(si.get("description", ""), THEME.FG)
            rtc.Newline()

        rtc.Newline()

        if conf == "fuzzy":
            self._write_color("No exact match found. Did you mean:\n\n", THEME.FG_AMBER)
            for mnem, score in result.alternatives:
                self._write_color(f"  {mnem}", THEME.FG_CYAN, bold=True)
                self._write_color(f"   (score: {score:.2f})\n", THEME.FG_DIM)
            return

        if conf == "none":
            self._write_color(result.notes, THEME.CONF_NONE)
            rtc.Newline()
            return

        # --- Analogues ---
        arrow = "→ x86 analogues:" if direction == "ppc" else "← PPC analogues:"
        self._write_bold(arrow, size=12)
        rtc.Newline()
        rtc.Newline()

        for i, tgt in enumerate(result.targets):
            ti = result.target_instrs[i] if i < len(result.target_instrs) else None
            self._write_color(f"  {tgt}", THEME.FG_BRIGHT, bold=True, size=12)
            if ti:
                fname = ti.get("full_name", "")
                syn   = ti.get("syntax", "")
                desc  = ti.get("description", "")
                self._write_color(f"  —  {fname}", THEME.FG_DIM)
                rtc.Newline()
                if syn:
                    self._write_color("    Syntax:  ", THEME.FG_AMBER)
                    self._write_color(syn, THEME.FG)
                    rtc.Newline()
                if desc:
                    self._write_color(f"    {desc}\n", THEME.FG_DIM)
            else:
                rtc.Newline()
            rtc.Newline()

        # Notes
        if result.notes:
            rtc.Newline()
            note_color = THEME.WARN_FG if conf == "suggestion" else THEME.FG_DIM
            prefix = "⚠  " if conf == "suggestion" else "ℹ  "
            self._write_color(prefix + result.notes, note_color)
            rtc.Newline()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _show_placeholder(self) -> None:
        self._rtc.Clear()
        self._write_color(
            "\n\n  Select an instruction from the list\n"
            "  or type a mnemonic in the search box.\n",
            THEME.FG_DIM,
        )

    def _write_color(self, text: str, colour: wx.Colour,
                     bold: bool = False, size: int = 11) -> None:
        attr = wx.richtext.RichTextAttr()
        attr.SetTextColour(colour)
        attr.SetBackgroundColour(THEME.BG)
        attr.SetFontSize(size)
        if bold:
            attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
        else:
            attr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        attr.SetFontFaceName("Menlo" if wx.Platform == "__WXMAC__" else "Consolas")
        self._rtc.SetDefaultStyle(attr)
        self._rtc.WriteText(text)

    def _write_bold(self, text: str, size: int = 11) -> None:
        self._write_color(text, THEME.FG_BRIGHT, bold=True, size=size)

    def _on_copy(self, _event) -> None:
        if not self._current_result:
            return
        r = self._current_result
        text_lines = [
            f"Source: {r.source_mnemonic.upper()} [{r.confidence.upper()}]",
            f"Targets: {', '.join(r.targets)}",
            f"Notes: {r.notes}",
        ]
        text = "\n".join(text_lines)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

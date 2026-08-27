"""
easter_eggs.py — EasterEggManager: attaches hidden interactions to the main frame.

Features
--------
- Konami code (↑↑↓↓←→←→BA) → full-screen ASCII splash
- Title label 7-click → ISA Graveyard dialog
- Status bar right-click → random compiler quote (wired in app.py)
- "Compiler Quotes" secret menu item revealed after Konami code
"""

from __future__ import annotations

import wx

from gui.theme import THEME, get_font
from data.isa_trivia import KONAMI_UNLOCK_TEXT, HIDDEN_MESSAGES, COMPILER_QUOTES


# Konami sequence as wx key codes
_KONAMI = [
    wx.WXK_UP, wx.WXK_UP,
    wx.WXK_DOWN, wx.WXK_DOWN,
    wx.WXK_LEFT, wx.WXK_RIGHT,
    wx.WXK_LEFT, wx.WXK_RIGHT,
    ord('B'), ord('A'),
]


class EasterEggManager:
    """
    Attach to a MainFrame on construction.
    Holds all Easter egg state — no module-level globals.
    """

    def __init__(self, frame: wx.Frame) -> None:
        self._frame = frame
        self._konami_idx = 0
        self._title_clicks = 0
        self._konami_unlocked = False
        self._quotes_menu_item: wx.MenuItem | None = None

        # Attach key listener globally on the frame
        frame.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

        # Attach title-click Easter egg to the frame title area by watching
        # left-clicks anywhere on the top bar (mode_bar acts as the clickable zone)
        if hasattr(frame, "_mode_bar"):
            frame._mode_bar.Bind(wx.EVT_LEFT_DOWN, self._on_title_click)

    # ------------------------------------------------------------------
    # Konami code
    # ------------------------------------------------------------------

    def _on_key_down(self, event: wx.KeyEvent) -> None:
        code = event.GetKeyCode()
        expected = _KONAMI[self._konami_idx]
        if code == expected:
            self._konami_idx += 1
            if self._konami_idx == len(_KONAMI):
                self._konami_idx = 0
                self._trigger_konami()
        else:
            self._konami_idx = 0
        event.Skip()

    def _trigger_konami(self) -> None:
        dlg = _KonamiSplash(self._frame)
        dlg.ShowModal()
        dlg.Destroy()

        if not self._konami_unlocked:
            self._konami_unlocked = True
            self._inject_quotes_menu()

    # ------------------------------------------------------------------
    # Secret compiler quotes menu item
    # ------------------------------------------------------------------

    def _inject_quotes_menu(self) -> None:
        """Add 'Show Compiler Quotes' to the Help menu after Konami."""
        help_menu = self._frame.get_help_menu()
        help_menu.AppendSeparator()
        self._quotes_menu_item = help_menu.Append(
            wx.ID_ANY, "Show Compiler Quotes",
            "Wisdom from ISA and compiler luminaries"
        )
        self._frame.Bind(
            wx.EVT_MENU, self._on_show_quotes, self._quotes_menu_item
        )

    def _on_show_quotes(self, _event) -> None:
        dlg = _CompilerQuotesDialog(self._frame)
        dlg.ShowModal()
        dlg.Destroy()

    # ------------------------------------------------------------------
    # Title 7-click
    # ------------------------------------------------------------------

    def _on_title_click(self, event: wx.MouseEvent) -> None:
        self._title_clicks += 1
        if self._title_clicks == 7:
            self._title_clicks = 0
            dlg = _ISAGraveyardDialog(self._frame)
            dlg.ShowModal()
            dlg.Destroy()
        event.Skip()


# ---------------------------------------------------------------------------
# Konami splash dialog
# ---------------------------------------------------------------------------

class _KonamiSplash(wx.Dialog):
    def __init__(self, parent: wx.Frame) -> None:
        super().__init__(
            parent, title="★ KONAMI CODE ACCEPTED ★",
            size=(660, 480),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetBackgroundColour(THEME.BG)
        sizer = wx.BoxSizer(wx.VERTICAL)

        txt = wx.TextCtrl(
            self,
            value=KONAMI_UNLOCK_TEXT,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE,
        )
        txt.SetBackgroundColour(THEME.BG)
        txt.SetForegroundColour(THEME.FG_AMBER)
        txt.SetFont(get_font(10))
        sizer.Add(txt, 1, wx.EXPAND | wx.ALL, 10)

        btn = wx.Button(self, wx.ID_OK, label="ACCEPT")
        btn.SetBackgroundColour(THEME.SEL_BG)
        btn.SetForegroundColour(THEME.FG_BRIGHT)
        btn.SetFont(get_font(11, bold=True))
        btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_OK))
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(sizer)


# ---------------------------------------------------------------------------
# Compiler quotes dialog (revealed by Konami)
# ---------------------------------------------------------------------------

class _CompilerQuotesDialog(wx.Dialog):
    def __init__(self, parent: wx.Frame) -> None:
        super().__init__(
            parent, title="Compiler & ISA Luminaries — Quotes",
            size=(680, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetBackgroundColour(THEME.BG)
        sizer = wx.BoxSizer(wx.VERTICAL)

        scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        scroll.SetBackgroundColour(THEME.BG)
        scroll.SetScrollRate(0, 20)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        for i, quote in enumerate(COMPILER_QUOTES):
            lbl = wx.StaticText(scroll, label=f'"{quote}"' if not quote.startswith('"') else quote)
            lbl.SetForegroundColour(THEME.FG_CYAN if i % 2 == 0 else THEME.FG_AMBER)
            lbl.SetFont(get_font(10, italic=True))
            lbl.Wrap(600)
            scroll_sizer.Add(lbl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 14)
            sep = wx.StaticLine(scroll)
            sep.SetBackgroundColour(THEME.BORDER)
            scroll_sizer.Add(sep, 0, wx.EXPAND | wx.TOP, 10)

        scroll.SetSizer(scroll_sizer)
        sizer.Add(scroll, 1, wx.EXPAND | wx.ALL, 6)

        btn = wx.Button(self, wx.ID_CLOSE, label="Close")
        btn.SetBackgroundColour(THEME.BG_SURFACE)
        btn.SetForegroundColour(THEME.FG_DIM)
        btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))
        sizer.Add(btn, 0, wx.ALIGN_RIGHT | wx.ALL, 6)
        self.SetSizer(sizer)


# ---------------------------------------------------------------------------
# ISA Graveyard dialog (7-click easter egg)
# ---------------------------------------------------------------------------

class _ISAGraveyardDialog(wx.Dialog):
    """Tombstone memorials for dead ISAs."""

    _EPITAPHS = [
        ("ALPHA AXP", "1992–2004",
         "\"I computed π to 50 decimal places\nbefore your JVM loaded.\""),
        ("ITANIUM", "2001–2021",
         "\"The compiler was supposed\nto do this part.\""),
        ("PA-RISC", "1986–2008",
         "\"HP promised Itanium would be better.\nHP was wrong.\""),
        ("VAX", "1977–2000",
         "\"MATCHC, LOCC, MOVC5 —\nfeatures x86 still doesn't have.\""),
        ("MIPS (desktop)", "1985–2002",
         "\"I taught a generation of CS students.\nThen they all bought Intel.\""),
    ]

    def __init__(self, parent: wx.Frame) -> None:
        super().__init__(
            parent, title="☩  The ISA Graveyard  ☩",
            size=(720, 460),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetBackgroundColour(THEME.BG)
        sizer = wx.BoxSizer(wx.VERTICAL)

        hdr = wx.StaticText(
            self,
            label="  Here lie the architectures that dared to challenge x86.",
        )
        hdr.SetForegroundColour(THEME.FG_DIM)
        hdr.SetFont(get_font(10, italic=True))
        sizer.Add(hdr, 0, wx.ALL, 10)

        stone_row = wx.BoxSizer(wx.HORIZONTAL)
        for name, years, epitaph in self._EPITAPHS:
            stone = _TombstonePanel(self, name, years, epitaph)
            stone_row.Add(stone, 1, wx.EXPAND | wx.ALL, 6)
        sizer.Add(stone_row, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        footer = wx.StaticText(
            self,
            label="  \"Any sufficiently successful ISA is indistinguishable from a mistake that won.\"\n"
                  "  Still alive: PowerPC / POWER  •  ARM  •  RISC-V  •  x86-64",
        )
        footer.SetForegroundColour(THEME.FG_CYAN)
        footer.SetFont(get_font(9, italic=True))
        sizer.Add(footer, 0, wx.ALL, 10)

        btn = wx.Button(self, wx.ID_CLOSE, label="Rest in Silicon Peace")
        btn.SetBackgroundColour(THEME.BG_SURFACE)
        btn.SetForegroundColour(THEME.FG_DIM)
        btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.SetSizer(sizer)


class _TombstonePanel(wx.Panel):
    """Single tombstone drawn with wx.DC."""

    def __init__(self, parent: wx.Window, name: str, years: str, epitaph: str) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)
        self._name = name
        self._years = years
        self._epitaph = epitaph
        self.SetMinSize((110, 160))
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _on_paint(self, _event: wx.PaintEvent) -> None:
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(THEME.BG))
        dc.Clear()
        w, h = self.GetSize()

        # Tombstone shape
        dc.SetBrush(wx.Brush(wx.Colour(40, 45, 40)))
        dc.SetPen(wx.Pen(THEME.BORDER, 1))
        radius = min(w // 2 - 4, 30)
        # Rectangle body
        dc.DrawRectangle(6, radius + 10, w - 12, h - radius - 20)
        # Rounded top
        dc.DrawCircle(w // 2, radius + 10, radius)

        # Cross
        cx, cy = w // 2, radius - 2
        dc.SetPen(wx.Pen(THEME.FG_DIM, 2))
        dc.DrawLine(cx, cy - 12, cx, cy + 12)
        dc.DrawLine(cx - 8, cy - 4, cx + 8, cy - 4)

        # Text
        dc.SetFont(get_font(8, bold=True))
        dc.SetTextForeground(THEME.FG_BRIGHT)
        # Name (may need wrapping)
        for i, part in enumerate(self._name.split()):
            tw, _ = dc.GetTextExtent(part)
            dc.DrawText(part, (w - tw) // 2, radius + 18 + i * 14)
        offset = radius + 18 + len(self._name.split()) * 14 + 4

        dc.SetFont(get_font(7))
        dc.SetTextForeground(THEME.FG_AMBER)
        tw, _ = dc.GetTextExtent(self._years)
        dc.DrawText(self._years, (w - tw) // 2, offset)
        offset += 14

        dc.SetFont(get_font(7, italic=True))
        dc.SetTextForeground(THEME.FG_DIM)
        for line in self._epitaph.split("\n"):
            tw, _ = dc.GetTextExtent(line)
            if tw > w - 8:
                line = line[:max(len(line) * (w - 12) // tw, 1)]
            dc.DrawText(line, max((w - tw) // 2, 4), offset)
            offset += 13

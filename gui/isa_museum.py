"""
isa_museum.py — ISA Museum tab and timeline dialog.

Panels
------
ISAMuseumPanel     — the full museum tab with sidebar + placard + random fact
ISATimelineDialog  — modal dialog showing a custom-drawn ISA timeline bar
"""

from __future__ import annotations

import wx
import wx.lib.scrolledpanel as scrolled

from gui.theme import THEME, get_font, confidence_colour
from data.isa_trivia import ISA_PROFILES, ISA_FACTS


class ISAMuseumPanel(wx.Panel):
    """Full ISA Museum tab panel."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)

        self._selected_isa: str | None = None

        outer = wx.BoxSizer(wx.HORIZONTAL)

        # --- Left sidebar: ISA list ---
        # Create the container panel FIRST, then parent all children to it.
        left_panel = wx.Panel(self, style=wx.BORDER_NONE)
        left_panel.SetBackgroundColour(THEME.BG_PANEL)
        left_panel.SetMinSize((170, -1))
        left = wx.BoxSizer(wx.VERTICAL)

        hdr = wx.StaticText(left_panel, label="  Architectures")
        hdr.SetForegroundColour(THEME.FG_AMBER)
        hdr.SetFont(get_font(11, bold=True))
        left.Add(hdr, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 6)

        self._isa_list = wx.ListBox(
            left_panel,
            choices=[k.upper() for k in ISA_PROFILES.keys()],
            style=wx.LB_SINGLE | wx.BORDER_NONE,
        )
        self._isa_list.SetBackgroundColour(THEME.BG_INPUT)
        self._isa_list.SetForegroundColour(THEME.FG)
        self._isa_list.SetFont(get_font(11))
        left.Add(self._isa_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        footer = wx.StaticText(
            left_panel,
            label=f"  {len(ISA_PROFILES)} ISAs  •  {len(ISA_FACTS)} facts",
        )
        footer.SetForegroundColour(THEME.FG_DIM)
        footer.SetFont(get_font(8))
        left.Add(footer, 0, wx.BOTTOM | wx.LEFT, 6)

        left_panel.SetSizer(left)
        outer.Add(left_panel, 0, wx.EXPAND)

        # Separator
        sep = wx.StaticLine(self, style=wx.LI_VERTICAL)
        sep.SetBackgroundColour(THEME.BORDER)
        outer.Add(sep, 0, wx.EXPAND)

        # --- Right: museum placard + buttons ---
        right = wx.BoxSizer(wx.VERTICAL)

        # Placard scroll area
        self._scroll = scrolled.ScrolledPanel(self, style=wx.BORDER_NONE)
        self._scroll.SetBackgroundColour(THEME.BG)
        self._scroll.SetupScrolling()
        self._placard_sizer = wx.BoxSizer(wx.VERTICAL)
        self._scroll.SetSizer(self._placard_sizer)
        right.Add(self._scroll, 1, wx.EXPAND | wx.ALL, 8)

        # Buttons row
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_fact = wx.Button(self, label="Random Fact")
        self._btn_compare = wx.Button(self, label="Compare…")
        self._btn_timeline = wx.Button(self, label="Timeline…")
        for btn in (self._btn_fact, self._btn_compare, self._btn_timeline):
            btn.SetBackgroundColour(THEME.BG_SURFACE)
            btn.SetForegroundColour(THEME.FG)
            btn.SetFont(get_font(10))
        btn_row.Add(self._btn_fact, 0, wx.RIGHT, 8)
        btn_row.Add(self._btn_compare, 0, wx.RIGHT, 8)
        btn_row.Add(self._btn_timeline, 0)
        right.Add(btn_row, 0, wx.LEFT | wx.BOTTOM, 10)

        outer.Add(right, 1, wx.EXPAND)
        self.SetSizer(outer)

        self._show_welcome()

        self._isa_list.Bind(wx.EVT_LISTBOX, self._on_isa_selected)
        self._btn_fact.Bind(wx.EVT_BUTTON, self._on_random_fact)
        self._btn_compare.Bind(wx.EVT_BUTTON, self._on_compare)
        self._btn_timeline.Bind(wx.EVT_BUTTON, self._on_timeline)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _show_welcome(self) -> None:
        self._clear_placard()
        lbl = wx.StaticText(
            self._scroll,
            label=(
                "\n\n  Welcome to the ISA Museum.\n\n"
                "  Select an architecture from the list\n"
                "  to view its museum placard.\n\n"
                "  Nine architectures are on display,\n"
                "  from the VAX (1977) to x86-64 (2003)."
            ),
        )
        lbl.SetForegroundColour(THEME.FG_DIM)
        lbl.SetFont(get_font(11))
        self._placard_sizer.Add(lbl, 0, wx.ALL, 16)
        self._scroll.Layout()
        self._scroll.SetupScrolling()

    def _clear_placard(self) -> None:
        for child in self._scroll.GetChildren():
            child.Destroy()
        self._placard_sizer.Clear()

    def _on_isa_selected(self, event: wx.CommandEvent) -> None:
        key = list(ISA_PROFILES.keys())[event.GetSelection()]
        self._selected_isa = key
        profile = ISA_PROFILES[key]
        self._render_placard(profile)

    def _render_placard(self, profile: dict) -> None:
        self._clear_placard()
        s = self._placard_sizer
        scroll = self._scroll

        def add_label(text: str, colour=None, bold=False, size=11):
            lbl = wx.StaticText(scroll, label=text)
            lbl.SetForegroundColour(colour or THEME.FG)
            lbl.SetFont(get_font(size, bold=bold))
            s.Add(lbl, 0, wx.LEFT | wx.TOP, 12)

        def add_sep():
            line = wx.StaticLine(scroll)
            line.SetBackgroundColour(THEME.BORDER)
            s.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        add_label(profile["name"], THEME.FG_BRIGHT, bold=True, size=18)
        add_sep()
        add_label(f"Vendor:   {profile['vendor']}", THEME.FG_DIM)
        born = profile["year"]
        died = profile.get("died")
        lifespan = f"{born} – {died}" if died else f"{born} – present"
        add_label(f"Lifespan: {lifespan}", THEME.FG_DIM)
        add_label(f"Bits:     {profile['bits']}-bit", THEME.FG_DIM)
        add_label(f"Endian:   {profile['endian']}", THEME.FG_DIM)
        add_label(f"Registers:{profile['registers']} integer registers", THEME.FG_DIM)
        add_sep()

        # Description — word-wrapped via wx.StaticText with wrap
        desc_lbl = wx.StaticText(scroll, label=profile.get("description", ""))
        desc_lbl.SetForegroundColour(THEME.FG)
        desc_lbl.SetFont(get_font(10))
        desc_lbl.Wrap(500)
        s.Add(desc_lbl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 14)

        add_sep()
        add_label("Famous for:", THEME.FG_AMBER, bold=True)
        fame_lbl = wx.StaticText(scroll, label=profile.get("famous_for", ""))
        fame_lbl.SetForegroundColour(THEME.FG_CYAN)
        fame_lbl.SetFont(get_font(10, italic=True))
        fame_lbl.Wrap(500)
        s.Add(fame_lbl, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT, 14)

        # Timeline bar
        timeline = _TimelineBar(scroll, profile)
        s.Add(timeline, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)

        scroll.Layout()
        scroll.SetupScrolling()

    def _on_random_fact(self, _event) -> None:
        import random
        pool = ISA_FACTS
        if self._selected_isa:
            pool = [f for f in ISA_FACTS if f.get("isa") == self._selected_isa]
            if not pool:
                pool = ISA_FACTS
        fact = random.choice(pool)
        isa  = fact.get("isa", "?").upper()
        cat  = fact.get("category", "")
        wx.MessageBox(
            f"[{isa}  —  {cat.upper()}]\n\n{fact['text']}",
            "ISA Fact",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _on_compare(self, _event) -> None:
        dlg = _ISACompareDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_timeline(self, _event) -> None:
        dlg = ISATimelineDialog(self)
        dlg.ShowModal()
        dlg.Destroy()


# ---------------------------------------------------------------------------
# Timeline bar (painted in placard)
# ---------------------------------------------------------------------------

class _TimelineBar(wx.Panel):
    """Horizontal bar showing ISA birth/death on a 1975–2025 scale."""

    _YEAR_START = 1975
    _YEAR_END   = 2025
    _HEIGHT     = 30

    def __init__(self, parent: wx.Window, profile: dict) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)
        self.SetMinSize((-1, self._HEIGHT))
        self._profile = profile
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _on_paint(self, _event: wx.PaintEvent) -> None:
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(THEME.BG))
        dc.Clear()

        w, h = self.GetSize()
        span = self._YEAR_END - self._YEAR_START

        def year_to_x(y: int) -> int:
            return int((y - self._YEAR_START) / span * (w - 20)) + 10

        # Draw axis
        dc.SetPen(wx.Pen(THEME.BORDER, 1))
        mid_y = h // 2
        dc.DrawLine(10, mid_y, w - 10, mid_y)

        # Decade ticks
        dc.SetFont(get_font(7))
        dc.SetTextForeground(THEME.FG_DIM)
        for decade in range(1980, 2025, 10):
            x = year_to_x(decade)
            dc.DrawLine(x, mid_y - 4, x, mid_y + 4)
            dc.DrawText(str(decade), x - 14, mid_y + 6)

        # ISA bar
        born = self._profile.get("year", 1990)
        died = self._profile.get("died") or 2025
        x1 = year_to_x(born)
        x2 = year_to_x(min(died, self._YEAR_END))
        bar_colour = THEME.FG_CYAN if not self._profile.get("died") else THEME.FG_DIM
        dc.SetBrush(wx.Brush(bar_colour))
        dc.SetPen(wx.Pen(THEME.BORDER_ACTIVE, 1))
        dc.DrawRectangle(x1, mid_y - 7, max(x2 - x1, 4), 14)

        # Label
        dc.SetTextForeground(THEME.FG_BRIGHT)
        dc.SetFont(get_font(7, bold=True))
        dc.DrawText(self._profile["name"], x1 + 2, 2)


# ---------------------------------------------------------------------------
# ISA Compare dialog
# ---------------------------------------------------------------------------

class _ISACompareDialog(wx.Dialog):
    """Side-by-side ISA comparison."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, title="Compare ISAs",
                         size=(800, 500),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetBackgroundColour(THEME.BG)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Selectors
        sel_row = wx.BoxSizer(wx.HORIZONTAL)
        isa_names = list(ISA_PROFILES.keys())
        choices = [k.upper() for k in isa_names]
        self._sel_a = wx.Choice(self, choices=choices)
        self._sel_b = wx.Choice(self, choices=choices)
        for sel in (self._sel_a, self._sel_b):
            sel.SetBackgroundColour(THEME.BG_INPUT)
            sel.SetForegroundColour(THEME.FG)
            sel.SetFont(get_font(10))
        self._sel_a.SetSelection(0)
        self._sel_b.SetSelection(1)
        sel_row.Add(wx.StaticText(self, label="ISA A:"), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        sel_row.Add(self._sel_a, 1, wx.EXPAND | wx.ALL, 4)
        sel_row.Add(wx.StaticText(self, label="ISA B:"), 0,
                    wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        sel_row.Add(self._sel_b, 1, wx.EXPAND | wx.ALL, 4)
        btn_go = wx.Button(self, label="Compare")
        btn_go.SetBackgroundColour(THEME.SEL_BG)
        btn_go.SetForegroundColour(THEME.FG_BRIGHT)
        btn_go.SetFont(get_font(10))
        sel_row.Add(btn_go, 0, wx.ALL, 4)
        sizer.Add(sel_row, 0, wx.EXPAND | wx.TOP, 8)

        # Content area
        self._content = wx.BoxSizer(wx.HORIZONTAL)
        self._panel_a = _PlacardMiniPanel(self)
        self._panel_b = _PlacardMiniPanel(self)
        self._content.Add(self._panel_a, 1, wx.EXPAND | wx.ALL, 8)
        self._content.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        self._content.Add(self._panel_b, 1, wx.EXPAND | wx.ALL, 8)
        sizer.Add(self._content, 1, wx.EXPAND)

        btn_close = wx.Button(self, wx.ID_CLOSE, label="Close")
        btn_close.SetBackgroundColour(THEME.BG_SURFACE)
        btn_close.SetForegroundColour(THEME.FG_DIM)
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.ALL, 8)

        self.SetSizer(sizer)

        btn_go.Bind(wx.EVT_BUTTON, self._on_compare)
        btn_close.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))

        self._on_compare(None)

    def _on_compare(self, _event) -> None:
        keys = list(ISA_PROFILES.keys())
        key_a = keys[self._sel_a.GetSelection()]
        key_b = keys[self._sel_b.GetSelection()]
        self._panel_a.show(ISA_PROFILES[key_a])
        self._panel_b.show(ISA_PROFILES[key_b])
        self.Layout()


class _PlacardMiniPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

    def show(self, profile: dict) -> None:
        for child in self.GetChildren():
            child.Destroy()
        self._sizer.Clear()

        def add(text, colour=None, bold=False, size=10):
            lbl = wx.StaticText(self, label=text)
            lbl.SetForegroundColour(colour or THEME.FG)
            lbl.SetFont(get_font(size, bold=bold))
            lbl.Wrap(320)
            self._sizer.Add(lbl, 0, wx.LEFT | wx.TOP, 6)

        add(profile["name"], THEME.FG_BRIGHT, bold=True, size=14)
        add(f"Vendor: {profile['vendor']}", THEME.FG_DIM)
        born = profile["year"]
        died = profile.get("died")
        add(f"Lifespan: {born} – {died or 'present'}", THEME.FG_DIM)
        add(f"Bits: {profile['bits']}-bit  |  Endian: {profile['endian']}", THEME.FG_DIM)
        add(f"Registers: {profile['registers']}", THEME.FG_DIM)
        desc_lbl = wx.StaticText(self, label=profile.get("description", ""))
        desc_lbl.SetForegroundColour(THEME.FG)
        desc_lbl.SetFont(get_font(9))
        desc_lbl.Wrap(320)
        self._sizer.Add(desc_lbl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 8)

        self.Layout()


# ---------------------------------------------------------------------------
# ISA Timeline Dialog
# ---------------------------------------------------------------------------

class ISATimelineDialog(wx.Dialog):
    """Full ISA timeline as a modal dialog with a custom-drawn chart."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, title="ISA Timeline (1975 – 2025)",
                         size=(760, 400),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetBackgroundColour(THEME.BG)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._canvas = _TimelineCanvas(self)
        sizer.Add(self._canvas, 1, wx.EXPAND | wx.ALL, 8)

        btn = wx.Button(self, wx.ID_CLOSE, label="Close")
        btn.SetBackgroundColour(THEME.BG_SURFACE)
        btn.SetForegroundColour(THEME.FG_DIM)
        btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CLOSE))
        sizer.Add(btn, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 8)
        self.SetSizer(sizer)


class _TimelineCanvas(wx.Panel):
    """Draws all ISAs as horizontal bars on a 1975–2025 timeline."""

    _YEAR_START = 1975
    _YEAR_END   = 2025
    _ROW_H      = 28
    _PAD_LEFT   = 100
    _PAD_RIGHT  = 20
    _PAD_TOP    = 30

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG)
        total_h = self._PAD_TOP + len(ISA_PROFILES) * self._ROW_H + 30
        self.SetMinSize((-1, total_h))
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _on_paint(self, _event: wx.PaintEvent) -> None:
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(THEME.BG))
        dc.Clear()
        w, h = self.GetSize()
        span = self._YEAR_END - self._YEAR_START
        avail_w = w - self._PAD_LEFT - self._PAD_RIGHT

        def year_to_x(y: int) -> int:
            return self._PAD_LEFT + int((y - self._YEAR_START) / span * avail_w)

        # Decade grid lines and labels
        dc.SetFont(get_font(8))
        dc.SetTextForeground(THEME.FG_DIM)
        dc.SetPen(wx.Pen(THEME.BORDER, 1, wx.PENSTYLE_DOT))
        for decade in range(1975, 2026, 5):
            x = year_to_x(decade)
            dc.DrawLine(x, self._PAD_TOP - 20, x,
                        self._PAD_TOP + len(ISA_PROFILES) * self._ROW_H)
            dc.DrawText(str(decade), x - 16, 4)

        # ISA bars
        colours = [
            THEME.FG_CYAN, THEME.FG_AMBER, THEME.CONF_CLOSE,
            THEME.CONF_DIRECT, THEME.CONF_SUGGESTION, THEME.FG,
            THEME.FG_DIM, THEME.FG_BRIGHT, THEME.CONF_NONE,
        ]
        dc.SetFont(get_font(9))
        for i, (key, profile) in enumerate(ISA_PROFILES.items()):
            y = self._PAD_TOP + i * self._ROW_H
            born = profile.get("year", 1980)
            died = profile.get("died") or 2025
            x1 = year_to_x(born)
            x2 = year_to_x(min(died, self._YEAR_END))
            col = colours[i % len(colours)]

            # Bar
            dc.SetBrush(wx.Brush(col))
            dc.SetPen(wx.Pen(THEME.BG, 1))
            bar_h = self._ROW_H - 6
            dc.DrawRoundedRectangle(x1, y + 3, max(x2 - x1, 6), bar_h, 3)

            # Label (left)
            dc.SetTextForeground(THEME.FG)
            dc.DrawText(profile["name"], 4, y + 7)

            # Year annotations
            dc.SetTextForeground(THEME.FG_DIM)
            dc.SetFont(get_font(7))
            dc.DrawText(str(born), x1 + 2, y + 3)
            if profile.get("died"):
                dc.DrawText(str(died), x2 - 28, y + 3)
            dc.SetFont(get_font(9))

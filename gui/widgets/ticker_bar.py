"""
ticker_bar.py — Scrolling ISA trivia ticker at the bottom of the window.

A wx.Panel that scrolls text from right to left using a wx.Timer.
Content is drawn with wx.PaintDC.

Usage
-----
    from gui.widgets.ticker_bar import TickerBar
    ticker = TickerBar(parent)
    ticker.start()
"""

from __future__ import annotations

import random
import wx

from gui.theme import THEME, get_font
from data.isa_trivia import ISA_FACTS


class TickerBar(wx.Panel):
    """Horizontally scrolling ISA trivia ticker."""

    _HEIGHT = 22
    _SPEED  = 2    # pixels per timer tick
    _FPS    = 40   # timer ticks per second → ~80 px/sec

    def __init__(self, parent: wx.Window, filter_isa: str | None = None) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.TICKER_BG)
        self.SetMinSize((-1, self._HEIGHT))

        self._filter_isa = filter_isa
        self._items: list[str] = []
        self._full_text = ""
        self._x_offset = 0
        self._text_width = 0
        self._font = get_font(9)
        self._running = False
        self._timer = wx.Timer(self)

        self._rebuild_text()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self.Bind(wx.EVT_SIZE,  self._on_size)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._x_offset = self.GetSize().Width
            self._timer.Start(1000 // self._FPS)

    def stop(self) -> None:
        self._running = False
        self._timer.Stop()

    def set_filter(self, isa: str | None) -> None:
        """Restrict ticker to a specific ISA (or None for all)."""
        self._filter_isa = isa
        self._rebuild_text()
        self._x_offset = self.GetSize().Width

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild_text(self) -> None:
        pool = ISA_FACTS
        if self._filter_isa:
            pool = [f for f in ISA_FACTS if f.get("isa") == self._filter_isa]
        if not pool:
            pool = ISA_FACTS
        # Shuffle and join with separators
        shuffled = random.sample(pool, len(pool))
        parts = []
        for item in shuffled:
            isa = item.get("isa", "?").upper()
            text = item.get("text", "")
            parts.append(f"  ★ [{isa}]  {text}  ")
        self._full_text = "".join(parts)
        # Measure text width using a temporary DC
        dc = wx.MemoryDC()
        dc.SetFont(self._font)
        self._text_width, _ = dc.GetTextExtent(self._full_text)

    def _on_timer(self, _event: wx.TimerEvent) -> None:
        self._x_offset -= self._SPEED
        if self._x_offset < -self._text_width:
            # Loop: rebuild with fresh shuffle
            self._rebuild_text()
            self._x_offset = self.GetSize().Width
        self.Refresh(False)

    def _on_paint(self, _event: wx.PaintEvent) -> None:
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(THEME.TICKER_BG))
        dc.Clear()
        dc.SetFont(self._font)
        dc.SetTextForeground(THEME.TICKER_FG)
        h = self.GetSize().Height
        _, th = dc.GetTextExtent("X")
        y = (h - th) // 2
        dc.DrawText(self._full_text, self._x_offset, y)

    def _on_size(self, _event: wx.SizeEvent) -> None:
        if not self._running:
            self._x_offset = self.GetSize().Width
        _event.Skip()

    def _on_right_click(self, event: wx.MouseEvent) -> None:
        """Context menu to filter by ISA."""
        menu = wx.Menu()
        item_all = menu.Append(wx.ID_ANY, "All ISAs")
        self.Bind(wx.EVT_MENU, lambda _e: self.set_filter(None), item_all)
        menu.AppendSeparator()
        for isa in ["sparc", "alpha", "mips", "pa-risc",
                    "itanium", "68k", "vax", "ppc", "x86"]:
            item = menu.Append(wx.ID_ANY, isa.upper())
            self.Bind(wx.EVT_MENU,
                      lambda _e, i=isa: self.set_filter(i),
                      item)
        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

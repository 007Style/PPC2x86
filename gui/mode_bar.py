"""
mode_bar.py — Direction toggle (PPC→x86 / x86→PPC) and mode selector (32/64-bit).

Emits two custom wx events:
    EVT_DIRECTION_CHANGED   — payload: "ppc" | "x86"
    EVT_MODE_CHANGED        — payload: "32" | "64"
"""

from __future__ import annotations

import wx
import wx.lib.newevent

from gui.theme import THEME, get_font, style_button

# ---------------------------------------------------------------------------
# Custom events
# ---------------------------------------------------------------------------

DirectionChangedEvent, EVT_DIRECTION_CHANGED = wx.lib.newevent.NewCommandEvent()
ModeChangedEvent,      EVT_MODE_CHANGED      = wx.lib.newevent.NewCommandEvent()


class ModeBar(wx.Panel):
    """
    Compact toolbar-style panel with:
      [PPC→x86] [x86→PPC]       [32-bit] [64-bit]
    """

    def __init__(self, parent: wx.Window, initial_dir: str = "ppc",
                 initial_mode: str = "32") -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG_SURFACE)

        self._direction = initial_dir
        self._mode = initial_mode

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # --- direction buttons ---
        dir_label = wx.StaticText(self, label="Direction:")
        dir_label.SetForegroundColour(THEME.FG_DIM)
        dir_label.SetFont(get_font(9))
        sizer.Add(dir_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)

        self._btn_ppc = wx.ToggleButton(self, label="PPC → x86")
        self._btn_x86 = wx.ToggleButton(self, label="x86 → PPC")
        for btn in (self._btn_ppc, self._btn_x86):
            btn.SetFont(get_font(10, bold=True))
            btn.SetBackgroundColour(THEME.BG)
            btn.SetForegroundColour(THEME.FG)
        sizer.Add(self._btn_ppc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        sizer.Add(self._btn_x86, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)

        sizer.AddStretchSpacer(1)

        # --- mode buttons ---
        mode_label = wx.StaticText(self, label="Mode:")
        mode_label.SetForegroundColour(THEME.FG_DIM)
        mode_label.SetFont(get_font(9))
        sizer.Add(mode_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self._btn_32 = wx.ToggleButton(self, label="32-bit")
        self._btn_64 = wx.ToggleButton(self, label="64-bit")
        for btn in (self._btn_32, self._btn_64):
            btn.SetFont(get_font(10, bold=True))
            btn.SetBackgroundColour(THEME.BG)
            btn.SetForegroundColour(THEME.FG)
        sizer.Add(self._btn_32, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._btn_64, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 4)

        self.SetSizer(sizer)
        self.SetMinSize((-1, 36))

        self._update_dir_buttons()
        self._update_mode_buttons()

        self._btn_ppc.Bind(wx.EVT_TOGGLEBUTTON, self._on_dir_ppc)
        self._btn_x86.Bind(wx.EVT_TOGGLEBUTTON, self._on_dir_x86)
        self._btn_32.Bind(wx.EVT_TOGGLEBUTTON, self._on_mode_32)
        self._btn_64.Bind(wx.EVT_TOGGLEBUTTON, self._on_mode_64)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def direction(self) -> str:
        return self._direction

    @property
    def mode(self) -> str:
        return self._mode

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_dir_ppc(self, _event: wx.Event) -> None:
        self._set_direction("ppc")

    def _on_dir_x86(self, _event: wx.Event) -> None:
        self._set_direction("x86")

    def _on_mode_32(self, _event: wx.Event) -> None:
        self._set_mode("32")

    def _on_mode_64(self, _event: wx.Event) -> None:
        self._set_mode("64")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_direction(self, direction: str) -> None:
        if self._direction == direction:
            # Re-press the current button so it stays toggled
            self._update_dir_buttons()
            return
        self._direction = direction
        self._update_dir_buttons()
        evt = DirectionChangedEvent(self.GetId(), direction=direction)
        wx.PostEvent(self, evt)

    def _set_mode(self, mode: str) -> None:
        if self._mode == mode:
            self._update_mode_buttons()
            return
        self._mode = mode
        self._update_mode_buttons()
        evt = ModeChangedEvent(self.GetId(), mode=mode)
        wx.PostEvent(self, evt)

    def _update_dir_buttons(self) -> None:
        self._btn_ppc.SetValue(self._direction == "ppc")
        self._btn_x86.SetValue(self._direction == "x86")
        for btn, active in [(self._btn_ppc, self._direction == "ppc"),
                            (self._btn_x86, self._direction == "x86")]:
            btn.SetForegroundColour(THEME.FG_BRIGHT if active else THEME.FG_DIM)
            btn.SetBackgroundColour(THEME.SEL_BG if active else THEME.BG)

    def _update_mode_buttons(self) -> None:
        self._btn_32.SetValue(self._mode == "32")
        self._btn_64.SetValue(self._mode == "64")
        for btn, active in [(self._btn_32, self._mode == "32"),
                            (self._btn_64, self._mode == "64")]:
            btn.SetForegroundColour(THEME.FG_BRIGHT if active else THEME.FG_DIM)
            btn.SetBackgroundColour(THEME.SEL_BG if active else THEME.BG)

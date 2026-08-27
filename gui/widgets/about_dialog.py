"""
about_dialog.py — Credits dialog with a hidden clickable zone.

Clicking the "★" marker area 3 times reveals the Hall of Fame credits panel.
"""

from __future__ import annotations

import wx
import wx.richtext

from gui.theme import THEME, get_font
from data.isa_trivia import HIDDEN_MESSAGES


class AboutDialog(wx.Dialog):
    """About PPC2x86 — with a hidden Easter egg click zone."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(
            parent, title="About PPC2x86",
            size=(480, 400),
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self.SetBackgroundColour(THEME.BG)
        self._hidden_clicks = 0

        sizer = wx.BoxSizer(wx.VERTICAL)

        # ASCII logo
        logo = wx.StaticText(
            self,
            label=(
                "\n"
                "  ██████╗ ██████╗  ██████╗██████╗ ██╗  ██╗ █████╗  ██████╗\n"
                "  ██╔══██╗██╔══██╗██╔════╝╚════██╗╚██╗██╔╝██╔══██╗██╔════╝\n"
                "  ██████╔╝██████╔╝██║      █████╔╝ ╚███╔╝ ╚█████╔╝███████╗\n"
                "  ██╔═══╝ ██╔═══╝ ██║     ██╔═══╝  ██╔██╗ ██╔══██╗██╔══██║\n"
                "  ██║     ██║     ╚██████╗███████╗██╔╝ ██╗╚█████╔╝╚██████╔╝\n"
                "  ╚═╝     ╚═╝      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚════╝  ╚═════╝\n"
            ),
        )
        logo.SetForegroundColour(THEME.FG_CYAN)
        logo.SetFont(get_font(7))
        sizer.Add(logo, 0, wx.ALIGN_CENTER | wx.TOP, 6)

        desc = wx.StaticText(
            self,
            label=(
                "PowerPC ↔ x86/x64 ISA Translation Station\n"
                "Version 1.0.0  —  Retro ISA Museum Edition\n\n"
                "A lookup tool for PPC and x86 instruction analogues,\n"
                "with 423 PPC + 524 x86 mnemonics and 273 mappings.\n\n"
                "Data: IBM POWER ISA v3.1  •  Intel SDM  •  AMD64 APM\n"
            ),
        )
        desc.SetForegroundColour(THEME.FG)
        desc.SetFont(get_font(10))
        sizer.Add(desc, 0, wx.ALIGN_CENTER | wx.TOP, 4)

        tagline = wx.StaticText(
            self,
            label="From the minds of IBM Bob & Daneyand",
        )
        tagline.SetForegroundColour(THEME.FG_AMBER)
        tagline.SetFont(get_font(10, bold=True))
        sizer.Add(tagline, 0, wx.ALIGN_CENTER | wx.TOP, 2)

        # Hidden click zone — the ★ star label
        self._star = wx.StaticText(self, label="   ★   ")
        self._star.SetForegroundColour(THEME.FG_DIM)
        self._star.SetFont(get_font(9))
        self._star.SetToolTip("…")
        self._star.Bind(wx.EVT_LEFT_DOWN, self._on_star_click)
        sizer.Add(self._star, 0, wx.ALIGN_CENTER | wx.TOP, 2)

        btn = wx.Button(self, wx.ID_OK, label="Close")
        btn.SetBackgroundColour(THEME.BG_SURFACE)
        btn.SetForegroundColour(THEME.FG_DIM)
        btn.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_OK))
        sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(sizer)

    def _on_star_click(self, _event: wx.MouseEvent) -> None:
        self._hidden_clicks += 1
        if self._hidden_clicks >= 3:
            self._hidden_clicks = 0
            wx.MessageBox(
                HIDDEN_MESSAGES["about_hidden_zone"],
                "Hall of Fame",
                wx.OK | wx.ICON_INFORMATION,
                self,
            )
        else:
            self._star.SetForegroundColour(
                THEME.FG_AMBER if self._hidden_clicks == 1 else THEME.FG_BRIGHT
            )
            self._star.Refresh()

"""
app.py — wx.App subclass and MainFrame for PPC2x86.

Launching
---------
    from gui.app import PPC2x86App
    app = PPC2x86App(initial_mode="32")
    app.MainLoop()
"""

from __future__ import annotations

import sys
import os

import wx
import wx.aui

# Make sure project root is on sys.path when running gui directly
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gui.theme import THEME, apply_theme, get_font
from gui.mode_bar import (
    ModeBar,
    EVT_DIRECTION_CHANGED,
    EVT_MODE_CHANGED,
)
from gui.widgets.ticker_bar import TickerBar


# ---------------------------------------------------------------------------
# ASCII art icon (shown in About when no image asset is present)
# ---------------------------------------------------------------------------

_ASCII_LOGO = (
    "  ██████╗ ██████╗  ██████╗██████╗ ██╗  ██╗ █████╗  ██████╗ \n"
    "  ██╔══██╗██╔══██╗██╔════╝╚════██╗╚██╗██╔╝██╔══██╗██╔════╝ \n"
    "  ██████╔╝██████╔╝██║      █████╔╝ ╚███╔╝ ╚█████╔╝███████╗ \n"
    "  ██╔═══╝ ██╔═══╝ ██║     ██╔═══╝  ██╔██╗ ██╔══██╗██╔══██║ \n"
    "  ██║     ██║     ╚██████╗███████╗██╔╝ ██╗╚█████╔╝╚██████╔╝\n"
    "  ╚═╝     ╚═╝      ╚═════╝╚══════╝╚═╝  ╚═╝ ╚════╝  ╚═════╝ \n"
    "  PowerPC ↔ x86/x64 ISA Translation Station\n"
)


# ---------------------------------------------------------------------------
# History log (module-level so all panels can append to it)
# ---------------------------------------------------------------------------

_HISTORY: list[dict] = []


def history_append(entry: dict) -> None:
    _HISTORY.append(entry)


def history_get() -> list[dict]:
    return list(_HISTORY)


# ---------------------------------------------------------------------------
# Main Frame
# ---------------------------------------------------------------------------

class MainFrame(wx.Frame):
    """Top-level application window."""

    _TITLE   = "PPC2x86 — ISA Translation Station"
    _MIN_W   = 900
    _MIN_H   = 600

    def __init__(self, initial_mode: str = "32") -> None:
        super().__init__(
            None,
            title=self._TITLE,
            size=(1100, 720),
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self.SetMinSize((self._MIN_W, self._MIN_H))
        self.SetBackgroundColour(THEME.BG)

        # Track title click count for Easter egg
        self._title_clicks = 0

        self._initial_mode = initial_mode

        self._build_menu()
        self._build_status_bar()
        self._build_body(initial_mode)

        self.Centre()
        self.Show()

        # Start ticker after window is shown
        self._ticker.start()

        # Attach easter egg manager
        from gui.easter_eggs import EasterEggManager
        self._egg_manager = EasterEggManager(self)

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        menubar = wx.MenuBar()
        menubar.SetBackgroundColour(THEME.BG_SURFACE)

        # File
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "Quit\tCtrl+Q", "Exit PPC2x86")
        self.Bind(wx.EVT_MENU, lambda _e: self.Close(), id=wx.ID_EXIT)

        # View
        view_menu = wx.Menu()
        view_menu.Append(wx.ID_ANY, "Reset Layout", "Reset panel layout")

        # ISA Museum
        museum_menu = wx.Menu()
        self._mi_museum = museum_menu.Append(wx.ID_ANY, "Open ISA Museum Tab",
                                             "Switch to the ISA Museum tab")
        self.Bind(wx.EVT_MENU, self._on_open_museum, self._mi_museum)

        # Extras
        extras_menu = wx.Menu()
        self._mi_timeline   = extras_menu.Append(wx.ID_ANY, "ISA Timeline")
        self._mi_count      = extras_menu.Append(wx.ID_ANY, "Instruction Count Stats")
        self._mi_rand_fact  = extras_menu.Append(wx.ID_ANY, "Random ISA Fact\tCtrl+R")
        self._mi_bench      = extras_menu.Append(wx.ID_ANY, "Benchmark Trivia")
        self.Bind(wx.EVT_MENU, self._on_random_fact, self._mi_rand_fact)
        self.Bind(wx.EVT_MENU, self._on_instr_stats, self._mi_count)
        self.Bind(wx.EVT_MENU, self._on_isa_timeline, self._mi_timeline)
        self.Bind(wx.EVT_MENU, self._on_bench_trivia, self._mi_bench)

        # Help
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "About PPC2x86")
        help_menu.AppendSeparator()
        help_menu.Append(wx.ID_ANY, "Konami Code Hint",
                         "↑↑↓↓←→←→BA — try it!")
        self.Bind(wx.EVT_MENU, self._on_about, id=wx.ID_ABOUT)

        menubar.Append(file_menu,   "&File")
        menubar.Append(view_menu,   "&View")
        menubar.Append(museum_menu, "&ISA Museum")
        menubar.Append(extras_menu, "E&xtras")
        menubar.Append(help_menu,   "&Help")

        self.SetMenuBar(menubar)
        self._menubar = menubar
        self._help_menu = help_menu  # Easter egg will inject "Compiler Quotes" here

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _build_status_bar(self) -> None:
        sb = self.CreateStatusBar(2)
        sb.SetStatusWidths([-1, 200])
        sb.SetBackgroundColour(THEME.STATUS_BG)
        sb.SetForegroundColour(THEME.STATUS_FG)
        sb.SetStatusText("Ready", 0)
        sb.SetStatusText(
            f"PPC: {len(self._ppc_count())}  x86: {len(self._x86_count())}", 1
        )
        sb.Bind(wx.EVT_RIGHT_DOWN, self._on_statusbar_right_click)
        self._status_bar = sb

    # ------------------------------------------------------------------
    # Body panels
    # ------------------------------------------------------------------

    def _build_body(self, initial_mode: str) -> None:
        outer = wx.BoxSizer(wx.VERTICAL)

        # Mode bar
        self._mode_bar = ModeBar(self, initial_mode=initial_mode)
        outer.Add(self._mode_bar, 0, wx.EXPAND)

        # Separator
        line = wx.StaticLine(self)
        line.SetBackgroundColour(THEME.BORDER)
        outer.Add(line, 0, wx.EXPAND)

        # Notebook
        self._notebook = wx.aui.AuiNotebook(
            self,
            style=(wx.aui.AUI_NB_TOP |
                   wx.aui.AUI_NB_TAB_SPLIT |
                   wx.aui.AUI_NB_SCROLL_BUTTONS),
        )
        outer.Add(self._notebook, 1, wx.EXPAND)

        # Ticker bar
        self._ticker = TickerBar(self)
        outer.Add(self._ticker, 0, wx.EXPAND)

        self.SetSizer(outer)

        # --- Lookup tab ---
        from gui.main_panel import MainLookupPanel
        self._lookup_panel = MainLookupPanel(
            self._notebook,
            direction=self._mode_bar.direction,
            mode=initial_mode,
        )
        self._notebook.AddPage(self._lookup_panel, "Lookup", select=True)

        # --- ISA Museum tab ---
        from gui.isa_museum import ISAMuseumPanel
        self._museum_panel = ISAMuseumPanel(self._notebook)
        self._notebook.AddPage(self._museum_panel, "ISA Museum", select=False)

        # --- History Log tab ---
        self._history_panel = _HistoryPanel(self._notebook)
        self._notebook.AddPage(self._history_panel, "History Log", select=False)

        # Wire mode bar events
        self._mode_bar.Bind(EVT_DIRECTION_CHANGED, self._on_direction_changed)
        self._mode_bar.Bind(EVT_MODE_CHANGED,      self._on_mode_changed)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_direction_changed(self, event) -> None:
        self._lookup_panel.set_direction(event.direction)
        self._status_bar.SetStatusText(
            f"Direction: {event.direction.upper()} → "
            f"{'x86' if event.direction == 'ppc' else 'PPC'}", 0
        )

    def _on_mode_changed(self, event) -> None:
        self._lookup_panel.set_mode(event.mode)
        self._status_bar.SetStatusText(f"Mode: {event.mode}-bit", 0)

    def _on_open_museum(self, _event) -> None:
        for i in range(self._notebook.GetPageCount()):
            if self._notebook.GetPageText(i) == "ISA Museum":
                self._notebook.SetSelection(i)
                break

    def _on_about(self, _event) -> None:
        from gui.widgets.about_dialog import AboutDialog
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_random_fact(self, _event) -> None:
        from data.isa_trivia import ISA_FACTS
        import random
        fact = random.choice(ISA_FACTS)
        isa  = fact.get("isa", "?").upper()
        text = fact.get("text", "")
        wx.MessageBox(
            f"[{isa}]\n\n{text}",
            "Random ISA Fact",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _on_instr_stats(self, _event) -> None:
        from data.ppc_instructions import PPC_INSTRUCTIONS
        from data.x86_instructions import X86_INSTRUCTIONS
        from data.mappings import PPC_TO_X86
        msg = (
            f"Instruction counts\n"
            f"──────────────────\n"
            f"PPC mnemonics   : {len(PPC_INSTRUCTIONS)}\n"
            f"x86 mnemonics   : {len(X86_INSTRUCTIONS)}\n"
            f"Mapping entries : {len(PPC_TO_X86)}\n"
        )
        wx.MessageBox(msg, "Instruction Count Stats", wx.OK | wx.ICON_INFORMATION, self)

    def _on_isa_timeline(self, _event) -> None:
        from gui.isa_museum import ISATimelineDialog
        dlg = ISATimelineDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_bench_trivia(self, _event) -> None:
        from data.isa_trivia import ISA_FACTS
        import random
        pool = [f for f in ISA_FACTS if f.get("category") == "benchmark"]
        if not pool:
            pool = ISA_FACTS
        fact = random.choice(pool)
        isa  = fact.get("isa", "?").upper()
        wx.MessageBox(
            f"[{isa}  BENCHMARK TRIVIA]\n\n{fact['text']}",
            "Benchmark Trivia",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _on_statusbar_right_click(self, _event) -> None:
        from data.isa_trivia import COMPILER_QUOTES
        import random
        quote = random.choice(COMPILER_QUOTES)
        wx.MessageBox(quote, "Compiler Quote", wx.OK | wx.ICON_INFORMATION, self)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def set_status(self, text: str) -> None:
        self._status_bar.SetStatusText(text, 0)

    def add_history(self, entry: dict) -> None:
        history_append(entry)
        self._history_panel.refresh()

    def get_help_menu(self) -> wx.Menu:
        return self._help_menu

    @staticmethod
    def _ppc_count():
        from data.ppc_instructions import PPC_INSTRUCTIONS
        return PPC_INSTRUCTIONS

    @staticmethod
    def _x86_count():
        from data.x86_instructions import X86_INSTRUCTIONS
        return X86_INSTRUCTIONS


# ---------------------------------------------------------------------------
# History panel (simple log)
# ---------------------------------------------------------------------------

class _HistoryPanel(wx.Panel):
    """Displays a log of all lookup operations performed this session."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent)
        self.SetBackgroundColour(THEME.BG)
        sizer = wx.BoxSizer(wx.VERTICAL)

        hdr = wx.StaticText(self, label="  Lookup History")
        hdr.SetForegroundColour(THEME.FG_AMBER)
        hdr.SetFont(get_font(11, bold=True))
        sizer.Add(hdr, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 6)

        self._list = wx.ListCtrl(self,
                                 style=wx.LC_REPORT | wx.LC_HRULES | wx.BORDER_NONE)
        self._list.SetBackgroundColour(THEME.BG_INPUT)
        self._list.SetForegroundColour(THEME.FG)
        self._list.SetFont(get_font(10))
        self._list.InsertColumn(0, "Mnemonic",  width=130)
        self._list.InsertColumn(1, "Direction", width=100)
        self._list.InsertColumn(2, "Result",    width=200)
        self._list.InsertColumn(3, "Confidence",width=110)
        self._list.InsertColumn(4, "Time",      width=150)
        sizer.Add(self._list, 1, wx.EXPAND | wx.ALL, 4)

        btn_clear = wx.Button(self, label="Clear History")
        btn_clear.SetBackgroundColour(THEME.BG_SURFACE)
        btn_clear.SetForegroundColour(THEME.FG_DIM)
        btn_clear.SetFont(get_font(9))
        btn_clear.Bind(wx.EVT_BUTTON, self._on_clear)
        sizer.Add(btn_clear, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.SetSizer(sizer)

    def refresh(self) -> None:
        import datetime
        entries = history_get()
        self._list.DeleteAllItems()
        for entry in reversed(entries):
            idx = self._list.InsertItem(0, entry.get("mnemonic", ""))
            self._list.SetItem(idx, 1, entry.get("direction", ""))
            self._list.SetItem(idx, 2, ", ".join(entry.get("targets", [])))
            self._list.SetItem(idx, 3, entry.get("confidence", ""))
            self._list.SetItem(idx, 4, entry.get("time", ""))

    def _on_clear(self, _event) -> None:
        _HISTORY.clear()
        self._list.DeleteAllItems()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class PPC2x86App(wx.App):
    """Top-level wxPython application."""

    def __init__(self, initial_mode: str = "32") -> None:
        self._initial_mode = initial_mode
        super().__init__(redirect=False)

    def OnInit(self) -> bool:
        self._frame = MainFrame(initial_mode=self._initial_mode)
        self.SetTopWindow(self._frame)
        return True

"""
searchable_list.py — A wx.Panel wrapping wx.SearchCtrl + wx.ListCtrl
with live filtering of instruction mnemonics.

Emits EVT_INSTR_SELECTED when the user selects an instruction.
"""

from __future__ import annotations

import wx
import wx.lib.newevent

from gui.theme import THEME, get_font

InstrSelectedEvent, EVT_INSTR_SELECTED = wx.lib.newevent.NewCommandEvent()


class SearchableList(wx.Panel):
    """
    Left-pane instruction list with live search filter.

    Parameters
    ----------
    parent      : wx.Window
    items       : list of (mnemonic, category) tuples
    """

    def __init__(self, parent: wx.Window,
                 items: list[tuple[str, str]] | None = None) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour(THEME.BG_PANEL)

        self._all_items: list[tuple[str, str]] = items or []
        self._filtered: list[tuple[str, str]] = list(self._all_items)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Search box
        self._search = wx.SearchCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._search.SetBackgroundColour(THEME.BG_INPUT)
        self._search.SetForegroundColour(THEME.FG)
        self._search.SetFont(get_font(10))
        self._search.ShowCancelButton(True)
        self._search.SetHint("Filter instructions…")
        sizer.Add(self._search, 0, wx.EXPAND | wx.ALL, 4)

        # List
        self._list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.BORDER_NONE,
        )
        self._list.SetBackgroundColour(THEME.BG_INPUT)
        self._list.SetForegroundColour(THEME.FG)
        self._list.SetFont(get_font(10))
        self._list.InsertColumn(0, "Mnemonic", width=130)
        self._list.InsertColumn(1, "Category", width=100)
        sizer.Add(self._list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        # Count label
        self._count_label = wx.StaticText(self, label="")
        self._count_label.SetForegroundColour(THEME.FG_DIM)
        self._count_label.SetFont(get_font(8))
        sizer.Add(self._count_label, 0, wx.LEFT | wx.BOTTOM, 6)

        self.SetSizer(sizer)

        self._populate()

        self._search.Bind(wx.EVT_TEXT, self._on_search_text)
        self._search.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_cancel)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def set_items(self, items: list[tuple[str, str]]) -> None:
        self._all_items = items
        self._apply_filter(self._search.GetValue())

    def get_selected(self) -> str | None:
        idx = self._list.GetFirstSelected()
        if idx == -1:
            return None
        return self._list.GetItemText(idx, 0)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _populate(self) -> None:
        self._list.DeleteAllItems()
        for mnem, cat in self._filtered:
            idx = self._list.InsertItem(self._list.GetItemCount(), mnem)
            self._list.SetItem(idx, 1, cat)
        self._count_label.SetLabel(f"  {len(self._filtered)} instructions")

    def _apply_filter(self, query: str) -> None:
        q = query.lower().strip()
        if q:
            self._filtered = [
                (m, c) for m, c in self._all_items
                if q in m.lower() or q in c.lower()
            ]
        else:
            self._filtered = list(self._all_items)
        self._populate()

    def _on_search_text(self, event: wx.CommandEvent) -> None:
        self._apply_filter(event.GetString())

    def _on_cancel(self, _event) -> None:
        self._search.SetValue("")
        self._apply_filter("")

    def _on_item_selected(self, event: wx.ListEvent) -> None:
        mnem = self._list.GetItemText(event.GetIndex(), 0)
        evt = InstrSelectedEvent(self.GetId(), mnemonic=mnem)
        wx.PostEvent(self, evt)

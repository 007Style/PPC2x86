"""
theme.py — Colour palette, fonts, and retro-terminal styling helpers.

The theme is a dark phosphor-green terminal aesthetic inspired by
classic ISA-era workstation consoles.

Usage
-----
    from gui.theme import THEME, apply_theme, get_font

    apply_theme(window)          # recursively set bg/fg on a wx.Window
    font = get_font(size=12, bold=True)
"""

from __future__ import annotations

import wx

# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------

class THEME:
    # Backgrounds
    BG          = wx.Colour(18, 20, 18)       # near-black green tint
    BG_SURFACE  = wx.Colour(26, 30, 26)       # slightly lighter surface
    BG_PANEL    = wx.Colour(20, 24, 20)       # panel background
    BG_INPUT    = wx.Colour(10, 14, 10)       # input box background

    # Text
    FG          = wx.Colour(140, 220, 100)    # phosphor green — primary text
    FG_DIM      = wx.Colour(80, 130, 60)      # dimmer secondary text
    FG_BRIGHT   = wx.Colour(190, 255, 140)    # highlighted / selected text
    FG_AMBER    = wx.Colour(230, 180, 40)     # amber accent (warnings, labels)
    FG_CYAN     = wx.Colour(60, 210, 200)     # cyan accent (links, titles)
    FG_RED      = wx.Colour(220, 70, 60)      # error / no-match
    FG_WHITE    = wx.Colour(220, 230, 220)    # near-white for emphasis

    # Confidence badge colours
    CONF_DIRECT     = wx.Colour(60, 210, 100)  # direct → green
    CONF_CLOSE      = wx.Colour(60, 200, 210)  # close → cyan
    CONF_SUGGESTION = wx.Colour(230, 180, 40)  # suggestion → amber
    CONF_NONE       = wx.Colour(220, 70, 60)   # none → red
    CONF_FUZZY      = wx.Colour(100, 100, 100) # fuzzy → grey

    # Borders & separators
    BORDER      = wx.Colour(40, 60, 40)
    BORDER_ACTIVE = wx.Colour(100, 200, 80)

    # Selection / hover
    SEL_BG      = wx.Colour(35, 60, 35)
    SEL_FG      = wx.Colour(200, 255, 160)

    # Ticker bar
    TICKER_BG   = wx.Colour(10, 14, 10)
    TICKER_FG   = wx.Colour(90, 180, 70)

    # Status bar
    STATUS_BG   = wx.Colour(14, 18, 14)
    STATUS_FG   = wx.Colour(80, 150, 60)

    # Suggestion warning banner
    WARN_BG     = wx.Colour(50, 40, 10)
    WARN_FG     = wx.Colour(230, 200, 50)


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_MONO_FAMILIES = [
    "Menlo", "Consolas", "DejaVu Sans Mono",
    "Courier New", "Courier", "Monospace",
]


def _pick_mono_face() -> str:
    """Return the first monospace face available on this system."""
    fe = wx.FontEnumerator()
    fe.EnumerateFacenames()
    available = set(fe.GetFacenames())
    for name in _MONO_FAMILIES:
        if name in available:
            return name
    return "Courier New"


_MONO_FACE: str | None = None   # lazily resolved


def get_font(size: int = 11, bold: bool = False, italic: bool = False) -> wx.Font:
    """Return a monospace wx.Font with the given attributes."""
    global _MONO_FACE
    if _MONO_FACE is None:
        _MONO_FACE = _pick_mono_face()
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    style  = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    return wx.Font(
        wx.FontInfo(size)
        .FaceName(_MONO_FACE)
        .Bold(bold)
        .Italic(italic)
    )


# ---------------------------------------------------------------------------
# Theme application
# ---------------------------------------------------------------------------

def apply_theme(window: wx.Window, recursive: bool = True) -> None:
    """Apply the retro terminal colour scheme to *window* and its children."""
    window.SetBackgroundColour(THEME.BG)
    window.SetForegroundColour(THEME.FG)
    if hasattr(window, "SetFont"):
        window.SetFont(get_font(10))
    if recursive:
        for child in window.GetChildren():
            apply_theme(child, recursive=True)


def style_button(btn: wx.Button) -> None:
    """Apply theme styling to a wx.Button."""
    btn.SetBackgroundColour(THEME.BG_SURFACE)
    btn.SetForegroundColour(THEME.FG_BRIGHT)
    btn.SetFont(get_font(10, bold=True))


def style_label(label: wx.StaticText, bright: bool = False, amber: bool = False) -> None:
    """Apply theme styling to a wx.StaticText label."""
    label.SetBackgroundColour(THEME.BG)
    fg = THEME.FG_BRIGHT if bright else (THEME.FG_AMBER if amber else THEME.FG)
    label.SetForegroundColour(fg)


def style_list(ctrl: wx.ListCtrl) -> None:
    """Apply theme styling to a wx.ListCtrl."""
    ctrl.SetBackgroundColour(THEME.BG_INPUT)
    ctrl.SetForegroundColour(THEME.FG)
    ctrl.SetFont(get_font(10))


def confidence_colour(confidence: str) -> wx.Colour:
    """Return the theme colour for a confidence level string."""
    return {
        "direct":     THEME.CONF_DIRECT,
        "close":      THEME.CONF_CLOSE,
        "suggestion": THEME.CONF_SUGGESTION,
        "none":       THEME.CONF_NONE,
        "fuzzy":      THEME.CONF_FUZZY,
    }.get(confidence, THEME.FG)

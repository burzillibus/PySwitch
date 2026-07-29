from pyswitch.ui.ui import DisplayBounds, DisplayElement
from pyswitch.ui.elements import DisplayLabel

# Lightweight default splash. The labels exist so inputs.py can bind actions,
# but backgrounds stay disabled and the root stays minimal to conserve RAM.
_ACTION_LABEL_LAYOUT = {
    "font": "/fonts/H15.pcf",
    "text": "",
}

DISPLAY_HEADER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 0, y = 0, w = 120, h = 40),
    id = 1
)
DISPLAY_HEADER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 120, y = 0, w = 120, h = 40),
    id = 2
)
DISPLAY_FOOTER_1 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 0, y = 200, w = 120, h = 40),
    id = 3
)
DISPLAY_FOOTER_2 = DisplayLabel(
    layout = _ACTION_LABEL_LAYOUT,
    bounds = DisplayBounds(x = 120, y = 200, w = 120, h = 40),
    id = 4
)
DISPLAY_RIG_NAME = DisplayLabel(
    layout = {
        "font": "/fonts/PTSans-NarrowBold-40.pcf",
        "lineSpacing": 0.8,
        "maxTextWidth": 220,
        "text": "PySwitch",
    },
    bounds = DisplayBounds(x = 0, y = 40, w = 240, h = 160),
    id = 5
)

class _WallpaperSplash(DisplayElement):
    # The bitmap stays on disk. OnDiskBitmap only allocates the small displayio
    # objects it needs, but it is still optional for the RP2040's small heap.
    def make_splash(self, font_loader):
        if self.splash:
            return

        super().make_splash(font_loader)

        try:
            from config import Config
            if not Config.get("enableWallpaper", False):
                return

            from displayio import OnDiskBitmap, TileGrid
            bitmap = OnDiskBitmap("/wallpaper.bmp")
            if bitmap.width != 240 or bitmap.height != 240:
                return

            # Retain both objects for as long as this root group is displayed.
            self._wallpaper_bitmap = bitmap
            self._wallpaper = TileGrid(bitmap, pixel_shader = bitmap.pixel_shader)
            self.splash.append(self._wallpaper)
        except (ImportError, OSError, ValueError):
            # A missing or invalid optional image must never prevent booting.
            pass


Splashes = _WallpaperSplash(
    bounds = DisplayBounds(
        x = 0,
        y = 0,
        w = 240,
        h = 240
    ),
    children = [
        DISPLAY_HEADER_1,
        DISPLAY_HEADER_2,
        DISPLAY_FOOTER_1,
        DISPLAY_FOOTER_2,
        DISPLAY_RIG_NAME,
    ]
)

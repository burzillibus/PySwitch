import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


class _Group:
    def __init__(self):
        self.content = []

    def append(self, item):
        self.content.append(item)


class _DisplayBounds:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _DisplayElement:
    def __init__(self, bounds = None, children = None, **kwargs):
        self.bounds = bounds
        self.children = children or []
        self.splash = None

    def make_splash(self, font_loader):
        self.splash = _Group()


class _DisplayLabel:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _Bitmap:
    def __init__(self, path):
        self.path = path

    width = 240
    height = 240
    pixel_shader = object()


class _TileGrid:
    def __init__(self, bitmap, pixel_shader):
        self.bitmap = bitmap
        self.pixel_shader = pixel_shader


def _load_display(enable, bitmap_factory = _Bitmap):
    ui = ModuleType("pyswitch.ui.ui")
    ui.DisplayBounds = _DisplayBounds
    ui.DisplayElement = _DisplayElement

    elements = ModuleType("pyswitch.ui.elements")
    elements.DisplayLabel = _DisplayLabel

    displayio = ModuleType("displayio")
    displayio.OnDiskBitmap = bitmap_factory
    displayio.TileGrid = _TileGrid

    config = ModuleType("config")
    config.Config = {"enableWallpaper": enable}

    modules = {
        "pyswitch.ui.ui": ui,
        "pyswitch.ui.elements": elements,
        "displayio": displayio,
        "config": config,
    }
    source = Path(__file__).parents[2] / "content" / "display.py"
    spec = importlib.util.spec_from_file_location("wallpaper_display_test", source)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    module._test_modules = modules
    return module


def _make_splash(module):
    with patch.dict(sys.modules, module._test_modules):
        module.Splashes.make_splash(None)


class TestOptionalWallpaper(unittest.TestCase):
    def test_disabled_does_not_allocate_bitmap_objects(self):
        module = _load_display(False)
        _make_splash(module)
        self.assertEqual(module.Splashes.splash.content, [])

    def test_enabled_appends_wallpaper_behind_labels(self):
        module = _load_display(True)
        _make_splash(module)
        self.assertEqual(len(module.Splashes.splash.content), 1)
        self.assertIsInstance(module.Splashes.splash.content[0], _TileGrid)

    def test_unreadable_wallpaper_does_not_prevent_splash_creation(self):
        def unreadable_bitmap(path):
            raise OSError("missing")

        module = _load_display(True, unreadable_bitmap)
        _make_splash(module)
        self.assertEqual(module.Splashes.splash.content, [])

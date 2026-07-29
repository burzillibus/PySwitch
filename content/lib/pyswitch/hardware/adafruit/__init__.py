import board as _board

# Display driver
from busio import SPI as _SPI
from displayio import release_displays as _release_displays
from busdisplay import BusDisplay as _BusDisplay
from adafruit_misc.neopixel import NeoPixel as _NeoPixel

try:
    from fourwire import FourWire as _FourWire
except ImportError:
    from displayio import FourWire as _FourWire

# Font loader
from adafruit_bitmap_font import bitmap_font as _bitmap_font

# ST7789 init sequence for busdisplay.
_ST7789_INIT_SEQUENCE = (
    b"\x01\x80\x96"
    b"\x11\x80\x0a"
    b"\x3a\x01\x55"
    b"\x36\x01\x08"
    b"\x21\x80\x0a"
    b"\x13\x80\x0a"
    b"\x29\x80\x0a"
)


# TFT driver class
class AdafruitST7789DisplayDriver:

    def __init__(self, 
                width = 240, 
                height = 240,
                tft_cs = _board.GP13,
                tft_dc = _board.GP12,
                spi_mosi = _board.GP15,
                spi_clk = _board.GP14,
                # With CircuitPython 10's BusDisplay driver this panel uses
                # the native top-left origin; the former 80-row offset leaves
                # a one-third-height artefact at the top of the panel.
                row_start = 0,
                rotation = 0,
                baudrate = 24000000         # 24MHz
        ):
        self.width = width
        self.height = height

        self.__tft_cs = tft_cs
        self.__tft_dc = tft_dc
        self.__spi_mosi = spi_mosi
        self.__spi_clk = spi_clk

        self.__row_start = row_start
        self.__rotation = rotation
        self.__baudrate = baudrate

    # Initialize the display
    def init(self):        
        _release_displays()
        
        spi = _SPI(
            self.__spi_clk, 
            MOSI = self.__spi_mosi
        )
        while not spi.try_lock():
            pass
        
        spi.configure(
            baudrate = self.__baudrate
        )
        spi.unlock()

        display_bus = _FourWire(
            spi, 
            command = self.__tft_dc, 
            chip_select = self.__tft_cs, 
            reset = None
        )

        self.tft = _BusDisplay(
            display_bus,
            _ST7789_INIT_SEQUENCE,
            width = self.width,
            height = self.height,
            colstart = 0,
            rowstart = self.__row_start,
            rotation = self.__rotation,
            color_depth = 16
        )


##################################################################################################


# Buffered font loader
class AdafruitFontLoader:
    __fonts = {}

    # Returns a font (buffered)
    def get(self, path):
        if path in self.__fonts:
            return self.__fonts[path]
        
        font = _bitmap_font.load_font(path)
        self.__fonts[path] = font

        return font


##################################################################################################


# Implements communication with an array of NeoPixels
class AdafruitNeoPixelDriver:

    def __init__(self, port = _board.GP7):
        self.__port = port
        self.leds = None
        
    # Initialize NeoPixel array. Neopixel documentation:
    # https://docs.circuitpython.org/projects/neopixel/en/latest/
    # https://learn.adafruit.com/adafruit-neopixel-uberguide/python-circuitpython
    def init(self, num_leds):
        self.leds = _NeoPixel(self.__port, num_leds)



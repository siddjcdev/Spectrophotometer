from machine import Pin, SoftI2C, SPI, freq
import gc
#from gui.core.tgui import Display
from drivers.ili93xx.ili9341 import ILI9341 as SSD

freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance

prst = Pin(14, Pin.OUT, value=1)
pdc = Pin(15, Pin.OUT, value=0) # Arbitrary pins
pcs = Pin(17, Pin.OUT, value=1)


spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16), baudrate=30_000_000)

gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height=240, width=320, usd=True)

from gui.core.tgui import Display, quiet
quiet()  # Suppress free RAM messages (optional)
#display = Display(ssd)
# Touch configuration
from touch.xpt2046 import XPT2046

tpad = XPT2046(spi, Pin(0, Pin.OUT, value=1), ssd)
# To create a tpad.init line for your displays please read SETUP.md
tpad.init(240, 320, 157, 150, 3863, 4095, True, True, True)
display = Display(ssd, tpad)
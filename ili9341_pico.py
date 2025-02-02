# ili9341_pico.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on Pi Pico
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# Pico      Display
# GPIO Pin
# 3v3  36   Vin
# IO6   9   CLK  Hardware SPI0
# IO7  10   DATA (AKA SI MOSI)
# IO8  11   DC
# IO9  12   Rst
# Gnd  13   Gnd
# IO10 14   CS

# Pushbuttons are wired between the pin and Gnd
# Pico pin  Meaning
# 16        Operate current control
# 17        Decrease value of current control
# 18        Select previous control
# 19        Select next control
# 20        Increase value of current control

from machine import Pin, SPI, freq
from drivers.ili93xx.ili9341 import ILI9341 as SSD
from gui.core.ugui import Display
import gc
TFT_CLK_PIN = const(18)
TFT_MOSI_PIN = const(19)
TFT_MISO_PIN = const(16)

TFT_CS_PIN = const(17)
TFT_RST_PIN = const(14)
TFT_DC_PIN = const(15)

spi = SPI(
    0,
    baudrate=40000000,
    miso=Pin(TFT_MISO_PIN),
    mosi=Pin(TFT_MOSI_PIN),
    sck=Pin(TFT_CLK_PIN))
print(spi)



freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance
pdc = Pin(8, Pin.OUT, value=0)  # Arbitrary pins
prst = Pin(9, Pin.OUT, value=1)
pcs = Pin(10, Pin.OUT, value=1)
#spi = SPI(0, sck=Pin(6), mosi=Pin(7), miso=Pin(4), baudrate=30_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, usd=True)


# Create and export a Display instance
# Define control buttons
nxt = Pin(19, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)

# display = Display(
#     spi,
#     cs=Pin(TFT_CS_PIN),
#     dc=Pin(TFT_DC_PIN),
#     rst=Pin(TFT_RST_PIN),
#     w=SCR_WIDTH,
#     h=SCR_HEIGHT,
#     r=SCR_ROT)

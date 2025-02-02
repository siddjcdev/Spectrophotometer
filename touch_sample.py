import touch_setup  # Create a display instance
from gui.core.tgui import Screen, ssd

from gui.widgets import Label, Button, CloseButton, LED
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *
import asyncio

async def stop_rfsh():
    await Screen.rfsh_lock.acquire()

def cby(_):
    asyncio.create_task(stop_rfsh())

def cbn(_):
    Screen.rfsh_lock.release()  # Allow refresh

class BaseScreen(Screen):
    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 2
        Label(wri, row, col, "Refresh test")
        self.led = LED(wri, row, 80)
        row = 50
        Button(wri, row, col, text="Stop", callback=cby)
        col += 60
        Button(wri, row, col, text="Start", callback=cbn)
        self.reg_task(self.flash())
        CloseButton(wri)  # Quit

    async def flash(self):  # Proof of stopped refresh
        while True:
            self.led.value(not self.led.value())
            await asyncio.sleep_ms(300)

def test():
    print("Refresh test.")
    Screen.change(BaseScreen)

test()
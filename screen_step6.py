import touch_setup  # Create a display instance
from gui.core.tgui import Screen, ssd

from gui.widgets import Button, CloseButton, Label
from gui.core.writer import CWriter

# Font for CWriter
#import gui.fonts.freesans20 as font
import gui.fonts.arial35 as font
import gui.fonts.freesans20 as small_font
import gui.fonts.arial10 as tiny_font
from gui.core.colors import *

# Defining a button in this way enables it to be re-used on
# multiple Screen instances. Note that a Screen class is
# passed, not an instance.
def fwdbutton(wri, row, col, cls_screen, text="Next"):
    def fwd(button):
        Screen.change(cls_screen)  # Callback

    Button(wri, row, col, callback=fwd, text=text, height=50, width=80)


wri = CWriter(ssd, font, GREEN, BLACK, verbose=True)
wri_small_green = CWriter(ssd, small_font, GREEN, BLACK, verbose=False)
wri_small_yellow = CWriter(ssd, small_font, YELLOW, BLACK, verbose=False)
wri_small_red = CWriter(ssd, small_font, RED, BLACK, verbose=False)
wri_tiny_yellow = CWriter(ssd, tiny_font, YELLOW, BLACK, verbose=False)

# This screen overlays BaseScreen.
class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, "New screen.")
        CloseButton(wri)


class BaseScreen(Screen):
    def __init__(self):

        super().__init__()
        #Button(wri_small, 210, 150, fwd, "Next", height=50, width=80)
        Label(wri_small_red, 10, 20, "SoluteSixthSense")
        Label(wri_small_yellow, 40, 20, "Selected color = red")
        #fwdbutton(wri, 40, 40, BackScreen)
        #CloseButton(wri)
        #Label (wri_small_yellow, 55, 50, "Ready for Experimentation")  
        Label(wri, 90, 50, "Scanning...")
        
        #Label(wri_small_green, 150 50, "using your favorite browser")
        #Label(wri_small_green, 180, 50, "to conduct an experiment.")
def test():
    print("Screen change demo.")
    Screen.change(BaseScreen)  # Pass class, not instance!


test()
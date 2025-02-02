
# colori.py

"""
This file licensed under the MIT License and incorporates work covered by
the following copyright and permission notice:

The MIT License (MIT)

Copyright (c) 2022-2024 Rob Hamerling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
 Colorimeter with AS7341 sensor

 Rob Hamerling, Version 1.4, November 2024

 Description:
 Light sensor as7341 accessed via I2C with a private library.
 Measurement results are sent to the serial terminal and
 stored in a log file, on SD-card or local (virtual) disk.
 Progress is shown on serial terminal and on OLED.
 Logging time is obtained from internal clock.

 Measurements:
 After startup of the program measurements are started by push button.
 After pushing the button a number of consecutive measurements are taken
 with presumably different settings of the AS7341 (atime, asteps, again).
 This cycle is repeated indefinitely until the program is terminated by
 keyboard interrupt (Ctrl-C).

 Requirements and setup:
 - One AS7341 sensor board via I2C (second hardware I2C module).
 - Start-button (pin normally high, start measurements at pull down)
 - DS3231 via hardware I2C bus to synchronize internal RTC.
 - OLED via hardware I2C bus to show measurement progress.
  Notes:
 - RTC is assumed to be set in UTC time (req'd for date/time SDcard).
   Localtime is supported by private 'time.py' library.
   Thonny may override RTC setting!

   Pin assignments of ESP32
    0 onboard push button (BOOT)
    2, 4, 12, 13, 14, 15 reserved for SDCard (currently not used)
    5  external LED (heartbeat)
    18, 19 hardware I2C bus 0 for OLED (and DS3231)
    21 onboard LED (could be used in stead of external LED on pin 5)
    25, 26 hardware I2C bus 1 for AS7341
    22-36 not used
    39 external push button: measurements start signal
"""


# $$$$$$$ to be added: rotary menu for gain/integration selection.

import sys
import time
from machine import I2C, Pin

from as7341 import *            # class for AS7341 sensor

#  display progress of measurements on OLED
from oled import *              # sh1106/ssd1306 (I2C-)display

# version
COLORIVERSION = "1.4"           # version (string)

startButton = Pin(39, Pin.IN, Pin.PULL_UP)    # trigger to (re-)start measurement

# class of sensor parameters
class sensor_parm:
    def __init__(self, atime, astep, again):
        self.atime = atime
        self.astep = astep
        self.again = again

# parameter settings for a number of consecutive measurements
measurement_variants = (
                        sensor_parm(29, 599, 4),
                        sensor_parm(29, 599, 6)
                       )

# date formatting strings
month = ("Jan","Feb","Mar","Apr","May", "Jun","Jul","Aug","Sep","Oct","Nov","Dec")

def oled_datetime(oled):
    """  show local date and time on second line of OLED """
    _, MM, DD, hh, mm, ss, _, _ = time.localtime()
    oled.string('{:2d} {:s}. {:2d}:{:02d}:{:02d}'.format(DD, month[MM-1], hh, mm, ss), 1, 0)

def oled_count(oled, count):
    """  show count of F6 on line 6 of OLED """
    oled.string(f'F6 count {count:5d}', 5, 0)

def heartbeat(status=True):
    """ When activated LED will blink once a second """
    heartbeatLed = Pin(heartbeatpin, Pin.OUT)
    tmr = Timer(1)                          # use Timer 1
    if status:                              # activate
        tmr.init(period=500, mode=Timer.PERIODIC,
             callback=lambda t: heartbeatLed.off() if heartbeatLed.value() else heartbeatLed.on())
    else:                                   # deactivate
        tmr.deinit()
        heartbeatLed.off()

def measure(sensor, oled, logfile):
    """ <sensor>  - AS7341 object
        <oled>    - OLED object for indication of progress
        <logfile> - file object for logging of measurement results
    """
    # logfile.write('"Overflow count", {:d}\n'.format(sensor.get_overflow_count()))
    # logfile.write('"Integration time", {:.2f}\n\n'.format(sensor.get_integration_time()))
    logfile.write('"time", " gain ", "integ", "F3", "F4", "F5", "F6", "F7", "F8"\n')
    logfile.write(', "factor", "msecs"\n\n')
    # Measurement mode and channel selection are fixed
    sensor.set_measure_mode(AS7341_MODE_SPM)        # interactive with user
    sensor.channel_select('F3F8')                   # configure for channels F3..F8
    try:
        while True:
            oled_datetime(oled)
            print('Ready! Push start button...')    # 'human' request to start measurement
            oled.string('Push start...', 7, 0)
            while startButton.value():
                time.sleep_ms(50)                   # loop until button pushed
            for i in range(len(measurement_variants)):  # all variants (in sequence)
                m = measurement_variants[i]         # m is actual parms combination
                sensor.set_atime(m.atime)           # number of asteps
                sensor.set_astep(m.astep)           # astep time
                sensor.set_again(m.again)           # again code
                sensor.start_measure()              # with pre-configured channels!
                counts = sensor.get_spectral_data() # obtain 6 counts
                if i == 0:                          # timestamp only with first measurement
                    _,_,_,hh,mm,ss,_,_ = time.localtime()
                    print(f'{hh:02d}:{mm:02d}:{ss:02d}', end="")
                    logfile.write(f'"{hh:02d}:{mm:02d}:{ss:02d}"')
                else:
                    print(' ' * 9, end="")
                    logfile.write('" "')            # filler
                print(' {:6.1f} {:6.2f}'.format(
                                sensor.get_again_factor(),
                                sensor.get_integration_time()), end='')
                logfile.write(',{:6.1f}, {:6.2f}'.format(
                                sensor.get_again_factor(),
                                sensor.get_integration_time()))
                for count in counts:
                    if count >= sensor.get_overflow_count():
                        count = -1                  # indicate overflow
                    print(f' {count:6d}', end='')
                    logfile.write(f', {count:6d}')
                print('')
                logfile.write('\n')
                oled_count(oled, counts[3])         # show count of F6
            time.sleep_ms(500)                      # sort of button 'debouncing'
            while not startButton.value():
                time.sleep_ms(50)                   # loop until button released
    except KeyboardInterrupt:
        print('Interrupted from keyboard')
        oled.clear(2, 7)
        oled.string('Interrupted!', 3, 2)
        return

def main():
    # initialize I2C interfaces 
    # I2C bus for OLED display:
    bus0 = I2C(0)                           # using default pins
    print('Detected devices on bus0 at I2C-addresses:',
          ' '.join(['0x{:02X}'.format(x) for x in bus0.scan()]))
    #  initialize OLED
    oled = OLED(bus0)                       # instance of OLED class
    if oled.connected:
        oled.flip(True)                     # depends on mounting
        oled.string('Colorimeter ' + COLORIVERSION, 0, 0)
    else:
        print('No OLED connected, proceeding without!')
    # I2C bus for light sensor
    bus1 = I2C(1, scl=Pin(27), sda=Pin(26))
    print('Detected devices on bus1 at I2C-addresses:',
          ' '.join(['0x{:02X}'.format(x) for x in bus1.scan()]))
    # initialize light sensor
    sensor = AS7341(bus1)
    if not sensor.isconnected():
        print('Failed to contact AS7341, terminating')
        return
    #  initialize logfile
    YY, MM, DD, hh, mm, ss, _, _ = time.localtime()
    logfilefmt = 'colori-{:02d}{:02d}{:02d}-{:02d}{:02d}{:02d}.csv'
    logfile = logfilefmt.format(YY-2000, MM, DD, hh, mm, ss)    # build filename
    print('Logging to file', logfile)
    with open(logfile, 'w') as flog:             #  start logging
        flog.write(f'\n"Colori", "version {COLORIVERSION}"')
        flog.write(f' ,"{DD:2d} {month[MM-1]} {YY:4d}"\n\n')
        # Ask operator for one-line description for logfile
        print('Enter comment to identify the measurement')
        measurement_comment = input('> ')        # input from user
        flog.write('"' + measurement_comment + '"\n\n')
        # start measurements (hit Ctrl-C to finish!)
        measure(sensor, oled, flog)              # start measurements
    # terminate
    oled.clear()
    sensor.disable()


# ===================
#  M A I N L I N E
# ===================
main()

#
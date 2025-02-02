from ili934xnew import ILI9341, color565
from machine import I2C, SoftI2C, Pin, SPI, Timer
from micropython import const
import sys
import os
import glcdfont
import tt24
import tt32
#import freesans20fixed
import utime


SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
#SCR_ROT = const(0)
SCR_ROT = const(1)

dispH = 100
dispW = 320
marginX = const(10)
marginY = const(30)
TempFrame_W = dispW-(2*marginX)
TempFrame_H = 120
TempFrame_X0 = marginX
TempFrame_Y0 = marginY
TempFrame_Y1 = marginY+TempFrame_H

TempPanel_X0 = TempFrame_X0
TempPanel_Y0 = TempFrame_Y1 + 10
TempPanel_W = TempFrame_W
TempPanel_H = 32

sampleSize = TempFrame_W      #200
tempValueLim = 23 #TempFrame_H  #100

# FreqFrame_W = dispW-(2*marginX)
# FreqFrame_H = 100
# FreqFrame_X0 = marginX
# FreqFrame_Y0 = marginY + 150
# 
# FreqFrame_Y1 = marginY+FreqFrame_H + 150
# 
# FreqPanel_X0 = FreqFrame_X0
# FreqPanel_Y0 = FreqFrame_Y1 + 10


#set default CPU freq
# machine.freq(125000000)
# FreqChangeInterval = 15  #change freq in 15 sec interval
# freqSet = [50000000, 250000000, 40000000, 260000000]
# freqCnt = FreqChangeInterval
# freqIdx = 0

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

display = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN),
    dc=Pin(TFT_DC_PIN),
    rst=Pin(TFT_RST_PIN),
    w=SCR_WIDTH,
    h=SCR_HEIGHT,
    r=SCR_ROT)

def drawHLine(x, y, w, color):
    for i in range(w):
        display.pixel(x+i,y,color)
        
def drawVLine(x, y, h, color):
    for i in range(h):
        display.pixel(x,y+i,color)
        
def drawVLineUp(x, y, h, color):
    for i in range(h):
        display.pixel(x,y-i,color)
        
def drawFrame(x, y, w, h):
    display.fill_rectangle(x, y, w, h, frameBGcolor)

    l1x = x-1
    l2x = x+w
    l1y = y-1
    l2y = y+h+1
    lcolor = color565(250, 250, 250)
    
    for i in range(w+2):
        display.pixel(l1x+i,l1y,lcolor)
        display.pixel(l1x+i,l2y,lcolor)
 
    for i in range(h+2):
        display.pixel(l1x,l1y+i,lcolor)
        display.pixel(l2x,l1y+i,lcolor)
        
        

frameBGcolor = color565(150, 150, 150)
TempPanel = color565(0, 0, 0)

display.erase()


#setup AS7341
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
print("Detected devices at I2C-addresses:",
      " ".join(["0x{:02X}".format(x) for x in i2c.scan()]))

from as7341 import *

sensor = AS7341(i2c)
if not sensor.isconnected():
    print("Failed to contact AS7341, terminating")
    sys.exit(1)
    
sensor.set_measure_mode(AS7341_MODE_SPM)
sensor.set_atime(29)                # 30 ASTEPS
sensor.set_astep(599)               # 1.67 ms
sensor.set_again(4)                 # factor 8 (with pretty much light)

print("Channel 2", sensor.get_channel_data(2))
print("Integration time:", sensor.get_integration_time(), "msec")

# formatting strings for the different channels
fmt = { "f1" : 'F1 (405-425nm): {:d}',
        "f2" : 'F2 (435-455nm): {:d}',
        "f3" : 'F3 (470-490nm): {:d}',
        "f4" : 'F4 (505-525nm): {:d}',
        "f5" : 'F5 (545-565nm): {:d}',
        "f6" : 'F6 (580-600nm): {:d}',
        "f7" : 'F7 (620-640nm): {:d}',
        "f8" : 'F8 (670-690nm): {:d}',
        "clr": 'Clear: {:d}',
        "nir": 'NIR: {:d}'
      }

def p(f,v):
    """ formatting function for a single channel """
    print(fmt[f].format(v))

#setup Temp
sensor_temp = machine.ADC(4) #internal temperature sensor
conversion_factor = 3.3/(65535)

timReached = False
tim = Timer()
def TimerTick(timer):
    global led
    #led.toggle()
    global timReached
    timReached = True
    
tim.init(freq=1, mode=Timer.PERIODIC, callback=TimerTick)

#Title
display.set_font(tt32)
#display.set_font(freesans20fixed)

display.set_font(tt24)
display.set_pos(0, 0)
display.set_color(color565(250, 250, 0), color565(0, 0, 0))
display.print("Spectrophotometer")
display.print("")

#End of Title

drawFrame(TempFrame_X0, TempFrame_Y0, TempFrame_W, TempFrame_H)

#sampleTemp=[0]*sampleSize
sampleIndex=0
tempString = "0"
while True:
    if timReached:
        
        timReached = False
        
        
        #Post AS7341 sensor
        sensor.start_measure("F1F4CN")
        f1,f2,f3,f4,c,n= sensor.get_spectral_data()
        p("f1", f1)
        p("f2", f2)
        p("f3", f3)
        p("f4", f4)
        sensor.start_measure("F5F8CN")
        f5,f6,f7,f8,c1,n1 = sensor.get_spectral_data()
        p("f5", f5)
        p("f6", f6)
        p("f7", f7)
        p("f8", f8)

        print('------------------------')
        
        #temperature
        reading = sensor_temp.read_u16()*conversion_factor
        tempValue = 27-(reading-0.706)/0.001721
        
        print(tempValue)
        
        tempString=str(tempValue)
        if tempValue >= tempValueLim:
            display.set_color(color565(250, 0, 0), color565(0, 0, 0))
        else:
            display.set_color(color565(0, 0, 250), color565(0, 0, 0))
        display.set_pos(TempPanel_X0, TempPanel_Y0)
        display.print(tempString)
        
        if sampleIndex == 0:
            
            #clear frame
             display.fill_rectangle(TempFrame_X0,
                                    TempFrame_Y0,
                                   TempFrame_W,
                                   TempFrame_H,
                                   frameBGcolor)
            
#             display.fill_rectangle(FreqFrame_X0,
#                                    FreqFrame_Y0,
#                                    FreqFrame_W,
#                                    FreqFrame_H, 
#                                    frameBGcolor)
        
        #plot temperature
        if tempValue >= tempValueLim:
            drawVLineUp(TempFrame_X0+sampleIndex,
                        TempFrame_Y1,
                        tempValue,
                        color565(0, 0, 250))
            display.pixel(TempFrame_X0+sampleIndex,f1,color565(126, 0, 219))
            display.pixel(TempFrame_X0+sampleIndex,f2,color565(0, 40, 255))
            display.pixel(TempFrame_X0+sampleIndex,f3,color565(0, 213, 255))
            display.pixel(TempFrame_X0+sampleIndex,f4,color565(31, 255, 0))
            display.pixel(TempFrame_X0+sampleIndex,f5,color565(179, 255, 0))
            display.pixel(TempFrame_X0+sampleIndex,f6,color565(255, 223, 0))
            display.pixel(TempFrame_X0+sampleIndex,f7,color565(255, 119, 0))
            display.pixel(TempFrame_X0+sampleIndex,f8,color565(223, 0, 0))
        else:
            display.pixel(TempFrame_X0+sampleIndex,f1,color565(126, 0, 219))
            display.pixel(TempFrame_X0+sampleIndex,f2,color565(0, 40, 255))
            display.pixel(TempFrame_X0+sampleIndex,f3,color565(0, 213, 255))
            display.pixel(TempFrame_X0+sampleIndex,f4,color565(31, 255, 0))
            display.pixel(TempFrame_X0+sampleIndex,f5,color565(179, 255, 0))
            display.pixel(TempFrame_X0+sampleIndex,f6,color565(255, 223, 0))
            display.pixel(TempFrame_X0+sampleIndex,f7,color565(255, 119, 0))
            display.pixel(TempFrame_X0+sampleIndex,f8,color565(223, 0, 0))
            
#         #plot CPU freq
#         freqValue = machine.freq()
#         print(freqValue)
#         
#         freqBar = freqValue/3000000  #freqBar in range 0~100
#         drawVLineUp(FreqFrame_X0+sampleIndex,
#                     FreqFrame_Y1,
#                     freqBar,
#                     color565(250, 250, 0))
#         
#         freqString=str(freqValue/1000000) + " (MHz)"
#         display.set_color(color565(0, 0, 250), color565(0, 0, 0))
#         display.set_pos(FreqPanel_X0, FreqPanel_Y0)
#         display.print(freqString)
        
        sampleIndex = sampleIndex+1
        if(sampleIndex>=sampleSize):
            sampleIndex = 0
            
        
        
#         #check if frequency changeinterval reached
#         freqCnt = freqCnt-1
#         if freqCnt == 0:
#             freqCnt = FreqChangeInterval
#             newFreq = freqSet[freqIdx]
#             print(newFreq)
#             machine.freq(newFreq)
#             freqIdx = freqIdx + 1
#             if freqIdx == len(freqSet):
#                 freqIdx = 0;
print("- bye-")
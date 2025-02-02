"""
Exercise on Raspberry Pi Pico/MicroPython
with 320x240 ILI9341 SPI Display

Pico plot internal temperature graphically
vs CPU Clock
"""
from ili934xnew import ILI9341, color565
from machine import Pin, SPI, Timer
from micropython import const
import os
import glcdfont
import tt24
import tt32
#import freesans20fixed
import utime

sensor_temp = machine.ADC(4) #internal temperature sensor
conversion_factor = 3.3/(65535)

SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
#SCR_ROT = const(0)
SCR_ROT = const(2)

dispW = 240
dispH = 320
marginX = const(20)
marginY = const(10)
TempFrame_W = dispW-(2*marginX)
TempFrame_H = 100
TempFrame_X0 = marginX
TempFrame_Y0 = marginY
TempFrame_Y1 = marginY+TempFrame_H

TempPanel_X0 = TempFrame_X0
TempPanel_Y0 = TempFrame_Y1 + 10
TempPanel_W = TempFrame_W
TempPanel_H = 32

sampleSize = TempFrame_W      #200
tempValueLim = TempFrame_H  #100

FreqFrame_W = dispW-(2*marginX)
FreqFrame_H = 100
FreqFrame_X0 = marginX
FreqFrame_Y0 = marginY + 150

FreqFrame_Y1 = marginY+FreqFrame_H + 150

FreqPanel_X0 = FreqFrame_X0
FreqPanel_Y0 = FreqFrame_Y1 + 10

led = Pin(25, Pin.OUT)

#set default CPU freq
machine.freq(125000000)
FreqChangeInterval = 15  #change freq in 15 sec interval
freqSet = [50000000, 250000000, 40000000, 260000000]
freqCnt = FreqChangeInterval
freqIdx = 0

print("MicroPython:")
print(os.uname()[3])
print(os.uname()[4])
print()

"""
spi = SPI(0,baudrate=10000000,polarity=1,phase=1,bits=8,firstbit=SPI.MSB,sck=Pin(18),mosi=Pin(19), miso=Pin(16))
        display = Display(spi, dc=Pin(15), cs=Pin(17), rst=Pin(14))
"""

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
      
frameBGcolor = color565(150, 150, 150)
TempPanel = color565(0, 0, 0)

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
      
display.erase()

display.set_font(tt24)
display.set_pos(0, 0)
display.set_color(color565(250, 250, 0), color565(0, 0, 0))
display.print("Pico plot internal temperature vs CPU Clock")
display.print("")
display.set_color(color565(250, 250, 250), color565(0, 0, 0))
display.print("MicroPython:")
display.print(os.uname()[3])
display.print("")
display.print(os.uname()[4])
utime.sleep(3)

timReached = False
tim = Timer()
def TimerTick(timer):
    global led
    led.toggle()
    global timReached
    timReached = True
    
tim.init(freq=1, mode=Timer.PERIODIC, callback=TimerTick)
    
display.set_font(tt32)
#display.set_font(freesans20fixed)

display.set_color(color565(250, 250, 0), color565(0, 0,0))
display.erase()

drawFrame(TempFrame_X0, TempFrame_Y0, TempFrame_W, TempFrame_H)
drawFrame(FreqFrame_X0, FreqFrame_Y0, FreqFrame_W, FreqFrame_H)

utime.sleep(1)

#sampleTemp=[0]*sampleSize
sampleIndex=0
tempString = "0"
while True:
    if timReached:
        
        timReached = False
        
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
            
            display.fill_rectangle(FreqFrame_X0,
                                   FreqFrame_Y0,
                                   FreqFrame_W,
                                   FreqFrame_H,
                                   frameBGcolor)
        
        #plot temperature
        if tempValue >= tempValueLim:
            drawVLineUp(TempFrame_X0+sampleIndex,
                        TempFrame_Y1,
                        tempValueLim,
                        color565(250, 0, 0))
        else:
            drawVLineUp(TempFrame_X0+sampleIndex,
                        TempFrame_Y1,
                        tempValue,
                        color565(0, 0, 250))
            
        #plot CPU freq
        freqValue = machine.freq()
        print(freqValue)
        
        freqBar = freqValue/3000000  #freqBar in range 0~100
        drawVLineUp(FreqFrame_X0+sampleIndex,
                    FreqFrame_Y1,
                    freqBar,
                    color565(250, 250, 0))
        
        freqString=str(freqValue/1000000) + " (MHz)"
        display.set_color(color565(0, 0, 250), color565(0, 0, 0))
        display.set_pos(FreqPanel_X0, FreqPanel_Y0)
        display.print(freqString)
        
        sampleIndex = sampleIndex+1
        if(sampleIndex>=sampleSize):
            sampleIndex = 0
            
        
        
        #check if frequency changeinterval reached
        freqCnt = freqCnt-1
        if freqCnt == 0:
            freqCnt = FreqChangeInterval
            newFreq = freqSet[freqIdx]
            print(newFreq)
            machine.freq(newFreq)
            freqIdx = freqIdx + 1
            if freqIdx == len(freqSet):
                freqIdx = 0;
print("- bye-")
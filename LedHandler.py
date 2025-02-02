import json
from machine import Pin
from time import sleep_us, sleep

class LedHandler:
    ledSource = Pin(15, Pin.OUT)
    ledSourceState = 'LED State Unknown'
    
    def __init__(self):
        print("LED Handler Initialization")
        self.ledSource.value(1)
        
    @classmethod   
    def setLed(self,state):
        print("State: ", state)
        if state == "ON":
            self.ledSource.value(1)
            self.ledSourceState = 'LED is On'
        else:
            self.ledSource.value(0)
            self.ledSourceState = 'Led is Off'
            
    @classmethod   
    def getLedState(self):
        return self.ledSourceState
            
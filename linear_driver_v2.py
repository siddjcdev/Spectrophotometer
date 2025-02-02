import json
from machine import Pin
from time import sleep_us, sleep

step_pin = Pin(28, Pin.OUT)
dir_pin = Pin(27, Pin.OUT)
en_pin = Pin(18, Pin.OUT)

# Initialize pins
en_pin.value(0)  # Set en_pin to LOW
led_builtin = Pin(2, Pin.OUT)  # Assuming LED_BUILTIN is GPIO 2, adjust as needed

#Load JSON config files
with open("config.json") as f:
    config = json.load(f)
    
def move():
    pass  # Define any movement function if needed

def loop():
    go_to_red()
    init_to_base()

def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f)
        
def init_to_base():
    base_position = config["linear_position"]
    if base_position > 0:
        for x in range(base_position):
            linear_base_down()
            
        config["linear_position"] = base_position
        save_config()
        print("Saved base position to json.config file")
      
    else:
        print("The linear rail is already in base position")
        
    
def go_to_red():
    red_position = 10
    for x in range(red_position):
        linear_base_up()
        
    config["linear_position"] = red_position
    save_config()
    print("Saved red position to json.config file")
  
def linear_base_up():
    dir_pin.value(0)  # Set dir_pin to LOW for reverse direction
    for x in range(800):
        step_pin.value(1)
        led_builtin.value(1)  # Turn LED on
        sleep_us(500)
        step_pin.value(0)
        led_builtin.value(0)  # Turn LED off
        sleep_us(500)
    

    sleep(1)  # One second delay
    
def linear_base_down():
    dir_pin.value(1)  # Set dir_pin to HIGH for forward direction
    for x in range(800):
        step_pin.value(1)
        led_builtin.value(1)  # Turn LED on
        sleep_us(500)
        step_pin.value(0)
        led_builtin.value(0)  # Turn LED off
        sleep_us(500)

    sleep(1)  # One second delay

# Initialize pin modes
step_pin.init(Pin.OUT)
dir_pin.init(Pin.OUT)
en_pin.init(Pin.OUT)
led_builtin.init(Pin.OUT)

# Run the loop function
#while True:
loop()



import json
from machine import Pin
from time import sleep_us, sleep

class LinearHandler:
    step_pin = Pin(28, Pin.OUT)
    dir_pin = Pin(27, Pin.OUT)
    en_pin = Pin(18, Pin.OUT)

    # Initialize pins
    en_pin.value(0)  # Set en_pin to LOW
    led_builtin = Pin(2, Pin.OUT)  # Assuming LED_BUILTIN is GPIO 2, adjust as needed
    
     # Initialize pin modes
    step_pin.init(Pin.OUT)
    dir_pin.init(Pin.OUT)
    en_pin.init(Pin.OUT)
    led_builtin.init(Pin.OUT)
        
    #Load JSON config files
    config = {"last_linear_position":"0"}
    with open("config.json") as f:
        config = json.load(f)
    

    # Creates a dictionary with wavelength and linear positional data 
    wavelength_positions = { "red": 30, "orange": 32, "yellow": 32, "green": 34, "cyan": 36, "blue": 38, "indigo": 40, "violet": 42}

    def __init__(self):
        print("Linear handler initialization")
        self.__class__.init_to_base()

        
    @classmethod
    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f)
       
    @classmethod   
    def init_to_base(self):
        base_position = self.config["last_linear_position"]
        if base_position > 0:
            for x in range(base_position):
                self.linear_base_down()
                
            self.config["last_linear_position"] = 0
            self.save_config()
            print("Saved base position to json.config file")
          
        else:
            print("The linear rail is already in base position")
            

    @classmethod
    def scan_classic(self, color):
        #Resets position to base (starting) position
        self.init_to_base()

        selected_color_position = self.wavelength_positions[color]
        print("Wavelength positions:", self.wavelength_positions[color])
        #counter = 1
        for x in range(selected_color_position):
            #print("go_to_red::Counter: ", counter)
            self.linear_base_up()
            #counter += 1
        self.config["last_linear_position"] = selected_color_position
        #print("last_linear_position:", self.config["last_linear_position"])
        self.save_config()
        print("Saved selected color position to json.config file")
    
    @classmethod
    def scan(self, color):
        #Calculates new position based off of position last saved in json.config file
        last_position = self.config["last_linear_position"]
        selected_color_position = self.wavelength_positions[color]
        new_position = selected_color_position-last_position

        print("Wavelength positions:", self.wavelength_positions[color])
        if new_position < 0:
            
            #counter = 1
            for x in range(abs(new_position)):
                #print("go_to_red::Counter: ", counter)
                self.linear_base_down()
                #counter += 1
            
        elif new_position > 0:
            for x in range(new_position):
                self.linear_base_up()
        else:
            pass
       
        self.config["last_linear_position"] = selected_color_position
        #print("last_linear_position:", self.config["last_linear_position"])
        self.save_config()
        print("Saved selected color position to json.config file")
    

    @classmethod
    def linear_base_up(self):
        self.dir_pin.value(0)  # Set dir_pin to LOW for reverse direction
        for x in range(800):
            self.step_pin.value(1)
            self.led_builtin.value(1)  # Turn LED on
            sleep_us(500)
            self.step_pin.value(0)
            self.led_builtin.value(0)  # Turn LED off
            sleep_us(500)
        

        sleep(1)  # One second delay
    
    @classmethod
    def linear_base_down(self):
        self.dir_pin.value(1)  # Set dir_pin to HIGH for forward direction
        for x in range(800):
            self.step_pin.value(1)
            self.led_builtin.value(1)  # Turn LED on
            sleep_us(500)
            self.step_pin.value(0)
            self.led_builtin.value(0)  # Turn LED off
            sleep_us(500)

        sleep(1)  # One second delay



    



                



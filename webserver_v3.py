import utime
from RequestParser import RequestParser
import json
import uasyncio
import _thread
from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from LedHandler import LedHandler
from LinearHandler import LinearHandler
import random

# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')

async def handle_request(reader, writer):
    try:
        raw_request = await reader.read(2048)

        request = RequestParser(raw_request)

        response_builder = ResponseBuilder()
        print("Request.post_data:")
        print(request.post_data)
        # filter out api request
        if request.url_match("/api"):
            action = request.get_action()
            print("action:")
            print(action)
            if action == 'getLed':
                # ajax request for potentiometer data
                # used in simple test
                led_value = LedHandler.getLedState()
                # send back reading as simple text
                response_builder.set_body(led_value)
#             elif action == 'readData':
#                 # ajax request for data
#                 pot_value = IoHandler.get_pot_reading()
#                 temp_value = IoHandler.get_temp_reading()
#                 cled_states = {
#                     'blue': IoHandler.get_blue_led(),
#                     'yellow': IoHandler.get_yellow_led(),
#                     'green': IoHandler.get_green_led()
#                 }
#                 response_obj = {
#                     'status': 0,
#                     'pot_value': pot_value,
#                     'temp_value': temp_value,
#                     'cled_states': cled_states,
#                     'rgb_leds': IoHandler.rgb_led_colours
#                 }
#                 response_builder.set_body_from_dict(response_obj)
            elif action == 'setLed':
                # set RGB colour of first 4 neopixels
                # returns json object with led states
                # turn on requested coloured led
                # returns json object with led states
 
                led_state = request.data()['state']

                status = 'OK'

                LedHandler.setLed(led_state)
                response_obj = {
                    'status': 'The state (ON/OFF) of the LED changed.'
                }
                response_builder.set_body_from_dict(response_obj)
            elif action == 'scanColor':
                # set RGB colour of first 4 neopixels
                # returns json object with led states
                # turn on requested coloured led
                # returns json object with led states
 
                red_wavelength = request.data()['color']

                status = 'OK'

                LinearHandler.scan(red_wavelength)

                response_obj = {
                    'I0':'14000',
                    'I1':'2000',
                    'A':'7.23',
                    'C':'20.92'
                }
                response_builder.set_body_from_dict(response_obj)
            else:
                # unknown action
                response_builder.set_status(404)
            
        # try to serve static file
        else:
            response_builder.serve_static_file(request.url, "/index.html")

        response_builder.build_response()
        writer.write(response_builder.response)
        await writer.drain()
        await writer.wait_closed()

    except OSError as e:
        print('connection error ' + str(e.errno) + " " + str(e))
    
async def main():
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, "0.0.0.0", 80)
    uasyncio.create_task(server)

    # main async loop on first core
    # just pulse the red led
    counter = 0
    while True:
        counter += 1
        await uasyncio.sleep(0)

try:
    # start asyncio tasks on first core
    uasyncio.run(main())
finally:
    print("running finally block")
    uasyncio.new_event_loop()
    



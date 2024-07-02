from micropython import const
import network
import socket
from machine import Pin, Timer, I2C, ADC
import socket
import json
import gc
from time import sleep, sleep_ms
import random

# Access Point Parameters
SSID = const("Gas Detector_Controller")
PASSWORD = const("12345678")

# Setup LED to display server working status, if blinking then it's working
led = Pin(14, Pin.OUT)
tim = Timer(-1)

# Setup the solenoid valves 
valve1 = Pin(13, Pin.OUT)
valve2 = Pin(12, Pin.OUT)
valve1.off()
valve2.off()

# ADC pin to read the sensor
sensor1 = ADC(0)
sensor1_value = 0
sensor2_value = sensor1_value + 3

def read_sensors():
    global sensor1_value, sensor2_value
    # sensor1_value += 1
    # sensor2_value += 2
    
    # sensor1_value = int(sensor1.read()/100)
    sensor1_value = random.getrandbits(3) + 10
    sensor2_value = sensor1_value - random.getrandbits(2) 

    return sensor1_value, sensor2_value

def setup_access_point():
    '''
    set up the Access Point
    '''
    # global SSID, PASSWORD, display
    global SSID, PASSWORD
    station = network.WLAN(network.AP_IF)
    station.active(True)
    station.config(ssid=SSID, password=PASSWORD)

    while not station.active():
        pass

    print('Access Point Active!')
    # display.home()
    # display.write("AP Active!      ")
    print(station.ifconfig())
    # display.move(0, 1)
    # display.write(f"{station.ifconfig()[0]}")

    sleep(3)

def web_page():
    '''
    return the HTML page
    '''
    with open('index.html', 'r') as f:
        web_page = f.read()

    return web_page

def run_server():
    '''
    Hosting the web page and processing HTML requests
    '''
    # global display

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)  # Reduce the backlog to minimize memory usage
    print('Listening on', addr)

    # display.home()

    while True:
        tim.init(period=500, mode=Timer.PERIODIC, callback=lambda t: led.value(not led.value()))

        try:

            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            print(request, end='\n\n')

            if '/get_sensors' in request:
                sensor1, sensor2 = read_sensors()
                difference = abs(sensor1 - sensor2)
                response = json.dumps({
                    "sensor1": sensor1,
                    "sensor2": sensor2,
                    "difference": difference
                })
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)

                # display.move(0, 0)
                # display.write(f"S1 {sensor1}, S2 {sensor2}")

            elif '/set_valve?valve=1' in request:
                valve1.value(not valve1.value())
                response = 'Valve 1 toggled'
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)

                # display.move(0, 1)
                # display.write(f"V1: {valve1.value()}")

            elif '/set_valve?valve=2' in request:
                valve2.value(not valve2.value())
                response = 'Valve 2 toggled'
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)

                # display.move(7, 1)
                # display.write(f"V2: {valve2.value()}")

            else:
                response = web_page()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)

                led.off()
        
        except Exception as e:
            print(f"Error: {e}")
            tim.deinit()

        finally:
            conn.close()
            gc.collect()

    tim.deinit()

# sleep(3)
# setup_access_point()
# run_server()

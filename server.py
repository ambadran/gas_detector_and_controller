'''
Server Handling
'''

'''
Meant to run on the second Core of Pico for Optimal Performance
    - Host Web App (HTML file including the CSS and JAVASCRIPT)
    - Serve the HTML GET and POST requests
    - Updates internal variables to control Actuators through other Core
    - Updates the real-time Sensor values displayed on the Web App
'''
from micropython import const
from machine import Pin
import network
import socket
import json
from time import sleep, sleep_ms
# import random

class HTML_REQUEST:
    GET_WEB = 0
    GET_SENSORS = 1
    POST_SWITCHES = 2

class Server:
    # Access Point Parameters
    SSID = const("Smart Gas Monitoring System")
    PASSWORD = const("12345678")

    def __init__(self):
        '''
        initiate server
        '''
        self.led = Pin(14, Pin.OUT)
        self.led.off()

        # self.reset()
        self.init_access_point()
        self.init_socket()

        self.sensors_dict = {
                'sensor1': 1,
                'sensor2': 2,
                'pressureDiff': 4
                }

        self.actuators_dict = {
                'mode': 'manual',
                'valve1': 'close',
                'valve2': 'close'
               }

        self.IDENTIFY_HTML_REQUEST = {
                'GET /': HTML_REQUEST.GET_WEB,
                'GET /sensor_data': HTML_REQUEST.GET_SENSORS,
                'POST /mode': HTML_REQUEST.POST_SWITCHES,
                'POST /valve1': HTML_REQUEST.POST_SWITCHES,
                'POST /valve2': HTML_REQUEST.POST_SWITCHES,

                } 

        self.HANDLE_HTML_REQUEST = {
                HTML_REQUEST.GET_WEB: self.handle_get_web,
                HTML_REQUEST.GET_SENSORS: self.handle_get_sensor_data,
                HTML_REQUEST.POST_SWITCHES: self.handle_post_actuator_states
                }
 
    def reset(self):
        '''
        returns station object on reset.
        just deactivate and activate again 
        '''
        self.station = network.WLAN(network.AP_IF)
        try:
            self.station.config(ssid=self.SSID, password=self.PASSWORD)
        except OSError as e:
            print("caught the annoying AF: {e}")

        self.station.active(False)
        sleep(2)
        self.station.active(True)

    def init_access_point(self):
        '''
        set up the Access Point
        '''
        self.station = network.WLAN(network.AP_IF)
        try:
            self.station.config(ssid=self.SSID, password=self.PASSWORD)
        except OSError as e:
            print(f"caught the annoying AF: {e}")

        self.station.active(False)
        sleep(2)
        self.station.active(True)

        while not self.station.active():
            print(f"Station Initializing.. ", end=' \r')

        self.led.on()
        print('Access Point Active!')
        print(self.station.ifconfig())

    def init_socket(self):
        '''
        initiate socket connection
        '''
        try:
            # self.station.config(ssid=self.SSID, password=self.PASSWORD)
            sleep_ms(500)

            self.addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(self.addr)
            self.s.listen(1)  # Reduce the backlog to minimize memory usage
            print('Listening on', self.addr)
        except OSError as e:
            print(f"Error in init_socket: {e}")

    def wait_for_client(self):
        '''
        Await client to connect then return new socket object used to 
        communicate with the connected client. 
        This socket is distinct from the listening socket (s) 
        and is used for sending and receiving data with the specific client that connected.
        '''
        try:
            # self.station.config(ssid=self.SSID, password=self.PASSWORD)
            sleep_ms(500)

            self.client, addr = self.s.accept()
            print('Got a connection from %s' % str(addr))
        except Exception as e:
            print(f"Error in wait_for_client: {e}")
        # finally:
        #     self.client.close()

    def identify_html_request(self) -> HTML_REQUEST:
        '''
        return what HTML request is given. 
        Every HTML request must be mapped to a function that handles it.
        '''
        self.request = self.client.recv(1024).decode()
        
        tmp = self.request.split(' ')
        if len(tmp) > 1:
            tmp = tmp[0] + ' ' + tmp[1]

        return self.IDENTIFY_HTML_REQUEST.get(tmp, None)

    def handle_html_request(self, html_request: HTML_REQUEST):
        '''
        handles the identified html request
        '''
        try:
            if html_request is not None:
                print(f"Got Request:\n{self.request.split(' ')[:2]}")
                self.HANDLE_HTML_REQUEST[html_request]()
        
            else:
                self.handle_unkonwn_request()
                print(f"Got unkonwn Request:\n{self.request}")

        except Exception as e:
            print(f"Error in handle web get request: {e}")
            print(f"html request detected: {html_request}")
            print(f"Raw html request:\n{self.request}")

        finally:
            self.client.close()

    def handle_get_web(self):
        '''
        Handles GET_ACTUATORS_WEB HTML GET Request
        '''
        with open('index.html', 'r') as f:
            web_page = f.read()

        self.client.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
        self.client.sendall(web_page)

    def handle_get_sensor_data(self):
        '''

        '''
        response = json.dumps(self.sensors_dict)

        self.client.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
        self.client.send(response)

    def handle_post_actuator_states(self):
        '''

        '''
        length = int(self.request.split('Content-Length: ')[1].split('\r\n')[0])
        body = eval(self.client.recv(length).decode('utf-8'))

        self.actuators_dict.update(body) 

        response = 'HTTP/1.1 200 OK\r\n\r\n'
        self.client.send(response)

    def handle_unkonwn_request(self):
        '''
        Handles unknown request
        '''
        self.client.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
        self.client.send('HTTP/1.1 404 Not Found\r\n\r\nFile Not Found')



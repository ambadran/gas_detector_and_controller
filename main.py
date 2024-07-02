'''
Main Routine
'''
from gas_sensors import GasSensors
from valves import Valves
from control import AutoControl
from server import Server
from display import Display
from time import sleep

def main():
    # Input, Output, Monitoring Inits
    gas_sensors = GasSensors()
    valves = Valves()
    display = Display()
    server = Server()

    while True:

        ### Read Input Sensor values ###
        gas_sensors.read()
        server.sensors_dict.update(gas_sensors.values_dict)
        
        ### Host Server ###
        server.wait_for_client()
        server.handle_html_request(server.identify_html_request())

        ### Handle Output Valve values ###
        # Manual Mode
        if server.actuators_dict['mode'] == 'manual':
            valves.update_valuestobe_from_dict(server.actuators_dict)
            valves.execute_tobe()
        # Auto Mode
        elif server.actuators_dict['mode'] == 'auto':
            AutoControl(gas_sensors, valves)

        ### Show in OLED ###
        display.show_latest(server.actuators_dict, server.sensors_dict)

        ### Show in UART ###
        print(server.actuators_dict)
        print(server.sensors_dict)

        ### Toggle LED to show System is Operational ###
        server.led.value(not server.led.value())

        print('\n')

sleep(4)
main()

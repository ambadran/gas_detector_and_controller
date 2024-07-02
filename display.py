'''
Abstraction for OLED Display
'''
from machine import Pin, I2C
from sh1106 import SH1106_I2C

class Display:
    '''
    Object to abstract displaying the data
    '''
    def __init__(self):
        self.i2c = I2C(scl=Pin(5), sda=Pin(4))
        self.display = SH1106_I2C(128, 64, self.i2c)

        self.display.fill(0)
        self.display.show()

    def show_latest(self, actuators_dict, sensors_dict):
        '''
        Shows Every thing on the screen
        '''
        self.display.fill(0)
        self.display.text(f"{actuators_dict['mode']} Mode", 0, 0, 1)
        self.display.text(f"valve1: {actuators_dict['valve1']}", 0, 12, 1)
        self.display.text(f"valve2: {actuators_dict['valve2']}", 0, 24, 1)
        self.display.text(f"sensor1: {sensors_dict['sensor1']}", 0, 36, 1)
        self.display.text(f"sensor2: {sensors_dict['sensor2']}", 0, 48, 1)
        self.display.show()


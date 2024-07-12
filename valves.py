'''
Abstraction for Valves
'''
from machine import Pin

class Valves:
    '''
    Abstraction Object to control the Two valves
    Relay Controled Signal: HIGH/LOW
    '''
    V1_PIN_NUM = 13
    V2_PIN_NUM = 12

    TEXT_TO_VALUE = {'open': 1, 'close': 0}
    def __init__(self):
        self.v1 = Pin(self.V1_PIN_NUM, Pin.OUT)
        self.v2 = Pin(self.V2_PIN_NUM, Pin.OUT)
        
        self.v1_tobe = 0
        self.v2_tobe = 0

        self.execute_tobe()

    def execute_tobe(self):
        self.v1.value(self.v1_tobe)
        self.v2.value(self.v2_tobe)

    def off(self):
        self.v1.off()
        self.v2.off()

    def on(self):
        self.v1.on()
        self.v2.on()

    def update_valuestobe_from_dict(self, dict_):
        self.v1_tobe = self.TEXT_TO_VALUE[dict_['valve1']]
        self.v2_tobe = self.TEXT_TO_VALUE[dict_['valve2']]

    @property
    def states(self) -> tuple[int, int]:
        '''
        returns a tuple of the current states of the valves
        '''
        return (self.v1.value(), self.v2.value())


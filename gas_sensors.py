'''
Abstraction for the Gas Sensors
'''
from machine import ADC
from random import getrandbits

class PseudoADC:
    def __init__(self, ind):
        self.ind = ind
        self.latest_value = 0

    def read(self):
        self.latest_value = 995 + getrandbits(4)
        return self.latest_value

class GasSensors:
    '''
    Abstraction Object for the Gas Sensors
    Read as ADC value
    '''
    GAS_SENSOR1_PIN_NUM = 0
    GAS_SENSOR2_PIN_NUM = 1
    def __init__(self):
        # self.ad1 = ADC(0)
        # self.ad2 = ADC(1)

        self.ad1 = PseudoADC(0)
        self.ad2 = PseudoADC(1)

    def read(self):
        self.ad1.read()
        self.ad2.read()

    @property
    def difference(self):
        return self.ad2.latest_value - self.ad1.latest_value

    @property
    def values_dict(self) -> dict[str, str]:
        return {'sensor1': self.ad1.latest_value,
                'sensor2': self.ad2.latest_value,
                'pressureDiff': self.difference}




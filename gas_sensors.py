'''
Abstraction for the Gas Sensors
'''
from machine import ADC

class GasSensorUserInput:
    '''
    Abstraction Object to handle GasSensor as a user textual input
    '''
    def __init__(self):
        self.latest_value = 0

    def set_kpa(self, kpa_value: int):
        '''
        expects a kpa value from user
        '''
        if type(kpa_value) == int:
            self.latest_value = kpa_value
        else:
            raise ValueError("kpa_value MUST be an int")

class GasSensor:
    '''
    Abstraction Object to handle ONE gas sensor
    '''
    ADC_MAX_VALUE = 1024  # 10-bit ADC for ESP8266
    VOLTAGE_REF = 1.0  # Reference voltage for ESP8266 ADC, typically 1V

    # Sensor-specific conversion constants (replace with actual sensor values)
    SENSOR_MIN_VOLTAGE = 0.5  # Minimum sensor output voltage corresponding to 0 kPa
    SENSOR_MAX_VOLTAGE = 4.5  # Maximum sensor output voltage corresponding to max pressure
    MAX_PRESSURE_KPA = 1000  # Maximum pressure corresponding to SENSOR_MAX_VOLTAGE in kPa
    def __init__(self, pin):
        # self.adc = ADC(pin)
        self.latest_value = 0

    def adc_to_voltage(self, adc_value):
        '''
        Convert ADC reading to voltage. 
        '''
        return adc_value * self.VOLTAGE_REF / self.ADC_MAX_VALUE

    def voltage_to_pressure_kpa(self, voltage):
        ''' 
        Convert voltage to pressure in kPa. 
        '''
        if voltage < self.SENSOR_MIN_VOLTAGE:
            return 0  # Return 0 kPa if voltage is below the minimum threshold

        # Linear interpolation between min and max voltage
        return ((voltage - self.SENSOR_MIN_VOLTAGE) / (self.SENSOR_MAX_VOLTAGE - self.SENSOR_MIN_VOLTAGE)) * self.MAX_PRESSURE_KPA

    def read(self):
        '''
        converts ADC value to voltage to kpa
        '''
        self.latest_value = self.voltage_to_pressure_kpa(self.adc_to_voltage(self.latest_value))
        # self.latest_value = 995 + getrandbits(4)
        # self.latest_value = 0
        return self.latest_value

class GasSensors:
    '''
    Abstraction Object to handle BOTH of the gas sensors
    Read as ADC value
    '''
    GAS_SENSOR1_PIN_NUM = 0
    GAS_SENSOR2_PIN_NUM = 1

    def __init__(self):
        self.gas_sensor1 = GasSensor(self.GAS_SENSOR1_PIN_NUM)
        self.gas_sensor2 = GasSensorUserInput()

    def read(self, gas_sensor_kpa_value2: int):
        '''
        reads the gas sensor analogue value for the first and sets the second from user
        '''
        self.gas_sensor1.read()
        self.gas_sensor2.set_kpa(gas_sensor_kpa_value2)

    @property
    def difference(self):
        return self.gas_sensor2.latest_value - self.gas_sensor1.latest_value

    @property
    def values_dict(self) -> dict[str, int]:
        return {'sensor1': self.gas_sensor1.latest_value,
                'sensor2': self.gas_sensor2.latest_value,
                'pressureDiff': self.difference}




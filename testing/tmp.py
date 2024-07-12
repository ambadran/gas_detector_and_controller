from machine import ADC
import time

class ActualADC:
    '''
    Actual ADC class for reading from hardware pins.
    '''
    def _init_(self, pin):
        self.adc = ADC(pin)
        self.latest_value = 0

    def read(self):
        self.latest_value = self.adc.read()
        return self.latest_value

class GasSensors:
    '''
    Abstraction class for handling multiple gas sensors.
    Reads and computes the difference between two sensors.
    '''
    GAS_SENSOR1_PIN_NUM = 0  # ESP8266 typically uses A0 (pin 0) for ADC

    ADC_MAX_VALUE = 1024  # 10-bit ADC for ESP8266
    VOLTAGE_REF = 1.0  # Reference voltage for ESP8266 ADC, typically 1V

    # Sensor-specific conversion constants (replace with actual sensor values)
    SENSOR_MIN_VOLTAGE = 0.5  # Minimum sensor output voltage corresponding to 0 kPa
    SENSOR_MAX_VOLTAGE = 4.5  # Maximum sensor output voltage corresponding to max pressure
    MAX_PRESSURE_KPA = 1000  # Maximum pressure corresponding to SENSOR_MAX_VOLTAGE in kPa

    def _init_(self):
        # Initialize one actual ADC
        self.ad1 = ActualADC(self.GAS_SENSOR1_PIN_NUM)
        self.user_kpa = 0  # Placeholder for user-provided pressure value in kPa

    def read(self):
        # Read value from the actual sensor
        self.ad1.read()

        # Prompt user for the second sensor value in kPa
        self.user_kpa = self.get_user_input_kpa()

    def get_user_input_kpa(self):
        ''' Get user input for the second sensor reading in kPa. '''
        while True:
            try:
                value = float(input(f"Enter pressure value for the second sensor (0-{self.MAX_PRESSURE_KPA} kPa): "))
                if 0 <= value <= self.MAX_PRESSURE_KPA:
                    return value
                else:
                    print(f"Please enter a value between 0 and {self.MAX_PRESSURE_KPA} kPa.")
            except ValueError:
                print("Invalid input. Please enter a numeric value for pressure in kPa.")

    def pressure_kpa_to_voltage(self, kpa):
        ''' Convert pressure in kPa to voltage. '''
        if kpa <= 0:
            return self.SENSOR_MIN_VOLTAGE  # Voltage at 0 kPa
        return ((kpa / self.MAX_PRESSURE_KPA) * (self.SENSOR_MAX_VOLTAGE - self.SENSOR_MIN_VOLTAGE)) + self.SENSOR_MIN_VOLTAGE

    def voltage_to_adc(self, voltage):
        ''' Convert voltage to ADC value. '''
        return int(voltage * self.ADC_MAX_VALUE / self.VOLTAGE_REF)

    @property
    def difference(self):
        # Calculate the difference between sensor readings in ADC values
        sensor2_adc = self.voltage_to_adc(self.pressure_kpa_to_voltage(self.user_kpa))
        return sensor2_adc - self.ad1.latest_value

    def adc_to_voltage(self, adc_value):
        ''' Convert ADC reading to voltage. '''
        return adc_value * self.VOLTAGE_REF / self.ADC_MAX_VALUE

    def voltage_to_pressure_kpa(self, voltage):
        ''' Convert voltage to pressure in kPa. '''
        if voltage < self.SENSOR_MIN_VOLTAGE:
            return 0  # Return 0 kPa if voltage is below the minimum threshold
        # Linear interpolation between min and max voltage
        return ((voltage - self.SENSOR_MIN_VOLTAGE) / (self.SENSOR_MAX_VOLTAGE - self.SENSOR_MIN_VOLTAGE)) * self.MAX_PRESSURE_KPA

    @property
    def values_dict(self):
        # Convert ADC readings to voltage
        voltage1 = self.adc_to_voltage(self.ad1.latest_value)
        
        # Convert the user-provided kPa to corresponding voltage and ADC value
        voltage2 = self.pressure_kpa_to_voltage(self.user_kpa)
        sensor2_adc = self.voltage_to_adc(voltage2)

        # Convert voltage to pressure in kPa
        pressure1_kpa = self.voltage_to_pressure_kpa(voltage1)
        
        return {
            'sensor1': self.ad1.latest_value,
            'sensor2': sensor2_adc,
            'pressureDiff': self.difference,
            'sensor1_voltage': voltage1,
            'sensor2_voltage': voltage2,
            'sensor1_pressure_kpa': pressure1_kpa,
            'sensor2_pressure_kpa': self.user_kpa,  # Directly from user input
            'pressure_diff_kpa': self.user_kpa - pressure1_kpa
        }

# Example usage
if _name_ == "_main_":
    sensors = GasSensors()
    
    while True:
        sensors.read()
        values = sensors.values_dict

        # Print sensor readings in ADC value, voltage, and pressure (kPa)
        print(f"Sensor 1: {values['sensor1']}, Voltage: {values['sensor1_voltage']:.2f} V, Pressure: {values['sensor1_pressure_kpa']:.2f} kPa")
        print(f"Sensor 2: {values['sensor2']}, Voltage: {values['sensor2_voltage']:.2f} V, Pressure: {values['sensor2_pressure_kpa']:.2f} kPa")
        print(f"Pressure Difference: {values['pressure_diff_kpa']:.2f} kPa\n")
        
        time.sleep(5)  # Read every 5 seconds

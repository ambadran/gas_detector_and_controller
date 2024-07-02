'''
Implements the control Algorithm in Auto Mode
'''

def AutoControl(gas_sensors, valves):
    '''
    if gas pressure difference is high enough -> close both valves
    else -> Leave both valves Open
    '''
    GAS_PRESSURE_DIFFERNCE_THRESHOLD = 20

    if gas_sensors.difference > GAS_PRESSURE_DIFFERNCE_THRESHOLD:
        valves.off()

    else:
        valves.on()


#!/usr/bin/env python3

from adafruit_extended_bus import ExtendedI2C as I2C
import time
i2c=I2C(3)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan = AnalogIn(ads, ADS.P0)
#chan2 = AnalogIn(ads, ADS.P1)
#chan3 = AnalogIn(ads, ADS.P2)
#chan4 = AnalogIn(ads, ADS.P3)
#offsetVoltage = 2500
#sensitivity = 66

# Voltage Assumptions
# Full battery is 20.53V and low battery is roughly 17.50V
# Also reference table below for gain data
# 0.67 is adjustment to match multimeter voltage readings

# Current Assumptions
# VCC to ACS712 is 5V
# Output voltage at VIOUT of ACS712 is 2.5V with no load, so need to subtract 2.5V from voltage measurement
# Sensitity of sensor 185mV/A for 5A Sensor, 100mV/A for 20A Sensor and 66 mV/A for 30A Sensor --------I have the 30A sensor

#while True:
#    voltage = ((float(chan.voltage)/4.096) * 20) + 0.67
#    print('Voltage: ' + str(voltage))
#    print()
#    time.sleep(0.5)
    #adc_voltage = (float(chan2.voltage)/1024.0) * 5000
    #current = ((adc_voltage - offsetVoltage) / sensitivity)
    #print('Current: ' + str(chan2.voltage))
    #time.sleep(0.5)
# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

def main():
    print(battery_status())

def get_voltage():
    voltage = ((float(chan.voltage)/4.096) * 20) + 0.67
    return voltage

def battery_status():
    # Full 20.53V | Low 17.50V = 3.03V difference
    voltage = ((float(chan.voltage)/4.096) * 20) + 0.67
    volt_status = 20.53 - voltage
    battery_level = round(100 - ((volt_status/3.03) * 100), -1)
    return battery_level

if __name__ == '__main__':
    main()

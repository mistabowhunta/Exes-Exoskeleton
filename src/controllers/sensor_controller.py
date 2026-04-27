#!/usr/bin/env python3
import os
import time
import sys
import error_controller
from sensors import mqtt
sys.path.append("sensors")

logger = error_controller

def main(sensor):
    if sensor == 'activate_all_sensors':
        activate_all_sensors()

def activate_all_sensors():
    try:
        mqtt.main()
    except Exception as e:
        logger.one_variable('sensor_controller.py','activate_all_sensors()', "Error: ", str(e))
        wav_file = f'/home/bossman/audio/exes_data/error_unknown.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
        return False
    return True

def get_upper_left():
    try:
        ul = mqtt.get_upper_left()
    except Exception as e:
        logger.one_variable('sensor_controller.py','get_upper_left()', "Error: ", str(e))
        wav_file = f'/home/bossman/audio/exes_data/error_unknown.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
    return ul

def get_upper_right():
    try:
        ur = mqtt.get_upper_right()
    except Exception as e:
        logger.one_variable('sensor_controller.py','get_upper_right()', "Error: ", str(e))
        wav_file = f'/home/bossman/audio/exes_data/error_unknown.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
    return ur

def get_battery_status():
    try:
        bat = mqtt.get_battery_status()
    except Exception as e:
        logger.one_variable('sensor_controller.py','battery_status()', "Error: ", str(e))
        wav_file = f'/home/bossman/audio/exes_data/error_unknown.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
    return bat

if __name__ == '__main__':
    main()
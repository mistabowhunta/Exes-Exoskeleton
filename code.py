#!/usr/bin/env python3
import os
import ast
import sys
import time
import requests
import queue
import threading
import datetime
import paho.mqtt.client as mqtt

# Custom Modules
import error_controller
import audio_controller
import sensor_controller

sys.path.append("audio")
sys.path.append("sensors")
sys.path.append("servos")
sys.path.append("safe")

from audio import porky
from servos import servo
from servos import save_servos_pos 
from servos import save_servos_synced
from safe import load_env
from enum import Enum
from sensors import save_sensor_servo_cal_results

save_servo = save_servos_pos
save_cal = save_sensor_servo_cal_results

class Servos(Enum):
    UPPER_LEFT = 0
    UPPER_RIGHT = 1
    LOWER_LEFT = 2
    LOWER_RIGHT = 3

# Global variables
load_env.main()
key = os.environ["PV_ACCESS_KEY"]
wakewords = ['/usr/local/lib/python3.11/dist-packages/pvporcupine/resources/keyword_files/raspberry-pi/exes_en_raspberry-pi_v3_0_0.ppn']
path = '/usr/local/lib/python3.11/dist-packages/pvrhino/lib/common/Exes_en_raspberry-pi_v3_0_0.rhn'   

processed_command = False
logger = error_controller
audio = audio_controller
sensors = sensor_controller
BAT = False 
sensor_flag = False
thread_running = False

# MQTT GLOBAL VARIABLES
broker_address = "---.---.---.--"  
port = 1883  
topic_bat = [("sensors/bat", 1)]
topic_sensors = [("sensors/upper/right", 1), ("sensors/upper/left", 1)]

client = mqtt.Client(client_id="p4b")

# ---------------------------------------------------------
# THREAD-SAFE QUEUE WORKER (Replaces Multiprocessing)
# ---------------------------------------------------------
telemetry_queue = queue.Queue()

def telemetry_worker():
    """Continuously processes sensor telemetry from the queue."""
    while True:
        topic, data_payload, dict_synced_servos = telemetry_queue.get()
        
        try:
            if 'left' in topic:
                servo_move_UL(data_payload, dict_synced_servos['UL'])
            elif 'right' in topic:
                servo_move_UR(data_payload, dict_synced_servos['UR'])
        except Exception as e:
            logger.one_variable('code.py', 'telemetry_worker()', "Queue Error: ", str(e))
        finally:
            telemetry_queue.task_done()

# Start the worker thread globally so it is always ready
worker_thread = threading.Thread(target=telemetry_worker, daemon=True, name="TelemetryWorker")
worker_thread.start()

# ---------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------
def main(initialized=False):
    global processed_command
    _initialized = initialized
    logger.one_variable('code.py', 'main()', "_initialized: ", str(_initialized))
    
    if not _initialized:
        initialize()
        
    try:
        while True:
            if processed_command:
                processed_command = False
                main(initialized=True)
            else:
                start_wakeword_detection()
    except Exception as e:
        logger.one_variable('code.py', 'main()', "Error: ", str(e))
        audio.play_wav('error_unknown') 
        reset()

def command_controller(intent):
    global processed_command
    global sensor_flag
    global thread_running

    try:
        if intent == 'activateServos':
            audio.main('ack')
            dict_synced_servos = save_servos_synced.read_variable('UL_UR')
            if dict_synced_servos is None: 
                time.sleep(1)
                audio.play_wav('error_activating_servos') 
                logger.msg('code.py', 'command_controller', "INTENT: activate_servos - user needs to calibrate")
            else:
                thread_activate_sensors = threading.Thread(target=mqtt_connect_sensors_servos, name="Thread ID activate_sensors")
                thread_activate_sensors.start()
                thread_running = True
                
        elif intent == 'calibrate':
            audio.main('ack')
            if thread_running:
                time.sleep(1)
                audio.play_wav('error_unsync_servos')
            else:
                servo.calibrate()
                calculate_servo_sensor_sync() 
                
        elif intent == 'unactivateServos':
            audio.main('ack') 
            sensor_flag = True
            thread_running = False
            
            # Note: Multiprocessing termination removed here. 
            # We just wait for the MQTT thread to exit via sensor_flag.
            for thread in threading.enumerate():
                if thread.name == "Thread ID activate_sensors":
                    print(f"Terminating thread {thread.name}")
                    thread.join()
                    
            # Clear any leftover data in the queue so it doesn't fire later
            with telemetry_queue.mutex:
                telemetry_queue.queue.clear()
                
            logger.msg('code.py', 'command_controller()', "unsynced servos")
            
        elif intent == 'reset':
            audio.play_wav('power_restarting')
            logger.msg('code.py', 'command_controller()', "RESTART")
            servo.servo_reset() 
            reset()
            
        elif intent == 'powerOff':
            audio.play_wav('power_shutting_down')
            logger.msg('code.py', 'command_controller()', "SHUTDOWN")
            servo.servo_reset() 
            os.system('sudo shutdown now')
            
        # --- Servo Movements ---
        elif intent == 'moveUpperLeftUp': 
            move_degrees = '-90'
            if servo.servo_movement_validation(Servos.UPPER_LEFT, move_degrees):
                audio.main('ack')
                servo.main(Servos.UPPER_LEFT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveUpperRightUp': 
            move_degrees = '-90'
            if servo.servo_movement_validation(Servos.UPPER_RIGHT, move_degrees):
                audio.main('ack')
                servo.main(Servos.UPPER_RIGHT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveUpperLeftDown': 
            move_degrees = '180'
            if servo.servo_movement_validation(Servos.UPPER_LEFT, move_degrees):
                audio.main('ack')
                servo.main(Servos.UPPER_LEFT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveUpperRightDown': 
            move_degrees = '90'
            if servo.servo_movement_validation(Servos.UPPER_RIGHT, move_degrees):
                audio.main('ack')
                servo.main(Servos.UPPER_RIGHT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveLowerLeftUp': 
            move_degrees = '-90'
            if servo.servo_movement_validation(Servos.LOWER_LEFT, move_degrees):
                audio.main('ack')
                servo.main(Servos.LOWER_LEFT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveLowerRightUp': 
            move_degrees = '-90'
            if servo.servo_movement_validation(Servos.LOWER_RIGHT, move_degrees):
                audio.main('ack')
                servo.main(Servos.LOWER_RIGHT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveLowerLeftDown': 
            move_degrees = '90'
            if servo.servo_movement_validation(Servos.LOWER_LEFT, move_degrees):
                audio.main('ack')
                servo.main(Servos.LOWER_LEFT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'moveLowerRightDown': 
            move_degrees = '90'
            if servo.servo_movement_validation(Servos.LOWER_RIGHT, move_degrees):
                audio.main('ack')
                servo.main(Servos.LOWER_RIGHT, move_degrees) 
            else:
                audio.main('warning', 'warning_dislocate')
                
        elif intent == 'batteryStatus':
            get_battery_status()
            
        elif intent == 'help':
            audio.main('ack')
            
        elif intent == 'none':
            pass
            
    except Exception as e:
        logger.one_variable('code.py', 'command_controller()', "Error: ", str(e))
        audio.play_wav('error_unknown') 
        reset()

    processed_command = True
    main(initialized=True)

def initialize():
    try:
        audio.play_wav('initializing')
        time.sleep(2)
        while True:
            if check_internet_connection('initial_check'):
                break
        thread_wifi = threading.Thread(target=check_internet_connection, args=('continous_check',), daemon=True)
        thread_wifi.start()
        calculate_servo_sensor_sync()
        audio.play_wav('initializing_complete')
    except Exception as e:
        logger.one_variable('code.py', 'initialize()', "Error: ", str(e))
        audio.play_wav('error_initializing') 
        reset()
    start_wakeword_detection()
               
def start_wakeword_detection():
    global key
    try:
        porky.main(key, wakewords) 
    except Exception as e:
        logger.one_variable('code.py', 'start_wakeword_detection()', "Error: ", str(e))
        audio.play_wav('error_unknown') 
        reset()

def check_internet_connection(mode):
    if mode == 'initial_check':
        try:
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.one_variable('code.py', 'check_internet_connection()', "Error: ", str(e))
            return False
    else:
        while True:
            try:
                response = requests.get("https://www.google.com", timeout=5)
                if response.status_code != 200:
                    logger.msg('code.py', 'check_internet_connection()', "Lost Connection")
                    audio.play_wav('error_lost_wifi') 
                    reset()
                time.sleep(3)
            except Exception as e:
                logger.one_variable('code.py', 'check_internet_connection()', "Error: ", str(e))

def get_battery_status():
    global BAT
    client.connect(broker_address, port)
    client.subscribe(topic_bat, 1) 
    client.on_message = on_message_bat
    while not BAT:
        client.loop()
    BAT = False
    client.disconnect()

def mqtt_connect_sensors_servos():
    global sensor_flag
    dict_synced_servos = save_servos_synced.read_variable('UL_UR')
    client.user_data_set(dict_synced_servos)
    client.connect(broker_address, port)
    client.subscribe(topic_sensors, 0) 
    client.on_message = on_message_sensors
    while not sensor_flag:
        client.loop()
    client.disconnect()
    sensor_flag = False

# ---------------------------------------------------------
# MQTT CALLBACKS & SERVO MATH
# ---------------------------------------------------------
def on_message_bat(client, userdata, message):
    global BAT
    bat = message.payload.decode("utf-8")
    print('on_message_bat: ' + str(bat))
    if bat != '':
        audio.main('battery', str(bat))
        time.sleep(2)
        BAT = True

def on_message_sensors(client, userdata, message):
    if message.payload is None or message.payload == b"":
        return
    
    data = message.payload.decode("utf-8")
    # Toss the payload and the dictionary directly into the thread queue
    telemetry_queue.put((message.topic, data, userdata))

def servo_move_UL(data_payload, dictUL):
    match_UL = data_payload.split(" ")
    UL_send = float(match_UL[1].split(":")[1])
    differencesUL = {key: abs(float(key) - float(UL_send)*100) for key in dictUL}
    closest_key_UL = min(differencesUL, key=differencesUL.get)

    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")
    print(f"[{timestamp}] " + Servos.UPPER_LEFT.name + ': ' + str(dictUL[closest_key_UL]))
    logger.msg('servo.py', 'servo_move_UL()', Servos.UPPER_LEFT.name + ': ' + str(dictUL[closest_key_UL]))
    
    if servo.servo_movement_validation(Servos.UPPER_LEFT, dictUL[closest_key_UL]):
        # servo.main(Servos.UPPER_LEFT, dictUL[closest_key_UL])
        pass

def servo_move_UR(data_payload, dictUR):
    match_UR = data_payload.split(" ")
    UR_send = float(match_UR[1].split(":")[1])
    differencesUR = {key: abs(float(key) - float(UR_send)*100) for key in dictUR}
    closest_key_UR = min(differencesUR, key=differencesUR.get)

    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")
    print(f"[{timestamp}] " + Servos.UPPER_RIGHT.name + ': ' + str(dictUR[closest_key_UR]))
    logger.msg('servo.py', 'servo_move_UR()', Servos.UPPER_RIGHT.name + ': ' + str(dictUR[closest_key_UR]))
    
    if servo.servo_movement_validation(Servos.UPPER_RIGHT, dictUR[closest_key_UR]):
        # servo.main(Servos.UPPER_RIGHT, dictUR[closest_key_UR])
        pass

def calculate_servo_sensor_sync():
    logger.msg('servo.py', 'calculate_servo_sensor_sync()', "INSIDE calculate_servo_sensor_sync")
    data_list_UL_down = ast.literal_eval(save_cal.read_variable('result_UL_down'))
    data_list_UL_up = ast.literal_eval(save_cal.read_variable('result_UL_up'))
    data_list_UR_down = ast.literal_eval(save_cal.read_variable('result_UR_down'))
    data_list_UR_up = ast.literal_eval(save_cal.read_variable('result_UR_up'))
    
    yUL_down = data_list_UL_down[1]
    yUL_up = data_list_UL_up[1]
    yUR_down = data_list_UR_down[1]
    yUR_up = data_list_UR_up[1]
    
    y_axis_down_UL = yUL_down * 100
    y_axis_up_UL = yUL_up * 100
    y_axis_down_UR = yUR_down * 100
    y_axis_up_UR = yUR_up * 100

    # UL Math
    start = y_axis_up_UL
    stop = y_axis_down_UL
    num_values = 181 
    step_size = (stop - start) / (num_values - 1)
    evenly_spaced_values = [start + i * step_size for i in range(num_values)]
    servo_synced_UL = {evenly_spaced_values[x]: x for x in range(0, 181)}

    # UR Math
    start = y_axis_up_UR
    stop = y_axis_down_UR
    num_values = 181 
    step_size = (stop - start) / (num_values - 1)
    evenly_spaced_values = [start + i * step_size for i in range(num_values)]
    servo_synced_UR = {evenly_spaced_values[x]: x for x in range(0, 181)}

    combined_dicts = {'UL': servo_synced_UL, 'UR': servo_synced_UR}
    save_servos_synced.write_variable('UL_UR', combined_dicts)

def reset():
    time.sleep(2)
    os.system('sudo reboot now')

if __name__ == '__main__':
    main(initialized=False)
#!/usr/bin/env python3
# region VARIABLES
from adafruit_servokit import ServoKit
from adafruit_extended_bus import ExtendedI2C as I2C
import paho.mqtt.client as mqtt
from enum import Enum
import re
import sys
import ast
import time
import board
import busio
import threading
import statistics
sys.path.append("/home/bossman")
sys.path.append("safe")
sys.path.append("sensors")
sys.path.append("servos")
import error_controller
import audio_controller
from sensors import save_sensor_servo_cal_results
from servos import save_servos_pos
#import code
audio = audio_controller
save_cal = save_sensor_servo_cal_results
save_servo = save_servos_pos
#Fields/Variables
nbPCAServo=2 #set this to the number of active servos. Total is 16
#i2c=I2C(2) # using software i2c bus 2
i2c = busio.I2C(board.SCL, board.SDA)
pca = ServoKit(channels=16, i2c=i2c, frequency=60)
logger = error_controller
sensor_flag = False #Adafruit 9DOF sensor/upper/right & Adafruit 9DOF sensor/upper/left
LIST_TOTAL_SENSORS_UL=[]
LIST_TOTAL_SENSORS_UR=[]

#MQTT GLOBAL VARIABLES#
# Broker address, port, and topic
broker_address = "192.168.254.24"  # Replace with your broker address | test.mosquitto.org for testing
port = 1883  # Default MQTT port
topic_sensors= [("sensors/upper/right",1),("sensors/upper/left",1)]
# Create a client instance
client = mqtt.Client(client_id="p4b")

class Servos(Enum):
    UPPER_LEFT = 0
    UPPER_RIGHT = 1
    LOWER_LEFT = 2
    LOWER_RIGHT = 3

#Parameters
MIN_IMP  =[500, 600, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500]
MAX_IMP  =[1500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500]
MIN_ANG  =[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MAX_ANG  =[180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180]
#endregion VARIABLES

def main(servo: Servos, move_degrees):
    servo_pos= save_servo.read_variable(servo.name)
    logger.one_variable('servo.py','main()', 'current_deg: ', servo_pos + ' | requested_move_angle: ' + str(move_degrees))
    servo_pos = int(servo_pos)
    requested_move_angle = int(move_degrees)
    pca.servo[servo.value].set_pulse_width_range(MIN_IMP[servo.value] , MAX_IMP[servo.value])
    for x in range(int(servo_pos), requested_move_angle + 1, 1):
        logger.one_variable('servo.py','main()', 'diff be ', str(servo_pos) + ' | requested_move_angle: ' + str(move_degrees))
        pca.servo[servo.value].angle = requested_move_angle
        time.sleep(0.01)
    save_servo.write_variable(servo.name, str(requested_move_angle))
    #time.sleep(0.1)
    
def servo_movement_validation(servo: Servos, move_degrees):
    logger.msg('servo.py','servo_movement_validation()', "INSIDE VALIDATION")
    servo_pos= save_servo.read_variable(servo.name)
    if servo_pos == None:
        servo_pos = '90'
        save_servo.write_variable(servo.name, servo_pos)
        pca.servo[servo.value].set_pulse_width_range(MIN_IMP[servo.value] , MAX_IMP[servo.value])
        pca.servo[servo.value].angle = int(servo_pos)
    logger.one_variable('servo.py','servo_movement_validation()', 'servo_move_degrees: ', servo.name + ': ' + servo_pos)
    move_degrees = int(move_degrees)
    if move_degrees < 0 or move_degrees > 180:
        return False
    return True

def servo_reset(): #180 is down
    logger.msg('servo.py','servo_reset()', "INSIDE SERVO RESET")
    default_servo_pos='90'
    save_servo.write_variable(Servos.UPPER_LEFT.name, default_servo_pos)
    save_servo.write_variable(Servos.UPPER_RIGHT.name, default_servo_pos)
#   save_servo.write_variable(Servos.LOWER_LEFT.name, default_servo_pos)
#   save_servo.write_variable(Servos.LOWER_RIGHT.name, default_servo_pos)

    for x in range(nbPCAServo):
        pca.servo[x].set_pulse_width_range(MIN_IMP[x] , MAX_IMP[x])
        pca.servo[x].angle = int(default_servo_pos)
    time.sleep(0.5)

def calibrate():
    try:
        save_cal.clear_json_values() # reset calibration variables
        audio.play_wav('place_hands_sides')
        time.sleep(1)
        audio.main('calibration')
        activate_sensors(mode='calibrate')
        calculate_sensor_data_cal(mode='down')
        audio.play_wav('ok_confirmed')
        time.sleep(1)
        audio.play_wav('reach_stars')
        time.sleep(1)
        audio.main('calibration')
        activate_sensors(mode='calibrate')
        calculate_sensor_data_cal(mode='up')
        audio.play_wav('ok_confirmed')
        time.sleep(1)
        
        #TESTING
        print('result_UL_down: ' + str(save_cal.read_variable("result_UL_down")))
        print('result_UR_down: ' + str(save_cal.read_variable("result_UR_down")))
        print('result_UL_up: ' + str(save_cal.read_variable("result_UL_up")))
        print('result_UR_up: ' + str(save_cal.read_variable("result_UR_up")))
        num_char = save_sensor_servo_cal_results.validate_variables()
        if int(num_char) < 154:
            logger.msg('servo.py','calibrate()', "Validation failed recalibrating")
            audio.play_wav('error_calibration')
            time.sleep(1)
            calibrate()
        validate = [str(save_cal.read_variable("result_UL_down")), str(save_cal.read_variable("result_UR_down")), str(save_cal.read_variable("result_UL_up")), str(save_cal.read_variable("result_UR_up"))]
        for x in validate:
            if x == None:
                logger.msg('servo.py','calibrate()', "Validation failed recalibrating")
                audio.play_wav('error_calibration')
                time.sleep(1)
                calibrate()
        audio.play_wav('calibration_complete')
    except Exception as e:
        logger.one_variable('servo.py','calibrate()', "Error: ", str(e))
        audio.play_wav('error_calibration')

def activate_sensors(mode):
    global sensor_flag
    # Full 20V | Low 18.30 = 1.7V difference\
    # Subscribe to a topic
    

    if mode == 'calibrate':
        client.connect(broker_address, port)
        client.subscribe(topic_sensors, 1) #Use this multiple times to subscribe to multiple topics
        client.on_message = on_message_calibrate_sensors
        while not sensor_flag:
            client.loop()
        client.disconnect()
        sensor_flag = False

DICT_SENSORS=dict()
def on_message_calibrate_sensors(client, userdata, message):
    global sensor_flag
    global DICT_SENSORS
    global LIST_TOTAL_SENSORS_UL
    global LIST_TOTAL_SENSORS_UR
    ur=''
    ul=''
    match str(message.topic):
        case 'sensors/upper/right' :
            ur = message.payload.decode("utf-8")
        case 'sensors/upper/left' :
            ul = message.payload.decode("utf-8")

    if ur != '' and 'ur' not in DICT_SENSORS:
        DICT_SENSORS['ur'] = ur
    if ul != '' and 'ul' not in DICT_SENSORS:
        DICT_SENSORS['ul'] = ul
    if len(DICT_SENSORS) == 2:
        ur_value = re.findall(r"-?[0-9]+\.[0-9]+", DICT_SENSORS['ur'])
        UR_send = str([round(float(num),2) for num in ur_value])
        ul_value = re.findall(r"-?[0-9]+\.[0-9]+", DICT_SENSORS['ul'])
        UL_send = str([round(float(num),2) for num in ul_value])
        LIST_TOTAL_SENSORS_UL.append(UL_send)
        LIST_TOTAL_SENSORS_UR.append(UR_send)
        print('on_message_calibrate_sensors_ul: ' + UL_send)
        print('on_message_calibrate_sensors_ur: ' + UR_send)
        DICT_SENSORS.clear()
    if len(LIST_TOTAL_SENSORS_UL)==20 and len(LIST_TOTAL_SENSORS_UR)==20:
        print('DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        sensor_flag = True

def calculate_sensor_data_cal(mode):
    threadUL = threading.Thread(target=CALC_LIST_TOTAL_SENSORS_UL, args=(mode,))
    threadUR = threading.Thread(target=CALC_LIST_TOTAL_SENSORS_UR, args=(mode,))
    threadUL.start()
    threadUR.start()
    threadUL.join()
    threadUR.join()

#def calculate_sensor_data_live():
#    threadUL = threading.Thread(target=CALC_LIST_TOTAL_SENSORS_UL, args=(mode,))
#    threadUR = threading.Thread(target=CALC_LIST_TOTAL_SENSORS_UR, args=(mode,))
#    threadUL.start()
#    threadUR.start()
#    threadUL.join()
#    threadUR.join()

def CALC_LIST_TOTAL_SENSORS_UL(mode):
    global LIST_TOTAL_SENSORS_UL
    listQuaternionsUpperLeft = []
    print("CALC_LIST_TOTAL_SENSORS_UL started")
    for x in range(0, len(LIST_TOTAL_SENSORS_UL) - 1, 1):
        print(" " + str(x) + " Upper Left Rotation Vector Quaternion:")
        data_list_UL = ast.literal_eval(LIST_TOTAL_SENSORS_UL[x])
        xUL=data_list_UL[0]
        yUL=data_list_UL[1]
        zUL=data_list_UL[2]
        print("     X: %0.2f  Y: %0.2f Z: %0.2f" % (xUL, yUL, zUL))
        arrSensorCalUL = [xUL, yUL, zUL]
        listQuaternionsUpperLeft.append(arrSensorCalUL)
        
    #Average the middle 10 of the 20 count list. At the begginning and end of calibrations, users may move so want to get the most accurate data
    listX = []
    listY = []
    listZ = []
    arrResultUL=[]
    if len(listQuaternionsUpperLeft) > 0:
        for x in range(5, 15, 1):
            listX.append(listQuaternionsUpperLeft[x][0])
            listY.append(listQuaternionsUpperLeft[x][1])
            listZ.append(listQuaternionsUpperLeft[x][2])
        arrResultUL = [statistics.mode(listX), statistics.mode(listY), statistics.mode(listZ)]
    else:
        # Setting arrResultUL to default
        print("     Failed to obtain average of listQuaternionsUpperLeft, setting to default values")
        arrResultUL = [-0.36, 0.6, 0.17]
    print("CALC_LIST_TOTAL_SENSORS_UL completed: " + str(arrResultUL))
    LIST_TOTAL_SENSORS_UL.clear()
    time.sleep(.5)
    if mode == 'down':
        save_cal.write_variable('result_UL_down', str(arrResultUL))
    elif mode == 'up':
        save_cal.write_variable('result_UL_up', str(arrResultUL))
    time.sleep(.5)
def CALC_LIST_TOTAL_SENSORS_UR(mode):
    global LIST_TOTAL_SENSORS_UR
    listQuaternionsUpperRight = []
    print("CALC_LIST_TOTAL_SENSORS_UR started")
    for x in range(0, len(LIST_TOTAL_SENSORS_UR) - 1, 1):
        print(" " + str(x) + " Upper Right Rotation Vector Quaternion:")
        data_list_UR = ast.literal_eval(LIST_TOTAL_SENSORS_UR[x])
        xUR=data_list_UR[0]
        yUR=data_list_UR[1]
        zUR=data_list_UR[2]
        print("     X: %0.2f  Y: %0.2f Z: %0.2f" % (xUR, yUR, zUR))
        arrSensorCalUR = [xUR, yUR, zUR]
        listQuaternionsUpperRight.append(arrSensorCalUR)
        
    #Average the middle 10 of the 20 count list. At the begginning and end of calibrations, users may move so want to get the most accurate data
    listX = []
    listY = []
    listZ = []
    arrResultUR=[]
    if len(listQuaternionsUpperRight) > 0:
        for x in range(5, 15, 1):
            listX.append(listQuaternionsUpperRight[x][0])
            listY.append(listQuaternionsUpperRight[x][1])
            listZ.append(listQuaternionsUpperRight[x][2])
        arrResultUR = [statistics.mode(listX), statistics.mode(listY), statistics.mode(listZ)]
    else:
        # Setting arrResultUR to default
        print("     Failed to obtain average of listQuaternionsUpperRight, setting to default values")
        arrResultUR = [0.66, -0.2, -0.72]
    print("CALC_LIST_TOTAL_SENSORS_UR completed: " + str(arrResultUR))
    LIST_TOTAL_SENSORS_UR.clear()
    time.sleep(.5)
    if mode == 'down':
        save_cal.write_variable('result_UR_down', str(arrResultUR))
    elif mode == 'up':
        save_cal.write_variable('result_UR_up', str(arrResultUR))
    time.sleep(.5)

def unsync_servos():
    global sensor_flag
    sensor_flag=True

if __name__ == '__main__':
    main()

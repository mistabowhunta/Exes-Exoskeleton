import pigpio
import time
import board
import busio
import numpy as np
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.SCL, board.SDA)
bno = BNO08X_I2C(i2c)
gyro_sensitivity = 1
bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
bno.enable_feature(adafruit_bno08x.BNO_REPORT_GAME_ROTATION_VECTOR)

# Config/Variables
servoBackRight = 18 #using BCM meaning specify GPIO number not pin #
servoBackRightExt = 19 #using BCM meaning specify GPIO number not pin #
pwmBackRight = pigpio.pi()
pwmBackRight.set_mode(servoBackRight, pigpio.OUTPUT)
pwmBackRightExt = pigpio.pi()
pwmBackRightExt.set_mode(servoBackRightExt, pigpio.OUTPUT)
pwmBackRight.set_PWM_frequency( servoBackRight, 50 )
pwmBackRightExt.set_PWM_frequency( servoBackRightExt, 50 )
arrRotOrigin = np.array([0.0, 0.0, 0.0])
prev_game_quat_j = 0


# Reset
time.sleep( 1 )

# pwmBackRight
def down_to_middle():
    print("*** Resetting Servo:  down_to_middle ***")
    for x in range(1500, 1000, -5):
        print( "Deg: " + str(x) )
        pwmBackRight.set_servo_pulsewidth( servoBackRight, x )
        time.sleep( .01 )
        
def quarter_down_to_middle():
    print("*** Resetting Servo:  quarter_down_to_middle ***")
    for x in range(1250, 1000, -5):
        print( "Deg: " + str(x) )
        pwmBackRight.set_servo_pulsewidth( servoBackRight, x )
        time.sleep( .01 )
        
def quarter_up_to_middle():
    print("*** Resetting Servo:  quarter_up_to_middle ***")
    for x in range(750, 1000, 5):
        print( "Deg: " + str(x) )
        pwmBackRight.set_servo_pulsewidth( servoBackRight, x )
        time.sleep( .01 )
        
def up_to_middle():
    print("*** Resetting Servo:  up_to_middle ***")
    for x in range(500, 1000, 5):
        print( "Deg: " + str(x) )
        pwmBackRight.set_servo_pulsewidth( servoBackRight, x )
        time.sleep( .01 )

pwmBackRight.set_PWM_dutycycle( servoBackRight, 0 )
pwmBackRight.set_PWM_frequency( servoBackRight, 0 )
pwmBackRightExt.set_PWM_dutycycle( servoBackRightExt, 0 )
pwmBackRightExt.set_PWM_frequency( servoBackRightExt, 0 )
pwmBackRight.set_servo_pulsewidth( servoBackRight, 0 )
pwmBackRightExt.set_servo_pulsewidth( servoBackRightExt, 0 )
time.sleep(1)
print("*** Complete ***")
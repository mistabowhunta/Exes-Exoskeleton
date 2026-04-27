#!/usr/bin/env python3
import os
import time
import random
import error_controller

logger = error_controller

def main(category, wav_file=None):
    if category == 'greetings':
        greetings_wavs()
    elif category == 'calibration':
        calibration_wavs()
    elif category == 'ack':
        ack_wavs()
    elif category == 'warning':
        warning_wavs(wav_file)
    elif category == 'battery':
        battery_wavs(wav_file)

def greetings_wavs():
    list_greetings = ['greeting_hello', 'greetings_whats_up', 'greetings_yes']
    play_wav(random.choice(list_greetings))

def calibration_wavs():
    play_wav('calibrating_in')
    time.sleep(0.3)
    play_wav('count_three')
    time.sleep(0.3)
    play_wav('count_two')
    time.sleep(0.3)
    play_wav('count_one')
    time.sleep(0.3)

def ack_wavs():
    list_ack = ['ok_confirmed', 'ok_ok', 'ok_understood', 'ok_will_do']
    play_wav(random.choice(list_ack))

def warning_wavs(wav_file):
    if wav_file == None:
        play_wav('warning_warning')
    else:
        play_wav('warning_warning')
        time.sleep(0.3)
        play_wav(wav_file)

def battery_wavs(wav_file):
    play_wav('battery_battery_is')
    if wav_file == '0.0':
        play_wav('battery_zero_percent')
    elif wav_file == '10.0':
        play_wav('battery_ten_percent')
    elif wav_file == '20.0':
        play_wav('battery_twenty_percent')
    elif wav_file == '30.0':
        play_wav('battery_thirty_percent')
    elif wav_file == '40.0':
        play_wav('battery_forty_percent')
    elif wav_file == '50.0':
        play_wav('battery_fifty_percent')
    elif wav_file == '60.0':
        play_wav('battery_sixty_percent')
    elif wav_file == '70.0':
        play_wav('battery_seventy_percent')
    elif wav_file == '80.0':
        play_wav('battery_eighty_percent')
    elif wav_file == '90.0':
        play_wav('battery_ninety_percent')
    elif wav_file == '100.0':
        play_wav('battery_full_one_hundred_percent')

def play_wav(filename):
    try:
        wav_file = f'/home/bossman/audio/exes_data/{filename}.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
    except Exception as e:
        logger.one_variable('audio_controller.py','play_wav()', "Error: ", str(e))
        wav_file = f'/home/bossman/audio/exes_data/error_audio.wav'
        os.system(f'sudo /usr/bin/aplay {wav_file}')
if __name__ == '__main__':
    main()
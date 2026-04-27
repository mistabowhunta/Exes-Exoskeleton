#
# Copyright 2018-2023 Picovoice Inc.
#
# You may not use this file except in compliance with the license. A copy of the license is located in the "LICENSE"
# file accompanying this source.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

import argparse
import os
import sys
import struct
import wave
from datetime import datetime
import error_controller
import audio_controller
sys.path.append("audio")
from audio import rhino
import pvporcupine
from pvrecorder import PvRecorder
context_path='/usr/local/lib/python3.11/dist-packages/pvrhino/lib/common/Exes_en_raspberry-pi_v3_0_0.rhn'
audio = audio_controller
logger = error_controller

def main(access_key, keywords):
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=keywords,
            sensitivities=[0.9])
            
    except pvporcupine.PorcupineInvalidArgumentError as e:
        print("One or more arguments provided to Porcupine is invalid: Access Key, Keywords")
        raise e
    except pvporcupine.PorcupineActivationError as e:
        print("AccessKey activation error")
        raise e
    except pvporcupine.PorcupineActivationLimitError as e:
        print("AccessKey has reached it's temporary device limit")
        raise e
    except pvporcupine.PorcupineActivationRefusedError as e:
        print("AccessKey refused")
        raise e
    except pvporcupine.PorcupineActivationThrottledError as e:
        print("AccessKey has been throttled")
        raise e
    except pvporcupine.PorcupineError as e:
        print("Failed to initialize Porcupine")
        raise e

    list_keywords = list()
    for x in keywords:
        keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
        if len(keyword_phrase_part) > 6:
            list_keywords.append(' '.join(keyword_phrase_part[0:-6]))
        else:
            list_keywords.append(keyword_phrase_part[0])

    print('Porcupine version: %s' % porcupine.version)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=0) # args.audio_device_index
    recorder.start()
    print('Porky is listening ... (press Ctrl+C to exit)')

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:
                logger.msg('porky.py', 'main()', 'Wakework activated: Exes')
                audio.main('greetings')
                rhino.main(access_key, context_path) 
                break
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        porcupine.delete()

if __name__ == '__main__':
    main()
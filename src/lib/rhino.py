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

#import argparse
import os
import struct
import wave
import code
import pvrhino
import error_controller
import audio_controller
from pvrecorder import PvRecorder

logger = error_controller
audio = audio_controller

def main(access_key, context_path):

    try:
        rhino = pvrhino.create(
            access_key=access_key,
            context_path=context_path,
            sensitivity=0.7)
    except pvrhino.RhinoInvalidArgumentError as e:
        print("One or more arguments provided to Rhino is invalid: Access Key or Context Path")
        raise e
    except pvrhino.RhinoActivationError as e:
        print("AccessKey activation error")
        raise e
    except pvrhino.RhinoActivationLimitError as e:
        print("AccessKey has reached it's temporary device limit")
        raise e
    except pvrhino.RhinoActivationRefusedError as e:
        print("AccessKey refused")
        raise e
    except pvrhino.RhinoActivationThrottledError as e:
        print("AccessKey has been throttled")
        raise e
    except pvrhino.RhinoError as e:
        print("Failed to initialize Rhino")
        raise e

    print('Rhino version: %s' % rhino.version)
    print('Context info: %s' % rhino.context_info)

    recorder = PvRecorder(
        frame_length=rhino.frame_length,
        device_index=0) #args.audio_device_index
    recorder.start()

    print('Using device: %s' % recorder.selected_device)
    print('Rhino is listening ... Press Ctrl+C to exit.\n')

    try:
        while True:
            pcm = recorder.read()
            is_finalized = rhino.process(pcm)
            if is_finalized:
                inference = rhino.get_inference()
                if inference.is_understood:
                    logger.one_variable('rhino.py', 'main()', 'Intent detected: ', inference.intent)
                    code.command_controller(inference.intent)
                    break
                else:
                    logger.msg('rhino.py', 'main()', 'Intent not understood')
                    audio.play_wav('ok_dont_understand')
                    code.command_controller('none')
                    break
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        rhino.delete()

if __name__ == '__main__':
    main()
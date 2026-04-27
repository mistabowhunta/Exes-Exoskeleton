import pvporcupine
import os

my_access_key=''

try:
    my_access_key=os.environ["PV_ACCESS_KEY"]
except KeyError:
    print("Environment key not set")
    exit(1)

def get_next_audio_frame():
    pass


handle = pvporcupine.create(access_key=os.environ["PV_ACCESS_KEY"],keywords=['x-e-s'])
#handle.delete()
while True:
    keyword_index = handle.process('/home/bossman/audio/data/test.wav')
    if keyword_index >= 0:
        print('Its working!!!!')
        pass
    else:
        print('No detection')
        
print('Handle deleted successfully')
handle.delete()
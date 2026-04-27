import socket
import time
#s1 = socket.socket()
#s2 = socket.socket()
#s3 = socket.socket()
#s4 = socket.socket()
s5 = socket.socket()

data5 = ()

def main(sensor):
    if sensor == 'battery_status':
        battery_status()
    #elif sensor == 'calibration':
    #    calibration_wavs()

    try:
        #pico_address_1 = ('192.168.10.143', 5007)
        #pico_address_2 = ('192.168.10.109', 5007)

        pico_address_5 = ('192.168.10.215', 5007)
        #s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s1.connect(pico_address_1)
        #s2.connect(pico_address_2)

        s5.connect(pico_address_5)
        #data5 = s5.recv(17)

        while True:
        #    #data1 = s1.recv(1024)
        #    #data2 = s2.recv(1024)

            data5 = s5.recv(17)
        ##    #print(f"Pico1: {data1}")
        ##    #print(f"Pico2: {data2}")
        ##    print(f"Pico5: {data5}")
        #    time.sleep(.1)
        ##    # s.sendall(b"Hello, world")
    except Exception as e:
        print("The error is: ", e)
        s5.close()
    #finally:
    #    print('Closing sockets')
        #s1.close()
        #s2.close()

        #s5.close()

def battery_status():
    try:
        results = data5
    except Exception as e:
        print("The error is: ", e)
    #finally:
        #print('Closing sockets')
        #s5.close()
    results_formatted = str(results.recv(17)[-4:])
    return results_formatted

if __name__ == '__main__':
    main('sensor')

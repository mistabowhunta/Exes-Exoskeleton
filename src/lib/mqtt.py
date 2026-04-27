import paho.mqtt.client as mqtt
import time
ur = ''
ul = ''
bat = ''


# Define callback functions for message events
def on_message(client, userdata, message):
    if message.payload.decode("utf-8") == '':
        return
    global ur
    global ul
    global bat

    match str(message.topic):
        case 'sensors/upper/right' :
            ur = message.payload.decode("utf-8")
        case 'sensors/upper/left' :
            ul = message.payload.decode("utf-8")
        case 'sensors/bat' :
            bat = message.payload.decode("utf-8")

def on_connect(client, userdata, flags, rc):
    flags_on_connect = flags

def on_disconnect(client, userdata, message):
    client = mqtt.Client(client_id="p4b")
    client.disconnect()

def get_upper_right():
    return ur

def get_upper_left():
    return ul

def get_battery_status():
    return bat

def main():

    # Broker address, port, and topic
    broker_address = "---.---.---.--"  # Replace with your broker address | test.mosquitto.org for testing
    port = 1883  # Default MQTT port
    topic= [("sensors/upper/right",1),("sensors/upper/left",1),("sensors/bat",1)]

    # Create a client instance
    client = mqtt.Client(client_id="p4b")

    # Connect to the broker
    client.connect(broker_address, port)

    # Subscribe to a topic
    client.subscribe(topic, 1) #Use this multiple times to subscribe to multiple topics

    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Start the network loop
    client.loop_start()


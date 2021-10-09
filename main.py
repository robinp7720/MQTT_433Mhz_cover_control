import paho.mqtt.client as mqtt
from datetime import datetime
from datetime import timedelta
from time import sleep
import sys
import RPi.GPIO as GPIO
from queue import Queue
from threading import Thread

TRANSMIT_PIN = 24

OPENING_TIME = 44

MQTT_SERVER = "prometheus"
MQTT_PATH = "test_channel"
OBJECT_ID = 'robin_projector_screen'
NAME = 'Projector'
UNIQUE_ID = "robin_projector_screen"

DISCOVERY_PAYLOAD =  '{{ "~": "homeassistant/cover/{}", "name": "{}", "unique_id": "{}", "cmd_t": "~/set", "stat_t": "~/state" }}'.format(OBJECT_ID, NAME, UNIQUE_ID)

PROJECTOR_OPEN = 1
PROJECTOR_CLOSED = 2
PROJECTOR_OPENING = 3
PROJECTOR_CLOSING = 4

projector_state = PROJECTOR_CLOSED


def load_signal(file):
    file = open(file)
    signal = []
    for i in file:
        signal.append(int(i))
    return signal


LOWER_SIGNAL = load_signal('/home/pi/screen_controller/signal_sequences/LOWER')
RAISE_SIGNAL = load_signal('/home/pi/screen_controller/signal_sequences/RAISE')
STOP_SIGNAL = load_signal('/home/pi/screen_controller/signal_sequences/STOP')

action_q = Queue()


def transmit_signal(signal):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRANSMIT_PIN, GPIO.OUT)
    current = 1

    for i in signal:
        sleep(i * 0.000001)
        #sleep(i * 0.00000075)
        GPIO.output(TRANSMIT_PIN, current)
        current = (current + 1) % 2
    GPIO.cleanup()


def lower_screen():
    transmit_signal(LOWER_SIGNAL)


def raise_screen():
    transmit_signal(RAISE_SIGNAL)


def stop_screen():
    transmit_signal(STOP_SIGNAL)


def set_state(mqtt_client, state):
    global projector_state
    projector_state = state
    update_state(mqtt_client)


def update_state(mqtt_client):
    global projector_state
    if projector_state == PROJECTOR_OPEN:
        publish_state(mqtt_client, 'open')

    if projector_state == PROJECTOR_CLOSED:
        publish_state(mqtt_client, 'closed')

    if projector_state == PROJECTOR_OPENING:
        publish_state(mqtt_client, 'opening')

    if projector_state == PROJECTOR_CLOSING:
        publish_state(mqtt_client, 'closing')


def open_screen(mqtt_client):
    global projector_state
    if projector_state != PROJECTOR_CLOSED:
        return

    set_state(mqtt_client, PROJECTOR_OPENING)

    lower_screen()
    sleep(OPENING_TIME)
    stop_screen()

    set_state(mqtt_client, PROJECTOR_OPEN)


def close_screen(mqtt_client):
    global projector_state

    set_state(mqtt_client, PROJECTOR_CLOSING)

    raise_screen()
    sleep(OPENING_TIME)

    set_state(mqtt_client, PROJECTOR_CLOSED)


# The callback for when the client receives a connect response from the server.
def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    mqtt_client.subscribe('homeassistant/cover/availability')
    mqtt_client.subscribe('homeassistant/cover/{}/set'.format(OBJECT_ID))
    mqtt_client.subscribe('homeassistant/cover/{}/state'.format(OBJECT_ID))


def publish_state(mqtt_client, state):
    global OBJECT_ID

    mqtt_client.publish('homeassistant/cover/{}/state'.format(OBJECT_ID), state)


def receive_set_state(payload):
    action_q.put(payload)


# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    if msg.topic == 'homeassistant/cover/{}/set'.format(OBJECT_ID):
        receive_set_state(msg.payload.decode('utf-8'))
        return

    print(msg.topic + " " + str(msg.payload))


def action_thread_consumer(action_q, mqtt_client):
    while True:
        data = action_q.get()

        if data == 'OPEN':
            open_screen(mqtt_client)
            continue

        if data == 'CLOSE':
            close_screen(mqtt_client)
            continue


        print(data)


if __name__ == '__main__':
    client = mqtt.Client()

    action_thread = Thread(target=action_thread_consumer, args=(action_q, client, ))
    action_thread.start()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60)
    client.publish('homeassistant/cover/{}/config'.format(OBJECT_ID), DISCOVERY_PAYLOAD)

    update_state(client)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

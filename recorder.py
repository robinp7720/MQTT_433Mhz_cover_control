from datetime import datetime
from datetime import timedelta
from time import sleep

import RPi.GPIO as GPIO

RECEIVE_PIN = 23
TRANSMIT_PIN = 24

RECIEVED = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(RECEIVE_PIN, GPIO.IN)
GPIO.setup(TRANSMIT_PIN, GPIO.OUT)

lastTime = datetime.now()
last = 0

while True:
    current = GPIO.input(RECEIVE_PIN)
    currentTime = datetime.now()

    if(current == last):
        if (currentTime - lastTime > timedelta(seconds=2)):
            break
        continue

    delta = (currentTime - lastTime).microseconds

    RECIEVED.append((delta, current))

    lastTime = currentTime
    last = current

print("DONE")

print("WRITING TO FILE")

file = open("output", "a")

for i in RECIEVED:
    print(i)
    file.write(str(i[0]) + '\n')

GPIO.cleanup()

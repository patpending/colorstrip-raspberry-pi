#!/usr/bin/python3
import paho.mqtt.client as mqtt

import time
from neopixel import *
import argparse
import signal
import sys
import json
import colorsys
MQTT_BROKER = "192.168.0.6"
MQTT_PORT = 1883
MQTT_TOPIC = "lights/ledstrip1/colour"
# The Neopixel stuff
# LED strip configuration:
LED_COUNT = 100  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53
stripColor = Color(0,0,0)

LED_STRIP = ws.WS2811_STRIP_BRG  # Strip type and colour ordering

def signal_handler(signal, frame):
    # colorWipe(strip, Color(0, 0, 0))
    sys.exit(0)


def opt_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    if args.c:
        signal.signal(signal.SIGINT, signal_handler)


# Define functions which animate LEDs in various ways.
def colorWipe(strip,color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
    #time.sleep(wait_ms / 1000.0)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(MQTT_TOPIC)

def hsv2rgb(h,s,v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global stripColor
    node_data = str(msg.payload)
    trimmed_data = node_data[2:-1]
    print(trimmed_data)
    if trimmed_data.startswith('{') and trimmed_data.endswith('}'):
        data = json.loads(trimmed_data)
        hue = data['hue']
        saturation = data['saturation']
        brightness = data['brightness']
        colorTuple = hsv2rgb(((1 / 360) * hue), saturation, brightness)
        stripColor = Color(colorTuple[0],colorTuple[1],colorTuple[2])
        colorWipe(strip, stripColor)
    if trimmed_data == "true":
        colorWipe(strip, stripColor)
    if trimmed_data == "false":
        colorWipe(strip, Color(0,0,0))


# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    # Process arguments
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()


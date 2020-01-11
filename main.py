from bmp180 import BMP180
from thingspeak import Thingspeak
from machine import I2C, Pin, Signal
import network
import time

# global variables contained in a seperate config.py file
import config

# create network instance
wlan = network.WLAN(network.STA_IF)

# define outputs
# esp LED
ACTIVE_LED_PIN = Pin(16, Pin.OUT)
ACTIVE_LED = Signal(ACTIVE_LED_PIN, invert=True)

# create bmp180 instance
bus = I2C(scl=Pin(14), sda=Pin(12), freq=100000)
bmp180 = BMP180(bus)

# create thingspeak instance
thingspeak = Thingspeak()

if __name__ == "__main__":

    # delay to allow network to connect
    time.sleep(10)
    wlan.connect()

    if wlan.isconnected():
        wlan.ifconfig()

    print("Running main routine")
    while True:
        # send pressure readings
        if not wlan.isconnected():
            wlan.connect()
        ACTIVE_LED.on()
        pressure = bmp180.get_pressure() / 100
        temperature = bmp180.get_temperature() / 10
        thingspeak.write_channel_field([("field1", pressure), ("field2", temperature)])

        # disconnect wifi
        wlan.disconnect()
        ACTIVE_LED.off()

        # sleep for 4 minutes
        time.sleep(30)

from bmp180 import BMP180
from thingspeak import Thingspeak
from machine import I2C, Pin, Signal
import network
import time

# global variables contained in a seperate config.py file
import config

SSID = config.SSID
SSID_PASSWORD = config.SSID_PASSWORD

# create network instance
wlan = network.WLAN(network.STA_IF)

# define outputs
# esp LED
WIFI_LED_PIN = Pin(16, Pin.OUT)
wifi_LED = Signal(WIFI_LED_PIN, invert=True)

# create bmp180 instance
bus = I2C(scl=Pin(14), sda=Pin(12), freq=100000)
bmp180 = BMP180(bus)

# create thingspeak instance
thingspeak = Thingspeak()


def wifi_connected():
    if not wlan.isconnected():
        wifi_LED.off()
        return False
    else:
        return True


def wifi_connect():
    print("turning WiFi on...")
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...", SSID)
        wlan.connect(SSID, SSID_PASSWORD)
        while not wlan.isconnected():
            pass
    print("connected to network", SSID)
    print("network config:", wlan.ifconfig())
    wifi_LED.on()
    return wlan


if __name__ == "__main__":
    # connect to the network
    wifi_connect()

    print("Running main routine")
    while True:
        if not wlan.isconnected():
            wifi_connect()
        pressure = bmp180.get_pressure() / 100
        temperature = bmp180.get_temperature() / 10
        thingspeak.write_channel_field("field1", pressure)
        time.sleep(1 * 60)
        thingspeak.write_channel_field("field2", temperature)
        time.sleep(4 * 60)

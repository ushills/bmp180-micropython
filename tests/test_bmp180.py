import pytest
from unittest.mock import Mock
from unittest.mock import MagicMock
import struct as ustruct
import sys


# mock Signal and Pin from Micropython as not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine

mock_I2C = MagicMock()
sys.modules["I2C"] = mock_I2C


from bmp180 import BMP180

# mock BMP180 __init__ method
fake_BMP180 = Mock()
fake_bus = Mock()
BMP180.__init__(fake_BMP180, fake_bus)

# mock BPM180.read_calibration_coefficients method
def fake_read_calibration_coefficients():
    BMP180._AC1 = 408
    BMP180._AC2 = -72
    BMP180._AC3 = -14383
    BMP180._AC4 = 32742
    BMP180._AC5 = 32757
    BMP180._AC6 = 23153
    BMP180._B1 = 6190
    BMP180._B2 = 4
    BMP180._MB = -32768
    BMP180._MC = -8711
    BMP180._MD = 2868


BMP180.read_calibration_coefficients = Mock(
    side_effect=fake_read_calibration_coefficients
)

# mock get_UT method
BMP180.get_UT = Mock(return_value=27898)

# mock get_UP method
BMP180.get_UP = Mock(return_value=23843)

# create bmp180 instance
bmp180 = BMP180(fake_bus)


def test_calibration_coefficients():
    assert bmp180.calibration_coefficients() == [
        408,
        -72,
        -14383,
        32742,
        32757,
        23153,
        6190,
        4,
        -32768,
        -8711,
        2868,
    ]


def test_get_UT():
    assert bmp180.get_UT() == 27898


def test_get_UP():
    assert bmp180.get_UP() == 23843


def test_get_temperature():
    assert bmp180.get_temperature() == 150


def test_get_pressure():
    assert bmp180.get_pressure() == 69962


def test_adjusted_pressure():
    assert bmp180.adjusted_pressure() == 69962


def test_adjusted_pressure_at_100m_at_15deg():
    bmp180.location_altitude = 100
    assert bmp180.adjusted_pressure() == 70797


# from thingspeak import Thingspeak

# thingspeak = Thingspeak()


# def test_create_url():
#     API_KEY = "9BLK4Y0CT76ICMG0"
#     field = "field"
#     value = 0


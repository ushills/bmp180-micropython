from machine import I2C, Pin
from struct import unpack
import time

# BMP180 class
class BMP180:
    def __init__(self, i2c_bus):

        self._bmp_address = 119  # address of BMP180

        # construct an I2C bus
        self._bmp_i2c = i2c_bus

        # read in calibration coefficients
        self.read_calibration_coefficients()

        # default settings can to be adjusted by user
        self.oversampling_setting = 0
        self.location_altitude = 0

    def read_calibration_coefficients(self):
        _bmp_address = self._bmp_address
        # read in calibration coefficients
        self._AC1 = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xAA, 2))[0]
        self._AC2 = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xAC, 2))[0]
        self._AC3 = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xAE, 2))[0]
        self._AC4 = unpack(">H", self._bmp_i2c.readfrom_mem(_bmp_address, 0xB0, 2))[0]
        self._AC5 = unpack(">H", self._bmp_i2c.readfrom_mem(_bmp_address, 0xB2, 2))[0]
        self._AC6 = unpack(">H", self._bmp_i2c.readfrom_mem(_bmp_address, 0xB4, 2))[0]
        self._B1 = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xB6, 2))[0]
        self._B2 = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xB8, 2))[0]
        self._MB = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xBA, 2))[0]
        self._MC = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xBC, 2))[0]
        self._MD = unpack(">h", self._bmp_i2c.readfrom_mem(_bmp_address, 0xBE, 2))[0]


    def calibration_coefficients(self):
        return [
            self._AC1,
            self._AC2,
            self._AC3,
            self._AC4,
            self._AC5,
            self._AC6,
            self._B1,
            self._B2,
            self._MB,
            self._MC,
            self._MD,
        ]

    def get_UT(self):
        # read uncompensated temperature
        # write 0x2E into reg 0xF4 and wait 5ms
        self._bmp_i2c.writeto_mem(self._bmp_address, 0xF4, bytearray([0x2E]))
        time.sleep_ms(5)
        UT_bytes = self._bmp_i2c.readfrom_mem(self._bmp_address, 0xF6, 2)
        UT = unpack(">h", UT_bytes)[0]
        return UT

    def get_UP(self):
        # read uncompensated pressure
        # write 0x34+(oss<<6) into 0xF4 and wait 5ms
        self._bmp_i2c.writeto_mem(
            self._bmp_address,
            0xF4,
            bytearray([0x34 + (self.oversampling_setting << 6)]),
        )
        delays = (5, 8, 14, 26)
        time.sleep_ms(delays[self.oversampling_setting])
        # b'\00' is required to add one blank byte to unpack a Long
        raw_UP = unpack(">L", b'\00' + self._bmp_i2c.readfrom_mem(self._bmp_address, 0xF6, 3))[0]
        UP = raw_UP >> (8 - self.oversampling_setting)
        return UP

    def get_B5(self):
        UT = self.get_UT()
        X1 = int((UT - self._AC6) * self._AC5) >> 15
        X2 = int((self._MC << 11) / (X1 + self._MD))
        B5 = X1 + X2
        return B5

    def get_temperature(self):
        B5 = self.get_B5()
        temperature = int((B5 + 8) >> 4)
        return temperature

    def get_pressure(self):
        B5 = self.get_B5()
        UP = self.get_UP()
        # calculate pressure
        B6 = B5 - 4000
        X1 = int((self._B2 * ((B6 * B6) >> 12)) >> 11)
        X2 = int((self._AC2 * B6) >> 11)
        X3 = int(X1 + X2)
        B3 = int((((self._AC1 * 4 + X3) << self.oversampling_setting) + 2) >> 2)
        X1 = int((self._AC3 * B6) >> 13)
        X2 = int((self._B1 * ((B6 * B6) >> 12)) >> 16)
        X3 = int(((X1 + X2) + 2) >> 2)
        B4 = int(abs(self._AC4) * (X3 + 32768) >> 15)
        B7 = abs(int((abs(UP) - B3) * (50000 >> self.oversampling_setting)))
        if B7 < 0x80000000:
            p = int((B7 << 1) / B4)
        else:
            p = int((B7 / B4) << 1)
        X1 = int((p >> 8) * (p >> 8))
        X1 = int((X1 * 3038) >> 16)
        X2 = int((-7357 * p) >> 16)
        pressure = int(p + ((X1 + X2 + 3791) >> 4))
        return pressure

    def adjusted_pressure(self):
        p = self.get_pressure()
        p0 = int(p / ((1 - (self.location_altitude / 44330)) ** 5.255))
        return p0

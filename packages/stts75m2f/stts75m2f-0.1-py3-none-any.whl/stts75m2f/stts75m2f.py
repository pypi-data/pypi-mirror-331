import smbus2

class STTS75M2F:
    def __init__(self, address=0x48, bus_number=1):
        self.address = address
        self.bus = smbus2.SMBus(bus_number)

    def read_temperature(self):
        data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
        temp = (data[0] << 8 | data[1]) >> 4
        temp_c = temp * 0.0625
        return temp_c


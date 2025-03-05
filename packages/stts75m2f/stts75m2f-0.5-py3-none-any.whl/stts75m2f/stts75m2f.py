import time
import smbus2

class STTS75M2F:
    # Constants for resolution settings
    RESOLUTION_9BIT  = 0x00
    RESOLUTION_10BIT = 0x20
    RESOLUTION_11BIT = 0x40
    RESOLUTION_12BIT = 0x60
    RESOLUTION_MASK  = 0x60

    def __init__(self, address=0x48, bus_number=1, auto_stabilize=True, dummy_reads=1, stabilize_delay=1.0):
        self.address = address
        self.bus = smbus2.SMBus(bus_number)
        self.reset()
        if auto_stabilize:
            self._stabilize(dummy_reads, stabilize_delay)

    def reset(self):
        """Reset sensor settings to factory defaults."""
        self.set_configuration(0x00)

    def _stabilize(self, dummy_reads, delay):
        """Perform dummy reads and wait so that sensor readings stabilize."""
        for _ in range(dummy_reads):
            _ = self.read_temperature()
        time.sleep(delay)

    def read_temperature(self):
        try:
            data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
            temp = (data[0] << 8 | data[1]) >> 4
            temp_c = temp * 0.0625
            return temp_c
        except Exception as e:
            raise RuntimeError(f"Failed to read temperature from STTS75M2F sensor: {e}")

    def set_configuration(self, config_value):
        try:
            self.bus.write_byte_data(self.address, 0x01, config_value)
        except Exception as e:
            raise RuntimeError(f"Failed to set configuration on STTS75M2F sensor: {e}")

    def read_configuration(self):
        try:
            return self.bus.read_byte_data(self.address, 0x01)
        except Exception as e:
            raise RuntimeError(f"Failed to read configuration from STTS75M2F sensor: {e}")

    def set_resolution(self, resolution):
        try:
            config = self.read_configuration()
            config &= ~STTS75M2F.RESOLUTION_MASK
            config |= resolution
            self.set_configuration(config)
        except Exception as e:
            raise RuntimeError(f"Failed to set resolution on STTS75M2F sensor: {e}")

    def set_high_limit(self, high_limit):
        try:
            high_limit_value = int(high_limit / 0.0625) << 4
            self.bus.write_word_data(self.address, 0x03, high_limit_value)
        except Exception as e:
            raise RuntimeError(f"Failed to set high limit on STTS75M2F sensor: {e}")

    def set_hysteresis(self, hysteresis):
        try:
            hysteresis_value = int(hysteresis / 0.0625) << 4
            self.bus.write_word_data(self.address, 0x02, hysteresis_value)
        except Exception as e:
            raise RuntimeError(f"Failed to set hysteresis on STTS75M2F sensor: {e}")

    def set_fault_tolerance(self, tolerance):
        """
        Set the fault tolerance for the alarm by configuring bits 4 and 3 in
        the configuration register.
        Valid tolerance values: 1, 2, 4, or 6.
          - 1: tolerance setting bits = 00
          - 2: tolerance setting bits = 01
          - 4: tolerance setting bits = 10
          - 6: tolerance setting bits = 11
        """
        valid = {1: 0, 2: 1, 4: 2, 6: 3}
        if tolerance not in valid:
            raise ValueError("Fault tolerance must be one of: 1, 2, 4, or 6.")
        
        mapping = valid[tolerance]
        config = self.read_configuration()
        # Clear bits 4 and 3 (mask 0x18 = 00011000b)
        config &= ~0x18
        # Set the fault tolerance bits (shift mapping into bits 4 and 3)
        config |= (mapping << 3)
        self.set_configuration(config)

    def close(self):
        self.bus.close()

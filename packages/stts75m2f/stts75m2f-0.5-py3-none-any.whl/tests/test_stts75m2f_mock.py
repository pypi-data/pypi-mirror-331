import sys
import os
# Add the project's root directory to PYTHONPATH so the module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import unittest
from unittest.mock import MagicMock, patch
from stts75m2f import STTS75M2F

class TestSTTS75M2FMock(unittest.TestCase):
    def setUp(self):
        # Patch smbus2.SMBus so that no actual I2C bus is opened
        self.patcher = patch('smbus2.SMBus', autospec=True)
        self.addCleanup(self.patcher.stop)
        self.mock_smbus_class = self.patcher.start()
        self.mock_bus = MagicMock()
        self.mock_smbus_class.return_value = self.mock_bus
        
        # For most tests, disable auto stabilization to easily control call counts
        self.sensor = STTS75M2F(auto_stabilize=False)

    def tearDown(self):
        self.sensor.close()

    def test_reset(self):
        # Test that reset() calls set_configuration(0x00)
        with patch.object(self.sensor, 'set_configuration') as mock_set_config:
            self.sensor.reset()
            mock_set_config.assert_called_with(0x00)

    def test_auto_stabilize_called(self):
        # Test the auto stabilization in the constructor by setting auto_stabilize=True.
        # We set dummy_reads=3 and stabilize_delay=0.5 seconds.
        with patch('time.sleep') as mock_sleep, \
             patch.object(STTS75M2F, 'read_temperature', return_value=25.0) as mock_read_temperature:
            sensor = STTS75M2F(auto_stabilize=True, dummy_reads=3, stabilize_delay=0.5)
            # Expect read_temperature to be called 3 times (for dummy reads)
            self.assertEqual(mock_read_temperature.call_count, 3)
            # And expect a sleep delay of 0.5 seconds
            mock_sleep.assert_called_once_with(0.5)
            sensor.close()

    def test_read_temperature(self):
        # Simulate that the I2C bus returns 2 bytes: [0x19, 0x00]
        # Calculation: ((0x19 << 8) | 0x00) >> 4 = (0x1900 >> 4) = 0x190 = 400, and 400 * 0.0625 = 25.0°C
        self.mock_bus.read_i2c_block_data.return_value = [0x19, 0x00]
        temperature = self.sensor.read_temperature()
        self.assertAlmostEqual(temperature, 25.0, places=2)
        self.mock_bus.read_i2c_block_data.assert_called_once_with(self.sensor.address, 0x00, 2)

    def test_set_configuration(self):
        # Test that set_configuration writes the correct value to configuration register
        config_value = 0x55
        # Reset the write_byte_data call counter (to ignore calls during initialization/reset)
        self.mock_bus.write_byte_data.reset_mock()
        self.sensor.set_configuration(config_value)
        self.mock_bus.write_byte_data.assert_called_once_with(self.sensor.address, 0x01, config_value)

    def test_set_resolution(self):
        # Test that setting the resolution updates the configuration register correctly
        self.mock_bus.read_byte_data.return_value = 0x00
        self.sensor.set_resolution(STTS75M2F.RESOLUTION_12BIT)
        self.mock_bus.write_byte_data.assert_called_with(self.sensor.address, 0x01, 0x60)

    def test_set_high_limit(self):
        # Test that set_high_limit calculates and writes the correct raw value
        high_limit = 75.0  # °C
        raw_value = int(high_limit / 0.0625) << 4
        self.sensor.set_high_limit(high_limit)
        self.mock_bus.write_word_data.assert_called_once_with(self.sensor.address, 0x03, raw_value)

    def test_set_hysteresis(self):
        # Test that set_hysteresis calculates and writes the correct raw value
        hysteresis = 20.0  # °C
        raw_value = int(hysteresis / 0.0625) << 4
        self.sensor.set_hysteresis(hysteresis)
        self.mock_bus.write_word_data.assert_called_once_with(self.sensor.address, 0x02, raw_value)

    def test_set_fault_tolerance(self):
        # Test the fault tolerance settings for various valid values.
        # Assume the initial configuration read returns 0x00.
        
        # Tolerance = 1 (mapping = 0) -> Expected config: 0x00
        self.mock_bus.read_byte_data.return_value = 0x00
        self.mock_bus.write_byte_data.reset_mock()
        self.sensor.set_fault_tolerance(1)
        self.mock_bus.write_byte_data.assert_called_with(self.sensor.address, 0x01, 0x00)
        
        # Tolerance = 2 (mapping = 1) -> Expected config: 1 << 3 = 0x08
        self.mock_bus.read_byte_data.return_value = 0x00
        self.mock_bus.write_byte_data.reset_mock()
        self.sensor.set_fault_tolerance(2)
        self.mock_bus.write_byte_data.assert_called_with(self.sensor.address, 0x01, 0x08)
        
        # Tolerance = 4 (mapping = 2) -> Expected config: 2 << 3 = 0x10
        self.mock_bus.read_byte_data.return_value = 0x00
        self.mock_bus.write_byte_data.reset_mock()
        self.sensor.set_fault_tolerance(4)
        self.mock_bus.write_byte_data.assert_called_with(self.sensor.address, 0x01, 0x10)
        
        # Tolerance = 6 (mapping = 3) -> Expected config: 3 << 3 = 0x18
        self.mock_bus.read_byte_data.return_value = 0x00
        self.mock_bus.write_byte_data.reset_mock()
        self.sensor.set_fault_tolerance(6)
        self.mock_bus.write_byte_data.assert_called_with(self.sensor.address, 0x01, 0x18)

    def test_set_fault_tolerance_invalid(self):
        # Test that setting an invalid fault tolerance value raises a ValueError
        with self.assertRaises(ValueError):
            self.sensor.set_fault_tolerance(3)

if __name__ == '__main__':
    unittest.main()

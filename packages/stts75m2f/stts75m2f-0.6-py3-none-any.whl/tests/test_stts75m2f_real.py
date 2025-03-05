import unittest
from stts75m2f import STTS75M2F

class TestSTTS75M2FReal(unittest.TestCase):

    def setUp(self):
        self.sensor = STTS75M2F()

    def test_reset(self):
        self.sensor.reset()
        config = self.sensor.read_configuration()
        self.assertEqual(config, 0x00)

    def test_read_temperature_all_resolutions(self):
        # Dummy data for different resolutions
        test_data = {
            STTS75M2F.RESOLUTION_9BIT:  [0x00, 0x80],  # Example raw data for 9-bit (0.5 * 2^9 / 128 = 0.5)
            STTS75M2F.RESOLUTION_10BIT: [0x01, 0x00],  # Example raw data for 10-bit (1.0 * 2^10 / 256 = 1.0)
            STTS75M2F.RESOLUTION_11BIT: [0x02, 0x00],  # Example raw data for 11-bit (2.0 * 2^11 / 512 = 2.0)
            STTS75M2F.RESOLUTION_12BIT: [0x04, 0x00]   # Example raw data for 12-bit (4.0 * 2^12 / 1024 = 4.0)
        }

        # Expected temperature values for different resolutions
        expected_temps = {
            STTS75M2F.RESOLUTION_9BIT:  0.5,
            STTS75M2F.RESOLUTION_10BIT: 1.0,
            STTS75M2F.RESOLUTION_11BIT: 2.0,
            STTS75M2F.RESOLUTION_12BIT: 4.0
        }

        for resolution, data in test_data.items():
            with self.subTest(resolution=resolution):
                # Set the resolution
                self.sensor.set_resolution(resolution)

                # Mock the I2C read to return the test data
                self.sensor.bus.read_i2c_block_data = lambda addr, cmd, len: data

                # Read the temperature
                temp = self.sensor.read_temperature()

                # Verify the temperature
                self.assertAlmostEqual(temp, expected_temps[resolution], places=2)

    def test_set_configuration(self):
        self.sensor.set_configuration(0x20)
        config = self.sensor.read_configuration()
        self.assertEqual(config, 0x20)

    def test_set_resolution(self):
        self.sensor.set_resolution(STTS75M2F.RESOLUTION_10BIT)
        config = self.sensor.read_configuration()
        self.assertEqual(config & STTS75M2F.RESOLUTION_MASK, STTS75M2F.RESOLUTION_10BIT)

    def test_set_high_limit(self):
        self.sensor.set_high_limit(25.0)
        # Read back value to confirm if possible

    def test_set_hysteresis(self):
        self.sensor.set_hysteresis(1.5)
        # Read back value to confirm if possible

    def test_set_fault_tolerance(self):
        self.sensor.set_fault_tolerance(4)
        config = self.sensor.read_configuration()
        self.assertEqual(config & 0x18, 0x10)

    def tearDown(self):
        self.sensor.close()

if __name__ == '__main__':
    unittest.main()

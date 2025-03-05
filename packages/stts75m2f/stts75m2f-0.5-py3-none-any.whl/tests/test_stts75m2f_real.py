import unittest
import time
from stts75m2f import STTS75M2F

class TestSTTS75M2FReal(unittest.TestCase):
    def setUp(self):
        """
        Create an instance of the sensor with auto stabilization enabled.
        The sensor will perform dummy reads (e.g., 3 reads) and wait for 1.0 second,
        so that unstable initial readings are discarded.
        """
        self.sensor = STTS75M2F(auto_stabilize=True, dummy_reads=3, stabilize_delay=1.0)

    def tearDown(self):
        """Close the I2C connection after each test."""
        self.sensor.close()

    def test_read_temperature(self):
        """
        Test that the read_temperature() method returns a float value and that the reading
        is within a reasonable range.
        Note: The acceptable temperature range should be adjusted to your environmental conditions.
        """
        temperature = self.sensor.read_temperature()
        self.assertIsInstance(temperature, float)
        # For example, assuming room temperature between -20°C and 100°C.
        self.assertTrue(-20.0 < temperature < 100.0, f"Temperature {temperature}°C is out of expected range.")

    def test_set_configuration(self):
        """
        Test that the configuration can be correctly set and read back.
        The sensor should return the configuration value that was written.
        """
        test_config = 0x55
        self.sensor.set_configuration(test_config)
        config = self.sensor.read_configuration()
        self.assertEqual(config, test_config, "The configuration read from the sensor does not match the set value.")

    def test_set_resolution(self):
        """
        Test that setting the resolution to 12-bit works correctly.
        The test verifies that the appropriate bits (bit mask RESOLUTION_MASK) in the configuration
        register match the 12-bit resolution setting.
        """
        self.sensor.set_resolution(STTS75M2F.RESOLUTION_12BIT)
        config = self.sensor.read_configuration()
        self.assertEqual(config & STTS75M2F.RESOLUTION_MASK, STTS75M2F.RESOLUTION_12BIT,
                         "Resolution bits in configuration do not match 12-bit setting.")

    def test_set_limits_and_hysteresis(self):
        """
        Test that setting the high limit and the hysteresis does not raise any exceptions.
        This is an integration test – it does not verify the exact raw register values
        (since that may depend on hardware variations), but ensures that the functions execute.
        """
        try:
            self.sensor.set_high_limit(75.0)
            self.sensor.set_hysteresis(20.0)
        except Exception as e:
            self.fail(f"Setting limits or hysteresis raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()

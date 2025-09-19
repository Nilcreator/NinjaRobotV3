import unittest
from unittest.mock import Mock, patch
import numpy as np
import pigpio
from vl53l0x_pigpio.driver import VL53L0X
from vl53l0x_pigpio.constants import (
    VALUE_00, VALUE_01, VALUE_10, VALUE_83, REG_92,
    GLOBAL_CFG_SPAD_ENABLES_REF_0, MSRC_CONFIG_CONTROL, SYSRANGE_START, RESULT_INTERRUPT_STATUS,
    PRE_RANGE_CONFIG_VCSEL_PERIOD, FINAL_RANGE_CONFIG_VCSEL_PERIOD, SYSTEM_SEQUENCE_CONFIG
)

class TestVL53L0XDriver(unittest.TestCase):

    def setUp(self) -> None:
        # Mock pigpio.pi
        self.mock_pi = Mock(spec=pigpio.pi)
        self.mock_pi.connected = True
        self.mock_pi.i2c_open.return_value = 1  # Mock I2C handle
        self.mock_pi.i2c_close.return_value = 0

        # Dictionary to store mock return values for specific registers
        # This simulates the sensor's responses during initialization and ranging
        self.mock_read_byte_data_returns = {
            # For _get_spad_info
            VALUE_83: [VALUE_00, VALUE_00, VALUE_01], # Simulate VALUE_83 changing from 0 to 1 to break the loop
            REG_92: 0x40, # Example: spad_count = 64, is_aperture = False
            # For _configure_signal_rate_limit
            MSRC_CONFIG_CONTROL: 0x00, # Default value before modification
            # For _configure_interrupt_gpio
            VALUE_10: 0x00, # Default value before modification
            # For perform_single_ref_calibration and get_range (simplified for debugging)
            RESULT_INTERRUPT_STATUS: lambda: [VALUE_01], # Return VALUE_01 immediately
            SYSRANGE_START: lambda: [VALUE_00], # Return VALUE_00 immediately after first read
            PRE_RANGE_CONFIG_VCSEL_PERIOD: 14,
            FINAL_RANGE_CONFIG_VCSEL_PERIOD: 10,
            SYSTEM_SEQUENCE_CONFIG: 0xE8,
            0x02: 0xCD, # For test_read_byte
        }

        # Mock for i2c_read_i2c_block_data specifically for GLOBAL_CFG_SPAD_ENABLES_REF_0 and test_read_block
        self.mock_pi.i2c_read_i2c_block_data.side_effect = lambda handle, register, count: (
            (6, bytearray([0x00] * 6)) if register == GLOBAL_CFG_SPAD_ENABLES_REF_0 and count == 6 else
            (3, bytearray([0x11, 0x22, 0x33])) if register == 0x05 and count == 3 else # For test_read_block
            (count, bytearray([0x00] * count))
        )

        def i2c_read_byte_data_side_effect(handle: int, register: int) -> int:
            if register in self.mock_read_byte_data_returns:
                return_value = self.mock_read_byte_data_returns[register]
                if callable(return_value):
                    return_value = return_value() # Call the lambda to get a fresh list
                if isinstance(return_value, list):
                    # If it's a list, pop the first element for sequential reads
                    if return_value:
                        return int(return_value.pop(0))
                    return 0x00 # Default if list is empty
                if isinstance(return_value, (int, float)):
                    return int(return_value)
                return 0x00
            # Fallback to original side_effect or a default value if not explicitly mocked
            return 0x00 # Default for unmocked registers

        self.mock_pi.i2c_read_byte_data.side_effect = i2c_read_byte_data_side_effect

        self.mock_pi.i2c_write_byte_data.return_value = 0
        self.mock_pi.i2c_read_word_data.return_value = 0  # Default mock return
        self.mock_pi.i2c_write_word_data.return_value = 0

        # Patch pigpio.pi to return our mock_pi instance
        self.patcher = patch('pigpio.pi', return_value=self.mock_pi)
        self.mock_pigpio_pi_class = self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

    def test_initialization(self) -> None:
        # Test if the driver can be initialized
        with VL53L0X(self.mock_pi) as tof:
            self.assertIsInstance(tof, VL53L0X)
            self.mock_pi.i2c_open.assert_called_once()
            # Ensure close is called when exiting the context
        self.mock_pi.i2c_close.assert_called_once()

    def test_get_range(self) -> None:
        # Mock a specific range value
        # VL53L0X returns big-endian, pigpio reads little-endian, so we mock pigpio's return
        # For example, if we want 1234mm (0x04D2), pigpio would read 0xD204
        self.mock_pi.i2c_read_word_data.return_value = 0xD204

        with VL53L0X(self.mock_pi) as tof:
            distance = tof.get_range()
            self.assertEqual(distance, 1234)
            self.mock_pi.i2c_read_word_data.assert_called()

    def test_get_ranges(self) -> None:
        num_samples = 5
        # Mock a sequence of range values
        mock_ranges_pigpio_endian = [0xD204, 0xD304, 0xD404, 0xD504, 0xD604] # 1234, 1235, 1236, 1237, 1238
        range_iterator = iter(mock_ranges_pigpio_endian)

        def read_word_side_effect(handle: int, register: int) -> int:
            if register == 30: # RESULT_RANGE_STATUS + 10
                return next(range_iterator)
            return 0

        # Configure the mock to return different values on successive calls
        self.mock_pi.i2c_read_word_data.side_effect = read_word_side_effect

        with VL53L0X(self.mock_pi) as tof:
            ranges = tof.get_ranges(num_samples)
            self.assertIsInstance(ranges, np.ndarray)
            self.assertEqual(ranges.shape, (num_samples,))
            self.assertTrue(np.array_equal(ranges, np.array([1234, 1235, 1236, 1237, 1238])))
            self.assertEqual(self.mock_pi.i2c_read_word_data.call_count, num_samples + 4) # +4 for initialization

    def test_read_byte(self) -> None:
        self.mock_pi.i2c_read_byte_data.return_value = 0xCD
        with VL53L0X(self.mock_pi) as tof:
            value = tof.read_byte(0x02)
            self.assertEqual(value, 0xCD)
            self.mock_pi.i2c_read_byte_data.assert_called_with(1, 0x02)

    def test_write_byte(self) -> None:
        with VL53L0X(self.mock_pi) as tof:
            tof.write_byte(0x02, 0xCD)
            self.mock_pi.i2c_write_byte_data.assert_called_with(1, 0x02, 0xCD)

    def test_read_word(self) -> None:
        # Mock pigpio reading 0xCDAB (little-endian for 0xABCD)
        self.mock_pi.i2c_read_word_data.return_value = 0xCDAB
        with VL53L0X(self.mock_pi) as tof:
            value = tof.read_word(0x03)
            self.assertEqual(value, 0xABCD)
            self.mock_pi.i2c_read_word_data.assert_called_with(1, 0x03)

    def test_write_word(self) -> None:
        # We want to write 0xABCD, which pigpio should receive as 0xCDAB
        with VL53L0X(self.mock_pi) as tof:
            tof.write_word(0x04, 0xABCD)
            self.mock_pi.i2c_write_word_data.assert_called_with(1, 0x04, 0xCDAB)

    def test_read_block(self) -> None:
        mock_block_data = [0x11, 0x22, 0x33]
        self.mock_pi.i2c_read_i2c_block_data.return_value = (0, mock_block_data)
        with VL53L0X(self.mock_pi) as tof:
            data = tof.read_block(0x05, 3)
            self.assertEqual(data, mock_block_data)
            self.mock_pi.i2c_read_i2c_block_data.assert_called_with(1, 0x05, 3)

    def test_write_block(self) -> None:
        test_data = [0xAA, 0xBB, 0xCC]
        with VL53L0X(self.mock_pi) as tof:
            tof.write_block(0x06, test_data)
            self.mock_pi.i2c_write_i2c_block_data.assert_called_with(1, 0x06, test_data)

if __name__ == '__main__':
    unittest.main()

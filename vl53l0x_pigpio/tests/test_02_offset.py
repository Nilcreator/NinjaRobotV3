
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from vl53l0x_pigpio.driver import VL53L0X
from vl53l0x_pigpio.config_manager import load_config

class TestVL53L0XOffset(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_pi = Mock()
        self.mock_pi.i2c_open.return_value = 1
        self.mock_pi.i2c_read_byte_data.side_effect = self.mock_read_byte_data
        self.mock_pi.i2c_read_i2c_block_data.return_value = (6, bytearray([0] * 6))
        self.patcher = patch('pigpio.pi', return_value=self.mock_pi)
        self.mock_pigpio_pi = self.patcher.start()

        # Minimal register values for initialization
        self.reg_map = {
            0x91: 0x00,
            0x89: 0x00,
            0x60: 0x00,
            0x84: 0x00,
            0x92: 0x00,
            0x83: 0x01, # To exit the loop in _get_spad_info
            0x13: 0x01, # To exit the loop in get_range
        }

    def tearDown(self) -> None:
        self.patcher.stop()

    def mock_read_byte_data(self, handle: int, register: int) -> int:
        return self.reg_map.get(register, 0)

    def test_offset_correction(self) -> None:
        """
        オフセット補正が正しく機能するかテストする
        """
        with VL53L0X(self.mock_pi) as tof:
            # オフセットを設定
            offset = 60
            tof.set_offset(offset)

            # センサーからの生の測定値をモック
            raw_measurement = 200
            # pigpioはリトルエンディアンで読み取るため、値を変換
            self.mock_pi.i2c_read_word_data.return_value = ((raw_measurement & 0xFF) << 8) | (raw_measurement >> 8)

            # 測定値を取得
            measured_distance = tof.get_range()

            # オフセットが適用されたか確認
            self.assertEqual(measured_distance, raw_measurement - offset)

    @patch('vl53l0x_pigpio.driver.load_config')
    def test_init_with_config_file_loads_offset(self, mock_load_config) -> None:
        mock_load_config.return_value = {"offset_mm": 75}
        config_file_path = Path("/tmp/test_config.json")

        with VL53L0X(self.mock_pi, config_file_path=config_file_path) as tof:
            self.assertEqual(tof.offset_mm, 75)
            mock_load_config.assert_called_once_with(config_file_path)

    @patch('vl53l0x_pigpio.driver.load_config')
    def test_init_with_config_file_no_offset(self, mock_load_config) -> None:
        mock_load_config.return_value = {}
        config_file_path = Path("/tmp/test_config.json")

        with VL53L0X(self.mock_pi, config_file_path=config_file_path) as tof:
            self.assertEqual(tof.offset_mm, 0)
            mock_load_config.assert_called_once_with(config_file_path)

if __name__ == '__main__':
    unittest.main()

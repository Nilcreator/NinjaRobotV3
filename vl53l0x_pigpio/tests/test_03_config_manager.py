import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json

from vl53l0x_pigpio.config_manager import (
    get_default_config_filepath, load_config, save_config
)

class TestConfigManager(unittest.TestCase):

    @patch('pathlib.Path.home')
    def test_get_default_config_filepath(self, mock_home):
        mock_home.return_value = Path("/home/testuser")
        expected_path = Path("/home/testuser/vl53l0x.json")
        
        # Mock mkdir to prevent actual directory creation
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result_path = get_default_config_filepath()
            self.assertEqual(result_path, expected_path)
            # Ensure mkdir was called for the parent directory if it doesn't exist
            # In this case, the parent is just home_dir, so mkdir is not called for it
            # mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_config(self, mock_exists, mock_file):
        mock_file.return_value.read.return_value = '{"offset_mm": 5}'
        filepath = Path("/tmp/test_config.json")
        config = load_config(filepath)
        self.assertEqual(config, {"offset_mm": 5})
        mock_file.assert_called_once_with(filepath, "r", encoding="utf-8")

    @patch('pathlib.Path.exists', return_value=False)
    def test_load_config_non_existent_file(self, mock_exists):
        filepath = Path("/tmp/non_existent.json")
        config = load_config(filepath)
        self.assertEqual(config, {})

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_config(self, mock_mkdir, mock_file, mock_json_dump):
        filepath = Path("/tmp/test_config.json")
        config_data = {"offset_mm": 10}
        save_config(filepath, config_data)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(filepath, "w", encoding="utf-8")
        mock_json_dump.assert_called_once_with(config_data, mock_file(), indent=4)


if __name__ == '__main__':
    unittest.main()


import unittest
import sys
import os
import json
import tempfile
from unittest.mock import patch
from config import get_config, load_apis_config


class TestLoadApisConfig(unittest.TestCase):
    """Tests para la carga y validación del archivo de configuración."""

    def _write_temp_config(self, data):
        """Helper: escribe un archivo temporal JSON y retorna su ruta."""
        path = os.path.join(tempfile.gettempdir(), "test_cronoscore_config.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return path

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_apis_config("non_existent_config_12345.json")

    def test_invalid_json_format(self):
        """El archivo debe contener una lista."""
        path = self._write_temp_config({"not": "a list"})
        try:
            with self.assertRaises(ValueError):
                load_apis_config(path)
        finally:
            os.unlink(path)

    def test_missing_required_fields(self):
        """Debe fallar si falta un campo requerido."""
        path = self._write_temp_config([{"name": "Test"}])
        try:
            with self.assertRaises(ValueError):
                load_apis_config(path)
        finally:
            os.unlink(path)

    def test_valid_config_with_defaults(self):
        """Debe setear valores por defecto para campos opcionales."""
        config = [{
            "name": "TestAPI",
            "endpoint": "http://test.com",
            "api_key": "key123",
            "validation_rules": [{"field": "score", "operator": ">=", "value": 80}]
        }]
        path = self._write_temp_config(config)
        try:
            result = load_apis_config(path)
            self.assertEqual(result[0]["method"], "GET")
            self.assertEqual(result[0]["param_name"], "email")
            self.assertEqual(result[0]["response_path"], "data")
            self.assertEqual(result[0]["timeout"], 30)
        finally:
            os.unlink(path)

    def test_env_var_api_key(self):
        """Debe resolver API keys desde variables de entorno."""
        config = [{
            "name": "TestAPI",
            "endpoint": "http://test.com",
            "api_key": "$TEST_API_KEY_CRONOSCORE",
            "validation_rules": []
        }]
        path = self._write_temp_config(config)
        try:
            os.environ["TEST_API_KEY_CRONOSCORE"] = "secret_key_123"
            result = load_apis_config(path)
            self.assertEqual(result[0]["api_key"], "secret_key_123")
        finally:
            if os.path.exists(path):
                os.unlink(path)
            if "TEST_API_KEY_CRONOSCORE" in os.environ:
                del os.environ["TEST_API_KEY_CRONOSCORE"]

    def test_env_var_api_key_not_set(self):
        """Debe fallar si la variable de entorno no está definida."""
        config = [{
            "name": "TestAPI",
            "endpoint": "http://test.com",
            "api_key": "$UNDEFINED_VAR_CRONOSCORE_TEST",
            "validation_rules": []
        }]
        path = self._write_temp_config(config)
        try:
            with self.assertRaises(ValueError):
                load_apis_config(path)
        finally:
            os.unlink(path)


class TestGetConfig(unittest.TestCase):
    """Tests para argumentos de línea de comandos."""

    def _mock_apis_config(self):
        """Retorna una configuración de APIs válida para mockear."""
        return [{
            "name": "MockAPI",
            "endpoint": "http://mock.api",
            "api_key": "mock_key",
            "validation_rules": [],
            "method": "GET",
            "headers": {},
            "param_name": "email",
            "response_path": "data",
            "timeout": 30,
        }]

    @patch('config.load_apis_config')
    def test_default_arguments(self, mock_load):
        mock_load.return_value = self._mock_apis_config()
        test_args = ["programa"]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.requests_per_second, 16)
            self.assertEqual(args.valid_emails_file, "valid_emails.txt")
            self.assertEqual(args.invalid_emails_file, "invalid_emails.txt")

    @patch('config.load_apis_config')
    def test_custom_arguments(self, mock_load):
        mock_load.return_value = self._mock_apis_config()
        test_args = [
            "programa",
            "--requests-per-second", "10",
            "--valid-emails-file", "my_valid.txt",
            "--invalid-emails-file", "my_invalid.txt",
        ]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.requests_per_second, 10)
            self.assertEqual(args.valid_emails_file, "my_valid.txt")
            self.assertEqual(args.invalid_emails_file, "my_invalid.txt")

    @patch('config.load_apis_config')
    def test_short_arguments(self, mock_load):
        mock_load.return_value = self._mock_apis_config()
        test_args = ["programa", "-rps", "5"]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.requests_per_second, 5)

    @patch('config.load_apis_config')
    def test_log_level_argument(self, mock_load):
        mock_load.return_value = self._mock_apis_config()
        test_args = ["programa", "--log-level", "DEBUG"]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.log_level, "DEBUG")


if __name__ == '__main__':
    unittest.main()

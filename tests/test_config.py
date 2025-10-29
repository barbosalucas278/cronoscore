
import unittest
import sys
from unittest.mock import patch
from config import get_config

class TestConfig(unittest.TestCase):

    def test_default_arguments(self):
        """Prueba que los argumentos por defecto se cargan correctamente."""
        test_args = ["programa"]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.endpoint, "https://api.example.com/validate")
            self.assertEqual(args.api_key, "DEFAULT_API_KEY")
            self.assertEqual(args.requests_per_second, 16)
            self.assertEqual(args.valid_emails_file, "valid_emails.txt")
            self.assertEqual(args.invalid_emails_file, "invalid_emails.txt")
            self.assertEqual(args.output_file, "results.json")
            self.assertEqual(args.valid_reason, "valid_email")

    def test_custom_arguments(self):
        """Prueba que los argumentos personalizados anulan los valores por defecto."""
        test_args = [
            "programa",
            "--endpoint", "http://custom.api/v2",
            "--api-key", "my-secret-key",
            "--requests-per-second", "10",
            "--valid-emails-file", "my_valid.txt",
            "--invalid-emails-file", "my_invalid.txt",
            "--output-file", "my_results.json",
            "--valid-reason", "approved"
        ]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.endpoint, "http://custom.api/v2")
            self.assertEqual(args.api_key, "my-secret-key")
            self.assertEqual(args.requests_per_second, 10)
            self.assertEqual(args.valid_emails_file, "my_valid.txt")
            self.assertEqual(args.invalid_emails_file, "my_invalid.txt")
            self.assertEqual(args.output_file, "my_results.json")
            self.assertEqual(args.valid_reason, "approved")

    def test_short_arguments(self):
        """Prueba que los argumentos cortos (como -rps) funcionan."""
        test_args = ["programa", "-rps", "5"]
        with patch.object(sys, 'argv', test_args):
            args = get_config()
            self.assertEqual(args.requests_per_second, 5)

if __name__ == '__main__':
    unittest.main()

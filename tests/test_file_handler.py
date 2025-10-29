
import unittest
import os
import json
from file_handler import read_emails_from_file, save_results_to_json

class TestFileHandler(unittest.TestCase):

    def setUp(self):
        """Configura el entorno para cada prueba."""
        self.valid_file = "test_valid_emails.txt"
        self.invalid_file = "test_invalid_emails.txt"
        self.output_file = "test_output.json"

        with open(self.valid_file, "w") as f:
            f.write("email1@example.com\n")
            f.write(" email2@example.com \n")
            f.write("\n")

        with open(self.invalid_file, "w") as f:
            f.write("email3@example.com\n")

    def tearDown(self):
        """Limpia el entorno después de cada prueba."""
        if os.path.exists(self.valid_file):
            os.remove(self.valid_file)
        if os.path.exists(self.invalid_file):
            os.remove(self.invalid_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_read_valid_emails(self):
        """Prueba que la lectura de emails válidos funciona y limpia los espacios."""
        emails = read_emails_from_file(self.valid_file)
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0], "email1@example.com")
        self.assertEqual(emails[1], "email2@example.com")

    def test_read_non_existent_file(self):
        """Prueba que devuelve una lista vacía si el archivo no existe."""
        emails = read_emails_from_file("non_existent_file.txt")
        self.assertEqual(emails, [])

    def test_save_and_read_json(self):
        """Prueba que los datos se guardan y se leen correctamente en formato JSON."""
        test_data = {
            "summary": "Test Summary",
            "details": [1, 2, 3]
        }
        save_results_to_json(test_data, self.output_file)

        self.assertTrue(os.path.exists(self.output_file))

        with open(self.output_file, 'r') as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data["summary"], "Test Summary")
        self.assertEqual(loaded_data["details"], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()

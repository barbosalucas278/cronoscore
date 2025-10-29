
import unittest
import asyncio
import aiohttp
from unittest.mock import MagicMock, AsyncMock
from api_client import process_email, run_api_tests

class TestApiClient(unittest.TestCase):

    def test_process_email_verdadero_positivo(self):
        """Prueba la clasificación de un Valido considerado valido."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "score": 30,
                "result": "deliverable",
                "reason": "valid_email"
            }
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Valido considerado valido')

    def test_process_email_falso_negativo(self):
        """Prueba la clasificación de un Valido considerado invalido."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "score": 10,
                "result": "risky",
                "reason": "invalid_email"
            }
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Valido considerado invalido')

    def test_process_email_api_error(self):
        """Prueba el manejo de un error de la API."""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Error de red")

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de red", result['error_message'])

    def test_process_email_invalido_considerado_valido(self):
        """Prueba la clasificación de un Invalido considerado valido."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "score": 30,
                "result": "deliverable",
                "reason": "valid_email"
            }
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", False, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Invalido considerado valido')

    def test_process_email_invalido_considerado_invalido(self):
        """Prueba la clasificación de un Invalido considerado Invalido."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "score": 10,
                "result": "risky",
                "reason": "invalid_email"
            }
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", False, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Invalido considerado Invalido')

    def test_process_email_with_custom_validation_fields(self):
        """Prueba la clasificación con nombres de campos de validación personalizados."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": {
                "custom_score": 90,
                "validation_status": "ok",
                "reason": "valid_email"
            }
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        validation_rule = {"score_field": "custom_score", "result_field": "validation_status", "score_value": "80", "result_value": "ok"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Valido considerado valido')

    def test_process_email_aiohttp_client_error(self):
        """Prueba el manejo de aiohttp.ClientError."""
        mock_session = MagicMock()
        mock_session.get.side_effect = aiohttp.ClientError("Error de cliente")

        validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", validation_rule
        ))

        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de cliente", result['error_message'])

    def test_run_api_tests_rate_limit(self):
        """Prueba que el limitador de velocidad funciona (aproximadamente)."""

        async def main_test():
            with unittest.mock.patch('api_client.process_email', new_callable=AsyncMock) as mock_process_email:
                mock_process_email.return_value = {"classification": "OK"}

                emails_to_process = [("email1", True), ("email2", False), ("email3", True)]
                rps = 10
                validation_rule = {"score_field": "score", "result_field": "result", "score_value": "20", "result_value": "deliverable"}

                start_time = asyncio.get_event_loop().time()
                await run_api_tests(emails_to_process, "key", "endpoint", rps, validation_rule)
                end_time = asyncio.get_event_loop().time()

                duration = end_time - start_time
                expected_duration = (len(emails_to_process) - 1) / rps

                self.assertGreater(duration, expected_duration)
                self.assertEqual(mock_process_email.call_count, len(emails_to_process))

        asyncio.run(main_test())

if __name__ == '__main__':
    unittest.main()

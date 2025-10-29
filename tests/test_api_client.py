
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from api_client import process_email, run_api_tests

class TestApiClient(unittest.TestCase):

    def test_process_email_verdadero_positivo(self):
        """Prueba la clasificación de un Verdadero Positivo."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        # Configurar el mock para que devuelva una razón de email válido
        mock_response.json.return_value = {"reason": "valid_email"}
        # Hacer que el 'async with' devuelva el mock_response
        mock_session.get.return_value.__aenter__.return_value = mock_response

        # Ejecutar la función
        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", "valid_email"
        ))

        # Verificar
        self.assertEqual(result['classification'], 'Verdadero Positivo')

    def test_process_email_falso_negativo(self):
        """Prueba la clasificación de un Falso Negativo."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"reason": "invalid_email"}
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", "valid_email"
        ))

        self.assertEqual(result['classification'], 'Falso Negativo')

    def test_process_email_api_error(self):
        """Prueba el manejo de un error de la API."""
        mock_session = MagicMock()
        # Simular una excepción al hacer la llamada
        mock_session.get.side_effect = Exception("Error de red")

        result = asyncio.run(process_email(
            mock_session, "test@example.com", True, "fake_key", "http://fake.api", "valid_email"
        ))

        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de red", result['error_message'])

    def test_run_api_tests_rate_limit(self):
        """Prueba que el limitador de velocidad funciona (aproximadamente)."""

        async def main_test():
            # Reemplazar la función real con nuestro mock
            with unittest.mock.patch('api_client.process_email', new_callable=AsyncMock) as mock_process_email:
                mock_process_email.return_value = {"classification": "OK"}

                emails_to_process = [("email1", True), ("email2", False), ("email3", True)]
                rps = 10 # 10 solicitudes por segundo -> 0.1s de delay

                start_time = asyncio.get_event_loop().time()
                await run_api_tests(emails_to_process, "key", "endpoint", rps, "valid")
                end_time = asyncio.get_event_loop().time()

                duration = end_time - start_time
                expected_duration = (len(emails_to_process) - 1) / rps

                # La duración real debería ser ligeramente mayor que la esperada
                self.assertGreater(duration, expected_duration)
                # El número de llamadas debe ser igual al número de emails
                self.assertEqual(mock_process_email.call_count, len(emails_to_process))

        asyncio.run(main_test())

if __name__ == '__main__':
    unittest.main()

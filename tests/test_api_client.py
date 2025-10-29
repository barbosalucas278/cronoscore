
import unittest
import asyncio
import aiohttp
from unittest.mock import MagicMock, AsyncMock
from api_client import process_email, evaluate_rule, run_api_tests

class TestApiClient(unittest.TestCase):

    def test_evaluate_rule_greater_than_or_equal_pass(self):
        rule = {"field": "score", "operator": ">=", "value": 80}
        api_response = {"data": {"score": 90}}
        self.assertTrue(evaluate_rule(api_response, rule))

    def test_evaluate_rule_greater_than_or_equal_fail(self):
        rule = {"field": "score", "operator": ">=", "value": 80}
        api_response = {"data": {"score": 70}}
        self.assertFalse(evaluate_rule(api_response, rule))

    def test_evaluate_rule_in_pass(self):
        rule = {"field": "result", "operator": "in", "value": ["deliverable", "risky"]}
        api_response = {"data": {"result": "deliverable"}}
        self.assertTrue(evaluate_rule(api_response, rule))

    def test_evaluate_rule_in_fail(self):
        rule = {"field": "result", "operator": "in", "value": ["deliverable"]}
        api_response = {"data": {"result": "risky"}}
        self.assertFalse(evaluate_rule(api_response, rule))

    def test_evaluate_rule_equal_pass(self):
        rule = {"field": "status", "operator": "==", "value": "valid"}
        api_response = {"data": {"status": "valid"}}
        self.assertTrue(evaluate_rule(api_response, rule))

    def test_process_email_all_rules_pass_verdadero_positivo(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 90, "result": "deliverable"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        rules = [{"field": "score", "operator": ">=", "value": 80}]
        result = asyncio.run(process_email(mock_session, "test@example.com", True, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Valido considerado valido')

    def test_process_email_any_rule_passes_verdadero_positivo(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 70, "result": "deliverable"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        rules = [
            {"field": "score", "operator": ">=", "value": 80},
            {"field": "result", "operator": "in", "value": ["deliverable", "risky"]}
        ]
        result = asyncio.run(process_email(mock_session, "test@example.com", True, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Valido considerado valido')

    def test_process_email_all_rules_fail_falso_negativo(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 70, "result": "undeliverable"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        rules = [
            {"field": "score", "operator": ">=", "value": 80},
            {"field": "result", "operator": "in", "value": ["deliverable", "risky"]}
        ]
        result = asyncio.run(process_email(mock_session, "test@example.com", True, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Valido considerado invalido')

    def test_process_email_invalido_considerado_valido(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 90, "result": "deliverable"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        rules = [{"field": "score", "operator": ">=", "value": 80}]
        result = asyncio.run(process_email(mock_session, "test@example.com", False, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Invalido considerado valido')

    def test_process_email_invalido_considerado_invalido(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 70, "result": "deliverable"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        rules = [{"field": "score", "operator": ">=", "value": 80}]
        result = asyncio.run(process_email(mock_session, "test@example.com", False, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Invalido considerado Invalido')

    def test_process_email_api_error(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Error de red")
        rules = [{"field": "score", "operator": ">=", "value": 80}]
        result = asyncio.run(process_email(mock_session, "test@example.com", True, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de red", result['error_message'])

    def test_process_email_aiohttp_client_error(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = aiohttp.ClientError("Error de cliente")
        rules = [{"field": "score", "operator": ">=", "value": 80}]
        result = asyncio.run(process_email(mock_session, "test@example.com", True, "fake_key", "http://fake.api", rules))
        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de cliente", result['error_message'])

    def test_run_api_tests_rate_limit(self):
        async def main_test():
            with unittest.mock.patch('api_client.process_email', new_callable=AsyncMock) as mock_process_email:
                mock_process_email.return_value = {"classification": "OK"}
                emails_to_process = [("email1", True), ("email2", False), ("email3", True)]
                rps = 10
                rules = [{"field": "score", "operator": ">=", "value": 80}]
                start_time = asyncio.get_event_loop().time()
                await run_api_tests(emails_to_process, "key", "endpoint", rps, rules)
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                expected_duration = (len(emails_to_process) - 1) / rps
                self.assertGreater(duration, expected_duration)
                self.assertEqual(mock_process_email.call_count, len(emails_to_process))
        asyncio.run(main_test())

if __name__ == '__main__':
    unittest.main()

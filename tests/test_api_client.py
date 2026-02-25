
import unittest
import asyncio
import aiohttp
from unittest.mock import MagicMock, AsyncMock
from api_client import process_email, evaluate_rule, resolve_field, run_api_tests


class TestResolveField(unittest.TestCase):
    """Tests para la función resolve_field con dot notation."""

    def test_simple_field(self):
        data = {"name": "test"}
        self.assertEqual(resolve_field(data, "name"), "test")

    def test_nested_field(self):
        data = {"data": {"score": 90}}
        self.assertEqual(resolve_field(data, "data.score"), 90)

    def test_deeply_nested(self):
        data = {"a": {"b": {"c": "value"}}}
        self.assertEqual(resolve_field(data, "a.b.c"), "value")

    def test_missing_field(self):
        data = {"data": {"score": 90}}
        self.assertIsNone(resolve_field(data, "data.missing"))

    def test_missing_intermediate(self):
        data = {"data": {"score": 90}}
        self.assertIsNone(resolve_field(data, "missing.score"))


class TestEvaluateRule(unittest.TestCase):
    """Tests para evaluate_rule con response_path."""

    def test_greater_than_or_equal_pass(self):
        rule = {"field": "score", "operator": ">=", "value": 80}
        api_response = {"data": {"score": 90}}
        self.assertTrue(evaluate_rule(api_response, rule, "data"))

    def test_greater_than_or_equal_fail(self):
        rule = {"field": "score", "operator": ">=", "value": 80}
        api_response = {"data": {"score": 70}}
        self.assertFalse(evaluate_rule(api_response, rule, "data"))

    def test_in_pass(self):
        rule = {"field": "result", "operator": "in", "value": ["deliverable", "risky"]}
        api_response = {"data": {"result": "deliverable"}}
        self.assertTrue(evaluate_rule(api_response, rule, "data"))

    def test_in_fail(self):
        rule = {"field": "result", "operator": "in", "value": ["deliverable"]}
        api_response = {"data": {"result": "risky"}}
        self.assertFalse(evaluate_rule(api_response, rule, "data"))

    def test_equal_pass(self):
        rule = {"field": "status", "operator": "==", "value": "valid"}
        api_response = {"data": {"status": "valid"}}
        self.assertTrue(evaluate_rule(api_response, rule, "data"))

    def test_custom_response_path(self):
        """Verifica que response_path personalizado funcione."""
        rule = {"field": "valid", "operator": "==", "value": True}
        api_response = {"result": {"valid": True}}
        self.assertTrue(evaluate_rule(api_response, rule, "result"))


class TestProcessEmail(unittest.TestCase):
    """Tests para process_email con la nueva API config."""

    def _make_api_config(self, **overrides):
        config = {
            "name": "TestAPI",
            "api_key": "fake_key",
            "endpoint": "http://fake.api",
            "method": "GET",
            "param_name": "email",
            "headers": {},
            "response_path": "data",
            "timeout": 10,
            "validation_rules": [{"field": "score", "operator": ">=", "value": 80}],
        }
        config.update(overrides)
        return config

    def test_valido_considerado_valido(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 90, "reason": "ok"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", True, config))
        self.assertEqual(result['classification'], 'Valido considerado valido')

    def test_valido_considerado_invalido(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 70, "reason": "low_score"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", True, config))
        self.assertEqual(result['classification'], 'Valido considerado invalido')

    def test_invalido_considerado_valido(self):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 90, "reason": "ok"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", False, config))
        self.assertEqual(result['classification'], 'Invalido considerado valido')

    def test_invalido_considerado_invalido(self):
        """Clasificación consistente: todo en minúsculas."""
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": {"score": 70, "reason": "low"}}
        mock_session.get.return_value.__aenter__.return_value = mock_response
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", False, config))
        self.assertEqual(result['classification'], 'Invalido considerado invalido')

    def test_api_error(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Error de red")
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", True, config))
        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de red", result['error_message'])

    def test_aiohttp_client_error(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = aiohttp.ClientError("Error de cliente")
        config = self._make_api_config()
        result = asyncio.run(process_email(mock_session, "test@example.com", True, config))
        self.assertEqual(result['classification'], 'Error')
        self.assertIn("Error de cliente", result['error_message'])


if __name__ == '__main__':
    unittest.main()

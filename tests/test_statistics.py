
import unittest
from stats_calculator import calculate_statistics


class TestStatistics(unittest.TestCase):

    def setUp(self):
        """Prepara datos de prueba comunes para las pruebas."""
        self.mock_results = [
            {'duration': 0.1, 'classification': 'Valido considerado valido'},
            {'duration': 0.2, 'classification': 'Valido considerado valido'},
            {'duration': 0.15, 'classification': 'Valido considerado invalido'},
            {'duration': 0.3, 'classification': 'Invalido considerado valido'},
            {'duration': 0.25, 'classification': 'Invalido considerado invalido'},
            {'duration': 0.4, 'classification': 'Error'},
        ]
        self.total_valid = 3
        self.total_invalid = 2
        self.rps = 15
        self.endpoint = "http://test.api"

    def test_performance_calculations(self):
        """Prueba que los cálculos de rendimiento (tiempos) son correctos."""
        stats = calculate_statistics(self.mock_results, self.total_valid, self.total_invalid, self.rps, self.endpoint)

        performance = stats['performance']
        self.assertAlmostEqual(performance['total_processing_time'], 1.4)
        self.assertAlmostEqual(performance['average_response_time'], 1.4 / 6)
        self.assertEqual(performance['max_response_time'], 0.4)
        self.assertEqual(performance['min_response_time'], 0.1)

    def test_accuracy_calculations(self):
        """Prueba que los cálculos de precisión (clasificaciones) son correctos."""
        stats = calculate_statistics(self.mock_results, self.total_valid, self.total_invalid, self.rps, self.endpoint)

        accuracy = stats['accuracy']
        counts = accuracy['classification_counts']

        self.assertEqual(counts['Valido considerado valido'], 2)
        self.assertEqual(counts['Valido considerado invalido'], 1)
        self.assertEqual(counts['Invalido considerado valido'], 1)
        self.assertEqual(counts['Invalido considerado invalido'], 1)
        self.assertEqual(counts['Error'], 1)

        # Tasa de Falsos Positivos = (Invalido considerado valido / Total Inválidos) * 100
        self.assertAlmostEqual(accuracy['false_positive_rate_percent'], (1 / 2) * 100)

        # Tasa de Falsos Negativos = (Valido considerado invalido / Total Válidos) * 100
        self.assertAlmostEqual(accuracy['false_negative_rate_percent'], (1 / 3) * 100)

    def test_summary_data(self):
        """Prueba que los datos del resumen son correctos."""
        stats = calculate_statistics(self.mock_results, self.total_valid, self.total_invalid, self.rps, self.endpoint)

        summary = stats['summary']
        self.assertEqual(summary['total_requests'], 6)
        self.assertEqual(summary['valid_source_emails'], self.total_valid)
        self.assertEqual(summary['invalid_source_emails'], self.total_invalid)
        self.assertEqual(summary['requests_per_second_limit'], self.rps)
        self.assertEqual(summary['api_endpoint'], self.endpoint)

    def test_no_results(self):
        """Prueba cómo se maneja una lista de resultados vacía."""
        stats = calculate_statistics([], 0, 0, 10, "http://empty.api")

        self.assertEqual(stats['summary']['total_requests'], 0)
        self.assertIn('error', stats['summary'])


if __name__ == '__main__':
    unittest.main()

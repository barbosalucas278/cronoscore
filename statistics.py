
from collections import Counter

def calculate_statistics(results, total_valid_source, total_invalid_source, rps, endpoint):
    """
    Calcula y resume las estadísticas de los resultados de la prueba.
    """
    if not results:
        return {
            "summary": {
                "total_requests": 0,
                "error": "No results to process."
            }
        }

    durations = [r['duration'] for r in results if 'duration' in r]
    total_time = sum(durations)
    avg_duration = total_time / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0

    classifications = [r['classification'] for r in results]
    classification_counts = Counter(classifications)

    false_positives = classification_counts.get("Falso Positivo", 0)
    false_negatives = classification_counts.get("Falso Negativo", 0)

    fp_rate = (false_positives / total_invalid_source * 100) if total_invalid_source > 0 else 0
    fn_rate = (false_negatives / total_valid_source * 100) if total_valid_source > 0 else 0

    output_data = {
        "summary": {
            "total_requests": len(results),
            "valid_source_emails": total_valid_source,
            "invalid_source_emails": total_invalid_source,
            "requests_per_second_limit": rps,
            "api_endpoint": endpoint
        },
        "performance": {
            "total_processing_time": total_time,
            "average_response_time": avg_duration,
            "max_response_time": max_duration,
            "min_response_time": min_duration
        },
        "accuracy": {
            "classification_counts": dict(classification_counts),
            "false_positive_rate_percent": fp_rate,
            "false_negative_rate_percent": fn_rate
        },
        "details": results
    }

    return output_data

if __name__ == '__main__':
    # Pruebas para el módulo de estadísticas
    mock_results = [
        {'email': 'valid1@test.com', 'duration': 0.1, 'classification': 'Verdadero Positivo'},
        {'email': 'valid2@test.com', 'duration': 0.2, 'classification': 'Falso Negativo'},
        {'email': 'invalid1@test.com', 'duration': 0.15, 'classification': 'Falso Positivo'},
        {'email': 'invalid2@test.com', 'duration': 0.12, 'classification': 'Verdadero Negativo'},
        {'email': 'error@test.com', 'duration': 0.5, 'classification': 'Error'},
    ]

    total_valid = 2
    total_invalid = 2
    rps_limit = 20
    api_endpoint = "http://fakeapi.com/validate"

    stats = calculate_statistics(mock_results, total_valid, total_invalid, rps_limit, api_endpoint)

    print("Estadísticas Generadas:")
    import json
    print(json.dumps(stats, indent=4))

    # Verificaciones
    assert stats['summary']['total_requests'] == 5
    assert stats['performance']['max_response_time'] == 0.5
    assert stats['accuracy']['classification_counts']['Falso Negativo'] == 1
    assert stats['accuracy']['false_positive_rate_percent'] == 50.0

    print("\nPruebas del módulo de estadísticas pasaron exitosamente.")

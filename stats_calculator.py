
import logging
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)


def calculate_statistics(
    results: list[dict[str, Any]],
    total_valid_source: int,
    total_invalid_source: int,
    rps: int,
    endpoint: str,
) -> dict[str, Any]:
    """
    Calcula y resume las estadísticas de los resultados de la prueba.
    """
    if not results:
        logger.warning("No hay resultados para procesar.")
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

    false_positives = classification_counts.get("Invalido considerado invalido por API", 0)
    false_negatives = classification_counts.get("Valido considerado invalido por API", 0)

    # NOTE: "Invalido considerado valido" = falso positivo (la API dice válido, pero es inválido)
    false_positives = classification_counts.get("Invalido considerado valido", 0)
    false_negatives = classification_counts.get("Valido considerado invalido", 0)

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

    logger.info(
        "Estadísticas calculadas: %d requests, FP=%.2f%%, FN=%.2f%%",
        len(results), fp_rate, fn_rate
    )

    return output_data

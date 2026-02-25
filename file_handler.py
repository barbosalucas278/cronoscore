
import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def read_emails_from_file(file_path: str) -> list[str]:
    """
    Lee una lista de emails desde un archivo, uno por línea.
    Devuelve una lista vacía si el archivo no existe.
    """
    if not os.path.exists(file_path):
        logger.warning("El archivo '%s' no fue encontrado.", file_path)
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        emails = [line.strip() for line in f.readlines() if line.strip()]

    logger.info("Leídos %d emails desde '%s'.", len(emails), file_path)
    return emails


def save_results_to_json(data: dict[str, Any], file_path: str) -> bool:
    """
    Guarda los datos de resultados en un archivo JSON.
    Retorna True si se guardó correctamente, False si hubo error.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info("Resultados guardados en '%s'.", file_path)
        return True
    except IOError as e:
        logger.error("Error al guardar el archivo de resultados: %s", e)
        return False


import asyncio
import aiohttp
import argparse
import json
import time
import os
from collections import Counter

# Constantes Configurables
# Estas son las constantes que el usuario mencionó que cambiaría manualmente si fuera necesario.
# Sin embargo, también se pueden sobrescribir a través de argumentos de línea de comandos.
API_ENDPOINT = "https://api.mails.so/v1/validate"
API_KEY = "0b90acda-a5ef-497f-8e39-f97974682047"
REQUESTS_PER_SECOND = 16
VALID_REASON = "valid_email"  # La 'reason' que indica un email válido

def read_emails_from_file(file_path):
    """Lee una lista de emails desde un archivo, uno por línea."""
    if not os.path.exists(file_path):
        print(f"Alerta: El archivo {file_path} no fue encontrado.")
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

async def process_email(session, email, is_valid_source, api_key, endpoint, valid_reason_str):
    """
    Envía un único email a la API y procesa la respuesta.
    """
    start_time = time.time()
    url = f"{endpoint}?email={email}"
    headers = {"x-mails-api-key": api_key}

    try:
        async with session.get(url, headers=headers) as response:
            duration = time.time() - start_time
            result_json = await response.json()

            # Determina si la API consideró el email como válido
            api_considers_valid = result_json.get("reason") == valid_reason_str

            # Clasifica el resultado
            if is_valid_source and api_considers_valid:
                classification = "Verdadero Positivo"
            elif is_valid_source and not api_considers_valid:
                classification = "Falso Negativo"
            elif not is_valid_source and api_considers_valid:
                classification = "Falso Positivo"
            else: # not is_valid_source and not api_considers_valid
                classification = "Verdadero Negativo"

            return {
                "email": email,
                "duration": duration,
                "classification": classification,
                "response_reason": result_json.get("reason", "N/A")
            }

    except aiohttp.ClientError as e:
        duration = time.time() - start_time
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": str(e)
        }
    except Exception as e:
        duration = time.time() - start_time
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": f"Error inesperado: {str(e)}"
        }

async def main(args):
    """
    Función principal para orquestar las pruebas a la API.
    """
    print("Iniciando prueba de API...")

    # Cargar listas de emails
    valid_emails = read_emails_from_file(args.valid_emails_file)
    invalid_emails = read_emails_from_file(args.invalid_emails_file)

    if not valid_emails and not invalid_emails:
        print("No se encontraron emails para procesar. Abortando.")
        return

    # Combina las listas para procesarlas
    emails_to_process = [(email, True) for email in valid_emails] + \
                        [(email, False) for email in invalid_emails]

    total_requests = len(emails_to_process)
    print(f"Total de emails a procesar: {total_requests}")

    # Configuración del limitador de velocidad
    delay = 1.0 / args.requests_per_second

    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for email, is_valid_source in emails_to_process:
            task = asyncio.create_task(process_email(
                session, email, is_valid_source, args.api_key, args.endpoint, args.valid_reason
            ))
            tasks.append(task)
            await asyncio.sleep(delay) # Respeta el límite de velocidad

        # Espera a que todas las tareas se completen
        processed_results = await asyncio.gather(*tasks)
        results.extend(processed_results)

    print("Prueba completada. Generando estadísticas...")

    # --- Cálculo de Estadísticas ---

    # Tiempos de respuesta
    durations = [r['duration'] for r in results if 'duration' in r]
    total_time = sum(durations)
    avg_duration = total_time / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0

    # Clasificaciones
    classifications = [r['classification'] for r in results]
    classification_counts = Counter(classifications)

    # Métricas de Falsos Positivos/Negativos
    total_valid_source = len(valid_emails)
    total_invalid_source = len(invalid_emails)

    false_positives = classification_counts.get("Falso Positivo", 0)
    false_negatives = classification_counts.get("Falso Negativo", 0)

    fp_rate = (false_positives / total_invalid_source * 100) if total_invalid_source > 0 else 0
    fn_rate = (false_negatives / total_valid_source * 100) if total_valid_source > 0 else 0

    # Ensamblar el output final
    output_data = {
        "summary": {
            "total_requests": total_requests,
            "valid_source_emails": total_valid_source,
            "invalid_source_emails": total_invalid_source,
            "requests_per_second_limit": args.requests_per_second,
            "api_endpoint": args.endpoint
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

    # Guardar resultados en JSON
    with open(args.output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

    print(f"Resultados guardados en '{args.output_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para pruebas de carga y validación de una API de emails.")

    parser.add_argument("--endpoint", type=str, default=API_ENDPOINT,
                        help="URL del endpoint de la API.")
    parser.add_argument("--api-key", type=str, default=API_KEY,
                        help="Tu clave de API para el header 'x-api-key'.")
    parser.add_argument("--requests-per-second", "-rps", type=int, default=REQUESTS_PER_SECOND,
                        help="Número de solicitudes a enviar por segundo.")
    parser.add_argument("--valid-emails-file", type=str, default="valid_emails.txt",
                        help="Archivo con la lista de emails válidos.")
    parser.add_argument("--invalid-emails-file", type=str, default="invalid_emails.txt",
                        help="Archivo con la lista de emails inválidos.")
    parser.add_argument("--output-file", type=str, default="results.json",
                        help="Archivo donde se guardará el output en formato JSON.")
    parser.add_argument("--valid-reason", type=str, default=VALID_REASON,
                        help="El valor de la propiedad 'reason' que la API devuelve para un email válido.")

    args = parser.parse_args()

    asyncio.run(main(args))

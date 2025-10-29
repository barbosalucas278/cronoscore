
import asyncio
from config import get_config
from file_handler import read_emails_from_file, save_results_to_json
from api_client import run_api_tests
from statistics import calculate_statistics

async def main():
    """
    Función principal para orquestar las pruebas a la API.
    """
    # Cargar configuración desde argumentos de línea de comandos
    args = get_config()

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

    # Ejecutar las pruebas
    results = await run_api_tests(
        emails_to_process,
        args.api_key,
        args.endpoint,
        args.requests_per_second,
        args.valid_reason
    )

    print("Prueba completada. Generando estadísticas...")

    # Calcular estadísticas
    stats = calculate_statistics(
        results,
        len(valid_emails),
        len(invalid_emails),
        args.requests_per_second,
        args.endpoint
    )

    # Guardar resultados
    save_results_to_json(stats, args.output_file)

if __name__ == "__main__":
    asyncio.run(main())

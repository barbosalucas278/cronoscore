
import asyncio
import sys
import logging
from config import get_config
from file_handler import read_emails_from_file, save_results_to_json
from api_client import run_api_tests
from stats_calculator import calculate_statistics

logger = logging.getLogger(__name__)


def create_progress_callback(api_name: str, total: int):
    """Crea un callback de progreso que imprime el avance."""
    def on_progress(completed: int, total_count: int) -> None:
        percent = (completed / total_count) * 100 if total_count > 0 else 0
        bar_length = 30
        filled = int(bar_length * completed // total_count)
        bar = '█' * filled + '░' * (bar_length - filled)
        sys.stdout.write(f"\r  [{bar}] {completed}/{total_count} ({percent:.0f}%)")
        sys.stdout.flush()
        if completed == total_count:
            sys.stdout.write("\n")
            sys.stdout.flush()
    return on_progress


async def main():
    """
    Función principal para orquestar las pruebas a las APIs.
    """
    # Cargar configuración desde el archivo JSON y argumentos
    try:
        args = get_config()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except ValueError as e:
        print(f"Error de configuración: {e}")
        return
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        return

    logger.info("Iniciando pruebas de APIs...")

    # Cargar listas de emails
    valid_emails = read_emails_from_file(args.valid_emails_file)
    invalid_emails = read_emails_from_file(args.invalid_emails_file)

    if not valid_emails and not invalid_emails:
        logger.error("No se encontraron emails para procesar. Abortando.")
        return

    emails_to_process = [(email, True) for email in valid_emails] + \
                        [(email, False) for email in invalid_emails]

    total_emails = len(emails_to_process)
    logger.info("Total de emails a procesar por cada API: %d", total_emails)

    # Estructura para almacenar todos los resultados
    all_apis_results = {}

    # Iterar sobre cada API configurada
    for api_config in args.apis:
        api_name = api_config['name']
        api_endpoint = api_config['endpoint']

        logger.info("--- Probando API: %s ---", api_name)
        logger.info("Endpoint: %s", api_endpoint)

        # Crear callback de progreso
        progress_cb = create_progress_callback(api_name, total_emails)

        # Ejecutar las pruebas para la API actual
        results = await run_api_tests(
            emails_to_process,
            api_config,
            args.requests_per_second,
            on_progress=progress_cb,
        )

        logger.info("Prueba para '%s' completada. Generando estadísticas...", api_name)

        # Calcular estadísticas para la API actual
        stats = calculate_statistics(
            results,
            len(valid_emails),
            len(invalid_emails),
            args.requests_per_second,
            api_endpoint,
        )

        # Guardar las estadísticas en el diccionario general
        all_apis_results[api_name] = stats

    # Guardar todos los resultados consolidados
    final_output = {
        "global_summary": {
            "total_apis_tested": len(args.apis),
            "total_emails_per_api": total_emails,
        },
        "individual_api_results": all_apis_results
    }

    save_results_to_json(final_output, "results.json")
    logger.info("Proceso finalizado exitosamente.")


if __name__ == "__main__":
    asyncio.run(main())

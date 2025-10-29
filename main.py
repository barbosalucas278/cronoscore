
import asyncio
from config import get_config
from file_handler import read_emails_from_file, save_results_to_json
from api_client import run_api_tests
from statistics import calculate_statistics

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
    except Exception as e:
        print(f"Error al cargar la configuración: {e}")
        return

    print("Iniciando pruebas de APIs...")

    # Cargar listas de emails
    valid_emails = read_emails_from_file(args.valid_emails_file)
    invalid_emails = read_emails_from_file(args.invalid_emails_file)

    if not valid_emails and not invalid_emails:
        print("No se encontraron emails para procesar. Abortando.")
        return

    emails_to_process = [(email, True) for email in valid_emails] + \
                        [(email, False) for email in invalid_emails]

    total_emails = len(emails_to_process)
    print(f"Total de emails a procesar por cada API: {total_emails}")

    # Estructura para almacenar todos los resultados
    all_apis_results = {}

    # Iterar sobre cada API configurada
    for api_config in args.apis:
        api_name = api_config['name']
        api_endpoint = api_config['endpoint']
        api_key = api_config['api_key']
        validation_rule = api_config['validation_rule']

        print(f"\n--- Probando API: {api_name} ---")
        print(f"Endpoint: {api_endpoint}")

        # Ejecutar las pruebas para la API actual
        results = await run_api_tests(
            emails_to_process,
            api_key,
            api_endpoint,
            args.requests_per_second,
            validation_rule
        )

        print(f"Prueba para '{api_name}' completada. Generando estadísticas...")

        # Calcular estadísticas para la API actual
        stats = calculate_statistics(
            results,
            len(valid_emails),
            len(invalid_emails),
            args.requests_per_second,
            api_endpoint  # Pasamos el endpoint para que quede registrado
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

if __name__ == "__main__":
    asyncio.run(main())

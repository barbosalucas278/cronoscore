
import argparse
import json
import os

# Constantes Configurables
REQUESTS_PER_SECOND = 16
VALID_REASON = "valid_email"
DEFAULT_CONFIG_FILE = "apis_config.json"

def load_apis_config(file_path):
    """
    Carga la configuración de las APIs desde un archivo JSON.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo de configuración '{file_path}' no fue encontrado.")

    with open(file_path, 'r') as f:
        return json.load(f)

def get_config():
    """
    Configura y devuelve los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(description="Script para pruebas de carga y validación de múltiples APIs de emails.")

    parser.add_argument("--config-file", type=str, default=DEFAULT_CONFIG_FILE,
                        help=f"Archivo JSON con la configuración de las APIs. Por defecto: {DEFAULT_CONFIG_FILE}")
    parser.add_argument("--requests-per-second", "-rps", type=int, default=REQUESTS_PER_SECOND,
                        help="Número de solicitudes a enviar por segundo.")
    parser.add_argument("--valid-emails-file", type=str, default="valid_emails.txt",
                        help="Archivo con la lista de emails válidos.")
    parser.add_argument("--invalid-emails-file", type=str, default="invalid_emails.txt",
                        help="Archivo con la lista de emails inválidos.")

    args = parser.parse_args()

    # Cargar la configuración de las APIs
    args.apis = load_apis_config(args.config_file)

    return args

if __name__ == '__main__':
    # Esto permite probar el módulo de forma independiente
    try:
        args = get_config()
        print("Configuración general cargada:")
        print(f"- RPS: {args.requests_per_second}")
        print("\nAPIs a probar:")
        for api in args.apis:
            print(f"- Nombre: {api['name']}")
            print(f"  Endpoint: {api['endpoint']}")
            print(f"  API Key: {'*' * (len(api['api_key']) - 4) + api['api_key'][-4:]}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

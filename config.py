
import argparse

# Constantes Configurables
API_ENDPOINT = "https://api.example.com/validate"
API_KEY = "DEFAULT_API_KEY"
REQUESTS_PER_SECOND = 16
VALID_REASON = "valid_email"

def get_config():
    """
    Configura y devuelve los argumentos de línea de comandos.
    """
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

    return parser.parse_args()

if __name__ == '__main__':
    # Esto permite probar el módulo de forma independiente
    args = get_config()
    print("Configuración cargada:")
    print(f"- Endpoint: {args.endpoint}")
    print(f"- API Key: {'*' * (len(args.api_key) - 4) + args.api_key[-4:]}")
    print(f"- RPS: {args.requests_per_second}")

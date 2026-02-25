
import os
import logging
import argparse
import json
from typing import Any

logger = logging.getLogger(__name__)

# Constantes Configurables
REQUESTS_PER_SECOND = 16
DEFAULT_CONFIG_FILE = "apis_config.json"
DEFAULT_REQUEST_TIMEOUT = 30  # segundos


def load_apis_config(file_path: str) -> list[dict[str, Any]]:
    """
    Carga la configuración de las APIs desde un archivo JSON.
    Valida que cada API tenga los campos requeridos.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo de configuración '{file_path}' no fue encontrado.")

    with open(file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if not isinstance(config, list):
        raise ValueError("El archivo de configuración debe contener una lista de APIs.")

    required_fields = {"name", "endpoint", "api_key", "validation_rules"}
    for i, api in enumerate(config):
        missing = required_fields - set(api.keys())
        if missing:
            raise ValueError(
                f"La API en la posición {i} le faltan los campos: {', '.join(missing)}"
            )

        # Soporte para variables de entorno en api_key
        api_key = api["api_key"]
        if api_key.startswith("$"):
            env_var = api_key[1:]
            env_value = os.getenv(env_var)
            if not env_value:
                raise ValueError(
                    f"La API '{api['name']}' usa la variable de entorno '{env_var}' "
                    f"pero no está definida."
                )
            api["api_key"] = env_value
            logger.info("API key para '%s' cargada desde variable de entorno '%s'.", api["name"], env_var)

        # Validar reglas de validación
        if not isinstance(api.get("validation_rules"), list):
            raise ValueError(
                f"La API '{api['name']}' debe tener 'validation_rules' como lista."
            )

        # Valores por defecto para configuración de request
        api.setdefault("method", "GET")
        api.setdefault("headers", {})
        api.setdefault("param_name", "email")
        api.setdefault("response_path", "data")
        api.setdefault("timeout", DEFAULT_REQUEST_TIMEOUT)
        api.setdefault("mode", "sync")

        # Validar modo
        mode = api["mode"]
        if mode not in ("sync", "webhook"):
            raise ValueError(
                f"La API '{api['name']}' tiene un modo inválido: '{mode}'. "
                f"Valores permitidos: 'sync', 'webhook'."
            )

        # Validar configuración de webhook
        if mode == "webhook":
            webhook_cfg = api.get("webhook")
            if not isinstance(webhook_cfg, dict):
                raise ValueError(
                    f"La API '{api['name']}' con modo 'webhook' debe tener "
                    f"un objeto 'webhook' con la configuración del callback."
                )

            webhook_cfg.setdefault("callback_param", "callback_url")
            webhook_cfg.setdefault("timeout", 120)
            webhook_cfg.setdefault("result_path", api.get("response_path", "data"))

            logger.info(
                "API '%s' configurada en modo webhook (callback_param='%s', timeout=%ds).",
                api["name"], webhook_cfg["callback_param"], webhook_cfg["timeout"],
            )

    logger.info("Configuración cargada: %d APIs encontradas.", len(config))
    return config


def get_config() -> argparse.Namespace:
    """
    Configura y devuelve los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Script para pruebas de carga y validación de múltiples APIs de emails."
    )

    parser.add_argument(
        "--config-file", type=str, default=DEFAULT_CONFIG_FILE,
        help=f"Archivo JSON con la configuración de las APIs. Por defecto: {DEFAULT_CONFIG_FILE}"
    )
    parser.add_argument(
        "--requests-per-second", "-rps", type=int, default=REQUESTS_PER_SECOND,
        help="Número de solicitudes a enviar por segundo."
    )
    parser.add_argument(
        "--valid-emails-file", type=str, default="valid_emails.txt",
        help="Archivo con la lista de emails válidos."
    )
    parser.add_argument(
        "--invalid-emails-file", type=str, default="invalid_emails.txt",
        help="Archivo con la lista de emails inválidos."
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de logging. Por defecto: INFO"
    )

    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

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
            masked_key = '*' * max(0, len(api['api_key']) - 4) + api['api_key'][-4:]
            print(f"  API Key: {masked_key}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

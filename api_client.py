
from __future__ import annotations

import aiohttp
import time
import asyncio
import operator
import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from webhook_server import WebhookServer

logger = logging.getLogger(__name__)


def resolve_field(data: dict[str, Any], field_path: str) -> Any:
    """
    Resuelve un campo usando dot notation.
    Ejemplo: 'data.nested.field' → data['data']['nested']['field']
    """
    keys = field_path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
        if current is None:
            return None
    return current


def evaluate_rule(api_response: dict[str, Any], rule: dict[str, Any], response_path: str = "data") -> bool:
    """
    Evalúa una única regla de validación contra la respuesta de la API.
    Soporta dot notation para acceder a campos anidados.
    """
    field = rule.get("field")
    op_str = rule.get("operator")
    value = rule.get("value")

    # Construir la ruta completa: response_path + field
    full_path = f"{response_path}.{field}" if response_path else field

    # Resolver el campo usando dot notation
    actual_value = resolve_field(api_response, full_path)

    if actual_value is None:
        logger.debug("Campo '%s' no encontrado en la respuesta.", full_path)
        return False

    # Mapeo de operadores
    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        'in': lambda a, b: a in b,
    }

    op_func = ops.get(op_str)
    if not op_func:
        raise ValueError(f"Operador no válido: {op_str}")

    # Convertir a int si es necesario para comparaciones numéricas
    try:
        if op_str in ['>', '<', '>=', '<=']:
            actual_value = int(actual_value)
            value = int(value)
    except (ValueError, TypeError):
        logger.debug("No se pudo convertir a número para la comparación de '%s'.", field)
        return False

    return op_func(actual_value, value)


async def process_email(
    session: aiohttp.ClientSession,
    email: str,
    is_valid_source: bool,
    api_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Envía un único email a la API y procesa la respuesta.
    La configuración de request (método, headers, params) es configurable por API.
    """
    start_time = time.time()

    api_key = api_config["api_key"]
    endpoint = api_config["endpoint"]
    validation_rules = api_config["validation_rules"]
    method = api_config.get("method", "GET").upper()
    custom_headers = api_config.get("headers", {})
    param_name = api_config.get("param_name", "email")
    response_path = api_config.get("response_path", "data")
    timeout_seconds = api_config.get("timeout", 30)

    # Construir headers: siempre incluir api_key, más los custom
    headers = {"x-mails-api-key": api_key}
    headers.update(custom_headers)

    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    try:
        if method == "GET":
            url = f"{endpoint}?{param_name}={email}"
            async with session.get(url, headers=headers, timeout=timeout) as response:
                duration = time.time() - start_time
                result_json = await response.json()
        elif method == "POST":
            url = endpoint
            payload = {param_name: email}
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
                duration = time.time() - start_time
                result_json = await response.json()
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")

        # Evaluar todas las reglas de validación
        api_considers_valid = all(
            evaluate_rule(result_json, rule, response_path) for rule in validation_rules
        )

        if is_valid_source and api_considers_valid:
            classification = "Valido considerado valido"
        elif is_valid_source and not api_considers_valid:
            classification = "Valido considerado invalido"
        elif not is_valid_source and api_considers_valid:
            classification = "Invalido considerado valido"
        else:
            classification = "Invalido considerado invalido"

        # Extraer reason de la respuesta usando response_path
        response_data = resolve_field(result_json, response_path) if response_path else result_json
        response_reason = None
        if isinstance(response_data, dict):
            response_reason = response_data.get("reason")

        return {
            "email": email,
            "duration": duration,
            "classification": classification,
            "response_reason": response_reason,
            "raw_response": result_json,
        }

    except asyncio.TimeoutError:
        duration = time.time() - start_time
        logger.warning("Timeout para email '%s' después de %.2fs.", email, duration)
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": f"Timeout después de {timeout_seconds}s",
        }
    except aiohttp.ClientError as e:
        duration = time.time() - start_time
        logger.error("Error de cliente para '%s': %s", email, str(e))
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": str(e),
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error("Error inesperado para '%s': %s", email, str(e))
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": f"Error inesperado: {str(e)}",
        }


async def process_email_webhook(
    session: aiohttp.ClientSession,
    email: str,
    is_valid_source: bool,
    api_config: dict[str, Any],
    webhook_server: WebhookServer,
) -> dict[str, Any]:
    """
    Envía un email a la API en modo webhook: incluye un callback_url
    y espera a que el proveedor envíe el resultado vía POST.
    """
    start_time = time.time()

    api_key = api_config["api_key"]
    endpoint = api_config["endpoint"]
    validation_rules = api_config["validation_rules"]
    method = api_config.get("method", "POST").upper()
    custom_headers = api_config.get("headers", {})
    param_name = api_config.get("param_name", "email")
    response_path = api_config.get("response_path", "data")

    webhook_cfg = api_config.get("webhook", {})
    callback_param = webhook_cfg.get("callback_param", "callback_url")
    callback_wrapper_param = webhook_cfg.get("callback_wrapper_param")
    webhook_timeout = webhook_cfg.get("timeout", 120)
    id_field = webhook_cfg.get("id_field")
    result_path = webhook_cfg.get("result_path", response_path)

    headers = {"x-mails-api-key": api_key}
    headers.update(custom_headers)

    # Crear callback pendiente en el servidor de webhooks
    request_id, callback_url, future = webhook_server.create_callback()

    # Construir el payload con el callback URL
    payload: dict[str, Any] = {param_name: email}

    if callback_wrapper_param:
        # Envolver: {"webhook": {"callback_url": "..."}}
        payload[callback_wrapper_param] = {callback_param: callback_url}
    else:
        # Parámetro plano: {"callback_url": "..."}
        payload[callback_param] = callback_url

    timeout = aiohttp.ClientTimeout(total=webhook_timeout)

    try:
        # 1. Enviar solicitud a la API
        if method == "POST":
            async with session.post(endpoint, headers=headers, json=payload, timeout=timeout) as response:
                initial_json = await response.json()
        elif method == "GET":
            params = {param_name: email}
            if callback_wrapper_param:
                params[f"{callback_wrapper_param}[{callback_param}]"] = callback_url
            else:
                params[callback_param] = callback_url
            async with session.get(endpoint, headers=headers, params=params, timeout=timeout) as response:
                initial_json = await response.json()
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")

        logger.debug(
            "Solicitud webhook enviada para '%s', request_id=%s, respuesta inicial: %s",
            email, request_id, initial_json,
        )

        # 2. Esperar el callback del proveedor
        try:
            webhook_payload = await asyncio.wait_for(future, timeout=webhook_timeout)
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.warning(
                "Timeout de webhook para '%s' (request_id=%s) después de %ds.",
                email, request_id, webhook_timeout,
            )
            return {
                "email": email,
                "duration": duration,
                "classification": "Error",
                "error_message": f"Webhook timeout después de {webhook_timeout}s",
            }

        duration = time.time() - start_time

        # 3. Evaluar reglas de validación sobre el payload del webhook
        api_considers_valid = all(
            evaluate_rule(webhook_payload, rule, result_path)
            for rule in validation_rules
        )

        if is_valid_source and api_considers_valid:
            classification = "Valido considerado valido"
        elif is_valid_source and not api_considers_valid:
            classification = "Valido considerado invalido"
        elif not is_valid_source and api_considers_valid:
            classification = "Invalido considerado valido"
        else:
            classification = "Invalido considerado invalido"

        # Extraer reason del payload del webhook
        response_data = resolve_field(webhook_payload, result_path) if result_path else webhook_payload
        response_reason = None
        if isinstance(response_data, dict):
            response_reason = response_data.get("reason")

        return {
            "email": email,
            "duration": duration,
            "classification": classification,
            "response_reason": response_reason,
            "raw_response": webhook_payload,
        }

    except asyncio.TimeoutError:
        duration = time.time() - start_time
        logger.warning("Timeout de solicitud para '%s' después de %.2fs.", email, duration)
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": f"Timeout de solicitud después de {webhook_timeout}s",
        }
    except aiohttp.ClientError as e:
        duration = time.time() - start_time
        logger.error("Error de cliente para '%s': %s", email, str(e))
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": str(e),
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error("Error inesperado (webhook) para '%s': %s", email, str(e))
        return {
            "email": email,
            "duration": duration,
            "classification": "Error",
            "error_message": f"Error inesperado: {str(e)}",
        }


async def run_api_tests(
    emails_to_process: list[tuple[str, bool]],
    api_config: dict[str, Any],
    rps: int,
    on_progress: Any = None,
    webhook_server: WebhookServer | None = None,
) -> list[dict[str, Any]]:
    """
    Ejecuta las pruebas de API para una lista de emails.
    on_progress es un callback opcional que recibe (completados, total).
    Si api_config["mode"] == "webhook" y webhook_server está disponible,
    usa el flujo de webhook en lugar del flujo síncrono.
    """
    delay = 1.0 / rps
    results: list[dict[str, Any]] = []
    total = len(emails_to_process)

    mode = api_config.get("mode", "sync")
    use_webhook = mode == "webhook" and webhook_server is not None

    if use_webhook:
        logger.info("Ejecutando pruebas en modo webhook para '%s'.", api_config.get("name", "?"))
    else:
        logger.info("Ejecutando pruebas en modo sync para '%s'.", api_config.get("name", "?"))

    async with aiohttp.ClientSession() as session:
        tasks = []
        for email, is_valid_source in emails_to_process:
            if use_webhook:
                task = asyncio.create_task(
                    process_email_webhook(
                        session, email, is_valid_source, api_config, webhook_server,
                    )
                )
            else:
                task = asyncio.create_task(
                    process_email(session, email, is_valid_source, api_config)
                )
            tasks.append(task)
            await asyncio.sleep(delay)

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            results.append(result)
            if on_progress:
                on_progress(i + 1, total)

    logger.info("Prueba completada: %d emails procesados.", len(results))
    return results

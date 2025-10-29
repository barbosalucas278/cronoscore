
import aiohttp
import time
import asyncio
import operator

def evaluate_rule(api_response, rule):
    """
    Evalúa una única regla de validación contra la respuesta de la API.
    """
    field = rule.get("field")
    op_str = rule.get("operator")
    value = rule.get("value")

    # Obtener el valor real de la respuesta de la API
    actual_value = api_response.get("data", {}).get(field)

    if actual_value is None:
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
        return False # No se pudo convertir a número para la comparación

    return op_func(actual_value, value)

async def process_email(session, email, is_valid_source, api_key, endpoint, validation_rules):
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

            # Evaluar todas las reglas de validación
            api_considers_valid = all(evaluate_rule(result_json, rule) for rule in validation_rules)

            if is_valid_source and api_considers_valid:
                classification = "Valido considerado valido"
            elif is_valid_source and not api_considers_valid:
                classification = "Valido considerado invalido"
            elif not is_valid_source and api_considers_valid:
                classification = "Invalido considerado valido"
            else:
                classification = "Invalido considerado Invalido"

            return {
                "email": email,
                "duration": duration,
                "classification": classification,
                "response_reason": result_json.get("data", {}).get("reason")
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

async def run_api_tests(emails_to_process, api_key, endpoint, rps, validation_rules):
    """
    Ejecuta las pruebas de API para una lista de emails.
    """
    delay = 1.0 / rps
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for email, is_valid_source in emails_to_process:
            task = asyncio.create_task(
                process_email(session, email, is_valid_source, api_key, endpoint, validation_rules)
            )
            tasks.append(task)
            await asyncio.sleep(delay)

        processed_results = await asyncio.gather(*tasks)
        results.extend(processed_results)

    return results

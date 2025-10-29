
import aiohttp
import time
import asyncio

async def process_email(session, email, is_valid_source, api_key, endpoint, validation_rule):
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
            print(result_json)

            # Lógica de validación dinámica
            score_field = validation_rule.get("score_field")
            result_field = validation_rule.get("result_field")
            score_value = validation_rule.get("score_value")
            result_value = validation_rule.get("result_value")

            score = result_json.get("data", {}).get(score_field)
            result = result_json.get("data", {}).get(result_field)

            api_considers_valid = (score is not None and int(score) >= int(score_value)) and \
                                  (result == result_value or result == "deliverable")

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
                "response_reason": result_json.get("data").get("reason")
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

async def run_api_tests(emails_to_process, api_key, endpoint, rps, validation_rule):
    """
    Ejecuta las pruebas de API para una lista de emails.
    """
    delay = 1.0 / rps
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for email, is_valid_source in emails_to_process:
            task = asyncio.create_task(
                process_email(session, email, is_valid_source, api_key, endpoint, validation_rule)
            )
            tasks.append(task)
            await asyncio.sleep(delay)

        processed_results = await asyncio.gather(*tasks)
        results.extend(processed_results)

    return results

if __name__ == '__main__':
    # Esta sección es para pruebas y demostraciones.
    # Para ejecutarla, necesitarás una API de prueba o simularla.

    async def mock_server(request):
        email = request.query.get("email", "")
        if "valid" in email:
            return aiohttp.web.json_response({"reason": "valid_email"})
        elif "invalid" in email:
            return aiohttp.web.json_response({"reason": "invalid_email"})
        else:
            return aiohttp.web.json_response({"reason": "unknown_error"}, status=500)

    async def main_test():
        # Configuración del servidor mock
        app = aiohttp.web.Application()
        app.router.add_get("/validate", mock_server)
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        print("Servidor mock iniciado en http://localhost:8080")

        # Configuración de la prueba
        test_emails = [("valid@example.com", True), ("invalid@example.com", False)]
        api_key = "test_key"
        endpoint = "http://localhost:8080/validate"
        rps = 10
        valid_reason = "valid_email"

        # Ejecutar la prueba
        results = await run_api_tests(test_emails, api_key, endpoint, rps, valid_reason)
        print("\nResultados de la prueba:")
        for res in results:
            print(res)

        # Verificar resultados
        assert len(results) == 2
        assert results[0]['classification'] == 'Valido considerado valido'
        assert results[1]['classification'] == 'Invalido considerado Invalido'
        print("\nPruebas del cliente API pasaron exitosamente.")

        # Detener el servidor
        await runner.cleanup()
        print("Servidor mock detenido.")

    # Ejecutar el bucle de eventos de asyncio
    asyncio.run(main_test())

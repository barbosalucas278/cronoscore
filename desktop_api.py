
import os
import sys
import json
import asyncio
import logging
import threading
from typing import Any

from config import load_apis_config, DEFAULT_CONFIG_FILE
from file_handler import read_emails_from_file, save_results_to_json
from api_client import run_api_tests
from stats_calculator import calculate_statistics
from webhook_server import WebhookServer

logger = logging.getLogger(__name__)

# Configurar logging para la app de escritorio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_base_path() -> str:
    """Retorna la ruta base del proyecto."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class DesktopApi:
    """
    API bridge entre Python y JavaScript para pywebview.
    Cada método público es accesible desde JS via window.pywebview.api.method_name()
    """

    def __init__(self):
        self._window = None
        self._base_path = get_base_path()
        self._is_running = False
        self._progress = {"status": "idle", "completed": 0, "total": 0, "current_api": "", "log": []}

    def set_window(self, window):
        self._window = window

    def _path(self, filename: str) -> str:
        return os.path.join(self._base_path, filename)

    # ── Configuración ──

    def load_config(self) -> dict[str, Any]:
        """Carga apis_config.json y retorna su contenido."""
        try:
            config_path = self._path(DEFAULT_CONFIG_FILE)
            if not os.path.exists(config_path):
                return {"success": False, "error": "Archivo apis_config.json no encontrado."}

            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_config(self, config_json: str) -> dict[str, Any]:
        """Guarda la configuración de APIs."""
        try:
            data = json.loads(config_json)
            config_path = self._path(DEFAULT_CONFIG_FILE)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Emails ──

    def load_emails(self, email_type: str) -> dict[str, Any]:
        """Lee emails válidos o inválidos."""
        filename = "valid_emails.txt" if email_type == "valid" else "invalid_emails.txt"
        filepath = self._path(filename)
        try:
            if not os.path.exists(filepath):
                return {"success": True, "data": ""}
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "data": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_emails(self, email_type: str, content: str) -> dict[str, Any]:
        """Guarda emails editados."""
        filename = "valid_emails.txt" if email_type == "valid" else "invalid_emails.txt"
        filepath = self._path(filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Ejecución de pruebas ──

    def get_progress(self) -> dict[str, Any]:
        """Retorna el estado actual de progreso."""
        return self._progress.copy()

    def run_tests(self, rps: int = 16) -> dict[str, Any]:
        """Lanza las pruebas en un hilo separado."""
        if self._is_running:
            return {"success": False, "error": "Ya hay una prueba en ejecución."}

        self._is_running = True
        self._progress = {"status": "starting", "completed": 0, "total": 0, "current_api": "", "log": []}

        thread = threading.Thread(target=self._run_tests_sync, args=(rps,), daemon=True)
        thread.start()

        return {"success": True, "message": "Pruebas iniciadas."}

    def _run_tests_sync(self, rps: int):
        """Ejecuta las pruebas sincrónicamente en un hilo."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_tests_async(rps))
        except Exception as e:
            self._progress["status"] = "error"
            self._progress["log"].append(f"Error fatal: {str(e)}")
            logger.error("Error en run_tests: %s", e)
        finally:
            self._is_running = False
            loop.close()

    async def _run_tests_async(self, rps: int):
        """Lógica async de pruebas."""
        self._add_log("Cargando configuración...")

        try:
            apis = load_apis_config(self._path(DEFAULT_CONFIG_FILE))
        except Exception as e:
            self._progress["status"] = "error"
            self._add_log(f"Error de configuración: {str(e)}")
            return

        valid_emails = read_emails_from_file(self._path("valid_emails.txt"))
        invalid_emails = read_emails_from_file(self._path("invalid_emails.txt"))

        if not valid_emails and not invalid_emails:
            self._progress["status"] = "error"
            self._add_log("No se encontraron emails para procesar.")
            return

        emails_to_process = [(e, True) for e in valid_emails] + [(e, False) for e in invalid_emails]
        total_emails = len(emails_to_process)

        self._add_log(f"Emails a procesar por API: {total_emails}")
        self._progress["total"] = total_emails * len(apis)

        # ── Webhook server: iniciar si alguna API lo necesita ──
        needs_webhook = any(api.get("mode") == "webhook" for api in apis)
        wh_server: WebhookServer | None = None

        if needs_webhook:
            wh_server = WebhookServer()
            try:
                await wh_server.start()
                self._add_log("Servidor de webhooks iniciado.")
            except Exception as e:
                self._progress["status"] = "error"
                self._add_log(f"Error al iniciar servidor de webhooks: {str(e)}")
                return

        all_apis_results = {}
        global_completed = 0

        try:
            for api_config in apis:
                api_name = api_config['name']
                mode = api_config.get('mode', 'sync')
                self._progress["current_api"] = api_name
                self._progress["status"] = "running"
                self._add_log(f"Probando API: {api_name} (modo: {mode})...")

                def on_progress(completed, total):
                    nonlocal global_completed
                    self._progress["completed"] = global_completed + completed

                results = await run_api_tests(
                    emails_to_process,
                    api_config,
                    rps,
                    on_progress=on_progress,
                    webhook_server=wh_server,
                )

                global_completed += total_emails

                stats = calculate_statistics(
                    results,
                    len(valid_emails),
                    len(invalid_emails),
                    rps,
                    api_config['endpoint'],
                )

                all_apis_results[api_name] = stats
                fp = stats['accuracy']['false_positive_rate_percent']
                fn = stats['accuracy']['false_negative_rate_percent']
                avg = stats['performance']['average_response_time']
                self._add_log(f"✓ {api_name}: FP={fp:.1f}%, FN={fn:.1f}%, Avg={avg:.3f}s")
        finally:
            # Siempre detener el servidor de webhooks
            if wh_server:
                await wh_server.stop()
                self._add_log("Servidor de webhooks detenido.")

        final_output = {
            "global_summary": {
                "total_apis_tested": len(apis),
                "total_emails_per_api": total_emails,
            },
            "individual_api_results": all_apis_results
        }

        save_results_to_json(final_output, self._path("results.json"))
        self._progress["status"] = "completed"
        self._progress["completed"] = self._progress["total"]
        self._add_log("¡Pruebas completadas! Los resultados están listos.")

    def _add_log(self, message: str):
        self._progress["log"].append(message)
        logger.info(message)

    # ── Resultados ──

    def get_last_results(self) -> dict[str, Any]:
        """Lee results.json si existe."""
        results_path = self._path("results.json")
        try:
            if not os.path.exists(results_path):
                return {"success": False, "error": "No hay resultados previos. Ejecutá las pruebas primero."}

            with open(results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_csv(self, api_name: str, details_json: str) -> dict[str, Any]:
        """Abre diálogo Guardar Como y exporta CSV."""
        try:
            if not self._window:
                return {"success": False, "error": "No se pudo acceder a la ventana."}

            result = self._window.create_file_dialog(
                dialog_type=2,  # SAVE_DIALOG
                file_types=('CSV Files (*.csv)',),
                save_filename=f'cronoscore_{api_name}_results.csv',
            )

            if not result:
                return {"success": False, "error": "Exportación cancelada."}

            save_path = result if isinstance(result, str) else result[0]
            details = json.loads(details_json)

            with open(save_path, 'w', encoding='utf-8') as f:
                f.write("Email,Duration (s),Classification,Reason/Error\n")
                for d in details:
                    email = d.get('email', '')
                    duration = f"{d['duration']:.4f}" if d.get('duration') else ''
                    classification = d.get('classification', '')
                    reason = d.get('response_reason') or d.get('error_message', '')
                    f.write(f'"{email}",{duration},"{classification}","{reason}"\n')

            return {"success": True, "path": save_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

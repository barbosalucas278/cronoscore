
import asyncio
import logging
import uuid
from typing import Any

from aiohttp import web

logger = logging.getLogger(__name__)


class WebhookServer:
    """
    Servidor HTTP local para recibir callbacks de webhooks.
    Cada solicitud de validación obtiene un request_id único.
    Cuando el proveedor envía el resultado al callback URL,
    el Future correspondiente se resuelve con el payload.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765, base_url: str | None = None):
        """
        Args:
            host: Dirección en la que escuchar.
            port: Puerto en el que escuchar.
            base_url: URL pública base (ej. de ngrok). Si no se da,
                      se usa http://{host}:{port}.
        """
        self._host = host
        self._port = port
        self._base_url = base_url or f"http://{host}:{port}"

        # Mapa de request_id → asyncio.Future pendiente
        self._pending: dict[str, asyncio.Future] = {}

        self._app: web.Application | None = None
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None

    # ── Ciclo de vida ───────────────────────────────────────────────

    async def start(self) -> None:
        """Inicia el servidor HTTP."""
        self._app = web.Application()
        self._app.router.add_post("/webhook/{request_id}", self._handle_webhook)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()

        logger.info("Webhook server escuchando en %s:%s", self._host, self._port)

    async def stop(self) -> None:
        """Detiene el servidor y cancela Futures pendientes."""
        # Cancelar todos los futures pendientes
        for req_id, future in self._pending.items():
            if not future.done():
                future.cancel()
                logger.debug("Future cancelado para request_id=%s", req_id)

        self._pending.clear()

        if self._runner:
            await self._runner.cleanup()
            logger.info("Webhook server detenido.")

    # ── API pública ─────────────────────────────────────────────────

    def create_callback(self, request_id: str | None = None) -> tuple[str, str, asyncio.Future]:
        """
        Registra un callback pendiente.

        Args:
            request_id: ID de la solicitud (se genera uno si no se proporciona).

        Returns:
            Tupla (request_id, callback_url, future).
              - request_id: identificador único de esta solicitud
              - callback_url: URL completa donde el proveedor debe enviar el resultado
              - future: se resuelve con el payload JSON del webhook
        """
        if request_id is None:
            request_id = uuid.uuid4().hex

        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self._pending[request_id] = future

        callback_url = f"{self._base_url}/webhook/{request_id}"
        logger.debug("Callback registrado: %s → %s", request_id, callback_url)

        return request_id, callback_url, future

    @property
    def pending_count(self) -> int:
        """Cantidad de callbacks pendientes."""
        return sum(1 for f in self._pending.values() if not f.done())

    # ── Handler interno ─────────────────────────────────────────────

    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """Recibe un POST del proveedor y resuelve el Future correspondiente."""
        request_id = request.match_info["request_id"]

        future = self._pending.get(request_id)
        if future is None:
            logger.warning("Webhook recibido para request_id desconocido: %s", request_id)
            return web.json_response(
                {"error": "request_id desconocido"},
                status=404,
            )

        if future.done():
            logger.warning("Webhook duplicado para request_id: %s", request_id)
            return web.json_response(
                {"error": "callback ya procesado"},
                status=409,
            )

        try:
            payload = await request.json()
        except Exception:
            logger.error("Payload inválido para request_id=%s", request_id)
            return web.json_response(
                {"error": "payload JSON inválido"},
                status=400,
            )

        future.set_result(payload)
        logger.info("Webhook resuelto para request_id=%s", request_id)

        return web.json_response({"status": "ok"})

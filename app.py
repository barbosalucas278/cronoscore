
import os
import sys
import webview
from desktop_api import DesktopApi


def get_resource_path(filename: str) -> str:
    """Resuelve la ruta a un recurso empaquetado (PyInstaller) o local."""
    if getattr(sys, 'frozen', False):
        # Cuando se ejecuta como .exe, los archivos bundleados están en _MEIPASS
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def main():
    api = DesktopApi()

    html_path = get_resource_path("app.html")

    if not os.path.exists(html_path):
        print(f"Error: No se encontró '{html_path}'.")
        sys.exit(1)

    # Crear ventana
    window = webview.create_window(
        title="CronoScore",
        url=html_path,
        js_api=api,
        width=1320,
        height=860,
        min_size=(900, 600),
    )

    api.set_window(window)

    # Iniciar la app
    webview.start(debug=False)


if __name__ == "__main__":
    main()


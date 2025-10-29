# Probador de APIs de Validación de Email

Este proyecto contiene un script de Python para realizar pruebas de carga y precisión a una API de validación de emails. El script envía una lista de correos electrónicos (válidos e inválidos), mide el rendimiento de la API y calcula métricas clave como tasas de falsos positivos y falsos negativos.

Los resultados se guardan en un archivo `results.json`, que puede ser visualizado en un dashboard interactivo.

## Características

- **Pruebas Concurrentes**: Utiliza `asyncio` y `aiohttp` para enviar solicitudes de forma asíncrona y eficiente.
- **Limitador de Velocidad**: Controla el número de solicitudes por segundo para no exceder los límites de la API.
- **Configurable**: Acepta parámetros de línea de comandos para personalizar el endpoint de la API, la clave de API, la velocidad de las solicitudes y los archivos de entrada/salida.
- **Análisis Detallado**: Calcula estadísticas sobre los tiempos de respuesta (promedio, máximo, mínimo) y la precisión (verdaderos/falsos positivos/negativos).
- **Dashboard Interactivo**: Incluye un archivo `dashboard.html` para visualizar los resultados de forma gráfica.

## Estructura del Proyecto

```
.
├── api_tester.py             # El script principal de Python para las pruebas
├── valid_emails.txt          # Lista de emails que se sabe que son válidos
├── invalid_emails.txt        # Lista de emails que se sabe que son inválidos
├── dashboard.html            # El dashboard para visualizar los resultados
├── requirements.txt          # Las dependencias de Python
└── README.md                 # Este archivo
```

## Cómo Empezar

### 1. Prerrequisitos

- Python 3.7 o superior.

### 2. Instalación

1.  **Clona o descarga este repositorio.**

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuración

1.  **Edita `valid_emails.txt`**: Añade los correos electrónicos que quieres probar y que esperas que sean válidos, uno por línea.
2.  **Edita `invalid_emails.txt`**: Añade los correos que esperas que la API marque como inválidos.
3.  Puedes modificar las constantes dentro de `api_tester.py` o, preferiblemente, usar los argumentos de la línea de comandos para configurar el script.

### 4. Ejecución del Script

Ejecuta el script desde tu terminal. Aquí tienes un ejemplo básico:

```bash
python api_tester.py --endpoint "https://TU_API_ENDPOINT/validate" --api-key "TU_API_KEY_REAL"
```

**Argumentos Disponibles:**

-   `--endpoint`: La URL completa de la API a la que quieres apuntar.
-   `--api-key`: Tu clave de API.
-   `--requests-per-second` (o `-rps`): El número de solicitudes por segundo. Por defecto es `16`.
-   `--valid-emails-file`: Ruta al archivo de emails válidos. Por defecto es `valid_emails.txt`.
-   `--invalid-emails-file`: Ruta al archivo de emails inválidos. Por defecto es `invalid_emails.txt`.
-   `--output-file`: Nombre del archivo JSON de salida. Por defecto es `results.json`.
-   `--valid-reason`: El valor de la propiedad `reason` en la respuesta JSON que indica que un email es válido. Por defecto es `valid_email`.

**Ejemplo con más parámetros:**
```bash
python api_tester.py \
    --endpoint "https://api.emailvalidator.co/v2/validate" \
    --api-key "your_secret_api_key_here" \
    --rps 10 \
    --valid-reason "ok" \
    --output-file "experimento_1_results.json"
```

### 5. Visualización de Resultados

Una vez que el script haya terminado, se creará un archivo `results.json`.

Para ver los resultados, simplemente **abre el archivo `dashboard.html` en tu navegador web**. Haz clic en el botón "Cargar Datos de results.json" y el dashboard mostrará los gráficos y las estadísticas.

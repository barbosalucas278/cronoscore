# CronoScore 🕐

Herramienta de **benchmarking para APIs de validación de email**. Prueba múltiples APIs de forma concurrente y compara su rendimiento (velocidad) y precisión (falsos positivos/negativos).

## Características

- **Multi-API**: Prueba varias APIs en una sola ejecución con configuración independiente por cada una
- **Async & Rate-Limited**: Requests asíncronas con `aiohttp` y control de velocidad configurable
- **Reglas Flexibles**: Define reglas de validación con operadores (`>=`, `==`, `in`, etc.) y dot notation para campos anidados
- **Request Configurable**: Método HTTP (GET/POST), headers, parámetros y timeout por API
- **Variables de Entorno**: Soporte para API keys desde variables de entorno (prefijo `$`)
- **Dashboard Interactivo**: Visualización con dark mode, gráficos comparativos, histograma de tiempos, tabla detallada y exportación a CSV
- **Barra de Progreso**: Progreso visual en la terminal durante la ejecución
- **Tests Unitarios**: Cobertura completa con `unittest`
- **CI/CD**: GitHub Actions configurado para tests automáticos

## Estructura del Proyecto

```
.
├── main.py                  # Orquestador principal
├── api_tester.py            # Punto de entrada alternativo
├── config.py                # Configuración CLI + validación JSON
├── api_client.py            # Cliente async de API
├── stats_calculator.py      # Cálculo de estadísticas
├── file_handler.py          # Lectura/escritura de archivos
├── apis_config.json         # Configuración de APIs a probar
├── valid_emails.txt         # Emails que se sabe son válidos
├── invalid_emails.txt       # Emails que se sabe son inválidos
├── dashboard.html           # Dashboard de visualización
├── requirements.txt         # Dependencias
├── tests/                   # Tests unitarios
│   ├── test_api_client.py
│   ├── test_config.py
│   ├── test_file_handler.py
│   └── test_statistics.py
└── .github/workflows/ci.yml # CI con GitHub Actions
```

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/cronoscore.git
cd cronoscore

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

### 1. Configurar APIs (`apis_config.json`)

```json
[
    {
        "name": "MiAPI",
        "endpoint": "https://api.example.com/validate",
        "api_key": "$EMAIL_API_KEY",
        "method": "GET",
        "param_name": "email",
        "headers": {},
        "response_path": "data",
        "timeout": 30,
        "validation_rules": [
            { "field": "score", "operator": ">=", "value": "80" },
            { "field": "result", "operator": "in", "value": ["deliverable"] }
        ]
    }
]
```

| Campo | Descripción | Valor por Defecto |
|-------|-------------|-------------------|
| `name` | Nombre identificador de la API | *requerido* |
| `endpoint` | URL completa del endpoint | *requerido* |
| `api_key` | API key directa o `$VARIABLE_DE_ENTORNO` | *requerido* |
| `method` | Método HTTP: `GET` o `POST` | `GET` |
| `param_name` | Nombre del parámetro del email | `email` |
| `headers` | Headers adicionales a enviar | `{}` |
| `response_path` | Ruta al objeto de datos en la respuesta (dot notation) | `data` |
| `timeout` | Timeout en segundos por request | `30` |
| `validation_rules` | Lista de reglas para determinar si el email es válido | *requerido* |

### 2. Configurar listas de emails

- `valid_emails.txt`: Un email por línea — emails que sabés que son **válidos**
- `invalid_emails.txt`: Un email por línea — emails que sabés que son **inválidos**

### 3. Variables de entorno (opcional)

Si usás `$` como prefijo en `api_key`, se resolverá desde variables de entorno:

```bash
# Windows
set EMAIL_API_KEY=tu_api_key_secreta

# Linux/Mac
export EMAIL_API_KEY=tu_api_key_secreta
```

## Ejecución

```bash
python main.py
```

**Argumentos disponibles:**

| Argumento | Corto | Descripción | Default |
|-----------|-------|-------------|---------|
| `--config-file` | | Archivo JSON de configuración | `apis_config.json` |
| `--requests-per-second` | `-rps` | Solicitudes por segundo | `16` |
| `--valid-emails-file` | | Archivo de emails válidos | `valid_emails.txt` |
| `--invalid-emails-file` | | Archivo de emails inválidos | `invalid_emails.txt` |
| `--log-level` | | Nivel de logging (DEBUG/INFO/WARNING/ERROR) | `INFO` |

**Ejemplo:**

```bash
python main.py -rps 10 --log-level DEBUG
```

## Visualización de Resultados

1. Ejecutar el script → genera `results.json`
2. Abrir `dashboard.html` en el navegador
3. Arrastrar `results.json` al dashboard (o hacer clic para seleccionarlo)

El dashboard incluye:
- **Estadísticas por API**: tiempos, tasas de falsos positivos/negativos
- **Histograma de tiempos** de respuesta
- **Comparación entre APIs**: gráficos de barras
- **Tabla detallada** con todos los emails y sus resultados
- **Exportar a CSV** los resultados
- **Calculadora de costos** estimados
- **Dark mode** con toggle y persistencia

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

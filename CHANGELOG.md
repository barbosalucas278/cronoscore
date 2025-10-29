
# Changelog

## [1.2.0] - 2024-10-29

### Added
- **Soporte para Múltiples APIs**: Ahora se pueden probar varias APIs en una sola ejecución. La configuración se gestiona a través de un archivo `apis_config.json`.
- **Dashboard Interactivo Mejorado**:
  - **Selector de API**: Permite ver las estadísticas detalladas de cada API de forma individual.
  - **Gráficos de Comparación**: Nuevos gráficos que comparan el rendimiento (tiempo de respuesta) y la precisión (falsos positivos/negativos) entre todas las APIs probadas.
  - **Calculadora de Costos**: Una nueva sección en el dashboard para estimar los costos basados en el número de solicitudes y el precio por solicitud.

### Changed
- **Formato de Salida**: El archivo `results.json` ahora tiene una estructura anidada para almacenar los resultados de cada API por separado.
- **Flujo Principal**: `main.py` fue actualizado para iterar sobre la lista de APIs configuradas y recolectar los resultados de cada una.
- **Salida de Fichero Hardcodeada**: El nombre del fichero de salida se ha fijado a `results.json` y ya no es configurable a través de argumentos de línea de comandos.
- **Reglas de Validación por API**: Cada API en `apis_config.json` puede ahora tener su propia `validation_rule` para determinar lo que constituye una respuesta de correo electrónico válida.

## [1.1.0] - 2024-10-26

### Added
- **Unit Tests**: Se agregaron tests unitarios para todos los módulos (`config`, `file_handler`, `api_client`, `statistics`) para garantizar la fiabilidad del código.
- **`CHANGELOG.md`**: Este archivo para documentar los cambios a lo largo del tiempo.

### Changed
- **Modularización del Código**: El script `api_tester.py` fue refactorizado en varios módulos para mejorar la claridad, mantenibilidad y escalabilidad.
  - `config.py`: Maneja la configuración y los argumentos de la línea de comandos.
  - `file_handler.py`: Gestiona la lectura de archivos de entrada y la escritura de resultados.
  - `api_client.py`: Encapsula toda la lógica de interacción con la API.
  - `statistics.py`: Realiza todos los cálculos de estadísticas.
  - `main.py`: Orquesta el flujo principal de la aplicación.
- **Punto de Entrada**: `api_tester.py` ahora actúa como un punto de entrada simple que invoca al orquestador principal.

### Fixed
- **Manejo de Errores**: Mejorado el manejo de errores en el cliente de la API para capturar excepciones de red y otros problemas inesperados.

## [1.0.0] - 2024-10-25

- **Versión Inicial**: Script monolítico `api_tester.py` con funcionalidades básicas de prueba de API.

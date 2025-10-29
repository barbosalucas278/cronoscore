
# Changelog

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

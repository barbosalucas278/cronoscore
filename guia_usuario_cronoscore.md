# 📊 CronoScore — Guía de Usuario

## ¿Qué es CronoScore?

CronoScore es una aplicación de escritorio que permite **probar y comparar servicios de validación de email**. Le das una lista de emails (algunos válidos y otros inválidos), y la herramienta los envía a una o varias APIs para medir:

- ⏱️ **Qué tan rápido** responde cada servicio
- ✅ **Qué tan preciso** es detectando emails válidos e inválidos
- 💰 **Cuánto costaría** usar el servicio a gran escala

Todo se maneja desde una interfaz gráfica — **no hace falta usar la terminal**.

---

## 🚀 Formas de usar CronoScore

Hay dos formas de usar la aplicación:

| Forma | Para quién | Requisitos |
| --- | --- | --- |
| **Ejecutable (.exe)** | Usuarios finales | Ninguno — solo doble clic |
| **Desde código fuente** | Desarrolladores | Python 3.10+ |

---

## 📦 Opción 1: Usar el Ejecutable (.exe)

### Lo que recibiste

Deberías tener una carpeta con estos archivos:

| Archivo | Qué es |
| --- | --- |
| `CronoScore.exe` | La aplicación (~13 MB) |
| `apis_config.json` | Configuración de las APIs a probar |
| `valid_emails.txt` | Lista de emails válidos de prueba |
| `invalid_emails.txt` | Lista de emails inválidos de prueba |

> ⚠️ **Importante**: Los 4 archivos deben estar **en la misma carpeta**.

### Abrir la aplicación

Hacé **doble clic en `CronoScore.exe`**. Se abre la ventana de CronoScore.

> 💡 La primera vez puede tardar unos segundos en abrir. Es normal.

> ⚠️ Windows puede mostrar un aviso de seguridad "Windows protegió su PC". Hacé clic en **"Más información"** → **"Ejecutar de todos modos"**.

---

## 🔧 Opción 2: Desde Código Fuente (Desarrolladores)

### Requisitos

- **Python 3.10 o superior** — [python.org](https://www.python.org/downloads/)
  - Al instalar, marcá **"Add Python to PATH"**

### Instalación (una sola vez)

1. Abrí la terminal (`Win + R` → `cmd` → Enter)
2. Navegá a la carpeta del proyecto:
   ```
   cd C:\ruta\a\cronoscore
   ```
3. Instalá las dependencias:
   ```
   pip install -r requirements.txt
   ```

### Abrir la aplicación

```
python app.py
```

### Generar el ejecutable (.exe)

Si necesitás generar un nuevo `.exe` después de hacer cambios:

```
build.bat
```

O manualmente:

```
python -m PyInstaller --name CronoScore --onefile --windowed --add-data "app.html;." --add-data "apis_config.json;." --add-data "valid_emails.txt;." --add-data "invalid_emails.txt;." --clean app.py
```

El ejecutable se genera en la carpeta `dist\`.

---

## 🖥️ Usando la Aplicación

La aplicación tiene **3 secciones** accesibles desde el menú lateral izquierdo.

---

### 1️⃣ ⚙️ Configuración

En esta sección configurás **qué APIs probar** y **con qué emails**.

#### Configurar una API

Cada API tiene estos campos:

| Campo | Qué poner | Ejemplo |
| --- | --- | --- |
| **Nombre** | Un nombre para identificar el servicio | `MailValidator` |
| **Endpoint** | La URL de la API (la da el proveedor) | `https://api.mailcheck.co/validate` |
| **API Key** | La clave que te dieron al registrarte | `abc123xyz` |
| **Método HTTP** | Generalmente `GET` | `GET` |
| **Nombre del Parámetro** | Generalmente `email` | `email` |
| **Response Path** | Dónde vienen los datos en la respuesta | `data` |
| **Timeout** | Segundos máximos de espera | `30` |

> 💡 **¿Querés probar varias APIs?** Hacé clic en **"+ Agregar API"**.

#### Reglas de Validación

Las reglas determinan **cuándo un email se considera "válido"** según la respuesta de la API.

Hacé clic en **"+ Agregar Regla"** y completá:

| Campo | Significado | Ejemplo |
| --- | --- | --- |
| **Campo** | El nombre del campo en la respuesta | `score` |
| **Operador** | La comparación a hacer | `>=` |
| **Valor** | El valor contra el que se compara | `80` |

**Operadores disponibles:**

| Operador | Significado |
| --- | --- |
| `>=` | Mayor o igual |
| `<=` | Menor o igual |
| `==` | Igual a |
| `!=` | Distinto de |
| `in` | Está en la lista (ej: `["deliverable","risky"]`) |

#### Configurar Emails

En la misma pantalla hay dos cuadros de texto:

- **✅ Emails Válidos**: emails que **sabés que son válidos**, uno por línea
- **❌ Emails Inválidos**: emails que **sabés que son inválidos**, uno por línea

> 💡 **Tip**: Mientras más emails pongas, más confiables serán las estadísticas. Recomendamos al menos 10 de cada tipo.

#### Guardar

Hacé clic en **"💾 Guardar Todo"**. Vas a ver un mensaje de confirmación verde.

---

### 2️⃣ ▶️ Ejecutar

En esta sección lanzás las pruebas contra las APIs configuradas.

#### Pasos:

1. **Configurar RPS** (Requests por Segundo): Cuántas solicitudes enviar por segundo. Si la API tiene límites, bajá este número (por ejemplo a 5).
2. Hacé clic en **"▶️ Iniciar Pruebas"**.
3. Vas a ver:
   - Una **barra de progreso** que se llena en tiempo real
   - Un **log de actividad** con mensajes de lo que va pasando
4. Cuando termine, aparece el mensaje **"✅ Completado"**.

> ⏳ **¿Cuánto tarda?** Depende de la cantidad de emails y APIs. Con 20 emails y 1 API, menos de 1 minuto.

---

### 3️⃣ 📊 Resultados

En esta sección ves todas las estadísticas y comparaciones.

#### Tarjetas de Resumen

| Tarjeta | Significado |
| --- | --- |
| **APIs Probadas** | Cuántos servicios probaste |
| **Emails por API** | Cuántos emails se enviaron a cada servicio |
| **Tiempo Promedio** | Cuánto tarda en promedio cada validación |
| **Tiempo Máx / Mín** | El request más lento y el más rápido |
| **Falsos Positivos** | % de inválidos que la API marcó como válidos ❌ |
| **Falsos Negativos** | % de válidos que la API marcó como inválidos ❌ |

#### Gráficos

- **Dona de Clasificación**: Muestra cuántos emails fueron clasificados correctamente y cuántos no
  - 🟢 **Válido → válido** y **Inválido → inválido** = ¡Correcto!
  - 🔴 **Inválido → válido** = Falso positivo (error)
  - 🟡 **Válido → inválido** = Falso negativo (error)
- **Histograma de Tiempos**: Distribución de la velocidad de respuesta
- **Comparación de APIs**: Gráficos de barras comparando rendimiento y precisión entre servicios

#### Calculadora de Costos

1. Ingresá el precio por solicitud de la API
2. Hacé clic en **"Calcular"**
3. Te muestra el costo total estimado

#### Tabla Detallada

Una tabla con el resultado de cada email individual, con colores por clasificación.

#### Exportar a CSV

Hacé clic en **"📥 Exportar CSV"** para guardar los resultados como planilla. Se abre un diálogo "Guardar como" para elegir dónde guardarlo.

---

## 🌙 Modo Oscuro

Hacé clic en **"🌙 Modo oscuro"** en la parte inferior del menú lateral. Tu preferencia se guarda automáticamente.

---

## 🔑 API Keys Seguras (Avanzado)

Si no querés dejar tu clave escrita en la configuración, podés usar **variables de entorno**.

En el campo API Key, escribí el nombre con `$` adelante:

```
$MI_CLAVE_API
```

Y antes de abrir la app, definí la variable:

**Windows:**
```
set MI_CLAVE_API=tu_clave_secreta
CronoScore.exe
```

**Desde código fuente:**
```
set MI_CLAVE_API=tu_clave_secreta
python app.py
```

---

## 🔧 Modo Terminal (Avanzado)

Si preferís usar la terminal en vez de la interfaz gráfica:

```
python main.py
```

| Argumento | Descripción | Default |
| --- | --- | --- |
| `-rps 10` | Requests por segundo | `16` |
| `--log-level DEBUG` | Nivel de detalle del log | `INFO` |
| `--config-file otro.json` | Archivo de configuración | `apis_config.json` |

Después abrí `dashboard.html` en el navegador y arrastrá `results.json` para ver los resultados.

---

## ❓ Preguntas Frecuentes

**¿Puedo probar varias APIs a la vez?**
Sí. En la sección Configuración, hacé clic en "+ Agregar API" para agregar tantas como quieras.

**¿Necesito internet?**
Sí, para ejecutar las pruebas. Para ver resultados ya generados, no.

**¿Dónde consigo la API Key?**
Cada proveedor te la da al registrarte. Buscá en su documentación o panel de control.

**¿Puedo ver resultados anteriores?**
Sí. Los resultados se guardan en `results.json`. Cada vez que abrís la pestaña Resultados, se cargan automáticamente.

**Me da error "variable de entorno no definida"**
Si usás `$` en la API Key, necesitás definir la variable antes de abrir la app.

**El .exe no abre / Windows lo bloquea**
Windows puede bloquear ejecutables no firmados. Hacé clic en "Más información" → "Ejecutar de todos modos".

**La app no abre desde código fuente**
1. Verificá Python: `python --version`
2. Reinstalá dependencias: `pip install -r requirements.txt`
3. Ejecutá `python app.py` desde la terminal para ver los errores

---

## 📞 Soporte

Si tenés problemas, contactá al equipo técnico con:

- Captura de pantalla del error
- El archivo `results.json` (si se generó)
- Versión de Python (si usás código fuente): `python --version`

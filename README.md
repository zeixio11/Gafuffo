# Sistema de Gafas con Cámara ESP32-S3-CAM

Este proyecto implementa un sistema de gafas con cámara inteligente basado en el microcontrolador **ESP32-S3-CAM**. Permite capturar fotos mediante un botón físico, enviarlas a un servidor Python vía WiFi, analizarlas con inteligencia artificial (YOLO) para detectar personas y objetos, y visualizar los resultados en una galería web.

---

## 🗂️ Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| [`reconocimiento.py`](reconocimiento.py) | Motor de reconocimiento de objetos con YOLO |
| [`servidor.py`](servidor.py) | Servidor web Flask para recibir, analizar y mostrar fotos |
| [`stckt-claude.cpp`](stckt-claude.cpp) | Firmware para el ESP32-S3-CAM (Arduino/C++) |
| [`yolo11n.pt`](yolo11n.pt) | Modelo de detección de objetos pre-entrenado de Ultralytics |

---

## 🏗️ Arquitectura del Sistema

📊 **[Abrir diagrama interactivo de arquitectura](diagramas/arquitectura.html)** — componentes, conexiones y regiones (hardware y servidor), con temas claro/oscuro y exportación a PNG/SVG.

> 💡 **Cómo abrir los diagramas interactivos:** son archivos HTML autocontenidos (no necesitan servidor ni conexión). Haz doble clic en el archivo dentro de la carpeta `diagramas/` o ábrelo con cualquier navegador (Chrome, Edge, Firefox). Dentro del visor puedes alternar entre tema claro/oscuro y exportar el diagrama como PNG, JPEG, WebP o SVG.

---

## 🔄 Flujo de Trabajo

📊 **[Abrir diagrama interactivo del flujo de trabajo](diagramas/flujo-de-trabajo.html)** — de la pulsación del botón a la galería, con carriles por actor, validaciones y análisis asíncrono.

---

## 📁 Detalle de Archivos

### `reconocimiento.py`

**Propósito:** Módulo de reconocimiento de personas y objetos usando el modelo YOLO (You Only Look Once) de Ultralytics.

**Función principal:** `Reconocedor.analizar(ruta_foto, ruta_anotada=None)`
- Detecta hasta 80 tipos de objetos diferentes, incluyendo la categoría **"persona"**.
- Filtra detecciones con menos del 40 % de confianza (`CONFIANZA_MIN = 0.40`).
- Devuelve un diccionario con:
  - `personas`: cantidad de personas detectadas
  - `resumen`: conteo de todos los objetos detectados
  - `descripcion`: frase descriptiva en español (ej: *"Veo 2 personas, 1 celular y 1 taza."*)
  - `objetos`: lista detallada con nombre, confianza y coordenadas de cada caja delimitadora
- Si se proporciona `ruta_anotada`, genera una copia de la imagen con recuadros de color y etiquetas.

**Dependencias:**
- [`ultralytics`](https://pypi.org/project/ultralytics/) (YOLO)
- [`Pillow`](https://pypi.org/project/Pillow/) (manipulación de imágenes)

**Uso desde línea de comandos:**

```bash
python reconocimiento.py ruta/a/foto.jpg
```

Genera automáticamente `foto_detectada.jpg` con los recuadros dibujados.

**Traducción:** Los nombres de objetos se traducen al español mediante el diccionario `NOMBRES_ES`.

---

### `servidor.py`

**Propósito:** Servidor web que recibe las fotos del ESP32, las analiza con YOLO y presenta una galería web con los resultados.

**Endpoints:**

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/upload` | `POST` | Recibe imágenes JPEG desde la cámara. Requiere header `X-Api-Key`. |
| `/` | `GET` | Galería web con todas las fotos, etiquetas y estado de análisis. |
| `/api/ultima` | `GET` | Devuelve JSON con el resultado del análisis de la última foto. |
| `/fotos/<nombre>` | `GET` | Sirve una imagen específica desde la carpeta `fotos/`. |

**Flujo de reconocimiento en segundo plano:**
1. La foto llega por `/upload` y se guarda en `fotos/`.
2. El nombre del archivo se encola en una cola (`queue.Queue`) para procesamiento asíncrono.
3. Un hilo trabajador (`trabajador`) consume la cola y ejecuta `analizar_foto()`.
4. La foto analizada se guarda en `fotos/detectadas/` junto con un archivo `.json` con los resultados.
5. La galería web muestra automáticamente los resultados con recuadros y etiquetas.

**Configuración clave:**
- `API_KEY = "cambia-esta-clave"` — debe coincidir con la clave en el firmware del ESP32.
- `PUERTO = 5000`
- `RECONOCIMIENTO = True` — permite desactivar el análisis YOLO y solo guardar fotos.

**Dependencias:**
- [`Flask`](https://pypi.org/project/Flask/)
- [`ultralytics`](https://pypi.org/project/ultralytics/)

**Ejecución:**

```bash
python servidor.py
```

La galería estará disponible en: [`http://localhost:5000`](http://localhost:5000)

---

### `stckt-claude.cpp`

**Propósito:** Firmware del microcontrolador ESP32-S3-CAM. Captura imágenes cuando se presiona un botón físico y las envía al servidor vía WiFi.

**Configuración de pines de la cámara:**

| Pin | Función |
|-----|---------|
| PWDN  | GPIO 32 |
| XCLK  | GPIO 0  |
| SDA   | GPIO 26 |
| SCL   | GPIO 27 |
| D7    | GPIO 35 |
| D6    | GPIO 34 |
| D5    | GPIO 39 |
| D4    | GPIO 36 |
| D3    | GPIO 21 |
| D2    | GPIO 19 |
| D1    | GPIO 18 |
| D0    | GPIO 5  |
| VSYNC | GPIO 25 |
| HREF  | GPIO 23 |
| PCLK  | GPIO 22 |

**Parámetros de la cámara:**
- Formato: JPEG (`PIXFORMAT_JPEG`)
- Resolución: UXGA (1600×1200)
- Calidad JPEG: 12 (mejor calidad)
- Frecuencia XCLK: 20 MHz
- Buffers: 2 en PSRAM

**Flujo del botón:**
1. Se detecta la pulsación del botón conectado al **GPIO 13** (con pull-up interno).
2. Se captura un frame de la cámara (`esp_camera_fb_get`).
3. Se envía al servidor mediante HTTP POST a la URL configurada.
4. Se libera el buffer de la cámara.
5. Se espera a que se suelte el botón para evitar capturas múltiples.

**Configuración de red:**

```cpp
const char* ssid = "TU_RED";
const char* pass = "TU_CLAVE";
const char* url  = "http://192.168.1.50:5000/upload";
```

> ⚠️ **Importante:** Actualiza `ssid`, `pass` y `url` con los datos de tu red WiFi y la IP del servidor.

---

### `yolo11n.pt`

**Propósito:** Modelo de detección de objetos pre-entrenado de [Ultralytics](https://docs.ultralytics.com/), versión YOLO11 nano (`yolo11n`).

**Características:**
- **Tamaño:** ~6 MB (descarga automática la primera vez si no está presente).
- **Velocidad:** Optimizado para inferencia rápida (variante "n" = nano).
- **Clases:** Detecta 80 categorías de objetos del dataset COCO.
- **Función en el sistema:** Es el modelo que `reconocimiento.py` carga al inicializar la clase `Reconocedor`.

**Variantes disponibles** (más precisas pero más lentas):
- `yolo11s.pt` (small)
- `yolo11m.pt` (medium)

> 💡 El modelo se descarga automáticamente desde Ultralytics la primera vez que se ejecuta el reconocimiento.

---

## 🚀 Requisitos

### Hardware
- **Placa:** ESP32-S3-CAM (u otra compatible con cámara OV2640)
- **Botón:** Pulsador conectado al GPIO 13
- **Servidor:** PC o Raspberry Pi en la misma red WiFi
- **Cámara:** OV2640 (generalmente incluida con el módulo ESP32-S3-CAM)

### Software
- **Python:** 3.8 o superior
- **pip:** Gestor de paquetes de Python

### Dependencias Python

Instala todas las dependencias con:

```bash
pip install flask ultralytics pillow
```

O instálalas individualmente:

| Paquete | Versión mínima | Propósito |
|---------|---------------|-----------|
| `flask` | ≥2.0 | Servidor web y galería |
| `ultralytics` | ≥8.0 | Motor YOLO para detección de objetos |
| `pillow` | ≥9.0 | Procesamiento de imágenes y dibujo de recuadros |

---

## 🛠️ Instalación y ejecución

### 1. Servidor Python

```bash
# Clona o descarga el proyecto
cd proyecto

# Instala dependencias
pip install flask ultralytics pillow

# Inicia el servidor
python servidor.py
```

El servidor estará escuchando en `http://0.0.0.0:5000`.

### 2. Firmware ESP32

1. Abre `stckt-claude.cpp` en el [Arduino IDE](https://www.arduino.cc/en/software) o [PlatformIO](https://platformio.org/).
2. Instala las librerías:
   - `esp_camera` (incluida en el core ESP32)
   - `WiFi` (incluida en el core ESP32)
   - `HTTPClient` (incluida en el core ESP32)
3. Configura las credenciales WiFi y la IP del servidor:
   ```cpp
   const char* ssid = "TU_RED";
   const char* pass = "TU_CLAVE";
   const char* url  = "http://192.168.1.X:5000/upload";
   ```
4. Compila y sube el firmware al ESP32-S3-CAM.

### 3. Uso

1. Enciende el ESP32 y espera a que se conecte a la red WiFi.
2. Abre la galería en tu navegador: [`http://localhost:5000`](http://localhost:5000)
3. Presiona el botón físico de las gafas para capturar una foto.
4. La foto aparecerá automáticamente en la galería con los objetos detectados resaltados.

---

## 📝 Estructura de Directorios Generada

```
proyecto/
├── reconocimiento.py      # Motor de IA
├── servidor.py            # Servidor web
├── stckt-claude.cpp       # Firmware ESP32
├── yolo11n.pt             # Modelo YOLO
└── fotos/                 # Creado automáticamente
    ├── foto_YYYYMMDD_HHMMSS_XXX.jpg
    └── detectadas/
        ├── foto_YYYYMMDD_HHMMSS_XXX.jpg   # Imagen con recuadros
        └── foto_YYYYMMDD_HHMMSS_XXX.json  # Resultados del análisis
```

---

## 🔒 Seguridad

- El endpoint `/upload` requiere el header `X-Api-Key`. Cambia la clave por defecto tanto en `servidor.py` como en `stckt-claude.cpp` antes de usar en producción.
- El servidor Flask en modo desarrollo no está optimizado para entornos de producción. Usa un servidor WSGI (como Gunicorn) si necesitas exponerlo a la red.

---

## 🧪 Pruebas Manuales

### Probar el reconocimiento sin el ESP32:

```bash
cd proyecto
python reconocimiento.py fotos/tu_foto.jpg
```

### Ver la última foto analizada:

```bash
curl http://localhost:5000/api/ultima | python -m json.tool
```

---

## 📄 Licencia

Este es un proyecto personal/educativo. Puedes adaptarlo y mejorarlo libremente.

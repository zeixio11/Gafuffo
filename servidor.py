"""
Servidor web para las gafas con cámara ESP32-S3-CAM, con reconocimiento
de personas y objetos.

- Recibe las fotos que envía la cámara (POST /upload)
- Las guarda en la carpeta 'fotos'
- Analiza cada foto con YOLO y guarda una copia con recuadros en 'fotos/detectadas'
- Galería web: abre http://localhost:5000 en el navegador
- Resultado de la última foto en JSON: http://localhost:5000/api/ultima

Instalación:   pip install flask ultralytics pillow
Ejecución:     python servidor.py
"""

# TODO(esp32-persistent-pc-connection): Uncomment the lines below to enable
#   mDNS advertisement so the ESP32 can discover this PC via 'steckt-server.local'.
#   Requires: pip install zeroconf
# import atexit
# import socket
import json
import os
import queue
import threading
from datetime import datetime
from html import escape

from flask import Flask, request, jsonify, send_from_directory, abort
# from zeroconf import Zeroconf, ServiceInfo

API_KEY = "cambia-esta-clave"      # Debe coincidir con API_KEY en main_ESP32code.cpp
PUERTO = 5000
RECONOCIMIENTO = True              # False = solo guarda las fotos, sin analizar

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(BASE, "fotos")
DETECTADAS = os.path.join(CARPETA, "detectadas")
os.makedirs(DETECTADAS, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024   # máx. 10 MB por foto

# ---------- Reconocimiento en segundo plano ----------
# La cámara recibe la respuesta enseguida; el análisis se hace después.
cola = queue.Queue()
reconocedor = None


def ruta_json(nombre):
    return os.path.join(DETECTADAS, nombre.rsplit(".", 1)[0] + ".json")


def analizar_foto(nombre):
    datos = reconocedor.analizar(
        os.path.join(CARPETA, nombre), os.path.join(DETECTADAS, nombre)
    )
    datos["archivo"] = nombre
    with open(ruta_json(nombre), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  {nombre}: {datos['descripcion']}")


def trabajador():
    while True:
        nombre = cola.get()
        try:
            analizar_foto(nombre)
        except Exception as e:
            print(f"  Error analizando {nombre}: {e}")
        cola.task_done()


def iniciar_reconocimiento():
    global reconocedor
    from reconocimiento import Reconocedor
    reconocedor = Reconocedor()
    threading.Thread(target=trabajador, daemon=True).start()
    # Analiza fotos que llegaron antes y aún no tienen resultado
    for f in sorted(os.listdir(CARPETA)):
        if f.lower().endswith(".jpg") and not os.path.exists(ruta_json(f)):
            cola.put(f)


# ---------- Rutas web ----------
@app.route("/upload", methods=["POST"])
def upload():
    if request.headers.get("X-Api-Key") != API_KEY:
        abort(401)
    datos = request.get_data()
    if not datos.startswith(b"\xff\xd8"):            # firma de un JPEG
        return jsonify(ok=False, error="No es un JPEG"), 400

    nombre = datetime.now().strftime("foto_%Y%m%d_%H%M%S_%f")[:-3] + ".jpg"
    with open(os.path.join(CARPETA, nombre), "wb") as f:
        f.write(datos)
    print(f"Foto guardada: {nombre} ({len(datos) / 1024:.0f} KB)")
    if reconocedor:
        cola.put(nombre)
    return jsonify(ok=True, archivo=nombre)


@app.route("/fotos/<path:nombre>")
def ver_foto(nombre):
    return send_from_directory(CARPETA, nombre)


def leer_resultado(nombre):
    try:
        with open(ruta_json(nombre), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def listar_fotos():
    return sorted(
        (f for f in os.listdir(CARPETA) if f.lower().endswith(".jpg")),
        reverse=True,
    )


@app.route("/api/ultima")
def api_ultima():
    fotos = listar_fotos()
    if not fotos:
        return jsonify(ok=False, error="No hay fotos"), 404
    datos = leer_resultado(fotos[0])
    if datos is None:
        return jsonify(ok=True, archivo=fotos[0], estado="analizando")
    return jsonify(ok=True, estado="listo", **datos)


@app.route("/")
def galeria():
    fotos = listar_fotos()
    tarjetas = []
    for f in fotos:
        res = leer_resultado(f)
        if res:
            img = f"detectadas/{f}"
            etiquetas = "".join(
                f'<b class="{"p" if n == "persona" else ""}">{escape(n)} × {c}</b>'
                for n, c in res["resumen"].items()
            ) or "<i>Nada reconocido</i>"
        else:
            img = f
            etiquetas = "<i>Analizando…</i>" if reconocedor else ""
        fecha = f"{f[5:9]}-{f[9:11]}-{f[11:13]} {f[14:16]}:{f[16:18]}:{f[18:20]}"
        tarjetas.append(
            f'<a href="/fotos/{img}" target="_blank"><img src="/fotos/{img}" loading="lazy">'
            f'<span>{fecha}</span><div class="tags">{etiquetas}</div></a>'
        )
    vacio = "<p>Aún no hay fotos. Presiona el botón de las gafas.</p>" if not fotos else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="5">
<title>Fotos de las gafas</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; padding: 16px; background: #f4f4f2; color: #222; }}
  h1 {{ font-size: 20px; font-weight: 500; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }}
  a {{ display: block; background: #fff; border-radius: 10px; overflow: hidden; text-decoration: none; color: #555; }}
  img {{ width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block; }}
  span {{ display: block; padding: 8px 10px 0; font-size: 13px; }}
  .tags {{ padding: 6px 10px 10px; display: flex; flex-wrap: wrap; gap: 4px; font-size: 12px; }}
  .tags b {{ font-weight: 500; background: #e6f1fb; color: #0c447c; padding: 2px 8px; border-radius: 99px; }}
  .tags b.p {{ background: #fcebeb; color: #791f1f; }}
  .tags i {{ color: #888; }}
</style></head>
<body>
<h1>Fotos de las gafas ({len(fotos)})</h1>
{vacio}
<div class="grid">{"".join(tarjetas)}</div>
</body></html>"""


# TODO(esp32-persistent-pc-connection): Uncomment the functions below to enable
#   mDNS advertisement so the ESP32 can discover this PC via 'steckt-server.local'.
# def _local_ip():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         ip = s.getsockname()[0]
#         s.close()
#         return ip
#     except Exception:
#         return "127.0.0.1"
#
#
# def _register_mdns():
#     zc = Zeroconf()
#     ip = _local_ip()
#     info = ServiceInfo(
#         type_="_http._tcp.local.",
#         name="steckt-server._http._tcp.local.",
#         addresses=[socket.inet_aton(ip)],
#         port=PUERTO,
#         properties={},
#         server="steckt-server.local.",
#     )
#     zc.register_service(info)
#     print(f"[mDNS] Registered steckt-server.local -> {ip}:{PUERTO}")
#     atexit.register(lambda: zc.unregister_service(info) or zc.close())
#     return zc


if __name__ == "__main__":
    if RECONOCIMIENTO:
        iniciar_reconocimiento()
    # TODO(esp32-persistent-pc-connection): Uncomment to enable mDNS:
    # _register_mdns()
    print(f"Galería en http://localhost:{PUERTO}  |  Fotos en: {CARPETA}")
    app.run(host="0.0.0.0", port=PUERTO)

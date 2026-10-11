"""
Reconocimiento de personas y objetos para las gafas con cámara.

Usa YOLO (Ultralytics), un modelo que detecta 80 tipos de objetos,
incluida la categoría "persona". La primera vez descarga el modelo
(unos 6 MB) automáticamente.

Uso directo, para probar con una foto:
    python reconocimiento.py ruta/a/foto.jpg
"""

import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

MODELO = "yolo11n.pt"     # n = rápido. Más preciso pero más lento: yolo11s.pt o yolo11m.pt
CONFIANZA_MIN = 0.40      # Ignora detecciones con menos de 40 % de seguridad

NOMBRES_ES = {
    "person": "persona", "bicycle": "bicicleta", "car": "carro", "motorcycle": "moto",
    "airplane": "avión", "bus": "bus", "train": "tren", "truck": "camión", "boat": "bote",
    "traffic light": "semáforo", "fire hydrant": "hidrante", "stop sign": "señal de pare",
    "parking meter": "parquímetro", "bench": "banca", "bird": "pájaro", "cat": "gato",
    "dog": "perro", "horse": "caballo", "sheep": "oveja", "cow": "vaca", "elephant": "elefante",
    "bear": "oso", "zebra": "cebra", "giraffe": "jirafa", "backpack": "morral",
    "umbrella": "sombrilla", "handbag": "bolso", "tie": "corbata", "suitcase": "maleta",
    "frisbee": "frisbee", "skis": "esquís", "snowboard": "snowboard", "sports ball": "balón",
    "kite": "cometa", "baseball bat": "bate", "baseball glove": "guante de béisbol",
    "skateboard": "patineta", "surfboard": "tabla de surf", "tennis racket": "raqueta",
    "bottle": "botella", "wine glass": "copa", "cup": "taza", "fork": "tenedor",
    "knife": "cuchillo", "spoon": "cuchara", "bowl": "tazón", "banana": "banano",
    "apple": "manzana", "sandwich": "sándwich", "orange": "naranja", "broccoli": "brócoli",
    "carrot": "zanahoria", "hot dog": "perro caliente", "pizza": "pizza", "donut": "dona",
    "cake": "torta", "chair": "silla", "couch": "sofá", "potted plant": "matera",
    "bed": "cama", "dining table": "mesa", "toilet": "inodoro", "tv": "televisor",
    "laptop": "portátil", "mouse": "mouse", "remote": "control remoto", "keyboard": "teclado",
    "cell phone": "celular", "microwave": "microondas", "oven": "horno", "toaster": "tostadora",
    "sink": "lavaplatos", "refrigerator": "nevera", "book": "libro", "clock": "reloj",
    "vase": "florero", "scissors": "tijeras", "teddy bear": "peluche",
    "hair drier": "secador", "toothbrush": "cepillo de dientes",
}


def _fuente(tamano):
    for nombre in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            pass
    return ImageFont.load_default()


def _color(nombre):
    if nombre == "persona":
        return (230, 60, 60)
    paleta = [(40, 150, 230), (30, 170, 110), (240, 160, 30), (150, 90, 210), (230, 100, 160)]
    return paleta[sum(map(ord, nombre)) % len(paleta)]


class Reconocedor:
    def __init__(self, modelo=MODELO, confianza=CONFIANZA_MIN):
        print(f"Cargando modelo {modelo}...")
        self.modelo = YOLO(modelo)
        self.confianza = confianza

    def analizar(self, ruta_foto, ruta_anotada=None):
        """Detecta personas y objetos. Devuelve un dict y, si se pide,
        guarda una copia de la foto con recuadros y nombres."""
        resultado = self.modelo(str(ruta_foto), conf=self.confianza, verbose=False)[0]

        objetos = []
        for caja in resultado.boxes:
            nombre_en = resultado.names[int(caja.cls)]
            x1, y1, x2, y2 = (int(v) for v in caja.xyxy[0].tolist())
            objetos.append({
                "nombre": NOMBRES_ES.get(nombre_en, nombre_en),
                "confianza": round(float(caja.conf), 2),
                "caja": [x1, y1, x2, y2],
            })
        objetos.sort(key=lambda o: o["confianza"], reverse=True)

        conteo = Counter(o["nombre"] for o in objetos)
        datos = {
            "personas": conteo.get("persona", 0),
            "resumen": dict(conteo.most_common()),
            "descripcion": describir(conteo),
            "objetos": objetos,
        }

        if ruta_anotada:
            self._dibujar(ruta_foto, objetos, ruta_anotada)
        return datos

    @staticmethod
    def _dibujar(ruta_foto, objetos, ruta_salida):
        img = Image.open(ruta_foto).convert("RGB")
        dibujo = ImageDraw.Draw(img)
        grosor = max(2, img.width // 300)
        fuente = _fuente(max(14, img.width // 45))
        for o in objetos:
            x1, y1, x2, y2 = o["caja"]
            color = _color(o["nombre"])
            dibujo.rectangle([x1, y1, x2, y2], outline=color, width=grosor)
            texto = f'{o["nombre"]} {int(o["confianza"] * 100)}%'
            tx1, ty1, tx2, ty2 = dibujo.textbbox((0, 0), texto, font=fuente)
            alto = ty2 - ty1 + 8
            y_texto = y1 - alto if y1 - alto > 0 else y1
            dibujo.rectangle([x1, y_texto, x1 + tx2 - tx1 + 10, y_texto + alto], fill=color)
            dibujo.text((x1 + 5, y_texto + 4 - ty1), texto, fill="white", font=fuente)
        img.save(ruta_salida, quality=90)


def _plural_palabra(p):
    if p.endswith("s"):
        return p
    if p.endswith("ón"):
        return p[:-2] + "ones"
    return p + ("s" if p[-1] in "aeiouáéíóú" else "es")


def plural(nombre):
    """'control remoto' -> 'controles remotos', 'señal de pare' -> 'señales de pare'."""
    palabras = nombre.split()
    if "de" in palabras:
        i = palabras.index("de")
        return " ".join([_plural_palabra(p) for p in palabras[:i]] + palabras[i:])
    return " ".join(_plural_palabra(p) for p in palabras)


def describir(conteo):
    """Frase corta en español, p. ej. 'Veo 2 personas, 1 celular y 1 taza.'"""
    if not conteo:
        return "No reconocí nada."
    partes = [f"1 {nombre}" if n == 1 else f"{n} {plural(nombre)}"
              for nombre, n in conteo.most_common()]
    if len(partes) == 1:
        return f"Veo {partes[0]}."
    return f"Veo {', '.join(partes[:-1])} y {partes[-1]}."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python reconocimiento.py foto.jpg")
        sys.exit(1)
    foto = Path(sys.argv[1])
    salida = foto.with_name(foto.stem + "_detectada.jpg")
    datos = Reconocedor().analizar(foto, salida)
    print(datos["descripcion"])
    print(json.dumps(datos["resumen"], ensure_ascii=False, indent=2))
    print(f"Imagen con recuadros: {salida}")

#!/usr/bin/env python3
"""
Regenera la lista FOTOS de index.html a partir de las imágenes de la carpeta fotos/.

- Pie de foto = nombre del archivo sin extensión y con las _ cambiadas por espacios.
  Ejemplo: fotos/Torre_del_spawn.jpg  ->  "Torre del spawn"
- Solo cambia lo que hay entre los marcadores FOTOS-AUTO-INICIO y FOTOS-AUTO-FIN.

Uso:  python3 scripts/actualizar_fotos.py [ruta/al/index.html]
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

CARPETA = Path("fotos")
HTML = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("index.html")
EXTENSIONES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
INICIO = "// >>> FOTOS-AUTO-INICIO"
FIN = "// <<< FOTOS-AUTO-FIN"


def pie_de_foto(nombre_archivo: str) -> str:
    texto = Path(nombre_archivo).stem.replace("_", " ")
    return re.sub(r"\s+", " ", texto).strip()


def texto_js(valor: str) -> str:
    # Cadena JavaScript segura (comillas escapadas; evita cerrar el <script> por error)
    return json.dumps(valor, ensure_ascii=False).replace("</", "<\\/")


imagenes = []
if CARPETA.is_dir():
    imagenes = sorted(
        (f for f in CARPETA.iterdir() if f.is_file() and f.suffix.lower() in EXTENSIONES),
        key=lambda f: f.name.lower(),
    )

lineas = ["const FOTOS = ["]
for f in imagenes:
    ruta = "fotos/" + quote(f.name)          # espacios y caracteres raros codificados para la URL
    lineas.append(f"  {{ archivo: {texto_js(ruta)}, pie: {texto_js(pie_de_foto(f.name))} }},")
lineas.append("];")
bloque = "\n".join(lineas)

html = HTML.read_text(encoding="utf-8")
patron = re.compile(re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)
if not patron.search(html):
    sys.exit(f"ERROR: no encuentro los marcadores {INICIO} / {FIN} en {HTML}")

nuevo = patron.sub(
    lambda _: f"{INICIO} (lo genera GitHub Actions, no editar a mano)\n{bloque}\n{FIN}", html
)

if nuevo == html:
    print(f"Sin cambios ({len(imagenes)} fotos).")
else:
    HTML.write_text(nuevo, encoding="utf-8")
    print(f"{HTML} actualizado con {len(imagenes)} fotos.")

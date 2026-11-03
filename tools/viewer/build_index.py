"""
Arma tools/viewer/models.json, el índice que lee el visor 3D (tools/viewer/index.html).

  py -I tools/viewer/build_index.py

Lo corren solos process_model (al terminar cada modelo), model_queue (al cambiar un estado) y
tools/roblox/anim_preview.py (al escribir una animación). Lista cada modelo de assets/models/western/
(sus GLB, reporte, capturas, receta, imagen de concepto y estado en la cola) y las animaciones de
western/_animations/. "stamp" es la fecha (ms) del archivo más nuevo de cada uno: el visor consulta el
índice cada 2 s y con eso sabe qué es nuevo o cambió, sin recargar el resto.
"""

import json
import os
import sys
import re
import struct
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"
DOC = REPO / "assets" / "models" / "Prompts de modelos - Western.md"
OUT = Path(__file__).resolve().parent / "models.json"
STATE = MODELS / "_estado.json"


def url(p):
    return "/" + p.relative_to(REPO).as_posix()


def glb_info(path):
    try:
        with open(path, "rb") as f:
            f.read(12)
            n, _ = struct.unpack("<II", f.read(8))
            doc = json.loads(f.read(n))
        return {"generator": doc.get("asset", {}).get("generator", ""),
                "animations": [a.get("name", "") for a in doc.get("animations", [])],
                "markers": {a.get("name", ""): a.get("extras", {}).get("markers", []) for a in doc.get("animations", [])}}
    except (OSError, ValueError, struct.error):
        return {}


def stamp(paths):
    return max((int(p.stat().st_mtime * 1000) for p in paths if p.exists()), default=0)


def names_from_doc():
    names = {}
    if DOC.exists():
        for line in DOC.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^#{3,4} `(WST_[A-Za-z_]+)` — (.+)$", line)
            if m:
                names[m.group(1)] = m.group(2).strip()
    return names


def build():
    names = names_from_doc()
    try:
        queue = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        queue = {}
    models = []
    for cat in sorted(p for p in MODELS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for folder in sorted(p for p in cat.iterdir() if p.is_dir()):
            mid = folder.name
            design, export = folder / "01_design", folder / "03_export"
            files = {}
            if (export / f"{mid}.glb").exists():
                files["final"] = url(export / f"{mid}.glb")
            if (design / f"{mid}.glb").exists():
                files["original"] = url(design / f"{mid}.glb")
            if (design / f"{mid}.claude-design.glb").exists():
                files["claude_design"] = url(design / f"{mid}.claude-design.glb")
            if not files:
                continue
            entry = {"id": mid, "name": names.get(mid, ""), "category": cat.name, "files": files,
                     "reviews": [url(p) for p in sorted(folder.glob("review_*.png"))],
                     "recipe": (design / f"{mid}.build.py").exists(),
                     "concept": [url(p) for p in sorted(design.glob("concept*.*"))]}
            if "original" in files:
                entry["source"] = "receta" if "Khronos" in glb_info(design / f"{mid}.glb").get("generator", "") \
                    else "Claude Design"
            rep = folder / "report.json"
            entry["stamp"] = stamp([REPO / f.lstrip("/") for f in files.values()] + [rep, design / f"{mid}.build.py"])
            entry["estado"] = queue.get(mid, {}).get("estado", "pendiente")
            if rep.exists():
                r = json.loads(rep.read_text(encoding="utf-8"))
                entry["report"] = {k: r.get(k) for k in ("pass", "tris", "budget", "size_studs", "errors", "warnings")}
            models.append(entry)
    anims = []
    adir = MODELS / "_animations"
    if adir.exists():
        for p in sorted(adir.glob("*.glb")):
            name, _, rig = p.stem.partition("@")          # <Clip>@<Id>: hecho para ese modelo (anim_preview)
            info = glb_info(p)
            anims.append({"file": url(p), "name": name, "rig": rig or None, "clips": info.get("animations", []),
                          "markers": info.get("markers", {}), "stamp": stamp([p])})
    # efectos (assets/vfx/western/*.json) y dónde salen (_bindings.json): el visor los simula con tools/viewer/vfx.js
    vdir = REPO / "assets" / "vfx" / "western"
    vfx = {"textures": "/assets/vfx/textures/", "effects": {}, "bindings": []}
    if vdir.exists():
        for p in sorted(vdir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                continue                              # a medio escribir: el próximo índice lo toma
            if p.name == "_bindings.json":
                vfx["bindings"] = data.get("bindings", [])
            else:
                vfx["effects"][p.stem] = data
    tmp = OUT.with_suffix(f".{os.getpid()}.tmp")      # atómico: varias construcciones a la vez no lo dejan a medias
    tmp.write_text(json.dumps({"models": models, "animations": anims, "vfx": vfx}, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    for i in range(40):                               # Windows no deja reemplazar un archivo que alguien está leyendo
        try:                                          # (el visor lo consulta cada 2 s): reintentar un rato
            os.replace(tmp, OUT)
            break
        except PermissionError:
            if i == 39:
                raise
            time.sleep(0.05)
    return len(models), len(anims)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no es UTF-8
    m, a = build()
    print(f"{m} modelos y {a} archivos de animación en {OUT}")

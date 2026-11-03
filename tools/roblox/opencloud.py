"""
Sube a Roblox, por Open Cloud, lo que sale de la fábrica: modelos (GLB de 03_export) y animaciones (.rbxm).

  py -I tools/roblox/opencloud.py model <Id>                 sube 03_export/<Id>.glb como Model
  py -I tools/roblox/opencloud.py animation <archivo.rbxm> <Nombre>
  py -I tools/roblox/opencloud.py status                     qué está subido y si cambió desde entonces

La key (Assets API, Read + Write) la crea Valentin y la guarda él en ~/.roblox/open-cloud-key.txt
(o en la variable ROBLOX_API_KEY). Este script la lee y nunca la imprime. El creador es la cuenta de
Valentin (CREATOR abajo; el id de usuario no es secreto).

Lo subido queda en assets/models/western/_roblox.json con el hash del archivo: si el archivo no
cambió, no se vuelve a subir (cada subida crea un asset nuevo en el inventario). Un Model de Open
Cloud llega como paquete (docs, 2026-10-28): al insertarlo en Studio se le saca el PackageLink.
"""

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"
REGISTRY = MODELS / "_roblox.json"
KEY_FILE = Path.home() / ".roblox" / "open-cloud-key.txt"
CREATOR = {"userId": "117522482"}          # StudioService:GetUserId() de la sesión de Valentin, 2026-10-28
ASSETS_URL = "https://apis.roblox.com/assets/v1/assets"
OPERATION_URL = "https://apis.roblox.com/assets/v1/operations/{op}"
CONTENT_TYPES = {".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".fbx": "model/fbx",
                 ".rbxm": "model/x-rbxm", ".rbxmx": "model/x-rbxm"}


def api_key():
    key = os.environ.get("ROBLOX_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit(f"falta la API key: la crea Valentin y la guarda en {KEY_FILE} (ver docstring)")
    return key


def load():
    return json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {"models": {}, "animations": {}}


def save(reg):
    tmp = REGISTRY.with_suffix(f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(reg, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, REGISTRY)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(method, url, key, body=None, headers=None):
    req = urllib.request.Request(url, data=body, method=method, headers={"x-api-key": key, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:      # el cuerpo explica el rechazo; la key no aparece en él
        raise SystemExit(f"{method} {url} -> {e.code}: {e.read().decode('utf-8', 'replace')[:800]}")


def upload(path, asset_type, name, description):
    """Crea el asset, espera a que la operación termine (un 200 es aceptación, no fin) y devuelve el id."""
    key = api_key()
    boundary = uuid.uuid4().hex
    meta = {"assetType": asset_type, "displayName": name[:50], "description": description,
            "creationContext": {"creator": CREATOR}}
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"request\"\r\nContent-Type: application/json\r\n\r\n".encode()
        + json.dumps(meta).encode() + b"\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"fileContent\"; filename=\"{path.name}\"\r\n"
        f"Content-Type: {CONTENT_TYPES[path.suffix.lower()]}\r\n\r\n".encode() + path.read_bytes() + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    body = request("POST", ASSETS_URL, key, b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    op = body.get("operationId") or body.get("path", "").rsplit("/", 1)[-1]
    t0 = time.time()
    while time.time() - t0 < 300:
        b = request("GET", OPERATION_URL.format(op=op), key)
        if b.get("done"):
            aid = (b.get("response") or {}).get("assetId")
            if not aid:
                raise SystemExit(f"{name}: la operación terminó sin assetId: {b}")
            return str(aid)
        time.sleep(2)
    raise SystemExit(f"{name}: la operación {op} no terminó en 300 s; consultarla de nuevo, no volver a subir")


def model_glb(model_id):
    hits = list(MODELS.glob(f"*/{model_id}/03_export/{model_id}.glb"))
    if not hits:
        raise SystemExit(f"no está {model_id}/03_export/{model_id}.glb: construir el modelo primero")
    return hits[0]


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    reg = load()
    if args[0] == "model":
        mid = args[1]
        path = model_glb(mid)
        h = sha(path)
        prev = reg["models"].get(mid)
        if prev and prev["sha256"] == h:
            print(f"{mid}: ya subido, sin cambios -> {prev['assetId']}")
            return
        aid = upload(path, "Model", mid, f"Dead Man's Rail, {mid} (fábrica de modelos).")
        reg["models"][mid] = {"assetId": aid, "sha256": h, "date": str(date.today()),
                              "previous": ([prev["assetId"]] + prev.get("previous", [])) if prev else []}
        save(reg)
        print(f"{mid}: Model {aid}")
    elif args[0] == "animation":
        path, name = Path(args[1]), args[2]
        h = sha(path)
        prev = reg["animations"].get(name)
        if prev and prev["sha256"] == h:
            print(f"{name}: ya subida, sin cambios -> {prev['assetId']}")
            return
        aid = upload(path, "Animation", name, f"Dead Man's Rail, animación {name}.")
        reg["animations"][name] = {"assetId": aid, "sha256": h, "date": str(date.today()), "file": str(path),
                                   "previous": ([prev["assetId"]] + prev.get("previous", [])) if prev else []}
        save(reg)
        print(f"{name}: Animation {aid}")
    elif args[0] == "status":
        for mid, e in sorted(reg["models"].items()):
            try:
                changed = sha(model_glb(mid)) != e["sha256"]
            except SystemExit:
                changed = None
            print(f"model     {mid:32} {e['assetId']:>16}  {'CAMBIÓ: volver a subir' if changed else ''}")
        for name, e in sorted(reg["animations"].items()):
            print(f"animation {name:32} {e['assetId']:>16}")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")   # la consola de Windows no es UTF-8
    main()

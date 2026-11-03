"""
Cola de la fábrica de modelos: qué sigue, en qué estado está cada uno y por qué.

  py -I tools/model_queue.py next                 el próximo modelo a construir (o "nada")
  py -I tools/model_queue.py set <Id> <estado> ["nota"]
  py -I tools/model_queue.py list                 resumen por estado
  py -I tools/model_queue.py show <Id>

Estados: pendiente · construido (pasa todo, espera revisión humana) · aprobado (lo aprobó Valentin) ·
rehacer (Valentin pidió cambios: va primero) · falló (no convergió; se reintenta hasta 3 veces) ·
bloqueado (espera una decisión de diseño; no se toca).

El orden es el de assets/models/western/_prompts/_INDICE.md. El estado vive en
assets/models/western/_estado.json, así cualquier sesión puede retomar donde quedó la anterior.
"""

import json
import os
import re
import sys
import time
from contextlib import contextmanager
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "assets" / "models" / "western" / "_prompts" / "_INDICE.md"
STATE = REPO / "assets" / "models" / "western" / "_estado.json"
STATES = ("pendiente", "construido", "aprobado", "rehacer", "falló", "bloqueado")
MAX_TRIES = 3

# Lo que espera una decisión de diseño (ver "Abierto" del documento de prompts) arranca bloqueado
INITIAL = {
    "WST_Boss_Preacher_TrueForm": ("bloqueado", "¿La verdadera forma es la 'casi hecha de plata'? Decide Valentin."),
    "WST_Train_StockCar": ("bloqueado", "Solo si los caballos van en el tren (choca con D003)."),
    "WST_Canyon_BrokenBridge": ("bloqueado", "No está definido cómo se cruza el puente roto."),
    "WST_Prop_Crate": ("construido", "Pieza de medición, de Claude Design; ya medida en Studio."),
    "WST_Weapon_Revolver": ("rehacer", "La versión de Claude Design no tiene LoadingGate ni EjectorRod separados (recarga)."),
    "WST_Enemy_Walker_A": ("construido", "Piloto de la receta (2026-10-28)."),
}


def order():
    ids = re.findall(r"^\| \d+ \| `(WST_[A-Za-z_]+)` \|", INDEX.read_text(encoding="utf-8"), re.M)
    if not ids:
        raise SystemExit(f"no hay modelos en {INDEX}: correr py -I tools/build_model_prompts.py")
    return ids


def load():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    st = {}
    for mid, (estado, nota) in INITIAL.items():
        st[mid] = {"estado": estado, "intentos": 0, "notas": [f"{date.today()}: {nota}"]}
    save(st)
    return st


def save(st):
    tmp = STATE.with_suffix(f".{os.getpid()}.tmp")    # escritura atómica: nadie lee un archivo a medias
    tmp.write_text(json.dumps(st, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, STATE)


@contextmanager
def locked():
    """Candado entre procesos: varios agentes pueden correr `set` a la vez sin pisarse los cambios."""
    lock = STATE.with_suffix(".lock")
    for _ in range(300):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > 30:    # candado viejo de un proceso que murió
                    lock.unlink(missing_ok=True)
            except FileNotFoundError:
                pass
            time.sleep(0.1)
    else:
        raise SystemExit(f"no se pudo tomar {lock}")
    try:
        yield
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def prompt_file(mid):
    for p in sorted(INDEX.parent.glob(f"*_{mid}.txt")):
        return p
    return None


def next_model(st):
    ids = order()
    for mid in ids:                                   # primero lo que Valentin pidió rehacer
        if st.get(mid, {}).get("estado") == "rehacer":
            return mid
    for mid in ids:
        e = st.get(mid, {"estado": "pendiente", "intentos": 0})
        if e["estado"] == "pendiente" or (e["estado"] == "falló" and e["intentos"] < MAX_TRIES):
            return mid
    return None


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    with locked():
        run(args)


def run(args):
    st = load()
    cmd = args[0]
    if cmd == "next":
        mid = next_model(st)
        if not mid:
            print("nada: no quedan modelos pendientes, a rehacer ni fallados con intentos")
            return
        e = st.get(mid, {"estado": "pendiente", "intentos": 0, "notas": []})
        print(json.dumps({"id": mid, "estado": e["estado"], "intentos": e["intentos"],
                          "prompt": str(prompt_file(mid).relative_to(REPO)) if prompt_file(mid) else None,
                          "notas": e.get("notas", [])[-3:]}, ensure_ascii=False, indent=1))
    elif cmd == "set":
        if len(args) < 3 or args[2] not in STATES:
            raise SystemExit(f"uso: set <Id> <estado> [nota]; estados: {', '.join(STATES)}")
        mid, estado = args[1], args[2]
        if mid not in order():
            raise SystemExit(f"{mid} no está en el índice")
        e = st.setdefault(mid, {"estado": "pendiente", "intentos": 0, "notas": []})
        if estado in ("construido", "falló"):
            e["intentos"] += 1
        e["estado"] = estado
        if len(args) > 3:
            e["notas"].append(f"{date.today()}: {args[3]}")
        save(st)
        print(f"{mid}: {estado} (intentos {e['intentos']})")
        sys.path.insert(0, str(REPO / "tools" / "viewer"))
        import build_index                           # el visor muestra el estado nuevo sin esperar otra construcción
        build_index.build()
    elif cmd == "list":
        ids = order()
        counts = {s: 0 for s in STATES}
        for mid in ids:
            counts[st.get(mid, {}).get("estado", "pendiente")] += 1
        print(f"{len(ids)} modelos: " + " · ".join(f"{k} {v}" for k, v in counts.items() if v))
        for s in ("rehacer", "falló", "bloqueado"):
            for mid in ids:
                if st.get(mid, {}).get("estado") == s:
                    print(f"  {s:9} {mid}  {st[mid]['notas'][-1] if st[mid]['notas'] else ''}")
    elif cmd == "show":
        print(json.dumps(st.get(args[1], {"estado": "pendiente"}), ensure_ascii=False, indent=1))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no es UTF-8
    main()

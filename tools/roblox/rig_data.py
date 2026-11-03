"""
Datos del rig de un personaje de la fábrica, para tools/roblox/rig_build.luau.

  py -I tools/roblox/rig_data.py glb <Id> <Nombre>          escribe 04_roblox/<Id>.rig.json desde 03_export/<Id>.glb
  py -I tools/roblox/rig_data.py ids <Id> <studio.json>     le suma los ids de malla y textura leídos en Studio

Un GLB con varios personajes (los Hermanos Doyle: "Brute_Head", "Shooter_Head"...) se separa por prefijo:

  py -I tools/roblox/rig_data.py glb <Id> <Nombre> <prefijo>      escribe 04_roblox/<Id>.<Nombre>.rig.json
  py -I tools/roblox/rig_data.py ids <Id> <studio.txt> <Nombre>

Se quedan los nodos con ese prefijo, sin él, y corridos en X y Z para que la articulación de LowerTorso
quede en x = z = 0. El prefijo y el corrimiento se guardan en "source", e "ids" los aplica a lo leído en
Studio (ahí las MeshParts conservan el nombre con prefijo y la posición del GLB).

El GLB de 03_export está girado 180° para el importador de Studio (process_model.rotate_for_studio):
en coordenadas de Roblox (+X derecha, -Z frente, igual que las recetas) un punto del GLB (x, y, z) es
(-x, y, -z). El origen de cada nodo es su articulación; el centro y el tamaño salen del min/max del
accessor POSITION. "ids" compara además lo que dejó la subida (centro y tamaño de cada MeshPart) con lo
calculado acá: si no coincide a 0,01, algo cambió en el camino y no se arma el rig.

Lo subido no trae la articulación: InsertService:LoadAsset devuelve cada nodo como un Model "<Pieza>_Node"
con WorldPivot en 0 y la MeshPart adentro (medido el 2026-10-28). La articulación sale siempre del GLB;
"origin" solo se compara si el JSON de Studio lo trae.
"""

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"


def model_dir(model_id):
    hits = [p for p in MODELS.glob(f"*/{model_id}") if p.is_dir()]
    if not hits:
        raise SystemExit(f"no está la carpeta de {model_id}")
    return hits[0]


def read_glb(path):
    b = path.read_bytes()
    n = struct.unpack_from("<I", b, 12)[0]
    return json.loads(b[20:20 + n])


def studio_material(folder, model_id):
    """Pieza cuyo único color pide otro Material de Studio (Neon, Glass, Metal): ese Material."""
    rep = folder / "report.json"
    if not rep.exists():
        return {}
    objs = json.loads(rep.read_text(encoding="utf-8")).get("objects", {})
    return {name: o["studio_material"][0] for name, o in objs.items()
            if len(o.get("studio_material") or []) == 1 and len(o.get("colors", [])) == 1}


def rig_path(folder, model_id, name=None):
    return folder / "04_roblox" / (f"{model_id}.{name}.rig.json" if name else f"{model_id}.rig.json")


def from_glb(model_id, name, prefix=None):
    folder = model_dir(model_id)
    j = read_glb(folder / "03_export" / f"{model_id}.glb")
    mats = studio_material(folder, model_id)
    nodes = []
    for nd in j["nodes"]:
        if "mesh" not in nd:
            continue
        if prefix and not nd["name"].startswith(prefix):
            continue
        if nd.get("rotation") or nd.get("scale"):
            raise SystemExit(f"{nd['name']}: el nodo trae rotación o escala; la fábrica deja solo traslación")
        t = nd.get("translation", [0, 0, 0])
        acc = j["accessors"][j["meshes"][nd["mesh"]]["primitives"][0]["attributes"]["POSITION"]]
        lo, hi = acc["min"], acc["max"]
        origin = [-t[0], t[1], -t[2]]
        center = [origin[0] - (lo[0] + hi[0]) / 2, origin[1] + (lo[1] + hi[1]) / 2, origin[2] - (lo[2] + hi[2]) / 2]
        node = {"name": nd["name"][len(prefix):] if prefix else nd["name"], "origin": origin, "cframe": center,
                "size": [round(hi[i] - lo[i], 4) for i in range(3)]}
        if nd["name"] in mats:
            node["material"] = mats[nd["name"]]
        nodes.append(node)
    source = None
    if prefix:
        if not nodes:
            raise SystemExit(f"ningún nodo empieza con {prefix}")
        hip = next((n["origin"] for n in nodes if n["name"] == "LowerTorso"), None)
        if hip is None:
            raise SystemExit(f"{prefix}: falta LowerTorso, que define dónde queda el personaje")
        shift = [-hip[0], 0, -hip[2]]
        for n in nodes:
            n["origin"] = [n["origin"][i] + shift[i] for i in range(3)]
            n["cframe"] = [n["cframe"][i] + shift[i] for i in range(3)]
        source = {"prefix": prefix, "shift": [round(v, 4) for v in shift]}
    for n in nodes:
        n["origin"] = [round(v, 4) for v in n["origin"]]
        n["cframe"] = [round(v, 4) for v in n["cframe"]] + [1, 0, 0, 0, 1, 0, 0, 0, 1]
    out = rig_path(folder, model_id, name if prefix else None)
    out.parent.mkdir(exist_ok=True)
    # lo que no sale del GLB y se agregó a mano ("skeleton" de una criatura, "rightGrip" de un NPC, el "weldTo" de
    # un nodo) se conserva. Los ids de Studio no: si cambió el GLB, hay que subirlo y leerlos de nuevo.
    keep = {}
    if out.exists():
        old = json.loads(out.read_text(encoding="utf-8"))
        keep = {k: v for k, v in old.items() if k not in ("name", "id", "nodes")}
        welds = {n["name"]: n["weldTo"] for n in old.get("nodes", []) if "weldTo" in n}
        for node in nodes:
            if node["name"] in welds:
                node["weldTo"] = welds[node["name"]]
    if source:
        keep["source"] = source
    out.write_text(json.dumps({"name": name, "id": model_id, "nodes": nodes, **keep}, indent=1) + "\n", encoding="utf-8")
    print(f"{len(nodes)} nodos -> {out.relative_to(REPO)}")


def parse_studio_txt(text):
    """Una línea por MeshPart, como la imprime tools/roblox/studio_nodes.luau:
    nombre|cx,cy,cz|sx,sy,sz|mx,my,mz|meshId|textureId|I (o los 9 números de la rotación)."""
    nodes = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, c, s, m, mesh, tex, rot = line.split("|")
        num = lambda t: [float(v) for v in t.split(",")]
        r = [1, 0, 0, 0, 1, 0, 0, 0, 1] if rot == "I" else num(rot)
        nodes.append({"name": name, "cframe": [round(v, 4) for v in num(c)] + r, "size": num(s), "meshSize": num(m),
                      "mesh": f"rbxassetid://{mesh}", "texture": f"rbxassetid://{tex}" if tex else None})
    return {"nodes": nodes}


def add_ids(model_id, studio_json, name=None):
    folder = model_dir(model_id)
    path = rig_path(folder, model_id, name)
    rig = json.loads(path.read_text(encoding="utf-8"))
    raw = Path(studio_json).read_text(encoding="utf-8")
    data = parse_studio_txt(raw) if studio_json.endswith(".txt") else json.loads(raw)
    studio = {n["name"]: n for n in data["nodes"]}
    src = rig.get("source")
    if src:  # uno de varios personajes del mismo GLB: el nombre sin prefijo y la posición corrida
        pre, sh = src["prefix"], src["shift"]
        studio = {k[len(pre):]: {**n, "cframe": [round(n["cframe"][i] + sh[i], 4) for i in range(3)] + n["cframe"][3:]}
                  for k, n in studio.items() if k.startswith(pre)}
    bad = []
    for node in rig["nodes"]:
        s = studio.get(node["name"])
        if not s:
            bad.append(f"{node['name']}: no está en lo subido")
            continue
        for key in ("origin", "size"):
            if key in s and max(abs(a - b) for a, b in zip(node[key], s[key])) > 0.01:
                bad.append(f"{node['name']}.{key}: GLB {node[key]} vs subido {s[key]}")
        center = s["cframe"][:3]
        if max(abs(a - b) for a, b in zip(node["cframe"][:3], center)) > 0.01:
            bad.append(f"{node['name']}: centro GLB {node['cframe'][:3]} vs subido {center}")
        node["cframe"] = s["cframe"]
        node["mesh"], node["texture"], node["meshSize"] = s["mesh"], s.get("texture"), s["meshSize"]
    if bad:
        raise SystemExit("no coincide lo subido con el GLB:\n  " + "\n  ".join(bad))
    path.write_text(json.dumps(rig, indent=1) + "\n", encoding="utf-8")
    print(f"ids de {len(rig['nodes'])} piezas -> {path.relative_to(REPO)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if len(a) in (3, 4) and a[0] == "glb":
        from_glb(*a[1:])
    elif len(a) in (3, 4) and a[0] == "ids":
        add_ids(*a[1:])
    else:
        raise SystemExit(__doc__)

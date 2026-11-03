"""
Un objeto en la mano del jugador (D024): rig combinado para animar y modelo de vista previa para el visor.

  py -I tools/roblox/held.py <ItemId> [--grip x,y,z] [--parts A,B] [--name Sufijo] [--extra Id:Pieza@Mano]
                             [--body <rig.json> --drop A,B]

--grip: el punto de agarre en coordenadas del objeto (las de la receta), cuando el objeto no trae el marcador
_Grip (los consumibles de una pieza): dónde cierra la mano, no la base.
--extra <Id>:<Pieza>@<Mano>[,...]: una pieza de otro modelo en una mano, por ejemplo la bala de la recarga
(WST_Item_Rounds:RevolverRound@LeftHand). Su centro va al agarre de esa mano; se anima como cualquier pieza del
objeto (rot/pos/pivot, colgando de la mano). En el juego: una parte con Motor6D a la mano que los marcadores muestran
o esconden.
--parts: solo esas piezas (y sus marcadores), para un archivo con variantes (la dinamita: Stick o Bundle);
--name: sufijo del modelo de vista previa en ese caso (WST_Held_Weapon_Dynamite_Stick).
--body: otro cuerpo en vez del jugador, por ejemplo un NPC (04_roblox/<Id>.rig.json de rig_data.py). Tiene que traer
"rightGrip": el punto de agarre de su mano derecha en sus coordenadas (rig_build lo vuelve RightGripAttachment).
--drop: piezas del cuerpo que no van en ese rig (la Viuda enfundada de Old Hank cuando la tiene en la mano). Con
--body, usá --name para no pisar el rig del jugador (WST_Held_Weapon_HanksWidow_OldHank).
La raíz es "Body" si existe; si no, la pieza cuya caja contiene el agarre (_Grip o --grip), y sin agarre la más grande.

- Lee el R15 por defecto (assets/animation/western/player/PlayerR15.rig.json, medido en Studio) y el GLB final
  del objeto (03_export, girado 180°: en coordenadas de Roblox un punto del GLB (x, y, z) es (-x, y, -z)).
- Pone el objeto en la mano como lo va a poner el juego: su marcador _Grip sobre el RightGripAttachment, sin
  rotación (los ejes del objeto son los de la mano). La raíz es "Body" (o la pieza que contiene el _Grip) y
  cuelga de RightHand; el resto de las piezas cuelga de la raíz.
- Escribe assets/animation/western/held/<Id corto>.rig.json (para anim_preview.py, con "tree": de quién cuelga
  cada pieza del objeto) y el modelo WST_Held_<Id corto> en assets/models/western/previews/ (jugador de cajas
  grises + las mallas del objeto), que el visor lista como cualquier otro modelo.
"""

import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"
PLAYER = REPO / "assets" / "animation" / "western" / "player" / "PlayerR15.rig.json"
OUT_RIG = REPO / "assets" / "animation" / "western" / "held"


def read_glb(path):
    b = path.read_bytes()
    n = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n
    m = struct.unpack_from("<I", b, off)[0]
    return j, bytearray(b[off + 8: off + 8 + m])


def game(v):
    return [-v[0], v[1], -v[2]]


def item_nodes(j):
    out = {}
    for nd in j["nodes"]:
        if "mesh" not in nd:
            continue
        t = nd.get("translation", [0, 0, 0])
        acc = j["accessors"][j["meshes"][nd["mesh"]]["primitives"][0]["attributes"]["POSITION"]]
        lo, hi = acc["min"], acc["max"]
        origin = game(t)
        center = [origin[0] - (lo[0] + hi[0]) / 2, origin[1] + (lo[1] + hi[1]) / 2, origin[2] - (lo[2] + hi[2]) / 2]
        out[nd["name"]] = {"origin": origin, "center": center, "size": [hi[i] - lo[i] for i in range(3)], "node": nd}
    return out


def box(center, size):
    """24 vértices con normales planas y 36 índices de una caja (coordenadas del marco del GLB)."""
    cx, cy, cz = center
    hx, hy, hz = (s / 2 for s in size)
    pos, nor, idx = [], [], []
    faces = [((1, 0, 0), [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)]), ((-1, 0, 0), [(-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1)]),
             ((0, 1, 0), [(-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)]), ((0, -1, 0), [(-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1)]),
             ((0, 0, 1), [(1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, -1, 1)]), ((0, 0, -1), [(-1, -1, -1), (-1, 1, -1), (1, 1, -1), (1, -1, -1)])]
    for n, quad in faces:
        base = len(pos) // 3
        for sx, sy, sz in quad:
            pos += [cx + sx * hx, cy + sy * hy, cz + sz * hz]
            nor += list(n)
        idx += [base, base + 1, base + 2, base, base + 2, base + 3]
    return pos, nor, idx


def merge_mesh(j, binary, j2, bin2, node_name):
    """Copia al glTF j la malla del nodo `node_name` de j2 (con sus accessors, vistas, material, textura e imagen,
    corriendo los índices). Devuelve el índice de la malla nueva en j."""
    nd = next(n for n in j2["nodes"] if n.get("name") == node_name and "mesh" in n)
    mesh = json.loads(json.dumps(j2["meshes"][nd["mesh"]]))
    view_map, acc_map, mat_map, tex_map, img_map = {}, {}, {}, {}, {}

    def view(i):
        if i not in view_map:
            v = dict(j2["bufferViews"][i])
            data = bin2[v.get("byteOffset", 0): v.get("byteOffset", 0) + v["byteLength"]]
            while len(binary) % 4:
                binary.append(0)
            v["byteOffset"], v["buffer"] = len(binary), 0
            binary.extend(data)
            j["bufferViews"].append(v)
            view_map[i] = len(j["bufferViews"]) - 1
        return view_map[i]

    def acc(i):
        if i not in acc_map:
            a = dict(j2["accessors"][i])
            a["bufferView"] = view(a["bufferView"])
            j["accessors"].append(a)
            acc_map[i] = len(j["accessors"]) - 1
        return acc_map[i]

    def image(i):
        if i not in img_map:
            im = dict(j2["images"][i])
            if "bufferView" in im:
                im["bufferView"] = view(im["bufferView"])
            j.setdefault("images", []).append(im)
            img_map[i] = len(j["images"]) - 1
        return img_map[i]

    def texture(i):
        if i not in tex_map:
            t = dict(j2["textures"][i])
            if "source" in t:
                t["source"] = image(t["source"])
            if "sampler" in t:
                j.setdefault("samplers", []).append(dict(j2["samplers"][t["sampler"]]))
                t["sampler"] = len(j["samplers"]) - 1
            j.setdefault("textures", []).append(t)
            tex_map[i] = len(j["textures"]) - 1
        return tex_map[i]

    def material(i):
        if i not in mat_map:
            m = json.loads(json.dumps(j2["materials"][i]))
            pbr = m.get("pbrMetallicRoughness", {})
            if "baseColorTexture" in pbr:
                pbr["baseColorTexture"]["index"] = texture(pbr["baseColorTexture"]["index"])
            j.setdefault("materials", []).append(m)
            mat_map[i] = len(j["materials"]) - 1
        return mat_map[i]

    for prim in mesh["primitives"]:
        prim["attributes"] = {k: acc(v) for k, v in prim["attributes"].items()}
        if "indices" in prim:
            prim["indices"] = acc(prim["indices"])
        if "material" in prim:
            prim["material"] = material(prim["material"])
    j["meshes"].append(mesh)
    return len(j["meshes"]) - 1


def main(item_id, grip_override=None, only=None, suffix=None, extras=(), body=None, drop=()):
    hits = list(MODELS.glob(f"*/{item_id}/03_export/{item_id}.glb"))
    if not hits:
        raise SystemExit(f"no está {item_id}/03_export/{item_id}.glb")
    j, binary = read_glb(hits[0])
    player = json.loads((Path(body) if body else PLAYER).read_text(encoding="utf-8"))
    if "rightGrip" not in player:
        raise SystemExit(f"{body}: falta \"rightGrip\" (el punto de agarre de la mano derecha, en coordenadas del cuerpo)")
    if body and not suffix:
        raise SystemExit("con --body pasá --name, para no pisar el rig del jugador con el mismo objeto")
    player["nodes"] = [n for n in player["nodes"] if n["name"] not in set(drop)]
    nodes = item_nodes(j)
    if only:
        keep = set(only)
        nodes = {k: v for k, v in nodes.items() if k in keep or (k.startswith("_") and any(k.endswith(o) for o in keep))}
        for nd in j["nodes"]:                    # se dejan los nodos (los índices de los hijos no cambian), sin malla
            if "mesh" in nd and nd["name"] not in nodes:
                del nd["mesh"]
    grip = nodes["_Grip"]["center"] if "_Grip" in nodes else None
    parts = [n for n in nodes if not n.startswith("_")]

    def box_dist(n, at):
        return sum(max(abs(at[i] - nodes[n]["center"][i]) - nodes[n]["size"][i] / 2, 0) ** 2 for i in range(3)) ** 0.5
    def volume(n):
        return nodes[n]["size"][0] * nodes[n]["size"][1] * nodes[n]["size"][2]
    at = grip_override or grip
    root = "Body" if "Body" in nodes else (min(parts, key=lambda n: (box_dist(n, at), -volume(n))) if at else max(parts, key=volume))
    if grip_override is not None:
        grip = grip_override
    if grip is None:
        print(f"  aviso: {item_id} no tiene _Grip; la mano va al origen de {root} (pasá --grip x,y,z si no es ahí)")
        grip = nodes[root]["origin"]
    hand = player["rightGrip"]
    shift = [hand[i] - grip[i] for i in range(3)]
    short = item_id.replace("WST_", "") + (f"_{suffix}" if suffix else "")
    pid = f"WST_Held_{short}"

    # ---- rig combinado ----
    rig = {"name": pid, "id": pid, "item": item_id, "root": root, "grip": grip,
           "_nota": f"{'cuerpo ' + player.get('id', '?') if body else 'jugador R15 por defecto'} + objeto en la mano "
                    "(tools/roblox/held.py, D024)",
           "nodes": list(player["nodes"]), "tree": {}}
    for name, n in nodes.items():
        if name.startswith("_"):
            continue
        # la articulación de la raíz es el agarre (ahí gira el Motor6D del juego), no el origen de la pieza:
        # con --grip lejos del origen la vista previa corría el objeto hasta 1,1 studs (whisky, 2026-10-28)
        origin = list(hand) if name == root else [n["origin"][i] + shift[i] for i in range(3)]
        rig["nodes"].append({"name": name, "origin": origin,
                             "cframe": [n["center"][i] + shift[i] for i in range(3)] + [1, 0, 0, 0, 1, 0, 0, 0, 1],
                             "size": n["size"]})
        rig["tree"][name] = "RightHand" if name == root else root
    # marcadores del objeto (_Grip2 = donde va la mano izquierda, _Muzzle...): posición en reposo y pieza que los lleva
    # cada marcador va con la pieza que lo contiene (el _Grip2 de la escopeta está en Barrels, no en Stock)
    rig["markers"] = {name: {"pos": [n["center"][i] + shift[i] for i in range(3)],
                             "part": min(parts, key=lambda q: (box_dist(q, n["center"]), q != root))}
                      for name, n in nodes.items() if name.startswith("_")}
    for name, m in rig["markers"].items():         # nodos chicos: el visor los mueve con su pieza (VFX en _Muzzle)
        rig["nodes"].append({"name": name, "origin": list(m["pos"]), "cframe": list(m["pos"]) + [1, 0, 0, 0, 1, 0, 0, 0, 1],
                             "size": [0.02, 0.02, 0.02]})
        rig["tree"][name] = m["part"]
    # piezas de otro modelo en una mano (la bala o el cartucho que la izquierda mete en la recarga): su centro va al
    # agarre de esa mano (el de la izquierda es el de la derecha espejado), sin rotación; cuelgan de la mano
    extra_glbs = []
    for spec in extras:
        other, rest = spec.split(":")
        part, hand_name = rest.split("@")
        found = list(MODELS.glob(f"*/{other}/03_export/{other}.glb"))
        if not found:
            raise SystemExit(f"--extra: no está {other}/03_export/{other}.glb")
        j2, bin2 = read_glb(found[0])
        n2 = item_nodes(j2)[part]
        g = list(player["rightGrip"]) if hand_name == "RightHand" else [-player["rightGrip"][0]] + list(player["rightGrip"][1:])
        center = [g[i] + n2["center"][i] - n2["origin"][i] for i in range(3)]
        rig["nodes"].append({"name": part, "origin": g, "cframe": center + [1, 0, 0, 0, 1, 0, 0, 0, 1], "size": n2["size"]})
        rig["tree"][part] = hand_name
        extra_glbs.append((j2, bin2, part, g))
    OUT_RIG.mkdir(parents=True, exist_ok=True)
    (OUT_RIG / f"{short}.rig.json").write_text(json.dumps(rig, indent=1) + "\n", encoding="utf-8")

    # ---- modelo de vista previa: se agregan cajas del jugador al GLB del objeto ----
    gshift = game(shift)
    for nd in j["nodes"]:
        if "mesh" in nd:
            t = nd.get("translation", [0, 0, 0])
            nd["translation"] = [t[i] + gshift[i] for i in range(3)]
    j.setdefault("materials", []).append({"name": "Player", "pbrMetallicRoughness": {
        "baseColorFactor": [0.42, 0.44, 0.48, 1], "metallicFactor": 0, "roughnessFactor": 1}})
    mat = len(j["materials"]) - 1
    tris = sum(j["accessors"][p["indices"]]["count"] // 3 for m in j["meshes"] for p in m["primitives"] if "indices" in p)
    new_nodes = []
    for pn in player["nodes"]:
        o = game(pn["origin"])
        c = game([pn["cframe"][i] - pn["origin"][i] for i in range(3)])
        pos, nor, idx = box(c, pn["size"])
        acc_ids = []
        for data, fmt, comp, typ, count in ((pos, "f", 5126, "VEC3", 24), (nor, "f", 5126, "VEC3", 24), (idx, "H", 5123, "SCALAR", 36)):
            while len(binary) % 4:
                binary.append(0)
            off = len(binary)
            binary.extend(struct.pack(f"<{len(data)}{fmt}", *data))
            j["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": len(data) * (4 if fmt == "f" else 2)})
            acc = {"bufferView": len(j["bufferViews"]) - 1, "componentType": comp, "count": count, "type": typ}
            if typ == "VEC3" and len(acc_ids) == 0:
                acc["min"] = [min(pos[i::3]) for i in range(3)]
                acc["max"] = [max(pos[i::3]) for i in range(3)]
            j["accessors"].append(acc)
            acc_ids.append(len(j["accessors"]) - 1)
        j["meshes"].append({"name": pn["name"], "primitives": [{"attributes": {"POSITION": acc_ids[0], "NORMAL": acc_ids[1]},
                                                              "indices": acc_ids[2], "material": mat}]})
        j["nodes"].append({"name": pn["name"], "mesh": len(j["meshes"]) - 1, "translation": o})
        new_nodes.append(len(j["nodes"]) - 1)
        tris += 12
    for j2, bin2, part, g in extra_glbs:
        mi = merge_mesh(j, binary, j2, bin2, part)
        j["nodes"].append({"name": part, "mesh": mi, "translation": game(g)})
        new_nodes.append(len(j["nodes"]) - 1)
        tris += sum(j["accessors"][pr["indices"]]["count"] // 3 for pr in j["meshes"][mi]["primitives"] if "indices" in pr)
    scene = j["scenes"][j.get("scene", 0)]
    parent = next((n for n in scene["nodes"] if "children" in j["nodes"][n]), None)
    (j["nodes"][parent]["children"] if parent is not None else scene["nodes"]).extend(new_nodes)
    while len(binary) % 4:
        binary.append(0)
    j["buffers"] = [{"byteLength": len(binary)}]
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(binary), 0x004E4942) + bytes(binary)
    folder = MODELS / "previews" / pid
    (folder / "03_export").mkdir(parents=True, exist_ok=True)
    (folder / "03_export" / f"{pid}.glb").write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)
    (folder / "report.json").write_text(json.dumps({"id": pid, "pass": True, "tris": {"after": tris}, "errors": [], "warnings": [],
                                                    "nota": f"vista previa de {item_id} en la mano del R15 por defecto (held.py)"},
                                                   indent=1, ensure_ascii=False), encoding="utf-8")
    sys.path.insert(0, str(REPO / "tools" / "viewer"))
    import build_index
    build_index.build()
    print(f"{item_id}: raíz {root}, _Grip -> mano {[round(v, 3) for v in hand]} · {len(rig['tree'])} piezas del objeto")
    print(f"  rig    {(OUT_RIG / f'{short}.rig.json').relative_to(REPO)}")
    print(f"  visor  http://127.0.0.1:8765/tools/viewer/?id={pid}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    opts = dict(zip(args[1::2], args[2::2]))
    if any(k not in ("--grip", "--parts", "--name", "--extra", "--body", "--drop") for k in opts) or len(args) % 2 == 0:
        raise SystemExit(__doc__)
    main(args[0], [float(v) for v in opts["--grip"].split(",")] if "--grip" in opts else None,
         opts["--parts"].split(",") if "--parts" in opts else None, opts.get("--name"),
         opts["--extra"].split(",") if "--extra" in opts else (), opts.get("--body"),
         opts["--drop"].split(",") if "--drop" in opts else ())

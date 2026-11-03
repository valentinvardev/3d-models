"""
Arma los modelos del pueblo (Dusty Gulch) y del loot con las mallas ya subidas del kit, para el juego.

  py -I tools/roblox/town.py loot                 assets/models/rbx/Loot/Coin.rbxm
  py -I tools/roblox/town.py town [<id> ...]      assets/models/rbx/Town/<id>.rbxm (sin ids: todos los que hay)
  py -I tools/roblox/town.py props [<tipo> ...]   assets/models/rbx/Props/<tipo>.rbxm

Lee las piezas de 04_roblox/<Id>.rig.json (rig_data.py glb + ids: centro, tamaño y mallas de cada nodo, en
coordenadas del juego) y las cajas del mapa de src/shared/Maps/DustyGulch.json (de la sesión del juego; se pasa
con --map si no está en este checkout). Escribe un layout por modelo en assets/models/western/_town/ y lo arma
con tools/roblox/prop_build.luau, que tiene el contrato con el juego.

Cada modelo tiene el origen en el centro de la caja de su pieza del mapa y ya viene orientado (+X, +Y, +Z del
mapa). Las piezas rompibles (columnas, techos de porche, cajones, barriles) no se salen de su caja: si se salen,
no se escribe el rbxm.
"""

import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"
RBX = REPO / "assets" / "models" / "rbx"
LAYOUTS = MODELS / "_town"
TOL = 0.02  # lo que se tolera fuera de la caja en una pieza rompible

_rigs = {}


def rig(model_id):
    if model_id not in _rigs:
        hits = list(MODELS.glob(f"*/{model_id}/04_roblox/{model_id}.rig.json"))
        if not hits:
            raise SystemExit(f"falta 04_roblox/{model_id}.rig.json (rig_data.py glb + ids)")
        data = json.loads(hits[0].read_text(encoding="utf-8"))
        _rigs[model_id] = {n["name"]: n for n in data["nodes"]}
    return _rigs[model_id]


# ---- transformaciones: posición + rotación (giros de 90° alrededor de Y) ---------------

def yaw(deg):
    """Rotación alrededor de Y como la de CFrame.Angles(0, rad, 0) (positivo: de +Z hacia +X)."""
    c, s = round(math.cos(math.radians(deg)), 6), round(math.sin(math.radians(deg)), 6)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


IDENT = yaw(0)


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(r, v):
    return [sum(r[i][k] * v[k] for k in range(3)) for i in range(3)]


class Frame:
    """Dónde va un grupo de piezas: origen, rotación y escala (en los ejes del grupo, antes de girar)."""

    def __init__(self, pos=(0, 0, 0), rot=IDENT, scale=(1, 1, 1)):
        self.pos, self.rot, self.scale = list(pos), rot, list(scale)

    def place(self, local):
        p = apply(self.rot, [local[i] * self.scale[i] for i in range(3)])
        return [self.pos[i] + p[i] for i in range(3)]


    def sub(self, local, rot=None, scale=(1, 1, 1)):
        """Un frame hijo en `local` (coordenadas de este frame), con la escala multiplicada."""
        return Frame(self.place(local), rot or self.rot, [self.scale[i] * scale[i] for i in range(3)])


def piece(model_id, node, frame, anchor=(0, 0, 0), name=None, squash=(1, 1, 1), **extra):
    """La pieza `node` del modelo, puesta con `frame`; `anchor` es el punto del kit que va al origen del frame.
    `squash` achica la pieza sobre su propio centro (la ménsula de la columna, para que entre en su caja)."""
    n = rig(model_id)[node]
    if n["cframe"][3:] != [1, 0, 0, 0, 1, 0, 0, 0, 1]:
        raise SystemExit(f"{model_id}.{node}: el nodo viene rotado; el pueblo solo arma piezas sin rotar")
    if not n.get("mesh"):
        raise SystemExit(f"{model_id}.{node}: sin malla (falta rig_data.py ids)")
    center = frame.place([n["cframe"][i] - anchor[i] for i in range(3)])
    size = [round(n["size"][i] * frame.scale[i] * squash[i], 4) for i in range(3)]
    rot = frame.rot
    p = {"name": name or node, "src": [model_id, node], "mesh": n["mesh"], "texture": n.get("texture"),
         "meshSize": n["meshSize"], "size": size,
         "cframe": [round(v, 4) for v in center] + [v for row in rot for v in row],
         "material": n.get("material", "SmoothPlastic")}
    p.update(extra)
    return p


def group(model_id, prefix, frame, anchor, tag="", **extra):
    """Todas las piezas del modelo cuyo nombre empieza con `prefix` (una variante del kit)."""
    nodes = sorted(k for k in rig(model_id) if k.startswith(prefix) and not k.startswith("_"))
    if not nodes:
        raise SystemExit(f"{model_id}: ninguna pieza empieza con {prefix}")
    return [piece(model_id, k, frame, anchor, name=f"{tag}{k}", **extra) for k in nodes]


def block(name, frame, local, size, color, material="SmoothPlastic"):
    """Una caja lisa (sin malla): el fondo oscuro detrás de ventanas y huecos, los durmientes de la vía."""
    c = frame.place(local)
    rot = frame.rot
    return {"name": name, "block": True, "size": [round(size[i] * frame.scale[i], 4) for i in range(3)],
            "cframe": [round(v, 4) for v in c] + [v for row in rot for v in row], "color": color,
            "material": material}


# ---- edificios ----------------------------------------------------------------------
#
# Cada edificio se arma en coordenadas de su fachada (x a lo largo del frente, y arriba, frente hacia -z, el
# origen en el centro de la caja) y se gira al mapa con el yaw que hace mirar a -z hacia la calle. Las piezas del
# kit son de 8 de ancho: un frente de largo L lleva n = round(L / 8) módulos estirados a L / n.

DOOR, WINDOW, PORCH = "WST_Kit_Door", "WST_Kit_Window", "WST_Kit_Porch"
# Paredes del kit: modelo, espesor y, por variante, el prefijo de sus piezas y dónde está en la fila del kit.
# Todas miden 10 de alto (la falsa fachada, 4) y miran afuera hacia -z.
KITS = {
    "wood": ("WST_Kit_Wall", 0.6, {"Plain": ("Wall_Plain_", 0), "Window": ("Wall_Window_", 8),
                                   "Door": ("Wall_Door_", 16), "DoubleWindow": ("Wall_DoubleWindow_", 24),
                                   "Cracked": ("Wall_Cracked_", 32)}),
    "brick": ("WST_Kit_WallBrick", 0.8, {"Plain": ("Brick_Wall_Plain_", 0), "Window": ("Brick_Wall_Window_", 8),
                                         "Door": ("Brick_Wall_Door_", 16),
                                         "DoubleWindow": ("Brick_Wall_DoubleWindow_", 24)}),
    "stone": ("WST_Kit_WallStone", 1.0, {"Plain": ("Wall_Stone_frag", 0), "Barred": ("Wall_Stone_Barred_", 8)}),
    "ff": ("WST_Kit_FalseFront", 0.6, {"Flat": ("FalseFront_Flat_", 0), "Stepped": ("FalseFront_Stepped_", 8),
                                      "Arched": ("FalseFront_Arched_", 16)}),
    # cercas: el cerco de estacas del cementerio (3,3 de alto) y la baranda del porche para el corral (3)
    "picket": ("WST_HC_CemeteryFence", 0.5, {"Picket": ("Fence_Picket_", 20)}),
    "railing": ("WST_Kit_Porch", 0.4, {"Railing": ("Porch_Railing_", 12)}),
}
WINDOW_X = {"Sash": 0, "Shutters": 8, "Broken": 16}
DARK = [34, 26, 22]  # el adentro que se ve por las ventanas
FACING = {"-x": 90, "+x": -90, "-z": 0, "+z": 180}  # hacia dónde mira el frente -> yaw de la fachada


class Facade:
    def __init__(self, box, facing):
        self.yaw = FACING[facing]
        self.R = yaw(self.yaw)
        across = abs(self.yaw) == 90
        self.L, self.H, self.D = (box[2], box[1], box[0]) if across else (box[0], box[1], box[2])
        self.front = apply(self.R, [0, 0, -1])

    def frame(self, local, module_yaw=0, scale=(1, 1, 1)):
        return Frame(apply(self.R, local), mul(self.R, yaw(module_yaw)), scale)


def modules(length):
    n = max(1, round(length / 8))
    return n, length / n


def wall_side(fac, side, kinds, y0, sy, thick=0.6, flip=False, ends=(0.6, 0.6), widths=None):
    """Una fila de módulos del kit (uno por variante de `kinds`, estirados al largo) en un lado de la caja:
    "front", "back", "left", "right". Los costados van entre el frente y el fondo (`ends`: sus espesores).
    `flip` da vuelta la pared: afuera queda la cara de adentro (la madera sin pintar).
    `widths`: el ancho de cada módulo (suman el largo); sin eso, todos iguales.
    Devuelve, por módulo, (variante, frame de la pared, frame que mira afuera) para los huecos."""
    L, D = fac.L, fac.D
    if side in ("front", "back"):
        length, mid = L, 0
    else:
        length, mid = D - ends[0] - ends[1], (ends[0] - ends[1]) / 2
    n = len(kinds)
    ws = widths or [length / n] * n
    if abs(sum(ws) - length) > 1e-6:
        raise SystemExit(f"los anchos de la pared {side} suman {sum(ws)} y el lado mide {length}")
    out_yaw = {"front": 0, "back": 180, "right": -90, "left": 90}[side]
    res = []
    for i, kind in enumerate(kinds):
        w = ws[i]
        t = -length / 2 + sum(ws[:i]) + w / 2
        if side == "front":
            local = [t, y0, -D / 2 + thick / 2]
        elif side == "back":
            local = [-t, y0, D / 2 - thick / 2]
        elif side == "right":
            local = [L / 2 - thick / 2, y0, mid - t]
        else:
            local = [-L / 2 + thick / 2, y0, mid + t]
        out = fac.frame(local, out_yaw, (w / 8, sy, 1))
        wall = fac.frame(local, out_yaw + (180 if flip else 0), (w / 8, sy, 1))
        res.append((kind, wall, out))
    return res


def walls(fac, side, kinds, y0, kit="wood", sy=1, flip=False, ends=(0.6, 0.6), tag="", widths=None):
    """Las piezas de una fila de paredes. La variante "Gap" deja el módulo vacío (ahí va otra pieza del mapa:
    la pared de la celda de la cárcel)."""
    model, thick, nodes = KITS[kit]
    parts, mods = [], wall_side(fac, side, kinds, y0, sy, thick, flip, ends, widths)
    for i, (kind, wall, _) in enumerate(mods):
        if kind == "Gap":
            continue
        prefix, x = nodes[kind]
        parts += group(model, prefix, wall, (x, 0, 0), tag=f"{tag}{side}{i + 1}_")
    return parts, mods


def ff_text(fac, x, y0, height, width, text, tag="FFText"):
    """El texto en la banda lisa de la falsa fachada del medio (banda de 6 x 1,6, y 1,2-2,8 del módulo)."""
    sy = height / 4
    f = fac.frame([x, y0, -fac.D / 2], 0, (width / 8, sy, 1))
    p = block(tag, f, [0, 2.0, -0.07], [5.4, 1.2, 0.02], [255, 255, 255])
    p["transparency"] = 1
    p["sign"] = {"faces": ["Front"], "text": text}
    return [p]


def openings(mods, window="Sash", door="Plank", tag="", dark=True):
    """Puertas y ventanas del kit en los huecos de las paredes, con el fondo oscuro detrás (`dark`: sin él en
    un edificio en el que se entra, el saloon)."""
    parts = []
    for i, (kind, _, out) in enumerate(mods):
        t = f"{tag}{i + 1}_"
        if kind == "Window":
            parts += group(WINDOW, f"Window_{window}_", out.sub([0, 3, 0]), (WINDOW_X[window], 0, 0), tag=t)
            if dark:
                parts.append(block(f"{t}Dark", out, [0, 5, 0.5], [3.2, 4.2, 0.1], DARK))
        elif kind == "DoubleWindow":
            for dx in (-1.8, 1.8):
                parts += group(WINDOW, f"Window_{window}_", out.sub([dx, 3, 0], scale=(0.8, 1, 1)),
                               (WINDOW_X[window], 0, 0), tag=f"{t}{'L' if dx < 0 else 'R'}_")
            if dark:
                parts.append(block(f"{t}Dark", out, [0, 5, 0.5], [6.2, 4.2, 0.1], DARK))
        elif kind == "Door":
            parts += group(DOOR, "Door_Frame_", out, (20, 0, 0), tag=t)
            if door == "Open":  # el hueco con su marco: las hojas van en otra pieza (puertas dobles que se mueven)
                continue
            if door == "Saloon":
                parts += group(DOOR, "Door_Saloon_", out, (14, 0, 0), tag=t)
                parts.append(block(f"{t}Dark", out, [0, 3.75, 0.5], [4.2, 7.6, 0.1], DARK))
            else:
                hinge = {"Plank": 0, "Panel": 6}[door]
                parts += group(DOOR, f"Door_{door}_", out.sub([-1.92, 0, 0]), (hinge, 0, 0), tag=t)
                if door == "Panel":
                    parts.append(block(f"{t}Dark", out, [0, 5.15, 0.5], [3, 3.6, 0.1], DARK))
    return parts


def corner_trims(fac, height, y0, corners=("FR", "BR", "BL", "FL"), tag="Corner"):
    """Esquineros en las esquinas de la caja (F/B: frente/fondo, R/L: derecha/izquierda de la fachada)."""
    parts = []
    L, D = fac.L, fac.D
    at = {"FR": (L / 2, -D / 2, 0), "BR": (L / 2, D / 2, -90), "BL": (-L / 2, D / 2, 180), "FL": (-L / 2, -D / 2, 90)}
    for c in corners:
        x, z, y_ = at[c]
        parts.append(piece("WST_Kit_Trim", "fixed_Trim_Corner", fac.frame([x, y0, z], y_, (1, height / 10, 1)),
                           (0, 0, 0), name=f"{tag}{c}"))
    return parts


def flat_roof(fac, y_top, thick=0.6, sy=1, model="WST_Kit_Roof", prefix="Roof_Flat_frag", tag="Roof"):
    """Losas de 8 x 8 (Roof_Flat; o el piso de tablas del interior) sobre todo el adentro de las paredes, con la
    cara de arriba en y_top y `sy` veces el espesor del kit (0,4)."""
    parts = []
    lx, lz = fac.L - 2 * thick, fac.D - 2 * thick
    nx, wx = modules(lx)
    nz, wz = modules(lz)
    x0 = 4 if prefix == "fixed_Floor_Planks" else 0  # en la fila del kit, el piso está centrado en x = 4
    for i in range(nx):
        for j in range(nz):
            f = fac.frame([-lx / 2 + (i + 0.5) * wx, y_top - 0.4 * sy, -lz / 2 + (j + 0.5) * wz], 0,
                          (wx / 8, sy, wz / 8))
            parts += group(model, prefix, f, (x0, 0, 0), tag=f"{tag}{i + 1}{j + 1}_")
    return parts


def sign_band(fac, x, y0, text, width=6, height=1.6, tag="SignBand"):
    """Cartel chato contra la fachada (Sign_Band, 6 x 1,6 en el kit), con el texto en una tapa invisible."""
    f = fac.frame([x, y0, -fac.D / 2], 0, (width / 6, height / 1.6, 1))
    parts = group("WST_Kit_Sign", "Sign_Band_", f, (0, 0, 0), tag=f"{tag}_")
    text_part = block(f"{tag}_Text", f, [0, 0.8, -0.215], [5.4, 1.2, 0.02], [255, 255, 255])
    text_part["transparency"] = 1
    text_part["sign"] = {"faces": ["Front"], "text": text}
    return parts + [text_part]


def sign_hanging(fac, x, y_arm, text, tag="SignHanging"):
    """Cartel colgado de una ménsula, perpendicular a la fachada: se lee desde la vereda, de los dos lados."""
    f = fac.frame([x, y_arm, -fac.D / 2], 0)
    parts = group("WST_Kit_Sign", "Sign_Hanging_", f, (6, 2, 0), tag=f"{tag}_")
    text_part = block(f"{tag}_Text", f, [0, -0.85, -1.77], [0.2, 0.95, 2.7], [255, 255, 255])
    text_part["transparency"] = 1
    text_part["sign"] = {"faces": ["Left", "Right"], "text": text}
    return parts + [text_part]


def porch_floor(fac, n, n_door=None, tag="Porch"):
    """Porch_Floor estirado al largo del frente (n módulos, como la pared), con los escalones delante de la
    puerta. El kit tiene la pared en z = 0 y el porche hacia -z: acá la pared es el borde de atrás de la caja."""
    parts = []
    w = fac.L / n
    for i in range(n):
        x = -fac.L / 2 + (i + 0.5) * w
        f = fac.frame([x, -fac.H / 2, fac.D / 2], 0, (w / 8, fac.H, fac.D / 6.1))
        parts += group(PORCH, "Porch_Floor_", f, (0, 0, 0), tag=f"{tag}{i + 1}_")
        if i == n_door:
            parts += group(PORCH, "Porch_Step_", fac.frame([x, -fac.H / 2, fac.D / 2]), (0, 0, 0), tag=f"{tag}{i + 1}_")
    return parts


def porch_roof(fac, n, tag="PorchRoof"):
    """Porch_Roof aplastado a la caja del techo del porche (rompible: no se sale)."""
    parts = []
    w = fac.L / n
    for i in range(n):
        f = fac.frame([-fac.L / 2 + (i + 0.5) * w, -fac.H / 2, 0], 0, (w / 8, fac.H / 1.7308, fac.D / 6.5))
        parts += group(PORCH, "Porch_Roof_", f, (0, 8.2692, -3.25), tag=f"{tag}{i + 1}_")
    return parts


def porch_column(fac, tag="Column"):
    """Porch_Column estirada al alto de su caja; la ménsula se angosta para no salirse (rompible)."""
    f = fac.frame([0, -fac.H / 2, 0], 0, (1, fac.H / 7.2693, 1))
    parts = []
    for k in sorted(k for k in rig(PORCH) if k.startswith("Porch_Column_")):
        squash = (0.5, 1, 1) if k.endswith("frag03") else (1, 1, 1)
        parts.append(piece(PORCH, k, f, (3, 1.0, -5.725), name=f"{tag}_{k}", squash=squash))
    return parts


def bounds(parts):
    """Caja (min, max) de todas las piezas, con su rotación."""
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    for p in parts:
        c, r = p["cframe"][:3], [p["cframe"][3:6], p["cframe"][6:9], p["cframe"][9:12]]
        half = [sum(abs(r[i][k]) * p["size"][k] / 2 for k in range(3)) for i in range(3)]
        for i in range(3):
            lo[i], hi[i] = min(lo[i], c[i] - half[i]), max(hi[i], c[i] + half[i])
    return lo, hi


def build(name, parts, out, box=None, strict=False, single=False, **extra):
    """Escribe el layout (en _town/, con la misma ruta que el rbxm), revisa la caja y arma el rbxm con
    prop_build.luau. `extra` va al layout para la captura de Blender ("at": dónde está en el mapa, "front").
    Sin piezas sale un Model con Root solo: el mapa esconde esa pieza porque otra la dibuja (el tanque de agua)."""
    lo, hi = bounds(parts) if parts else ([0, 0, 0], [0, 0, 0])
    out_of_box = []
    if box:
        for i, axis in enumerate("xyz"):
            if lo[i] < -box[i] / 2 - TOL or hi[i] > box[i] / 2 + TOL:
                out_of_box.append(f"{axis}: {lo[i]:.2f}..{hi[i]:.2f} (caja ±{box[i] / 2:g})")
    if strict and out_of_box:
        raise SystemExit(f"{name} es rompible y se sale de su caja: " + ", ".join(out_of_box))
    layout_path = LAYOUTS / Path(out).with_suffix(".layout.json")
    layout_path.parent.mkdir(parents=True, exist_ok=True)
    layout = {"name": name, "single": single, "box": box, **extra, "parts": parts}
    layout_path.write_text(json.dumps(layout, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    out_path = RBX / out
    res = subprocess.run(["lune", "run", "tools/roblox/prop_build.luau", str(layout_path), out_path.as_posix()],
                         cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise SystemExit(f"prop_build falló con {name}:\n{res.stdout}{res.stderr}")
    size = [round(hi[i] - lo[i], 2) for i in range(3)]
    note = f" | fuera de la caja: {', '.join(out_of_box)}" if out_of_box else ""
    print(f"{name}: {len(parts)} piezas, mide {size[0]} x {size[1]} x {size[2]}{note} -> {out_path.relative_to(REPO)}")


# ---- props: Props/<Tipo>.rbxm --------------------------------------------------------
#
# Parados, con el origen en el centro de la caja de su pieza del mapa y orientados como esa pieza con yaw 0: el
# juego les aplica solo el yaw de la pieza. La base queda al ras del piso de la caja.

def fit(model_id, prefix, box, mode="uniform", turn=0, skip=None):
    """Las piezas del kit que empiezan con `prefix` (y no con `skip`), escaladas a la caja `box` (x, y, z del
    mapa). mode: "uniform" (escala pareja, la menor de los tres ejes), "xz" (pareja en planta y el alto a la
    caja), "stretch" (cada eje a la caja), "plan" (pareja por la planta; el alto puede pasarse).
    `turn`: 90 para girar el objeto del kit (lo largo en x pasa a z)."""
    nodes = [n for k, n in rig(model_id).items()
             if k.startswith(prefix) and not k.startswith("_") and not (skip and k.startswith(skip))]
    if not nodes:
        raise SystemExit(f"{model_id}: ninguna pieza empieza con {prefix}")
    lo = [min(n["cframe"][i] - n["size"][i] / 2 for n in nodes) for i in range(3)]
    hi = [max(n["cframe"][i] + n["size"][i] / 2 for n in nodes) for i in range(3)]
    ext = [hi[i] - lo[i] for i in range(3)]
    kbox = [box[2], box[1], box[0]] if turn in (90, -90) else list(box)  # la caja en ejes del kit
    k = [kbox[i] / ext[i] for i in range(3)]
    if mode == "none":
        s = [1, 1, 1]
    elif mode == "uniform":
        s = [min(k)] * 3
    elif mode == "xz":
        s = [min(k[0], k[2]), k[1], min(k[0], k[2])]
    elif mode == "plan":
        s = [min(k[0], k[2])] * 3
    else:
        s = k
    anchor = ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)
    f = Frame([0, -box[1] / 2, 0], yaw(turn), s)
    return [piece(model_id, n["name"], f, anchor) for n in sorted(nodes, key=lambda n: n["name"])]


def rot_x(deg):
    """Rotación alrededor de X (de +Y hacia +Z)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def centered(parts):
    """Corre las piezas para que el origen quede en el centro de su caja; devuelve (piezas, caja)."""
    lo, hi = bounds(parts)
    shifted(parts, [-(lo[i] + hi[i]) / 2 for i in range(3)])
    return parts, [round(hi[i] - lo[i], 3) for i in range(3)]


def barricade_store():
    """Barricada del almacenero contra la puerta (que mira a -x): dos cajones abajo y dos bolsas acostadas
    arriba, a lo ancho de la puerta (z). Ya orientada como va (el mapa no la gira)."""
    p = []
    for k, z in enumerate((-1.3, 1.3)):
        p += group("WST_Prop_Crate", "frag", Frame([0, 0, z], yaw(4 if k else -3), (2.0 / 3, 2.4 / 3, 2.6 / 3)),
                   (0, 0, 0), tag=f"Crate{k + 1}_")
    for k, z in enumerate((-1.25, 1.2)):
        p += group("WST_Prop_Sacks", "Sack_Lying_", Frame([0.05 * (k - 0.5), 2.4, z], yaw(90 + 6 * k), (1.2,) * 3),
                   (2.61, 0, 0), tag=f"Sack{k + 1}_")
    return centered(p)


def barricade_ammo():
    """Barricada del armero: dos baúles de munición con esquineros de hierro, uno arriba del otro, a lo ancho
    de la puerta (z)."""
    p = []
    for k, (y, turn) in enumerate(((0, 90), (2.2, 86))):
        p += group("WST_Prop_AmmoCrateRailway", "", Frame([0, y, 0], yaw(turn)), (0, 0, 0), tag=f"Ammo{k + 1}_")
    return centered(p)


def barricade_boards(w, h):
    """Tablones clavados en una ventana (la pared mira a ±x: el tablero queda en el plano YZ): dos travesaños y
    una cruz, en tres capas para que no se pisen. w, h: lo que tapa."""
    plank = rig(DOOR)["Door_Plank_frag02"]
    c = plank["cframe"][:3]
    p = []

    def board(name, x, y, z, length, deg):
        s = (0.45 / plank["size"][0], length / plank["size"][1], 0.15 / plank["size"][2])
        p.append(piece(DOOR, "Door_Plank_frag02", Frame([x, y, z], mul(rot_x(deg), yaw(90)), s), c, name=name))

    for k, y in enumerate((h / 2 - 0.5, -h / 2 + 0.5)):
        board(f"Board{k + 1}", 0.0, y, 0, w, 90 + (2 if k else -1.5))
    diag = math.hypot(w - 0.3, h - 1.0)
    ang = math.degrees(math.atan2(w - 0.3, h - 1.0))
    board("Cross1", 0.15, 0, 0, diag, ang)
    board("Cross2", 0.3, 0, 0, diag, -ang)
    return centered(p)


BARRICADES = {
    "BarricadeStore": barricade_store,                              # almacenero
    "BarricadeAmmo": barricade_ammo,                                # armero
    "BarricadeBoards": lambda: barricade_boards(2.6, 4.4),          # barman, ventana doble (hueco 2,1 x 4)
    "BarricadeBoardsWide": lambda: barricade_boards(3.1, 4.4),      # barman, ventana simple (hueco 2,6 x 4)
}


def counter(box):
    """Mostrador del almacén y la armería, con la barra del saloon: las dos puntas y los dos tramos de al lado
    (frag01, 02, 05 y 06; sin la grieta del medio), juntos y escalados a la caja. Los clientes de -x: la cara
    de adelante del kit (-z) va hacia -x, y lo largo, en z. Tapa a 2,5, donde el almacenero apoya las manos."""
    zc, run = 1.8038, 2 * 5.3333  # centro del fondo de la barra en el kit; largo de los cuatro tramos
    f = Frame([0, -box[1] / 2, 0], yaw(90), [box[2] / run, box[1] / 4, box[0] / 2.3924])
    parts = [piece(SALOON, f"BarCounter_frag0{k}", f, (-2.6667, 0, zc)) for k in (1, 2)]
    parts += [piece(SALOON, f"BarCounter_frag0{k}", f, (2.6667, 0, zc)) for k in (5, 6)]
    return parts


# Silla del telegrafista: la del saloon, a las medidas de su Telegraphist_Tap (marco del HRP, piso en y = 0):
# asiento con la tapa a 1,12, de z -0,45 a +0,55 y x ±0,6; respaldo con la cara de adelante en z = +0,56.
CHAIR_SEAT, CHAIR_BACK, CHAIR_W, CHAIR_DEPTH = 1.12, 0.56, 1.2, 1.0


def shifted(parts, d):
    for p in parts:
        p["cframe"][:3] = [round(p["cframe"][i] + d[i], 4) for i in range(3)]
    return parts


# Mesa del telegrafista (WST_DG_TelegraphDesk, tapa a 2,6): a 0,7885 de alto la tapa queda en 2,05 y la
# perilla de la llave en 2,21, donde la golpea Telegraphist_Tap. Perilla del clip, en el marco del HRP (piso
# en y = 0, -Z adelante): (0,36; 2,21; -1,42).
DESK_SY, KNOB = 2.05 / 2.6, (0.36, -1.42)


def telegraph_desk():
    """Mesa y silla juntas, en el lugar que pide el clip: la mesa girada 180° (su lado del operador, -z del
    kit, mira al telegrafista), corrida para que la perilla caiga donde golpea. Sin WallCoil (va en una pared).
    El origen queda en el centro de la caja de las dos; imprime dónde va el HRP."""
    k = rig("WST_DG_TelegraphDesk")
    key = k["Key"]
    knob = (key["cframe"][0], key["cframe"][2] - key["size"][2] / 2)   # la punta de la palanca, hacia el operador
    t = (KNOB[0] + knob[0], 0, KNOB[1] + knob[1])                        # girada 180°: (x, z) -> (-x, -z)
    f = Frame(t, yaw(180), (1, DESK_SY, 1))
    parts = [piece("WST_DG_TelegraphDesk", n, f) for n in ("Body", "Key", "Lamp_Glow")]
    chair, h_chair, hrp_z = telegraph_chair(report=False)
    parts += shifted(chair, (0, h_chair / 2, -hrp_z))                   # la silla en el marco del HRP
    lo, hi = bounds(parts)
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    d = (-c[0], -(lo[1] + hi[1]) / 2, -c[2])
    shifted(parts, d)
    print(f"TelegraphDesk: caja {hi[0] - lo[0]:.2f} x {hi[1] - lo[1]:.2f} x {hi[2] - lo[2]:.2f}; el HRP del "
          f"telegrafista en ({d[0]:.3f}, piso, {d[2]:.3f}) del centro de la caja, mirando a -z")
    return parts


def telegraph_chair(report=True):
    """La silla queda con el origen en el centro de su caja. El HRP del telegrafista va en
    (0, piso, z_respaldo - CHAIR_BACK), mirando a -z."""
    k = rig(SALOON)
    seat, back = k["Chair_frag01"], k["Chair_frag02"]
    seat_top = seat["cframe"][1] + seat["size"][1] / 2
    back_front = back["cframe"][2] - back["size"][2] / 2   # la cara de adelante del respaldo (-z)
    seat_front = seat["cframe"][2] - seat["size"][2] / 2
    s = [CHAIR_W / seat["size"][0], CHAIR_SEAT / seat_top, CHAIR_DEPTH / (back_front - seat_front)]
    nodes = [k[f"Chair_frag0{i}"] for i in (1, 2, 3)]
    lo = [min(n["cframe"][i] - n["size"][i] / 2 for n in nodes) for i in range(3)]
    hi = [max(n["cframe"][i] + n["size"][i] / 2 for n in nodes) for i in range(3)]
    h = (hi[1] - lo[1]) * s[1]
    anchor = ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)
    f = Frame([0, -h / 2, 0], IDENT, s)
    parts = [piece(SALOON, n["name"], f, anchor) for n in nodes]
    hrp_z = (back_front - anchor[2]) * s[2] - CHAIR_BACK
    if report:
        print(f"TelegraphChair: caja {(hi[0] - lo[0]) * s[0]:.2f} x {h:.2f} x {(hi[2] - lo[2]) * s[2]:.2f}; "
              f"el HRP del telegrafista en (0, piso, {hrp_z:.3f}) del centro de la caja, mirando a -z")
        return parts
    return parts, h, hrp_z


# Lo que se rompe: el color y el material dominantes, para los pedazos (van al color/material de la pieza
# en el JSON del mapa).
DEBRIS = {
    "Column": ("7E5A3A", "WoodPlanks", "poste wood_mid"),
    "Roof": ("4E3524", "WoodPlanks", "tejuelas wood_dark"),
    "Barrel": ("7E5A3A", "WoodPlanks", "duelas wood_mid con aros de hierro"),
    "BarrelExplosive": ("D2301F", "WoodPlanks", "pintura warning_red"),
    "Crate": ("A7804F", "WoodPlanks", "tablas wood_light"),
    "Wall": ("8C8273", "Slate", "piedra stone_grey (JailWall)"),
    "Glass": ("9FC7C9", "Glass", "vidrio (SaloonGlass*)"),
    "Door": ("7E5A3A", "WoodPlanks", "puertas vaivén wood_mid (SaloonDoors)"),
}


def props(want):
    out = {
        "Barrel": (fit("WST_Prop_Barrel", "frag", [2.5, 3.5, 2.5], "xz"), [2.5, 3.5, 2.5], True),
        "BarrelExplosive": (fit("WST_Prop_BarrelExplosive", "frag", [2.5, 3.5, 2.5], "xz"), [2.5, 3.5, 2.5], True),
        "Crate": (fit("WST_Prop_Crate", "frag", [3, 3, 3], "stretch"), [3, 3, 3], True),
        "CrateLow": (fit("WST_Prop_Crate", "frag", [3, 2, 3], "stretch"), [3, 2, 3], True),
        # fardos: la pila de dos hileras, al tamaño de cada caja del mapa
        "HayBale": (fit("WST_Prop_HayBale", "HayBale_Stack_", [4, 3, 4], "stretch"), [4, 3, 4], False),
        "HayBaleLow": (fit("WST_Prop_HayBale", "HayBale_Stack_", [4, 2.5, 4.5], "stretch"), [4, 2.5, 4.5], False),
        "HayBaleWide": (fit("WST_Prop_HayBale", "HayBale_Stack_", [5, 3, 4], "stretch"), [5, 3, 4], False),
        # cactus: saguaro de dos brazos (6 y 7 de alto) y el seco para los de 5
        "Cactus": (fit("WST_Prop_Cactus", "Saguaro_B", [2, 6, 2]), [2, 6, 2], False),
        "CactusTall": (fit("WST_Prop_Cactus", "Saguaro_B", [2, 7, 2]), [2, 7, 2], False),
        "CactusDead": (fit("WST_Prop_Cactus", "Saguaro_Dead", [2, 5, 2]), [2, 5, 2], False),
        # lápidas: cuatro formas para alternar en las seis del cementerio
        "TombstoneRound": (fit("WST_HC_Tombstones", "Tombstone_Round_", [2, 3, 0.6]), [2, 3, 0.6], False),
        "TombstoneCross": (fit("WST_HC_Tombstones", "Tombstone_Cross_", [2, 3, 0.6]), [2, 3, 0.6], False),
        "TombstoneSquare": (fit("WST_HC_Tombstones", "Tombstone_Square_", [2, 3, 0.6]), [2, 3, 0.6], False),
        "TombstoneWood": (fit("WST_HC_Tombstones", "WoodCross_A_", [2, 3, 0.6]), [2, 3, 0.6], False),
        # bebedero: lo largo del kit (x) pasa a z, como la caja del mapa
        "WaterTrough": (fit("WST_Prop_WaterTrough", "", [3, 2.5, 8], turn=90, skip="WaterTrough_Pump_"),
                        [3, 2.5, 8], False),
        "Wagon": (fit("WST_Vehicle_Wagon", "", [6, 5, 12]), [6, 5, 12], False),
        # la carreta rota está volcada (7 de alto en el kit): escala por la planta, sale 1 arriba de la caja
        "WagonWreck": (fit("WST_Prop_Wagon_Wreck", "", [6, 3, 10], "plan"), [6, 3, 10], False),
        "Counter": (counter([2, 2.5, 6]), [2, 2.5, 6], False),
        "Woodpile": (fit("WST_Prop_Woodpile", "Pile", [4, 2, 6]), [4, 2, 6], False),
        # la letrina mide 3,5 de paredes: va sin escalar y el alero (0,3) sale de la caja
        "Outhouse": (fit("WST_Prop_Outhouse", "", [3.5, 8, 3.5], "none"), [3.5, 8, 3.5], False),
        "TelegraphDesk": (telegraph_desk(), None, False),
    }
    # barricadas de los NPCs (las cajas salen de las piezas: el mapa las pone contra cada puerta o ventana)
    for name, make in BARRICADES.items():
        parts, box = make()
        out[name] = (parts, box, True)
    for name, (parts, box, strict) in out.items():
        if want and name not in want:
            continue
        build(name, parts, f"Props/{name}.rbxm", box=box, strict=strict, front=[0, 0, -1])


# ---- loot -------------------------------------------------------------------------

def loot():
    coin = piece("WST_Pickup_SilverDollar", "Coin", Frame(), name="Coin", material="Metal")
    build("Coin", [coin], "Loot/Coin.rbxm", single=True)


# ---- Dusty Gulch ------------------------------------------------------------------

TOWN = "DustyGulch"


def shop(m, bid, facing, front, back, sides, door="Plank", window="Sash", name=None, hanging=None,
         kits=("wood", "wood", "wood"), flip=False, top_name=None, widths=None, box=None, dark=True):
    """Un local de una planta con pretil: el Almacén, la Armería, la Cárcel. Devuelve {id: (piezas, fachada,
    rompible)} con el edificio, su porche, el techo del porche y las columnas.
    - kits: de qué es la pared del frente, del fondo y de los costados ("wood", "brick", "stone").
    - El techo y el pretil van al ras de la caja: los buitres se paran arriba (Perch) y no tienen que flotar.
      Por eso la falsa fachada no sube más que el resto: el frente se distingue por la cornisa y el cartel.
    - El techo del porche (y 11-11,6) tapa la falsa fachada desde la calle: el nombre va también en un cartel
      sobre la puerta y en uno colgado, perpendicular a la fachada, que se lee desde la vereda."""
    box = box or m[bid]["size"]
    fac = Facade(box, facing)
    y0, h_top = -fac.H / 2, fac.H - 10
    k_front, k_back, k_side = kits
    t_front, t_back = KITS[k_front][1], KITS[k_back][1]
    parts = []
    for side, kit, kinds in (("front", k_front, front), ("back", k_back, back), ("left", k_side, sides),
                             ("right", k_side, sides)):
        wood_flip = flip and kit == "wood"
        ws = widths if side == "front" else None
        p, mods = walls(fac, side, kinds, y0, kit, flip=wood_flip, ends=(t_front, t_back), widths=ws)
        parts += p + openings(mods, window=window, door=door, tag=side.capitalize(), dark=dark)
        if side == "front" and kit == "wood":  # falsa fachada pintada, aunque la pared sea de madera cruda
            parts += walls(fac, side, ["Flat"] * len(kinds), y0 + 10, "ff", sy=h_top / 4, tag="FF_", widths=ws)[0]
            if name and h_top >= 3:  # en un pretil de 2 la banda queda de 0,8: sin texto
                parts += ff_text(fac, 0, y0 + 10, h_top, fac.L / len(kinds), name)
        else:
            parts += walls(fac, side, ["Plain"] * len(kinds), y0 + 10, kit, sy=h_top / 10, flip=wood_flip,
                           ends=(t_front, t_back), tag="Top_", widths=ws)[0]
    if k_front != "wood" and (top_name or name):
        parts += sign_band(fac, 0, y0 + 10 + (h_top - 1.6) / 2, top_name or name, width=8, tag="SignTop")
    parts += flat_roof(fac, fac.H / 2, thick=max(t_front, t_back))
    parts += corner_trims(fac, fac.H, y0)
    doors = [i for i, k in enumerate(front) if k == "Door"]
    i_door = min(doors, key=lambda i: abs(i - (len(front) - 1) / 2))  # la puerta del medio
    ws = widths or [fac.L / len(front)] * len(front)
    x_door = -fac.L / 2 + sum(ws[:i_door]) + ws[i_door] / 2
    if name:
        parts += sign_band(fac, x_door, y0 + 8.4, name)
    if hanging:
        parts += sign_hanging(fac, fac.L / 2 - 3, y0 + 9.7, hanging)
    out = {bid: (parts, fac, False)}
    if f"Porch{bid}" in m:
        out.update(porch_set(m, bid, facing, len(front), i_door))
    return out


def porch_set(m, bid, facing, n, i_door):
    """El porche de un edificio: piso (con escalones frente a la puerta), techo y columnas, n módulos."""
    out = {}
    porch = m[f"Porch{bid}"]
    pf = Facade(porch["size"], facing)
    out[f"Porch{bid}"] = (porch_floor(pf, n, i_door), pf, False)
    roof = m[f"PorchRoof{bid}"]
    rf = Facade(roof["size"], facing)
    out[f"PorchRoof{bid}"] = (porch_roof(rf, n), rf, True)
    for k, v in m.items():
        if k.startswith(f"Column{bid}"):
            cf = Facade(v["size"], facing)
            out[k] = (porch_column(cf), cf, True)
    return out


SALOON = "WST_DG_SaloonInterior"


def saloon_wall(m, pid, facing, floors, top, corners=(), windows=("Sash", "Shutters"), ff=None):
    """Una pared del saloon (cada una es su pieza del mapa, de 1 de espesor y 22 de alto): dos plantas de 10
    y un pretil de 2 (falsa fachada `ff` adelante, pared lisa al fondo y los costados). Sin fondo oscuro en
    las ventanas: al saloon se entra. Abajo guillotina: los postigos de la ventana de al lado de la entrada
    se meterían en el hueco."""
    fac = Facade(m[pid]["size"], facing)
    y0 = -fac.H / 2
    parts = []
    for k, kinds in enumerate(floors):
        p, mods = walls(fac, "front", kinds, y0 + 10 * k, tag=f"F{k + 1}_")
        parts += p + openings(mods, window=windows[k], tag=f"F{k + 1}_", dark=False)
    y_top = y0 + 10 * len(floors)
    n = len(floors[0])
    if ff:
        parts += walls(fac, "front", [ff] * n, y_top, "ff", sy=top / 4, tag="FF_")[0]
    else:
        parts += walls(fac, "front", ["Plain"] * n, y_top, sy=top / 10, tag="Top_")[0]
    parts += corner_trims(fac, fac.H, y0, corners)
    return fac, parts


def saloon(m):
    """El saloon: se entra por el hueco del frente (8 x 11) y adentro están la barra, la contrabarra y la araña.
    Todo en madera pintada; el nombre grande arriba de la entrada, sobre el techo del porche."""
    out = {}
    fac, p = saloon_wall(m, "SaloonFrontN", "+x", [["DoubleWindow", "Window"], ["Window", "Window"]], 2,
                         corners=("FR",), ff="Flat")
    out["SaloonFrontN"] = (p, fac, False)
    fac, p = saloon_wall(m, "SaloonFrontS", "+x", [["Window", "DoubleWindow"], ["Window", "Window"]], 2,
                         corners=("FL",), ff="Flat")
    out["SaloonFrontS"] = (p, fac, False)
    fac, p = saloon_wall(m, "SaloonSideN", "+z", [["Plain", "Window", "Plain"], ["Window", "Plain", "Window"]], 2)
    out["SaloonSideN"] = (p, fac, False)
    fac, p = saloon_wall(m, "SaloonSideS", "-z", [["Plain", "Window", "Plain"], ["Window", "Plain", "Window"]], 2)
    out["SaloonSideS"] = (p, fac, False)
    fac, p = saloon_wall(m, "SaloonBack", "-x", [["Plain"] * 4, ["Window", "Plain", "Plain", "Window"]], 2,
                         corners=("FR", "FL"))
    # contrabarra contra la pared de atrás, mirando adentro (+z de la pared), sobre el piso (y 1,2 del mapa)
    floor_y = m["SaloonFloor"]["pos"][1] + m["SaloonFloor"]["size"][1] / 2 - m["SaloonBack"]["pos"][1]
    p += group(SALOON, "BackBar_", fac.frame([0, floor_y, 0.1], 180), (0, 0, 6.3), tag="")
    out["SaloonBack"] = (p, fac, False)

    # arriba de la entrada: pared lisa de 9, pretil con arco y el cartel grande; el marco de la entrada baja
    # hasta el piso (fuera de su caja: es solo de vista)
    top = m["SaloonFrontTop"]
    fac = Facade(top["size"], "+x")
    y0 = -fac.H / 2
    p = walls(fac, "front", ["Plain"], y0, sy=0.9, tag="")[0]
    p += walls(fac, "front", ["Arched"], y0 + 9, "ff", sy=0.5, tag="FF_")[0]
    p += sign_band(fac, 0, -1.4, "SALOON", width=7.4, height=2.4, tag="SignBig")
    floor_top = m["SaloonFloor"]["pos"][1] + m["SaloonFloor"]["size"][1] / 2
    entrance = (top["pos"][1] - top["size"][1] / 2) - floor_top  # del piso al dintel: 10
    p += group(DOOR, "Door_Frame_", fac.frame([0, floor_top - top["pos"][1], -fac.D / 2 + 0.3], 0,
                                              (2, entrance / 7.5, 1)), (20, 0, 0), tag="Entrance_")
    out["SaloonFrontTop"] = (p, fac, False)

    roof = m["SaloonRoof"]
    fac = Facade(roof["size"], "+x")
    p = flat_roof(fac, fac.H / 2, thick=0, sy=fac.H / 0.4)
    p += group(SALOON, "Chandelier", fac.frame([0, -fac.H / 2, 0]), (-4, 10.1, -4), tag="")
    p += group(SALOON, "Lamp_Glow_", fac.frame([0, -fac.H / 2, 0]), (-4, 10.1, -4), tag="")
    out["SaloonRoof"] = (p, fac, False)

    floor = m["SaloonFloor"]
    fac = Facade(floor["size"], "+x")
    out["SaloonFloor"] = (flat_roof(fac, fac.H / 2, thick=0, sy=fac.H / 0.4, model="WST_Kit_Interior",
                                    prefix="fixed_Floor_Planks", tag="Floor"), fac, False)

    bar = m["SaloonBar"]
    fac = Facade(bar["size"], "+x")
    out["SaloonBar"] = (group(SALOON, "BarCounter_", fac.frame([0, -fac.H / 2, 0], 0, (fac.L / 16, fac.H / 4, fac.D / 2.3924)),
                              (0, 0, 1.8038), tag=""), fac, False)
    out.update(porch_set(m, "Saloon", "+x", 5, 2))
    saloon_breakables(m, out)
    return out


def take(out, pid, pick, new_id, piece_attrs, m):
    """Saca de la pieza `pid` las partes que elige `pick` y las pasa a una pieza nueva del mapa, con la caja
    justa de esas partes (+0,02): rompible, el modelo no se sale. Propone la pieza y devuelve su id."""
    parts, fac, strict = out[pid]
    mine = [p for p in parts if pick(p)]
    if not mine:
        raise SystemExit(f"{pid}: no hay partes para {new_id}")
    out[pid] = ([p for p in parts if not pick(p)], fac, strict)
    lo, hi = bounds(mine)
    lo, hi = [v - 0.02 for v in lo], [v + 0.02 for v in hi]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    shifted(mine, [-v for v in c])
    base = m[pid]["pos"]
    propose(m, {"id": new_id, "size": [round(hi[i] - lo[i], 3) for i in range(3)],
                "pos": [round(base[i] + c[i], 3) for i in range(3)], **piece_attrs})
    out[new_id] = (mine, Facade(m[new_id]["size"], "+x"), True)
    return new_id


# (la vida sale del Kind en el juego: sin atributo Health, como quedó en el mapa)
GLASS = {"roles": ["cover"], "decor": True, "tags": ["Destructible"], "attrs": {"Kind": "Glass"},
         "material": "Glass", "color": [159, 199, 201]}
SWING = {"roles": ["cover"], "decor": True, "solid": False, "tags": ["Destructible"], "attrs": {"Kind": "Door"},
         "material": "WoodPlanks", "color": [126, 90, 58]}


def saloon_breakables(m, out):
    """Para la defensa de la oleada 4: los vidrios de cada ventana del frente (Kind "Glass", 1 de vida) y las
    puertas vaivén de la entrada (Kind "Door", 20 de vida), cada uno en su pieza. Los marcos quedan en la
    pared. Las paredes del frente siguen macizas detrás del vidrio: si los vidrios tienen que abrir paso, hay
    que partir SaloonFrontN/S alrededor de los huecos."""
    for wid, tag in (("SaloonFrontN", "N"), ("SaloonFrontS", "S")):
        keys = sorted({p["name"].split("Window_")[0] for p in out[wid][0] if "_Pane_" in p["name"]})
        for i, key in enumerate(keys):
            take(out, wid, lambda p, k=key: "_Pane_" in p["name"] and p["name"].startswith(k),
                 f"SaloonGlass{tag}{i + 1}", GLASS, m)
    # puertas vaivén: las del kit (1,99 x 3,5 cada hoja) estiradas al hueco de 8, 2 sobre el piso
    top = m["SaloonFrontTop"]
    fac = Facade(top["size"], "+x")
    floor_top = m["SaloonFloor"]["pos"][1] + m["SaloonFloor"]["size"][1] / 2
    entrance_w = top["size"][2]
    f = fac.frame([0, floor_top - top["pos"][1], -fac.D / 2 + 0.3], 0, (entrance_w / 4, 1, 1))
    doors = group(DOOR, "Door_Saloon_", f, (14, 0, 0), tag="Swing_")
    out["SaloonFrontTop"] = (out["SaloonFrontTop"][0] + doors, fac, False)
    take(out, "SaloonFrontTop", lambda p: p["name"].startswith("Swing_"), "SaloonDoors", SWING, m)


# ---- piezas nuevas que propongo para el JSON del mapa ---------------------------------
#
# La sesión del juego es dueña del mapa: las cajas nuevas se le pasan escritas (`_town/DustyGulch.proposed.json`)
# y ella las mete. Hasta que estén, town.py arma con las de acá; cuando estén, usa las del mapa.

PROPOSED = {}
MARKS = {}  # dónde van NPCs, mostradores y barricadas (para la sesión del juego)


def propose(m, piece):
    """Agrega (o reemplaza, con "replaces") una pieza propuesta al mapa en memoria, si el mapa no la tiene."""
    PROPOSED[piece["id"]] = piece
    if piece["id"] not in m or piece.get("_force"):
        m[piece["id"]] = piece


def _box(lo, hi):
    return {"size": [round(hi[i] - lo[i], 4) for i in range(3)],
            "pos": [round((lo[i] + hi[i]) / 2, 4) for i in range(3)]}


def jail(m):
    """La cárcel con la celda del Sheriff (sale rompiendo la pared, Fase 1). La caja de hoy (x -44..-20) se
    parte para dejar la celda libre en el centro del frente:
    - Jail: la cárcel maciza, de x -44 a -27 (lleva el modelo de todo el edificio, con el hueco de la celda).
    - JailFrontS / JailFrontN: los dos tramos del frente a los costados de la celda (macizos, sin modelo).
    - JailFrontTop: arriba de la celda, hasta el techo (maciza, sin modelo).
    - JailCell: la celda (6 de fondo, 8 de ancho, 10 de alto), sin colisión: reja hacia la oficina, catre,
      balde, piso de piedra, techo de tablas, paredes de piedra a los costados.
    - JailWall: la pared de la celda que da a la calle, de piedra con la ventanita de rejas (1 x 10 x 8,
      Kind "Wall", 150 de vida), justo del tamaño de su caja.
    El frente queda de 9 + 8 + 9: la puerta de la oficina pasa al tramo sur."""
    full = m["Jail"] if "JailWall" not in m else None
    if full is None:  # el mapa ya está partido: la caja entera es la unión de las piezas
        ids = ("Jail", "JailFrontS", "JailFrontN", "JailFrontTop", "JailCell", "JailWall")
        lo = [min(m[i]["pos"][k] - m[i]["size"][k] / 2 for i in ids) for k in range(3)]
        hi = [max(m[i]["pos"][k] + m[i]["size"][k] / 2 for i in ids) for k in range(3)]
        full = {"id": "Jail", **_box(lo, hi)}
    lo = [full["pos"][k] - full["size"][k] / 2 for k in range(3)]
    hi = [full["pos"][k] + full["size"][k] / 2 for k in range(3)]
    front = hi[0]                       # la cárcel mira a +x
    zc = (lo[2] + hi[2]) / 2
    cell_lo, cell_hi = (front - 7, lo[1], zc - 4), (front, lo[1] + 10, zc + 4)
    base = {k: v for k, v in m["Jail"].items() if k not in ("size", "pos")}
    stone = {"material": "Slate", "color": [140, 130, 115]}
    propose(m, {**base, "id": "Jail", **_box(lo, (front - 7, hi[1], hi[2])), "_force": "JailWall" not in m})
    propose(m, {"id": "JailFrontS", **_box((front - 7, lo[1], lo[2]), (front, hi[1], cell_lo[2])),
                "roles": ["building"], "decor": True, "material": "Brick", "color": [140, 120, 100]})
    propose(m, {"id": "JailFrontN", **_box((front - 7, lo[1], cell_hi[2]), (front, hi[1], hi[2])),
                "roles": ["building"], "decor": True, "material": "Brick", "color": [140, 120, 100]})
    propose(m, {"id": "JailFrontTop", **_box((front - 7, cell_hi[1], cell_lo[2]), (front, hi[1], cell_hi[2])),
                "roles": ["building"], "decor": True, "material": "Brick", "color": [140, 120, 100]})
    propose(m, {"id": "JailCell", **_box(cell_lo, (front - 1, cell_hi[1], cell_hi[2])),
                "roles": ["decor"], "decor": True, "solid": False, "material": "Slate", "color": [90, 84, 76],
                "label": "Celda del Sheriff"})
    propose(m, {"id": "JailWall", **_box((front - 1, cell_lo[1], cell_lo[2]), cell_hi),
                "roles": ["building"], "decor": True, "tags": ["Destructible"], "attrs": {"Kind": "Wall"}, **stone,
                "label": "Pared de la celda"})

    # el edificio entero, armado en la caja de siempre y corrido al centro de la pieza Jail nueva
    out = shop(m, "Jail", "+x", ["Door", "Gap", "Window"], ["Barred", "Plain", "Barred"],
               ["Plain", "Barred", "Plain"], door="Plank", window="Sash", name="SHERIFF", hanging="JAIL",
               kits=("brick", "stone", "stone"), widths=[9, 8, 9], box=full["size"])
    parts, fac, _ = out["Jail"]
    shifted(parts, [full["pos"][k] - m["Jail"]["pos"][k] for k in range(3)])
    out["Jail"] = (parts, Facade(m["Jail"]["size"], "+x"), False)
    for pid in ("JailFrontS", "JailFrontN", "JailFrontTop"):
        out[pid] = ([], Facade(m[pid]["size"], "+x"), False)

    # la pared de la celda: el módulo de piedra con rejas, del tamaño exacto de su caja (rompible)
    wf = Facade(m["JailWall"]["size"], "+x")
    out["JailWall"] = (walls(wf, "front", ["Barred"], -wf.H / 2, "stone", tag="")[0], wf, True)

    # adentro de la celda (marco del mapa, centro de la caja JailCell): x -3 reja .. +3 pared de la calle
    c = m["JailCell"]
    hx, hy, hz = [s / 2 for s in c["size"]]
    fr = Frame([0, 0, 0])
    p = [block("Floor", fr, [0, -hy + 0.05, 0], [2 * hx, 0.1, 2 * hz], [110, 104, 96], "Slate"),
         block("Ceiling", fr, [0, hy - 0.1, 0], [2 * hx, 0.2, 2 * hz], [78, 53, 36], "WoodPlanks"),
         block("Dark", fr, [-hx - 0.9, 0, 0], [0.1, 2 * hy, 2 * hz], DARK)]          # el pasillo oscuro tras la reja
    bars = Frame([-hx, -hy, 0], yaw(90))       # la reja mira a la oficina (-x); su -z del kit va a -x
    p += [piece("WST_DG_JailInterior", n, bars) for n in ("CellFront", "CellDoor")]
    p.append(block("Lintel", fr, [-hx + 0.1, hy - 0.5, 0], [0.4, 1.0, 2 * hz], [140, 130, 115], "Slate"))
    for side in (-1, 1):  # paredes de piedra a los costados, mirando adentro
        sf = Frame([0, -hy, side * (hz - 0.25)], yaw(0 if side > 0 else 180), (2 * hx / 8, 1, 0.5))
        p += group("WST_Kit_WallStone", "Wall_Stone_frag", sf, (0, 0, 0), tag=f"Side{'N' if side > 0 else 'S'}_")
    # catre colgado de la pared norte, a lo largo de la celda; balde en la esquina de la reja, al sur
    p.append(piece("WST_DG_JailInterior", "Bunk", Frame([0.1, -hy, hz - 0.5], IDENT, (0.9, 1, 1)), (-0.5, 0, 6)))
    p.append(piece("WST_DG_JailInterior", "Bucket", Frame([-hx + 0.9, -hy + 0.1, -hz + 1.0]), (3.0, 0, 5.0)))
    out["JailCell"] = (p, Facade(c["size"], "+x"), False)
    return out


# ---- locales en los que se entra: Almacén y Armería (pedido de Valentin, 2026-10-30) -------------------
#
# "todos los npcs deberían estar adentro, y cuando empiezan las oleadas una animación de ellos tapando la puerta
# con algo, según el npc y sus recursos accesibles"; "las puertas deberían ser reactivas a los personajes".

DOOR_HOLE_H = 7.0   # el hueco de Wall_Door (las piezas de arriba arrancan en y = 7 del módulo)
CEILING = 10.0      # el techo de adentro, sobre la base de la pared (10,2 del mapa): arriba queda el pretil
WALL_T = 1.0        # espesor de las cajas de pared (como el saloon; la pared del kit es de 0,6, al ras de afuera)
LEAF = {"Panel": (6, ["Door_Panel_frag01", "Door_Panel_frag02", "Door_Panel_frag03", "Door_Panel_frag04",
                      "Door_Panel_Glass"]),
        "Plank": (0, ["Door_Plank_frag01", "Door_Plank_frag02", "Door_Plank_frag03", "Door_Plank_frag04"])}
LAMP = ["Chain", "fixed_Hook", "frag01", "frag02", "frag03", "Lamp_Glow"]   # el farol colgante (no el de pared)


def fbox(fac, center, lo, hi):
    """Caja en coordenadas de la fachada (lo, hi) -> {"size", "pos"} del mapa; `center`: el de la caja entera."""
    pts = [apply(fac.R, [x, y, z]) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return _box([min(p[i] for p in pts) + center[i] for i in range(3)],
                [max(p[i] for p in pts) + center[i] for i in range(3)])


def nodes_of(model_id, names, frame, anchor, tag=""):
    return [piece(model_id, n, frame, anchor, name=f"{tag}{n}") for n in names]


def store_furniture(fac, yf, yc):
    """Almacén: dos estanterías de mercadería al fondo, el mueble de sombreros, revólveres y chalecos en el
    costado sur, la caja fuerte en la esquina, bolsas, barril y cajón al costado norte, dos faroles."""
    L, D = fac.L, fac.D
    back = D / 2 - 0.6                                   # la cara de adentro de la pared del fondo (kit de 0,6)
    p = []
    for k, x in enumerate((-6, 6)):
        p += group("WST_DG_StoreShelves", "Shelves_General_", fac.frame([x, yf, back - 0.75]), (-10, 0, 0),
                   tag=f"Shelf{k + 1}_")
    p += group("WST_Prop_GunRack", "", fac.frame([L / 2 - 0.6 - 0.62, yf, 2.0], 90), (0, 0, 0), tag="Rack_")
    p += group("WST_Prop_Safe", "", fac.frame([L / 2 - 2.0, yf, back - 1.6], 90), (0, 0, 0), tag="Safe_")
    p += group("WST_Prop_Sacks", "Sack_Pile_", fac.frame([-L / 2 + 2.0, yf, -6.5]), (7.04, 0, 0), tag="Sacks_")
    p += group("WST_Prop_Sacks", "Sack_Upright_", fac.frame([-L / 2 + 1.6, yf, -3.5]), (0, 0, 0), tag="Sack_")
    p += group("WST_Prop_Barrel", "frag", fac.frame([-L / 2 + 1.8, yf, 3.0]), (0, 0, 0), tag="Barrel_")
    p += group("WST_Prop_Crate", "frag", fac.frame([-L / 2 + 2.2, yf, 7.0], 15), (0, 0, 0), tag="Crate_")
    for k, z in enumerate((-4.0, 4.0)):
        p += nodes_of("WST_Prop_OilLamp", LAMP, fac.frame([0, yc, z]), (0, 3.88, 0), tag=f"Lamp{k + 1}_")
    return p


def armory_furniture(fac, yf, yc):
    """Armería: el tablero de armas largas y revólveres en el fondo, baúles de munición al costado sur, cajones
    de dinamita apilados y un barril al norte, un farol."""
    L, D = fac.L, fac.D
    back = D / 2 - 0.6
    p = group("WST_DG_StoreShelves", "GunDisplay_Wall", fac.frame([0, yf, back - 0.75]), (10, 0, 0), tag="")
    p += group("WST_DG_StoreShelves", "Gun_", fac.frame([0, yf, back - 0.75]), (10, 0, 0), tag="Display_")
    for k, z in enumerate((3.0, 7.5)):
        p += group("WST_Prop_AmmoCrateRailway", "", fac.frame([L / 2 - 0.6 - 1.2, yf, z], 90), (0, 0, 0),
                   tag=f"Ammo{k + 1}_")
    for k, (y, turn) in enumerate(((0, 0), (1.4, 12))):
        p += group("WST_Prop_DynamiteCrate", "frag", fac.frame([-L / 2 + 2.0, yf + y, 7.5], turn), (0, 0, 0),
                   tag=f"Dynamite{k + 1}_")
    p += group("WST_Prop_Barrel", "frag", fac.frame([-L / 2 + 1.8, yf, 3.0]), (0, 0, 0), tag="Barrel_")
    p += nodes_of("WST_Prop_OilLamp", LAMP, fac.frame([0, yc, 2.0]), (0, 3.88, 0), tag="Lamp_")
    return p


def enterable(m, bid, facing, front, back, sides, door, window, name, hanging, flip, furnish, barricade):
    """Un local en el que se entra. El edificio de siempre con el hueco de la puerta abierto (solo el marco);
    adentro piso de tablas a 1,2, techo a 10,2 y los muebles de `furnish`. La caja maciza se parte como la de la
    cárcel: frente en tres alrededor del hueco (FrontN, FrontS, FrontTop), fondo, costados, piso y el bloque de
    arriba (la pieza `bid`, que lleva el modelo de todo el edificio; las demás, un Model vacío). Las puertas
    dobles van en `<bid>Doors`, sin colisión: hojas Swing_DoorLeft / Swing_DoorRight (la parte del lado de la
    bisagra; el resto de la hoja va soldado a ella). Devuelve también dónde va el NPC, el mostrador y la
    barricada (`barricade`: (prop, fondo, alto, ancho))."""
    split = [bid + s for s in ("Back", "SideN", "SideS", "FrontN", "FrontS", "FrontTop", "Floor")]
    if split[0] in m:
        ids = [bid] + split
        full = {"id": bid, **_box([min(m[i]["pos"][k] - m[i]["size"][k] / 2 for i in ids) for k in range(3)],
                                  [max(m[i]["pos"][k] + m[i]["size"][k] / 2 for i in ids) for k in range(3)])}
    else:
        full = dict(m[bid])
    size, center = full["size"], full["pos"]
    original = {k: v for k, v in m[bid].items() if k not in ("size", "pos", "id")}
    out = shop(m, bid, facing, front, back, sides, door="Open", window=window, name=name, hanging=hanging,
               flip=flip, box=size, dark=False)
    parts = out[bid][0]
    fac = Facade(size, facing)
    L, H, D = fac.L, fac.H, fac.D
    y0, yt, t = -H / 2, H / 2, WALL_T
    yf, yc = y0 + 1.0, y0 + CEILING
    parts += flat_roof(fac, yf, thick=t, sy=2.5, model="WST_Kit_Interior", prefix="fixed_Floor_Planks", tag="Floor")
    parts.append(block("Ceiling", fac.frame([0, 0, 0]), [0, yc + 0.1, 0], [L - 2 * t, 0.2, D - 2 * t],
                       [126, 90, 58], "WoodPlanks"))
    parts += furnish(fac, yf, yc)

    # el hueco de la puerta: 4 del kit en el módulo de la puerta, estirado como el módulo
    n = len(front)
    w = L / n
    xc = -L / 2 + (front.index("Door") + 0.5) * w
    hw = 2 * w / 8
    dz = -D / 2 + 0.3                                    # el plano del medio de la pared del frente (kit de 0,6)
    hinge, leaf_nodes = LEAF[door]
    s = ((hw - 0.03) / 3.84, (DOOR_HOLE_H - 1.0) / 7.38, 1)
    leaves = []
    for side, x, turn in (("Left", xc - hw + 0.015, 0), ("Right", xc + hw - 0.015, 180)):
        f = fac.frame([x, yf, dz], turn, s)
        main = f"Swing_Door{side}"
        for k, nd in enumerate(leaf_nodes):
            pc = piece(DOOR, nd, f, (hinge, 0, 0), name=main if k == 0 else f"{main}_{nd.split('_')[-1]}")
            if k:
                pc["weldTo"] = main
            leaves.append(pc)

    def label(lo, hi, base):
        """N o S según de qué lado del centro del edificio cae en el mapa."""
        b = fbox(fac, center, lo, hi)
        return b, base + ("S" if b["pos"][2] < center[2] else "N")

    wall = {"roles": ["building"], "decor": True, "material": original.get("material", "WoodPlanks"),
            "color": original.get("color", [170, 130, 90])}
    pieces = {}
    b = fbox(fac, center, (-L / 2 + t, yc, -D / 2 + t), (L / 2 - t, yt, D / 2 - t))
    pieces[bid] = {**original, **b, "id": bid}
    pieces[bid + "Back"] = {**wall, **fbox(fac, center, (-L / 2, y0, D / 2 - t), (L / 2, yt, D / 2))}
    for lo, hi, base in (((-L / 2, y0, -D / 2 + t), (-L / 2 + t, yt, D / 2 - t), "Side"),
                         ((L / 2 - t, y0, -D / 2 + t), (L / 2, yt, D / 2 - t), "Side"),
                         ((-L / 2, y0, -D / 2), (xc - hw, yt, -D / 2 + t), "Front"),
                         ((xc + hw, y0, -D / 2), (L / 2, yt, -D / 2 + t), "Front")):
        bx, nm = label(lo, hi, base)
        pieces[bid + nm] = {**wall, **bx}
    pieces[bid + "FrontTop"] = {**wall, **fbox(fac, center, (xc - hw, y0 + DOOR_HOLE_H, -D / 2),
                                               (xc + hw, yt, -D / 2 + t))}
    pieces[bid + "Floor"] = {"roles": ["arena_floor"], "material": "WoodPlanks", "color": [139, 94, 60],
                             **fbox(fac, center, (-L / 2 + t, y0, -D / 2 + t), (L / 2 - t, yf, D / 2 - t))}
    pieces[bid + "Doors"] = {"roles": ["decor"], "decor": True, "solid": False, "material": "WoodPlanks",
                             "color": [126, 90, 58], "label": f"Puertas ({original.get('label', bid)})",
                             **fbox(fac, center, (xc - hw, yf, -D / 2), (xc + hw, y0 + DOOR_HOLE_H, -D / 2 + t))}
    for pid, pc in pieces.items():
        propose(m, {"id": pid, **pc, "_force": split[0] not in m})

    # el edificio entero va en la pieza de arriba; las puertas, en la suya; el resto vacío
    shifted(parts, [center[k] - m[bid]["pos"][k] for k in range(3)])
    out[bid] = (parts, Facade(m[bid]["size"], facing), False)
    shifted(leaves, [center[k] - m[bid + "Doors"]["pos"][k] for k in range(3)])
    out[bid + "Doors"] = (leaves, Facade(m[bid + "Doors"]["size"], facing), False)
    for pid in split:
        if pid != bid + "Floor":
            out[pid] = ([], Facade(m[pid]["size"], facing), False)
    out[bid + "Floor"] = ([], Facade(m[bid + "Floor"]["size"], facing), False)   # las tablas van en el modelo

    # marcas para el juego: mostrador y NPC en el medio del salón frente a la puerta; barricada contra la puerta
    zc = 1.0
    counter = fbox(fac, center, (xc - 3, yf, zc - 1), (xc + 3, yf + 2.5, zc + 1))
    spot = fbox(fac, center, (xc - 1, yf, zc + 1.75 - 1), (xc + 1, yf + 1, zc + 1.75 + 1))
    prop = barricade                      # su caja es la del prop (armado ya orientado: fondo en x, ancho en z)
    depth, height, width = BARRICADES[prop]()[1]
    bar = fbox(fac, center, (xc - width / 2, yf, -D / 2 + t), (xc + width / 2, yf + height, -D / 2 + t + depth))
    marks = {"counter": {**counter, "model": "Counter"}, "npc": {**spot, "yaw": fac.yaw},
             "barricade": {**bar, "model": prop}}
    return out, marks


BAR_H = 3.0  # la barra del saloon: arriba de la cintura del barman (2,94), que se le vean pecho, brazos y vaso


def dusty_gulch(m):
    town = {}
    # La barra del JSON medía 4 y le tapaba al barman hasta el cuello. La sesión del juego baja la caja a
    # BAR_H con la base en el piso del saloon; acá se arma con esa caja aunque el JSON todavía no cambió.
    bar, floor = m["SaloonBar"], m["SaloonFloor"]
    floor_top = floor["pos"][1] + floor["size"][1] / 2
    m["SaloonBar"] = {**bar, "size": [bar["size"][0], BAR_H, bar["size"][2]],
                      "pos": [bar["pos"][0], round(floor_top + BAR_H / 2, 4), bar["pos"][2]]}
    # Almacén: madera pintada crema, vidrieras dobles y la puerta de almacén con vidrio. Se entra.
    built, marks = enterable(m, "Store", "-x", ["DoubleWindow", "Door", "DoubleWindow"], ["Plain", "Window", "Plain"],
                             ["Plain", "Window", "Plain"], "Panel", "Sash", "GENERAL STORE", "STORE", False,
                             store_furniture, "BarricadeStore")
    town.update(built)
    MARKS["Storekeeper"] = marks
    # Armería: madera cruda (las paredes dadas vuelta), postigos y puerta de tablas; falsa fachada pintada.
    built, marks = enterable(m, "Armory", "-x", ["Window", "Door", "Window"], ["Plain", "Plain", "Plain"],
                             ["Plain", "Window", "Plain"], "Plank", "Shutters", "GUNSMITH", "GUNS", True,
                             armory_furniture, "BarricadeAmmo")
    town.update(built)
    MARKS["Gunsmith"] = marks
    # Cárcel: la oficina del sheriff adelante en ladrillo; las celdas atrás y a los costados en piedra con rejas.
    town.update(jail(m))
    town.update(saloon(m))
    # el barman entablona por dentro cada ventana de abajo del frente del saloon (la vaivén queda abierta)
    boards = []
    for gid in sorted(k for k in m if k.startswith("SaloonGlass")):
        g = m[gid]
        if g["pos"][1] > 10:          # las de arriba no
            continue
        wide = g["size"][2] > 2.0
        prop = "BarricadeBoardsWide" if wide else "BarricadeBoards"
        size = BARRICADES[prop]()[1]
        inner = m["SaloonFrontN"]["pos"][0] - m["SaloonFrontN"]["size"][0] / 2      # cara de adentro (x)
        boards.append({"window": gid, "model": prop, "size": size,
                       "pos": [round(inner - size[0] / 2, 3), g["pos"][1], g["pos"][2]]})
    MARKS["Bartender"] = {"barricades": boards}

    # Casas: sin carteles; se alternan pintadas y crudas, ventanas de guillotina o con postigos. La E4, al sur,
    # abandonada (vidrios rotos). Pretil de 2 (de 4 en la W3, que es más alta).
    plain3, win3 = ["Plain", "Window", "Plain"], ["Window", "Door", "Window"]
    for bid, facing, front, window, flip in (
            ("HouseW1", "+x", win3, "Shutters", False),
            ("HouseW2", "+x", ["DoubleWindow", "Door", "Window"], "Sash", True),
            ("HouseW3", "+x", win3, "Sash", False),
            ("HouseE1", "-x", ["Window", "Door", "DoubleWindow"], "Sash", True),
            ("HouseE2", "-x", win3, "Shutters", False),
            ("HouseE3", "-x", win3, "Shutters", True),
            ("HouseE4", "-x", win3, "Broken", True)):
        town.update(shop(m, bid, facing, front, plain3, plain3, window=window, flip=flip))

    # Estación (sin porche en el mapa: el andén es aparte): ladrillo, como la cárcel pero entera.
    town.update(shop(m, "Station", "+x", ["Window", "Door", "Window"], plain3, plain3,
                     door="Panel", name="STATION", hanging="TELEGRAPH", kits=("brick", "brick", "brick"),
                     top_name="DUSTY GULCH"))
    # Establo: madera cruda, tres portones de tablas mirando al pueblo (-z).
    town.update(shop(m, "Stable", "-z", ["Window", "Door", "Door", "Door", "Window"], ["Plain"] * 5,
                     ["Plain", "Window"], name="LIVERY STABLE", flip=True))

    # Andén: tablas del porche en dos hileras de 6 de fondo, a lo largo de las vías (x).
    plat = m["Platform"]
    fac = Facade(plat["size"], "-z")
    n, w = modules(fac.L)
    p = []
    for row in range(2):
        for i in range(n):
            f = fac.frame([-fac.L / 2 + (i + 0.5) * w, -fac.H / 2, fac.D / 2 - row * fac.D / 2], 0,
                          (w / 8, fac.H, fac.D / 2 / 6.1))
            p += group(PORCH, "Porch_Floor_", f, (0, 0, 0), tag=f"Row{row + 1}_{i + 1}_")
    town["Platform"] = (p, fac, False)

    # Cercas: estacas en el cementerio (corren a lo largo de z), baranda en el corral (a lo largo de x).
    for fid, facing, kit, kind, h in (("CemeteryFenceW", "-x", "picket", "Picket", 3.3),
                                      ("CemeteryFenceE", "-x", "picket", "Picket", 3.3),
                                      ("CorralFenceW", "-z", "railing", "Railing", 3.0),
                                      ("CorralFenceE", "-z", "railing", "Railing", 3.0)):
        fac = Facade(m[fid]["size"], facing)
        n, _ = modules(fac.L)
        town[fid] = (walls(fac, "front", [kind] * n, -fac.H / 2, kit, sy=fac.H / h, tag="")[0], fac, False)

    # Tanque de agua: el modelo es una sola malla (patas y tanque), así que va entero en la pieza de la base,
    # escalado al alto de base + tanque; la del tanque lleva un modelo vacío para que el mapa la esconda.
    base, tank = m["WaterTowerBase"], m["WaterTowerTank"]
    total = (tank["pos"][1] + tank["size"][1] / 2) - (base["pos"][1] - base["size"][1] / 2)
    nodes = list(rig("WST_DG_WaterTower").values())
    lo_y = min(n["cframe"][1] - n["size"][1] / 2 for n in nodes)
    hi_y = max(n["cframe"][1] + n["size"][1] / 2 for n in nodes)
    s = total / (hi_y - lo_y)
    fac = Facade(base["size"], "-z")
    town["WaterTowerBase"] = (group("WST_DG_WaterTower", "", Frame([0, -base["size"][1] / 2, 0], IDENT, [s] * 3),
                                    (0, lo_y, 0.0442), tag=""), fac, False)
    town["WaterTowerTank"] = ([], Facade(tank["size"], "-z"), False)
    town.update(railbed(m))
    town.update(street(m))
    return town


STREET_TEX = ("WST_Tex_StreetDirt", "StreetDirt")  # el GLB que sube la imagen (tools/blender/dirt_texture.py)


def street(m):
    """La calle: una Part del tamaño de la caja de Street, visible (el mapa esconde la pieza), con la tierra
    de dirt_texture.py en la cara de arriba: un cuadro cubre los 28 de ancho y se repite cada 28 a lo largo.
    Sin el id de la imagen (falta leerlo en Studio) no se arma."""
    try:
        tex = rig(STREET_TEX[0])[STREET_TEX[1]].get("texture")
    except SystemExit:
        tex = None
    if not tex:
        print("Street: falta el id de la imagen (rig_data.py ids de WST_Tex_StreetDirt); no se arma")
        return {}
    s = m["Street"]
    fac = Facade(s["size"], "-z")
    p = block("Street", Frame(), [0, 0, 0], s["size"], [139, 100, 66], "Mud")
    p["surface"] = {"name": "Dirt", "texture": tex, "face": "Top", "tileU": s["size"][0], "tileV": s["size"][0]}
    return {"Street": ([p], fac, False)}


def railbed(m):
    """La vía de la estación, con cajas lisas y materiales de Roblox (no hace falta subir nada).
    - Balasto de piedra (Pebble) apenas arriba del piso.
    - Durmientes de madera cada 2.
    - Los dos rieles con patín y hongo, al alto de las cajas Rail1/Rail2 del mapa (tope a 0,6).
    Va todo en Rail1; Rail2 lleva un modelo vacío para que el mapa la esconda. El WST_Track_Tile de la
    fábrica no sirve acá: es una malla de 58 x 64 con su propio desierto, y en el pueblo el balasto y los
    durmientes quedarían bajo el piso."""
    r1, r2 = m["Rail1"], m["Rail2"]
    length = r1["size"][0]
    bottom = r1["pos"][1] - r1["size"][1] / 2          # el piso (0,2)
    top = r1["pos"][1] + r1["size"][1] / 2             # tope del riel (0,6)
    dz = r2["pos"][2] - r1["pos"][2]                   # trocha entre centros (5)
    mid = dz / 2                                       # el centro de la vía, en el marco de Rail1
    f = Frame([0, -r1["pos"][1], 0])                   # y del mapa -> marco de Rail1
    iron, wood, gravel = [59, 58, 58], [78, 53, 36], [128, 120, 108]
    parts = [block("Ballast", f, [0, bottom + 0.03, mid], [length, 0.06, dz + 4.0], gravel, "Pebble")]
    n = int(length // 2)
    for i in range(n):
        x = -length / 2 + 1 + i * 2
        parts.append(block(f"Tie{i + 1:02d}", f, [x, bottom + 0.06 + 0.06, mid], [0.7, 0.12, dz + 2.2], wood,
                           "WoodPlanks"))
    for k, z in enumerate((0, dz)):
        parts.append(block(f"Rail{k + 1}_Web", f, [0, (bottom + top) / 2 - 0.04, z], [length, top - bottom - 0.08, 0.16],
                           iron, "Metal"))
        parts.append(block(f"Rail{k + 1}_Head", f, [0, top - 0.06, z], [length, 0.12, 0.3], iron, "Metal"))
        parts.append(block(f"Rail{k + 1}_Foot", f, [0, bottom + 0.15, z], [length, 0.06, 0.4], iron, "Metal"))
    fac = Facade(r1["size"], "-z")
    return {"Rail1": (parts, fac, False), "Rail2": ([], Facade(r2["size"], "-z"), False)}


def load_map(args):
    path = Path(args[args.index("--map") + 1]) if "--map" in args else REPO / "src" / "shared" / "Maps" / f"{TOWN}.json"
    if not path.exists():
        raise SystemExit(f"no está el mapa {path}: pasalo con --map <ruta a {TOWN}.json>")
    return {p["id"]: p for p in json.loads(path.read_text(encoding="utf-8"))["parts"]}


def town(args):
    m = load_map(args)
    want = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] != "--map")]
    models = dusty_gulch(m)
    for bid, (parts, fac, strict) in models.items():
        if want and bid not in want:
            continue
        build(bid, parts, f"Town/{TOWN}/{bid}.rbxm", box=m[bid]["size"], strict=strict, at=m[bid]["pos"],
              front=fac.front)
    if PROPOSED:  # las cajas que el mapa todavía no tiene (o que cambian), para la sesión del juego
        path = LAYOUTS / f"{TOWN}.proposed.json"
        rows = [{k: v for k, v in p.items() if not k.startswith("_")} for p in PROPOSED.values()]
        path.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{len(rows)} piezas propuestas para el mapa -> {path.relative_to(REPO)}")
    if MARKS:
        path = LAYOUTS / f"{TOWN}.marks.json"
        path.write_text(json.dumps(MARKS, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"marcas de NPCs, mostradores y barricadas -> {path.relative_to(REPO)}")


def main():
    a = sys.argv[1:]
    if a[:1] == ["loot"]:
        loot()
    elif a[:1] == ["town"]:
        town(a[1:])
    elif a[:1] == ["props"]:
        props(a[1:])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

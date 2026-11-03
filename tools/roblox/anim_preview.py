"""
Vista previa y chequeos de animaciones R15 de la fábrica, sin Studio.

  py -I tools/roblox/anim_preview.py <rig.json> <Clip.poses.json> [...]

Por cada clip:
- Hace la cinemática directa (FK) a 30 fps con las Pose.CFrame exactas que escribió anim_build.luau,
  interpolando como Roblox: el easing de un tramo es el de la pose donde arranca, la rotación se
  interpola por slerp y una articulación sin Pose en un key se interpola entre los keys que sí la tienen.
- Chequea, con números:
    piso       el punto más bajo de cada cuadro (bajo -0,05 = se mete en el piso; en un clip parado,
               sobre 0,08 = flota). Lo que el spec pone o saca del cuerpo en un marcador ("attach":
               {"Grab": ["Body"]}, "detach": {"Release": ["Body"]}) cuenta solo entre esos marcadores, con
               lo que cuelga de esas piezas.
    pie        en un loop con "Walk" o "Run" en el nombre (en una criatura, también "Trot" y "Gallop"): lo que
               avanza el pie apoyado por segundo,
               que es el walkAnimationSpeed de la ficha para que no patine
    loop       diferencia entre el primer y el último cuadro (grados) si el clip es loop
    golpes     velocidad angular máxima por articulación, a 60 fps (lo que dibuja Roblox) y con la raíz del
               objeto en la mano: sobre 1600 °/s en miembros y objeto o 2400 °/s en el cuerpo se lee como un
               salto de cuadro (umbrales de vendor/skills/hildlabs-openrig-studio)
- Escribe assets/models/western/_animations/<Clip>@<Id>.glb para el visor. Es de ese modelo: las piezas no
  están anidadas, así que el GLB lleva la posición de cada articulación, que cambia con las proporciones.
  Para ver un clip en otro cuerpo, se corre de nuevo con su rig.json. Está en el marco del GLB de 03_export
  (girado 180°).

Criatura con esqueleto propio (rig.json "skeleton", ver tools/roblox/rig_build.luau): la FK sigue
"skeleton.tree", con cada articulación en "skeleton.joints" o en el origin de la pieza. Cambia:
    piso       con "air" (en el spec, o en el skeleton para toda la criatura: el buitre) no se marca ni
               SE METE ni FLOTA: solo se informa el punto más bajo
    pie        las piezas de "skeleton.ground" (las patas del toro), por el centro del fondo de su caja
    golpes     todas las articulaciones de la criatura, con el umbral de miembros (1600 °/s)
"""

import json
import math
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "assets" / "models" / "western" / "_animations"
FPS = 30
VEL_FPS = 60                                # lo que dibuja Roblox: un pico más corto que un cuadro no se ve
R15 = {
    "LowerTorso": ("HumanoidRootPart", "Root"), "UpperTorso": ("LowerTorso", "Waist"), "Head": ("UpperTorso", "Neck"),
    "LeftUpperArm": ("UpperTorso", "LeftShoulder"), "LeftLowerArm": ("LeftUpperArm", "LeftElbow"),
    "LeftHand": ("LeftLowerArm", "LeftWrist"), "RightUpperArm": ("UpperTorso", "RightShoulder"),
    "RightLowerArm": ("RightUpperArm", "RightElbow"), "RightHand": ("RightLowerArm", "RightWrist"),
    "LeftUpperLeg": ("LowerTorso", "LeftHip"), "LeftLowerLeg": ("LeftUpperLeg", "LeftKnee"),
    "LeftFoot": ("LeftLowerLeg", "LeftAnkle"), "RightUpperLeg": ("LowerTorso", "RightHip"),
    "RightLowerLeg": ("RightUpperLeg", "RightKnee"), "RightFoot": ("RightLowerLeg", "RightAnkle"),
}
ORDER = ["LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
         "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg",
         "RightLowerLeg", "RightFoot"]
BODY = {"Root", "Waist", "Neck"}


# ---- cuaterniones (w, x, y, z) y transformaciones (q, p) ----------------------------------------

def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz, aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw)


def qrot(q, v):
    w, x, y, z = q
    p = qmul(qmul(q, (0.0, *v)), (w, -x, -y, -z))
    return p[1:]


def qfrom_rows(r):
    (m00, m01, m02), (m10, m11, m12), (m20, m21, m22) = r
    tr = m00 + m11 + m22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = (0.25 * s, (m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s)
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2
        q = ((m21 - m12) / s, 0.25 * s, (m01 + m10) / s, (m02 + m20) / s)
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2
        q = ((m02 - m20) / s, (m01 + m10) / s, 0.25 * s, (m12 + m21) / s)
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2
        q = ((m10 - m01) / s, (m02 + m20) / s, (m12 + m21) / s, 0.25 * s)
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q)


def slerp(a, b, u):
    d = sum(x * y for x, y in zip(a, b))
    if d < 0:
        b, d = tuple(-c for c in b), -d
    if d > 0.9995:
        r = tuple(x + (y - x) * u for x, y in zip(a, b))
    else:
        th = math.acos(d)
        s = math.sin(th)
        r = tuple((math.sin((1 - u) * th) * x + math.sin(u * th) * y) / s for x, y in zip(a, b))
    n = math.sqrt(sum(c * c for c in r))
    return tuple(c / n for c in r)


def compose(a, b):
    """(qa, pa) * (qb, pb)"""
    return qmul(a[0], b[0]), tuple(pa + v for pa, v in zip(a[1], qrot(a[0], b[1])))


def angle(a, b):
    d = abs(sum(x * y for x, y in zip(a, b)))
    return math.degrees(2 * math.acos(min(1.0, d)))


IDENT = ((1.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0))


def ease(style, direction, u):
    if style == "Constant":
        return 0.0
    if style == "Linear":
        return u
    if direction == "In":
        return u ** 3
    if direction == "Out":
        return 1 - (1 - u) ** 3
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


# ---- clip --------------------------------------------------------------------------------------

def tracks(clip):
    """parte -> lista de (t, q, p, style, dir) de los keys donde tiene Pose."""
    out = {}
    for k in clip["keys"]:
        for part, po in k["poses"].items():
            c = po["cf"]
            q = qfrom_rows((c[3:6], c[6:9], c[9:12]))
            out.setdefault(part, []).append((k["t"], q, tuple(c[0:3]), po["style"], po["dir"]))
    return out


def sample(tr, t):
    if not tr:
        return IDENT
    if t <= tr[0][0]:
        return tr[0][1], tr[0][2]
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            u = ease(a[3], a[4], (t - a[0]) / (b[0] - a[0]))
            return slerp(a[1], b[1], u), tuple(x + (y - x) * u for x, y in zip(a[2], b[2]))
    return tr[-1][1], tr[-1][2]


def creature(rig):
    """Esqueleto propio (rig.json "skeleton"): (árbol pieza -> padre, orden de la raíz hacia afuera, articulación de
    cada pieza). None en un R15."""
    sk = rig.get("skeleton")
    if not sk:
        return None
    if "_order" not in sk:
        tree = sk["tree"]
        origin = {n["name"]: n["origin"] for n in rig["nodes"]}

        def depth(p):
            d = 0
            while p in tree:
                p, d = tree[p], d + 1
            return d
        sk["_order"] = sorted(tree, key=lambda p: (depth(p), p))
        sk["_joint"] = {p: tuple(sk.get("joints", {}).get(p, origin[p])) for p in tree}
    return sk["tree"], sk["_order"], sk["_joint"]


def pose_at(rig, trs, t):
    """parte -> transformación de mundo de su articulación (origen del nodo)."""
    origin = {n["name"]: tuple(n["origin"]) for n in rig["nodes"]}
    world = {}
    sk = creature(rig)
    if sk:                                       # criatura: la articulación puede no ser el origen de la pieza
        tree, order, joint = sk
        jw = {}
        for part in order:
            parent = tree[part]
            if parent == "HumanoidRootPart":
                base = (IDENT[0], joint[part])
            else:
                base = compose(jw[parent], (IDENT[0], tuple(a - b for a, b in zip(joint[part], joint[parent]))))
            jw[part] = compose(base, sample(trs.get(part), t))
            world[part] = compose(jw[part], (IDENT[0], tuple(a - b for a, b in zip(origin[part], joint[part]))))
    for part in ORDER if not sk else ():
        parent, _ = R15[part]
        local = sample(trs.get(part), t)
        if parent == "HumanoidRootPart":
            base = (IDENT[0], origin[part])
        else:
            off = tuple(a - b for a, b in zip(origin[part], origin[parent]))
            base = compose(world[parent], (IDENT[0], off))
        world[part] = compose(base, local)
    tree = rig.get("tree", {})                   # objeto en la mano (held.py): la raíz cuelga de RightHand
    def depth(p):
        d = 0
        while p in tree:
            p, d = tree[p], d + 1
        return d
    for part in sorted(tree, key=depth):
        off = tuple(a - b for a, b in zip(origin[part], origin[tree[part]]))
        world[part] = compose(compose(world[tree[part]], (IDENT[0], off)), sample(trs.get(part), t))
    for name, host in hosts(rig).items():        # piezas extra soldadas (ojos, accesorios, overlays, marcadores)
        off = tuple(a - b for a, b in zip(origin[name], origin[host]))
        world[name] = compose(world[host], (IDENT[0], off))
    return world


def hosts(rig):
    """A qué pieza va soldado cada extra: la misma regla que tools/roblox/rig_build.luau."""
    if "_hosts" in rig:
        return rig["_hosts"]
    nodes = {n["name"]: n for n in rig["nodes"]}

    def box_dist(part, at):
        c, s = nodes[part]["cframe"][:3], nodes[part]["size"]
        return math.sqrt(sum(max(abs(a - b) - h / 2, 0) ** 2 for a, b, h in zip(at, c, s)))

    out = {}
    sk = creature(rig)
    if sk:                                       # criatura: la misma regla que buildCreature de rig_build.luau
        tree = sk[0]
        for name, n in nodes.items():
            if name in tree:
                continue
            if name.startswith("_"):
                at = n["cframe"][:3]
                cands = [p for p in nodes if p not in tree and not p.startswith("_") and box_dist(p, at) <= 0.15]
                out[name] = min(cands or [p for p in nodes if not p.startswith("_")], key=lambda p: box_dist(p, at))
            elif n.get("weldTo") in nodes:
                out[name] = n["weldTo"]
            elif rig["skeleton"].get("weldTo", {}).get(name) in nodes:   # skeleton.weldTo, como rig_build
                out[name] = rig["skeleton"]["weldTo"][name]
            else:                                # el centro de su caja, no el origen (el de las vetas está en el piso)
                at = n["cframe"][:3]
                out[name] = min(sk[1], key=lambda p: (round(box_dist(p, at), 6), math.dist(nodes[p]["cframe"][:3], at)))
        rig["_hosts"] = dict(sorted(out.items(), key=lambda kv: kv[0].startswith("_")))
        return rig["_hosts"]
    for name, n in nodes.items():
        if name in R15 or name in rig.get("tree", {}):
            continue
        if name.startswith("_"):                 # marcador: el accesorio que lo contiene (0,15) o lo más cercano
            at = n["cframe"][:3]
            cands = [p for p in nodes if p not in R15 and not p.startswith("_") and box_dist(p, at) <= 0.15]
            out[name] = min(cands or [p for p in nodes if not p.startswith("_") and p != name], key=lambda p: box_dist(p, at))
        elif n.get("weldTo") in nodes:           # a mano en el rig.json (la Viuda de Old Hank va a la cadera)
            out[name] = n["weldTo"]
        elif name in ("Eyes", "Acc_Hat"):
            out[name] = "Head"
        else:
            same = [p for p in R15 if math.dist(nodes[p]["origin"], n["origin"]) < 0.02]
            # empate de distancia (el origen adentro de dos cajas): gana el centro más cercano, como en rig_build
            out[name] = same[0] if same else min(
                R15, key=lambda p: (round(box_dist(p, n["origin"]), 6), math.dist(nodes[p]["cframe"][:3], n["origin"])))
    # un marcador puede ir en un accesorio: se resuelve después de los accesorios
    rig["_hosts"] = dict(sorted(out.items(), key=lambda kv: kv[0].startswith("_")))
    return rig["_hosts"]


def read_spec(spec_path):
    return json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}


def in_air(rig, spec):
    """Un clip en el aire no tiene piso: "air" del spec o, si no lo dice, del skeleton (el buitre vuela siempre)."""
    return spec.get("air", (rig.get("skeleton") or {}).get("air", False))


def present(rig, clip, spec_path):
    """pieza -> (desde, hasta): cuándo es del cuerpo. Sale de "attach" y "detach" del spec ({marcador: [piezas]}),
    con lo que cuelga de esas piezas: el arma que el juego pone en la mano en Grab y suelta en Release, el
    sombrero que cae en HatOff."""
    spec = read_spec(spec_path)
    at = {m["name"]: m["t"] for m in clip.get("markers", [])}
    parent = {**hosts(rig), **rig.get("tree", {}), **(rig.get("skeleton") or {}).get("tree", {})}
    out = {}
    for field, side in (("attach", 0), ("detach", 1)):
        for marker, parts in spec.get(field, {}).items():
            for name in (n["name"] for n in rig["nodes"]):
                p = name
                while p not in parts and p in parent:
                    p = parent[p]
                if p in parts:
                    span = list(out.get(name, (-math.inf, math.inf)))
                    span[side] = at[marker]
                    out[name] = tuple(span)
    return out


def lowest(rig, world, who=False, skip=()):
    low, part = math.inf, None
    for n in rig["nodes"]:
        if n["name"].startswith("_") or n["name"] in skip:   # marcadores y lo ya soltado: no son cuerpo
            continue
        q, p = world[n["name"]]
        c = tuple(a - b for a, b in zip(n["cframe"][:3], n["origin"]))
        h = [s / 2 for s in n["size"]]
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    v = qrot(q, (c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2]))
                    if p[1] + v[1] < low:
                        low, part = p[1] + v[1], n["name"]
    return (low, part) if who else low


def contact_speeds(rig, frames, lows, dt):
    """Criatura: lo que avanza por segundo cada pieza de "skeleton.ground" mientras apoya. Se sigue el centro del
    fondo de su caja (la pezuña), apoyado si queda a menos de 0,06 del punto más bajo del cuadro."""
    nodes = {n["name"]: n for n in rig["nodes"]}
    speeds = []
    for g in rig["skeleton"].get("ground", []):
        n = nodes[g]
        c = (n["cframe"][0] - n["origin"][0], n["cframe"][1] - n["size"][1] / 2 - n["origin"][1],
             n["cframe"][2] - n["origin"][2])
        rest = n["cframe"][1] - n["size"][1] / 2
        for a, b, la, lb in zip(frames, frames[1:], lows, lows[1:]):
            pa = tuple(x + v for x, v in zip(a[g][1], qrot(a[g][0], c)))
            pb = tuple(x + v for x, v in zip(b[g][1], qrot(b[g][0], c)))
            if pa[1] - rest < min(la, lb) + 0.06:
                speeds.append((pa[2] - pb[2]) / dt)
    return speeds


def check(rig, clip, frames, dt, trs, spans, air=False):
    rep = []
    eps = 1e-6
    sk = creature(rig)
    gone = [{p for p, (a, b) in spans.items() if not a - eps <= i * dt < b - eps} for i in range(len(frames))]
    lows = [lowest(rig, w, skip=g) for w, g in zip(frames, gone)]
    stand = not any(s in clip["name"] for s in ("Death", "Fall"))
    worst = lows.index(min(lows))
    high = lows.index(max(lows))
    roots = {p: s for p, s in spans.items() if not p.startswith("_") and spans.get(rig.get("tree", {}).get(p)) != s}
    if roots:                                  # una línea por grupo: la pieza de arriba, no cada hija
        rep.append("cuenta para el piso: " + ", ".join(
            f"{p} " + (f"desde {a:.2f}" if a > -math.inf else "") + (" " if a > -math.inf and b < math.inf else "")
            + (f"hasta {b:.2f}" if b < math.inf else "") for p, (a, b) in roots.items()))
    if air:                                    # vuela: el servidor lo sostiene, no hay piso que pisar ni atravesar
        rep.append(f"piso: no aplica (\"air\") · punto más bajo {min(lows):+.3f}"
                   f" ({lowest(rig, frames[worst], True, gone[worst])[1]}, t={worst * dt:.2f})"
                   f" a {max(lows):+.3f} (t={high * dt:.2f}), con el HumanoidRootPart quieto")
    else:
        rep.append(f"piso: mínimo {min(lows):+.3f} ({lowest(rig, frames[worst], True, gone[worst])[1]}, t={worst * dt:.2f})"
                   f" · máximo del punto más bajo {max(lows):+.3f} (t={high * dt:.2f})"
                   + ("  <- SE METE EN EL PISO" if min(lows) < -0.05 else "")
                   + ("  <- FLOTA" if stand and max(lows) > 0.08 else ""))
    if clip["loop"] and re.search(r"(Walk|Run|Trot|Gallop)$", clip["name"]) and sk:
        speeds = sorted(contact_speeds(rig, frames, lows, dt))
        if speeds:
            med = speeds[len(speeds) // 2]
            rep.append(f"pata apoyada: avanza {med:.2f} studs/s (mediana de {len(speeds)} tramos) -> walkAnimationSpeed ≈ {abs(med):.1f}")
    elif clip["loop"] and re.search(r"(Walk|Run)$", clip["name"]):
        speeds = []
        ankle_h = min(n["origin"][1] for n in rig["nodes"] if n["name"] in ("LeftFoot", "RightFoot"))
        for foot in ("LeftFoot", "RightFoot"):
            for a, b, la, lb in zip(frames, frames[1:], lows, lows[1:]):
                ya = a[foot][1][1]
                if ya - ankle_h < min(la, lb) + 0.06:   # el tobillo, a su altura de reposo: pie apoyado
                    speeds.append((a[foot][1][2] - b[foot][1][2]) / dt)
        if speeds:
            speeds.sort()
            med = speeds[len(speeds) // 2]
            rep.append(f"pie apoyado: avanza {med:.2f} studs/s (mediana de {len(speeds)} tramos) -> walkAnimationSpeed ≈ {abs(med):.1f}")
    if clip["loop"]:
        worst = max(angle(frames[0][p][0], frames[-1][p][0]) for p in (sk[1] if sk else ORDER))
        rep.append(f"loop: el último cuadro difiere {worst:.2f}° del primero" + ("  <- NO CIERRA" if worst > 0.1 else ""))
    grip2 = rig.get("markers", {}).get("_Grip2")
    if grip2:                                   # arma de dos manos: la izquierda tiene que llegar al guardamanos
        nodes = {n["name"]: n for n in rig["nodes"]}
        lh = nodes["LeftHand"]
        hand_local = tuple(lh["cframe"][i] - lh["origin"][i] + (-0.158 if i == 1 else 0) for i in range(3))
        dists = []
        for w in frames:
            hq, hp = w["LeftHand"]
            hand = tuple(a + b for a, b in zip(hp, qrot(hq, hand_local)))
            rq, rp = w[grip2["part"]]
            off = tuple(grip2["pos"][i] - nodes[grip2["part"]]["origin"][i] for i in range(3))
            g2 = tuple(a + b for a, b in zip(rp, qrot(rq, off)))
            dists.append(math.dist(hand, g2))
        rep.append(f"mano izquierda al guardamanos (_Grip2): {min(dists):.2f} a {max(dists):.2f} studs"
                   + ("  <- NO LLEGA (Hold: < 0,25)" if clip["name"].endswith("_Hold") and max(dists) > 0.25 else ""))
    snaps = []
    length = dt * (len(frames) - 1)
    n = max(1, round(length * VEL_FPS))       # a 30 fps no se ven los picos de los tramos cortos con easing
    times = [length * i / n for i in range(n + 1)]
    # el objeto en la mano, por su raíz; los mecanismos (martillo, portón de carga) saltan a propósito
    props = [p for p, parent in rig.get("tree", {}).items() if parent in R15 and not p.startswith("_")]
    for part in (sk[1] if sk else ORDER + props):  # velocidad de cada articulación (rotación local, como openrig)
        joint = R15[part][1] if part in R15 and not sk else part
        local = [sample(trs.get(part), t)[0] for t in times]
        top = max(angle(a, b) for a, b in zip(local, local[1:])) / (length / n)
        if top > (2400 if joint in BODY and not sk else 1600):  # criatura: todo con el umbral de miembros
            snaps.append(f"{joint} {top:.0f}°/s")
    rep.append("golpes: " + (", ".join(snaps) + "  <- SALTO DE CUADRO" if snaps else "ninguno"))
    return rep


# ---- GLB para el visor -------------------------------------------------------------------------

def write_glb(rig, clip, times, frames, path):
    names = [n["name"] for n in rig["nodes"]]
    rest = {n["name"]: n["origin"] for n in rig["nodes"]}
    bin_, views, accs = bytearray(), [], []

    def add(data, comp, count, typ, mn=None, mx=None):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(struct.pack(f"<{len(data)}f", *data))
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(data) * 4})
        acc = {"bufferView": len(views) - 1, "componentType": 5126, "count": count, "type": typ}
        if mn is not None:
            acc["min"], acc["max"] = mn, mx
        accs.append(acc)
        return len(accs) - 1

    t_acc = add(times, None, len(times), "SCALAR", [times[0]], [times[-1]])
    channels, samplers = [], []
    for i, name in enumerate(names):
        pos, rot = [], []
        for w in frames:
            q, p = w[name]
            pos += [-p[0], p[1], -p[2]]                  # marco del GLB de 03_export: girado 180° en Y
            rot += [-q[1], q[2], -q[3], q[0]]            # glTF guarda (x, y, z, w)
        for path_, data, typ in (("translation", pos, "VEC3"), ("rotation", rot, "VEC4")):
            samplers.append({"input": t_acc, "output": add(data, None, len(times), typ), "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1, "target": {"node": i, "path": path_}})
    gltf = {
        "asset": {"version": "2.0", "generator": "tools/roblox/anim_preview.py"},
        "scene": 0, "scenes": [{"nodes": list(range(len(names)))}],
        "nodes": [{"name": n, "translation": [-rest[n][0], rest[n][1], -rest[n][2]]} for n in names],
        "animations": [{"name": clip["name"], "channels": channels, "samplers": samplers,
                        "extras": {"markers": clip.get("markers", []), "loop": clip["loop"], "priority": clip["priority"]}}],
        "buffers": [{"byteLength": len(bin_)}], "bufferViews": views, "accessors": accs,
    }
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    bin_ += b"\0" * (-len(bin_) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(__doc__)
    rig = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in args[1:]:
        clip = json.loads(Path(path).read_text(encoding="utf-8"))
        trs = tracks(clip)
        length = clip["keys"][-1]["t"]
        n = max(1, round(length * FPS))
        times = [length * i / n for i in range(n + 1)]
        frames = [pose_at(rig, trs, t) for t in times]
        print(f"== {clip['name']} ({length:.2f} s, {'loop' if clip['loop'] else 'una vez'}, {clip['priority']})")
        if clip.get("rig") and Path(clip["rig"]).name != Path(args[0]).name:
            print(f"   aviso: las poses son para {clip['rig']}, no para {args[0]}")
        spec_path = Path(path).with_name(Path(path).name.replace(".poses.json", ".json"))
        spans = present(rig, clip, spec_path)
        for line in check(rig, clip, frames, length / n, trs, spans, in_air(rig, read_spec(spec_path))):
            print("   " + line)
        out = OUT_DIR / f"{clip['name']}@{rig['id']}.glb"      # las posiciones de las articulaciones son de ESE esqueleto
        write_glb(rig, clip, times, frames, out)
        print(f"   -> {out.relative_to(REPO)}")
    sys.path.insert(0, str(REPO / "tools" / "viewer"))
    import build_index                               # el visor ve las animaciones nuevas solo
    build_index.build()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

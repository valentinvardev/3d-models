"""
Copiado del agente de animación de enemigos (2026-10-28).
Hoja de contacto sin navegador: dibuja las cajas de cada pieza (rig.json) en N cuadros, de costado y en 3/4,
con sombreado plano. Es la silueta aproximada (cajas, no mallas), para juzgar poses cuando el visor no está.

  py -I tools/roblox/anim_sheet.py <rig.json> <Clip.poses.json> <out.png> [N=8]

Criatura con esqueleto propio (rig.json "skeleton"): tres filas (costado, 3/4 y frente) y la escala se ajusta
a lo que ocupa el clip en todos los cuadros (el toro mide 10 de largo; con la escala del R15 no entra). La línea
del piso no se dibuja si el clip va en el aire ("air").
"""

import json
import math
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/roblox
import anim_preview as ap  # noqa: E402

W, H, S = 170, 230, 30.0  # celda y escala (px por stud)
COL = {"Head": (205, 200, 180), "Eyes": (40, 40, 40), "UpperTorso": (200, 190, 160), "LowerTorso": (90, 105, 130),
       "Acc": (70, 60, 55), "Silver": (130, 220, 240)}


def color(name):
    if name.startswith("Acc_"):
        return COL["Acc"]
    if name.startswith("Silver"):
        return COL["Silver"]
    if name.startswith("Left"):
        return (150, 165, 140) if "Leg" in name or "Foot" in name else (175, 190, 160)
    if name.startswith("Right"):
        return (120, 135, 115) if "Leg" in name or "Foot" in name else (150, 165, 135)
    return COL.get(name, (160, 160, 160))


CREATURE_COL = {"Head": (205, 200, 180), "Torso": (200, 190, 160), "Body": (200, 190, 160),
                "Neck": (175, 160, 130), "Tail": (120, 105, 90)}


def creature_color(name):
    """Criatura: izquierda clara, derecha oscura, y el segmento de afuera (Lower, Outer) más oscuro."""
    if name.startswith("Silver"):
        return COL["Silver"]
    side = (175, 190, 160) if "Left" in name else (135, 150, 125) if "Right" in name else None
    if side:
        return tuple(int(c * 0.8) for c in side) if ("Lower" in name or "Outer" in name) else side
    return CREATURE_COL.get(name, (160, 160, 160))


def faces(rig, world, paint=color):
    out = []
    for n in rig["nodes"]:
        if n["name"].startswith("_"):
            continue
        q, p = world[n["name"]]
        c = tuple(a - b for a, b in zip(n["cframe"][:3], n["origin"]))
        h = [s / 2 for s in n["size"]]
        corner = {}
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    v = ap.qrot(q, (c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2]))
                    corner[(sx, sy, sz)] = tuple(a + b for a, b in zip(p, v))
        for axis in range(3):
            for s in (-1, 1):
                quad = []
                for a in (-1, 1):
                    for b in ((-1, 1) if a == -1 else (1, -1)):
                        k = [0, 0, 0]
                        k[axis] = s
                        k[(axis + 1) % 3] = a
                        k[(axis + 2) % 3] = b
                        quad.append(corner[tuple(k)])
                nrm = [0, 0, 0]
                nrm[axis] = s
                out.append((quad, ap.qrot(q, tuple(nrm)), paint(n["name"])))
    return out


def render(img, ox, oy, rig, world, yaw, fit=None, paint=color):
    """fit = (ancho y alto de la celda, px por stud, centro horizontal, y de abajo de todo); sin fit, la del R15."""
    w, h, s, uc, yb = fit or (W, H, S, 0.0, 0.0)
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    light = (0.5, 0.8, -0.3)
    polys = []
    for quad, nrm, col in faces(rig, world, paint):
        pts, depth = [], 0
        for x, y, z in quad:
            u = -(x * cy + z * sy)   # eje horizontal de la vista (+ = derecha de quien mira)
            d = -x * sy + z * cy     # profundidad (+ = lejos)
            pts.append((ox + w / 2 + (u - uc) * s, oy + h - 18 - (y - yb) * s))
            depth += d
        nd = -nrm[0] * sy + nrm[2] * cy
        if nd > 0.02:              # cara de espaldas a la cámara
            continue
        lit = 0.45 + 0.55 * max(0, nrm[0] * light[0] + nrm[1] * light[1] + nrm[2] * light[2])
        polys.append((depth / 4, pts, tuple(min(255, int(c * lit)) for c in col)))
    polys.sort(key=lambda t: -t[0])
    for _, pts, col in polys:
        fill(img, pts, col)


def fill(img, pts, col):
    ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(img["h"] - 1, int(max(ys))) + 1):
        xs = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            row = img["px"][y]
            for x in range(max(0, int(a)), min(img["w"] - 1, int(b)) + 1):
                row[x] = col


def write_png(img, path):
    raw = b"".join(b"\0" + bytes(c for px in row for c in px) for row in img["px"])

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", img["w"], img["h"], 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


DIGITS = {  # 3x5
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
    "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001001001001",
    "8": "111101111101111", "9": "111101111001111", ".": "000000000000010",
}


def text(img, x, y, s, col=(200, 200, 200)):
    for ch in s:
        g = DIGITS.get(ch)
        if g:
            for i, b in enumerate(g):
                if b == "1":
                    for dx in range(2):
                        for dy in range(2):
                            img["px"][y + (i // 3) * 2 + dy][x + (i % 3) * 2 + dx] = col
        x += 8


def creature_sheet(rig, clip, trs, length, n, out):
    """Hoja de una criatura: escala común a las tres vistas, que entre todo el clip."""
    cw, ch = 230, 190
    views = (90, 35, 0)  # costado (desde su derecha), 3/4 de frente y de frente
    times = [length * i / n if clip["loop"] or n == 1 else length * i / (n - 1) for i in range(n)]
    worlds = [ap.pose_at(rig, trs, t) for t in times]
    span = []
    for yaw in views:
        cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        us, ys = [], []
        for world in worlds:
            for quad, _, _ in faces(rig, world):
                for x, y, z in quad:
                    us.append(-(x * cy + z * sy))
                    ys.append(y)
        yb = min(0.0, min(ys))
        span.append((min((cw - 12) / (max(us) - min(us)), (ch - 30) / (max(ys) - yb)), (min(us) + max(us)) / 2, yb))
    s = min(f[0] for f in span)
    fits = [(cw, ch, s, uc, yb) for _, uc, yb in span]
    spec = ap.read_spec(Path(sys.argv[2]).with_name(Path(sys.argv[2]).name.replace(".poses.json", ".json")))
    air = ap.in_air(rig, spec)
    img = {"w": cw * n, "h": ch * len(views), "px": [[(18, 18, 18)] * (cw * n) for _ in range(ch * len(views))]}
    for r, fit in enumerate(fits):
        y0 = int(r * ch + ch - 18 + fit[4] * s)
        for i in range(n):
            for x in range(i * cw, i * cw + cw):
                if not air:
                    img["px"][y0][x] = (70, 70, 70)
                img["px"][r * ch][x] = (40, 40, 40)  # separación entre filas
    for i, (t, world) in enumerate(zip(times, worlds)):
        for r, yaw in enumerate(views):
            render(img, i * cw, r * ch, rig, world, yaw, fits[r], creature_color)
            text(img, i * cw + 4, r * ch + 4, f"{t:.2f}")
    write_png(img, out)
    print(f"-> {out} ({s:.1f} px por stud)")


def main():
    rig = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    clip = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    trs = ap.tracks(clip)
    length = clip["keys"][-1]["t"]
    if ap.creature(rig):
        return creature_sheet(rig, clip, trs, length, n, sys.argv[3])
    views = (90, 35)  # de costado (mirando desde la derecha del personaje) y 3/4 de frente
    img = {"w": W * n, "h": H * len(views), "px": [[(18, 18, 18)] * (W * n) for _ in range(H * len(views))]}
    for r in range(len(views)):
        for i in range(n):
            y0 = r * H + H - 18
            for x in range(i * W, i * W + W):
                img["px"][y0][x] = (70, 70, 70)
    for i in range(n):
        t = length * i / n if clip["loop"] or n == 1 else length * i / (n - 1)
        world = ap.pose_at(rig, trs, t)
        for r, yaw in enumerate(views):
            render(img, i * W, r * H, rig, world, yaw)
            text(img, i * W + 4, r * H + 4, f"{t:.2f}")
    write_png(img, sys.argv[3])
    print("->", sys.argv[3])


if __name__ == "__main__":
    main()

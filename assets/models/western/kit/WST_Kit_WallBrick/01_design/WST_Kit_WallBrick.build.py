"""
Receta de WST_Kit_WallBrick, las paredes de ladrillo del kit (banco, hotel) (prompt 077, Bloques A + C).

Brief
- Silueta a 40 studs: paño rojo con líneas horizontales oscuras cada 0,5, zócalo de piedra gris abajo,
  dinteles y alféizares de piedra sobre y bajo los huecos: el lado rico de Silver Bend.
- Grilla: 8 de ancho, 10 de alto, 0,8 de espesor (z de -0,4 a 0,4; el zócalo sale a -0,44), origen abajo
  al centro, frente a -Z. Las cuatro variantes en fila sobre X cada 8 (se tocan: calzan).
- Hiladas: zócalo stone_grey de 0,8 con un chaflán de 0,2 arriba (la primera junta cae en y = 1,0), y 18
  hiladas de ladrillo de 0,5 hasta 10: alféizar (3), dintel (7) y puerta (7,5) caen en juntas.
- Ladrillo paint_red; cada hilada tiene abajo un surco de 0,04 de hondo y 0,05 de alto (redrock_dark).
  Juntas verticales pintadas (0,05, redrock_dark) solo cada 3 hiladas, corridas medio ladrillo entre una y
  otra (sin ladrillos sueltos). Adentro, revoque paint_cream.
- Dinteles stone_grey de una hilada sobre cada hueco (0,3 más anchos por lado, 0,03 afuera) y alféizares
  stone_grey bajo las ventanas (salen 0,08).
- Fragmentos: 8 por variante, prisma de hiladas recortado en escalera por las juntas (grieta escalonada),
  caras de corte paint_red; los empalmes del corte se pintan como junta vertical.
- Variantes: Wall_Plain, Wall_Window (3 x 4, alféizar en 3), Wall_Door (4 x 7,5), Wall_DoubleWindow (dos de
  2,4, centros en x = ±1,8, igual que la de tablas). Nombres: Brick_<Variante>_fragNN.
- Inferido: chaflán del zócalo, revoque adentro, dinteles y alféizares (el prompt pide dinteles), cortes.

Vueltas: 1) primera versión: en la doble ventana el corte de la hilada 4 caía justo en la punta de un
alféizar de piedra (caras coplanares en la booleana: 2 bordes con giro invertido) -> corte en x = 0, entre
los dos alféizares. Capturas sin más cambios.

Revisión
- Triángulos contra 600 por pieza: Plain 1292, Window 1852, Door 1302, DoubleWindow 1488. Calidad primero
  pero es caro: 18 surcos reales de 0,04 (los pide el prompt) por 8 fragmentos cerrados con cortes en
  escalera, más juntas verticales pintadas. Con los surcos solo pintados (franja redrock_dark coplanar,
  como pide el Bloque A para tablas) bajaría ~40 %; decide Valentin si el surco real vale el costo.
- Medidas: cada variante 8,000 x 10,000, espesor 0,8 (0,84 con el zócalo, 0,88 donde sale el alféizar),
  apoyada en y = 0; calzan entre sí (mismas hiladas en todas).
- Fragmentos: 8 por variante, el mayor 20,6 %, todos de 0,8 de espesor.
- Normales del GLB final: 6 esquinas desviadas en los dinteles (bug de process_model, ver el informe).
"""

RED, MORTAR, STONE, PLASTER = "paint_red", "redrock_dark", "stone_grey", "paint_cream"
W, ZB, NC = 8.0, 0.4, 19                                 # NC hiladas: 0 = zócalo, 1..18 = ladrillo


def course(c):
    return (0.0, 1.0) if c == 0 else (1.0 + 0.5 * (c - 1), 1.5 + 0.5 * (c - 1))


def front(c):
    y0, y1 = course(c)
    if c == 0:
        return [(-0.44, 0.0), (-0.44, 0.8), (-0.4, 1.0)]
    return [(-0.36, y0), (-0.36, y0 + 0.05), (-0.4, y0 + 0.05), (-0.4, y1)]


def clean(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 1e-9:
                out.pop(i)
                changed = True
                break
    return out


def profile(c0, c1):
    pts = []
    for c in range(c0, c1 + 1):
        pts += front(c)
    return clean(pts + [(ZB, course(c1)[1]), (ZB, course(c0)[0])])


class BrickWall:
    def __init__(self, mk, name, ox, frags, stones=()):
        self.mk, self.name, self.ox, self.frags, self.stones = mk, name, ox, frags, stones
        self.parts = {}
        for fname, iv in frags.items():
            ks = sorted(iv)
            assert ks == list(range(ks[0], ks[-1] + 1)), f"{name} {fname}: hiladas salteadas"
        for c in range(NC):
            spans = sorted(iv[c] for iv in frags.values() if c in iv)
            for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
                assert a1 <= b0 + 1e-6, f"{name} hilada {c}: se pisan {a0, a1} {b0, b1}"

    def neighbour(self, fname, c, x):
        return any(c in iv and (abs(iv[c][0] - x) < 1e-6 or abs(iv[c][1] - x) < 1e-6)
                   for n, iv in self.frags.items() if n != fname)

    def build(self):
        mk, ox = self.mk, self.ox
        for fname, iv in self.frags.items():
            ks = sorted(iv)
            c0, c1 = ks[0], ks[-1]
            xmin, xmax = min(a for a, _ in iv.values()), max(b for _, b in iv.values())
            p = mk.part(f"{self.name}_{fname}", (ox, 0, 0))
            self.parts[fname] = p
            mk.prism(p, profile(c0, c1), xmax - xmin, RED, plane="zy", center=(ox + (xmin + xmax) / 2, 0, 0))
            for (sa, sb, c, kind) in self.stones:                       # dinteles y alféizares de piedra
                if c in iv:
                    a, b = max(sa, iv[c][0]), min(sb, iv[c][1])
                    if b - a > 0.05:
                        y0, y1 = course(c)
                        zf = -0.43 if kind == "lintel" else -0.48
                        mk.box(p, (ox + (a + b) / 2, (y0 + y1) / 2, (zf + 0.1) / 2), (b - a, y1 - y0, 0.1 - zf), STONE)
            ybot, ytop = course(c0)[0] - 0.5, course(c1)[1] + 0.5
            for side in (1, -1):                                         # corte en escalera
                edge = xmax if side > 0 else xmin
                xs = [(iv[c][1] if side > 0 else iv[c][0]) for c in ks]
                if all(abs(x - edge) < 1e-6 for x in xs):
                    mk.carve(p, RED, points=mk.pts_box((ox, -3, 0), (0.1, 0.1, 0.1)))   # une igual
                    continue
                pts = []
                for c, x in zip(ks, xs):
                    if abs(x - edge) < 1e-6:
                        x = edge + side * 0.5
                    y0, y1 = course(c)
                    pts += [(ox + x, ybot if c == c0 else y0), (ox + x, ytop if c == c1 else y1)]
                pts += [(ox + edge + side, ytop), (ox + edge + side, ybot)]
                mk.carve(p, RED, prism=dict(profile=clean(pts), depth=2.0, plane="xy"))
            mk.paint(p, STONE, box=((ox, 0.495, -0.42), (W + 0.2, 0.99, 0.06)))                # zócalo
            mk.paint(p, PLASTER, box=((ox, 5.0, ZB), (W + 0.2, 10.2, 0.02)))                  # revoque adentro
            for c in ks:
                if c == 0:
                    continue
                y0, y1 = course(c)
                mk.paint(p, MORTAR, box=((ox, y0 + 0.025, -0.38), (W + 0.2, 0.052, 0.045)))   # surco
                for x, d in ((iv[c][0], 1), (iv[c][1], -1)):                                  # empalmes del corte
                    if abs(abs(x) - W / 2) < 1e-6 or not self.neighbour(fname, c, x):
                        continue
                    mk.slice(p, (ox + x + d * 0.025, 0, 0), (1, 0, 0))
                    mk.paint(p, MORTAR, box=((ox + x + d * 0.0125, (y0 + 0.05 + y1) / 2, -0.4), (0.027, y1 - y0 - 0.06, 0.02)))
                if c % 3 == 0:                                                                # juntas verticales
                    off = 0.5 if (c // 3) % 2 else 0.0
                    for k in range(8):
                        x = -3.5 + k + off
                        if not iv[c][0] + 0.15 < x < iv[c][1] - 0.15:
                            continue
                        if any(sa - 0.1 < x < sb + 0.1 and cc == c for sa, sb, cc, _ in self.stones):
                            continue
                        for d in (-0.025, 0.025):
                            mk.slice(p, (ox + x + d, 0, 0), (1, 0, 0))
                        mk.paint(p, MORTAR, box=((ox + x, (y0 + 0.05 + y1) / 2, -0.4), (0.052, y1 - y0 - 0.06, 0.02)))


def stairs(c0, c1, x0, step):
    """Tramos de corte en escalera: x por hilada que avanza `step` por hilada desde x0."""
    return {c: x0 + step * (c - c0) for c in range(c0, c1 + 1)}


def two(c0, c1, cut, lo=-4.0, hi=4.0):
    return ({c: (lo, cut[c]) for c in range(c0, c1 + 1)}, {c: (cut[c], hi) for c in range(c0, c1 + 1)})


def build(mk):
    # ---------------- Brick_Wall_Plain: 4 franjas x 2, grietas escalonadas que alternan ----------------
    frags = {}
    for i, (c0, c1, x0, st) in enumerate(((0, 4, 0.9, -0.35), (5, 8, -0.8, 0.4), (9, 13, 1.1, -0.3), (14, 18, -0.6, 0.35))):
        l, r = two(c0, c1, stairs(c0, c1, x0, st))
        frags[f"frag0{2 * i + 1}"], frags[f"frag0{2 * i + 2}"] = l, r
    BrickWall(mk, "Brick_Wall_Plain", 0.0, frags).build()

    # ---------------- Brick_Wall_Window: hueco 3 x 4 (x ±1,5, hiladas 5-12) ----------------
    sill = {0: 2.9, 1: 2.6, 2: 2.3, 3: 2.0, 4: 1.8}                       # antepecho en trapecio
    head = {13: 1.8, 14: 2.0, 15: 2.3, 16: 2.6, 17: 2.8, 18: 3.0}
    fw = {
        "frag01": {c: (-4, -sill[c]) for c in range(0, 5)} | {c: (-4, -1.5) for c in range(5, 9)},
        "frag02": {c: (-sill[c], 0.2 + 0.1 * (c % 2)) for c in range(0, 5)},
        "frag03": {c: (0.2 + 0.1 * (c % 2), sill[c]) for c in range(0, 5)},
        "frag04": {c: (sill[c], 4) for c in range(0, 5)} | {c: (1.5, 4) for c in range(5, 10)},
        "frag05": {c: (-4, -1.5) for c in range(9, 13)} | {c: (-4, -head[c]) for c in range(13, 19)},
        "frag06": {c: (-head[c], -0.3 + 0.2 * (c % 2)) for c in range(13, 19)},
        "frag07": {c: (-0.3 + 0.2 * (c % 2), head[c]) for c in range(13, 19)},
        "frag08": {c: (1.5, 4) for c in range(10, 13)} | {c: (head[c], 4) for c in range(13, 19)},
    }
    BrickWall(mk, "Brick_Wall_Window", 8.0, fw, stones=((-1.8, 1.8, 13, "lintel"), (-1.8, 1.8, 4, "sill"))).build()

    # ---------------- Brick_Wall_Door: hueco 4 x 7,5 (x ±2, hiladas 0-13) ----------------
    dhead = {14: 2.3, 15: 2.6, 16: 2.9, 17: 3.1, 18: 3.3}
    fd = {
        "frag01": {c: (-4, -2) for c in range(0, 5)},
        "frag02": {c: (-4, -2) for c in range(5, 10)},
        "frag03": {c: (-4, -2) for c in range(10, 14)} | {c: (-4, -dhead[c]) for c in range(14, 19)},
        "frag04": {c: (2, 4) for c in range(0, 4)},
        "frag05": {c: (2, 4) for c in range(4, 9)},
        "frag06": {c: (2, 4) for c in range(9, 14)} | {c: (dhead[c], 4) for c in range(14, 19)},
        "frag07": {c: (-dhead[c], 0.1 + 0.15 * (c % 2)) for c in range(14, 19)},
        "frag08": {c: (0.1 + 0.15 * (c % 2), dhead[c]) for c in range(14, 19)},
    }
    BrickWall(mk, "Brick_Wall_Door", 16.0, fd, stones=((-2.3, 2.3, 14, "lintel"),)).build()

    # ---------------- Brick_Wall_DoubleWindow: huecos -3,0..-0,6 y 0,6..3,0 (hiladas 5-12) ----------------
    cut = stairs(0, 4, 1.2, -0.3)                                         # en la hilada 4 corta en x = 0, entre los alféizares
    fdw = {
        "frag01": {c: (-4, cut[c]) for c in range(0, 5)},
        "frag02": {c: (cut[c], 4) for c in range(0, 5)},
        "frag03": {c: (-4, -3.0) for c in range(5, 13)},
        "frag04": {c: (-0.6, 0.6) for c in range(5, 13)},
        "frag05": {c: (3.0, 4) for c in range(5, 13)},
        "frag06": {c: (-4, -1.6 - 0.2 * (c % 2)) for c in range(13, 19)},
        "frag07": {c: (-1.6 - 0.2 * (c % 2), 1.4 + 0.25 * (c % 2)) for c in range(13, 19)},
        "frag08": {c: (1.4 + 0.25 * (c % 2), 4) for c in range(13, 19)},
    }
    BrickWall(mk, "Brick_Wall_DoubleWindow", 24.0, fdw,
              stones=((-3.3, -0.3, 13, "lintel"), (0.3, 3.3, 13, "lintel"), (-3.3, -0.3, 4, "sill"), (0.3, 3.3, 4, "sill"))).build()

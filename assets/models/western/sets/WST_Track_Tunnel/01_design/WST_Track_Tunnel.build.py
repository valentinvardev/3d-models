"""
Receta de WST_Track_Tunnel, el túnel del escenario que corre (prompt 114, Bloques A + B). Usa la vía, el
balasto y el terreno de WST_Track_Tile (se importan) para que las puntas calcen con el tile llano.

Brief
- Silueta a 40 studs: un acantilado de roca roja de 40 de alto con la boca del túnel en arco de piedra gris
  tallada y su clave; adentro, roca oscura y cuadros de madera cada 8.
- Medidas: tiles de 64 (z ±32), tope del riel en y = 0 (como todo el tren). Ancho del túnel 14 (paredes en
  x ±7); el techo libre sobre el eje de la vía es exactamente 15,5: es la cara de abajo de los cuadros de
  madera (la roca queda a 16,2). Los techos de los vagones están a 12: parado (5) no pasa, agachado sí.
- Tunnel_Portal (origen x = 0): de z = -12 a +32 vía al aire libre con el mismo terreno que Track_Plain (la
  punta +32 calza con él); de z = -32 a -12 el acantilado (x ±29, alto 40 desde el suelo) con la boca en la
  cara z = -12, que mira a +Z: hacia el tren que viene (el escenario corre hacia +Z). La punta -32 calza
  con Tunnel_Inner.
- Tunnel_Inner (origen x = +50): roca oscura (redrock_dark) de perfil irregular, piso, vía y 8 cuadros de
  madera en z = -28, -20 … 28 (cada 8 también al empalmar).
- Inferido: qué punta es la boca (la -Z, para que el tren entre de frente), cuadros de dos postes y dos
  pares inclinados, dovelas con juntas, piedras de escombro al pie del acantilado.

Vueltas: 1) primera versión: la placa roja de la cara compartía el perfil del hueco y la junta del medio con la
cáscara oscura (z-fighting en la boca) · 2) placa con el hueco 0,04 más grande y la junta corrida; la cara del
acantilado era una pared plana con cuatro "ventanas" de roca: borde de arriba recortado, clave más grande ·
3) en vez de peñascos pegados (se leían como papas en una pared), columnas de roca lado a lado con el frente
inclinado, como los riscos del cañón.

Revisión
- 2334 triángulos contra 1500 (+56 %): Tunnel_Portal ~1240, Tunnel_Inner ~1090. Cada tile lleva su vía
  (528, de los que 384 son los 32 durmientes): sin ella no calza con el tile llano. Los 10 cuadros de madera
  son ~480.
- Techo libre medido en el eje: 15,5 sobre el tope del riel, en la cara de abajo de los cuadros (los pares se
  cruzan justo ahí; la roca queda a 16,2). La chimenea de la locomotora (15,0) pasa con 0,5 de margen.
- La punta +32 del portal es la del tile llano (mismo terreno y balasto); la -32 y las dos del interior son
  el mismo perfil de roca, piso y vía. Cuadros cada 8 también al empalmar (-28 … 28).
- La boca mira a +Z (hacia el tren que se acerca: el escenario corre hacia +Z); si el escenario corriera al
  revés, se gira el tile 180°.
"""

import importlib.util
import math
import random
from pathlib import Path


def _load(mid, folder="sets"):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(f"recipe_{mid}", root / folder / mid / "01_design" / f"{mid}.build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TT = _load("WST_Track_Tile")
HALF, GROUND_Y = TT.HALF, TT.GROUND_Y
CLEAR = 15.5
BORE = [(7.0, -1.6), (7.25, 1.5), (6.9, 4.5), (7.2, 7.5), (6.8, 9.8), (6.0, 12.0), (4.6, 13.9), (2.6, 15.4), (0.0, 16.2)]
BORE_L = [(7.05, -1.6), (7.15, 1.2), (7.3, 4.2), (6.85, 7.0), (7.0, 9.6), (6.1, 12.2), (4.4, 14.0), (2.5, 15.5), (0.0, 16.2)]
SHELL_X, SHELL_Y = 12.0, 21.0
ARCH_Z = [-28.0 + 8.0 * k for k in range(8)]
X_INNER = 50.0


def shell_half(x0, s, bore, xo=SHELL_X, yt=SHELL_Y, yb=GROUND_Y - 1.3, seam=0.05):
    """Media cáscara en C alrededor del hueco (perfil para prisma a lo largo de Z); s = lado (+1 derecha)."""
    pts = [(x0 + s * 7.0, yb), (x0 + s * xo, yb), (x0 + s * xo, yt), (x0 - s * seam, yt), (x0 - s * seam, bore[-1][1])]
    pts += [(x0 + s * x, y) for x, y in reversed(bore[:-1])]
    return pts if s > 0 else list(reversed(pts))


def timber_set(mk, part, x0, z, w=0.5):
    """Cuadro de madera: dos postes y dos pares inclinados que se cruzan con la cara de abajo a CLEAR."""
    px, py = 6.3, 9.3
    yc = CLEAR + 0.3
    for _ in range(3):                                                           # la cara de abajo en x = 0 da CLEAR
        th = math.atan2(yc - py, px)
        yc = CLEAR + (w / 2) / math.cos(th)
    for s in (-1, 1):
        mk.box(part, (x0 + s * px, (GROUND_Y + py + 0.3) / 2 - 0.05, z), (w, py + 0.3 - GROUND_Y + 0.1, w), "wood_dark")
        a, b = (x0 + s * (px + 0.1), py - 0.1, z), (x0, yc, z)
        d = (b[0] - a[0], b[1] - a[1])
        ln = math.hypot(*d)
        ux, uy = d[0] / ln, d[1] / ln
        ext = (w / 2) * abs(ux) / max(1e-6, abs(uy)) + 0.02                     # llega al eje del otro lado
        b2 = (b[0] + ux * ext, b[1] + uy * ext, z)
        nx, ny = -uy * w / 2, ux * w / 2
        mk.hull(part, [(p[0] + sx * nx, p[1] + sx * ny, p[2] + sz * (w / 2 - 0.01 * (s > 0)))
                       for p in (a, b2) for sx in (-1, 1) for sz in (-1, 1)], "wood_dark")


def build(mk):
    rnd = random.Random(9)
    # ======================= Tunnel_Portal =======================
    p = mk.part("Tunnel_Portal", (0, 0, 0))
    TT.track(mk, p, 0.0, seed=5)
    zc_open, d_open = (-12.0 + HALF) / 2, HALF + 12.0
    mk.prism(p, TT.ground_profile(0, -5.4, 5.4, GROUND_Y, [], depth=1.25), d_open + 0.004, "sand", plane="xy",
             center=(0, 0, zc_open))
    for s, bumps in ((1, [(5.5, 0.22), (11.0, -0.12), (16.5, 0.28), (21.0, 0.05)]),
                     (-1, [(4.5, 0.18), (10.5, 0.3), (15.5, -0.1), (20.5, 0.22)])):
        mk.prism(p, TT.ground_profile(0, s * 5.3, s * 29.0, GROUND_Y, bumps), d_open, "sand", plane="xy",
                 center=(0, 0, zc_open))
    zc_in, d_in = (-HALF - 12.0) / 2, HALF - 12.0
    mk.prism(p, TT.ground_profile(0, -7.3, 7.3, GROUND_Y, [], depth=1.2), d_in + 0.002, "stone_grey", plane="xy",
             center=(0, 0, zc_in))
    # acantilado: cáscara oscura adentro, placa de roca roja en la cara, bloques de roca alrededor
    for s, bore in ((1, BORE), (-1, BORE_L)):
        mk.prism(p, shell_half(0, s, bore), d_in - 0.3 - 0.004 * (s > 0), "redrock_dark", plane="xy",
                 center=(0, 0, zc_in - 0.15))
        grown = [(x + 0.04, y) for x, y in bore[:-1]] + [(0.0, bore[-1][1] + 0.04)]
        mk.prism(p, shell_half(0, s, grown, xo=SHELL_X + 0.3, yt=SHELL_Y + 0.3, yb=GROUND_Y - 1.36, seam=0.09),
                 0.36 - 0.004 * (s > 0),
                 "redrock",
                 plane="xy", center=(0, 0, -12.18))
    # masa del acantilado: dos prismas en L con el borde de arriba recortado (silueta de risco)
    tops = [(29.1, 32.5), (24.0, 36.8), (19.0, 35.0), (13.5, 39.4), (7.0, 37.6), (0.1, 39.0)]
    tops_l = [(29.1, 31.0), (25.0, 34.2), (20.5, 37.9), (15.0, 35.6), (9.0, 38.8), (0.1, 38.4)]
    for s, tp in ((1, tops), (-1, tops_l)):
        prof = [(s * 11.9, GROUND_Y - 1.4), (s * 29.1, GROUND_Y - 1.4)] + [(s * x, y) for x, y in tp]
        prof += [(s * 0.1, SHELL_Y - 0.2), (s * 11.9, SHELL_Y - 0.2)]
        mk.prism(p, prof if s > 0 else list(reversed(prof)), d_in - 0.04 - 0.004 * (s > 0), "redrock", plane="xy",
                 center=(0, 0, zc_in - 0.02))
    # cara del acantilado: columnas de roca con el frente inclinado (como los riscos del cañón), lado a lado,
    # dejando libre la boca; rompen el plano y tapan la junta de los dos prismas
    cols = [(-25.0, 7.6, GROUND_Y - 0.5, 30.4, 1.2, 2.6, "redrock"), (-17.5, 8.0, GROUND_Y - 0.5, 34.6, 2.4, 0.8, "redrock"),
            (-10.0, 7.4, 19.3, 37.8, 1.0, 2.2, "redrock_dark"), (-2.5, 7.6, 20.4, 38.0, 2.0, 1.1, "redrock"),
            (5.0, 7.4, 19.6, 37.0, 0.9, 2.5, "redrock"), (12.5, 7.6, 19.0, 38.6, 2.2, 1.0, "redrock_dark"),
            (19.0, 7.0, GROUND_Y - 0.5, 34.4, 1.0, 2.8, "redrock"), (25.5, 7.2, GROUND_Y - 0.5, 32.0, 2.0, 1.2, "redrock")]
    for x, w, y0, y1, d0, d1, mat in cols:
        hw = w / 2
        back = [(x + sx * hw, y, -12.06) for sx in (-1, 1) for y in (y0, y1)]
        front = [(x + sx * (hw - 0.35) + rnd.uniform(-0.3, 0.3), y0 + 0.4, -12.0 + d0) for sx in (-1, 1)]
        front += [(x + sx * (hw - 0.5) + rnd.uniform(-0.3, 0.3), y1 - 0.6, -12.0 + d1) for sx in (-1, 1)]
        front += [(x + rnd.uniform(-1.0, 1.0), (y0 + y1) / 2, -12.0 + max(d0, d1) + 0.4)]
        mk.hull(p, back + front, mat)
    for s in (-1, 1):
        mk.hull(p, [(s * x, GROUND_Y - 0.2, z) for x in (9.0, 27.0) for z in (-12.2, -6.5)]
                + [(s * 10.5, GROUND_Y + 3.5, -12.1), (s * 24.0, GROUND_Y + 5.0, -12.1), (s * 17.0, GROUND_Y + 1.4, -8.0)],
                "ochre")
        TT.rock(mk, p, (s * 12.5, GROUND_Y + 0.3, -7.5), 1.0, 0.8, "redrock", rnd)
    # boca: jambas, dovelas con juntas y clave
    for s in (-1, 1):
        mk.box(p, (s * 7.85, (GROUND_Y + 9.85) / 2, -11.8), (1.6, 9.85 - GROUND_Y, 0.8), "stone_grey")
        mk.box(p, (s * 7.9, GROUND_Y + 0.3, -11.75), (2.0, 0.7, 1.0), "stone_grey")                 # zócalo
    n = 7
    a_in, b_in, a_out, b_out = 7.05, 6.45, 8.65, 8.05
    for k in range(n):
        g = math.radians(1.0)
        t0, t1 = math.pi * k / n + g, math.pi * (k + 1) / n - g
        key = k == n // 2
        ao, bo = (a_out + 0.7, b_out + 1.1) if key else (a_out, b_out)
        zf = -11.0 if key else -11.4
        pts = []
        for t in (t0, t1):
            for a, b in ((a_in, b_in), (ao, bo)):
                for z in (-12.2, zf):
                    pts.append((a * math.cos(t), 9.8 + b * math.sin(t), z))
        mk.hull(p, pts, "stone_grey")
    for z in (-28.0, -20.0):
        timber_set(mk, p, 0.0, z)

    # ======================= Tunnel_Inner =======================
    x0 = X_INNER
    q = mk.part("Tunnel_Inner", (x0, 0, 0))
    TT.track(mk, q, x0, seed=6)
    mk.prism(q, TT.ground_profile(x0, -7.3, 7.3, GROUND_Y, [], depth=1.2), 2 * HALF + 0.002, "stone_grey", plane="xy",
             center=(0, 0, 0))
    for s, bore in ((1, BORE), (-1, BORE_L)):
        mk.prism(q, shell_half(x0, s, bore), 2 * HALF - 0.004 * (s > 0), "redrock_dark", plane="xy", center=(0, 0, 0))
    for z, s, y, r in ((-24.0, 1, 3.0, 1.1), (-12.0, -1, 6.5, 1.3), (4.0, 1, 10.5, 1.2), (16.0, -1, 2.0, 1.0),
                       (24.0, 1, 7.0, 0.9)):                                                       # bultos de roca
        xw = 7.0 if s > 0 else -7.05
        TT.rock(mk, q, (x0 + xw * 0.97, y, z), r, r * 0.5, "redrock_dark", rnd, k=1.0)
    for z in ARCH_Z:
        timber_set(mk, q, x0, z)

"""
Receta de WST_Track_Trestle, el puente de caballetes de madera sobre un barranco (prompt 115, Bloques
A + B). Usa los rieles, el terreno y las medidas de WST_Track_Tile (se importan) para que las puntas calcen.

Brief
- Silueta a 40 studs: el tablero con la vía muy arriba de un cauce seco, sostenido por caballetes de madera
  oscura cada 8 (postes de afuera inclinados, cruces en X), una pasarela de tablas claras a un costado.
- Medidas: tile de 64 (z ±32), tope del riel en y = 0 como el tile llano (sus puntas calzan: mismos rieles,
  durmientes cada 2 en z = -31 … 31). Durmientes sobre 4 largueros; caballetes en z = -28, -20 … 28 (cada 8
  también al empalmar): sombrero a -1,5, 4 postes (los de afuera de x ±3,6 arriba a ±6,6 abajo), solera a
  -30,4, cauce a -31 (30 abajo del tablero). Pasarela de 1,8 a la derecha (x 3,75 a 5,55) sobre los
  durmientes estirados de ese lado.
- Piezas: Trestle (origen x = 0) y Trestle_Start (origen x = +45): igual, pero desde z = +20 el terreno del
  tile llano (con balasto) y un talud que baja hasta el cauce en z = -10: la punta +32 calza con Track_Plain.
  En el talud los caballetes se acortan hasta el suelo; en el llano no hay.
- Inferido: pasarela a la derecha sin baranda, 4 largueros, una riostra horizontal larga a media altura de cada
  lado, cauce de piedra gris con arena, soleras apoyadas en el suelo.

Vueltas: 1) primera versión: 3144 triángulos; los largueros terminaban en z = 31,998 igual que el balasto de
Trestle_Start (z-fighting en la punta) y una piedra flotaba 0,12 sobre el cauce · 2) sin zapatas de piedra
(-192: la solera apoya en el suelo), largueros a ±31,995, piedras metidas en el cauce.

Revisión
- 2808 triángulos contra 1200 para el modelo entero (2,3 veces): son dos tiles completos (Trestle ~1440 y
  Trestle_Start ~1370) y cada uno lleva la vía del tile llano (rieles 88 + 32 durmientes 384) para que las
  puntas calcen; los 8 caballetes de 4 postes con cruz en X son ~770 por tile. Si hace falta bajar: un solo
  tile con el talud como pieza aparte (Trestle_Start pasaría a ser solo el terreno, ~250).
- Tablero: tope del riel en y = 0 (como el tile llano), cauce a -31 (30 abajo del tablero, como pide).
- Trestle_Start: desde z = +20 el mismo terreno y balasto que Track_Plain (calza en +32), talud ocre hasta el
  cauce en z = -10; los caballetes en el talud llegan hasta el suelo (los de z 20 y 28 no hacen falta).
- La pasarela no tiene baranda: el prompt no la pide y en el tren caerse es parte del juego.
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
CAP_Y0, CAP_Y1 = -2.05, -1.5
SILL_Y = -30.4
BED_Y = -31.0
BENTS = [-28.0 + 8.0 * k for k in range(8)]
X_START = 45.0
SLOPE = [(20.0, -1.52), (16.0, -4.0), (11.0, -8.5), (5.0, -15.5), (-1.0, -22.5), (-6.0, -28.0), (-10.0, BED_Y)]


def bar(mk, part, a, b, w, h, mat, ext=0.0, axis_up=(0, 0, 1)):
    """Barra de sección w (en el plano) x h (en `axis_up`) de a a b."""
    ax, ay, az = a
    bx, by, bz = b
    d = [bx - ax, by - ay, bz - az]
    ln = math.sqrt(sum(c * c for c in d))
    d = [c / ln for c in d]
    a = [ax - d[0] * ext, ay - d[1] * ext, az - d[2] * ext]
    b = [bx + d[0] * ext, by + d[1] * ext, bz + d[2] * ext]
    u = axis_up
    s = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    sl = math.sqrt(sum(c * c for c in s))
    s = [c / sl for c in s]
    pts = []
    for p in (a, b):
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.append(tuple(p[i] + s[i] * sx * w / 2 + u[i] * sy * h / 2 for i in range(3)))
    mk.hull(part, pts, mat)


def slope_y(z):
    """Alto del talud de Trestle_Start en z (el cauce más allá)."""
    if z >= SLOPE[0][0]:
        return SLOPE[0][1]
    for (z0, y0), (z1, y1) in zip(SLOPE, SLOPE[1:]):
        if z1 <= z <= z0:
            return y0 + (y1 - y0) * (z0 - z) / (z0 - z1)
    return BED_Y


def deck(mk, p, x0, seed):
    """Rieles, durmientes (estirados a la derecha para la pasarela), largueros y pasarela."""
    for s in (-1, 1):
        mk.prism(p, [(x0 + s * TT.RAIL_X + dx, y) for dx, y in TT.RAIL_PROFILE], 2 * HALF, "iron", plane="xy",
                 center=(0, 0, 0))
    rnd = random.Random(seed)
    for i in range(32):
        z = -HALF + 1.0 + 2.0 * i
        a = rnd.choice((0.0, 0.0, 1.0, -1.0))
        mk.box(p, (x0 + 1.05, (TT.TIE_Y0 + TT.TIE_Y1) / 2 + 0.002 * (i % 2), z), (9.3, TT.TIE_Y1 - TT.TIE_Y0, 0.7),
               "wood_dark" if i % 3 else "wood_mid", rot=(0, a, 0))
    for x in (-2.6, -1.0, 1.0, 2.6):
        mk.box(p, (x0 + x, (CAP_Y1 + 0.02 + TT.TIE_Y0 + 0.02) / 2, 0), (0.45, TT.TIE_Y0 - CAP_Y1, 2 * HALF - 0.01), "wood_dark")
    for k, x in enumerate((3.75, 4.37, 4.99)):
        mk.box(p, (x0 + x + 0.28, TT.TIE_Y1 + 0.05, 0), (0.56, 0.12, 2 * HALF - 0.01 * k), "wood_mid")


def bent(mk, p, x0, z, foot):
    """Caballete en z: sombrero, 4 postes hasta `foot` (y del suelo), solera, zapatas y cruz en X."""
    w = 0.5
    mk.box(p, (x0, (CAP_Y0 + CAP_Y1) / 2, z), (8.4, CAP_Y1 - CAP_Y0, 0.6), "wood_dark")                 # sombrero
    sill_top = foot + 0.6
    t = (CAP_Y0 - sill_top) / (CAP_Y0 - SILL_Y)                                                        # cuánto baja
    xo_bot = 3.6 + 3.0 * t
    for s in (-1, 1):
        bar(mk, p, (x0 + s * 1.5, CAP_Y0 + 0.02, z), (x0 + s * 1.5, sill_top - 0.02, z), w, w - 0.02, "wood_dark")
        bar(mk, p, (x0 + s * 3.6, CAP_Y0 + 0.02, z), (x0 + s * xo_bot, sill_top - 0.02, z), w, w, "wood_dark")
    mk.box(p, (x0, sill_top - 0.35, z), (2 * xo_bot + 1.2, 0.7, 0.62), "wood_dark")                       # solera (se mete 0,1)
    if CAP_Y0 - sill_top > 4.0:                                                                         # cruz en X
        for k, s in enumerate((-1, 1)):
            a = (x0 + s * 3.75, CAP_Y0 - 0.6, z - 0.31 - 0.02 * k)
            b = (x0 - s * (xo_bot + 0.1), sill_top + 0.5, z - 0.31 - 0.02 * k)
            bar(mk, p, a, b, 0.4, 0.14, "wood_dark", ext=0.1)


def riverbed(mk, p, x0, z0, z1, rnd):
    zc, d = (z0 + z1) / 2, z1 - z0
    prof = [(x0 - 16.0, BED_Y + 0.4), (x0 - 8.0, BED_Y + 0.1), (x0 - 2.0, BED_Y - 0.25), (x0 + 3.0, BED_Y - 0.2),
            (x0 + 9.0, BED_Y + 0.15), (x0 + 16.0, BED_Y + 0.5), (x0 + 16.0, BED_Y - 1.3), (x0 - 16.0, BED_Y - 1.3)]
    mk.prism(p, list(reversed(prof)), d, "sand", plane="xy", center=(0, 0, zc))
    mk.prism(p, [(x0 - 3.0, BED_Y - 0.15), (x0 + 3.6, BED_Y - 0.1), (x0 + 4.2, BED_Y - 0.5), (x0 - 3.6, BED_Y - 0.55)][::-1],
             d - 0.004, "stone_grey", plane="xy", center=(0, 0, zc))


def build(mk):
    rnd = random.Random(12)
    # ======================= Trestle =======================
    p = mk.part("Trestle", (0, 0, 0))
    deck(mk, p, 0.0, seed=21)
    for z in BENTS:
        bent(mk, p, 0.0, z, BED_Y)
    for s in (-1, 1):
        bar(mk, p, (s * 5.35, -16.0, -HALF), (s * 5.35, -16.0, HALF), 0.4, 0.5, "wood_dark", axis_up=(1, 0, 0))
    riverbed(mk, p, 0.0, -HALF, HALF, rnd)
    for x, z, r in ((-9.0, -14.0, 1.6), (11.0, 9.0, 1.3), (-5.0, 22.0, 1.0)):
        TT.rock(mk, p, (x, BED_Y - 0.1, z), r, r * 0.6, "stone_grey", rnd, k=1.0)

    # ======================= Trestle_Start =======================
    x0 = X_START
    q = mk.part("Trestle_Start", (x0, 0, 0))
    deck(mk, q, x0, seed=22)
    for z in BENTS:
        foot = slope_y(z)
        if foot < -4.0:
            bent(mk, q, x0, z, foot)
    for s in (-1, 1):
        bar(mk, q, (x0 + s * 5.35, -16.0, -HALF), (x0 + s * 5.35, -16.0, 4.8), 0.4, 0.5, "wood_dark", axis_up=(1, 0, 0))
    # el terreno del tile llano desde z = 20 (calza con Track_Plain en +32) y el talud hasta el cauce
    zc, d = (20.0 + HALF) / 2, HALF - 20.0
    TT_lo = [(x0 - 5.0, GROUND_Y - 0.03), (x0 + 5.0, GROUND_Y - 0.03), (x0 + 4.5, -1.06), (x0 - 4.5, -1.06)]
    TT_hi = [(x0 - 4.56, -1.1), (x0 + 4.56, -1.1), (x0 + 3.95, -0.7), (x0 + 3.7, TT.BALLAST_TOP), (x0 - 3.7, TT.BALLAST_TOP),
             (x0 - 3.95, -0.7)]
    mk.prism(q, TT_lo, d, "ochre", plane="xy", center=(0, 0, zc))
    mk.prism(q, TT_hi, d - 0.004, "stone_grey", plane="xy", center=(0, 0, zc))
    mk.prism(q, TT.ground_profile(x0, -5.4, 5.4, GROUND_Y, [], depth=1.25), d + 0.004, "sand", plane="xy",
             center=(0, 0, zc))
    for s, bumps in ((1, [(5.5, 0.22), (11.0, -0.12), (16.5, 0.28), (21.0, 0.05)]),
                     (-1, [(4.5, 0.18), (10.5, 0.3), (15.5, -0.1), (20.5, 0.22)])):
        mk.prism(q, TT.ground_profile(x0, s * 5.3, s * 29.0, GROUND_Y, bumps), d, "sand", plane="xy", center=(0, 0, zc))
    prof = [(z, y) for z, y in SLOPE] + [(SLOPE[-1][0], BED_Y - 1.3), (20.6, BED_Y - 1.3), (20.6, GROUND_Y - 0.12)]
    mk.prism(q, prof, 58.0, "ochre", plane="zy", center=(x0, 0, 0))
    riverbed(mk, q, x0, -HALF, -9.0, rnd)
    TT.rock(mk, q, (x0 - 8.0, slope_y(8.0) + 0.2, 8.0), 1.6, 1.0, "redrock", rnd, k=1.0)
    TT.rock(mk, q, (x0 + 10.0, slope_y(-3.0) + 0.2, -3.0), 1.4, 0.8, "stone_grey", rnd, k=1.0)

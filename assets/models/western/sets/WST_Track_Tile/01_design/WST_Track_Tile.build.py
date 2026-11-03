"""
Receta de WST_Track_Tile, los tramos de vía y terreno que corren bajo el tren quieto (prompt 113, Bloques
A + B; D002: se mueve el escenario). Tres variantes en fila sobre X, cada una con su origen. Las ayudas de la
vía (rieles, durmientes, balasto) las importan el túnel y el puente.

Brief
- Silueta a 40 studs: la vía recta con durmientes oscuros sobre un lomo de balasto gris, desierto de arena a
  los costados con piedras bajas; en Track_Cut, paredes de roca roja a los dos lados; en Track_Embankment, la
  vía arriba de un terraplén de 6 con taludes ocres.
- Medidas: 64 de largo (z de -32 a +32; las puntas calzan exacto: todo lo que llega a la punta es un prisma con
  el mismo perfil en las dos caras y los durmientes van en z = -31, -29 … 31, cada 2 también entre tiles).
  Rieles con trocha 4,6 (centro en x = ±2,43, como las ruedas del tren), tope del riel en y = 0 = el origen de
  cada tile (los vagones tienen los rieles en y = 0: tren y escenario comparten la altura). Durmientes de 7,2
  x 0,7; balasto de 10 de ancho y 1 de alto (base a -1,5); 24 de desierto a cada lado (x ±29).
  Track_Cut: paredes de 6 sobre el piso (tope a 4,5), separadas 14 (caras en x = ±7).
  Track_Embankment: terraplén de 6 (el suelo a -7,5), taludes hasta x = ±15.
- Piezas: Track_Plain (origen x = 0), Track_Cut (x = +75), Track_Embankment (x = -75), con el origen al centro
  del tile sobre el tope del riel. Marcadores vacíos _Cactus_<variante>_<n> donde van los cactus.
- Inferido: el origen en el tope del riel (no en el suelo: con terraplén y corte el suelo cambia de altura);
  perfil de riel en doble T; balasto gris arriba y faldón ocre; terreno con lomitas suaves (prisma, igual en
  las dos puntas); estratos más oscuros al pie de las paredes del corte; nombres de los marcadores con la
  variante (no puede haber dos objetos con el mismo nombre).

Vueltas: 1) primera versión: fondos coplanares donde se pisaban la franja del medio y los costados del
terreno (y en el corte con las paredes y en el terraplén), una piedra flotando 0,05 · 2) piedras 1,6 veces
más grandes (a la distancia de juego eran puntitos) y la tapa de arena del corte siempre por encima de la
roca (asomaba como una franja roja).

Revisión
- Triángulos por tile (tope 800): Track_Plain ~700, Track_Cut ~790, Track_Embankment ~690. Los 32 durmientes
  son 384 de cada tile; el riel en doble T es un prisma de 44.
- Las puntas calzan: rieles, balasto y terreno son prismas de 64 (o 64,004) con el mismo perfil en z = ±32;
  durmientes en z = -31 … 31 (separación 2 también al empalmar); piedras y salientes lejos de las puntas.
- El tope del riel queda en y = 0 en las tres variantes (el suelo del llano a -1,5, el del terraplén a -7,5,
  el borde del corte a 4,5): tren y escenario se ubican con el mismo origen. Si Valentin prefiere el origen en
  el suelo, es correr cada tile 1,5 hacia arriba.
- Los marcadores de cactus llevan la variante en el nombre (_Cactus_Plain_1…): dos objetos no pueden llamarse
  igual en el mismo archivo.
"""

import math
import random

HALF = 32.0
GAUGE = 4.6
RAIL_X = GAUGE / 2 + 0.13
TIE_Y0, TIE_Y1 = -0.72, -0.39
BALLAST_TOP, GROUND_Y = -0.55, -1.5
RAIL_PROFILE = [(-0.13, 0.0), (0.13, 0.0), (0.13, -0.12), (0.05, -0.16), (0.05, -0.3), (0.18, -0.34), (0.18, -0.4),
                (-0.18, -0.4), (-0.18, -0.34), (-0.05, -0.3), (-0.05, -0.16), (-0.13, -0.12)]
OFFSETS = {"Track_Plain": 0.0, "Track_Cut": 75.0, "Track_Embankment": -75.0}


def B(mk, part, x0, x1, y0, y1, z0, z1, mat, rot=(0, 0, 0)):
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mat, rot=rot)


def track(mk, part, x0=0.0, base=GROUND_Y, seed=1, ballast=True, tie_mats=("wood_dark", "wood_dark", "wood_mid")):
    """Rieles, durmientes cada 2 y balasto, con las puntas en z = ±32."""
    for s in (-1, 1):
        mk.prism(part, [(x0 + s * RAIL_X + dx, y) for dx, y in RAIL_PROFILE], 2 * HALF, "iron", plane="xy",
                 center=(0, 0, 0))
    rnd = random.Random(seed)
    for i in range(32):
        z = -HALF + 1.0 + 2.0 * i
        a = rnd.choice((0.0, 0.0, 0.0, 1.5, -1.5, 2.5))
        dx = rnd.uniform(-0.12, 0.12)
        mk.box(part, (x0 + dx, (TIE_Y0 + TIE_Y1) / 2 + 0.002 * (i % 2), z), (7.2, TIE_Y1 - TIE_Y0, 0.7),
               tie_mats[i % len(tie_mats)], rot=(0, a, 0))
    if ballast:
        lo = [(x0 - 5.0, base - 0.03), (x0 + 5.0, base - 0.03), (x0 + 4.5, -1.06), (x0 - 4.5, -1.06)]
        hi = [(x0 - 4.56, -1.1), (x0 + 4.56, -1.1), (x0 + 3.95, -0.7), (x0 + 3.7, BALLAST_TOP),
              (x0 - 3.7, BALLAST_TOP), (x0 - 3.95, -0.7)]
        mk.prism(part, lo, 2 * HALF, "ochre", plane="xy", center=(0, 0, 0))
        mk.prism(part, hi, 2 * HALF - 0.004, "stone_grey", plane="xy", center=(0, 0, 0))


def rock(mk, part, c, r, h, mat, rnd, n=7, k=1.6):
    """Piedra baja facetada apoyada en el suelo (se mete 0,15); k agranda (a 40 studs las de 1 no se veían)."""
    cx, cy, cz = c
    r, h = r * k, h * k * 0.9
    pts = [(cx + r * rnd.uniform(0.7, 1.0) * math.cos(a), cy - 0.15, cz + r * rnd.uniform(0.6, 1.0) * math.sin(a))
           for a in [2 * math.pi * k / n + rnd.uniform(-0.25, 0.25) for k in range(n)]]
    pts += [(cx + r * 0.55 * rnd.uniform(0.6, 1.0) * math.cos(a), cy + h * rnd.uniform(0.6, 0.9),
             cz + r * 0.5 * rnd.uniform(0.6, 1.0) * math.sin(a)) for a in [2 * math.pi * k / 4 + 0.4 for k in range(4)]]
    pts.append((cx + rnd.uniform(-0.2, 0.2) * r, cy + h, cz + rnd.uniform(-0.2, 0.2) * r))
    mk.hull(part, pts, mat)


def ground_profile(x0, x_in, x_out, y, bumps, depth=1.1):
    """Arriba del terreno de x_in a x_out (con lomitas) y base 1,1 más abajo: perfil para prisma (sentido antihorario)."""
    s = 1 if x_out > x_in else -1
    top = [(x0 + x_in, y)] + [(x0 + x_in + s * d, y + dy) for d, dy in bumps] + [(x0 + x_out, y)]
    prof = top + [(x0 + x_out, y - depth), (x0 + x_in, y - depth)]
    return prof if s > 0 else list(reversed(prof))


def build(mk):
    rnd = random.Random(4)
    # ======================= Track_Plain =======================
    x0 = OFFSETS["Track_Plain"]
    p = mk.part("Track_Plain", (x0, 0, 0))
    track(mk, p, x0, seed=1)
    mk.prism(p, ground_profile(x0, -5.4, 5.4, GROUND_Y, [], depth=1.25), 2 * HALF + 0.004, "sand", plane="xy",
             center=(0, 0, 0))
    for s, bumps in ((1, [(5.5, 0.22), (11.0, -0.12), (16.5, 0.28), (21.0, 0.05)]),
                     (-1, [(4.5, 0.18), (10.5, 0.3), (15.5, -0.1), (20.5, 0.22)])):
        mk.prism(p, ground_profile(x0, s * 5.3, s * 29.0, GROUND_Y, bumps), 2 * HALF, "sand", plane="xy", center=(0, 0, 0))
    for (x, z, r, h, mat) in ((9.5, -18.0, 1.4, 0.7, "redrock"), (14.0, 6.0, 0.9, 0.45, "stone_grey"),
                              (23.5, 20.0, 1.7, 0.9, "redrock"), (-12.5, -6.0, 1.2, 0.6, "ochre"),
                              (-20.0, 17.0, 1.5, 0.8, "redrock"), (-8.5, 24.0, 0.8, 0.4, "stone_grey")):
        rock(mk, p, (x0 + x, GROUND_Y + 0.1, z), r, h, mat, rnd)
    mk.marker("_Cactus_Plain_1", (x0 + 17.0, GROUND_Y, -8.0))
    mk.marker("_Cactus_Plain_2", (x0 - 15.0, GROUND_Y, 9.0))

    # ======================= Track_Cut =======================
    x0 = OFFSETS["Track_Cut"]
    p = mk.part("Track_Cut", (x0, 0, 0))
    track(mk, p, x0, seed=2)
    mk.prism(p, ground_profile(x0, -7.3, 7.3, GROUND_Y, [], depth=1.25), 2 * HALF + 0.004, "sand", plane="xy",
             center=(0, 0, 0))
    top_y = GROUND_Y + 6.0
    for s in (-1, 1):
        face = [(7.0, GROUND_Y - 0.1), (7.45, GROUND_Y + 1.3), (7.15, GROUND_Y + 2.5), (7.8, GROUND_Y + 3.7),
                (7.5, GROUND_Y + 4.8), (8.3, top_y)]
        rockp = [(x0 + s * x, y) for x, y in face] + [(x0 + s * 29.0, top_y), (x0 + s * 29.0, GROUND_Y - 1.1),
                                                     (x0 + s * 7.0, GROUND_Y - 1.1)]
        mk.prism(p, rockp if s > 0 else list(reversed(rockp)), 2 * HALF, "redrock", plane="xy", center=(0, 0, 0))
        strata = [(x0 + s * x, y) for x, y in ((6.88, GROUND_Y - 0.05), (7.32, GROUND_Y + 1.3), (7.12, GROUND_Y + 2.2),
                                                 (9.5, GROUND_Y + 2.2), (9.5, GROUND_Y - 0.05))]
        mk.prism(p, strata if s > 0 else list(reversed(strata)), 2 * HALF - 0.004, "redrock_dark", plane="xy",
                 center=(0, 0, 0))
        bumps = [(4.0, 0.3), (9.0, 0.08), (14.5, 0.35)]
        mk.prism(p, ground_profile(x0, s * 8.1, s * 28.98, top_y, bumps), 2 * HALF + 0.004, "sand", plane="xy",
                 center=(0, 0, 0))
        for z, r, h in ((-20.0, 1.2, 1.6), (-3.0, 1.0, 1.2), (15.0, 1.4, 1.9)):                     # salientes de la pared
            zz = z * s + (4.0 if s < 0 else 0.0)
            mk.hull(p, [(x0 + s * 8.0, GROUND_Y + yy, zz + dz) for yy in (0.4, 0.4 + h * 2.2) for dz in (-r, r)]
                    + [(x0 + s * (7.0 - 0.7 * rnd.uniform(0.6, 1.0)), GROUND_Y + 0.4 + h * 1.1, zz + rnd.uniform(-0.3, 0.3))],
                    "redrock")
        rock(mk, p, (x0 + s * 6.0, GROUND_Y + 0.1, -11.0 * s), 0.8, 0.6, "redrock", rnd, k=1.2)
        rock(mk, p, (x0 + s * 18.0, top_y + 0.1, 8.0 * s), 1.3, 0.7, "stone_grey", rnd)
    mk.marker("_Cactus_Cut_1", (x0 + 20.0, top_y, -14.0))

    # ======================= Track_Embankment =======================
    x0 = OFFSETS["Track_Embankment"]
    p = mk.part("Track_Embankment", (x0, 0, 0))
    track(mk, p, x0, seed=3)
    low = GROUND_Y - 6.0
    emb = [(-6.0, GROUND_Y), (6.0, GROUND_Y), (8.8, GROUND_Y - 1.7), (11.7, GROUND_Y - 4.0), (15.2, low - 0.1),
           (15.2, low - 1.25), (-15.2, low - 1.25), (-15.2, low - 0.1), (-11.9, GROUND_Y - 4.1), (-9.0, GROUND_Y - 1.8)]
    mk.prism(p, [(x0 + x, y) for x, y in emb], 2 * HALF, "ochre", plane="xy", center=(0, 0, 0))
    for s, bumps in ((1, [(4.0, 0.2), (9.0, -0.1)]), (-1, [(3.5, 0.25), (8.5, 0.05)])):
        mk.prism(p, ground_profile(x0, s * 15.0, s * 29.0, low, bumps), 2 * HALF + 0.004, "sand", plane="xy",
                 center=(0, 0, 0))
    for (x, y, z, r, h, mat) in ((10.2, GROUND_Y - 2.6, -12.0, 0.9, 0.5, "stone_grey"),
                                 (-10.6, GROUND_Y - 3.0, 9.0, 1.1, 0.6, "redrock"),
                                 (20.0, low + 0.1, 14.0, 1.6, 0.8, "redrock"),
                                 (-22.0, low + 0.1, -16.0, 1.3, 0.7, "stone_grey"),
                                 (24.0, low - 0.05, -22.0, 0.9, 0.5, "ochre")):
        rock(mk, p, (x0 + x, y, z), r, h, mat, rnd)
    mk.marker("_Cactus_Embankment_1", (x0 - 19.0, low, 4.0))
    mk.marker("_Cactus_Embankment_2", (x0 + 21.0, low, -6.0))

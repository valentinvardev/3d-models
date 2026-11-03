"""
Receta de WST_Mine_Gallery, la galería amplia de la mina (prompt 099, Bloques A + B).

Brief
- Lo que se lee adentro: una cueva grande de roca facetada (40 x 40 de piso, techo de 20 a 23), con la
  vía que la cruza sobre un caballete bajo de punta a punta, un andamio de dos pisos contra la pared
  izquierda y tres columnas de cuadros de troncos apilados que sostienen panzas de roca del techo.
- Grilla: el piso de la galería (el pozo trabajado) está en y = 0 y es el origen. Las dos bocas tienen el
  perfil de WST_Mine_Tunnel y su piso a y = 3: el módulo de túnel se pone con el origen en (0, 3, ±31,5)
  (su punta en z = ±23,5, la cara de afuera de la galería). La vía sale de cada boca sobre una repisa de
  tierra (y = 3) y cruza el pozo sobre el caballete (riel a y = 3,5, igual que en los túneles).
- Shell: un bloque de roca (48 x 27,5 x 47) tallado por un casco irregular (cinco anillos de 16 puntos,
  de esquinas redondeadas: piso 40 x 39, panza a y 8, techo en punta a y 23) y por las dos bocas; piso de
  tierra en losa, dos repisas en las bocas, estribos de roca en las paredes, piedras en el piso y tres
  panzas de roca colgando sobre las columnas. Parches redrock_dark y ochre pintados.
- Scaffolding: contra la pared -X, de z = -12,4 a 8,4: piso bajo de 3,8 a y = 6 y pasarela de 2,3 a
  y = 12 con baranda, postes cada 4, vigas, cruces y dos escaleras (piso -> 6 y 6 -> 12).
- RailTrestle: la vía de z = -23,5 a 23,5 (41 durmientes) sobre dos largueros y cinco caballetes de
  poste y sombrero en el pozo.
- Pillars: tres columnas de cuadros de 4 x 4 (troncos de 1,0, capas cruzadas que alternan dos maderas)
  del piso hasta el techo: la altura sale de un rayo contra el casco de la cámara (17,5-19,5), con una
  almohada y dos cuñas que se meten en la roca.
- Inferido: el pozo bajado 3 respecto de las bocas (así el caballete bajo tiene sentido y hay altura para
  combatir), las repisas, la pasarela más angosta que el piso bajo, la posición de las escaleras y las
  columnas, la cantidad de caballetes y los colores.

Vueltas: 1) pasa la revisión (3312) · 2) un estribo quedaba entero adentro de la roca y una piedra adentro
de una repisa (avisos "enclosed"): movidos; vigas del andamio al ras de los pisos y la escalera de arriba
apoyada fuera del borde del piso bajo · 3) las panzas de roca sobre las columnas se leían como piedras
apoyadas encima (hongos): sin panzas, los cuadros suben hasta el techo medido.

Revisión
- 3496 triángulos contra 4000: Pillars 1428 (54 capas de troncos: es lo que las hace "cuadros"), RailTrestle
  780 (41 durmientes en 47 de vía, 492), Scaffolding 688, Shell 600.
- Medidas: 48 x 27,5 x 47 por afuera (la cámara: piso de ~40 x 39, techo en punta a 23); el punto más
  bajo (-1,5) es la roca debajo del piso. Bocas a z = ±23,5 con el perfil exacto del túnel y su piso a
  y = 3: el riel queda a y 3,5, igual que el de un módulo de túnel puesto en (0, 3, ±31,5).
- Paso: pisos del andamio a 6 y 12 (pasarela de 2,3 con baranda a 13); el caballete a 3 deja pasar por
  debajo entre caballetes (4,8 de luz, 2,0 de alto bajo el sombrero).
- Dudoso (Valentin): el pozo bajado 3 respecto de las bocas es inferido (el prompt no dice dónde está el
  piso respecto de los túneles); la cáscara es un objeto hueco y necesita PreciseConvexDecomposition, igual
  que el andamio y las columnas (tres juntas en un objeto).
"""

import importlib.util
import math
from pathlib import Path

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

_spec = importlib.util.spec_from_file_location(
    "mine_tunnel", Path(__file__).resolve().parents[2] / "WST_Mine_Tunnel" / "01_design" / "WST_Mine_Tunnel.build.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
RAILS = T.RAILS

ROCK, ROCK2, DIRT = "stone_grey", "redrock_dark", "ochre"
WOOD, WOOD2, IRON = "wood_dark", "wood_mid", "iron"
LEDGE_Y = 3.0
OPEN_Z = 23.5                       # cara de afuera, donde calza el túnel
PILLARS = [(8.0, -7.0), (12.5, 5.0), (-7.5, 3.5)]
CRIB_TOP = 16.0


# ---------------- cáscara ----------------
def squircle(rx, rz, n, rng, jit, y, ph=0.0):
    pts = []
    for k in range(n):
        t = 2 * math.pi * (k + 0.5 + ph) / n
        c, s = math.cos(t), math.sin(t)
        x = rx * math.copysign(abs(c) ** 0.5, c)
        z = rz * math.copysign(abs(s) ** 0.5, s)
        f = 1.0 + jit * (rng.u() - 0.5)
        pts.append((x * f, y + 0.6 * (rng.u() - 0.5) if y > 0 else y, z * f))
    return pts


def chamber_pts():
    r = T.Rng(17)
    pts = []
    for y, rx, rz, n, jit, ph in ((-0.3, 19.6, 19.4, 16, 0.04, 0.0), (8.0, 20.6, 20.3, 16, 0.07, 0.25),
                                  (15.0, 17.6, 17.2, 14, 0.09, 0.1), (20.0, 11.0, 10.4, 10, 0.12, 0.3),
                                  (22.6, 4.5, 3.8, 6, 0.2, 0.0)):
        pts += squircle(rx, rz, n, r, jit, y, ph)
    pts.append((1.2, 23.4, -0.8))
    return pts


def shell(mk):
    p = mk.part("Shell", (0, 0, 0))
    mk.box(p, (0, 12.25, 0), (48.0, 27.5, 2 * OPEN_Z), ROCK2)
    mk.carve(p, ROCK, points=chamber_pts())
    pc = [(x, y + LEDGE_Y) for x, y in T.sunk(T.PC, T.FLOOR_CUT)]
    for s in (-1, 1):
        mk.carve(p, ROCK, points=[(x, y, s * (OPEN_Z + 0.5)) for x, y in pc] + [(x, y, s * 15.5) for x, y in pc])
    # parches de color en las paredes y el techo
    for c, rad, mat in (((-19.5, 9.0, -6.0), 5.0, ROCK2), ((19.0, 4.0, 8.0), 4.5, DIRT), ((6.0, 21.0, 4.0), 5.0, ROCK2),
                        ((-8.0, 12.0, 18.5), 4.5, DIRT), ((12.0, 13.0, -17.5), 5.0, ROCK2), ((-15.0, 17.0, 8.0), 4.0, DIRT),
                        ((17.0, 15.0, -4.0), 4.0, DIRT), ((-4.0, 20.0, -10.0), 4.5, ROCK2)):
        mk.paint(p, mat, ball=(c, rad))
    # piso de tierra (losa metida en las paredes) y las dos repisas de las bocas
    r = T.Rng(5)
    floor = [(x * 1.035, z * 1.035) for x, _, z in squircle(19.6, 19.4, 16, r, 0.0, -0.3)]
    mk.prism(p, floor, 0.31, DIRT, plane="xz", center=(0, -0.155, 0), detail=True)
    for s in (-1, 1):
        mk.hull(p, [(x, y, s * z) for x, y, z in ((-6.0, LEDGE_Y, 11.6), (6.0, LEDGE_Y, 11.8), (-6.2, LEDGE_Y, OPEN_Z - 0.05),
                                                   (6.2, LEDGE_Y, OPEN_Z - 0.05), (-9.5, -0.2, 8.6), (9.0, -0.2, 8.8),
                                                   (-10.5, -0.2, OPEN_Z - 0.05), (10.0, -0.2, OPEN_Z - 0.05),
                                                   (-8.2, 1.6, 9.8), (7.6, 1.8, 10.2))], DIRT, detail=True)
    # estribos de roca contra las paredes (rompen la cúpula convexa) y piedras en el piso
    for i, (c, size, rot, mat) in enumerate((
            ((-20.2, 4.0, 14.0), (3.4, 8.5, 4.2), (0, 20, 6), ROCK), ((20.3, 6.0, -12.0), (3.6, 11.0, 5.0), (0, -15, -5), ROCK),
            ((19.8, 3.0, 12.5), (3.0, 6.0, 4.0), (0, 30, 4), ROCK2), ((-14.6, 12.0, -16.6), (4.0, 6.0, 4.4), (10, 40, 0), ROCK),
            ((14.0, 4.0, -19.4), (6.0, 8.0, 3.2), (0, 10, 0), ROCK2), ((-13.0, 3.0, 19.6), (5.0, 6.0, 3.0), (0, -8, 0), ROCK),
            ((16.0, 16.0, 12.0), (5.0, 3.5, 6.0), (15, 30, 10), ROCK), ((-6.0, 21.5, 9.0), (5.0, 3.0, 4.0), (0, 40, 10), ROCK2))):
        T.chunk(mk, p, c, size, 200 + i, rot=rot, mat=mat)
    for i, (x, z, sz) in enumerate(((4.0, 3.0, 1.2), (14.5, -2.0, 1.6), (-12.0, -12.0, 1.4), (-13.5, -7.0, 1.0),
                                    (16.0, 16.0, 1.3), (-10.5, 13.0, 0.9))):
        T.chunk(mk, p, (x, 0.3 * sz, z), (1.6 * sz, 1.1 * sz, 1.4 * sz), 230 + i, rot=(0, 47 * i, 6),
                mat=ROCK if i % 2 else ROCK2)


# ---------------- andamio ----------------
XB, XF, XU = -18.7, -15.2, -16.8           # postes de atrás, de adelante (piso bajo) y de la pasarela
Z0, Z1 = -12.4, 8.4


def scaffolding(mk):
    p = mk.part("Scaffolding", (0, 0, 0))
    zs = [-12.0, -8.0, -4.0, 0.0, 4.0, 8.0]
    for z in zs:
        mk.box(p, (XB, 6.55, z), (0.45, 13.14, 0.45), WOOD)                     # atrás, de 0 a 13,1
        mk.box(p, (XF, 3.49, z), (0.45, 7.02, 0.45), WOOD)                      # adelante, hasta el piso bajo
        mk.box(p, (XU, 9.5, z), (0.4, 7.1, 0.4), WOOD)                          # pasarela, parados en el piso bajo
        mk.box(p, ((XB + XF) / 2 - 0.15, 5.57, z), (4.04, 0.4, 0.36), WOOD)      # vigas bajo el piso
        mk.box(p, ((XB + XU) / 2 - 0.1, 11.57, z), (2.44, 0.4, 0.34), WOOD)     # vigas bajo la pasarela
    # pisos de tablas (a lo largo de Z) con juntas pintadas
    mk.box(p, ((XB + XF) / 2 - 0.15, 5.875, (Z0 + Z1) / 2), (4.1, 0.25, Z1 - Z0), WOOD2)
    mk.box(p, ((XB + XU) / 2 - 0.1, 11.875, (Z0 + Z1) / 2), (2.5, 0.25, Z1 - Z0 + 0.02), WOOD2)
    for x in (-17.9, -16.9, -15.9):
        for d in (-0.03, 0.03):
            mk.slice(p, (x + d, 0, 0), (1, 0, 0))
        for y in (6.0, 12.0):
            mk.paint(p, WOOD, box=((x, y, (Z0 + Z1) / 2), (0.07, 0.02, Z1 - Z0 + 0.1)))
    # baranda de la pasarela (con un hueco donde llega la escalera)
    mk.box(p, (XU, 13.0, (-9.2 + Z1) / 2), (0.16, 0.16, Z1 + 9.2), WOOD)
    mk.box(p, (XU, 12.5, (Z0 - 10.8) / 2 + 0.0), (0.14, 0.14, abs(Z0 - (-10.8))), WOOD)
    # cruces en el frente del piso bajo (dos tramos)
    for za, zb in ((-8.0, -4.0), (0.0, 4.0)):
        T_beam(mk, p, (XF, 0.4, za), (XF, 5.3, zb), 0.22)
        T_beam(mk, p, (XF + 0.03, 0.4, zb), (XF + 0.03, 5.3, za), 0.22)
    # escaleras
    ladder(mk, p, (-13.4, 0.0, 6.0), (-15.0, 6.85, 6.0))
    ladder(mk, p, (-15.35, 5.98, -10.0), (-16.6, 12.85, -10.0))


def T_beam(mk, part, a, b, w, mat=WOOD):
    ax, ay, az = a
    bx, by, bz = b
    d = (bx - ax, by - ay, bz - az)
    ln = math.sqrt(sum(c * c for c in d))
    u = tuple(c / ln for c in d)
    ref = (1, 0, 0) if abs(u[0]) < 0.9 else (0, 1, 0)
    v = (u[1] * ref[2] - u[2] * ref[1], u[2] * ref[0] - u[0] * ref[2], u[0] * ref[1] - u[1] * ref[0])
    vl = math.sqrt(sum(c * c for c in v))
    v = tuple(c / vl for c in v)
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    pts = [tuple(q[k] + v[k] * sv + n[k] * sn for k in range(3)) for q in (a, b) for sv in (-w / 2, w / 2)
           for sn in (-w / 2, w / 2)]
    mk.hull(part, pts, mat)


def ladder(mk, part, base, top):
    """Escalera inclinada en el plano XY (ancho a lo largo de Z): dos largueros y peldaños cada 1,0."""
    (bx, by, bz), (tx, ty, tz) = base, top
    for dz in (-0.42, 0.42):
        T_beam(mk, part, (bx, by - 0.02, bz + dz), (tx, ty, tz + dz), 0.16)
    n = int((ty - by) / 1.0)
    for i in range(1, n + 1):
        t = i / (n + 0.6)
        x, y = bx + (tx - bx) * t, by + (ty - by) * t
        mk.box(part, (x, y, bz), (0.09, 0.09, 0.96), WOOD2)


# ---------------- caballete de la vía ----------------
def rail_trestle(mk):
    p = mk.part("RailTrestle", (0, 0, 0))
    RAILS.straight_track(mk, p, 0.0, OPEN_Z, -OPEN_Z, y0=LEDGE_Y)
    for s in (-1, 1):
        mk.box(p, (s * 1.0, LEDGE_Y - 0.29, 0), (0.5, 0.6, 25.0), WOOD)          # largueros bajo los durmientes
    for k, z in enumerate((-9.6, -4.8, 0.0, 4.8, 9.6)):
        mk.box(p, (0, LEDGE_Y - 0.8, z), (4.0, 0.45, 0.55), WOOD)                # sombrero
        for s in (-1, 1):
            mk.box(p, (s * 1.65, (LEDGE_Y - 1.0) / 2 - 0.02, z), (0.5, LEDGE_Y - 0.97, 0.5), WOOD)
        a, b = ((-1.65, 0.2), (1.65, LEDGE_Y - 1.1)) if k % 2 else ((1.65, 0.2), (-1.65, LEDGE_Y - 1.1))
        T_beam(mk, p, (a[0], a[1], z - 0.3), (b[0], b[1], z - 0.3), 0.2)


# ---------------- columnas de cuadros ----------------
def ceiling_at(x, z):
    """Altura del techo de la cámara sobre (x, z): rayo hacia arriba contra el casco del cortador."""
    bm = bmesh.new()
    bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in chamber_pts()], use_existing_faces=False)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    loc, _, _, _ = bvh.ray_cast(Vector((x, 1.0, z)), Vector((0, 1, 0)))
    return loc.y


def pillars(mk):
    p = mk.part("Pillars", (0, 0, 0))
    t, ln, off = 1.0, 4.2, 1.5
    for x, z in PILLARS:
        roof = min(ceiling_at(x + dx, z + dz) for dx in (-2.2, 2.2) for dz in (-2.2, 2.2))
        n = int((roof - 0.25) / (t - 0.004))
        for k in range(n):
            y = k * (t - 0.004) + t / 2 - 0.02
            mat = WOOD if k % 2 else WOOD2
            for s in (-1, 1):
                if k % 2:
                    mk.box(p, (x, y, z + s * off), (ln, t, t), mat)
                else:
                    mk.box(p, (x + s * off, y, z), (t, t, ln), mat)
        top = n * (t - 0.004) - 0.02
        # almohada y cuñas hasta la roca (se meten en el techo)
        mk.box(p, (x, top + 0.2, z), (4.4, 0.44, 4.4), WOOD)
        for dx in (-1.2, 1.2):
            mk.box(p, (x + dx, (top + 0.4 + roof + 0.6) / 2, z), (0.9, roof + 0.6 - top - 0.4, 3.6), WOOD2)


def build(mk):
    shell(mk)
    scaffolding(mk)
    rail_trestle(mk)
    pillars(mk)

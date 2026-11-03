"""
Receta de WST_Mine_Tunnel, los túneles modulares de la mina (prompt 098, Bloques A + B).

Brief
- Lo que se lee adentro (los jugadores están en el túnel): la línea de puntales oscuros cada 4 studs
  contra la roca más clara, el piso de tierra ocre con la vía al medio y una roca facetada que no es un
  caño perfecto (cada tramo de 4 tiene su propio perfil, con piedras salientes).
- Grilla: sección interior de 8 x 8 al centro, módulos de 16 de largo (z de -8 a +8), origen en el piso
  al centro. El perfil de las puntas es el mismo en todos los módulos y es simétrico: así calzan aunque
  uno esté girado 180° (y la curva sirve para los dos lados).
- Perfil de las puntas (PC, 12 vértices): piso de 7,6, ancho máximo 8 a y = 2, hombros a 6,4, techo
  chato de 1,9 a y = 8. Adentro, cada estación (z = ±4 y 0) mueve sus vértices hasta 0,45 hacia afuera
  o adentro: facetas irregulares. Cáscara de roca de 1,5 (el contorno de afuera es PC corrido 1,5).
- Construcción: un prisma macizo del contorno de afuera tallado por cortadores convexos (un casco por
  tramo entre dos estaciones, con PC recto más allá de las puntas): las paredes salen cerradas y del
  color del cortador; manchas de redrock_dark y ocre pintadas, piso ochre pintado.
- Puntales cada 4 (z = ±2, ±6): dos postes inclinados apoyados contra la pared, sombrero de 0,6 a
  y 6,6-7,2 metido en la roca, y dos tacos hasta el techo. Paso libre: 6,6 bajo el sombrero (jugador
  parado en la vagoneta: 6,42) y 5,6 de ancho arriba.
- Vía al medio (WST_Mine_Rails: trocha 3,0, cara del riel a y = 0,5, durmientes cada 1,143 con medio
  paso en las puntas): continúa exacto en el módulo vecino.
- Piezas (un objeto por módulo, en fila sobre X):
  Tunnel_Straight; Tunnel_Curve90 (dobla a la derecha, eje de radio 16 = pared de adentro a radio 12;
  entra por z = +8 como la recta y sale en x = +16, z = -8 hacia +X); Tunnel_T (ramal a +X que termina en
  x = +8, para un módulo centrado en x = 16); Tunnel_Narrow (puntas normales, el medio angosto de 6 x 7:
  se puede intercalar en cualquier lado); Tunnel_End (derrumbe que cierra el túnel a z = -4,5).
- Inferido: el perfil exacto y su simetría, la Narrow como estrechamiento con puntas normales, la T sin
  vía en el ramal, el radio 12 como pared de adentro (eje 16), los tacos sobre el sombrero, el derrumbe
  del End con un puntal quebrado, los colores de los parches.

Vueltas: 1) la recta salió con 360 triángulos y piedras flotando: la booleana se rompía con los pisos
de los cortadores coplanares en y = 0 donde se enciman. Ahora el piso es una losa ochre aparte (detalle) y
los cortadores bajan a -0,30/-0,32 alternados · 2) z-fighting de la cara de la punta de la losa con el
anillo de roca: la losa termina 0,004 antes · 3) la vía no aparecía (el cortador la tallaba: ahora es
detalle); los tacos sobre el sombrero se leían como antenas: entablado de tres tablas; las piedras
icosaedro se leían como gemas: lajas angulosas (caja con esquinas metidas al azar) · 4) la tabla
colgando del End se leía como un pilar: corrida al costado e inclinada.

Revisión
- Triángulos contra 1200 por módulo: Straight 1090, Narrow 904, End 952, T 1426 (es módulo y medio: ramal
  con su puntal, cabezal y entablado), Curve90 2182 (25,1 de largo = 1,57 módulos: 22 durmientes, 6
  puntales y 7 tramos de entablado; la cáscara tallada son ~1000). Por pieza, lejos de 10 000.
- Medidas: sección de 8 x 8 en las puntas (ancho 8,0 a y = 2, alto 8,0 al centro); cáscara de 1,5 por
  debajo del piso (el punto más bajo, -1,51, es la roca debajo de la losa: a propósito).
- Paso libre: 6,6 bajo los sombreros, 5,6 de ancho entre postes arriba; la vagoneta (3,67 de ancho) con
  un jugador parado adentro llega a 6,42. En el medio de la Narrow, 5,5 bajo los sombreros y ~5,7 de ancho.
- Avisos: un borde suelto que deja la booleana en Curve90 (0,27, en la cara de la salida) y en End
  (0,001): no tienen caras y no se exportan.
- Dudoso (Valentin): cada módulo es un solo objeto, como los nombra el prompt; con colisión de casco
  convexo el túnel quedaría macizo. En Studio necesitan CollisionFidelity = PreciseConvexDecomposition
  (o colisionadores invisibles).
"""

import importlib.util
import math
from pathlib import Path

from mathutils import Euler, Vector

_spec = importlib.util.spec_from_file_location(
    "mine_rails", Path(__file__).resolve().parents[2] / "WST_Mine_Rails" / "01_design" / "WST_Mine_Rails.build.py")
RAILS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RAILS)

HALF_L = 8.0                                     # medio largo del módulo
SHELL = 1.5
CAP_Y0, CAP_Y1 = 6.6, 7.2                        # sombrero de los puntales
NAR_CAP = 5.5                                    # en el medio de la Narrow (techo a 7)
TIMBER = 0.6
SETS = (6.0, 2.0, -2.0, -6.0)
R_CURVE = 16.0                                   # eje de la curva (pared de adentro a 12)
ROCK, ROCK2, DIRT, WOOD = "stone_grey", "redrock_dark", "ochre", "wood_dark"

_HALF = [(3.8, 0.0), (4.0, 2.0), (3.85, 4.6), (3.5, 6.4), (2.6, 7.5), (0.95, 8.0)]
PC = _HALF + [(-x, y) for x, y in reversed(_HALF)]     # antihorario: sube por la derecha, baja por la izquierda


# ---------------- perfiles ----------------
def _normal(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return dy / n, -dx / n


def offset(poly, d):
    """Contorno corrido d hacia afuera (polígono convexo antihorario, esquinas a inglete)."""
    out = []
    n = len(poly)
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        n1, n2 = _normal(p0, p1), _normal(p1, p2)
        k = d / (1 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((p1[0] + (n1[0] + n2[0]) * k, p1[1] + (n1[1] + n2[1]) * k))
    return out


OUTER = offset(PC, SHELL)


def jitter(prof, amounts, keep_floor=True):
    """Mueve cada vértice sobre su normal (positivo = afuera). El piso queda en y = 0."""
    n = len(prof)
    out = []
    for i, p in enumerate(prof):
        n1, n2 = _normal(prof[i - 1], p), _normal(p, prof[(i + 1) % n])
        nx, ny = n1[0] + n2[0], n1[1] + n2[1]
        ln = math.hypot(nx, ny)
        a = amounts[i % len(amounts)]
        q = (p[0] + nx / ln * a, p[1] + ny / ln * a)
        if keep_floor and abs(p[1]) < 1e-6:
            q = (p[0] + (a * 0.5 if p[0] > 0 else -a * 0.5), 0.0)
        out.append(q)
    return out


def scaled(prof, sx, sy):
    return [(x * sx, y * sy) for x, y in prof]


def lerp_prof(a, b, t):
    return [(pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t) for pa, pb in zip(a, b)]


def wall_x(prof, y, side):
    best = None
    n = len(prof)
    for i in range(n):
        (x0, y0), (x1, y1) = prof[i], prof[(i + 1) % n]
        if (y0 - y) * (y1 - y) <= 0 and abs(y1 - y0) > 1e-9:
            x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            if x * side > 0 and (best is None or x * side > best * side):
                best = x
    return best


def roof_y(prof, x):
    best = None
    n = len(prof)
    for i in range(n):
        (x0, y0), (x1, y1) = prof[i], prof[(i + 1) % n]
        if (x0 - x) * (x1 - x) <= 0 and abs(x1 - x0) > 1e-9:
            y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            if best is None or y > best:
                best = y
    return best


# jitter fijo por estación (12 vértices: piso der, ..., techo, ..., piso izq)
J = {
    "a": [0.15, 0.35, -0.2, 0.4, 0.1, -0.15, 0.3, 0.45, -0.1, 0.25, 0.3, -0.1],
    "b": [-0.1, -0.15, 0.4, 0.1, 0.45, 0.2, -0.1, 0.15, 0.4, -0.2, 0.1, 0.2],
    "c": [0.2, 0.3, 0.1, -0.15, 0.25, 0.4, 0.3, -0.15, 0.2, 0.45, -0.15, 0.0],
    "d": [0.05, 0.4, 0.25, 0.35, -0.1, 0.1, 0.45, 0.2, 0.05, 0.1, 0.4, 0.15],
    "e": [0.1, -0.1, 0.35, 0.2, 0.3, -0.1, 0.1, 0.4, 0.3, 0.2, -0.05, 0.1],
}


# ---------------- marcos (dónde cae un punto del perfil en el mundo) ----------------
class Frame:
    def __init__(self, origin, right, fwd):
        self.o, self.r, self.f = origin, right, fwd

    def at(self, x, y, u=0.0):
        o, r, f = self.o, self.r, self.f
        return (o[0] + r[0] * x + f[0] * u, o[1] + y, o[2] + r[2] * x + f[2] * u)


def straight_frame(ox, z):
    return Frame((ox, 0.0, z), (1.0, 0.0, 0.0), (0.0, 0.0, -1.0))


def curve_frame(ox, deg):
    t = math.radians(deg)
    return Frame((ox + R_CURVE - R_CURVE * math.cos(t), 0.0, HALF_L - R_CURVE * math.sin(t)),
                 (math.cos(t), 0.0, math.sin(t)), (math.sin(t), 0.0, -math.cos(t)))


def branch_frame(ox, x):
    """Ramal de la T: avanza hacia +X; su derecha es +Z."""
    return Frame((ox + x, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))


def section(frame, prof, u=0.0):
    return [frame.at(x, y, u) for x, y in prof]


# ---------------- cáscara ----------------
FLOOR_CUT = -0.3                                 # los cortadores bajan hasta acá; el piso es una losa aparte


def sunk(prof, y):
    return [(x, y if abs(v) < 1e-6 else v) for x, v in prof]


def carve_run(mk, part, frames, profs, mats, ext=0.05):
    """Cortadores convexos entre estaciones consecutivas, estirados `ext` en las juntas internas. Bajan
    por debajo del piso (losa aparte) y alternan 0,02 de profundidad: dos cortadores nunca dejan caras
    coplanares donde se enciman (con el piso en y = 0 la booleana se rompía: medido)."""
    for i in range(len(frames) - 1):
        fl = FLOOR_CUT - 0.02 * (i % 2)
        a = section(frames[i], sunk(profs[i], fl), -ext if i > 0 else 0.0)
        b = section(frames[i + 1], sunk(profs[i + 1], fl), ext if i + 1 < len(frames) - 1 else 0.0)
        mk.carve(part, mats[i % len(mats)], points=a + b)


def prism_shell_z(mk, part, ox, z0, z1, prof=OUTER, mat=ROCK2):
    mk.prism(part, prof, z0 - z1, mat, plane="xy", center=(ox, 0, (z0 + z1) / 2))


# ---------------- puntales ----------------
def timber_set(mk, part, frame, prof, k=0, posts=(-1, 1), cap=True, cap_y0=CAP_Y0):
    """Dos postes contra la pared y el sombrero metido en la roca."""
    t = TIMBER / 2
    cap_y1 = cap_y0 + TIMBER
    lean = (0.02, -0.03, 0.04, -0.02)[k % 4]
    for side in posts:
        xb = wall_x(prof, 0.6, side) - side * (t - 0.06)
        xt = wall_x(prof, cap_y0, side) - side * (t - 0.06)
        pts = []
        for x, y in ((xb, -0.05), (xt, cap_y0 + 0.05)):
            for dx in (-t, t):
                for du in (-t, t):
                    pts.append(frame.at(x + dx, y, du + (lean if y > 1 else 0.0)))
        mk.hull(part, pts, WOOD, detail=True)
    if cap:
        xl = wall_x(prof, cap_y0, -1) - 0.15                 # las puntas del sombrero, metidas en la roca
        xr = wall_x(prof, cap_y0, 1) + 0.15
        pts = [frame.at(x, y, du) for x in (xl, xr) for y in (cap_y0, cap_y1) for du in (-t - 0.02, t + 0.02)]
        mk.hull(part, pts, WOOD, detail=True)


LAG_X = (-1.55, 0.0, 1.55)                       # entablado sobre los sombreros
LAG_W, LAG_T = 0.85, 0.13


def lagging(mk, part, stations, xs=LAG_X):
    """Tablas a lo largo del túnel apoyadas en los sombreros. stations: [(frame, y_arriba_del_sombrero)].
    Cada tramo entre estaciones es un casco; los tramos vecinos se enciman 0,15 con alturas alternadas."""
    for i in range(len(stations) - 1):
        (fa, ya), (fb, yb) = stations[i], stations[i + 1]
        d0 = 0.01 + 0.012 * (i % 2)
        ea = -0.15 if i > 0 else 0.0
        eb = 0.15 if i + 1 < len(stations) - 1 else 0.0
        for j, x in enumerate(xs):
            t = LAG_T + 0.015 * ((i + j) % 2)
            w = LAG_W * (0.92 + 0.08 * ((i + 2 * j) % 3) / 2)
            pts = []
            for fr, y, u in ((fa, ya, ea), (fb, yb, eb)):
                for dx in (-w / 2, w / 2):
                    for yy in (y - d0, y - d0 + t):
                        pts.append(fr.at(x + dx, yy, u))
            mk.hull(part, pts, WOOD, detail=True)


# ---------------- piedras ----------------
class Rng:
    """Pseudoazar fijo (la receta da siempre lo mismo)."""

    def __init__(self, seed):
        self.s = (seed * 7919 + 104729) % 2147483648

    def u(self):
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return self.s / 2147483648


def chunk_pts(c, size, seed, rot=(0, 0, 0)):
    """Laja de roca angulosa: las 8 esquinas de una caja metidas al azar y tres caras abultadas."""
    r = Rng(seed)
    sx, sy, sz = (v / 2 for v in size)
    pts = []
    for ix in (-1, 1):
        for iy in (-1, 1):
            for iz in (-1, 1):
                pts.append(Vector((ix * sx * (0.62 + 0.38 * r.u()), iy * sy * (0.62 + 0.38 * r.u()),
                                   iz * sz * (0.62 + 0.38 * r.u()))))
    for _ in range(3):
        axis = int(r.u() * 3) % 3
        p = Vector(((r.u() - 0.5) * sx, (r.u() - 0.5) * sy, (r.u() - 0.5) * sz))
        p[axis] = (1 if r.u() > 0.5 else -1) * (sx, sy, sz)[axis] * (1.0 + 0.12 * r.u())
        pts.append(p)
    m = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    cv = Vector(c)
    return [tuple(cv + m @ p) for p in pts]


def chunk(mk, part, c, size, seed, rot=(0, 0, 0), mat=ROCK, detail=True):
    mk.hull(part, chunk_pts(c, size, seed, rot), mat, detail=detail)


def wall_rocks(mk, part, frame_at, prof_at, specs):
    """specs: (u, side, y, r, out, mat) -> piedra apoyada en la pared a la altura y, que sale `out`."""
    for i, (u, side, y, r, out, mat) in enumerate(specs):
        prof = prof_at(u)
        x = wall_x(prof, max(y, 0.3), side) - side * (out - r * 0.55)
        fr = frame_at(u)
        rot = ((17 * i) % 40 - 20, (29 * i) % 60, (11 * i) % 30 - 15)
        chunk(mk, part, fr.at(x, y, 0.0), (1.5 * r, (1.5 + 0.2 * (i % 3)) * r, 2.4 * r), 31 * i + int(u * 7), rot=rot, mat=mat)


def paint_patches(mk, part, spots):
    for c, r, mat in spots:
        mk.paint(part, mat, ball=(c, r))


FLOOR_HALF = 4.3                                 # la losa del piso entra 0,3-0,5 en las paredes


def floor_slab(mk, part, poly):
    """Piso de tierra apisonada: losa (x, z) de y = FLOOR_CUT a 0, metida en las paredes."""
    mk.prism(part, poly, -FLOOR_CUT + 0.01, DIRT, plane="xz", center=(0, (FLOOR_CUT - 0.01) / 2, 0), detail=True)


def rect_xz(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


SEAM = 0.004                                     # la losa termina apenas antes de la punta (si no, coplanar con la cara del anillo)


# ---------------- módulos ----------------
def stations_z(profs):
    """Estaciones de un módulo recto: PC más allá de las puntas, PC en ±6 y las del medio."""
    zs = [HALF_L + 0.5, 6.0] + [z for z, _ in profs] + [-6.0, -HALF_L - 0.5]
    ps = [PC, PC] + [p for _, p in profs] + [PC, PC]
    return zs, ps


def prof_at_z(zs, ps, z):
    for i in range(len(zs) - 1):
        if zs[i] >= z >= zs[i + 1]:
            return lerp_prof(ps[i], ps[i + 1], (zs[i] - z) / (zs[i] - zs[i + 1]))
    return PC


def tunnel_straight(mk, ox):
    p = mk.part("Tunnel_Straight", (ox, 0, 0))
    prism_shell_z(mk, p, ox, HALF_L, -HALF_L)
    zs, ps = stations_z([(4.0, jitter(PC, J["a"])), (0.0, jitter(PC, J["b"])), (-4.0, jitter(PC, J["c"]))])
    carve_run(mk, p, [straight_frame(ox, z) for z in zs], ps, [ROCK, ROCK, ROCK2, ROCK, ROCK, ROCK])
    floor_slab(mk, p, rect_xz(ox - FLOOR_HALF, ox + FLOOR_HALF, -HALF_L + SEAM, HALF_L - SEAM))
    paint_patches(mk, p, [((ox - 4.2, 3.0, 3.0), 2.2, ROCK2), ((ox + 4.0, 5.0, -3.5), 2.4, DIRT),
                          ((ox + 1.0, 8.2, 1.0), 2.0, ROCK2), ((ox - 3.6, 6.0, -5.0), 1.8, DIRT),
                          ((ox + 4.1, 1.5, 5.0), 1.8, ROCK2)])
    for k, z in enumerate(SETS):
        timber_set(mk, p, straight_frame(ox, z), prof_at_z(zs, ps, z), k)
    lagging(mk, p, [(straight_frame(ox, HALF_L - SEAM), CAP_Y1), (straight_frame(ox, -HALF_L + SEAM), CAP_Y1)])
    RAILS.straight_track(mk, p, ox, HALF_L, -HALF_L, detail=True)
    wall_rocks(mk, p, lambda u: straight_frame(ox, u), lambda u: prof_at_z(zs, ps, u),
               [(4.0, -1, 0.35, 0.55, 0.35, ROCK), (3.4, -1, 0.3, 0.38, 0.3, ROCK2), (-0.3, 1, 0.3, 0.5, 0.35, ROCK),
                (-4.2, 1, 4.6, 0.7, 0.35, ROCK2), (0.2, -1, 5.0, 0.8, 0.4, ROCK), (-4.0, -1, 0.3, 0.45, 0.3, ROCK)])


def tunnel_narrow(mk, ox):
    p = mk.part("Tunnel_Narrow", (ox, 0, 0))
    prism_shell_z(mk, p, ox, HALF_L, -HALF_L)
    nar = scaled(PC, 0.75, 0.875)
    zs, ps = stations_z([(3.5, jitter(nar, J["d"])), (0.0, jitter(nar, J["e"])), (-3.5, jitter(nar, J["a"]))])
    carve_run(mk, p, [straight_frame(ox, z) for z in zs], ps, [ROCK, ROCK2, ROCK, ROCK2, ROCK, ROCK])
    floor_slab(mk, p, rect_xz(ox - FLOOR_HALF, ox + FLOOR_HALF, -HALF_L + SEAM, HALF_L - SEAM))
    paint_patches(mk, p, [((ox - 3.2, 4.0, 0.0), 2.0, DIRT), ((ox + 3.0, 2.0, -2.0), 1.8, ROCK2)])
    for k, z in enumerate(SETS):
        timber_set(mk, p, straight_frame(ox, z), prof_at_z(zs, ps, z), k, cap_y0=CAP_Y0 if abs(z) > 4 else NAR_CAP)
    # entablado: en las puntas (sigue el del módulo vecino) y sobre los dos puntales bajos del medio
    for z0, z1, y in ((HALF_L - SEAM, 5.7, CAP_Y1), (-5.7, -HALF_L + SEAM, CAP_Y1), (2.7, -2.7, NAR_CAP + TIMBER)):
        lagging(mk, p, [(straight_frame(ox, z0), y), (straight_frame(ox, z1), y)], xs=LAG_X if y > 7 else (-0.95, 0.95))
    wall_rocks(mk, p, lambda u: straight_frame(ox, u), lambda u: prof_at_z(zs, ps, u),
               [(1.0, -1, 0.35, 0.6, 0.45, ROCK), (0.3, -1, 0.6, 0.45, 0.4, ROCK2), (-1.2, 1, 0.4, 0.55, 0.45, ROCK),
                (3.6, 1, 0.3, 0.5, 0.35, ROCK2), (-3.8, -1, 0.3, 0.5, 0.3, ROCK), (0.0, 1, 4.3, 0.75, 0.4, ROCK2),
                (-0.5, -1, 5.0, 0.6, 0.35, ROCK)])


def tunnel_end(mk, ox):
    p = mk.part("Tunnel_End", (ox, 0, 0))
    prism_shell_z(mk, p, ox, HALF_L, -HALF_L)
    zs = [HALF_L + 0.5, 6.0, 2.0, -1.5, -4.5]
    ps = [PC, PC, jitter(PC, J["c"]), jitter(scaled(PC, 0.95, 0.95), J["b"]), jitter(scaled(PC, 0.8, 0.85), J["e"])]
    carve_run(mk, p, [straight_frame(ox, z) for z in zs], ps, [ROCK, ROCK, ROCK2, ROCK])
    floor_slab(mk, p, rect_xz(ox - FLOOR_HALF, ox + FLOOR_HALF, -4.6, HALF_L - SEAM))
    paint_patches(mk, p, [((ox + 4.0, 4.0, 4.0), 2.0, ROCK2), ((ox - 3.0, 7.5, 1.0), 2.0, DIRT)])
    timber_set(mk, p, straight_frame(ox, 6.0), PC, 0)
    lagging(mk, p, [(straight_frame(ox, HALF_L - SEAM), CAP_Y1), (straight_frame(ox, 4.6), CAP_Y1)])
    mk.hull(p, [(ox + x + 0.35 * (y - 7.1), y, z) for x in (1.13, 1.97) for y, z in ((7.06, 5.5), (7.2, 5.56), (5.3, 3.7), (5.44, 3.76))],
            WOOD, detail=True)                                                                        # tabla colgando
    # puntal de z = 2 quebrado: queda el poste derecho; el izquierdo partido y el sombrero caído sobre el derrumbe
    pr = prof_at_z(zs, ps, 2.0)
    timber_set(mk, p, straight_frame(ox, 2.0), pr, 1, posts=(1,), cap=False)
    xl = wall_x(pr, 0.6, -1) + 0.24
    mk.hull(p, [(ox + xl + dx, y, 2.0 + dz) for dx in (-0.3, 0.3) for dz in (-0.3, 0.3) for y in (-0.05, 1.6)]
            + [(ox + xl + 0.1, 2.15, 2.1)], WOOD, detail=True)                                       # muñón astillado
    mk.hull(p, [(ox + x, y, z) for x, y, z in ((2.9, 6.55, 2.2), (2.9, 7.15, 2.2), (2.9, 6.55, 1.6), (2.9, 7.15, 1.6),
                                               (-2.2, 2.05, 0.1), (-2.2, 2.65, 0.1), (-2.0, 2.05, -0.5), (-2.0, 2.65, -0.5))],
            WOOD, detail=True)                                                                        # sombrero caído
    # vía que entra al derrumbe
    RAILS.straight_track(mk, p, ox, HALF_L, -1.15, detail=True)
    # derrumbe: piedras grandes hasta el techo, más chicas adelante (en pendiente hacia el jugador)
    pile = [((-2.4, 0.8, -2.0), 1.5, ROCK), ((0.3, 1.0, -2.6), 1.7, ROCK2), ((2.6, 0.9, -1.8), 1.4, ROCK),
            ((-1.2, 3.0, -3.2), 1.6, ROCK), ((1.6, 3.1, -3.4), 1.6, ROCK2), ((0.0, 5.2, -3.8), 1.7, ROCK),
            ((-2.4, 5.0, -4.0), 1.3, ROCK2), ((2.3, 5.4, -4.0), 1.3, ROCK), ((0.4, 6.6, -4.4), 1.2, ROCK2),
            ((-1.0, 0.5, 0.3), 0.85, ROCK), ((1.2, 0.45, 0.6), 0.75, ROCK2), ((-2.9, 0.4, 0.9), 0.6, ROCK),
            ((2.9, 0.5, 0.2), 0.7, ROCK), ((0.2, 2.1, -1.0), 1.0, ROCK), ((-2.6, 2.6, -1.6), 0.9, ROCK2),
            ((2.4, 2.6, -1.2), 0.8, ROCK), ((-0.6, 0.35, 1.8), 0.45, ROCK2), ((1.8, 0.3, 2.6), 0.35, ROCK)]
    for i, (c, r, mat) in enumerate(pile):
        chunk(mk, p, (ox + c[0], c[1], c[2]), (2.3 * r, (1.4 + 0.2 * (i % 3)) * r, 2.0 * r), 11 * i + 3,
              rot=((23 * i) % 50 - 25, (37 * i) % 90, (13 * i) % 40 - 20), mat=mat)


def tunnel_t(mk, ox):
    p = mk.part("Tunnel_T", (ox, 0, 0))
    prism_shell_z(mk, p, ox, HALF_L, -HALF_L)
    # ramal: prisma del contorno de afuera hacia +X, con piso y techo 0,01 adentro (no coplanares con los del túnel)
    outer_b = [(x, y + 0.01) if y < -1.0 else ((x, y - 0.01) if y > 9.0 else (x, y)) for x, y in OUTER]
    mk.prism(p, outer_b, HALF_L, ROCK2, plane="zy", center=(ox + HALF_L / 2, 0, 0))
    zs, ps = stations_z([(4.0, jitter(PC, J["d"])), (0.0, jitter(PC, J["e"])), (-4.0, jitter(PC, J["a"]))])
    carve_run(mk, p, [straight_frame(ox, z) for z in zs], ps, [ROCK, ROCK, ROCK2, ROCK, ROCK, ROCK])
    bf = [branch_frame(ox, x) for x in (0.0, 4.0, 6.0, HALF_L + 0.5)]
    carve_run(mk, p, bf, [PC, jitter(PC, J["b"]), PC, PC], [ROCK2, ROCK, ROCK])
    fh = FLOOR_HALF
    e = HALF_L - SEAM
    floor_slab(mk, p, [(ox - fh, -e), (ox + fh, -e), (ox + fh, -fh), (ox + e, -fh), (ox + e, fh),
                       (ox + fh, fh), (ox + fh, e), (ox - fh, e)])
    paint_patches(mk, p, [((ox - 4.2, 3.0, -2.0), 2.2, ROCK2), ((ox - 3.6, 6.2, 4.0), 1.8, DIRT),
                          ((ox + 6.0, 6.0, 4.2), 2.0, ROCK2)])
    for k, z in enumerate((6.0, -6.0)):
        timber_set(mk, p, straight_frame(ox, z), PC, k)
    # cabezal sobre la boca del ramal: dos postes en sus esquinas y una viga a lo largo de Z
    hx = 3.55
    for zc in (-4.45, 4.45):
        pr = prof_at_z(zs, ps, zc)
        x = wall_x(pr, 3.0, 1) - 0.24
        mk.hull(p, [(ox + x + dx, y, zc + dz) for dx in (-0.3, 0.3) for dz in (-0.3, 0.3) for y in (-0.05, CAP_Y0 + 0.05)],
                WOOD, detail=True)
    mk.hull(p, [(ox + hx + dx, y, z) for dx in (-0.32, 0.32) for y in (CAP_Y0, CAP_Y1) for z in (-5.0, 5.0)], WOOD, detail=True)
    # del lado izquierdo, puntales con el sombrero que apoya en el cabezal
    for k, zc in enumerate((2.0, -2.0)):
        pr = prof_at_z(zs, ps, zc)
        fr = straight_frame(ox, zc)
        timber_set(mk, p, fr, pr, k + 2, posts=(-1,), cap=False)
        xl = wall_x(pr, CAP_Y1, -1) - 0.25
        mk.hull(p, [fr.at(x, y, du) for x in (xl, hx + 0.1) for y in (CAP_Y0 + 0.02, CAP_Y1 + 0.02) for du in (-0.32, 0.32)],
                WOOD, detail=True)
    timber_set(mk, p, branch_frame(ox, 6.0), PC, 1)
    lagging(mk, p, [(straight_frame(ox, HALF_L - SEAM), CAP_Y1), (straight_frame(ox, -HALF_L + SEAM), CAP_Y1)])
    lagging(mk, p, [(branch_frame(ox, 4.4), CAP_Y1), (branch_frame(ox, HALF_L - SEAM), CAP_Y1)])
    RAILS.straight_track(mk, p, ox, HALF_L, -HALF_L, detail=True)
    wall_rocks(mk, p, lambda u: straight_frame(ox, u), lambda u: prof_at_z(zs, ps, u),
               [(4.0, -1, 0.35, 0.55, 0.35, ROCK), (-0.5, -1, 0.3, 0.45, 0.3, ROCK2), (0.6, -1, 4.8, 0.8, 0.4, ROCK),
                (-6.8, 1, 0.3, 0.45, 0.3, ROCK2)])


def tunnel_curve(mk, ox):
    p = mk.part("Tunnel_Curve90", (ox, 0, 0))
    angs = [0, 15, 30, 45, 60, 75, 90]
    # cáscara: tres cascos del contorno de afuera (30° cada uno), encimados 0,3°; el del medio con el piso
    # 0,01 más abajo (no coplanares donde se enciman)
    shell_angs = [0, 30, 60, 90]
    for i in range(len(shell_angs) - 1):
        a0 = shell_angs[i] - (0.3 if i > 0 else 0)
        a1 = shell_angs[i + 1] + (0.3 if i + 1 < len(shell_angs) - 1 else 0)
        prof = [(x, y - 0.01) if (y < -1.0 and i % 2) else (x, y) for x, y in OUTER]
        mk.hull(p, section(curve_frame(ox, a0), prof) + section(curve_frame(ox, a1), prof), ROCK2)
    profs = [PC, jitter(PC, J["a"]), jitter(PC, J["c"]), jitter(PC, J["b"]), jitter(PC, J["d"]), jitter(PC, J["e"]), PC]
    carve_run(mk, p, [curve_frame(ox, a) for a in angs], profs, [ROCK, ROCK2, ROCK, ROCK, ROCK2, ROCK])
    # PC recto más allá de cada punta
    f0, f1 = curve_frame(ox, 0), curve_frame(ox, 90)
    mk.carve(p, ROCK, points=section(f0, sunk(PC, FLOOR_CUT - 0.04), -0.6) + section(f0, sunk(PC, FLOOR_CUT - 0.04), 0.3))
    mk.carve(p, ROCK, points=section(f1, sunk(PC, FLOOR_CUT - 0.04), -0.3) + section(f1, sunk(PC, FLOOR_CUT - 0.04), 0.6))
    c = (ox + R_CURVE, HALF_L)
    da = math.degrees(SEAM / R_CURVE)
    floor_slab(mk, p, RAILS.arc_band(c, R_CURVE, 2 * FLOOR_HALF, da, 90.0 - da, 12, +1))

    def prof_at(a):
        for i in range(len(angs) - 1):
            if angs[i] <= a <= angs[i + 1]:
                return lerp_prof(profs[i], profs[i + 1], (a - angs[i]) / (angs[i + 1] - angs[i]))
        return PC

    set_angs = (7.5, 22.5, 37.5, 52.5, 67.5, 82.5)
    for k, a in enumerate(set_angs):
        timber_set(mk, p, curve_frame(ox, a), prof_at(a), k)
    ends = math.degrees(SEAM / R_CURVE)
    lagging(mk, p, [(curve_frame(ox, a), CAP_Y1) for a in (ends,) + set_angs + (90 - ends,)])
    RAILS.curve_track(mk, p, c, R_CURVE, 0.0, 90.0, +1, detail=True)
    paint_patches(mk, p, [(curve_frame(ox, 30).at(-4.3, 3.0), 2.4, ROCK2), (curve_frame(ox, 60).at(4.2, 5.0), 2.2, DIRT),
                          (curve_frame(ox, 45).at(0.5, 8.3), 2.2, ROCK2), (curve_frame(ox, 80).at(-4.0, 2.0), 1.8, DIRT)])
    wall_rocks(mk, p, lambda u: curve_frame(ox, u), prof_at,
               [(15.0, -1, 0.35, 0.6, 0.35, ROCK), (30.0, 1, 0.3, 0.5, 0.35, ROCK2), (45.0, -1, 4.8, 0.85, 0.4, ROCK),
                (60.0, -1, 0.3, 0.45, 0.3, ROCK2), (75.0, 1, 4.6, 0.7, 0.35, ROCK)])


def build(mk):
    tunnel_straight(mk, 0.0)
    tunnel_t(mk, 14.0)
    tunnel_narrow(mk, 34.0)
    tunnel_end(mk, 48.0)
    tunnel_curve(mk, 62.0)

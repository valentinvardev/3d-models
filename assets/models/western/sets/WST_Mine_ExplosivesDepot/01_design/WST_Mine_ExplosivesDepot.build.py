"""
Receta de WST_Mine_ExplosivesDepot, el polvorín tallado en la roca (prompt 105, Bloques A + C). En la pelea
del Capataz, al 50 % se enciende la mecha: hay que apagarla o escapar.

Brief
- Lo que se lee a 40 studs: un nicho oscuro en un bloque de roca, con marco de vigas, dos hojas de puerta
  de tablas abiertas hacia afuera, adentro una pila de cajones claros con franja roja y tres barriles, un
  cartel de peligro con borde rojo al costado y la mecha clara que sale por el piso y trepa la roca.
- Medidas (origen en el piso al centro de la boca; la cara de la roca en z ≈ 0, el nicho hacia +Z):
  bloque de roca ~13,5 x 9,8 x 8,5 en tres columnas (como el paredón de WST_Mine_Entrance); nicho de 8 x 7 x 6 (x ±4, y 0-7, z 0-6); marco de vigas de 0,6 (postes en
  x = ±3,7, cabezal a y 6,4-7,0) y un segundo marco al fondo (z = 5,4). Puertas: dos hojas de 3,4 x 6,4 x
  0,3, de tablones verticales con juntas pintadas, travesaños, riostra en Z y bisagras de hierro; abiertas
  105° (izquierda) y 80° (derecha). Cajones de 2,4 x 1,4 x 1,6 (como WST_Prop_DynamiteCrate): cuerpo
  wood_light, franja warning_red, tapa wood_mid; uno destapado con seis cartuchos. Barriles de pólvora de
  1,5 de alto con zunchos de hierro y franja roja. Cartel de 2,2 x 1,5 con borde rojo y tablero en blanco.
- Fragmentos (8, origen común): frag01-frag03 pares de cajones apilados, frag04 un cajón cruzado arriba de
  la pila, frag05 un cajón suelto adelante (el destapado), frag06-frag08 los tres barriles (uno acostado).
  fixed_Alcove: la roca tallada, los dos marcos y el cartel (queda en pie). DoorL y DoorR con el origen en
  la bisagra. Fuse: mecha de 0,06 que sale del cajón destapado, cruza la puerta por el piso y trepa la
  roca a la izquierda (≈20 de largo, esquinas redondeadas), con _FuseEnd en la pila y _FuseStart en la otra
  punta.
- Inferido: las puertas abiertas (si no, no se ve la carga ni se llega a la mecha), el reparto de los 8
  fragmentos, el segundo marco, el recorrido de la mecha, el lado del cartel, el bloque de roca alrededor.

Vueltas: 1) las puertas se abrían hacia adentro (signo del giro), los cajones de arriba flotaban 0,185
(la tapa tenía 0,22 y no 0,4), los cartuchos coplanares con el relleno, la mecha de 516 triángulos ·
2) barriles de 8 lados; un barril quedó suelto al achicarse (se acercó); la mecha cruzaba la hoja abierta de
la puerta izquierda: la rodea por adelante · 3) el bloque de roca se leía como una casita: tres columnas
abombadas; la mecha se apoya en la roca después de redondear las esquinas (se metía en la roca).

Revisión
- 1712 triángulos contra 1500 (+14 %): cajones 360 (8, uno destapado con seis cartuchos), barriles 420,
  mecha 252 (es lo que hay que seguir y apagar), puertas 288, roca y marcos 182 + cartel.
- Medidas: 13,5 x 9,8 x 12,4 con las puertas abiertas; nicho de 8 x 7 x 6. Fragmentos (medidos): pares de
  cajones 22 % cada uno, cajón de arriba 11 %, cajón destapado 12 %, barriles 3,7 % cada uno; el lado más
  chico, 1,33.
- La mecha mide ≈20 (≈13 por el piso y ≈7 trepando la roca a la izquierda); _FuseEnd adentro del cajón
  destapado, _FuseStart a y ≈ 5,9 sobre la roca.
- 8 materiales en el modelo (cada objeto, hasta 5): la carga necesita el rojo de peligro y la soga clara.
- Dudoso: el nicho no tiene piso propio (es el de la galería); la mecha y los fragmentos apoyan en y = 0.
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

ROCK, ROCK2 = "stone_grey", "redrock_dark"
WOOD, PLANK, CRATE = "wood_dark", "wood_mid", "wood_light"
RED, IRON, ROPE = "warning_red", "iron", "rope"
NW, NH, ND = 4.0, 7.0, 6.0                 # medio ancho, alto y hondo del nicho
POST_X = NW - 0.3
HEAD_Y = 6.4


def beam(mk, part, a, b, w, h, mat, detail=False):
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    ref = Vector((0, 1, 0)) if abs(u.y) < 0.9 else Vector((1, 0, 0))
    v = u.cross(ref).normalized()
    n = u.cross(v)
    pts = [tuple(q + v * sv + n * sn) for q in (a, b) for sv in (-w / 2, w / 2) for sn in (-h / 2, h / 2)]
    mk.hull(part, pts, mat, detail=detail)


# ---------------- roca, marcos y cartel ----------------
COLS = [(-6.8, -1.6, 7.6, 8.4, -0.7, 1), (-3.2, 3.4, 9.6, 9.2, -0.2, 2), (1.8, 6.6, 8.2, 6.9, -0.6, 3)]


def col_pts(x0, x1, h0, h1, zf, seed, base):
    """Columna de roca (como en WST_Mine_Entrance): frente que abomba y se recuesta, tope biselado."""
    r = T.Rng(seed)
    xm, hm = (x0 + x1) / 2, max(h0, h1)
    j = [r.u() for _ in range(10)]
    return [(x0, base, zf - 0.2 * j[0]), (x1, base, zf - 0.25 * j[1]),
            (x0 + 0.2, 0.45 * h0, zf - 0.5 - 0.3 * j[2]), (x1 - 0.2, 0.5 * h1, zf - 0.45 - 0.2 * j[3]),
            (x0 + 0.5, 0.85 * h0, zf + 0.4 * j[4]), (x1 - 0.5, 0.85 * h1, zf + 0.3 * j[5]),
            (x0 + 1.0, h0, zf + 1.6), (x1 - 1.0, h1, zf + 1.4), (xm + (j[6] - 0.5), hm + 0.4 * j[7], zf + 3.0),
            (x0, base, 8.4), (x1, base, 8.4 - 0.3 * j[8]), (x0 + 0.5, h0 - 1.2, 7.6), (x1 - 0.5, h1 - 1.0, 7.8)]


def alcove(mk):
    p = mk.part("fixed_Alcove", (0, 0, 0))
    pts = [col_pts(*c, base=0.006 * (i % 2)) for i, c in enumerate(COLS)]
    for hull in pts:
        mk.hull(p, hull, ROCK2)
    mk.carve(p, ROCK, points=[(sx * w, y, z) for sx in (-1, 1) for w, y in ((NW, -0.3), (NW - 0.15, NH))
                              for z in (-2.0, ND)])
    for c, rad in (((-5.5, 7.5, -0.6), 2.0), ((5.5, 2.0, -0.6), 1.8), ((0.0, 9.0, -0.3), 1.6)):
        mk.paint(p, ROCK, ball=(c, rad))
    # dos marcos: postes contra las paredes del nicho y cabezal contra el techo
    for z in (0.35, ND - 0.6):
        for sx in (-1, 1):
            mk.box(p, (sx * POST_X, (HEAD_Y + 0.02) / 2 - 0.01, z), (0.6, HEAD_Y + 0.02, 0.6), WOOD, detail=True)
        mk.box(p, (0, HEAD_Y + 0.3, z), (2 * NW + 0.2, 0.62, 0.64), WOOD, detail=True)
    # cartel de peligro a la derecha: tablero claro en blanco con borde rojo (marco de cuatro listones)
    bx, by, bz = 5.6, 4.3, surface_z(pts, 5.6, 4.3) - 0.06
    mk.box(p, (bx, by, bz), (2.0, 1.3, 0.12), CRATE, detail=True)
    for dy in (-0.7, 0.7):
        mk.box(p, (bx, by + dy, bz - 0.04), (2.24, 0.14, 0.14), RED, detail=True)
    for dx in (-1.07, 1.07):
        mk.box(p, (bx + dx, by, bz - 0.042), (0.12, 1.29, 0.13), RED, detail=True)
    return pts


def surface_z(hulls, x, y):
    """z de la cara de la roca en (x, y): rayo desde adelante contra la unión de las columnas."""
    bm = bmesh.new()
    for pts in hulls:
        bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    loc, _, _, _ = bvh.ray_cast(Vector((x, y, -10.0)), Vector((0, 0, 1)))
    return loc.z


# ---------------- puertas ----------------
def door(mk, name, side, angle):
    """Hoja de tablones abisagrada en x = side * POST_X (cara de afuera del marco); se abre hacia -Z."""
    hx, hz = side * (POST_X - 0.3), -0.02
    p = mk.part(name, (hx, 0.0, hz))
    a = -math.radians(angle) * side                # hacia afuera (-Z)
    c, s = math.cos(a), math.sin(a)

    def rot(q):
        x, y, z = q[0] - hx, q[1], q[2] - hz
        return (hx + x * c + z * s, y, hz - x * s + z * c)

    w = POST_X - 0.3                           # la hoja llega al medio
    xm = hx - side * w / 2
    t = 0.3

    def box(center, size, mat, detail=False):
        mk.hull(p, [rot(q) for q in mk.pts_box(center, size)], mat, detail=detail)

    box((xm, HEAD_Y / 2, hz - t / 2 - 0.01), (w, HEAD_Y - 0.04, t), PLANK)
    for k in (1, 2):                                                             # juntas de los tablones
        xs = hx - side * w * k / 3
        for d in (-0.035, 0.035):
            q0, q1 = rot((xs + d, 0, hz)), rot((xs + d + 1, 0, hz))
            mk.slice(p, q0, (q1[0] - q0[0], 0, q1[2] - q0[2]))
        cx, _, cz = rot((xs, 0, hz - t - 0.01))
        mk.paint(p, WOOD, box=((cx, HEAD_Y / 2, cz), (0.2, HEAD_Y + 0.2, 0.2)))
    for y in (1.0, HEAD_Y - 1.0):                                                # travesaños de afuera
        box((xm, y, hz - t - 0.1), (w - 0.1, 0.42, 0.2), WOOD, detail=True)
    a0, b0 = rot((hx - side * 0.35, 1.25, hz - t - 0.12)), rot((hx - side * (w - 0.35), HEAD_Y - 1.25, hz - t - 0.12))
    beam(mk, p, a0, b0, 0.36, 0.16, WOOD, detail=True)                           # riostra
    for y in (1.0, HEAD_Y - 1.0):                                                # bisagras
        box((hx - side * 0.75, y, hz - t - 0.22), (1.5, 0.16, 0.05), IRON, detail=True)
        mk.cyl(p, (hx, y, hz), 0.09, 0.5, IRON, axis="y", sides=6, detail=True)


# ---------------- carga ----------------
def crate(mk, part, c, rot_y=0.0, k=0, open_lid=False):
    """Cajón de dinamita simplificado: cuerpo claro con franja roja pintada y tapa wood_mid."""
    x, y, z = c
    a = math.radians(rot_y)

    def rp(q):
        dx, dz = q[0] - x, q[2] - z
        return (x + dx * math.cos(a) + dz * math.sin(a), q[1], z - dx * math.sin(a) + dz * math.cos(a))

    mk.hull(part, [rp(q) for q in mk.pts_box((x, y + 0.5, z), (2.4, 1.0, 1.6))], CRATE)
    yb = y + 0.42
    for yy in (yb - 0.13, yb + 0.13):
        mk.slice(part, (x, yy, z), (0, 1, 0))
    mk.paint(part, RED, box=((x, yb, z), (3.2, 0.25, 3.2)))
    if open_lid:
        # tapa corrida y apoyada de canto; seis cartuchos asomando
        lid = [rp(q) for q in mk.pts_box((x, y + 1.47, z + 0.12), (2.46, 0.4, 1.66), rot=(20, 0, 0))]   # bisagra atrás
        mk.hull(part, lid, PLANK, detail=True)
        mk.hull(part, [rp(q) for q in mk.pts_box((x, y + 0.98, z), (2.2, 0.06, 1.4))], "wood_dark", detail=True)
        for i in range(6):
            sx = x - 0.75 + 0.3 * i
            mk.hull(part, [rp(q) for q in mk.pts_box((sx, y + 1.06, z - 0.1), (0.2, 0.2, 1.3))], RED, detail=True)
    else:
        mk.hull(part, [rp(q) for q in mk.pts_box((x, y + 1.2, z), (2.46, 0.4, 1.66))], PLANK, detail=True)


def keg(mk, part, c, lying=False):
    """Barril de pólvora: tres anillos de 8 lados (panza), zunchos y franja roja pintados."""
    x, y, z = c
    pts = []
    for yy, r in ((0.0, 0.6), (0.75, 0.72), (1.5, 0.6)):
        for i in range(8):
            t = 2 * math.pi * (i + 0.5) / 8
            if lying:                                    # acostado a lo largo de X
                pts.append((x - 0.75 + yy, y + 0.66 + r * math.sin(t), z + r * math.cos(t)))
            else:
                pts.append((x + r * math.cos(t), y + yy, z + r * math.sin(t)))
    mk.hull(part, pts, WOOD)
    axis = (1, 0, 0) if lying else (0, 1, 0)
    for h, mat in ((0.62, RED), (0.88, RED)):
        q = (x - 0.75 + h, y, z) if lying else (x, y + h, z)
        mk.slice(part, q, axis)
    for h0, h1, mat in ((0.12, 0.28, IRON), (0.62, 0.88, RED), (1.22, 1.38, IRON)):
        mid = (h0 + h1) / 2
        if lying:
            mk.paint(part, mat, box=((x - 0.75 + mid, y + 0.66, z), (h1 - h0, 2.0, 2.0)))
        else:
            mk.paint(part, mat, box=((x, y + mid, z), (2.0, h1 - h0, 2.0)))
    for h in (0.2, 1.3):
        mk.slice(part, (x - 0.75 + h - 0.08, y, z) if lying else (x, y + h - 0.08, z), axis)
        mk.slice(part, (x - 0.75 + h + 0.08, y, z) if lying else (x, y + h + 0.08, z), axis)


def load(mk):
    stack = [("frag01", -2.55, 4.6, 0, 0), ("frag02", 0.0, 4.55, 3, 1), ("frag03", 2.55, 4.6, -2, 2)]
    for name, x, z, r, k in stack:
        p = mk.part(name, (0, 0, 0))
        crate(mk, p, (x, 0.0, z), r, k)
        crate(mk, p, (x + 0.06, 1.395, z - 0.05), r + 2, k + 1)
    p = mk.part("frag04", (0, 0, 0))
    crate(mk, p, (-1.3, 2.785, 4.45), 6, 5)
    p = mk.part("frag05", (0, 0, 0))
    crate(mk, p, (-1.4, 0.0, 2.0), -14, 6, open_lid=True)
    for name, c, lying in (("frag06", (2.3, 0.0, 1.9), False), ("frag07", (3.0, 0.0, 2.85), False),
                           ("frag08", (1.9, 0.0, 0.7), True)):
        p = mk.part(name, (0, 0, 0))
        keg(mk, p, c, lying)


# ---------------- mecha ----------------
def chaikin(pts, n=2):
    for _ in range(n):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            a, b = Vector(a), Vector(b)
            out += [tuple(a.lerp(b, 0.25)), tuple(a.lerp(b, 0.75))]
        out.append(pts[-1])
        pts = out
    return pts


def fuse(mk, rock):
    end = (-1.0, 1.04, 2.1)                      # adentro del cajón destapado, entre los cartuchos
    p = mk.part("Fuse", end)
    floor = [end, (-0.9, 0.04, 1.1), (-0.6, 0.04, -0.2), (-1.2, 0.04, -2.0), (-3.0, 0.04, -4.0), (-5.2, 0.04, -4.0),
             (-6.4, 0.04, -2.2)]                  # rodea la hoja abierta de la puerta izquierda
    wall = []
    for x, y in ((-6.2, 0.6), (-6.1, 2.0), (-5.5, 3.2), (-6.0, 4.6), (-5.3, 5.9)):
        wall.append((x, y, surface_z(rock, x, y) - 0.025))
    path = chaikin(floor + wall, 1)
    path = [path[0]] + [(x, max(y, 0.035), z) for x, y, z in path[1:]]
    # los puntos de la pared se vuelven a apoyar en la roca después de redondear las esquinas
    path = [q if (i == 0 or q[1] < 0.3) else (q[0], q[1], surface_z(rock, q[0], q[1]) - 0.025) for i, q in enumerate(path)]
    total = 0.0
    for i, (a, b) in enumerate(zip(path, path[1:])):
        w = 0.06 + 0.004 * (i % 2)
        a2 = Vector(b) + (Vector(b) - Vector(a)).normalized() * 0.02
        beam(mk, p, a, tuple(a2), w, w, ROPE)
        total += (Vector(b) - Vector(a)).length
    mk.marker("_FuseEnd", end)
    mk.marker("_FuseStart", path[-1])
    return total


def build(mk):
    rock = alcove(mk)
    door(mk, "DoorL", -1, 105)
    door(mk, "DoorR", 1, 80)
    load(mk)
    fuse(mk, rock)

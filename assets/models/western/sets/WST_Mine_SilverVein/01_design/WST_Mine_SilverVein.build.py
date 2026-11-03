"""
Receta de WST_Mine_SilverVein, las vetas de plata viva que marcan el camino en la mina (prompt 103,
Bloques A + B + G).

Brief
- Lo que se lee en la oscuridad: líneas celestes (Neon) que se ramifican como raíces o un rayo sobre una
  laja de roca oscura. En la pared A, un tronco grueso que nace a la izquierda y se afina hacia +X, con
  dos ramas grandes que se abren y vuelven a cerrar hacia la punta: se lee como una flecha. En la B, lo
  mismo hacia arriba. En el piso, raíces que salen de tres cristales. El racimo suelto es un manojo de
  cristales grises con juntas celestes que brota de una piedra.
- Medidas y orígenes:
  Vein_Wall_A / Vein_Wall_B: laja de 6 x 4 (x, y) y 0,5 de grueso, con la espalda en z = 0 (contra la pared)
  y el frente facetado hacia -Z; origen en el centro de la espalda (se apoya en la pared y se gira).
  Vein_Floor: laja de 3 x 3 en el piso (y 0 a ~0,3), origen abajo al centro.
  Vein_Cluster: piedra de ~1,7 x 0,7 y cristales hasta 2,0 de alto, origen abajo al centro.
- Plata (Bloque G): objetos aparte <Pieza>_Silver_Veins (silver_neon: tiras de 0,2 en el tronco a 0,04 en
  las puntas, 0,03-0,04 sobre la roca y metidas 0,02, siguiendo las facetas: cada punto se apoya con un rayo
  contra la laja) y <Pieza>_Silver_Crust (silver_crust con juntas silver_neon: un núcleo de neón que se ve
  entre los cristales). La laja queda completa sin la plata.
- Inferido: el origen de las lajas de pared en la espalda, los nombres con prefijo de pieza (Blender no deja
  dos objetos con el mismo nombre), el dibujo de las ramas, los cristales como prismas de 6 lados con punta,
  la cantidad de cristales del racimo (9).

Vueltas: 1) un rayo caía afuera de la laja (las ramas se salían): los puntos se recortan a la laja · 2)
z-fighting entre tramos: las caras de abajo de todos los tramos estaban a la misma profundidad; ahora la
altura alterna en un ciclo de 5 (las ramas evitan la de su punto de nacimiento) y la profundidad crece
0,002 por tramo (un ciclo de 11 chocaba entre tramos que caían 11 lugares aparte: medido) · 3) la piedra
del racimo era una caja: icosaedro achatado.

Revisión
- Triángulos por pieza contra 400 (laja + plata): Vein_Wall_A 522 (54 + 468: 39 tramos de veta),
  Vein_Wall_B 438, Vein_Floor 446 (48 + 312 + 86 de cristales), Vein_Cluster 256. La veta es lo que
  marca el camino en la oscuridad: el exceso está todo en tramos de neón (12 triángulos cada uno).
- Medidas: lajas de pared 6,0 x 4,0 x ~0,5; laja de piso ~3 x 3 x 0,3; racimo 2,0 de alto.
- En la pared A la flecha apunta a +X: el tronco nace grueso (0,2) en x = -2,65 y la punta fina queda en
  x ≈ +2,6, con las dos ramas que se abren y vuelven hacia el tronco. Mirada de frente (-Z), +X queda a la
  izquierda de la pantalla.
- El punto más bajo (-1,9) es el borde de abajo de las lajas de pared (su origen está en el centro).
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

ROCK, ROCK2, NEON, CRUST = "stone_grey", "redrock_dark", "silver_neon", "silver_crust"
HEIGHTS = (0.030, 0.034, 0.038, 0.032, 0.036)     # cuánto sobresale cada tramo (vecinos nunca iguales)
DEPTH0, DEPTH_STEP = 0.016, 0.002                # cuánto se mete: distinto en cada tramo (las caras de abajo nunca coplanares)


# ---------------- superficie para apoyar la plata ----------------
class Surface:
    def __init__(self, hulls):
        bm = bmesh.new()
        for pts in hulls:
            bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        self.bvh = BVHTree.FromBMesh(bm)
        bm.free()

    def hit(self, origin, direction):
        loc, n, _, _ = self.bvh.ray_cast(Vector(origin), Vector(direction))
        if loc is None:
            raise ValueError(f"el rayo no toca la laja desde {origin}")
        d = Vector(direction)
        return loc, (n if n.dot(d) < 0 else -n)


class Veins:
    """Tiras de neón sobre una superficie: cada tramo es un casco de 8 puntos, metido 0,02 y saliendo 0,03-0,038."""

    def __init__(self, mk, part, surf, to_ray, limit=None):
        self.mk, self.part, self.surf, self.to_ray = mk, part, surf, to_ray
        self.limit = limit or (lambda p: p)               # mantiene los puntos adentro de la laja
        self.k = 0

    def line(self, pts2d, w0, w1, avoid=()):
        """Polilínea (puntos en el plano de la laja) de ancho w0 a w1. Devuelve los índices de altura usados."""
        pts2d = [self.limit(p) for p in pts2d]
        hits = [self.surf.hit(*self.to_ray(p)) for p in pts2d]
        used = []
        n = len(hits) - 1
        for i in range(n):
            (p0, n0), (p1, n1) = hits[i], hits[i + 1]
            while HEIGHTS[self.k % 5] in avoid or (used and HEIGHTS[self.k % 5] == used[-1]):  # noqa
                self.k += 1
            h, dp = HEIGHTS[self.k % 5], DEPTH0 + DEPTH_STEP * self.k
            used.append(h)
            avoid = ()
            self.k += 1
            wa = w0 + (w1 - w0) * i / n
            wb = w0 + (w1 - w0) * (i + 1) / n
            d = (p1 - p0)
            ext = d.normalized() * (wb * 0.5 if i < n - 1 else 0.0)
            pts = []
            for p, nn, w in ((p0, n0, wa), (p1 + ext, n1, wb)):
                s = nn.cross(d).normalized()
                for sw in (-w / 2, w / 2):
                    for sh in (-dp, h):
                        pts.append(tuple(p + s * sw + nn * sh))
            self.mk.hull(self.part, pts, NEON)
        return used


def wiggle(start, ang, length, step, amps, rng):
    """Polilínea que dobla en cada punto entre ±amps grados (alternando el lado: nunca menos de 3°)."""
    pts = [start]
    a = math.radians(ang)
    n = max(2, round(length / step))
    for i in range(n):
        lo, hi = amps
        turn = (lo + (hi - lo) * rng.u()) * (1 if i % 2 else -1)
        a += math.radians(turn)
        p = pts[-1]
        pts.append((p[0] + step * math.cos(a), p[1] + step * math.sin(a)))
    return pts


# ---------------- lajas ----------------
def wall_slab_pts(ox, w, h, seed):
    """Laja de pared: contorno irregular en la espalda (z = 0) y frente facetado hacia -Z."""
    r = T.Rng(seed)
    pts = []
    n = 12
    for k in range(n):
        t = 2 * math.pi * (k + 0.3 * r.u()) / n
        c, s = math.cos(t), math.sin(t)
        x = w / 2 * math.copysign(abs(c) ** 0.6, c) * (0.92 + 0.08 * r.u())
        y = h / 2 * math.copysign(abs(s) ** 0.6, s) * (0.9 + 0.1 * r.u())
        pts.append((ox + x, y, 0.0))
        pts.append((ox + x * 0.86, y * 0.84, -0.32 - 0.06 * r.u()))
    for x, y in ((-1.6, 0.6), (0.2, -0.5), (1.5, 0.7), (-0.4, 0.9), (0.9, -0.9), (-1.2, -0.7)):
        pts.append((ox + x * w / 6, y * h / 4, -0.44 - 0.08 * r.u()))
    return pts


def wall_piece(mk, name, ox, seed, design):
    slab = mk.part(name, (ox, 0, 0))
    pts = wall_slab_pts(ox, 6.0, 4.0, seed)
    mk.hull(slab, pts, ROCK2)
    for c, rad in (((ox - 1.6, 0.9, -0.5), 1.1), ((ox + 1.9, -1.0, -0.5), 1.0), ((ox + 0.3, 1.4, -0.4), 0.8)):
        mk.paint(slab, ROCK, ball=(c, rad))
    surf = Surface([pts])
    veins = Veins(mk, mk.part(f"{name}_Silver_Veins", (ox, 0, 0)), surf,
                  lambda p: ((ox + p[0], p[1], -2.0), (0, 0, 1)),
                  limit=lambda p: (max(-2.55, min(2.55, p[0])), max(-1.5, min(1.5, p[1]))))
    design(veins, T.Rng(seed + 7))


def at(used, j):
    """Alturas de los tramos que tocan el punto j de una línea (las de la rama tienen que ser otras)."""
    return {used[k] for k in (j - 1, j) if 0 <= k < len(used)}


def design_arrow(v, r):
    """Pared A: tronco de izquierda a derecha que se afina hacia +X; ramas que se abren y cierran (flecha)."""
    trunk = wiggle((-2.65, -0.15), 2, 5.4, 0.45, (6, 12), r)
    tu = v.line(trunk, 0.2, 0.04)
    up = wiggle(trunk[2], 34, 2.8, 0.4, (5, 11), r)
    up = [(x, y - 0.18 * max(0.0, (x - up[0][0]) - 1.2) ** 1.4) for x, y in up]      # vuelve hacia el tronco
    uu = v.line(up, 0.13, 0.035, avoid=at(tu, 2))
    dn = wiggle(trunk[3], -36, 2.6, 0.4, (5, 11), r)
    dn = [(x, y + 0.2 * max(0.0, (x - dn[0][0]) - 1.1) ** 1.4) for x, y in dn]
    du = v.line(dn, 0.12, 0.035, avoid=at(tu, 3) | {uu[0]})
    v.line(wiggle(up[3], 62, 0.9, 0.3, (8, 14), r), 0.07, 0.03, avoid=at(uu, 3))
    v.line(wiggle(dn[3], -60, 0.9, 0.3, (8, 14), r), 0.07, 0.03, avoid=at(du, 3))
    v.line(wiggle(trunk[7], 30, 1.0, 0.33, (8, 14), r), 0.07, 0.03, avoid=at(tu, 7))
    v.line(wiggle(trunk[8], -28, 0.9, 0.3, (8, 14), r), 0.065, 0.03, avoid=at(tu, 8))
    v.line(wiggle(trunk[1], 150, 0.6, 0.3, (6, 12), r), 0.08, 0.035, avoid=at(tu, 1))   # raicita hacia atrás


def design_up(v, r):
    """Pared B: el mismo dibujo hacia arriba."""
    trunk = wiggle((0.15, -1.5), 92, 3.2, 0.4, (6, 12), r)
    tu = v.line(trunk, 0.2, 0.04)
    left = wiggle(trunk[2], 128, 2.4, 0.4, (5, 11), r)
    lu = v.line(left, 0.13, 0.035, avoid=at(tu, 2))
    right = wiggle(trunk[3], 52, 2.6, 0.4, (5, 11), r)
    ru = v.line(right, 0.12, 0.035, avoid=at(tu, 3) | {lu[0]})
    v.line(wiggle(left[3], 160, 0.9, 0.3, (8, 14), r), 0.07, 0.03, avoid=at(lu, 3))
    v.line(wiggle(right[3], 20, 1.0, 0.3, (8, 14), r), 0.07, 0.03, avoid=at(ru, 3))
    v.line(wiggle(trunk[6], 125, 0.8, 0.3, (8, 14), r), 0.065, 0.03, avoid=at(tu, 6))
    v.line(wiggle(trunk[6], 60, 0.8, 0.3, (8, 14), r), 0.065, 0.03, avoid=at(tu, 6) | {HEIGHTS[(v.k - 1) % 5]})


# ---------------- cristales ----------------
def shard(mk, part, base, direction, length, radius, sides=6, twist=0.0):
    """Cristal: prisma de `sides` lados (raíz metida) con punta piramidal; el 75 % del largo es prisma."""
    d = Vector(direction).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    w = d.cross(u)
    b = Vector(base) - d * 0.12
    pts = []
    for ring_t, rr in ((0.0, radius * 0.9), (0.75, radius)):
        c = b + d * (length * ring_t)
        for i in range(sides):
            a = 2 * math.pi * i / sides + twist
            pts.append(tuple(c + (u * math.cos(a) + w * math.sin(a)) * rr))
    pts.append(tuple(b + d * (length + 0.12)))
    mk.hull(part, pts, CRUST)


def floor_piece(mk, ox):
    name = "Vein_Floor"
    slab = mk.part(name, (ox, 0, 0))
    r = T.Rng(41)
    pts = []
    for k in range(11):
        t = 2 * math.pi * (k + 0.3 * r.u()) / 11
        rad = 1.5 * (0.85 + 0.2 * r.u())
        pts.append((ox + rad * math.cos(t), 0.0, rad * math.sin(t)))
        pts.append((ox + rad * 0.8 * math.cos(t), 0.16 + 0.06 * r.u(), rad * 0.8 * math.sin(t)))
    for x, z in ((0.3, 0.2), (-0.5, -0.4), (0.4, -0.6), (-0.3, 0.6)):
        pts.append((ox + x, 0.27 + 0.05 * r.u(), z))
    mk.hull(slab, pts, ROCK2)
    mk.paint(slab, ROCK, ball=((ox + 0.9, 0.2, 0.7), 0.7))
    surf = Surface([pts])
    v = Veins(mk, mk.part(f"{name}_Silver_Veins", (ox, 0, 0)), surf, lambda p: ((ox + p[0], 2.0, p[1]), (0, -1, 0)),
              limit=lambda p: (p[0] * min(1.0, 1.2 / max(1e-6, math.hypot(*p))), p[1] * min(1.0, 1.2 / max(1e-6, math.hypot(*p)))))
    rr = T.Rng(47)
    for i, a in enumerate((10, 82, 150, 220, 290)):
        line = wiggle((0.2 * math.cos(math.radians(a)), 0.2 * math.sin(math.radians(a))), a, 1.15 + 0.15 * (i % 2), 0.3,
                      (8, 16), rr)
        lu = v.line(line, 0.13, 0.035)
        if i % 2 == 0:
            v.line(wiggle(line[2], a + 40, 0.5, 0.25, (8, 14), rr), 0.06, 0.03, avoid=at(lu, 2))
    crust = mk.part(f"{name}_Silver_Crust", (ox, 0, 0))
    top = surf.hit((ox, 2.0, 0.0), (0, -1, 0))[0]
    mk.ball(crust, (ox, top.y + 0.02, 0.0), 0.2, NEON, scale=(1.2, 0.5, 1.2), subdiv=0)          # junta de neón
    for i, (dx, dz, tilt) in enumerate(((0.12, 0.0, 22), (-0.08, 0.1, 18), (-0.03, -0.12, 26))):
        a = math.radians(120 * i + 15)
        d = (math.sin(math.radians(tilt)) * math.cos(a), math.cos(math.radians(tilt)), math.sin(math.radians(tilt)) * math.sin(a))
        shard(mk, crust, (ox + dx, top.y, dz), d, 0.5, 0.09, twist=0.3 * i)


def cluster_piece(mk, ox):
    name = "Vein_Cluster"
    lump = mk.part(name, (ox, 0, 0))
    mk.ball(lump, (ox, 0.22, 0.0), 0.95, ROCK2, scale=(1.0, 0.55, 0.85), rot=(8, 25, -6), subdiv=0)
    T.chunk(mk, lump, (ox + 0.55, 0.25, 0.35), (0.9, 0.55, 0.8), 62, rot=(0, -35, 8), mat=ROCK, detail=False)
    crust = mk.part(f"{name}_Silver_Crust", (ox, 0, 0))
    mk.ball(crust, (ox, 0.62, 0.0), 0.42, NEON, scale=(1.3, 0.9, 1.1), subdiv=1)                  # núcleo que se ve entre cristales
    specs = ((0.0, 0.0, 4, 1.45, 0.17), (0.25, 0.1, 18, 1.1, 0.13), (-0.25, 0.05, 20, 1.0, 0.14),
             (0.05, -0.28, 24, 0.95, 0.12), (-0.05, 0.3, 26, 0.85, 0.11), (0.38, -0.2, 38, 0.7, 0.1),
             (-0.4, -0.18, 40, 0.65, 0.1), (0.3, 0.32, 42, 0.6, 0.09), (-0.32, 0.35, 48, 0.55, 0.09))
    for i, (dx, dz, tilt, ln, rad) in enumerate(specs):
        a = math.atan2(dz, dx) if (dx or dz) else 0.0
        d = (math.sin(math.radians(tilt)) * math.cos(a), math.cos(math.radians(tilt)), math.sin(math.radians(tilt)) * math.sin(a))
        shard(mk, crust, (ox + dx, 0.62, dz), d, ln, rad, twist=0.4 * i)


def build(mk):
    wall_piece(mk, "Vein_Wall_A", 0.0, 11, design_arrow)
    wall_piece(mk, "Vein_Wall_B", 8.0, 23, design_up)
    floor_piece(mk, 14.0)
    cluster_piece(mk, 18.5)

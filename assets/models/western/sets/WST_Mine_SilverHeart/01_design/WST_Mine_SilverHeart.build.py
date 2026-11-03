"""
Receta de WST_Mine_SilverHeart, el corazón de plata de la galería central (prompt 104, Bloques A + B + G).
Pieza de foco del Chapter: acá pelea el Capataz y se descubre que la plata está viva.

Brief
- Silueta a 40 studs: un huevo de roca oscura gigante que revienta de la esquina entre pared y piso,
  partido al frente con labios dentados; de adentro salen decenas de cristales gris plata que apuntan
  hacia afuera, y en el fondo late una masa celeste (Neon). Seis raíces de neón gruesas se arrastran por el
  piso y trepan la pared.
- Medidas: 16 (x) x 12 (alto) x 8 (z: frente en -4, espalda plana contra la pared en +4). Origen en el piso
  al centro del crecimiento. La pared de la galería es el plano z = +4 y el piso y = 0.
- Geode (roca, Bloque B): casco elipsoidal facetado (centro (0, 5, 2), radios 8 x 7 x 6) aplanado contra
  la pared y el piso; hueco tallado adentro (cáscara de ~1,2) con paredes coal; boca dentada al frente
  (perfil en zigzag tallado de punta a punta, cortes stone_grey: la roca recién partida) y cinco grietas
  que salen de la boca. Tres pedazos de cáscara caídos adelante.
- Silver_Crust (Bloque G): ~33 cristales (prismas de 6 lados con punta, 1 a 4 de largo): los que tapizan
  el hueco nacen en la pared y apuntan al núcleo (paran 1,75 antes: el núcleo se ve entre las puntas),
  siete revientan por la boca desde el labio, hacia afuera y adelante. Juntas de neón: un hexágono chato de
  silver_neon en la raíz de cada cristal de la pared (brilla entre las bases).
- Silver_Core: masa facetada de neón de 3 de ancho con forma de corazón (cuerpo, dos lóbulos y punta),
  en (0, 5, 2,2), al fondo.
- Silver_Roots: seis troncos de neón (0,5 de ancho al nacer, 0,1 en la punta, 0,1 sobre la superficie):
  tres por el piso (11-15 de largo) y tres por la pared (10-13), con horquillas.
- Inferido: los nombres Geode y Silver_Crust (el prompt no nombra la roca ni la masa), el hueco coal, los
  cristales de la pared apuntando al núcleo (como una geoda real), las grietas, los pedazos caídos, el dibujo
  de las raíces.

Vueltas: 1) los 26 cristales salieron en abanico hacia arriba (se cortaba la esfera de Fibonacci a los
primeros), el labio era un anillo gris ancho como un neumático, las juntas eran placas sueltas que se leían
como calcomanías y los pedazos caídos flotaban · 2) cáscara más fina (hueco 7 x 6 x 5,1), cristales que
tapizan el hueco apuntando al núcleo, neón en la raíz de cada uno; 3468 triángulos · 3) la mitad de los
cristales de la pared (eran 47: el prompt pide 30-40) y los del labio sin el hexágono de neón (se leían
como tuercas) · 4) los pedazos caídos se apoyan con un rayo contra el pie de la cáscara (el pie real es
más chico que el elipsoide: los puntos de abajo se aplastan contra el piso).

Revisión
- 2824 triángulos contra 3000: Silver_Crust 1288 (~33 cristales con sus juntas), Silver_Roots 1008 (seis
  troncos con horquilla), Geode 446, Silver_Core 82.
- Medidas: el crecimiento mide 16 x 12 x 8 (la cáscara); el modelo entero, 35,6 x 21 x 19,1 porque las
  raíces corren 10-15 por el piso y por la pared (z = 4). El punto más bajo (-0,28) son las raíces y los
  pedazos metidos en el piso.
- El núcleo (3,0 de ancho) se ve de frente entre las puntas de los cristales; desde los costados, por la
  boca.
- Dudoso: las raíces de la pared corren sobre el plano z = 4 (la pared de la galería): si el corazón se pone
  en otra pared hay que moverlas en Studio (son un objeto aparte).
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

ROCK, ROCK2, DARK, CRUST, NEON = "stone_grey", "redrock_dark", "coal", "silver_crust", "silver_neon"
WALL_Z = 4.0
C_OUT, R_OUT = Vector((0.0, 5.0, 2.0)), Vector((8.0, 7.0, 6.0))
C_IN, R_IN = Vector((0.0, 5.3, 1.9)), Vector((7.0, 6.0, 5.1))
CORE = Vector((0.0, 5.0, 2.3))


def ellipsoid_pts(c, r, subdiv, seed, jit, ymin, zmax):
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=subdiv, radius=1.0)
    rng = T.Rng(seed)
    pts = []
    for v in tmp.verts:
        f = 1.0 + jit * (rng.u() - 0.5)
        p = Vector((c.x + v.co.x * r.x * f, c.y + v.co.z * r.y * f, c.z + v.co.y * r.z * f))
        p.y = max(p.y, ymin)
        p.z = min(p.z, zmax)
        pts.append(tuple(p))
    tmp.free()
    return pts


def bvh_of(pts):
    bm = bmesh.new()
    bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def ray_ellipsoid(o, d, c, r):
    """Distancia a lo largo de d desde o (adentro) hasta la superficie del elipsoide."""
    oc = Vector(((o.x - c.x) / r.x, (o.y - c.y) / r.y, (o.z - c.z) / r.z))
    dd = Vector((d.x / r.x, d.y / r.y, d.z / r.z))
    a, b, cc = dd.dot(dd), 2 * oc.dot(dd), oc.dot(oc) - 1
    return (-b + math.sqrt(b * b - 4 * a * cc)) / (2 * a)


# boca: contorno dentado (x, y) de la rotura al frente
MOUTH = [(-5.2, 3.0), (-4.6, 4.4), (-5.6, 5.4), (-4.4, 6.5), (-4.9, 7.9), (-3.3, 8.4), (-2.6, 9.7), (-1.3, 8.9),
         (-0.2, 10.1), (0.9, 9.0), (2.0, 9.9), (2.9, 8.5), (4.3, 8.7), (4.4, 7.3), (5.6, 6.6), (4.7, 5.5),
         (5.5, 4.4), (4.6, 3.4), (4.9, 2.2), (3.4, 2.4), (2.2, 1.6), (0.8, 2.3), (-0.6, 1.5), (-1.9, 2.3),
         (-3.2, 1.7), (-4.1, 2.5)]


def geode(mk):
    p = mk.part("Geode", (0, 0, 0))
    outer = ellipsoid_pts(C_OUT, R_OUT, 2, 7, 0.07, 0.0, WALL_Z)
    mk.hull(p, outer, ROCK2)
    mk.carve(p, DARK, points=ellipsoid_pts(C_IN, R_IN, 1, 9, 0.12, 1.1, WALL_Z - 1.0))
    mk.carve(p, ROCK, prism=dict(profile=MOUTH, depth=6.5, plane="xy", center=(0, 0, -4.5)))
    # grietas que salen de la boca: cuñas angostas talladas en la cáscara (cara de la grieta oscura)
    surf = bvh_of(outer)
    for i, (a, b, c) in enumerate((((-5.3, 5.0), (-6.8, 6.2), (-7.4, 5.4)), ((-2.6, 9.6), (-3.4, 11.0), (-2.4, 11.8)),
                                   ((2.0, 9.8), (2.9, 11.2), (2.4, 12.0)), ((5.4, 6.4), (6.8, 7.4), (7.3, 6.9)),
                                   ((4.8, 2.4), (6.4, 1.6), (7.2, 1.0)))):
        pts = []
        for k, (x, y) in enumerate((a, b, c)):
            o = Vector((x, y, -8.0))
            loc, n, _, _ = surf.ray_cast(o, Vector((0, 0, 1)))
            if loc is None:
                continue
            w = 0.16 if k < 2 else 0.05
            for dz in (-0.6, 0.55):
                for dx, dy in ((w, w), (-w, -w)):
                    pts.append((loc.x + dx, loc.y + dy, loc.z + dz))
        for k in range(len(pts) // 4 - 1):
            mk.carve(p, DARK, points=pts[4 * k:4 * k + 8])
    for c, rad in (((-6.5, 3.0, -1.5), 2.6), ((5.0, 9.5, 0.5), 2.4), ((6.8, 2.5, 0.0), 2.0), ((-3.5, 11.0, 2.0), 2.2)):
        mk.paint(p, ROCK, ball=(c, rad))
    # pedazos de cáscara caídos al pie
    fallen = [(-4.6, (2.4, 0.9, 1.8), (8, 30, 14)), (2.4, (1.8, 0.75, 1.5), (-10, -40, 6)),
              (6.0, (1.4, 0.6, 1.2), (12, 70, -8))]
    for i, (x, size, rot) in enumerate(fallen):
        for yt in (0.4, 0.8, 1.2, 1.6, 2.0, 2.5):               # la primera altura donde el rayo toca la cáscara
            loc, _, _, _ = surf.ray_cast(Vector((x, yt, -12.0)), Vector((0, 0, 1)))
            if loc is not None:
                break
        y = max(size[1] * 0.35, yt - size[1] * 0.3)
        T.chunk(mk, p, (x, y, loc.z + size[2] * 0.2), size, 400 + i, rot=rot, mat=ROCK2)   # apoyado contra el pie
    return surf


# ---------------- cristales ----------------
def shard(mk, part, base, direction, length, radius, mat=CRUST, sides=6, twist=0.0, sink=0.15):
    d = Vector(direction).normalized()
    ref = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    w = d.cross(u)
    b = Vector(base) - d * sink
    pts = []
    for ring_t, rr in ((0.0, radius * 0.85), (0.72, radius)):
        c = b + d * ((length + sink) * ring_t)
        for i in range(sides):
            a = 2 * math.pi * i / sides + twist
            pts.append(tuple(c + (u * math.cos(a) + w * math.sin(a)) * rr))
    pts.append(tuple(b + d * (length + sink)))
    mk.hull(part, pts, mat)


def in_mouth(x, y):
    inside = False
    n = len(MOUTH)
    for k in range(n):
        (x0, y0), (x1, y1) = MOUTH[k - 1], MOUTH[k]
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            inside = not inside
    return inside


def cavity_point(d):
    """Punto de la pared del hueco en la dirección d desde su centro (con los recortes de piso y pared)."""
    q = C_IN + Vector((d.x * R_IN.x, d.y * R_IN.y, d.z * R_IN.z)) * 0.985
    q.y = max(q.y, 1.2)
    q.z = min(q.z, WALL_Z - 1.05)
    return q


def collar(mk, part, base, d, r):
    """Junta de neón al pie de un cristal: hexágono chato alrededor de la raíz, apoyado en la pared."""
    ref = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    w = d.cross(u)
    pts = []
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        rim = base + (u * math.cos(a) + w * math.sin(a)) * r * (1.5 + 0.25 * (k % 2))
        pts += [tuple(rim - d * 0.12), tuple(rim + d * (0.1 + 0.03 * (k % 3)))]
    mk.hull(part, pts, NEON)


def crystals(mk, surf):
    p = mk.part("Silver_Crust", (0, 0, 0))
    rng = T.Rng(77)
    # 1) cristales que tapizan el hueco y apuntan al núcleo (paran antes de tocarlo: el núcleo se ve)
    N, golden, made = 64, math.pi * (3 - math.sqrt(5)), 0
    for i in range(N):
        y = 1 - 2 * (i + 0.5) / N
        rad = math.sqrt(max(0.0, 1 - y * y))
        d0 = Vector((math.cos(golden * i) * rad, y, math.sin(golden * i) * rad))
        q = cavity_point(d0)
        if q.z < -0.6 and in_mouth(q.x, q.y):            # ahí la cáscara está abierta
            continue
        if i % 2 == 1:
            continue
        to_core = CORE - q
        dist = to_core.length
        d = (to_core.normalized() + Vector(((rng.u() - 0.5) * 0.5, (rng.u() - 0.5) * 0.5, (rng.u() - 0.5) * 0.3))).normalized()
        ln = max(1.0, min(4.0, dist - 1.75))
        r = 0.2 + 0.07 * ln
        shard(mk, p, q, d, ln, r, twist=rng.u(), sink=0.25)
        collar(mk, p, q, d, r)
        made += 1
    # 2) cristales que revientan por la boca: nacen en el labio de adentro y apuntan hacia afuera y adelante
    for k, tilt in ((1, 0.55), (5, 0.3), (8, 0.6), (12, 0.35), (17, 0.5), (21, 0.25), (24, 0.45)):
        x, y = MOUTH[k]
        inward = Vector((x, y - 5.4, 0.0))
        q = Vector((x, y, 0.0)) - inward.normalized() * 0.55
        loc, n, _, _ = surf.ray_cast(Vector((q.x, q.y, -8.0)), Vector((0, 0, 1)))
        z0 = (loc.z if loc else -3.0) + 1.3                 # adentro del labio, detrás de la cara de afuera
        d = (inward.normalized() * tilt + Vector((0, 0, -1))).normalized()
        ln = 2.4 + 1.4 * rng.u()
        shard(mk, p, Vector((q.x, q.y, z0)), d, ln, 0.22 + 0.07 * ln, twist=rng.u(), sink=0.2)


def core(mk):
    p = mk.part("Silver_Core", tuple(CORE))
    body = mk.pts_ball(tuple(CORE + Vector((0, -0.15, 0))), 1.15, scale=(1.15, 1.0, 0.9), subdiv=1)
    mk.hull(p, body + [tuple(CORE + Vector((0.15, -1.75, -0.05)))], NEON)                   # cuerpo con la punta abajo
    for sx in (-1, 1):
        mk.ball(p, tuple(CORE + Vector((sx * 0.62, 0.85, -0.05))), 0.72, NEON, scale=(1.0, 0.95, 0.85), subdiv=1)
    mk.cyl(p, tuple(CORE + Vector((0.25, 1.55, 0.1))), 0.28, 0.9, NEON, axis="y", sides=6, rot=(0, 0, -18))   # aorta


# ---------------- raíces ----------------
class Root:
    """Tronco de neón sobre un plano (piso y = 0 o pared z = 4): tramos de 8 puntos, alturas alternadas."""
    H = (0.10, 0.115, 0.13, 0.108, 0.124)

    def __init__(self, mk, part):
        self.mk, self.part, self.k = mk, part, 0

    def line(self, pts3, n, w0, w1, avoid=()):
        used = []
        m = len(pts3) - 1
        for i in range(m):
            while self.H[self.k % 5] in avoid or (used and self.H[self.k % 5] == used[-1]):
                self.k += 1
            h = self.H[self.k % 5]
            dp = 0.03 + 0.003 * self.k
            used.append(h)
            avoid = ()
            self.k += 1
            p0, p1 = Vector(pts3[i]), Vector(pts3[i + 1])
            d = p1 - p0
            wa, wb = w0 + (w1 - w0) * i / m, w0 + (w1 - w0) * (i + 1) / m
            ext = d.normalized() * (wb * 0.5 if i < m - 1 else 0.0)
            s = n.cross(d).normalized()
            pts = [tuple(p + s * sw + n * sh) for p, w in ((p0, wa), (p1 + ext, wb)) for sw in (-w / 2, w / 2)
                   for sh in (-dp, h)]
            self.mk.hull(self.part, pts, NEON)
        return used


def wander(start, ang, length, step, amps, rng):
    pts = [start]
    a = math.radians(ang)
    for i in range(max(2, round(length / step))):
        lo, hi = amps
        a += math.radians((lo + (hi - lo) * rng.u()) * (1 if i % 2 else -1))
        pts.append((pts[-1][0] + step * math.cos(a), pts[-1][1] + step * math.sin(a)))
    return pts


def roots(mk):
    p = mk.part("Silver_Roots", (0, 0, 0))
    rt = Root(mk, p)
    rng = T.Rng(91)
    up = Vector((0, 1, 0))
    # por el piso (x, z): nacen al pie de la cáscara
    for ang, start, ln in ((200, (-6.4, 0.6), 13.0), (262, (-1.2, -3.2), 11.5), (318, (5.6, -0.4), 14.5)):
        line = wander(start, ang, ln, 1.2, (6, 14), rng)
        pts = [(x, 0.0, z) for x, z in line]
        used = rt.line(pts, up, 0.5, 0.1)
        fork = wander(line[4], ang + (35 if ang < 260 else -35), 4.0, 1.0, (8, 16), rng)
        rt.line([(x, 0.0, z) for x, z in fork], up, 0.24, 0.07, avoid={used[3], used[4]})
    # por la pared (x, y) en z = 4: nacen donde la cáscara toca la pared
    wall = Vector((0, 0, -1))
    for ang, start, ln in ((160, (-7.4, 5.5), 11.0), (95, (-2.8, 11.2), 10.0), (35, (6.9, 8.0), 12.5)):
        line = wander(start, ang, ln, 1.2, (6, 14), rng)
        pts = [(x, y, WALL_Z) for x, y in line]
        used = rt.line(pts, wall, 0.48, 0.1)
        fork = wander(line[3], ang - 40, 3.6, 1.0, (8, 16), rng)
        rt.line([(x, y, WALL_Z) for x, y in fork], wall, 0.22, 0.07, avoid={used[2], used[3]})


def build(mk):
    surf = geode(mk)
    crystals(mk, surf)
    core(mk)
    roots(mk)

"""
Receta de WST_Overlay_SilverCrust, la plata viva en costras (prompt 053, Bloques A + G).

Brief
- Lo que se lee a 40 studs: costras de cristal gris metálico que rompen la silueta del caminante:
  media cabeza (lado izquierdo del cráneo y la mejilla) con tres púas en la sien, el hombro derecho con
  un racimo de cuatro púas, una manga de cristal en el antebrazo derecho y un parche en el muslo
  izquierdo. Las juntas celestes (Neon) entre placas las pone el motor a brillar.
- Calza con el cuerpo de los caminantes (humanoid.py, H = 5,2): cada pieza Silver_<BodyPart>_Crust tiene el
  origen de su pieza R15 y se apoya en la superficie del caminante A (rayos desde afuera, como en
  SilverVeins). Ninguna cruza una articulación: cabeza sobre el cuello, hombro arriba de la cintura,
  manga entre y = 2,30 y 2,94 (codo 3,016, muñeca 2,184), muslo entre 1,72 y 2,18.
- Placa: casco de una base irregular de 5 puntos metida 0,04 en el cuerpo (calza en A, B, C y D, que
  difieren menos de 0,03) y una tapa achicada de 4 puntos a 0,10-0,18 por fuera, a alturas distintas:
  facetas de mineral, nunca blandas. Púa: pirámide de base cuadrada.
- Juntas de neón: debajo de cada grupo de placas, una "cama" de silver_neon 0,045 por fuera de la piel
  que se ve en las rendijas entre placas.
- Inferido: cantidad y tamaño de las placas (6 en la cabeza, 5 en el hombro, 6 en la manga, 3 en el
  muslo), largos de las púas (0,30 / 0,26 / 0,22 en la sien; 0,40 / 0,34 / 0,30 / 0,24 en el hombro).

Vueltas: 1) primera versión (placas chicas, la manga parecía una lata lisa) · 2) placas del cráneo más
grandes y una más, púas de 0,36/0,32/0,28 (la base metida se come 0,06: quedan 0,30 a la vista), manga
con una cresta por placa y puntas de 0,09-0,10, parche del muslo más grande · 3) las tres púas de la
sien arrancaban del mismo punto (dos caras coplanares): raíces separadas 0,04-0,05.

Revisión
- 586 triángulos contra 600.
- Revisado montado sobre A y C (script que junta los .blend y corre la revisión de z-fighting): sin
  coplanares; en C las placas del muslo quedan medio metidas en el ala de la chaparrera (aviso de caras
  tapadas, no error).
- Dudoso: con sombrero (A, C, D) las placas del cráneo y las púas de la sien atraviesan la copa y el ala.
  El prompt las pide así; probablemente la variante Crust tenga que sacar Acc_Hat en el motor.
"""

import math

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

head, hp = hu.head_space()
ring, round_ring = hu.ring, hu.round_ring
JIT = (1.0, 0.82, 1.08, 0.9, 1.12, 0.86, 1.04, 0.95)       # irregularidad fija (la receta da siempre lo mismo)


class _Probe:
    def __init__(self, mk):
        self.hulls = []
        self.pts_box, self.pts_ball = mk.pts_box, mk.pts_ball

    def hull(self, part, points, mat, detail=False):
        if not detail:
            self.hulls.append([tuple(p) for p in points])


class Surface:
    """Superficie del caminante A (cascos convexos, coordenadas del juego) con su dirección hacia afuera."""

    def __init__(self, hulls, outward):
        bm = bmesh.new()
        for pts in hulls:
            bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        self.bvh, self.outward = BVHTree.FromBMesh(bm), outward
        bm.free()

    def snap(self, p):
        p = Vector(p)
        d = self.outward(p).normalized()
        loc, n, _, _ = self.bvh.ray_cast(p + d * 0.8, -d)
        if loc is None:
            raise ValueError(f"el rayo no toca la superficie cerca de {tuple(round(k, 3) for k in p)}")
        return loc, (n if n.dot(d) > 0 else -n)


def radial_from_point(c):
    c = Vector(c)
    return lambda p: Vector(p) - c


def radial_from_axis(a, b):
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()

    def out(p):
        v = Vector(p) - a
        return v - ax * v.dot(ax)
    return out


def frame(n, hint):
    u = Vector(hint) - n * Vector(hint).dot(n)
    u.normalize()
    return u, n.cross(u)


def plate(mk, part, surf, center, size, height, hint=(0, 1, 0), k=0, embed=0.04, xform=lambda p: p, bed=None):
    """Placa de cristal: base irregular de 5 puntos apoyada (metida `embed`), tapa de 4 puntos achicada a
    `height` con alturas distintas. `bed` (lista) junta la huella para la cama de neón."""
    c, n = surf.snap(center)
    u, v = frame(n, hint)
    base, top = [], []
    for i in range(5):
        a = 2 * math.pi * (i + 0.15 * JIT[(i + k) % 8]) / 5
        r = size * JIT[(i + k + 3) % 8]
        loc, nn = surf.snap(c + (u * math.cos(a) + v * math.sin(a)) * r * 1.3)   # el rayo se acerca; se recorta abajo
        loc = c + (loc - c).normalized() * min((loc - c).length, r)
        base.append(loc - nn * embed)
        if bed is not None:
            bed.append((loc, nn))
    for i in range(4):
        a = 2 * math.pi * (i + 0.5 + 0.2 * JIT[(i + k + 5) % 8]) / 4
        top.append(c + (u * math.cos(a) + v * math.sin(a)) * size * 0.5 * JIT[(i + k + 1) % 8]
                   + n * height * JIT[(i + k + 2) % 8])
    mk.hull(part, xform([tuple(q) for q in base + top]), "silver_crust")
    return c, n


def shard(mk, part, root, direction, length, width=0.07, xform=lambda p: p):
    """Púa de cristal: pirámide de base cuadrada metida en la placa, punta a `length`."""
    d = Vector(direction).normalized()
    u, v = frame(d, (0, 0, 1) if abs(d.z) < 0.9 else (1, 0, 0))
    root = Vector(root) - d * 0.05
    pts = [root + (u * x + v * y) * width for x, y in ((1, 0), (0, 1), (-1, 0), (0, -0.8))] + [root + d * length]
    mk.hull(part, xform([tuple(q) for q in pts]), "silver_crust")


def neon_bed(mk, part, bed, lift=0.045, embed=0.04, grow=1.06, xform=lambda p: p):
    """Cama de neón bajo un grupo de placas: la huella juntada, un poco más grande, de -embed a +lift."""
    c = sum((p for p, _ in bed), Vector()) / len(bed)
    pts = []
    for p, n in bed:
        q = c + (p - c) * grow
        pts += [q - n * embed, q + n * lift]
    mk.hull(part, xform([tuple(q) for q in pts]), "silver_neon")


def build(mk):
    # ---------------- cabeza: lado izquierdo del cráneo y la mejilla, tres púas en la sien ----------------
    probe = _Probe(mk)
    hu.cranium(probe, None, lambda pts: list(pts))
    skull = Surface(probe.hulls, radial_from_point((0, 4.78, -0.26)))
    hc = mk.part("Silver_Head_Crust", hu.NECK_P)
    scalp, cheek = [], []
    for k, (p, s, h) in enumerate((((-0.16, 5.17, -0.40), 0.20, 0.13), ((-0.38, 5.04, -0.44), 0.19, 0.11),
                                   ((-0.42, 5.00, -0.12), 0.20, 0.14), ((-0.15, 5.16, -0.04), 0.20, 0.12),
                                   ((-0.32, 5.13, -0.24), 0.18, 0.15))):
        plate(mk, hc, skull, p, s, h, hint=(0, 0, -1), k=k, xform=head, bed=scalp)
    for k, (p, s, h) in enumerate((((-0.38, 4.56, -0.42), 0.15, 0.10), ((-0.43, 4.72, -0.30), 0.14, 0.11))):
        plate(mk, hc, skull, p, s, h, hint=(0, 1, 0), k=k + 5, xform=head, bed=cheek)
    neon_bed(mk, hc, scalp, xform=head)
    neon_bed(mk, hc, cheek, xform=head)
    for at, d, ln in (((-0.44, 4.92, -0.33), (-0.35, 1.0, 0.05), 0.36), ((-0.43, 4.88, -0.40), (-0.6, 0.9, -0.3), 0.32),
                      ((-0.45, 4.90, -0.25), (-0.25, 1.0, 0.35), 0.28)):                         # 0,30 a la vista
        root, rn = skull.snap(at)
        shard(mk, hc, root + rn * 0.06, d, ln, width=0.07, xform=head)

    # ---------------- hombro derecho y omóplato, racimo de cuatro púas arriba ----------------
    top = [(-0.70, 3.90, -0.30), (-0.70, 3.90, 0.18), (0.72, 4.00, -0.30), (0.72, 4.00, 0.18),
           (-0.30, 4.02, -0.26), (0.30, 4.08, -0.26), (-0.30, 4.02, 0.14), (0.30, 4.08, 0.14)]
    hump = [(-0.40, 3.70, 0.40), (0.40, 3.74, 0.40), (0.0, 3.80, 0.44)]
    vest = ([(x, y, z) for x in (-0.60, 0.60) for y, z in ((2.95, -0.05), (2.95, 0.34))]
            + [(-0.72, 3.82, -0.05), (0.72, 3.90, -0.05), (-0.72, 3.82, 0.24), (0.72, 3.90, 0.24),
               (-0.42, 3.70, 0.45), (0.42, 3.74, 0.45), (0.0, 3.80, 0.49), (-0.67, 3.40, 0.41), (0.67, 3.40, 0.41)])
    torso = Surface([ring(2.82, 0, 0, 1.02, 0.56) + ring(3.40, 0, 0.02, 1.30, 0.66) + top + hump, vest],
                    radial_from_point((0.25, 3.55, 0.02)))
    uc = mk.part("Silver_UpperTorso_Crust", (0, hu.WAIST, 0))
    shoulder, blade = [], []
    for k, (p, s, h) in enumerate((((0.44, 4.04, -0.08), 0.15, 0.14), ((0.56, 3.96, -0.27), 0.14, 0.12),
                                   ((0.34, 4.05, 0.12), 0.14, 0.12))):
        plate(mk, uc, torso, p, s, h, hint=(1, 0, 0), k=k, bed=shoulder)
    for k, (p, s, h) in enumerate((((0.40, 3.74, 0.46), 0.17, 0.16), ((0.22, 3.52, 0.44), 0.15, 0.12),
                                   ((0.55, 3.52, 0.40), 0.14, 0.13))):
        plate(mk, uc, torso, p, s, h, hint=(0, 1, 0), k=k + 3, bed=blade)
    neon_bed(mk, uc, shoulder)
    neon_bed(mk, uc, blade)
    root, rn = torso.snap((0.45, 4.04, -0.04))
    for d, ln in (((0.15, 1.0, 0.10), 0.40), ((0.30, 1.0, -0.25), 0.34), ((-0.10, 1.0, 0.30), 0.30), ((0.05, 0.9, -0.45), 0.24)):
        shard(mk, uc, root + rn * 0.08, d, ln, width=0.075)

    # ---------------- manga de cristal en el antebrazo derecho, dentada en las dos puntas ----------------
    shR, elR, wrR = hu.arm_joints(1)
    lc = mk.part("Silver_RightLowerArm_Crust", elR)
    ax0, ax1 = Vector(elR), Vector(wrR)

    def axis_at(y):
        return ax0.lerp(ax1, (y - ax0.y) / (ax1.y - ax0.y))

    def rad(y):                                      # radio del antebrazo de A (0,26 -> 0,21, con 0,05 de solape)
        return (0.26 + (0.21 - 0.26) * (hu.ELBOW + 0.05 - y) / (hu.ELBOW - hu.WRIST + 0.10)) / 2
    ring_pts = []
    for y in (2.34, 2.88):
        c = axis_at(y)
        for i in range(8):
            a = 2 * math.pi * (i + 0.5) / 8
            for r in (rad(y) - 0.04, rad(y) + 0.045):
                ring_pts.append((c.x + r * math.cos(a), y, c.z + r * math.sin(a)))
    mk.hull(lc, ring_pts, "silver_neon")                                                       # junta de neón
    for k in range(6):                     # 6 placas con una cresta al medio y puntas largas arriba y abajo
        a0, a1 = math.radians(60 * k + 6), math.radians(60 * k + 54)
        y0, y1 = 2.36 + 0.03 * JIT[k] - 0.03, 2.84 + 0.04 * JIT[k + 2] - 0.04
        out = 0.08 + 0.05 * JIT[(k + 1) % 8]
        pts = []
        for y in (y0, y1):
            c = axis_at(y)
            for a in (a0, a1):
                for r in (rad(y) - 0.04, rad(y) + out):
                    pts.append((c.x + r * math.cos(a), y, c.z + r * math.sin(a)))
        am = (a0 + a1) / 2 + math.radians(6 * (JIT[k + 1] - 1) * 10)
        ym = (y0 + y1) / 2 + 0.06 * (JIT[k] - 1) * 5
        c = axis_at(ym)
        r = rad(ym) + out + 0.06
        pts.append((c.x + r * math.cos(am), ym, c.z + r * math.sin(am)))                     # cresta
        for y, dy in ((y0, -0.10 * JIT[k + 1]), (y1, 0.09 * JIT[k])):                           # puntas dentadas
            c = axis_at(y + dy)
            r = rad(y) + 0.04
            pts.append((c.x + r * math.cos(am), y + dy, c.z + r * math.sin(am)))
        mk.hull(lc, pts, "silver_crust")

    # ---------------- parche en el muslo izquierdo, del lado de afuera ----------------
    hipL, kneeL, _ = hu.leg_joints(-1)
    thigh = Surface([ring(hu.HIP + 0.05, hipL[0], 0, 0.50, 0.52) + ring(hu.KNEE - 0.05, hipL[0], 0, 0.40, 0.42)],
                    radial_from_axis(hipL, kneeL))
    tc = mk.part("Silver_LeftUpperLeg_Crust", hipL)
    patch = []
    for k, (p, s, h) in enumerate((((-0.54, 2.04, -0.02), 0.16, 0.14), ((-0.53, 1.84, 0.10), 0.15, 0.12),
                                   ((-0.52, 1.86, -0.14), 0.14, 0.11))):
        plate(mk, tc, thigh, p, s, h, hint=(0, 1, 0), k=k + 2, embed=0.05, bed=patch)
    neon_bed(mk, tc, patch, embed=0.05)

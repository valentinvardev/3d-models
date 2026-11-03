"""
Receta de WST_Enemy_ZombieBull, el toro zombie que embiste (prompt 056, Bloques A + E + G).

Brief
- Silueta a 40 studs: un ariete. Joroba y cuello enormes adelante, ancas flacas atrás (el frente 1,6 × el
  fondo), cabeza baja con la frente ancha y chata, cuernos largos (6,5 de punta a punta) que salen a los
  costados y se curvan adelante y arriba; un cuerno con la punta rota.
- Medidas: 10 de largo de la nariz a la base de la cola (z de -5,40 a +4,60), 5,8 de alto en la joroba,
  3,4 de ancho en los hombros. Patas rectas, de pie y cuadrado; la cabeza adelante y un poco abajo.
- Piezas (nombres del prompt): Torso (origen del modelo, en el piso bajo el centro de masa), Neck (en la
  base del cuello), Head (en la nuca), Tail (en la base), las 8 de las patas (UpperLeg en hombro o
  cadera, LowerLeg en la rodilla o el garrón, con la pezuña). Más Silver_Veins (origen del Torso) y
  Silver_Eyes (origen de la Head), del Bloque G.
- Cuero hide_brown con manchas hide_white pintadas (las caras grandes del low poly dan manchas
  angulosas de vaca). Costado izquierdo abierto: hueco tallado oscuro con 4 costillas de hueso.
- Cabeza: frente chata con una placa de hueso partida en dos (dos prismas con el borde en zigzag y una
  rendija entre ellas), argolla de hierro oxidado en la nariz, cuencas talladas con los ojos de plata.
- Plata: vetas que salen del costado abierto y suben por el hombro hasta la joroba (apoyadas 0,005
  adentro del cuero: tocan el Torso y no titilan).
- Inferido: altura de las articulaciones (hombro 3,3, rodilla 1,55, cadera 3,35, garrón 1,65), orejas
  chicas bajo los cuernos, papada, cola con borla negra, el cuerno roto es el derecho (+X).

Vueltas: 1) primera versión (el cuerpo era un tubo con un bultito de joroba; orejas flotando; placa de
la frente cóncava adentro de la booleana) · 2) hombros, joroba, cuello y patas delanteras más grandes,
ancas más flacas, orejas que arrancan adentro del cráneo, placa como detalle · 3) los ollares quedaban
abiertos (el cortador terminaba justo en la cara del hocico): ahora entran 0,1 · 4) la rotura del
costado era chica y atrás, con las costillas rectas como una rejilla: más grande y adelante, costillas
inclinadas, las vetas arrancan del borde.

Revisión
- 1668 triángulos contra 2200: las patas y el torso son pocos cascos grandes; el gasto está en la
  cabeza (cuernos de 4-5 tramos, placa partida, argolla, cuencas y ollares).
- Medidas: 10,0 de la nariz a la base de la cola (10,58 con la borla), 5,80 en la joroba, cuernos de
  6,24 (el derecho roto; entero darían 6,44).
- Las manchas blancas son caras enteras pintadas: quedan angulosas, a propósito.
- Vista lateral izquierda revisada aparte (la revisión estándar no la muestra): rotura con 4 costillas y
  las vetas que salen de ella hacia el hombro y la joroba.
"""

import math

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

round_ring = hu.round_ring
F_X, F_SH, F_KN, F_Z = 1.0, 3.30, 1.55, -1.35          # pata delantera: x, hombro, rodilla, z
B_X, B_HIP, B_HK, B_Z = 0.80, 3.35, 1.65, 3.55         # pata trasera: x, cadera, garrón, z


def vring(z, cx, cy, w, h, n=12):
    """Anillo vertical (a z constante): elipse de ancho w y alto h."""
    return [(cx + w / 2 * math.cos(2 * math.pi * (i + 0.5) / n), cy + h / 2 * math.sin(2 * math.pi * (i + 0.5) / n), z)
            for i in range(n)]


def bvh_of(hulls):
    bm = bmesh.new()
    for pts in hulls:
        bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def tangent_rot(n):
    """Euler (grados) que lleva el eje z de un prisma a la normal n."""
    return (math.degrees(-math.asin(max(-1, min(1, n.y)))), math.degrees(math.atan2(n.x, n.z)), 0)


def c_shape(r_in, r_out, a0, a1, n=5):
    angs = [math.radians(a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]
    return [(r_out * math.cos(a), r_out * math.sin(a)) for a in angs] + [(r_in * math.cos(a), r_in * math.sin(a)) for a in reversed(angs)]


def horn(mk, part, s, path, radii, mat="bone", tip_mat="coal"):
    """Cuerno: tramos convexos de anillo hexagonal a anillo hexagonal, que se encastran; la última punta oscura."""
    for i in range(len(path) - 1):
        a, b = Vector(path[i]), Vector(path[i + 1])
        d = (b - a).normalized()
        u = d.cross(Vector((0, 0, 1))).normalized() if abs(d.z) < 0.9 else Vector((1, 0, 0))
        v = d.cross(u).normalized()
        pts = []
        for c, r in ((a - d * 0.03, radii[i]), (b, radii[i + 1])):
            if r <= 0:
                pts.append(tuple(c))
                continue
            pts += [tuple(c + (u * math.cos(k * math.pi / 3) + v * math.sin(k * math.pi / 3)) * r) for k in range(6)]
        mk.hull(part, pts, tip_mat if i == len(path) - 2 and radii[-1] <= 0 else mat)


def vein(mk, part, bvh, outward, path, widths, base=-0.005, ridge=0.035):
    """Veta que sigue la superficie (como en SilverVeins), con la base metida `base` en el cuero."""
    def snap(p):
        p = Vector(p)
        d = outward(p).normalized()
        loc, n, _, _ = bvh.ray_cast(p + d * 1.0, -d)
        if loc is None:
            raise ValueError(f"la veta no toca el cuero cerca de {tuple(round(k, 2) for k in p)}")
        return loc, (n if n.dot(d) > 0 else -n)
    cs = [snap(p) for p in path]
    secs = []
    for i, (c, n) in enumerate(cs):
        t = cs[min(i + 1, len(cs) - 1)][0] - cs[max(i - 1, 0)][0]
        t = (t - n * t.dot(n)).normalized()
        side = n.cross(t).normalized()
        w = widths[i]
        if w <= 0:
            secs.append([c + n * (base + ridge) / 2])
            continue
        l, nl = snap(c - side * w / 2)
        r, nr = snap(c + side * w / 2)
        secs.append([l + nl * base, r + nr * base, c + n * ridge])
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        if i + 1 < len(secs) - 1 and len(b) == 3:
            cb = sum(b, Vector()) / 3
            lift = (b[2] - (b[0] + b[1]) / 2).normalized() * 0.004
            fwd = (cb - sum(a, Vector()) / len(a)).normalized() * 0.015
            b = [cb + (q - cb) * 0.8 + fwd + lift for q in b]
        mk.hull(part, [tuple(q) for q in a + b], "silver_neon")


def build(mk):
    # ---------------- torso: hombros y joroba enormes, ancas flacas ----------------
    torso = mk.part("Torso", (0, 0, 0))
    body = (vring(-2.30, 0, 3.20, 2.50, 2.80) + vring(-1.40, 0, 3.60, 3.40, 3.60) + vring(-0.30, 0, 3.50, 3.00, 3.10)
            + vring(1.20, 0, 3.30, 2.50, 2.40) + vring(2.80, 0, 3.45, 1.95, 1.85) + vring(4.30, 0, 3.55, 1.75, 1.60)
            + vring(4.70, 0, 3.70, 1.10, 0.90, n=8))
    hump = [(-0.85, 5.10, -2.20), (0.85, 5.10, -2.20), (-0.95, 5.15, -0.20), (0.95, 5.15, -0.20), (0, 5.80, -1.30),
            (-0.55, 5.62, -1.00), (0.55, 5.62, -1.00), (0, 5.55, -0.10), (0, 5.45, -2.20), (-0.50, 5.60, -1.90), (0.50, 5.60, -1.90)]
    mk.hull(torso, body, "hide_brown")
    mk.hull(torso, hump, "hide_brown")
    for c, r in (((1.0, 4.6, -0.6), 0.75), ((-0.9, 4.3, 2.6), 0.65), ((0.7, 3.0, 2.2), 0.7), ((-0.6, 5.2, -1.6), 0.5),
                 ((1.2, 2.6, -1.6), 0.55), ((0.2, 4.4, 3.9), 0.5)):
        mk.paint(torso, "hide_white", ball=(c, r))                                                  # manchas
    # costado izquierdo abierto: hueco en zigzag con 4 costillas
    flank = [(0.40, 2.85), (0.70, 2.70), (1.00, 2.88), (1.30, 2.72), (1.60, 2.86), (1.95, 2.78), (2.10, 3.20), (2.00, 3.60),
             (2.12, 4.00), (1.85, 4.25), (1.55, 4.12), (1.25, 4.32), (0.95, 4.16), (0.62, 4.30), (0.35, 4.05), (0.25, 3.50)]
    mk.carve(torso, "skin_dead_dark", prism=dict(profile=flank, depth=0.6, plane="zy", center=(-1.30, 0, 0)))
    for z in (0.55, 0.95, 1.35, 1.75):                       # costillas inclinadas hacia atrás y abajo
        mk.hull(torso, [(-1.02, 4.30, z - 0.06), (-1.02, 4.30, z + 0.04), (-1.02, 2.72, z + 0.24), (-1.02, 2.72, z + 0.34),
                        (-1.24, 4.18, z - 0.01), (-1.24, 2.86, z + 0.27), (-1.20, 3.50, z + 0.08), (-1.20, 3.50, z + 0.17)],
                "bone", detail=True)

    # ---------------- cuello y cabeza ----------------
    neck = mk.part("Neck", (0, 3.90, -2.00))
    mk.hull(neck, vring(-1.75, 0, 4.00, 2.30, 2.80) + vring(-2.80, 0, 3.60, 1.70, 2.00) + vring(-3.70, 0, 3.30, 1.25, 1.40),
            "hide_brown")
    mk.hull(neck, [(-0.20, 2.60, -2.00), (0.20, 2.60, -2.00), (0, 2.05, -2.40), (-0.18, 2.30, -3.10), (0.18, 2.30, -3.10),
                   (0, 2.40, -2.20)], "hide_brown")                                                 # papada
    mk.paint(neck, "hide_white", ball=((0.7, 3.9, -2.6), 0.45))
    hd = mk.part("Head", (0, 3.30, -3.65))
    skull = [(-0.62, 4.15, -3.70), (0.62, 4.15, -3.70), (-0.55, 4.05, -3.30), (0.55, 4.05, -3.30),
             (-0.66, 4.05, -4.10), (0.66, 4.05, -4.10), (-0.52, 3.20, -4.70), (0.52, 3.20, -4.70),
             (-0.45, 2.85, -5.30), (0.45, 2.85, -5.30), (-0.40, 2.45, -5.40), (0.40, 2.45, -5.40),
             (-0.38, 2.30, -5.10), (0.38, 2.30, -5.10), (-0.45, 2.35, -4.40), (0.45, 2.35, -4.40),
             (-0.50, 2.70, -3.70), (0.50, 2.70, -3.70), (-0.70, 3.40, -3.90), (0.70, 3.40, -3.90)]
    mk.hull(hd, skull, "hide_brown")
    mk.paint(hd, "hide_white", ball=((0, 3.75, -4.40), 0.30))                                        # estrella blanca en la frente
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=mk.pts_ball((s * 0.66, 3.55, -4.05), 0.14, scale=(0.8, 1.0, 1.2), subdiv=0))   # cuencas
        mk.carve(hd, "coal", points=mk.pts_cyl((s * 0.18, 2.62, -5.40), 0.07, 0.30, axis="z", sides=6))   # ollares: 0,1 adentro (el corte justo en la cara dejaba el hueco abierto)
        mk.hull(hd, [(s * 0.52, 3.95, -3.55), (s * 0.52, 3.75, -3.45), (s * 1.00, 3.82, -3.50), (s * 0.56, 3.85, -3.40),
                     (s * 0.95, 3.74, -3.58)], "hide_brown")                                         # oreja (arranca adentro del cráneo)
    # placa de hueso partida sobre la frente: dos prismas apoyados en el plano de la frente, rendija en zigzag
    fa, fb, fc = Vector((-0.66, 4.05, -4.10)), Vector((0.66, 4.05, -4.10)), Vector((0, 3.20, -4.70))
    fn = (fb - fa).cross(fc - fa).normalized()
    fn = fn if fn.z < 0 else -fn
    center = (fa + fb + fc) / 3 + Vector((0, 0.05, 0)) + fn * 0.02
    crack = [(-0.04, 0.34), (0.06, 0.18), (-0.05, 0.04), (0.05, -0.10), (-0.03, -0.26)]
    left = [(-0.42, 0.30), (-0.30, 0.38)] + [(x - 0.02, y) for x, y in crack] + [(-0.20, -0.30), (-0.36, -0.12)]
    right = [(0.30, 0.38), (0.42, 0.30), (0.36, -0.12), (0.20, -0.30)] + [(x + 0.02, y) for x, y in reversed(crack)]
    for prof in (left, right):
        mk.prism(hd, [(-x, y) for x, y in prof], 0.07, "bone", plane="xy", center=tuple(center), rot=tangent_rot(fn),
                 detail=True)                                                                         # detalle: la booleana no la toca
    # argolla oxidada en la nariz: dos C que se encastran (profundidades distintas)
    for a0, a1, dep in ((-10, 190, 0.05), (170, 370, 0.046)):
        mk.prism(hd, c_shape(0.12, 0.17, a0, a1), dep, "rust", plane="zy", center=(0, 2.40, -5.40), detail=True)
    # cuernos: salen a los costados y se curvan adelante y arriba; el derecho con la punta rota
    for s, n in ((-1, 6), (1, 5)):
        path = [(s * 0.50, 4.02, -3.80), (s * 1.30, 4.10, -3.75), (s * 2.10, 4.32, -3.95), (s * 2.70, 4.75, -4.30),
                (s * 3.05, 5.25, -4.55), (s * 3.22, 5.60, -4.70)][:n]
        radii = [0.24, 0.20, 0.15, 0.11, 0.07, 0.0][:n]
        if s > 0:   # roto: termina en un corte dentado en vez de punta
            path[-1] = (s * 2.95, 5.05, -4.45)
            radii[-1] = 0.09
        horn(mk, hd, s, path, radii)
        if s > 0:
            end = Vector(path[-1])
            mk.hull(hd, [tuple(end + Vector(q)) for q in ((0.0, 0.09, 0.0), (0.04, 0.0, 0.07), (-0.04, -0.05, 0.06),
                                                           (0.03, -0.07, -0.06), (-0.05, 0.03, -0.07), (0.02, 0.16, 0.02))], "bone")  # astilla

    se = mk.part("Silver_Eyes", (0, 3.30, -3.65))
    for s in (-1, 1):
        mk.ball(se, (s * 0.62, 3.55, -4.05), 0.075, "silver_neon", scale=(0.8, 1.0, 1.1), subdiv=0)

    # ---------------- cola ----------------
    tail = mk.part("Tail", (0, 3.75, 4.65))
    horn(mk, tail, 1, [(0, 3.80, 4.55), (0, 3.40, 4.85), (0, 2.60, 4.95), (0, 1.90, 4.90)], [0.13, 0.09, 0.07, 0.06], mat="hide_brown")
    mk.hull(tail, [(x, y, z) for x in (-0.13, 0.13) for y, z in ((2.00, 4.82), (2.00, 4.98))] + [(0, 1.45, 4.92), (0.04, 1.55, 4.80)],
            "hide_black")                                                                           # borla

    # ---------------- patas: delanteras gruesas, traseras flacas; pezuñas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        fu = mk.part(f"Front{side}UpperLeg", (s * F_X, F_SH, F_Z))
        mk.hull(fu, round_ring(F_SH + 0.40, s * F_X, F_Z, 1.10, 1.20) + round_ring(F_KN - 0.05, s * F_X, F_Z, 0.68, 0.74), "hide_brown")
        fl = mk.part(f"Front{side}LowerLeg", (s * F_X, F_KN, F_Z))
        mk.hull(fl, round_ring(F_KN + 0.10, s * F_X, F_Z, 0.64, 0.68, n=8) + round_ring(0.40, s * F_X, F_Z, 0.50, 0.54, n=8), "hide_brown")
        mk.hull(fl, round_ring(0.44, s * F_X, F_Z - 0.03, 0.56, 0.62, n=8) + round_ring(0.0, s * F_X, F_Z - 0.06, 0.64, 0.74, n=8), "coal")
        bu = mk.part(f"Back{side}UpperLeg", (s * B_X, B_HIP, B_Z))
        mk.hull(bu, round_ring(B_HIP + 0.40, s * B_X, B_Z, 0.72, 0.96) + round_ring(B_HK - 0.05, s * B_X, B_Z, 0.38, 0.44), "hide_brown")
        bl = mk.part(f"Back{side}LowerLeg", (s * B_X, B_HK, B_Z))
        mk.hull(bl, round_ring(B_HK + 0.10, s * B_X, B_Z, 0.40, 0.46, n=8) + round_ring(0.38, s * B_X, B_Z, 0.32, 0.36, n=8), "hide_brown")
        mk.hull(bl, round_ring(0.42, s * B_X, B_Z - 0.02, 0.38, 0.44, n=8) + round_ring(0.0, s * B_X, B_Z - 0.05, 0.44, 0.54, n=8), "coal")

    # ---------------- plata: vetas que salen del costado abierto y suben por el hombro ----------------
    sv = mk.part("Silver_Veins", (0, 0, 0))
    skin = bvh_of([body, hump])

    def out_body(p):
        return Vector((p.x, p.y - (3.6 if p.y < 4.7 else 4.2), 0))
    trunk = [(-1.48, 3.60, 0.18), (-1.55, 3.85, -0.30), (-1.62, 4.10, -0.75), (-1.55, 4.40, -1.15), (-1.10, 5.00, -1.40),
             (-0.50, 5.55, -1.40), (0.05, 5.75, -1.35)]
    vein(mk, sv, skin, out_body, trunk, (0.16, 0.15, 0.14, 0.12, 0.10, 0.08, 0.0))
    vein(mk, sv, skin, out_body, [(-1.62, 4.10, -0.75), (-1.65, 3.55, -1.10), (-1.55, 3.00, -1.50)], (0.09, 0.07, 0.0))
    vein(mk, sv, skin, out_body, [(-1.55, 4.40, -1.10), (-1.40, 4.45, -1.80), (-1.10, 4.35, -2.20)], (0.08, 0.06, 0.0))
    vein(mk, sv, skin, out_body, [(-1.50, 3.75, 0.10), (-1.45, 4.40, 0.05), (-1.15, 4.85, 0.0)], (0.08, 0.06, 0.0))
    vein(mk, sv, skin, out_body, [(-1.40, 2.95, 0.25), (-1.45, 2.55, -0.10), (-1.30, 2.30, -0.40)], (0.07, 0.05, 0.0))
    vein(mk, sv, skin, out_body, [(-0.50, 5.55, -1.40), (-0.70, 5.20, -0.70), (-0.85, 4.95, -0.20)], (0.07, 0.05, 0.0))

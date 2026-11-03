"""
Receta de WST_Enemy_BloatedMiner, el minero hinchado que explota (prompt 054, Bloques A + D + H + G).

Brief
- Silueta a 40 studs: un barril sobre piernas. Panza de 3,2 de ancho y 2,6 de fondo, cabeza chica,
  sombrero blando de minero con portavelas, brazos y piernas de grosor normal (para que la panza se
  lea). El aviso de que explota: grietas en la panza con luz de plata adentro y pústulas de cristal.
- Medidas (Bloque D, H = 5,4): tobillo 0,27 · rodilla 1,35 · cadera 2,538 · cintura 2,97 · codo 3,13 ·
  muñeca 2,27 · hombro 4,10 · cuello 4,32. Panza: máximo 3,2 × 2,6 justo en la cintura (y = 2,95),
  repartida entre LowerTorso (abajo del barril) y UpperTorso (arriba).
- Piezas: las 15 de R15, Eyes (oscuros), Acc_Hat, Silver_Cracks (neón adentro de cada grieta) y
  Silver_Pustules (5 en la panza y 1 en el cuello). Las dos de plata llevan el origen de UpperTorso.
- Ropa: pantalón del overol en el barril de abajo, reventado a los costados (tajos tallados que
  muestran la piel); un tirante entero que sube por la panza y el hombro izquierdo, el derecho cortado
  colgando de la pretina; camisa de lona solo en hombros, espalda y pecho de arriba, rota sobre la panza.
- Grietas: 5 zigzags tallados 0,05 en la piel de la panza y el pecho; cada cortador es un prisma
  orientado a la normal de la panza en ese punto (rayo contra el casco de la piel).
- Inferido: brazos abiertos 35° (el de arriba) y 8° (antebrazo) para pasar por fuera de la panza: con
  la I-pose de 8° la atravesaban; cabeza de ~1,0 (chica para el cuerpo); mangas arremangadas; botas de
  minero; la punta del tirante cortado cuelga de la pretina.

Vueltas: 1) primera versión · 2) tapa de la camisa coplanar con la de la piel (y = 4,15: la capa no
subía en y) y tapa de LowerTorso en el plano de la espalda de arriba · 3) grietas más largas y anchas
(±0,45, 0,10 de ancho; las de ±0,3 eran rayitas), pústulas como bulbo de cristal facetado con punta de
neón (parecían tuercas), un tajo grande por costado · 4) techo del tajo bajo la pretina (coplanares en
y = 2,86) · 5) sin los jirones de la camisa (quedaban enterrados en la panza, solo asomaba una punta),
ceja más pesada, cuencas más grandes, boca caída.

Revisión
- 2330 triángulos contra 1800 (+29 %): el aviso de que explota es lo que se tiene que leer, y cuesta
  ~800 entre las 5 grietas talladas de UpperTorso, el neón de adentro (Silver_Cracks, 172) y las 6
  pústulas (Silver_Pustules, 156); el barril de 12 lados es la silueta.
- Medidas: 5,46 de alto con el sombrero, panza 3,2 × 2,6 (4,15 de ancho con los brazos abiertos).
- Dudoso: los brazos abiertos 35° no son la I-pose de 8° del Bloque D (con 8° atravesaban la panza);
  la cara, redonda y con la boca abierta, puede leerse algo caricaturesca.
- A 96 px se lee: barril sobre piernas, sombrero chico, puntos de luz en la panza.
"""

import math

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

H = 5.4
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH, EL, WR = (1.12, SHOULDER, -0.10), (1.80, ELBOW, -0.10), (1.92, WRIST, -0.10)
LEG_X = 0.42
NECK_P = (0.0, NECK, -0.15)
NECK_W = (0.0, hu.NECK, -0.10)
HEAD_K, HEAD_FWD, HEAD_TILT = 0.95, 0.10, -5
ring, round_ring = hu.ring, hu.round_ring

# perfil del barril: (y, ancho, fondo, centro z)
BARREL = [(2.05, 1.40, 1.20, -0.10), (2.25, 2.10, 1.80, -0.20), (2.60, 2.90, 2.40, -0.30), (2.95, 3.20, 2.60, -0.35),
          (3.25, 2.90, 2.45, -0.32), (3.60, 2.44, 2.10, -0.26), (3.95, 2.10, 1.70, -0.18), (4.15, 1.40, 1.10, -0.10)]


def head(pts):
    out = [(x * HEAD_K, NECK_P[1] + (y - NECK_W[1]) * HEAD_K, NECK_P[2] + (z - NECK_W[2]) * HEAD_K - HEAD_FWD)
           for x, y, z in pts]
    return hu.about(out, NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def barrel(y0, y1, grow=0.0, zfilter=None):
    """Anillos del barril entre y0 e y1; con `grow`, una capa encima (el anillo de arriba sube `grow` también:
    si no, la tapa de la capa queda coplanar con la de la piel)."""
    pts = []
    for y, w, d, cz in BARREL:
        if y0 <= y <= y1:
            yy = y + grow if y == BARREL[-1][0] else y
            pts += [p for p in round_ring(yy, 0, cz, w + 2 * grow, d + 2 * grow, n=12) if zfilter is None or zfilter(p, cz)]
    return pts


def bvh_of(hulls):
    bm = bmesh.new()
    for pts in hulls:
        bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def band(points, half):
    """Polígono de una franja en zigzag alrededor de una polilínea 2D (inglete en las esquinas, puntas finas)."""
    P = [Vector(p) for p in points]
    left, right = [], []
    for i, p in enumerate(P):
        d0 = (p - P[i - 1]).normalized() if i > 0 else (P[1] - p).normalized()
        d1 = (P[i + 1] - p).normalized() if i < len(P) - 1 else d0
        n0, n1 = Vector((-d0.y, d0.x)), Vector((-d1.y, d1.x))
        m = (n0 + n1).normalized()
        w = half * (0.35 if i in (0, len(P) - 1) else 1.0) / max(m.dot(n0), 0.4)
        left.append(tuple(p + m * w))
        right.append(tuple(p - m * w))
    return left + right[::-1]


def tangent_rot(n):
    """Euler (grados) que lleva el eje z del prisma a la normal n (el eje x queda horizontal)."""
    return (math.degrees(-math.asin(max(-1, min(1, n.y)))), math.degrees(math.atan2(n.x, n.z)), 0)


def puffy_hand(mk, part, s, wx, wrist, z):
    mk.hull(part, round_ring(wrist + 0.05, wx, z, 0.24, 0.36) + round_ring(wrist - 0.20, wx + s * 0.01, z, 0.26, 0.40)
            + round_ring(wrist - 0.44, wx + s * 0.02, z, 0.21, 0.32), "skin_dead")
    mk.box(part, (wx - s * 0.08, wrist - 0.14, z - 0.20), (0.12, 0.22, 0.12), "skin_dead", rot=(-15, 0, 0))
    mk.paint(part, "skin_dead_dark", box=((wx, wrist - 0.44, z), (0.4, 0.08, 0.5)))


def build(mk):
    # ---------------- abajo del barril: pantalón del overol reventado a los costados ----------------
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, barrel(2.0, 2.96) + round_ring(3.02, 0, -0.35, 3.06, 2.46, n=12), "cloth_blue")   # tapa adentro del de arriba
    for s in (-1, 1):                                            # costura reventada a cada costado: muestra la piel
        mk.carve(lt, "skin_dead", points=[(s * x, y, z) for x, y, z in
                                           ((1.20, 2.83, -0.20), (1.75, 2.83, -0.20), (1.20, 2.83, 0.10), (1.75, 2.83, 0.10),   # abajo de la pretina (2,86)
                                            (1.05, 2.30, -0.06), (1.45, 2.30, -0.06), (1.20, 2.62, -0.36), (1.75, 2.62, -0.36),
                                            (1.20, 2.58, 0.26), (1.75, 2.58, 0.26))])
    mk.hull(lt, round_ring(2.86, 0, -0.35, 3.27, 2.67, n=12) + round_ring(2.97, 0, -0.35, 3.27, 2.67, n=12),
            "cloth_blue", detail=True)                                                                      # pretina
    surf_lt = bvh_of([barrel(2.0, 2.96)])
    for s in (-1, 1):
        loc, nrm, _, _ = surf_lt.ray_cast(Vector((s * 0.55, 2.92, -3.0)), Vector((0, 0, 1)))
        mk.cyl(lt, tuple(loc + nrm * 0.05), 0.06, 0.04, "iron", axis="z", sides=6, rot=tangent_rot(nrm), detail=True)  # botones
    # tirante derecho cortado: cuelga de la pretina sobre el pantalón
    pts = []
    for y in (2.92, 2.30):
        loc, nrm, _, _ = surf_lt.ray_cast(Vector((0.62 + (2.92 - y) * 0.15, y, -3.0)), Vector((0, 0, 1)))
        for dx in (-0.06, 0.06):
            pts += [tuple(loc + Vector((dx, 0, 0)) + nrm * 0.01), tuple(loc + Vector((dx, 0, 0)) + nrm * 0.045)]
    mk.hull(lt, pts, "cloth_blue", detail=True)

    # ---------------- arriba del barril: piel tirante con grietas, camisa rota, tirante izquierdo ----------------
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    skin = barrel(2.90, 4.2) + [(-1.00, 4.00, -0.30), (1.00, 4.00, -0.30), (-1.00, 4.00, 0.12), (1.00, 4.00, 0.12)]
    mk.hull(ut, skin, "skin_dead")
    mk.cyl(ut, (0, 4.24, -0.15), 0.25, 0.36, "skin_dead", rot=(-12, 0, 0), sides=10)                 # cuello gordo
    surf = bvh_of([skin])
    cracks = [((-0.55, 3.15), [(-0.46, 0.04), (-0.28, -0.08), (-0.10, 0.07), (0.08, -0.06), (0.26, 0.06), (0.42, -0.03)]),
              ((0.55, 3.38), [(-0.40, -0.07), (-0.22, 0.06), (-0.04, -0.06), (0.14, 0.07), (0.32, -0.04)]),
              ((-0.05, 2.99), [(-0.40, 0.03), (-0.20, -0.06), (0.0, 0.05), (0.20, -0.05), (0.38, 0.03)]),
              ((-0.45, 3.66), [(-0.30, -0.08), (-0.12, 0.05), (0.06, -0.05), (0.24, 0.08)]),
              ((1.10, 3.02), [(-0.26, 0.10), (-0.10, -0.04), (0.06, 0.08), (0.22, -0.06)])]
    silver_cracks = []
    for (x, y), line in cracks:
        loc, nrm, _, _ = surf.ray_cast(Vector((x, y, -3.0)), Vector((0, 0, 1)))
        if loc is None:
            raise ValueError(f"grieta fuera de la panza: {(x, y)}")
        rot = tangent_rot(nrm)
        # 0,07 en el centro: la panza se curva y en las puntas la grieta queda de ~0,04
        mk.carve(ut, "skin_dead_dark", prism=dict(profile=band(line, 0.048), depth=0.14, plane="xy",
                                                  center=tuple(loc), rot=rot))
        silver_cracks.append((band(line, 0.03), tuple(loc - nrm * 0.05), rot))
    # camisa (detalle): espalda, hombros y pecho de arriba, 0,035 por fuera; la panza la rompe adelante
    shirt = barrel(3.2, 4.2, grow=0.035, zfilter=lambda p, cz: p[2] > cz - 0.2) + barrel(3.9, 4.2, grow=0.035)
    shirt += [(-1.04, 4.04, -0.33), (1.04, 4.04, -0.33), (-1.04, 4.04, 0.15), (1.04, 4.04, 0.15)]
    mk.hull(ut, shirt, "canvas", detail=True)
    # tirante izquierdo: de la pretina sube por la panza y pasa por el hombro
    surf_all = bvh_of([skin, shirt])
    prev = None
    for y, x in ((2.95, -0.62), (3.30, -0.64), (3.65, -0.66), (3.98, -0.68)):
        loc, nrm, _, _ = surf_all.ray_cast(Vector((x, y, -3.0)), Vector((0, 0, 1)))
        sec = [tuple(loc + Vector((dx, 0, 0)) + nrm * dz) for dx in (-0.065, 0.065) for dz in (-0.01, 0.035)]
        if prev:
            mk.hull(ut, prev + sec, "cloth_blue", detail=True)
        prev = [tuple(Vector(p) + Vector((0, 0.012, 0))) for p in sec]
    mk.hull(ut, prev + [(-0.66, 4.24, -0.20), (-0.80, 4.24, -0.20), (-0.66, 4.20, 0.10), (-0.80, 4.20, 0.10)],
            "cloth_blue", detail=True)
    # sangre en la boca de la camisa y en el cuello
    mk.paint(ut, "blood_dry", ball=((0.15, 4.12, -0.42), 0.10))

    # ---------------- plata: neón adentro de las grietas, pústulas de cristal ----------------
    sc = mk.part("Silver_Cracks", (0, WAIST, 0))
    for prof, center, rot in silver_cracks:
        mk.prism(sc, prof, 0.034, "silver_neon", plane="xy", center=center, rot=rot)   # de 0,033 a 0,067 adentro
    sp = mk.part("Silver_Pustules", (0, WAIST, 0))

    def pustule(part, loc, nrm, k=1.0, seed=0):
        """Bulbo de cristal facetado (base metida 0,06, panza a 0,08, tapa a 0,15) y una punta de neón a 0,26."""
        u = Vector((nrm.z, 0, -nrm.x)).normalized()
        v = nrm.cross(u)

        def rim(r, h, n, off):
            return [tuple(loc + nrm * h * k + (u * math.cos(a) + v * math.sin(a)) * r * k)
                    for a in [(i + off) * 2 * math.pi / n for i in range(n)]]
        mk.hull(part, rim(0.10, -0.06, 5, 0) + rim(0.13, 0.08, 5, 0.5 + 0.1 * seed) + rim(0.06, 0.15, 3, 0.2 * seed), "silver_crust")
        mk.hull(part, rim(0.045, 0.13, 3, 0.5 + 0.2 * seed) + [tuple(loc + nrm * 0.26 * k)], "silver_neon")
    for k, (x, y) in enumerate(((0.10, 3.40), (-0.85, 3.30), (0.95, 3.55), (-0.20, 3.82), (0.55, 2.98))):
        loc, nrm, _, _ = surf.ray_cast(Vector((x, y, -3.0)), Vector((0, 0, 1)))
        pustule(sp, loc, nrm, 1.0, k)
    pustule(sp, Vector((0.18, 4.26, -0.30)), Vector((0.6, 0.0, -0.8)).normalized(), 0.8, 5)          # la del cuello

    # ---------------- cabeza chica, cachetes hinchados ----------------
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.22, 0, -0.22, 0.72, 0.66) + round_ring(4.40, 0, -0.25, 0.94, 0.84)
                     + round_ring(4.58, 0, -0.26, 1.00, 0.88) + round_ring(4.82, 0, -0.26, 0.86, 0.82)
                     + round_ring(5.02, 0, -0.26, 0.72, 0.74) + round_ring(5.14, 0, -0.26, 0.44, 0.50)), "skin_dead")
    mk.hull(hd, head(mk.pts_box((0, 4.86, -0.66), (0.78, 0.15, 0.22), top=(0.9, 0.75))), "skin_dead")     # ceja pesada y baja
    mk.ball(hd, hp((0, 4.64, -0.72)), 0.08, "skin_dead", scale=(1.0, 0.9, 1.1), subdiv=0)                 # nariz chata
    for s in (-1, 1):
        mk.hull(hd, head(mk.pts_box((s * 0.47, 4.66, -0.24), (0.08, 0.20, 0.14), top=(1, 0.7))), "skin_dead")   # orejas
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.18, 4.75, -0.72), 0.14, scale=(1.0, 0.8, 0.9), subdiv=0)))
    mouth = [(-0.18, 4.40), (-0.08, 4.47), (0.08, 4.48), (0.18, 4.39), (0.10, 4.28), (-0.11, 4.29)]          # boca caída
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.90, -0.55)]))
    for i in range(4):
        x = -0.09 + 0.06 * i
        mk.hull(hd, head([(x - 0.025, 4.50, -0.70), (x + 0.025, 4.50, -0.70), (x, 4.43, -0.70), (x - 0.02, 4.50, -0.52),
                          (x + 0.02, 4.50, -0.52), (x, 4.44, -0.52)]), "bone", detail=True)
    mk.paint(hd, "blood_dry", ball=(hp((0.08, 4.26, -0.74)), 0.09))
    mk.paint(hd, "blood_dry", ball=(hp((-0.19, 4.37, -0.70)), 0.07))
    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.17, 4.76, -0.62)), 0.065, "coal", scale=(1.0, 0.8, 0.8), subdiv=0)

    # sombrero blando de minero con portavelas (como el caminante D)
    base = hp((0, 5.00, -0.26))
    hat = mk.part("Acc_Hat", base)

    def hat_pts(pts):
        return hu.about(head(pts), base, (-4, 0, 6))
    mk.hull(hat, hat_pts(round_ring(4.99, 0, -0.26, 0.86, 0.82, n=12) + round_ring(5.18, 0, -0.27, 0.90, 0.86, n=12)
                         + round_ring(5.34, 0, -0.29, 0.62, 0.60, n=10) + [(0.0, 5.38, -0.30)]), "cloth_brown")
    brim = [(0.60 * math.cos(a), 5.00 - 0.05 * math.sin(a) - 0.04 * abs(math.cos(a)), -0.26 + 0.58 * math.sin(a))
            for a in [(i + 0.5) * math.pi / 6 for i in range(12)]]
    mk.hull(hat, hat_pts(brim + [(x, y - 0.05, z) for x, y, z in brim]), "cloth_brown")
    mk.box(hat, hat_pts([(0, 5.18, -0.71)])[0], (0.10, 0.18, 0.03), "iron", rot=(-9, 0, 0), detail=True)
    mk.box(hat, hat_pts([(0, 5.21, -0.755)])[0], (0.03, 0.04, 0.10), "iron", rot=(-9, 0, 0), detail=True)
    mk.cyl(hat, hat_pts([(0, 5.24, -0.78)])[0], 0.05, 0.07, "iron", sides=8, rot=(-9, 0, 0), detail=True)

    # ---------------- brazos: abiertos para pasar por fuera de la panza ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH[0], SH[1], SH[2]), (s * EL[0], EL[1], EL[2]), (s * WR[0], WR[1], WR[2])
        ua = mk.part(f"{side}UpperArm", sh)
        top = (sh[0] - s * 0.06, sh[1] + 0.10, sh[2])
        hu.limb(mk, ua, top, (el[0] - s * 0.04, el[1] + 0.12, el[2]), 0.42, 0.44, 0.38, 0.38, "canvas")
        hu.limb(mk, ua, (el[0] - s * 0.03, el[1] + 0.22, el[2]), (el[0], el[1] + 0.02, el[2]), 0.42, 0.42, 0.42, 0.42,
                "canvas", over=0.0)                                                                       # manga arremangada
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.30, 0.30, 0.26, 0.26, "skin_dead")
        hand = mk.part(f"{side}Hand", wr)
        puffy_hand(mk, hand, s, wr[0] + s * 0.02, WRIST, wr[2])

    # ---------------- piernas: overol y botas de minero ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.54, 0.56, 0.44, 0.46, "cloth_blue")
        ll = mk.part(f"{side}LowerLeg", knee)
        hu.limb(mk, ll, knee, (hip[0], 0.72, 0), 0.44, 0.46, 0.36, 0.38, "cloth_blue")
        mk.hull(ll, ring(0.76, hip[0], 0, 0.46, 0.48) + ring(0.22, hip[0], 0, 0.42, 0.44), "leather_dark")
        mk.hull(ll, ring(0.68, hip[0], 0, 0.50, 0.52) + ring(0.78, hip[0], 0, 0.50, 0.52), "leather_dark")
        ft = mk.part(f"{side}Foot", ankle)
        cx = hip[0]
        mk.hull(ft, [(cx + x, y, z) for x in (-0.22, 0.22) for y, z in ((0.07, 0.22), (0.33, 0.20), (0.30, -0.18))]
                + [(cx + x, y, z) for x in (-0.20, 0.20) for y, z in ((0.24, -0.48), (0.07, -0.60))], "leather_dark")
        mk.hull(ft, [(cx + x, y, z) for x in (-0.23, 0.23) for y, z in ((0.0, 0.23), (0.09, 0.23), (0.0, -0.56), (0.09, -0.58))]
                + [(cx + x, 0.0, -0.62) for x in (-0.16, 0.16)], "coal")

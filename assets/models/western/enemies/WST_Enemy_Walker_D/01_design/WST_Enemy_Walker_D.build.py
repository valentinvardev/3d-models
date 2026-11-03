"""
Receta de WST_Enemy_Walker_D, el caminante "minero" (prompt 051, Bloques A + D + H).

Brief
- Silueta a 40 studs, distinta de A, B y C: sombrero blando de fieltro, redondo y caído, con el
  portavelas de lata adelante; overol azul de pechera con un tirante cortado que cuelga; botas
  pesadas y anchas; tizne negro en la cara y las manos; bigote caído.
- Mismo cuerpo que A, B y C (humanoid.py: H = 5,2, articulaciones del Bloque D). La piel que cubren los
  overlays de plata es la de A: cabeza (hu.cranium 0,94, hu.zombie_face), cuello, antebrazos al aire
  (0,26 → 0,21) y manos (hu.hand).
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes y Acc_Hat (origen en la base de la copa).
- Capas: camisa de lona (base) · pechera y espalda del overol 0,035 por fuera · tirantes 0,035 más.
- Daños del prompt: mordida con un pedazo menos en el hombro izquierdo, dedo roto (mano izquierda), el
  labio de abajo arrancado mostrando los dientes (hueco tallado con encías y dientes largos), la pierna
  derecha del overol rota hasta la rodilla, el tirante derecho cortado y colgando.
- Tizne (coal): pintado en una mejilla, la frente y los dedos.
- Inferido (sin concepto): el bigote caído, la mano del dedo roto (izquierda), botas de trabajo a media
  caña, el sombrero con el ala caída atrás y levantada adelante, botones de hierro del overol.

Vueltas: 1) primera versión · 2) el tirante cortado era azul sobre la pechera azul (no se veía):
cuelga hacia afuera sobre la camisa; el tizne pintado teñía caras enteras (un triángulo negro en la
frente, otro en la mejilla, parecían agujeros): ahora son manchas talladas de 0,012 cuyo contorno se
proyecta sobre la cara con rayos; bigote, bolsillo, hebillas y copita del portavelas apoyados (flotaban
0,002-0,16) · 3) contorno de las manchas adentro de la silueta de la cara (dos rayos no la tocaban) ·
4) manchas a la mejilla derecha y al entrecejo: la izquierda la cruzan las vetas de SilverVeins.

Revisión
- 1874 triángulos contra 1800 (+4 %): boca con el labio arrancado (dientes largos con la raíz a la
  vista), dos manchas de tizne talladas, portavelas, tirantes que siguen el hombro.
- Medidas: 5,37 de alto con el sombrero, 2,37 de ancho (brazos).
- Piel compartida con A para los overlays: cabeza, cuello, antebrazos (0,26 → 0,21) y manos idénticos.
  Ojo: la plata del pecho (SilverVeins/Crust) va a quedar sobre la pechera, no sobre piel.
- A 96 px se distingue de A, B y C: sombrero redondo caído, overol azul de pechera, botas anchas.
"""

import math

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

head, hp = hu.head_space()
ring, round_ring = hu.ring, hu.round_ring


class _Probe:
    """Hace de `mk` para hu.cranium: junta los cascos en vez de construirlos, para medir la cara."""

    def __init__(self, mk):
        self.hulls = []
        self.pts_box, self.pts_ball = mk.pts_box, mk.pts_ball

    def hull(self, part, points, mat, detail=False):
        if not detail:
            self.hulls.append([tuple(p) for p in points])


def smudge(mk, part, outline, depth=0.012):
    """Mancha tallada poco profunda que sigue la cara (coordenadas de la cabeza sin girar): cada punto del
    contorno se proyecta con un rayo desde el frente; el cortador va de 0,05 afuera a `depth` adentro."""
    probe = _Probe(mk)
    hu.cranium(probe, None, lambda pts: list(pts))
    bm = bmesh.new()
    for pts in probe.hulls:
        bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    cut = []
    for x, y in outline:
        loc, n, _, _ = bvh.ray_cast(Vector((x, y, -3.0)), Vector((0, 0, 1)))
        if loc is None:
            raise ValueError(f"smudge: el rayo no toca la cara en ({x}, {y})")
        n = n if n.z < 0 else -n
        cut += [tuple(loc + n * 0.05), tuple(loc - n * depth)]
    mk.carve(part, "coal", points=head(cut))


def strap(mk, part, path, width=0.10, thick=0.035, mat="cloth_blue"):
    """Tira que sigue una lista de (punto apoyado, normal hacia afuera): tramos convexos que se encastran."""
    secs = []
    for p, n in path:
        p, n = Vector(p), Vector(n).normalized()
        w = Vector((width / 2, 0, 0))
        secs.append([p - w, p + w, p - w + n * thick, p + w + n * thick])
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        if i < len(secs) - 2:
            ca, cb = sum(a, Vector()) / 4, sum(b, Vector()) / 4
            fwd = (cb - ca).normalized() * 0.012
            b = [cb + (q - cb) * 0.94 + fwd for q in b]
        mk.hull(part, [tuple(q) for q in a + b], mat, detail=True)


def build(mk):
    # ---------------- cadera: el pantalón del overol ----------------
    lt = mk.part("LowerTorso", (0, hu.HIP, 0))
    mk.hull(lt, ring(2.28, 0, 0, 1.04, 0.58) + ring(2.93, 0, 0, 1.10, 0.60), "cloth_blue")
    for s in (-1, 1):
        mk.cyl(lt, (s * 0.50, 2.80, -0.12), 0.045, 0.04, "iron", axis="x", sides=6, detail=True)   # botones de costado

    # ---------------- torso: camisa, pechera del overol, tirantes, mordida en el hombro izquierdo ----------------
    ut = mk.part("UpperTorso", (0, hu.WAIST, 0))
    top = [(-0.70, 3.90, -0.30), (-0.70, 3.90, 0.18), (0.72, 4.00, -0.30), (0.72, 4.00, 0.18),
           (-0.30, 4.02, -0.26), (0.30, 4.08, -0.26), (-0.30, 4.02, 0.14), (0.30, 4.08, 0.14)]
    hump = [(-0.40, 3.70, 0.40), (0.40, 3.74, 0.40), (0.0, 3.80, 0.44)]
    mk.hull(ut, ring(2.82, 0, 0, 1.02, 0.56) + ring(3.40, 0, 0.02, 1.30, 0.66) + top + hump, "canvas")
    mk.carve(ut, "blood_dry", points=mk.pts_ball((-0.58, 3.92, -0.24), 0.12, scale=(1.1, 0.9, 1.0), subdiv=0))
    mk.paint(ut, "blood_dry", ball=((-0.52, 3.78, -0.33), 0.10))
    mk.cyl(ut, (0, 4.12, -0.14), 0.17, 0.42, "skin_dead", rot=(-20, 0, 0), sides=10)              # cuello (igual que A)
    mk.paint(ut, "coal", ball=((0.10, 4.08, -0.30), 0.08))                                         # tizne en el cuello
    # pechera: 0,035 por fuera de la camisa, del pantalón al pecho; espalda del overol hasta la cintura
    mk.hull(ut, [(x, y, z) for x in (-0.36, 0.36) for y, z in ((2.84, -0.32), (3.40, -0.348), (3.72, -0.348))]
            + [(x, y, -0.22) for x in (-0.36, 0.36) for y in (2.84, 3.72)], "cloth_blue", detail=True)
    mk.hull(ut, [(x, y, z) for x in (-0.50, 0.50) for y, z in ((2.84, 0.32), (3.30, 0.375))]
            + [(x, y, 0.20) for x in (-0.50, 0.50) for y in (2.84, 3.30)], "cloth_blue", detail=True)
    mk.hull(ut, [(x, y, z) for x in (-0.12, 0.12) for y, z in ((3.42, -0.34), (3.60, -0.34), (3.42, -0.375), (3.60, -0.375))],
            "cloth_blue", detail=True)                                                                # bolsillo de la pechera
    # tirante izquierdo entero: de la pechera, por arriba del hombro, a la espalda
    strap(mk, ut, [((-0.27, 3.66, -0.34), (0, 0, -1)), ((-0.37, 3.95, -0.30), (0, 0.5, -1)),
                   ((-0.40, 4.02, -0.05), (0, 1, 0)), ((-0.37, 3.90, 0.21), (0, 0.5, 1)),
                   ((-0.24, 3.28, 0.365), (0, 0, 1))])
    mk.box(ut, (-0.27, 3.68, -0.385), (0.12, 0.08, 0.03), "iron", detail=True)                     # hebilla
    # tirante derecho cortado: cuelga de la punta de la pechera hacia afuera, sobre la camisa clara
    mk.hull(ut, [(0.24, 3.72, -0.35), (0.34, 3.72, -0.35), (0.24, 3.72, -0.385), (0.34, 3.72, -0.385),
                 (0.42, 3.10, -0.325), (0.52, 3.12, -0.32), (0.42, 3.10, -0.36), (0.52, 3.12, -0.355)],
            "cloth_blue", detail=True)
    mk.prism(ut, [(-0.05, 0), (0.05, 0), (0.02, -0.12), (-0.01, -0.06)], 0.03, "cloth_blue", plane="xy",
             center=(0.47, 3.12, -0.34), rot=(0, 0, 10), detail=True)                              # punta deshilachada
    mk.box(ut, (0.29, 3.70, -0.39), (0.12, 0.08, 0.03), "iron", detail=True)                       # hebilla que quedó

    # ---------------- cabeza: la de A, con el labio de abajo arrancado, bigote y tizne ----------------
    hd = mk.part("Head", hu.NECK_P)
    hu.cranium(mk, hd, head)
    hu.zombie_face(mk, hd, head, hp, teeth_down=0)
    lip = [(-0.18, 4.40), (0.14, 4.40), (0.18, 4.34), (0.10, 4.27), (-0.12, 4.28)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in lip for z in (-0.85, -0.52)]))      # labio arrancado
    for i in range(5):                                                                                # dientes de abajo largos, raíz a la vista
        x = -0.13 + 0.065 * i
        mk.hull(hd, head([(x - 0.03, 4.29, -0.64), (x + 0.03, 4.29, -0.64), (x - 0.02, 4.44, -0.64), (x + 0.02, 4.44, -0.64),
                          (x - 0.028, 4.29, -0.46), (x + 0.028, 4.29, -0.46), (x, 4.43, -0.46)]), "bone", detail=True)
    for s in (-1, 1):
        mk.hull(hd, head(mk.pts_box((s * 0.47, 4.70, -0.22), (0.08, 0.24, 0.16), top=(1, 0.7))), "skin_dead")   # orejas
        mk.hull(hd, head([(s * 0.02, 4.60, -0.72), (s * 0.02, 4.555, -0.71), (s * 0.02, 4.58, -0.62),
                          (s * 0.21, 4.57, -0.69), (s * 0.21, 4.53, -0.67), (s * 0.20, 4.56, -0.58),
                          (s * 0.27, 4.38, -0.65), (s * 0.25, 4.39, -0.58)]), "hair_dark", detail=True)       # bigote caído
    mk.hull(hd, head(mk.pts_box((0, 4.82, 0.12), (0.84, 0.48, 0.24), top=(0.9, 0.9))), "hair_dark")             # pelo de atrás
    # tizne: mejilla derecha y entrecejo (el lado izquierdo de la cara es el de las vetas de SilverVeins)
    smudge(mk, hd, [(0.22, 4.50), (0.30, 4.52), (0.36, 4.60), (0.29, 4.645), (0.21, 4.57)])
    smudge(mk, hd, [(-0.10, 4.92), (0.08, 4.93), (0.10, 4.86), (-0.08, 4.85)])
    mk.paint(hd, "blood_dry", ball=(hp((0.06, 4.22, -0.70)), 0.08))
    hu.eyes(mk, hp)

    # ---------------- sombrero blando de minero con portavelas ----------------
    base = hp((0, 5.04, -0.26))
    hat = mk.part("Acc_Hat", base)

    def hat_pts(pts):
        return hu.about(head(pts), base, (-4, 0, 5))
    crown = (round_ring(5.03, 0, -0.26, 0.90, 0.86, n=12) + round_ring(5.22, 0, -0.27, 0.94, 0.90, n=12)
             + round_ring(5.38, 0, -0.29, 0.66, 0.64, n=10) + [(0.0, 5.42, -0.30)])
    mk.hull(hat, hat_pts(crown), "cloth_brown")
    brim = [(0.62 * c, 5.04 + 0.05 * (-s) - 0.04 * abs(c), -0.26 + 0.60 * s) for c, s in
            [(math.cos(a), math.sin(a)) for a in [(i + 0.5) * math.pi / 6 for i in range(12)]]]
    mk.hull(hat, hat_pts(brim + [(x, y - 0.05, z) for x, y, z in brim]), "cloth_brown")       # ala caída atrás, alzada adelante
    mk.hull(hat, hat_pts(round_ring(5.06, 0, -0.26, 0.95, 0.91, n=12) + round_ring(5.13, 0, -0.26, 0.95, 0.91, n=12)),
            "leather_dark", detail=True)                                                         # cinta
    mk.box(hat, hat_pts([(0, 5.22, -0.735)])[0], (0.10, 0.18, 0.03), "iron", rot=(-14, 0, 0), detail=True)  # chapa del portavelas
    mk.cyl(hat, hat_pts([(0, 5.28, -0.80)])[0], 0.05, 0.07, "iron", sides=8, rot=(-14, 0, 0), detail=True)  # copita, sin vela
    mk.box(hat, hat_pts([(0, 5.25, -0.78)])[0], (0.03, 0.04, 0.10), "iron", rot=(-14, 0, 0), detail=True)   # brazo

    # ---------------- brazos: mangas arremangadas, antebrazos al aire con tizne ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = hu.arm_joints(s)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1] + 0.10, sh[2]), (el[0], el[1] + 0.10, el[2]), 0.40, 0.42, 0.35, 0.36, "canvas")
        hu.limb(mk, ua, (el[0], el[1] + 0.22, el[2]), (el[0], el[1] + 0.02, el[2]), 0.40, 0.41, 0.40, 0.41, "canvas", over=0.0)
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.26, 0.26, 0.21, 0.21, "skin_dead")
        hand = mk.part(f"{side}Hand", wr)
        hu.hand(mk, hand, s, broken_finger=(side == "Left"))
        mk.paint(hand, "coal", box=((wr[0] + s * 0.04, hu.WRIST - 0.40, hu.ARM_Z), (0.4, 0.20, 0.5)))    # dedos tiznados

    # ---------------- piernas: overol (el derecho roto a la rodilla), botas pesadas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = hu.leg_joints(s)
        cx = hip[0]
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.52, 0.54, 0.42, 0.44, "cloth_blue")
        ll = mk.part(f"{side}LowerLeg", knee)
        if side == "Right":
            mk.hull(ll, ring(hu.KNEE + 0.06, cx, 0, 0.44, 0.46) + ring(hu.KNEE - 0.16, cx, 0, 0.42, 0.44), "cloth_blue")
            for dx, dz in ((-0.12, -0.19), (0.11, -0.18), (0.0, 0.20), (0.19, 0.04)):
                mk.prism(ll, [(-0.07, 0), (0.07, 0), (0.0, -0.15)], 0.03, "cloth_blue", plane="xy",
                         center=(cx + dx, hu.KNEE - 0.15, dz), rot=(0, 0 if abs(dz) > 0.1 else 90, 0), detail=True)
            hu.limb(mk, ll, (cx, hu.KNEE - 0.10, 0), (cx, 0.70, 0), 0.24, 0.26, 0.22, 0.24, "skin_dead")
        else:
            hu.limb(mk, ll, knee, (cx, 0.70, 0), 0.42, 0.44, 0.34, 0.36, "cloth_blue")
        mk.hull(ll, ring(0.74, cx, 0, 0.44, 0.46) + ring(0.22, cx, 0, 0.40, 0.42), "leather_dark")      # caña ancha
        mk.hull(ll, ring(0.66, cx, 0, 0.48, 0.50) + ring(0.76, cx, 0, 0.48, 0.50), "leather_dark")
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(cx + x, y, z) for x in (-0.21, 0.21) for y, z in ((0.07, 0.21), (0.33, 0.19), (0.30, -0.18))]
                + [(cx + x, y, z) for x in (-0.19, 0.19) for y, z in ((0.24, -0.46), (0.07, -0.58))], "leather_dark")   # puntera redonda
        mk.hull(ft, [(cx + x, y, z) for x in (-0.22, 0.22) for y, z in ((0.0, 0.22), (0.09, 0.22), (0.0, -0.54), (0.09, -0.56))]
                + [(cx + x, 0.0, -0.60) for x in (-0.15, 0.15)], "coal")                                                # suela gruesa

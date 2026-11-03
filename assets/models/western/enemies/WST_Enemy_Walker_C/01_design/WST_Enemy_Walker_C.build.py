"""
Receta de WST_Enemy_Walker_C, el caminante "peón de rancho" (prompt 050, Bloques A + D + H).

Brief
- Silueta a 40 studs, distinta de A (bombín, chaleco) y B (rodete, pollera): sombrero de cowboy de ala
  alzada a los costados y copa con hendidura, chaparreras con alas que ensanchan las piernas, camisa de
  lona clara con antebrazos al aire y el pañuelo rojo al cuello (el acento de color).
- Mismo cuerpo que A y B (humanoid.py: H = 5,2, articulaciones del Bloque D). Para que los overlays de
  plata calcen, la piel que cubren es la de A: cabeza (hu.cranium 0,94, hu.zombie_face), cuello,
  antebrazos al aire (0,26 → 0,21) y manos (hu.hand).
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes y Acc_Hat (origen en la base de la copa).
- Tallado: cuencas y boca, camisa abierta de arriba abajo con tres costillas adentro, oreja derecha
  arrancada, mordida en el hombro derecho, mordisco en el ala del sombrero. Pintado: sangre en mentón,
  hombro y comisura, uñas.
- Daños del prompt: dedo roto en la mano derecha, sin oreja derecha, mordida con un pedazo menos en el
  hombro derecho; la manga izquierda rota en jirones (la derecha arremangada).
- Inferido (sin concepto): chaparreras "batwing" con un ala de 0,10-0,14 hacia afuera, cinta del
  sombrero en leather_dark como la mancha de sudor, pelo corto oscuro bajo el sombrero, sombrero
  inclinado hacia atrás y a la derecha.

Vueltas (7 construcciones): 1) primera versión · 2) hebilla y bolsillos flotaban (0,015 por delante), la
patilla derecha quedaba suelta al tallar la oreja, techo de la chaparrera coplanar con el pantalón en
y = 1,35 · 3) la rotura angosta y simétrica del pecho se leía como corbata: ahora ancha y despareja, sin
bolsillos; el pañuelo no se veía de frente (lo tapa la mandíbula caída): triángulo grande corrido a la
izquierda que baja a y = 3,58 · 4) costillas más abajo; copa y cinta como detalle (el sombrero bajó de
398 a 330 triángulos) · 5-7) el mordisco del ala: tallado con booleana dejaba la cara de abajo como
polígono cóncavo con dos triángulos encimados; ahora el ala del medio es un prisma con el mordisco
dentado en el contorno (sin booleana) y las dos mitades de la copa no comparten el plano de abajo.

Revisión
- 1902 triángulos contra 1800 (+6 %): sombrero de tres piezas de ala, copa con hendidura y mordisco
  dentado; chaparreras con alas en las cuatro piezas de las piernas.
- Medidas: 5,48 de alto con el sombrero, 2,37 de ancho (brazos).
- Piel compartida con A para los overlays: cabeza, cuello, antebrazos (0,26 → 0,21) y manos idénticos.
- A 96 px se distingue de A y de B: sombrero de cowboy de ala alzada y piernas marrones más anchas.
"""

import math

from mathutils import Euler

import humanoid as hu

head, hp = hu.head_space()
ring = hu.ring


def chaps_ring(y, cx, w, d, s):
    """Los vértices de adelante y de afuera de un octógono 0,035 más grande que la pierna (lado s)."""
    r = ring(y, cx, 0, w + 0.07, d + 0.07)
    return [r[i] for i in ((0, 1, 2, 3) if s > 0 else (6, 7, 0, 1))]


def build(mk):
    # ---------------- cadera: pantalón y cinto con hebilla grande ----------------
    lt = mk.part("LowerTorso", (0, hu.HIP, 0))
    mk.hull(lt, ring(2.28, 0, 0, 1.02, 0.56) + ring(2.92, 0, 0, 1.08, 0.58), "cloth_blue")
    mk.hull(lt, ring(2.78, 0, 0, 1.13, 0.63) + ring(2.93, 0, 0, 1.13, 0.63), "leather_dark")
    mk.hull(lt, [(x, y, -0.30) for x in (-0.10, 0.10) for y in (2.80, 2.92)] + [(x, y, -0.36) for x in (-0.08, 0.08) for y in (2.82, 2.90)],
            "brass", detail=True)                                                                        # hebilla de rodeo

    # ---------------- torso: camisa de lona abierta, pañuelo rojo, mordida en el hombro ----------------
    ut = mk.part("UpperTorso", (0, hu.WAIST, 0))
    top = [(-0.70, 3.90, -0.30), (-0.70, 3.90, 0.18), (0.72, 4.00, -0.30), (0.72, 4.00, 0.18),
           (-0.30, 4.02, -0.26), (0.30, 4.08, -0.26), (-0.30, 4.02, 0.14), (0.30, 4.08, 0.14)]
    hump = [(-0.40, 3.70, 0.40), (0.40, 3.74, 0.40), (0.0, 3.80, 0.44)]
    mk.hull(ut, ring(2.82, 0, 0, 1.02, 0.56) + ring(3.40, 0, 0.02, 1.30, 0.66) + top + hump, "canvas")
    # camisa rasgada de arriba abajo, abierta y despareja: hueco en zigzag 0,12 hacia adentro, tres
    # costillas en el fondo (la parte de arriba la tapa el pañuelo)
    left = [(-0.06, 3.94), (-0.15, 3.80), (-0.11, 3.70), (-0.27, 3.58), (-0.21, 3.47), (-0.29, 3.34), (-0.17, 3.22), (-0.13, 3.08)]
    right = [(0.10, 3.92), (0.21, 3.78), (0.16, 3.66), (0.31, 3.54), (0.24, 3.43), (0.30, 3.30), (0.18, 3.19), (0.05, 3.05)]
    mk.carve(ut, "skin_dead_dark", prism=dict(profile=left + right[::-1], depth=0.24, plane="xy", center=(0, 0, -0.31)))
    for i, y in enumerate((3.26, 3.40, 3.54)):
        w = (0.34, 0.46, 0.46)[i]
        mk.hull(ut, [(-w / 2, y - 0.025, -0.16), (w / 2, y - 0.025, -0.16), (-w / 2, y + 0.025, -0.16),
                     (w / 2, y + 0.025, -0.16), (-w / 2 + 0.02, y, -0.26), (w / 2 - 0.02, y, -0.26)], "bone", detail=True)
    # mordida en el hombro derecho: falta un pedazo, con sangre alrededor
    mk.carve(ut, "blood_dry", points=mk.pts_ball((0.50, 3.98, -0.24), 0.12, scale=(1.1, 0.9, 1.0), subdiv=0))
    mk.paint(ut, "blood_dry", ball=((0.46, 3.84, -0.32), 0.10))
    mk.cyl(ut, (0, 4.12, -0.14), 0.17, 0.42, "skin_dead", rot=(-20, 0, 0), sides=10)            # cuello (igual que A)
    # pañuelo rojo: vuelta alrededor del cuello, nudo al costado derecho y un triángulo grande corrido a
    # la izquierda que cuelga por debajo de la mandíbula (de frente, la cabeza caída tapa el cuello)
    mk.cyl(ut, (0, 4.03, -0.12), 0.215, 0.13, "cloth_red", rot=(-20, 0, 0), sides=10, detail=True)
    mk.hull(ut, [(-0.30, 4.00, -0.27), (0.20, 4.02, -0.29), (-0.30, 3.98, -0.32), (0.20, 4.00, -0.34),
                 (-0.13, 3.58, -0.37), (-0.11, 3.58, -0.33)], "cloth_red", detail=True)
    mk.ball(ut, (0.22, 3.98, -0.30), 0.07, "cloth_red", subdiv=0, detail=True)
    for dx, ln in ((0.18, 0.18), (0.27, 0.14)):                                                       # puntas del nudo
        mk.prism(ut, [(-0.035, 0), (0.035, 0), (0.0, -ln)], 0.025, "cloth_red", plane="xy",
                 center=(dx, 3.96, -0.34), rot=(0, 0, 10), detail=True)

    # ---------------- cabeza: la de A, sin la oreja derecha ----------------
    hd = mk.part("Head", hu.NECK_P)
    hu.cranium(mk, hd, head)
    hu.zombie_face(mk, hd, head, hp)
    mk.hull(hd, head(mk.pts_box((-0.47, 4.70, -0.22), (0.08, 0.24, 0.16), top=(1, 0.7))), "skin_dead")     # oreja izquierda
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((0.50, 4.70, -0.22), (0.16, 0.20, 0.18))))              # oreja arrancada
    mk.hull(hd, head(mk.pts_box((0, 4.80, 0.12), (0.84, 0.48, 0.24), top=(0.9, 0.9))), "hair_dark")         # pelo corto atrás
    mk.hull(hd, head([(-0.45, 4.98, -0.32), (-0.49, 4.98, -0.10), (-0.46, 4.66, -0.30),
                      (-0.48, 4.70, -0.16)]), "hair_dark")                                                   # patilla (la derecha se fue con la oreja)
    mk.paint(hd, "blood_dry", ball=(hp((0.10, 4.20, -0.70)), 0.08))
    mk.paint(hd, "blood_dry", ball=(hp((-0.24, 4.42, -0.64)), 0.07))
    hu.eyes(mk, hp)

    # ---------------- sombrero de cowboy: ala alzada a los costados, copa con hendidura, mordisco ----------------
    base = hp((0, 5.06, -0.26))
    hat = mk.part("Acc_Hat", base)

    def hat_pts(pts):
        return hu.about(head(pts), base, (6, 0, -7))
    brim = [(0.80 * math.cos(a), 0.72 * math.sin(a) - 0.26) for a in [(i + 0.5) * math.pi / 8 for i in range(16)]]
    # ala del medio: prisma con el contorno del ala y el mordisco dentado adelante a la izquierda (sin
    # booleana: tallarlo dejaba la cara de abajo como un polígono cóncavo mal triangulado)
    def edge_z(x, sgn):
        return sgn * 0.72 * math.sqrt(1 - (x / 0.80) ** 2)
    bx, bz = -0.22, edge_z(-0.22, -1)
    notch = [(bx + r * math.cos(a), bz + r * math.sin(a)) for k in range(7)
             for a, r in [(math.radians(30 * k), 0.16 if k % 2 == 0 else 0.115)]]
    outline = ([(x, edge_z(x, -1)) for x in (0.46, 0.30, 0.15, 0.02)] + notch + [(x, edge_z(x, -1)) for x in (-0.40, -0.46)]
               + [(x, edge_z(x, 1)) for x in (-0.46, -0.30, -0.15, 0.0, 0.15, 0.30, 0.46)])
    rot = (Euler([math.radians(v) for v in (6, 0, -7)], "XYZ").to_matrix()
           @ Euler([math.radians(v) for v in (-10, 0, 0)], "XYZ").to_matrix()).to_euler("XYZ")
    mk.prism(hat, outline, 0.05, "cloth_brown", plane="xz", center=hat_pts([(0, 5.075, -0.26)])[0],
             rot=tuple(math.degrees(v) for v in rot))
    for s in (-1, 1):                                                                                        # alas alzadas 28°
        wing = [(x, z) for x, z in brim if s * x > 0.40] + [(s * 0.40, -0.26 - 0.60), (s * 0.40, -0.26 + 0.60)]
        pts = [(x, y, z) for x, z in wing for y in (5.05, 5.10)]
        mk.hull(hat, hat_pts(hu.about(pts, (s * 0.42, 5.075, -0.26), (0, 0, s * 28))), "cloth_brown")
    for s in (-1, 1):                                                                                        # copa: dos mitades, hendidura al medio
        half = [(x, y, z) for y, r in ((5.06 + 0.006 * (s < 0), 0.42 + 0.004 * (s < 0)), (5.36, 0.38 + 0.004 * (s < 0))) for x, z in   # mitades apenas distintas: sin caras coplanares al medio
                [(s * (r * abs(math.cos(a)) - 0.02), -0.26 + r * 0.92 * math.sin(a)) for a in [i * math.pi / 6 - math.pi / 2 for i in range(7)]]]
        half += [(s * 0.20, 5.52, -0.40), (s * 0.20, 5.52, -0.10), (s * 0.04, 5.44, -0.34), (s * 0.04, 5.46, -0.16)]
        mk.hull(hat, hat_pts(half), "cloth_brown", detail=True)      # detalle: la booleana del ala no la toca
    mk.hull(hat, hat_pts(hu.round_ring(5.08, 0, -0.26, 0.90, 0.82, n=12) + hu.round_ring(5.17, 0, -0.26, 0.88, 0.80, n=12)),
            "leather_dark", detail=True)                                                                      # cinta sudada

    # ---------------- brazos: mangas arremangadas (la izquierda rota), antebrazos al aire ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = hu.arm_joints(s)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1] + 0.10, sh[2]), (el[0], el[1] + 0.10, el[2]), 0.40, 0.42, 0.35, 0.36, "canvas")
        if side == "Right":     # manga arremangada: rollo grueso arriba del codo
            hu.limb(mk, ua, (el[0], el[1] + 0.22, el[2]), (el[0], el[1] + 0.02, el[2]), 0.40, 0.41, 0.40, 0.41, "canvas", over=0.0)
        else:                   # manga rota: termina en jirones que cuelgan sobre el codo
            for dx, dz, ln in ((-0.13, -0.10, 0.18), (0.13, -0.06, 0.12), (0.0, -0.17, 0.15), (-0.06, 0.16, 0.20)):
                mk.prism(ua, [(-0.07, 0), (0.07, 0), (0.0, -ln)], 0.03, "canvas", plane="xy",
                         center=(el[0] + dx, el[1] + 0.12, el[2] + dz), rot=(0, 0 if abs(dz) > 0.12 else 90, 0), detail=True)
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.26, 0.26, 0.21, 0.21, "skin_dead")
        hand = mk.part(f"{side}Hand", wr)
        hu.hand(mk, hand, s, broken_finger=(side == "Right"))

    # ---------------- piernas: pantalón azul, chaparreras con alas, botas gastadas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = hu.leg_joints(s)
        cx = hip[0]
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.50, 0.52, 0.40, 0.42, "cloth_blue")
        mk.hull(ul, chaps_ring(hu.HIP + 0.03, cx, 0.50, 0.52, s) + chaps_ring(hu.KNEE - 0.03, cx, 0.40, 0.42, s), "leather")
        mk.hull(ul, [(cx + s * 0.27, y, z) for y in (hu.HIP - 0.02, hu.KNEE - 0.02) for z in (-0.16, 0.14)]
                + [(cx + s * 0.38, hu.HIP - 0.10, -0.01), (cx + s * 0.40, hu.KNEE - 0.02, -0.01)], "leather")   # ala
        ll = mk.part(f"{side}LowerLeg", knee)
        hu.limb(mk, ll, knee, (cx, 0.70, 0), 0.40, 0.42, 0.32, 0.34, "cloth_blue")
        mk.hull(ll, chaps_ring(hu.KNEE + 0.03, cx, 0.42, 0.44, s) + chaps_ring(0.78, cx, 0.48, 0.50, s), "leather")
        mk.hull(ll, [(cx + s * 0.25, y, z) for y in (hu.KNEE + 0.03, 0.80) for z in (-0.14, 0.12)]
                + [(cx + s * 0.36, hu.KNEE + 0.0, -0.01), (cx + s * 0.42, 0.80, -0.01)], "leather")             # ala
        mk.hull(ll, ring(0.84, cx, 0, 0.42, 0.44) + ring(0.22, cx, 0, 0.36, 0.38), "leather_dark")              # caña
        mk.hull(ll, ring(0.70, cx, 0, 0.46, 0.48) + ring(0.80, cx, 0, 0.46, 0.48), "leather_dark")
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(cx + x, y, z) for x in (-0.17, 0.17) for y, z in
                     ((0.04, 0.18), (0.34, 0.16), (0.30, -0.16), (0.04, -0.48), (0.18, -0.46))], "leather_dark")
        mk.hull(ft, [(cx + x, y, z) for x in (-0.18, 0.18) for y, z in
                     ((0.0, 0.19), (0.06, 0.19), (0.0, -0.50), (0.06, -0.50))], "coal")                         # suela
        mk.carve(ft, "leather", points=mk.pts_box((cx + s * 0.10, 0.20, -0.42), (0.12, 0.14, 0.16), rot=(0, 30, 0)))  # punta gastada

"""
Receta de WST_Enemy_Walker_A, el caminante "hombre del pueblo" (prompt 004, Bloques A + D + H).

Brief
- Silueta que tiene que leerse a 40 studs: cabeza grande caída hacia adelante, hombros caídos (el
  izquierdo más bajo) con joroba, bombín torcido, brazo derecho sin manga, pie izquierdo descalzo.
- Medidas (Bloque D, H = 5,2): tobillo 0,26 · rodilla 1,30 · cadera 2,444 · cintura 2,86 ·
  codo 3,016 · muñeca 2,184 · hombro 3,952 · cuello 4,16. Cabeza de 1,04 (1/5 de H).
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes y Acc_Hat.
- Huecos tallados (no calcomanías): cuencas, boca, oreja arrancada, rotura del pecho, mordida del
  antebrazo. Color sobre la superficie con paint: mejillas, sangre, uñas, dedos.
- Inferido (sin concepto todavía): ancho de hombros 1,5, largo del pie 0,6, forma de la joroba.

Vueltas: 1) primera versión · 2) brazos adentro, cabeza y manos más grandes, chaleco entero ·
3) vena y sangre fuera del volumen · 4) huecos tallados, color pintado, cráneo y manos de 10 lados ·
5) dientes apoyados en la boca, cortadores más simples · 6) mejillas hundidas con la forma del cráneo
(pintar una cara grande la tiñe entera; tallarlas costaba 90 triángulos), sombrero más simple, costillas apoyadas.
"""

import math

from mathutils import Euler, Vector

ANKLE, KNEE, HIP, WAIST = 0.26, 1.30, 2.444, 2.86
ELBOW, WRIST, SHOULDER, NECK = 3.016, 2.184, 3.952, 4.16
SH_X, EL_X, WR_X, LEG_X = 0.80, 0.93, 1.05, 0.30
ARM_Z = -0.10                       # los brazos cuelgan un poco adelante (hombros caídos)
NECK_P = (0.0, NECK, -0.10)
HEAD_ROT = (-10, 0, 0)              # cabeza caída hacia adelante


def ring(y, cx, cz, w, d, ch=0.28):
    """Octógono horizontal (ancho w en x, profundidad d en z) a la altura y."""
    a, b, ca, cb = w / 2, d / 2, w / 2 * (1 - ch), d / 2 * (1 - ch)
    return [(cx + x, y, cz + z) for x, z in
            ((-ca, -b), (ca, -b), (a, -cb), (a, cb), (ca, b), (-ca, b), (-a, cb), (-a, -cb))]


def round_ring(y, cx, cz, w, d, n=10):
    """Polígono de n lados (elipse) a la altura y: formas más redondas que el octógono."""
    return [(cx + w / 2 * math.cos(2 * math.pi * (i + 0.5) / n), y, cz + d / 2 * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def about(points, pivot, rot):
    e = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    p = Vector(pivot)
    return [tuple(p + e @ (Vector(q) - p)) for q in points]


def head(pts):
    """Todo lo de la cabeza se adelanta 0,15 y cae 10° alrededor del cuello."""
    return about([(x, y, z - 0.15) for x, y, z in pts], NECK_P, HEAD_ROT)


def hp(p):
    return head([p])[0]


def limb(mk, part, top, bottom, wt, dt, wb, db, mat, over=0.05):
    (x1, y1, z1), (x2, y2, z2) = top, bottom
    mk.hull(part, ring(y1 + over, x1, z1, wt, dt) + ring(y2 - over, x2, z2, wb, db), mat)


def build(mk):
    # ---------------- torso ----------------
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.28, 0, 0, 1.02, 0.56) + ring(2.92, 0, 0, 1.08, 0.58), "cloth_blue")
    mk.hull(lt, ring(2.78, 0, 0, 1.13, 0.63) + ring(2.93, 0, 0, 1.13, 0.63), "leather_dark")   # cinturón
    mk.box(lt, (0.18, 2.86, -0.33), (0.14, 0.11, 0.04), "brass", detail=True)                 # hebilla

    ut = mk.part("UpperTorso", (0, WAIST, 0))
    top = [(-0.70, 3.90, -0.30), (-0.70, 3.90, 0.18), (0.72, 4.00, -0.30), (0.72, 4.00, 0.18),
           (-0.30, 4.02, -0.26), (0.30, 4.08, -0.26), (-0.30, 4.02, 0.14), (0.30, 4.08, 0.14)]
    hump = [(-0.40, 3.70, 0.40), (0.40, 3.74, 0.40), (0.0, 3.80, 0.44)]
    mk.hull(ut, ring(2.82, 0, 0, 1.02, 0.56) + ring(3.40, 0, 0.02, 1.30, 0.66) + top + hump, "cloth_white")
    # chaleco: espalda entera (con la joroba) + dos paneles de adelante, 0,04 por fuera de la camisa
    mk.hull(ut, [(x, y, z) for x in (-0.60, 0.60) for y, z in ((2.95, -0.05), (2.95, 0.34))]
            + [(-0.72, 3.82, -0.05), (0.72, 3.90, -0.05), (-0.72, 3.82, 0.24), (0.72, 3.90, 0.24),
               (-0.42, 3.70, 0.45), (0.42, 3.74, 0.45), (0.0, 3.80, 0.49), (-0.67, 3.40, 0.41), (0.67, 3.40, 0.41)],
            "cloth_brown")
    for s in (-1, 1):
        mk.hull(ut, [(s * 0.10, 2.95, -0.33), (s * 0.61, 2.95, -0.33), (s * 0.61, 2.95, 0.0),
                     (s * 0.22, 3.85, -0.37), (s * 0.73, 3.83 + 0.07 * (s > 0), -0.35),
                     (s * 0.73, 3.83 + 0.07 * (s > 0), 0.0), (s * 0.67, 3.40, -0.38), (s * 0.68, 3.40, 0.0)],
                "cloth_brown")
        # tiradores por encima del chaleco
        mk.hull(ut, [(s * 0.22, 2.92, -0.36), (s * 0.30, 2.92, -0.36), (s * 0.22, 2.92, -0.40), (s * 0.30, 2.92, -0.40),
                     (s * 0.34, 3.92, -0.37), (s * 0.42, 3.92, -0.37), (s * 0.34, 3.96, -0.41), (s * 0.42, 3.96, -0.41)],
                "leather_dark", detail=True)
    # camisa rota en el pecho: rotura en zigzag tallada 0,12 hacia adentro, costillas en el fondo
    rip = ([(-0.15, 3.30), (-0.17, 3.48), (-0.12, 3.70)]
           + [(p[0], p[1]) for p in mk.zigzag((-0.12, 3.70, 0), (0.13, 3.72, 0), 3, 0.07, (0, 1, 0))[1:]]
           + [(0.16, 3.50), (0.14, 3.30)]
           + [(p[0], p[1]) for p in mk.zigzag((0.14, 3.30, 0), (-0.15, 3.30, 0), 3, 0.06, (0, -1, 0))[1:-1]])
    mk.carve(ut, "skin_dead_dark", prism=dict(profile=rip, depth=0.24, plane="xy", center=(0, 0, -0.31)))
    for i, y in enumerate((3.38, 3.50, 3.62)):
        w = 0.24 - 0.03 * i
        mk.hull(ut, [(-w / 2, y - 0.025, -0.16), (w / 2, y - 0.025, -0.16), (-w / 2, y + 0.025, -0.16),
                     (w / 2, y + 0.025, -0.16), (-w / 2 + 0.02, y, -0.26), (w / 2 - 0.02, y, -0.26)], "bone", detail=True)
    mk.paint(ut, "blood_dry", ball=((0.06, 3.70, -0.31), 0.09))
    # cuello inclinado 20° hacia adelante, con sangre seca
    mk.cyl(ut, (0, 4.12, -0.14), 0.17, 0.42, "skin_dead", rot=(-20, 0, 0), sides=10)
    mk.paint(ut, "blood_dry", ball=((0.12, 4.06, -0.30), 0.09))

    # ---------------- cabeza ----------------
    hd = mk.part("Head", NECK_P)
    cranium = (round_ring(4.28, 0, -0.17, 0.66, 0.62) + round_ring(4.52, 0, -0.21, 0.80, 0.82)   # mejillas hundidas bajo los pómulos
               + round_ring(4.80, 0, -0.25, 0.94, 0.90) + round_ring(5.02, 0, -0.26, 0.84, 0.84)
               + round_ring(5.16, 0, -0.26, 0.56, 0.60))
    mk.hull(hd, head(cranium), "skin_dead")
    mk.hull(hd, head(mk.pts_box((0, 4.87, -0.66), (0.84, 0.12, 0.18), top=(0.9, 0.8))), "skin_dead")      # ceja
    mk.hull(hd, head([(0, 4.82, -0.68), (0, 4.62, -0.84), (-0.09, 4.60, -0.68), (0.09, 4.60, -0.68),
                      (0, 4.58, -0.71), (-0.05, 4.72, -0.70), (0.05, 4.72, -0.70)]), "skin_dead")           # nariz
    mk.hull(hd, head([(-0.29, 4.44, -0.60), (0.29, 4.44, -0.60), (-0.30, 4.46, -0.18), (0.30, 4.46, -0.18),
                      (-0.21, 4.18, -0.70), (0.21, 4.18, -0.70), (-0.24, 4.22, -0.16), (0.24, 4.22, -0.16),
                      (0, 4.15, -0.72)]), "skin_dead")                                                       # mandíbula caída
    mk.hull(hd, head(mk.pts_box((0.47, 4.70, -0.22), (0.08, 0.24, 0.16), top=(1, 0.7))), "skin_dead")       # oreja derecha
    mk.hull(hd, head(mk.pts_box((0, 4.86, 0.16), (0.80, 0.42, 0.18), top=(0.85, 0.9))), "hair_dark")        # pelo de atrás
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.45, 5.02, -0.30), (s * 0.49, 5.00, 0.02), (s * 0.45, 4.70, -0.10),
                          (s * 0.51, 4.78, -0.02), (s * 0.41, 4.98, -0.04)]), "hair_dark")                  # mechones
    # huecos tallados: cuencas, boca abierta, oreja arrancada
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.74, -0.74), 0.15, scale=(1.0, 0.75, 0.9), subdiv=0)))
    mouth = [(-0.22, 4.46), (-0.13, 4.52), (0.13, 4.53), (0.24, 4.47), (0.18, 4.38), (-0.17, 4.39)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.85, -0.50)]))
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((-0.50, 4.70, -0.22), (0.16, 0.20, 0.18))))
    # color sobre la superficie: sangre en la comisura y el mentón
    mk.paint(hd, "blood_dry", ball=(hp((0.24, 4.42, -0.64)), 0.07))
    mk.paint(hd, "blood_dry", ball=(hp((-0.08, 4.22, -0.70)), 0.08))
    # dientes de detalle, en el borde de la boca
    for i in range(5):
        x = -0.15 + 0.075 * i
        mk.hull(hd, head([(x - 0.032, 4.56, -0.66), (x + 0.032, 4.56, -0.66), (x - 0.02, 4.47, -0.66),
                          (x + 0.02, 4.47, -0.66), (x - 0.03, 4.56, -0.45), (x + 0.03, 4.56, -0.45),
                          (x, 4.48, -0.45)]), "bone", detail=True)
    for i in range(4):
        x = -0.11 + 0.075 * i
        mk.hull(hd, head([(x - 0.032, 4.36, -0.66), (x + 0.032, 4.36, -0.66), (x - 0.02, 4.44, -0.66),
                          (x + 0.02, 4.44, -0.66), (x - 0.03, 4.36, -0.45), (x + 0.03, 4.36, -0.45),
                          (x, 4.43, -0.45)]), "bone", detail=True)

    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.74, -0.60)), 0.08, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)

    # bombín aplastado y torcido
    hat_c = hp((0, 5.08, -0.27))
    hat = mk.part("Acc_Hat", hat_c)
    hat_pts = lambda pts: about(head(pts), hat_c, (0, 0, 12))  # noqa: E731
    brim = [(0.64 * math.cos(a), 5.06, -0.27 + 0.64 * math.sin(a)) for a in [i * math.pi / 5 for i in range(10)]]
    mk.hull(hat, hat_pts(brim + [(x, 5.10, z) for x, _, z in brim]), "cloth_black")
    crown = [(0.40 * math.cos(a), y, -0.27 + 0.40 * k * math.sin(a))
             for y, k in ((5.08, 1.0), (5.26, 0.95), (5.36, 0.7)) for a in [i * math.pi / 4 for i in range(8)]]
    crown = [(x * (0.8 if y > 5.3 and x > 0 else 1), y - (0.06 if x > 0.1 and y > 5.3 else 0), z) for x, y, z in crown]
    mk.hull(hat, hat_pts(crown), "cloth_black")
    mk.hull(hat, hat_pts(round_ring(5.10, 0, -0.27, 0.84, 0.84, n=8) + round_ring(5.16, 0, -0.27, 0.84, 0.84, n=8)), "leather_dark")

    # ---------------- brazos ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)
        ua = mk.part(f"{side}UpperArm", sh)
        limb(mk, ua, (sh[0], sh[1] + 0.10, sh[2]), el, 0.40, 0.42, 0.34, 0.34, "cloth_white")
        la = mk.part(f"{side}LowerArm", el)
        hand = mk.part(f"{side}Hand", wr)
        if side == "Right":
            # manga arrancada en el codo: jirones y antebrazo flaco al aire
            for dz, dx in ((-0.14, 0.05), (0.10, -0.06), (0.0, 0.14)):
                mk.prism(ua, [(-0.07, 0), (0.07, 0), (0.0, -0.16)], 0.03, "cloth_white", plane="xy",
                         center=(el[0] + dx, el[1] - 0.02, el[2] + dz), detail=True)
            limb(mk, la, el, wr, 0.26, 0.26, 0.21, 0.21, "skin_dead")
        else:
            # manga hasta media altura; abajo, la mordida arranca un pedazo del antebrazo
            mid = (s * (EL_X + 0.06), 2.62, ARM_Z)
            limb(mk, la, el, mid, 0.30, 0.30, 0.29, 0.29, "cloth_white")
            limb(mk, la, mid, wr, 0.22, 0.24, 0.20, 0.21, "skin_dead")
            mk.carve(la, "blood_dry", points=mk.pts_ball((mid[0] - 0.14, 2.45, ARM_Z), 0.09, scale=(1, 1.4, 1), subdiv=0))
            for dz in (-0.10, 0.08):
                mk.prism(la, [(-0.06, 0), (0.06, 0), (0.0, -0.14)], 0.03, "cloth_white", plane="xy",
                         center=(mid[0] + 0.02, mid[1] + 0.01, ARM_Z + dz), detail=True)
        # mano grande y redondeada: mitón y pulgar, uñas sucias pintadas
        hx = wr[0] + s * 0.02
        mk.hull(hand, round_ring(WRIST + 0.05, hx, ARM_Z, 0.21, 0.35) + round_ring(WRIST - 0.20, hx + s * 0.01, ARM_Z, 0.22, 0.37)
                + round_ring(WRIST - 0.46, hx + s * 0.02, ARM_Z, 0.17, 0.29), "skin_dead")
        mk.box(hand, (hx - s * 0.07, WRIST - 0.15, ARM_Z - 0.19), (0.10, 0.23, 0.10), "skin_dead", rot=(-15, 0, 0))
        mk.paint(hand, "skin_dead_dark", box=((hx, WRIST - 0.46, ARM_Z), (0.4, 0.08, 0.5)))

    # ---------------- piernas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = mk.part(f"{side}UpperLeg", hip)
        limb(mk, ul, hip, knee, 0.50, 0.52, 0.40, 0.42, "cloth_blue")
        ll = mk.part(f"{side}LowerLeg", knee)
        ft = mk.part(f"{side}Foot", ankle)
        if side == "Left":
            # pantalón roto en la rodilla, canilla flaca, descalzo
            mk.hull(ll, ring(KNEE + 0.06, hip[0], 0, 0.42, 0.44) + ring(KNEE - 0.16, hip[0], 0, 0.40, 0.42), "cloth_blue")
            for dx, dz in ((-0.12, -0.18), (0.10, -0.17), (0.0, 0.19), (0.17, 0.05)):
                mk.prism(ll, [(-0.07, 0), (0.07, 0), (0.0, -0.14)], 0.03, "cloth_blue", plane="xy",
                         center=(hip[0] + dx, KNEE - 0.16, dz), detail=True)
            limb(mk, ll, (hip[0], KNEE - 0.10, 0), ankle, 0.24, 0.26, 0.20, 0.22, "skin_dead")
            mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.14, 0.14) for y, z in
                         ((0.0, 0.16), (0.30, 0.12), (0.30, -0.12), (0.0, -0.44), (0.14, -0.44))], "skin_dead")
            mk.paint(ft, "skin_dead_dark", box=((hip[0], 0.07, -0.43), (0.4, 0.2, 0.06)))     # dedos sucios
        else:
            limb(mk, ll, knee, (hip[0], 0.70, 0), 0.40, 0.42, 0.32, 0.34, "cloth_blue")
            mk.hull(ll, ring(0.84, hip[0], 0, 0.42, 0.44) + ring(0.22, hip[0], 0, 0.36, 0.38), "leather_dark")  # caña
            mk.hull(ll, ring(0.78, hip[0], 0, 0.46, 0.48) + ring(0.88, hip[0], 0, 0.46, 0.48), "leather_dark")
            mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.17, 0.17) for y, z in
                         ((0.04, 0.18), (0.34, 0.16), (0.30, -0.16), (0.04, -0.48), (0.18, -0.46))], "leather_dark")
            mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.18, 0.18) for y, z in
                         ((0.0, 0.19), (0.05, 0.19), (0.0, -0.50), (0.05, -0.50))], "coal")        # suela

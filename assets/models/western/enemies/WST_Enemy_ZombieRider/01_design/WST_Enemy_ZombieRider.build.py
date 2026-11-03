"""
Receta de WST_Enemy_ZombieRider, el jinete zombie (prompt 055, Bloques A + D + H).

Brief
- Silueta a 40 studs (persiguiendo a caballo): sombrero de ala enorme (2,2) y copa alta en punta,
  poncho mostaza con dos bandas rojas que tapa el torso hasta la cadera con el ruedo dentado,
  chaparreras, espuelas grandes, el lazo enrollado en la cadera derecha.
- Medidas (Bloque D, H = 5,3): tobillo 0,265 · rodilla 1,325 · cadera 2,491 · cintura 2,915 · codo 3,074 ·
  muñeca 2,226 · hombro 4,028 · cuello 4,24. Cabeza de ~1,04 (la del caminante escalada 1,02).
- Piezas: las 15 de R15 (de pie en I-pose; la pose de montar es animación), Eyes (oscuros), Acc_Hat
  (origen en la base de la copa) y Acc_Lasso (origen donde cuelga del cinto).
- Cabeza: la del caminante (hu.cranium y hu.zombie_face) con la piel de la mandíbula arrancada del
  lado izquierdo: hueco tallado con sangre y muelas de hueso a la vista.
- Poncho (detalle sobre la camisa de lona): un casco que cubre el torso, con hombreras que tapan el
  arranque de los brazos y el ruedo dentado a la altura de la cadera; dos bandas rojas en relieve.
- Inferido: hombreras del poncho hasta x = ±0,95 (los brazos salen por debajo), chaparreras sin alas,
  cinta del sombrero de cuero, tres roturas en el ala, lazo de dos vueltas de 0,24 de radio.

Vueltas: 1) primera versión · 2) coplanares: banda roja de abajo con la base de la camisa (y = 2,86),
espalda de la hebilla con el pantalón, frente de la chaparrera a 0,002 del pantalón de la cadera
(ahora 0,05 arriba), cuerdas de las dos vueltas del lazo (la segunda girada 25°); una muela flotaba al
costado de la mandíbula · 3) dos muelas compartían puntos (bordes no manifold) · 4) el poncho parecía
una caja: hombros caídos a 3,80-3,98 y punta en V (2,30 al medio, 2,62 a los costados); el lazo
quedaba tapado por el poncho: cuelga más abajo y afuera, con una tira al cinto · 5) la joroba de la
camisa asomaba por la espalda del poncho; bandas que siguen la espalda; espuela de 8 puntas.

Revisión
- 2028 triángulos contra 1600 (+27 %): sombrero de ala enorme con roturas (prisma de 24 lados) y copa
  alta (182), lazo de dos vueltas (182), cara con la mandíbula descarnada y muelas (552).
- Medidas: 5,75 de alto con la copa del sombrero (H = 5,3 sin él), ala de 2,16.
- A 96 px se lee: sombrero ancho, poncho mostaza con dos bandas rojas, chaparreras.
"""

import math

from mathutils import Euler

import humanoid as hu

H = 5.3
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH_X, EL_X, WR_X, LEG_X, ARM_Z = 0.80, 0.93, 1.05, 0.30, -0.10
NECK_P = (0.0, NECK, -0.12)
NECK_W = (0.0, hu.NECK, -0.10)
HEAD_K, HEAD_FWD, HEAD_TILT = 1.02, 0.15, -9
ring, round_ring = hu.ring, hu.round_ring


def head(pts):
    out = [(x * HEAD_K, NECK_P[1] + (y - NECK_W[1]) * HEAD_K, NECK_P[2] + (z - NECK_W[2]) * HEAD_K - HEAD_FWD)
           for x, y, z in pts]
    return hu.about(out, NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def chaps_ring(y, cx, w, d, s, out=0.035):
    r = ring(y, cx, 0, w + 2 * out, d + 2 * out)
    return [r[i] for i in ((0, 1, 2, 3) if s > 0 else (6, 7, 0, 1))]


def bony_hand(mk, part, s, wx, wrist, z):
    mk.hull(part, round_ring(wrist + 0.05, wx, z, 0.20, 0.33) + round_ring(wrist - 0.20, wx + s * 0.01, z, 0.21, 0.35)
            + round_ring(wrist - 0.45, wx + s * 0.02, z, 0.16, 0.27), "skin_dead")
    mk.box(part, (wx - s * 0.07, wrist - 0.15, z - 0.18), (0.09, 0.22, 0.09), "skin_dead", rot=(-15, 0, 0))
    mk.paint(part, "skin_dead_dark", box=((wx, wrist - 0.45, z), (0.4, 0.08, 0.5)))


def c_shape(r_in, r_out, a0, a1, n=5):
    """Perfil de medio anillo (forma de C) entre los ángulos a0 y a1, en grados."""
    angs = [math.radians(a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]
    return [(r_out * math.cos(a), r_out * math.sin(a)) for a in angs] + [(r_in * math.cos(a), r_in * math.sin(a)) for a in reversed(angs)]


def build(mk):
    # ---------------- cadera: pantalón y cinto ----------------
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.33, 0, 0, 1.00, 0.56) + ring(2.97, 0, 0, 1.06, 0.58), "cloth_blue")
    mk.hull(lt, ring(2.80, 0, 0, 1.12, 0.63) + ring(2.94, 0, 0, 1.12, 0.63), "leather_dark")
    mk.box(lt, (0.0, 2.87, -0.325), (0.16, 0.12, 0.04), "steel_light", detail=True)

    # ---------------- torso: camisa de lona y poncho mostaza con bandas rojas ----------------
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    top = [(-0.68, 3.86, -0.30), (-0.68, 3.86, 0.16), (0.70, 3.94, -0.30), (0.70, 3.94, 0.16),
           (-0.28, 3.98, -0.26), (0.28, 4.04, -0.26), (-0.28, 3.98, 0.12), (0.28, 4.04, 0.12)]
    hump = [(-0.38, 3.66, 0.38), (0.38, 3.70, 0.38), (0.0, 3.76, 0.42)]
    mk.hull(ut, ring(2.86, 0, 0, 1.00, 0.56) + ring(3.42, 0, 0.02, 1.26, 0.64) + top + hump, "canvas")
    mk.cyl(ut, (0, 4.06, -0.14), 0.165, 0.42, "skin_dead", rot=(-20, 0, 0), sides=10)              # cuello
    mk.paint(ut, "blood_dry", ball=((-0.10, 4.02, -0.30), 0.08))
    poncho = (hu.round_ring(4.08, 0, -0.06, 0.62, 0.52, n=10)
              + [(s * 0.95, y, z) for s in (-1, 1) for y, z in ((3.98, -0.30), (3.98, 0.28), (3.80, -0.32), (3.80, 0.30))]
              + [(s * 0.68, 3.60, z) for s in (-1, 1) for z in (-0.41, 0.48)] + [(0.0, 3.86, 0.47)]   # tapa la joroba
              + [(s * 0.64, 2.62, z) for s in (-1, 1) for z in (-0.37, 0.39)]
              + [(0.0, 2.30, -0.41), (0.0, 2.30, 0.43)])                  # hombros caídos y la punta en V adelante y atrás
    mk.hull(ut, poncho, "paint_mustard", detail=True)
    for y, zb in ((3.30, 0.50), (2.96, 0.49)):                                                      # bandas rojas en relieve
        mk.hull(ut, [(s * x, y + dy, z) for s in (-1, 1) for dy in (-0.06, 0.06)
                     for x, z in ((0.70, -0.40), (0.70, zb - 0.04), (0.42, -0.435), (0.42, zb))],
                "cloth_red", detail=True)
    for k in range(5):                                         # ruedo dentado: cuelga del borde en V del poncho
        x = -0.52 + 0.26 * k
        t = 1 - abs(x) / 0.64
        y_edge = 2.30 + 0.32 * (1 - t)
        for z, sgn in ((-(0.37 + 0.04 * t), -1), (0.39 + 0.04 * t, 1)):
            mk.prism(ut, [(-0.10, 0), (0.10, 0), (0.02, -0.16 - 0.05 * (k % 2))], 0.03, "paint_mustard", plane="xy",
                     center=(x, y_edge + 0.03, z), detail=True)

    # ---------------- cabeza: sin la piel de la mandíbula a la izquierda ----------------
    hd = mk.part("Head", NECK_P)
    hu.cranium(mk, hd, head)
    hu.zombie_face(mk, hd, head, hp)
    for s in (-1, 1):
        mk.hull(hd, head(mk.pts_box((s * 0.47, 4.70, -0.22), (0.08, 0.24, 0.16), top=(1, 0.7))), "skin_dead")   # orejas
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((-0.27, 4.32, -0.58), (0.16, 0.24, 0.36))))                  # mandíbula descarnada
    for (y0, y1), xs in (((4.47, 4.34), (-0.22, -0.28)), ((4.17, 4.30), (-0.16, -0.215))):   # muelas, raíz en la pared
        for x in xs:
            mk.hull(hd, head([(x - 0.025, y0, -0.64), (x + 0.025, y0, -0.64), (x - 0.02, y1, -0.64), (x + 0.02, y1, -0.64),
                              (x - 0.025, y0, -0.38), (x + 0.025, y0, -0.38), (x, y1, -0.38)]), "bone", detail=True)
    mk.hull(hd, head(mk.pts_box((0, 4.82, 0.14), (0.82, 0.40, 0.20), top=(0.9, 0.9))), "hair_dark")             # pelo atrás
    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.74, -0.60)), 0.075, "coal", scale=(1.0, 0.8, 0.8), subdiv=0)

    # ---------------- sombrero de ala enorme y copa alta, roto en el borde ----------------
    base = hp((0, 5.04, -0.26))
    hat = mk.part("Acc_Hat", base)

    def hat_pts(pts):
        return hu.about(head(pts), base, (4, 0, 5))
    rot = (Euler([math.radians(v) for v in (4, 0, 5)], "XYZ").to_matrix()
           @ Euler([math.radians(v) for v in (HEAD_TILT, 0, 0)], "XYZ").to_matrix()).to_euler("XYZ")
    rot = tuple(math.degrees(v) for v in rot)
    outline = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        r = 1.08
        if i in (3, 10, 17):          # tres roturas: muesca en V
            outline.append(((r - 0.20) * math.cos(a), (r - 0.20) * math.sin(a) * 0.96))
            continue
        outline.append((r * math.cos(a), r * math.sin(a) * 0.96))
    mk.prism(hat, outline, 0.05, "canvas", plane="xz", center=hat_pts([(0, 5.06, -0.26)])[0], rot=rot)       # ala
    mk.hull(hat, hat_pts(round_ring(5.08, 0, -0.26, 0.86, 0.82, n=10) + round_ring(5.40, 0, -0.26, 0.64, 0.60, n=10)
                         + round_ring(5.62, 0, -0.26, 0.34, 0.32, n=8) + [(0, 5.70, -0.26)]), "canvas")      # copa alta
    mk.hull(hat, hat_pts(round_ring(5.09, 0, -0.26, 0.90, 0.86, n=10) + round_ring(5.18, 0, -0.26, 0.86, 0.82, n=10)),
            "leather", detail=True)                                                                         # cinta

    # ---------------- lazo enrollado en la cadera derecha ----------------
    lasso_o = (0.585, 2.82, 0.0)
    lasso = mk.part("Acc_Lasso", lasso_o)
    for k, (dx, dy, dz, r) in enumerate(((0.0, 2.25, 0.0, 0.24), (0.035, 2.21, 0.03, 0.22))):   # cuelga abajo del poncho
        for a0, a1, depth in ((-10, 190, 0.070), (170, 370, 0.064)):    # dos C que se encastran, profundidades distintas
            a0, a1 = a0 + 25 * k, a1 + 25 * k                               # la segunda vuelta girada: sus cuerdas no coinciden
            mk.prism(lasso, c_shape(r - 0.07, r, a0, a1, n=5 + k), depth - 0.004 * k, "rope", plane="zy",
                     center=(0.66 + dx, dy, dz))
    mk.hull(lasso, [(0.675 + dx, y, z) for dx in (-0.03, 0.03) for y, z in ((2.05, -0.06), (2.05, -0.01))]
            + [(0.69 + dx, 1.80, -0.10) for dx in (-0.03, 0.03)] + [(0.69, 1.80, -0.05)], "rope")             # punta que cuelga
    mk.hull(lasso, [(x, y, z) for x in (0.55, 0.63) for y in (2.90, 2.44) for z in (-0.04, 0.04)]
            + [(0.66, 2.44, -0.04), (0.66, 2.44, 0.04)], "leather_dark")                                        # tira del cinto al lazo

    # ---------------- brazos: mangas de lona; manos huesudas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1], sh[2]), el, 0.38, 0.40, 0.32, 0.33, "canvas")              # arranque bajo la hombrera del poncho
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.30, 0.30, 0.25, 0.25, "canvas")
        hu.limb(mk, la, (wr[0], wr[1] + 0.12, ARM_Z), (wr[0], wr[1] + 0.02, ARM_Z), 0.29, 0.29, 0.29, 0.29, "canvas", over=0.0)
        hand = mk.part(f"{side}Hand", wr)
        bony_hand(mk, hand, s, wr[0] + s * 0.02, WRIST, ARM_Z)

    # ---------------- piernas: chaparreras, botas con espuelas grandes ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        cx = hip[0]
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.48, 0.50, 0.38, 0.40, "cloth_blue")
        mk.hull(ul, chaps_ring(HIP + 0.03, cx, 0.48, 0.50, s, 0.05) + chaps_ring(KNEE - 0.03, cx, 0.38, 0.40, s), "leather")   # arriba 0,05: no coincide con el pantalón de la cadera
        ll = mk.part(f"{side}LowerLeg", knee)
        hu.limb(mk, ll, knee, (cx, 0.72, 0), 0.38, 0.40, 0.30, 0.32, "cloth_blue")
        mk.hull(ll, chaps_ring(KNEE + 0.03, cx, 0.40, 0.42, s) + chaps_ring(0.80, cx, 0.46, 0.48, s), "leather")
        mk.hull(ll, ring(0.84, cx, 0, 0.40, 0.42) + ring(0.22, cx, 0, 0.34, 0.36), "leather_dark")
        mk.hull(ll, ring(0.72, cx, 0, 0.44, 0.46) + ring(0.82, cx, 0, 0.44, 0.46), "leather_dark")
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(cx + x, y, z) for x in (-0.16, 0.16) for y, z in ((0.10, 0.17), (0.32, 0.15), (0.26, -0.16))]
                + [(cx - 0.08, 0.06, -0.50), (cx + 0.08, 0.06, -0.50), (cx, 0.14, -0.48)], "leather_dark")
        mk.hull(ft, [(cx + x, y, z) for x in (-0.13, 0.13) for y, z in ((0.0, 0.18), (0.13, 0.18), (0.0, 0.0), (0.13, 0.0))]
                + [(cx - 0.07, 0.0, -0.48), (cx + 0.07, 0.0, -0.48), (cx, 0.08, -0.50),
                   (cx - 0.14, 0.09, -0.12), (cx + 0.14, 0.09, -0.12)], "leather_dark")
        star = [((0.13 if i % 2 == 0 else 0.045) * math.cos(math.pi * i / 4), (0.13 if i % 2 == 0 else 0.045) * math.sin(math.pi * i / 4))
                for i in range(8)]
        mk.prism(ft, star, 0.025, "steel_light", plane="zy", center=(cx, 0.13, 0.36), detail=True)          # rodaja
        mk.box(ft, (cx, 0.13, 0.25), (0.035, 0.035, 0.18), "steel_light", detail=True)                      # brazo de la espuela

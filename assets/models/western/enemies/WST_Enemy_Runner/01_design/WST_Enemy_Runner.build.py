"""
Receta de WST_Enemy_Runner, el corredor (prompt 023, Bloques A + D + H).

Brief
- Silueta a 40 studs, distinta del caminante: flaco y largo, piernas largas, sin sombrero, pelo largo
  revuelto que cuelga, el torso tirado hacia adelante (cuello y cabeza más adelante que el caminante),
  la camisa abierta colgando en tiras, manos de garra largas.
- Medidas (H = 5,4; cadera a 0,50 H por las piernas un 5 % más largas): tobillo 0,27 · rodilla 1,43 ·
  cadera 2,70 · cintura 3,02 · codo 3,13 · muñeca 2,20 · hombro 4,10 · cuello 4,32. Cabeza de ~1,06.
  Grosores de torso y miembros 0,8 × los del caminante (brazo 0,32 → 0,25, muslo 0,40 → 0,32).
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes (oscuros: coal).
- Tallado: cuencas, boca entreabierta, mordida del cuello. Costillas: tres crestas en V sobre el pecho
  al aire. Pintado: sangre en la boca y el cuello, uñas de las garras, dedos de los pies.
- Lo que no se talla (pelo, camisa, tiras) va como detalle: así la booleana de la cara y del cuello no
  lo une con la piel y no suma triángulos.
- Inferido: cintura a 0,56 H (a 0,55 la LowerTorso quedaba de 0,27), muñeca a 0,41 H (brazos largos),
  hombros 0,66 (flaco), brazos 0,12 más adelante que el caminante (torso tirado adelante), cinturón de
  soga, forma del pelo.

Vueltas: 1) primera versión · 2) costillas en V en relieve (el hueco rectangular del pecho se leía como
una puerta), tiras de camisa más anchas, torso más tirado adelante, sin pómulos en caja, boca menos
abierta (el prompt dice entreabierta), pelo y camisa como detalle (1954 -> 1476) · 3) espalda y
paneles de la camisa a 0,035 y 0,045 (compartían puntos: z-fighting y bordes no manifold) y corridos
también en y (caras de los hombros coplanares) · 4) pecho hundido con fondo oscuro y costillas en V
adentro (en relieve sobre la piel no se veían).

Revisión
- 1490 triángulos contra 1400 (+6 %): la cara (boca entreabierta tallada, 9 dientes, cuencas) y el pecho
  hundido con las costillas. Pelo y camisa van como detalle: la booleana no los une (la cabeza bajó de
  826 a ~500).
- Medidas: 5,43 de alto (H = 5,4 más el pelo), 1,96 de ancho con los brazos.
- Sin avisos de la revisión. Inferido: cintura 0,56 H, muñeca 0,41 H, hombros 0,66, soga de cinturón,
  pelo en cortina despareja.
"""

import humanoid as hu

ANKLE, KNEE, HIP, WAIST = 0.27, 1.43, 2.70, 3.02
ELBOW, WRIST, SHOULDER, NECK = 3.13, 2.20, 4.10, 4.32
SH_X, EL_X, WR_X, LEG_X = 0.66, 0.77, 0.87, 0.26
ARM_Z = -0.22
NECK_P = (0.0, NECK, -0.24)
NECK_W = (0.0, hu.NECK, -0.10)      # cuello del caminante: la cabeza se dibuja en sus medidas y se trae acá
HEAD_K, HEAD_FWD, HEAD_TILT = 1.05, 0.20, -6

ring, round_ring = hu.ring, hu.round_ring


def head(pts):
    """Medidas de la cabeza del caminante -> escaladas 1,05, en el cuello del corredor, 0,20 adelante y caída 6°."""
    out = [(x * HEAD_K, NECK_P[1] + (y - NECK_W[1]) * HEAD_K, NECK_P[2] + (z - NECK_W[2]) * HEAD_K - HEAD_FWD)
           for x, y, z in pts]
    return hu.about(out, NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def grow(points, dx, dz, zc):
    """Los mismos puntos, dx más afuera en x y dz más afuera en z (respecto de zc): una capa encima.
    Arriba de los hombros (y > 3,9) sube dz y abajo (y < 3,0) baja dz: sin caras horizontales coplanares."""
    return [(x + (dx if x > 0 else -dx if x < 0 else 0), y + (dz if y > 3.9 else -dz if y < 3.0 else 0),
             z + (dz if z > zc else -dz)) for x, y, z in points]


def build(mk):
    # ---------------- cadera: pantalón y cinturón de soga ----------------
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.50, 0, 0, 0.74, 0.44) + ring(3.07, 0, -0.02, 0.80, 0.46), "cloth_blue")
    mk.hull(lt, ring(2.94, 0, -0.02, 0.86, 0.52) + ring(3.04, 0, -0.02, 0.86, 0.52), "rope")
    mk.hull(lt, [(0.20, 2.96, -0.29), (0.27, 2.96, -0.29), (0.20, 3.02, -0.29), (0.27, 3.02, -0.29),
                 (0.22, 2.74, -0.32), (0.25, 2.74, -0.32), (0.23, 2.98, -0.26)], "rope", detail=True)   # punta que cuelga

    # ---------------- torso tirado adelante: pecho flaco al aire, camisa abierta ----------------
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    r0, r1 = ring(2.97, 0, -0.02, 0.78, 0.44), ring(3.55, 0, -0.12, 0.96, 0.52)
    top = [(-0.58, 4.02, -0.42), (-0.58, 4.02, -0.02), (0.60, 4.08, -0.42), (0.60, 4.08, -0.02),
           (-0.26, 4.14, -0.38), (0.26, 4.18, -0.38), (-0.26, 4.14, -0.04), (0.26, 4.18, -0.04)]
    hump = [(-0.30, 3.80, 0.24), (0.30, 3.84, 0.24), (0.0, 3.92, 0.28)]
    skin = r0 + r1 + top + hump
    mk.hull(ut, skin, "skin_dead")
    # camisa 0,04 por fuera: espalda y costados enteros; adelante solo los costados (queda abierta)
    back, front = grow(skin, 0.035, 0.035, -0.12), grow(skin, 0.045, 0.045, -0.12)   # 0,01 entre capas: no coplanares
    mk.hull(ut, [p for p in back if p[2] > -0.20], "cloth_white", detail=True)
    for s in (-1, 1):
        mk.hull(ut, [p for p in front if s * p[0] > 0.24], "cloth_white", detail=True)
        # tiras anchas que cuelgan del ruedo, con la punta rota en diagonal
        for x, z, ln in ((0.36, -0.30, 0.34), (0.45, -0.16, 0.20), (0.30, 0.24, 0.26)):
            prof = [(-0.07, 0), (0.07, 0), (0.05, -ln + 0.06), (-0.02, -ln)]
            mk.prism(ut, [(s * a, b) for a, b in prof], 0.03, "cloth_white", plane="xy",
                     center=(s * x, 3.02, z), rot=(0, s * 25 if z < 0 else 0, 0), detail=True)
    # pecho hundido: hueco 0,05 con fondo oscuro, los costados escondidos bajo la camisa y el borde de
    # abajo en arco (dos mitades convexas); adentro, tres costillas en V que bajan desde el esternón
    def floor(y, side=0.0):             # fondo del hueco: 0,05 detrás del frente del pecho (que se tira adelante)
        f = -0.24 - 0.14 * (y - 2.97) / 0.58 if y < 3.55 else -0.38 - 0.04 * (y - 3.55) / 0.5
        return f + 0.05 + side
    for s in (-1, 1):
        out = [(s * 0.36, 3.86, 0), (s * 0.36, 3.30, 0.02), (-s * 0.01, 3.86, 0), (-s * 0.01, 3.45, 0)]
        mk.carve(ut, "skin_dead_dark", points=[(x, y, floor(y, d)) for x, y, d in out] + [(x, y, -0.80) for x, y, _ in out])
    for i, y in enumerate((3.74, 3.62, 3.50)):
        for s in (-1, 1):
            a, b = (s * 0.02, y, floor(y)), (s * (0.36 - 0.02 * i), y - 0.12, floor(y - 0.12, 0.02))
            mk.hull(ut, [(a[0], a[1] + 0.035, a[2] + 0.02), (a[0], a[1] - 0.035, a[2] + 0.02), (a[0], a[1], a[2] - 0.042),
                         (b[0], b[1] + 0.03, b[2] + 0.02), (b[0], b[1] - 0.03, b[2] + 0.02), (b[0], b[1], b[2] - 0.035)],
                    "skin_dead", detail=True)
    # cuello flaco tirado 25° adelante, con la mordida tallada
    mk.cyl(ut, (0, 4.28, -0.28), 0.135, 0.46, "skin_dead", rot=(-25, 0, 0), sides=10)
    mk.carve(ut, "blood_dry", points=mk.pts_ball((0.13, 4.30, -0.37), 0.08, scale=(1, 1.3, 1), subdiv=0))
    mk.paint(ut, "blood_dry", ball=((0.12, 4.15, -0.37), 0.08))

    # ---------------- cabeza: demacrada, mandíbula entreabierta, pelo largo ----------------
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.30, 0, -0.17, 0.60, 0.58) + round_ring(4.52, 0, -0.21, 0.70, 0.80)
                     + round_ring(4.80, 0, -0.25, 0.90, 0.88) + round_ring(5.02, 0, -0.26, 0.82, 0.84)
                     + round_ring(5.16, 0, -0.26, 0.54, 0.58)), "skin_dead")      # mejillas muy hundidas
    mk.hull(hd, head(mk.pts_box((0, 4.87, -0.66), (0.80, 0.12, 0.18), top=(0.9, 0.8))), "skin_dead")    # ceja
    mk.hull(hd, head([(0, 4.82, -0.68), (0, 4.63, -0.83), (-0.08, 4.61, -0.68), (0.08, 4.61, -0.68),
                      (0, 4.59, -0.71), (-0.04, 4.72, -0.70), (0.04, 4.72, -0.70)]), "skin_dead")       # nariz fina
    mk.hull(hd, head([(-0.27, 4.42, -0.58), (0.27, 4.42, -0.58), (-0.28, 4.44, -0.18), (0.28, 4.44, -0.18),
                      (-0.18, 4.12, -0.65), (0.18, 4.12, -0.65), (-0.21, 4.16, -0.16), (0.21, 4.16, -0.16),
                      (0, 4.09, -0.67)]), "skin_dead")                                                    # mandíbula caída
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.74, -0.74), 0.16, scale=(1.0, 0.78, 0.9), subdiv=0)))
    mouth = [(-0.20, 4.44), (-0.12, 4.53), (0.12, 4.54), (0.21, 4.45), (0.15, 4.32), (-0.14, 4.33)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.85, -0.48)]))
    mk.paint(hd, "blood_dry", ball=(hp((-0.20, 4.38, -0.60)), 0.07))
    mk.paint(hd, "blood_dry", ball=(hp((0.06, 4.16, -0.65)), 0.07))
    for i in range(5):                          # dientes de arriba, colgando del borde de la boca
        x = -0.13 + 0.065 * i
        mk.hull(hd, head([(x - 0.028, 4.57, -0.64), (x + 0.028, 4.57, -0.64), (x - 0.018, 4.48, -0.64),
                          (x + 0.018, 4.48, -0.64), (x - 0.026, 4.57, -0.44), (x + 0.026, 4.57, -0.44),
                          (x, 4.49, -0.44)]), "bone", detail=True)
    for i in range(4):                          # de abajo, saliendo de la mandíbula
        x = -0.10 + 0.066 * i
        mk.hull(hd, head([(x - 0.028, 4.29, -0.63), (x + 0.028, 4.29, -0.63), (x - 0.018, 4.38, -0.63),
                          (x + 0.018, 4.38, -0.63), (x - 0.026, 4.29, -0.44), (x + 0.026, 4.29, -0.44),
                          (x, 4.37, -0.44)]), "bone", detail=True)
    # pelo (detalle): casquete y una cortina larga y despareja atrás, mechones a los costados y flequillo
    mk.hull(hd, head(round_ring(4.86, 0, -0.06, 0.96, 0.74) + round_ring(5.06, 0, -0.22, 0.92, 0.92)
                     + round_ring(5.22, 0, -0.24, 0.62, 0.68)), "hair_dark", detail=True)
    for x0, x1, y0 in ((-0.44, 0.03, 4.02), (-0.03, 0.44, 4.16)):
        mk.hull(hd, head([(x0, 5.00, -0.10), (x1, 5.00, -0.10), (x0, 5.00, 0.14), (x1, 5.00, 0.14),
                          (x0 + 0.04, y0 + 0.14, 0.14), (x1 - 0.04, y0 + 0.14, 0.14), ((x0 + x1) / 2, y0, 0.18),
                          (x0 + 0.06, y0 + 0.20, 0.04), (x1 - 0.06, y0 + 0.20, 0.04)]), "hair_dark", detail=True)
    for s, y0 in ((-1, 4.36), (1, 4.50)):
        mk.hull(hd, head([(s * 0.42, 5.04, -0.40), (s * 0.48, 5.04, -0.14), (s * 0.40, 5.00, -0.08),
                          (s * 0.48, y0, -0.30), (s * 0.45, y0 + 0.08, -0.22)]), "hair_dark", detail=True)
    mk.hull(hd, head([(-0.32, 5.10, -0.54), (0.06, 5.14, -0.58), (-0.10, 5.16, -0.38), (-0.22, 4.92, -0.68),
                      (-0.15, 4.96, -0.67)]), "hair_dark", detail=True)                                 # flequillo caído

    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.74, -0.60)), 0.08, "coal", scale=(1.0, 0.8, 0.8), subdiv=0)

    # ---------------- brazos al aire, largos; manos de garra ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1] + 0.08, sh[2]), el, 0.30, 0.32, 0.24, 0.25, "skin_dead")
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.23, 0.23, 0.17, 0.18, "skin_dead")
        mk.hull(la, ring(ELBOW + 0.04, el[0], ARM_Z, 0.25, 0.26) + ring(ELBOW - 0.08, el[0], ARM_Z, 0.25, 0.26),
                "skin_dead")                                                                             # codo huesudo
        hd_ = mk.part(f"{side}Hand", wr)
        hx = wr[0] + s * 0.01
        mk.hull(hd_, round_ring(WRIST + 0.05, hx, ARM_Z, 0.17, 0.26) + round_ring(WRIST - 0.16, hx + s * 0.01, ARM_Z, 0.19, 0.30),
                "skin_dead")                                                                             # palma
        # dedos: un bloque largo que se curva hacia adelante como garra
        mk.hull(hd_, [(hx + s * dx, y, ARM_Z + z) for dx in (-0.06, 0.08) for y, z in
                      ((WRIST - 0.12, -0.13), (WRIST - 0.12, 0.12), (WRIST - 0.42, -0.14), (WRIST - 0.40, 0.08))]
                + [(hx + s * 0.01, WRIST - 0.56, ARM_Z - 0.20)], "skin_dead")
        mk.paint(hd_, "skin_dead_dark", box=((hx, WRIST - 0.50, ARM_Z - 0.16), (0.3, 0.14, 0.14)))       # uñas
        mk.hull(hd_, [(hx - s * 0.08, WRIST - 0.06, ARM_Z - 0.10), (hx - s * 0.02, WRIST - 0.06, ARM_Z - 0.14),
                      (hx - s * 0.06, WRIST - 0.10, ARM_Z - 0.02), (hx - s * 0.06, WRIST - 0.30, ARM_Z - 0.24),
                      (hx - s * 0.03, WRIST - 0.30, ARM_Z - 0.22)], "skin_dead")                         # pulgar

    # ---------------- piernas: pantalón cortado bajo la rodilla, descalzo ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.40, 0.42, 0.31, 0.33, "cloth_blue")
        ll = mk.part(f"{side}LowerLeg", knee)
        hem = KNEE - (0.20 if side == "Left" else 0.28)
        mk.hull(ll, ring(KNEE + 0.06, hip[0], 0, 0.34, 0.36) + ring(hem, hip[0], 0, 0.33, 0.35), "cloth_blue")
        for k, (dx, dz) in enumerate(((-0.10, -0.15), (0.09, -0.15), (0.14, 0.06), (-0.04, 0.16))):
            mk.prism(ll, [(-0.07, 0), (0.07, 0), (0.0, -0.11 - 0.04 * (k % 2))], 0.025, "cloth_blue", plane="xy",
                     center=(hip[0] + dx, hem + 0.01, dz), rot=(0, 0 if abs(dz) > 0.1 else 90, 0), detail=True)
        hu.limb(mk, ll, (hip[0], hem + 0.06, 0), ankle, 0.19, 0.20, 0.15, 0.16, "skin_dead")
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.12, 0.12) for y, z in
                     ((0.0, 0.14), (0.30, 0.10), (0.28, -0.10), (0.0, -0.34), (0.12, -0.32))], "skin_dead")
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.11, 0.11) for y, z in ((0.0, -0.30), (0.13, -0.30))]
                + [(hip[0] - 0.08, 0.0, -0.62), (hip[0] + 0.08, 0.0, -0.60), (hip[0], 0.06, -0.60)], "skin_dead")   # dedos largos
        mk.paint(ft, "skin_dead_dark", box=((hip[0], 0.03, -0.60), (0.3, 0.1, 0.08)))

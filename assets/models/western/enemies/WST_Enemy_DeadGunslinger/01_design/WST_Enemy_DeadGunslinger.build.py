"""
Receta de WST_Enemy_DeadGunslinger, el pistolero muerto (prompt 024, Bloques A + D + H).

Brief
- Silueta a 40 studs (recortada contra el cielo, en un techo): sombrero chato de ala ancha (2,0), guardapolvo
  largo que se abre abajo hasta media pierna, flaco, pañuelo rojo tapando la cara (el acento de color),
  pelo gris largo y ralo que cuelga bajo el ala.
- Medidas (Bloque D, H = 5,4): tobillo 0,27 · rodilla 1,35 · cadera 2,538 · cintura 2,97 · codo 3,13 ·
  muñeca 2,27 · hombro 4,10 · cuello 4,32. Cabeza de ~1,05. Miembros 0,9 × los del caminante (demacrado).
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes (oscuros), Acc_Hat (origen en la base
  del sombrero) y Acc_Weapon (cubo de 0,1 en el punto de agarre de la mano derecha, origen ahí).
- Capas: camisa negra (base) · chaleco de cuero 0,035 por fuera · canana y guardapolvo 0,07 por fuera.
  El guardapolvo se parte en UpperTorso (espalda, hombros, solapas, cuello alzado), LowerTorso (faldón
  de atrás y los costados) y UpperLegs (paneles con el ruedo deshilachado en zigzag).
- Tallado: cuencas profundas, agujero de bala en el chaleco (mancha de sangre poco profunda con el
  agujero en el medio), agujero de bala en la copa del sombrero.
- Detalle (sin booleana): pañuelo, pelo, guardapolvo, canana con cartuchos, cartucheras, espuelas.
- Inferido: pantalón en cloth_black (el prompt dice "dark"), cartucheras vacías (el arma la lleva en
  la mano), canana del hombro derecho a la cadera izquierda (deja ver el agujero del pecho), copa del
  sombrero chata de 0,40, cuello del guardapolvo alzado.

Vueltas: 1) primera versión (2154 triángulos; canana recta que atravesaba el pecho) · 2) canana como
polilínea apoyada en el chaleco · 3) techo del faldón 0,03 abajo del pantalón (coplanares en y = 3,02),
pie 0,01 más ancho que la caña (coplanares en x = ±0,15), suela que se mete en el pie (flotaba),
picos del ruedo adentro de la cuerda del panel, sin mandíbula ni espalda del chaleco (las tapan el
pañuelo y el guardapolvo), sombrero 0,03 más arriba para que se vea la ceja.

Revisión
- 2030 triángulos contra 1700 (+19 %): guardapolvo en tres piezas con el ruedo en zigzag, canana con 7
  cartuchos, sombrero con cinta y balazo, cuencas talladas. La espalda y lo tapado no gastan.
- Medidas: 5,64 de alto con el sombrero (H = 5,4 sin él), 2,34 de ancho (el ala de 2,0 y los brazos).
- Aviso aceptado: Acc_Weapon queda adentro de la mano ("enclosed"): es el cubo de agarre que pide el prompt.
- A 96 px se lee: ala ancha, pañuelo rojo, guardapolvo claro abierto, botas.
"""

import math

from mathutils import Vector

import humanoid as hu

H = 5.4
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH_X, EL_X, WR_X, LEG_X = 0.78, 0.90, 1.01, 0.30
ARM_Z = -0.10
NECK_P = (0.0, NECK, -0.14)
NECK_W = (0.0, hu.NECK, -0.10)
HEAD_K, HEAD_FWD, HEAD_TILT = 1.04, 0.12, -8

ring, round_ring = hu.ring, hu.round_ring


def head(pts):
    """Medidas de la cabeza del caminante -> escaladas 1,04, en el cuello del pistolero, 0,12 adelante y caída 8°."""
    out = [(x * HEAD_K, NECK_P[1] + (y - NECK_W[1]) * HEAD_K, NECK_P[2] + (z - NECK_W[2]) * HEAD_K - HEAD_FWD)
           for x, y, z in pts]
    return hu.about(out, NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def grow(points, d, zc=0.0, ytop=3.9, ybot=2.95):
    """Capa encima: los puntos d más afuera en x, en z (respecto de zc) y en y arriba de ytop / abajo de ybot."""
    return [(x + (d if x > 0 else -d if x < 0 else 0), y + (d if y > ytop else -d if y < ybot else 0),
             z + (d if z > zc else -d)) for x, y, z in points]


def gaunt_hand(mk, part, s, wx, wrist, z):
    """Mano huesuda: mitón de 3 anillos y pulgar; uñas oscuras pintadas."""
    mk.hull(part, round_ring(wrist + 0.05, wx, z, 0.19, 0.32) + round_ring(wrist - 0.20, wx + s * 0.01, z, 0.21, 0.35)
            + round_ring(wrist - 0.45, wx + s * 0.02, z, 0.16, 0.27), "skin_dead")
    mk.box(part, (wx - s * 0.07, wrist - 0.15, z - 0.18), (0.09, 0.22, 0.09), "skin_dead", rot=(-15, 0, 0))
    mk.paint(part, "skin_dead_dark", box=((wx, wrist - 0.45, z), (0.4, 0.08, 0.5)))


def build(mk):
    # ---------------- cadera: pantalón, cinto con dos cartucheras, faldón del guardapolvo ----------------
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.36, 0, 0, 0.82, 0.48) + ring(3.02, 0, 0, 0.88, 0.50), "cloth_black")
    mk.hull(lt, ring(2.60, 0, 0, 0.96, 0.58) + ring(2.74, 0, 0, 0.96, 0.58), "leather")            # cinto
    mk.box(lt, (0.0, 2.67, -0.30), (0.16, 0.12, 0.04), "brass", detail=True)                       # hebilla
    for s in (-1, 1):                                                                                # cartucheras
        mk.hull(lt, [(s * 0.44, 2.70, -0.20), (s * 0.58, 2.70, -0.20), (s * 0.44, 2.70, 0.06), (s * 0.58, 2.70, 0.06),
                     (s * 0.47, 2.06, -0.16), (s * 0.57, 2.06, -0.16), (s * 0.47, 2.10, -0.02), (s * 0.57, 2.10, -0.02)],
                "leather_dark", detail=True)
        mk.box(lt, (s * 0.52, 2.58, -0.07), (0.12, 0.10, 0.20), "leather_dark", detail=True)        # boca de la cartuchera
    # faldón: espalda y costados, 0,07 por fuera del pantalón, de la cintura a debajo de la cadera
    mk.hull(lt, [(x, y, z) for x in (-0.55, 0.55) for y in (2.42, 2.99) for z in (0.02, 0.33)]
            + [(-0.40, 2.42, 0.40), (0.40, 2.42, 0.40), (-0.36, 2.99, 0.36), (0.36, 2.99, 0.36)], "canvas", detail=True)

    # ---------------- torso: camisa negra, chaleco con agujero de bala, canana, guardapolvo ----------------
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    shirt = (ring(2.92, 0, 0, 0.90, 0.50) + ring(3.50, 0, -0.02, 1.14, 0.60)
             + [(-0.66, 3.98, -0.28), (-0.66, 3.98, 0.14), (0.68, 4.04, -0.28), (0.68, 4.04, 0.14),
                (-0.28, 4.10, -0.24), (0.28, 4.14, -0.24), (-0.28, 4.10, 0.12), (0.28, 4.14, 0.12),
                (-0.36, 3.74, 0.36), (0.36, 3.78, 0.36), (0.0, 3.84, 0.40)])
    mk.hull(ut, shirt, "cloth_black")
    for s in (-1, 1):                                                                              # dos delanteros en V
        mk.hull(ut, [(s * 0.08, 2.86, -0.29), (s * 0.48, 2.88, -0.21), (s * 0.50, 2.88, 0.0), (s * 0.12, 3.40, -0.37),
                     (s * 0.43, 3.50, -0.37), (s * 0.62, 3.50, -0.16), (s * 0.62, 3.50, 0.05),
                     (s * 0.23, 4.13 + 0.02 * (s > 0), -0.28), (s * 0.70, 4.02 + 0.06 * (s > 0), -0.31),
                     (s * 0.70, 4.02 + 0.06 * (s > 0), 0.0)], "leather")
    # agujero de bala en el pecho izquierdo: mancha poco profunda (sangre) y el agujero en el medio
    mk.carve(ut, "blood_dry", points=mk.pts_cyl((-0.30, 3.64, -0.42), 0.10, 0.16, axis="z", sides=8))
    mk.carve(ut, "coal", points=mk.pts_cyl((-0.30, 3.64, -0.40), 0.04, 0.20, axis="z", sides=6))
    mk.cyl(ut, (0, 4.18, -0.16), 0.15, 0.40, "skin_dead", rot=(-18, 0, 0), sides=10)            # cuello flaco
    # canana: del hombro derecho a la cadera izquierda, apoyada en el chaleco (cada punto es la cara de
    # atrás de la tira, 0,01 adentro del chaleco), con cartuchos de bronce cruzados a la tira
    path = [(0.50, 4.13, 0.10), (0.42, 4.03, -0.29), (0.12, 3.58, -0.355), (-0.42, 2.92, -0.25)]
    for i in range(len(path) - 1):
        a, b = Vector(path[i]), Vector(path[i + 1])
        if i < len(path) - 2:
            b = b + (b - a).normalized() * 0.02          # se mete 0,02 en el tramo siguiente
        d = Vector((b.x - a.x, b.y - a.y)).normalized()
        perp = Vector((-d.y, d.x, 0)) * 0.075
        pts = [tuple(c + sgn * perp + Vector((0, 0, dz))) for c in (a, b) for sgn in (-1, 1) for dz in (0.0, -0.05)]
        mk.hull(ut, pts, "leather", detail=True)
    for i in range(7):
        t = (i + 0.5) / 7
        seg, u = (1, t * 2) if t < 0.5 else (2, (t - 0.5) * 2)
        c = Vector(path[seg]).lerp(Vector(path[seg + 1]), u)
        mk.box(ut, (c.x, c.y, c.z - 0.07), (0.05, 0.10, 0.05), "brass", rot=(0, 0, 56), detail=True)
    # guardapolvo: espalda entera y hombros, dos solapas al costado del chaleco, cuello alzado atrás
    coat = grow(shirt, 0.075)
    mk.hull(ut, [p for p in coat if p[2] > -0.10], "canvas", detail=True)
    for s in (-1, 1):
        mk.hull(ut, [p for p in grow(shirt, 0.085) if s * p[0] > 0.30], "canvas", detail=True)
        mk.hull(ut, [(s * 0.40, 2.90, -0.32), (s * 0.48, 2.90, -0.30), (s * 0.30, 4.10, -0.36), (s * 0.40, 4.06, -0.36),
                     (s * 0.44, 3.50, -0.42), (s * 0.40, 2.90, -0.27), (s * 0.30, 4.10, -0.30)], "canvas", detail=True)  # solapa
    mk.hull(ut, [(x, y, z) for x in (-0.32, 0.32) for y, z in ((4.08, 0.02), (4.08, 0.24), (4.40, 0.10), (4.40, 0.28))],
            "canvas", detail=True)                                                                   # cuello alzado

    # ---------------- cabeza: calavera con la piel tirante, pañuelo rojo, pelo gris ralo ----------------
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.28, 0, -0.17, 0.62, 0.60) + round_ring(4.52, 0, -0.21, 0.70, 0.80)
                     + round_ring(4.80, 0, -0.25, 0.92, 0.88) + round_ring(5.02, 0, -0.26, 0.84, 0.84)
                     + round_ring(5.16, 0, -0.26, 0.56, 0.60)), "skin_dead")
    mk.hull(hd, head(mk.pts_box((0, 4.88, -0.66), (0.86, 0.14, 0.20), top=(0.9, 0.8))), "skin_dead")    # ceja
    for s in (-1, 1):                                                                                     # pómulos marcados
        mk.hull(hd, head([(s * 0.18, 4.70, -0.68), (s * 0.40, 4.72, -0.52), (s * 0.44, 4.76, -0.30),
                          (s * 0.30, 4.82, -0.62), (s * 0.40, 4.62, -0.40), (s * 0.24, 4.64, -0.62)]), "skin_dead")
    mk.hull(hd, head([(0, 4.82, -0.68), (0, 4.63, -0.82), (-0.08, 4.61, -0.68), (0.08, 4.61, -0.68),
                      (0, 4.59, -0.71)]), "skin_dead")                                                  # nariz
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.77, -0.74), 0.17, scale=(1.0, 0.8, 0.9), subdiv=0)))
    # pañuelo: de arriba de la nariz a una punta bajo el mentón, atado atrás con el nudo y dos puntas
    mk.hull(hd, head([(-0.40, 4.60, -0.42), (0.40, 4.60, -0.42), (-0.20, 4.62, -0.74), (0.20, 4.62, -0.74),
                      (0.0, 4.63, -0.86), (-0.33, 4.38, -0.63), (0.33, 4.38, -0.63), (0.0, 4.04, -0.75),
                      (-0.25, 4.14, -0.68), (0.25, 4.14, -0.68), (-0.44, 4.60, -0.12), (0.44, 4.60, -0.12),
                      (-0.34, 4.26, -0.18), (0.34, 4.26, -0.18)]), "cloth_red", detail=True)
    mk.hull(hd, head(round_ring(4.57, 0, -0.20, 0.92, 0.86, n=8) + round_ring(4.67, 0, -0.22, 0.98, 0.90, n=8)),
            "cloth_red", detail=True)                                                                # vuelta atrás
    mk.ball(hd, hp((0.0, 4.62, 0.26)), 0.08, "cloth_red", scale=(1.2, 1, 0.8), subdiv=0, detail=True)  # nudo
    for s in (-1, 1):
        mk.prism(hd, [(-0.05, 0), (0.05, 0), (s * 0.03, -0.30)], 0.025, "cloth_red", plane="xy",
                 center=hp((s * 0.05, 4.60, 0.28)), rot=(-8, 0, s * 12), detail=True)
    # pelo gris largo y ralo, colgando bajo el ala a los costados y atrás
    for x, z, y0 in ((-0.44, -0.18, 4.28), (-0.40, 0.06, 4.16), (-0.18, 0.28, 4.10), (0.14, 0.30, 4.20),
                     (0.38, 0.10, 4.14), (0.45, -0.16, 4.34)):
        mk.hull(hd, head([(x - 0.07, 5.00, z - 0.06), (x + 0.07, 5.00, z - 0.06), (x, 5.00, z + 0.06),
                          (x * 1.06, y0, z * 1.1), (x * 1.06 + 0.02, y0 + 0.10, z * 1.1 + 0.02)]), "hair_grey", detail=True)

    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.76, -0.60)), 0.075, "coal", scale=(1.0, 0.8, 0.8), subdiv=0)

    # ---------------- sombrero chato de ala ancha, con un balazo en la copa ----------------
    base = hp((0, 5.00, -0.26))
    hat = mk.part("Acc_Hat", base)

    def hat_pts(pts):
        return head([(x, y + 0.03, z - 0.26) for x, y, z in pts])
    brim = [(0.98 * math.cos(a), 0, 0.92 * math.sin(a)) for a in [i * math.pi / 6 for i in range(12)]]
    mk.hull(hat, hat_pts([(x, 4.97 + 0.03 * (abs(x) > 0.7), z) for x, _, z in brim]
                         + [(x, 5.03 + 0.03 * (abs(x) > 0.7), z) for x, _, z in brim]), "cloth_black")
    crown = [(r * math.cos(a), y, r * 0.92 * math.sin(a)) for y, r in ((4.99, 0.44), (5.40, 0.40))
             for a in [i * math.pi / 5 for i in range(10)]]
    mk.hull(hat, hat_pts(crown), "cloth_black")
    mk.hull(hat, hat_pts(round_ring(5.04, 0, 0, 0.96, 0.88) + round_ring(5.13, 0, 0, 0.96, 0.88)), "leather")    # cinta
    mk.carve(hat, "coal", points=hat_pts(mk.pts_cyl((0.16, 5.27, -0.40), 0.05, 0.30, axis="z", sides=6)))     # balazo

    # ---------------- brazos: mangas del guardapolvo con puño vuelto; manos huesudas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1] + 0.10, sh[2]), el, 0.40, 0.42, 0.33, 0.34, "canvas")
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.31, 0.31, 0.26, 0.26, "canvas")
        hu.limb(mk, la, (wr[0], wr[1] + 0.16, ARM_Z), (wr[0], wr[1] + 0.02, ARM_Z), 0.32, 0.32, 0.32, 0.32, "canvas", over=0.0)
        hand = mk.part(f"{side}Hand", wr)
        gaunt_hand(mk, hand, s, wr[0] + s * 0.02, WRIST, ARM_Z)
    grip = (WR_X + 0.04, WRIST - 0.24, ARM_Z)
    wpn = mk.part("Acc_Weapon", grip)
    mk.box(wpn, grip, (0.1, 0.1, 0.1), "steel_light")

    # ---------------- piernas: pantalón oscuro, paneles del guardapolvo, botas con espuelas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.42, 0.44, 0.34, 0.36, "cloth_black")
        # panel del guardapolvo: envuelve el costado de afuera y la parte de atrás, abre abajo
        arc = [math.radians(a) for a in (-55, -10, 35, 80, 125)]
        pts = [(hip[0] + s * r * math.cos(a), y, r * math.sin(a)) for y, r in ((2.52, 0.29), (1.96, 0.34)) for a in arc]
        mk.hull(ul, pts, "canvas", detail=True)
        for k, a in enumerate(arc[:-1]):                                                             # ruedo en zigzag
            b = (a + arc[k + 1]) / 2
            mk.prism(ul, [(-0.08, 0), (0.08, 0), (0.0, -0.12 - 0.05 * (k % 2))], 0.025, "canvas", plane="xy",
                     center=(hip[0] + s * 0.30 * math.cos(b), 1.98, 0.30 * math.sin(b)),
                     rot=(0, -math.degrees(b) * s + (90 if s > 0 else -90), 0), detail=True)
        ll = mk.part(f"{side}LowerLeg", knee)
        hu.limb(mk, ll, knee, (hip[0], 0.92, 0), 0.34, 0.36, 0.28, 0.30, "cloth_black")
        mk.hull(ll, ring(1.02, hip[0], 0, 0.34, 0.36) + ring(0.22, hip[0], 0, 0.30, 0.33), "leather_dark")     # caña
        mk.hull(ll, ring(0.94, hip[0], 0, 0.38, 0.40) + ring(1.06, hip[0], 0, 0.38, 0.40), "leather_dark")
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.16, 0.16) for y, z in ((0.10, 0.17), (0.32, 0.15), (0.26, -0.16))]
                + [(hip[0] - 0.08, 0.06, -0.52), (hip[0] + 0.08, 0.06, -0.52), (hip[0], 0.14, -0.50)], "leather_dark")  # bota en punta
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.13, 0.13) for y, z in ((0.0, 0.18), (0.13, 0.18), (0.0, 0.0), (0.13, 0.0))]
                + [(hip[0] - 0.07, 0.0, -0.50), (hip[0] + 0.07, 0.0, -0.50), (hip[0], 0.08, -0.52),
                   (hip[0] - 0.14, 0.09, -0.12), (hip[0] + 0.14, 0.09, -0.12)], "leather_dark")              # taco y suela
        mk.cyl(ft, (hip[0], 0.13, 0.26), 0.075, 0.025, "steel_light", axis="x", sides=8, detail=True)      # rodaja
        mk.box(ft, (hip[0], 0.13, 0.20), (0.03, 0.03, 0.10), "steel_light", detail=True)                   # espuela

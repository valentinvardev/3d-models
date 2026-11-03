"""
Receta de WST_Boss_Engineer, el maquinista infectado (prompt 061, Bloques A + D + H + G).

Brief
- Silueta a 40 studs: gorra de maquinista gris pizarra inflada con las antiparras de bronce arriba,
  cara tiznada de hollín con la marca clara de las antiparras alrededor de los ojos, bigote negro
  grueso, mameluco azul con pechera, pañuelo rojo, brazos largos con guanteletes de cuero, y la pala de
  carbón clavada en el piso al lado, con el agarre en D a la altura del hombro.
- Escala: H = 6,0 (k = 6,0 / 5,2 = 1,154). Articulaciones del Bloque D escaladas salvo los brazos, que
  son largos (prompt): tobillo 0,30 · rodilla 1,50 · cadera 2,82 · cintura 3,30 · codo 3,39 (0,565 H) ·
  muñeca 2,34 (0,39 H) · hombro 4,56 · cuello 4,80. Torso fornido (pecho 1,86): hombros x = ±1,06,
  codos ±1,22, muñecas ±1,37 (8° hacia afuera), caderas ±0,40, brazos en z = -0,12. Va a la ficha.
- Piezas: las 15 de R15, Eyes, Acc_Cap (base de la copa), Acc_Goggles (puente de las antiparras),
  Acc_Shovel (el agarre de la mano derecha), Silver_Eyes, Silver_Neck (cintura, como UpperTorso),
  Silver_LeftLowerArm, Silver_RightLowerArm (codo), _Grip (agarre en D), _Grip2 (mitad del mango),
  _Blade (centro de la hoja).
- Tallado: cuencas, boca, mordida en el cuello, quemaduras en los antebrazos, mameluco roto en la
  rodilla izquierda. Pintado: hollín (coal) en manchas sobre la cara, con la marca de las antiparras
  limpia (cortes con slice para que los bordes sean nítidos).
- Inferido: la pala no puede ir "en las dos manos" en pose I (las manos están a 2,8 una de otra): la
  sostiene la derecha por el mango, clavada en el piso al lado del pie derecho; _Grip y _Grip2 marcan
  dónde van las manos al animar. Mangas arremangadas por arriba del codo (así se ve el antebrazo entre
  la manga y el guantelete); las manos van enguantadas (cuero); cinturón de herramientas con dos bolsas
  y un martillo; tirantes del mameluco cruzados atrás; la visera de la gorra en leather_dark (el prompt
  dice gorra "plain" paint_slate: la visera oscura la separa de la cara).

Vueltas: 1) primera versión; tirantes de atrás cruzados en el mismo plano, hollín metido en la franja de
las antiparras, visera que no pasaba de la copa (0,01), antiparras hundidas 0,02 en la gorra · 2) bigote
en dos mitades que compartían la cara del medio (3 caras por borde); alas de la pala de 0,02 que el
chanflán daba vuelta; puente de las antiparras 0,008 corto (el cráneo escala x por 1,154 y el anillo no)
· 3) las dos mitades del bigote con la cara de arriba en el mismo plano · 4) la pechera tenía dos filas
(3,24 y 4,20) y la camisa sobresalía en el quiebre del pecho (4,04): se veía solo un rectángulo abajo;
ahora tiene la fila del quiebre y se ve entera; hollín más grande en las mejillas.

Revisión
- 3552 triángulos contra 3400 (4 % más): la pala con chanflanes (filo de acero) y las antiparras.
- Alto 6,248 con la gorra; el cuerpo, 6,0.
- Dudoso: la pala clavada en el piso (en pose I no se puede tener con las dos manos); los marcadores
  _Grip y _Grip2 dicen dónde van las manos al animar.
"""

import math

from mathutils import Vector

import humanoid as hu

H = 6.0
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.565 * H, 0.39 * H, 0.76 * H, 0.80 * H
SH_X, ARM_Z, LEG_X = 1.06, -0.12, 0.40
TAN8 = math.tan(math.radians(8))
EL_X, WR_X = SH_X + (SHOULDER - ELBOW) * TAN8, SH_X + (SHOULDER - WRIST) * TAN8
NECK_P = (0.0, NECK, -0.12)
HEAD_FWD, HEAD_TILT = 0.14, -8

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def head(pts):
    return about([(x * K, y * K, z * K - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def head_up():
    e = Vector(hp((0, 5.0, 0))) - Vector(hp((0, 4.0, 0)))
    return tuple(e.normalized())


def arm_x(y):
    return SH_X + (SHOULDER - y) * TAN8


def shirt_front(y):
    if y <= 4.04:
        return -0.46 - 0.12 * (y - 3.24) / 0.80
    return -0.58 + 0.20 * (y - 4.04) / 0.48


def rod(mk, part, a, b, r, mat, sides=6, detail=False):
    A, B = Vector(a), Vector(b)
    d = (B - A).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u)
    pts = [tuple(P + r * (math.cos(t) * u + math.sin(t) * v)) for P in (A, B)
           for t in [2 * math.pi * (i + 0.5) / sides for i in range(sides)]]
    mk.hull(part, pts, mat, detail=detail)


def strap(mk, part, path, w, mat, back=0.12, detail=False):
    for i in range(len(path) - 1):
        (x0, y0, z0), (x1, y1, z1) = path[i], path[i + 1]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        ex, ey = dx / ln * 0.02, dy / ln * 0.02
        pts = []
        for (x, y, z), e in (((x0, y0, z0), -1), ((x1, y1, z1), 1)):
            for s in (-1, 1):
                for dz in (0.0, back):
                    pts.append((x + s * nx + e * ex, y + s * ny + e * ey, z + dz))
        mk.hull(part, pts, mat, detail=detail)


def veins(mk, part, axis, branches, mat="silver_neon"):
    for k, ((y0, a0), (y1, a1), w0, w1) in enumerate(branches):
        out, dep = 0.02 + 0.007 * (k % 3), -0.05 - 0.006 * k
        y0, y1 = y0 - 0.007 * k, y1 + 0.005 * k
        pts = []
        for y, a, w in ((y0, a0, w0), (y1, a1, w1)):
            cx, cz, rx, rz = axis(y)
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            for off in (out, dep):
                for sw in (-1, 1):
                    pts.append((cx + (rx + off) * ca - sa * sw * w / 2, y, cz + (rz + off) * sa + ca * sw * w / 2))
        mk.hull(part, pts, mat)


def c_ring(mk, part, center, rx, ry, wire, depth, mat, plane="xy", rot=(0, 0, 0), n=10, gap=10, detail=False):
    prof = []
    for i in range(n + 1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append((rx * math.cos(a), ry * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append(((rx - wire) * math.cos(a), (ry - wire) * math.sin(a)))
    mk.prism(part, prof, depth, mat, plane=plane, center=center, rot=rot, detail=detail)


def splash(r, rot=0):
    rad = (1.0, 0.82, 0.95, 0.72, 1.05, 0.78, 0.92, 0.7, 1.0, 0.8)
    return [(r * rad[k] * math.cos(math.radians(36 * k + rot)), r * rad[k] * math.sin(math.radians(36 * k + rot)))
            for k in range(10)]


# ======================================================================================
def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    top = [(-0.50, 4.52, -0.38), (0.50, 4.52, -0.38), (-0.98, 4.38, -0.28), (0.98, 4.46, -0.28),
           (-0.98, 4.40, 0.30), (0.98, 4.48, 0.30), (-0.34, 4.60, 0.20), (0.34, 4.60, 0.20)]
    hump = [(-0.46, 4.30, 0.56), (0.46, 4.32, 0.56), (0.0, 4.38, 0.60)]
    mk.hull(ut, ring(3.24, 0, 0.02, 1.52, 0.96) + ring(4.04, 0, -0.03, 1.86, 1.10) + top + hump, "canvas")
    # pechera del mameluco y tirantes que cruzan atrás
    mk.hull(ut, [p for x, y in ((-0.52, 3.24), (0.52, 3.24), (-0.48, 4.04), (0.48, 4.04), (-0.46, 4.22), (0.46, 4.22))
                 for p in ((x, y, shirt_front(y) - 0.04), (x, y, shirt_front(y) + 0.12))], "cloth_blue")
    mk.hull(ut, [(x, y, max(z, -0.30)) for x, y, z in ring(3.22, 0, 0.02, 1.58, 1.02) + ring(3.50, 0, 0.02, 1.66, 1.06)],
            "cloth_blue")                                                                         # cintura del mameluco
    for s in (-1, 1):
        strap(mk, ut, [(s * 0.38, 4.16, shirt_front(4.16) - 0.04), (s * 0.44, 4.46, shirt_front(4.46) - 0.04),
                       (s * 0.46, 4.60, 0.0)], 0.14, "cloth_blue", back=0.10)
        dz = 0.012 if s > 0 else 0.0                                                             # se cruzan atrás
        strap(mk, ut, [(s * 0.46, 4.60, 0.0), (s * 0.40, 4.36, 0.64 + dz), (-s * 0.30, 3.50, 0.56 + dz)], 0.14,
              "cloth_blue", back=-0.10)
        mk.cyl(ut, (s * 0.38, 4.12, shirt_front(4.12) - 0.05), 0.045, 0.03, "brass", axis="z", sides=6, detail=True)
    mk.carve(ut, "cloth_blue", points=mk.pts_box((0, 3.82, shirt_front(3.82) - 0.05), (0.30, 0.22, 0.04)))   # bolsillo
    # cuello, pañuelo y mordida
    mk.cyl(ut, (0, 4.66, -0.12), 0.26, 0.46, "skin_dead", rot=(-20, 0, 0), sides=10)
    mk.carve(ut, "blood_dry", points=mk.pts_ball((0.24, 4.74, -0.08), 0.09, scale=(1, 1.3, 1), subdiv=0))
    mk.cyl(ut, (0, 4.58, -0.13), 0.31, 0.16, "cloth_red", rot=(-20, 0, 0), sides=10)
    mk.hull(ut, [(-0.22, 4.56, -0.42), (0.22, 4.56, -0.42), (0.0, 4.28, shirt_front(4.28) - 0.09),
                 (-0.20, 4.56, -0.34), (0.20, 4.56, -0.34), (0.0, 4.30, shirt_front(4.30) - 0.03)], "cloth_red")
    mk.ball(ut, (0.0, 4.54, -0.45), 0.07, "cloth_red", subdiv=0)
    return ut


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.74, 0, 0, 1.40, 0.86) + ring(3.40, 0, 0.02, 1.58, 1.00), "cloth_blue")
    # cinturón de herramientas, caído a la derecha, con dos bolsas y un martillo
    tilt = (0, 0, -5)
    mk.hull(lt, about(ring(2.92, 0, 0.02, 1.62, 1.06) + ring(3.06, 0, 0.02, 1.62, 1.06), (0, 3.0, 0), tilt), "leather_dark")
    mk.box(lt, (0.02, 3.00, -0.53), (0.18, 0.16, 0.05), "iron")
    for s, y in ((1, 2.80), (-1, 2.88)):
        mk.box(lt, (s * 0.62, y, -0.40), (0.30, 0.30, 0.16), "leather", rot=(0, s * 35, 0))
        mk.box(lt, (s * 0.62, y + 0.15, -0.40), (0.31, 0.06, 0.17), "leather_dark", rot=(0, s * 35, 0))
    rod(mk, lt, (-0.60, 2.86, -0.44), (-0.56, 3.30, -0.46), 0.035, "wood_mid", sides=6)            # mango del martillo
    mk.box(lt, (-0.56, 3.32, -0.46), (0.26, 0.08, 0.08), "iron")
    return lt


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(mk, ul, (x, HIP, 0), (x, KNEE, 0), 0.70, 0.72, 0.56, 0.58, "cloth_blue", over=0.06)
        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(mk, ll, (x, KNEE, 0), (x, 0.70, 0), 0.56, 0.58, 0.52, 0.54, "cloth_blue", over=0.06)
        mk.hull(ll, ring(0.86, x, 0.0, 0.58, 0.62) + ring(0.24, x, 0.0, 0.52, 0.58), "leather_dark")   # caña
        mk.hull(ll, ring(0.80, x, 0.0, 0.62, 0.66) + ring(0.90, x, 0.0, 0.62, 0.66), "leather_dark")
        if side == "Left":
            mk.carve(ll, "skin_dead", points=mk.pts_box((x - 0.02, 1.38, -0.27), (0.24, 0.24, 0.14), rot=(0, 0, -18)))
        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + d, y, z) for d in (-0.27, 0.27) for y, z in ((0.08, 0.28), (0.40, 0.26), (0.36, -0.16))]
                + [(x + d, y, z) for d in (-0.25, 0.25) for y, z in ((0.08, -0.62), (0.28, -0.56))], "leather_dark")
        mk.hull(ft, [(x + d, y, z) for d in (-0.28, 0.28) for y in (0.0, 0.09) for z in (0.30, -0.64)], "coal")


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        ua = mk.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        mk.hull(ua, round_ring(4.66, s * arm_x(4.66), ARM_Z, 0.42, 0.46) + round_ring(4.44, s * arm_x(4.44), ARM_Z, 0.60, 0.62)
                + round_ring(3.52, s * arm_x(3.52), ARM_Z, 0.54, 0.56), "canvas")
        mk.hull(ua, round_ring(3.66, s * arm_x(3.66), ARM_Z, 0.64, 0.66, n=8) + round_ring(3.42, s * arm_x(3.42), ARM_Z, 0.64, 0.66, n=8),
                "canvas")                                                                         # manga arremangada
        la = mk.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        mk.hull(la, round_ring(3.48, s * arm_x(3.48), ARM_Z, 0.52, 0.54) + round_ring(3.20, s * (arm_x(3.20) + 0.02), ARM_Z, 0.56, 0.56)
                + round_ring(2.90, s * arm_x(2.90), ARM_Z, 0.50, 0.52), "skin_dead")
        mk.carve(la, "skin_dead_dark", prism=dict(profile=splash(0.10, 20 * s), depth=0.08, plane="zy",
                                                  center=(s * (arm_x(3.12) + 0.29), 3.12, ARM_Z - 0.04)))   # quemadura
        mk.hull(la, round_ring(3.00, s * arm_x(3.00), ARM_Z, 0.64, 0.66) + round_ring(2.86, s * arm_x(2.86), ARM_Z, 0.60, 0.62)
                + round_ring(2.40, s * arm_x(2.40), ARM_Z, 0.48, 0.52), "leather_dark")                    # guantelete
        hd = mk.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hx = s * (WR_X + 0.03)
        mk.hull(hd, round_ring(2.42, hx, ARM_Z, 0.34, 0.52) + round_ring(2.06, hx + s * 0.01, ARM_Z, 0.36, 0.56)
                + round_ring(1.72, hx + s * 0.02, ARM_Z, 0.28, 0.44), "leather_dark")
        mk.box(hd, (hx - s * 0.11, 2.16, ARM_Z - 0.28), (0.15, 0.34, 0.15), "leather_dark", rot=(-15, 0, 0))   # pulgar


def head_cap_goggles(mk):
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.28, 0, -0.17, 0.74, 0.64) + round_ring(4.52, 0, -0.21, 0.86, 0.84)
                     + round_ring(4.80, 0, -0.25, 0.94, 0.90) + round_ring(5.02, 0, -0.26, 0.86, 0.86)
                     + round_ring(5.16, 0, -0.26, 0.58, 0.62)), "skin_dead")
    mk.hull(hd, head([(-0.30, 4.44, -0.58), (0.30, 4.44, -0.58), (-0.32, 4.46, -0.16), (0.32, 4.46, -0.16),
                      (-0.22, 4.16, -0.68), (0.22, 4.16, -0.68), (-0.26, 4.20, -0.14), (0.26, 4.20, -0.14),
                      (0, 4.12, -0.72)]), "skin_dead")                                               # mandíbula
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.03, 4.86, -0.71), (s * 0.44, 4.90, -0.58), (s * 0.03, 4.95, -0.67),
                          (s * 0.44, 4.97, -0.54), (s * 0.03, 4.88, -0.45), (s * 0.42, 4.94, -0.40)]), "skin_dead")
        mk.hull(hd, head(mk.pts_box((s * 0.47, 4.70, -0.22), (0.09, 0.24, 0.16), top=(1, 0.7))), "skin_dead")
    mk.hull(hd, head([(0, 4.84, -0.70), (0, 4.64, -0.86), (-0.12, 4.60, -0.70), (0.12, 4.60, -0.70),
                      (0, 4.58, -0.76), (-0.07, 4.64, -0.80), (0.07, 4.64, -0.80)]), "skin_dead")   # nariz de papa
    cap = [p for y, w, d in ((4.56, 0.88, 0.84), (4.80, 0.98, 0.94), (5.00, 0.90, 0.90))
           for p in round_ring(y, 0, -0.25, w, d, n=12) if p[2] > -0.22]
    mk.hull(hd, head(cap + [(0, 4.48, 0.06)]), "hair_dark")                                        # pelo
    # hollín: cortes nítidos en el borde de la marca de las antiparras y manchas de carbón alrededor
    up = head_up()
    mk.slice(hd, hp((0, 4.645, -0.6)), up)
    mk.slice(hd, hp((0, 4.885, -0.6)), up)
    for c, r in (((0.0, 4.38, -0.62), 0.24), ((-0.33, 4.44, -0.45), 0.22), ((0.33, 4.44, -0.45), 0.22),
                 ((0.0, 4.60, -0.80), 0.06), ((0.0, 5.08, -0.62), 0.18), ((-0.36, 5.06, -0.40), 0.15),
                 ((0.36, 5.06, -0.40), 0.15)):
        mk.paint(hd, "coal", ball=(hp(c), r * K))
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.76, -0.75), 0.14, scale=(1.0, 0.70, 0.9),
                                                               subdiv=0)))
    mouth = [(-0.16, 4.44), (0.16, 4.44), (0.14, 4.30), (-0.14, 4.30), (0, 4.27)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.95, -0.52)]))
    for i in range(4):
        x = -0.10 + 0.0667 * i
        mk.hull(hd, head([(x - 0.03, 4.30, -0.68), (x + 0.03, 4.30, -0.68), (x - 0.02, 4.39, -0.68),
                          (x + 0.02, 4.39, -0.68), (x - 0.03, 4.30, -0.46), (x + 0.03, 4.30, -0.46),
                          (x, 4.38, -0.46)]), "bone", detail=True)
    for s in (-1, 1):                                                                              # bigote escoba
        c, t = -s * 0.02, (0.006 if s < 0 else 0.0)                                             # se cruzan, desfasadas
        mk.hull(hd, head([(c, 4.60 + t, -0.86), (s * 0.20, 4.60 + t, -0.82), (s * 0.34, 4.54, -0.70), (s * 0.33, 4.44, -0.72),
                          (s * 0.18, 4.45, -0.86), (c, 4.47, -0.88), (c, 4.58, -0.68), (s * 0.30, 4.52, -0.56)]),
                "hair_dark", detail=True)

    eyes = mk.part("Eyes", NECK_P)
    se = mk.part("Silver_Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.76, -0.62)), 0.075 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)
        mk.ball(se, hp((s * 0.19, 4.76, -0.62)), 0.075 * K + 0.012, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)

    # gorra de maquinista: copa inflada y visera corta
    base = hp((0, 4.98, -0.26))
    cp = mk.part("Acc_Cap", base)
    mk.hull(cp, head(round_ring(4.97, 0, -0.26, 0.94, 0.98, n=12) + round_ring(5.18, 0, -0.26, 1.12, 1.16, n=12)
                     + round_ring(5.34, 0, -0.25, 1.00, 1.04, n=12) + round_ring(5.42, 0, -0.25, 0.60, 0.64, n=10)),
            "paint_slate")
    mk.hull(cp, head(round_ring(4.98, 0, -0.26, 0.97, 1.01, n=12) + round_ring(5.06, 0, -0.26, 0.98, 1.02, n=12)),
            "paint_slate")
    visor = [(0.40 * math.cos(a), -0.26 - 0.80 * math.sin(a)) for a in [math.pi * i / 8 for i in range(9)]]
    mk.hull(cp, head([(x, 4.99 - 0.10 * max(0.0, -0.66 - z) / 0.32, z) for x, z in visor]
                     + [(x, 5.03 - 0.10 * max(0.0, -0.66 - z) / 0.32, z) for x, z in visor]), "leather_dark")   # visera
    # antiparras de bronce subidas sobre la gorra, con la correa alrededor de la copa
    gc = hp((0, 5.24, -0.88))
    gg = mk.part("Acc_Goggles", gc)
    mk.hull(gg, head(round_ring(5.14, 0, -0.26, 1.15, 1.19, n=12) + round_ring(5.22, 0, -0.26, 1.15, 1.19, n=12)),
            "leather_dark")                                                                       # correa
    for s in (-1, 1):
        lc = hp((s * 0.19, 5.24, -0.88))
        c_ring(mk, gg, lc, 0.13, 0.13, 0.04, 0.08, "brass", plane="xy", rot=(HEAD_TILT - 20, 0, 0), n=10, gap=8)
        mk.hull(gg, head(mk.pts_cyl((s * 0.19, 5.24, -0.87), 0.105, 0.03, axis="z", sides=10, rot=(-20, 0, 0))), "glass")
    mk.hull(gg, head(mk.pts_box((0, 5.24, -0.88), (0.21, 0.05, 0.08))), "brass")                    # puente
    return hd


def shovel(mk):
    """Pala de carbón clavada en el piso, la mano derecha en el mango y el agarre en D a la altura del hombro."""
    hgrip = Vector((WR_X + 0.03, WRIST - 0.30, ARM_Z - 0.04))
    sv = mk.part("Acc_Shovel", tuple(hgrip))
    d = Vector((-0.02, 2.36, -0.59)).normalized()            # eje del mango, hacia arriba y adelante
    t_bot = (1.10 - hgrip.y) / d.y                           # donde empieza la hoja
    t_top = t_bot + 3.0
    P = lambda t: hgrip + d * t  # noqa: E731
    rod(mk, sv, tuple(P(t_bot - 0.02)), tuple(P(t_top)), 0.06, "wood_mid", sides=8, detail=True)           # mango de 3,0
    rod(mk, sv, tuple(P(t_top - 0.04)), tuple(P(t_top + 0.06)), 0.072, "iron", sides=8, detail=True)      # virola
    xv = Vector((1, 0, 0))
    n = xv.cross(d).normalized()                               # hacia adelante, perpendicular al mango
    top = P(t_top + 0.04)
    grip = P(t_top + 0.42)
    for s in (-1, 1):
        rod(mk, sv, tuple(top), tuple(grip + xv * s * 0.17), 0.035, "wood_mid", sides=6, detail=True)
    rod(mk, sv, tuple(grip - xv * 0.19), tuple(grip + xv * 0.19), 0.04, "wood_mid", sides=6, detail=True)  # D
    # hoja: plato central, dos alas levantadas adelante (la cuchara) y labios a los costados
    bc = P(t_bot - 0.55)

    def B(pd, px, pn):
        return tuple(bc + d * pd + xv * px + n * pn)
    mk.hull(sv, [B(pd, px, pn) for pd in (-0.55, 0.50) for px in (-0.22, 0.22) for pn in (-0.02, 0.02)], "iron")
    for s in (-1, 1):
        mk.hull(sv, [B(pd, s * px, pn + dn) for pd in (-0.55, 0.50) for px, pn in ((0.20, 0.0), (0.45, -0.10))
                     for dn in (-0.025, 0.025)], "iron")
        mk.hull(sv, [B(pd, s * 0.45, pn) for pd in (-0.50, 0.50) for pn in (-0.10, -0.20)]
                + [B(pd, s * 0.42, pn) for pd in (-0.50, 0.50) for pn in (-0.10, -0.20)], "iron")
    mk.hull(sv, [B(pd, px, pn) for pd, w in ((0.48, 0.24), (0.66, 0.08)) for px in (-w, w) for pn in (-0.05, 0.05)],
            "iron")                                                                               # cuello de la hoja
    mk.bevel(sv, width=0.014, angle=35, mat="steel_light")
    mk.marker("_Grip", tuple(grip))
    mk.marker("_Grip2", tuple(P(t_bot + 1.5)))
    mk.marker("_Blade", tuple(bc))


def silver(mk):
    sn = mk.part("Silver_Neck", (0, WAIST, 0))
    base, r, tilt = (0, 4.66, -0.12), 0.26, -20
    cy, sz = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def NP(t, a, off):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + off
        return (rr * ca, base[1] + cy * t - rr * sa * sz, base[2] + sz * t + rr * sa * cy)
    for k, (t0, a0, t1, a1, w0, w1) in enumerate(((-0.06, 160, 0.14, 150, 0.08, 0.06), (0.12, 151, 0.22, 125, 0.05, 0.035),
                                                  (0.12, 152, 0.22, 175, 0.05, 0.03), (-0.06, 40, 0.14, 55, 0.07, 0.05))):
        out, dep = 0.02 + 0.007 * (k % 3), -0.05 - 0.006 * k
        t0, t1 = t0 - 0.008 * k, t1 + 0.006 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [NP(t, a - da, out), NP(t, a + da, out), NP(t, a - da, dep), NP(t, a + da, dep)]
        mk.hull(sn, pts, "silver_neon")
    for side, s in (("Left", -1), ("Right", 1)):
        part = mk.part(f"Silver_{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))

        def axis(y, s=s):
            if y >= 3.20:
                t = (3.48 - y) / 0.28
                rx, rz, dx = 0.26 + 0.02 * t, 0.27 + 0.01 * t, 0.02 * t
            else:
                t = (3.20 - y) / 0.30
                rx, rz, dx = 0.28 - 0.03 * t, 0.28 - 0.02 * t, 0.02 * (1 - t)
            return s * (arm_x(y) + dx), ARM_Z, rx, rz
        b = 180 if s < 0 else 0
        br = [((3.40, b - s * 60), (3.06, b - s * 75), 0.07, 0.05), ((3.08, b - s * 75), (2.94, b - s * 95), 0.05, 0.035),
              ((3.08, b - s * 74), (2.94, b - s * 50), 0.045, 0.03)]
        veins(mk, part, axis, br)


def build(mk):
    upper_torso(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_cap_goggles(mk)
    shovel(mk)
    silver(mk)

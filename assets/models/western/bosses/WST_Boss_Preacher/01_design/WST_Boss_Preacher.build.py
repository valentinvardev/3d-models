"""
Receta de WST_Boss_Preacher, Ezekiel Crane en forma humana (prompt 062, Bloques A + D + H + G). Jefe final.

Brief
- Silueta a 40 studs: alto y flaco como un palo, sombrero de predicador de ala ancha perfectamente
  plana, pelo gris largo y lacio hasta los hombros, levita negra abotonada hasta el cuello con los
  faldones quemados y deshilachados, la biblia negra en la mano izquierda, dedos largos colgando, la
  cara chupada con vetas de plata que suben a la frente como una corona.
- Escala: H = 6,5 (k = 6,5 / 5,2 = 1,25). Articulaciones del Bloque D escaladas: tobillo 0,325 ·
  rodilla 1,625 · cadera 3,055 · cintura 3,575 · codo 3,77 · muñeca 2,73 · hombro 4,94 · cuello 5,20.
  Flaco: pecho 1,50 (0,92 del caminante escalado), miembros 0,85 de grosor, hombros x = ±0,95, codos
  ±1,12, muñecas ±1,26, caderas ±0,32, brazos en z = -0,06. Cuello largo: los hombros caen hacia el
  cuello. El programador pasa esto a la ficha.
- Piezas: las 15 de R15, Eyes, Acc_Hat (base de la copa), Acc_Bible (la mano izquierda),
  Acc_RevolverL y Acc_RevolverR (centro de la empuñadura, en cada mano; ocultos hasta la fase 2),
  Silver_Head (cuello, como Head), Silver_Neck (cintura), Silver_LeftHand, Silver_RightHand,
  Silver_LeftHand_Crust, Silver_RightHand_Crust (muñeca), _MuzzleL, _MuzzleR.
- Tallado: cuencas hondas, boca de labios finos con la comisura derecha rota, botón que falta,
  quemaduras en el ruedo. Pintado: hollín en los puños de las mangas.
- Inferido: los marcadores se llaman _MuzzleL y _MuzzleR (dos objetos no pueden llamarse _Muzzle);
  los revólveres se modelan como los sostiene el brazo colgando (caño hacia abajo) y el izquierdo
  queda superpuesto a la biblia, que es de la fase 1; cachas wood_dark, caños gunmetal con la
  incrustación de neón, armazón silver_crust (prompt); cinta del sombrero leather_dark; sin Silver_Eyes
  (el prompt no las pide); las vetas van en una pieza por segmento; botas hide_black (negro con algo
  de matiz, para que no se fundan con el pantalón cloth_black).

Vueltas: 1) primera versión; el frente de la levita estaba mal medido (-0,44 en vez de -0,46 a 4,30),
la cruz flotaba 0,02, el rosario quedaba tapado por el puño, la biblia tapaba los dedos; las vetas de la
cara, sobre el cráneo, caían adentro de pómulos y mandíbula: ahora suben por el costado de la cara,
detrás del pómulo · 2) coplanares: barras de las dos cruces, vetas de la frente contra el ala del
sombrero (4,98-5,015), vetas de la mano contra la tapa de la palma (2,78), tapas de la levita (3,62),
biblia contra los dedos (x = -1,365); nariz flotando 0,06 adelante de la cara; botas negras; puntas del
pelo · 3) espaldas de las barras de la cruz todavía en el mismo plano (el corrimiento se compensaba con el
grosor); dos vetas de la frente terminando a la misma altura; rosario centrado en la mano (estaba en el
brazo, 0,022 afuera).

Revisión
- 4102 triángulos contra 4500: entra en el tope.
- Alto 6,616 con el sombrero; el cuerpo, 6,5. Ancho 2,95.
- Dudoso: el revólver izquierdo queda superpuesto a la biblia (son de fases distintas, el motor muestra
  uno u otro); los marcadores se llaman _MuzzleL/_MuzzleR; la abertura de la levita abajo de la cintura
  muestra el pantalón como un rectángulo más claro de frente.
"""

import math

from mathutils import Vector

import humanoid as hu

H = 6.5
K = H / 5.2
XW = 0.92                               # cara angosta (chupada)
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH_X, ARM_Z, LEG_X = 0.95, -0.06, 0.32
TAN8 = math.tan(math.radians(8))
EL_X, WR_X = SH_X + (SHOULDER - ELBOW) * TAN8, SH_X + (SHOULDER - WRIST) * TAN8
NECK_P = (0.0, NECK, -0.06)
HEAD_FWD, HEAD_TILT = 0.10, -6

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def head(pts):
    return about([(x * K * XW, y * K, z * K - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def arm_x(y):
    return SH_X + (SHOULDER - y) * TAN8


def coat_front(y):
    """z del frente de la levita (cara plana) a la altura y."""
    if y <= 4.30:
        return -0.40 - 0.06 * (y - 3.50) / 0.80
    return -0.46 + 0.16 * (y - 4.30) / 0.58


def rod(mk, part, a, b, r, mat, sides=6, detail=False):
    A, B = Vector(a), Vector(b)
    d = (B - A).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u)
    pts = [tuple(P + r * (math.cos(t) * u + math.sin(t) * v)) for P in (A, B)
           for t in [2 * math.pi * (i + 0.5) / sides for i in range(sides)]]
    mk.hull(part, pts, mat, detail=detail)


def coat_tail(mk, ul, s):
    """Faldón de la levita sobre el muslo, abierto adelante, ruedo quemado y deshilachado."""
    top = [(0.03, 3.10, 0.46), (0.34, 3.10, 0.48), (0.62, 3.10, 0.34), (0.72, 3.10, 0.06), (0.70, 3.10, -0.26),
           (0.50, 3.10, -0.44)]
    bot = [(0.03, 2.30, 0.56), (0.36, 2.28, 0.60), (0.70, 2.30, 0.44), (0.82, 2.32, 0.08), (0.78, 2.36, -0.28),
           (0.56, 2.38, -0.44)]
    inner = [(0.22, 3.10, 0.06), (0.22, 2.30, 0.12)]
    mk.hull(ul, [(s * x, y, z) for x, y, z in top + bot + inner], "cloth_black")
    hem = [(0.06, 2.30, 0.57), (0.30, 2.285, 0.60), (0.56, 2.29, 0.52), (0.76, 2.305, 0.30), (0.82, 2.32, 0.04),
           (0.79, 2.35, -0.22)]
    for i in range(len(hem) - 1):
        (x0, y0, z0), (x1, y1, z1) = hem[i], hem[i + 1]
        ang = -math.degrees(math.atan2(z1 - z0, s * (x1 - x0)))
        mat = "wood_charred" if i % 2 == 0 else "cloth_black"                                     # chamuscado
        mk.prism(ul, [(-0.10, 0), (0.10, 0), (0.03, -0.13 - 0.05 * (i % 2))], 0.03, mat, plane="xy",
                 center=(s * (x0 + x1) / 2, (y0 + y1) / 2 + 0.02, (z0 + z1) / 2), rot=(0, ang, 0), detail=True)
    mk.paint(ul, "wood_charred", box=((s * 0.45, 2.36, 0.30), (1.2, 0.14, 1.0)))                  # borde quemado


def hand(mk, part, s, hx):
    """Mano flaca de dedos largos: palma, pulgar y dos bloques de dedos estirados (prompt)."""
    mk.hull(part, round_ring(2.78, hx, ARM_Z, 0.20, 0.32) + round_ring(2.54, hx + s * 0.01, ARM_Z, 0.22, 0.36)
            + round_ring(2.40, hx + s * 0.015, ARM_Z, 0.20, 0.34), "skin_dead")
    for dz, ln in ((-0.085, 0.44), (0.085, 0.38)):                                                # dos bloques de dedos
        mk.hull(part, [(hx + s * 0.015 + dx, y, ARM_Z + dz + d) for dx in (-0.07, 0.07)
                       for y, w in ((2.44, 0.075), (2.44 - ln, 0.055)) for d in (-w, w)], "skin_dead")
    mk.box(part, (hx - s * 0.08, 2.52, ARM_Z - 0.17), (0.08, 0.22, 0.08), "skin_dead", rot=(-15, 0, 0))   # pulgar


# ======================================================================================
def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    # levita abotonada hasta el cuello: un solo casco negro, hombros que caen hacia el cuello largo
    mk.hull(ut, ring(3.50, 0, 0.02, 1.30, 0.84) + ring(4.30, 0, -0.02, 1.50, 0.88)
            + [(-0.40, 4.88, -0.30), (0.40, 4.88, -0.30), (-0.84, 4.70, -0.24), (0.84, 4.74, -0.24),
               (-0.84, 4.72, 0.28), (0.84, 4.76, 0.28), (-0.30, 4.96, 0.20), (0.30, 4.96, 0.20),
               (-0.42, 4.64, 0.52), (0.42, 4.66, 0.52), (0.0, 4.72, 0.56)], "cloth_black")
    # botones de la levita (falta uno) y la costura del cierre
    for y in (3.66, 3.92, 4.44, 4.70):
        mk.cyl(ut, (0.05, y, coat_front(y) - 0.01), 0.035, 0.03, "iron", axis="z", sides=6, detail=True)
    mk.carve(ut, "coal", points=mk.pts_cyl((0.05, 4.18, coat_front(4.18)), 0.03, 0.06, axis="z", sides=6))
    # cuello largo, cuello blanco de la camisa, corbatín de cordón
    mk.cyl(ut, (0, 5.10, -0.10), 0.19, 0.62, "skin_dead", rot=(-12, 0, 0), sides=10)
    mk.cyl(ut, (0, 4.94, -0.12), 0.24, 0.14, "cloth_white", rot=(-12, 0, 0), sides=10)
    for s in (-1, 1):
        mk.hull(ut, [(s * 0.03, 4.94, -0.37), (s * 0.15, 4.95, -0.33), (s * 0.08, 4.82, -0.36),
                     (s * 0.03, 4.94, -0.33), (s * 0.15, 4.95, -0.29), (s * 0.08, 4.82, -0.32)], "cloth_white")
        mk.hull(ut, [(s * 0.012, 4.84, coat_front(4.84) - 0.02), (s * 0.035, 4.84, coat_front(4.84) - 0.02),
                     (s * 0.035, 4.50, coat_front(4.50) - 0.015), (s * 0.06, 4.50, coat_front(4.50) - 0.015),
                     (s * 0.012, 4.84, coat_front(4.84) + 0.02), (s * 0.06, 4.50, coat_front(4.50) + 0.02)],
                "cloth_black", detail=True)
    mk.box(ut, (0, 4.86, -0.355), (0.07, 0.06, 0.05), "cloth_black", detail=True)
    # cruz de hierro colgando de una cadena sobre el pecho
    chain = [(-0.20, 4.90, -0.36), (-0.12, 4.60, coat_front(4.60) - 0.03), (0.0, 4.40, coat_front(4.40) - 0.03),
             (0.12, 4.60, coat_front(4.60) - 0.03), (0.20, 4.90, -0.36)]
    for p0, p1 in zip(chain, chain[1:]):
        rod(mk, ut, p0, p1, 0.014, "iron", sides=4, detail=True)
    cz = coat_front(4.26) - 0.025
    mk.box(ut, (0, 4.24, cz), (0.06, 0.26, 0.04), "iron", detail=True)
    mk.box(ut, (0, 4.29, cz - 0.006), (0.18, 0.06, 0.04), "iron", detail=True)
    return ut


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.98, 0, 0, 1.10, 0.68) + ring(3.64, 0, 0.02, 1.30, 0.82), "cloth_black")    # pantalón
    # levita abajo: atrás y costados, abierta adelante abajo de la cintura
    mk.hull(lt, [(x, y, max(z, -0.26)) for x, y, z in ring(3.00, 0, 0.04, 1.40, 0.92) + ring(3.62, 0, 0.02, 1.36, 0.88)],
            "cloth_black")
    for s in (-1, 1):
        mk.hull(lt, [(s * 0.14, 3.61, -0.43), (s * 0.30, 3.02, -0.44), (s * 0.68, 3.61, -0.30), (s * 0.72, 3.02, -0.32),
                     (s * 0.40, 3.61, -0.10), (s * 0.44, 3.02, -0.10)], "cloth_black")
    return lt


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(mk, ul, (x, HIP, 0), (x, KNEE, 0), 0.54, 0.56, 0.44, 0.46, "cloth_black", over=0.06)
        coat_tail(mk, ul, s)
        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(mk, ll, (x, KNEE, 0), (x, 0.80, 0), 0.44, 0.46, 0.38, 0.40, "cloth_black", over=0.06)
        mk.hull(ll, ring(0.96, x, 0.0, 0.44, 0.48) + ring(0.24, x, 0.0, 0.40, 0.46), "hide_black")     # bota negra
        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + d, y, z) for d in (-0.21, 0.21) for y, z in ((0.07, 0.24), (0.36, 0.22), (0.32, -0.14))]
                + [(x + d, y, z) for d in (-0.15, 0.15) for y, z in ((0.07, -0.60), (0.18, -0.54))]
                + [(x, 0.07, -0.68), (x, 0.15, -0.62)], "hide_black")
        mk.hull(ft, [(x + d, y, z) for d in (-0.22, 0.22) for y in (0.0, 0.08) for z in (0.26, -0.56)]
                + [(x, 0.0, -0.70), (x, 0.08, -0.70)], "coal")


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        ua = mk.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        mk.hull(ua, round_ring(5.02, s * arm_x(5.02), ARM_Z, 0.34, 0.38) + round_ring(4.80, s * arm_x(4.80), ARM_Z, 0.44, 0.46)
                + round_ring(3.72, s * arm_x(3.72), ARM_Z, 0.38, 0.40), "cloth_black")
        la = mk.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        mk.hull(la, round_ring(3.84, s * arm_x(3.84), ARM_Z, 0.38, 0.40) + round_ring(2.92, s * arm_x(2.92), ARM_Z, 0.32, 0.34),
                "cloth_black")
        mk.hull(la, round_ring(3.04, s * arm_x(3.04), ARM_Z, 0.40, 0.42, n=8) + round_ring(2.80, s * arm_x(2.80), ARM_Z, 0.40, 0.42, n=8),
                "cloth_black")                                                                     # puño
        mk.hull(la, round_ring(2.86, s * arm_x(2.86), ARM_Z, 0.30, 0.32, n=8) + round_ring(2.74, s * arm_x(2.74), ARM_Z, 0.28, 0.30, n=8),
                "cloth_white")
        mk.paint(la, "wood_charred", ball=((s * (arm_x(2.86) + 0.20), 2.86, ARM_Z - 0.10), 0.14))  # puño chamuscado
        hd = mk.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hand(mk, hd, s, s * (WR_X + 0.02))
        if side == "Left":   # rosario de cuentas de plata enrollado en la muñeca
            for i in range(14):
                a = 2 * math.pi * i / 14
                mk.ball(la, (s * (WR_X + 0.02) + 0.112 * math.cos(a), 2.74 + 0.02 * math.sin(3 * a), ARM_Z + 0.16 * math.sin(a)),
                        0.035, "silver_crust", subdiv=0, detail=True)
            for i in range(4):
                mk.ball(la, (s * arm_x(2.74) - 0.14, 2.65 - 0.065 * i, ARM_Z - 0.06), 0.032, "silver_crust", subdiv=0,
                        detail=True)
            mk.box(la, (s * arm_x(2.74) - 0.14, 2.35, ARM_Z - 0.06), (0.03, 0.10, 0.03), "silver_crust", detail=True)
            mk.box(la, (s * arm_x(2.74) - 0.14, 2.37, ARM_Z - 0.06), (0.036, 0.03, 0.08), "silver_crust", detail=True)


def head_and_hat(mk):
    hd = mk.part("Head", NECK_P)
    # cara larga y chupada: mejillas hundidas, mandíbula fina, pómulos marcados
    mk.hull(hd, head(round_ring(4.26, 0, -0.18, 0.62, 0.60) + round_ring(4.52, 0, -0.21, 0.72, 0.80)
                     + round_ring(4.80, 0, -0.25, 0.92, 0.90) + round_ring(5.02, 0, -0.26, 0.86, 0.86)
                     + round_ring(5.16, 0, -0.26, 0.58, 0.62)), "skin_dead")
    mk.hull(hd, head([(-0.22, 4.40, -0.58), (0.22, 4.40, -0.58), (-0.26, 4.44, -0.16), (0.26, 4.44, -0.16),
                      (-0.14, 4.10, -0.64), (0.14, 4.10, -0.64), (-0.18, 4.14, -0.16), (0.18, 4.14, -0.16),
                      (0, 4.04, -0.68)]), "skin_dead")                                                # mandíbula fina
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.26, 4.66, -0.62), (s * 0.44, 4.68, -0.50), (s * 0.34, 4.58, -0.56),
                          (s * 0.30, 4.66, -0.44), (s * 0.44, 4.62, -0.36)]), "skin_dead")           # pómulos
        mk.hull(hd, head([(s * 0.03, 4.86, -0.70), (s * 0.44, 4.90, -0.58), (s * 0.03, 4.94, -0.66),
                          (s * 0.44, 4.96, -0.54), (s * 0.03, 4.88, -0.45), (s * 0.42, 4.93, -0.40)]), "skin_dead")
        mk.hull(hd, head(mk.pts_box((s * 0.46, 4.70, -0.22), (0.08, 0.24, 0.15), top=(1, 0.7))), "skin_dead")
    mk.hull(hd, head([(0, 4.84, -0.66), (0, 4.62, -0.86), (-0.07, 4.58, -0.60), (0.07, 4.58, -0.60),
                      (0, 4.57, -0.70)]), "skin_dead")                                               # nariz fina
    # pelo gris largo y lacio hasta los hombros (cuelga atrás y a los costados)
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.42, 5.04, -0.34), (s * 0.48, 5.04, 0.0), (s * 0.40, 5.04, 0.20),
                          (s * 0.44, 4.04, -0.24), (s * 0.52, 3.98, 0.02), (s * 0.40, 3.98, 0.26),
                          (s * 0.30, 5.04, 0.0), (s * 0.30, 4.0, 0.0)]), "hair_grey")
    mk.hull(hd, head([(s * x, y, z) for s in (-1, 1) for x, y, z in ((0.40, 5.06, 0.10), (0.30, 4.00, 0.30),
                                                                   (0.10, 5.10, 0.24), (0.10, 3.96, 0.40))]
                     + [(0, 5.08, 0.0)]), "hair_grey")                                                # atrás
    for x in (-0.30, -0.12, 0.06, 0.24):
        mk.hull(hd, head([(x - 0.08, 4.02, 0.30 + 0.25 * (0.4 - abs(x))), (x + 0.08, 4.02, 0.30 + 0.25 * (0.4 - abs(x))),
                          (x - 0.07, 4.02, 0.20), (x + 0.07, 4.02, 0.20),
                          (x + 0.01, 3.86 - 0.04 * (abs(x) < 0.2), 0.32)]), "hair_grey", detail=True)   # mechones
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.76, -0.74), 0.16, scale=(1.0, 0.75, 1.0),
                                                               subdiv=0)))                          # cuencas hondas
    mouth = [(-0.13, 4.36), (0.15, 4.37), (0.20, 4.33), (0.14, 4.30), (-0.13, 4.31)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.90, -0.52)]))     # labios finos, comisura rota
    for i in range(5):
        x = -0.10 + 0.05 * i
        mk.hull(hd, head([(x - 0.022, 4.37, -0.62), (x + 0.022, 4.37, -0.62), (x - 0.015, 4.33, -0.62),
                          (x + 0.015, 4.33, -0.62), (x - 0.02, 4.37, -0.50), (x + 0.02, 4.37, -0.50),
                          (x, 4.335, -0.50)]), "bone", detail=True)
    mk.paint(hd, "skin_dead_dark", ball=(hp((0.0, 4.20, -0.62)), 0.12))
    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.76, -0.64)), 0.065 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)

    # sombrero de predicador: copa chata y ala ancha perfectamente plana (2,0)
    base = hp((0, 5.00, -0.26))
    hat = mk.part("Acc_Hat", base)
    rx, rz = 1.0 / (K * XW), 1.0 / K
    brim = [(rx * math.cos(2 * math.pi * i / 24), rz * math.sin(2 * math.pi * i / 24)) for i in range(24)]
    mk.hull(hat, head([(x, y, z - 0.26) for x, z in brim for y in (4.98, 5.015)]), "cloth_black")
    mk.hull(hat, head(round_ring(4.99, 0, -0.26, 0.96, 0.98, n=14) + round_ring(5.28, 0, -0.26, 0.92, 0.94, n=14)),
            "cloth_black")
    mk.hull(hat, head(round_ring(5.03, 0, -0.26, 0.975, 0.995, n=14) + round_ring(5.10, 0, -0.26, 0.97, 0.99, n=14)),
            "leather_dark")


def bible(mk):
    """Biblia gruesa negra en la mano izquierda, con esquineras de bronce."""
    c = (-(WR_X + 0.02), WRIST - 0.40, ARM_Z - 0.26)
    bb = mk.part("Acc_Bible", c)
    cx, cy, cz = c
    mk.box(bb, (cx, cy, cz), (0.18, 0.56, 0.42), "cloth_black")                                    # tapas
    mk.box(bb, (cx, cy - 0.005, cz - 0.012), (0.13, 0.54, 0.41), "paint_cream")                    # hojas
    mk.bevel(bb, width=0.012, angle=35)
    for dy in (-0.25, 0.25):
        for dz in (-0.19, 0.19):
            for sx in (-1, 1):
                mk.box(bb, (cx + sx * 0.087, cy + dy, cz + dz), (0.012, 0.07, 0.07), "brass", detail=True)


def revolver(mk, name, marker, g):
    """Revólver de caño largo: armazón silver_crust, caño con incrustación de neón (fase 2).
    Espacio del arma: caño a -Z, lomo +Y, origen en la empuñadura; se lleva a la mano colgando (caño abajo)."""
    def G(p):
        x, y, z = p
        return (g[0] + x, g[1] + z, g[2] - y)

    def GS(pts):
        return [G(p) for p in pts]
    rv = mk.part(name, g)
    by, bz0, bz1 = 0.30, -0.46, -1.30                                    # eje del caño, del armazón a la boca
    mk.hull(rv, GS([(x, y, z) for x in (-0.07, 0.07) for y, z in ((0.40, -0.48), (0.40, -0.06), (0.12, -0.48),
                                                                  (0.10, -0.04), (0.34, 0.02))]), "silver_crust")   # armazón
    mk.hull(rv, GS(mk.pts_cyl((0, 0.27, -0.28), 0.12, 0.28, axis="z", sides=12)), "gunmetal")             # tambor
    mk.hull(rv, GS(mk.pts_cyl((0, by, (bz0 + bz1) / 2), 0.055, bz0 - bz1, axis="z", sides=8)), "gunmetal")  # caño largo
    mk.hull(rv, GS(mk.pts_cyl((0, 0.205, -0.70), 0.03, 0.46, axis="z", sides=6)), "silver_crust")        # funda de la varilla
    mk.hull(rv, GS([(x, y, z) for x in (-0.06, 0.06) for y, z in ((0.14, 0.02), (0.22, 0.10), (-0.24, 0.06),
                                                                  (-0.22, 0.22), (-0.10, 0.20))]), "wood_dark")   # cacha
    mk.bevel(rv, width=0.012, angle=35)
    mk.carve(rv, "coal", points=GS(mk.pts_cyl((0, by, bz1), 0.028, 0.12, axis="z", sides=8)))
    for sx in (-1, 1):   # incrustación de neón a lo largo del caño
        mk.hull(rv, GS([(sx * 0.05, by + dy, z) for dy in (-0.012, 0.012) for z in (bz0 - 0.02, bz1 + 0.04)]
                       + [(sx * 0.062, by + dy, z) for dy in (-0.012, 0.012) for z in (bz0 - 0.02, bz1 + 0.04)]),
                "silver_neon", detail=True)
    mk.hull(rv, GS([(x, y, z) for x in (-0.03, 0.03) for y, z in ((0.36, -0.02), (0.36, 0.04), (0.46, 0.10),
                                                                  (0.44, 0.14))]), "silver_crust", detail=True)   # martillo
    guard = [(-0.20, 0.12), (-0.19, 0.02), (-0.13, -0.04), (-0.04, -0.04), (0.0, 0.02), (0.0, 0.12),
             (-0.03, 0.12), (-0.04, 0.03), (-0.06, 0.005), (-0.12, 0.005), (-0.15, 0.03), (-0.16, 0.12)]
    mk.prism(rv, guard, 0.04, "silver_crust", plane="zy", center=g, rot=(-90, 0, 0), detail=True)
    mk.marker(marker, G((0, by, bz1)))


def silver(mk):
    # cara: dos ramas de cada lado que suben por las sienes y se juntan en la frente como una corona
    sh = mk.part("Silver_Head", NECK_P)
    rings = ((4.26, -0.18, 0.62, 0.60), (4.52, -0.21, 0.72, 0.80), (4.80, -0.25, 0.92, 0.90), (5.02, -0.26, 0.86, 0.86),
             (5.16, -0.26, 0.58, 0.62))

    def FP(y, a, off):
        for (ya, ca, wa, da), (yb, cb, wb, db) in zip(rings, rings[1:]):
            if ya <= y <= yb:
                t = (y - ya) / (yb - ya)
                cz, w, d = ca + (cb - ca) * t, wa + (wb - wa) * t, da + (db - da) * t
                break
        ang = math.radians(a)
        return (math.cos(ang) * (w / 2 + off), y, cz + math.sin(ang) * (d / 2 + off))
    branches = []
    for s in (-1, 1):
        A = (lambda a, s=s: 270 + s * (a - 270))
        branches += [((4.34, A(202)), (4.58, A(198)), 0.07, 0.06), ((4.57, A(198)), (4.84, A(212)), 0.06, 0.05),
                     ((4.83, A(212)), (4.945, A(238)), 0.05, 0.04), ((4.94, A(238)), (4.958, A(262)), 0.04, 0.035),
                     ((4.60, A(199)), (4.72, A(220)), 0.04, 0.03)]
    branches += [((4.952, 262), (4.962, 278), 0.04, 0.04)]
    for k, ((y0, a0), (y1, a1), w0, w1) in enumerate(branches):
        out, dep = 0.03 + 0.006 * (k % 3), -0.04 - 0.004 * k
        y0, y1 = y0 - 0.003 * k, y1 + 0.0025 * k
        pts = []
        for y, a, w in ((y0, a0, w0), (y1, a1, w1)):
            da = math.degrees(w / 2 / 0.45)
            for off in (out, dep):
                pts += [FP(y, a - da, off), FP(y, a + da, off)]
        mk.hull(sh, head(pts), "silver_neon")
    # cuello largo
    sn = mk.part("Silver_Neck", (0, WAIST, 0))
    base, r, tilt = (0, 5.10, -0.10), 0.19, -12
    cy, sz = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def NP(t, a, off):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + off
        return (rr * ca, base[1] + cy * t - rr * sa * sz, base[2] + sz * t + rr * sa * cy)
    for k, (t0, a0, t1, a1, w0, w1) in enumerate(((-0.16, 200, 0.12, 215, 0.07, 0.05), (0.10, 214, 0.26, 235, 0.045, 0.03),
                                                  (-0.16, 340, 0.12, 325, 0.07, 0.05), (0.10, 326, 0.26, 305, 0.045, 0.03),
                                                  (-0.12, 120, 0.20, 100, 0.06, 0.04))):
        out, dep = 0.018 + 0.006 * (k % 3), -0.04 - 0.005 * k
        t0, t1 = t0 - 0.007 * k, t1 + 0.005 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [NP(t, a - da, out), NP(t, a + da, out), NP(t, a - da, dep), NP(t, a + da, dep)]
        mk.hull(sn, pts, "silver_neon")
    # manos: vetas en el dorso y costras en los nudillos
    for side, s in (("Left", -1), ("Right", 1)):
        hx = s * (WR_X + 0.02)
        sv = mk.part(f"Silver_{side}Hand", (s * WR_X, WRIST, ARM_Z))
        for k, ((y0, dz0), (y1, dz1), w0, w1) in enumerate((((2.76, 0.02), (2.54, 0.0), 0.05, 0.04),
                                                             ((2.55, 0.0), (2.42, -0.07), 0.04, 0.03),
                                                             ((2.56, 0.01), (2.42, 0.08), 0.035, 0.025))):
            out, dep = 0.018 + 0.005 * k, -0.03 - 0.004 * k
            y0, y1 = y0 - 0.005 * k, y1 + 0.004 * k
            pts = []
            for y, dz, w in ((y0, dz0, w0), (y1, dz1, w1)):
                half = (0.20 if y > 2.54 else 0.21) / 2 * 0.95
                for off in (out, dep):
                    for sw in (-1, 1):
                        pts.append((hx + s * (half + off), y, ARM_Z + dz + sw * w / 2))
            mk.hull(sv, pts, "silver_neon")
        cr = mk.part(f"Silver_{side}Hand_Crust", (s * WR_X, WRIST, ARM_Z))
        for dz, h in ((-0.10, 0.07), (0.0, 0.09), (0.10, 0.06)):
            base_x = hx + s * 0.105
            mk.hull(cr, [(base_x - s * 0.03, 2.46, ARM_Z + dz - 0.045), (base_x - s * 0.03, 2.46, ARM_Z + dz + 0.045),
                         (base_x - s * 0.03, 2.36, ARM_Z + dz - 0.04), (base_x - s * 0.03, 2.36, ARM_Z + dz + 0.04),
                         (base_x + s * h, 2.43, ARM_Z + dz), (base_x + s * h * 0.7, 2.38, ARM_Z + dz + 0.02)],
                    "silver_crust")
        mk.hull(cr, [(hx + s * 0.08, y, ARM_Z + dz) for y in (2.47, 2.35) for dz in (-0.15, 0.15)]
                + [(hx + s * 0.125, y, ARM_Z + dz) for y in (2.46, 2.36) for dz in (-0.14, 0.14)], "silver_neon")


def build(mk):
    upper_torso(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_and_hat(mk)
    bible(mk)
    revolver(mk, "Acc_RevolverR", "_MuzzleR", (WR_X + 0.02, WRIST - 0.24, ARM_Z))
    revolver(mk, "Acc_RevolverL", "_MuzzleL", (-(WR_X + 0.02), WRIST - 0.24, ARM_Z))
    silver(mk)

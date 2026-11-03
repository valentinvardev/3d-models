"""
Receta de WST_Boss_Sheriff, el Sheriff infectado (prompt 025, Bloques A + D + H + G). Jefe del MVP.

Brief
- Silueta a 40 studs: sombrero cattleman negro alto de ala ancha, hombros anchos con levita marrón
  abierta y faldones que se abren atrás, frente blanco y negro (camisa y chaleco) con la estrella de
  plata en el pecho izquierdo, bigote de morsa gris, escopeta recortada colgando de la mano derecha y
  grilletes rotos colgando de la muñeca izquierda.
- Escala: H = 6,2 (k = 6,2 / 5,2 = 1,192). Articulaciones del Bloque D escaladas: tobillo 0,31 ·
  rodilla 1,55 · cadera 2,914 · cintura 3,41 · codo 3,596 · muñeca 2,604 · hombro 4,712 · cuello 4,96.
  Torso 1,25 veces el ancho del caminante escalado (pecho 1,96): hombros en x = ±1,12, codos ±1,27,
  muñecas ±1,41 (8° hacia afuera), caderas ±0,40, brazos en z = -0,14. El programador pasa esto a la ficha.
- Piezas: las 15 de R15 con el origen en su articulación, Eyes, Acc_Badge (centro de la estrella),
  Acc_Hat (base de la copa), Acc_Shotgun (centro de la empuñadura, dentro de la mano derecha),
  Acc_Shackles (centro del grillete, muñeca izquierda), Silver_Eyes (cuello, como Eyes),
  Silver_Neck (cintura, como UpperTorso: las vetas van sobre el cuello, que es de UpperTorso), _Muzzle.
- Tallado: cuencas, boca, mejilla derecha rota con muelas, dos balazos en el chaleco, el agujero del
  alfiler de la placa (queda a la vista cuando se cae), hebilla calada, bocas de los caños. Pintado:
  mentón y yemas. El pliegue de la copa se arma con dos lomos (sin booleanas: ver vuelta 2).
- Daños (Bloque H): mejilla rota (prompt), balazos en el pecho, ruedo de los faldones deshilachado.
- Cabeza: se dibuja en el espacio del caminante (H = 5,2) y head() la escala por k, la adelanta 0,15 y
  la baja 8° alrededor del cuello: mandíbula pesada y cuadrada, ceño fruncido, pómulos, bigote de morsa
  con las puntas por fuera de la mandíbula.
- Inferido (el prompt no lo dice): pantalón cloth_blue (dice "dark trousers"), botas leather_dark con
  la vuelta en leather; la escopeta se modela como la sostiene el brazo colgando (caños hacia abajo,
  -Y): cuando el brazo R15 se levanta 90° adelante apunta a -Z; el cinturón de cartuchos va cruzado y
  más bajo a la derecha; sin cartucheras (pelea con escopeta); martingala atrás; chaleco cruzado
  (el panel izquierdo, el de los botones, monta sobre el derecho).

Vueltas: 1) primera versión · 2) hombros: el tope del brazo asomaba 0,14 sobre la levita como una
hombrera (brazos de 10 lados, levita hasta x = 1,16); faldones 0,1 más abiertos; nuca con la forma del
cráneo (era una caja); sombrero sin booleanas (el ala y la copa encimadas dejaban 8 bordes abiertos);
hebilla 0,02 adentro del cinturón (estaba a 0,005: bordes rotos) · 3) puntas del chaleco encimadas
(se tocaban justo en x = 0: borde con 4 caras), grillete 0,03 más arriba (flotaba 0,003), vetas a
distinta altura (eran coplanares) · 4-5) bigote de morsa: las caídas medían 0,16 y tapaban el mentón
como una máscara; ahora miden 0,11 y salen 0,06 por fuera de la mandíbula; boca de ±0,15 · 6) escopeta
rehecha (era una caja con dos caños): fences, placas de acero, martillos con espuela, palanca, banda,
delantera y culata que asoma atrás del puño; chaleco cruzado (dejaba un borde suelto).

Revisión
- 5930 triángulos contra 3500 de referencia (calidad primero, jefe del MVP): Acc_Shotgun 1396 (chanflanes
  en todas las piezas y el detalle mecánico; sin chanflanes ~900), Head 976 (cuencas, boca, mejilla rota
  con muelas, bigote), Acc_Badge 296 contra 120 del prompt (seis bolitas de 20 y el chanflán; con bolitas
  de 8 se leían como rombos), Acc_Shackles 352 (eslabones que son anillos de verdad). Ninguna pieza pasa de 1400.
- Alto 6,656 con el sombrero; el cuerpo, 6,2. Ancho 3,45 (de la cadena de los grilletes a la mano derecha).
- Silver_Eyes es 0,012 más grande que Eyes y lo encierra: en las capturas se ven los ojos de plata
  (etapa Dusty Gulch). Sin el overlay, Eyes queda en hueso.
- Dudoso: el cuello parado de la levita sube a 4,99 detrás de la cabeza y de costado se ve como un bloque;
  hair_grey y skin_dead tienen casi el mismo valor, el bigote se separa por la forma y el mentón pintado.
"""

import math

import humanoid as hu

H = 6.2
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH_X, EL_X, WR_X, LEG_X = 1.12, 1.27, 1.41, 0.40
ARM_Z = -0.14
NECK_P = (0.0, NECK, -0.12)
HEAD_FWD, HEAD_TILT = 0.15, -8
GRIP = (WR_X + 0.03, WRIST - 0.30, ARM_Z)      # centro de la empuñadura de la escopeta (mano derecha)
BADGE = (-0.40, 4.25)                          # centro de la estrella en el pecho izquierdo (x, y)

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def head(pts):
    """Puntos del espacio del caminante (H = 5,2) a la cabeza del Sheriff: escala k, adelanta y baja."""
    return about([(x * K, y * K, z * K - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def shirt_front(y):
    """z del frente de la camisa (cara plana del casco del torso) a la altura y."""
    if y <= 4.0:
        return -0.38 - 0.2059 * (y - 3.32)
    return -0.52 + 0.2727 * (y - 4.0)


def arm_x(y):
    """x del eje del brazo a la altura y (del hombro a la muñeca, 8° hacia afuera)."""
    return SH_X + (SHOULDER - y) * (WR_X - SH_X) / (SHOULDER - WRIST)


def clip_front(points, zmin):
    return [(x, y, max(z, zmin)) for x, y, z in points]


def gun(p):
    """Espacio del arma (caño a -Z, arriba +Y, origen en la empuñadura) -> mano derecha colgando:
    el caño apunta abajo, el lomo adelante y la empuñadura atrás."""
    x, y, z = p
    return (GRIP[0] + x, GRIP[1] + z, GRIP[2] - y)


def guns(points):
    return [gun(p) for p in points]


def c_ring(mk, part, center, rx, ry, wire, depth, mat, plane="xy", rot=(0, 0, 0), n=10, gap=14, detail=False):
    """Anillo abierto (perfil en C extruido): grilletes y eslabones."""
    prof = []
    for i in range(n + 1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append((rx * math.cos(a), ry * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append(((rx - wire) * math.cos(a), (ry - wire) * math.sin(a)))
    mk.prism(part, prof, depth, mat, plane=plane, center=center, rot=rot, detail=detail)


def star(n, r_out, r_in, phase=90):
    return [((r_out if k % 2 == 0 else r_in) * math.cos(math.radians(phase + 180 / n * k)),
             (r_out if k % 2 == 0 else r_in) * math.sin(math.radians(phase + 180 / n * k))) for k in range(2 * n)]


# ======================================================================================
def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    # camisa: casco base del torso, pecho ancho y adelantado, joroba arriba atrás
    top = [(-0.62, 4.64, -0.345), (0.62, 4.64, -0.345), (-0.96, 4.58, -0.28), (0.96, 4.68, -0.28),
           (-0.96, 4.60, 0.20), (0.96, 4.70, 0.20), (-0.36, 4.72, 0.16), (0.36, 4.74, 0.16)]
    hump = [(-0.50, 4.40, 0.52), (0.50, 4.44, 0.52), (0.0, 4.52, 0.56)]
    mk.hull(ut, ring(3.32, 0, 0.02, 1.50, 0.80) + ring(4.00, 0, -0.02, 1.96, 1.00) + top + hump, "cloth_white")

    # chaleco negro largo: dos paneles de adelante, 0,04 por fuera de la camisa, escote en V
    # el panel izquierdo (el de los botones) monta 0,006 por delante del derecho y cruza el medio
    for s, off, inner in ((-1, 0.046, 0.03), (1, 0.04, 0.0)):
        mk.hull(ut, [p for x, y in ((inner, 3.28), (inner, 3.88), (s * 0.034, 4.00), (s * 0.26, 4.62), (s * 0.80, 3.28),
                                    (s * 0.80, 4.00), (s * 0.78, 4.58))
                     for p in ((x, y, shirt_front(y) - off), (x, y, shirt_front(y) + 0.12))], "cloth_black")

    # levita: espalda y costados (el frente queda adentro de la camisa) + solapas
    def lowered(pts):  # hombro izquierdo 0,1 más bajo
        return [(x, y - 0.10 * max(0.0, (-x - 0.6) / 0.44), z) for x, y, z in pts]
    back = (clip_front(ring(3.30, 0, 0.04, 1.62, 0.96), -0.30) + clip_front(ring(4.00, 0, 0.0, 2.10, 1.10), -0.40)
            + lowered([(-1.16, 4.60, -0.26), (1.16, 4.60, -0.26), (-1.16, 4.62, 0.24), (1.16, 4.62, 0.24),
                       (-0.82, 4.76, -0.30), (0.82, 4.76, -0.30), (-0.82, 4.78, 0.28), (0.82, 4.78, 0.28),
                       (-0.40, 4.82, 0.24), (0.40, 4.82, 0.24), (-0.40, 4.78, -0.28), (0.40, 4.78, -0.28)])
            + [(-0.54, 4.42, 0.60), (0.54, 4.46, 0.60), (0.0, 4.54, 0.64)])
    mk.hull(ut, back, "cloth_brown")
    for s in (-1, 1):
        drop = 0.10 if s < 0 else 0.0
        lap = [(s * 0.60, 3.30, shirt_front(3.30) - 0.08), (s * 0.66, 4.00, shirt_front(4.00) - 0.08),
               (s * 0.62, 4.40, shirt_front(4.40) - 0.08), (s * 0.42, 4.72, -0.38),
               (s * 1.00, 3.30, -0.26), (s * 1.07, 4.00, -0.38), (s * 1.12, 4.58 - drop, -0.27),
               (s * 0.75, 3.30, -0.10), (s * 0.80, 4.00, -0.10), (s * 0.60, 4.66, -0.10)]
        mk.hull(ut, lap, "cloth_brown")
        # vuelta de la solapa: una cuña encima, de la cintura del pecho al cuello
        mk.hull(ut, [(s * 0.66, 4.02, shirt_front(4.02) - 0.08), (s * 0.50, 4.62, -0.40), (s * 0.90, 4.42, -0.38),
                     (s * 0.68, 4.04, shirt_front(4.04) - 0.115), (s * 0.52, 4.60, -0.43), (s * 0.86, 4.40, -0.415)],
                "cloth_brown", detail=True)
    # cuello de la levita, parado atrás
    mk.hull(ut, [(-0.40, 4.66, 0.02), (0.40, 4.68, 0.02), (-0.44, 4.70, 0.18), (0.44, 4.72, 0.18),
                 (-0.30, 4.94, 0.10), (0.30, 4.96, 0.10), (-0.30, 4.96, 0.22), (0.30, 4.98, 0.22),
                 (0.0, 4.99, 0.16), (0.0, 4.99, 0.30), (0.0, 4.66, 0.36)], "cloth_brown")

    mk.box(ut, (0, 3.42, 0.56), (0.62, 0.10, 0.06), "cloth_brown", detail=True)            # martingala
    for x in (-0.24, 0.24):
        mk.cyl(ut, (x, 3.42, 0.595), 0.03, 0.03, "brass", axis="z", sides=6, detail=True)
    # cuello del muerto, inclinado 20° adelante, y cuello de la camisa con corbatín de cordón
    mk.cyl(ut, (0, 4.80, -0.16), 0.25, 0.52, "skin_dead", rot=(-20, 0, 0), sides=10)
    mk.cyl(ut, (0, 4.70, -0.17), 0.29, 0.16, "cloth_white", rot=(-20, 0, 0), sides=10)
    for s in (-1, 1):   # puntas del cuello de la camisa
        mk.hull(ut, [(s * 0.04, 4.70, -0.47), (s * 0.20, 4.72, -0.42), (s * 0.10, 4.56, -0.45),
                     (s * 0.04, 4.70, -0.43), (s * 0.20, 4.72, -0.38), (s * 0.10, 4.56, -0.41)], "cloth_white")
    mk.box(ut, (0, 4.61, -0.465), (0.09, 0.07, 0.05), "cloth_black", detail=True)          # nudo
    for s in (-1, 1):
        y0, y1 = 4.58, 4.24
        mk.hull(ut, [(s * 0.015, y0, shirt_front(y0) - 0.03), (s * 0.045, y0, shirt_front(y0) - 0.03),
                     (s * 0.045, y1, shirt_front(y1) - 0.015), (s * 0.075, y1, shirt_front(y1) - 0.015),
                     (s * 0.015, y0, shirt_front(y0) + 0.02), (s * 0.075, y1, shirt_front(y1) + 0.02)],
                "cloth_black", detail=True)                                                 # cordones

    # botones del chaleco
    for y in (3.42, 3.60, 3.78):
        mk.cyl(ut, (-0.06, y, shirt_front(y) - 0.05), 0.032, 0.03, "brass", axis="z", sides=6, detail=True)

    # balazos en el lado derecho del pecho, y el agujero del alfiler de la placa
    for x, y in ((0.30, 3.74), (0.44, 3.58)):
        mk.carve(ut, "blood_dry", points=mk.pts_cyl((x, y, shirt_front(y)), 0.05, 0.30, axis="z", sides=6))
    mk.carve(ut, "coal", points=mk.pts_cyl((BADGE[0], BADGE[1], shirt_front(BADGE[1]) - 0.04), 0.025, 0.14,
                                         axis="z", sides=6))
    return ut


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.82, 0, 0, 1.30, 0.76) + ring(3.50, 0, 0.02, 1.50, 0.82), "cloth_blue")     # pantalón
    for s, zf in ((-1, -0.436), (1, -0.43)):   # puntas del chaleco (la izquierda monta sobre la derecha)
        mk.hull(lt, [(x, y, z) for x, y in ((-s * 0.02, 3.50), (s * 0.60, 3.50), (s * 0.62, 3.22), (s * 0.12, 3.08))
                     for z in (zf, -0.28)], "cloth_black")
    # cinturón de las armas con hebilla grande
    mk.hull(lt, ring(3.04, 0, 0.02, 1.62, 0.98) + ring(3.20, 0, 0.02, 1.62, 0.98), "leather_dark")
    mk.box(lt, (0, 3.12, -0.49), (0.32, 0.24, 0.08), "brass")
    mk.carve(lt, "leather_dark", points=mk.pts_box((0, 3.12, -0.5575), (0.18, 0.11, 0.085)))
    mk.box(lt, (0.0, 3.12, -0.52), (0.03, 0.12, 0.03), "brass", detail=True)                # pasador
    # cinturón de cartuchos, cruzado: más bajo a la derecha
    tilt = (0, 0, -7)
    shell_belt = about(ring(2.94, 0, 0.02, 1.68, 1.02) + ring(3.06, 0, 0.02, 1.68, 1.02), (0, 3.0, 0), tilt)
    mk.hull(lt, shell_belt, "leather")
    for x in (-0.56, -0.44, -0.32, 0.26, 0.38, 0.50):
        yc = 3.0 - x * math.tan(math.radians(7))
        c = (x, yc + 0.03, -0.51)
        mk.cyl(lt, c, 0.045, 0.16, "cloth_red", rot=tilt, sides=6, detail=True)
        cb = (c[0] + 0.01, c[1] - 0.10, c[2])
        mk.cyl(lt, cb, 0.048, 0.05, "brass", rot=tilt, sides=6, detail=True)
    # levita: atrás y costados, con los paneles de adelante abiertos
    mk.hull(lt, clip_front(ring(2.84, 0, 0.05, 1.84, 1.18) + ring(3.48, 0, 0.04, 1.76, 1.10), -0.30), "cloth_brown")
    for s in (-1, 1):
        mk.hull(lt, [(s * 0.62, 3.48, -0.49), (s * 0.64, 2.86, -0.57), (s * 0.90, 3.48, -0.38), (s * 0.95, 2.86, -0.44),
                     (s * 0.70, 3.48, -0.20), (s * 0.70, 2.86, -0.20)], "cloth_brown")
    return lt


def coat_tail(mk, ul, s):
    """Faldón de la levita sobre el muslo: atrás y afuera, abierto adelante, ruedo deshilachado."""
    top = [(0.03, 2.96, 0.60), (0.40, 2.96, 0.62), (0.78, 2.96, 0.46), (0.93, 2.96, 0.10), (0.91, 2.96, -0.32),
           (0.66, 2.96, -0.58)]
    bot = [(0.03, 2.04, 0.76), (0.42, 2.02, 0.82), (0.88, 2.04, 0.62), (1.04, 2.06, 0.14), (1.00, 2.10, -0.34),
           (0.74, 2.12, -0.56)]
    inner = [(0.30, 2.96, 0.10), (0.30, 2.04, 0.20)]
    mk.hull(ul, [(s * x, y, z) for x, y, z in top + bot + inner], "cloth_brown")
    # flecos: triángulos colgando del ruedo, 0,02 adentro de la tela
    hem = [(0.08, 2.04, 0.77), (0.36, 2.025, 0.81), (0.64, 2.03, 0.74), (0.90, 2.045, 0.58), (1.03, 2.06, 0.20),
           (1.01, 2.09, -0.20)]
    for i in range(len(hem) - 1):
        (x0, y0, z0), (x1, y1, z1) = hem[i], hem[i + 1]
        cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2 + 0.02, (z0 + z1) / 2
        ang = -math.degrees(math.atan2(z1 - z0, s * (x1 - x0)))
        mk.prism(ul, [(-0.12, 0), (0.12, 0), (0.02, -0.14 - 0.05 * (i % 2))], 0.03, "cloth_brown", plane="xy",
                 center=(s * cx, cy, cz), rot=(0, ang, 0), detail=True)


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(mk, ul, (x, HIP, 0), (x, KNEE, 0), 0.64, 0.66, 0.50, 0.52, "cloth_blue", over=0.06)
        coat_tail(mk, ul, s)

        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(mk, ll, (x, KNEE, 0), (x, 1.32, 0), 0.52, 0.54, 0.48, 0.50, "cloth_blue", over=0.06)
        mk.hull(ll, ring(1.44, x, 0, 0.58, 0.62) + ring(0.24, x, 0, 0.46, 0.52), "leather_dark")     # caña alta
        mk.hull(ll, ring(1.30, x, 0, 0.62, 0.66) + ring(1.46, x, 0, 0.62, 0.66), "leather")          # vuelta
        for sx in (-1, 1):                                                                            # tiradores
            mk.box(ll, (x + sx * 0.30, 1.40, 0.0), (0.05, 0.22, 0.12), "leather", detail=True)

        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.20, 0.20) for y, z in ((0.06, 0.24), (0.40, 0.22), (0.36, -0.12))]
                + [(x + dx, y, z) for dx in (-0.18, 0.18) for y, z in ((0.24, -0.40), (0.06, -0.40))]
                + [(x - 0.10, 0.06, -0.62), (x + 0.10, 0.06, -0.62), (x - 0.06, 0.15, -0.60), (x + 0.06, 0.15, -0.60),
                   (x, 0.08, -0.70)], "leather_dark")
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.21, 0.21) for y, z in ((0.0, 0.0), (0.07, 0.0))]
                + [(x - 0.11, 0.0, -0.64), (x + 0.11, 0.0, -0.64), (x - 0.11, 0.07, -0.64), (x + 0.11, 0.07, -0.64),
                   (x, 0.0, -0.72), (x, 0.07, -0.72)], "coal")                                         # suela
        mk.box(ft, (x, 0.08, 0.15), (0.34, 0.16, 0.20), "coal", top=(1.0, 1.15), shift=(0, 0.01))       # taco
        # espuela: arco al talón, vástago y rodaja estrellada
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.215, 0.215) for y in (0.18, 0.24) for z in (0.06, 0.20)]
                + [(x, 0.18, 0.27), (x, 0.24, 0.27)], "steel_light", detail=True)
        mk.box(ft, (x, 0.21, 0.33), (0.04, 0.04, 0.14), "steel_light", detail=True)
        mk.prism(ft, star(6, 0.11, 0.05), 0.025, "steel_light", plane="zy", center=(x, 0.21, 0.42), detail=True)


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        sh = (s * SH_X, SHOULDER, ARM_Z)
        el = (s * EL_X, ELBOW, ARM_Z)
        wr = (s * WR_X, WRIST, ARM_Z)
        ua = mk.part(f"{side}UpperArm", sh)
        mk.hull(ua, round_ring(4.74, s * arm_x(4.74), ARM_Z, 0.40, 0.46) + round_ring(4.52, s * arm_x(4.52), ARM_Z, 0.62, 0.64)
                + round_ring(3.54, s * arm_x(3.54), ARM_Z, 0.54, 0.56), "cloth_brown")
        la = mk.part(f"{side}LowerArm", el)
        mk.hull(la, round_ring(3.66, s * arm_x(3.66), ARM_Z, 0.56, 0.58) + round_ring(2.90, s * arm_x(2.90), ARM_Z, 0.48, 0.50),
                "cloth_brown")
        mk.hull(la, round_ring(3.02, s * arm_x(3.02), ARM_Z, 0.58, 0.60, n=8)
                + round_ring(2.76, s * arm_x(2.76), ARM_Z, 0.56, 0.58, n=8), "cloth_brown")          # vuelta del puño
        mk.hull(la, round_ring(2.80, s * arm_x(2.80), ARM_Z, 0.46, 0.48, n=8) + round_ring(2.60, wr[0], ARM_Z, 0.44, 0.46, n=8),
                "cloth_white")
        hd = mk.part(f"{side}Hand", wr)
        hx = s * (WR_X + 0.03)
        mk.hull(hd, round_ring(2.67, hx, ARM_Z, 0.28, 0.46) + round_ring(2.30, hx + s * 0.01, ARM_Z, 0.30, 0.50)
                + round_ring(1.98, hx + s * 0.02, ARM_Z, 0.23, 0.38), "skin_dead")
        mk.box(hd, (hx - s * 0.09, 2.42, ARM_Z - 0.25), (0.13, 0.30, 0.13), "skin_dead", rot=(-15, 0, 0))   # pulgar
        mk.paint(hd, "skin_dead_dark", box=((hx, 1.98, ARM_Z), (0.5, 0.10, 0.6)))


def head_and_hat(mk):
    hd = mk.part("Head", NECK_P)
    # cráneo y cara pesada (espacio del caminante)
    mk.hull(hd, head(round_ring(4.24, 0, -0.18, 0.78, 0.66) + round_ring(4.50, 0, -0.22, 0.90, 0.86)
                     + round_ring(4.80, 0, -0.25, 0.96, 0.92) + round_ring(5.02, 0, -0.26, 0.86, 0.86)
                     + round_ring(5.16, 0, -0.26, 0.58, 0.62)), "skin_dead")
    mk.hull(hd, head([(-0.36, 4.44, -0.58), (0.36, 4.44, -0.58), (-0.38, 4.46, -0.16), (0.38, 4.46, -0.16),
                      (-0.30, 4.12, -0.64), (0.30, 4.12, -0.64), (-0.32, 4.16, -0.14), (0.32, 4.16, -0.14),
                      (-0.16, 4.06, -0.70), (0.16, 4.06, -0.70)]), "skin_dead")                     # mandíbula cuadrada
    for s in (-1, 1):                                                                              # ceño fruncido
        mk.hull(hd, head([(s * 0.03, 4.84, -0.72), (s * 0.46, 4.92, -0.58), (s * 0.03, 4.95, -0.68),
                          (s * 0.46, 4.99, -0.54), (s * 0.03, 4.88, -0.45), (s * 0.44, 4.96, -0.40)]), "skin_dead")
    for s in (-1, 1):                                                                              # pómulos
        mk.hull(hd, head([(s * 0.22, 4.66, -0.66), (s * 0.40, 4.68, -0.56), (s * 0.30, 4.56, -0.62),
                          (s * 0.26, 4.66, -0.50), (s * 0.40, 4.60, -0.44)]), "skin_dead")
    mk.hull(hd, head([(0, 4.84, -0.70), (0, 4.62, -0.90), (-0.11, 4.58, -0.70), (0.11, 4.58, -0.70),
                      (0, 4.56, -0.78), (-0.07, 4.62, -0.82), (0.07, 4.62, -0.82), (-0.05, 4.76, -0.73),
                      (0.05, 4.76, -0.73)]), "skin_dead")                                            # nariz
    for s in (-1, 1):
        mk.hull(hd, head(mk.pts_box((s * 0.48, 4.70, -0.22), (0.09, 0.26, 0.17), top=(1, 0.7))), "skin_dead")   # orejas
        mk.hull(hd, head([(s * 0.45, 4.98, -0.30), (s * 0.50, 4.96, -0.04), (s * 0.45, 4.62, -0.24),
                          (s * 0.50, 4.64, -0.08), (s * 0.40, 4.96, -0.06)]), "hair_grey")            # patillas
    cap = [p for y, w, d in ((4.50, 0.86, 0.80), (4.80, 1.00, 0.96), (5.02, 0.90, 0.92))
           for p in round_ring(y, 0, -0.25, w, d, n=12) if p[2] > -0.30]
    mk.hull(hd, head(cap + [(0, 4.42, 0.06), (0, 5.08, 0.10)]), "hair_grey")                    # nuca
    # bigote de morsa: masa de arriba y dos caídas a los costados de la boca
    for s in (-1, 1):
        mk.hull(hd, head([(0, 4.62, -0.84), (0, 4.46, -0.88), (0, 4.60, -0.64), (s * 0.18, 4.63, -0.82),
                          (s * 0.21, 4.44, -0.87), (s * 0.18, 4.58, -0.62), (s * 0.40, 4.56, -0.66),
                          (s * 0.41, 4.43, -0.71), (s * 0.34, 4.52, -0.52)]), "hair_grey")
        mk.hull(hd, head([(s * 0.26, 4.50, -0.82), (s * 0.42, 4.50, -0.68), (s * 0.30, 4.28, -0.78), (s * 0.44, 4.28, -0.64),
                          (s * 0.40, 4.10, -0.68), (s * 0.34, 4.48, -0.56), (s * 0.38, 4.26, -0.56)]), "hair_grey")
        for x, y in ((0.06, 4.46), (0.14, 4.45)):                                                 # mechones del borde
            mk.hull(hd, head([(s * (x - 0.04), y + 0.03, -0.86), (s * (x + 0.04), y + 0.03, -0.86),
                              (s * x, y - 0.06, -0.84), (s * x, y + 0.03, -0.74)]), "hair_grey", detail=True)
    # huecos: cuencas, boca abierta, mejilla derecha rota
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.75, -0.75), 0.15, scale=(1.0, 0.75, 0.9),
                                                               subdiv=0)))
    mouth = [(-0.15, 4.47), (0.15, 4.47), (0.14, 4.32), (-0.14, 4.32), (0, 4.29)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.95, -0.52)]))
    mk.carve(hd, "blood_dry", points=head(mk.pts_ball((0.38, 4.44, -0.46), 0.13, scale=(0.9, 0.75, 1.3), subdiv=0)))
    mk.paint(hd, "skin_dead_dark", ball=(hp((0, 4.18, -0.68)), 0.22))                       # mentón podrido
    # dientes de abajo apoyados en la boca, muelas en la mejilla rota
    for i in range(4):
        x = -0.10 + 0.0667 * i
        mk.hull(hd, head([(x - 0.03, 4.32, -0.68), (x + 0.03, 4.32, -0.68), (x - 0.02, 4.41, -0.68),
                          (x + 0.02, 4.41, -0.68), (x - 0.03, 4.32, -0.46), (x + 0.03, 4.32, -0.46),
                          (x, 4.40, -0.46)]), "bone", detail=True)
    for i in range(3):
        z = -0.56 + 0.08 * i
        for y0, y1 in ((4.52, 4.45), (4.36, 4.42)):
            mk.hull(hd, head([(0.20, y0, z - 0.03), (0.20, y0, z + 0.03), (0.33, y0, z - 0.03), (0.33, y0, z + 0.03),
                              (0.31, y1, z - 0.02), (0.31, y1, z + 0.02), (0.20, y1, z)]), "bone", detail=True)

    eyes = mk.part("Eyes", NECK_P)
    silver = mk.part("Silver_Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.75, -0.61)), 0.08 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)
        mk.ball(silver, hp((s * 0.19, 4.75, -0.61)), 0.08 * K + 0.012, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)

    # sombrero cattleman: ala de 2,1 con los costados levantados, copa alta con pliegue y pellizcos
    base = hp((0, 5.00, -0.26))
    hat = mk.part("Acc_Hat", base)
    ax, az = 2.1 / 2 / K, 2.0 / 2 / K
    ell = [(ax * math.cos(2 * math.pi * i / 28), az * math.sin(2 * math.pi * i / 28)) for i in range(28)]
    mid = [(x, z) for x, z in ell if abs(x) <= 0.52]
    zc = az * math.sqrt(1 - (0.52 / ax) ** 2)
    mid += [(-0.52, zc), (-0.52, -zc), (0.52, zc), (0.52, -zc)]
    mk.hull(hat, head([(x, y, z - 0.26) for x, z in mid for y in (4.98, 5.025)]), "cloth_black")
    for s in (-1, 1):
        zc2 = az * math.sqrt(1 - (0.50 / ax) ** 2)
        wing = [(x, z) for x, z in ell if s * x >= 0.50] + [(s * 0.50, zc2), (s * 0.50, -zc2)]
        lift = math.tan(math.radians(24))
        mk.hull(hat, head([(x, y + (abs(x) - 0.50) * lift, z - 0.26) for x, z in wing for y in (4.98, 5.025)]),
                "cloth_black")
    crown = (round_ring(4.99, 0, -0.26, 0.92, 0.98, n=12) + round_ring(5.30, 0, -0.26, 0.88, 0.96, n=12)
             + [(x * (0.80 if z < -0.42 else 1.0), y, z) for x, y, z in round_ring(5.47, 0, -0.25, 0.80, 0.90, n=12)])
    mk.hull(hat, head(crown), "cloth_black")
    for s in (-1, 1):   # dos lomos arriba: el pliegue al medio y los pellizcos adelante
        ridge = []
        for z, k in ((-0.66, 0.62), (-0.52, 0.80), (-0.30, 0.97), (-0.05, 0.97), (0.14, 0.80)):
            half = 0.40 * math.sqrt(max(0.0, 1 - ((z + 0.25) / 0.45) ** 2))
            ridge += [(s * half * k, 5.58, z), (s * 0.05, 5.48, z), (s * (half * k + 0.01), 5.42, z), (s * 0.05, 5.42, z)]
        mk.hull(hat, head(ridge), "cloth_black")
    mk.hull(hat, head(round_ring(5.03, 0, -0.26, 0.955, 1.015, n=12) + round_ring(5.11, 0, -0.26, 0.945, 1.005, n=12)),
            "leather_dark")
    return hd


def badge(mk):
    zf = shirt_front(BADGE[1]) - 0.04          # frente del chaleco
    tilt = math.degrees(math.atan(0.2727))     # el pecho se inclina hacia atrás arriba
    c = (BADGE[0], BADGE[1], zf - 0.015)
    bg = mk.part("Acc_Badge", c)
    mk.prism(bg, star(6, 0.225, 0.13), 0.05, "steel_light", plane="xy", center=c, rot=(tilt, 0, 0))
    mk.bevel(bg, width=0.012, angle=35)
    n = (0.0, math.sin(math.radians(tilt)), -math.cos(math.radians(tilt)))   # normal hacia afuera
    for k in range(6):
        a = math.radians(90 + 60 * k)
        p = about([(c[0] + 0.235 * math.cos(a), c[1] + 0.235 * math.sin(a), c[2])], c, (tilt, 0, 0))[0]
        mk.ball(bg, p, 0.036, "steel_light", subdiv=0, detail=True)
    disc = (c[0] + n[0] * 0.025, c[1] + n[1] * 0.025, c[2] + n[2] * 0.025)
    mk.cyl(bg, disc, 0.08, 0.03, "steel_light", axis="z", sides=10, rot=(tilt, 0, 0), detail=True)


def shotgun(mk):
    """Escopeta recortada de dos caños. Se dibuja en el espacio del arma (caño a -Z, lomo +Y, origen en
    la empuñadura) y gun() la lleva a la mano derecha colgando."""
    sg = mk.part("Acc_Shotgun", GRIP)
    # caños de hierro (0,9), cinta de arriba y de abajo, banda que sostiene la delantera
    for sx in (-1, 1):
        mk.hull(sg, guns(mk.pts_cyl((sx * 0.088, 0.30, -0.75), 0.088, 0.90, axis="z", sides=8)), "iron")
    mk.hull(sg, guns(mk.pts_box((0, 0.385, -0.75), (0.07, 0.04, 0.90))), "iron")
    mk.hull(sg, guns(mk.pts_box((0, 0.215, -0.75), (0.07, 0.04, 0.90))), "iron")
    mk.hull(sg, guns(mk.pts_box((0, 0.30, -0.80), (0.375, 0.22, 0.04))), "gunmetal")
    # delantera de madera torneada bajo los caños
    mk.hull(sg, guns([(sx * w, y, z) for sx in (-1, 1) for z, w, k in ((-0.31, 0.11, 1.0), (-0.74, 0.085, 0.8))
                      for y in (0.25, 0.17 + 0.03 * (1 - k)) for w in (w,)]
                     + [(0, 0.11, -0.33), (0, 0.14, -0.72)]), "wood_dark")
    # cajón (boxlock) con el frente redondeado abajo, fences donde entran los caños, gargantilla
    mk.hull(sg, guns([(sx * 0.15, y, z) for sx in (-1, 1) for y, z in ((0.385, -0.32), (0.385, -0.03), (0.21, -0.32))]
                     + [(sx * 0.13, y, z) for sx in (-1, 1) for y, z in ((0.13, -0.24), (0.13, -0.03), (0.16, -0.30))]),
            "gunmetal")
    for sx in (-1, 1):
        mk.hull(sg, guns(mk.pts_cyl((sx * 0.088, 0.30, -0.33), 0.10, 0.06, axis="z", sides=8)), "gunmetal")
    # culata de pistola: gargantilla, empuñadura inclinada y chapa de hierro (asoma atrás del puño)
    mk.hull(sg, guns([(sx * 0.10, y, z) for sx in (-1, 1) for y, z in ((0.36, -0.05), (0.17, -0.05))]
                     + [(sx * 0.085, y, z) for sx in (-1, 1) for y, z in ((0.33, 0.10), (0.20, 0.12))]), "wood_dark")
    mk.hull(sg, guns([(sx * 0.085, y, z) for sx in (-1, 1) for y, z in ((0.30, 0.02), (0.22, 0.14))]
                     + [(sx * 0.075, y, z) for sx in (-1, 1) for y, z in ((-0.30, 0.08), (-0.30, 0.27))]), "wood_dark")
    mk.hull(sg, guns([(sx * 0.08, y, z) for sx in (-1, 1) for y, z in ((-0.29, 0.07), (-0.29, 0.28), (-0.35, 0.08),
                                                                       (-0.35, 0.28))]), "iron")
    mk.bevel(sg, width=0.014, angle=35)
    for sx in (-1, 1):   # bocas de los caños
        mk.carve(sg, "coal", points=guns(mk.pts_cyl((sx * 0.088, 0.30, -1.20), 0.058, 0.16, axis="z", sides=8)))
    # detalle: placas laterales de acero, martillos con espuela curva, palanca, gatillos, mira
    lock = [(-0.29, 0.30), (-0.22, 0.355), (-0.07, 0.355), (-0.03, 0.29), (-0.06, 0.18), (-0.24, 0.165), (-0.29, 0.22)]
    for sx in (-1, 1):
        mk.prism(sg, lock, 0.016, "steel_light", plane="zy", center=gun((sx * 0.152, 0, 0)), rot=(-90, 0, 0),
                 detail=True)
        x0 = sx * 0.085
        mk.hull(sg, guns([(x0 + dx, y, z) for dx in (-0.028, 0.028) for y, z in
                          ((0.34, -0.07), (0.34, -0.01), (0.47, -0.05), (0.47, 0.01))]), "steel_light", detail=True)
        mk.hull(sg, guns([(x0 + dx, y, z) for dx in (-0.025, 0.025) for y, z in
                          ((0.45, -0.05), (0.50, -0.01), (0.535, 0.09), (0.51, 0.13), (0.465, 0.04))]),
                "steel_light", detail=True)
    mk.hull(sg, guns([(dx, y, z) for dx in (-0.025, 0.025) for y, z in ((0.38, -0.14), (0.42, -0.12), (0.41, 0.03),
                                                                        (0.38, 0.03))]
                     + [(0.07, 0.40, 0.03), (0.07, 0.42, 0.01)]), "steel_light", detail=True)        # palanca
    guard = [(-0.22, 0.14), (-0.21, 0.02), (-0.15, -0.04), (-0.04, -0.04), (0.0, 0.02), (0.0, 0.14),
             (-0.03, 0.14), (-0.04, 0.03), (-0.06, 0.005), (-0.14, 0.005), (-0.17, 0.03), (-0.18, 0.14)]
    mk.prism(sg, guard, 0.05, "gunmetal", plane="zy", center=GRIP, rot=(-90, 0, 0), detail=True)
    for z in (-0.14, -0.08):
        mk.hull(sg, guns([(dx, y, z + dz) for dx in (-0.02, 0.02) for y, dz in ((0.14, 0.0), (0.14, 0.03), (0.04, 0.02))]),
                "steel_light", detail=True)
    mk.hull(sg, guns(mk.pts_cyl((0, 0.415, -1.16), 0.024, 0.05, axis="y", sides=6)), "brass", detail=True)   # mira
    mk.marker("_Muzzle", gun((0, 0.30, -1.20)))


def shackles(mk):
    c = (-(WR_X), WRIST + 0.06, ARM_Z)
    sh = mk.part("Acc_Shackles", c)
    c_ring(mk, sh, c, 0.29, 0.30, 0.08, 0.12, "iron", plane="xz", rot=(0, 160, 0), n=12, gap=10)
    # bisagra y tres eslabones colgando por afuera, después el otro grillete abierto y roto
    mk.box(sh, (c[0] - 0.30, c[1] - 0.03, c[2]), (0.08, 0.14, 0.10), "iron")
    links = [((c[0] - 0.33, c[1] - 0.17, c[2]), "zy"), ((c[0] - 0.33, c[1] - 0.33, c[2]), "xy"),
             ((c[0] - 0.33, c[1] - 0.49, c[2]), "zy")]
    for p, pl in links:
        c_ring(mk, sh, p, 0.06, 0.10, 0.03, 0.035, "iron", plane=pl, n=6, gap=8)
    c2 = (c[0] - 0.33, c[1] - 0.77, c[2])
    c_ring(mk, sh, c2, 0.22, 0.22, 0.06, 0.10, "iron", plane="zy", rot=(90, 0, 0), n=10, gap=70)


def silver_neck(mk):
    sn = mk.part("Silver_Neck", (0, WAIST, 0))
    base, r = (0.0, 4.80, -0.16), 0.25 + 0.025
    ax = (0.0, math.cos(math.radians(-20)), math.sin(math.radians(-20)))
    v = (0.0, -math.sin(math.radians(-20)), math.cos(math.radians(-20)))

    def P(t, a, out=0.0):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + out
        return (base[0] + rr * ca, base[1] + ax[1] * t + rr * sa * v[1], base[2] + ax[2] * t + rr * sa * v[2])

    count = [0]

    def vein(t0, a0, t1, a1, w0, w1):
        k = count[0]
        count[0] += 1
        out, dep = 0.008 * (k % 3), -0.04 - 0.007 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [P(t, a - da, out), P(t, a + da, out), P(t, a - da, dep), P(t, a + da, dep)]
        mk.hull(sn, pts, "silver_neon")

    # tronco que sale del cuello de la camisa a la derecha y se abre en tres; una rama a la izquierda
    vein(-0.04, 10, 0.10, 18, 0.11, 0.09)
    vein(0.08, 17, 0.24, 6, 0.08, 0.04)
    vein(0.07, 19, 0.22, 40, 0.07, 0.04)
    vein(0.05, 13, 0.18, -12, 0.06, 0.035)
    vein(-0.04, 150, 0.08, 160, 0.09, 0.07)
    vein(0.06, 159, 0.22, 150, 0.06, 0.035)
    vein(0.05, 161, 0.20, 178, 0.05, 0.03)


def build(mk):
    upper_torso(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_and_hat(mk)
    badge(mk)
    shotgun(mk)
    shackles(mk)
    silver_neck(mk)

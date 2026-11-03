"""
Receta de WST_Boss_Butcher, el Carnicero del rancho (prompt 058, Bloques A + D + H + G).

Brief
- Silueta a 40 studs: una mole de espaldas anchas y joroba, cabeza chica y pelada hundida entre los
  trapecios, brazos pelados enormes con antebrazos de Popeye, delantal de cuero oscuro largo hasta
  arriba de las rodillas, piernas cortas con botas de goma, gancho de carne colgando de la mano derecha
  con la cadena, cuchilla colgada en la cadera izquierda.
- Escala: H = 7,0 (k = 7,0 / 5,2 = 1,346) con piernas cortas (cadera 0,43 H, prompt). Articulaciones:
  tobillo 0,32 · rodilla 1,60 · cadera 3,01 · cintura 3,57 · codo 4,06 · muñeca 2,94 · hombro 5,25 ·
  cuello 5,74. Las de la pierna bajan en proporción a la cadera (0,43 / 0,47); la cintura queda 0,08 H
  arriba de la cadera, como en el Bloque D; la cabeza es chica (1,26 = 0,18 H) y el cuello 0,82 H.
  Torso 1,5 veces el ancho del caminante escalado (pecho 2,56): hombros en x = ±1,50, codos ±1,67,
  muñecas ±1,82 (8° hacia afuera), caderas ±0,52, brazos en z = -0,20. El programador pasa esto a la ficha.
- Piezas: las 15 de R15 con el origen en su articulación, Eyes, Acc_Hook (centro del mango en T, dentro
  de la mano derecha; trae la cadena de 6 eslabones), Acc_Cleaver (el mango, colgado del cordón del
  delantal), Silver_Eyes, Silver_LeftLowerArm, Silver_RightLowerArm (codo), Silver_Neck (cintura, como
  UpperTorso: el cuello es de UpperTorso), _HookTip, _ChainEnd.
- Tallado: cuencas, boca, oreja izquierda arrancada, tajo en la pelada, mordida en el trapecio derecho,
  manchas de sangre del delantal (talladas poco profundas: en caras grandes pintar tiñe la cara entera),
  agujero de la cuchilla. Pintado: manchas oscuras de la piel (moteado), sangre en el filo.
- Daños (Bloque H): oreja arrancada, mordida en el hombro, tajo en la cabeza.
- Inferido (el prompt no lo dice): pantalón cloth_blue; el gancho es de los de mango en T (el puño cierra
  el mango, como sostiene un arma el brazo colgando: el gancho cuelga abajo con la punta adelante) y la
  cadena sale de un ojal en la punta de atrás del mango; las vetas del prompt ("Silver_Veins") van en
  tres piezas, una por segmento que se mueve (Bloque G: Silver_<Where>); el delantal se ata con un
  cordón de soga con moño atrás y la cuchilla va calzada en ese cordón, girada 35° para verse de frente.

Vueltas: 1) primera versión · 2) brazos con deltoide, bíceps, codo de 0,64 y antebrazo de 0,98 (eran
tubos parejos); manos 0,44 (eran 0,36); ceja en dos arcos (la barra recta se leía como visera de gorra);
manchas con chorreado (eran estrellas de 10 puntas); camiseta sobre la joroba (atrás quedaba una faja);
errores: tapas de las vetas coplanares, cordón coplanar con la camiseta, paños del delantal, remache a
0,001 del cordón, moño y hebillas flotando · 3) trapecios 0,1 más altos (cuello más corto), cuchilla
girada 35° (de frente se veía de canto), manos 0,52, punta de la soga dentro del anillo (flotaba 0,015)
· 4) tiras del delantal por encima de los trapecios (quedaban enterradas y asomaban como orejitas),
manchas más redondas; los eslabones sin chanflán (el gancho bajó de 2112 a 1120 triángulos).

Revisión
- 4082 triángulos contra 3800 de referencia: Acc_Hook 1120 (gancho y mango con chanflán, ojal y seis
  eslabones que son anillos de verdad), UpperTorso 610, Head 466.
- Alto 6,975 (H = 7,0). Ancho 4,49 (de la punta de la soga a la mano izquierda): es una mole a propósito.
- Las manchas de sangre son tallados de 0,015 con chorreado, no parches en relieve como dice el prompt
  ("flat raised patches"): la fábrica no pega calcomanías y se leen igual.
- Dudoso: 16 colores (el Bloque A pide hasta 12; el prompt ya nombra 13 con los del Bloque H); el gancho
  es de 1,2 de alto como pide el prompt y al lado de esa mano se ve chico.
"""

import math

import humanoid as hu

H = 7.0
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.32, 1.60, 0.43 * H, 0.51 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.75 * H, 0.82 * H
SH_X, ARM_Z, LEG_X = 1.50, -0.20, 0.52
TAN8 = math.tan(math.radians(8))
EL_X, WR_X = SH_X + (SHOULDER - ELBOW) * TAN8, SH_X + (SHOULDER - WRIST) * TAN8
NECK_P = (0.0, NECK, -0.30)
KH = 1.26 / 1.04                      # la cabeza: 1,26 de alto contra 1,04 del caminante
HEAD_FWD, HEAD_TILT = 0.12, -6
GRIP = (WR_X + 0.04, WRIST - 0.36, ARM_Z)

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def head(pts):
    """Puntos del espacio de la cabeza del caminante (cuello en 4,16) a la del Carnicero."""
    return about([(x * KH, NECK + (y - 4.16) * KH, NECK_P[2] + (z + 0.10) * KH - HEAD_FWD) for x, y, z in pts],
                 NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def arm_x(y):
    return SH_X + (SHOULDER - y) * TAN8


def shirt_front(y):
    """z del frente de la camiseta (cara plana) a la altura y."""
    if y <= 4.50:
        return -0.65 - 0.12 * (y - 3.48) / 1.02
    return -0.77 + 0.02 * (y - 4.50) / 0.42


def splash(r, rot=0):
    """Perfil de una salpicadura: borde irregular y un chorreado hacia abajo."""
    rad = (1.0, 0.82, 0.95, 0.72, 1.05, 0.78, 0.92, 0.7, 1.0, 0.8)
    pts = []
    for k in range(10):
        a = math.radians(36 * k + rot)
        if abs(((36 * k + rot) % 360) - 270) < 18:
            pts += [(-0.14 * r, -0.9 * r), (-0.05 * r, -2.3 * r), (0.06 * r, -2.4 * r), (0.14 * r, -0.9 * r)]
        else:
            pts.append((r * rad[k] * math.cos(a), r * rad[k] * math.sin(a)))
    return pts


def c_ring(mk, part, center, rx, ry, wire, depth, mat, plane="xy", rot=(0, 0, 0), n=10, gap=14, detail=False):
    """Anillo abierto (perfil en C extruido): eslabones, soga."""
    prof = []
    for i in range(n + 1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append((rx * math.cos(a), ry * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(gap / 2 + (360 - gap) * i / n)
        prof.append(((rx - wire) * math.cos(a), (ry - wire) * math.sin(a)))
    mk.prism(part, prof, depth, mat, plane=plane, center=center, rot=rot, detail=detail)


def tube(mk, part, pts, w0, w1, mat, ext=0.02, detail=False):
    """Barra de sección cuadrada por una línea quebrada en el plano zy (ancho en x constante w0,
    grosor en el plano que va de w0 a w1): ganchos y mangos curvos."""
    n = len(pts) - 1
    for i in range(n):
        (x, y0, z0), (_, y1, z1) = pts[i], pts[i + 1]
        dy, dz = y1 - y0, z1 - z0
        ln = math.hypot(dy, dz)
        ty, tz = dy / ln, dz / ln
        ny, nz = -tz, ty
        ha, hb = (w0 + (w1 - w0) * i / n) / 2, (w0 + (w1 - w0) * (i + 1) / n) / 2
        a = (y0 - ty * ext, z0 - tz * ext)
        b = (y1 + ty * ext, z1 + tz * ext)
        q = []
        for (yy, zz), h in ((a, ha), (b, hb)):
            hx = min(h, w0 / 2)
            for sx in (-1, 1):
                for sn in (-1, 1):
                    q.append((x + sx * hx, yy + sn * ny * h, zz + sn * nz * h))
        mk.hull(part, q, mat, detail=detail)


def veins(mk, part, axis, branches, mat="silver_neon"):
    """Vetas sobre un miembro vertical: axis(y) -> (cx, cz, rx, rz). branches: [((y0, a0), (y1, a1), w0, w1)].
    Ángulo 0 = +x, 90 = atrás (+z), -90 = adelante. Cada veta a distinta altura para no quedar coplanar."""
    for k, ((y0, a0), (y1, a1), w0, w1) in enumerate(branches):
        out, dep = 0.02 + 0.007 * (k % 3), -0.05 - 0.006 * k
        y0, y1 = y0 - 0.007 * k, y1 + 0.005 * k
        pts = []
        for y, a, w in ((y0, a0, w0), (y1, a1, w1)):
            cx, cz, rx, rz = axis(y)
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            tx, tz = -sa, ca                       # tangente
            for off in (out, dep):
                for sw in (-1, 1):
                    pts.append((cx + (rx + off) * ca + sw * tx * w / 2, y, cz + (rz + off) * sa + sw * tz * w / 2))
        mk.hull(part, pts, mat)


# ======================================================================================
def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    # cuerpo (piel): panza, pecho enorme, trapecios que suben al cuello, joroba
    body = (ring(3.48, 0, 0.0, 2.04, 1.24) + ring(4.50, 0, -0.05, 2.56, 1.38)
            + [(-1.36, 5.06, -0.32), (1.36, 5.14, -0.32), (-1.36, 5.08, 0.34), (1.36, 5.16, 0.34),
               (-1.0, 5.20, -0.62), (1.0, 5.26, -0.62), (-0.62, 5.72, -0.26), (0.62, 5.74, -0.26),
               (-0.62, 5.70, 0.34), (0.62, 5.72, 0.34), (-0.70, 5.08, 0.86), (0.70, 5.12, 0.86), (0.0, 5.42, 0.92),
               (0.0, 5.76, 0.30)])
    mk.hull(ut, body, "skin_dead")
    # camiseta de lona sin mangas, 0,03 por fuera: la sisa deja los hombros al aire
    mk.hull(ut, ring(3.46, 0, 0.0, 2.10, 1.30) + ring(4.50, 0, -0.05, 2.62, 1.44) + ring(4.92, 0, -0.05, 2.30, 1.40)
            + [(-0.72, 5.06, 0.90), (0.72, 5.10, 0.90), (0.0, 5.26, 0.96)], "canvas")
    # cuello grueso, inclinado 25° adelante
    mk.cyl(ut, (0, 5.62, -0.22), 0.50, 0.70, "skin_dead", rot=(-25, 0, 0), sides=10)
    # pechera del delantal (cuero oscuro), 0,04 por delante de la camiseta, y la tira al cuello
    bib = [(-0.86, 3.46), (0.86, 3.46), (-0.90, 4.50), (0.90, 4.50), (-0.72, 4.96), (0.72, 4.96)]
    mk.hull(ut, [p for x, y in bib for p in ((x, y, shirt_front(y) - 0.04), (x, y, shirt_front(y) + 0.12))],
            "leather_dark")
    for s in (-1, 1):
        mk.hull(ut, [(s * 0.50, 4.90, shirt_front(4.90) - 0.04), (s * 0.68, 4.90, shirt_front(4.90) - 0.04),
                     (s * 0.50, 4.90, -0.55), (s * 0.68, 4.90, -0.55),
                     (s * 0.47, 5.84, -0.34), (s * 0.63, 5.80, -0.34), (s * 0.47, 5.84, -0.12), (s * 0.63, 5.80, -0.12)],
                "leather_dark")
    mk.hull(ut, [(-0.60, 5.76, -0.04), (0.60, 5.78, -0.04), (-0.60, 5.86, -0.04), (0.60, 5.88, -0.04),
                 (-0.36, 5.76, 0.40), (0.36, 5.78, 0.40), (-0.36, 5.86, 0.38), (0.36, 5.88, 0.38)], "leather_dark")
    # sangre: salpicaduras talladas poco profundas en la pechera y la camiseta
    for (x, y, r, rot) in ((0.30, 4.36, 0.15, 270), (-0.45, 3.95, 0.12, 270), (0.05, 3.78, 0.09, 90),
                           (-0.20, 4.72, 0.10, 270)):
        mk.carve(ut, "blood_dry", prism=dict(profile=splash(r, rot), depth=0.08, plane="xy",
                                             center=(x, y, shirt_front(y) - 0.065)))
    # mordida en el trapecio derecho
    mk.carve(ut, "blood_dry", points=mk.pts_ball((0.92, 5.42, 0.08), 0.20, scale=(1.0, 0.8, 1.2), subdiv=0))
    # moteado oscuro en la piel
    for c, r in (((-1.05, 5.20, 0.10), 0.22), ((0.30, 5.55, 0.55), 0.25), ((-0.40, 5.40, 0.70), 0.2)):
        mk.paint(ut, "skin_dead_dark", ball=(c, r))
    return ut


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.92, 0, 0, 1.90, 1.10) + ring(3.64, 0, 0, 2.04, 1.22), "cloth_blue")        # pantalón
    # delantal colgando derecho desde la panza
    mk.hull(lt, [(x, y, z) for x in (-0.94, 0.94) for y in (2.94, 3.66) for z in (-0.72, -0.56)], "leather_dark")
    mk.hull(lt, ring(3.42, 0, 0, 2.18, 1.38) + ring(3.52, 0, 0, 2.18, 1.38)
            + [(x, y, -0.75) for x in (-0.94, 0.94) for y in (3.42, 3.52)], "rope")                  # cordón
    for s in (-1, 1):                                                                              # moño atrás
        mk.hull(lt, [(s * 0.02, 3.42, 0.64), (s * 0.02, 3.52, 0.64), (s * 0.22, 3.36, 0.70), (s * 0.22, 3.58, 0.70),
                     (s * 0.02, 3.47, 0.70)], "rope", detail=True)
        mk.box(lt, (s * 0.10, 3.30, 0.69), (0.06, 0.32, 0.04), "rope", rot=(0, 0, s * 12), detail=True)
    for (x, y, r) in ((0.55, 3.24, 0.11), (-0.25, 3.12, 0.08)):
        mk.carve(lt, "blood_dry", prism=dict(profile=splash(r, 270), depth=0.08, plane="xy", center=(x, y, -0.745)))
    return lt


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(mk, ul, (x, HIP, 0), (x, KNEE, 0), 0.90, 0.92, 0.70, 0.72, "cloth_blue", over=0.06)
        # paño del delantal sobre el muslo, plano adelante, ruedo con dos muescas
        x0, x1, zf = s * -0.02, s * 0.98, (-0.741 if s < 0 else -0.735)
        y0, y1 = (3.06, 1.76) if s < 0 else (3.07, 1.77)
        mk.hull(ul, [(xx, y, z) for xx in (x0, x1) for y in (y0, y1) for z in (zf, zf + 0.12)], "leather_dark")
        for dx in (0.30, 0.70):
            mk.carve(ul, "leather_dark", prism=dict(profile=[(-0.07, 0.0), (0.07, 0.0), (0.0, 0.16)], depth=0.3,
                                                    plane="xy", center=(s * dx, 1.75, -0.66)))
        if side == "Right":
            mk.carve(ul, "blood_dry", prism=dict(profile=splash(0.12, 270), depth=0.08, plane="xy",
                                                 center=(x + 0.05, 2.46, -0.76)))

        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(mk, ll, (x, KNEE, 0), (x, 1.36, 0), 0.70, 0.72, 0.66, 0.68, "cloth_blue", over=0.06)
        mk.hull(ll, ring(1.46, x, 0.0, 0.80, 0.86) + ring(0.30, x, 0.02, 0.72, 0.82), "leather_dark")   # bota de goma
        mk.hull(ll, ring(1.34, x, 0.0, 0.86, 0.92) + ring(1.48, x, 0.0, 0.86, 0.92), "leather_dark")    # borde grueso

        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.30, 0.30) for y, z in ((0.07, 0.34), (0.44, 0.32), (0.40, -0.20))]
                + [(x + dx, y, z) for dx in (-0.27, 0.27) for y, z in ((0.07, -0.60), (0.24, -0.58))]
                + [(x - 0.16, 0.07, -0.80), (x + 0.16, 0.07, -0.80), (x - 0.13, 0.20, -0.76), (x + 0.13, 0.20, -0.76)],
                "leather_dark")
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.31, 0.31) for y in (0.0, 0.08) for z in (0.35, -0.58)]
                + [(x + dx, y, -0.82) for dx in (-0.16, 0.16) for y in (0.0, 0.08)], "coal")             # suela


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        ua = mk.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        mk.hull(ua, round_ring(5.40, s * arm_x(5.40), ARM_Z, 0.66, 0.72) + round_ring(5.12, s * (arm_x(5.12) + 0.05), ARM_Z, 0.98, 0.96)
                + round_ring(4.60, s * (arm_x(4.60) + 0.02), ARM_Z, 0.86, 0.90) + round_ring(4.02, s * arm_x(4.02), ARM_Z, 0.64, 0.68),
                "skin_dead")
        mk.paint(ua, "skin_dead_dark", ball=((s * (SH_X + 0.40), 4.70, ARM_Z - 0.10), 0.25))
        la = mk.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        mk.hull(la, round_ring(4.14, s * arm_x(4.14), ARM_Z, 0.70, 0.74) + round_ring(3.80, s * (arm_x(3.80) + 0.03), ARM_Z, 0.98, 0.96)
                + round_ring(2.98, s * arm_x(2.98), ARM_Z, 0.60, 0.64), "skin_dead")
        hd = mk.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hx = s * (WR_X + 0.04)
        mk.hull(hd, round_ring(3.02, hx, ARM_Z, 0.48, 0.72) + round_ring(2.56, hx + s * 0.01, ARM_Z, 0.52, 0.78)
                + round_ring(2.04, hx + s * 0.02, ARM_Z, 0.40, 0.60), "skin_dead")
        mk.box(hd, (hx - s * 0.17, 2.72, ARM_Z - 0.38), (0.21, 0.46, 0.21), "skin_dead", rot=(-15, 0, 0))   # pulgar
        mk.paint(hd, "skin_dead_dark", box=((hx, 2.04, ARM_Z), (0.8, 0.10, 0.9)))
        if side == "Right":     # soga atada a la muñeca: dos vueltas y la punta colgando
            for y, tilt, rr in ((3.10, 6, 0.37), (3.22, -5, 0.41)):
                c_ring(mk, la, (hx - s * 0.04, y, ARM_Z), rr, rr + 0.02, 0.07, 0.07, "rope", plane="xz",
                       rot=(tilt, -90, 0), n=12, gap=8)
            mk.hull(la, [(hx + 0.25, 3.12, ARM_Z - 0.18), (hx + 0.31, 3.10, ARM_Z - 0.12), (hx + 0.32, 2.80, ARM_Z - 0.26),
                         (hx + 0.38, 2.80, ARM_Z - 0.22), (hx + 0.27, 3.14, ARM_Z - 0.08)], "rope")
        else:                   # guantelete de cuero hasta media altura, con dos correas
            mk.hull(la, round_ring(3.60, s * (arm_x(3.60) + 0.025), ARM_Z, 0.95, 0.95) + round_ring(3.48, s * (arm_x(3.48) + 0.02), ARM_Z, 0.90, 0.90)
                    + round_ring(2.96, s * arm_x(2.96), ARM_Z, 0.68, 0.72), "leather_dark")
            for y in (3.10, 3.34):
                w = 0.70 + (y - 2.96) * 0.38 + 0.05
                mk.hull(la, round_ring(y - 0.04, s * arm_x(y), ARM_Z, w, w, n=8)
                        + round_ring(y + 0.04, s * arm_x(y), ARM_Z, w, w, n=8), "leather")
                mk.box(la, (s * (arm_x(y) + w / 2 * math.cos(math.radians(22.5)) + 0.01), y, ARM_Z), (0.04, 0.12, 0.12),
                       "brass", detail=True)


def head_part(mk):
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.26, 0, -0.18, 0.80, 0.70) + round_ring(4.52, 0, -0.21, 0.88, 0.86)
                     + round_ring(4.80, 0, -0.25, 0.94, 0.92) + round_ring(5.02, 0, -0.26, 0.86, 0.88)
                     + round_ring(5.18, 0, -0.26, 0.56, 0.62)), "skin_dead")                     # pelada
    mk.hull(hd, head([(-0.36, 4.44, -0.56), (0.36, 4.44, -0.56), (-0.38, 4.48, -0.14), (0.38, 4.48, -0.14),
                      (-0.28, 4.12, -0.66), (0.28, 4.12, -0.66), (-0.32, 4.16, -0.12), (0.32, 4.16, -0.12),
                      (-0.14, 4.06, -0.72), (0.14, 4.06, -0.72)]), "skin_dead")                    # mandíbula
    for s in (-1, 1):                                                                              # ceja
        mk.hull(hd, head([(s * 0.03, 4.84, -0.72), (s * 0.44, 4.92, -0.60), (s * 0.03, 4.94, -0.68),
                          (s * 0.44, 4.98, -0.56), (s * 0.03, 4.88, -0.46), (s * 0.42, 4.95, -0.42)]), "skin_dead")
    mk.hull(hd, head([(0, 4.82, -0.70), (0, 4.64, -0.80), (-0.14, 4.60, -0.68), (0.14, 4.60, -0.68),
                      (0, 4.59, -0.76), (-0.08, 4.62, -0.78), (0.08, 4.62, -0.78)]), "skin_dead")  # nariz chata
    mk.hull(hd, head(mk.pts_box((0.47, 4.70, -0.22), (0.09, 0.22, 0.15), top=(1, 0.7))), "skin_dead")   # oreja derecha
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.74, -0.74), 0.15, scale=(1.0, 0.7, 0.9),
                                                               subdiv=0)))
    mouth = [(-0.22, 4.47), (-0.12, 4.52), (0.13, 4.53), (0.24, 4.46), (0.18, 4.36), (-0.17, 4.37)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.90, -0.50)]))
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((-0.50, 4.70, -0.22), (0.16, 0.22, 0.20))))      # oreja arrancada
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((0.12, 5.12, -0.30), (0.08, 0.10, 0.50), rot=(0, 30, 0))))  # tajo
    for c, r in (((0.30, 4.98, -0.30), 0.14), ((-0.25, 5.10, 0.05), 0.15), ((0.10, 4.50, -0.10), 0.12)):
        mk.paint(hd, "skin_dead_dark", ball=(hp(c), r * KH))
    mk.paint(hd, "blood_dry", ball=(hp((-0.20, 4.30, -0.68)), 0.10))
    for i in range(5):
        x = -0.15 + 0.075 * i
        mk.hull(hd, head([(x - 0.032, 4.56, -0.64), (x + 0.032, 4.56, -0.64), (x - 0.02, 4.47, -0.64),
                          (x + 0.02, 4.47, -0.64), (x - 0.03, 4.56, -0.45), (x + 0.03, 4.56, -0.45),
                          (x, 4.48, -0.45)]), "bone", detail=True)
    for i in range(4):
        x = -0.11 + 0.075 * i
        mk.hull(hd, head([(x - 0.032, 4.38, -0.64), (x + 0.032, 4.38, -0.64), (x - 0.02, 4.46, -0.64),
                          (x + 0.02, 4.46, -0.64), (x - 0.03, 4.38, -0.45), (x + 0.03, 4.38, -0.45),
                          (x, 4.45, -0.45)]), "bone", detail=True)
    eyes = mk.part("Eyes", NECK_P)
    silver = mk.part("Silver_Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.74, -0.61)), 0.075 * KH, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)
        mk.ball(silver, hp((s * 0.19, 4.74, -0.61)), 0.075 * KH + 0.012, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)


def hook(mk):
    """Gancho de carne con mango en T (el puño lo cierra), la curva colgando abajo con la punta adelante
    y la cadena de seis eslabones que sale del ojal de atrás del mango."""
    g = GRIP
    hk = mk.part("Acc_Hook", g)

    def G(x, y, z):
        return (g[0] + x, g[1] + y, g[2] + z)
    mk.cyl(hk, G(0, 0, 0), 0.08, 0.90, "iron", axis="z", sides=8)                                  # mango en T
    for z in (-0.45, 0.45):
        mk.cyl(hk, G(0, 0, z), 0.105, 0.06, "iron", axis="z", sides=8)                            # topes
    curve = [(0.0, 0.0), (-0.55, 0.0), (-0.82, 0.03), (-0.98, -0.08), (-1.06, -0.26), (-1.00, -0.44),
             (-0.84, -0.55), (-0.62, -0.58), (-0.48, -0.56)]
    tube(mk, hk, [G(0, y, z) for y, z in curve], 0.12, 0.03, "iron")
    mk.bevel(hk, width=0.012, angle=35)
    c_ring(mk, hk, G(0, 0, 0.50), 0.12, 0.12, 0.045, 0.06, "iron", plane="xy", n=10, gap=8, detail=True)   # ojal
    for i in range(6):
        y = -0.18 - 0.24 * i
        c_ring(mk, hk, G(0, y, 0.50), 0.10, 0.16, 0.05, 0.06, "iron", plane="zy" if i % 2 == 0 else "xy",
               n=8, gap=8, detail=True)
    mk.marker("_HookTip", G(0, -0.48, -0.56))
    mk.marker("_ChainEnd", G(0, -0.18 - 0.24 * 5 - 0.16, 0.50))


def cleaver(mk):
    c = (-1.10, 3.47, -0.21)
    cv = mk.part("Acc_Cleaver", c)
    turn = (0, 35, 0)

    def T(pts):
        return about(pts, c, turn)
    blade = [(-0.22, 3.26), (-0.58, 3.26), (-0.62, 3.20), (-0.62, 2.70), (-0.56, 2.62), (-0.22, 2.62),
             (-0.18, 2.68), (-0.18, 3.22)]
    mk.prism(cv, [(z + 0.21, y) for z, y in blade], 0.05, "gunmetal", plane="zy", center=(-1.10, 0, -0.21),
             rot=turn)                                                                              # hoja (lomo atrás)
    mk.bevel(cv, width=0.014, angle=35, mat="steel_light")
    mk.carve(cv, "coal", points=T(mk.pts_cyl((-1.10, 3.14, -0.27), 0.045, 0.2, axis="x", sides=8)))   # agujero
    mk.paint(cv, "blood_dry", ball=(T([(-1.10, 2.78, -0.62)])[0], 0.20))                            # sangre en el filo
    mk.hull(cv, T([(x, y, z) for x in (-1.14, -1.06) for y in (3.62, 3.22) for z in (-0.25, -0.17)]), "wood_dark",
            detail=True)                                                                            # mango
    mk.hull(cv, T(mk.pts_box((-1.10, 3.66, -0.21), (0.09, 0.06, 0.10))), "iron", detail=True)      # remate
    for y in (3.30, 3.585):
        mk.hull(cv, T(mk.pts_cyl((-1.10, y, -0.21), 0.022, 0.10, axis="x", sides=6)), "brass", detail=True)   # remaches


def silver(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        part = mk.part(f"Silver_{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))

        def axis(y, s=s):
            if y >= 3.80:
                t = (4.14 - y) / 0.34
                rx, rz, dx = 0.35 + 0.14 * t, 0.37 + 0.11 * t, 0.03 * t
            else:
                t = (3.80 - y) / 0.82
                rx, rz, dx = 0.49 - 0.19 * t, 0.48 - 0.16 * t, 0.03 * (1 - t)
            return s * (arm_x(y) + dx), ARM_Z, rx, rz
        base = 180 if s < 0 else 0
        if side == "Left":   # arriba del guantelete
            br = [((4.10, base - 30), (3.82, base - 10), 0.11, 0.08), ((3.84, base - 12), (3.62, base + 10), 0.08, 0.05),
                  ((3.84, base - 12), (3.64, base - 45), 0.07, 0.04), ((4.06, base + 40), (3.80, base + 60), 0.07, 0.04)]
        else:                # bajan hasta la soga
            br = [((4.10, base + 30), (3.70, base + 10), 0.11, 0.09), ((3.72, base + 10), (3.30, base - 5), 0.09, 0.06),
                  ((3.74, base + 12), (3.40, base + 50), 0.07, 0.04), ((3.32, base - 5), (3.24, base - 30), 0.05, 0.03),
                  ((4.00, base - 50), (3.66, base - 70), 0.07, 0.04)]
        veins(mk, part, axis, br)
    # cuello, lado izquierdo
    sn = mk.part("Silver_Neck", (0, WAIST, 0))
    base, r, tilt = (0, 5.62, -0.22), 0.50, -25
    ax = (0.0, math.cos(math.radians(tilt)), math.sin(math.radians(tilt)))
    v = (0.0, -math.sin(math.radians(tilt)), math.cos(math.radians(tilt)))

    def P(t, a, off):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + off
        return (rr * ca, base[1] + ax[1] * t + rr * sa * v[1], base[2] + ax[2] * t + rr * sa * v[2])
    for k, (t0, a0, t1, a1, w0, w1) in enumerate(((-0.06, 155, 0.14, 150, 0.12, 0.10), (0.12, 151, 0.32, 135, 0.09, 0.05),
                                                  (0.12, 151, 0.30, 172, 0.08, 0.04), (0.0, 157, 0.20, 125, 0.07, 0.04))):
        out, dep = 0.02 + 0.007 * (k % 3), -0.05 - 0.006 * k
        t0, t1 = t0 - 0.008 * k, t1 + 0.006 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [P(t, a - da, out), P(t, a + da, out), P(t, a - da, dep), P(t, a + da, dep)]
        mk.hull(sn, pts, "silver_neon")


def build(mk):
    upper_torso(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_part(mk)
    hook(mk)
    cleaver(mk)
    silver(mk)

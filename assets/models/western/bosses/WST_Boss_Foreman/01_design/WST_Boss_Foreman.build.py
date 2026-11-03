"""
Receta de WST_Boss_Foreman, el Capataz de la mina (prompt 059, Bloques A + D + H + G). Jefe mediano.

Brief
- Silueta a 40 studs: un barril de hombre, pecho y panza redondos, sombrero duro de minero con la vela
  encendida adelante, patillas grises de hacha, bandolera de dinamita roja cruzada del hombro derecho a
  la cadera izquierda, un cartucho en la mano derecha con la mecha arriba y cristales de plata que le
  revientan la espalda por el hombro derecho.
- Escala: H = 6,4 (k = 6,4 / 5,2 = 1,231). Articulaciones del Bloque D: tobillo 0,32 · rodilla 1,60 ·
  cadera 3,008 · cintura 3,52 · codo 3,712 · muñeca 2,688 · hombro 4,864 · cuello 5,12. Pecho de barril
  1,94 de ancho y 1,24 de fondo (1,25 y 1,5 veces el caminante escalado): hombros x = ±1,10, codos ±1,26,
  muñecas ±1,41 (8° hacia afuera), caderas ±0,40, brazos en z = -0,12. El programador pasa esto a la ficha.
- Piezas: las 15 de R15, Eyes, Acc_Hat (base de la copa), Acc_Hat_Flame (pabilo de la vela),
  Acc_Dynamite (la mano derecha), Acc_Whistle (donde se engancha la cadena), Silver_Head (cuello, como
  Head), Silver_Neck, Silver_UpperTorso_Crust (cintura, como UpperTorso), Silver_LeftLowerArm,
  Silver_RightLowerArm, Silver_LeftLowerArm_Crust (codo), _Fuse.
- Tallado: cuencas, boca, cicatriz sobre la nariz (prompt), oreja derecha mordida, camisa rota en la
  panza, pantalón roto en la rodilla derecha. Pintado: moteado, nudillos.
- Inferido: sombrero cloth_brown (como el del minero atrapado), vela paint_cream en un soporte de hierro;
  chaleco abierto (así se ven los tiradores); la bandolera es una correa leather_dark con presillas
  leather y 10 cartuchos perpendiculares a la correa; el silbato cuelga del lado izquierdo (la bandolera
  ocupa el derecho); el cartucho de la mano se sostiene parado con la mecha arriba, delante del puño;
  sin Silver_Eyes (el prompt no las pide); las vetas van en una pieza por segmento que se mueve.

Vueltas: 1) primera versión; errores: tiradores de arriba y de abajo con los costados en el mismo plano,
puntera y bota con la base a la misma altura · 2) cicatriz de 0,07 de ancho (la de 0,04 no se veía),
antebrazos 0,62 (0,54), muslos 0,76 (0,68); las vetas de la cara van en la mejilla entre la nariz y la
patilla (sobre el cráneo quedaban enterradas en la mandíbula y las patillas) · 3) nuca con la forma del
cráneo (era una caja plana), tres púas de cristal en la placa del antebrazo.

Revisión
- 4014 triángulos contra 4200: entra en el tope.
- Alto 6,853 con el sombrero y la vela; el cuerpo, 6,4.
- Dudoso: el sombrero duro se parece a un bombín (el prompt pide "hard felt"); el torso es un barril de
  caras planas, como los caminantes; la cicatriz es una banda de 0,07 tallada en blood_dry.
"""

import math

from mathutils import Vector

import humanoid as hu

H = 6.4
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
SH_X, ARM_Z, LEG_X = 1.10, -0.12, 0.40
TAN8 = math.tan(math.radians(8))
EL_X, WR_X = SH_X + (SHOULDER - ELBOW) * TAN8, SH_X + (SHOULDER - WRIST) * TAN8
NECK_P = (0.0, NECK, -0.12)
HEAD_FWD, HEAD_TILT = 0.14, -8

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def head(pts):
    """Espacio de la cabeza del caminante (H = 5,2) -> Capataz: escala k, adelanta y baja."""
    return about([(x * K, y * K, z * K - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def arm_x(y):
    return SH_X + (SHOULDER - y) * TAN8


def shirt_front(y):
    """z del frente de la camisa (cara plana del barril) a la altura y."""
    if y <= 4.30:
        return -0.50 - 0.16 * (y - 3.44) / 0.86
    return -0.66 + 0.26 * (y - 4.30) / 0.56


def rod(mk, part, a, b, r, mat, sides=6, detail=False):
    """Cilindro entre dos puntos."""
    A, B = Vector(a), Vector(b)
    d = (B - A).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u)
    pts = [tuple(P + r * (math.cos(t) * u + math.sin(t) * v)) for P in (A, B)
           for t in [2 * math.pi * (i + 0.5) / sides for i in range(sides)]]
    mk.hull(part, pts, mat, detail=detail)


def strap(mk, part, path, w, mat, back=0.12, detail=False):
    """Correa por una línea quebrada de puntos de la superficie (frente de la correa); el ancho va
    perpendicular en el plano xy y la correa se mete `back` hacia adentro (+z)."""
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
    """Vetas sobre un miembro vertical: axis(y) -> (cx, cz, rx, rz). branches: [((y0, a0), (y1, a1), w0, w1)].
    Ángulo 0 = +x, 90 = atrás (+z), 270 = adelante. Alturas y profundidades distintas: nada coplanar."""
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


def shard(mk, part, base, direction, length, r, mat="silver_crust"):
    """Cristal hexagonal que termina en punta."""
    B = Vector(base)
    d = Vector(direction).normalized()
    up = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u)
    ring_pts = [tuple(B + r * (math.cos(t) * u + math.sin(t) * v)) for t in [math.pi / 3 * i for i in range(6)]]
    mid = [tuple(B + d * length * 0.55 + r * 0.8 * (math.cos(t) * u + math.sin(t) * v)) for t in
           [math.pi / 3 * i + 0.3 for i in range(6)]]
    mk.hull(part, ring_pts + mid + [tuple(B + d * length)], mat)


# ======================================================================================
def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    top = [(-0.55, 4.86, -0.40), (0.55, 4.86, -0.40), (-1.00, 4.70, -0.30), (1.00, 4.80, -0.30),
           (-1.00, 4.72, 0.30), (1.00, 4.82, 0.30), (-0.36, 4.94, 0.22), (0.36, 4.94, 0.22)]
    hump = [(-0.50, 4.62, 0.62), (0.50, 4.64, 0.62), (0.0, 4.70, 0.66)]
    mk.hull(ut, ring(3.44, 0, 0.02, 1.62, 1.04) + ring(4.30, 0, -0.04, 1.94, 1.24) + top + hump, "canvas")
    # camisa rota en la panza
    mk.carve(ut, "skin_dead", points=mk.pts_box((0.12, 3.62, -0.52), (0.26, 0.20, 0.12), rot=(0, 0, 18)))
    # chaleco de cuero abierto: espalda y costados + dos paneles adelante
    mk.hull(ut, [(x, y, max(z, -0.36)) for x, y, z in ring(3.40, 0, 0.02, 1.72, 1.14) + ring(4.30, 0, -0.04, 2.02, 1.32)]
            + [(-1.04, 4.72, -0.30), (1.04, 4.82, -0.30), (-1.04, 4.74, 0.32), (1.04, 4.84, 0.32),
               (-0.40, 4.96, 0.24), (0.40, 4.96, 0.24), (-0.52, 4.64, 0.68), (0.52, 4.66, 0.68), (0.0, 4.72, 0.72)],
            "leather")
    for s in (-1, 1):
        mk.hull(ut, [p for x, y in ((0.36, 3.40), (0.30, 4.30), (0.28, 4.80), (0.96, 3.40), (0.99, 4.30), (0.98, 4.76))
                     for p in ((s * x, y, shirt_front(y) - 0.04), (s * x, y, shirt_front(y) + 0.14))], "leather")
    # tiradores (se ven en la abertura del chaleco)
    for s in (-1, 1):
        strap(mk, ut, [(s * 0.22, 3.36, shirt_front(3.36) - 0.02), (s * 0.22, 4.30, shirt_front(4.30) - 0.02),
                       (s * 0.22, 4.86, shirt_front(4.86) - 0.02)], 0.10, "leather_dark", back=0.06)
    # cuello grueso y cuello de la camisa
    mk.cyl(ut, (0, 5.00, -0.16), 0.30, 0.50, "skin_dead", rot=(-20, 0, 0), sides=10)
    mk.cyl(ut, (0, 4.90, -0.17), 0.34, 0.14, "canvas", rot=(-20, 0, 0), sides=10)
    # cadena del reloj sobre el panel derecho
    chain = [(0.40, 3.86), (0.52, 3.72), (0.66, 3.68), (0.80, 3.74)]
    for (x0, y0), (x1, y1) in zip(chain, chain[1:]):
        rod(mk, ut, (x0, y0, shirt_front(y0) - 0.05), (x1, y1, shirt_front(y1) - 0.05), 0.018, "brass", sides=4,
            detail=True)
    mk.cyl(ut, (0.40, 3.86, shirt_front(3.86) - 0.05), 0.03, 0.03, "brass", axis="z", sides=6, detail=True)
    # bandolera de dinamita: del hombro derecho a la cadera izquierda, adelante y atrás
    front = [(0.70, 4.98, 0.0), (0.64, 4.88, -0.30)] + [(x, y, shirt_front(y) - 0.09) for x, y in
                                                      ((0.50, 4.70), (0.10, 4.25), (-0.30, 3.85), (-0.66, 3.48),
                                                       (-0.80, 3.34))]
    strap(mk, ut, front, 0.22, "leather_dark")
    strap(mk, ut, [(0.70, 4.98, 0.0), (0.66, 4.88, 0.42), (0.10, 4.30, 0.74), (-0.50, 3.70, 0.66),
                   (-0.84, 3.34, 0.62)], 0.22, "leather_dark", back=-0.12)
    a, b = Vector((0.50, 4.70, 0)), Vector((-0.66, 3.48, 0))
    d = (b - a).normalized()
    n = Vector((d.y, -d.x, 0))                          # perpendicular, hacia abajo a la derecha
    for i in range(10):
        c = a.lerp(b, 0.04 + 0.92 * i / 9)
        p0, p1 = c + n * 0.17, c - n * 0.17
        z0, z1 = shirt_front(p0.y) - 0.165, shirt_front(p1.y) - 0.165
        rod(mk, ut, (p0.x, p0.y, z0), (p1.x, p1.y, z1), 0.055, "dynamite_red", sides=6, detail=True)
        rod(mk, ut, (c.x + n.x * 0.03, c.y + n.y * 0.03, shirt_front(c.y) - 0.16),
            (c.x - n.x * 0.03, c.y - n.y * 0.03, shirt_front(c.y) - 0.16), 0.068, "leather", sides=6, detail=True)
    return ut


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, ring(2.92, 0, 0, 1.42, 0.88) + ring(3.58, 0, 0.02, 1.62, 1.06), "cloth_blue")        # pantalón
    mk.hull(lt, ring(3.28, 0, 0.02, 1.72, 1.16) + ring(3.42, 0, 0.02, 1.72, 1.16), "leather_dark")    # cinturón
    mk.box(lt, (0, 3.35, -0.575), (0.24, 0.20, 0.06), "iron")
    mk.carve(lt, "leather_dark", points=mk.pts_box((0, 3.35, -0.62), (0.14, 0.10, 0.08)))
    for s in (-1, 1):   # puntas del chaleco, metidas atrás del cinturón
        zf = -0.545 if s < 0 else -0.54
        mk.hull(lt, [(x, y, z) for x, y in ((s * 0.36, 3.58), (s * 0.98, 3.58), (s * 0.98, 3.44), (s * 0.40, 3.38))
                     for z in (zf, -0.36)], "leather")
        mk.hull(lt, [(x, y, z) for x in (s * 0.176, s * 0.264) for y in (3.60, 3.42) for z in (-0.53, -0.47)],
                "leather_dark")                                                                    # tiradores
        mk.cyl(lt, (s * 0.22, 3.47, -0.535), 0.03, 0.03, "brass", axis="z", sides=6, detail=True)
    # la bandolera rodea la cadera izquierda
    strap(mk, lt, [(-0.78, 3.60, -0.60), (-0.90, 3.30, -0.54)], 0.22, "leather_dark", back=0.10)
    mk.hull(lt, [(x, y, z) for x in (-0.80, -0.97) for y, z in ((3.18, -0.56), (3.40, -0.56), (3.16, 0.0), (3.38, 0.0),
                                                                 (3.26, 0.60), (3.48, 0.60))], "leather_dark")
    strap(mk, lt, [(-0.92, 3.30, 0.62), (-0.84, 3.52, 0.64)], 0.22, "leather_dark", back=-0.10)
    return lt


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(mk, ul, (x, HIP, 0), (x, KNEE, 0), 0.76, 0.78, 0.58, 0.60, "cloth_blue", over=0.06)
        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(mk, ll, (x, KNEE, 0), (x, 0.66, 0), 0.58, 0.60, 0.50, 0.52, "cloth_blue", over=0.06)
        mk.hull(ll, ring(0.80, x, 0.0, 0.52, 0.56) + ring(0.24, x, 0.0, 0.48, 0.54), "leather_dark")   # caña de la bota
        if side == "Right":     # pantalón roto en la rodilla
            mk.carve(ll, "skin_dead", points=mk.pts_box((x + 0.02, 1.52, -0.26), (0.24, 0.24, 0.14), rot=(0, 0, 20)))
        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.25, 0.25) for y, z in ((0.07, 0.26), (0.40, 0.24), (0.36, -0.14))]
                + [(x + dx, y, z) for dx in (-0.23, 0.23) for y, z in ((0.07, -0.58), (0.26, -0.52))], "leather_dark")
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.255, 0.255) for y, z in ((0.09, -0.30), (0.29, -0.30), (0.09, -0.62),
                                                                          (0.24, -0.60))], "iron")   # puntera de acero
        mk.hull(ft, [(x + dx, y, z) for dx in (-0.26, 0.26) for y in (0.0, 0.08) for z in (0.28, -0.63)], "coal")


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        ua = mk.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        mk.hull(ua, round_ring(4.94, s * arm_x(4.94), ARM_Z, 0.46, 0.50) + round_ring(4.70, s * arm_x(4.70), ARM_Z, 0.62, 0.64)
                + round_ring(3.68, s * arm_x(3.68), ARM_Z, 0.54, 0.56), "canvas")
        la = mk.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        mk.hull(la, round_ring(3.80, s * arm_x(3.80), ARM_Z, 0.68, 0.70, n=8) + round_ring(3.54, s * arm_x(3.54), ARM_Z, 0.68, 0.70, n=8),
                "canvas")                                                                          # manga arremangada
        mk.hull(la, round_ring(3.60, s * arm_x(3.60), ARM_Z, 0.56, 0.58) + round_ring(3.30, s * (arm_x(3.30) + 0.02), ARM_Z, 0.62, 0.62)
                + round_ring(2.72, s * arm_x(2.72), ARM_Z, 0.44, 0.48), "skin_dead")
        mk.paint(la, "skin_dead_dark", ball=((s * (arm_x(3.10) + 0.25), 3.10, ARM_Z), 0.16))
        hd = mk.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hx = s * (WR_X + 0.03)
        mk.hull(hd, round_ring(2.76, hx, ARM_Z, 0.33, 0.50) + round_ring(2.40, hx + s * 0.01, ARM_Z, 0.35, 0.54)
                + round_ring(2.06, hx + s * 0.02, ARM_Z, 0.27, 0.42), "skin_dead")
        mk.box(hd, (hx - s * 0.10, 2.50, ARM_Z - 0.26), (0.14, 0.32, 0.14), "skin_dead", rot=(-15, 0, 0))   # pulgar
        mk.paint(hd, "skin_dead_dark", box=((hx, 2.06, ARM_Z), (0.5, 0.10, 0.6)))


def head_and_hat(mk):
    hd = mk.part("Head", NECK_P)
    mk.hull(hd, head(round_ring(4.26, 0, -0.18, 0.76, 0.66) + round_ring(4.52, 0, -0.21, 0.88, 0.84)
                     + round_ring(4.80, 0, -0.25, 0.96, 0.92) + round_ring(5.02, 0, -0.26, 0.86, 0.86)
                     + round_ring(5.16, 0, -0.26, 0.56, 0.60)), "skin_dead")
    mk.hull(hd, head([(-0.32, 4.44, -0.58), (0.32, 4.44, -0.58), (-0.34, 4.46, -0.16), (0.34, 4.46, -0.16),
                      (-0.24, 4.16, -0.66), (0.24, 4.16, -0.66), (-0.28, 4.20, -0.14), (0.28, 4.20, -0.14),
                      (0, 4.12, -0.70)]), "skin_dead")                                               # mandíbula
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.03, 4.86, -0.71), (s * 0.44, 4.90, -0.58), (s * 0.03, 4.95, -0.67),
                          (s * 0.44, 4.97, -0.54), (s * 0.03, 4.88, -0.45), (s * 0.42, 4.94, -0.40)]), "skin_dead")   # ceja
        mk.hull(hd, head(mk.pts_box((s * 0.48, 4.70, -0.22), (0.09, 0.24, 0.16), top=(1, 0.7))), "skin_dead")   # orejas
        # patillas de hacha: anchas abajo, bajan por la mejilla hasta la mandíbula
        mk.hull(hd, head([(s * 0.44, 4.96, -0.34), (s * 0.49, 4.96, -0.10), (s * 0.48, 4.42, -0.56),
                          (s * 0.44, 4.26, -0.58), (s * 0.40, 4.24, -0.40), (s * 0.50, 4.52, -0.20),
                          (s * 0.30, 4.40, -0.64), (s * 0.30, 4.28, -0.66)]), "hair_grey")
        mk.hull(hd, head([(0, 4.60, -0.80), (s * 0.20, 4.58, -0.76), (s * 0.32, 4.48, -0.66), (s * 0.30, 4.40, -0.66),
                          (s * 0.14, 4.52, -0.80), (0, 4.54, -0.82), (0, 4.58, -0.66), (s * 0.28, 4.48, -0.52)]),
                "hair_grey")                                                                       # bigote que une
    mk.hull(hd, head([(0, 4.84, -0.70), (0, 4.62, -0.86), (-0.10, 4.60, -0.70), (0.10, 4.60, -0.70),
                      (0, 4.58, -0.74), (-0.05, 4.74, -0.72), (0.05, 4.74, -0.72)]), "skin_dead")   # nariz
    cap = [p for y, w, d in ((4.56, 0.86, 0.80), (4.80, 1.00, 0.96), (5.00, 0.92, 0.92))
           for p in round_ring(y, 0, -0.25, w, d, n=12) if p[2] > -0.20]
    mk.hull(hd, head(cap + [(0, 4.50, 0.08)]), "hair_grey")                                         # nuca bajo el sombrero
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.75, -0.75), 0.15, scale=(1.0, 0.72, 0.9),
                                                               subdiv=0)))
    mouth = [(-0.17, 4.47), (0.17, 4.47), (0.15, 4.33), (-0.15, 4.33), (0, 4.30)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.95, -0.52)]))
    scar = head([(x, y, z) for x, y in ((-0.30, 4.90), (-0.24, 4.93), (0.30, 4.58), (0.24, 4.55)) for z in (-0.97, -0.74)])
    mk.carve(hd, "blood_dry", points=scar)                                                         # cicatriz
    mk.carve(hd, "blood_dry", points=head(mk.pts_box((0.52, 4.80, -0.22), (0.12, 0.12, 0.14), rot=(30, 0, 0))))  # oreja mordida
    for i in range(4):
        x = -0.11 + 0.073 * i
        mk.hull(hd, head([(x - 0.03, 4.33, -0.68), (x + 0.03, 4.33, -0.68), (x - 0.02, 4.42, -0.68),
                          (x + 0.02, 4.42, -0.68), (x - 0.03, 4.33, -0.46), (x + 0.03, 4.33, -0.46),
                          (x, 4.41, -0.46)]), "bone", detail=True)
    mk.paint(hd, "skin_dead_dark", ball=(hp((0.30, 5.02, -0.40)), 0.18))
    mk.paint(hd, "blood_dry", ball=(hp((0.10, 4.22, -0.68)), 0.09))

    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.75, -0.61)), 0.08 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)

    # sombrero duro de minero: copa redonda alta, ala corta, soporte con la vela adelante
    base = hp((0, 4.98, -0.26))
    hat = mk.part("Acc_Hat", base)
    mk.hull(hat, head(round_ring(4.97, 0, -0.26, 1.24, 1.30, n=14) + round_ring(5.02, 0, -0.26, 1.24, 1.30, n=14)),
            "cloth_brown")                                                                        # ala corta
    mk.hull(hat, head(round_ring(4.98, 0, -0.26, 0.96, 1.02, n=12) + round_ring(5.26, 0, -0.26, 0.98, 1.04, n=12)
                      + round_ring(5.46, 0, -0.26, 0.86, 0.92, n=12) + round_ring(5.58, 0, -0.26, 0.54, 0.60, n=12)),
            "cloth_brown")
    mk.hull(hat, head(round_ring(5.04, 0, -0.26, 0.99, 1.05, n=12) + round_ring(5.10, 0, -0.26, 0.99, 1.05, n=12)),
            "leather_dark")                                                                       # cinta
    mk.hull(hat, head(mk.pts_box((0, 5.20, -0.78), (0.16, 0.22, 0.05))), "iron")                  # chapa del soporte
    mk.hull(hat, head(mk.pts_box((0, 5.20, -0.84), (0.05, 0.05, 0.10))), "iron")
    mk.hull(hat, head(mk.pts_cyl((0, 5.24, -0.90), 0.07, 0.06, axis="y", sides=8)), "iron")       # copita
    mk.hull(hat, head(mk.pts_cyl((0, 5.33, -0.90), 0.045, 0.14, axis="y", sides=6)), "paint_cream")   # vela
    flame_base = hp((0, 5.40, -0.90))
    fl = mk.part("Acc_Hat_Flame", flame_base)
    mk.hull(fl, head([(dx, 5.40, -0.90 + dz) for dx, dz in ((-0.035, 0), (0.035, 0), (0, -0.035), (0, 0.035))]
                     + [(dx, 5.45, -0.90 + dz) for dx, dz in ((-0.045, 0), (0.045, 0), (0, -0.045), (0, 0.045))]
                     + [(0, 5.56, -0.90)]), "lamp_glow")


def dynamite(mk):
    """Cartucho parado en la mano derecha, delante del puño, con la mecha arriba."""
    hx = WR_X + 0.03
    c = (hx, WRIST - 0.32, ARM_Z - 0.28)
    dy = mk.part("Acc_Dynamite", (hx, WRIST - 0.32, ARM_Z))
    mk.cyl(dy, c, 0.075, 0.48, "dynamite_red", sides=8)
    for y in (c[1] - 0.24, c[1] + 0.24):
        mk.cyl(dy, (c[0], y, c[2]), 0.072, 0.03, "paint_cream", sides=8)                          # tapas de papel
    fuse = [(c[0], c[1] + 0.25, c[2]), (c[0], c[1] + 0.36, c[2] - 0.02), (c[0] + 0.03, c[1] + 0.46, c[2] - 0.08)]
    for p0, p1 in zip(fuse, fuse[1:]):
        rod(mk, dy, p0, p1, 0.016, "rope", sides=4)
    mk.marker("_Fuse", fuse[-1])


def whistle(mk):
    top = (-0.30, 4.74, shirt_front(4.74) - 0.05)
    wh = mk.part("Acc_Whistle", top)
    links = [top, (-0.31, 4.58, shirt_front(4.58) - 0.05), (-0.32, 4.42, shirt_front(4.42) - 0.055)]
    for p0, p1 in zip(links, links[1:]):
        rod(mk, wh, p0, p1, 0.016, "brass", sides=4)
    bz = shirt_front(4.36) - 0.075
    rod(mk, wh, (-0.36, 4.36, bz), (-0.18, 4.36, bz), 0.04, "brass", sides=8)                     # silbato
    mk.hull(wh, mk.pts_box((-0.20, 4.385, bz), (0.05, 0.03, 0.06)), "coal")                         # boca


def silver(mk):
    # cuello y media cara izquierda
    sn = mk.part("Silver_Neck", (0, WAIST, 0))
    base, r, tilt = (0, 5.00, -0.16), 0.30, -20
    ax = (math.cos(math.radians(tilt)), math.sin(math.radians(tilt)))

    def NP(t, a, off):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + off
        return (rr * ca, base[1] + ax[0] * t - rr * sa * ax[1], base[2] + ax[1] * t + rr * sa * ax[0])
    for k, (t0, a0, t1, a1, w0, w1) in enumerate(((-0.10, 200, 0.14, 210, 0.10, 0.08), (0.10, 208, 0.26, 228, 0.07, 0.05),
                                                  (0.08, 206, 0.24, 186, 0.06, 0.04))):
        out, dep = 0.02 + 0.007 * k, -0.05 - 0.006 * k
        t0, t1 = t0 - 0.008 * k, t1 + 0.006 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [NP(t, a - da, out), NP(t, a + da, out), NP(t, a - da, dep), NP(t, a + da, dep)]
        mk.hull(sn, pts, "silver_neon")

    sh = mk.part("Silver_Head", NECK_P)
    rings = ((4.26, -0.18, 0.76, 0.66), (4.52, -0.21, 0.88, 0.84), (4.80, -0.25, 0.96, 0.92), (5.02, -0.26, 0.86, 0.86))

    def FP(y, a, off):
        for (ya, ca, wa, da), (yb, cb, wb, db) in zip(rings, rings[1:]):
            if ya <= y <= yb:
                t = (y - ya) / (yb - ya)
                cz, w, d = ca + (cb - ca) * t, wa + (wb - wa) * t, da + (db - da) * t
                break
        ang = math.radians(a)
        return (math.cos(ang) * (w / 2 + off), y, cz + math.sin(ang) * (d / 2 + off))
    for k, ((y0, a0), (y1, a1), w0, w1) in enumerate((((4.48, 248), (4.66, 240), 0.07, 0.06), ((4.65, 240), (4.84, 226), 0.05, 0.035),
                                                      ((4.64, 241), (4.74, 256), 0.045, 0.03), ((4.50, 248), (4.44, 236), 0.04, 0.03))):
        out, dep = 0.022 + 0.006 * k, -0.04 - 0.006 * k
        y0, y1 = y0 - 0.006 * k, y1 + 0.005 * k
        pts = []
        for y, a, w in ((y0, a0, w0), (y1, a1, w1)):
            for off in (out, dep):
                rr = 0.45
                da = math.degrees(w / 2 / rr)
                pts += [FP(y, a - da, off), FP(y, a + da, off)]
        mk.hull(sh, head(pts), "silver_neon")

    # antebrazos (arremangados)
    for side, s in (("Left", -1), ("Right", 1)):
        part = mk.part(f"Silver_{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))

        def axis(y, s=s):
            if y >= 3.30:
                t = (3.60 - y) / 0.30
                rx, rz, dx = 0.28 + 0.03 * t, 0.29 + 0.02 * t, 0.02 * t
            else:
                t = (3.30 - y) / 0.58
                rx, rz, dx = 0.31 - 0.09 * t, 0.31 - 0.07 * t, 0.02 * (1 - t)
            return s * (arm_x(y) + dx), ARM_Z, rx, rz
        b = 180 if s < 0 else 0
        if side == "Left":   # adelante de la costra (la costra va atrás y afuera)
            br = [((3.50, b + 60), (3.12, b + 75), 0.08, 0.06), ((3.14, b + 75), (2.86, b + 95), 0.06, 0.04),
                  ((3.15, b + 74), (2.92, b + 55), 0.05, 0.03)]
        else:
            br = [((3.50, b - 40), (3.10, b - 20), 0.08, 0.06), ((3.12, b - 20), (2.84, b - 5), 0.06, 0.04),
                  ((3.13, b - 21), (2.90, b - 50), 0.05, 0.03), ((3.44, b + 20), (3.20, b + 40), 0.05, 0.03)]
        veins(mk, part, axis, br)
        if side == "Left":   # placa de costra en el antebrazo: base de neón y placas encima (las juntas brillan)
            cr = mk.part("Silver_LeftLowerArm_Crust", (s * EL_X, ELBOW, ARM_Z))
            for y0, y1, a0, a1, out in ((3.42, 3.20, 150, 200, 0.05), (3.22, 3.00, 145, 195, 0.06), (3.40, 3.04, 195, 225, 0.045)):
                pts = []
                for y in (y0, y1):
                    cx, cz, rx, rz = axis(y)
                    for a in (a0, (a0 + a1) / 2, a1):
                        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                        jag = 0.02 if a == (a0 + a1) / 2 else 0.0
                        for off in (out + jag, -0.03):
                            pts.append((cx + (rx + off) * ca, y, cz + (rz + off) * sa))
                mk.hull(cr, pts, "silver_crust")
            pts = []
            for y in (3.44, 2.98):
                cx, cz, rx, rz = axis(y)
                for a in (140, 170, 200, 228):
                    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                    for off in (0.02, -0.04):
                        pts.append((cx + (rx + off) * ca, y, cz + (rz + off) * sa))
            mk.hull(cr, pts, "silver_neon")
            for y, a, d, ln in ((3.30, 175, (-0.6, 0.6, 0.3), 0.18), (3.12, 160, (-0.7, 0.2, 0.6), 0.14),
                                (3.28, 205, (-0.6, 0.4, -0.5), 0.12)):
                cx, cz, rx, rz = axis(y)
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                shard(mk, cr, (cx + (rx + 0.03) * ca, y, cz + (rz + 0.03) * sa), d, ln, 0.035)

    # cristales que revientan la espalda por el hombro derecho
    cr = mk.part("Silver_UpperTorso_Crust", (0, WAIST, 0))
    mk.hull(cr, [(0.30, 4.40, 0.60), (0.85, 4.46, 0.52), (0.40, 4.86, 0.40), (0.80, 4.84, 0.34), (0.60, 4.70, 0.74),
                 (0.50, 4.50, 0.40), (0.70, 4.60, 0.40)], "silver_crust")                          # costra base
    mk.hull(cr, [(0.36, 4.46, 0.66), (0.78, 4.50, 0.62), (0.44, 4.80, 0.55), (0.74, 4.78, 0.52), (0.60, 4.66, 0.80),
                 (0.55, 4.60, 0.50)], "silver_neon")                                                # grieta que brilla
    for base, d, ln, r in (((0.56, 4.66, 0.66), (0.3, 0.9, 0.5), 0.60, 0.09), ((0.70, 4.58, 0.62), (0.8, 0.5, 0.5), 0.45, 0.075),
                           ((0.44, 4.56, 0.66), (-0.2, 0.6, 0.8), 0.36, 0.07), ((0.66, 4.78, 0.50), (0.4, 1.0, 0.1), 0.30, 0.06)):
        shard(mk, cr, base, d, ln, r)


def build(mk):
    upper_torso(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_and_hat(mk)
    dynamite(mk)
    whistle(mk)
    silver(mk)

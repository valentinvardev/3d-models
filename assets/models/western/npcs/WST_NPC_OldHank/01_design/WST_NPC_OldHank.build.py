"""
Receta de WST_NPC_OldHank, Old Hank (prompt 021, Bloques A + D). Vivo: guía del tutorial.

Brief
- Silueta a 40 studs: sombrero de ala ancha claro con el ala izquierda levantada, guardapolvo corto
  claro abierto adelante (chaleco oscuro, camisa roja y la cartuchera cruzada de bronce a la vista),
  bigote gris largo y caído, botas altas con espuelas, revólver con cachas de hueso en la cadera derecha.
- Medidas: H = 5,3 (se construye en el espacio de referencia de H = 5,2 con las articulaciones del
  Bloque D y se escala por K = 5,3 / 5,2). Cabeza 1/5 de H. Derecho: el encorvado lo hace la animación.
- Piezas: las 15 de R15 con el origen en su articulación, Eyes (origen en el cuello, como la cabeza),
  Acc_Hat (origen en la base del sombrero), Acc_HanksWidow (origen en el centro de la cacha),
  Acc_BiteWound (origen en el codo izquierdo, el mismo pivote que LeftLowerArm: se suelda sin offset).
- Capas de ropa con el mismo esqueleto de anillos ("niveles") crecido 0,04 por capa: camisa,
  chaleco (+0,04), cartuchera (+0,085), guardapolvo (+0,10). Paneles abiertos con planos de corte.
- Tallado: cuencas (piel más oscura), boca entre bigote y barba, patas de gallo, abolladura de la copa.
  Pintado: dedos fuera de los mitones, sangre de la mordida.
- Inferido (el prompt no lo dice): guardapolvo de lona (no marrón) para contrastar con el chaleco; el
  lado derecho del guardapolvo va recogido atrás de la funda; mangas del guardapolvo arremangadas con
  la camisa (puño de lona + vuelta roja en el codo); la cartuchera pasa por debajo del guardapolvo;
  la mordida es un trapo de lona atado con sangre y la marca tallada; botas de puntera aguzada con taco;
  ojos con blanco (bone) además del iris hair_dark que pide el prompt, para que la mirada se lea viva.

Vueltas: 1) primera versión · 2) cara: ceja curva (la caja plana sacaba 0,19 las puntas en las sienes),
cejas grises, barba pegada a la mandíbula y bigote 0,16 por delante (se fundían en un bloque), orejas
más chicas inclinadas, sin patas de gallo (se leían como cicatrices y rompían la malla); z-fighting de
las tapas de las capas y de los planos de corte repetidos · 3) blanco del ojo y párpados más altos
(tapaban el 70 % del ojo: parecía dormido) · 4) pliegue de la copa más suave (quedaba un tajo en V).

Revisión
- 3074 triángulos contra 2200 de referencia (+40 %, calidad primero; es el NPC principal): cara con
  tres niveles (cejas, párpados, bigote con puntas, labio, entrecejo tallado: Head 926), tres capas de
  ropa con solapas y la cartuchera de 9 balas (UpperTorso 614) y los accesorios (sombrero, revólver,
  mordida: 364). Lo que no se ve (espalda, suelas) está en el mínimo.
- 18 colores en total, 13 en el cuerpo (Bloque A pide hasta 12 en personajes): el prompt solo ya
  nombra 14 con los accesorios.
- Alto 5,3 al pelo (5,63 con el sombrero). Avisos de "floating": ninguno.
"""

import math

from mathutils import Euler, Vector

# =============== base común de los NPC (primera versión; la completa, con la cara viva, está en las otras recetas del lote) ===============
H = 5.3
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.26, 1.30, 2.444, 2.86
ELBOW, WRIST, SHOULDER, NECK = 3.016, 2.184, 3.952, 4.16
SH_X, EL_X, WR_X, LEG_X = 0.80, 0.93, 1.05, 0.30
ARM_Z = -0.04                       # vivo y derecho: los brazos casi en el plano del cuerpo
NECK_P = (0.0, NECK, -0.06)
HEAD_FWD, HEAD_TILT = 0.04, 0.0


def ring(y, cx, cz, w, d, ch=0.28):
    """Octógono horizontal (ancho w en x, profundidad d en z) a la altura y."""
    a, b, ca, cb = w / 2, d / 2, w / 2 * (1 - ch), d / 2 * (1 - ch)
    return [(cx + x, y, cz + z) for x, z in
            ((-ca, -b), (ca, -b), (a, -cb), (a, cb), (ca, b), (-ca, b), (-a, cb), (-a, -cb))]


def round_ring(y, cx, cz, w, d, n=10):
    return [(cx + w / 2 * math.cos(2 * math.pi * (i + 0.5) / n), y, cz + d / 2 * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def about(points, pivot, rot):
    e = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    p = Vector(pivot)
    return [tuple(p + e @ (Vector(q) - p)) for q in points]


def head(pts):
    return about([(x, y, z - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def clip(poly, a, b, c):
    """Recorta un polígono horizontal: se queda con a*x + b*z + c >= 0."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[2] + c, a * q[0] + b * q[2] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append(tuple(p[j] + t * (q[j] - p[j]) for j in range(3)))
    return out


def XL(v):
    return (-1, 0, v)        # x <= v


def XG(v):
    return (1, 0, -v)        # x >= v


def ZL(v):
    return (0, -1, v)        # z <= v


def ZG(v):
    return (0, 1, -v)        # z >= v


def layer(levels, g, planes=()):
    """Puntos de una capa de ropa: los niveles (y, cx, cz, w, d) crecidos g y recortados por planos."""
    pts = []
    levels = sorted(levels)
    for i, (y, cx, cz, w, d) in enumerate(levels):
        gg = g(y) if callable(g) else g
        # cada capa termina un poco más allá que la de abajo: las tapas no quedan coplanares
        y += -0.3 * gg if i == 0 else 0.3 * gg if i == len(levels) - 1 else 0.0
        poly = ring(y, cx, cz, w + 2 * gg, d + 2 * gg)
        for pl in (planes(y) if callable(planes) else planes):
            poly = clip(poly, *pl)
        pts += poly
    return pts


def surf_z(levels, x, y, g=0.0):
    """z del frente de la capa g en (x, y): sirve para apoyar tiras, botones y balas."""
    lv = sorted(levels)
    y = min(max(y, lv[0][0]), lv[-1][0])
    for l0, l1 in zip(lv, lv[1:]):
        if l0[0] <= y <= l1[0]:
            t = (y - l0[0]) / (l1[0] - l0[0]) if l1[0] > l0[0] else 0
            _, cx, cz, w, d = (l0[j] + t * (l1[j] - l0[j]) for j in range(5))
            break
    a, b = w / 2 + g, d / 2 + g
    ca, cb = (w / 2 + g) * 0.72, (d / 2 + g) * 0.72
    ax = abs(x - cx)
    if ax <= ca:
        return cz - b
    t = min((ax - ca) / (a - ca), 1.0)
    return cz - (b + t * (cb - b))


class Ref:
    """modelkit en el espacio de referencia (H = 5,2): cada punto se escala por K al pasar."""

    def __init__(self, mk, k=K):
        self.mk, self.k = mk, k

    def P(self, p):
        return (p[0] * self.k, p[1] * self.k, p[2] * self.k)

    def part(self, name, origin):
        return self.mk.part(name, self.P(origin))

    def hull(self, part, pts, mat, detail=False):
        self.mk.hull(part, [self.P(p) for p in pts], mat, detail=detail)

    def box(self, part, center, size, mat, rot=(0, 0, 0), top=(1, 1), shift=(0, 0), detail=False):
        self.hull(part, self.mk.pts_box(center, size, rot, top, shift), mat, detail)

    def cyl(self, part, center, radius, length, mat, axis="y", sides=8, rot=(0, 0, 0), top=1.0, detail=False):
        self.hull(part, self.mk.pts_cyl(center, radius, length, axis, sides, rot, top), mat, detail)

    def ball(self, part, center, radius, mat, scale=(1, 1, 1), rot=(0, 0, 0), subdiv=1, detail=False):
        self.hull(part, self.mk.pts_ball(center, radius, scale, rot, subdiv), mat, detail)

    def prism(self, part, profile, depth, mat, plane="xy", center=(0, 0, 0), rot=(0, 0, 0), detail=False):
        k = self.k
        self.mk.prism(part, [(a * k, b * k) for a, b in profile], depth * k, mat, plane, self.P(center), rot, detail)

    def limb(self, part, top, bottom, wt, dt, wb, db, mat, over=0.05, detail=False):
        (x1, y1, z1), (x2, y2, z2) = top, bottom
        self.hull(part, ring(y1 + over, x1, z1, wt, dt) + ring(y2 - over, x2, z2, wb, db), mat, detail)

    def carve(self, part, mat, pts):
        self.mk.carve(part, mat, points=[self.P(p) for p in pts])

    def paint(self, part, mat, ball=None, box=None):
        if ball is not None:
            self.mk.paint(part, mat, ball=(self.P(ball[0]), ball[1] * self.k))
        else:
            self.mk.paint(part, mat, box=(self.P(box[0]), tuple(s * self.k for s in box[1])))

    def slice(self, part, point, normal):
        self.mk.slice(part, self.P(point), normal)


def strap(k, part, levels, path, width, thick, g, mat, inset=0.03, ext=0.03):
    """Tira (correa, cartuchera, tirador) apoyada en la capa g, por los puntos (x, y) de path."""
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        dx, dy = xb - xa, yb - ya
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        px, py = -uy * width / 2, ux * width / 2
        pts = []
        for x, y in ((xa - ux * ext, ya - uy * ext), (xb + ux * ext, yb + uy * ext)):
            for sg in (-1, 1):
                qx, qy = x + sg * px, y + sg * py
                z = surf_z(levels, qx, qy, g)
                pts += [(qx, qy, z + inset), (qx, qy, z - thick)]
        k.hull(part, pts, mat)


def along(path, step):
    """Puntos (x, y, ángulo en grados) cada `step` sobre un camino de segmentos."""
    out, carry = [], step / 2
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        n = math.hypot(xb - xa, yb - ya)
        ang = math.degrees(math.atan2(yb - ya, xb - xa))
        t = carry
        while t < n:
            out.append((xa + (xb - xa) * t / n, ya + (yb - ya) * t / n, ang))
            t += step
        carry = t - n
    return out


def hand(k, part, s, skin, glove=None, fingerless=False):
    """Mano grande de mitón con pulgar (Bloque D); con guante, y sin dedos si fingerless."""
    wx = s * WR_X + s * 0.02
    mat = glove or skin
    k.hull(part, round_ring(WRIST + 0.05, wx, ARM_Z, 0.21, 0.35) + round_ring(WRIST - 0.20, wx + s * 0.01, ARM_Z, 0.23, 0.38)
           + round_ring(WRIST - 0.47, wx + s * 0.02, ARM_Z, 0.18, 0.30), mat)
    k.box(part, (wx - s * 0.07, WRIST - 0.15, ARM_Z - 0.19), (0.10, 0.23, 0.11), mat, rot=(-15, 0, 0))
    if glove and fingerless:
        k.slice(part, (0, WRIST - 0.30, 0), (0, 1, 0))
        k.paint(part, skin, box=((wx, WRIST - 0.42, ARM_Z), (0.5, 0.24, 0.6)))
    if glove:   # puño del guante: tapa la muñeca
        k.hull(part, ring(WRIST + 0.10, wx - s * 0.01, ARM_Z, 0.28, 0.36) + ring(WRIST - 0.06, wx, ARM_Z, 0.28, 0.40), glove)


# =============== Old Hank ===============
SKIN, SKIN_DK = "skin_b", "skin_c"
UT_LV = [(2.80, 0, 0.00, 1.00, 0.56), (3.30, 0, -0.03, 1.24, 0.68), (3.72, 0, -0.01, 1.38, 0.64),
         (3.98, 0, -0.02, 1.42, 0.44), (4.08, 0, -0.02, 0.64, 0.36)]
LT_LV = [(2.30, 0, 0.0, 1.00, 0.56), (2.62, 0, 0.0, 1.06, 0.58), (2.94, 0, 0.0, 1.02, 0.56)]
G_VEST, G_COAT = 0.04, 0.10


def vest_edge(y):       # borde interior del chaleco abierto (V más ancha arriba)
    return 0.10 + 0.07 * (y - 2.80) / 1.28


def coat_edge(y):       # borde del guardapolvo abierto: más abierto abajo
    return 0.40 - 0.18 * (y - 2.80) / 1.28


def build(mk):
    k = Ref(mk)

    # ---------------- UpperTorso: camisa, chaleco abierto, cartuchera, guardapolvo ----------------
    ut = k.part("UpperTorso", (0, WAIST, 0))
    k.hull(ut, layer(UT_LV, 0), "cloth_red")
    for s in (-1, 1):
        k.hull(ut, layer(UT_LV, G_VEST, lambda y, s=s: [(s, 0, -vest_edge(y)), ZL(0.02)]), "cloth_brown")
        k.hull(ut, layer(UT_LV, G_COAT, lambda y, s=s: [(s, 0, -coat_edge(y)), ZL(0.03)]), "canvas")
        # solapa doblada sobre el panel del guardapolvo
        e0, e1 = coat_edge(3.98), coat_edge(3.40)
        lap = [(s * (e0 + 0.012), 3.98), (s * (e0 + 0.20), 3.92), (s * (e1 + 0.012), 3.40)]
        k.hull(ut, [(x, y, surf_z(UT_LV, x, y, G_COAT) + dz) for x, y in lap for dz in (0.02, -0.035)]
               + [(s * (e1 + 0.10), 3.62, surf_z(UT_LV, s * (e1 + 0.10), 3.62, G_COAT) - 0.035)], "canvas")
    # espaldas 0,012 más afuera: donde se solapan con los paneles de adelante no quedan coplanares
    k.hull(ut, layer(UT_LV, G_VEST + 0.012, [ZG(0.0)]), "cloth_brown")
    k.hull(ut, layer(UT_LV, G_COAT + 0.012, [ZG(-0.01)]), "canvas")
    # cuello de la camisa y cuello alto del guardapolvo atrás
    k.cyl(ut, (0, 4.16, -0.08), 0.18, 0.40, SKIN, rot=(-6, 0, 0), sides=10)
    k.hull(ut, clip(ring(4.02, 0, -0.04, 0.78, 0.58), *ZG(-0.06)) + clip(ring(4.26, 0, -0.02, 0.60, 0.46), *ZG(-0.02)), "canvas")
    # pañuelo negro: vuelta al cuello y punta sobre el pecho
    k.cyl(ut, (0, 4.08, -0.08), 0.215, 0.14, "cloth_black", rot=(-8, 0, 0), sides=10)
    k.hull(ut, [(-0.15, 4.08, -0.27), (0.15, 4.08, -0.27), (0, 4.04, -0.33), (-0.10, 3.94, -0.33), (0.10, 3.94, -0.33),
                (0, 3.74, -0.40), (0, 3.80, -0.33), (-0.08, 3.96, -0.24), (0.08, 3.96, -0.24)], "cloth_black")
    # cartuchera: del hombro izquierdo a la cadera derecha, por encima del chaleco y debajo del guardapolvo
    band = [(-0.34, 4.00), (-0.08, 3.56), (0.20, 3.18), (0.46, 2.88)]   # curva suave: tramos no colineales
    strap(k, ut, UT_LV, band, 0.15, 0.045, G_VEST, "leather")
    for x, y, ang in along(band, 0.105):
        if abs(x) < coat_edge(y) - 0.05:
            z = surf_z(UT_LV, x, y, G_VEST) - 0.045
            k.box(ut, (x, y, z + 0.01), (0.05, 0.12, 0.09), "brass", rot=(0, 0, ang), detail=True)

    # ---------------- LowerTorso: pantalón, cinto con funda, faldón del guardapolvo ----------------
    lt = k.part("LowerTorso", (0, HIP, 0))
    k.hull(lt, layer(LT_LV, 0), "cloth_blue")
    belt_rot = (0, 0, -5)
    belt = layer([(2.72, 0, 0.0, 1.05, 0.575), (2.86, 0, 0.0, 1.035, 0.567)], 0.05)
    k.hull(lt, about(belt, (0, 2.79, 0), belt_rot), "leather")
    zb = surf_z(LT_LV, 0, 2.79, 0.05)
    k.box(lt, (0.0, 2.79, zb - 0.015), (0.17, 0.13, 0.05), "brass", rot=belt_rot, detail=True)
    k.box(lt, (0.0, 2.79, zb - 0.035), (0.08, 0.05, 0.03), "leather", rot=belt_rot, detail=True)
    # funda en la cadera derecha (+X), colgada del cinto
    k.hull(lt, [(x, y, z) for x, y, z in ((0.60, 2.74, -0.20), (0.75, 2.74, -0.20), (0.60, 2.74, 0.02), (0.75, 2.74, 0.02),
                                          (0.63, 2.02, -0.14), (0.73, 2.02, -0.14), (0.63, 2.02, -0.04), (0.73, 2.02, -0.04))],
           "leather")
    k.hull(lt, mk.pts_box((0.60, 2.74, -0.09), (0.14, 0.26, 0.16)), "leather")              # presilla al cinto
    # faldón del guardapolvo: atrás entero; adelante solo a la izquierda (a la derecha va recogido atrás de la funda)
    k.hull(lt, layer(LT_LV, lambda y: 0.122 + 0.06 * (2.94 - y) / 0.64, [ZG(0.06)]), "canvas")
    k.hull(lt, layer(LT_LV, lambda y: 0.11 + 0.06 * (2.94 - y) / 0.64, [XL(-0.40), ZL(0.08)]), "canvas")
    # bolsillo con tapa en el faldón izquierdo
    k.hull(lt, [(x, y, surf_z(LT_LV, x, y, 0.136) + dz) for x in (-0.62, -0.44) for y in (2.60, 2.72)
                for dz in (0.03, -0.035)], "canvas")

    # ---------------- Head: cara larga curtida, nariz ganchuda, bigote caído, barba corta ----------------
    hd = k.part("Head", NECK_P)
    skull = [(4.24, -0.33, 0.40, 0.40), (4.40, -0.27, 0.70, 0.78), (4.62, -0.25, 0.84, 0.90),
             (4.86, -0.25, 0.90, 0.94), (5.06, -0.24, 0.82, 0.88), (5.18, -0.23, 0.54, 0.60)]
    k.hull(hd, head([p for y, cz, w, d in skull for p in round_ring(y, 0, cz, w, d)]), SKIN)
    # ceja pesada que sigue la curva de la frente (una caja plana sacaba las puntas 0,19 en las sienes)
    brow = [(0.0, -0.755), (0.20, -0.715), (0.36, -0.575)]
    k.hull(hd, head([(sx * x, y, z + dz) for sx in (-1, 1) for x, z in brow
                     for y, dz in ((4.80, 0.0), (4.93, 0.04), (4.87, 0.16))]), SKIN)
    k.hull(hd, head([(0, 4.86, -0.70), (-0.06, 4.80, -0.70), (0.06, 4.80, -0.70), (0, 4.71, -0.87),
                     (0, 4.61, -0.93), (0, 4.53, -0.86), (-0.11, 4.57, -0.72), (0.11, 4.57, -0.72),
                     (-0.08, 4.52, -0.75), (0.08, 4.52, -0.75), (0, 4.51, -0.77)]), SKIN)               # nariz ganchuda
    for s in (-1, 1):
        k.hull(hd, head([(s * 0.20, 4.67, -0.64), (s * 0.36, 4.66, -0.52), (s * 0.29, 4.57, -0.62),
                         (s * 0.35, 4.60, -0.42), (s * 0.29, 4.73, -0.55)]), SKIN)                   # pómulos
        k.hull(hd, head(mk.pts_box((s * 0.455, 4.65, -0.19), (0.08, 0.21, 0.15), rot=(0, s * -14, 0), top=(1, 0.75))), SKIN)  # orejas
        # cejas grises tupidas, caídas hacia afuera
        k.hull(hd, head([(s * 0.06, 4.89, -0.79), (s * 0.06, 4.94, -0.77), (s * 0.24, 4.93, -0.75), (s * 0.24, 4.87, -0.77),
                         (s * 0.39, 4.83, -0.60), (s * 0.38, 4.88, -0.60), (s * 0.06, 4.91, -0.70), (s * 0.30, 4.90, -0.62)]),
               "hair_grey")
        # bigote: ala debajo de la nariz y la punta larga que cae al costado del mentón, 0,16 por delante de la barba
        k.hull(hd, head([(s * 0.02, 4.56, -0.86), (s * 0.02, 4.465, -0.86), (s * 0.18, 4.545, -0.82),
                         (s * 0.18, 4.47, -0.81), (s * 0.17, 4.53, -0.64), (s * 0.02, 4.54, -0.68)]), "hair_grey")
        k.hull(hd, head([(s * 0.12, 4.55, -0.83), (s * 0.26, 4.52, -0.75), (s * 0.26, 4.50, -0.62), (s * 0.30, 4.22, -0.66),
                         (s * 0.23, 4.18, -0.73), (s * 0.18, 4.27, -0.78), (s * 0.12, 4.46, -0.85)]), "hair_grey")
    # barba corta pegada a la mandíbula: deja la boca, las mejillas y las puntas del bigote adelante
    k.hull(hd, head([(sx * x, y, z) for sx in (-1, 1) for x, y, z in
                     ((0.40, 4.58, -0.16), (0.41, 4.50, -0.36), (0.33, 4.41, -0.55), (0.18, 4.37, -0.68), (0.07, 4.37, -0.71),
                      (0.14, 4.18, -0.62), (0.28, 4.24, -0.46), (0.34, 4.30, -0.16))]
                    + [(0, 4.36, -0.72), (0, 4.12, -0.64), (0, 4.16, -0.30)]), "hair_grey")
    k.hull(hd, head([(-0.10, 4.415, -0.74), (0.10, 4.415, -0.74), (-0.08, 4.365, -0.75), (0.08, 4.365, -0.75),
                     (0, 4.41, -0.62), (0, 4.36, -0.64)]), SKIN)                                    # labio de abajo
    # pelo gris: atrás hasta el cuello, costados (tapa la parte de arriba de las orejas) y la coronilla
    k.hull(hd, head([(sx * x, y, z) for sx in (-1, 1) for x, y, z in
                     ((0.45, 5.04, -0.10), (0.47, 4.74, -0.02), (0.44, 4.48, 0.06), (0.36, 4.22, 0.14), (0.20, 4.16, 0.20),
                      (0.28, 5.08, 0.22), (0.30, 4.50, 0.25))]
                    + [(0, 4.16, 0.22), (0, 5.12, 0.25), (0, 4.70, 0.29)]), "hair_grey")
    k.hull(hd, head(round_ring(5.02, 0, -0.18, 0.94, 0.86) + round_ring(5.21, 0, -0.21, 0.56, 0.60)), "hair_grey")
    # huecos: cuencas hondas bajo la ceja, boca entre bigote y barba, arrugas del entrecejo
    for s in (-1, 1):
        k.carve(hd, SKIN_DK, head(mk.pts_ball((s * 0.19, 4.725, -0.71), 0.12, scale=(1.1, 0.62, 0.8), subdiv=0)))
        k.carve(hd, SKIN_DK, head(mk.pts_box((s * 0.045, 4.85, -0.77), (0.03, 0.10, 0.10), rot=(0, 0, s * 8))))
    k.carve(hd, "hair_dark", head(mk.pts_box((0, 4.44, -0.76), (0.30, 0.04, 0.26))))
    # párpados de detalle: la mirada entrecerrada de viejo (cálida, no de muerto)
    for s in (-1, 1):
        k.hull(hd, head([(s * 0.09, 4.785, -0.665), (s * 0.29, 4.785, -0.615), (s * 0.19, 4.80, -0.70),
                         (s * 0.10, 4.758, -0.675), (s * 0.28, 4.758, -0.635), (s * 0.19, 4.752, -0.705),
                         (s * 0.19, 4.79, -0.60)]), SKIN, detail=True)

    eyes = k.part("Eyes", NECK_P)
    for s in (-1, 1):
        k.ball(eyes, hp((s * 0.19, 4.72, -0.625)), 0.07, "bone", scale=(1.25, 0.7, 0.5), subdiv=0)      # blanco
        k.ball(eyes, hp((s * 0.18, 4.72, -0.655)), 0.05, "hair_dark", scale=(1.0, 1.0, 0.6), subdiv=0)   # iris oscuro

    # ---------------- Acc_Hat: ala ancha (1,8), copa abollada con pliegue, ala izquierda levantada ----------------
    hb = (0, 5.00, -0.24)
    hat = k.part("Acc_Hat", hp(hb))

    def hat_pts(pts):
        return head(about(pts, hb, (-3, 0, 0)))

    brim = [(0.90 * math.cos(a), 0, -0.24 + 0.84 * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
    brim2 = lambda y, pl: [(x, y, z) for x, _, z in clip(brim, *pl)]  # noqa: E731
    k.hull(hat, hat_pts([p for y in (4.99, 5.04) for p in clip(brim2(y, XG(-0.46)), *XL(0.46))]), "canvas")
    k.hull(hat, hat_pts(about([p for y in (4.99, 5.04) for p in brim2(y, XL(-0.40))], (-0.40, 5.02, -0.24), (0, 0, -24))), "canvas")
    k.hull(hat, hat_pts(about([p for y in (4.99, 5.04) for p in brim2(y, XG(0.40))], (0.40, 5.02, -0.24), (0, 0, 9))), "canvas")
    crown_b = round_ring(5.02, 0, -0.24, 0.92, 1.00, n=12)
    crown_t = round_ring(5.50, 0, -0.22, 0.74, 0.78, n=12)
    for s in (-1, 1):
        top = clip(crown_t, s, 0, -0.05)
        if s > 0:   # abolladura: la copa hundida adelante a la derecha
            top = [(x * 0.86, y - 0.09, z) if z < -0.30 else (x, y, z) for x, y, z in top]
        half = [(x * (1 - 0.01 * (s > 0)), y + 0.006 * (s > 0), -0.24 + (z + 0.24) * (1 - 0.01 * (s > 0)))
                for x, y, z in clip(crown_b, s, 0, 0.02)] + top
        k.hull(hat, hat_pts(half + [(s * 0.004, 5.46, -0.585), (s * 0.004, 5.46, 0.10)]), "canvas")
    k.hull(hat, hat_pts(round_ring(5.03, 0, -0.24, 0.98, 1.06, n=12) + round_ring(5.14, 0, -0.24, 0.96, 1.04, n=12)), "leather")

    # ---------------- brazos: manga del guardapolvo arremangada, antebrazo curtido, mitones ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)
        ua = k.part(f"{side}UpperArm", sh)
        k.limb(ua, (sh[0], sh[1] + 0.10, ARM_Z), (el[0], el[1] + 0.14, ARM_Z), 0.44, 0.46, 0.38, 0.40, "canvas")
        k.hull(ua, ring(3.23, el[0] - s * 0.005, ARM_Z, 0.47, 0.48) + ring(3.06, el[0], ARM_Z, 0.49, 0.50), "canvas")   # vuelta de lona
        k.hull(ua, ring(3.08, el[0], ARM_Z, 0.43, 0.44) + ring(2.93, el[0] + s * 0.005, ARM_Z, 0.43, 0.44), "cloth_red")  # vuelta de la camisa
        la = k.part(f"{side}LowerArm", el)
        k.limb(la, el, wr, 0.31, 0.31, 0.25, 0.26, SKIN)
        hn = k.part(f"{side}Hand", wr)
        hand(k, hn, s, SKIN, glove="leather_dark", fingerless=True)

    # Acc_BiteWound: trapo de lona atado sobre la mordida del antebrazo izquierdo (oculto hasta la mordida)
    el = (-EL_X, ELBOW, ARM_Z)
    bw = k.part("Acc_BiteWound", el)
    cx = -EL_X - 0.12 * (ELBOW - 2.60) / (ELBOW - WRIST)
    k.hull(bw, ring(2.71, cx + 0.005, ARM_Z, 0.355, 0.355) + ring(2.49, cx - 0.005, ARM_Z, 0.345, 0.345), "canvas")
    for dz, h in ((-0.115, 0.15), (0.0, 0.11), (0.115, 0.17)):
        k.prism(bw, [(-0.05, 0), (0.05, 0), (0.0, -h)], 0.03, "canvas", plane="zy",
                center=(cx - 0.16, 2.50, ARM_Z + dz), detail=True)
    k.carve(bw, "blood_dry", mk.pts_box((cx - 0.05, 2.60, ARM_Z - 0.18), (0.12, 0.07, 0.08), rot=(0, 0, 25)))
    k.paint(bw, "blood_dry", ball=((cx - 0.10, 2.56, ARM_Z - 0.14), 0.12))

    # Acc_HanksWidow: niquelado con cachas de hueso, boca abajo en la funda; asoman cacha y cilindro
    gx = 0.675
    gun = k.part("Acc_HanksWidow", (gx, 3.05, 0.03))
    k.cyl(gun, (gx, 2.82, -0.10), 0.085, 0.17, "steel_light", sides=6, rot=(8, 0, 0))
    k.box(gun, (gx, 2.94, -0.07), (0.10, 0.10, 0.22), "steel_light")
    k.box(gun, (gx, 2.995, 0.05), (0.045, 0.11, 0.06), "gunmetal", rot=(-35, 0, 0))
    k.hull(gun, [(gx + dx, y, z) for dx in (-0.045, 0.045) for y, z in
                 ((2.95, -0.13), (2.95, 0.03), (3.12, 0.04), (3.17, 0.10), (3.15, 0.17), (3.04, 0.15))], "bone")
    k.hull(gun, [(gx + dx, y, z) for dx in (-0.055, 0.055) for y, z in
                 ((3.07, 0.02), (3.12, 0.03), (3.10, 0.17), (3.05, 0.16))], "cloth_black")             # moño negro
    for dz in (0.03, 0.12):
        k.box(gun, (gx + 0.06, 2.98, dz), (0.025, 0.22, 0.045), "cloth_black", rot=(0, 0, 4), detail=True)

    # ---------------- piernas: pantalón azul, faldón partido en la cadera, botas altas con espuelas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = k.part(f"{side}UpperLeg", hip)
        k.limb(ul, hip, knee, 0.52, 0.54, 0.42, 0.44, "cloth_blue")
        coat_lv = [(2.50, s * 0.30, 0.0, 0.50, 0.52), (1.86, s * 0.31, 0.02, 0.46, 0.50)]
        g = lambda y: 0.10 if y > 2 else 0.17  # noqa: E731
        k.hull(ul, layer(coat_lv, lambda y: g(y) + 0.012, [(s, 0, -0.01), ZG(0.045)]), "canvas")
        if side == "Left":
            k.hull(ul, layer(coat_lv, g, [(s, 0, -0.42), ZL(0.095)]), "canvas")
        ll = k.part(f"{side}LowerLeg", knee)
        k.limb(ll, knee, (hip[0], 1.05, 0), 0.42, 0.44, 0.36, 0.38, "cloth_blue")
        k.hull(ll, ring(1.18, hip[0], 0, 0.44, 0.46) + ring(0.22, hip[0], 0.0, 0.38, 0.40), "leather_dark")      # caña
        k.hull(ll, ring(1.12, hip[0], 0, 0.47, 0.49) + ring(1.27, hip[0], -0.01, 0.53, 0.55), "leather_dark")    # boca de la caña
        ft = k.part(f"{side}Foot", ankle)
        x0 = hip[0]
        k.hull(ft, [(x0 + sx * dx, y, z) for sx in (-1, 1) for dx, y, z in
                    ((0.15, 0.10, 0.20), (0.15, 0.36, 0.16), (0.16, 0.32, -0.10), (0.15, 0.10, -0.30),
                     (0.07, 0.08, -0.54), (0.06, 0.18, -0.50))], "leather_dark")
        k.hull(ft, [(x0 + sx * dx, y, z) for sx in (-1, 1) for dx, y, z in
                    ((0.16, 0.0, -0.28), (0.16, 0.10, -0.28), (0.08, 0.0, -0.56), (0.08, 0.09, -0.56))], "hair_dark")   # suela
        k.hull(ft, [(x0 + sx * 0.13, y, z) for sx in (-1, 1) for y, z in
                    ((0.0, 0.05), (0.0, 0.21), (0.12, 0.04), (0.12, 0.22))], "hair_dark")                 # taco
        k.box(ft, (x0, 0.17, 0.27), (0.04, 0.035, 0.16), "steel_light")                                # espuela
        k.cyl(ft, (x0, 0.16, 0.36), 0.075, 0.03, "steel_light", axis="x", sides=8)

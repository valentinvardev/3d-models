"""
Receta de WST_NPC_Peddler, el buhonero (prompt 049, Bloques A + D). Vivo, excéntrico y teatral.

Brief
- Silueta a 40 studs: galera negra altísima (copa 1,1) torcida, con pluma roja; levita marrón larga con
  faldones hasta arriba de las rodillas y tres parches cuadrados mostaza y turquesa; flaco; la botella
  verde de tónico en la mano derecha. Teatral: mentón arriba, una ceja levantada, sonrisa pícara, pera gris
  en punta.
- Medidas: H = 5,3 (espacio de referencia H = 5,2 escalado por K = 5,3 / 5,2). Torso 10 % más angosto
  que el de referencia. La copa de la galera mide 1,1 de verdad (se divide por K).
- Piezas: las 15 de R15 con el origen en su articulación, Eyes (origen en el cuello), Acc_Hat (origen en
  la base de la galera), Acc_Bottle (origen donde cierra la mano derecha).
- Capas: camisa, chaleco (+0,04), levita (+0,08). Faldones partidos en la cadera: LowerTorso (costados
  y atrás) y un paño atrás en cada UpperLeg.
- Inferido: chaleco mostaza cerrado; bigote fino unido a la pera (barba "Van Dyke", teatral); pelo gris
  largo y desordenado asomando bajo la galera; vueltas de los puños en turquesa (el forro); mitones de
  cuero; banda mostaza en la galera; pluma roja; etiqueta crema y corcho en la botella; parches: pecho
  izquierdo (mostaza), adelante abajo a la derecha (turquesa) y en la espalda (mostaza).

Vueltas: 1) primera versión · 2) parches con grilla de 3x3 puntos y 0,032 por fuera (la levita convexa
partía el parche turquesa en dos barritas), mechones de pelo con la raíz adentro del casquete (flotaban).

Revisión
- 2338 triángulos contra 1800 de referencia (+30 %, calidad primero): galera en dos tramos (la de arriba
  torcida 9°) con abolladura, pluma y banda; cara con pera, bigote, cejas tupidas y mechones; levita con
  solapas anchas y tres parches; botella con hombro, cuello, corcho y etiqueta.
- Alto 5,3 a la cabeza, 6,32 con la galera (copa de 1,1 reales).
- 15 colores en total (13 en el cuerpo): el prompt ya nombra 11.
"""

import math

from mathutils import Euler, Vector

# parámetros de este NPC
H = 5.3
SH_X, EL_X, WR_X = 0.76, 0.88, 1.00
ARM_Z = -0.03
HEAD_FWD, HEAD_TILT = 0.04, 5.0

# =============== base común de los NPC (la misma en todas las recetas del lote; sale de Old Hank) ===============
# Se construye en el espacio de referencia de H = 5,2 (articulaciones del Bloque D, las de humanoid.py) y
# Ref escala cada punto por K = H / 5,2 al pasarlo a modelkit.
K = H / 5.2
ANKLE, KNEE, HIP, WAIST = 0.26, 1.30, 2.444, 2.86
ELBOW, WRIST, SHOULDER, NECK = 3.016, 2.184, 3.952, 4.16
LEG_X = 0.30
NECK_P = (0.0, NECK, -0.06)


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
    """Espacio de la cabeza: adelantada HEAD_FWD y girada HEAD_TILT alrededor del cuello (actitud)."""
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
    """Capa de ropa: los niveles (y, cx, cz, w, d) crecidos g y recortados por planos. Cada capa termina
    0,3·g más allá que la de abajo para que las tapas no queden coplanares (medido con Old Hank)."""
    pts = []
    levels = sorted(levels)
    for i, (y, cx, cz, w, d) in enumerate(levels):
        gg = g(y) if callable(g) else g
        y += -0.3 * gg if i == 0 else 0.3 * gg if i == len(levels) - 1 else 0.0
        poly = ring(y, cx, cz, w + 2 * gg, d + 2 * gg)
        for pl in (planes(y) if callable(planes) else planes):
            poly = clip(poly, *pl)
        pts += poly
    return pts


def surf_z(levels, x, y, g=0.0):
    """z del frente de la capa g en (x, y): para apoyar tiras, botones y bolsillos."""
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


def lv_at(levels, y):
    """Nivel interpolado a la altura y."""
    lv = sorted(levels)
    for l0, l1 in zip(lv, lv[1:]):
        if l0[0] <= y <= l1[0]:
            t = (y - l0[0]) / (l1[0] - l0[0]) if l1[0] > l0[0] else 0
            return tuple(l0[j] + t * (l1[j] - l0[j]) for j in range(5))
    return lv[0] if y < lv[0][0] else lv[-1]


def lv_range(levels, y0, y1):
    """Los niveles entre y0 y y1, con los extremos interpolados (capas que no cubren todo el tramo)."""
    return [lv_at(levels, y0)] + [l for l in sorted(levels) if y0 < l[0] < y1] + [lv_at(levels, y1)]


def surf_back(levels, x, y, g=0.0):
    """z de la espalda de la capa g en (x, y)."""
    return -surf_z([(l[0], l[1], -l[2], l[3], l[4]) for l in levels], x, y, g)


class Ref:
    """modelkit en el espacio de referencia (H = 5,2): cada punto se escala por K al pasar."""

    def __init__(self, mk, k=None):
        self.mk, self.k = mk, (K if k is None else k)

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

    def carve_prism(self, part, mat, profile, depth, center, rot=(0, 0, 0)):
        k = self.k
        self.mk.carve(part, mat, prism=dict(profile=[(a * k, b * k) for a, b in profile], depth=depth * k,
                                            plane="xy", center=self.P(center), rot=rot))

    def paint(self, part, mat, ball=None, box=None):
        if ball is not None:
            self.mk.paint(part, mat, ball=(self.P(ball[0]), ball[1] * self.k))
        else:
            self.mk.paint(part, mat, box=(self.P(box[0]), tuple(s * self.k for s in box[1])))

    def slice(self, part, point, normal):
        self.mk.slice(part, self.P(point), normal)


def strap(k, part, levels, path, width, thick, g, mat, inset=0.03, ext=0.03, detail=False, back=False):
    """Tira (correa, tirador, cadena) apoyada en la capa g por los puntos (x, y) de path. Los tramos
    vecinos tienen que doblar más de 3°: si son colineales, sus costados quedan coplanares en el solape."""
    base_thick, base_inset = thick, inset
    for i, ((xa, ya), (xb, yb)) in enumerate(zip(path, path[1:])):
        # tramos alternados 0,004 más gruesos: sobre una zona plana del pecho, dos tramos que se solapan
        # quedan con el frente coplanar aunque doblen (medido con el almacenero)
        thick, inset = base_thick + 0.004 * (i % 2), base_inset + 0.004 * (i % 2)
        dx, dy = xb - xa, yb - ya
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        px, py = -uy * width / 2, ux * width / 2
        pts = []
        for x, y in ((xa - ux * ext, ya - uy * ext), (xb + ux * ext, yb + uy * ext)):
            for sg in (-1, 1):
                qx, qy = x + sg * px, y + sg * py
                if back:
                    z = surf_back(levels, qx, qy, g)
                    pts += [(qx, qy, z - inset), (qx, qy, z + thick)]
                else:
                    z = surf_z(levels, qx, qy, g)
                    pts += [(qx, qy, z + inset), (qx, qy, z - thick)]
        k.hull(part, pts, mat, detail=detail)


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


def arm_joints(s):
    return (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)


def arm_x(s, y):
    """x del eje del brazo a la altura y (hombro-codo-muñeca, abiertos 8°)."""
    if y >= ELBOW:
        return s * (SH_X + (EL_X - SH_X) * (SHOULDER - y) / (SHOULDER - ELBOW))
    return s * (EL_X + (WR_X - EL_X) * (ELBOW - y) / (ELBOW - WRIST))


def band(k, part, s, y0, y1, w, mat, d=None, detail=False):
    """Anillo alrededor del brazo entre y0 y y1 (puño, liga, vuelta de manga, vendaje)."""
    k.hull(part, ring(y0, arm_x(s, y0), ARM_Z, w, d or w) + ring(y1, arm_x(s, y1), ARM_Z, w, d or w), mat, detail=detail)


def hand(k, part, s, skin, glove=None, fingerless=False, size=1.0, tips=None):
    """Mano grande de mitón con pulgar (Bloque D); con guante, y sin dedos si fingerless; tips pinta los
    dedos (manchas de aceite u hollín) después de cortar la banda con slice (sin cortar, tiñe caras enteras)."""
    wx = s * WR_X + s * 0.02
    mat = glove or skin
    q = size
    k.hull(part, round_ring(WRIST + 0.05, wx, ARM_Z, 0.21 * q, 0.35 * q) + round_ring(WRIST - 0.20 * q, wx + s * 0.01, ARM_Z, 0.23 * q, 0.38 * q)
           + round_ring(WRIST - 0.47 * q, wx + s * 0.02, ARM_Z, 0.18 * q, 0.30 * q), mat)
    k.box(part, (wx - s * 0.07 * q, WRIST - 0.15 * q, ARM_Z - 0.19 * q), (0.10 * q, 0.23 * q, 0.11 * q), mat, rot=(-15, 0, 0))
    if glove and fingerless:
        k.slice(part, (0, WRIST - 0.30 * q, 0), (0, 1, 0))
        k.paint(part, skin, box=((wx, WRIST - 0.42 * q, ARM_Z), (0.5, 0.24 * q, 0.6)))
    if tips and not glove:
        k.slice(part, (0, WRIST - 0.33 * q, 0), (0, 1, 0))
        k.paint(part, tips, box=((wx, WRIST - 0.44 * q, ARM_Z), (0.5, 0.22 * q, 0.6)))
    if glove:   # puño del guante: tapa la muñeca
        k.hull(part, ring(WRIST + 0.10, wx - s * 0.01, ARM_Z, 0.28 * q, 0.36 * q) + ring(WRIST - 0.06, wx, ARM_Z, 0.28 * q, 0.40 * q), glove)


def shoe(k, ft, x0, mat, sole, kind="shoe"):
    """Pie (Bloque D: 1,2x): "shoe" zapato bajo, "boot" bota de trabajo de punta redonda, "cowboy" con taco."""
    if kind == "cowboy":
        prof = ((0.15, 0.10, 0.20), (0.15, 0.36, 0.16), (0.16, 0.32, -0.10), (0.15, 0.10, -0.30), (0.07, 0.08, -0.54), (0.06, 0.18, -0.50))
    elif kind == "boot":
        prof = ((0.17, 0.06, 0.20), (0.17, 0.40, 0.18), (0.18, 0.30, -0.12), (0.18, 0.06, -0.36), (0.13, 0.06, -0.52), (0.12, 0.22, -0.48))
    else:
        prof = ((0.15, 0.06, 0.18), (0.14, 0.32, 0.14), (0.15, 0.26, -0.10), (0.16, 0.06, -0.34), (0.11, 0.06, -0.50), (0.10, 0.17, -0.46))
    k.hull(ft, [(x0 + sx * dx, y, z) for sx in (-1, 1) for dx, y, z in prof], mat)
    if kind == "cowboy":
        k.hull(ft, [(x0 + sx * dx, y, z) for sx in (-1, 1) for dx, y, z in
                    ((0.16, 0.0, -0.28), (0.16, 0.10, -0.28), (0.08, 0.0, -0.56), (0.08, 0.09, -0.56))], sole)
        k.hull(ft, [(x0 + sx * 0.13, y, z) for sx in (-1, 1) for y, z in ((0.0, 0.05), (0.0, 0.21), (0.12, 0.04), (0.12, 0.22))], sole)
    else:
        w = 0.185 if kind == "boot" else 0.165
        k.hull(ft, [(x0 + sx * w, y, z) for sx in (-1, 1) for y, z in ((0.0, 0.21), (0.075, 0.21), (0.0, -0.53), (0.075, -0.53))]
               + [(x0 + sx * (w - 0.05), y, -0.555) for sx in (-1, 1) for y in (0.0, 0.07)], sole)


# ---------------- cara viva ----------------
NOSES = {
    "straight": [(0, 4.86, -0.70), (-0.06, 4.80, -0.69), (0.06, 4.80, -0.69), (0, 4.62, -0.86), (0, 4.55, -0.84),
                 (-0.10, 4.57, -0.72), (0.10, 4.57, -0.72), (-0.07, 4.53, -0.74), (0.07, 4.53, -0.74), (0, 4.52, -0.76)],
    "button": [(0, 4.80, -0.70), (-0.05, 4.78, -0.70), (0.05, 4.78, -0.70), (0, 4.63, -0.82), (0, 4.56, -0.81),
               (-0.06, 4.64, -0.80), (0.06, 4.64, -0.80), (-0.11, 4.58, -0.72), (0.11, 4.58, -0.72),
               (-0.08, 4.54, -0.74), (0.08, 4.54, -0.74), (0, 4.53, -0.75)],
    "long": [(0, 4.86, -0.70), (-0.05, 4.80, -0.69), (0.05, 4.80, -0.69), (0, 4.58, -0.89), (0, 4.52, -0.84),
             (-0.08, 4.55, -0.72), (0.08, 4.55, -0.72), (-0.06, 4.51, -0.74), (0.06, 4.51, -0.74), (0, 4.50, -0.76)],
    "broad": [(0, 4.84, -0.70), (-0.07, 4.80, -0.70), (0.07, 4.80, -0.70), (0, 4.63, -0.85), (0, 4.55, -0.84),
              (-0.13, 4.57, -0.72), (0.13, 4.57, -0.72), (-0.10, 4.52, -0.75), (0.10, 4.52, -0.75), (0, 4.52, -0.77)],
}


def face(k, mk, hd, skin, skin_dk, nose="straight", nose_dz=0.0, brow_front=-0.755, brow_half=0.36, ear=(0.455, 4.65, -0.19),
         cheeks=True, cheek_dz=0.0):
    """Ceja (sigue la curva de la frente: una caja plana saca las puntas en las sienes), nariz, pómulos y orejas."""
    pts = [(0.0, brow_front), (0.20, brow_front + 0.04), (brow_half, brow_front + 0.18)]
    k.hull(hd, head([(sx * x, y, z + dz) for sx in (-1, 1) for x, z in pts
                     for y, dz in ((4.80, 0.0), (4.93, 0.04), (4.87, 0.16))]), skin)
    k.hull(hd, head([(x, y, z + nose_dz) for x, y, z in NOSES[nose]]), skin)
    for s in (-1, 1):
        if cheeks:
            k.hull(hd, head([(s * 0.20, 4.67, -0.64 + cheek_dz), (s * 0.36, 4.66, -0.52 + cheek_dz), (s * 0.29, 4.57, -0.62 + cheek_dz),
                             (s * 0.35, 4.60, -0.42), (s * 0.29, 4.73, -0.55 + cheek_dz)]), skin)
        ex, ey, ez = ear
        k.hull(hd, head(mk.pts_box((s * ex, ey, ez), (0.08, 0.21, 0.15), rot=(0, s * -14, 0), top=(1, 0.75))), skin,
               detail=True)   # de detalle: lo que no toca un tallado no entra en la unión de las booleanas (menos triángulos)


def eyes(k, mk, hd, skin, skin_dk, ex=0.19, ey=4.72, ez=-0.625, lid=4.758, iris="hair_dark", look=0.01, socket=0.0,
         size=1.0, gaze=(0.0, 0.0)):
    """Cuencas talladas, párpados de detalle (lid = altura del borde: más alto = más abiertos) y la pieza Eyes
    con blanco e iris (vivos: la mirada se lee; con solo iris oscuro parecían cerrados)."""
    for s in (-1, 1):
        k.carve(hd, skin_dk, head(mk.pts_ball((s * ex, ey + 0.005, ez - 0.085 + socket), 0.12 * size, scale=(1.1, 0.62, 0.8), subdiv=0)))
        k.hull(hd, head([(s * (ex - 0.10), lid + 0.027, ez - 0.04), (s * (ex + 0.10), lid + 0.027, ez + 0.01),
                         (s * ex, lid + 0.042, ez - 0.075), (s * (ex - 0.09), lid, ez - 0.05), (s * (ex + 0.09), lid, ez - 0.01),
                         (s * ex, lid - 0.006, ez - 0.08), (s * ex, lid + 0.032, ez + 0.025)]), skin, detail=True)
    e = k.part("Eyes", NECK_P)
    for s in (-1, 1):
        k.ball(e, hp((s * ex, ey, ez)), 0.07 * size, "bone", scale=(1.25, 0.7, 0.5), subdiv=0)
        k.ball(e, hp((s * (ex - look) + gaze[0], ey + gaze[1], ez - 0.03)), 0.05 * size, iris, scale=(1.0, 1.0, 0.6), subdiv=0)
    return e


def eyebrows(k, hd, mat, inner=(0.06, 4.90), outer=(0.38, 4.86), front=-0.78, thick=0.05, raise_side=None, raise_dy=0.06):
    """Cejas de pelo sobre la ceja de la frente. inner/outer = (x, y) de cada punta; raise_side levanta una."""
    for s in (-1, 1):
        dy = raise_dy if raise_side == s else 0.0
        (xi, yi), (xo, yo) = inner, outer
        k.hull(hd, head([(s * xi, yi + dy, front), (s * xi, yi + thick + dy, front + 0.02),
                         (s * (xi + xo) / 2, (yi + yo) / 2 + 0.025 + dy, front + 0.03), (s * (xi + xo) / 2, (yi + yo) / 2 + 0.025 + thick + dy, front + 0.05),
                         (s * xo, yo + dy, front + 0.18), (s * xo, yo + thick * 0.8 + dy, front + 0.18),
                         (s * xi, yi + thick / 2 + dy, front + 0.09), (s * (xo - 0.06), yo + thick / 2 + dy, front + 0.22)]), mat,
               detail=True)


def jaw(k, hd, skin, front=-0.71, chin=(4.24, -0.61), w=0.19, jaw_w=0.34):
    """Boca y mentón de cara afeitada: adelanta la zona de la boca sobre el cráneo para que labio y mentón
    salgan de la cara y no queden como bloques sueltos (medido con el telegrafista)."""
    cy, cz = chin
    k.hull(hd, head([(sx * x, y, z) for sx in (-1, 1) for x, y, z in
                     ((0.12, 4.53, front + 0.035), (w, 4.43, front + 0.075), (0.12, cy + 0.05, cz + 0.025),
                      (jaw_w, 4.45, -0.36), (0.20, cy + 0.02, -0.42))]
                    + [(0, 4.53, front), (0, 4.43, front - 0.005), (0, cy, cz)]), skin)


def mouth(k, mk, hd, skin, kind="line", w=0.26, y=4.43, front=-0.76, lip=True, inner="hair_dark"):
    """Boca tallada: "line" cerrada, "smile" sonrisa (comisuras arriba), "open" entreabierta, "grin" mostrando dientes."""
    h = {"line": 0.03, "smile": 0.035, "open": 0.07, "grin": 0.06}[kind]
    up = 0.035 if kind in ("smile", "grin") else 0.0
    prof = [(-w / 2, up), (-w / 4, -h / 2 + 0.005), (w / 4, -h / 2 + 0.005), (w / 2, up), (w / 4, h / 2), (-w / 4, h / 2)]
    if kind in ("smile", "grin"):
        prof = [(-w / 2, up + 0.01), (-w / 3, -h / 2 + 0.01), (0, -h / 2), (w / 3, -h / 2 + 0.01), (w / 2, up + 0.01),
                (w / 3, h / 2 - 0.005), (0, h / 2 - 0.01), (-w / 3, h / 2 - 0.005)]
    k.carve_prism(hd, inner, prof, 0.26, hp((0, y, front)), rot=(HEAD_TILT, 0, 0))
    if kind == "grin":   # fila de dientes de arriba, apoyada en la pared de la boca
        k.hull(hd, head([(x, y + h / 2 - 0.004, z) for x in (-w / 3, w / 3) for z in (front + 0.02, front + 0.10)]
                        + [(x, y - 0.002, z) for x in (-w / 3.4, w / 3.4) for z in (front + 0.025, front + 0.10)]), "bone", detail=True)
    if lip:
        lo = y - h / 2 - 0.005
        k.hull(hd, head([(-w * 0.38, lo, front + 0.02), (w * 0.38, lo, front + 0.02), (-w * 0.30, lo - 0.05, front + 0.01),
                         (w * 0.30, lo - 0.05, front + 0.01), (0, lo, front + 0.14), (0, lo - 0.05, front + 0.12)]), skin)


def specs(k, hd, ex=0.19, ey=4.72, ez=-0.71, r=0.105, lens_cut=None, frame="iron", glass="glass", ear_x=0.43, ear_z=-0.20):
    """Anteojos redondos de alambre en la cabeza: aros, puente y patillas hasta las orejas. El vidrio es
    opaco en Studio (un MeshPart por pieza): solo se pone en la parte que pide lens_cut ("top" = reflejo
    arriba, "bottom" = media luna de lectura) para que los ojos se sigan viendo. Todo de detalle: en la
    base, las booleanas de la cara (use_self) unían y cortaban los aros (medido con el telegrafista)."""
    def arc(r0, r1, a0, a1, n=7):
        angs = [a0 + (a1 - a0) * j / (n - 1) for j in range(n)]
        return [(r1 * math.cos(a), r1 * math.sin(a)) for a in angs] + [(r0 * math.cos(a), r0 * math.sin(a)) for a in reversed(angs)]

    for s in (-1, 1):
        cx = s * ex
        c = hp((cx, ey, ez))
        # aro: dos medias lunas que se solapan en las puntas, de distinta profundidad (no coplanares)
        k.prism(hd, arc(r - 0.024, r, -0.12, math.pi + 0.12), 0.024, frame, plane="xy", center=c, rot=(HEAD_TILT, 0, 0),
                detail=True)
        k.prism(hd, arc(r - 0.024, r, math.pi - 0.12, 2 * math.pi + 0.12), 0.032, frame, plane="xy", center=c, rot=(HEAD_TILT, 0, 0),
                detail=True)
        if lens_cut:
            sg = 1 if lens_cut == "top" else -1
            pts = [(cx + (r - 0.012) * math.cos(a), ey + (r - 0.012) * math.sin(a)) for a in
                   [math.pi * (0.2 + 0.6 * j / 5) * sg for j in range(6)]]
            k.hull(hd, head([(x, y, ez + dz) for x, y in pts for dz in (-0.004, 0.004)]), glass, detail=True)
        k.hull(hd, head([(cx + s * r * 0.98, ey + 0.02, ez + dz) for dz in (-0.012, 0.012)]
                        + [(s * ear_x, ey + 0.05, ear_z + dz) for dz in (-0.012, 0.012)]
                        + [(cx + s * r * 0.98, ey + 0.04, ez), (s * ear_x, ey + 0.07, ear_z)]), frame, detail=True)       # patilla
    k.hull(hd, head([(-ex + r * 0.95, ey + 0.02, ez - 0.01), (ex - r * 0.95, ey + 0.02, ez - 0.01),
                     (-ex + r * 0.95, ey + 0.045, ez - 0.01), (ex - r * 0.95, ey + 0.045, ez - 0.01),
                     (0, ey + 0.035, ez - 0.035)]), frame, detail=True)                                      # puente

# =============== Buhonero ===============
SKIN, SKIN_DK = "skin_a", "skin_b"
UT_LV = [(2.80, 0, 0.00, 0.92, 0.52), (3.30, 0, -0.02, 1.10, 0.60), (3.72, 0, 0.0, 1.26, 0.58),
         (3.98, 0, -0.02, 1.32, 0.42), (4.08, 0, -0.02, 0.58, 0.34)]
LT_LV = [(2.30, 0, 0.0, 0.92, 0.52), (2.62, 0, 0.0, 0.96, 0.54), (2.94, 0, 0.0, 0.92, 0.52)]
G_VEST, G_COAT = 0.04, 0.085


def vest_edge(y):
    return 0.004 if y < 3.46 else 0.004 + 0.15 * (y - 3.46) / 0.62


def coat_edge(y):
    return 0.30 - 0.10 * (y - 2.80) / 1.28


def patch(k, part, levels, g, x, y, size, mat, ang=0.0, back=False):
    """Parche cuadrado cosido sobre la levita, 0,03 por fuera y un poco torcido. Grilla de 3x3 puntos: con
    solo las 4 esquinas, la levita convexa lo atravesaba en el medio (medido)."""
    h = size / 2
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    pts = []
    for dx, dy in [(a, b) for a in (-h, 0, h) for b in (-h, 0, h)]:
        px, py = x + dx * c - dy * s_, y + dx * s_ + dy * c
        if back:
            z = surf_back(levels, px, py, g)
            pts += [(px, py, z - 0.02), (px, py, z + 0.032)]
        else:
            z = surf_z(levels, px, py, g)
            pts += [(px, py, z + 0.02), (px, py, z - 0.032)]
    k.hull(part, pts, mat)


def build(mk):
    k = Ref(mk)
    q = 1.0 / K

    # ---------------- UpperTorso: camisa, chaleco mostaza, levita abierta con parches, corbata, cadena ----------------
    ut = k.part("UpperTorso", (0, WAIST, 0))
    k.hull(ut, layer(UT_LV, 0), "cloth_white")
    for s in (-1, 1):
        k.hull(ut, layer(UT_LV, G_VEST, lambda y, s=s: [(s, 0, -vest_edge(y)), ZL(0.02)]), "paint_mustard")
        k.hull(ut, layer(UT_LV, G_COAT, lambda y, s=s: [(s, 0, -coat_edge(y)), ZL(0.03)]), "cloth_brown")
        e0, e1 = coat_edge(3.96), coat_edge(3.30)
        lap = [(s * (e0 + 0.012), 3.96), (s * (e0 + 0.24), 3.90), (s * (e1 + 0.012), 3.30)]          # solapa ancha
        k.hull(ut, [(x, y, surf_z(UT_LV, x, y, G_COAT) + dz) for x, y in lap for dz in (0.02, -0.035)]
               + [(s * (e1 + 0.12), 3.58, surf_z(UT_LV, s * (e1 + 0.12), 3.58, G_COAT) - 0.035)], "cloth_brown")
    k.hull(ut, layer(UT_LV, G_VEST + 0.012, [ZG(0.0)]), "paint_mustard")
    k.hull(ut, layer(UT_LV, G_COAT + 0.012, [ZG(-0.01)]), "cloth_brown")
    patch(k, ut, UT_LV, G_COAT, -0.44, 3.52, 0.20, "paint_mustard", ang=8)
    patch(k, ut, UT_LV, G_COAT, 0.42, 3.02, 0.18, "paint_teal", ang=-6)
    patch(k, ut, UT_LV, G_COAT + 0.012, -0.22, 3.62, 0.22, "paint_mustard", ang=-10, back=True)
    # cadena del reloj: del botón del medio al bolsillo, colgando
    strap(k, ut, UT_LV, [(0.0, 3.16), (0.12, 3.06), (0.26, 3.12)], 0.035, 0.025, G_VEST, "brass", detail=True)
    k.cyl(ut, (0, 4.15, -0.08), 0.16, 0.40, SKIN, rot=(-4, 0, 0), sides=10)                              # cuello
    k.cyl(ut, (0, 4.07, -0.08), 0.195, 0.16, "cloth_white", rot=(-4, 0, 0), sides=10)                   # cuello alto
    # corbata roja: moño abultado y caída sobre la camisa
    zt = -0.27
    k.ball(ut, (0, 4.00, zt - 0.02), 0.075, "cloth_red", scale=(1.3, 0.9, 0.8), subdiv=1)
    k.hull(ut, [(-0.10, 3.98, zt + 0.01), (0.10, 3.98, zt + 0.01), (-0.07, 3.98, zt - 0.06), (0.07, 3.98, zt - 0.06),
                (-0.12, 3.62, zt - 0.05), (0.12, 3.62, zt - 0.05), (0, 3.56, zt - 0.08), (0, 3.62, zt - 0.01)], "cloth_red")

    # ---------------- LowerTorso: pantalón, faldones de la levita (costados y atrás) ----------------
    lt = k.part("LowerTorso", (0, HIP, 0))
    k.hull(lt, layer(LT_LV, 0), "cloth_blue")
    k.hull(lt, layer(LT_LV, lambda y: 0.09 + 0.05 * (2.94 - y) / 0.64, [ZG(-0.12)]), "cloth_brown")

    # ---------------- Head: cara larga y flaca, pera gris en punta, cejas tupidas, una levantada ----------------
    hd = k.part("Head", NECK_P)
    skull = [(4.22, -0.34, 0.34, 0.38), (4.40, -0.27, 0.66, 0.76), (4.62, -0.25, 0.80, 0.88),
             (4.86, -0.25, 0.84, 0.92), (5.06, -0.24, 0.78, 0.86), (5.18, -0.23, 0.50, 0.56)]
    k.hull(hd, head([p for y, cz, w, d in skull for p in round_ring(y, 0, cz, w, d)]), SKIN)
    face(k, mk, hd, SKIN, SKIN_DK, nose="long", nose_dz=-0.02, brow_front=-0.745, brow_half=0.35, ear=(0.43, 4.65, -0.19),
         cheek_dz=0.03)
    jaw(k, hd, SKIN, front=-0.71, chin=(4.20, -0.62), w=0.18, jaw_w=0.30)
    eyes(k, mk, hd, SKIN, SKIN_DK, ex=0.18, lid=4.76, look=0.0, gaze=(-0.015, 0.0))
    eyebrows(k, hd, "hair_grey", inner=(0.05, 4.90), outer=(0.37, 4.88), front=-0.78, thick=0.065, raise_side=1, raise_dy=0.07)
    mouth(k, mk, hd, SKIN, kind="smile", w=0.22, y=4.42, front=-0.72)
    # pera gris en punta y bigote fino unido
    k.hull(hd, head([(-0.10, 4.37, -0.70), (0.10, 4.37, -0.70), (-0.12, 4.28, -0.62), (0.12, 4.28, -0.62),
                     (0, 4.04, -0.70), (0, 4.10, -0.62), (0, 4.36, -0.73), (-0.06, 4.20, -0.56), (0.06, 4.20, -0.56)]),
           "hair_grey", detail=True)
    for s in (-1, 1):
        k.hull(hd, head([(s * 0.02, 4.525, -0.785), (s * 0.02, 4.48, -0.785), (s * 0.18, 4.50, -0.73), (s * 0.20, 4.46, -0.70),
                         (s * 0.12, 4.42, -0.72), (s * 0.03, 4.50, -0.70), (s * 0.15, 4.47, -0.66)]), "hair_grey", detail=True)
    # pelo gris largo y revuelto asomando bajo la galera
    for s in (-1, 1):
        for dz, dy in ((-0.10, 0.0), (0.03, -0.05), (0.12, -0.02)):
            k.hull(hd, head([(s * 0.33, 5.02, -0.08 + dz), (s * 0.37, 5.02, 0.02 + dz), (s * 0.34, 4.92, -0.06 + dz),
                             (s * 0.54, 4.46 + dy, 0.00 + dz), (s * 0.50, 4.50 + dy, 0.06 + dz)]), "hair_grey", detail=True)
    k.hull(hd, head(round_ring(4.98, 0, -0.16, 0.86, 0.84) + round_ring(5.20, 0, -0.21, 0.56, 0.60)
                    + [(-0.30, 4.48, 0.20), (0.30, 4.48, 0.20), (0, 4.44, 0.25)]), "hair_grey", detail=True)

    # ---------------- Acc_Hat: galera alta abollada y torcida, banda mostaza, pluma roja ----------------
    hb = (0, 5.04, -0.22)
    hat = k.part("Acc_Hat", hp(hb))
    k.hull(hat, head(round_ring(5.03, 0, -0.22, 1.10, 1.06, n=14) + round_ring(5.07, 0, -0.22, 1.10, 1.06, n=14)
                     + [(sx * 0.58, 5.12, -0.22) for sx in (-1, 1)]), "cloth_black")                    # ala con los costados arriba
    ch = 1.1 * q
    low = round_ring(5.04, 0, -0.22, 0.80, 0.82, n=12) + round_ring(5.04 + ch * 0.55, 0, -0.22, 0.82, 0.84, n=12)
    k.hull(hat, head(low), "cloth_black")
    bend = (0, 5.04 + ch * 0.55, -0.22)
    up = about(round_ring(5.04 + ch * 0.53, 0, -0.22, 0.815, 0.835, n=12) + round_ring(5.04 + ch, 0, -0.22, 0.86, 0.86, n=12),
               bend, (0, 0, -9))                                                                          # mitad de arriba torcida
    k.hull(hat, head(up), "cloth_black")
    k.hull(hat, head(round_ring(5.08, 0, -0.22, 0.85, 0.87, n=12) + round_ring(5.20, 0, -0.22, 0.85, 0.87, n=12)), "paint_mustard")
    k.carve(hat, "cloth_black", head(mk.pts_ball((0.40, 5.04 + ch * 0.75, -0.50), 0.16, scale=(1, 1.3, 1), subdiv=0)))  # abolladura
    k.hull(hat, head([(-0.42, 5.12, -0.30), (-0.44, 5.12, -0.18), (-0.40, 5.20, -0.24), (-0.52, 5.62, -0.10),
                      (-0.50, 5.66, -0.02), (-0.47, 5.50, -0.10)]), "cloth_red")                       # pluma

    # ---------------- brazos: mangas de la levita con vuelta turquesa, mitones de cuero ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = arm_joints(s)
        ua = k.part(f"{side}UpperArm", sh)
        k.limb(ua, (sh[0], sh[1] + 0.10, ARM_Z), (el[0], el[1] + 0.05, ARM_Z), 0.40, 0.42, 0.34, 0.36, "cloth_brown")
        la = k.part(f"{side}LowerArm", el)
        k.limb(la, el, wr, 0.33, 0.34, 0.28, 0.29, "cloth_brown")
        k.hull(la, ring(2.44, arm_x(s, 2.44), ARM_Z, 0.34, 0.35) + ring(2.17, arm_x(s, 2.17), ARM_Z, 0.40, 0.41), "paint_teal")  # vuelta
        hn = k.part(f"{side}Hand", wr)
        hand(k, hn, s, SKIN, glove="leather", fingerless=True)

    # Acc_Bottle: botella de tónico verde, parada delante del puño derecho
    gx, gz = WR_X + 0.04, ARM_Z - 0.27
    bt = k.part("Acc_Bottle", (gx, WRIST - 0.24, gz))
    yb = WRIST - 0.30
    k.cyl(bt, (gx, yb, gz), 0.10, 0.32, "glass_green", sides=8)
    k.cyl(bt, (gx, yb + 0.20, gz), 0.098, 0.08, "glass_green", sides=8, top=0.45)                        # hombro
    k.cyl(bt, (gx, yb + 0.30, gz), 0.042, 0.14, "glass_green", sides=8)                                 # cuello
    k.cyl(bt, (gx, yb + 0.385, gz), 0.036, 0.05, "wood_light", sides=8)                                  # corcho
    k.cyl(bt, (gx, yb - 0.02, gz), 0.104, 0.16, "paint_cream", sides=8)                                 # etiqueta

    # ---------------- piernas: pantalón azul, faldones atrás, botas gastadas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)
        ul = k.part(f"{side}UpperLeg", hip)
        k.limb(ul, hip, knee, 0.46, 0.48, 0.38, 0.40, "cloth_blue")
        tails = [(2.48, s * 0.30, 0.0, 0.46, 0.48), (1.42, s * 0.31, 0.02, 0.40, 0.42)]
        k.hull(ul, layer(tails, lambda y: 0.10 if y > 2 else 0.14, [(s, 0, -0.006), ZG(0.02)]), "cloth_brown")
        ll = k.part(f"{side}LowerLeg", knee)
        k.limb(ll, knee, (hip[0], 0.40, 0), 0.38, 0.40, 0.33, 0.35, "cloth_blue")
        ft = k.part(f"{side}Foot", ankle)
        shoe(k, ft, hip[0], "leather", "hair_dark", kind="boot")

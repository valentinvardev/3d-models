"""
Receta de WST_Canyon_Wall, las paredes modulares del cañón (prompt 085, Bloques A + B).

Brief
- Se ve a caballo desde la ruta (media distancia) y de lejos: silueta y estratos legibles, pocos triángulos
  por área, nada de detalle chico. Silueta: talud a 55° abajo, acantilado en capas que entran y salen, dos
  cornisas grandes y la línea de arriba cortada por un par de torres de roca.
- Medidas: módulo de 32 (X, de -16 a 16) x 30 de alto x 12 de fondo (Z, de 0 a 12; la ruta hacia -Z).
  Origen abajo al centro del borde de la ruta (el pie del talud). Talud de 0 a 8 a 55° (llega a z = 5,6);
  ocho estratos de 2 a 3,5 de alto de y = 7,8 a 30, alternando redrock_dark / redrock / ochre, cada uno
  corrido 0,3-1,0 del de abajo; cornisas de 1,8 (y = 15,5) y 1,7 (y = 24,5). Torres arriba hasta ~31,8.
- Calce: las puntas (x = ±16) tienen el mismo perfil en las tres variantes; el entrante/saliente de cada
  estrato vale 0 en las puntas y varía adentro (hasta ±1,2). Las tres en fila (A en x = 0, B en 32, C en 64) se tocan.
- Construcción: cada estrato es UN prisma de su planta (frente quebrado cada 2,4-4,4, en x propias de cada
  estrato: si caen en las mismas x se lee como pared de ladrillos) extruido en vertical:
  caras verticales facetadas en planta y el techo del estrato de abajo queda como repisa. Los estratos se
  meten 0,05 en el de abajo; las puntas y la espalda de los impares van 0,003 adentro (si no, las caras de
  punta de dos estratos vecinos son coplanares). El talud es un prisma del perfil (55°) con piedras sueltas y grupos de
  tres al pie (1,2 a 3), medio enterradas.
- Variantes: Canyon_Wall_A (recto). Canyon_Wall_B: cárcava al medio (boca de 9 al frente que se cierra a 3
  atrás): cada estrato tiene la muesca más honda que el de abajo, así los techos de los estratos quedan como
  escalones de 1,6 de fondo y 2-3,5 de alto hasta salir por atrás (y ~19); abajo, un cono de derrumbe sobre
  el talud (pendiente ~45°) para que bajen los corredores. Canyon_Wall_C: rincón de 30°: la mitad derecha
  gira 30° hacia la ruta sobre el origen; las fajas se cortan en el encuentro y los dos taludes se meten uno
  en el otro.
- Colisión: con casco convexo el talud y la cárcava quedan tapados por un plano; en Studio estas piezas van
  con PreciseConvexDecomposition.
- Inferido: alturas y colores de cada estrato, alturas de las cornisas, color del talud (ochre), torres,
  piedras del talud, forma y fondo de la cárcava, eje del giro del rincón.

Vueltas: 1) z-fighting entre los dos medios taludes del rincón (mismo piso y techo) · 2) se leía como pared
de ladrillos (quiebres de todos los estratos en las mismas x) y el talud liso · 3) quiebres propios por
estrato (2,4-4,4) y lomos en el talud · 4) los lomos parecían aletas: abanicos más bajos · 5) siguen
artificiales: grupos de piedras · 6) piedras que se hundían 0,22 bajo el piso.

Revisión
- Por módulo contra 1500: A 642, B 718, C 676 (43-48 %, a propósito: pieza grande vista de media distancia,
  "pocos triángulos por área"; la silueta y los estratos no ganan con más).
- Medidas: módulo 32 x 31,8 (con las torres; la corona en 30) x 12. C mide 35,9 x 21,4 en planta por el
  giro. Puntas en x = ±16 con el mismo perfil en las tres (se ve en la fila A-B-C, que se tocan).
- Cornisas de 1,8 (y = 15,5) y 1,7 (y = 24,5); talud de 55° de 0 a 8; cárcava con escalones de 1,6 de
  fondo hasta salir por atrás en y = 15,5 y cono de derrumbe de ~45° adelante.
- Colisión: en Studio, PreciseConvexDecomposition (con casco, el talud y la cárcava quedan tapados).
- Dudoso: las caras verticales de los estratos dan el look de "mesa en capas" (Monument Valley); si se
  quiere más erosión (paredes inclinadas), cada estrato tendría que partirse en dos alturas (+250 por
  módulo).
"""

import math
import random

from mathutils import Vector

W2 = 16.0
DEPTH = 12.0
SCREE_H, SCREE_Z = 8.0, 8.0 / math.tan(math.radians(55))      # 5,6
# (y0, y1, color, z del frente en las puntas)
BANDS = [(7.8, 10.5, "redrock_dark", 5.3), (10.5, 13.5, "redrock", 5.7), (13.5, 15.5, "ochre", 5.4),
         (15.5, 19.0, "redrock", 7.2), (19.0, 21.0, "redrock_dark", 6.9), (21.0, 24.5, "ochre", 7.5),
         (24.5, 27.0, "redrock", 9.2), (27.0, 30.0, "redrock_dark", 8.9)]


def band_xs(j, seed):
    """Quiebres propios de cada estrato (si todos caen en las mismas x, la pared parece de ladrillos)."""
    rnd = random.Random(seed * 7 + j * 31)
    xs, x = [-W2], -W2
    while True:
        x += rnd.uniform(2.4, 4.4)
        if x > W2 - 1.5:
            break
        xs.append(x)
    return xs + [W2]


def front_line(j, seed):
    """Frente de un estrato: (x, z) de punta a punta, con entrante/saliente 0 en las puntas."""
    rnd = random.Random(seed * 101 + j * 17)
    zf = BANDS[j][3]
    xs = band_xs(j, seed)
    return [(x, zf + (0.0 if i in (0, len(xs) - 1) else rnd.uniform(-1.2, 1.2))) for i, x in enumerate(xs)]


def cluster(mk, part, ox, xc, seed, rot=None):
    """Grupo de tres piedras al pie del talud (de 1,2 a 2,6), medio enterradas."""
    rnd = random.Random(seed)
    for k in range(3):
        sz = rnd.uniform(1.2, 2.6)
        x = xc + rnd.uniform(-2.2, 2.2)
        y = max(rnd.uniform(0.4, 1.6), 0.47 * 0.65 * sz + 0.03)     # que no se hunda bajo el piso
        c = (x, y, 0.7 * y - 0.3 * sz)
        if rot is not None:
            c = rot(c)
        rock(mk, part, (ox + c[0], c[1], c[2]), (sz, sz * 0.65, sz * 0.9), seed * 10 + k,
             ("redrock", "redrock_dark", "ochre")[k])


def end_trim(j):
    """Estratos impares: puntas y espalda 0,003 adentro."""
    return 0.003 if j % 2 else 0.0


def band_height(j):
    y0, y1, mat, _ = BANDS[j]
    return (y0 - (0.05 if j > 0 else 0.0)), y1, mat


def prism_xz(mk, part, poly, y0, y1, mat):
    mk.prism(part, poly, y1 - y0, mat, plane="xz", center=(0, (y0 + y1) / 2, 0))


def rock(mk, part, c, size, seed, mat):
    """Piedra facetada: casco de 12 puntos al azar sobre un elipsoide, aplastado abajo."""
    rnd = random.Random(seed)
    pts = []
    for k in range(12):
        a = 2 * math.pi * k / 6 + rnd.uniform(-0.3, 0.3)
        e = (-0.35, 0.45)[k // 6] + rnd.uniform(-0.1, 0.1)
        r = rnd.uniform(0.75, 1.0)
        pts.append((c[0] + size[0] * r * math.cos(a) * math.cos(e), c[1] + size[1] * math.sin(e),
                    c[2] + size[2] * r * math.sin(a) * math.cos(e)))
    pts.append((c[0], c[1] + size[1] * 0.9, c[2]))
    mk.hull(part, pts, mat)


def scree(mk, part, ox, x0, x1, rot=None, lift=0.0):
    """Talud a 55° de x0 a x1 (locales), con el origen del módulo en ox. lift sube el piso y baja el techo
    (los dos medios taludes del rincón no pueden compartir esas caras)."""
    prof = [(lift * 0.7, lift), (SCREE_Z - lift * 0.7, SCREE_H - lift), (DEPTH - 0.006, SCREE_H - lift),
            (DEPTH - 0.006, lift)]
    pts = []
    for x in (x0, x1):
        for z, y in prof:
            pts.append((x, y, z))
    if rot is not None:
        pts = [rot(p) for p in pts]
    mk.hull(part, [(ox + x, y, z) for x, y, z in pts], "ochre")


def towers(mk, part, ox, seed):
    """Dos torres de roca sobre la corona (lejos de las puntas): cortan la línea del horizonte."""
    rnd = random.Random(seed)
    za = BANDS[7][3] + 1.0
    for (xa, xb), h, mat in (((-10.5, -5.0), 1.8, "redrock_dark"), ((3.0, 8.5), 1.1, "redrock")):
        poly = [(ox + xa, za + rnd.uniform(0, 0.6)), (ox + xb, za + rnd.uniform(0, 0.6)),
                (ox + xb - 0.6, DEPTH - 0.4), (ox + xa + 0.4, DEPTH - 0.4)]
        prism_xz(mk, part, poly, 29.95, 30.0 + h, mat)


def build_a(mk, ox):
    p = mk.part("Canyon_Wall_A", (ox, 0, 0))
    for j in range(8):
        y0, y1, mat = band_height(j)
        t = end_trim(j)
        line = front_line(j, 1)
        line[0] = (line[0][0] + t, line[0][1])
        line[-1] = (line[-1][0] - t, line[-1][1])
        poly = [(ox + x, z) for x, z in line] + [(ox + W2 - t, DEPTH - t), (ox - W2 + t, DEPTH - t)]
        prism_xz(mk, p, poly, y0, y1, mat)
    scree(mk, p, ox, -W2 + 0.006, W2 - 0.006)
    cluster(mk, p, ox, -7.5, 11)
    cluster(mk, p, ox, 4.5, 12)
    for k, (x, sz) in enumerate(((-12.0, 2.4), (-3.0, 3.0), (1.0, 1.6), (8.0, 2.2), (13.5, 1.8))):
        y = 1.2 + k % 2 * 2.2
        rock(mk, p, (ox + x, y, y / math.tan(math.radians(55)) - 0.3 * sz), (sz, sz * 0.7, sz), 30 + k,
             "redrock" if k % 2 else "redrock_dark")
    towers(mk, p, ox, 5)


# ---------------------------------------------------------------- B: cárcava
def gully_hw(z):
    """Media anchura de la cárcava a la profundidad z (boca de 9 en z = 4, 3 en z = 12)."""
    return 4.5 - 3.0 * (z - 4.0) / 8.0


def build_b(mk, ox):
    p = mk.part("Canyon_Wall_B", (ox, 0, 0))
    for j in range(8):
        y0, y1, mat = band_height(j)
        t = end_trim(j)
        line = front_line(j, 2)
        line[0] = (line[0][0] + t, line[0][1])
        line[-1] = (line[-1][0] - t, line[-1][1])
        zn = SCREE_Z + 1.6 * (j + 1)                           # fondo de la muesca de este estrato
        zf = BANDS[j][3]
        g = 0.02 * (j % 2)                                      # paredes de estratos vecinos no coplanares
        hw_f = gully_hw(zf) + g
        left = [q for q in line if q[0] < -hw_f - 0.4]
        right = [q for q in line if q[0] > hw_f + 0.4]
        if zn < DEPTH - 0.3:                                    # muesca: el estrato sigue entero atrás
            hw_n = gully_hw(zn) + g
            poly = (left + [(-hw_f, zf), (-hw_n, zn), (hw_n, zn), (hw_f, zf)] + right
                    + [(W2 - t, DEPTH - t), (-W2 + t, DEPTH - t)])
            prism_xz(mk, p, [(ox + x, z) for x, z in poly], y0, y1, mat)
        else:                                                   # atraviesa: dos pedazos
            hw_b = gully_hw(DEPTH) + g
            lp = left + [(-hw_f, zf), (-hw_b, DEPTH - t), (-W2 + t, DEPTH - t)]
            rp = [(hw_f, zf)] + right + [(W2 - t, DEPTH - t), (hw_b, DEPTH - t)]
            prism_xz(mk, p, [(ox + x, z) for x, z in lp], y0, y1, mat)
            prism_xz(mk, p, [(ox + x, z) for x, z in rp], y0, y1, mat)
    scree(mk, p, ox, -W2 + 0.006, W2 - 0.006)
    # cono de derrumbe al pie de la cárcava
    fan = [(0.0, SCREE_H + 0.4, SCREE_Z + 0.9), (-3.2, SCREE_H - 0.2, SCREE_Z + 0.2), (3.0, SCREE_H - 0.2, SCREE_Z + 0.3),
           (-5.2, 0.0, -0.9), (5.0, 0.0, -0.8), (-1.5, 0.0, -2.2), (1.8, 0.0, -2.0), (0.2, 3.5, 1.4),
           (-2.6, 2.0, -0.4), (2.4, 2.4, -0.2)]
    mk.hull(p, [(ox + x, y, z) for x, y, z in fan], "ochre")
    cluster(mk, p, ox, -10.0, 21)
    cluster(mk, p, ox, 10.0, 22)
    for k, (x, sz) in enumerate(((-13.0, 2.4), (-6.5, 2.0), (7.0, 2.8), (13.0, 1.9))):
        y = 1.4 + k % 2 * 2.5
        rock(mk, p, (ox + x, y, y / math.tan(math.radians(55)) - 0.3 * sz), (sz, sz * 0.7, sz), 40 + k,
             "redrock_dark" if k % 2 else "redrock")
    rock(mk, p, (ox - 0.8, 1.2, -1.2), (1.1, 0.8, 1.0), 49, "redrock")                # piedra caída de la cárcava
    rock(mk, p, (ox + 1.6, 0.9, -1.6), (0.9, 0.7, 0.8), 50, "redrock_dark")
    towers(mk, p, ox, 6)


# ---------------------------------------------------------------- C: rincón de 30°
C_ANG = math.radians(30)


def rot_c(p):
    """Gira un punto (x, y, z) del módulo 30° sobre Y (la derecha hacia la ruta)."""
    x, y, z = p
    c, s = math.cos(C_ANG), math.sin(C_ANG)
    return (x * c + z * s, y, -x * s + z * c)


def build_c(mk, ox):
    p = mk.part("Canyon_Wall_C", (ox, 0, 0))
    k = math.tan(C_ANG / 2)                                    # 0,268: el encuentro de las dos mitades
    for j in range(8):
        y0, y1, mat = band_height(j)
        t = end_trim(j)
        line = front_line(j, 3)
        line[0] = (line[0][0] + t, line[0][1])
        line[-1] = (line[-1][0] - t, line[-1][1])
        zf = BANDS[j][3]
        left = [q for q in line if q[0] < -0.5]
        right = [rot_c((x, 0, z)) for x, z in line if x > 0.5]
        right = [(x, z) for x, _, z in right]
        corner = (k * zf, zf)
        back_r = rot_c((W2 - t, 0, DEPTH - t))
        back_c = (k * (DEPTH - t), DEPTH - t)
        poly = left + [corner] + right + [(back_r[0], back_r[2]), back_c, (-W2 + t, DEPTH - t)]
        prism_xz(mk, p, [(ox + x, z) for x, z in poly], y0, y1, mat)
    scree(mk, p, ox, -W2 + 0.006, 6.0)
    scree(mk, p, ox, -6.0, W2 - 0.006, rot=rot_c, lift=0.01)
    cluster(mk, p, ox, -8.0, 31)
    cluster(mk, p, ox, 8.5, 32, rot=rot_c)
    for kk, (x, sz) in enumerate(((-12.0, 2.4), (-3.5, 2.0))):
        y = 1.4 + kk * 2.0
        rock(mk, p, (ox + x, y, y / math.tan(math.radians(55)) - 0.3 * sz), (sz, sz * 0.7, sz), 60 + kk, "redrock")
    for kk, (x, sz) in enumerate(((4.5, 2.2), (12.5, 2.6))):
        y = 2.2 + kk * 1.5
        c = rot_c((x, y, y / math.tan(math.radians(55)) - 0.3 * sz))
        rock(mk, p, (ox + c[0], c[1], c[2]), (sz, sz * 0.7, sz), 70 + kk, "redrock_dark")
    rnd = random.Random(8)
    za = BANDS[7][3] + 1.0
    poly = [(-10.0, za + 0.3), (-4.5, za), (-5.0, DEPTH - 0.4), (-9.6, DEPTH - 0.4)]
    prism_xz(mk, p, [(ox + x, z) for x, z in poly], 29.95, 31.6, "redrock_dark")
    poly = [rot_c((x, 0, z)) for x, z in ((5.0, za + rnd.uniform(0, 0.5)), (10.0, za), (9.6, DEPTH - 0.4), (5.4, DEPTH - 0.4))]
    prism_xz(mk, p, [(ox + x, z) for x, _, z in poly], 29.95, 31.0, "redrock")


def build(mk):
    build_a(mk, 0.0)
    build_b(mk, 32.0)
    build_c(mk, 64.0)

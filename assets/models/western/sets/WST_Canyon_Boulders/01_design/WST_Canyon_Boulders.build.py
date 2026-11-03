"""
Receta de WST_Canyon_Boulders, las rocas sueltas del desierto (prompt 087, Bloques A + B).

Brief
- Relleno del cañón y del desierto: rocas angulosas con la base chata, que se lean como roca de la zona (los
  mismos colores y vetas que el cañón). Silueta: piedra facetada, más ancha que alta, apoyada.
- Seis variantes en fila (cada una con su origen abajo al centro): Boulder_S1 y S2 (~1,5), M1 y M2 (~3,5),
  L1 y L2 (~7).
- Construcción: cada roca es la intersección de los planos tangentes a un elipsoide (12 direcciones
  del icosaedro en las chicas, 20 en las medianas y grandes, giradas al azar y con distancias de
  0,82 a 1) y el piso: caras planas parejas, sin astillas. Los vértices se calculan en la receta (tríos de
  planos) y se pasan a `hull`. Las grandes llevan un segundo bulto metido en el primero (silueta no
  convexa); las medianas y grandes, una veta horizontal de otro color (corte + pintura).
- Colores: S1 sand, S2 redrock_dark, M1 redrock con veta ochre, M2 ochre con veta redrock_dark, L1 redrock
  con veta ochre, L2 redrock_dark con veta redrock.
- Inferido: proporciones de cada una, colores, altura de las vetas, el segundo bulto de las grandes.

Vueltas: 1) grandes de 244 y 228 (32 direcciones) y la veta era una raya (12 % del alto) · 2) 20
direcciones en el bulto principal y 12 en el segundo, veta del 20 %.

Revisión
- Por roca contra 150: S1 34, S2 32, M1 106, M2 110, L1 172, L2 166 (+15 % en las grandes: el segundo
  bulto, que saca la silueta de huevo).
- Medidas (ancho x alto x fondo, aprox.): S ~1,6 x 1,1, M ~3,5 x 2,4, L ~7 x 4,7 (chatas: base plana en y = 0).
- Avisos aceptados: "floating" de cada roca (están sueltas en la fila; cada una con su origen).
"""

import math
import random

from mathutils import Euler, Vector

PHI = (1 + 5 ** 0.5) / 2


def icosa():
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            out += [Vector((0, a, b * PHI)), Vector((a, b * PHI, 0)), Vector((b * PHI, 0, a))]
    return [v.normalized() for v in out]


def dodeca():
    out = [Vector((a, b, c)) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    for a in (-1, 1):
        for b in (-1, 1):
            out += [Vector((0, a / PHI, b * PHI)), Vector((a / PHI, b * PHI, 0)), Vector((a * PHI, 0, b / PHI))]
    return [v.normalized() for v in out]


def polytope(planes):
    pts = []
    m = len(planes)
    for i in range(m):
        n1, d1 = planes[i]
        for j in range(i + 1, m):
            n2, d2 = planes[j]
            for k in range(j + 1, m):
                n3, d3 = planes[k]
                det = n1.dot(n2.cross(n3))
                if abs(det) < 1e-9:
                    continue
                x = (n2.cross(n3) * d1 + n3.cross(n1) * d2 + n1.cross(n2) * d3) / det
                if all(n.dot(x) <= d + 1e-6 for n, d in planes) and all((x - q).length > 1e-4 for q in pts):
                    pts.append(x)
    return pts


def lump(c, axes, dirs, seed, floor_y):
    rnd = random.Random(seed)
    rot = Euler((rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)), "XYZ").to_matrix()
    c = Vector(c)
    planes = [(Vector((0, -1, 0)), -floor_y)]
    for d in dirs:
        n = (rot @ d).normalized()
        h = math.sqrt((axes[0] * n.x) ** 2 + (axes[1] * n.y) ** 2 + (axes[2] * n.z) ** 2)
        planes.append((n, n.dot(c) + h * rnd.uniform(0.82, 1.0)))
    return [tuple(p) for p in polytope(planes)]


# (nombre, x, semiejes, color, veta, segundo bulto (offset, semiejes), semilla)
ROCKS = [
    ("Boulder_S1", -15.0, (0.85, 0.62, 0.7), "sand", None, None, 1),
    ("Boulder_S2", -12.2, (0.75, 0.7, 0.8), "redrock_dark", None, None, 2),
    ("Boulder_M1", -7.6, (1.85, 1.35, 1.5), "redrock", "ochre", None, 3),
    ("Boulder_M2", -2.6, (1.7, 1.5, 1.6), "ochre", "redrock_dark", None, 4),
    ("Boulder_L1", 4.4, (3.3, 2.5, 2.8), "redrock", "ochre", ((1.9, 0.0, 0.9), (2.0, 1.7, 1.9)), 5),
    ("Boulder_L2", 13.6, (3.0, 2.8, 2.6), "redrock_dark", "redrock", ((-1.8, 0.0, -0.8), (1.9, 1.6, 2.0)), 6),
]


def build(mk):
    small = icosa()
    for name, x, axes, mat, band, extra, seed in ROCKS:
        p = mk.part(name, (x, 0, 0))
        dirs = icosa() + dodeca()[:8] if axes[0] > 1 else small                # 20 direcciones o 12
        cy = 0.55 * axes[1]
        mk.hull(p, lump((x, cy, 0), axes, dirs, seed, 0.0), mat)
        if extra:
            off, ax2 = extra
            mk.hull(p, lump((x + off[0], 0.55 * ax2[1], off[2]), ax2, small, seed + 50, 0.02), mat)
        if band:
            top = cy + axes[1]
            yb = 0.45 * top
            th = 0.2 * top
            mk.slice(p, (0, yb - th / 2, 0), (0, 1, 0))
            mk.slice(p, (0, yb + th / 2, 0), (0, 1, 0))
            mk.paint(p, band, box=((x, yb, 0), (12, th, 12)))

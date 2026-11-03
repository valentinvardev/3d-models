"""
Receta de WST_Canyon_Rockslide, el derrumbe que corta el camino del cañón (prompt 086, Bloques A + C).

Brief
- Obstáculo del viaje: hay que bajar del caballo, cubrir y volar el derrumbe con dinamita. Silueta a 40
  studs: un montón de ocho rocas angulosas grandes, apoyadas unas en otras, más alto que un jinete
  (7), con piedras sueltas al pie; colores redrock / ochre / redrock_dark y vetas de estrato en tres.
- Medidas: 16 de ancho (X) x 7 de alto x 8 de fondo (Z), cortando el camino a lo ancho; frente hacia -Z.
  Origen abajo al centro. Rocas de 2,5 a 5.
- Fragmentos: frag01..frag08, una roca cada uno, convexas. Cada roca es la intersección de semiespacios:
  su celda de Voronoi entre las 8 semillas (no se pisan y las vecinas comparten una cara plana de
  contacto), el contorno facetado del montón (16 x 7 x 8), el piso y las caras de su propio elipsoide
  facetado (20 direcciones giradas al azar), que redondean cada roca por afuera: donde se juntan dos rocas
  quedan grietas reales. Los vértices se calculan en la receta (intersección de tríos de planos) y se
  pasan a `hull`.
- Abajo cinco rocas, arriba tres. Piedras sueltas al pie, cada una con la roca más cercana.
- _ChargeSpot: al pie del montón, al centro, del lado de la ruta (-Z), donde se pone la carga.
- Inferido: semillas y tamaños, colores de cada roca, vetas (franja de otro color en 3 rocas), piedras
  sueltas, el marcador del lado del frente.

Vueltas: 1) tres piedras sueltas flotaban (corridas 0,45 del vértice más adelantado de su roca) y se veían
chicas (0,45-0,85) · 2) metidas 0,12 y de 0,6 a 1,1.

Revisión
- 724 triángulos (+12 del marcador) contra 1200 (60 %): rocas de 56 a 132 (con vetas y piedras sueltas).
  Más facetas no cambian la lectura a la distancia de juego.
- Medidas: 15,95 x 7,0 x 10,4 (el montón mide 8,4 de fondo; las piedras sueltas de atrás llegan a 10,4).
- Fragmentos: 8 de ~12 % del volumen cada uno, todos de más de 2 de espesor; las vecinas comparten una cara
  plana (celdas de Voronoi), sin encimes.
- _ChargeSpot en (0, 0,05, -4,6), al pie del frente.
"""

import math
import random

from mathutils import Euler, Vector

PILE = Vector((8.2, 7.0, 4.2))            # semiejes del montón
SEEDS = [(-5.7, 1.7, -0.9), (-2.9, 1.5, 1.1), (0.1, 1.7, -1.0), (3.0, 1.5, 1.0), (5.9, 1.6, -0.8),
         (-3.4, 4.5, 0.2), (0.3, 4.9, -0.3), (3.7, 4.4, 0.4)]
SIZES = [(2.4, 2.0, 4.4), (2.3, 1.9, 4.4), (2.5, 2.1, 4.4), (2.3, 1.9, 4.4), (2.4, 2.0, 4.4),
         (2.7, 2.2, 3.6), (2.6, 2.4, 3.4), (2.6, 2.1, 3.6)]
MATS = ["redrock", "redrock_dark", "ochre", "redrock", "redrock_dark", "ochre", "redrock", "redrock_dark"]
BANDED = {0: "ochre", 3: "redrock_dark", 6: "ochre"}         # vetas de estrato


def dodeca_dirs():
    """20 direcciones (vértices del dodecaedro)."""
    phi = (1 + 5 ** 0.5) / 2
    out = []
    for a in (-1, 1):
        for b in (-1, 1):
            for c in (-1, 1):
                out.append(Vector((a, b, c)))
    for a in (-1, 1):
        for b in (-1, 1):
            out += [Vector((0, a / phi, b * phi)), Vector((a / phi, b * phi, 0)), Vector((a * phi, 0, b / phi))]
    return [v.normalized() for v in out]


def support(c, axes, n):
    """Plano tangente al elipsoide (centro c, semiejes axes) con normal n: n.x <= d."""
    h = math.sqrt((axes[0] * n.x) ** 2 + (axes[1] * n.y) ** 2 + (axes[2] * n.z) ** 2)
    return (n, n.dot(c) + h)


def polytope(planes):
    """Vértices de la intersección de semiespacios n.x <= d (tríos de planos que cumplen todos)."""
    pts = []
    m = len(planes)
    for i in range(m):
        n1, d1 = planes[i]
        for j in range(i + 1, m):
            n2, d2 = planes[j]
            c23 = None
            for k in range(j + 1, m):
                n3, d3 = planes[k]
                det = n1.dot(n2.cross(n3))
                if abs(det) < 1e-9:
                    continue
                x = (n2.cross(n3) * d1 + n3.cross(n1) * d2 + n1.cross(n2) * d3) / det
                if all(n.dot(x) <= d + 1e-6 for n, d in planes):
                    if all((x - q).length > 1e-4 for q in pts):
                        pts.append(x)
    return pts


def rock(mk, part, c, size, seed, mat):
    rnd = random.Random(seed)
    pts = []
    for k in range(10):
        a = 2 * math.pi * k / 5 + rnd.uniform(-0.3, 0.3)
        e = (-0.25, 0.5)[k // 5] + rnd.uniform(-0.1, 0.1)
        r = rnd.uniform(0.75, 1.0)
        pts.append((c[0] + size * r * math.cos(a) * math.cos(e), c[1] + 0.7 * size * math.sin(e),
                    c[2] + size * r * math.sin(a) * math.cos(e)))
    pts.append((c[0], c[1] + 0.65 * size, c[2]))
    mk.hull(part, pts, mat)


def build(mk):
    seeds = [Vector(s) for s in SEEDS]
    dirs = dodeca_dirs()
    pile_dirs = [d for d in dirs] + [Vector((0, 1, 0))]
    pile = [support(Vector((0, 0, 0)), PILE, d) for d in pile_dirs if d.y > -0.2]
    floor = (Vector((0, -1, 0)), 0.0)
    parts, all_pts = [], []
    for i, s in enumerate(seeds):
        rnd = random.Random(100 + i)
        planes = [floor] + pile
        for j, t in enumerate(seeds):                                         # celda de Voronoi
            if j != i:
                n = (t - s)
                planes.append((n, n.dot((s + t) / 2)))
        rot = Euler((rnd.uniform(0, 6.3), rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)), "XYZ").to_matrix()
        for d in dirs:                                                        # su propio elipsoide facetado
            n = (rot @ d).normalized()
            pn, pd = support(s, SIZES[i], n)
            planes.append((pn, pd * rnd.uniform(0.86, 1.0) + (0.0 if n.y < -0.3 else 0.0)))
        pts = polytope(planes)
        all_pts.append(pts)
        name = f"frag{i + 1:02d}"
        p = mk.part(name, (0, 0, 0))
        mk.hull(p, [tuple(q) for q in pts], MATS[i])
        if i in BANDED:                                                       # veta de estrato
            yb = s.y + 0.35
            for y in (yb - 0.3, yb + 0.3):
                mk.slice(p, (0, y, 0), (0, 1, 0))
            mk.paint(p, BANDED[i], box=((s.x, yb, s.z), (12, 0.6, 12)))
        parts.append(p)
    # piedras sueltas al pie: cada una metida en su roca de abajo (adelante y atrás), sin tocar a las vecinas
    rnd = random.Random(7)
    for i in range(5):
        low = [q for q in all_pts[i] if q.y < 1.0]
        for k, (side, r) in enumerate(((-1, rnd.uniform(0.75, 1.1)), (1, rnd.uniform(0.6, 0.9)))):
            if i in (1, 3) and side > 0:
                continue
            anchor = min(low, key=lambda q: side * -q.z) if side < 0 else max(low, key=lambda q: q.z)
            c = (anchor.x + rnd.uniform(-0.15, 0.15), 0.42 * r, anchor.z + side * 0.12 * r)   # metida en su roca
            rock(mk, parts[i], c, r, 200 + 2 * i + k, ("redrock", "redrock_dark", "ochre")[(i + k) % 3])
    mk.marker("_ChargeSpot", (0.0, 0.05, -4.6))

"""
Receta de WST_Bg_Mesa, las mesas y buttes del horizonte (prompt 089, Bloques A + B).

Brief
- Fondo del cañón y de Red Mesa, nunca se llega: solo silueta contra el cielo del atardecer y 2-3 franjas de
  estrato. Formas muy simples: cima plana, paredes a pique, talud al pie.
- Cuatro variantes en fila, cada una con su origen abajo al centro: Mesa_A (150 x 50 de alto, la más ancha),
  Mesa_B (100 x 40), Butte_A (60 x 80, torre alta y angosta), Butte_B (70 x 65).
- Construcción: talud = casco de dos anillos irregulares (base ancha, pie del acantilado); acantilado = 3
  estratos, cada uno un prisma de una planta irregular (14 puntos, ±18 %, dos bahías) extruido en vertical, cada
  uno un poco más adentro que el de abajo y metido 1 en el de abajo. Colores redrock / ochre / redrock_dark
  (el de arriba es la roca de la corona). Fondo (Z) de 0,4 a 0,7 del ancho.
- Inferido: nombres (Mesa_A, Mesa_B, Butte_A, Butte_B), medidas de cada una dentro de los rangos del
  prompt, alturas y colores de los estratos, fondo, forma de la planta.

Vueltas: 1) plantas demasiado elípticas (se leían como tortas apiladas) · 2) 14 puntos, ±18 % y dos bahías
por planta, pie del talud menos parejo.

Revisión
- Por pieza contra 300: Mesa_A 192, Mesa_B 194, Butte_A 194, Butte_B 192.
- Medidas (base del talud): Mesa_A ~150 x 50 de alto, Mesa_B ~100 x 40, Butte_A ~60 x 80, Butte_B ~70 x 65;
  fondo de 0,42 a 0,7 del ancho. En fila en x = 0, 150, 255 y 345.
- Dudoso: el talud de los buttes sale hasta el ancho total (el cuerpo es la mitad): de muy lejos parece un
  ala de sombrero; se puede cerrar más si molesta en el horizonte.
"""

import math
import random


def outline(n, rx, rz, seed, bay=True, jitter=0.18):
    """Planta irregular: n puntos sobre una elipse, radios con ±jitter y dos bahías (una honda)."""
    rnd = random.Random(seed)
    bays = {}
    if bay:
        k1 = rnd.randrange(n)
        bays = {k1: 0.62, (k1 + n // 2 + rnd.choice((-1, 1))) % n: 0.8}
    pts = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.25, 0.25)) / n
        r = (1.0 + rnd.uniform(-jitter, jitter)) * bays.get(i, 1.0)
        pts.append((rx * r * math.cos(a), rz * r * math.sin(a)))
    return pts


def scaled(poly, k, dx=0.0, dz=0.0):
    return [(x * k + dx, z * k + dz) for x, z in poly]


# (nombre, x, ancho de la base, fondo/ancho, alto del talud, [(y0, y1, color)], semilla)
SHAPES = [
    ("Mesa_A", 0.0, 150.0, 0.42, 14.0, [(13.0, 28.0, "redrock"), (27.0, 42.0, "ochre"), (41.0, 50.0, "redrock_dark")], 1),
    ("Mesa_B", 150.0, 100.0, 0.48, 11.0, [(10.0, 22.0, "ochre"), (21.0, 34.0, "redrock"), (33.0, 40.0, "redrock_dark")], 2),
    ("Butte_A", 255.0, 60.0, 0.7, 20.0, [(19.0, 45.0, "redrock"), (44.0, 68.0, "ochre"), (67.0, 80.0, "redrock_dark")], 3),
    ("Butte_B", 345.0, 70.0, 0.65, 16.0, [(15.0, 34.0, "redrock_dark"), (33.0, 55.0, "redrock"), (54.0, 65.0, "ochre")], 4),
]


def build(mk):
    for name, ox, width, ratio, h_talus, bands, seed in SHAPES:
        p = mk.part(name, (ox, 0, 0))
        base_rx, base_rz = width / 2, width / 2 * ratio
        cliff = 0.72 if name.startswith("Mesa") else 0.5                      # el acantilado sobre el talud
        plan = outline(14, base_rx * cliff, base_rz * cliff, seed)
        # talud: anillo de la base (convexo, ancho) y anillo del pie del acantilado
        foot = outline(12, base_rx, base_rz, seed + 10, bay=False, jitter=0.14)
        ring = scaled(outline(10, base_rx * cliff, base_rz * cliff, seed + 20, bay=False, jitter=0.05), 1.08)
        mk.hull(p, [(ox + x, 0.0, z) for x, z in foot] + [(ox + x, h_talus, z) for x, z in ring], "ochre")
        k = 1.0
        for i, (y0, y1, mat) in enumerate(bands):
            rnd = random.Random(seed * 10 + i)
            k *= rnd.uniform(0.9, 0.96) if i else 1.0
            poly = scaled(plan, k, rnd.uniform(-0.02, 0.02) * width, rnd.uniform(-0.02, 0.02) * width * ratio)
            mk.prism(p, [(ox + x, z) for x, z in poly], y1 - y0, mat, plane="xz", center=(0, (y0 + y1) / 2, 0))

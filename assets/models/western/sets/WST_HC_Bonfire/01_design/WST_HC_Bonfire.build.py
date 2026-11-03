"""
Receta de WST_HC_Bonfire, la fogata que encienden los jugadores en Hollow Creek (prompt 119, Bloques A + B).

Brief
- Silueta a 40 studs: un anillo bajo de piedras y una carpa de troncos en punta (2,5 de alto) apagada;
  encendida, las brasas brillan en la base.
- Anillo de 8 piedras (stone_grey) de 4 de diámetro: cada piedra es un casco de 9 puntos (bloque
  irregular de ~1,35 a lo largo del anillo, 0,6 de ancho y ~0,45 de alto) que se mete en las vecinas: el
  anillo es una sola cadena de piedras.
- Seis troncos de 5 lados (r 0,16, wood_mid) en carpa: abajo apoyan en un círculo de radio 1,05 y arriba
  se cruzan pasando el centro (punta a 2,5). Las puntas y el tercio de abajo (lo que quema el fuego) en
  wood_charred. Cama de ceniza (coal) en el centro.
- Embers_Glow: cinco brasas lamp_glow sobre la ceniza (objeto aparte: se esconde apagada).
- _Fire: marcador arriba al centro de los troncos (y 2,4), donde nace la llama.
- Objetos: Bonfire (piedras, troncos, ceniza; el raíz del modelo ya se llama WST_HC_Bonfire, como en el
  resto de la fábrica: "Body", "Building"), Embers_Glow, _Fire. Origen en la base al centro.
- Inferido: forma de piedras y troncos, cantidad de troncos, cama de ceniza, carbonizado del tercio de abajo.

Vueltas: 1) primera versión: la pieza "WST_HC_Bonfire" chocaba con el raíz del modelo (salía .001) y las
bases de las piedras vecinas quedaban en el mismo plano y = 0 (z-fighting donde se enciman) · 2) pieza
"Bonfire", bases a -0,005/-0,015/-0,025, brasas como octaedros chatos (100 -> 40 triángulos).

Revisión
- 364 triángulos contra 250 (+46 %): piedras 8 x 14, troncos 6 x 16 más el corte del tercio carbonizado
  (~60), cama de ceniza 28, brasas 40, marcador 12. El carbonizado del tercio de abajo es lo que dice
  "fogata usada" a la distancia.
- Medidas: 4,22 x 2,6 x 4,22 (anillo de 4 de diámetro + vuelo de las piedras; punta de los troncos 2,5).
- Embers_Glow toca la ceniza: escondido, queda la fogata apagada.
- _Fire en (0, 2,4, 0): arriba al centro, donde se cruzan los troncos.
"""

import math

from mathutils import Vector

STONE, WOOD, CHAR, ASH, GLOW = "stone_grey", "wood_mid", "wood_charred", "coal", "lamp_glow"


def rock(mk, part, a, r_ring, length, width, height, seed):
    """Piedra del anillo: bloque irregular orientado a lo largo del anillo (a en grados)."""
    js = (0.08, -0.06, 0.1, -0.09, 0.05, -0.04, 0.07, -0.1, 0.03)
    t = Vector((-math.sin(math.radians(a)), 0, math.cos(math.radians(a))))       # tangente
    n = Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a))))        # radial
    c = n * r_ring
    pts = []
    k = 0
    y0 = -0.005 - 0.01 * (seed % 3)                      # bases a distinta profundidad: las vecinas se enciman
    for y, sl, sw in ((y0, 1.0, 1.0), (height, 0.7, 0.6)):
        for st in (-1, 1):
            for sn in (-1, 1):
                j = js[(k + seed) % 9]
                p = c + t * (st * length / 2 * sl * (1 + j)) + n * (sn * width / 2 * sw * (1 - j))
                pts.append((p.x, y + (j * 0.6 if y > 0 else 0.0), p.z))
                k += 1
    top = c + t * (0.12 * (1 if seed % 2 else -1)) + n * 0.04
    pts.append((top.x, height * 1.18, top.z))
    mk.hull(part, pts, STONE)


def log(mk, part, a, r0, r1, y0, y1, rad=0.16, sides=5):
    """Tronco recto de (r0, y0) a (r1, y1) en el azimut a."""
    d = Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a))))
    p0 = d * r0 + Vector((0, y0, 0))
    p1 = d * r1 + Vector((0, y1, 0))
    ax = (p1 - p0).normalized()
    u = ax.cross(Vector((0, 1, 0))).normalized()
    v = ax.cross(u)
    pts = []
    for p in (p0, p1):
        for i in range(sides):
            q = 2 * math.pi * (i + 0.5) / sides + math.radians(a)
            pts.append(tuple(p + (u * math.cos(q) + v * math.sin(q)) * rad))
    mk.hull(part, pts, WOOD)
    return p0, p1


def build(mk):
    p = mk.part("Bonfire", (0, 0, 0))                               # el raíz ya se llama WST_HC_Bonfire
    for i in range(8):                                                       # anillo de piedras
        rock(mk, p, 22.5 + 45 * i, 1.68, 1.42, 0.62, 0.44 + 0.06 * ((i * 5) % 3), i)
    ends = []
    for i in range(6):                                                       # carpa de troncos
        a = 15 + 60 * i
        ends.append((a, log(mk, p, a, 1.05, -0.14, 0.05, 2.5 - 0.06 * (i % 2))))
    mk.cyl(p, (0, 0.02, 0), 0.82, 0.08, ASH, sides=8)                          # cama de ceniza
    # carbonizado: las puntas y el tercio de abajo de cada tronco
    mk.slice(p, (0, 0.7, 0), (0, 1, 0))
    for a, (p0, p1) in ends:
        for c, r in ((p0, 0.24), (p1, 0.22), (p0.lerp(p1, 0.12), 0.24)):
            mk.paint(p, CHAR, ball=(tuple(c), r))
    g = mk.part("Embers_Glow", (0, 0, 0))
    for i, (x, z, r) in enumerate(((0.0, 0.0, 0.22), (0.35, 0.2, 0.15), (-0.3, 0.25, 0.17), (0.15, -0.38, 0.16),
                                   (-0.32, -0.22, 0.13))):
        q = math.radians(40 * i)
        pts = [(x + r * math.cos(q + k * math.pi / 2), 0.05, z + r * math.sin(q + k * math.pi / 2) * 0.8)
               for k in range(4)] + [(x, 0.05 + r * 0.7, z), (x + 0.02, 0.0, z)]
        mk.hull(g, pts, GLOW)                                               # brasa: octaedro chato
    mk.marker("_Fire", (0, 2.4, 0))

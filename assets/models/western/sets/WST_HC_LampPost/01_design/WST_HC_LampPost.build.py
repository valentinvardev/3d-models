"""
Receta de WST_HC_LampPost, el farol de calle de Hollow Creek (prompt 120, Bloques A + C).

Brief
- Silueta a 40 studs: poste alto y oscuro con un travesaño arriba (donde se apoya la escalera) y un farol
  de cuatro caras de vidrio con techito en punta: se lee como farol de calle aunque esté apagado.
- Poste wood_dark de 0,45 x 0,45 y 9 de alto; travesaño de 1,7 x 0,2 x 0,2 a 8,0 que lo atraviesa. Farol
  arriba (y 9 a 11,1): base de hierro de 0,95, cuerpo de vidrio que se abre hacia arriba (0,74 -> 0,98, 1,2
  de alto), cuatro aristas de hierro, tapa, techo en pirámide, sombrerete y mechero bajo la llama.
- Fragmentos (3, origen común en la base): frag01 el poste de abajo y frag02 el de arriba con el
  travesaño, partidos por un plano en diagonal (y 4,3 a 4,75; el de arriba corrido 0,03 a lo largo del
  corte, técnica del poste de atar); frag03 el farol entero.
- Lamp_Glow: la llama (gota de 6 puntos, lamp_glow) adentro del farol, con el origen en ella. _Light:
  marcador en la llama.
- Inferido: sección del poste, alto y largo del travesaño, forma y medidas del farol, dónde se parte.

Vueltas: 1) primera versión: pasa la revisión, pero la llama flotaba en el aire adentro del farol y el
farol (0,8) se perdía arriba de un poste de 9 · 2) mechero de hierro bajo la llama y farol más grande
(base 0,95, vidrio de 0,74 a 0,98 y 1,2 de alto, techo de 1,2).

Revisión
- 186 triángulos contra 200: poste 36 (dos tramos y travesaño), farol 130, llama 8, marcador 12.
- Medidas: 1,7 (travesaño) x 11,11 x 1,2; poste de 9, farol de 9 a 11,1.
- Fragmentos: poste partido al medio (4,3-4,75): ~48 % del volumen cada tramo (el Bloque C pide <= 45 %;
  "el poste se parte en dos" lo hace imposible, como en el poste de telégrafo). El farol, ~4 %.
- Lamp_Glow apoya en el mechero (frag03) y tiene el origen en la llama; _Light en el mismo punto.
"""

import math

WOOD, IRON, GLASS, GLOW = "wood_dark", "iron", "glass", "lamp_glow"
S = 0.225                      # medio lado del poste
H = 9.0
CUT = (4.3, 4.75)              # alto del corte en x = -S y x = +S
SLIDE = 0.03
FLAME = (0.0, 9.6, 0.0)


def build(mk):
    y_at = lambda x: CUT[0] + (CUT[1] - CUT[0]) * (x + S) / (2 * S)          # noqa: E731
    lo = mk.part("frag01", (0, 0, 0))
    mk.hull(lo, [(x, y, z) for x in (-S, S) for z in (-S, S) for y in (0.0, y_at(x))], WOOD)

    d = (2 * S, CUT[1] - CUT[0])
    n = math.hypot(*d)
    sx, sy = -d[0] / n * SLIDE, -d[1] / n * SLIDE
    up = mk.part("frag02", (0, 0, 0))
    mk.hull(up, [(x + sx, y, z) for x in (-S, S) for z in (-S, S) for y in (y_at(x) + sy, H)], WOOD)
    mk.box(up, (sx, 8.0, 0), (1.7, 0.2, 0.2), WOOD)                                       # travesaño

    lamp = mk.part("frag03", (0, 0, 0))
    yb = H + sy
    mk.box(lamp, (sx, yb + 0.06, 0), (0.95, 0.13, 0.95), IRON, top=(0.85, 0.85))            # base
    g0, g1 = yb + 0.12, yb + 1.32                                                           # vidrio
    mk.hull(lamp, [(sx + x * k, y, z * k) for k, y in ((0.37, g0), (0.49, g1)) for x in (-1, 1) for z in (-1, 1)], GLASS)
    for cx in (-1, 1):                                                                      # aristas
        for cz in (-1, 1):
            pts = [(sx + cx * k + dx, y, cz * k + dz) for k, y in ((0.37, g0 - 0.02), (0.49, g1 + 0.02))
                   for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)]
            mk.hull(lamp, pts, IRON)
    mk.box(lamp, (sx, g1 + 0.06, 0), (1.12, 0.12, 1.12), IRON)                              # tapa
    mk.hull(lamp, [(sx + x, g1 + 0.11, z) for x in (-0.6, 0.6) for z in (-0.6, 0.6)] + [(sx, g1 + 0.72, 0)], IRON)  # techo
    mk.cyl(lamp, (sx, g1 + 0.72, 0), 0.16, 0.18, IRON, sides=6, top=0.6)                     # sombrerete
    mk.cyl(lamp, (sx, (g0 + FLAME[1] + sy - 0.1) / 2, 0), 0.09, FLAME[1] + sy - 0.1 - g0 + 0.02, IRON, sides=6)  # mechero

    flame = (sx, FLAME[1] + sy, 0.0)
    fl = mk.part("Lamp_Glow", flame)
    fx, fy, fz = flame
    mk.hull(fl, [(fx + 0.1 * math.cos(a), fy, fz + 0.1 * math.sin(a)) for a in (0.0, 2.1, 4.2)]
            + [(fx, fy - 0.12, fz), (fx, fy + 0.3, fz), (fx + 0.03, fy + 0.12, fz + 0.05)], GLOW)
    mk.marker("_Light", flame)

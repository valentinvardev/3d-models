"""
Receta de WST_Prop_Sacks, las bolsas de arpillera (prompt 137, Bloques A + C).

Brief
- Silueta a 40 studs: bulto blando y abultado abajo, cuello atado con soga y la boca de arpillera
  abierta en flor arriba. Color canvas, atadura rope, etiqueta paint_cream al frente.
- Piezas (tres variantes en el archivo, en fila sobre X):
  Sack_Upright (x = 0): parada, 1,2 x 2 x 1. Sack_Lying (x = 2,6): acostada a lo largo de X (2,2 x 1,0 de
  alto). Sack_Pile (x = 7): 5 bolsas acostadas en tres capas (2 + 2 + 1), 3 de alto: cubre agachado.
- Cuerpo de 8 lados con radios que varían ±7 % (bolsa blanda, no tubo); boca: cuello atado (anillo de
  soga de 6 lados) y la arpillera que se abre arriba (tronco de cono invertido).
- Etiqueta en blanco (para "FLOUR"/"FEED"): la cara del frente (-Z) del cuerpo pintada paint_cream, sin
  geometría encima (tinta sobre la tela; el texto va en Studio).
- Fragmentos (2 por bolsa, origen común de cada variante): mitad de abajo / mitad de la boca, cortadas en
  un anillo (cara de contacto plana). En la pila serían 10 y el Bloque C permite 8: las 2 bolsas de abajo
  van enteras (Sack_Pile_frag01-02) y las 3 de arriba en dos (frag03-08).
- Inferido: forma; tamaño acostada; la pila en capas 2+2+1; que la etiqueta sea pintura; qué bolsas
  de la pila no se parten; nombres <Variante>_fragNN.

Vueltas: 1) la parada medía 1,18 de fondo (pide 1,0); la punta de las acostadas era un octógono plano
de r 0,55 que se leía como tronco cortado · 2) sección elíptica en la parada (1,17 x 2,01 x 1,0) y punta
de las acostadas con r 0,42.

Revisión
- ~128 triángulos por bolsa (el tope dice 120 "para todo el modelo", pero el modelo tiene 7 bolsas: se
  tomó por bolsa). Parada 128, acostada 128, pila 614 (5 bolsas). Total 870.
- DUDOSO, etiqueta con poco contraste: paint_cream (E3D6BC) sobre canvas (CDBB97). Es el color de
  etiqueta de la paleta (el mismo que la placa de la caja); la calcomanía en Studio le va a dar la
  lectura. Si hace falta que se vea sin calcomanía, no hay un tono más claro en la paleta.
- Mitades 59/41 % (el Bloque C pide <= 45 %: con 2 fragmentos por bolsa es imposible; la mitad con la
  panza es la más pesada). En la pila las bolsas de abajo son el 21 % cada una.
- En la pila, las bolsas de arriba se hunden ~0,05 en las de abajo (bolsas blandas): no hay contacto
  exacto entre cascos irregulares.
"""

import math

from mathutils import Euler, Vector

# (posición a lo largo, factor de radio): fondo, panza, corte, hombro, cuello
STANDING = ((0.0, 0.55), (0.14, 1.0), (0.5, 1.0), (0.8, 0.8), (0.9, 0.36))     # fondo ancho: apoya
LYING = ((0.0, 0.42), (0.14, 1.0), (0.5, 1.0), (0.8, 0.8), (0.9, 0.36))        # punta más redonda (con 0,55
#                                                                                 se leía como tronco cortado)


def sack(mk, names, origin, base, axis, length, radius, flat=1.0, seed=0.0, depth=1.0):
    """Bolsa con el fondo en `base` y la boca hacia `axis`. names: 1 (entera) o 2 (dos mitades)."""
    ax = Vector(axis).normalized()
    stations = LYING if abs(ax.y) < 0.7 else STANDING
    n1 = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    n1 = (n1 - ax * n1.dot(ax)).normalized()
    n2 = ax.cross(n1).normalized()
    if n2.y < 0:
        n2 = -n2

    def ring(i, s, k_r, sides=8, jitter=True):
        c = Vector(base) + ax * (s * length)
        pts = []
        for k in range(sides):
            t = 2 * math.pi * (k + 0.5) / sides
            j = 1 + 0.07 * math.sin(1.7 * k + 2.3 * i + seed) if jitter else 1.0
            r = radius * k_r * j
            fl = flat if abs(n2.y) > 0.7 else 1.0                       # acostada: se achata contra el piso
            pts.append(c + n1 * (r * depth * math.cos(t)) + n2 * (r * fl * math.sin(t)))
        return pts

    rings = [ring(i, s, k) for i, (s, k) in enumerate(stations)]
    tie = ring(9, 0.88, 0.42, 6, False) + ring(9, 0.95, 0.42, 6, False)
    tuft = ring(9, 0.93, 0.3, 6, False) + ring(10, 1.06, 0.52, 6)
    allp = [p for r in rings for p in r] + tie + tuft
    dy = Vector(base).y - min(p.y for p in allp)                           # apoya en su base

    def T(pts):
        return [tuple(p + Vector((0, dy, 0))) for p in pts]

    lower = rings[0] + rings[1] + rings[2]
    upper = rings[2] + rings[3] + rings[4]
    if len(names) == 1:                     # entera: un solo casco (dos en el mismo objeto se soldarían en el corte)
        parts = [mk.part(names[0], origin)] * 2
        mk.hull(parts[0], T([p for r in rings for p in r]), "canvas")
    else:
        parts = [mk.part(names[0], origin), mk.part(names[1], origin)]
        mk.hull(parts[0], T(lower), "canvas")
        mk.hull(parts[1], T(upper), "canvas")
    mk.hull(parts[1], T(tie), "rope")
    mk.hull(parts[1], T(tuft), "canvas")
    # etiqueta: la cara del cuerpo que mira a -Z, entre la panza y el corte
    best = None
    for k in range(8):
        quad = [rings[1][k], rings[1][(k + 1) % 8], rings[2][k], rings[2][(k + 1) % 8]]
        c = sum(quad, Vector()) / 4
        nrm = (c - (Vector(base) + ax * (0.32 * length)))
        if best is None or nrm.normalized().z < best[0]:
            best = (nrm.normalized().z, c)
    mk.paint(parts[0], "paint_cream", ball=(tuple(best[1] + Vector((0, dy, 0))), 0.3 * radius / 0.6))


def build(mk):
    # ---- parada ----
    # sección elíptica: 1,2 de ancho y 1,0 de fondo (redonda medía 1,18 de fondo)
    sack(mk, ("Sack_Upright_frag01", "Sack_Upright_frag02"), (0, 0, 0), (0, 0, 0), (0, 1, 0), 1.9, 0.6, seed=0.4,
         depth=0.85)
    # ---- acostada ----
    x0 = 2.6
    sack(mk, ("Sack_Lying_frag01", "Sack_Lying_frag02"), (x0, 0, 0), (x0 - 1.05, 0, 0), (1, 0, 0), 2.0, 0.6,
         flat=0.82, seed=1.3)
    # ---- pila: 2 + 2 + 1 acostadas ----
    x0 = 7.0
    o = (x0, 0, 0)
    sack(mk, ("Sack_Pile_frag01",), o, (x0 - 1.05, 0, -0.6), (1, 0, 0.05), 2.0, 0.6, flat=0.82, seed=2.1)
    sack(mk, ("Sack_Pile_frag02",), o, (x0 + 1.0, 0, 0.62), (-1, 0, -0.04), 2.0, 0.6, flat=0.82, seed=3.7)
    sack(mk, ("Sack_Pile_frag03", "Sack_Pile_frag04"), o, (x0 - 0.85, 0.96, -0.52), (1, 0, -0.08), 1.9, 0.58,
         flat=0.82, seed=4.2)
    sack(mk, ("Sack_Pile_frag05", "Sack_Pile_frag06"), o, (x0 + 0.95, 0.96, 0.55), (-1, 0, 0.06), 1.9, 0.58,
         flat=0.82, seed=5.9)
    sack(mk, ("Sack_Pile_frag07", "Sack_Pile_frag08"), o, (x0 - 0.9, 1.95, 0.05), (1, 0, 0.18), 1.85, 0.6,
         flat=0.82, seed=6.6)

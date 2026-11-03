"""
Receta de WST_Weapon_WhiskeyMolotov, botella de whisky con trapo (prompt 031, Bloques A + F).

Brief
- Silueta a 30 studs: botella ámbar de hombros cuadrados y cuello corto, etiqueta crema al frente y un trapo
  rojo metido en el pico con una cola que cae por encima del hombro (ahí va el fuego, VFX).
- Medidas: alto 0,75 (cuerpo 0,44, hombro 0,06, cuello 0,18, boca 0,07), ancho 0,28 (octógono de 8 lados con
  una cara plana al frente para la etiqueta). Origen en el centro del cuerpo, botella parada en Y.
- Piezas: Bottle (vidrio, etiqueta 0,01 afuera, boca tallada) y Rag (bollo en la boca + cola de 0,3 desde el
  pico, rota en dos tiras en la punta). Marcador _Fuse en la punta de la cola.
- Chanflán en los bordes de la botella que dan 90° (base, hombro, boca), no entre las caras del octógono.

Inferido (el prompt no lo dice)
- La cola cae hacia adelante a la derecha (diagonal): se ve de frente y de costado, y no tapa la etiqueta.
- La punta de la cola se lee rota con dos tiras de largo distinto.
- La etiqueta tiene una esquina rota (sin texto: va como calcomanía en el motor).

Vueltas: 1) primera versión: la cola salía derecha en diagonal y se leía como una tabla roja apoyada;
z-fighting entre tramos de la tira (los costados de dos tramos casi del mismo ancho quedaban a < 1,5°) ·
2) tramos vecinos con 6 % de ancho distinto · 3) cola pegada al cuello, que sale por el hombro y cuelga al
costado, corrida de lado en cada tramo y más angosta hacia la punta.

Revisión
- 432 triángulos contra 200 de referencia (calidad primero): la botella (260) lleva chanflán en la base, el
  hombro y la boca, que es lo que le da brillo de vidrio con luz plana; el trapo (160) son el bollo y nueve
  tramos con la punta rota.
- La cola mide ~0,4 desde la boca (el prompt dice 0,3): con 0,3 terminaba arriba del hombro y no "colgaba".
"""

import math

from mathutils import Vector

R_BODY, R_NECK, R_LIP = 0.14, 0.052, 0.068
Y_BOT, Y_SHOULDER, Y_NECK, Y_LIP, Y_TOP = -0.22, 0.22, 0.28, 0.46, 0.53
FACE = math.cos(math.pi / 8)          # distancia a la cara plana / radio del octógono
DIR = math.radians(315)               # la cola cae hacia adelante a la derecha (t medido de +X a +Z)


def drape(rad, y):
    """Punto (radial, alto) en el plano vertical de la cola -> coordenadas del juego."""
    return Vector((rad * math.cos(DIR), y, rad * math.sin(DIR)))


def strip(mk, part, pts, widths, t, mat):
    """Tira de tela por tramos: ancho `widths[k]` horizontal, grosor t en el plano de la cola."""
    wax = Vector((-math.sin(DIR), 0, math.cos(DIR)))                  # eje del ancho (horizontal)
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        d = (b - a).normalized()
        n = d.cross(wax).normalized() * (t / 2)
        ext = d * 0.004
        alt = 1.0 + 0.06 * (k % 2)          # tramos vecinos con ancho distinto: sus costados no quedan coplanares
        hull = []
        for c, w in ((a - ext, widths[k] * alt), (b + ext, widths[k + 1] * alt)):
            for sn in (-1, 1):
                for sw in (-1, 1):
                    hull.append(tuple(c + n * sn + wax * (sw * w / 2)))
        mk.hull(part, hull, mat)


def build(mk):
    # ---------------- botella ----------------
    bot = mk.part("Bottle", (0, 0, 0))
    mk.cyl(bot, (0, (Y_BOT + Y_SHOULDER) / 2, 0), R_BODY, Y_SHOULDER - Y_BOT, "glass_amber", sides=8)
    mk.hull(bot, mk.pts_cyl((0, Y_SHOULDER - 0.005, 0), R_BODY, 0.01, sides=8)
            + mk.pts_cyl((0, Y_NECK + 0.005, 0), R_NECK, 0.01, sides=8), "glass_amber")       # hombro cuadrado
    mk.cyl(bot, (0, (Y_NECK + Y_LIP) / 2, 0), R_NECK, Y_LIP - Y_NECK + 0.01, "glass_amber", sides=8)
    mk.cyl(bot, (0, (Y_LIP + Y_TOP) / 2, 0), R_LIP, Y_TOP - Y_LIP, "glass_amber", sides=8)   # boca
    mk.bevel(bot, width=0.012, angle=50)
    mk.carve(bot, "coal", points=mk.pts_cyl((0, Y_TOP, 0), 0.036, 0.1, sides=8))           # pico
    front = R_BODY * FACE                                                                  # cara plana de adelante
    label = [(-0.046, -0.1), (0.046, -0.1), (0.046, 0.075), (0.02, 0.095), (-0.046, 0.095)]  # una esquina rota
    mk.prism(bot, label, 0.016, "paint_cream", plane="xy", center=(0, -0.01, -(front + 0.002)), detail=True)

    # ---------------- trapo: bollo en el pico y una cola sobre el hombro ----------------
    rag = mk.part("Rag", (0, 0, 0))
    mk.ball(rag, (0.0, Y_TOP + 0.012, 0.0), 0.05, "cloth_red", scale=(1.0, 0.8, 1.0), subdiv=1)
    mk.ball(rag, (-0.025, Y_TOP + 0.035, 0.018), 0.035, "cloth_red", scale=(1.1, 0.9, 0.9), subdiv=0)
    wax = Vector((-math.sin(DIR), 0, math.cos(DIR)))
    # pegada al cuello, sale por el hombro y cuelga al costado del cuerpo (corrida de lado: tela, no tabla)
    drop = ((0.0, Y_TOP + 0.035, 0.0), (0.045, Y_TOP + 0.03, 0.0), (0.078, Y_TOP - 0.002, 0.006),
            (0.074, Y_LIP + 0.005, 0.012), (0.064, 0.39, 0.016), (0.068, 0.31, 0.01), (0.10, 0.268, 0.0),
            (0.145, 0.226, -0.01), (0.16, 0.17, -0.018))
    path = [drape(r, y) + wax * o for r, y, o in drop]
    widths = [0.068, 0.072, 0.07, 0.066, 0.062, 0.06, 0.058, 0.054, 0.05]
    strip(mk, rag, path, widths, 0.022, "cloth_red")
    end, prev = path[-1], path[-2]
    d = (end - prev).normalized()
    for off, ln, w in ((-0.016, 0.06, 0.026), (0.018, 0.035, 0.024)):                    # dos tiras rotas
        a = end - d * 0.01 + wax * off
        strip(mk, rag, [a, a + d * ln], [w, w * 0.6], 0.018, "cloth_red")
    mk.marker("_Fuse", tuple(end + d * 0.05 + wax * -0.016))

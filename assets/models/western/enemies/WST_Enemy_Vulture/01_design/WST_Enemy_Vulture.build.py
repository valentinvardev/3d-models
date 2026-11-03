"""
Receta de WST_Enemy_Vulture, el buitre zombie (prompt 057, Bloques A + E).

Brief
- Silueta a 40 studs (en bandada, contra el cielo): alas abiertas de 5 de punta a punta con los dedos de
  las plumas separados en las puntas, borde de atrás deshilachado, cuello pelado largo con la gorguera
  blanca, pico ganchudo. Barato: van muchos a la vez.
- Medidas: envergadura 5,0 (x de -2,5 a 2,5), cuerpo 1,6 de largo y 0,9 de alto. Pose de reposo: alas
  extendidas planas y horizontales (en T), patas recogidas, cabeza adelante (-Z).
- Piezas (nombres del prompt): Body (origen del modelo, en el piso bajo el centro de masa), Head (con el
  cuello; origen donde el cuello sale del cuerpo), WingLeftInner/WingRightInner (origen en el hombro),
  WingLeftOuter/WingRightOuter (origen en la muñeca), Tail (origen en la base) y Silver_Eyes (origen de
  la cabeza).
- Alas y cola como prismas planos (sin booleanas): el borde de atrás en zigzag, los agujeros como
  ranuras abiertas (una por ala adentro y un dedo que falta afuera), el abanico de 6 plumas con muescas
  en la punta. El ala de afuera es 0,01 más fina que la de adentro: donde se encastran, las tapas no
  quedan en el mismo plano.
- Ala izquierda de adentro: el borde de adelante roto deja ver los dos huesos del ala (bone).
- Inferido: altura de las alas (y = 0,62), largo del cuello (0,6), gorguera como una bola facetada,
  patas recogidas como dos cuñas bajo la cola.

Vueltas: 1) primera versión (una pata flotaba: el icosaedro del cuerpo tiene la panza más alta de lo
calculado) · 2) cuerpo como casco de anillos hexagonales con la panza en y = 0 · 3) pico más corto y
ganchudo (era una cuña larga y chata), cuello en dos tramos.

Revisión
- 396 triángulos contra 400.
- Medidas: 5,00 de envergadura, cuerpo 1,6 × 0,93, 2,79 de largo con cabeza y cola.
- Revisado desde arriba y desde abajo (vistas aparte): se ven las ranuras del borde de atrás, el dedo
  que falta en cada punta y los dos huesos en el ala izquierda.
- El cuello en S casi no se nota con dos tramos; más tramos pasan el tope.
"""

import math


def mirror_xz(profile):
    return [(-x, z) for x, z in profile][::-1]


WING_Y = 0.62
INNER_L = [(-0.25, -0.32), (-0.55, -0.31), (-0.62, -0.12), (-0.98, -0.12), (-1.05, -0.28), (-1.42, -0.24),
           (-1.42, 0.40), (-1.30, 0.62), (-1.18, 0.46), (-1.06, 0.66), (-0.94, 0.48), (-0.86, 0.20), (-0.76, 0.20),
           (-0.70, 0.50), (-0.58, 0.66), (-0.46, 0.48), (-0.25, 0.45)]
INNER_R = [(0.25, -0.32), (1.42, -0.24), (1.42, 0.40), (1.30, 0.62), (1.18, 0.46), (1.06, 0.66), (0.94, 0.48),
           (0.86, 0.20), (0.76, 0.20), (0.70, 0.50), (0.58, 0.66), (0.46, 0.48), (0.25, 0.45)]
OUTER_L = [(-1.37, -0.24), (-1.75, -0.24), (-2.10, -0.20), (-2.50, -0.12), (-2.28, -0.04), (-2.46, 0.06),
           (-2.22, 0.08), (-2.38, 0.21), (-2.02, 0.15), (-2.04, 0.44), (-1.86, 0.34), (-1.84, 0.48), (-1.66, 0.38),
           (-1.37, 0.42)]                       # el dedo entre la 3ª y la 5ª pluma falta: ranura hasta x = -2,02


def build(mk):
    body = mk.part("Body", (0, 0, 0))

    def hexring(z, w, h, cy=0.45):                 # hexágono vertical con un vértice abajo (la panza toca el piso)
        return [(w / 2 * math.cos(math.radians(-90 + 60 * k)), cy + h / 2 * math.sin(math.radians(-90 + 60 * k)), z)
                for k in range(6)]
    mk.hull(body, hexring(-0.45, 0.62, 0.66, 0.50) + hexring(0.0, 0.84, 0.90) + hexring(0.45, 0.68, 0.66, 0.43)
            + [(0, 0.52, -0.80), (0, 0.45, 0.80)], "feather_black")
    for s in (-1, 1):                                                                                  # patas recogidas
        mk.hull(body, [(s * 0.08, 0.16, 0.20), (s * 0.18, 0.16, 0.20), (s * 0.13, 0.08, 0.40), (s * 0.08, 0.20, 0.44),
                       (s * 0.18, 0.20, 0.44)], "vulture_skin")

    # cuello pelado y cabeza, con la gorguera blanca en la base y el pico ganchudo
    hd = mk.part("Head", (0, 0.62, -0.62))
    for a, b in ((((0, 0.62, -0.55), 0.10), ((0, 0.84, -0.80), 0.075)), (((0, 0.82, -0.78), 0.072), ((0, 0.78, -1.08), 0.068))):
        mk.hull(hd, [(c[0] + dx * r, c[1] + dy * r, c[2]) for c, r in (a, b) for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1))],
                "vulture_skin")                                                                      # cuello en S, dos tramos
    mk.hull(hd, [(-0.11, 0.80, -1.08), (0.11, 0.80, -1.08), (0, 0.93, -1.12), (0, 0.70, -1.12), (-0.09, 0.86, -1.36),
                 (0.09, 0.86, -1.36), (-0.08, 0.72, -1.34), (0.08, 0.72, -1.34), (0, 0.92, -1.30)], "vulture_skin")  # cabeza
    mk.hull(hd, [(-0.045, 0.86, -1.33), (0.045, 0.86, -1.33), (-0.045, 0.76, -1.33), (0.045, 0.76, -1.33),
                 (0, 0.87, -1.46), (0, 0.80, -1.55), (0, 0.69, -1.52), (0, 0.75, -1.42)], "bone")       # pico corto y ganchudo
    mk.ball(hd, (0, 0.64, -0.66), 1.0, "hide_white", scale=(0.30, 0.20, 0.18), subdiv=0)            # gorguera
    se = mk.part("Silver_Eyes", (0, 0.62, -0.62))
    for s in (-1, 1):
        c = (s * 0.095, 0.85, -1.24)
        mk.hull(se, [(c[0] + s * 0.03, c[1], c[2]), (c[0] - s * 0.02, c[1], c[2]), (c[0], c[1] + 0.03, c[2]),
                     (c[0], c[1] - 0.03, c[2]), (c[0], c[1], c[2] - 0.03), (c[0], c[1], c[2] + 0.03)], "silver_neon")

    # alas: planas, abiertas en T
    for side, s, inner in (("Left", -1, INNER_L), ("Right", 1, INNER_R)):
        wi = mk.part(f"Wing{side}Inner", (s * 0.30, WING_Y, -0.10))
        mk.prism(wi, inner, 0.07, "feather_black", plane="xz", center=(0, WING_Y, 0))
        wo = mk.part(f"Wing{side}Outer", (s * 1.40, WING_Y, -0.05))
        outer = OUTER_L if s < 0 else mirror_xz(OUTER_L)
        mk.prism(wo, outer, 0.06, "feather_black", plane="xz", center=(0, WING_Y, 0))
    wl = "WingLeftInner"
    for z in (-0.24, -0.17):                                                                         # huesos a la vista
        mk.hull(wl, [(-0.40, WING_Y - 0.01, z - 0.025), (-0.40, WING_Y + 0.045, z - 0.025), (-0.40, WING_Y + 0.02, z + 0.025),
                     (-1.20, WING_Y - 0.01, z - 0.02), (-1.20, WING_Y + 0.04, z - 0.02), (-1.20, WING_Y + 0.02, z + 0.02)], "bone")

    tail = mk.part("Tail", (0, 0.50, 0.70))
    mk.prism(tail, [(-0.18, 0.60), (0.18, 0.60), (0.30, 1.10), (0.20, 1.02), (0.12, 1.22), (0.02, 1.08), (-0.08, 1.24),
                    (-0.18, 1.04), (-0.30, 1.12)], 0.05, "feather_black", plane="xz", center=(0, 0.50, 0))

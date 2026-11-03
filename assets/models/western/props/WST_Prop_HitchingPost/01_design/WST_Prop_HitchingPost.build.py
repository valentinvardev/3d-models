"""
Receta de WST_Prop_HitchingPost, el poste para atar caballos (prompt 134, Bloques A + C).

Brief
- Silueta a 40 studs: poste cuadrado con remate en punta y una argolla de hierro colgando al frente.
- Medidas: 3,5 de alto, 0,5 x 0,5 (fragmentos >= 0,4), remate piramidal de 0,12. Argolla de 0,56 de
  diámetro (0,08 de grueso) colgando de un cáncamo en la cara del frente a y 3,0.
- Fragmentos (2, origen común): el poste partido por un plano en diagonal (de y 1,55 a 1,95): frag01 el
  tramo de abajo, frag02 el de arriba con el remate, el cáncamo y la argolla. Los dos tramos son
  convexos sin tallar; el de arriba está corrido 0,03 a lo largo del corte, así la rajadura se ve en las
  caras con el poste entero ("ya rajado y listo para caer").
- Variante HitchRail_Short (mismo archivo, en x = 4): dos postes de 3,1 (HitchRail_Short_fixed_PostL y
  _PostR, quedan en pie) y una baranda de 4 x 0,4 x 0,4 arriba (tope 3,5) partida en diagonal al medio:
  HitchRail_Short_frag01 y _frag02.
- Inferido: sección de 0,5; remate; argolla al frente colgando plana contra el poste; dónde se parte;
  en la variante los postes quedan y se rompe la baranda; sin argollas en la baranda (las riendas se
  atan a la baranda); nombres de la variante.

Vueltas: 1) pasa la revisión.

Revisión
- 104 triángulos el poste (tope 100): la argolla en dos mitades es 56. La variante 48.
- Con 2 fragmentos cada uno es ~50 % del volumen (el Bloque C pide <= 45 %): con dos piezas es
  imposible; manda el "Frag 2" del prompt.
- La argolla es hexagonal (3 tramos por mitad): a la distancia de juego se lee redonda.
"""

import math

H = 3.5
S = 0.25                                   # medio lado del poste
CUT = (1.55, 1.95)                         # alto del corte en x = -S y x = +S
SLIDE = 0.03
RAIL_X = 4.0


def ring_half(mk, part, c, r_out, r_in, a0, a1, depth, n=3):
    angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
    prof = ([(r_out * math.cos(math.radians(a)), r_out * math.sin(math.radians(a))) for a in angs]
            + [(r_in * math.cos(math.radians(a)), r_in * math.sin(math.radians(a))) for a in reversed(angs)])
    mk.prism(part, [(c[0] + x, c[1] + y) for x, y in prof], depth, "iron", plane="xy", center=(0, 0, c[2]))


def build(mk):
    # ---------------- poste suelto ----------------
    y_at = lambda x: CUT[0] + (CUT[1] - CUT[0]) * (x + S) / (2 * S)        # noqa: E731
    lo = mk.part("frag01", (0, 0, 0))
    mk.hull(lo, [(x, y, z) for x in (-S, S) for z in (-S, S) for y in (0.0, y_at(x))], "wood_mid")

    # el tramo de arriba, corrido SLIDE a lo largo del corte (bajando por la pendiente)
    d = (2 * S, CUT[1] - CUT[0])
    n = math.hypot(*d)
    sx, sy = -d[0] / n * SLIDE, -d[1] / n * SLIDE
    up = mk.part("frag02", (0, 0, 0))
    mk.hull(up, [(x + sx, y, z) for x in (-S, S) for z in (-S, S) for y in (y_at(x) + sy, H - 0.12)], "wood_mid")
    mk.hull(up, [(x * k + sx, y, z * k) for k, y in ((0.998, H - 0.13), (0.3, H)) for x in (-S, S)
                 for z in (-S, S)], "wood_mid")                                       # remate
    mk.box(up, (sx, 3.02, -S - 0.05), (0.1, 0.12, 0.12), "iron")                       # cáncamo
    c = (sx, 2.74, -S - 0.08)
    # argolla en dos mitades (una corona no es convexa) que se solapan 3° con 0,01 menos de grosor:
    # con junturas, la mitad de abajo no tocaba nada (flotaba)
    ring_half(mk, up, c, 0.28, 0.2, -3, 183, 0.08)
    ring_half(mk, up, c, 0.28, 0.2, 177, 363, 0.07)

    # ---------------- variante: dos postes y baranda ----------------
    x0 = RAIL_X
    for name, xp in (("HitchRail_Short_fixed_PostL", -1.75), ("HitchRail_Short_fixed_PostR", 1.75)):
        p = mk.part(name, (x0, 0, 0))
        mk.box(p, (x0 + xp, 1.55, 0), (2 * S, 3.1, 2 * S), "wood_mid")
    rail_y = (3.1, 3.5)
    zig = (-0.15, 0.15)                                                # corte en diagonal (en planta) al medio
    for name, side in (("HitchRail_Short_frag01", -1), ("HitchRail_Short_frag02", 1)):
        p = mk.part(name, (x0, 0, 0))
        pts = []
        for z, xc in ((-0.2, zig[0]), (0.2, zig[1])):
            for xe in (xc, side * 2.0):
                for y in rail_y:
                    pts.append((x0 + xe, y, z))
        mk.hull(p, pts, "wood_mid")

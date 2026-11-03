"""
Receta de WST_Weapon_HuntingRifle, rifle de caza de bloque que cae, con mira de bronce (prompt 030, Bloques A + F).

Brief
- Silueta a 30 studs: el arma más larga del juego, caño octogonal pesado con un tubo de bronce fino y largo
  encima (la mira, lo que lo identifica), martillo grande al costado derecho y la palanca-guardamonte en S.
- Medidas: largo 3,7 (caño 2,0), alto 0,7 con la mira (de la punta de la cantonera al tope del ocular),
  ancho 0,22. Se arma en "espacio del rifle" (eje del caño en y = 0, fondo del cajón en z = 0) y P() lo corre
  para que el centro de la muñeca quede en (0,0,0).
- Piezas: Body (caño, cajón, caña, culata, chapas de la llave, gatillo, bases de la mira), Lever (punta de
  adelante, baja 45°), BreechBlock (borde de arriba adelante, baja 0,2 por la mortaja del cajón y deja ver la
  recámara), Hammer (base, a la derecha), Scope (tubo de bronce con ocular y abrazaderas; fijo, origen en el
  del modelo).
- Materiales (5): gunmetal (caño, cajón, bloque, martillo, palanca) · brass (mira, cantonera) · iron detalle
  (chapas, bases y abrazaderas de la mira, puntera de la caña, gatillo, tornillos) · wood_mid · coal (huecos).
- Tallado: boca, recámara, mortaja del bloque, los dos agujeros de la palanca, ranura del gatillo, ocular.

Inferido (el prompt no lo dice)
- El gatillo no figura como pieza: va fijo en Body, adentro del aro de la palanca (pasa por una ranura).
- El bloque cae por una mortaja cerrada a los costados (se ve arriba y abajo del cajón, no de costado).
- Chapa de la llave a la derecha (donde gira el martillo) y una igual a la izquierda, sobre la muñeca.
- La mira empieza sobre el bloque (z -0,2 del cajón) y termina 0,32 antes de la boca; bases de hierro.
- El costado del bloque se marca con un rebaje de 0,008 en el cajón (de costado no se ve el bloque).

Vueltas: 1) primera versión: Body con ~300 bordes no-manifold después del chanflán + la booleana; buje de
la palanca y cubo del martillo con una cara en el mismo plano que su perfil · 2) caña más ancha que el caño,
chapas más bajas, buje 0,004 afuera y cubo sin cara común: palanca y martillo bien, Body igual · 3) con un
script que construye salteando una forma por vez: el culpable era el gatillo, con la cara de arriba en el
mismo plano que la de abajo de la muñeca (y = -0,165) · 4) gatillo subido y como detalle (cóncavo y fino,
el chanflán lo rompía igual) · 5-6) rebaje del costado del bloque.

Revisión
- 2426 triángulos contra 900 de referencia (calidad primero): la mira (508, con ocular, objetivo y
  abrazaderas), el martillo enrulado y estriado (412), la palanca con dos agujeros de verdad (352) y los
  chanflanes del cajón y el caño. Cada pieza muy por debajo de 10 000.
- BreechBlock no toca el cuerpo: a propósito (corre adentro de la mortaja).
- El rebaje del costado del bloque es sutil: de costado, con luz plana, casi no se ve; de 3/4 sí.
"""

import math

OFF = (0.0, 0.07, -0.17)          # centro de la muñeca en espacio del rifle -> origen del modelo
REC_FRONT, MUZZLE_Z = -0.42, -2.42
FLAT_R, FLAT_F = 0.055, 0.047     # medio ancho entre caras del octógono, atrás y en la boca
HW = 0.075
SCOPE_Y, SCOPE_R, SCOPE_REAR, SCOPE_LEN = 0.145, 0.045, -0.20, 1.9
LEVER_PIVOT = (0.0, -0.19, -0.38)
HAMMER_PIVOT = (0.07, -0.02)      # (z, y), a la derecha


def P(x, y, z):
    return (x + OFF[0], y + OFF[1], z + OFF[2])


def PP(points):
    return [P(*p) for p in points]


def ring(z, ybot, ytop, hw, c=0.35):
    k = min(hw, (ytop - ybot) / 2) * c
    pts = []
    for s in (-1, 1):
        pts += [(s * (hw - k), ytop, z), (s * hw, ytop - k, z), (s * hw, ybot + k, z), (s * (hw - k), ybot, z)]
    return pts


def band(path, half):
    """Contorno (z, y) de una tira que sigue `path` con medio ancho `half[k]` en cada punto."""
    top, bot = [], []
    for k, (z, y) in enumerate(path):
        za, ya = path[max(k - 1, 0)]
        zb, yb = path[min(k + 1, len(path) - 1)]
        ln = math.hypot(zb - za, yb - ya)
        nz, ny = -(yb - ya) / ln, (zb - za) / ln
        top.append((z + nz * half[k], y + ny * half[k]))
        bot.append((z - nz * half[k], y - ny * half[k]))
    return top + list(reversed(bot))


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- cajón ----------------
    rec = [(REC_FRONT, 0.075), (REC_FRONT, -0.13), (-0.39, -0.17), (0.0, -0.17), (0.03, -0.14), (0.03, 0.04),
           (0.0, 0.075)]
    mk.prism(body, rec, 2 * HW, "gunmetal", plane="zy", center=P(0, 0, 0))
    # ---------------- caño octogonal pesado (caras planas arriba y a los lados) ----------------
    z0 = REC_FRONT + 0.02
    rb, rf = FLAT_R / math.cos(math.pi / 8), FLAT_F / math.cos(math.pi / 8)
    mk.cyl(body, P(0, 0, (z0 + MUZZLE_Z) / 2), rf, z0 - MUZZLE_Z, "gunmetal", axis="z", sides=8, top=rb / rf)
    # ---------------- caña con puntera de hierro ----------------
    fore_end = -1.10
    mk.hull(body, PP(ring(REC_FRONT + 0.01, -0.13, 0.0, 0.068) + ring(fore_end, -0.115, 0.0, 0.064)), "wood_mid")  # más ancha que el caño: sin caras casi paralelas
    mk.hull(body, PP(ring(fore_end + 0.005, -0.12, 0.004, 0.069) + ring(fore_end - 0.07, -0.105, 0.004, 0.062)),
            "iron")
    # ---------------- muñeca recta y culata ----------------
    mk.hull(body, PP(ring(0.02, -0.165, 0.035, 0.058) + ring(0.32, -0.17, -0.03, 0.052)), "wood_mid")
    mk.hull(body, PP(ring(0.31, -0.17, -0.03, 0.053) + ring(1.235, -0.51, -0.05, 0.095, c=0.3)), "wood_mid")
    butt = [(1.23, -0.043), (1.262, -0.043), (1.274, -0.15), (1.274, -0.40), (1.262, -0.516), (1.23, -0.516)]
    mk.prism(body, butt, 0.196, "brass", plane="zy", center=P(0, 0, 0))              # cantonera
    # ---------------- chapas de la llave (las dos), gatillo, bases de la mira ----------------
    lock = [(-0.035, -0.11), (-0.035, 0.022), (0.08, 0.026), (0.20, 0.0), (0.25, -0.04), (0.20, -0.09),
            (0.08, -0.118)]
    for s in (-1, 1):
        mk.prism(body, lock, 0.04, "iron", plane="zy", center=P(s * 0.065, 0, 0))     # x de 0,045 a 0,085
    mk.prism(body, [(0.03, -0.15), (0.065, -0.15), (0.06, -0.21), (0.075, -0.255), (0.055, -0.26), (0.04, -0.215)],
             0.035, "iron", plane="zy", center=P(0, 0, 0), detail=True)               # gatillo: detalle (cóncavo y fino, el chanflán + la booleana lo rompían)
    for z in (-0.33, -1.55):                                                           # bases de la mira
        top = 0.075 if z > REC_FRONT else FLAT_R
        mk.box(body, P(0, top + 0.016, z), (0.05, 0.05, 0.07), "iron")
    mk.bevel(body, width=0.012, angle=50)

    mk.carve(body, "coal", points=mk.pts_cyl(P(0, 0, MUZZLE_Z), 0.022, 0.12, axis="z", sides=8))      # boca
    mk.carve(body, "coal", points=mk.pts_box(P(0, 0, -0.09), (0.12, 0.40, 0.10)))                   # mortaja del bloque
    mk.carve(body, "coal", points=mk.pts_cyl(P(0, 0, -0.20), 0.026, 0.14, axis="z", sides=8))       # recámara
    for s in (-1, 1):                                                                  # costado del bloque, hundido
        mk.carve(body, "gunmetal", points=mk.pts_box(P(s * (HW + 0.016), -0.05, -0.09), (0.048, 0.225, 0.088)))
    for s in (-1, 1):                                                                  # tornillos de las chapas
        for z, y in ((0.0, -0.06), (0.17, -0.04)):
            mk.cyl(body, P(s * 0.086, y, z), 0.015, 0.02, "iron", axis="x", sides=6, detail=True)
    mk.cyl(body, P(-0.086, HAMMER_PIVOT[1], HAMMER_PIVOT[0]), 0.018, 0.02, "iron", axis="x", sides=6, detail=True)

    # ---------------- bloque que cae ----------------
    blk = mk.part("BreechBlock", P(0, 0.065, -0.136))
    mk.box(blk, P(0, -0.05, -0.09), (0.112, 0.23, 0.092), "gunmetal")
    mk.bevel(blk, width=0.006, angle=35)
    mk.carve(blk, "coal", points=mk.pts_cyl(P(0, 0, -0.136), 0.008, 0.03, axis="z", sides=6))     # aguja

    # ---------------- martillo lateral (derecha) ----------------
    hz, hy = HAMMER_PIVOT
    hx = 0.103
    ham = mk.part("Hammer", P(hx, hy, hz))
    spine = [(0.075, -0.03), (0.06, 0.02), (0.035, 0.06), (0.03, 0.095), (0.06, 0.125), (0.11, 0.14), (0.155, 0.13),
             (0.17, 0.105)]
    half = [0.03, 0.027, 0.025, 0.023, 0.02, 0.018, 0.017, 0.015]
    mk.prism(ham, band(spine, half), 0.034, "gunmetal", plane="zy", center=P(hx, 0, 0))
    mk.prism(ham, [(-0.02, 0.05), (0.01, 0.045), (0.045, 0.085), (0.035, 0.11), (0.0, 0.085), (-0.02, 0.068)],
             0.032, "gunmetal", plane="zy", center=P(hx - 0.004, 0, 0))                 # nariz
    mk.cyl(ham, P(hx - 0.002, hy, hz), 0.03, 0.042, "gunmetal", axis="x", sides=8)   # cubo: entra en la chapa, sin cara común con el perfil
    mk.bevel(ham, width=0.006, angle=35)
    for k in range(3):
        mk.carve(ham, "coal", points=mk.pts_box(P(hx, 0.16, 0.08 + 0.022 * k), (0.06, 0.02, 0.007)))

    # ---------------- palanca-guardamonte en S ----------------
    lev = mk.part("Lever", P(*LEVER_PIVOT))
    outer = [(-0.40, -0.192), (-0.385, -0.175), (0.30, -0.186), (0.335, -0.20), (0.345, -0.235), (0.325, -0.27),
             (0.28, -0.285), (0.22, -0.275), (0.17, -0.262), (0.13, -0.29), (0.06, -0.312), (-0.01, -0.305),
             (-0.06, -0.28), (-0.085, -0.235), (-0.10, -0.205), (-0.25, -0.205), (-0.385, -0.21)]
    mk.prism(lev, outer, 0.06, "gunmetal", plane="zy", center=P(0, 0, 0))
    mk.cyl(lev, P(*LEVER_PIVOT), 0.026, 0.068, "gunmetal", axis="x", sides=8)      # buje, 0,004 afuera de cada lado
    mk.bevel(lev, width=0.007, angle=35)
    guard = [(-0.055, -0.215), (0.12, -0.215), (0.125, -0.25), (0.09, -0.28), (0.02, -0.285), (-0.035, -0.268),
             (-0.062, -0.24)]
    finger = [(0.165, -0.215), (0.30, -0.212), (0.31, -0.235), (0.29, -0.258), (0.24, -0.262), (0.19, -0.245)]
    for hole in (guard, finger):
        mk.carve(lev, "gunmetal", prism=dict(profile=hole, depth=0.2, plane="zy", center=P(0, 0, 0)))
    mk.carve(lev, "coal", points=mk.pts_box(P(0, -0.20, 0.05), (0.042, 0.06, 0.05)))   # ranura del gatillo
    mk.cyl(lev, P(*LEVER_PIVOT), 0.014, 0.066, "iron", axis="x", sides=6, detail=True)  # perno

    # ---------------- mira de bronce ----------------
    sc = mk.part("Scope", (0, 0, 0))
    front = SCOPE_REAR - SCOPE_LEN
    mk.cyl(sc, P(0, SCOPE_Y, (SCOPE_REAR + front) / 2), SCOPE_R, SCOPE_LEN - 0.1, "brass", axis="z", sides=10)
    mk.cyl(sc, P(0, SCOPE_Y, SCOPE_REAR - 0.055), SCOPE_R + 0.011, 0.11, "brass", axis="z", sides=10,
           top=1.0)                                                                    # ocular, más ancho
    mk.cyl(sc, P(0, SCOPE_Y, front + 0.035), SCOPE_R + 0.006, 0.07, "brass", axis="z", sides=10)  # objetivo
    for z in (-0.33, -1.55):                                                           # abrazaderas
        base_top = (0.075 if z > REC_FRONT else FLAT_R) + 0.041
        mk.cyl(sc, P(0, SCOPE_Y, z), SCOPE_R + 0.012, 0.045, "iron", axis="z", sides=10)
        mk.box(sc, P(0, (base_top + SCOPE_Y) / 2, z), (0.03, SCOPE_Y - base_top + 0.004, 0.035), "iron")
    mk.bevel(sc, width=0.008, angle=40)
    mk.carve(sc, "coal", points=mk.pts_cyl(P(0, SCOPE_Y, SCOPE_REAR), SCOPE_R - 0.008, 0.05, axis="z", sides=10))
    mk.carve(sc, "coal", points=mk.pts_cyl(P(0, SCOPE_Y, front), SCOPE_R - 0.01, 0.05, axis="z", sides=10))

    # ---------------- marcadores ----------------
    mk.marker("_Muzzle", P(0, 0, MUZZLE_Z))
    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Grip2", P(0, -0.13, -0.80))
    mk.marker("_Eject", P(0, 0.08, -0.09))
    mk.marker("_Chamber", P(0, 0, -0.14))
    mk.marker("_Scope", P(0, SCOPE_Y, SCOPE_REAR))

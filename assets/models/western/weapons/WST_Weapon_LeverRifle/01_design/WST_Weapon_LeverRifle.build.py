"""
Receta de WST_Weapon_LeverRifle, rifle de palanca estilo 1873 (prompt 028, Bloques A + F).

Brief
- Silueta a 30 studs: caño largo con el tubo cargador abajo, cajón de bronce gordo (el rasgo que lo
  identifica), aro de la palanca grande colgando bajo la muñeca, culata recta con cantonera de media luna.
- Medidas: largo 3,2 (caño 1,6), alto 0,65 en la culata (de la punta de la cantonera a la espuela del
  martillo), ancho ~0,17 (el cajón, 0,15). Se arma en "espacio del rifle" (eje del caño en y = 0, fondo
  del cajón en z = 0) y P() lo corre para que el centro de la muñeca quede en (0,0,0).
- Piezas móviles con el origen en su eje: Lever (punta de adelante, gira 50° para abajo), Bolt (punta de
  adelante, corre 0,25 para atrás por un canal arriba del cajón), LoadingGate (bisagra de adelante, se
  hunde 15° en su hueco), Hammer (base), Trigger (arriba, pasa por una ranura de la palanca). Body fijo.
- Materiales (5): gunmetal metal principal (caño, tubo, palanca, cerrojo, martillo, gatillo, tapa) ·
  brass (cajón, cantonera, puntera de la caña) · steel_light detalle (miras, tornillos, tapón del tubo) ·
  wood_mid (culata y caña) · coal (huecos).
- Tallado: boca del caño, canal del cerrojo, ranura del martillo, hueco de la tapa de carga, aro de la
  palanca (agujero de verdad) y ranura del gatillo. Chanflanes en el cajón, puntas del caño y la palanca.

Inferido (el prompt no lo dice)
- Cerrojo, martillo, gatillo y tapa de carga en gunmetal (oscuros sobre el bronce, para que se lean).
- Abrazadera del tubo cargador cerca de la boca y tornillo-tapón en la punta del tubo.
- Forma del aro de la palanca: un solo aro grande para los dedos con el gatillo adelante.
- Chapas laterales del cajón hundidas 0,008 (segundo nivel de detalle en el bronce).

Vueltas: 1) primera versión: silueta y medidas bien (3,19 x 0,65 x 0,17); el cajón era una losa de
bronce lisa en el primer plano y el cerrojo tenía una cara degenerada (estrías talladas sobre el chanflán
de un octógono) · 2) chapas laterales hundidas, cerrojo con chanflán solo en las puntas y estrías más
angostas; tornillos encastrados 0,011 en la chapa (si no, quedaban apoyados en el fondo de la chapa).

Revisión
- 1788 triángulos contra 900 de referencia (calidad primero): chanflanes del cajón, caño y palanca, el aro
  con agujero de verdad, los huecos tallados (canal del cerrojo, ranura del martillo, tapa de carga, chapas)
  y el detalle de la boca (abrazadera, tapón, mira). Cada pieza bien por debajo de 10 000.
- Bolt, Hammer y LoadingGate no tocan el cuerpo: a propósito (corren o giran dentro de su canal o hueco).
- Ancho 0,17 contra 0,2: el cajón de 0,15 ya es más gordo que el caño (0,09); más ancho se veía de caja.
"""

import math

OFF = (0.0, 0.10, -0.17)          # centro de la muñeca en espacio del rifle -> origen del modelo
BARREL_R, MAG_R, MAG_Y = 0.045, 0.035, -0.077
REC_FRONT, MUZZLE_Z, MAG_END = -0.46, -2.06, -1.76
FORE_END = -1.02
HW = 0.075                        # medio ancho del cajón
LEVER_PIVOT = (0.0, -0.196, -0.42)


def P(x, y, z):
    return (x + OFF[0], y + OFF[1], z + OFF[2])


def PP(points):
    return [P(*p) for p in points]


def ring(z, ybot, ytop, hw, c=0.35):
    """Sección octogonal (espacio del rifle) a la altura z: caja de ybot a ytop con las esquinas cortadas."""
    k = min(hw, (ytop - ybot) / 2) * c
    pts = []
    for s in (-1, 1):
        pts += [(s * (hw - k), ytop, z), (s * hw, ytop - k, z), (s * hw, ybot + k, z), (s * (hw - k), ybot, z)]
    return pts


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- cajón de bronce ----------------
    rec = [(REC_FRONT, 0.065), (REC_FRONT, -0.15), (-0.43, -0.175), (0.0, -0.175), (0.04, -0.15), (0.045, -0.02),
           (0.0, 0.07), (-0.06, 0.085), (-0.44, 0.085)]
    mk.prism(body, rec, 2 * HW, "brass", plane="zy", center=P(0, 0, 0))
    # ---------------- caño, tubo cargador, abrazadera ----------------
    z0 = REC_FRONT + 0.02                                                              # el caño entra 0,02 en el cajón
    mk.cyl(body, P(0, 0, (z0 + MUZZLE_Z) / 2), BARREL_R, z0 - MUZZLE_Z, "gunmetal", axis="z", sides=12,
           rot=(0, 0, 15))                                                             # arista abajo: sin cara paralela al tubo
    mk.cyl(body, P(0, MAG_Y, (z0 + MAG_END) / 2), MAG_R, z0 - MAG_END, "gunmetal", axis="z", sides=12)
    band = mk.pts_cyl(P(0, 0, -1.70), BARREL_R + 0.011, 0.045, axis="z", sides=12, rot=(0, 0, 15)) + \
        mk.pts_cyl(P(0, MAG_Y, -1.70), MAG_R + 0.011, 0.045, axis="z", sides=12)
    mk.hull(body, band, "gunmetal")                                                    # abrazadera
    # ---------------- caña (recta) y su puntera de bronce ----------------
    mk.hull(body, PP(ring(REC_FRONT + 0.01, -0.15, 0.0, 0.06) + ring(FORE_END, -0.145, 0.0, 0.058)), "wood_mid")
    mk.hull(body, PP(ring(FORE_END + 0.005, -0.153, 0.004, 0.064) + ring(FORE_END - 0.045, -0.15, 0.004, 0.062)),
            "brass")
    # ---------------- muñeca y culata recta ----------------
    mk.hull(body, PP(ring(0.03, -0.175, -0.02, 0.055) + ring(0.30, -0.19, -0.045, 0.05)), "wood_mid")      # muñeca
    mk.hull(body, PP(ring(0.29, -0.19, -0.045, 0.051) + ring(1.05, -0.48, -0.05, 0.08, c=0.3)), "wood_mid")  # culata
    crescent = [(1.045, -0.045), (1.12, -0.04), (1.095, -0.11), (1.085, -0.26), (1.10, -0.40), (1.135, -0.49),
                (1.045, -0.49)]
    mk.prism(body, crescent, 0.172, "brass", plane="zy", center=P(0, 0, 0))          # cantonera de media luna
    mk.bevel(body, width=0.012, angle=50)

    mk.carve(body, "coal", points=mk.pts_cyl(P(0, 0, MUZZLE_Z), 0.02, 0.12, axis="z", sides=8))       # boca
    mk.carve(body, "coal", points=mk.pts_box(P(0, 0.085, -0.175), (0.068, 0.10, 0.49)))              # canal del cerrojo
    mk.carve(body, "coal", points=mk.pts_box(P(0, 0.045, 0.01), (0.054, 0.17, 0.12)))                # ranura del martillo
    mk.carve(body, "coal", points=mk.pts_box(P(0.065, -0.0825, -0.29), (0.11, 0.075, 0.15)))         # hueco de la tapa
    panel = [(-0.425, 0.05), (-0.425, -0.13), (-0.40, -0.15), (-0.06, -0.15), (-0.035, -0.125), (-0.035, 0.02),
             (-0.06, 0.05)]
    for s in (-1, 1):                                                                   # chapas laterales hundidas
        mk.carve(body, "brass", prism=dict(profile=panel, depth=0.016, plane="zy", center=P(s * HW, 0, 0)))
    # ---------------- detalle: miras, tornillos, tapón ----------------
    mk.box(body, P(0, 0.06, -2.0), (0.024, 0.06, 0.08), "steel_light", top=(1, 0.55), detail=True)   # mira de adelante
    buck = [(-0.05, 0.03), (0.05, 0.03), (0.056, 0.06), (0.07, 0.112), (0.046, 0.106), (0.02, 0.076), (0.0, 0.066),
            (-0.02, 0.076), (-0.046, 0.106), (-0.07, 0.112), (-0.056, 0.06)]
    mk.prism(body, buck, 0.03, "steel_light", plane="xy", center=P(0, 0, -0.82), detail=True)        # mira de cuerno
    mk.cyl(body, P(0, MAG_Y, MAG_END - 0.012), 0.026, 0.03, "steel_light", axis="z", sides=8, detail=True)  # tapón
    for s in (-1, 1):
        for y, z in ((0.0, 0.0), (-0.035, -0.13), (0.03, -0.40)):                     # el de (0, 0): eje del martillo
            mk.cyl(body, P(s * (HW - 0.001), y, z), 0.016, 0.026, "steel_light", axis="x", sides=6, detail=True)

    # ---------------- tapa de carga (derecha) ----------------
    gate = mk.part("LoadingGate", P(0.067, -0.0825, -0.355))
    mk.box(gate, P(0.067, -0.0825, -0.285), (0.024, 0.063, 0.135), "gunmetal")
    mk.bevel(gate, width=0.006, angle=35)

    # ---------------- cerrojo arriba del cajón ----------------
    bolt = mk.part("Bolt", P(0, 0.075, -0.40))
    mk.cyl(bolt, P(0, 0.075, -0.27), 0.03, 0.26, "gunmetal", axis="z", sides=8)       # caras planas arriba y a los lados
    mk.bevel(bolt, width=0.006, angle=50)
    for z in (-0.185, -0.165):                                                          # estrías de agarre
        mk.carve(bolt, "coal", points=mk.pts_box(P(0, 0.105, z), (0.036, 0.02, 0.008)))

    # ---------------- martillo ----------------
    ham = mk.part("Hammer", P(0, 0.0, 0.0))
    mk.hull(ham, PP([(x, y, z) for x in (-0.022, 0.022) for z, y in
                     ((-0.025, -0.025), (0.03, -0.025), (-0.012, 0.10), (0.03, 0.092))]), "gunmetal")
    mk.hull(ham, PP([(x, y, z) for x in (-0.03, 0.03) for z, y in
                     ((0.0, 0.088), (0.04, 0.08), (0.105, 0.14), (0.09, 0.162), (0.03, 0.12))]), "gunmetal")
    mk.bevel(ham, width=0.006, angle=35)
    for i in range(3):
        z, y = 0.06 + 0.014 * i, 0.135 + 0.011 * i
        mk.carve(ham, "coal", points=mk.pts_box(P(0, y + 0.02, z - 0.012), (0.09, 0.008, 0.03), rot=(-40, 0, 0)))

    # ---------------- gatillo ----------------
    trig = mk.part("Trigger", P(0, -0.175, -0.025))
    mk.prism(trig, [(-0.04, -0.168), (-0.01, -0.168), (-0.013, -0.215), (0.0, -0.265), (-0.02, -0.272),
                    (-0.036, -0.222)], 0.035, "gunmetal", plane="zy", center=P(0, 0, 0))
    mk.bevel(trig, width=0.005, angle=35)

    # ---------------- palanca: aro grande con agujero de verdad ----------------
    lever = mk.part("Lever", P(*LEVER_PIVOT))
    outer = [(-0.45, -0.196), (-0.43, -0.179), (-0.06, -0.179), (0.05, -0.18), (0.17, -0.186), (0.25, -0.191),
             (0.30, -0.21), (0.31, -0.27), (0.275, -0.335), (0.20, -0.372), (0.02, -0.377), (-0.08, -0.348),
             (-0.118, -0.27), (-0.10, -0.213), (-0.30, -0.213), (-0.43, -0.213)]
    mk.prism(lever, outer, 0.07, "gunmetal", plane="zy", center=P(0, 0, 0))
    mk.cyl(lever, P(0, LEVER_PIVOT[1], LEVER_PIVOT[2]), 0.03, 0.07, "gunmetal", axis="x", sides=8)  # buje
    mk.bevel(lever, width=0.008, angle=35)
    inner = [(-0.07, -0.222), (0.24, -0.226), (0.265, -0.262), (0.24, -0.31), (0.18, -0.338), (0.03, -0.342),
             (-0.05, -0.318), (-0.083, -0.27)]
    mk.carve(lever, "gunmetal", prism=dict(profile=inner, depth=0.2, plane="zy", center=P(0, 0, 0)))  # aro
    mk.carve(lever, "coal", points=mk.pts_box(P(0, -0.196, -0.022), (0.045, 0.06, 0.05)))            # ranura gatillo
    mk.cyl(lever, P(0, LEVER_PIVOT[1], LEVER_PIVOT[2]), 0.017, 0.076, "steel_light", axis="x", sides=6,
           detail=True)                                                                 # perno

    # ---------------- marcadores ----------------
    mk.marker("_Muzzle", P(0, 0, MUZZLE_Z))
    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Grip2", P(0, -0.15, -0.74))
    mk.marker("_Eject", P(0, 0.09, -0.33))
    mk.marker("_Load", P(0.08, -0.0825, -0.29))

"""
Receta de WST_Weapon_Revolver, el revólver de acción simple (prompt 002, Bloques A + F).

Brief
- Silueta que se lee a 30 studs: caño largo y fino octogonal, cilindro gordo con estrías, cacha curva
  tipo "plow handle", espuela del martillo grande (se abanica en el duelo).
- Lenguaje de armas estilizadas de juegos conocidos (sin copiar ninguna): proporciones exageradas,
  chanflanes que agarran luz, materiales bien separados (acero, bronce, madera), mecánica legible.
- Medidas: largo 1,3 (caño 0,6), cilindro 0,3 x 0,27 de diámetro. Origen = centro de la empuñadura,
  caño hacia -Z. Se construye en "espacio del armazón" y P() lo corre para que la mano quede en (0,0,0).
- Piezas móviles con el origen en su eje: Cylinder (eje), LoadingGate (bisagra abajo), EjectorRod
  (punta de adelante), Hammer (base), Trigger (arriba). Body y Grip, fijos.
- Tallado: boca del caño, bocas de las recámaras, hueco de la tapa, ranura de la mira, estriado del
  martillo. Chanflanes: armazón, cilindro (filo gastado en acero claro), martillo, cacha, tapa, gatillo.
- Inferido: alturas del armazón, forma de la cacha, armazón de bronce a la vista en la cacha.

Vueltas: 1) primera versión · 2) cacha 0,15 de ancho (coincidía con la base del armazón) ·
3) cacha proporcionada, armazón inclinado atrás, espuela 40 % más grande · 4) estrías en el contorno
del cilindro (prisma de 12 puntos) en vez de 6 booleanas · 5) calidad primero: chanflanes, boca del
caño hueca, anillo del caño, perno, ranura de la mira, estriado del martillo, cacha con armazón de
bronce y paneles de madera con medallón, cabeza de bulbo en la varilla · 6) correa de arriba apoyada
en el cilindro (de costado se veía el fondo, 0,025 de luz).

Revisión
- Alto 0,78 en vez de 0,55: el prompt pide cilindro de 0,27 de diámetro y 0,55 de alto, y con una cacha
  proporcionada no entran juntos. Se priorizó el cilindro gordo (prioridad de silueta del prompt).
  Para 0,55 habría que bajar el cilindro a ~0,20: decide Valentin.
- Ancho 0,27 (el del cilindro) en vez de 0,2: misma causa.
- LoadingGate no toca el armazón: es a propósito (costura para que se abra).
- 2000 triángulos contra un tope de 800 (calidad primero, decisión de Valentin del 2026-10-28): los
  chanflanes de todas las piezas (~900) y el detalle mecánico (boca hueca, perno, tornillos, estriado,
  medallones). Sin chanflanes queda en ~1100 y se ve de caja.
"""

import math

OFF = (0.0, 0.07, -0.10)            # centro de la empuñadura en espacio del armazón -> origen del modelo
CYL_Y, CYL_Z, CYL_R, CYL_L = 0.24, -0.27, 0.135, 0.30
BARREL_Y = CYL_Y + 0.085            # el caño se alinea con la recámara de arriba
MUZZLE_Z = -1.065
CHAMBER = (0.0736, CYL_Y - 0.0425, -0.12)   # recámara a las 4, la que queda detrás de la tapa


def P(x, y, z):
    return (x + OFF[0], y + OFF[1], z + OFF[2])


def PP(points):
    return [P(*p) for p in points]


def shrink(profile, k):
    """El mismo perfil achicado hacia su centro (paneles de madera dentro del armazón de la cacha)."""
    cx = sum(a for a, _ in profile) / len(profile)
    cy = sum(b for _, b in profile) / len(profile)
    return [(cx + (a - cx) * k, cy + (b - cy) * k) for a, b in profile]


def build(mk):
    # ---------------- armazón y caño ----------------
    body = mk.part("Body", (0, 0, 0))
    mk.box(body, P(0, 0.392, -0.25), (0.13, 0.05, 0.44), "gunmetal")                    # correa de arriba (apoya en el cilindro)
    mk.hull(body, PP([(x, y, z) for x, y in ((-0.075, 0.42), (0.075, 0.42), (-0.06, 0.09), (0.06, 0.09))
                      for z in (-0.50, -0.43)]), "gunmetal")                              # frente del armazón
    mk.hull(body, PP([(x, y, z) for x in (-0.07, 0.07) for y, z in
                      ((0.05, -0.49), (0.10, -0.49), (0.05, 0.0), (0.11, 0.0))]), "gunmetal")   # base
    mk.hull(body, PP([(x, y, z) for x in (-0.085, 0.085) for y, z in ((0.41, -0.12), (0.07, -0.12))]
                     + [(x, y, z) for x in (-0.06, 0.06) for y, z in ((0.39, -0.03), (0.30, 0.05), (0.08, 0.07))]),
            "gunmetal")                                                                   # escudo, inclinado atrás
    mk.cyl(body, P(0, BARREL_Y, -0.785), 0.06, 0.56, "gunmetal", axis="z", sides=8)    # caño octogonal
    mk.cyl(body, P(0, BARREL_Y, -0.525), 0.072, 0.07, "gunmetal", axis="z", sides=8)   # anillo donde entra el caño
    mk.cyl(body, P(0.055, 0.255, -0.71), 0.032, 0.42, "gunmetal", axis="z", sides=6)   # funda de la varilla
    mk.cyl(body, P(0.055, 0.255, -0.505), 0.04, 0.05, "gunmetal", axis="z", sides=6)   # tope de la funda
    guard = [(-0.16, 0.07), (-0.15, -0.03), (-0.10, -0.09), (0.0, -0.09), (0.04, -0.03), (0.05, 0.07),
             (0.0, 0.07), (-0.005, -0.02), (-0.03, -0.045), (-0.09, -0.045), (-0.11, -0.02), (-0.11, 0.07)]
    mk.prism(body, guard, 0.06, "brass", plane="zy", center=P(0, 0, 0))                # guardamonte en U
    mk.bevel(body, width=0.012, angle=35)
    mk.carve(body, "coal", points=mk.pts_cyl(P(0, BARREL_Y, MUZZLE_Z), 0.027, 0.16, axis="z", sides=8))  # boca del caño
    mk.carve(body, "coal", points=mk.pts_box(P(0.11, 0.20, -0.075), (0.10, 0.10, 0.072)))               # hueco de la tapa
    mk.carve(body, "gunmetal", points=mk.pts_box(P(0, 0.42, -0.10), (0.03, 0.03, 0.26), rot=(0, 0, 45)))   # ranura de la mira
    mk.box(body, P(0, BARREL_Y + 0.075, -1.02), (0.06, 0.07, 0.09), "steel_light", top=(1, 0.5), detail=True)  # mira
    mk.cyl(body, P(0, CYL_Y, -0.49), 0.022, 0.08, "steel_light", axis="z", sides=6, detail=True)       # perno del cilindro
    for x, y, z in ((0.086, 0.33, -0.07), (0.086, 0.13, -0.05), (0.071, 0.08, -0.40)):                # tornillos
        mk.cyl(body, P(x, y, z), 0.018, 0.03, "steel_light", axis="x", sides=6, detail=True)

    # ---------------- cilindro: estrías en el contorno, filos gastados ----------------
    cyl = mk.part("Cylinder", P(0, CYL_Y, CYL_Z))
    star = [((CYL_R if k % 2 == 0 else CYL_R - 0.024) * math.cos(math.radians(30 * k)),
             (CYL_R if k % 2 == 0 else CYL_R - 0.024) * math.sin(math.radians(30 * k))) for k in range(12)]
    mk.prism(cyl, star, CYL_L, "gunmetal", plane="xy", center=P(0, CYL_Y, CYL_Z))
    mk.bevel(cyl, width=0.012, angle=40, mat="steel_light")
    for k in range(6):                                                                  # bocas de las recámaras
        a = math.radians(90 + 60 * k)
        mk.carve(cyl, "coal", points=mk.pts_cyl(P(math.cos(a) * 0.085, CYL_Y + math.sin(a) * 0.085, CYL_Z - CYL_L / 2),
                                                0.032, 0.07, axis="z", sides=6))
    mk.cyl(cyl, P(0, CYL_Y, CYL_Z - CYL_L / 2 - 0.01), 0.03, 0.03, "steel_light", axis="z", sides=6, detail=True)  # buje

    # ---------------- tapa de carga ----------------
    gate = mk.part("LoadingGate", P(0.085, 0.155, -0.075))
    mk.box(gate, P(0.085, 0.20, -0.075), (0.045, 0.085, 0.062), "gunmetal", top=(0.8, 1))
    mk.bevel(gate, width=0.006, angle=35)

    # ---------------- varilla expulsora ----------------
    rod = mk.part("EjectorRod", P(0.055, 0.255, -0.95))
    mk.cyl(rod, P(0.055, 0.255, -0.755), 0.018, 0.39, "steel_light", axis="z", sides=6)
    mk.ball(rod, P(0.055, 0.255, -0.94), 0.034, "steel_light", scale=(1.0, 1.0, 0.8))      # cabeza de bulbo

    # ---------------- martillo: espuela grande, estriada ----------------
    ham = mk.part("Hammer", P(0, 0.30, -0.01))
    mk.hull(ham, PP([(x, y, z) for x in (-0.04, 0.04) for y, z in
                     ((0.26, -0.03), (0.26, 0.04), (0.38, -0.04), (0.38, 0.05))]), "steel_light")
    mk.hull(ham, PP([(x, y, z) for x in (-0.045, 0.045) for y, z in
                     ((0.36, -0.01), (0.40, 0.05), (0.51, 0.14), (0.49, 0.19), (0.44, 0.15))]), "steel_light")
    mk.bevel(ham, width=0.008, angle=35)
    for i in range(3):                                                                  # estriado de agarre
        y, z = 0.465 + 0.014 * i, 0.135 + 0.016 * i
        mk.carve(ham, "iron", points=mk.pts_box(P(0, y + 0.03, z - 0.02), (0.12, 0.012, 0.03), rot=(40, 0, 0)))

    # ---------------- gatillo ----------------
    trig = mk.part("Trigger", P(0, 0.07, -0.05))
    mk.prism(trig, [(-0.07, 0.07), (-0.03, 0.07), (-0.035, 0.0), (-0.05, -0.04), (-0.08, -0.035), (-0.065, 0.0)],
             0.06, "steel_light", plane="zy", center=P(0, 0, 0))
    mk.bevel(trig, width=0.006, angle=35)

    # ---------------- cacha: armazón de bronce a la vista, paneles de madera con medallón ----------------
    grip = mk.part("Grip", (0, 0, 0))
    frame = [(0.00, 0.08), (0.10, 0.10), (0.135, 0.00), (0.185, -0.13), (0.235, -0.205), (0.195, -0.265),
             (0.075, -0.265), (0.04, -0.13), (0.005, -0.02)]
    mk.prism(grip, frame, 0.11, "brass", plane="zy", center=P(0, 0, 0))                 # armazón de la cacha
    panel = shrink([(0.015, 0.06), (0.095, 0.075), (0.125, -0.005), (0.17, -0.13), (0.205, -0.20), (0.17, -0.24),
                    (0.085, -0.24), (0.05, -0.13), (0.02, -0.03)], 0.97)
    for s in (-1, 1):                                                                   # paneles de madera
        mk.prism(grip, panel, 0.035, "wood_mid", plane="zy", center=P(s * 0.065, 0, 0))
        mk.cyl(grip, P(s * 0.084, -0.10, 0.10), 0.022, 0.012, "brass", axis="x", sides=8, detail=True)   # medallón
    mk.bevel(grip, width=0.01, angle=35)
    mk.cyl(grip, P(0.084, -0.02, 0.07), 0.012, 0.012, "steel_light", axis="x", sides=6, detail=True)     # tornillo

    # ---------------- marcadores ----------------
    mk.marker("_Muzzle", P(0, BARREL_Y, MUZZLE_Z))
    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Eject", P(0.11, 0.20, -0.075))
    mk.marker("_Chamber", P(*CHAMBER))

"""
Receta de WST_Weapon_HanksWidow, La Viuda de Hank (prompt 022, Bloques A + F).

Brief
- Es el revólver base con la misma construcción, las mismas piezas y los mismos pivotes (recarga igual),
  pero se tiene que distinguir de un vistazo. Rasgos que se leen a 30 studs:
  1) acabado niquelado claro (steel_light) donde el base es gris oscuro, 2) caño 0,25 más largo
  (0,85), 3) cachas de hueso blancas, 4) la cinta negra de luto con dos colas colgando bajo la cacha.
  De cerca: la banda de volutas de bronce a los dos lados del armazón y las 6 muescas de la cacha derecha.
- Medidas: largo 1,55 (caño 0,85). Se construye en "espacio del armazón" como el revólver y P() lo
  corre para que la mano quede en (0,0,0). Origen = centro de la empuñadura, caño hacia -Z.
- Piezas móviles con el origen en su eje (iguales al revólver): Cylinder (eje), LoadingGate (bisagra
  abajo), EjectorRod (punta de adelante), Hammer (base), Trigger (arriba). Body, Grip y Ribbon, fijos.
- Materiales (6): steel_light metal principal · gunmetal metal de detalle (martillo, gatillo, varilla,
  mira, tornillos, perno) · brass (volutas, guardamonte, armazón de la cacha) · bone (cachas) ·
  cloth_black (cinta) · coal (huecos).
- Tallado: boca del caño, recámaras, hueco de la tapa, ranura de la mira, estriado del martillo, muescas.

Inferido (el prompt no lo dice)
- Martillo y gatillo en gunmetal (el prompt dice que el metal de detalle es gunmetal).
- Volutas: una banda ondulada de bronce por lado sobre la correa de abajo del armazón y el escudo, que
  termina en un rulo; el armazón de abajo es un poco más alto que en el revólver para que la banda entre.
- La cinta va atada alrededor de una culata de bronce que baja 0,035 más que la del revólver, justo debajo
  de las muescas (si la cinta tapaba el borde de abajo de la cacha, las muescas no se veían). Nudo atrás.

Vueltas: 1) primera versión: la banda de volutas (0,027 de alto, 3 ondas) se leía como un gusano y con
chanflán costaba ~600 triángulos; las colas de la cinta, de canto desde atrás, parecían palitos ·
2) banda de 0,038 con 2,5 ondas suaves y rulo, como detalle sin chanflán (Body 1680 -> 1426); colas giradas
35-40° y de largo distinto (0,25 y 0,22) · 3) el rulo tocaba la tapa de carga (no la dejaba abrir) y un
tornillo: rulo bajado a y <= 0,15 del armazón y tornillos de abajo corridos.

Revisión
- 2632 triángulos contra 800 de referencia (calidad primero): la base es la del revólver (1982) más las
  volutas (~300), la corona de la boca y dos tornillos (~70), las 6 muescas talladas (~110) y la cinta (80).
- Alto 1,03 contra 0,58 y ancho 0,26 contra 0,21: el armazón, el cilindro de 0,27 y la cacha son los del
  revólver base (alto 0,77, misma decisión pendiente que el revólver) y las colas de la cinta cuelgan 0,25
  debajo de la culata. Sin la cinta el alto es 0,80. Largo 1,61: 1,55 del arma más el nudo atrás.
- LoadingGate no toca el armazón: a propósito (costura para que se abra), igual que en el revólver.
"""

import math

OFF = (0.0, 0.07, -0.10)            # centro de la empuñadura en espacio del armazón -> origen del modelo
CYL_Y, CYL_Z, CYL_R, CYL_L = 0.24, -0.27, 0.135, 0.30
BARREL_Y = CYL_Y + 0.085            # el caño se alinea con la recámara de arriba
EXTRA = 0.25                        # caño 0,85 en vez de 0,6
MUZZLE_Z = -1.065 - EXTRA
CHAMBER = (0.0736, CYL_Y - 0.0425, -0.12)   # recámara a las 4, la que queda detrás de la tapa


def P(x, y, z):
    return (x + OFF[0], y + OFF[1], z + OFF[2])


def PP(points):
    return [P(*p) for p in points]


def shrink(profile, k):
    """El mismo perfil achicado hacia su centro (paneles dentro del armazón de la cacha)."""
    cx = sum(a for a, _ in profile) / len(profile)
    cy = sum(b for _, b in profile) / len(profile)
    return [(cx + (a - cx) * k, cy + (b - cy) * k) for a, b in profile]


def lerp_edge(p0, p1, b):
    """a (z) del borde entre p0 y p1 del perfil (a, b) a la altura b."""
    t = (b - p0[1]) / (p1[1] - p0[1])
    return p0[0] + (p1[0] - p0[0]) * t


def scroll_profile():
    """Banda de volutas en el plano zy (a = z, b = y, espacio del armazón): una onda por la correa de
    abajo que sube en un rulo sobre el escudo."""
    path = []
    n = 10
    for i in range(n + 1):                                   # tramo ondulado bajo el cilindro
        z = -0.455 + 0.40 * i / n
        path.append((z, 0.068 + 0.008 * math.sin(i / n * 2.5 * 2 * math.pi)))
    path += [(-0.02, 0.075), (0.004, 0.092), (0.012, 0.115), (0.0, 0.132), (-0.02, 0.13)]   # rulo, bajo la tapa
    half = 0.019
    top, bot = [], []
    for k, (z, y) in enumerate(path):
        za, ya = path[max(k - 1, 0)]
        zb, yb = path[min(k + 1, len(path) - 1)]
        tz, ty = zb - za, yb - ya
        ln = math.hypot(tz, ty)
        nz, ny = -ty / ln, tz / ln                              # normal del camino
        top.append((z + nz * half, y + ny * half))
        bot.append((z - nz * half, y - ny * half))
    return top + list(reversed(bot))


def build(mk):
    # ---------------- armazón y caño: niquelado, con la banda de volutas de bronce ----------------
    body = mk.part("Body", (0, 0, 0))
    mk.box(body, P(0, 0.392, -0.25), (0.13, 0.05, 0.44), "steel_light")                 # correa de arriba
    mk.hull(body, PP([(x, y, z) for x, y in ((-0.075, 0.42), (0.075, 0.42), (-0.06, 0.06), (0.06, 0.06))
                      for z in (-0.50, -0.43)]), "steel_light")                           # frente del armazón
    mk.hull(body, PP([(x, y, z) for x in (-0.07, 0.07) for y, z in
                      ((0.03, -0.49), (0.10, -0.49), (0.03, 0.0), (0.11, 0.0))]), "steel_light")   # base, más alta
    mk.hull(body, PP([(x, y, z) for x in (-0.085, 0.085) for y, z in ((0.41, -0.12), (0.05, -0.12))]
                     + [(x, y, z) for x in (-0.06, 0.06) for y, z in ((0.39, -0.03), (0.30, 0.05), (0.06, 0.07))]),
            "steel_light")                                                                # escudo, inclinado atrás
    mk.cyl(body, P(0, BARREL_Y, -0.785 - EXTRA / 2), 0.06, 0.56 + EXTRA, "steel_light", axis="z", sides=8)  # caño
    mk.cyl(body, P(0, BARREL_Y, -0.525), 0.072, 0.07, "steel_light", axis="z", sides=8)  # anillo donde entra el caño
    mk.cyl(body, P(0, BARREL_Y, MUZZLE_Z + 0.04), 0.066, 0.06, "steel_light", axis="z", sides=8)  # corona de la boca
    mk.cyl(body, P(0.055, 0.255, -0.71), 0.032, 0.42, "steel_light", axis="z", sides=6)  # funda de la varilla
    mk.cyl(body, P(0.055, 0.255, -0.505), 0.04, 0.05, "steel_light", axis="z", sides=6)  # tope de la funda
    guard = [(-0.16, 0.07), (-0.15, -0.03), (-0.10, -0.09), (0.0, -0.09), (0.04, -0.03), (0.05, 0.07),
             (0.0, 0.07), (-0.005, -0.02), (-0.03, -0.045), (-0.09, -0.045), (-0.11, -0.02), (-0.11, 0.07)]
    mk.prism(body, guard, 0.06, "brass", plane="zy", center=P(0, 0, 0))                # guardamonte en U
    mk.bevel(body, width=0.012, angle=35)
    for s in (-1, 1):                                                                   # volutas, 0,02 afuera
        mk.prism(body, scroll_profile(), 0.03, "brass", plane="zy", center=P(s * 0.075, 0, 0), detail=True)
    mk.carve(body, "coal", points=mk.pts_cyl(P(0, BARREL_Y, MUZZLE_Z), 0.027, 0.16, axis="z", sides=8))  # boca
    mk.carve(body, "coal", points=mk.pts_box(P(0.11, 0.20, -0.075), (0.10, 0.10, 0.072)))               # hueco tapa
    mk.carve(body, "gunmetal", points=mk.pts_box(P(0, 0.42, -0.10), (0.03, 0.03, 0.26), rot=(0, 0, 45)))  # ranura mira
    mk.box(body, P(0, BARREL_Y + 0.075, MUZZLE_Z + 0.045), (0.06, 0.07, 0.09), "gunmetal", top=(1, 0.5),
           detail=True)                                                                 # mira
    mk.cyl(body, P(0, CYL_Y, -0.49), 0.022, 0.08, "gunmetal", axis="z", sides=6, detail=True)          # perno
    for x, y, z in ((0.086, 0.33, -0.07), (0.086, 0.118, -0.085), (-0.086, 0.33, -0.07), (-0.086, 0.118, -0.085)):
        mk.cyl(body, P(x, y, z), 0.018, 0.03, "gunmetal", axis="x", sides=6, detail=True)             # tornillos

    # ---------------- cilindro niquelado ----------------
    cyl = mk.part("Cylinder", P(0, CYL_Y, CYL_Z))
    star = [((CYL_R if k % 2 == 0 else CYL_R - 0.024) * math.cos(math.radians(30 * k)),
             (CYL_R if k % 2 == 0 else CYL_R - 0.024) * math.sin(math.radians(30 * k))) for k in range(12)]
    mk.prism(cyl, star, CYL_L, "steel_light", plane="xy", center=P(0, CYL_Y, CYL_Z))
    mk.bevel(cyl, width=0.012, angle=40)
    for k in range(6):                                                                  # bocas de las recámaras
        a = math.radians(90 + 60 * k)
        mk.carve(cyl, "coal", points=mk.pts_cyl(P(math.cos(a) * 0.085, CYL_Y + math.sin(a) * 0.085, CYL_Z - CYL_L / 2),
                                                0.032, 0.07, axis="z", sides=6))
    mk.cyl(cyl, P(0, CYL_Y, CYL_Z - CYL_L / 2 - 0.01), 0.03, 0.03, "gunmetal", axis="z", sides=6, detail=True)  # buje

    # ---------------- tapa de carga (igual al revólver) ----------------
    gate = mk.part("LoadingGate", P(0.085, 0.155, -0.075))
    mk.box(gate, P(0.085, 0.20, -0.075), (0.045, 0.085, 0.062), "steel_light", top=(0.8, 1))
    mk.bevel(gate, width=0.006, angle=35)

    # ---------------- varilla expulsora (igual al revólver) ----------------
    rod = mk.part("EjectorRod", P(0.055, 0.255, -0.95))
    mk.cyl(rod, P(0.055, 0.255, -0.755), 0.018, 0.39, "gunmetal", axis="z", sides=6)
    mk.ball(rod, P(0.055, 0.255, -0.94), 0.034, "gunmetal", scale=(1.0, 1.0, 0.8))

    # ---------------- martillo ----------------
    ham = mk.part("Hammer", P(0, 0.30, -0.01))
    mk.hull(ham, PP([(x, y, z) for x in (-0.04, 0.04) for y, z in
                     ((0.26, -0.03), (0.26, 0.04), (0.38, -0.04), (0.38, 0.05))]), "gunmetal")
    mk.hull(ham, PP([(x, y, z) for x in (-0.045, 0.045) for y, z in
                     ((0.36, -0.01), (0.40, 0.05), (0.51, 0.14), (0.49, 0.19), (0.44, 0.15))]), "gunmetal")
    mk.bevel(ham, width=0.008, angle=35)
    for i in range(3):                                                                  # estriado
        y, z = 0.465 + 0.014 * i, 0.135 + 0.016 * i
        mk.carve(ham, "coal", points=mk.pts_box(P(0, y + 0.03, z - 0.02), (0.12, 0.012, 0.03), rot=(40, 0, 0)))

    # ---------------- gatillo ----------------
    trig = mk.part("Trigger", P(0, 0.07, -0.05))
    mk.prism(trig, [(-0.07, 0.07), (-0.03, 0.07), (-0.035, 0.0), (-0.05, -0.04), (-0.08, -0.035), (-0.065, 0.0)],
             0.06, "gunmetal", plane="zy", center=P(0, 0, 0))
    mk.bevel(trig, width=0.006, angle=35)

    # ---------------- cacha: armazón de bronce, paneles de hueso, 6 muescas en la derecha ----------------
    grip = mk.part("Grip", (0, 0, 0))
    frame = [(0.00, 0.08), (0.10, 0.10), (0.135, 0.00), (0.185, -0.13), (0.235, -0.205), (0.22, -0.30),
             (0.085, -0.30), (0.04, -0.13), (0.005, -0.02)]
    mk.prism(grip, frame, 0.11, "brass", plane="zy", center=P(0, 0, 0))                 # armazón y culata
    panel = shrink([(0.015, 0.06), (0.095, 0.075), (0.125, -0.005), (0.17, -0.13), (0.205, -0.20), (0.17, -0.24),
                    (0.085, -0.24), (0.05, -0.13), (0.02, -0.03)], 0.97)
    for s in (-1, 1):
        mk.prism(grip, panel, 0.035, "bone", plane="zy", center=P(s * 0.065, 0, 0))
    mk.bevel(grip, width=0.01, angle=35)
    bottom_b = min(b for _, b in panel)
    for i in range(6):                                                                  # muescas: borde de abajo
        a = 0.095 + 0.0135 * i
        mk.carve(grip, "coal", points=mk.pts_box(P(0.085, bottom_b + 0.012, a), (0.05, 0.05, 0.007)))
    for s in (-1, 1):
        mk.cyl(grip, P(s * 0.084, -0.02, 0.07), 0.013, 0.012, "gunmetal", axis="x", sides=6, detail=True)  # tornillo

    # ---------------- cinta de luto: vuelta a la culata, nudo atrás, dos colas ----------------
    rib = mk.part("Ribbon", (0, 0, 0))
    ring = []
    for b in (-0.252, -0.288):
        af = lerp_edge((0.04, -0.13), (0.085, -0.30), b) - 0.012
        ab = lerp_edge((0.235, -0.205), (0.22, -0.30), b) + 0.012
        for x, a in ((0.068, af + 0.02), (0.068, ab - 0.02), (0.05, af), (0.05, ab)):
            for s in (-1, 1):
                ring.append(P(s * x, b, a))
    mk.hull(rib, ring, "cloth_black")
    knot = P(0, -0.272, 0.238)
    mk.ball(rib, knot, 0.038, "cloth_black", scale=(1.3, 0.9, 0.7), subdiv=0)
    for s, length, tilt, yaw in ((1, 0.25, 12, 40), (-1, 0.22, -4, -35)):          # colas en V, caídas
        tail = [(-0.038, 0.02), (0.038, 0.02), (0.038, -length), (0.0, -length + 0.045), (-0.038, -length)]
        mk.prism(rib, tail, 0.02, "cloth_black", plane="zy", center=(knot[0] + s * 0.02, knot[1], knot[2] + 0.004),
                 rot=(tilt, yaw, s * 7))

    # ---------------- marcadores ----------------
    mk.marker("_Muzzle", P(0, BARREL_Y, MUZZLE_Z))
    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Eject", P(0.11, 0.20, -0.075))
    mk.marker("_Chamber", P(*CHAMBER))

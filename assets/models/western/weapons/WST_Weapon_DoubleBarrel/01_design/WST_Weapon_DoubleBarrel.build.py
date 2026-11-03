"""
Receta de WST_Weapon_DoubleBarrel, escopeta de doble caño "coach gun" con martillos (prompt 029, Bloques A + F).

Brief
- Silueta a 30 studs (prioridad del prompt): dos caños gordos paralelos y las dos "orejas" de los
  martillos arriba del bloque. Después: culata recta de madera oscura y la caña de astilla debajo.
- Medidas: largo 2,7 (caños 1,4), alto 0,6 en la culata (de la punta de la cantonera a la espuela), ancho
  0,27. Se arma en "espacio de la escopeta" (ejes de los caños en y = 0, x = ±0,068; cara de la recámara
  en z = 0) y P() lo corre para que el centro de la muñeca quede en (0,0,0).
- Piezas móviles con el origen en su eje: Barrels (perno de la bisagra; bajan 40° y muestran las dos
  recámaras), Extractor (su cara de adelante; corre 0,08 para atrás), HammerL y HammerR (base),
  Triggers (arriba). Stock fijo: bloque de hierro con la barra y el perno, muñeca, culata y guardamonte.
- Materiales (6): gunmetal (caños) · iron (bloque, barra, perno, guardamonte, gatillos, cantonera) ·
  wood_dark (culata y caña) · steel_light (martillos, extractor) · brass (punto de mira) · coal (huecos).
- Tallado: bocas, recámaras, bolsillo del extractor, ranura de la barra donde entra el tetón de los caños,
  estriado de las espuelas. Chanflanes en el bloque, caños y martillos; chapas de las llaves a los lados.

Inferido (el prompt no lo dice o no cierra)
- El prompt pone el perno "at its front top" del bloque. Con el perno arriba los caños no pueden bajar
  sin meterse en el bloque; va en la punta de la barra que sale adelante del bloque, justo debajo de los
  caños (como en una escopeta de quiebre real), y el tetón de los caños calza en una ranura de la barra.
- Martillos y extractor en steel_light: con caños gunmetal, bloque iron y madera oscura todo era oscuro,
  y las orejas de los martillos son la prioridad de silueta.
- Gatillo de adelante a la derecha (caño derecho) y el de atrás a la izquierda, en un solo objeto.
- El extractor es una chapa entre los caños con media muesca hacia cada recámara (no da la vuelta: del
  lado de afuera la pared del caño queda en 0,004 y la booleana rompía bordes).

Vueltas: 1) primera versión: espuelas armadas con tramos sueltos (se leían como eslabones, 494 triángulos
cada martillo); extractor de 0,24 que asomaba por debajo de los caños; z-fighting entre el fondo del tetón
y el perno (los dos en y = -0,135) · 2) martillo en un solo perfil (cuello + espuela enrulada) más cabeza
y cubo; chapas de las llaves; tetón bajado; cinta y relleno 0,004 adentro de las puntas de los caños
(caras coplanares) · 3-5) bordes no-manifold donde el bolsillo del extractor rozaba el fondo de los caños
(a 0,001 de la cara de abajo): bolsillo y chapa subidos hasta dejar 0,007 de pared · 6) ancho 0,303 -> 0,289
(bloque 0,005 más angosto, chapas y tornillos más bajos).

Revisión
- 2434 triángulos contra 800 de referencia (calidad primero): chanflanes de bloque, caños y martillos, los
  dos martillos con espuela enrulada y estriada (392 cada uno), recámaras, bocas y bolsillo tallados, chapas
  de las llaves y guardamonte. El estriado (~90 por martillo) solo se ve de cerca: se dejó por la
  inspección y por familia con el revólver.
- El bloque es iron y los caños gunmetal, como pide el prompt: de lejos la escopeta es oscura; el acento
  claro son los martillos (steel_light), que es lo que tiene que leerse.
"""

import math

OFF = (0.0, 0.065, -0.47)        # centro de la muñeca en espacio de la escopeta -> origen del modelo
BX, BR, BR_F = 0.068, 0.066, 0.06   # eje de cada caño, radio atrás y en la boca
MUZZLE_Z = -1.40
PIN = (0.0, -0.115, -0.15)       # perno de la bisagra
HAMMER_PIVOT = (0.16, 0.03)      # (z, y) de la base de los martillos


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


def frame_hw(z):
    """Medio ancho del bloque a la altura z (lados casi planos hasta 0,2, después se angosta a la muñeca)."""
    if z <= 0.2:
        return 0.132 - 0.005 * z / 0.2
    return 0.127 - (0.127 - 0.075) * (z - 0.2) / 0.135


def build(mk):
    # ---------------- Stock: bloque de hierro, barra con el perno, muñeca, culata, guardamonte ----------------
    st = mk.part("Stock", (0, 0, 0))
    mk.hull(st, PP([(s * frame_hw(0.0), y, 0.0) for s in (-1, 1) for y in (-0.165, 0.072)]
                   + [(s * frame_hw(0.2), y, 0.2) for s in (-1, 1) for y in (-0.165, 0.048)]
                   + [(s * frame_hw(0.335), y, 0.335) for s in (-1, 1) for y in (-0.10, 0.012)]), "iron")  # bloque
    lock = [(0.025, -0.03), (0.03, 0.03), (0.11, 0.04), (0.185, 0.028), (0.2, 0.0), (0.185, -0.04), (0.11, -0.068),
            (0.045, -0.062)]
    for s in (-1, 1):                                                                   # chapas de las llaves
        mk.hull(st, PP([(s * (frame_hw(z) + d), y, z) for z, y in lock for d in (-0.025, 0.006)]), "iron")
    mk.hull(st, PP([(s * 0.115, y, z) for s in (-1, 1) for y in (-0.165, -0.07) for z in (-0.175, 0.01)]),
            "iron")                                                                    # barra
    mk.hull(st, PP(ring(0.31, -0.10, 0.012, 0.07) + ring(0.62, -0.14, -0.03, 0.055)), "wood_dark")    # muñeca
    mk.hull(st, PP(ring(0.60, -0.145, -0.03, 0.057) + ring(1.28, -0.40, -0.05, 0.085, c=0.3)), "wood_dark")  # culata
    mk.hull(st, PP(ring(1.275, -0.405, -0.045, 0.089, c=0.3) + ring(1.30, -0.40, -0.05, 0.087, c=0.3)), "iron")  # cantonera
    guard = [(0.05, -0.15), (0.04, -0.21), (0.07, -0.265), (0.14, -0.285), (0.22, -0.27), (0.28, -0.22),
             (0.33, -0.15), (0.37, -0.09), (0.31, -0.09), (0.27, -0.175), (0.215, -0.235), (0.145, -0.247),
             (0.095, -0.233), (0.078, -0.20), (0.085, -0.15)]
    mk.prism(st, guard, 0.06, "iron", plane="zy", center=P(0, 0, 0))                 # guardamonte
    mk.bevel(st, width=0.012, angle=50)
    mk.carve(st, "coal", points=mk.pts_box(P(0, -0.10, -0.09), (0.11, 0.09, 0.19)))  # ranura del tetón
    mk.cyl(st, P(*PIN), 0.022, 0.24, "steel_light", axis="x", sides=8, detail=True)  # perno de la bisagra
    for s in (-1, 1):
        mk.cyl(st, P(s * (frame_hw(0.07) + 0.006), -0.025, 0.07), 0.015, 0.016, "steel_light", axis="x", sides=6,
               detail=True)                                                            # tornillo de la chapa
        mk.cyl(st, P(s * (frame_hw(HAMMER_PIVOT[0]) + 0.006), HAMMER_PIVOT[1], HAMMER_PIVOT[0]), 0.02, 0.016,
               "steel_light", axis="x", sides=6, detail=True)                          # eje del martillo

    # ---------------- Barrels: dos caños, cinta arriba, relleno abajo, tetón y caña ----------------
    br = mk.part("Barrels", P(*PIN))
    for s in (-1, 1):
        mk.cyl(br, P(s * BX, 0, (MUZZLE_Z - 0.004) / 2), BR_F, abs(MUZZLE_Z) - 0.004, "gunmetal", axis="z",
               sides=12, top=BR / BR_F)
    zb, zm = -0.008, MUZZLE_Z + 0.004                                                  # cinta y relleno, 0,004 adentro
    mk.hull(br, PP([(s * 0.034, y, z) for s in (-1, 1) for y, z in
                    ((0.03, zb), (0.078, zb), (0.026, zm), (0.07, zm))]), "gunmetal")  # cinta
    mk.hull(br, PP([(s * 0.03, y, z) for s in (-1, 1) for y in (-0.05, 0.0) for z in (zb, zm)]),
            "gunmetal")                                                                # relleno de abajo
    mk.hull(br, PP([(s * 0.05, y, z) for s in (-1, 1) for y in (-0.14, -0.04) for z in (-0.012, -0.168)]),
            "gunmetal")                                                                # tetón (abajo del perno)
    mk.hull(br, PP(ring(-0.18, -0.16, -0.035, 0.10) + ring(-0.62, -0.15, -0.035, 0.085)
                   + ring(-0.665, -0.12, -0.04, 0.06)), "wood_dark")                  # caña de astilla
    mk.bevel(br, width=0.01, angle=50)
    for s in (-1, 1):
        mk.carve(br, "coal", points=mk.pts_cyl(P(s * BX, 0, MUZZLE_Z), 0.042, 0.2, axis="z", sides=10))   # bocas
        mk.carve(br, "coal", points=mk.pts_cyl(P(s * BX, 0, 0.0), 0.044, 0.3, axis="z", sides=10))        # recámaras
    pocket = [(s * x, y, z) for s in (-1, 1) for x, y in ((0.046, -0.066), (0.064, -0.0565), (0.07, -0.02))
              for z in (-0.04, 0.04)]                                                  # adentro de los caños (pared >= 0,004)
    mk.carve(br, "coal", points=PP(pocket))                                            # bolsillo del extractor
    mk.ball(br, P(0, 0.083, MUZZLE_Z + 0.04), 0.017, "brass", subdiv=1, detail=True)  # punto de mira

    # ---------------- Extractor: chapa entre los caños con media muesca para cada culote ----------------
    ex = mk.part("Extractor", P(0, -0.045, -0.036))
    prof = [(-0.042, -0.063), (0.042, -0.063), (0.06, -0.054)]
    for k in range(4):                                                                 # muesca del caño derecho (lado de adentro)
        a = math.radians(-100 - 55 * k / 3)
        prof.append((BX + 0.046 * math.cos(a), 0.046 * math.sin(a)))
    prof.append((0.0, -0.021))
    for k in range(4):                                                                 # muesca del caño izquierdo
        a = math.radians(-25 - 55 * k / 3)
        prof.append((-BX + 0.046 * math.cos(a), 0.046 * math.sin(a)))
    prof.append((-0.06, -0.054))
    mk.prism(ex, prof, 0.03, "steel_light", plane="xy", center=P(0, 0, -0.021))

    # ---------------- martillos: cuello, cabeza y espuela enrulada en un solo perfil ----------------
    spine = [(0.168, 0.0), (0.14, 0.05), (0.108, 0.095), (0.10, 0.13), (0.13, 0.163), (0.18, 0.182), (0.225, 0.177),
             (0.253, 0.155), (0.252, 0.127)]
    half = [0.03, 0.026, 0.027, 0.024, 0.02, 0.019, 0.018, 0.017, 0.015]
    head = [(0.03, 0.068), (0.06, 0.062), (0.118, 0.108), (0.112, 0.135), (0.06, 0.115), (0.03, 0.088)]
    for name, s in (("HammerL", -1), ("HammerR", 1)):
        x = s * 0.09
        hz, hy = HAMMER_PIVOT
        ham = mk.part(name, P(x, hy, hz))
        mk.prism(ham, band(spine, half), 0.04, "steel_light", plane="zy", center=P(x, 0, 0))   # cuello y espuela
        mk.prism(ham, head, 0.036, "steel_light", plane="zy", center=P(x, 0, 0))              # cabeza (nariz)
        mk.cyl(ham, P(x, hy, hz), 0.034, 0.038, "steel_light", axis="x", sides=8)            # cubo
        mk.bevel(ham, width=0.006, angle=35)
        for k in range(3):                                                             # estriado de la espuela
            mk.carve(ham, "iron", points=mk.pts_box(P(x, 0.205, 0.163 + 0.02 * k), (0.06, 0.02, 0.007)))

    # ---------------- gatillos (dos, un objeto) ----------------
    tr = mk.part("Triggers", P(0, -0.165, 0.155))
    for z, x in ((0.125, 0.012), (0.19, -0.012)):
        blade = [(z - 0.018, -0.16), (z + 0.012, -0.16), (z + 0.006, -0.195), (z + 0.02, -0.222),
                 (z + 0.002, -0.228), (z - 0.016, -0.197)]
        mk.prism(tr, blade, 0.03, "iron", plane="zy", center=P(x, 0, 0))
    mk.bevel(tr, width=0.005, angle=35)

    # ---------------- marcadores ----------------
    mk.marker("_Muzzle", P(0, 0, MUZZLE_Z))
    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Grip2", P(0, -0.17, -0.40))
    mk.marker("_Eject", P(0, 0.02, -0.01))
    mk.marker("_ChamberL", P(-BX, 0, -0.004))
    mk.marker("_ChamberR", P(BX, 0, -0.004))

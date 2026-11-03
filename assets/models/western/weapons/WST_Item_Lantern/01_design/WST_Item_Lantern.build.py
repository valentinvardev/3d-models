"""
Receta de WST_Item_Lantern, el farol de mano de kerosén de la mina (prompt 033, Bloques A + F).

Brief
- Silueta a 40 studs: tanque redondo abajo, globo de vidrio claro panzón con 4 alambres arqueados, sombrero
  cónico con chimenea y tapa ventilada, y el asa grande en arco por arriba con su manija de madera.
- Medidas: 0,9 de alto sin el asa (tanque abajo en y = -1,3, tapa arriba en -0,4), 0,5 de ancho; el asa
  suma 0,4. Origen = la manija del asa (donde cierra la mano, Bloque F): el farol cuelga de ahí.
- Piezas: Body (tanque, anillo del quemador, alambres, sombrero, chimenea, asa, manija), Globe (vidrio),
  Flame (llama en gota, lamp_glow). Marcadores _Grip (origen) y _Light (centro de la llama).
- 8 lados en lo redondo (tanque, globo, sombrero), 6 en lo chico (chimenea, manija). Sin chanflanes.
- Inferido: Globe como pieza propia (en Studio cada pieza es un MeshPart: el vidrio necesita su propio
  material Glass y transparencia, como la llama su Neon); el nombre Body; el anillo del quemador en
  bronce (metal de detalle, Bloque F) y la manija de madera (wood_dark); el asa cruzada sobre X (la mano
  lo lleva con el vidrio hacia adelante); las orejas donde pivotea el asa.

Vueltas: 1) z-fighting: el pie de los alambres coincidía con el de abajo del anillo (y = -1,12); el asa
por fuera del tanque daba 0,56 de ancho · 2) alambres desde -1,13, asa de 0,22 de radio (0,50 de ancho).

Revisión
- 414 triángulos contra 250 de referencia (calidad primero): el asa en U con su manija (~90) y los cuatro
  alambres arqueados (~80) son la silueta de farol de establo; con alambres rectos se ahorran 32 y se
  pierde la jaula. Lo redondo ya va en 8 lados y lo chico en 6.
- Alto 1,35: 0,9 de cuerpo + 0,4 de asa + la mitad de arriba de la manija (0,05).
- Flame queda encerrada en Globe sin tocar (aviso "enclosed"): es a propósito. En las capturas el vidrio
  es opaco y no deja ver la llama; en Studio Globe lleva Glass con transparencia.
- El aviso de "lowest point" es porque el origen está en la manija (Bloque F), no en el piso.
"""

import math

Y_BOT, Y_TOP = -1.3, -0.4          # tanque abajo, tapa arriba (0,9 de alto sin el asa)
GLOBE = [(-1.06, 0.14), (-0.84, 0.18), (-0.62, 0.13)]   # (y, radio) del globo
FLAME_C = (0.0, -0.88, 0.0)


def ring(y, r, sides=8, rot=0.0):
    return [(r * math.cos(2 * math.pi * (i + 0.5) / sides + rot), y, r * math.sin(2 * math.pi * (i + 0.5) / sides + rot))
            for i in range(sides)]


def bail_profile(rx=0.22, ry=0.3, yc=-0.3, y0=-0.6, t=0.03, n=6):
    """Asa en U invertida (x, y): patas rectas de y0 a yc y medio óvalo hasta y = 0, espesor 2t."""
    outer = [(rx + t, y0)] + [((rx + t) * math.cos(math.pi * k / n), yc + (ry + t) * math.sin(math.pi * k / n))
                              for k in range(n + 1)] + [(-(rx + t), y0)]
    inner = [(-(rx - t), y0)] + [((rx - t) * math.cos(math.pi * k / n), yc + (ry - t) * math.sin(math.pi * k / n))
                                 for k in range(n, -1, -1)] + [(rx - t, y0)]
    return outer + inner


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # tanque redondo de lata y anillo del quemador
    mk.cyl(body, (0, -1.2, 0), 0.26, 0.2, "iron", sides=8, top=0.9)
    mk.cyl(body, (0, -1.085, 0), 0.19, 0.07, "brass", sides=8)
    # cuatro alambres arqueados, a 45° del frente para que la llama se vea
    guard = [(0.15, -1.13), (0.185, -0.84), (0.15, -0.58), (0.20, -0.58), (0.235, -0.84), (0.20, -1.13)]   # abajo en -1,13: en -1,12 coincidía con el anillo
    for k in range(4):
        mk.prism(body, guard, 0.05, "iron", plane="xy", rot=(0, 45 + 90 * k, 0))
    # sombrero cónico, chimenea y tapa ventilada (la luz entre el cono y la tapa son los respiraderos)
    mk.cyl(body, (0, -0.57, 0), 0.235, 0.14, "iron", sides=8, top=0.5)
    mk.cyl(body, (0, -0.475, 0), 0.07, 0.09, "iron", sides=6)
    mk.cyl(body, (0, -0.425, 0), 0.115, 0.05, "iron", sides=8, top=0.75)
    # asa: orejas en el borde del sombrero, U de alambre y manija de madera
    for s in (-1, 1):
        mk.box(body, (s * 0.205, -0.58, 0), (0.08, 0.06, 0.08), "iron")
    mk.prism(body, bail_profile(), 0.06, "iron", plane="xy")
    mk.cyl(body, (0, 0, 0), 0.055, 0.2, "wood_dark", axis="x", sides=6)

    globe = mk.part("Globe", (0, 0, 0))
    mk.hull(globe, [p for y, r in GLOBE for p in ring(y, r)], "glass")

    flame = mk.part("Flame", (0, 0, 0))
    mk.hull(flame, ring(-0.975, 0.025, 6) + ring(-0.92, 0.05, 6) + [(0, -0.78, 0)], "lamp_glow")

    mk.marker("_Grip", (0, 0, 0))
    mk.marker("_Light", FLAME_C)

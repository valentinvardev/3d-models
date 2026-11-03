"""
Receta de WST_Vehicle_PeddlerWagon, la carreta-tienda del buhonero (prompt 067, Bloques A + B).

Brief
- Silueta que se lee a 40 studs: casilla alta con techo de madera en arco, chimenea de caño, cartel
  liso arriba, toldo rojo festoneado sobre el mostrador del costado derecho, ollas y botellas
  colgando del alero izquierdo, ruedas de rayos (las mismas que la carreta).
- Medidas: casilla 9 (z) x 5 (x), piso a 2,55, paredes hasta 6,4, techo en arco con la cumbrera a
  8,0 y alero de 0,4 (baja a 5,85 en x = ±2,9); cartel 5 x 1,2 sobre la cumbrera (arriba a 9,45);
  mostrador de 4,8 x 1,6 con la bisagra abajo a 2,8 (bajado queda a la altura de la cintura de un
  jugador); ruedas de 3,2 (z -3,0) y 3,8 (z +3,0) en x = ±2,85.
- Piezas: Body (chasis, casilla, techo, chimenea, puerta de atrás con escalera, pescante, estantes de
  adentro, ganchos y cacharros colgados, lanza apoyada en el piso), Counter (origen en la bisagra de
  abajo, afuera), Awning (origen en la bisagra del alero), WheelFL/FR/BL/BR (de WST_Vehicle_Wagon,
  origen en el cubo), SignBoard (origen en su base). Marcador _Shopkeeper.
- Paredes de tabla y listón: paño teal con listones oscuros 0,03 afuera (las juntas), marco mostaza
  0,05 afuera (esquineros, fajas, marco del mostrador). Pintura gastada: un paño de madera pelada.
- Inferido: toldo abierto (20° hacia abajo) y mostrador cerrado; el buhonero parado en el piso al
  lado del frente del mostrador; estantes adentro (se ven con el mostrador bajado); lanza apoyada en
  el piso; botellas en glass_green (séptimo material: el prompt pide botellas).

Vueltas: 1) primera versión: 55 pares coplanares (esquineros, fajas y paredes con la misma base y el
mismo tope; hastiales al ras de las puntas de los costados; escalones al ras de los largueros) y
bordes no-manifold (aristas comunes entre el piso y la pared izquierda, y entre las piezas del marco
del mostrador) · 2) todo corrido 0,005-0,02 o metido en el vecino · 3) marco del mostrador sin
aristas comunes · 4) ollas, sartenes y botellas más grandes y colgando más abajo, contra la pared
(se perdían bajo el alero); menos mercadería en los estantes de adentro.

Revisión
- 4072 triángulos contra 1600 de referencia. Las ruedas son 1968 (las mismas de la carreta: 12 rayos
  sueltos, llanta de hierro, 16 lados; misma familia). Casilla 1800: paredes de tabla y listón,
  marco mostaza, techo en arco con juntas, chimenea, puerta con escalera, pescante, 7 cacharros
  colgados y 6 de mercadería adentro. Toldo 128, mostrador 120, cartel 60.
- Alto 9,54 con el cartel (la cumbrera del techo está a 8,0 como pide el prompt).
- 7 materiales (uno más que el tope del Bloque A) por las botellas de vidrio.
- Dudoso para Valentin: dónde se para el buhonero. Con el mostrador a 2,8 del piso, adentro le
  quedaría a la rodilla; lo puse afuera, al lado del frente del mostrador (_Shopkeeper en el piso).
"""

import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "wagon_recipe", Path(__file__).resolve().parents[2] / "WST_Vehicle_Wagon" / "01_design" / "WST_Vehicle_Wagon.build.py")
W = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W)

HX, HZ = 2.5, 4.5                 # medio ancho y medio largo de la casilla
FLOOR, EAVE, RIDGE = 2.55, 6.4, 8.0
OVER = 2.9                        # alero
OPEN_Z, OPEN_Y = (-2.4, 2.4), (2.8, 4.4)      # hueco del mostrador (pared derecha)
WHEEL_Z = 3.0


def roof_y(x):
    """Cara de arriba del techo en arco."""
    return RIDGE - (RIDGE - EAVE) * (x / HX) ** 2


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- chasis ----------------
    for s in (-1, 1):
        mk.box(body, (s * 2.10, 2.17, 0), (0.30, 0.44, 2 * HZ - 0.2), "wood_dark")                 # largueros
    mk.box(body, (0, 1.60, -WHEEL_Z), (5.2, 0.28, 0.30), "wood_dark")                              # eje de adelante
    mk.box(body, (0, 1.90, WHEEL_Z), (5.2, 0.28, 0.30), "wood_dark")                               # eje de atrás
    mk.box(body, (0, 1.88, -WHEEL_Z), (4.4, 0.32, 0.40), "wood_dark")                              # traviesa de adelante
    mk.box(body, (0, 2.47, 0), (2 * HX - 0.04, 0.16, 2 * HZ - 0.04), "wood_dark")                  # piso (sin aristas comunes con las paredes)
    # lanza apoyada en el piso
    mk.hull(body, [(x, y, z) for x in (-0.10, 0.10) for y, z in ((1.50, -3.0), (1.72, -3.0), (0.02, -9.0), (0.20, -9.0))],
            "wood_dark")

    # ---------------- paredes: paño teal, listones oscuros, marco mostaza ----------------
    def wall_x(s, z0, z1, y0, y1, battens=True, mat="paint_teal", th=0.12):
        xo = s * HX
        mk.box(body, (xo - s * 0.06, (y0 + y1) / 2, (z0 + z1) / 2), (th, y1 - y0, z1 - z0), mat)
        if battens:
            n = max(1, int(round((z1 - z0) / 0.9)))
            for i in range(1, n):
                z = z0 + (z1 - z0) * i / n
                mk.box(body, (xo + s * 0.015, (y0 + y1) / 2, z), (0.05, y1 - y0 - 0.02, 0.08), "wood_dark")

    wall_x(-1, -HZ, HZ, FLOOR, EAVE)
    wall_x(1, -HZ, OPEN_Z[0], FLOOR, EAVE)
    wall_x(1, OPEN_Z[1], HZ, FLOOR, EAVE, mat="wood_mid")                     # paño de madera pelada
    # arriba y abajo del hueco: 0,01 más finos y metidos 0,01 en los paños vecinos (ni coplanares ni vértices compartidos)
    wall_x(1, OPEN_Z[0] - 0.01, OPEN_Z[1] + 0.01, FLOOR, OPEN_Y[0], battens=False, th=0.11)
    wall_x(1, OPEN_Z[0] - 0.01, OPEN_Z[1] + 0.01, OPEN_Y[1], EAVE, th=0.11)
    # frente y fondo: hastiales con el arco del techo
    arch = [(x, roof_y(x) - 0.05) for x in [HX - 0.5 * i for i in range(11)]]
    gable = [(-HX + 0.10, FLOOR), (HX - 0.10, FLOOR)] + [(min(max(x, -HX + 0.10), HX - 0.10), y) for x, y in arch]
    for zc in (-HZ + 0.065, HZ - 0.065):                                     # 0,005 adentro: no coplanar con las puntas de los costados
        mk.prism(body, gable, 0.11, "paint_teal", plane="xy", center=(0, 0, zc))
        sgn = 1 if zc > 0 else -1
        for x in (-1.6, -0.8, 0.8, 1.6):
            if zc > 0 and abs(x) < 1.0:
                continue                                                       # ahí va la puerta
            mk.box(body, (x, (FLOOR + roof_y(x)) / 2 - 0.05, zc + sgn * 0.075), (0.08, roof_y(x) - FLOOR - 0.2, 0.05), "wood_dark")
    # marco mostaza: esquineros, fajas de abajo y de arriba, marco del mostrador
    for sx in (-1, 1):
        for sz in (-1, 1):
            mk.box(body, (sx * (HX - 0.04), (FLOOR + EAVE) / 2 - 0.075, sz * (HZ - 0.04)), (0.22, EAVE - FLOOR + 0.05, 0.22),
                   "paint_mustard")                                            # esquinero: de 2,45 a 6,35
        mk.box(body, (sx * (HX + 0.03), FLOOR + 0.14, 0), (0.10, 0.24, 2 * HZ - 0.16), "paint_mustard")
        mk.box(body, (sx * (HX + 0.03), EAVE - 0.20, 0), (0.10, 0.24, 2 * HZ - 0.16), "paint_mustard")
    for sz in (-1, 1):
        mk.box(body, (0, FLOOR + 0.14, sz * (HZ + 0.03)), (2 * HX - 0.16, 0.24, 0.10), "paint_mustard")
    ox = HX + 0.045
    for y in (OPEN_Y[0] - 0.07, OPEN_Y[1] + 0.07):
        mk.box(body, (ox, y, 0), (0.10, 0.14, OPEN_Z[1] - OPEN_Z[0] + 0.31), "paint_mustard")
    for z in (OPEN_Z[0] - 0.07, OPEN_Z[1] + 0.07):
        mk.box(body, (ox - 0.005, sum(OPEN_Y) / 2, z), (0.09, OPEN_Y[1] - OPEN_Y[0] + 0.04, 0.14), "paint_mustard")

    # ---------------- techo en arco de tablas, con juntas oscuras ----------------
    xs = [-OVER + 2 * OVER * i / 10 for i in range(11)]
    outer = [(x, roof_y(x)) for x in xs]
    inner = [(x, roof_y(x) - 0.16) for x in reversed(xs)]
    mk.prism(body, outer + inner, 2 * HZ + 0.8, "wood_mid", plane="xy", center=(0, 0, 0))
    for x0, x1 in zip(xs[1:-2], xs[2:-1]):                                     # juntas sobre el techo
        xm, ym = (x0 + x1) / 2, (roof_y(x0) + roof_y(x1)) / 2          # sobre la cuerda de la faceta, no sobre el arco
        ang = math.degrees(math.atan((roof_y(x1) - roof_y(x0)) / (x1 - x0)))
        mk.box(body, (xm, ym + 0.015, 0), (0.07, 0.05, 2 * HZ + 0.84), "wood_dark", rot=(0, 0, ang))
    # chimenea de caño con sombrerete
    cxz = (-1.2, 2.6)
    mk.cyl(body, (cxz[0], roof_y(cxz[0]) + 0.55, cxz[1]), 0.17, 1.60, "iron", sides=8)
    mk.cyl(body, (cxz[0], roof_y(cxz[0]) + 0.02, cxz[1]), 0.26, 0.14, "iron", sides=8)            # collarín
    mk.cyl(body, (cxz[0], roof_y(cxz[0]) + 1.16, cxz[1]), 0.36, 0.22, "iron", sides=8, top=0.25)  # sombrerete
    mk.cyl(body, (cxz[0], roof_y(cxz[0]) + 1.02, cxz[1]), 0.10, 0.12, "iron", sides=6)

    # ---------------- puerta de atrás y escalera ----------------
    zb = HZ + 0.02
    mk.box(body, (0, 4.05, zb + 0.03), (1.56, 2.50, 0.06), "wood_mid")                           # hoja (arriba de la faja)
    for x in (-0.86, 0.86):
        mk.box(body, (x, 4.15, zb + 0.05), (0.14, 2.70, 0.10), "paint_mustard")                   # jambas
    mk.box(body, (0, 5.46, zb + 0.05), (1.90, 0.14, 0.12), "paint_mustard")                      # dintel
    for y in (3.10, 4.80):
        mk.box(body, (-0.50, y, zb + 0.075), (0.50, 0.10, 0.04), "iron")                          # bisagras
    mk.box(body, (0.55, 4.05, zb + 0.09), (0.08, 0.24, 0.08), "iron")                            # tirador
    for s in (-1, 1):                                                                            # escalera colgada del piso
        mk.box(body, (s * 0.62, 1.50, HZ + 0.15), (0.10, 1.95, 0.12), "wood_dark", rot=(-12, 0, 0))
    for y in (0.85, 1.65):
        mk.box(body, (0, y, HZ + 0.15 + (1.50 - y) * 0.213), (1.30, 0.08, 0.34), "wood_dark")    # escalones

    # ---------------- pescante chico adelante ----------------
    mk.box(body, (0, 4.32, -HZ - 0.385), (3.0, 0.12, 0.77), "wood_mid")                         # asiento (se mete en la pared)
    for s in (-1, 1):
        mk.hull(body, [(s * x, y, z) for x in (1.30, 1.40) for y, z in ((4.26, -HZ - 0.02), (4.26, -HZ - 0.72), (3.60, -HZ - 0.02))],
                "wood_dark")                                                                     # escuadras
    mk.hull(body, [(x, y, z) for x in (-1.5, 1.5) for y, z in ((2.62, -HZ - 0.02), (2.72, -HZ - 0.02), (3.20, -HZ - 0.95), (3.10, -HZ - 0.97))],
            "wood_mid")                                                                          # tablero de los pies

    # ---------------- adentro: estantes con mercadería (se ven con el mostrador bajado) ----------------
    for y in (3.55, 4.75):
        mk.box(body, (-HX + 0.40, y, 0), (0.58, 0.08, 4.6), "wood_mid")
        for i, z in enumerate((-1.5, 0.0, 1.5)):
            if (i + int(y)) % 2:
                mk.cyl(body, (-HX + 0.40, y + 0.22, z), 0.11, 0.36, "glass_green", sides=6)
                mk.cyl(body, (-HX + 0.40, y + 0.46, z), 0.045, 0.14, "glass_green", sides=6)
            else:
                mk.box(body, (-HX + 0.38, y + 0.20, z), (0.40, 0.32, 0.46), "paint_red" if i % 3 else "paint_mustard")

    # ---------------- ganchos en el alero izquierdo: ollas, sartenes y botellas colgando contra la pared ----------------
    hx_ = -2.72
    hook_y = roof_y(hx_) - 0.16

    def cord(a, b, mat, w=0.035):
        mk.hull(body, [(x + dx, y, z + dz) for x, y, z in (a, b) for dx in (-w, w) for dz in (-w, w)], mat)

    goods = (("pot", -3.6), ("pan", -2.5), ("bottle", -1.6), ("pot", -0.5), ("bottle", 0.5), ("pan", 1.5), ("pot", 2.7))
    for kind, z in goods:
        mk.box(body, (hx_, hook_y - 0.08, z), (0.06, 0.24, 0.06), "iron")                        # gancho (entra en el alero)
        if kind == "pot":
            cy = hook_y - 1.00
            cord((hx_, hook_y - 0.15, z), (-2.86, cy + 0.20, z), "iron")                           # asa
            mk.cyl(body, (-2.86, cy, z), 0.34, 0.42, "iron", sides=8, top=0.85)
            mk.cyl(body, (-2.86, cy + 0.20, z), 0.30, 0.05, "iron", sides=8)                       # borde
        elif kind == "pan":
            cy = hook_y - 1.15
            cord((hx_, hook_y - 0.15, z), (-2.62, cy + 0.30, z), "iron", w=0.045)                  # mango
            mk.cyl(body, (-2.62, cy, z), 0.38, 0.07, "iron", axis="x", sides=10)
        else:
            cy = hook_y - 1.10
            cord((hx_, hook_y - 0.15, z), (-2.78, cy + 0.40, z), "wood_dark", w=0.02)              # cordel
            mk.cyl(body, (-2.78, cy + 0.32, z), 0.06, 0.18, "glass_green", sides=6)
            mk.cyl(body, (-2.78, cy, z), 0.14, 0.46, "glass_green", sides=6)

    # ---------------- ruedas (las de la carreta) ----------------
    for name, s, hy, hz in (("WheelFL", -1, 1.6, -WHEEL_Z), ("WheelFR", 1, 1.6, -WHEEL_Z),
                            ("WheelBL", -1, 1.9, WHEEL_Z), ("WheelBR", 1, 1.9, WHEEL_Z)):
        W.wheel(mk, name, (s * W.WHEEL_X, hy, hz), hy)

    # ---------------- mostrador: la tabla del costado derecho, bisagra abajo ----------------
    counter = mk.part("Counter", (HX, OPEN_Y[0], 0))
    zc, yc = sum(OPEN_Z) / 2, sum(OPEN_Y) / 2
    zl, yl = OPEN_Z[1] - OPEN_Z[0] - 0.02, OPEN_Y[1] - OPEN_Y[0] - 0.02
    mk.box(counter, (HX - 0.06, yc, zc), (0.11, yl, zl), "paint_teal")                           # cara de afuera
    mk.box(counter, (HX - 0.135, yc, zc), (0.05, yl - 0.04, zl - 0.04), "wood_mid")              # cara de adentro: tapa del mostrador
    for i in range(1, 5):
        mk.box(counter, (HX + 0.015, yc, OPEN_Z[0] + (OPEN_Z[1] - OPEN_Z[0]) * i / 5), (0.05, yl - 0.02, 0.08), "wood_dark")
    mk.box(counter, (HX + 0.03, OPEN_Y[1] - 0.12, zc), (0.06, 0.12, zl - 0.2), "paint_mustard")  # listón de arriba
    mk.box(counter, (HX + 0.06, OPEN_Y[1] - 0.12, 0.0), (0.06, 0.10, 0.30), "iron")             # pestillo
    for z in (-1.95, 1.95):
        mk.box(counter, (HX + 0.03, OPEN_Y[0] + 0.06, z), (0.05, 0.10, 0.36), "iron")             # bisagras

    # ---------------- toldo rojo festoneado, bisagra en el alero ----------------
    hinge = (OVER - 0.02, roof_y(OVER) - 0.12, 0.0)
    awn = mk.part("Awning", hinge)
    out_x, out_y = OVER + 1.75, hinge[1] - 0.64                         # 20° hacia abajo
    zs = (OPEN_Z[0] - 0.25, OPEN_Z[1] + 0.25)
    mk.hull(awn, [(x, y + dy, z) for x, y in ((hinge[0], hinge[1]), (out_x, out_y)) for dy in (0.0, 0.05) for z in zs],
            "paint_red")
    scallop = [(zs[0], out_y + 0.04), (zs[1], out_y + 0.04)]
    n = 7
    for i in range(n, 0, -1):                                           # borde de abajo en festones
        z1, z0 = zs[0] + (zs[1] - zs[0]) * i / n, zs[0] + (zs[1] - zs[0]) * (i - 1) / n
        zm = (z0 + z1) / 2
        scallop += [(z1, out_y - 0.30), (zm + (z1 - zm) * 0.5, out_y - 0.42), (zm - (zm - z0) * 0.5, out_y - 0.42)]
    scallop.append((zs[0], out_y - 0.30))
    mk.prism(awn, scallop, 0.05, "paint_red", plane="zy", center=(out_x - 0.02, 0, 0))
    for z in zs:                                                        # brazos de hierro
        mk.hull(awn, [(x, y, z + dz) for x, y in ((HX + 0.0, 5.15), (HX + 0.06, 5.15), (out_x - 0.04, out_y), (out_x - 0.10, out_y))
                      for dz in (-0.03, 0.03)], "iron")

    # ---------------- cartel liso sobre la cumbrera ----------------
    sign = mk.part("SignBoard", (0, RIDGE, 0))
    mk.box(sign, (0, RIDGE + 0.87, 0), (0.12, 1.2, 5.0), "wood_mid")                           # tabla
    mk.box(sign, (0, RIDGE + 1.50, 0), (0.18, 0.08, 5.12), "paint_mustard")                    # moldura de arriba
    mk.box(sign, (0, RIDGE + 0.24, 0), (0.18, 0.08, 5.12), "paint_mustard")                    # moldura de abajo
    for z in (-1.9, 1.9):
        mk.box(sign, (0, RIDGE + 0.10, z), (0.12, 0.34, 0.12), "wood_dark")                     # patas

    mk.marker("_Shopkeeper", (3.70, 0.0, -3.10))

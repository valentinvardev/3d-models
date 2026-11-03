"""
Receta de WST_Vehicle_MineCart, la vagoneta de la mina para dos (prompt 068, Bloques A + B).

Brief
- Silueta que se lee a 40 studs: tina de hierro abierta más ancha arriba que abajo (10°), con labio
  y esquineros remachados, manchas de óxido, ruedas chicas con pestaña sobre la trocha de 3,0,
  barra de empuje atrás y palanca de freno alta en la esquina izquierda de atrás.
- Medidas: tina 5 (z) x 3,4 (x) x 2,4 (y 0,8 a 3,2 sobre el riel); abajo 4,15 x 2,55 (10° de
  inclinación en las cuatro caras); ruedas de 1,0 (eje a 0,5) en x = ±1,5, ejes en z = ±1,55.
  Origen: centro, a la altura de la cara de arriba del riel (la pestaña baja 0,08 por adentro del riel).
- Piezas: Body (tina, labio, esquineros, remaches, bastidor de madera, cajas de eje, barra de
  empuje, soporte y zapata del freno), Brake (origen en su base), WheelFront y WheelBack (eje con dos
  ruedas, origen en el eje). Marcadores _Seat_Driver, _Seat_1, _RailGauge.
- La tina es un casco tallado por dentro: las cuatro paredes y el piso salen unidos (sin tapas
  encimadas) y el adentro queda de óxido. Afuera, óxido pintado en paños que arman los cortes.
- Inferido: la tina de 2,4 incluye el labio; las pestañas van del lado de adentro; freno de zapata
  contra la rueda de atrás izquierda; _RailGauge en el contacto de la rueda delantera izquierda.

Vueltas: 1) primera versión: 1466 triángulos; los cortes para el óxido partían también bastidor,
labios, barra y remaches (cilindros cortados en tiras) · 2) todo lo que no es la tina como detalle
(no se corta ni se pinta): 1022 · 3) dos cortes en diagonal: las manchas de óxido dejan de ser
rectángulos perfectos.

Revisión
- 1024 triángulos contra 600 de referencia: los remaches (24 pirámides, ~150) y las dos ruedas por eje
  con pestaña y cubo (204 por eje) son lo que la hace "vagoneta remachada sobre rieles"; los
  jugadores van adentro y la ven de cerca. Tina con labio, esquineros y óxido: 518 con el bastidor.
- El punto más bajo está a -0,05: son las pestañas, que van por adentro del riel, más abajo de la
  cara de arriba (que es y = 0). Es a propósito.
- Ancho 3,67 (tina 3,4 + labio + cubos de las ruedas); largo 5,73 con la barra de empuje.
"""

import math

TOP, BOTTOM = 3.20, 0.80
TAN = math.tan(math.radians(10))
HX_T, HZ_T = 1.70, 2.50                       # medio ancho y medio largo arriba
HX_B, HZ_B = HX_T - (TOP - BOTTOM) * TAN, HZ_T - (TOP - BOTTOM) * TAN
AXLE_Y, AXLE_Z, WHEEL_X = 0.50, 1.55, 1.50


def wall_x(y):
    return HX_B + (y - BOTTOM) * TAN


def wall_z(y):
    return HZ_B + (y - BOTTOM) * TAN


def rivet(mk, part, p, n, size=0.07):
    """Remache: pirámide chata que sale `size` hacia `n` (eje x o z)."""
    x, y, z = p
    if n[0]:
        base = [(x - n[0] * 0.03, y + dy, z + dz) for dy in (-size, size) for dz in (-size, size)]
    else:
        base = [(x + dx, y + dy, z - n[2] * 0.03) for dx in (-size, size) for dy in (-size, size)]
    mk.hull(part, base + [(x + n[0] * size, y, z + n[2] * size)], "steel_light", detail=True)


def wheelset(mk, name, z):
    part = mk.part(name, (0, AXLE_Y, z))
    mk.cyl(part, (0, AXLE_Y, z), 0.08, 2 * WHEEL_X + 0.16, "iron", axis="x", sides=6)          # eje
    for s in (-1, 1):
        x = s * WHEEL_X
        mk.cyl(part, (x, AXLE_Y, z), 0.50, 0.14, "iron", axis="x", sides=10)                    # rueda
        mk.cyl(part, (x - s * 0.085, AXLE_Y, z), 0.58, 0.05, "iron", axis="x", sides=10)        # pestaña, del lado de adentro
        mk.cyl(part, (x + s * 0.10, AXLE_Y, z), 0.16, 0.08, "steel_light", axis="x", sides=6)   # cubo
    return part


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- tina: casco tallado por dentro ----------------
    mk.hull(body, [(sx * hx, y, sz * hz) for y, hx, hz in ((BOTTOM, HX_B, HZ_B), (TOP, HX_T, HZ_T))
                   for sx in (-1, 1) for sz in (-1, 1)], "iron")
    t, floor = 0.10, BOTTOM + 0.12
    mk.carve(body, "rust", points=[(sx * (wall_x(y) - t), y, sz * (wall_z(y) - t)) for y in (floor, TOP + 0.4)
                                   for sx in (-1, 1) for sz in (-1, 1)])
    # cortes para los paños de óxido y el óxido pintado afuera (solo la tina: lo demás es detalle y no se corta)
    mk.slice(body, (0, 1.55, 0), (0, 1, 0))
    for z in (-1.2, 0.3, 1.4):
        mk.slice(body, (0, 0, z), (0, 0, 1))
    mk.slice(body, (0.4, 0, 0), (1, 0, 0))
    mk.slice(body, (0, 1.95, 0), (0, 1, 0.55))                         # cortes en diagonal: manchas irregulares, no rectángulos
    mk.slice(body, (0, 2.05, 0), (0.6, 1, 0))
    for c, size in (((-1.6, 1.15, 0.9), (0.6, 0.8, 1.2)),          # izquierda, abajo, atrás
                    ((1.7, 2.35, -1.9), (0.6, 1.4, 1.4)),          # derecha, arriba, adelante
                    ((-0.6, 1.15, -2.3), (1.9, 0.8, 0.6)),         # frente, abajo
                    ((1.0, 2.40, 2.5), (1.2, 1.5, 0.6))):          # fondo, arriba a la derecha
        mk.paint(body, "rust", box=(c, size))
    # labio de arriba: cuatro planchuelas con alturas apenas distintas (no coplanares en las esquinas)
    for s in (-1, 1):
        mk.hull(body, [(s * x, y, sz * z) for sz in (-1, 1) for x, y, z in
                       ((HX_T + 0.07, 3.27, HZ_T + 0.05), (HX_T - 0.12, 3.27, HZ_T + 0.05),
                        (wall_x(3.06) + 0.07, 3.06, wall_z(3.06) + 0.05), (wall_x(3.06) - 0.12, 3.06, wall_z(3.06) + 0.05))],
                "iron", detail=True)
        mk.hull(body, [(sx * x, y, s * z) for sx in (-1, 1) for x, y, z in
                       ((HX_T + 0.06, 3.26, HZ_T + 0.06), (HX_T + 0.06, 3.26, HZ_T - 0.12),
                        (wall_x(3.07) + 0.06, 3.07, wall_z(3.07) + 0.06), (wall_x(3.07) + 0.06, 3.07, wall_z(3.07) - 0.12))],
                "iron", detail=True)
    # esquineros remachados
    for sx in (-1, 1):
        for sz in (-1, 1):
            pts = []
            for y in (BOTTOM - 0.02, 3.08):
                cx, cz = sx * (wall_x(y) + 0.04), sz * (wall_z(y) + 0.04)
                pts += [(cx, y, cz), (cx - sx * 0.20, y, cz), (cx, y, cz - sz * 0.20)]
            mk.hull(body, pts, "iron", detail=True)
            for y in (1.30, 2.30):
                rivet(mk, body, (sx * (wall_x(y) + 0.05), y, sz * (wall_z(y) - 0.08)), (sx, 0, 0))
                rivet(mk, body, (sx * (wall_x(y) - 0.08), y, sz * (wall_z(y) + 0.05)), (0, 0, sz))
    for s in (-1, 1):                                                   # remaches del labio
        for z in (-1.6, -0.55, 0.55, 1.6):
            rivet(mk, body, (s * (HX_T + 0.075), 3.17, z), (s, 0, 0), size=0.06)
        for x in (-0.8, 0.8):
            rivet(mk, body, (x, 3.17, s * (HZ_T + 0.065)), (0, 0, s), size=0.06)

    # ---------------- bastidor de madera y cajas de eje ----------------
    for s in (-1, 1):
        mk.box(body, (s * 0.95, 0.71, 0), (0.22, 0.22, 4.50), "wood_dark", detail=True)                       # largueros
        mk.box(body, (0, 0.69, s * 2.14), (2.36, 0.20, 0.24), "wood_dark", detail=True)                       # cabezales
        for z in (-AXLE_Z, AXLE_Z):
            mk.box(body, (s * 1.16, 0.56, z), (0.24, 0.28, 0.30), "iron", detail=True)                         # caja de eje

    # ---------------- barra de empuje atrás ----------------
    for s in (-1, 1):
        mk.hull(body, [(s * x, y, z) for x in (1.02, 1.14) for y, z in
                       ((2.55, wall_z(2.55) - 0.02), (2.67, wall_z(2.67) - 0.02), (2.70, 3.02), (2.82, 3.02))], "iron", detail=True)
    mk.cyl(body, (0, 2.76, 3.02), 0.075, 2.60, "iron", axis="x", sides=8, detail=True)
    mk.cyl(body, (0, 2.76, 3.02), 0.095, 1.70, "wood_dark", axis="x", sides=8, detail=True)                 # empuñadura gastada

    # ---------------- freno: soporte y zapata contra la rueda de atrás izquierda ----------------
    # la palanca va atrás de la pared del fondo (que se abre hacia arriba) y sube inclinada con ella
    bx, by, bz = -1.45, 1.00, 2.30
    mk.box(body, (bx, by, bz - 0.08), (0.24, 0.26, 0.30), "iron", detail=True)                               # soporte, metido en la pared
    mk.hull(body, [(x, y, z) for x in (-1.46, -1.54) for y, z in ((0.92, bz), (1.02, bz), (0.62, 2.06), (0.52, 2.06))], "iron", detail=True)
    mk.box(body, (-WHEEL_X, 0.55, AXLE_Z + 0.55), (0.16, 0.36, 0.12), "wood_dark", detail=True)              # zapata

    brake = mk.part("Brake", (bx, by, bz))
    mk.hull(brake, [(x, y, z) for x in (bx - 0.05, bx + 0.05) for y, z in ((by - 0.08, bz - 0.05), (by - 0.08, bz + 0.05),
                                                                          (3.75, bz + 0.50), (3.75, bz + 0.58))], "iron")
    mk.cyl(brake, (bx - 0.10, by, bz), 0.11, 0.08, "steel_light", axis="x", sides=6)            # perno
    mk.cyl(brake, (bx, 3.92, bz + 0.56), 0.08, 0.40, "wood_dark", sides=8)                      # manija

    # ---------------- ruedas ----------------
    wheelset(mk, "WheelFront", -AXLE_Z)
    wheelset(mk, "WheelBack", AXLE_Z)

    mk.marker("_Seat_Driver", (0, BOTTOM + 0.12, 1.20))
    mk.marker("_Seat_1", (0, BOTTOM + 0.12, -1.20))
    mk.marker("_RailGauge", (-WHEEL_X, 0.0, -AXLE_Z))

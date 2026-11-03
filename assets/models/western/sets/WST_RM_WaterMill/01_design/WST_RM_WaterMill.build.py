"""
Receta de WST_RM_WaterMill, el molino de agua del rancho (prompt 093, Bloques A + B). Oleada 3: se carga
el molino para apagar el fuego del granero.

Brief
- Silueta a 40 studs: casita de base de piedra y paredes de tabla con techo a dos aguas, una rueda de
  agua grande (12 de diámetro) más alta que la casa pegada a su testero, y la canaleta elevada sobre
  caballetes que le llega por arriba. Un caño de madera largo que sale hacia adelante.
- Medidas: casa 12 (X) x 10 (Z), base de piedra de 3 (sale 0,15), paredes de tabla hasta 7,5, cumbrera a
  lo largo de X a 11 (35°), alero de 0,7. Rueda: centro en (8, 6,3, 0), eje en X, 3 de ancho, 16
  cangilones; el eje entra en la casa y apoya afuera en un pilar de piedra. Canaleta: 16 de largo a lo
  largo de Z (de z = 15,6 a -0,4: termina pasando el punto más alto de la rueda), fondo a 12,7-13,2.
- Piezas: MillHouse (casa, pilar del eje), Wheel (origen en el eje), Flume (canaleta, agua, caballetes,
  compuerta y varilla), SluiceLever (origen en su pie, al alcance de la mano: y 1,3), Pipe (caño de
  duelas con zunchos sobre soportes, 20 hacia -Z, termina en un pico hacia abajo), _WaterOut.
- Inferido: rueda en el testero +X con la canaleta desde +Z, compuerta junto al último caballete, palanca
  abajo con una varilla de hierro hasta la compuerta (arriba no la alcanza nadie), puerta y ventana al
  frente, caño hacia -Z (el granero no tiene posición fija), juntas de la piedra y esquinas con sillares.

Vueltas: 1) z-fighting (compuerta al ras del agua, pie de la puerta al ras de la piedra) y aristas de 3-4 caras:
los dos faldones compartían la cara de la cumbrera y el eslabón de la compuerta compartía una arista con la
varilla · 2) faldones pasados 0,004, compuerta 0,01 más angosta, puerta a 0,02 del piso, varilla adentro del
eslabón; pilar del eje más fino (tapaba la maza de costado).

Revisión
- 2304 triángulos contra 2500: casa ~760 (piedra con hiladas y sillares, tabla y tapajuntas, puerta y
  ventana), rueda ~800 (2 llantas talladas de 16 lados, 32 tablas de cangilón, 8 rayos, maza y eje),
  canaleta ~420, caño ~250, palanca ~60.
- Medidas: 17,85 x 15,73 x 41,12 (la casa 12 x 10 con aleros de 0,7; rueda de 12 de diámetro y 3 de ancho;
  canaleta de 16; caño de 20 desde la pared hasta el pico). Lo más alto son las guías de la compuerta.
- Orígenes: Wheel en el eje (8, 6,3, 0); SluiceLever en su pie (10,08, 1,3, 6,9); el resto en (0, 0, 0).
- 6 materiales: stone_grey, wood_mid, wood_dark, wood_light, iron, water.
- Dudoso: la palanca está abajo (al alcance del jugador) con una varilla hasta la compuerta de arriba: el
  prompt la pone "en la canaleta", que está a 13 de alto. El caño sale hacia -Z: girarlo según dónde quede
  el granero en el mapa.
"""

import math

STONE, BARE, DARK, LIGHT, IRON, WATER = "stone_grey", "wood_mid", "wood_dark", "wood_light", "iron", "water"
XC, YC, R = 8.0, 6.3, 6.0          # rueda: centro y radio
ROOF_T, STEP = 0.4, 0.1


def v_add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def v_unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return (dx / n, dy / n)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def intersect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


def plank_x(mk, part, a, b, x0, x1, h, mat, detail=True):
    """Tabla de a a b (puntos (z, y)) con espesor h en el plano zy y de x0 a x1 (rueda)."""
    d = v_unit(a, b)
    nz, ny = -d[1] * h / 2, d[0] * h / 2
    pts = [(x, p[1] + k * ny, p[0] + k * nz) for p in (a, b) for k in (-1, 1) for x in (x0, x1)]
    mk.hull(part, pts, mat, detail=detail)


def ring(c, r, n, axis="z", start=0.5):
    """Puntos de un anillo de n lados alrededor de c, perpendicular a axis."""
    pts = []
    for k in range(n):
        t = 2 * math.pi * (k + start) / n
        a, b = r * math.cos(t), r * math.sin(t)
        pts.append((c[0] + a, c[1] + b, c[2]) if axis == "z" else (c[0], c[1] + b, c[2] + a))
    return pts


def hull_box(mk, part, a, b, w, h, mat, detail=False):
    """Viga de a a b (puntos 3D), sección w x h; w va en la horizontal perpendicular, h en la otra."""
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in d))
    d = [x / n for x in d]
    up = (0.0, 1.0, 0.0) if abs(d[1]) < 0.9 else (1.0, 0.0, 0.0)
    s = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0])
    sn = math.sqrt(sum(x * x for x in s))
    s = [x / sn for x in s]
    t = (s[1] * d[2] - s[2] * d[1], s[2] * d[0] - s[0] * d[2], s[0] * d[1] - s[1] * d[0])
    pts = []
    for p in (a, b):
        for i in (-0.5, 0.5):
            for j in (-0.5, 0.5):
                pts.append(tuple(p[k] + s[k] * w * i + t[k] * h * j for k in range(3)))
    mk.hull(part, pts, mat, detail=detail)


# ---------------------------------------------------------------- casa
def millhouse(mk):
    part = mk.part("MillHouse", (0, 0, 0))
    mk.box(part, (0, 1.5, 0), (12.3, 3.0, 10.3), STONE)                                    # base de piedra
    # paredes de tabla con los hastiales (cumbrera a lo largo de X)
    prof = [(-5.0, 2.95), (5.0, 2.95), (5.0, 7.5), (0.0, 11.0), (-5.0, 7.5)]
    mk.prism(part, prof, 12.0, BARE, plane="zy", center=(0, 0, 0))
    mk.box(part, (0, 3.02, 0), (12.2, 0.24, 10.2), DARK)                                   # solera sobre la piedra
    # techo: dos faldones de tejuelas escalonadas
    roof_y = lambda z: 7.5 + (5.0 - abs(z)) * 3.5 / 5.0
    E, Pk = (5.0, 7.5), (0.0, 11.0)
    d = v_unit(E, Pk)
    n = (d[1], -d[0])                                                                      # normal de afuera
    e_ext = v_add(E, d, -0.8)
    o_p = intersect(v_add(E, n, ROOF_T), d, (0.0, 0.0), (0.0, 1.0))
    base = v_add(e_ext, n, ROOF_T)
    L = v_dot((o_p[0] - base[0], o_p[1] - base[1]), d)
    nr = max(1, round(L / 1.2))
    pts, rows = [], []
    for i in range(nr):
        a = v_add(v_add(base, d, L * i / nr), n, STEP)
        b = v_add(base, d, L * (i + 1) / nr)
        pts += [a, b]
        rows.append((a, b))
    half = [e_ext, Pk] + pts[::-1]
    # los dos faldones se pasan 0,004 de la cumbrera: si comparten la cara del medio, process_model suelda
    # sus vértices y quedan aristas de 3 caras (medido)
    half = [(z - 0.004, y) if abs(z) < 1e-6 else (z, y) for z, y in half]
    for s in (-1, 1):
        pr = [(s * z, y) for z, y in half]
        mk.prism(part, pr if s > 0 else pr[::-1], 13.4, BARE, plane="zy", center=(0, 0, 0))
        for i, (a, b) in enumerate(rows):
            c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            mk.paint(part, DARK, box=((0, c[1], s * c[0]), (14, 0.3, 0.3)))
            if i > 0:
                lip = rows[i - 1][1]
                c2 = ((a[0] + lip[0]) / 2, (a[1] + lip[1]) / 2)
                mk.paint(part, IRON, box=((0, c2[1], s * c2[0]), (14, 0.06, 0.06)))
    # juntas de las hiladas de piedra y sillares en las esquinas
    for y in (1.0, 2.0):
        for dy in (-0.03, 0.03):
            mk.slice(part, (0, y + dy, 0), (0, 1, 0))
        for c, sz in (((0, y, -5.15), (13, 0.062, 0.02)), ((0, y, 5.15), (13, 0.062, 0.02)),
                      ((-6.15, y, 0), (0.02, 0.062, 11)), ((6.15, y, 0), (0.02, 0.062, 11))):
            mk.paint(part, IRON, box=(c, sz))
    for sx in (-1, 1):
        for sz in (-1, 1):
            for k, (y0, y1) in enumerate(((0.05, 0.95), (1.05, 1.95), (2.05, 2.85))):
                long_x = k % 2 == 0
                lx, lz = (1.3, 0.8) if long_x else (0.8, 1.3)
                cx, cz = sx * (6.15 - lx / 2 + 0.08), sz * (5.15 - lz / 2 + 0.08)
                mk.box(part, (cx, (y0 + y1) / 2, cz), (lx, y1 - y0, lz), STONE, detail=True)
    # tapajuntas: frente y atrás cada 1,5; hastiales siguen el techo
    door = (-4.0, -1.6, 6.0)
    win = (1.0, 3.0, 4.3, 6.0)
    for zs in (-1, 1):
        for x in (-4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5):
            spans = [(3.16, 7.35)]
            if zs < 0 and door[0] - 0.2 < x < door[1] + 0.2:
                spans = [(door[2] + 0.12, 7.35)]
            if zs < 0 and win[0] - 0.2 < x < win[1] + 0.2:
                spans = [(3.16, win[2] - 0.15), (win[3] + 0.15, 7.35)]
            for y0, y1 in spans:
                mk.box(part, (x, (y0 + y1) / 2, zs * 5.055), (0.24, y1 - y0, 0.13), DARK, detail=True)
    for xs in (-1, 1):
        for z in (-3.75, -2.25, -0.75, 0.75, 2.25, 3.75):
            top = min(roof_y(z - 0.12), roof_y(z + 0.12)) - 0.1
            if xs > 0 and abs(z) < 0.9:
                continue                                                                   # ahí entra el eje
            mk.box(part, (xs * 6.055, (3.16 + top) / 2, z), (0.13, top - 3.16, 0.24), DARK, detail=True)
    # puerta al pie (atraviesa la base de piedra) y ventana
    x0, x1, yt = door
    mk.box(part, ((x0 + x1) / 2, yt / 2 + 0.01, -5.15), (x1 - x0, yt - 0.02, 0.34), BARE, detail=True)   # pie a 0,02
    for y in (1.2, 4.6):
        mk.box(part, ((x0 + x1) / 2 - 0.3, y, -5.34), (x1 - x0 - 0.5, 0.18, 0.06), IRON, detail=True)
    mk.box(part, ((x0 + x1) / 2, yt + 0.15, -5.2), (x1 - x0 + 0.5, 0.3, 0.3), DARK, detail=True)   # dintel
    wx0, wx1, wy0, wy1 = win
    mk.box(part, ((wx0 + wx1) / 2, (wy0 + wy1) / 2, -5.06), (wx1 - wx0, wy1 - wy0, 0.16), DARK, detail=True)
    for xa, xb, ya, yb in ((wx0 - 0.15, wx0 + 0.1, wy0 - 0.15, wy1 + 0.15), (wx1 - 0.1, wx1 + 0.15, wy0 - 0.15, wy1 + 0.15),
                           (wx0 + 0.08, wx1 - 0.08, wy1 - 0.08, wy1 + 0.17), (wx0 + 0.08, wx1 - 0.08, wy0 - 0.2, wy0 + 0.08),
                           ((wx0 + wx1) / 2 - 0.05, (wx0 + wx1) / 2 + 0.05, wy0 + 0.05, wy1 - 0.05)):
        dz, emb = (0.2, 0.01) if xb - xa < 0.5 else (0.18, 0.015)                         # sin caras de atrás coplanares
        mk.box(part, ((xa + xb) / 2, (ya + yb) / 2, -5.0 - dz / 2 + emb), (xb - xa, yb - ya, dz), LIGHT, detail=True)
    # pilar de piedra del eje (afuera de la rueda)
    mk.box(part, (XC + 2.4, (YC - 0.25) / 2, 0), (0.8, YC - 0.25, 0.9), STONE)
    return part


# ---------------------------------------------------------------- rueda
def wheel(mk):
    part = mk.part("Wheel", (XC, YC, 0))
    c = (XC, YC, 0.0)
    rin = 5.1
    for xr in (XC - 1.35, XC + 1.35):                                                      # llantas
        outer = [(R * math.cos(2 * math.pi * (k + 0.5) / 16), YC + R * math.sin(2 * math.pi * (k + 0.5) / 16))
                 for k in range(16)]
        mk.prism(part, [(z, y) for z, y in outer], 0.3, DARK, plane="zy", center=(xr, 0, 0))
        inner = [(rin * math.cos(2 * math.pi * (k + 0.5) / 16), YC + rin * math.sin(2 * math.pi * (k + 0.5) / 16))
                 for k in range(16)]
        mk.carve(part, DARK, prism=dict(profile=inner, depth=0.8, plane="zy", center=(xr, 0, 0)))
    P = lambda r, t: (r * math.cos(t), YC + r * math.sin(t))                              # (z, y)
    xa, xb = XC - 1.43, XC + 1.43                                                          # entre llantas (se meten 0,08)
    for k in range(16):                                                                    # cangilones: arranque radial y brazo
        t = 2 * math.pi * (k + 0.5) / 16                                                   # inclinado, boca abierta afuera
        plank_x(mk, part, P(rin - 0.05, t), P(5.62, t), xa, xb, 0.14, LIGHT)
        plank_x(mk, part, P(5.58, t - 0.015), P(R - 0.04, t + 0.2), xa + 0.01, xb - 0.01, 0.12, LIGHT)
    for xr in (XC - 1.35, XC + 1.35):                                                      # rayos: 4 travesaños por lado
        for k in range(4):
            t = math.pi * k / 4 + math.pi / 16
            w = 0.24 + 0.012 * k                                                           # anchos distintos: sin caras coplanares
            plank_x(mk, part, P(rin + 0.1, t), P(rin + 0.1, t + math.pi), xr - w / 2, xr + w / 2, 0.32 + 0.01 * k, BARE)
    mk.cyl(part, c, 0.8, 3.1, IRON, axis="x", sides=8, detail=True)                        # maza
    mk.cyl(part, (5.75 + (XC + 3.15 - 5.75) / 2, YC, 0), 0.3, XC + 3.15 - 5.75, IRON, axis="x", sides=8, detail=True)  # eje


# ---------------------------------------------------------------- canaleta
FZ0, FZ1 = -0.4, 15.6               # punta sobre la rueda y punta de arriba
FX0, FX1 = XC - 1.0, XC + 1.0


def flume_y(z):
    """Abajo del fondo de la canaleta."""
    return 12.7 + (z - FZ0) * 0.5 / (FZ1 - FZ0)


def flume(mk):
    part = mk.part("Flume", (0, 0, 0))
    fy = flume_y
    mk.hull(part, [(x, fy(z) + dy, z) for x in (FX0, FX1) for z in (FZ0, FZ1) for dy in (0.0, 0.3)], BARE)  # fondo
    for xa, xb in ((FX0, FX0 + 0.3), (FX1 - 0.3, FX1)):                                    # costados (0,01 más cortos: tapas no coplanares)
        mk.hull(part, [(x, fy(z) + dy, z) for x in (xa, xb) for z in (FZ0 + 0.01, FZ1 - 0.01) for dy in (0.28, 1.3)], BARE)
    mk.hull(part, [(x, fy(z) + dy, z) for x in (FX0 + 0.28, FX1 - 0.28) for z in (FZ0 + 0.02, FZ1 - 0.02)
                   for dy in (0.29, 0.95)], WATER)                                           # agua
    for z in (2.0, 5.5, 9.5, 13.5):                                                        # costillas
        for xa, xb in ((FX0 - 0.12, FX0 + 0.05), (FX1 - 0.05, FX1 + 0.12)):
            mk.hull(part, [(x, fy(z) + dy, z + dz) for x in (xa, xb) for dy in (-0.05, 1.35) for dz in (-0.12, 0.12)],
                    DARK, detail=True)
    # caballetes (patas abiertas, sombrero, travesaño y cruz)
    for zt in (7.4, 11.4, 15.0):
        top = fy(zt)
        for s in (-1, 1):
            hull_box(mk, part, (XC + s * 1.8, 0.03, zt), (XC + s * 1.1, top - 0.2, zt), 0.42, 0.42, DARK)
        mk.box(part, (XC, top - 0.2, zt), (3.0, 0.4, 0.5), DARK)
        mk.box(part, (XC, 5.0, zt), (3.3, 0.3, 0.3), DARK)
        hull_box(mk, part, (XC - 1.5, 5.1, zt + 0.02), (XC + 1.3, top - 0.6, zt + 0.02), 0.26, 0.26, DARK)
    # tornapuntas del voladizo sobre la rueda
    for s in (-1, 1):
        hull_box(mk, part, (XC + s * 1.25, flume_y(7.4) - 3.5, 7.15), (XC + s * 0.95, flume_y(3.2) - 0.1, 3.2),
                 0.3, 0.3, DARK)
    # compuerta (corrediza en dos guías) y varilla de hierro hasta la palanca de abajo
    zg = 6.9
    gy = fy(zg)
    mk.box(part, (XC, gy + 1.25, zg), (FX1 - FX0 - 0.58, 1.9, 0.18), DARK)               # no al ras del agua
    for s in (-1, 1):
        mk.box(part, (XC + s * (1.0 - 0.15), gy + 1.6, zg), (0.36, 2.4, 0.42), DARK)       # guías (más anchas que el costado)
    mk.box(part, (XC + 0.91, gy + 2.32, zg), (2.52, 0.14, 0.14), IRON)
    mk.box(part, (XC + 2.08, (gy + 2.36 + 4.75) / 2, zg), (0.14, gy + 2.36 - 4.75, 0.14), IRON)   # punta adentro del eslabón
    mk.box(part, (XC + 2.0, 1.3, 7.05), (0.6, 0.7, 0.5), DARK)                             # taco de la palanca en la pata


def sluice_lever(mk):
    pv = (XC + 2.08, 1.3, 6.9)
    part = mk.part("SluiceLever", pv)
    mk.box(part, (pv[0], pv[1], pv[2]), (0.5, 0.6, 0.5), IRON)                              # pivote
    top = (pv[0] - 0.05, 4.9, pv[2])
    hull_box(mk, part, (pv[0], pv[1] - 0.1, pv[2]), top, 0.32, 0.32, LIGHT)                 # brazo
    hull_box(mk, part, (top[0], top[1] - 0.15, pv[2] - 0.55), (top[0], top[1] - 0.15, pv[2] + 0.55), 0.18, 0.18, LIGHT)
    mk.box(part, (top[0], top[1] - 0.15, pv[2]), (0.4, 0.4, 0.4), IRON)                     # unión con la varilla


# ---------------------------------------------------------------- caño
def pipe(mk):
    part = mk.part("Pipe", (0, 0, 0))
    x = 4.5
    za, zb = -5.0, -24.6
    ya, yb = 2.2, 1.65
    y_at = lambda z: ya + (z - za) * (yb - ya) / (zb - za)
    mk.hull(part, ring((x, ya, za), 0.42, 8) + ring((x, yb, zb), 0.42, 8), BARE)              # duelas
    for z in (-8.5, -13.0, -17.5, -22.0):                                                   # zunchos
        mk.hull(part, ring((x, y_at(z), z - 0.08), 0.47, 8) + ring((x, y_at(z), z + 0.08), 0.47, 8), IRON, detail=True)
    for z in (-10.5, -16.0, -21.0):                                                         # soportes
        yp = y_at(z) - 0.4
        mk.box(part, (x, yp / 2, z), (0.4, yp, 0.4), DARK)
        mk.box(part, (x, yp - 0.1, z), (1.2, 0.3, 0.45), DARK)
    # pico: codo hacia abajo y boca
    end = (x, yb, zb)
    tip = (x, yb - 0.75, zb - 0.6)
    mk.hull(part, ring((end[0], end[1], end[2] + 0.1), 0.42, 8) + ring((tip[0], tip[1] + 0.18, tip[2] - 0.12), 0.38, 8), BARE)
    mk.hull(part, ring((tip[0], tip[1] + 0.25, tip[2] - 0.05), 0.42, 8) + ring((tip[0], tip[1] - 0.05, tip[2] - 0.32), 0.42, 8),
            IRON, detail=True)
    mk.marker("_WaterOut", (tip[0], tip[1] - 0.2, tip[2] - 0.4))


def build(mk):
    millhouse(mk)
    wheel(mk)
    flume(mk)
    sluice_lever(mk)
    pipe(mk)

"""
Receta de WST_CH_Altar, el presbiterio de la iglesia (prompt 126, Bloques A + B + G).

Brief
- Silueta: tarima ancha de tres escalones, mesa de altar oscura con un mantel blanco roto y manchado, y atrás,
  contra la pared, una cruz de hierro enorme de puntas abiertas; candeleros de bronce con velas encendidas y
  la costra de plata que nace al pie de la cruz y se desparrama por la tarima.
- Medidas: tarima de 16 (X) x 8 (Z) x 1,5: tres escalones de 0,5 x 0,6 adelante (z -4 a -2,8) y el estrado
  hasta z = 4 (la pared). Mesa de 6 x 3,0 x 2,4 (arriba a 4,5) centrada en z = 1,2. Cruz de 8 (y 1,5 a 9,5),
  brazo de 5 a 7,0 de alto, barras cuadradas de 0,5, puntas que se abren a 1,0 en los últimos 0,8; apoyada en
  la pared (z 3,5 a 4,0) con dos grapas. Candeleros: dos en la mesa (1,2) y dos de pie (4,6) junto a la cruz.
- Piezas (convexas para la colisión de casco): Platform, Table (mesa y mantel), Cross, Candlestick_1..4,
  Candle_Glow_1..4 (llamas), Silver_Crust.
- La cruz es el diseño del arma del Predicador (fase 3) en grande: el arma tiene que copiar estas
  proporciones (barra 1/16 del alto, brazo a 11/16, puntas abiertas al doble del ancho).
- Inferido: nombres de las piezas, mesa con patas y travesaño, mantel con caída adelante de borde
  desgarrado y dos manchas talladas, velas cloth_white, rombo en el cruce de la cruz, dónde crece la costra.
  9 materiales: los nombra el prompt (madera, cloth_white, blood_dry, brass, llamas, iron, plata).

Vueltas: 1) restos de perfiles repetidos; mantel de arriba y caídas compartían aristas (se soldarían) ·
2) las grapas a la pared asomaban a los costados y la cruz se leía de tres brazos; la cama de la costra en
neón entera se leía como un charco de agua · 3) grapas del ancho de la barra; cama de silver_crust con juntas
de neón finas que salen del pie de la cruz.

Revisión
- 1056 triángulos contra 800 (+32 %, calidad primero): mesa y mantel 336 (caída desgarrada y dos manchas
  talladas), candeleros 288 (4, dos de pie de 4,6), costra 236 (cama, 10 placas, 8 juntas de neón),
  cruz 128, tarima 28, llamas 40.
- Medidas: 16 x 9,5 x 8,01 (la tarima 16 x 1,5 x 8; la cruz hasta 9,5; el 8,01 son las grapas, 0,01 en la
  pared). Mesa 6 x 3,0 x 2,4; cruz de 8 con brazo de 5.
- Orígenes: tarima, mesa, cruz y costra en (0, 0, 0); cada candelero en su pie; cada llama en la punta de su
  vela (para prenderlas o apagarlas de a una).
- Dudoso: el arma del Predicador (fase 3) todavía no existe: tiene que copiar esta cruz (barras de 1/16 del
  alto, brazo a 11/16, puntas abiertas al doble). Los nombres de las piezas son inferidos.
"""

import math

MID, DARK, CLOTH, BLOOD, BRASS, GLOW, IRON, CRUST, NEON = ("wood_mid", "wood_dark", "cloth_white", "blood_dry",
                                                           "brass", "lamp_glow", "iron", "silver_crust",
                                                           "silver_neon")
TOP = 1.5                      # estrado
WALL_Z = 4.0


def ring(c, r, n, y, start=0.5):
    return [(c[0] + r * math.cos(2 * math.pi * (k + start) / n), y, c[2] + r * math.sin(2 * math.pi * (k + start) / n))
            for k in range(n)]


def build(mk):
    # ---- tarima: un prisma con los escalones (perfil en zy) ----
    part = mk.part("Platform", (0, 0, 0))
    prof = [(WALL_Z, 0.0), (WALL_Z, TOP), (-2.8, TOP), (-2.8, 1.0), (-3.4, 1.0), (-3.4, 0.5), (-4.0, 0.5), (-4.0, 0.0)]
    mk.prism(part, prof, 16.0, MID, plane="zy", center=(0, 0, 0))
    for z, y in ((-2.8, 1.25), (-3.4, 0.75), (-4.0, 0.25)):                               # contrahuellas oscuras
        mk.paint(part, DARK, box=((0, y, z), (17, 0.4, 0.02)))
    # ---- mesa con mantel ----
    part = mk.part("Table", (0, 0, 0))
    tx, tz0, tz1, ty = 3.0, 0.0, 2.4, TOP + 3.0
    mk.box(part, (0, ty - 0.15, (tz0 + tz1) / 2), (2 * tx, 0.3, tz1 - tz0), DARK)          # tablero
    for sx in (-1, 1):
        for zz in (tz0 + 0.3, tz1 - 0.3):
            mk.box(part, (sx * (tx - 0.3), (TOP + ty - 0.3) / 2, zz), (0.42, ty - 0.3 - TOP + 0.02, 0.42), DARK)
        mk.box(part, (sx * (tx - 0.3), TOP + 0.7, (tz0 + tz1) / 2), (0.3, 0.3, tz1 - tz0 - 0.6), DARK)  # travesaño
    mk.box(part, (0, TOP + 0.7, (tz0 + tz1) / 2), (2 * tx - 0.6, 0.28, 0.28), DARK)
    # mantel: encima, caída de adelante con borde desgarrado, caídas cortas a los costados
    mk.box(part, (0, ty + 0.03, (tz0 + tz1) / 2), (2 * tx + 0.3, 0.06, tz1 - tz0 + 0.3), CLOTH)
    torn = [(3.15, 2.7), (2.4, 2.25), (1.8, 2.55), (1.0, 2.0), (0.3, 2.35), (-0.5, 1.9), (-1.2, 2.45), (-1.9, 2.15),
            (-2.6, 2.6), (-3.15, 2.4)]
    # (las caídas se meten 0,01 en el mantel de arriba y quedan 0,01 más bajas: si comparten la arista, se sueldan)
    torn = [(min(3.12, max(-3.12, x)), y) for x, y in torn]
    front = [(x, TOP + y) for x, y in torn] + [(-3.12, ty + 0.05), (3.12, ty + 0.05)]
    mk.prism(part, front, 0.06, CLOTH, plane="xy", center=(0, 0, tz0 - 0.17))
    for sx in (-1, 1):
        side = [(tz0 - 0.12, ty + 0.05), (tz1 + 0.12, ty + 0.05), (tz1 + 0.12, ty - 0.7), (1.6, ty - 0.95),
                (0.8, ty - 0.6), (tz0 - 0.12, ty - 1.0)]
        mk.prism(part, side, 0.06, CLOTH, plane="zy", center=(sx * (tx + 0.17), 0, 0))
    for (cx, cy, rx, ry) in ((0.9, ty - 0.7, 0.42, 0.35), (-1.6, ty - 1.4, 0.3, 0.42)):     # manchas de sangre seca
        blob = [(1.0, 0.1), (0.6, 0.8), (-0.2, 1.0), (-0.9, 0.55), (-1.0, -0.2), (-0.4, -0.9), (0.5, -0.8)]
        mk.carve(part, BLOOD, prism=dict(profile=[(cx + bx * rx, cy + by * ry) for bx, by in blob], depth=0.06,
                                         plane="xy", center=(0, 0, tz0 - 0.22)))
    # ---- cruz de hierro contra la pared ----
    part = mk.part("Cross", (0, 0, 0))
    b, f, fl = 0.25, 0.5, 0.8                     # media barra, media punta abierta, largo del abanico
    y0, y1, ya, xa = TOP, TOP + 8.0, TOP + 5.5, 2.5
    cross = [(-b, y0), (b, y0), (b, ya - b), (xa - fl, ya - b), (xa, ya - f), (xa, ya + f), (xa - fl, ya + b),
             (b, ya + b), (b, y1 - fl), (f, y1), (-f, y1), (-b, y1 - fl), (-b, ya + b), (-(xa - fl), ya + b),
             (-xa, ya + f), (-xa, ya - f), (-(xa - fl), ya - b), (-b, ya - b)]
    zc = WALL_Z - 0.25
    mk.prism(part, cross, 0.5, IRON, plane="xy", center=(0, 0, zc))
    mk.hull(part, [(0, ya + 0.6, zc - 0.32), (0.6, ya, zc - 0.32), (0, ya - 0.6, zc - 0.32), (-0.6, ya, zc - 0.32),
                   (0, ya + 0.75, zc), (0.75, ya, zc), (0, ya - 0.75, zc), (-0.75, ya, zc)], IRON, detail=True)  # rombo
    for y in (TOP + 1.6, y1 - 1.6):                                                        # grapas a la pared
        # apenas más anchas que la barra: si asoman a los costados se leen como un brazo más (medido)
        mk.box(part, (0, y, zc - 0.05), (0.62, 0.22, 0.62), IRON, detail=True)
        mk.box(part, (0, y, zc - 0.38), (0.12, 0.12, 0.08), IRON, detail=True)              # perno
    # ---- candeleros y llamas ----
    sticks = [((-2.3, ty + 0.06, 1.6), 1.2, 0.32), ((2.3, ty + 0.06, 1.6), 1.2, 0.32),
              ((-5.2, TOP, 2.9), 4.6, 0.55), ((5.2, TOP, 2.9), 4.6, 0.55)]
    for i, (c, h, rb) in enumerate(sticks, start=1):
        part = mk.part(f"Candlestick_{i}", (c[0], c[1], c[2]))
        mk.hull(part, ring(c, rb, 6, c[1]) + ring(c, rb * 0.55, 6, c[1] + 0.18 * h / 1.2 * 0.6), BRASS)  # pie
        mk.box(part, (c[0], c[1] + h * 0.5, c[2]), (0.12 + 0.04 * (h > 2), h * 0.85, 0.12 + 0.04 * (h > 2)), BRASS)
        cup = c[1] + h * 0.9
        mk.hull(part, ring(c, 0.1, 6, cup - 0.12) + ring(c, 0.26, 6, cup), BRASS)          # platillo
        mk.cyl(part, (c[0], cup + 0.35, c[2]), 0.11, 0.72, CLOTH, sides=6)                 # vela
        g = mk.part(f"Candle_Glow_{i}", (c[0], cup + 0.71, c[2]))
        mk.hull(g, ring((c[0], 0, c[2]), 0.07, 5, cup + 0.78) + [(c[0], cup + 0.69, c[2]), (c[0], cup + 1.02, c[2])], GLOW)
    # ---- costra de plata al pie de la cruz, desparramada por el estrado ----
    part = mk.part("Silver_Crust", (0, 0, 0))
    # cama de costra (una cama de neón entera se leía como un charco de agua, medido) con juntas de neón finas
    # que salen del pie de la cruz
    bed = [(0.0, 3.85), (1.8, 3.6), (3.6, 2.8), (4.2, 1.6), (3.4, 0.6), (1.2, 2.6), (-1.0, 2.7), (-3.2, 0.2),
           (-4.4, 1.2), (-3.6, 3.0), (-1.6, 3.7)]
    mk.prism(part, bed, 0.06, CRUST, plane="xz", center=(0, TOP + 0.025, 0))
    for path in (((0.0, 3.5), (1.6, 3.1), (2.9, 2.3), (3.8, 1.3)), ((0.0, 3.5), (-1.4, 3.15), (-2.7, 2.2), (-3.7, 1.0)),
                 ((1.6, 3.1), (1.0, 2.75)), ((-2.7, 2.2), (-3.1, 0.8))):
        for (xa, za), (xb, zb) in zip(path, path[1:]):
            dx, dz = xb - xa, zb - za
            L = math.hypot(dx, dz)
            nx, nz = -dz / L * 0.045, dx / L * 0.045
            xb2, zb2 = xb + dx / L * 0.05, zb + dz / L * 0.05                           # se pasa del próximo
            mk.hull(part, [(x + s2 * nx, y, z + s2 * nz) for x, z in ((xa, za), (xb2, zb2)) for s2 in (-1, 1)
                           for y in (TOP + 0.04, TOP + 0.075)], NEON, detail=True)
    plates = [(0.0, 3.55, 0.45, 0.55), (0.9, 3.3, 0.35, 0.35), (-0.8, 3.35, 0.38, 0.42), (2.2, 3.0, 0.3, 0.3),
              (3.3, 2.0, 0.28, 0.25), (-2.3, 2.9, 0.32, 0.3), (-3.4, 1.6, 0.3, 0.28), (-3.0, 0.7, 0.24, 0.2),
              (3.6, 1.2, 0.22, 0.18), (1.4, 2.7, 0.24, 0.22)]
    for k, (x, z, size, height) in enumerate(plates):
        base = [(x + size * math.cos(2 * math.pi * (a + 0.13 * k) / 5), TOP + 0.045,
                 z + size * 0.85 * math.sin(2 * math.pi * (a + 0.13 * k) / 5)) for a in range(5)]
        tip = (x + size * 0.2, TOP + 0.04 + height, z - size * 0.15)
        ridge = (x - size * 0.3, TOP + 0.04 + height * 0.65, z + size * 0.2)
        mk.hull(part, base + [tip, ridge], CRUST)

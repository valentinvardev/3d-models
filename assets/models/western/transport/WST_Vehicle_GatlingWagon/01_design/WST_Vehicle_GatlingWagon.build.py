"""
Receta de WST_Vehicle_GatlingWagon, la Gatling sobre pedestal giratorio para la carreta (prompt 066, Bloques A + F).

Brief
- Silueta que se lee a 40 studs: haz de 6 caños largos con dos platos redondos, caja de culata de
  bronce gorda, cargador vertical arriba, manivela grande a la derecha, timón de puntería atrás,
  todo sobre un pedestal de hierro con base redonda pesada atornillada a una tabla.
- Lenguaje de armas estilizadas de juegos conocidos (sin copiar ninguna): proporciones un poco
  exageradas (caja y platos gruesos), chanflanes en lo que manda (caja, platos, base), bronce /
  pavonado / hierro bien separados, la mecánica a la vista (manivela, tolva, eje central de los caños).
- Medidas: tabla 1,8 x 0,15 x 1,8; base giratoria de 1,4 de diámetro; pedestal de 0,15 a 1,35 (1,2);
  muñones a 1,85; caja 1,0 x 0,8 x 1,2 (z -0,2 a 1,0); caños de 2,8 (z -0,2 a -3,0); cargador
  0,3 x 0,9 x 0,5 sobre la tolva.
- Piezas: Mount (fija, origen del modelo = _Mount, abajo del pedestal), Body (cureña: horquilla,
  caja, tolva, timón; origen en los muñones sobre el eje del pedestal, gira y apunta), Magazine
  (origen en su base), Barrels (origen en el eje del haz, gira), Crank (origen en su eje).
- Tallado: bocas de los 6 caños. Chanflanes: caja, platos, base y horquilla.
- Inferido: origen del modelo abajo del pedestal y no en una empuñadura (no es un arma de mano; se
  atornilla a la carreta); timón con dos empuñaduras atrás para apuntar; _Seat_Gunner a la altura
  de la cadera de un jugador sentado detrás (no hay asiento en la lista de piezas).

Vueltas: 1) primera versión: 4440 triángulos; el chanflán a 35° agarraba los lados de los cilindros de
10 caras (36°) y la booleana de las bocas unía caños y platos (1812 en el haz) · 2) chanflán a 40°,
haz sin chanflán, cascabel y muñones como detalle · 3) platos del haz como detalle (558 en el haz),
z-fighting de la horquilla (plato y puente con la misma base) y de la manivela · 4) brazo de la
manivela de verdad ancho (los puntos estaban corridos a lo largo del brazo: se veía un alambre).

Revisión
- 2978 triángulos contra 1500 de referencia (arma: calidad primero). Cureña 1164 (caja de bronce
  con chanflanes, horquilla, tolva, alzas, timón con empuñaduras, tornillos), montaje 668 (base de 16
  lados con chanflán y 12 pernos), haz 558 (6 caños de 8 lados con boca tallada, eje, 3 platos),
  manivela 376, cargador 176.
- Alto 3,3 con el cargador; el eje de los caños a 1,85 de la tabla: montado en el piso de la carreta
  (2,6) queda a 4,45, por encima de las barandas (4,2).
- Dudoso para Valentin: el Bloque F pide el origen en la empuñadura; acá el origen y _Mount están
  abajo del pedestal, porque se atornilla a la carreta. Body gira y apunta desde los muñones (la
  horquilla va con Body, así que al subir los caños la horquilla se inclina con ellos).
"""

import math

AXIS_Y = 1.85                    # eje de los caños y de los muñones
HOUSING = (-0.20, 1.00)          # caja de culata en z
BARREL_Z = (-3.00, -0.20)        # caños
CRANK_AX = (0.58, AXIS_Y, 0.62)  # eje de la manivela
MAG_BASE = (0.0, 2.37, 0.30)     # base del cargador


def build(mk):
    # ---------------- montaje fijo ----------------
    mount = mk.part("Mount", (0, 0, 0))
    mk.box(mount, (0, 0.075, 0), (1.80, 0.15, 1.80), "wood_dark")                         # tabla
    mk.cyl(mount, (0, 0.275, 0), 0.70, 0.25, "iron", sides=16)                             # base giratoria pesada
    mk.cyl(mount, (0, 0.44, 0), 0.40, 0.10, "iron", sides=12, top=0.85)                   # cuello de la base
    mk.cyl(mount, (0, 0.85, 0), 0.19, 0.84, "iron", sides=10, top=0.80)                   # columna
    mk.cyl(mount, (0, 1.30, 0), 0.24, 0.10, "iron", sides=12)                             # collar
    mk.bevel(mount, width=0.025, angle=40)          # 40°: solo los filos, no los lados de los cilindros de 10-16 caras
    for i in range(8):                                                                      # pernos de la base
        a = 2 * math.pi * (i + 0.5) / 8
        mk.cyl(mount, (0.58 * math.cos(a), 0.415, 0.58 * math.sin(a)), 0.055, 0.06, "steel_light", sides=6, detail=True)
    for x in (-0.76, 0.76):                                                                 # tirafondos de la tabla
        for z in (-0.76, 0.76):
            mk.cyl(mount, (x, 0.165, z), 0.06, 0.04, "steel_light", sides=6, detail=True)

    # ---------------- cureña: horquilla, caja de culata, tolva, timón ----------------
    body = mk.part("Body", (0, AXIS_Y, 0))
    mk.cyl(body, (0, 1.395, 0), 0.26, 0.07, "iron", sides=12)                             # plato de la horquilla
    for s in (-1, 1):
        mk.hull(body, [(s * x, y, z) for x in (0.56, 0.68) for y, z in
                       ((1.36, -0.20), (1.36, 0.20), (1.92, -0.12), (1.92, 0.12))], "iron")       # brazos
        mk.hull(body, [(s * x, y, z) for x in (0.20, 0.665) for y, z in ((1.35, -0.16), (1.35, 0.16), (1.44, -0.16), (1.44, 0.16))],
                "iron")                                                                    # puente (corrido: no coplanar con el brazo)
    zc = sum(HOUSING) / 2
    mk.box(body, (0, AXIS_Y, zc), (1.0, 0.8, HOUSING[1] - HOUSING[0]), "brass")            # caja de culata
    mk.box(body, (0, AXIS_Y + 0.43, 0.82), (0.84, 0.08, 0.30), "gunmetal")                # tapa de atrás
    mk.cyl(body, (0, AXIS_Y, HOUSING[0] - 0.05), 0.40, 0.12, "gunmetal", axis="z", sides=12, detail=True)   # collar del haz
    mk.cyl(body, (0, AXIS_Y, HOUSING[1] + 0.06), 0.18, 0.14, "gunmetal", axis="z", sides=8, top=0.6, detail=True)  # cascabel
    mk.cyl(body, (0, AXIS_Y, HOUSING[1] + 0.16), 0.07, 0.08, "gunmetal", axis="z", sides=8, detail=True)
    for s in (-1, 1):
        mk.cyl(body, (s * 0.56, AXIS_Y, 0), 0.13, 0.14, "iron", axis="x", sides=10, detail=True)   # muñones
    # tolva: marco abierto arriba donde calza el cargador
    mk.box(body, (0, AXIS_Y + 0.44, MAG_BASE[2]), (0.40, 0.10, 0.62), "iron")
    for s in (-1, 1):
        mk.box(body, (s * 0.19, AXIS_Y + 0.55, MAG_BASE[2]), (0.06, 0.16, 0.62), "iron")
    # alzas
    mk.prism(body, [(-0.12, 0.0), (0.0, 0.0), (-0.03, 0.13), (-0.09, 0.13)], 0.05, "iron", plane="zy",
             center=(0, AXIS_Y + 0.40, HOUSING[0] + 0.12))
    mk.prism(body, [(0.0, 0.0), (0.14, 0.0), (0.14, 0.12), (0.09, 0.12), (0.07, 0.06), (0.05, 0.12), (0.0, 0.12)],
             0.14, "iron", plane="zy", center=(0, AXIS_Y + 0.47, 0.78))
    # timón de puntería con dos empuñaduras
    mk.hull(body, [(x, y, z) for x in (-0.06, 0.06) for y, z in ((1.50, 0.90), (1.62, 0.90), (1.40, 1.62), (1.50, 1.62))], "iron")
    mk.box(body, (0, 1.45, 1.62), (0.90, 0.10, 0.10), "iron")
    mk.bevel(body, width=0.022, angle=40)
    for s in (-1, 1):
        mk.cyl(body, (s * 0.58, 1.45, 1.62), 0.075, 0.30, "wood_dark", axis="x", sides=8, detail=True)   # empuñaduras
        for y, z in ((AXIS_Y + 0.25, 0.10), (AXIS_Y - 0.25, 0.10), (AXIS_Y + 0.25, 0.80), (AXIS_Y - 0.25, 0.80)):
            mk.cyl(body, (s * 0.51, y, z), 0.045, 0.04, "steel_light", axis="x", sides=6, detail=True)  # tornillos
        mk.cyl(body, (s * 0.645, AXIS_Y, 0), 0.07, 0.05, "steel_light", axis="x", sides=6, detail=True)  # tapa del muñón
    mk.cyl(body, (0.52, CRANK_AX[1], CRANK_AX[2]), 0.12, 0.06, "gunmetal", axis="x", sides=10, detail=True)  # buje de la manivela

    # ---------------- haz de caños (gira) ----------------
    bar = mk.part("Barrels", (0, AXIS_Y, BARREL_Z[1]))
    z0, z1 = BARREL_Z
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        mk.cyl(bar, (0.18 * math.cos(a), AXIS_Y + 0.18 * math.sin(a), (z0 + z1) / 2), 0.066, z1 - z0, "gunmetal",
               axis="z", sides=8)
    mk.cyl(bar, (0, AXIS_Y, (z0 + z1) / 2 - 0.04), 0.07, z1 - z0 + 0.08, "iron", axis="z", sides=8)     # eje central
    # platos como detalle: si entran en la base, la booleana de las bocas une caños y platos (1400 triángulos)
    for z, r, t in ((-0.34, 0.33, 0.10), (-1.55, 0.31, 0.08), (-2.78, 0.32, 0.10)):
        mk.cyl(bar, (0, AXIS_Y, z), r, t, "iron", axis="z", sides=12, detail=True)
    mk.cyl(bar, (0, AXIS_Y, z0 - 0.03), 0.10, 0.08, "iron", axis="z", sides=8)                          # tuerca de punta
    for k in range(6):                                                                                   # bocas
        a = 2 * math.pi * k / 6 + math.pi / 6
        mk.carve(bar, "coal", points=mk.pts_cyl((0.18 * math.cos(a), AXIS_Y + 0.18 * math.sin(a), z0), 0.034, 0.16,
                                                axis="z", sides=6))

    # ---------------- manivela (gira sobre su eje) ----------------
    crank = mk.part("Crank", CRANK_AX)
    cx, cy, cz = CRANK_AX
    mk.cyl(crank, (cx + 0.06, cy, cz), 0.06, 0.16, "iron", axis="x", sides=8)                          # eje
    ang = math.radians(35)                                                                               # brazo hacia abajo y atrás
    ey, ez = cy - 0.46 * math.cos(ang), cz + 0.46 * math.sin(ang)
    py_, pz_ = math.sin(ang), math.cos(ang)                                                              # perpendicular al brazo
    mk.hull(crank, [(x, y, z) for x in (cx + 0.10, cx + 0.21) for y, z in
                    ((cy + 0.10 * py_, cz + 0.10 * pz_), (cy - 0.10 * py_, cz - 0.10 * pz_),
                     (ey + 0.065 * py_, ez + 0.065 * pz_), (ey - 0.065 * py_, ez - 0.065 * pz_))], "iron")
    mk.cyl(crank, (cx + 0.155, cy, cz), 0.12, 0.13, "iron", axis="x", sides=8)                         # cubo del brazo
    mk.cyl(crank, (cx + 0.155, ey, ez), 0.09, 0.13, "iron", axis="x", sides=8)                         # ojo de la manija
    mk.bevel(crank, width=0.014, angle=40)
    mk.cyl(crank, (cx + 0.40, ey, ez), 0.075, 0.36, "wood_dark", axis="x", sides=8, detail=True)       # manija de madera
    mk.cyl(crank, (cx + 0.59, ey, ez), 0.09, 0.05, "steel_light", axis="x", sides=8, detail=True)      # tope

    # ---------------- cargador vertical (se saca y se cambia) ----------------
    mag = mk.part("Magazine", MAG_BASE)
    mx, my, mz = MAG_BASE
    mk.box(mag, (mx, my + 0.45, mz), (0.30, 0.90, 0.50), "iron", top=(0.92, 0.95))
    for y in (my + 0.20, my + 0.62):
        mk.box(mag, (mx, y, mz), (0.33, 0.06, 0.53), "steel_light")                                     # costillas
    mk.box(mag, (mx, my + 0.92, mz), (0.22, 0.05, 0.40), "brass")                                       # tapa
    mk.bevel(mag, width=0.012, angle=35)

    mk.marker("_Muzzle", (0, AXIS_Y, z0))
    mk.marker("_Seat_Gunner", (0, 0.95, 1.85))
    mk.marker("_Mount", (0, 0, 0))

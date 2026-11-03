"""
Receta de WST_Vehicle_Wagon, la carreta abierta para 4 (prompt 065, Bloques A + B).

Brief
- Silueta que se lee a 40 studs: caja larga y baja con barandas de tablas mostaza, ruedas de rayos
  grandes atrás y chicas adelante (se ve el aire entre los rayos), pescante alto adelante con
  respaldo y freno de palanca, lanza larga hacia adelante con el balancín para dos caballos.
- Medidas: caja 10 (z) x 5 (x) x 1,0 (y 1,6 a 2,6), piso a 2,6; barandas de 1,6 (arriba a 4,2);
  asiento del pescante a 3,8; ruedas de 3,2 adelante (eje en y 1,6, z -3,3) y 3,8 atrás (eje en
  y 1,9, z +3,3), con el plano de la rueda en x = ±2,85 (afuera de la caja); lanza que sale 6 del
  frente de la caja (punta en z = -11). Origen del modelo: piso, centro de la caja.
- Piezas: Body (caja, bastidor, barandas, pescante, estribo, freno, lanza, balancín, ejes), WheelFL,
  WheelFR, WheelBL, WheelBR (origen en el cubo), Chest (origen en su base) y Lid (origen en la
  bisagra de atrás), Load (la variante AmmoLoad, origen en el piso). Marcadores _Seat_Driver,
  _Seat_1.._3, _Hitch.
- Tablas: cada tabla es una pieza con su color y detrás hay un alma de wood_dark metida 0,03: las
  juntas se leen como líneas oscuras de verdad (nada coplanar, nada pegado encima). Pintura mostaza
  gastada: algunas tablas son de madera pelada (reemplazadas), una esquina mordida.
- Rueda (función `wheel`, la reusa WST_Vehicle_PeddlerWagon): llanta de hierro y pina de madera
  como dos medios anillos encimados 1°, 12 rayos sueltos con aire entre ellos, cubo con zuncho.
- Inferido: el lado de la lanza "que sale 6" se mide desde el frente de la caja; trocha de ruedas;
  tablero de los pies inclinado; carga a la derecha para dejar un pasillo a la izquierda (_Seat_3).

Vueltas: 1) primera versión; z-fighting en las puntas de los medios anillos (pina y llanta cortadas
en el mismo plano), en el alma de las barandas (su base coincidía con la de las tablas) y en las
puntas de culata/frente contra las barandas; bordes no-manifold donde las dos varas de la tijera
terminaban en el mismo punto (la soldadura las une) · 2) almas y paredes corridas 0,01-0,04, tijera
abierta · 3) sin el zuncho de adentro del cubo (no se ve; 28 triángulos por rueda).

Revisión
- 3856 triángulos contra 1800 de referencia; sin la carga (variante) son 3280. Las cuatro ruedas son
  1968: el prompt pide 12 rayos sueltos con aire entre ellos y llanta de hierro, y con 16 lados la
  rueda grande (3,8) sigue redonda. Caja 1096 (tablas sueltas con juntas oscuras de verdad, parantes,
  pescante, freno con cremallera, lanza, balancín y voleas). Ninguna pieza pasa de 1100.
- Ancho 6,4 (la caja mide 5; las ruedas van afuera en x = ±2,85). Largo 16,2: caja 10 + lanza 6.
- La caja (Body) es cóncava: la colisión por casco convexo la va a cerrar arriba; si molesta para
  pararse adentro, en Studio va con colisión "Box"/"Precise" o con piezas de colisión aparte.
"""

import math

from mathutils import Vector

BED_Z, BED_X = 5.0, 2.5                      # medio largo y medio ancho de la caja
FLOOR, BED_BOTTOM, SIDE_TOP = 2.6, 1.62, 4.2
WHEEL_X = 2.85
FRONT_HUB, BACK_HUB = (1.6, -3.3), (1.9, 3.3)   # (alto del cubo = radio, z)
TONGUE_TIP = (0.0, 2.45, -11.0)


def wheel(mk, name, hub, radius, sides=16, spokes=12, rim="wood_mid", spoke="wood_mid", hubmat="wood_dark",
          tire="iron", width=0.22):
    """Rueda de rayos en el plano y-z (eje en x), con el origen en el cubo."""
    part = mk.part(name, hub)
    hx, hy, hz = hub

    def half_ring(r_in, r_out, w, mat, a0, over):
        n = sides // 2
        d = math.radians(over)                    # las dos mitades se enciman: sin vértices compartidos
        angs = [a0 - d + (math.pi + 2 * d) * i / n for i in range(n + 1)]
        outer = [(hz + r_out * math.cos(a), hy + r_out * math.sin(a)) for a in angs]
        inner = [(hz + r_in * math.cos(a), hy + r_in * math.sin(a)) for a in reversed(angs)]
        mk.prism(part, outer + inner, w, mat, plane="zy", center=(hx, 0, 0))

    for k, a0 in enumerate((0.0, math.pi)):
        half_ring(radius - 0.30, radius - 0.08, width - 0.004 * k, rim, a0, 1.0)        # pina de madera
        half_ring(radius - 0.11, radius, width + 0.05 - 0.004 * k, tire, a0, 1.6)       # llanta (otro corte: no coplanar)
    for i in range(spokes):                                                       # rayos sueltos
        a = 2 * math.pi * (i + 0.5) / spokes
        c, s = math.cos(a), math.sin(a)
        tang = Vector((0, c, -s))
        pts = []
        for r, wt in ((0.20, 0.07), (radius - 0.26, 0.05)):
            p = Vector((hx, hy + r * s, hz + r * c))
            pts += [tuple(p + tang * sa * wt + Vector((sx * 0.06, 0, 0))) for sa in (-1, 1) for sx in (-1, 1)]
        mk.hull(part, pts, spoke)
    mk.cyl(part, hub, 0.26, 0.56, hubmat, axis="x", sides=8)                    # cubo
    out = 1 if hx > 0 else -1
    mk.cyl(part, (hx + out * 0.16, hy, hz), 0.285, 0.07, tire, axis="x", sides=8)   # zuncho (el de adentro no se ve)
    mk.cyl(part, (hx + out * 0.31, hy, hz), 0.15, 0.08, tire, axis="x", sides=6)   # tapa del cubo
    return part


def planks_x(mk, part, x0, x1, y0, y1, z_in, z_out, mats, gap=0.05, chip=None):
    """Pared de tablas horizontales a lo largo de x (frente o culata), entre z_in y z_out, con alma oscura."""
    n = len(mats)
    h = (y1 - y0 - gap * (n - 1)) / n
    zc, th = (z_in + z_out) / 2, abs(z_out - z_in)
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2 - 0.02, zc), (x1 - x0 - 0.06, y1 - y0 - 0.06, th - 0.06), "wood_dark")
    for i, m in enumerate(mats):
        yb = y0 + i * (h + gap)
        mk.box(part, ((x0 + x1) / 2, yb + h / 2, zc), (x1 - x0, h, th), m)


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- bastidor y piso ----------------
    for s in (-1, 1):
        mk.box(body, (s * 2.33, (BED_BOTTOM + 2.44) / 2, 0), (0.34, 2.44 - BED_BOTTOM, 2 * BED_Z), "wood_dark")   # largueros
    for z, y in ((FRONT_HUB[1], 1.80), (BACK_HUB[1], 2.08)):
        mk.box(body, (0, y + 0.18, z), (2 * BED_X - 0.02, 0.40, 0.42), "wood_dark")                            # traviesas
    mk.box(body, (0, 2.48, 0), (2 * BED_X - 0.04, 0.12, 2 * BED_Z - 0.02), "wood_dark")                       # alma del piso
    n = 10
    for i in range(n):
        x = -BED_X + (i + 0.5) * (2 * BED_X / n)
        mk.box(body, (x, 2.53, 0), (2 * BED_X / n - 0.05, 0.14, 2 * BED_Z - 0.04), "wood_light" if i % 2 else "wood_mid")
    # ejes (el de adelante pasa por debajo de los largueros, el de atrás los cruza)
    mk.box(body, (0, FRONT_HUB[0], FRONT_HUB[1]), (2 * WHEEL_X - 0.5, 0.28, 0.30), "wood_dark")
    mk.box(body, (0, BACK_HUB[0], BACK_HUB[1]), (2 * WHEEL_X - 0.5, 0.28, 0.30), "wood_dark")

    # ---------------- barandas: tablas mostaza gastadas, juntas oscuras, parantes afuera ----------------
    stakes = (-4.86, -1.70, 1.70, 4.86)
    for s in (-1, 1):
        xi, xo = s * 2.38, s * BED_X
        xc = (xi + xo) / 2
        mk.box(body, (xc, (FLOOR + SIDE_TOP) / 2, 0), (0.06, SIDE_TOP - FLOOR - 0.08, 2 * BED_Z - 0.06), "wood_dark")
        h = (SIDE_TOP - FLOOR - 0.10) / 3
        bare = {(0, 1), (2, 2)} if s > 0 else {(1, 0), (2, 1)}       # tablas reemplazadas, sin pintura
        for row in range(3):
            yb = FLOOR + row * (h + 0.05)
            # tramos separados 0,02 detrás de los parantes: sin vértices compartidos (la soldadura los rompería)
            for seg, (z0, z1) in enumerate(((-BED_Z, -1.71), (-1.69, 1.69), (1.71, BED_Z))):
                mat = "wood_mid" if (row, seg) in bare else "paint_mustard"
                if row == 2 and seg == 2 and s < 0:       # esquina mordida arriba atrás
                    mk.hull(body, [(x, y, z) for x in (xi, xo) for y, z in
                                   ((yb, z0), (yb, z1), (yb + h - 0.22, z1), (yb + h, z1 - 0.40), (yb + h, z0))], mat)
                else:
                    mk.box(body, (xc, yb + h / 2, (z0 + z1) / 2), (0.12, h, z1 - z0), mat)
        for z in stakes:
            mk.box(body, (s * 2.55, 3.05, z), (0.12, 2.40, 0.18), "wood_dark", top=(0.9, 0.9))
            mk.box(body, (s * 2.55, 4.18, z), (0.15, 0.10, 0.21), "iron")                     # casquillo del parante
    # culata baja (dos tablas) y frente bajo (una tabla)
    planks_x(mk, body, -2.40, 2.40, FLOOR, 3.62, BED_Z - 0.13, BED_Z - 0.01, ["paint_mustard", "wood_mid"])
    planks_x(mk, body, -2.40, 2.40, FLOOR, 3.12, -BED_Z + 0.01, -BED_Z + 0.13, ["paint_mustard"])
    # tablero de los pies, inclinado hacia adelante, con sus escuadras
    mk.hull(body, [(x, y, z) for x in (-2.36, 2.36) for y, z in ((3.04, -4.96), (3.14, -4.96), (3.82, -5.60), (3.72, -5.62))],
            "wood_mid")
    for s in (-1, 1):
        mk.hull(body, [(s * x, y, z) for x in (2.18, 2.30) for y, z in ((3.06, -4.98), (3.68, -5.50), (3.10, -5.30))], "wood_dark")

    # ---------------- pescante ----------------
    for s in (-1, 1):
        mk.box(body, (s * 1.80, 3.14, -4.35), (0.12, 1.08, 0.72), "wood_dark")                 # costados del cajón
        mk.box(body, (s * 1.45, 4.09, -3.88), (0.10, 0.78, 0.10), "wood_dark")                 # postes del respaldo
        mk.hull(body, [(s * x, y, z) for x in (1.62, 1.76) for y, z in ((3.66, -4.62), (3.66, -4.08), (3.48, -4.35))], "iron")  # ballestas
    mk.box(body, (0, 3.74, -4.35), (3.90, 0.13, 0.86), "wood_mid")                             # asiento
    mk.box(body, (0, 4.28, -3.86), (3.70, 0.36, 0.10), "wood_mid", rot=(-8, 0, 0))            # respaldo
    mk.box(body, (0, 3.10, -4.70), (3.50, 0.95, 0.08), "wood_dark")                            # frente del cajón
    mk.marker("_Seat_Driver", (-0.80, 3.81, -4.35))

    # ---------------- freno de palanca (derecha) y zapatas en las ruedas de atrás ----------------
    mk.prism(body, [(-4.58, 2.86), (-4.05, 2.86), (-4.10, 3.30), (-4.40, 3.38)], 0.14, "iron", plane="zy",
             center=(2.555, 0, 0))                                                             # cremallera, contra la baranda
    mk.hull(body, [(x, y, z) for x in (2.60, 2.70) for y, z in ((2.92, -4.36), (2.92, -4.26), (4.62, -4.02), (4.62, -3.92))],
            "wood_dark")                                                                       # palanca
    mk.box(body, (2.65, 4.68, -3.97), (0.14, 0.18, 0.14), "iron")                             # empuñadura
    mk.hull(body, [(x, y, z) for x in (2.56, 2.62) for y, z in ((2.88, -4.32), (2.94, -4.30), (1.96, 1.20), (2.02, 1.22))],
            "iron")                                                                            # varilla
    mk.box(body, (0, 1.95, 1.22), (2 * WHEEL_X + 0.1, 0.14, 0.14), "wood_dark")              # balancín del freno
    for s in (-1, 1):
        mk.box(body, (s * WHEEL_X, 1.92, 1.35), (0.24, 0.42, 0.22), "wood_dark")              # zapata contra la llanta

    # ---------------- lanza, tijera y balancín ----------------
    tail = Vector((0.0, 1.62, -3.0))
    tip = Vector(TONGUE_TIP)
    d = (tip - tail).normalized()
    side = Vector((1, 0, 0))
    up = side.cross(d).normalized()
    pts = []
    for p, w in ((tail, 0.13), (tip, 0.10)):
        pts += [tuple(p + side * sx * w + up * sy * w) for sx in (-1, 1) for sy in (-1, 1)]
    mk.hull(body, pts, "wood_dark")
    mk.cyl(body, tuple(tip - d * 0.12), 0.13, 0.22, "iron", axis="z", sides=8, rot=(math.degrees(math.asin(d.y)), 0, 0))
    for s in (-1, 1):                                                                          # tijera hasta el eje
        a, b = Vector((s * 1.0, 1.66, FRONT_HUB[1])), tail + d * 2.6 + Vector((s * 0.05, 0, 0))   # no comparten la punta
        mk.hull(body, [tuple(p + Vector((0, sy, sz))) for p in (a, b) for sy in (-0.07, 0.07) for sz in (-0.07, 0.07)], "wood_dark")
    dt = tail + d * 2.75
    mk.box(body, (0, dt.y + 0.16, dt.z), (3.40, 0.16, 0.18), "wood_dark")                     # balancín
    mk.box(body, (0, dt.y + 0.16, dt.z), (0.30, 0.22, 0.24), "iron")
    for s in (-1, 1):
        mk.box(body, (s * 1.40, dt.y + 0.16, dt.z - 0.30), (0.12, 0.10, 0.44), "iron")         # gancho
        mk.box(body, (s * 1.40, dt.y + 0.16, dt.z - 0.56), (1.60, 0.14, 0.14), "wood_dark")   # volea
        for x in (-0.72, 0.72):
            mk.box(body, (s * 1.40 + x, dt.y + 0.16, dt.z - 0.66), (0.08, 0.08, 0.16), "iron")
    mk.marker("_Hitch", TONGUE_TIP)

    # ---------------- ruedas ----------------
    for name, s, (hy, hz) in (("WheelFL", -1, FRONT_HUB), ("WheelFR", 1, FRONT_HUB),
                              ("WheelBL", -1, BACK_HUB), ("WheelBR", 1, BACK_HUB)):
        wheel(mk, name, (s * WHEEL_X, hy, hz), hy)

    # ---------------- baúl compartido ----------------
    cz, cy0, cy1, lid_h = 4.03, FLOOR - 0.01, 3.86, 0.34
    chest = mk.part("Chest", (0, cy0, cz))
    mk.box(chest, (0, (cy0 + cy1) / 2, cz), (2.94, cy1 - cy0 - 0.02, 1.54), "wood_dark")           # alma
    hb = (cy1 - cy0 - 0.10) / 3
    for i in range(3):                                                                          # tres tablas por cara
        yb = cy0 + i * (hb + 0.05)
        mk.box(chest, (0, yb + hb / 2, cz), (3.0, hb, 1.60), "wood_mid")
    for x in (-0.95, 0.95):                                                                     # zunchos de hierro
        mk.box(chest, (x, (cy0 + cy1) / 2, cz), (0.16, cy1 - cy0 + 0.03, 1.66), "iron")
    for s in (-1, 1):                                                                          # manijas
        mk.box(chest, (s * 1.53, 3.30, cz), (0.08, 0.10, 0.50), "iron")
    mk.box(chest, (0, 3.58, cz - 0.82), (0.26, 0.32, 0.06), "iron")                           # cerradura
    lid = mk.part("Lid", (0, cy1, cz + 0.80))
    mk.box(lid, (0, cy1 + lid_h / 2, cz), (3.04, lid_h, 1.64), "wood_mid", top=(0.96, 0.86))
    for x in (-0.95, 0.95):                                                                     # 0,17: no coplanar con los del baúl
        mk.box(lid, (x, cy1 + lid_h / 2 + 0.01, cz), (0.17, lid_h + 0.03, 1.69), "iron", top=(1, 0.86))
    mk.box(lid, (0, cy1 + 0.10, cz - 0.84), (0.16, 0.26, 0.06), "iron")                      # pasador
    mk.marker("_Seat_1", (-1.60, FLOOR, -2.80))
    mk.marker("_Seat_2", (1.60, FLOOR, -2.80))
    mk.marker("_Seat_3", (-1.75, FLOOR, 1.20))

    # ---------------- variante AmmoLoad: 6 cajones de munición y 2 barriles de pólvora con sogas ----------------
    load = mk.part("Load", (0, FLOOR, 0))

    def crate(c, rot=0.0):
        cx, cy, cz_ = c
        mk.box(load, (cx, cy, cz_), (1.24, 0.70, 0.86), "wood_light", rot=(0, rot, 0))
        for k in (-1, 1):                                                                    # listones de las puntas
            dx, dz = k * 0.54 * math.cos(math.radians(rot)), -k * 0.54 * math.sin(math.radians(rot))
            mk.box(load, (cx + dx, cy, cz_ + dz), (0.14, 0.74, 0.90), "wood_dark", rot=(0, rot, 0))

    y1, y2 = FLOOR + 0.35, FLOOR + 1.05
    for x, z in ((0.90, -0.30), (0.90, 0.62), (0.90, 1.54), (-0.42, -0.30), (-0.42, 0.62)):
        crate((x, y1, z))
    crate((0.25, y2, 0.20), rot=12)
    for x, z in ((-0.50, 1.78), (1.88, 2.42)):                                                # barriles de pólvora
        mk.cyl(load, (x, FLOOR + 0.52, z), 0.40, 1.04, "wood_mid", sides=10, top=1.0)
        mk.cyl(load, (x, FLOOR + 0.52, z), 0.44, 0.30, "wood_mid", sides=10)                  # panza
        for y in (FLOOR + 0.20, FLOOR + 0.84):
            mk.cyl(load, (x, y, z), 0.43, 0.07, "iron", sides=10)
    # sogas: vueltas que abrazan la fila de abajo, una al cajón de arriba y una a un barril
    for z in (-0.30, 0.62):
        mk.box(load, (0.24, y1, z), (2.66, 0.75, 0.09), "rope")
    mk.box(load, (0.25, y2, 0.20), (0.09, 0.75, 0.91), "rope", rot=(0, 12, 0))
    mk.cyl(load, (-0.50, FLOOR + 0.58, 1.78), 0.47, 0.08, "rope", sides=10)

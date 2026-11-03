"""
Receta de WST_Mine_Elevator, el montacargas de la mina (prompt 097, Bloques A + B). Lo usan los 4
jugadores y la cinemática de bajada ("un montacargas que cruje").

Brief
- Silueta a 40 studs: una torre de vigas oscuras de 18 de alto, angosta arriba, con la rueda de rayos
  grande en la punta y un puntal largo hacia atrás; abajo, la jaula de hierro con el piso de tablas
  claras y el portón de reja en el frente.
- Medidas (origen en el piso, al centro de la boca del pozo):
  boca del pozo de 9 x 9 (x, z de -4,5 a 4,5), collar de soleras con la cara de arriba en y = 0;
  torre: cuatro patas de 0,8 en las esquinas (centro ±5,1 abajo, ±3,6 arriba), travesaños a y 6 y 12,
  cruces en los costados y atrás (el frente queda libre para cargar), plataforma de la rueda a y 15,0-15,6
  y puntal trasero hasta z = 13; rueda de 5 de diámetro con eje a y 15,9 y z = +2,3 (el cable baja por
  su frente, sobre el centro de la jaula).
  Jaula de 8 x 8: piso de tablas (cara de arriba a y = 0), cuatro postes de hierro, baranda de 3,4 en
  tres lados (izquierda, derecha y atrás), marco de arriba a y 7,0 con dos vigas en cruz y la oreja del
  cable. Portón de reja en el frente (z = -4,1), 7,4 x 3,4, que corre sobre X por dos guías.
  Forro del pozo: 9 x 9 x 30 de hondo, tablones verticales con juntas pintadas y un marco de cuadros de
  madera cada 4 (y = -2 a -30) que sobresale 0,15: la jaula pasa con 0,5 de luz por lado.
- Piezas: Headframe, Pulley (origen en el eje), Cage (origen en el centro del piso), CageGate (origen en
  su base al centro: se corre sobre X), Cable (dos cables; origen arriba, donde dejan la rueda, así se
  estira hacia abajo), ShaftWalls (origen en la boca).
- Inferido: el lado abierto es el frente (-Z), la altura de la jaula y la baranda, el portón de media
  altura que corre por guías, la rueda detrás del eje del pozo para que el cable caiga al centro, el
  puntal trasero, el collar al ras del piso, los tablones del forro y su luz con la jaula.

Vueltas: 1) z-fighting y bordes rotos: largueros y montantes del portón compartían esquinas (4 caras
por borde), los postes de la jaula al ras del piso y del marco de arriba, el travesaño de atrás de la
plataforma (además la rueda lo atravesaba: ahora va partido), las juntas de la garganta de la rueda con
las de la llanta, el eje al ras de los cojinetes, las paredes del forro al ras en las esquinas; 2184
triángulos · 2) sin la garganta de óxido de la rueda (no se ve a 40 studs, ~140) y juntas del forro cada
2,25 en vez de 1,5.

Revisión
- 1984 triángulos contra 1800 (+10 %): ShaftWalls 552 (32 vigas de cuadros: es lo que se ve en toda la
  bajada), Headframe 480, Cage 416, Pulley 280, CageGate 216, Cable 40.
- Medidas: torre de 18,4 con la rueda (plataforma a 15,6); boca 9 x 9; jaula 8 x 8 con el marco a 7,3;
  forro de 30 de hondo (el punto más bajo, -30,3, es el pie del forro). Luz de la jaula con el forro: 0,5
  por lado (los cuadros sobresalen 0,15 de los tablones).
- La jaula y el portón no tocan la torre ni el forro: cuelgan del cable (la oreja y la rueda los tocan).
  Entre el piso de la jaula y la solera del frente quedan 0,65 de luz (el pozo).
- Dudoso: el travesaño de adelante a y 6 deja 5,75 de paso para entrar a la jaula (alcanza para el
  jugador de 5); ShaftWalls es hueco: con colisión de casco convexo taparía el pozo (CanCollide apagado o
  PreciseConvexDecomposition en Studio).
"""

import math

WOOD, PLANK, IRON, RUST = "wood_dark", "wood_mid", "iron", "rust"
HALF = 4.5                       # medio ancho de la boca del pozo
DEPTH = 30.0
CAGE = 4.0                       # medio ancho de la jaula
CAGE_TOP = 7.0
LEG_B, LEG_T = 5.1, 3.6          # centro de las patas abajo y arriba
TOWER_Y = 15.0
AXLE_Y, AXLE_Z, WHEEL_R = 15.9, 2.3, 2.5
CABLE_X = 0.3


def leg_x(y):
    return LEG_B + (LEG_T - LEG_B) * (y / TOWER_Y)


def beam(mk, part, a, b, w, mat, h=None, detail=False):
    """Viga recta de a a b (puntos del juego) de sección w x h."""
    h = h or w
    ax, ay, az = a
    bx, by, bz = b
    d = (bx - ax, by - ay, bz - az)
    ln = math.sqrt(sum(c * c for c in d))
    u = (d[0] / ln, d[1] / ln, d[2] / ln)
    ref = (0, 1, 0) if abs(u[1]) < 0.9 else (1, 0, 0)
    v = (u[1] * ref[2] - u[2] * ref[1], u[2] * ref[0] - u[0] * ref[2], u[0] * ref[1] - u[1] * ref[0])
    vl = math.sqrt(sum(c * c for c in v))
    v = tuple(c / vl for c in v)
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    pts = []
    for p in (a, b):
        for sv in (-w / 2, w / 2):
            for sn in (-h / 2, h / 2):
                pts.append((p[0] + v[0] * sv + n[0] * sn, p[1] + v[1] * sv + n[1] * sn, p[2] + v[2] * sv + n[2] * sn))
    mk.hull(part, pts, mat, detail=detail)


# ---------------- torre ----------------
def headframe(mk):
    p = mk.part("Headframe", (0, 0, 0))
    # collar: cuatro soleras al ras del piso alrededor de la boca (las de adelante y atrás, más largas)
    for s in (-1, 1):
        mk.box(p, (0, -0.3, s * (HALF + 0.55)), (2 * HALF + 2.4, 0.6, 1.1), WOOD)
        mk.box(p, (s * (HALF + 0.55), -0.302, 0), (1.1, 0.596, 2 * HALF - 0.02), WOOD)
    # patas (inclinadas hacia adentro)
    for sx in (-1, 1):
        for sz in (-1, 1):
            beam(mk, p, (sx * LEG_B, -0.05, sz * LEG_B), (sx * LEG_T, TOWER_Y + 0.6, sz * LEG_T), 0.8, WOOD)
    # travesaños a y 6 y 12 en los cuatro lados (el de adelante a y 12 deja pasar la jaula)
    for y in (6.0, 12.0):
        x = leg_x(y)
        for s in (-1, 1):
            beam(mk, p, (-x - 0.3, y, s * x), (x + 0.3, y, s * x), 0.5, WOOD, h=0.6)
            beam(mk, p, (s * x, y + 0.02, -x - 0.3), (s * x, y + 0.02, x + 0.3), 0.5, WOOD, h=0.6)
    # cruces: costados y atrás, dos tramos
    for y0, y1 in ((0.3, 6.0), (6.0, 12.0)):
        x0, x1 = leg_x(y0), leg_x(y1)
        for s in (-1, 1):
            beam(mk, p, (s * x0, y0, -x0), (s * x1, y1, x1), 0.32, WOOD)
            beam(mk, p, (s * (x0 + 0.04), y0, x0), (s * (x1 + 0.04), y1, -x1), 0.32, WOOD)
        beam(mk, p, (-x0, y0, x0 + 0.04), (x1, y1, x1 + 0.04), 0.32, WOOD)
        beam(mk, p, (x0, y0, x0), (-x1, y1, x1), 0.32, WOOD)
    # plataforma de la rueda: dos largueros a lo largo de Z sobre las patas, y travesaños
    xt = leg_x(TOWER_Y)
    mk.box(p, (0, TOWER_Y + 0.27, -xt), (2 * xt + 0.9, 0.56, 0.7), WOOD)
    for s in (-1, 1):
        mk.box(p, (s * 0.85, TOWER_Y + 0.3, AXLE_Z - 0.6), (0.5, 0.6, 2 * xt + 4.6), WOOD)
        # el travesaño de atrás va partido: la rueda pasa por el medio
        mk.box(p, (s * (xt + 0.45 + 0.7) / 2, TOWER_Y + 0.27, xt), (xt + 0.45 - 0.7, 0.56, 0.7), WOOD)
        mk.box(p, (s * 0.85, AXLE_Y - 0.25, AXLE_Z), (0.6, 0.62, 0.8), IRON)                  # cojinete
    # puntal trasero: de lo alto de la torre a una zapata en el piso, en z = 13
    top, foot = (0.85, TOWER_Y + 0.2, AXLE_Z + 2.0), (2.6, 0.3, 13.0)
    for s in (-1, 1):
        beam(mk, p, (s * top[0], top[1], top[2]), (s * foot[0], foot[1], foot[2]), 0.6, WOOD)
        mk.box(p, (s * 2.6, 0.2, 13.1), (1.2, 0.4, 1.6), WOOD)
    mid = [top[k] + 0.5 * (foot[k] - top[k]) for k in range(3)]
    beam(mk, p, (-mid[0] - 0.2, mid[1], mid[2]), (mid[0] + 0.2, mid[1], mid[2]), 0.45, WOOD)


def pulley(mk):
    p = mk.part("Pulley", (0, AXLE_Y, AXLE_Z))
    c = (0, AXLE_Y, AXLE_Z)
    n = 16

    def ring(r, a0, a1, k):
        return [(r * math.cos(math.radians(a0 + (a1 - a0) * i / k)), r * math.sin(math.radians(a0 + (a1 - a0) * i / k)))
                for i in range(k + 1)]
    # llanta: dos medios anillos (z, y) encimados 1° con 0,004 de diferencia de ancho
    for a0, a1, w in ((0, 181, 0.42), (180, 361, 0.424)):
        prof = ring(WHEEL_R, a0, a1, n // 2) + ring(WHEEL_R - 0.36, a1, a0, n // 2)
        mk.prism(p, [(c[2] + z, c[1] + y) for z, y in prof], w, IRON, plane="zy", center=(0, 0, 0))
    mk.cyl(p, c, 0.42, 0.62, IRON, axis="x", sides=8)                                         # cubo
    mk.cyl(p, c, 0.16, 2.36, RUST, axis="x", sides=6)                                         # eje
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        r0, r1 = 0.3, WHEEL_R - 0.3
        beam(mk, p, (0, c[1] + r0 * math.sin(a), c[2] + r0 * math.cos(a)),
             (0, c[1] + r1 * math.sin(a), c[2] + r1 * math.cos(a)), 0.16, IRON, h=0.12)


# ---------------- jaula ----------------
def cage(mk):
    p = mk.part("Cage", (0, 0, 0))
    # piso de tablas a lo largo de X con juntas pintadas, sobre dos vigas de hierro
    mk.box(p, (0, -0.15, 0), (2 * CAGE, 0.3, 2 * CAGE), PLANK)
    for z in (-2.4, -0.8, 0.8, 2.4):
        for d in (-0.03, 0.03):
            mk.slice(p, (0, 0, z + d), (0, 0, 1))
        mk.paint(p, WOOD, box=((0, 0, z), (2 * CAGE + 0.1, 0.02, 0.07)))
    for x in (-2.6, 2.6):
        mk.box(p, (x, -0.45, 0), (0.3, 0.32, 2 * CAGE - 0.2), IRON, detail=True)
    mk.box(p, (0, -0.45, 0), (2 * CAGE - 0.2, 0.3, 0.3), IRON, detail=True)
    # postes de las esquinas
    for sx in (-1, 1):
        for sz in (-1, 1):
            mk.box(p, (sx * (CAGE - 0.15), (CAGE_TOP - 0.31) / 2, sz * (CAGE - 0.15)), (0.28, CAGE_TOP + 0.31, 0.28), IRON, detail=True)
    # baranda en tres lados (dos barras y un zócalo de tabla)
    for y, hgt, mat in ((1.7, 0.12, IRON), (3.3, 0.14, IRON)):
        for s in (-1, 1):
            mk.box(p, (s * (CAGE - 0.14), y, 0), (0.1, hgt, 2 * CAGE - 0.3), mat, detail=True)
        mk.box(p, (0, y + 0.004, CAGE - 0.14), (2 * CAGE - 0.3, hgt, 0.1), mat, detail=True)
    for s in (-1, 1):
        mk.box(p, (s * (CAGE - 0.16), 0.3, 0), (0.08, 0.6, 2 * CAGE - 0.3), PLANK, detail=True)
    mk.box(p, (0, 0.3, CAGE - 0.16), (2 * CAGE - 0.3, 0.6, 0.08), PLANK, detail=True)
    # barrotes verticales de la baranda (dos por lado)
    for t in (-1.35, 1.35):
        for s in (-1, 1):
            mk.box(p, (s * (CAGE - 0.14), 1.7, t), (0.08, 3.3, 0.08), IRON, detail=True)
        mk.box(p, (t, 1.7, CAGE - 0.14), (0.08, 3.3, 0.08), IRON, detail=True)
    # marco de arriba, cruz y oreja del cable
    for s in (-1, 1):
        mk.box(p, (s * (CAGE - 0.14), CAGE_TOP + 0.05, 0), (0.26, 0.3, 2 * CAGE - 0.04), IRON, detail=True)
        mk.box(p, (0, CAGE_TOP + 0.052, s * (CAGE - 0.14)), (2 * CAGE - 0.3, 0.29, 0.26), IRON, detail=True)
    mk.box(p, (0, CAGE_TOP + 0.18, 0), (2 * CAGE - 0.3, 0.3, 0.4), RUST, detail=True)
    mk.box(p, (0, CAGE_TOP + 0.181, 0), (0.4, 0.302, 2 * CAGE - 0.3), RUST, detail=True)
    mk.box(p, (0, CAGE_TOP + 0.5, -0.1), (1.2, 0.36, 0.5), IRON, detail=True)                   # oreja
    # guías del portón (frente)
    for y in (0.08, 3.62):
        mk.box(p, (0, y, -CAGE - 0.06), (2 * CAGE, 0.12, 0.16), IRON, detail=True)


def cage_gate(mk):
    zg = -CAGE - 0.06
    p = mk.part("CageGate", (0, 0.1, zg))
    w, y0, y1 = 7.4, 0.1, 3.62
    mk.box(p, (0, y0 + 0.06, zg), (w, 0.12, 0.08), IRON)
    mk.box(p, (0, y1 - 0.06, zg), (w, 0.12, 0.08), IRON)
    for s in (-1, 1):
        mk.box(p, (s * (w / 2 - 0.06), (y0 + y1) / 2, zg), (0.1, y1 - y0 - 0.02, 0.086), IRON)
    # reja: barras cruzadas a ±45°, las de un sentido delante de las del otro
    h = y1 - y0 - 0.2
    for k in range(-3, 4):
        cx = k * 1.06
        for sgn, dz in ((1, -0.035), (-1, 0.035)):
            a = math.radians(45)
            half = h / 2 / math.sin(a)
            dx, dy = half * math.cos(a) * sgn, half * math.sin(a)
            p0 = (cx - dx, (y0 + y1) / 2 - dy, zg + dz)
            p1 = (cx + dx, (y0 + y1) / 2 + dy, zg + dz)
            # recortada al marco del portón
            x0c, x1c = max(min(p0[0], p1[0]), -w / 2 + 0.05), min(max(p0[0], p1[0]), w / 2 - 0.05)
            if x1c - x0c < 0.3:
                continue
            ya = (y0 + y1) / 2 + (x0c - cx) * sgn
            yb = (y0 + y1) / 2 + (x1c - cx) * sgn
            beam(mk, p, (x0c, ya, zg + dz), (x1c, yb, zg + dz), 0.07, IRON, h=0.05)


def cable(mk):
    top = (0, AXLE_Y, AXLE_Z - WHEEL_R + 0.1)
    p = mk.part("Cable", top)
    for sx in (-CABLE_X, CABLE_X):
        y0, y1 = CAGE_TOP + 0.6, AXLE_Y
        mk.cyl(p, (sx, (y0 + y1) / 2, top[2]), 0.07, y1 - y0, IRON, axis="y", sides=6)


def shaft_walls(mk):
    p = mk.part("ShaftWalls", (0, 0, 0))
    t = 0.35
    wall = HALF + 0.15                                     # cara de los tablones (los cuadros salen 0,15)
    for s in (-1, 1):
        mk.box(p, (s * (wall + t / 2), -15.06, 0), (t, 29.88, 2 * wall + 0.1), PLANK)
        mk.box(p, (0, -15.06, s * (wall + t / 2)), (2 * wall + 2 * t - 0.04, 29.92, t), PLANK)
    # juntas verticales de los tablones (cada 2,25), pintadas en la cara de adentro
    for v in (-2.25, 0.0, 2.25):
        for d in (-0.035, 0.035):
            mk.slice(p, (v + d, 0, 0), (1, 0, 0))
            mk.slice(p, (0, 0, v + d), (0, 0, 1))
        mk.paint(p, WOOD, box=((v, -DEPTH / 2, 0), (0.075, DEPTH, 2 * wall + 0.1)))
        mk.paint(p, WOOD, box=((0, -DEPTH / 2, v), (2 * wall + 0.1, DEPTH, 0.075)))
    # cuadros de madera cada 4: cuatro vigas que se cruzan en las esquinas (alternan arriba/abajo)
    for k, y in enumerate([-2.0 - 4 * i for i in range(8)]):
        e = 0.02 * (k % 2)
        for s in (-1, 1):
            mk.box(p, (s * (HALF + 0.3), y + e, 0), (0.6, 0.55, 2 * HALF + 1.3), WOOD, detail=True)
            mk.box(p, (0, y - e + 0.01, s * (HALF + 0.3)), (2 * HALF + 1.3, 0.55, 0.6), WOOD, detail=True)


def build(mk):
    headframe(mk)
    pulley(mk)
    cage(mk)
    cage_gate(mk)
    cable(mk)
    shaft_walls(mk)

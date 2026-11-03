"""
Receta de WST_SB_Forge, la herrería de Silver Bend (prompt 112, Bloques A + B).

Brief
- Silueta a 40 studs: fogón de ladrillo con campana de hierro y chimenea alta, fuelle de cuero al
  costado, yunque con cuerno sobre un tronco adelante, barril de templar, rueda de carreta apoyada contra
  el fogón y un estante con herraduras, tenazas y martillos.
- Hearth: fogón de ladrillo redrock (juntas sand: hiladas de 0,4 en el frente y los costados, llagas
  trabadas en el frente) de 4 x 2,8 x 3, mesa de hierro de 4,2 x 0,2 x 3,2 arriba (alto total 3), fosa del
  fuego tallada (2 x 0,6 x 1,6, paredes coal) con carbón apagado adentro, cenicero tallado abajo al frente,
  tobera de hierro en el costado izquierdo. Chimenea de ladrillo atrás (1,6 x 0,9) hasta 9 con remate, y
  campana de chapa de hierro (tronco de pirámide hueco por abajo, hollín coal adentro) agarrada a la
  chimenea. Caballetes del fuelle de madera oscura.
- Coals_Glow: brasas lamp_glow sobre el carbón de la fosa (se apagan escondiendo el objeto).
- Bellows: fuelle de dos tablas en forma de pera (wood_mid) con el cuero en dos fuelles (leather_dark,
  cintura en el medio), boquilla de hierro hasta la tobera y manija atrás. Origen en la bisagra de la
  punta angosta (x -2,75, y 2,04, z -0,2): ahí gira al bombear.
- Anvil: yunque de hierro (cara de arriba gunmetal, más clara) con cuerno hacia -X, talón con agujero
  y martillo apoyado, sobre un tronco de 1,55 (corteza wood_dark, corte wood_mid).
- QuenchBarrel: barril de 10 duelas con panza, dos zunchos y agua (water) 0,2 bajo el borde.
- ToolRack: estante de madera con 4 herraduras colgadas de clavijas arriba, y abajo dos tenazas y dos
  martillos colgados.
- WagonWheel: rueda de 12 rayos (r 1,6, llanta de hierro) apoyada contra el costado derecho del fogón,
  inclinada 12°.
- Objetos (Bloque B: el set tiene concavidades grandes, va en piezas): Hearth, Coals_Glow, Bellows,
  Anvil, QuenchBarrel, ToolRack, WagonWheel. Todos con el origen del modelo (0, 0, 0) salvo el fuelle.
- Inferido: armado (fogón al fondo, yunque adelante, fuelle a la izquierda, barril adelante a la derecha,
  rueda contra el fogón, estante atrás a la derecha), ladrillos y juntas, alturas de campana y chimenea,
  formas y medidas del fuelle, yunque, barril, herramientas y rueda; los nombres de las piezas que el
  prompt no nombra; carbón apagado bajo las brasas.

Vueltas: 1) primera versión: z-fighting entre herraduras vecinas (0,64 de ancho cada 0,55), clavijas a
ras del travesaño, patas y postes con la base en y = 0 los dos, y la punta del cuero del fuelle en el
mismo plano que la punta de las tablas; las dos ramas de cada tenaza compartían el cuadrado de arriba
(bordes de tres caras) · 2) herraduras de 0,52 cada 0,6, clavijas 0,04 más abajo, postes desde 0,02,
cuero 0,17 atrás de la punta, ramas de la tenaza en planos distintos (0,09) y contorno del fuelle de 5
puntos por lado (296 -> 216).

Revisión
- 2556 triángulos contra 1500 (+70 %): el fogón con chimenea, campana y ladrillos lleva 916 (las llagas y
  hiladas del frente y los costados son ~500; sin ellas sería una caja roja), el estante con 4
  herraduras, 2 tenazas y 2 martillos 480, la rueda de 12 rayos con llanta 372, el barril 246, el fuelle
  216, el yunque 206 y las brasas 120. Es un set que se recorre de cerca (recuperar el transporte).
- Medidas: fogón 4 x 3 x 3 (mesa 4,2 x 3,2), chimenea hasta 9,23; yunque con la cara a 2,52; barril de 2 x
  1,76; rueda de 3,2 de diámetro; estante de 2,9 x 3,4. Todo el set: 12,65 x 9,23 x 6,56.
- Materiales: 10 (redrock, sand, iron, gunmetal, wood_mid, wood_dark, leather_dark, lamp_glow, coal,
  water): lo pide el set (ladrillo, hierro, cuero, brasas, agua). Por pieza, 5 como mucho.
- Coals_Glow toca el carbón apagado de la fosa (objeto Hearth): al esconderlo queda el fuego apagado.
- La espalda del fogón y de la chimenea va lisa (sin juntas): el set va contra una pared.
"""

import math

from mathutils import Euler, Vector

BRICK, MORTAR, IRON, GUN, MID, DARK = "redrock", "sand", "iron", "gunmetal", "wood_mid", "wood_dark"
LEATHER, GLOW, COAL, WATER = "leather_dark", "lamp_glow", "coal", "water"

HX, HZ, HY = 2.0, 1.5, 2.8              # fogón: medio ancho, medio fondo, alto del ladrillo
TOP = 3.0
CH = (-0.8, 0.8, 0.6, 1.5, 9.0)          # chimenea: x0, x1, z0, z1, alto


def ring(c, r, n=8, phase=0.5, axis="y"):
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + phase) / n
        u, v = r * math.cos(a), r * math.sin(a)
        out.append({"y": (c[0] + u, c[1], c[2] + v), "x": (c[0], c[1] + v, c[2] + u),
                    "z": (c[0] + u, c[1] + v, c[2])}[axis])
    return out


# --------------------------------------------------------------------------------------------------- fogón
def hearth(mk):
    p = mk.part("Hearth", (0, 0, 0))
    mk.box(p, (0, HY / 2, 0), (2 * HX, HY, 2 * HZ), BRICK)                                   # cuerpo
    mk.box(p, (0, HY + 0.1 - 0.005, 0), (2 * HX + 0.2, 0.21, 2 * HZ + 0.2), IRON)             # mesa
    x0, x1, z0, z1, top = CH
    mk.box(p, ((x0 + x1) / 2, (HY + top) / 2, (z0 + z1) / 2), (x1 - x0, top - HY, z1 - z0), BRICK)   # chimenea
    mk.box(p, ((x0 + x1) / 2, top + 0.11, (z0 + z1) / 2), (x1 - x0 + 0.3, 0.24, z1 - z0 + 0.3), BRICK)  # remate
    # campana: tronco de pirámide agarrado a la chimenea, hueco por abajo
    hood_lo, hood_hi = 4.7, 6.3
    lo = [(x, hood_lo, z) for x in (-1.75, 1.75) for z in (-1.35, 1.05)]
    hi = [(x, hood_hi, z) for x in (-0.72, 0.72) for z in (0.3, 1.05)]
    mk.hull(p, lo + hi, IRON)
    mk.carve(p, COAL, points=[(x, hood_lo - 0.3, z) for x in (-1.65, 1.65) for z in (-1.25, 0.62)]
             + [(x, hood_hi - 0.12, z) for x in (-0.6, 0.6) for z in (0.4, 0.62)])
    # fosa del fuego y cenicero
    mk.carve(p, COAL, points=mk.pts_box((0, TOP - 0.25, -0.35), (2.0, 0.7, 1.6)))
    mk.carve(p, COAL, points=mk.pts_box((0, 0.45, -HZ), (1.4, 0.9, 1.4)))
    # juntas de ladrillo: hiladas en frente y costados, llagas trabadas en el frente
    for k in range(1, 7):
        y = 0.4 * k
        for d in (-0.035, 0.035):
            mk.slice(p, (0, y + d, 0), (0, 1, 0))
        mk.paint(p, MORTAR, box=((0, y, -HZ), (2 * HX + 0.1, 0.072, 0.02)))
        for s in (-1, 1):
            mk.paint(p, MORTAR, box=((s * HX, y, 0), (0.02, 0.072, 2 * HZ + 0.1)))
    xs_even, xs_odd = (-1.2, 0.0, 1.2), (-1.8, -0.6, 0.6, 1.8)
    for x in sorted(set(xs_even + xs_odd)):
        for d in (-0.035, 0.035):
            mk.slice(p, (x + d, 0, 0), (1, 0, 0))
    for k in range(7):
        for x in (xs_even if k % 2 == 0 else xs_odd):
            mk.paint(p, MORTAR, box=((x, 0.4 * k + 0.2, -HZ), (0.072, 0.32, 0.02)))
    # hiladas de la chimenea (frente y costados)
    for k in range(1, 16):
        y = HY + 0.4 * k
        if y > top - 0.1:
            break
        for d in (-0.035, 0.035):
            mk.slice(p, (0, y + d, 0), (0, 1, 0))
        mk.paint(p, MORTAR, box=(((x0 + x1) / 2, y, z0), (x1 - x0 + 0.1, 0.072, 0.02)))
        for xx in (x0, x1):
            mk.paint(p, MORTAR, box=((xx, y, (z0 + z1) / 2), (0.02, 0.072, z1 - z0 + 0.1)))
    # carbón apagado en la fosa
    for i, (cx, cz, r) in enumerate(((-0.55, -0.5, 0.28), (0.1, -0.2, 0.32), (0.6, -0.6, 0.26), (-0.2, -0.85, 0.24),
                                     (0.45, 0.1, 0.22), (-0.6, 0.05, 0.25))):
        mk.ball(p, (cx, TOP - 0.55 + r * 0.5, cz), r, COAL, scale=(1.0, 0.7, 1.0), rot=(0, 30 * i, 0), subdiv=1,
                detail=True)
    # tobera en el costado izquierdo
    mk.cyl(p, (-HX - 0.15, 2.04, -0.2), 0.14, 0.4, IRON, axis="x", sides=8, detail=True)
    # caballetes del fuelle
    for x in (-3.3, -4.75):
        mk.box(p, (x, 0.81, -0.2), (0.24, 1.58, 1.2), DARK, detail=True)
        mk.box(p, (x, 0.12, -0.2), (0.5, 0.24, 1.5), DARK, detail=True)
    return p


def coals_glow(mk):
    p = mk.part("Coals_Glow", (0, 0, 0))
    for i, (cx, cz, r) in enumerate(((-0.25, -0.45, 0.2), (0.3, -0.35, 0.22), (0.0, -0.7, 0.18), (-0.45, -0.15, 0.17),
                                     (0.25, -0.05, 0.16), (0.65, -0.3, 0.15))):
        mk.ball(p, (cx, TOP - 0.58 + r * 0.6, cz), r, GLOW, scale=(1.0, 0.75, 1.0), rot=(0, 25 * i, 0), subdiv=1)
    return p


# --------------------------------------------------------------------------------------------------- fuelle
HINGE = (-2.75, 2.04, -0.2)


def pear(y, grow=0.0):
    """Contorno de las tablas del fuelle en planta (x, z), de la punta angosta hacia atrás."""
    zc = HINGE[2]
    pts = [(-2.75 if grow == 0 else -2.92, 0.22), (-3.6, 0.6), (-4.6, 0.85), (-5.25, 0.6), (-5.45, 0.0)]
    out = [(x, y, zc + w + grow) for x, w in pts] + [(x, y, zc - w - grow) for x, w in pts]
    return [(x - (grow if x < -5.3 else 0.0), yy, z) for x, yy, z in out]


def bellows(mk):
    p = mk.part("Bellows", HINGE)
    mk.hull(p, pear(1.58) + pear(1.7), MID)                                                    # tabla de abajo
    mk.hull(p, pear(2.38) + pear(2.5), MID)                                                    # tabla de arriba
    mk.hull(p, pear(1.68, -0.06) + pear(1.86, 0.1) + pear(2.04, -0.04), LEATHER)               # cuero, dos fuelles
    mk.hull(p, pear(2.02, -0.04) + pear(2.2, 0.1) + pear(2.4, -0.06), LEATHER)
    mk.hull(p, ring((-2.85, 2.04, HINGE[2]), 0.2, axis="x") + ring((-2.05, 2.04, HINGE[2]), 0.1, axis="x"), IRON)
    mk.hull(p, [(x, y, HINGE[2] + dz) for (x, y) in ((-5.3, 2.42), (-5.3, 2.56), (-6.2, 2.78), (-6.2, 2.92))
                for dz in (-0.08, 0.08)], DARK)                                                # manija
    return p


# --------------------------------------------------------------------------------------------------- yunque
def anvil(mk):
    p = mk.part("Anvil", (0, 0, 0))
    ax, az = 0.6, -3.6
    mk.hull(p, ring((ax, 0.0, az), 0.72, 9) + ring((ax, 1.55, az), 0.64, 9, phase=0.3), DARK)    # tronco
    mk.paint(p, MID, box=((ax, 1.55, az), (1.5, 0.02, 1.5)))                                         # corte
    y0 = 1.54
    mk.box(p, (ax, y0 + 0.16, az), (1.05, 0.32, 0.8), IRON, top=(0.75, 0.7))                        # pie
    mk.box(p, (ax, y0 + 0.47, az), (0.62, 0.32, 0.44), IRON)                                         # cintura
    mk.box(p, (ax + 0.05, y0 + 0.8, az), (1.4, 0.36, 0.6), IRON, top=(1.0, 1.0))                     # cuerpo
    mk.hull(p, ring((ax - 0.62, y0 + 0.82, az), 0.2, 8, axis="x") + [(ax - 1.45, y0 + 0.9, az)], IRON)  # cuerno
    mk.box(p, (ax + 0.85, y0 + 0.84, az), (0.4, 0.24, 0.42), IRON)                                   # talón
    mk.paint(p, GUN, box=((ax + 0.2, y0 + 0.98, az), (2.0, 0.02, 0.7)))                             # cara
    mk.carve(p, IRON, points=mk.pts_box((ax + 0.85, y0 + 0.98, az), (0.14, 0.2, 0.14)))             # agujero
    mk.box(p, (ax - 0.1, y0 + 1.025, az + 0.05), (1.1, 0.1, 0.1), DARK, rot=(0, 25, 0), detail=True)  # martillo
    mk.box(p, (ax + 0.38, y0 + 1.065, az - 0.18), (0.2, 0.18, 0.46), IRON, rot=(0, 25, 0), detail=True)
    return p


# ---------------------------------------------------------------------------------------------- barril
def quench_barrel(mk):
    p = mk.part("QuenchBarrel", (0, 0, 0))
    bx, bz, h = 2.9, -2.6, 2.0
    rings = [(0.0, 0.74), (0.5, 0.84), (1.0, 0.88), (1.5, 0.84), (h, 0.74)]
    mk.hull(p, [q for y, r in rings for q in ring((bx, y, bz), r, 10, phase=0.0)], MID)
    mk.carve(p, MID, points=mk.pts_cyl((bx, h - 0.1, bz), 0.64, 0.4, sides=10))
    mk.cyl(p, (bx, h - 0.24, bz), 0.66, 0.06, WATER, sides=10, detail=True)
    for y, r in ((0.3, 0.83), (h - 0.45, 0.86)):                                             # zunchos
        mk.hull(p, ring((bx, y - 0.07, bz), r, 10, phase=0.0) + ring((bx, y + 0.07, bz), r + 0.005, 10, phase=0.0),
                IRON, detail=True)
    return p


# ------------------------------------------------------------------------------------------- estante
def horseshoe(mk, part, cx, cy, z):
    """Herradura colgada con la abertura para abajo (perfil en U, prisma)."""
    ro, ri, n = 0.26, 0.15, 5
    outer = [(cx + ro * math.cos(math.radians(a)), cy + ro * math.sin(math.radians(a))) for a in
             [-20 + 220 * i / n for i in range(n + 1)]]
    inner = [(cx + ri * math.cos(math.radians(a)), cy + ri * math.sin(math.radians(a))) for a in
             [200 - 220 * i / n for i in range(n + 1)]]
    prof = [(cx + 0.245, cy - 0.27)] + outer + [(cx - 0.245, cy - 0.27), (cx - 0.14, cy - 0.27)] + inner + [(cx + 0.14, cy - 0.27)]
    mk.prism(part, prof, 0.12, IRON, plane="xy", center=(0, 0, z), detail=True)


def tool_rack(mk):
    p = mk.part("ToolRack", (0, 0, 0))
    z = 1.7
    for x in (3.7, 6.3):
        mk.box(p, (x, 1.71, z), (0.26, 3.38, 0.26), DARK)                                       # postes
        mk.box(p, (x, 0.12, z), (0.3, 0.24, 1.1), DARK)                                         # patas
    for y in (3.05, 1.95):
        mk.box(p, (5.0, y, z - 0.02), (2.9, 0.24, 0.16), MID)                                   # travesaños
    for i, x in enumerate((4.15, 4.75, 5.35, 5.95)):                                             # herraduras
        mk.box(p, (x, 3.08, z - 0.2), (0.1, 0.1, 0.3), DARK, detail=True)                        # clavija
        horseshoe(mk, p, x, 2.88 - 0.02 * (i % 2), z - 0.18)
    for x, s in ((4.1, 1), (4.7, -1)):                                                           # tenazas
        for k in (-1, 1):
            zk = z - 0.13 + k * 0.045                                    # las dos ramas en planos distintos
            mk.hull(p, [(x + dx - k * 0.012, 2.0 + k * 0.01, zk + dz) for dx in (-0.05, 0.05) for dz in (-0.04, 0.04)]
                    + [(x + k * 0.16 + dx, 0.7, zk + dz) for dx in (-0.05, 0.05) for dz in (-0.04, 0.04)],
                    IRON, detail=True)
        mk.box(p, (x, 2.0, z - 0.17), (0.18, 0.18, 0.12), IRON, detail=True)
    for x in (5.4, 6.0):                                                                         # martillos
        mk.box(p, (x, 1.45, z - 0.14), (0.1, 1.05, 0.1), DARK, detail=True)
        mk.box(p, (x, 0.9, z - 0.14), (0.46, 0.2, 0.2), IRON, detail=True)
    return p


# ------------------------------------------------------------------------------------------------ rueda
def wagon_wheel(mk):
    p = mk.part("WagonWheel", (0, 0, 0))
    tilt = 12.0
    R = 1.6
    c = Vector((HX + R * math.sin(math.radians(tilt)) + 0.11 - 0.02, R * math.cos(math.radians(tilt)) + 0.11 * math.sin(math.radians(tilt)), 0.3))
    for k, a0 in enumerate((0.0, 180.0)):
        for r_in, r_out, w, mat, over in ((R - 0.32, R - 0.08, 0.22 - 0.004 * k, MID, 1.0),
                                          (R - 0.11, R, 0.17 - 0.004 * k, IRON, 1.6)):
            angs = [a0 - over + (180 + 2 * over) * i / 8 for i in range(9)]
            outer = [(r_out * math.cos(math.radians(a)), r_out * math.sin(math.radians(a))) for a in angs]
            inner = [(r_in * math.cos(math.radians(a)), r_in * math.sin(math.radians(a))) for a in reversed(angs)]
            mk.prism(p, outer + inner, w, mat, plane="zy", center=tuple(c), rot=(0, 0, tilt))
    e = Euler((0, 0, math.radians(tilt)), "XYZ").to_matrix()
    for i in range(6):                                                                           # 6 barras = 12 rayos
        a = math.radians(15 + 30 * i)
        d = Vector((0, math.sin(a), math.cos(a)))
        t = Vector((0, math.cos(a), -math.sin(a)))
        pts = [c + e @ (d * s * (R - 0.25) + t * tw + Vector((sx * 0.06, 0, 0))) for s in (-1, 1) for tw in (-0.05, 0.05)
               for sx in (-1, 1)]
        mk.hull(p, [tuple(q) for q in pts], MID)
    mk.hull(p, [tuple(c + e @ Vector(q)) for q in ring((0, 0, 0), 0.28, 8, axis="x")
                for q in [(q[0] - 0.3, q[1], q[2]), (q[0] + 0.3, q[1], q[2])]], DARK)                # cubo
    return p


def build(mk):
    hearth(mk)
    coals_glow(mk)
    bellows(mk)
    anvil(mk)
    quench_barrel(mk)
    tool_rack(mk)
    wagon_wheel(mk)

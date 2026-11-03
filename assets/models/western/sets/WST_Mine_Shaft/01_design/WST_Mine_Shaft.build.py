"""
Receta de WST_Mine_Shaft, el pozo vertical por donde trepan los caminantes (prompt 100, Bloques A + B).

Brief
- Lo que se lee: un agujero negro cuadrado en el piso con un brocal bajo de troncos cruzados, el torno
  roto encima (un poste partido, el rodillo caído en diagonal y la soga cortada colgando) y, al asomarse,
  la escalera de madera que baja pegada a una pared entre marcos de madera cada 4.
- Medidas: boca de 6 x 6 (x, z de -3 a 3); brocal de 0,8 en dos hiladas de troncos de 0,6 x 0,4 que se
  cruzan en las esquinas (las puntas salen 0,3); forro de tablones con la cara a ±3,15 hasta y = -30 y piso
  de tierra al fondo; marcos de madera cada 4 (y = -2 a -30) que salen 0,3 de los tablones (la luz del
  pozo es 5,7); entre marco y marco, dos puntas de viga por pared en las paredes ±X (agarraderas a
  y -4, -8, ...). Escalera contra la pared +Z, de y = +1,0 a -30, peldaños cada 1,2.
  Torno: dos caballetes sobre el brocal en x = ±3,4; el de la izquierda partido a 1,0 de altura; el rodillo
  (0,45 de radio) cae de y 2,6 a la derecha a 0,9 a la izquierda; manivela de hierro; soga de 3,5 colgando.
- Piezas (el prompt no lista sub-objetos; se separan para la colisión y para el motor): Body (brocal y
  forro), Ladder (escalera: se puede marcar como trepable), Windlass (torno roto).
- Inferido: los nombres y la partición, las dos hiladas del brocal, el piso al fondo, la pared de la
  escalera, la forma de la rotura del torno, las agarraderas entre marcos.

Vueltas: 1) el brocal de una hilada por lado dejaba los troncos de arriba en el aire: dos hiladas de cabaña
(dos enteros y dos entre ellos por hilada); paredes del forro con tapas y fondos coplanares · 2) las dos
patas del caballete derecho tenían las caras de los costados coplanares donde se cruzan (el ancho que
importaba era el otro eje de beam()): anchos 0,30 y 0,27.

Revisión
- 1308 triángulos contra 800: lo pedido ya cuesta ~1100 (32 vigas de marcos cada 4 en 30 de hondo: 384;
  25 peldaños cada 1,2: 300; forro, brocal y fondo: 156; torno roto: 240). Body 708, Ladder 360, Windlass
  240. No hay detalle escondido: las caras traseras de los marcos van contra la roca.
- Medidas: boca de 6 x 6 dentro del brocal (7,8 por afuera con las puntas), brocal de 0,81, 30 de hondo
  (el punto más bajo, -30,27, es el piso de tierra); luz del pozo entre marcos 5,7.
- Dudoso (Valentin): los túneles y la galería no tienen agujero en el piso; para poner el pozo hay que
  abrirlo en Studio (o pedir una variante con hueco). El forro es hueco: colisión con
  PreciseConvexDecomposition. Nombres Body/Ladder/Windlass inferidos (el prompt no lista objetos).
"""

import math

WOOD, PLANK, IRON, ROPE, DIRT = "wood_dark", "wood_mid", "iron", "rope", "ochre"
HOLE = 3.0                      # medio ancho de la boca
WALL = 3.15                     # cara de los tablones
DEPTH = 30.0


def beam(mk, part, a, b, w, h, mat, detail=False):
    ax, ay, az = a
    bx, by, bz = b
    d = (bx - ax, by - ay, bz - az)
    ln = math.sqrt(sum(c * c for c in d))
    u = tuple(c / ln for c in d)
    ref = (0, 1, 0) if abs(u[1]) < 0.9 else (1, 0, 0)
    v = (u[1] * ref[2] - u[2] * ref[1], u[2] * ref[0] - u[0] * ref[2], u[0] * ref[1] - u[1] * ref[0])
    vl = math.sqrt(sum(c * c for c in v))
    v = tuple(c / vl for c in v)
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    pts = [tuple(q[k] + v[k] * sv + n[k] * sn for k in range(3)) for q in (a, b) for sv in (-w / 2, w / 2)
           for sn in (-h / 2, h / 2)]
    mk.hull(part, pts, mat, detail=detail)


def body(mk):
    p = mk.part("Body", (0, 0, 0))
    # brocal: dos hiladas como una cabaña de troncos; en cada una, dos troncos enteros (las puntas salen
    # 0,3) y dos entre ellos, metidos 0,05 en los enteros y 0,004 más bajos (no coplanares)
    c = HOLE + 0.3
    for k, (y0, y1) in enumerate(((-0.02, 0.40), (0.39, 0.81))):
        yc, h = (y0 + y1) / 2, y1 - y0
        for s in (-1, 1):
            if k == 0:
                mk.box(p, (s * c, yc, 0), (0.6, h, 2 * c + 1.2), WOOD)
                mk.box(p, (0, yc - 0.004, s * c), (2 * HOLE + 0.1, h - 0.008, 0.6), WOOD)
            else:
                mk.box(p, (0, yc, s * c), (2 * c + 1.2, h, 0.6), WOOD)
                mk.box(p, (s * c, yc - 0.004, 0), (0.6, h - 0.008, 2 * HOLE + 0.1), WOOD)
    # forro: cuatro paredes de tablones (las de ±X entran en las de ±Z) y el piso de tierra al fondo
    t = 0.3
    for s in (-1, 1):
        mk.box(p, (s * (WALL + t / 2), -15.015, 0), (t, 29.93, 2 * WALL + 0.1), PLANK)
        mk.box(p, (0, -15.0, s * (WALL + t / 2)), (2 * WALL + 2 * t - 0.04, 30.0, t), PLANK)
    mk.box(p, (0, -30.12, 0), (2 * WALL + 0.1, 0.3, 2 * WALL + 0.1), DIRT)
    # marcos cada 4 (salen 0,3 de los tablones) y agarraderas en zigzag entre marcos (paredes ±X)
    cr = WALL - 0.3
    for k, y in enumerate([-2.0 - 4 * i for i in range(8)]):
        e = 0.015 * (k % 2)
        for s in (-1, 1):
            mk.box(p, (s * (cr + 0.35), y + e, 0), (0.7, 0.5, 2 * cr + 0.02), WOOD, detail=True)
            mk.box(p, (0, y - e + 0.008, s * (cr + 0.35)), (2 * cr + 1.38, 0.5, 0.7), WOOD, detail=True)
        if y > -29:
            for s in (-1, 1):
                z = (1.2 if k % 2 else -1.2) * s
                mk.box(p, (s * (WALL - 0.12), y - 2.0, z), (0.5, 0.36, 0.42), WOOD, detail=True)


def ladder(mk):
    p = mk.part("Ladder", (0, 0, 0))
    z = WALL - 0.3 - 0.2                     # delante de los marcos
    top, bot = 1.0, -DEPTH + 0.02
    for x in (-0.48, 0.48):
        mk.box(p, (x, (top + bot) / 2, z), (0.14, top - bot, 0.14), PLANK)
    y = 0.0
    k = 0
    while y > bot + 0.4:
        mk.box(p, (0, y + 0.004 * (k % 2), z), (1.06, 0.09, 0.09), PLANK)
        y -= 1.2
        k += 1
    # dos grampas de hierro que la tienen contra el marco (arriba y a mitad)
    for yg in (-2.0, -14.0, -26.0):
        mk.box(p, (0, yg, z + 0.16), (1.2, 0.08, 0.2), IRON)


def windlass(mk):
    p = mk.part("Windlass", (0, 0, 0))
    xs = HOLE + 0.4
    # caballete derecho entero (dos patas en V sobre el brocal y un cojinete)
    for dz, w in ((-0.7, 0.3), (0.7, 0.27)):                    # anchos distintos: donde se cruzan no son coplanares
        beam(mk, p, (xs, 0.78, dz), (xs, 2.75, 0.0), w, w, WOOD)
    mk.box(p, (xs, 2.75, 0), (0.4, 0.3, 0.5), WOOD)
    # caballete izquierdo partido: dos muñones y la punta caída sobre el brocal
    for dz in (-0.7, 0.7):
        beam(mk, p, (-xs, 0.78, dz), (-xs, 1.5 + 0.25 * dz, dz * 0.6), 0.3, 0.3, WOOD)
    beam(mk, p, (-xs - 0.2, 0.95, 1.3), (-xs + 0.9, 0.95, 2.9), 0.3, 0.3, WOOD)
    # rodillo caído en diagonal (derecha arriba, izquierda sobre el brocal) y manivela
    a, b = (xs + 0.3, 2.95, 0.0), (-xs + 0.3, 1.05, -0.2)
    d = [b[k] - a[k] for k in range(3)]
    ln = math.sqrt(sum(v * v for v in d))
    ang = math.degrees(math.atan2(d[1], -d[0]))
    mid = [(a[k] + b[k]) / 2 for k in range(3)]
    mk.cyl(p, tuple(mid), 0.45, ln, PLANK, axis="x", sides=8, rot=(0, 0, -ang))
    for k in (0.12, 0.88):
        q = [a[i] + d[i] * k for i in range(3)]
        mk.cyl(p, tuple(q), 0.5, 0.12, IRON, axis="x", sides=8, rot=(0, 0, -ang))
    mk.box(p, (xs + 0.42, 2.95, 0), (0.3, 0.12, 0.12), IRON)
    mk.box(p, (xs + 0.6, 2.62, 0), (0.1, 0.7, 0.1), IRON)
    mk.box(p, (xs + 0.6, 2.3, -0.25), (0.1, 0.1, 0.5), IRON)
    # soga enroscada y el tramo cortado que cuelga adentro del pozo
    q = [a[i] + d[i] * 0.4 for i in range(3)]
    mk.cyl(p, tuple(q), 0.5, 1.6, ROPE, axis="x", sides=8, rot=(0, 0, -ang))
    top = (q[0], q[1] - 0.45, q[2])
    mk.hull(p, [(top[0] + dx, top[1], top[2] + dz) for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)]
            + [(top[0] + 0.25 + dx, -3.4, 0.3 + dz) for dx in (-0.05, 0.05) for dz in (-0.05, 0.05)], ROPE)
    mk.hull(p, [(top[0] + 0.25 + dx, -3.38, 0.3 + dz) for dx in (-0.05, 0.05) for dz in (-0.05, 0.05)]
            + [(top[0] + 0.33, -3.75, 0.22), (top[0] + 0.15, -3.7, 0.42)], ROPE)              # punta deshilachada


def build(mk):
    body(mk)
    ladder(mk)
    windlass(mk)

"""
Receta de WST_DG_WaterTower, el tanque de agua del ferrocarril (prompt 079, Bloques A + B).

Brief
- Silueta a 40 studs: un barril de duelas panzón sobre cuatro patas abiertas con cruces en X, coronado por
  un cono de tejuelas; el caño basculante levantado contra el costado del lado de las vías, con la soga
  para bajarlo colgando. Es el hito vertical de la estación (21 de alto).
- Medidas: caballete de 10 (patas de 0,85 de sección, abiertas de 2,9 arriba a 3,7 abajo desde el centro),
  vigas de cabeza y 5 durmientes; tanque de 8 de diámetro (radio 4 en la panza, 3,82 en las puntas) y 7 de
  alto, de y = 10,8 a 17,8; techo cónico con alero de 0,6 y punta a ~20,6. Origen en el centro de la base.
- Piezas: Body (tanque, techo, caballete, escalera, bisagra del caño) y Spout (caño, collar, boca y soga;
  origen en el eje de la bisagra, gira sobre X). El vacío raíz ya se llama como el id, por eso "Body".
- Duelas: 16 cascos separados por una ranura de 0,07 que deja ver un núcleo wood_dark (ranuras reales,
  como pide el prompt); cada duela con dos facetas en altura (la panza del barril). Zunchos de hierro a
  14, 50 y 86 % del alto, con las caras paralelas a las duelas (sin cortarlas).
- Colores: duelas wood_mid, núcleo y techo wood_dark, caballete y escalera wood_light (madera curtida por
  el sol, se separa del tanque), hierro en zunchos, bisagra y caño, soga rope.
- Desgaste: una duela astillada arriba, una cruz rota en el lado -X (queda el muñón).
- Inferido: lado de las vías = +Z (como WST_DG_Station), caño guardado a 72° con la soga colgando,
  escalera en la pata del frente a la izquierda (-X, -Z), separada 0,25 de la pata con tres tacos,
  alturas de las cruces y la solera, 5 durmientes que asoman bajo el tanque.

Vueltas: 1) se lee a 96 px; patas de 0,7 flacas para 10 de alto y alero corto · 2) patas de 0,85, alero de
0,6 y techo más alto.

Revisión
- 1470 triángulos contra 1200 (+22 %): las 16 duelas con ranura real son ~320 (el prompt pide las ranuras)
  y la escalera con 11 peldaños ~150. Body 1298, Spout 172.
- Medidas: 9,0 x 21,1 x 11,0 (tanque de 8 de diámetro y 7 de alto sobre un caballete de 10; el ancho
  pasa de 8 por el alero y las patas abiertas; el fondo, por el caño y la soga).
- Colisión: con casco convexo, Body tapa el espacio entre las patas (no se puede pasar por abajo). Si los
  jugadores tienen que cruzar por debajo, en Studio va PreciseConvexDecomposition.
- Spout gira sobre X en su bisagra (origen en el eje); la soga se mueve con él.
"""

import math

from mathutils import Vector

N = 16                                    # duelas (y lados de núcleo y zunchos)
STEP = 2 * math.pi / N
Y0, H = 10.8, 7.0                         # tanque
R_MID, R_END = 4.0, 3.82
R_CORE = 3.72
LEG_B, LEG_T, LEG_YT = 3.7, 2.9, 10.0     # centro de las patas abajo / arriba (a y = 10), sección 0,7
LH = 0.425
WOOD, DARK, TRESTLE = "wood_mid", "wood_dark", "wood_light"
PIVOT = (0.0, 11.35, 4.5)
SPOUT_DEG = 72.0


def xc(y):
    """Centro de las patas (distancia al eje) a la altura y."""
    return LEG_B + (LEG_T - LEG_B) * y / LEG_YT


def r_at(y):
    """Radio de las duelas (esquinas) a la altura y: la panza del barril."""
    m = Y0 + H / 2
    return R_END + (R_MID - R_END) * (1 - abs(y - m) / (H / 2))


def ring(c, r, axis_dir, n, phase=0.5):
    """Puntos de un anillo de radio r alrededor de c, perpendicular a axis_dir."""
    a = Vector(axis_dir).normalized()
    u = a.cross(Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = a.cross(u)
    c = Vector(c)
    return [tuple(c + r * (math.cos(2 * math.pi * (i + phase) / n) * u + math.sin(2 * math.pi * (i + phase) / n) * v))
            for i in range(n)]


def sp(n, l, y, d):
    """Punto en la cara de afuera de un lado del caballete: n = normal (x o z), l lateral, d hacia afuera."""
    nx, nz = n
    off = xc(y) + LH + d
    if nx != 0:
        return (nx * off, y, l)
    return (l, y, nz * off)


def board(mk, part, n, a, b, w, d0, d1, mat):
    """Tabla en la cara de un lado, de a=(l, y) a b=(l, y), de w de alto medido en vertical."""
    pts = []
    for l, y in (a, b):
        for dy in (-w / 2, w / 2):
            for d in (d0, d1):
                pts.append(sp(n, l, y + dy, d))
    mk.hull(part, pts, mat)


def build(mk):
    body = mk.part("Body", (0, 0, 0))

    # ---------------- tanque ----------------
    mk.cyl(body, (0, Y0 + 0.01 + (H - 0.04) / 2, 0), R_CORE, H - 0.04, DARK, sides=N)
    ys = (Y0, Y0 + H / 2, Y0 + H)
    for k in range(N):
        g = 0.035 / R_MID
        a0, a1 = (k - 0.5) * STEP + g, (k + 0.5) * STEP - g
        top = Y0 + H - (0.45 if k == 5 else 0.0)                   # duela astillada arriba
        pts = []
        for y in (Y0, Y0 + H / 2, top):
            r = r_at(y)
            for a in (a0, a1):
                for rr in (r, r - 0.3):
                    pts.append((rr * math.cos(a), y, rr * math.sin(a)))
        if k == 5:                                                  # punta en diagonal de la astilla
            r = r_at(Y0 + H)
            for rr in (r, r - 0.3):
                pts.append((rr * math.cos(a1), Y0 + H, rr * math.sin(a1)))
        mk.hull(body, pts, WOOD)
    for f in (0.14, 0.5, 0.86):                                     # zunchos
        y = Y0 + f * H
        mk.cyl(body, (0, y, 0), r_at(y) + 0.08, 0.3, "iron", sides=N)

    # ---------------- techo cónico en dos hiladas ----------------
    yb = Y0 + H - 0.08
    low = ring((0, yb - 0.12, 0), R_MID + 0.6, (0, 1, 0), N) + ring((0, yb + 1.25, 0), 2.6, (0, 1, 0), N)
    mk.hull(body, low, DARK)
    up = ring((0, yb + 1.15, 0), 2.8, (0, 1, 0), N) + [(0, yb + 2.85, 0)]
    mk.hull(body, up, DARK)
    mk.cyl(body, (0, yb + 2.95, 0), 0.12, 0.5, "iron", sides=6)    # remate
    mk.ball(body, (0, yb + 3.25, 0), 0.16, "iron", subdiv=0)

    # ---------------- caballete ----------------
    for sx in (-1, 1):
        for sz in (-1, 1):
            pts = []
            for y in (0.0, LEG_YT - 0.05):
                c = xc(y)
                pts += [(sx * c + dx, y, sz * c + dz) for dx in (-LH, LH) for dz in (-LH, LH)]
            mk.hull(body, pts, TRESTLE)
    for sz in (-1, 1):                                              # vigas de cabeza
        mk.box(body, (0, 10.15, sz * LEG_T), (2 * LEG_B, 0.5, 0.8), DARK)
    for x in (-3.2, -1.6, 0.0, 1.6, 3.2):                           # durmientes bajo el tanque
        mk.box(body, (x, 10.6, 0), (0.45, 0.44, 8.4), DARK)
    sides = ((0, -1), (0, 1), (-1, 0), (1, 0))
    for n in sides:
        for yg in (0.7, 5.0):                                       # soleras
            board(mk, body, n, (-xc(yg), yg), (xc(yg), yg), 0.36, -0.04, 0.22, TRESTLE)
        for (y_a, y_b) in ((0.95, 4.8), (5.2, 9.6)):
            ya, yb_ = y_a, y_b
            broken = n == (-1, 0) and y_a > 5
            board(mk, body, n, (-xc(ya), ya), (xc(yb_), yb_), 0.34, -0.05, 0.18, TRESTLE)
            if broken:                                              # cruz rota: queda el muñón
                lb = (xc(ya) + 0.0, ya)
                mid = (xc(ya) - 0.3 * 2 * xc(ya), ya + 0.3 * (yb_ - ya))
                board(mk, body, n, lb, mid, 0.34, -0.06, 0.2, TRESTLE)
            else:
                board(mk, body, n, (xc(ya), ya), (-xc(yb_), yb_), 0.34, -0.06, 0.2, TRESTLE)

    # ---------------- escalera en la pata del frente a la izquierda ----------------
    n = (0, -1)
    for dl in (-0.45, 0.45):
        pts = []
        for y in (0.0, 11.2):
            l = -xc(y) + dl
            pts += [sp(n, l + e, y, d) for e in (-0.07, 0.07) for d in (0.2, 0.33)]
        mk.hull(body, pts, TRESTLE)
    for k in range(11):                                             # peldaños
        y = 0.7 + 0.95 * k
        pts = [sp(n, -xc(y) + dl, y + e, d) for dl in (-0.45, 0.45) for e in (-0.06, 0.06) for d in (0.215, 0.315)]
        mk.hull(body, pts, TRESTLE)
    for y in (2.4, 7.3):                                            # tacos que la separan de la pata
        pts = [sp(n, -xc(y) + dl, y + e, d) for dl in (-0.5, 0.5) for e in (-0.12, 0.12) for d in (-0.05, 0.25)]
        mk.hull(body, pts, DARK)

    # ---------------- bisagra del caño (fija) ----------------
    px, py, pz = PIVOT
    for sx in (-1, 1):
        mk.box(body, (sx * 0.42, py, pz - 0.42), (0.12, 0.6, 1.0), "iron")
    mk.cyl(body, PIVOT, 0.1, 1.0, "iron", axis="x", sides=6)
    mk.cyl(body, (0, py - 0.05, pz - 0.75), 0.32, 0.5, "iron", axis="z", sides=8)   # boca de salida del tanque

    # ---------------- caño basculante (gira sobre X en la bisagra) ----------------
    sp_ = mk.part("Spout", PIVOT)
    a = math.radians(SPOUT_DEG)
    d = Vector((0, math.sin(a), math.cos(a)))
    P = Vector(PIVOT)
    mk.cyl(sp_, PIVOT, 0.22, 0.66, "iron", axis="x", sides=8)                       # collar
    mk.hull(sp_, ring(P + d * 0.05, 0.36, d, 8) + ring(P + d * 4.5, 0.36, d, 8), "iron")
    mk.hull(sp_, ring(P + d * 4.4, 0.4, d, 8) + ring(P + d * 5.0, 0.56, d, 8), "iron")  # boca abocinada
    for t in (1.6, 3.2):                                                            # abrazaderas
        mk.hull(sp_, ring(P + d * (t - 0.08), 0.42, d, 8) + ring(P + d * (t + 0.08), 0.42, d, 8), "iron")
    # soga para bajarlo, colgando de la boca
    tip = P + d * 4.85 + Vector((0, -0.45, 0.25))
    pts = [tuple(tip + Vector((ex, 0.15, ez))) for ex in (-0.05, 0.05) for ez in (-0.05, 0.05)]
    pts += [tuple(Vector((tip.x, 3.2, tip.z)) + Vector((ex, 0, ez))) for ex in (-0.05, 0.05) for ez in (-0.05, 0.05)]
    mk.hull(sp_, pts, "rope")
    mk.ball(sp_, (tip.x, 3.15, tip.z), 0.13, "rope", subdiv=0)                     # nudo

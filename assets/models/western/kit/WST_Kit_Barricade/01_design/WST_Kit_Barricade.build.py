"""
Receta de WST_Kit_Barricade, las barricadas improvisadas del kit modular (prompt 015, Bloques A + C).

Brief
- Silueta a 40 studs: tablas claras clavadas en cruz sobre la ventana; tablas atravesadas sobre la puerta;
  en la calle, una mesa volcada con cajones, una rueda de carreta apoyada y bolsas: cobertura agachado.
- Barricade_Window (x = 0, 3 fragmentos, uno por tabla): origen abajo al centro del hueco de la ventana
  (igual que WST_Kit_Window: z = 0 plano medio de la pared). Dos tablas atrás que no se cruzan (una
  diagonal y una horizontal arriba) apoyadas en el tapajuntas (z = -0,40) y una diagonal adelante que se
  cruza con la primera: va combada (dos tramos) para montarse sobre ella y tocar el tapajuntas en las puntas.
- Barricade_Door (x = 8, 5 fragmentos): origen abajo al centro del hueco de la puerta. Cinco tablas de
  largos y ángulos distintos, de jamba a jamba sobre el tapajuntas del marco (|x| de 2,2 a 2,4).
- Barricade_Street (x = 20, 6 fragmentos): 8 x 3, origen abajo al centro. frag01 mesa volcada (tablero de
  3,6 x 2,2 de pie mirando a -Z, patas hacia atrás); frag02 y frag03 cajones (1,6 en el piso y 1,3 encima,
  girado); frag04 rueda de carreta apoyada en la mesa (llanta de hierro, 6 rayos); frag05 y frag06 bolsas
  de lona.
- Tablas wood_light (recién clavadas) con alguna wood_mid, clavos doblados como cuñitas de hierro.
- Nombres: <Pieza>_fragNN.
- Inferido: espesor de tablas 0,18 (menos que el 0,4 del Bloque C: tablas de 0,4 parecen vigas), capas
  de la ventana, alturas y ángulos de las tablas, composición de la barricada de calle (qué va dónde),
  diámetro de la rueda (2,6), bolsas.

Vueltas: 1) primera versión: el hueco de la rueda se comía los rayos y la maza (eran base) -> van como
detalle · 2) cajones con esquineros unidos a 252 triángulos cada uno -> chanflán con material oscuro (108);
la tabla combada sin unión (la booleana dejaba 9 esquinas con normales desviadas) · 3) las bolsas se leían
como piedras facetadas -> bolsa acostada que se angosta hacia la boca atada con soga y punta de lona.

Revisión
- Triángulos contra 300 por pieza: Window 84, Door 150, Street 954 (mesa 108, cajones 108 + 108, rueda
  292 con llanta de hierro, 6 rayos y maza, bolsas 238 + 100). Calidad primero: la de calle es una
  cobertura que se mira de cerca; la rueda es el rasgo que la hace leer como barricada de pueblo.
- Medidas: Window 4,5 x 3,7 (cubre el hueco de 3 x 4 de lado a lado del tapajuntas); Door 5 x 6,5 (de 0,65 a
  7,14); Street 7,9 x 2,9 x 3,6 (las patas de la mesa salen 2,4 hacia atrás).
- Fragmentos: Window 35/30/36 %, Door 5 x 20 %, Street el mayor 40 % (el cajón de abajo). Las tablas de 0,18
  quedan por debajo del 0,4 del Bloque C (a propósito: tablas de 0,4 parecen vigas).
- Normales del GLB final: 2 esquinas apenas desviadas (11°) en las bolsas (bug de process_model, ver
  el informe); no se ve.
"""

import math

LIGHT, MID, DARK, CANVAS, IRON, ROPE = "wood_light", "wood_mid", "wood_dark", "canvas", "iron", "rope"
PT = 0.18                                  # espesor de tabla


def rotate(p, rot):
    """Euler XYZ en grados (como modelkit): primero X, después Y, después Z."""
    x, y, z = p
    ax, ay, az = (math.radians(a) for a in rot)
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return (x, y, z)


def plank_pts(a, b, w, zb_a, zb_b, rough=(0.0, 0.0)):
    """Tabla de a a b (x, y) de ancho w; zb: z de la cara de atrás en cada punta; rough: corte en ángulo."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy, ux
    pts = []
    for (cx, cy), zb, r, s in ((a, zb_a, rough[0], 1), (b, zb_b, rough[1], -1)):
        for k in (-1, 1):
            ox = cx + px * k * w / 2 + ux * s * r * k
            oy = cy + py * k * w / 2 + uy * s * r * k
            pts += [(ox, oy, zb), (ox, oy, zb - PT)]
    return pts


def nails(mk, part, pts, zf):
    """Clavos doblados: cuñitas de hierro sobre la cara de adelante (zf)."""
    for x, y, bend in pts:
        mk.hull(part, [(x + dx, y + dy, zf + 0.01) for dx in (-0.04, 0.04) for dy in (-0.04, 0.04)]
                + [(x + bend * 0.12, y + 0.03, zf - 0.07)], IRON, detail=True)


def union(mk, part):
    mk.carve(part, LIGHT, points=mk.pts_box((0, -30, 0), (0.1, 0.1, 0.1)))      # sin efecto: une los cascos


# ---------------------------------------------------------------------------------------- ventana
def window(mk, ox):
    z0 = -0.40                                                                  # frente del tapajuntas
    planks = [  # (a, b, ancho, z atrás en a, en b, material, combada)
        ((-2.0, 0.45), (1.95, 2.85), 0.55, z0, z0, LIGHT, False),
        ((-2.2, 3.55), (2.15, 3.62), 0.5, z0, z0, MID, False),
        ((2.0, 0.42), (-1.95, 2.95), 0.55, z0, z0, LIGHT, True),
    ]
    for i, (a, b, w, za, zb, mat, bow) in enumerate(planks):
        p = mk.part(f"Barricade_Window_frag0{i + 1}", (ox, 0, 0))
        A, B = (ox + a[0], a[1]), (ox + b[0], b[1])
        if bow:                                                                 # monta sobre la diagonal de atrás
            M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
            ext = lambda P, Q, t: (P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t)
            mk.hull(p, plank_pts(A, ext(A, M, 1.02), w, za, z0 - PT, (0.12, 0.0)), mat)
            mk.hull(p, plank_pts(ext(B, M, 1.02), B, w, z0 - PT, zb, (0.0, -0.1)), mat)   # sin unión: no hay caras coplanares
            zf_end = z0 - PT
        else:
            mk.hull(p, plank_pts(A, B, w, za, zb, (0.1, -0.08)), mat)
            zf_end = z0 - PT
        u = ((B[0] - A[0]), (B[1] - A[1]))
        n = math.hypot(*u)
        nails(mk, p, [(A[0] + u[0] / n * 0.25, A[1] + u[1] / n * 0.25, 1),
                      (B[0] - u[0] / n * 0.25, B[1] - u[1] / n * 0.25, -1)], zf_end)


# ----------------------------------------------------------------------------------------- puerta
def door(mk, ox):
    z0 = -0.40
    planks = [((-2.35, 0.95), (2.2, 1.15), LIGHT), ((-2.25, 2.6), (2.4, 2.35), MID), ((-2.4, 3.85), (2.1, 4.0), LIGHT),
              ((-2.2, 5.3), (2.35, 5.05), LIGHT), ((-2.3, 6.6), (2.25, 6.85), MID)]
    for i, (a, b, mat) in enumerate(planks):
        p = mk.part(f"Barricade_Door_frag0{i + 1}", (ox, 0, 0))
        A, B = (ox + a[0], a[1]), (ox + b[0], b[1])
        mk.hull(p, plank_pts(A, B, 0.6, z0, z0, (0.12 * (-1) ** i, 0.1)), mat)
        nails(mk, p, [(A[0] + 0.25, A[1], 1), (A[0] + 0.3, A[1] + 0.15, -1), (B[0] - 0.25, B[1], -1)], z0 - PT)


# ------------------------------------------------------------------------------------------ calle
def crate(mk, p, c, s, turn):
    """Cajón de lado s con cantos oscuros (chanflán con material) y juntas de tablas; girado `turn` en Y."""
    cx, cy, cz = c
    mk.box(p, c, (s, s, s), LIGHT, rot=(0, turn, 0))
    mk.bevel(p, width=0.12, angle=35, mat=DARK)                                                   # cantos oscuros (marco)
    for k in (1, 2):                                                                             # juntas de tablas
        y = cy - s / 2 + s * k / 3
        for d in (-0.025, 0.025):
            mk.slice(p, (cx, y + d, cz), (0, 1, 0))
        mk.paint(p, MID, box=((cx, y, cz), (s * 1.5, 0.052, s * 1.5)))


def sack(mk, p, c, size, rot):
    """Bolsa de lona acostada: cuerpo que se angosta hacia la boca, atadura de soga y la punta de lona."""
    cx, cy, cz = c
    w, h, d = size
    sec = [(-1, -0.6), (-0.6, -1), (0.6, -1), (1, -0.6), (1, 0.6), (0.6, 1), (-0.6, 1), (-1, 0.6)]   # sección (y, z)
    body = []
    for x, k in ((-w / 2, 0.7), (-w / 4, 1.0), (w / 5, 0.95), (w / 2 - 0.12, 0.5)):
        body += [(x, sy * h / 2 * k, sz * d / 2 * k) for sy, sz in sec]
    T = lambda pts: [(cx + q[0], cy + q[1], cz + q[2]) for q in (rotate(t, rot) for t in pts)]
    mk.hull(p, T(body), CANVAS)
    nx = w / 2 - 0.08                                                                           # atadura
    tie = [(x, r * math.cos(2 * math.pi * i / 6) * h / d, r * math.sin(2 * math.pi * i / 6)) for i in range(6)
           for x, r in ((nx - 0.06, 0.2), (nx + 0.06, 0.2))]
    mk.hull(p, T(tie), ROPE)
    tuft = [(nx + 0.04, sy * 0.08, sz * 0.1) for sy, sz in sec[::2]] + [(nx + 0.3, sy * 0.16, sz * 0.2) for sy, sz in sec[::2]]
    mk.hull(p, T(tuft), CANVAS)


def street(mk, ox):
    # frag01: mesa volcada: tablero de pie mirando a -Z, patas hacia atrás
    p = mk.part("Barricade_Street_frag01", (ox, 0, 0))
    tx0, tx1, ty0, ty1, tz = ox - 2.4, ox + 1.2, 0.0, 2.2, -0.5
    mk.box(p, ((tx0 + tx1) / 2, (ty0 + ty1) / 2, tz), (tx1 - tx0, ty1 - ty0, 0.2), MID)
    for x in (tx0 + 0.25, tx1 - 0.25):
        for y in (0.09, ty1 - 0.25):
            mk.box(p, (x, y, tz + 1.3), (0.18, 0.18, 2.4), DARK)                                  # patas
    mk.box(p, ((tx0 + tx1) / 2, 0.09, tz + 0.2), (tx1 - tx0 - 0.4, 0.18, 0.2), DARK)             # bastidor
    for k in (1, 2):                                                                             # juntas del tablero
        y = ty0 + (ty1 - ty0) * k / 3
        for d in (-0.025, 0.025):
            mk.slice(p, (ox, y + d, tz), (0, 1, 0))
        mk.paint(p, DARK, box=(((tx0 + tx1) / 2, y, tz - 0.1), (tx1 - tx0 + 0.2, 0.052, 0.02)))
    mk.carve(p, LIGHT, prism=dict(profile=[(tx0 - 0.1, 1.5), (tx0 + 0.4, 2.3), (tx0 - 0.1, 2.3)], depth=1.0,
                                  plane="xy", center=(0, 0, tz)))                                 # esquina rota
    # frag02 / frag03: cajones
    p = mk.part("Barricade_Street_frag02", (ox, 0, 0))
    crate(mk, p, (ox - 3.2, 0.8, -0.1), 1.6, 0)
    union(mk, p)
    p = mk.part("Barricade_Street_frag03", (ox, 0, 0))
    crate(mk, p, (ox - 3.1, 1.6 + 0.65, -0.05), 1.3, 17)
    union(mk, p)
    # frag04: rueda apoyada en la mesa (gira 20° en Y, se inclina 12° hacia atrás)
    p = mk.part("Barricade_Street_frag04", (ox, 0, 0))
    R, rot = 1.3, (15, -20, 0)
    wc = (ox + 1.55, R * math.cos(math.radians(15)) + 0.03, -0.95)
    ring = lambda r, n=12: [(r * math.cos(2 * math.pi * (i + 0.5) / n), r * math.sin(2 * math.pi * (i + 0.5) / n)) for i in range(n)]
    mk.prism(p, ring(R + 0.06), 0.2, IRON, plane="xy", center=wc, rot=rot)                      # llanta
    mk.prism(p, ring(R), 0.24, MID, plane="xy", center=wc, rot=rot)                             # pina
    for k in range(6):                                                                           # rayos
        a = math.radians(30 + 60 * k)
        pts = [(math.cos(a) * r + math.sin(a) * t, math.sin(a) * r - math.cos(a) * t, z)
               for r in (0.18, R - 0.12) for t in (-0.06, 0.06) for z in (-0.07, 0.07)]
        mk.hull(p, [(wc[0] + q[0], wc[1] + q[1], wc[2] + q[2]) for q in (rotate(t, rot) for t in pts)], MID, detail=True)
    hub = [(0.24 * math.cos(2 * math.pi * i / 8), 0.24 * math.sin(2 * math.pi * i / 8), z) for i in range(8) for z in (-0.21, 0.21)]
    mk.hull(p, [(wc[0] + q[0], wc[1] + q[1], wc[2] + q[2]) for q in (rotate(t, rot) for t in hub)], DARK, detail=True)
    # el hueco de la rueda: rayos y maza van como detalle para que el tallado no se los coma
    mk.carve(p, MID, prism=dict(profile=ring(R - 0.2), depth=0.6, plane="xy", center=wc, rot=rot))
    # frag05 / frag06: bolsas de lona
    p = mk.part("Barricade_Street_frag05", (ox, 0, 0))
    sack(mk, p, (ox + 3.05, 0.32, -0.5), (1.3, 0.62, 0.85), (0, 8, 0))
    sack(mk, p, (ox + 3.0, 0.32, 0.3), (1.3, 0.62, 0.85), (0, -6, 0))
    union(mk, p)
    p = mk.part("Barricade_Street_frag06", (ox, 0, 0))
    sack(mk, p, (ox + 2.95, 0.86, -0.1), (1.25, 0.55, 0.8), (6, 25, 4))
    union(mk, p)


def build(mk):
    window(mk, 0.0)
    door(mk, 8.0)
    street(mk, 20.0)

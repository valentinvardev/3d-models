"""
Receta de WST_SB_Dock, los muelles del río de Silver Bend (prompt 109, Bloques A + C).

Brief
- Silueta a 40 studs: plataforma de tablas sobre pilotes redondos a 3 del agua, con dos pilotes que
  pasan el tablero como bitas (una con la amarra enrollada), rollo de soga en el piso; la punta con
  escalera al agua y un bote atado; el módulo con casilla de pesca.
- Módulo de 8 x 8, origen en la superficie del agua (y = 0) bajo el centro del módulo: el tablero queda
  arriba en y = 3 (inferido: "the ground plane" de un muelle es el agua). Tablas a lo largo de X.
- Tablero: 12 tablas de 8 x 0,4 x 0,667 (0,4 de espesor por la regla de fragmentos) en 6 fragmentos de
  dos tablas (frag01 en la punta -Z ... frag06 en +Z). Colores wood_mid / wood_light salteados, juntas
  wood_dark pintadas de 0,06 (la del borde de cada fragmento, repartida 0,03 y 0,03).
- fixed_Frame (queda en pie): 4 pilotes de 8 lados (r 0,42 -> 0,4) en x = ±3,5, z = ±3,2, de y = -3 al
  cabezal; dos cabezales a lo largo de X (0,7 x 0,5, y 1,6..2,1); tres largueros a lo largo de Z
  (0,45 x 0,5, y 2,1..2,6, x = -3,5, 0, 3,5); una riostra en diagonal en cada costado. Los dos pilotes
  de +X siguen hasta y = 4 (bitas): los fragmentos llevan la muesca tallada alrededor (luz 0,03); una
  bita lleva dos vueltas de soga.
- Variantes en fila sobre Z, cada una con su origen (prefijo <Variante>_): Dock_Shack en z = -8 (contra
  la orilla), Dock_Straight en z = 0, Dock_End en z = 8 (punta del muelle).
- Dock_End: escalera fija a la punta +Z (Dock_End_fixed_Ladder: largueros de y -1 a 3,9, 5 peldaños cada
  0,8). Rowboat (objeto aparte, 8 de largo, origen en la línea de agua al centro del bote) flotando al
  costado +X, atado a la bita de la punta -Z del Dock_End con una amarra que cuelga.
- Dock_Shack: casilla de pesca de 6 x 6 sobre el tablero (Dock_Shack_Shack: un objeto macizo, no se entra;
  tablas verticales wood_mid / wood_light, esquineros oscuros, techo de una sola agua hacia +Z de 6 a 5,
  puerta de tablas con Z y bisagras, ventana con postigos, caño de estufa).
- Inferido: origen en el agua, espesores y alturas de la estructura, bitas como pilotes que pasan el
  tablero, soga enrollada (dos tambores de soga con el centro tallado), escalera, la casilla cerrada (no
  se entra), colores del bote (paint_teal gastado afuera, wood_mid adentro), nombres con prefijo y
  Rowboat sin prefijo (es uno solo).

Vueltas: 1) primera versión: z-fighting del alféizar con el piso del hueco de la ventana y de la puerta
con la base de la casilla, las palas de los dos remos en el mismo plano, y los tramos de la amarra
compartían el cuadrado de la junta (bordes de tres caras) · 2) alféizar más abajo, puerta 0,03 arriba
del piso, una pala hacia cada punta, tramos de amarra que pasan 0,05 la junta con grosores alternados,
una sola vuelta de amarra en la bita.

Revisión
- Triángulos por módulo (tope 600 de referencia): Dock_Straight 780, Dock_End 868 (con la escalera, 84),
  Dock_Shack 1202 (la casilla, 642), Rowboat 530. Total 3380. El exceso del módulo es lo que lo hace leer:
  las muescas talladas alrededor de las bitas (~90), el rollo de soga (~100) y las juntas pintadas de las
  12 tablas; la casilla gasta en las tablas verticales de las cuatro caras.
- Medidas: módulo 8 x 8 (las bitas suben a 4, 1 sobre el tablero), tablero arriba en y = 3, pilotes hasta
  y = -3 (3 bajo el agua). Casilla 6 x 6 (7 x 7 con el alero), 6 de alto adelante y 5 atrás. Bote de
  7,95 x 2,8 (borda a ~1,0, fondo a -0,4).
- Fragmentos: 6 por módulo, cada uno 1/6 del tablero (16,7 %), de 0,4 de espesor.
- Materiales: 6 (wood_light, wood_mid, wood_dark, rope, paint_teal, iron).
- La casilla es maciza (no se entra): su casco convexo es una caja. Si se quiere entrar, hay que partirla
  en paredes (decide Valentin).
- El bote queda al costado +X del Dock_End con su origen en la línea de agua: si se mueve el muelle, la
  amarra queda colgando de la bita de z = 4,8.
"""

import math

LIGHT, MID, DARK, ROPE, TEAL, IRON = "wood_light", "wood_mid", "wood_dark", "rope", "paint_teal", "iron"
DECK_Y = (2.6, 3.0)
FW = 8.0 / 6                      # ancho de un fragmento (dos tablas)
PILE_X, PILE_Z = 3.5, 3.2
CAP_Y, JOIST_Y = (1.6, 2.1), (2.1, 2.6)
BOLLARD_TOP = 4.0


def ring(cx, y, cz, r, n=8, phase=0.5):
    return [(cx + r * math.cos(2 * math.pi * (i + phase) / n), y, cz + r * math.sin(2 * math.pi * (i + phase) / n))
            for i in range(n)]


# ------------------------------------------------------------------------------------------------ tablero
def deck(mk, pre, oz, colors, damage=None, coil=None):
    """colors: 12 colores de tabla (de -Z a +Z). damage: {frag: callable(part, z0, z1)}."""
    parts = []
    for k in range(6):
        z0, z1 = oz - 4.0 + k * FW, oz - 4.0 + (k + 1) * FW
        zm = (z0 + z1) / 2
        p = mk.part(f"{pre}_frag{k + 1:02d}", (0, 0, oz))
        mk.box(p, (0, sum(DECK_Y) / 2, zm), (8.0, DECK_Y[1] - DECK_Y[0], FW), MID)
        for j, (za, zb) in enumerate(((z0, zm), (zm, z1))):
            if colors[2 * k + j] == LIGHT:
                mk.paint(p, LIGHT, box=((0, sum(DECK_Y) / 2, (za + zb) / 2), (8.2, 0.42, zb - za - 0.002)))
        mk.slice(p, (0, 0, zm), (0, 0, 1))
        for zc, w in ((zm, 0.06), (z0 + 0.015, 0.03), (z1 - 0.015, 0.03)):
            for d in (-w / 2, w / 2):
                mk.slice(p, (0, 0, zc + d), (0, 0, 1))
            mk.paint(p, DARK, box=((0, DECK_Y[1], zc), (8.2, 0.02, w + 0.002)))
        for zb in (oz - PILE_Z, oz + PILE_Z):                         # muesca alrededor de las bitas
            if z0 < zb < z1:
                mk.carve(p, DARK, points=mk.pts_cyl((PILE_X, 2.8, zb), 0.45, 1.2, sides=8))
        if damage and k in damage:
            damage[k](p, z0, z1)
        if coil and coil[0] == k:
            rope_coil(mk, p, coil[1], coil[2])
        parts.append(p)
    return parts


def rope_coil(mk, part, x, z):
    """Rollo de soga en el piso: dos tambores de soga encimados y girados, con el centro tallado."""
    y = DECK_Y[1]
    mk.hull(part, ring(x, y - 0.02, z, 0.62) + ring(x, y + 0.16, z, 0.6), ROPE)
    mk.hull(part, ring(x, y + 0.14, z, 0.54, phase=0.0) + ring(x, y + 0.3, z, 0.5, phase=0.0), ROPE)
    mk.carve(part, DARK, points=mk.pts_cyl((x, y + 0.3, z), 0.22, 0.4, sides=8))


def hole(mk, x0, x1):
    """Tabla con un pedazo roto en el borde -Z de un fragmento."""
    def f(p, z0, z1):
        prof = [(x0, z0 - 0.1), (x1, z0 - 0.1), (x1 - 0.12, z0 + 0.22), (x1 - 0.35, z0 + 0.3), ((x0 + x1) / 2, z0 + 0.42),
                (x0 + 0.25, z0 + 0.28), (x0 + 0.08, z0 + 0.32)]
        mk.carve(p, DARK, prism=dict(profile=prof, depth=1.0, plane="xz", center=(0, 2.8, 0)))
    return f


def notch_end(mk, side, zfrac):
    """Punta de una tabla comida (en x = side * 4)."""
    def f(p, z0, z1):
        za = z0 + (z1 - z0) * zfrac
        tri = [(side * 4.1, za - 0.05), (side * 4.1, za + 0.62), (side * 3.55, za + 0.62), (side * 3.75, za + 0.2)]
        mk.carve(p, LIGHT, prism=dict(profile=tri, depth=1.0, plane="xz", center=(0, 2.8, 0)))
    return f


# --------------------------------------------------------------------------------------------- estructura
def frame(mk, pre, oz, rope_on=None):
    p = mk.part(f"{pre}_fixed_Frame", (0, 0, oz))
    for s in (-1, 1):
        for sz in (-1, 1):
            top = BOLLARD_TOP if s > 0 else CAP_Y[0] + 0.05
            x, z = s * PILE_X, oz + sz * PILE_Z
            mk.hull(p, ring(x, -3.0, z, 0.42) + ring(x, top - (0.12 if s > 0 else 0.0), z, 0.4), MID)
            if s > 0:                                                         # remate de la bita
                mk.hull(p, ring(x, top - 0.13, z, 0.398) + ring(x, top, z, 0.26), MID)
    for sz in (-1, 1):
        mk.box(p, (0, sum(CAP_Y) / 2, oz + sz * PILE_Z), (8.6, CAP_Y[1] - CAP_Y[0], 0.7), DARK)       # cabezales
    for x in (-PILE_X, 0.0, PILE_X):
        mk.box(p, (x, sum(JOIST_Y) / 2, oz), (0.45, JOIST_Y[1] - JOIST_Y[0], 8.0), DARK)            # largueros
    for s in (-1, 1):                                                         # riostra en cada costado
        xi = s * (PILE_X + 0.35)
        a, b = (oz - s * PILE_Z, 1.5), (oz + s * PILE_Z, -0.4)
        dz, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dz, dy)
        nz, ny = -dy / n * 0.25, dz / n * 0.25
        pts = [(xi + s * t, y + sy * ny, z + sy * nz) for t in (0.0, 0.16) for (z, y) in (a, b) for sy in (-1, 1)]
        mk.hull(p, pts, DARK)
    if rope_on is not None:                                                   # dos vueltas de amarra en una bita
        z = oz + rope_on * PILE_Z
        mk.hull(p, ring(PILE_X, 3.3, z, 0.47, phase=0.0) + ring(PILE_X, 3.62, z, 0.47, phase=0.0), ROPE)
    return p


def ladder(mk, pre, oz):
    p = mk.part(f"{pre}_fixed_Ladder", (0, 0, oz))
    z = oz + 4.0 + 0.125
    for s in (-1, 1):
        mk.box(p, (s * 0.65, (-1.0 + 3.9) / 2, z), (0.2, 4.9, 0.25), DARK)
    for y in (-0.6, 0.2, 1.0, 1.8, 2.6):
        mk.box(p, (0, y, z), (1.4, 0.15, 0.15), MID)
    return p


# ------------------------------------------------------------------------------------------------- casilla
def shack(mk, pre, oz):
    p = mk.part(f"{pre}_Shack", (0, 0, oz))
    y0, hf, hb = DECK_Y[1], 6.0, 5.0
    zf, zb = oz - 3.0, oz + 3.0
    body = [(x, y0, z) for x in (-3.0, 3.0) for z in (zf, zb)]
    body += [(x, y0 + hf, zf) for x in (-3.0, 3.0)] + [(x, y0 + hb, zb) for x in (-3.0, 3.0)]
    mk.hull(p, body, MID)
    # techo: losa de 0,25 con alero de 0,5, sobre la pendiente de las paredes
    slope = (hf - hb) / 6.0
    def ry(z):
        return y0 + hf - slope * (z - zf)
    roof = []
    for z in (zf - 0.5, zb + 0.5):
        for x in (-3.5, 3.5):
            roof += [(x, ry(z) - 0.03, z), (x, ry(z) + 0.25, z)]
    mk.hull(p, roof, DARK)
    # esquineros
    for x in (-3.0, 3.0):
        for z in (zf, zb):
            h = (hf if z == zf else hb) - 0.05
            mk.box(p, (x, y0 + h / 2, z), (0.36, h, 0.36), DARK)
    # tablas verticales: juntas oscuras y tablas claras salteadas en las cuatro caras
    xs = [-3.0 + 0.6 * i for i in range(1, 10)]
    for x in xs:
        for d in (-0.03, 0.03):
            mk.slice(p, (x + d, 0, 0), (1, 0, 0))
        for z in (zf, zb):
            mk.paint(p, DARK, box=((x, y0 + 3.0, z), (0.062, 6.0, 0.02)))
    for z in [oz - 3.0 + 0.6 * i for i in range(1, 10)]:
        for d in (-0.03, 0.03):
            mk.slice(p, (0, 0, z + d), (0, 0, 1))
        for x in (-3.0, 3.0):
            mk.paint(p, DARK, box=((x, y0 + 3.0, z), (0.02, 6.0, 0.062)))
    for i in (1, 4, 5, 8):                                         # tablas claras (frente y atrás)
        xc = -3.0 + 0.6 * i + 0.3
        for z in (zf, zb):
            mk.paint(p, LIGHT, box=((xc, y0 + 3.0, z), (0.5, 6.0, 0.02)))
    for i in (2, 3, 7):                                            # tablas claras (costados)
        zc = oz - 3.0 + 0.6 * i + 0.3
        for x in (-3.0, 3.0):
            mk.paint(p, LIGHT, box=((x, y0 + 3.0, zc), (0.02, 6.0, 0.5)))
    # puerta de tablas con Z (frente), un poco salida de la pared
    dx0, dx1, dh = -1.9, 0.5, 5.0
    mk.box(p, ((dx0 + dx1) / 2, y0 + 0.03 + dh / 2, zf - 0.03), (dx1 - dx0, dh, 0.1), MID, detail=True)
    for yy in (0.8, dh - 0.8):
        mk.box(p, ((dx0 + dx1) / 2, y0 + yy, zf - 0.1), (dx1 - dx0 - 0.2, 0.4, 0.08), DARK, detail=True)
    mk.hull(p, [(x, y0 + y, zf - 0.1 + dz) for (x, y) in ((dx0 + 0.25, 1.0), (dx0 + 0.25, 1.45), (dx1 - 0.25, dh - 1.0),
                                                         (dx1 - 0.25, dh - 1.45)) for dz in (-0.04, 0.04)], DARK, detail=True)
    for yy in (0.8, dh - 0.8):                                    # bisagras de pletina
        mk.box(p, (dx0 + 0.45, y0 + yy, zf - 0.16), (0.9, 0.14, 0.05), IRON, detail=True)
    mk.box(p, (dx1 - 0.3, y0 + 2.6, zf - 0.12), (0.1, 0.4, 0.1), IRON, detail=True)        # tirador
    # ventana con postigos (costado +X)
    wz, wy, ww, wh = oz - 0.2, y0 + 3.0, 1.4, 1.2
    mk.carve(p, DARK, points=mk.pts_box((3.0, wy, wz), (0.4, wh, ww)))
    mk.box(p, (3.1, wy - wh / 2 - 0.09, wz), (0.3, 0.12, ww + 0.3), DARK, detail=True)        # alféizar (abajo del hueco)
    for s in (-1, 1):                                             # postigos abiertos contra la pared
        mk.box(p, (3.04, wy, wz + s * (ww / 2 + 0.38)), (0.1, wh + 0.1, 0.7), LIGHT, detail=True)
    # caño de estufa atrás
    sx, sz = 1.6, oz + 2.0
    mk.cyl(p, (sx, ry(sz) + 0.8, sz), 0.22, 2.0, IRON, sides=8, detail=True)
    mk.cyl(p, (sx, ry(sz) + 1.9, sz), 0.38, 0.3, IRON, sides=8, top=0.3, detail=True)
    return p


# ------------------------------------------------------------------------------------------------- bote
def rowboat(mk, cx, cz, tie):
    """Bote de 8 (a lo largo de Z, proa hacia -Z), origen en la línea de agua al centro."""
    p = mk.part("Rowboat", (cx, 0, cz))
    # estaciones: (z, medio ancho borda, y borda, medio ancho pantoque, medio ancho quilla, y fondo)
    st = [(-4.0, 0.12, 1.3, 0.1, 0.08, 0.35), (-3.0, 0.9, 1.15, 0.62, 0.22, -0.22), (-1.5, 1.3, 1.05, 0.95, 0.3, -0.38),
          (0.4, 1.4, 1.0, 1.05, 0.32, -0.4), (2.3, 1.3, 1.02, 0.95, 0.3, -0.35), (3.95, 0.95, 1.1, 0.75, 0.26, -0.12)]
    outer, inner = [], []
    for z, hw, yt, hc, hk, yb in st:
        for s in (-1, 1):
            outer += [(cx + s * hw, yt + 0.2, cz + z), (cx + s * hc, 0.1, cz + z), (cx + s * hk, yb, cz + z)]
        zi = max(min(z, 3.8), -3.75)
        k = 0.13
        for s in (-1, 1):
            if hw - k > 0.05:
                inner += [(cx + s * (hw - k), 3.0, cz + zi), (cx + s * (hc - k), 0.1, cz + zi),
                          (cx + s * max(hk - k, 0.05), yb + 0.16, cz + zi)]
    mk.hull(p, outer, TEAL)
    mk.carve(p, MID, points=inner)
    sheer = [(cz - 4.6, 3.0), (cz - 4.6, 1.3), (cz - 3.0, 1.15), (cz - 1.5, 1.05), (cz + 0.4, 1.0), (cz + 2.3, 1.02),
             (cz + 4.6, 1.12), (cz + 4.6, 3.0)]
    mk.carve(p, DARK, prism=dict(profile=sheer, depth=4.0, plane="zy", center=(cx, 0, 0)))      # línea de la borda
    for yy in (0.42, 0.72):                                           # tracas: juntas oscuras afuera
        for d in (-0.03, 0.03):
            mk.slice(p, (cx, yy + d, cz), (0, 1, 0))
        mk.paint(p, DARK, box=((cx, yy, cz), (3.2, 0.062, 8.4)))
    for zt, w in ((-1.0, 2.2), (1.6, 2.2)):                           # bancadas
        mk.box(p, (cx, 0.62, cz + zt), (w, 0.12, 0.5), LIGHT, detail=True)
    for s, a in ((-1, 4.0), (1, 183.0)):                              # remos sobre las bancadas, palas a cada punta
        r = math.radians(a)
        L = 5.8
        x0, x1 = cx + s * 0.35 - math.sin(r) * L / 2, cx + s * 0.35 + math.sin(r) * L / 2
        z0, z1 = cz + 0.1 - math.cos(r) * L / 2, cz + 0.1 + math.cos(r) * L / 2
        mk.hull(p, [(x + dx, 0.67 + dy, z) for (x, z) in ((x0, z0), (x1, z1)) for dx in (-0.06, 0.06)
                    for dy in (0.0, 0.1)], LIGHT, detail=True)
        sg = 1 if z1 > z0 else -1
        mk.hull(p, [(x1 + dx, 0.68 + dy, z1 + sg * dz) for dx in (-0.22, 0.22) for dy in (0.0, 0.06) for dz in (-0.1, 0.8)],
                LIGHT, detail=True)                                    # pala
    # amarra: de la roda a la bita, colgando en tres tramos
    a = (cx, 1.25, cz - 3.95)
    m1 = (a[0] + (tie[0] - a[0]) * 0.35, 0.9, a[2] + (tie[2] - a[2]) * 0.35)
    m2 = (a[0] + (tie[0] - a[0]) * 0.7, 1.6, a[2] + (tie[2] - a[2]) * 0.7)
    for i, (q0, q1) in enumerate(((a, m1), (m1, m2), (m2, tie))):
        d = [q1[k] - q0[k] for k in range(3)]
        n = math.sqrt(sum(c * c for c in d))
        e = [c / n * 0.05 for c in d]
        q0 = [q0[k] - (e[k] if i else 0) for k in range(3)]            # cada tramo pasa 0,05 la junta
        q1 = [q1[k] + (e[k] if i < 2 else 0) for k in range(3)]
        t = 0.06 if i % 2 == 0 else 0.056
        mk.hull(p, [(q[0] + dx, q[1] + dy, q[2]) for q in (q0, q1) for dx in (-t, t) for dy in (-t, t)],
                ROPE, detail=True)
    return p


# ------------------------------------------------------------------------------------------------ armado
def build(mk):
    # recto
    pre, oz = "Dock_Straight", 0.0
    deck(mk, pre, oz, [MID, LIGHT, MID, MID, LIGHT, MID, LIGHT, LIGHT, MID, LIGHT, MID, MID],
         damage={2: hole(mk, -2.2, -0.9), 4: notch_end(mk, -1, 0.5)}, coil=(3, 2.4, oz + 0.2))
    frame(mk, pre, oz, rope_on=1)

    # punta, con escalera y bote
    pre, oz = "Dock_End", 8.0
    deck(mk, pre, oz, [LIGHT, MID, MID, LIGHT, MID, LIGHT, MID, MID, LIGHT, MID, LIGHT, MID],
         damage={1: notch_end(mk, 1, 0.1), 5: hole(mk, 0.8, 2.0)}, coil=(4, -2.3, oz + 1.6))
    frame(mk, pre, oz, rope_on=-1)
    ladder(mk, pre, oz)
    rowboat(mk, 6.3, oz, (PILE_X + 0.42, 3.42, oz - PILE_Z))

    # con casilla
    pre, oz = "Dock_Shack", -8.0
    deck(mk, pre, oz, [MID, MID, LIGHT, MID, LIGHT, LIGHT, MID, LIGHT, MID, MID, LIGHT, MID],
         damage={0: notch_end(mk, 1, 0.3)})
    frame(mk, pre, oz)
    shack(mk, pre, oz)

"""
Receta de WST_DG_Station, la estación de tren de Dusty Gulch (prompt 078, Bloques A + B).

Brief
- Silueta a 40 studs: un galpón bajo color mostaza con tablas verticales y molduras oscuras, un techo de
  dos aguas muy ancho cuyo faldón del lado de las vías sigue de largo (menos inclinado) como alero sobre el
  andén, con ménsulas en diagonal; el mirador del jefe de estación que sobresale hacia las vías; un andén
  largo de madera sobre pilotes. Es la llegada del pueblo ("estación vacía: falsa calma").
- Medidas (studs): edificio 16 (X) x 8 (Z), z de -8 a 0; piso a 1,2 (la altura del andén), una planta de 10
  (paredes hasta 11,2), puertas de 4 x 7,5 y ventanas de 3 x 4 con alféizar a 3 del piso (grilla del kit).
  Andén 40 x 8 x 1,2 del lado de las vías (+Z, z de 0 a 8) con escalones en las puntas. Techo de 24 de largo
  (sale 4 en cada punta): dos aguas a 35° con la cumbrera en z = -4 y el alero de la calle en z = -9,5; del
  lado de las vías el faldón quiebra en la pared (z = 0) y sigue a 18° hasta z = 6 cubriendo el andén
  (canto a 9,25: 8 sobre el andén). "Footprint 24 x 10" leído como la planta de la estación: techo de 24 de
  largo y edificio + mirador de ~10 de fondo; el andén de 40 x 8 va aparte, como dice el prompt.
- Piezas (todas con el origen del modelo en el piso, z = 0 en la pared de las vías, salvo las sueltas):
  Platform (andén: tablas atravesadas con juntas, faja, pilotes, escalones), Building (cuerpo, tablas y
  tapajuntas, molduras, mirador, puertas y ventanas cerradas, escalinata de la calle), Roof (faldones con
  hiladas de tejuelas, cumbrera, cabios a la vista bajo el alero, ménsulas, caño de la estufa), Bench
  (origen en su base), HandCart (carro de equipaje, origen en su base), Sign (cartel colgante, origen
  arriba al centro, entre las cadenas: puede hamacarse como Sign_Hanging).
- Colores: paint_mustard (recoloreable) en tablas y tapajuntas; wood_dark en molduras, zócalo, ménsulas y
  canto del techo; wood_mid en tejuelas, puertas y bancos; wood_light en el andén; iron, glass, leather,
  canvas y paint_cream (cartel, como el kit de carteles). 9 materiales: es un conjunto de 6 piezas.
- Tallado: ventanas y puertas son huecos tallados (jambas wood_dark) con vidrio, travesaños y hojas como
  detalle adentro; molduras como tablas reales encima. Pintado: hiladas de tejuelas y juntas del andén.
- Inferido: lectura del footprint, quiebre del alero a 18°, puertas cerradas (la colisión de casco no deja
  entrar igual), mirador de 4,4 a 2,8 de ancho y 1,6 de fondo, ménsulas en la pared de las vías (x = ±2,45 y
  ±7,75) y en las puntas (z = -1,5 y -6,5), cartel de 7 x 1,4 mirando a las vías en z = 4, banco bajo la
  ventana de la derecha, carro de equipaje de 4 ruedas con baúl, valijas y sombrerera, caño de estufa.

Técnica: el cuerpo, los hastiales, las fajas y el mirador son la base (las booleanas de los huecos los
funden). Tapajuntas y molduras son DETALLE apoyado a 0,001 de la pared (dentro de la tolerancia de contacto
del QA): metidos en la base, cada uno abría un agujero en la pared y en las fajas (+700 medido). El fondo de
cada hueco se pinta: vidrio en las ventanas, hoja wood_mid en las puertas, con tableros y vidrios tallados.

Vueltas: 1) 5270 tris y z-fighting (parante y travesaño con la misma base, largueros del carro al ras del
piso, parantes del cartel, patas del brazo del banco) · 2) molduras a la base, fondos pintados: 5140 ·
3) tapajuntas a 0,001 de las fajas: la pared quedó con 15 agujeros, sin cambio · experimentos sin render:
base 368, tapajuntas +708, aberturas +1490 · 4) molduras y tapajuntas como detalle apoyado: edificio 2206 ·
5) desgaste: la tabla rota tallada unía toda la base del andén (+470 y una cara degenerada) · 6) tabla
floja levantada como detalle, tapajunta suelta y otra que falta, escalón astillado.

Revisión
- 4420 triángulos contra 2500 de referencia (+77 %, calidad primero): Building 2196 (10 aberturas con
  jambas, molduras, cabezal con botaguas y vidrio con travesaños; 60 tapajuntas con relieve; mirador),
  Roof 716 (hiladas de tejuelas, 12 cabios y 8 ménsulas que se ven desde el andén), Platform 652 (40 tablas
  con juntas, faja y pilotes), HandCart 536, Bench 188, Sign 132. Ninguna pieza pasa de 2200.
- Medidas: andén 40 x 8 x 1,2 (con escalones 44,8 de largo); edificio 16 x 8, paredes de 10 desde el piso
  a 1,2; techo de 24 x 15,5 (alero de la calle 1,5, alero de las vías 6); alto con el caño 15,4.
  Puertas 4 x 7,5 y ventanas 3 x 4 con alféizar a 3 del piso (grilla del kit).
- 10 materiales (conjunto de 6 piezas): mostaza, tres maderas, hierro, vidrio, dos cueros, lona y crema.
- Colisión: Roof incluye las ménsulas pero su casco queda arriba de 7,3 (el jugador en el andén llega a
  6,2). Puertas cerradas: con colisión de casco el edificio no se recorre por adentro.
- Dudoso: la lectura del "footprint 24 x 10" (techo de 24 y edificio + mirador de ~10 de fondo); el alero
  de las vías sale 4 más allá de cada punta del edificio sin postes (el prompt dice "on brackets").
"""

import math

from mathutils import Vector

E = 0.003
F = 1.2                       # piso del edificio = andén
WALL_TOP = 11.2               # 10 de planta
T35, T18 = math.tan(math.radians(35)), math.tan(math.radians(18))
ROOF_T = 0.4                  # espesor del faldón (vertical)
X_ROOF = 12.0                 # medio largo del techo
Z_EAVE_ST, Z_RIDGE, Z_EDGE = -9.5, -4.0, 6.0
PAINT, TRIM, MID, LIGHT = "paint_mustard", "wood_dark", "wood_mid", "wood_light"

# paredes: (punto de la cara, dirección u a lo largo, normal hacia afuera)
FRONT = ((0.0, 0.0, -8.0), (1.0, 0.0, 0.0), (0.0, 0.0, -1.0))
TRACK = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
LEFT = ((-8.0, 0.0, -4.0), (0.0, 0.0, 1.0), (-1.0, 0.0, 0.0))
RIGHT = ((8.0, 0.0, -4.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0))
# mirador: 4,4 de ancho en la pared, 2,8 al frente, 1,6 de fondo
BW0, BW1, BD = 2.2, 1.4, 1.6
_side = Vector((BW1 - BW0, 0.0, BD)).normalized()
BAY_F = ((0.0, 0.0, BD), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
BAY_R = (((BW0 + BW1) / 2, 0.0, BD / 2), tuple(_side), (_side.z, 0.0, -_side.x))
BAY_L = ((-(BW0 + BW1) / 2, 0.0, BD / 2), (-_side.x, 0.0, _side.z), (-_side.z, 0.0, -_side.x))


def yb(z):
    """Cara de abajo del techo en z."""
    if z <= Z_RIDGE:
        return WALL_TOP + (z + 8.0) * T35
    if z <= 0.0:
        return WALL_TOP - z * T35
    return WALL_TOP - z * T18


def wpt(wall, u, y, d):
    p, uu, n = wall
    return (p[0] + uu[0] * u + n[0] * d, y, p[2] + uu[2] * u + n[2] * d)


def wbox(mk, part, wall, u0, u1, y0, y1, d0, d1, mat, detail=False):
    """Caja en coordenadas de una pared: u a lo largo, y alto, d hacia afuera de la cara."""
    mk.hull(part, [wpt(wall, u, y, d) for u in (u0, u1) for y in (y0, y1) for d in (d0, d1)], mat, detail)


def bx(mk, part, x0, x1, y0, y1, z0, z1, mat, detail=False):
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat, detail=detail)


def tube(mk, part, a, b, r, mat, sides=4, detail=False):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    u = d.cross(Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = d.cross(u)
    mk.hull(part, [tuple(p + r * (math.cos(t) * u + math.sin(t) * v)) for p in (a, b)
                   for t in (2 * math.pi * (k + 0.5) / sides for k in range(sides))], mat, detail)


# ---- aberturas: (pared, centro u, ancho, abajo, arriba, puerta?, ancho de jamba) ----
WIN0, WIN1 = F + 3.0, F + 7.0
DOOR1 = F + 7.5
OPENINGS = [
    (FRONT, 0.0, 4.0, F, DOOR1, True, 0.2),
    (FRONT, -5.0, 3.0, WIN0, WIN1, False, 0.2),
    (FRONT, 5.0, 3.0, WIN0, WIN1, False, 0.2),
    (TRACK, -5.0, 4.0, F, DOOR1, True, 0.2),
    (TRACK, 5.0, 3.0, WIN0, WIN1, False, 0.2),
    (LEFT, 0.0, 3.0, WIN0, WIN1, False, 0.2),
    (RIGHT, 0.0, 3.0, WIN0, WIN1, False, 0.2),
    (BAY_F, 0.0, 2.2, WIN0, WIN1, False, 0.15),
    (BAY_R, 0.0, 1.0, WIN0, WIN1, False, 0.15),
    (BAY_L, 0.0, 1.0, WIN0, WIN1, False, 0.15),
]
WT0, WT1 = 1.15, 1.75             # zócalo (moldura de abajo)
CD = 0.001                        # molduras y tapajuntas: detalle apoyado a 0,001 de la pared (sin booleana)
FR0, FR1 = 10.45, 11.22           # friso bajo el alero
HEAD_H, SILL_H = 0.35, 0.15


def casing_span(op):
    _, uc, w, _, _, _, cw = op
    return uc - w / 2 - cw - 0.12, uc + w / 2 + cw + 0.12


def battens(mk, part, wall, us, ops):
    """Tapajuntas de 0,2 cada 1 stud, 0,08 afuera; se cortan donde hay una abertura con su moldura."""
    for u in us:
        segs = [(WT1 + 0.001, FR0 - 0.001)]
        for op in ops:
            a, b = casing_span(op)
            if b <= u - 0.1 or a >= u + 0.1:
                continue
            _, _, _, y0, y1, door, _ = op
            new = []
            for s0, s1 in segs:
                lo = (s0, y0 - SILL_H - 0.001) if not door else None
                hi = (y1 + HEAD_H + 0.1 + 0.001, s1)
                for seg in (lo, hi):
                    if seg and seg[1] - seg[0] > 0.3:
                        new.append(seg)
            segs = new
        if (wall, u) in MISSING:
            continue
        for s0, s1 in segs:
            if (wall, u) in LOOSE:                    # tapajunta suelta: se despegó abajo y se corrió
                du = LOOSE[(wall, u)]
                pts = [wpt(wall, uu + du, s0 + 0.35, d) for uu in (u - 0.1, u + 0.1) for d in (CD + 0.03, 0.11)]
                pts += [wpt(wall, uu, s1, d) for uu in (u - 0.1, u + 0.1) for d in (CD, 0.08)]
                mk.hull(part, pts, PAINT, True)
                continue
            wbox(mk, part, wall, u - 0.1, u + 0.1, s0, s1, CD, 0.08, PAINT, True)


def head(mk, part, wall, u0, u1, y):
    """Cabezal con botaguas en un solo casco: más ancho y más salido arriba."""
    pts = [wpt(wall, u, y, d) for u in (u0 - 0.1, u1 + 0.1) for d in (CD, 0.15)]
    pts += [wpt(wall, u, y + HEAD_H, d) for u in (u0 - 0.1, u1 + 0.1) for d in (CD, 0.15)]
    pts += [wpt(wall, u, y + HEAD_H + 0.1, d) for u in (u0 - 0.17, u1 + 0.17) for d in (CD, 0.22)]
    mk.hull(part, pts, TRIM, True)


MISSING = {(LEFT, 2.5)}                         # tapajunta que falta
LOOSE = {(FRONT, 7.0): 0.16, (RIGHT, -2.5): -0.14}


def opening(mk, part, op):
    """Hueco tallado (jambas wood_dark) con sus molduras en la base: la booleana las funde con la pared y
    se van sus caras escondidas. Ventana: el fondo del hueco se pinta de vidrio y lleva travesaño y
    parante. Puerta: el fondo es la hoja (pintada wood_mid) con tableros y vidrios tallados."""
    wall, uc, w, y0, y1, door, cw = op
    u0, u1 = uc - w / 2, uc + w / 2
    depth = 0.2 if door else 0.3
    yc0 = y0 + (0.02 if door else 0.0)               # puertas desde 1,22: el umbral no es coplanar con el escalón
    mk.carve(part, TRIM, points=[wpt(wall, u, y, d) for u in (u0, u1) for y in (yc0, y1) for d in (-depth, 0.6)])
    # molduras apenas afuera del hueco (sin caras coplanares con las jambas), espaldas a distinta profundidad
    for a, b in ((u0 - cw, u0 - 0.004), (u1 + 0.004, u1 + cw)):
        wbox(mk, part, wall, a, b, (WT1 + 0.001) if door else (y0 - 0.003), y1 + 0.003, CD, 0.13, TRIM, True)
    head(mk, part, wall, u0 - cw, u1 + cw, y1 + 0.004)
    back = (wpt(wall, uc, (yc0 + y1) / 2, -depth), w - 0.02, y1 - yc0 - 0.02)
    if not door:
        wbox(mk, part, wall, u0 - cw - 0.12, u1 + cw + 0.12, y0 - SILL_H, y0 - 0.004, CD, 0.26, TRIM, True)
        PAINT_BACK.append((part, wall, back, "glass"))
        ym = (y0 + y1) / 2
        wbox(mk, part, wall, u0 + 0.01, u1 - 0.01, ym - 0.09, ym + 0.09, -depth - 0.02, -depth + 0.12, TRIM, True)
        if w > 1.5:
            wbox(mk, part, wall, uc - 0.05, uc + 0.05, y0 + 0.1, y1 - 0.1, -depth - 0.02, -depth + 0.1, TRIM, True)
    else:
        PAINT_BACK.append((part, wall, back, MID))
        yd0, yd1 = yc0, y1
        cuts = [((uc - 0.03, uc + 0.03), (yd0 - 0.01, yd1 + 0.01), 0.06, TRIM)]        # junta entre las hojas
        for a, b in ((u0, uc), (uc, u1)):
            cuts.append(((a + 0.32, b - 0.32), (yd0 + 0.55, yd0 + 3.4), 0.05, MID))      # tablero hundido
            cuts.append(((a + 0.32, b - 0.32), (yd0 + 3.95, yd1 - 0.45), 0.05, "glass"))  # vidrio
        for (ua, ub), (ya, yb_), dd, mat in cuts:
            mk.carve(part, mat, points=[wpt(wall, u, y, d) for u in (ua, ub) for y in (ya, yb_)
                                        for d in (-depth - dd, -depth + 0.3)])
        for kx in (uc - 0.35, uc + 0.35):                                                 # tiradores
            wbox(mk, part, wall, kx - 0.06, kx + 0.06, yd0 + 3.3, yd0 + 3.6, -depth - 0.02, -depth + 0.1, "iron", True)


PAINT_BACK = []


def paint_backs(mk):
    """Pinta el fondo de cada hueco (vidrio u hoja de puerta): una caja fina en la profundidad del fondo."""
    for part, wall, (c, w, h), mat in PAINT_BACK:
        _, uu, n = wall
        if abs(uu[0]) in (0.0, 1.0):                  # pared alineada: caja fina del tamaño del fondo
            size = tuple(abs(uu[k]) * w + abs(n[k]) * 0.02 + (h if k == 1 else 0.0) for k in range(3))
        else:                                         # cara en ángulo (mirador): el fondo es una sola cara
            size = (0.1, 0.1, 0.1)
        mk.paint(part, mat, box=(c, size))


def build_platform(mk):
    p = mk.part("Platform", (0, 0, 0))
    bx(mk, p, -20.0, 20.0, 0.9, F, 0.0, 8.0, LIGHT)                                # tablero
    bx(mk, p, -19.6, 19.6, 0.1, 0.92, 0.05, 7.6, TRIM)                             # sombra bajo el tablero
    for k in range(11):                                                            # pilotes del lado de las vías
        x = -19.75 + k * 3.95
        bx(mk, p, x - 0.22, x + 0.22, 0.0, 0.95, 7.52, 7.98, MID)
    for x in (-17.5, -11.5, 11.5, 17.5):                                           # y del lado de la calle
        bx(mk, p, x - 0.22, x + 0.22, 0.0, 0.95, 0.02, 0.48, MID)
    bx(mk, p, -20.1, 20.1, 0.76, 1.17, 7.96, 8.1, TRIM)                           # faja del canto (las otras, corridas)
    for s in (-1, 1):
        bx(mk, p, min(s * 8.0, s * 20.093), max(s * 8.0, s * 20.093), 0.765, 1.168, -0.1, 0.04, TRIM)
        x0, x1 = sorted((s * 19.96, s * 20.096))
        bx(mk, p, x0, x1, 0.755, 1.166, -0.096, 8.096, TRIM)
        # escalones en las puntas (dos de 0,4; el tercero es el tablero)
        for i, (h, dx) in enumerate(((0.4, 2.4), (0.8, 1.6))):
            a, b = sorted((s * 19.98, s * (20.0 + dx)))
            bx(mk, p, a, b, 0.0 if i == 0 else 0.38, h, 2.0 + 0.004 * i, 6.0 - 0.004 * i, MID)
    # juntas de las tablas (atravesadas al andén, de 1 de ancho)
    for k in range(-19, 20):
        mk.slice(p, (k - 0.03, 0, 0), (1, 0, 0))
        mk.slice(p, (k + 0.03, 0, 0), (1, 0, 0))
        mk.paint(p, TRIM, box=((k, F, 4.0), (0.07, 0.02, 8.3)))
    for xc in (-9.5, 13.5, 14.5):                                                  # tablas cambiadas
        mk.paint(p, MID, box=((xc, F, 4.0), (0.9, 0.02, 8.3)))
    # tabla floja: la punta del lado de las vías se levantó (detalle; tallarla une toda la base: +470)
    mk.box(p, (6.5, F + 0.07, 7.15), (0.9, 0.12, 1.75), LIGHT, rot=(-7, 0, 0), detail=True)


def build_building(mk):
    b = mk.part("Building", (0, 0, 0))
    bx(mk, b, -8.0, 8.0, 0.0, WALL_TOP, -8.0, 0.0, PAINT)                           # cuerpo
    # hastial bajo los faldones (0,05 metido en el techo)
    mk.prism(b, [(-7.997, 11.0), (-0.003, 11.0), (-0.003, yb(-0.003) + 0.05), (Z_RIDGE, yb(Z_RIDGE) + 0.05),
                 (-7.997, yb(-7.997) + 0.05)], 2 * 7.997, PAINT, plane="zy", center=(0, 0, 0))
    bx(mk, b, -8.14, 8.14, WT0, WT1, -8.14, 0.14, TRIM)                             # zócalo
    bx(mk, b, -8.14, 8.14, FR0, FR1, -8.14, 0.14, TRIM)                             # friso
    for sx in (-1, 1):                                                             # esquineros
        for z0, z1 in ((-8.12, -7.45), (-0.68, 0.12)):
            x0, x1 = sorted((sx * 7.45, sx * 8.12))
            bx(mk, b, x0, x1, WT1 + 0.001, FR0 - 0.001, z0, z1, TRIM, detail=True)
    # mirador (prisma en planta, metido 0,3 en el cuerpo) y su cornisa
    bay = [(-BW0, -0.3), (BW0, -0.3), (BW0, 0.0), (BW1, BD), (-BW1, BD), (-BW0, 0.0)]
    mk.prism(b, bay, 10.25 - 1.4, PAINT, plane="xz", center=(0, (1.4 + 10.25) / 2, 0))
    band = [(-BW0 - 0.06, -0.3), (BW0 + 0.06, -0.3), (BW0 + 0.06, 0.0), (BW1 + 0.03, BD + 0.06),
            (-BW1 - 0.03, BD + 0.06), (-BW0 - 0.06, 0.0)]
    mk.prism(b, band, WT1 - 1.205, TRIM, plane="xz", center=(0, (1.205 + WT1) / 2, 0))     # zócalo
    mk.prism(b, band, 0.5, TRIM, plane="xz", center=(0, 9.75, 0))                          # friso
    corn = [(-BW0 - 0.17, -0.3), (BW0 + 0.17, -0.3), (BW0 + 0.17, 0.0), (BW1 + 0.1, BD + 0.15),
            (-BW1 - 0.1, BD + 0.15), (-BW0 - 0.17, 0.0)]
    mk.prism(b, corn, 0.4, TRIM, plane="xz", center=(0, 10.15, 0))
    # tapajuntas
    ops = OPENINGS
    for wall in (FRONT, TRACK):
        battens(mk, b, wall, [-7.0 + k for k in range(15)], [o for o in ops if o[0] is wall])
    for wall in (LEFT, RIGHT):
        battens(mk, b, wall, [-2.5 + k for k in range(6)], [o for o in ops if o[0] is wall])
    # tapajuntas del hastial (siguen la pendiente)
    for sx in (-1, 1):
        for z in (-6.5, -5.5, -4.5, -3.5, -2.5, -1.5):
            xa, xb = sorted((sx * 7.998, sx * 8.077))
            pts = []
            for zz in (z - 0.1, z + 0.1):
                for xx in (xa, xb):
                    pts += [(xx, FR1 + 0.001, zz), (xx, yb(zz) - 0.001, zz)]
            mk.hull(b, pts, PAINT, detail=True)
    # escalinata de la calle (tres escalones de 0,4 hasta el piso)
    for i in range(3):
        bx(mk, b, -2.8 + 0.004 * i, 2.8 - 0.004 * i, 0.4 * i - (0.02 if i else 0.0), 0.4 * (i + 1),
           -10.4 + 0.8 * i, -7.98 + 0.01 * i, MID)
    mk.carve(b, LIGHT, points=[(2.82, 1.25, -8.85), (2.0, 1.25, -8.85), (2.82, 1.25, -8.1), (2.82, 0.95, -8.85)])
    for op in ops:
        opening(mk, b, op)
    paint_backs(mk)
    # cimiento oscuro bajo el zócalo y bandas oscuras del mirador
    mk.slice(b, (0, 1.18, 0), (0, 1, 0))
    for c, s in (((0, 0.59, -8.0), (16.3, 1.18, 0.02)), ((0, 0.59, 0.0), (16.3, 1.18, 0.02)),
                 ((-8.0, 0.59, -4.0), (0.02, 1.18, 8.3)), ((8.0, 0.59, -4.0), (0.02, 1.18, 8.3))):
        mk.paint(b, TRIM, box=(c, s))


def build_roof(mk):
    r = mk.part("Roof", (0, 0, 0))
    zs = (Z_EAVE_ST, Z_RIDGE, 0.0, Z_EDGE)
    bottom = [(z, yb(z)) for z in zs]
    top = [(z, y + ROOF_T) for z, y in reversed(bottom)]
    mk.prism(r, bottom + top, 2 * X_ROOF, TRIM, plane="zy", center=(0, 0, 0))
    # hiladas de tejuelas: cortes perpendiculares a cada faldón, franja oscura de 0,06 cada 0,8
    for (za, ya), (zb, yb_) in (((Z_EAVE_ST, yb(Z_EAVE_ST)), (Z_RIDGE, yb(Z_RIDGE))),
                                ((0.0, yb(0.0)), (Z_RIDGE, yb(Z_RIDGE))),
                                ((Z_EDGE, yb(Z_EDGE)), (0.0, yb(0.0)))):
        a, c = Vector((0, ya + ROOF_T, za)), Vector((0, yb_ + ROOF_T, zb))
        d = (c - a)
        L = d.length
        d.normalize()
        n = int(L / 0.8)
        cuts = [0.0] + [0.8 * k for k in range(1, n + 1) if 0.8 * k < L - 0.3] + [L]
        for k in range(1, len(cuts) - 1):
            q = a + d * cuts[k]
            for o in (-0.03, 0.03):
                mk.slice(r, tuple(q + d * o), tuple(d))
        for k in range(len(cuts) - 1):
            s0 = cuts[k] + (0.03 if k > 0 else 0.0)
            s1 = cuts[k + 1] - (0.03 if k + 1 < len(cuts) - 1 else 0.0)
            q = a + d * ((s0 + s1) / 2)
            mk.paint(r, MID, box=(tuple(q), (2 * X_ROOF - 0.1, 0.1, 0.1)))
    # cumbrera
    pts = []
    for z in (Z_RIDGE - 0.32, Z_RIDGE + 0.32):
        for x in (-X_ROOF - 0.08, X_ROOF + 0.08):
            pts += [(x, yb(z) + ROOF_T - 0.04, z), (x, yb(Z_RIDGE) + ROOF_T + 0.2, z)]
    mk.hull(r, pts, TRIM)
    # cabios a la vista bajo el alero de las vías
    for k in range(12):
        x = -11.0 + 2.0 * k
        pts = []
        for z in (0.0, Z_EDGE - 0.08):
            for xx in (x - 0.1, x + 0.1):
                pts += [(xx, yb(z) + 0.03, z), (xx, yb(z) - 0.28, z)]
        mk.hull(r, pts, MID)
    # ménsulas en la pared de las vías: taco en la pared, brazo bajo el alero y diagonal
    for x, z0 in ((-7.75, 0.1), (-2.45, -0.02), (2.45, -0.02), (7.75, 0.1)):
        bx(mk, r, x - 0.13, x + 0.13, 7.3, yb(z0) - 0.02, z0, z0 + 0.25, TRIM)
        pts = []
        for z in (z0 + 0.05, 3.6):
            for xx in (x - 0.12, x + 0.12):
                pts += [(xx, yb(z) + 0.03, z), (xx, yb(z) - 0.32, z)]
        mk.hull(r, pts, TRIM)
        tube(mk, r, (x, 7.75, z0 + 0.15), (x, yb(3.0) - 0.2, 3.0), 0.12, TRIM)
    # ménsulas en las puntas, bajo el alero de los hastiales
    for sx in (-1, 1):
        for z in (-6.5, -1.5):
            x0, x1 = sorted((sx * 8.06, sx * 8.31))
            bx(mk, r, x0, x1, 8.6, yb(z) - 0.02, z - 0.13, z + 0.13, TRIM)
            pts = []
            for x in (sx * 8.1, sx * 11.0):
                for zz in (z - 0.12, z + 0.12):
                    pts += [(x, yb(zz) + 0.03, zz), (x, yb(z) - 0.32, zz)]
            mk.hull(r, pts, TRIM)
            tube(mk, r, (sx * 8.2, 9.0, z), (sx * 10.4, yb(z) - 0.2, z), 0.12, TRIM)
    # caño de la estufa sobre el faldón de la calle
    yt = yb(-6.2) + ROOF_T
    mk.cyl(r, (5.0, yt + 1.0, -6.2), 0.25, 2.6, "iron", sides=8)
    mk.cyl(r, (5.0, yt + 0.08, -6.2), 0.36, 0.36, "iron", sides=8)
    mk.cyl(r, (5.0, yt + 2.42, -6.2), 0.48, 0.3, "iron", sides=8, top=0.35)


def build_bench(mk):
    x0, x1, zb = 3.2, 6.8, 0.3
    bn = mk.part("Bench", ((x0 + x1) / 2, F, zb + 0.75))
    # costado de hierro: pata de adelante, travesaño del asiento, pata y parante de atrás; el brazo aparte
    prof = [(1.32, 0.0), (1.5, 0.0), (1.48, 1.45), (0.36, 1.45), (0.16, 3.0), (0.0, 3.0), (0.2, 1.3), (0.06, 0.0),
            (0.24, 0.0), (0.38, 1.18), (1.3, 1.18)]
    for x in (x0 + 0.15, x1 - 0.15):
        mk.prism(bn, [(zb + z, F + y) for z, y in prof], 0.14, "iron", plane="zy", center=(x, 0, 0))
        bx(mk, bn, x - 0.06, x + 0.06, F + 1.43, F + 2.2, zb + 1.36, zb + 1.49, "iron")
        bx(mk, bn, x - 0.075, x + 0.075, F + 2.12, F + 2.26, zb + 0.17, zb + 1.58, "iron")
    for zc in (zb + 0.45, zb + 0.85, zb + 1.25):                                   # asiento
        bx(mk, bn, x0, x1, F + 1.4, F + 1.52, zc - 0.17, zc + 0.17, MID)
    for yc, zc in ((F + 1.95, zb + 0.24), (F + 2.5, zb + 0.16)):                    # respaldo
        mk.box(bn, (0.5 * (x0 + x1), yc, zc), (x1 - x0, 0.34, 0.1), MID, rot=(-12, 0, 0))


def build_cart(mk):
    cx, cz, L, W = -14.0, 3.6, 4.4, 2.4
    yd = F + 1.2                                                                   # piso del carro
    c = mk.part("HandCart", (cx, F, cz))
    bx(mk, c, cx - L / 2, cx + L / 2, yd - 0.15, yd, cz - W / 2, cz + W / 2, MID)
    for s in (-1, 1):                                                              # largueros
        bx(mk, c, cx - L / 2 - 0.05, cx + L / 2 + 0.05, yd - 0.4, yd - 0.12, cz + s * (W / 2 - 0.13) - 0.12,
           cz + s * (W / 2 - 0.13) + 0.12, TRIM)
    for k in (-1, 0, 1):                                                           # juntas del piso
        z = cz + k * 0.6
        mk.slice(c, (0, 0, z - 0.03), (0, 0, 1))
        mk.slice(c, (0, 0, z + 0.03), (0, 0, 1))
        mk.paint(c, TRIM, box=((cx, yd, z), (L + 0.2, 0.02, 0.07)))
    rw = 0.55
    for xw in (cx - 1.4, cx + 1.4):                                                # ejes, tacos y ruedas
        bx(mk, c, xw - 0.14, xw + 0.14, F + rw - 0.06, yd - 0.38, cz - W / 2 + 0.05, cz + W / 2 - 0.05, TRIM)
        for s in (-1, 1):
            zw = cz + s * (W / 2 + 0.05)
            mk.cyl(c, (xw, F + rw, zw), rw, 0.16, "iron", axis="z", sides=8)
            mk.cyl(c, (xw, F + rw, zw), 0.16, 0.42, "iron", axis="z", sides=6)
    # baranda de hierro en la punta de atrás
    xe = cx + L / 2 - 0.12
    for s in (-1, 1):
        tube(mk, c, (xe, yd - 0.05, cz + s * (W / 2 - 0.15)), (xe, yd + 1.0, cz + s * (W / 2 - 0.15)), 0.06, "iron")
    tube(mk, c, (xe, yd + 1.0, cz - W / 2 + 0.08), (xe, yd + 1.0, cz + W / 2 - 0.08), 0.06, "iron")
    tube(mk, c, (xe, yd + 0.55, cz - W / 2 + 0.1), (xe, yd + 0.55, cz + W / 2 - 0.1), 0.05, "iron")
    # lanza con la manija en T, apoyada en el andén
    a = (cx - L / 2 + 0.2, yd - 0.3, cz)
    tip = (cx - L / 2 - 2.3, F + 0.09, cz)
    tube(mk, c, a, tip, 0.09, TRIM)
    tube(mk, c, (tip[0] + 0.02, F + 0.09, cz - 0.55), (tip[0] + 0.02, F + 0.09, cz + 0.55), 0.08, TRIM)
    # equipaje: baúl con zunchos, dos valijas, sombrerera
    tx, tz = cx - 0.7, cz - 0.05
    mk.box(c, (tx, yd + 0.49, tz), (1.7, 1.0, 1.15), "leather", top=(0.97, 0.94))
    for dx in (-0.5, 0.5):
        mk.box(c, (tx + dx, yd + 0.49, tz), (0.14, 1.04, 1.19), TRIM, top=(0.97, 0.94))
    for o in (-0.03, 0.03):                                                       # junta de la tapa
        mk.slice(c, (0, yd + 0.74 + o, 0), (0, 1, 0))
    mk.paint(c, TRIM, box=((tx, yd + 0.74, tz), (1.75, 0.065, 1.25)))
    bx(mk, c, cx + 0.55, cx + 1.85, yd - 0.01, yd + 0.86, cz - 1.0, cz - 0.55, "canvas")
    tube(mk, c, (cx + 0.95, yd + 0.86, cz - 0.78), (cx + 1.45, yd + 0.86, cz - 0.78), 0.05, "leather", detail=True)
    mk.box(c, (tx + 0.1, yd + 1.17, tz + 0.05), (1.2, 0.4, 0.8), "leather_dark", rot=(0, 8, 0))
    mk.cyl(c, (cx + 1.2, yd + 0.29, cz + 0.55), 0.42, 0.6, "canvas", sides=10)
    mk.cyl(c, (cx + 1.2, yd + 0.62, cz + 0.55), 0.45, 0.08, "leather", sides=10)


def build_sign(mk):
    zc, ytop = 5.0, yb(5.0)
    s = mk.part("Sign", (0.0, ytop, zc))
    y0, y1, hx = 7.7, 9.05, 3.5
    bx(mk, s, -hx + 0.12, hx - 0.12, y0 + 0.13, y1 - 0.13, zc - 0.08, zc + 0.08, "paint_cream")
    bx(mk, s, -hx, hx, y1 - 0.15, y1, zc - 0.11, zc + 0.11, TRIM)
    bx(mk, s, -hx, hx, y0, y0 + 0.15, zc - 0.11, zc + 0.11, TRIM)
    for sx in (-1, 1):
        a, b = sorted((sx * (hx - 0.15), sx * (hx - E)))
        bx(mk, s, a, b, y0 + 0.1, y1 - 0.1, zc - 0.105, zc + 0.105, TRIM)
    # cadenas: tres eslabones cruzados por lado, del cartel al alero
    for sx in (-2.6, 2.6):
        n = 3
        h = (ytop + 0.03 - (y1 - 0.03)) / n
        for i in range(n):
            ya = y1 - 0.03 + i * h
            size = (0.05, h + 0.04, 0.16) if i % 2 == 0 else (0.16, h + 0.04, 0.05)
            mk.box(s, (sx, ya + h / 2, zc), size, "iron")


def build(mk):
    build_platform(mk)
    build_building(mk)
    build_roof(mk)
    build_bench(mk)
    build_cart(mk)
    build_sign(mk)

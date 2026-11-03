"""
Receta de WST_DG_SaloonInterior, el interior del saloon (prompt 080, Bloques A + C).

Brief
- Se recorre por adentro (oleada 4: "aguantar en el saloon"): lo que importa es lo que se ve parado en el
  salón y detrás de la barra. Silueta a 40 studs: la barra larga oscura con la baranda de bronce, el mueble
  de atrás con el espejo grande y las botellas que brillan, la mesa redonda con la silla y la rueda de
  carreta colgando con seis faroles.
- Disposición de muestra (cada objeto con su origen propio en su base; el builder los reparte):
  BackBar contra la pared del fondo (origen en z = 5,5, frente a z = 4,75), BarCounter delante (origen en
  z = 2, frente a z = 1; queda un pasillo de 1,75 para el barman), Table_Round en (-4, -4), Chair en
  (-4, -1,9) mirando a la mesa, Chandelier colgado arriba de la mesa (eje arriba de la cadena en y = 10).
- BarCounter (16 x 4 x 2, frag 6): perfil con zócalo hundido, frente de tableros (2 tableros en relieve
  por fragmento, wood_mid sobre marco wood_dark), tapa wood_dark que sale 0,15, baranda de bronce para el
  pie con una ménsula por fragmento; atrás, dos estantes tallados. Cortes en los parantes, y una grieta en
  zigzag entre frag03 y frag04.
- BackBar (12 x 7 x 1,5, frag 6): mueble bajo con 4 puertas (frag01 y frag02, partido por una grieta en
  zigzag), dos alas de estantes con botellas glass_amber / glass_green (frag03 y frag04) y el espejo
  paint_slate en el centro bajo un copete (frag05 y frag06: el espejo rajado en diagonal).
- Table_Round (Ø 3,5, frag 3): tapa de 0,35 con faldón (las dos mitades partidas en zigzag) y pie
  torneado con cuatro patas en cruz (frag03). Cartas y fichas apoyadas, cada una en su mitad.
- Chair (frag 3): asiento y patas de adelante (frag01); cada parante de atrás con media cresta y dos
  husillos (frag02 izquierda, frag03 derecha).
- Chandelier: rueda de carreta de Ø 4 colgada de una cadena (eje arriba, en la cadena), 6 faroles de
  bronce; cada tubo de vidrio es Lamp_Glow_1..6 (lamp_glow), con el mismo eje que la araña.
- Grietas: los dos fragmentos de cada grieta se cortan con el mismo zigzag (caras de corte wood_light) y
  cada uno se talla una franja de 0,05 en coal sobre el frente: la pieza entera ya se ve rajada.
- Inferido: la disposición, profundidad del mueble de atrás (1,5), alturas (mesa 2,55, asiento 1,75,
  rueda a 7,6), colores de marco y tableros, cantidad de botellas, cartas cloth_white, fichas paint_red y
  paint_cream, varillas en vez de cadenas cortas para colgar la rueda.

Vueltas: 1) las grietas rompían las booleanas (bordes con giro invertido y abiertos en los 6 fragmentos
rajados): la franja de coal compartía la cara del corte de separación; z-fighting en columnas y moldura
(0,001 de separación), cresta de la silla contra el parante y pie de la mesa contra su collar · 2) franja
corrida 0,01 hacia el lado que se tira, separaciones de 0,004-0,008, cresta más gruesa: pasa limpio ·
3) faroles sin collar (el vidrio apoya en el depósito).

Revisión
- ~3600 triángulos contra 2500 (+44 %, calidad primero: es el interior que se defiende de cerca 90 s).
  BarCounter ~1090 (6 fragmentos con tableros en relieve, baranda, estantes tallados atrás y la grieta),
  BackBar ~1180 (16 botellas ~380, espejo tallado y rajado, columnas y cornisas), Table_Round ~530 (tapa de
  16 lados partida y ranurada, cartas y fichas), Chair 184, Chandelier ~420 + 6 vidrios de 32.
- Medidas: barra 16 x 4 x 2,3 (la baranda sale 0,3 adelante), mueble 12 x 7 x 1,6, mesa Ø 3,5 x 2,57,
  silla 1,6 x 3,85, rueda Ø 4 colgada a 7,6 de una cadena hasta y = 10.
- Fragmentos: barra 6 de ~16 % (cortes en los parantes y la grieta entre 03 y 04), mueble 6 (bajo en dos
  mitades de ~33 %, alas, espejo en dos), mesa 3, silla 3; todos de 0,4 o más (la tapa de la mesa con su
  faldón: 0,55).
- Materiales: 14 en el conjunto de 5 piezas (maderas, bronce, coal de las grietas, dos vidrios de botella,
  pizarra del espejo, hierro, lamp_glow, cartas y fichas).
- Dudoso: la silla rota en parantes de 0,18 (cada mitad del respaldo mide 0,48 de fondo por la inclinación,
  justo para la regla de 0,4); los fragmentos de la silla se tocan en líneas, no en caras.
"""

import math

from mathutils import Vector

E = 0.003
DARK, MID, LIGHT, FRESH, CRACK = "wood_dark", "wood_mid", "wood_light", "wood_light", "coal"
BAR_Z, BACK_Z = 2.0, 5.5
TABLE = (-4.0, -4.0)
CHAIR_Z = -1.9
PIVOT = (-4.0, 10.0, -4.0)


# ---- geometría 2D (de WST_Prop_CrateLarge): recorte de polígonos ----
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _area(poly):
    return 0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def _inter(p, q, a, b):
    d1, d2 = _cross(a, b, p), _cross(a, b, q)
    t = d1 / (d1 - d2)
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def clip(subject, clipper):
    """Sutherland-Hodgman: subject recortado por clipper (convexo)."""
    if _area(clipper) < 0:
        clipper = clipper[::-1]
    out = list(subject)
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            pin, qin = _cross(a, b, p) >= -1e-9, _cross(a, b, q) >= -1e-9
            if qin:
                if not pin:
                    out.append(_inter(p, q, a, b))
                out.append(q)
            elif pin:
                out.append(_inter(p, q, a, b))
        if not out:
            return []
    return out


def crack(mk, part, zig, keep, plane, center, depth, groove=None):
    """Corta part con el zigzag `zig` (lista de puntos 2D de una punta a la otra, en el plano dado) y se queda
    con el lado `keep` (+1: el de la izquierda de la recorrida, -1: el otro). Las caras del corte
    quedan FRESH. groove = (shift, clip_rect, center, depth): franja de 0,05 tallada en coal sobre el frente,
    del lado propio (shift = vector 2D hacia ese lado), recortada a clip_rect."""
    a, b = Vector(zig[0]), Vector(zig[-1])
    d = (b - a).normalized()
    left = Vector((-d.y, d.x))
    far = 50.0
    side = left * (-keep)                                   # el lado que se tira
    poly = [tuple(p) for p in zig] + [tuple(b + d * far + side * far), tuple(a - d * far + side * far)]
    mk.carve(part, FRESH, prism=dict(profile=poly, depth=depth, plane=plane, center=center))
    if groove:
        shift, rect, gcenter, gdepth = groove
        # la franja arranca 0,01 del otro lado del zigzag: si compartiera la cara del corte, la booleana se rompe
        band = ([(p[0] - 0.2 * shift[0], p[1] - 0.2 * shift[1]) for p in zig]
                + [(p[0] + shift[0], p[1] + shift[1]) for p in reversed(zig)])
        band = clip(band, rect)
        if len(band) >= 3:
            mk.carve(part, CRACK, prism=dict(profile=band, depth=gdepth, plane=plane, center=gcenter))


def bx(mk, part, x0, x1, y0, y1, z0, z1, mat, detail=False):
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat, detail=detail)


def raised(mk, part, x0, x1, y0, y1, z_face, proud, mat, inset=0.07):
    """Tablero en relieve (frente hacia -Z): base sobre la cara, frente más chico (bisel)."""
    zb, zf = z_face + 0.02, z_face - proud
    pts = [(x, y, zb) for x in (x0, x1) for y in (y0, y1)]
    pts += [(x, y, zf) for x in (x0 + inset, x1 - inset) for y in (y0 + inset, y1 - inset)]
    mk.hull(part, pts, mat)


def ring(c, r, axis_dir, n, phase=0.5):
    a = Vector(axis_dir).normalized()
    u = a.cross(Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = a.cross(u)
    c = Vector(c)
    return [tuple(c + r * (math.cos(2 * math.pi * (i + phase) / n) * u + math.sin(2 * math.pi * (i + phase) / n) * v))
            for i in range(n)]


def tube(mk, part, a, b, r, mat, sides=4, detail=False):
    a, b = Vector(a), Vector(b)
    mk.hull(part, ring(a, r, b - a, sides) + ring(b, r, b - a, sides), mat, detail)


def bottle(mk, part, x, y, z, kind):
    """Botella como un casco: cuerpo de 6 lados, hombro y cuello."""
    if kind == "whiskey":
        r, h, rn, mat = 0.15, 0.42, 0.05, "glass_amber"
    else:
        r, h, rn, mat = 0.12, 0.5, 0.045, "glass_green"
    pts = ring((x, y - 0.005, z), r, (0, 1, 0), 6) + ring((x, y + h, z), r, (0, 1, 0), 6)
    pts += ring((x, y + h + 0.1, z), rn + 0.02, (0, 1, 0), 4) + ring((x, y + h + 0.3, z), rn, (0, 1, 0), 4)
    mk.hull(part, pts, mat)


# ---------------------------------------------------------------- barra
BAR_PROFILE = [(-0.75, 0.0), (-0.75, 0.4), (-0.85, 0.4), (-0.85, 3.75), (-1.0, 3.75), (-1.0, 4.0), (1.0, 4.0),
               (1.0, 3.75), (0.9, 3.75), (0.9, 0.0)]
BAR_X = [-8.0, -16 / 3, -8 / 3, 0.0, 8 / 3, 16 / 3, 8.0]
BAR_ZIG = [(0.55, 4.4), (0.1, 3.3), (0.45, 2.4), (-0.15, 1.5), (0.2, 0.7), (-0.3, -0.4)]
_PW = (8 / 3 - 3 * 0.22) / 2
BAR_PANELS = [(BAR_X[j] + 0.22 + k * (_PW + 0.22), BAR_X[j] + 0.22 + k * (_PW + 0.22) + _PW)
              for j in range(6) for k in range(2)]


def build_bar(mk):
    oz = BAR_Z
    prof = [(oz + z, y) for z, y in BAR_PROFILE]
    for i in range(6):
        xa, xb = BAR_X[i], BAR_X[i + 1]
        name = f"BarCounter_frag{i + 1:02d}"
        p = mk.part(name, (0, 0, oz))
        ea = xa - (0.8 if i == 3 else 0.0)                  # los de la grieta se estiran y el zigzag los corta
        eb = xb + (0.8 if i == 2 else 0.0)
        mk.prism(p, prof, eb - ea, DARK, plane="zy", center=((ea + eb) / 2, 0, 0))
        w = xb - xa
        for x0, x1 in BAR_PANELS:                            # tableros en relieve (los vecinos de la grieta también)
            if x1 > ea + 0.05 and x0 < eb - 0.05:
                raised(mk, p, x0, x1, 0.75, 3.4, oz - 0.85, 0.07, MID)
        # baranda de bronce para el pie y su ménsula
        mk.cyl(p, ((ea + eb) / 2, 0.55, oz - 1.3), 0.1, eb - ea - 0.004, "brass", axis="x", sides=8)
        xm = (xa + xb) / 2
        bx(mk, p, xm - 0.06, xm + 0.06, 0.47, 0.63, oz - 1.32, oz - 0.83, "brass")
        # estantes del barman, tallados en la espalda
        r0 = xa + (0.15 if i != 3 else 0.95)
        r1 = xb - (0.15 if i != 2 else 0.95)
        for y0, y1 in ((0.6, 1.8), (2.05, 3.4)):
            mk.carve(p, MID, points=mk.pts_box(((r0 + r1) / 2, (y0 + y1) / 2, oz + 0.85), (r1 - r0, y1 - y0, 0.9)))
        mk.paint(p, "wood_charred", box=(((ea + eb) / 2, 0.2, oz - 0.75), (eb - ea + 0.1, 0.42, 0.02)))  # zócalo
        if i in (2, 3):
            keep = -1 if i == 2 else 1
            shift = (-0.05, 0.0) if i == 2 else (0.05, 0.0)
            crack(mk, p, BAR_ZIG, keep, "xy", (0, 0, oz), 3.0,
                  groove=(shift, [(-3, 0.72), (3, 0.72), (3, 4.5), (-3, 4.5)], (0, 0, oz - 1.18), 0.75))


# ---------------------------------------------------------------- mueble de atrás
BACK_PROFILE = [(-0.65, 0.0), (-0.65, 0.35), (-0.75, 0.35), (-0.75, 3.0), (-0.85, 3.0), (-0.85, 3.2), (0.75, 3.2),
                (0.75, 0.0)]
BASE_ZIG = [(0.35, 3.5), (-0.15, 2.6), (0.3, 1.7), (-0.2, 0.9), (0.1, -0.3)]
MIRROR_ZIG = [(-1.05, 7.3), (-0.45, 6.05), (-0.8, 5.3), (0.2, 4.55), (-0.05, 3.85), (0.75, 3.1)]


def build_backbar(mk):
    oz = BACK_Z
    prof = [(oz + z, y) for z, y in BACK_PROFILE]
    # ---- mueble bajo, en dos mitades partidas por una grieta ----
    for i, (xa, xb, keep) in enumerate(((-6.0, 0.9, -1), (-0.9, 6.0, 1))):
        p = mk.part(f"BackBar_frag{i + 1:02d}", (0, 0, oz))
        mk.prism(p, prof, xb - xa, DARK, plane="zy", center=((xa + xb) / 2, 0, 0))
        for xc in (-4.5, -1.5, 1.5, 4.5):
            if xc + 1.3 > xa + 0.05 and xc - 1.3 < xb - 0.05:
                raised(mk, p, xc - 1.3, xc + 1.3, 0.55, 2.8, oz - 0.75, 0.07, MID, inset=0.1)
            if (xc < 0) == (i == 0):
                kx = xc + (1.05 if xc < 0 else -1.05) * (1 if abs(xc) > 3 else -1)
                bx(mk, p, kx - 0.06, kx + 0.06, 1.6, 1.8, oz - 0.86, oz - 0.79, "brass", detail=True)
        mk.paint(p, "wood_charred", box=((0, 0.17, oz - 0.65), (12.2, 0.36, 0.02)))
        crack(mk, p, BASE_ZIG, keep, "xy", (0, 0, oz), 3.0,
              groove=(((-0.05, 0.0) if keep < 0 else (0.05, 0.0)),
                      [(-3, -0.5), (3, -0.5), (3, 3.05), (-3, 3.05)], (0, 0, oz - 1.0), 0.6))
        for bxp in ((-5.2, -3.9) if i == 0 else (3.9, 5.2)):                         # botellas sobre el mostrador
            bottle(mk, p, bxp, 3.2, oz - 0.45, "whiskey" if bxp < 0 else "wine")
    # ---- alas de estantes ----
    for i, s in enumerate((-1, 1)):
        p = mk.part(f"BackBar_frag{i + 3:02d}", (0, 0, oz))
        x_in, x_out = s * 2.52, s * 6.0
        a, b = sorted((x_in, x_out))
        bx(mk, p, a + 0.004, b - 0.004, 3.2, 6.52, oz + 0.35, oz + 0.75, MID)        # fondo
        for xa_, xb_ in (sorted((s * 2.522, s * 2.88)), sorted((s * 5.64, s * 5.998))):  # columnas
            bx(mk, p, xa_, xb_, 3.205, 6.47, oz - 0.05, oz + 0.74, DARK)
        ca, cb = sorted((s * 2.88 - s * 0.01, s * 5.64 + s * 0.01))
        for yb in (4.2, 5.35):                                                       # estantes
            bx(mk, p, ca, cb, yb, yb + 0.1, oz - 0.03, oz + 0.37, DARK)
        ca2, cb2 = sorted((s * 2.52, s * 6.1))
        bx(mk, p, ca2, cb2, 6.5, 6.8, oz - 0.2, oz + 0.8, DARK)                      # cornisa
        bx(mk, p, ca2 + (0.1 if s < 0 else 0.008), cb2 - (0.1 if s > 0 else 0.008), 6.42, 6.51, oz - 0.12,
           oz + 0.76, DARK)                                                          # moldura bajo la cornisa
        kinds = ("whiskey", "wine", "whiskey")
        for yb, xs in ((4.3, (3.4, 4.3, 5.1)), (5.45, (3.3, 4.05, 4.9))):
            for k, xx in enumerate(xs):
                bottle(mk, p, s * xx, yb, oz + 0.17, kinds[(k + int(yb)) % 3])
    # ---- espejo con copete, rajado en diagonal ----
    for i, keep in enumerate((-1, 1)):
        p = mk.part(f"BackBar_frag{i + 5:02d}", (0, 0, oz))
        bx(mk, p, -2.516, 2.516, 3.2, 6.52, oz + 0.35, oz + 0.75, MID)                # fondo
        bx(mk, p, -2.4, 2.4, 3.42, 6.36, oz + 0.2, oz + 0.37, DARK)                  # marco del espejo
        bx(mk, p, -2.52, 2.52, 6.5, 6.8, oz - 0.2, oz + 0.8, DARK)                   # cornisa
        bx(mk, p, -2.517, 2.517, 6.42, 6.51, oz - 0.12, oz + 0.76, DARK)
        mk.prism(p, [(-1.6, 6.78), (1.6, 6.78), (0.9, 7.0), (-0.9, 7.0)], 0.3, DARK, plane="xy",
                 center=(0, 0, oz + 0.3))                                            # copete
        mk.carve(p, "paint_slate", points=mk.pts_box((0, 4.89, oz + 0.2), (4.3, 2.47, 0.12)))  # espejo hundido
        crack(mk, p, MIRROR_ZIG, keep, "xy", (0, 0, oz), 3.0,
              groove=(((-0.05, 0.0) if keep < 0 else (0.05, 0.0)),
                      [(-2.2, 3.7), (2.2, 3.7), (2.2, 6.08), (-2.2, 6.08)], (0, 0, oz + 0.23), 0.18))


# ---------------------------------------------------------------- mesa redonda
TABLE_ZIG = [(-2.2, 0.35), (-1.1, 0.05), (-0.4, 0.42), (0.3, -0.05), (1.1, 0.25), (2.2, -0.2)]


def build_table(mk):
    tx, tz = TABLE
    zig = [(tx + x, tz + z) for x, z in TABLE_ZIG]
    for i, keep in enumerate((1, -1)):                     # frag01 atrás (+z), frag02 adelante
        p = mk.part(f"Table_Round_frag{i + 1:02d}", (tx, 0, tz))
        mk.cyl(p, (tx, 2.375, tz), 1.75, 0.35, MID, sides=16)
        mk.cyl(p, (tx, 2.11, tz), 1.5, 0.24, DARK, sides=16)
        crack(mk, p, zig, keep, "xz", (0, 1.5, 0), 3.0,
              groove=(((0.0, 0.05) if keep > 0 else (0.0, -0.05)),
                      [(tx - 2.5, tz - 2.5), (tx + 2.5, tz - 2.5), (tx + 2.5, tz + 2.5), (tx - 2.5, tz + 2.5)],
                      (0, 2.62, 0), 0.26))
        y = 2.55
        if keep > 0:                                        # cartas y fichas, apoyadas en su mitad
            mk.box(p, (tx - 0.7, y + 0.01, tz + 0.75), (0.36, 0.03, 0.52), "cloth_white", rot=(0, 20, 0))
            mk.box(p, (tx - 0.35, y + 0.01, tz + 0.95), (0.36, 0.03, 0.52), "cloth_white", rot=(0, -12, 0))
            mk.cyl(p, (tx + 0.6, y + 0.085, tz + 0.8), 0.13, 0.18, "paint_red", sides=8)
        else:
            mk.box(p, (tx + 0.4, y + 0.01, tz - 0.8), (0.36, 0.03, 0.52), "cloth_white", rot=(0, 35, 0))
            mk.cyl(p, (tx - 0.6, y + 0.055, tz - 0.7), 0.13, 0.12, "paint_cream", sides=8)
            mk.cyl(p, (tx - 0.9, y + 0.025, tz - 0.95), 0.13, 0.06, "paint_red", sides=8, rot=(6, 0, 0))
    p = mk.part("Table_Round_frag03", (tx, 0, tz))
    mk.cyl(p, (tx, 1.135, tz), 0.2, 1.67, DARK, sides=8)
    mk.cyl(p, (tx, 1.89, tz), 0.32, 0.2, DARK, sides=8)
    mk.cyl(p, (tx, 0.43, tz), 0.3, 0.3, DARK, sides=8)
    star = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        u = (math.cos(a), math.sin(a))
        v = (-u[1], u[0])
        star += [(0.2 * u[0] - 0.2 * v[0], 0.2 * u[1] - 0.2 * v[1]), (1.1 * u[0] - 0.08 * v[0], 1.1 * u[1] - 0.08 * v[1]),
                 (1.1 * u[0] + 0.08 * v[0], 1.1 * u[1] + 0.08 * v[1])]
    mk.prism(p, [(tx + a, tz + b) for a, b in star], 0.3, DARK, plane="xz", center=(0, 0.15, 0))


# ---------------------------------------------------------------- silla
def build_chair(mk):
    cx, cz = TABLE[0], CHAIR_Z
    seat_y0, seat_y1 = 1.6, 1.75

    def post_z(y):
        return cz + 0.62 + 0.33 * y / 3.8

    p = mk.part("Chair_frag01", (cx, 0, cz))
    oct_ = [(-0.8, -0.62), (-0.62, -0.78), (0.62, -0.78), (0.8, -0.62), (0.8, 0.5), (0.68, 0.668 - 0.0),
            (-0.68, 0.668), (-0.8, 0.5)]
    mk.prism(p, [(cx + a, cz + b) for a, b in oct_], seat_y1 - seat_y0, LIGHT, plane="xz",
             center=(0, (seat_y0 + seat_y1) / 2, 0))
    for sx in (-1, 1):                                                        # patas de adelante
        x = cx + sx * 0.6
        mk.hull(p, [(x + dx, 0.0, cz - 0.6 + dz) for dx in (-0.08, 0.08) for dz in (-0.08, 0.08)]
                + [(x + dx, seat_y0 + 0.01, cz - 0.56 + dz) for dx in (-0.08, 0.08) for dz in (-0.08, 0.08)], MID)
    bx(mk, p, cx - 0.53, cx + 0.53, 0.42, 0.56, cz - 0.64, cz - 0.52, MID)  # travesaño de adelante
    for sx in (-1, 1):                                                        # travesaños de los costados
        x0, x1 = sorted((cx + sx * 0.55, cx + sx * 0.67))
        bx(mk, p, x0, x1, 0.6, 0.72, cz - 0.52, cz + 0.585, MID)
    # parantes de atrás, cresta y husillos
    for i, sx in enumerate((-1, 1)):
        q = mk.part(f"Chair_frag{i + 2:02d}", (cx, 0, cz))
        x = cx + sx * 0.6
        mk.hull(q, [(x + dx, 0.0, post_z(0.0) + dz) for dx in (-0.09, 0.09) for dz in (-0.09, 0.09)]
                + [(x + dx, 3.85, post_z(3.85) + dz) for dx in (-0.09, 0.09) for dz in (-0.09, 0.09)], MID)
        xa, xb = sorted((cx, cx + sx * 0.72))
        pts = []
        for xx in (xa, xb):
            for y in (3.3, 3.78):
                for dz in (-0.12, 0.12):
                    pts.append((xx, y, post_z(y) + dz + 0.02 * abs(xx - cx)))
        mk.hull(q, pts, DARK)                                                 # media cresta
        for xs in (0.2, 0.42):                                                # husillos
            xx = cx + sx * xs
            mk.hull(q, [(xx + dx, seat_y1, cz + 0.6 + dz) for dx in (-0.045, 0.045)
                        for dz in (-0.045, 0.045)]
                    + [(xx + dx, 3.32, post_z(3.32) + dz) for dx in (-0.045, 0.045) for dz in (-0.045, 0.045)], MID)


# ---------------------------------------------------------------- araña de rueda de carreta
def build_chandelier(mk):
    px, py, pz = PIVOT
    yw = 7.6
    c = mk.part("Chandelier", PIVOT)
    r_out, r_in, gap, n = 2.0, 1.78, 0.4, 8
    for a0, a1 in ((gap, 180 - gap), (180 + gap, 360 - gap)):                 # pina en dos mitades
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([(px + r_out * math.cos(math.radians(a)), pz + r_out * math.sin(math.radians(a))) for a in angs]
                + [(px + r_in * math.cos(math.radians(a)), pz + r_in * math.sin(math.radians(a))) for a in reversed(angs)])
        mk.prism(c, prof, 0.22, DARK, plane="xz", center=(0, yw, 0))
        for i in range(n):                                                    # llanta de hierro
            m, h = (angs[i] + angs[i + 1]) / 2, (angs[i + 1] - angs[i]) / 2
            rr = r_out * math.cos(math.radians(h))
            mk.paint(c, "iron", ball=((px + rr * math.cos(math.radians(m)), yw, pz + rr * math.sin(math.radians(m))), 0.05))
    mk.cyl(c, (px, yw, pz), 0.3, 0.46, DARK, sides=8)                          # maza
    for k in range(3):                                                        # rayos
        a = math.radians(60 * k)
        u = Vector((math.cos(a), 0, math.sin(a)))
        v = Vector((-u.z, 0, u.x))
        pts = [tuple(Vector((px, yw, pz)) + u * t + v * w + Vector((0, h, 0)))
               for t in (-1.83, 1.83) for w in (-0.07, 0.07) for h in (-0.06 + 0.002 * k, 0.06 - 0.002 * k)]
        mk.hull(c, pts, MID)
    rm = (r_out + r_in) / 2
    for k in range(6):                                                        # faroles
        a = math.radians(30 + 60 * k)
        x, z = px + rm * math.cos(a), pz + rm * math.sin(a)
        mk.cyl(c, (x, yw + 0.22, z), 0.16, 0.26, "brass", sides=6, top=0.75)
        g = mk.part(f"Lamp_Glow_{k + 1}", PIVOT)
        pts = (ring((x, yw + 0.33, z), 0.08, (0, 1, 0), 6) + ring((x, yw + 0.52, z), 0.135, (0, 1, 0), 6)
               + ring((x, yw + 0.82, z), 0.065, (0, 1, 0), 6))
        mk.hull(g, pts, "lamp_glow")
    # varillas de la rueda al aro, y cadena al techo
    ring_y = 8.9
    mk.cyl(c, (px, ring_y, pz), 0.2, 0.12, "iron", sides=8)
    for k in range(3):
        a = math.radians(120 * k)
        x, z = px + rm * math.cos(a), pz + rm * math.sin(a)
        tube(mk, c, (x, yw + 0.08, z), (px + 0.12 * math.cos(a), ring_y, pz + 0.12 * math.sin(a)), 0.05, "iron")
    nl = 4
    h = (py + 0.02 - (ring_y + 0.04)) / nl
    for i in range(nl):
        y = ring_y + 0.04 + i * h + h / 2
        size = (0.06, h + 0.05, 0.17) if i % 2 == 0 else (0.17, h + 0.05, 0.06)
        mk.box(c, (px, y, pz), size, "iron")
    mk.box(c, (px, py + 0.05, pz), (0.3, 0.1, 0.3), "iron")                   # gancho del techo


def build(mk):
    build_bar(mk)
    build_backbar(mk)
    build_table(mk)
    build_chair(mk)
    build_chandelier(mk)

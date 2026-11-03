"""
Receta de WST_DG_StoreShelves, las estanterías del almacén y la armería (prompt 083, Bloques A + C).

Brief
- Interiores que se recorren (tienda al liberar el pueblo, D016): se miran de cerca y desde el salón.
  Silueta a 40 studs: un mueble alto lleno de mercadería de colores, un mostrador con vitrina y la caja
  registradora de bronce, y un tablero de pared con cuatro armas largas acostadas y dos revólveres.
- Disposición de muestra en fila (cada pieza con su origen en su base al centro, frente hacia -Z):
  Shelves_General en x = -10, Counter_Store en x = 0, GunDisplay_Wall en x = 10.
- Shelves_General (8 x 8 x 1,5, frag 4): costados, divisor al medio, fondo de tablas, zócalo, 5 estantes
  y corona. Abajo bolsas de lona y un cajón; latas de colores; frascos con tapa; telas dobladas arriba.
  Fragmentos: izquierda abajo / arriba cortados por el estante de 4,3 (frag01, frag03); derecha partida por
  una grieta en zigzag que cruza el fondo (frag02 abajo, frag04 arriba). Divisor del lado izquierdo.
- Counter_Store (8 x 3,5 x 2, frag 4): mitad izquierda con vitrina (vidrio arriba, al frente y en la
  punta, marco wood_dark, mercadería adentro: cajas de balas, un reloj, una lata), mitad derecha de madera
  con tableros, la caja registradora de bronce (cartel en blanco) y una balanza. Fragmentos de a 2 de largo;
  la grieta en zigzag entre frag03 y frag04.
- GunDisplay_Wall (8 x 5, colgado de 2,5 a 7,5): tablero de tablas con marco y clavijas a la altura que
  pide cada arma; repisa abajo. Gun_1 rifle de palanca (cajón de bronce), Gun_2 escopeta de dos caños,
  Gun_3 rifle de caza con mira de bronce, Gun_4 carabina de palanca (cajón de hierro), Gun_5 y Gun_6
  revólveres colgados con el caño para abajo. Siluetas de ~150-200 triángulos, proporciones de los modelos
  de armas (3,2 / 2,7 / 3,7 / 2,8 / 1,3 de largo). Origen de cada arma en su centro.
- Grietas como en WST_DG_SaloonInterior: el mismo zigzag corta los dos fragmentos (caras wood_light) y cada
  uno se talla una franja de coal de 0,05 en la cara que se ve.
- Inferido: disposición, alturas de los estantes, qué mercadería va en cada uno, vitrina en la mitad
  izquierda, armero sin fragmentos (el prompt no da frag: una pieza GunDisplay_Wall), 4 armas largas con el
  rifle de palanca repetido como carabina, 2 revólveres (Gun_5 y Gun_6) para llegar a 6.

Vueltas: 1) recortar todos los elementos de la estantería en el mismo plano dejaba puntas coplanares
(estante, zócalo, divisor, fondo); paño de la vitrina al ras del perfil; palancas con caras al ras; el
revólver de la izquierda metido en la culata de la carabina; teclas y manija de la registradora flotando ·
2) cada elemento se recorta 0,002 más adentro que el anterior en los bordes interiores, corte de la
izquierda en 4,32 (no sobre la cara del estante), latas sin tapa aparte, revólveres a ±2 · 3) mercadería,
registradora y balanza como detalle (la talla de la grieta las unía con los estantes): estantería de 1854
a 1466 · 4) dos cajas de balas que se tocaban justo en un borde.

Revisión
- Por pieza contra 800: Shelves_General 1466 (+83 %: ~40 objetos de mercadería, ~800 de ellos; es la vidriera
  de la tienda), Counter_Store 866 (+8 %), GunDisplay_Wall 478; armas 144 / 128 / 160 / 144 / 112 / 112
  (siluetas, el prompt pedía ~300).
- Medidas: estantería 8,2 x 8 x 1,6 (la corona sale 0,1); mostrador 8 x 3,5 x 2 (con la registradora 4,75);
  armero 8 x 5 colgado de 2,5 a 7,5 con clavijas que salen 0,5 de la pared.
- Fragmentos: estantería 4 (izquierda cortada por el estante de 4,3; derecha por la grieta), mostrador 4 de
  a 2 de largo; todos de 0,4 o más.
- Dudoso: las armas son siluetas planas de ~0,15 de espesor (se miran de frente en la pared); el armero no
  tiene fragmentos porque el prompt no los da.
"""

import math

from mathutils import Euler, Vector

DARK, MID, LIGHT, FRESH, CRACK = "wood_dark", "wood_mid", "wood_light", "wood_light", "coal"
SX, CX, GX = -10.0, 0.0, 10.0


# ---- geometría 2D (de WST_Prop_CrateLarge) y grietas (de WST_DG_SaloonInterior) ----
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _area(poly):
    return 0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def _inter(p, q, a, b):
    d1, d2 = _cross(a, b, p), _cross(a, b, q)
    t = d1 / (d1 - d2)
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def clip(subject, clipper):
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
    """Corta con el zigzag y se queda con el lado `keep` (+1: el de la izquierda de la recorrida). groove =
    (shift, clip_rect, center, depth): franja de coal de 0,05 del lado propio, arrancando 0,01 del otro lado
    (si comparte la cara del corte, la booleana se rompe: medido en el saloon)."""
    a, b = Vector(zig[0]), Vector(zig[-1])
    d = (b - a).normalized()
    left = Vector((-d.y, d.x))
    side = left * (-keep)
    far = 50.0
    poly = [tuple(p) for p in zig] + [tuple(b + d * far + side * far), tuple(a - d * far + side * far)]
    mk.carve(part, FRESH, prism=dict(profile=poly, depth=depth, plane=plane, center=center))
    if groove:
        shift, rect, gcenter, gdepth = groove
        band = ([(p[0] - 0.2 * shift[0], p[1] - 0.2 * shift[1]) for p in zig]
                + [(p[0] + shift[0], p[1] + shift[1]) for p in reversed(zig)])
        band = clip(band, rect)
        if len(band) >= 3:
            mk.carve(part, CRACK, prism=dict(profile=band, depth=gdepth, plane=plane, center=gcenter))


def bx(mk, part, x0, x1, y0, y1, z0, z1, mat, detail=False):
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat, detail=detail)


def ring(c, r, axis_dir, n, phase=0.5):
    a = Vector(axis_dir).normalized()
    u = a.cross(Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = a.cross(u)
    c = Vector(c)
    return [tuple(c + r * (math.cos(2 * math.pi * (i + phase) / n) * u + math.sin(2 * math.pi * (i + phase) / n) * v))
            for i in range(n)]


def raised(mk, part, x0, x1, y0, y1, z_face, proud, mat, inset=0.07):
    zb, zf = z_face + 0.02, z_face - proud
    pts = [(x, y, zb) for x in (x0, x1) for y in (y0, y1)]
    pts += [(x, y, zf) for x in (x0 + inset, x1 - inset) for y in (y0 + inset, y1 - inset)]
    mk.hull(part, pts, mat)


# ---------------------------------------------------------------- estantería
SHELF_Y = (0.4, 2.3, 4.2, 6.1)            # cara de abajo de cada estante (0,1 de espesor)
SHELF_ZIG = [(-0.1, 5.7), (0.9, 5.25), (1.7, 5.5), (2.5, 4.4), (3.2, 3.95), (4.25, 3.0)]


def shelf_structure(mk, p, ox, xa, xb, ya, yb_):
    """Estructura de la estantería recortada a la caja x [xa, xb], y [ya, yb] (coordenadas locales). En los
    bordes interiores (no en los de afuera del mueble) cada elemento se corta 0,002 más adentro que el
    anterior: si todos se cortan en el mismo plano, las puntas de los que se tocan quedan coplanares."""
    k = [0]

    def put(x0, x1, y0, y1, z0, z1, mat):
        e = 0.002 * k[0]
        k[0] += 1
        cx0 = xa + (e if xa > -3.99 else 0.0)
        cx1 = xb - (e if xb < 3.99 else 0.0)
        cy0 = ya + (e if ya > 0.01 else 0.0)
        cy1 = yb_ - (e if yb_ < 7.99 else 0.0)
        x0, x1 = max(x0, cx0), min(x1, cx1)
        y0, y1 = max(y0, cy0), min(y1, cy1)
        if x1 - x0 > 0.01 and y1 - y0 > 0.01:
            bx(mk, p, ox + x0, ox + x1, y0, y1, z0, z1, mat)
    put(-3.99, 3.99, 0.0, 7.85, 0.62, 0.748, MID)                                       # fondo
    put(-4.0, -3.85, 0.0, 7.82, -0.75, 0.744, DARK)                                      # costados
    put(3.85, 4.0, 0.0, 7.82, -0.75, 0.744, DARK)
    put(-0.075, 0.075, 0.45, 7.82, -0.7, 0.63, DARK)                                     # divisor
    put(-3.84, 3.84, 0.0, 0.41, -0.65, 0.63, DARK)                                       # zócalo
    for y in SHELF_Y:
        put(-3.86, 3.86, y, y + 0.1, -0.72, 0.63, MID)                                   # estantes
    put(-4.1, 4.1, 7.8, 8.0, -0.85, 0.75, DARK)                                          # corona


def can(mk, p, x, y, z, mat, h=0.42):
    """Lata pintada con el canto de arriba achaflanado (la tapa aparte costaba 24 por lata)."""
    mk.hull(p, ring((x, y - 0.005, z), 0.16, (0, 1, 0), 6) + ring((x, y + h - 0.03, z), 0.16, (0, 1, 0), 6)
            + ring((x, y + h, z), 0.13, (0, 1, 0), 6), mat, detail=True)


def jar(mk, p, x, y, z, mat):
    mk.hull(p, ring((x, y - 0.005, z), 0.19, (0, 1, 0), 6) + ring((x, y + 0.5, z), 0.19, (0, 1, 0), 6)
            + ring((x, y + 0.6, z), 0.13, (0, 1, 0), 6), mat, detail=True)
    mk.box(p, (x, y + 0.64, z), (0.26, 0.1, 0.26), "iron", rot=(0, 30, 0), detail=True)


def sack(mk, p, x, y, z, w=0.9, h=1.1):
    pts = ring((x, y - 0.01, z), w / 2, (0, 1, 0), 6, 0.0)
    pts += [(px * 1.0, py, pz) for px, py, pz in ring((x, y + h * 0.6, z), w / 2 * 1.08, (0, 1, 0), 6, 0.0)]
    pts += ring((x, y + h, z), w / 2 * 0.45, (0, 1, 0), 4)
    mk.hull(p, pts, "canvas", detail=True)


def cloth(mk, p, x, y, z, mats):
    for i, m in enumerate(mats):                                                       # pila de telas dobladas
        mk.box(p, (x + 0.03 * (i % 2), y + 0.095 + 0.19 * i, z), (1.0, 0.2, 0.9), m, rot=(0, 3 * (i - 1), 0),
               detail=True)


def build_shelves(mk):
    o = SX
    y4 = SHELF_Y[2] + 0.1                                                              # 4,3
    # izquierda: cortes por el estante de 4,3
    for name, ya, yb_ in (("frag01", 0.0, y4 + 0.02), ("frag03", y4 + 0.02, 8.0)):
        p = mk.part(f"Shelves_General_{name}", (o, 0, 0))
        shelf_structure(mk, p, o, -4.0, 0.075, ya, yb_)
    # derecha: grieta en zigzag por el fondo
    for name, keep in (("frag02", -1), ("frag04", 1)):
        p = mk.part(f"Shelves_General_{name}", (o, 0, 0))
        shelf_structure(mk, p, o, 0.075, 4.0, 0.0, 8.0)
        zig = [(o + x, y) for x, y in SHELF_ZIG]
        crack(mk, p, zig, keep, "xy", (0, 0, 0), 3.0,
              groove=(((0.0, -0.05) if keep < 0 else (0.0, 0.05)), [(o + 0.1, 0.5), (o + 3.84, 0.5), (o + 3.84, 7.79),
                                                                      (o + 0.1, 7.79)], (0, 0, 0.62), 0.12))
    f1, f2, f3, f4 = (f"Shelves_General_frag0{i}" for i in (1, 2, 3, 4))
    z = -0.15
    # abajo: bolsas y un cajón
    sack(mk, f1, o - 3.0, 0.5, z)
    sack(mk, f1, o - 1.9, 0.5, z + 0.05, 0.85, 1.0)
    bx(mk, f1, o - 1.2, o - 0.25, 0.495, 1.35, z - 0.4, z + 0.45, LIGHT, detail=True)
    sack(mk, f2, o + 0.9, 0.5, z)
    sack(mk, f2, o + 2.0, 0.5, z - 0.05, 0.95, 1.15)
    sack(mk, f2, o + 3.1, 0.5, z + 0.05, 0.8, 0.95)
    # latas de colores
    for ox_, f in ((-3.4, f1), (0.55, f2)):
        for i, mat in enumerate(("paint_red", "paint_teal", "paint_mustard", "paint_red", "paint_teal")):
            can(mk, f, o + ox_ + 0.45 * i, 2.4, z - 0.15 + 0.12 * (i % 2), mat)
        can(mk, f, o + ox_ + 0.68, 2.81, z - 0.05, "paint_mustard")
        can(mk, f, o + ox_ + 1.13, 2.81, z + 0.05, "paint_red")
    # frascos (en la derecha, lejos del zigzag que cruza este estante en x ~ 2,7)
    for x, mat, f in ((-3.2, "glass_amber", f1), (-2.4, "glass_green", f1), (-1.6, "glass_amber", f1),
                      (-0.75, "glass_green", f1), (0.65, "glass_amber", f2), (1.5, "glass_green", f2),
                      (3.4, "glass_amber", f4)):
        jar(mk, f, o + x, 4.3, z, mat)
    # telas dobladas arriba
    for x, mats, f in ((-3.0, ("cloth_blue", "cloth_red", "cloth_white"), f3), (-1.4, ("cloth_white", "cloth_blue"), f3),
                       (1.2, ("cloth_red", "cloth_brown", "cloth_blue"), f4), (2.8, ("cloth_brown", "cloth_white"), f4)):
        cloth(mk, f, o + x, 6.2, z, mats)


# ---------------------------------------------------------------- mostrador
WOOD_PROFILE = [(-0.85, 0.0), (-0.85, 0.35), (-0.95, 0.35), (-0.95, 3.35), (-1.0, 3.35), (-1.0, 3.5), (1.0, 3.5),
                (1.0, 3.35), (0.95, 3.35), (0.95, 0.0)]
CASE_PROFILE = [(-0.85, 0.0), (-0.85, 0.35), (-0.95, 0.35), (-0.95, 2.85), (0.95, 2.85), (0.95, 0.0)]
COUNTER_ZIG = [(2.3, 3.9), (1.9, 2.9), (2.3, 2.1), (1.85, 1.2), (2.2, 0.5), (1.9, -0.4)]


def build_counter(mk):
    o = CX
    for i in range(4):
        xa, xb = -4.0 + 2.0 * i, -2.0 + 2.0 * i
        p = mk.part(f"Counter_Store_frag{i + 1:02d}", (o, 0, 0))
        if i < 2:                                                                       # vitrina
            mk.prism(p, CASE_PROFILE, xb - xa, MID, plane="zy", center=(o + (xa + xb) / 2, 0, 0))
            bx(mk, p, o + xa + 0.004, o + xb - 0.004, 2.83, 2.86, -0.9, 0.85, "cloth_red")   # paño del fondo
            for x0, x1 in ((xa + 0.003, xa + 0.1), (xb - 0.1, xb - 0.003)):             # parantes
                bx(mk, p, o + x0, o + x1, 2.84, 3.45, -0.99, -0.88, DARK)
                bx(mk, p, o + x0, o + x1, 2.84, 3.45, 0.83, 0.94, DARK)
            bx(mk, p, o + xa, o + xb, 3.38, 3.5, -1.0, -0.88, DARK)                     # marcos de arriba
            bx(mk, p, o + xa, o + xb, 3.38, 3.5, 0.82, 0.95, DARK)
            bx(mk, p, o + xa + 0.09, o + xb - 0.09, 3.41, 3.47, -0.89, 0.83, "glass")   # vidrio de arriba
            bx(mk, p, o + xa + 0.09, o + xb - 0.09, 2.85, 3.39, -0.97, -0.92, "glass")  # vidrio del frente
            bx(mk, p, o + xa + 0.09, o + xb - 0.09, 2.85, 3.39, 0.86, 0.9, DARK)        # puertitas de atrás
            if i == 0:
                bx(mk, p, o - 3.97, o - 3.92, 2.85, 3.39, -0.88, 0.83, "glass")         # vidrio de la punta
            pz = -0.95
            for x0 in (xa + 0.22, xa + 1.11):
                raised(mk, p, o + x0, o + x0 + 0.67, 0.6, 2.6, pz, 0.06, DARK)
            # mercadería adentro
            if i == 0:
                bx(mk, p, o - 3.4, o - 2.9, 2.855, 3.05, -0.5, -0.15, "paint_red", detail=True)
                bx(mk, p, o - 2.75, o - 2.25, 2.855, 3.05, -0.55, -0.2, "paint_red", detail=True)
                mk.cyl(p, (o - 3.1, 2.9, 0.2), 0.16, 0.08, "brass", sides=8, detail=True)
            else:
                mk.cyl(p, (o - 1.4, 3.06, -0.3), 0.15, 0.42, "paint_teal", sides=6, detail=True)
                bx(mk, p, o - 0.9, o - 0.35, 2.855, 3.0, -0.6, -0.2, "paint_cream", detail=True)
        else:                                                                           # madera
            ea = xa - (0.8 if i == 3 else 0.0)
            eb = xb + (0.8 if i == 2 else 0.0)
            mk.prism(p, WOOD_PROFILE, eb - ea, MID, plane="zy", center=(o + (ea + eb) / 2, 0, 0))
            for x0 in (0.22, 1.11, 2.22, 3.11):
                if x0 + 0.67 > ea + 0.05 and x0 < eb - 0.05:
                    raised(mk, p, o + x0, o + x0 + 0.67, 0.6, 3.1, -0.95, 0.06, DARK)
            mk.paint(p, DARK, box=((o + (ea + eb) / 2, 3.43, 0), (eb - ea + 0.2, 0.2, 2.2)))   # tapa
            crack(mk, p, [(o + x, y) for x, y in COUNTER_ZIG], -1 if i == 2 else 1, "xy", (0, 0, 0), 3.0,
                  groove=(((-0.05, 0.0) if i == 2 else (0.05, 0.0)), [(o, 0.45), (o + 4, 0.45), (o + 4, 3.3), (o, 3.3)],
                          (0, 0, -1.1), 0.4))
        mk.paint(p, "wood_charred", box=((o + (xa + xb) / 2, 0.17, -0.85), (2.2, 0.36, 0.02)))
    # caja registradora (bronce, cartel en blanco) sobre frag03
    r = "Counter_Store_frag03"
    rx, rz = o + 1.0, 0.15
    mk.hull(r, [(rx + dx, 3.49, rz + dz) for dx in (-0.55, 0.55) for dz in (-0.45, 0.45)]
            + [(rx + dx, 4.35, rz + dz) for dx in (-0.5, 0.5) for dz in (0.05, 0.42)]
            + [(rx + dx, 3.95, rz - 0.42) for dx in (-0.5, 0.5)], "brass", detail=True)
    for k in range(3):                                                                  # filas de teclas
        t = 0.2 + 0.25 * k
        y, zz = 3.95 + (4.35 - 3.95) * t, rz - 0.42 + 0.47 * t
        mk.box(r, (rx, y + 0.01, zz - 0.005), (0.82, 0.05, 0.08), "coal", rot=(-40, 0, 0), detail=True)
    bx(mk, r, rx - 0.42, rx + 0.42, 4.3, 4.75, rz + 0.12, rz + 0.3, "brass", detail=True)   # cartel (en blanco)
    bx(mk, r, rx - 0.48, rx + 0.48, 3.5, 3.7, rz - 0.52, rz - 0.4, DARK, detail=True)     # cajón del dinero
    bx(mk, r, rx + 0.5, rx + 0.62, 3.85, 4.05, rz - 0.05, rz + 0.05, "iron")             # manija
    bx(mk, r, rx + 0.6, rx + 0.66, 3.75, 4.15, rz - 0.04, rz + 0.04, "iron", detail=True)
    # balanza sobre frag04
    s = "Counter_Store_frag04"
    sx_, sz_ = o + 3.0, 0.2
    bx(mk, s, sx_ - 0.4, sx_ + 0.4, 3.49, 3.64, sz_ - 0.3, sz_ + 0.3, "iron", detail=True)
    mk.cyl(s, (sx_ + 0.25, 3.95, sz_), 0.05, 0.64, "brass", sides=6, detail=True)
    bx(mk, s, sx_ - 0.45, sx_ + 0.5, 4.24, 4.31, sz_ - 0.04, sz_ + 0.04, "brass", detail=True)   # cruz
    mk.cyl(s, (sx_ - 0.1, 3.665, sz_), 0.3, 0.06, "brass", sides=8, top=1.25, detail=True)  # plato
    mk.cyl(s, (sx_ + 0.47, 4.18, sz_), 0.06, 0.12, "iron", sides=6, detail=True)        # pesa


# ---------------------------------------------------------------- armas (siluetas)
def gun_shapes(kind):
    """Cascos de un arma acostada: caño hacia +X, alma en y = 0, espesor en z. Devuelve [(puntos, material)]."""
    S = []

    def box(x0, x1, y0, y1, t, mat, z=0.0):
        S.append(([(x, y, z + w) for x in (x0, x1) for y in (y0, y1) for w in (-t / 2, t / 2)], mat))

    def poly(pts2, t, mat):
        S.append(([(x, y, w) for x, y in pts2 for w in (-t / 2, t / 2)], mat))

    def cylx(x0, x1, y, r, mat, z=0.0, n=6):
        S.append((ring((x0, y, z), r, (1, 0, 0), n) + ring((x1, y, z), r, (1, 0, 0), n), mat))

    if kind in ("lever", "carbine"):
        L = 1.6 if kind == "lever" else 1.4
        rec = "brass" if kind == "lever" else "iron"
        poly([(-L, 0.12), (-L, -0.44), (-L + 0.14, -0.44), (-0.9, -0.2), (-0.9, 0.08)], 0.16, "wood_mid")   # culata
        poly([(-0.95, -0.22), (-0.95, 0.07), (-0.53, 0.06), (-0.53, -0.1)], 0.13, "wood_mid")              # garganta
        box(-0.56, -0.12, -0.12, 0.07, 0.14, rec)                                                          # cajón
        cylx(-0.13, L, 0.0, 0.038, "gunmetal")                                                             # caño
        cylx(-0.13, L - 0.3, -0.075, 0.032, "gunmetal", n=4)                                               # tubo
        box(-0.12, 0.62, -0.115, -0.01, 0.12, "wood_mid")                                                  # guardamano
        box(0.6, 0.68, -0.12, 0.05, 0.1, "iron")                                                           # abrazadera
        box(-0.5, -0.38, -0.42, -0.11, 0.05, "iron")                                                       # palanca
        box(-0.78, -0.4, -0.46, -0.4, 0.044, "iron")
        S.append(([(x, y, w) for x, y in ((-0.8, -0.46), (-0.8, -0.38), (-0.6, -0.1), (-0.66, -0.12))
                   for w in (-0.025, 0.025)], "iron"))
        box(-0.6, -0.5, 0.06, 0.16, 0.05, "iron")                                                          # martillo
    elif kind == "double":
        poly([(-1.35, 0.1), (-1.35, -0.42), (-1.22, -0.42), (-0.75, -0.18), (-0.75, 0.07)], 0.17, "wood_mid")
        poly([(-0.8, -0.2), (-0.8, 0.06), (-0.48, 0.05), (-0.48, -0.08)], 0.15, "wood_mid")
        box(-0.5, -0.24, -0.11, 0.07, 0.17, "gunmetal")                                                    # báscula
        for z in (-0.048, 0.048):
            cylx(-0.25, 1.35, 0.0, 0.046, "gunmetal", z=z)                                                 # caños
        box(-0.23, 0.35, -0.12, -0.03, 0.13, "wood_mid")                                                   # guardamano
        for z in (-0.05, 0.05):
            box(-0.55, -0.47, 0.05, 0.15, 0.03, "steel_light", z=z)                                        # martillos
        S.append(([(x, y, w) for x, y in ((-0.6, -0.12), (-0.38, -0.12), (-0.45, -0.25), (-0.58, -0.24))
                   for w in (-0.025, 0.025)], "iron"))                                                     # guardamonte
    elif kind == "hunting":
        poly([(-1.85, 0.12), (-1.85, -0.44), (-1.7, -0.44), (-1.05, -0.17), (-1.05, 0.08)], 0.16, "wood_mid")
        poly([(-1.1, -0.19), (-1.1, 0.07), (-0.66, 0.06), (-0.66, -0.1)], 0.13, "wood_mid")
        box(-0.68, -0.2, -0.13, 0.07, 0.14, "iron")                                                        # cajón
        cylx(-0.21, 1.85, 0.0, 0.042, "gunmetal")                                                          # caño
        box(-0.2, 0.95, -0.12, -0.02, 0.13, "wood_mid")                                                    # guardamano largo
        cylx(-0.75, 1.3, 0.17, 0.045, "brass", n=6)                                                        # mira
        cylx(-0.85, -0.72, 0.17, 0.065, "brass", n=6)                                                      # ocular
        for x in (-0.45, 0.95):
            box(x - 0.04, x + 0.04, 0.03, 0.14, 0.05, "iron")                                              # monturas
        box(-0.55, -0.43, -0.4, -0.12, 0.05, "iron")                                                       # palanca
        box(-0.9, -0.45, -0.43, -0.37, 0.044, "iron")
    elif kind == "revolver":
        poly([(-0.62, -0.08), (-0.38, -0.08), (-0.42, -0.5), (-0.62, -0.5), (-0.7, -0.4)], 0.17, "wood_dark")  # cacha
        box(-0.42, 0.0, -0.12, 0.08, 0.15, "gunmetal")                                                     # armazón
        cylx(-0.3, 0.02, -0.02, 0.135, "gunmetal", n=8)                                                    # tambor
        cylx(0.0, 0.68, 0.03, 0.045, "gunmetal")                                                           # caño
        cylx(0.02, 0.5, -0.06, 0.03, "gunmetal", n=4)                                                      # varilla
        box(-0.52, -0.42, 0.04, 0.16, 0.05, "gunmetal")                                                    # martillo
        S.append(([(x, y, w) for x, y in ((-0.42, -0.1), (-0.2, -0.1), (-0.28, -0.26), (-0.4, -0.25))
                   for w in (-0.025, 0.025)], "gunmetal"))                                                 # guardamonte
    return S


GUN_BOTTOM = {"lever": (-0.243, -0.115), "carbine": (-0.267, -0.115), "double": (-0.308, -0.044),
              "hunting": (-0.17, -0.12)}           # fondo del arma bajo el alma en x = -1 y x = +0,6 (del perfil)


def build_guns(mk):
    o = GX
    rack = mk.part("GunDisplay_Wall", (o, 0, 0))
    bx(mk, rack, o - 4.0, o + 4.0, 2.5, 7.5, 0.6, 0.75, MID)                             # tablero
    for x0, x1, y0, y1, z0 in ((-4.005, 4.005, 7.32, 7.505, 0.54), (-4.005, 4.005, 2.495, 2.68, 0.54),
                               (-3.998, -3.82, 2.67, 7.33, 0.545), (3.82, 3.998, 2.67, 7.33, 0.545)):   # marco
        bx(mk, rack, o + x0, o + x1, y0, y1, z0, 0.62, DARK)
    bx(mk, rack, o - 3.95, o + 3.95, 2.62, 2.74, 0.15, 0.61, DARK)                      # repisa
    for k in range(-3, 4):                                                               # juntas de las tablas
        mk.slice(rack, (o + k - 0.03, 0, 0), (1, 0, 0))
        mk.slice(rack, (o + k + 0.03, 0, 0), (1, 0, 0))
        mk.paint(rack, DARK, box=((o + k, 5.0, 0.6), (0.07, 4.66, 0.02)))
    for x, mat, w in ((-3.3, "paint_red", 0.5), (-2.8, "paint_red", 0.45), (2.9, "paint_cream", 0.5),
                      (3.4, "paint_red", 0.4)):                                     # cajas de balas en la repisa
        bx(mk, rack, o + x - w / 2, o + x + w / 2, 2.735, 3.0, 0.2, 0.52, mat)
    zg = 0.3
    rows = (("Gun_1", "lever", 6.75), ("Gun_2", "double", 5.85), ("Gun_3", "hunting", 4.95), ("Gun_4", "carbine", 4.05))
    for name, kind, yb in rows:
        g = mk.part(name, (o, yb, zg))
        for pts, mat in gun_shapes(kind):
            mk.hull(g, [(o + x, yb + y, zg + z) for x, y, z in pts], mat)
        for px, dy in zip((-1.0, 0.6), GUN_BOTTOM[kind]):                                # clavijas a la altura justa
            top = yb + dy
            mk.cyl(rack, (o + px, top - 0.07, 0.35), 0.07, 0.52, DARK, axis="z", sides=6)
            bx(mk, rack, o + px - 0.05, o + px + 0.05, top - 0.12, top + 0.06, 0.085, 0.15, DARK)  # tope
    # revólveres colgados del guardamonte, caño para abajo, en una fila de ganchos
    R = Euler((0, 0, math.radians(-90)), "XYZ").to_matrix()
    for name, gx in (("Gun_5", -2.0), ("Gun_6", 2.0)):
        hook = Vector((o + gx, 3.75, zg))
        # el guardamonte (x ~ -0.3, y ~ -0.18 en el arma) cuelga del gancho
        anchor = R @ Vector((-0.3, -0.16, 0))
        c = hook - anchor
        g = mk.part(name, tuple(c))
        for pts, mat in gun_shapes("revolver"):
            mk.hull(g, [tuple(c + R @ Vector(pp)) for pp in pts], mat)
        mk.cyl(rack, (o + gx, 3.75, 0.4), 0.04, 0.42, "iron", axis="z", sides=4)          # gancho
        bx(mk, rack, o + gx - 0.03, o + gx + 0.03, 3.75, 3.86, 0.17, 0.23, "iron")


def build(mk):
    build_shelves(mk)
    build_counter(mk)
    build_guns(mk)

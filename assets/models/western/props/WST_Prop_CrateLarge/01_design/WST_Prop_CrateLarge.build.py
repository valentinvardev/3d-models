"""
Receta de WST_Prop_CrateLarge, el cajón grande de carga (prompt 020, Bloques A + C).

Brief
- Silueta a 40 studs: un bloque de 6 x 4 x 4 con marco oscuro en todas las aristas, una X en el frente y
  atrás, y dos flejes de hierro que lo abrazan a 1/4 y 3/4 del largo (pasan por el frente, la tapa y atrás).
  Es cobertura agachado: 4 de alto.
- Misma construcción que la caja chica (WST_Prop_Crate, Claude Design): paredes de 0,4 (tabla 0,25 +
  listón 0,15), tablas wood_light con juntas pintadas wood_dark de 0,06, marco wood_dark de 0,4 de ancho,
  diagonales wood_mid, placa crema en el frente.
- Caja hueca: un núcleo de 5,7 x 3,7 x 3,7 (tablas) y los marcos por fuera hasta 6 x 4 x 4. El frente y
  atrás llevan el marco hasta las esquinas verticales; los costados, hasta las de arriba y abajo; la tapa
  y el fondo quedan adentro de los costados (como la caja chica, sin huecos ni encimes).
- Fragmentos (8, origen común en el piso al centro): frag01 tapa izquierda, frag02 tapa derecha (cada mitad
  con su listón del medio), frag03 frente izquierdo, frag04 frente derecho (grieta en zigzag de 5 quiebres
  que corta tablas, marco y la X), frag05 atrás, frag06 izquierda, frag07 derecha, frag08 fondo (losa).
- Grieta: franja coal de 0,07 a cada lado (geometría coplanar, no tallada), así se lee a 40 studs.
- Flejes: cada tramo es de la pieza sobre la que apoya; el perfil escalonado sube por encima de los
  listones y baja a las tablas (sin luz por debajo). La X de las tablas pasa por encima del fleje.
- Desgaste: dos esquinas del marco astilladas a 45° (recorte 2D, la cara del corte pintada wood_light).
- Inferido: espesores (copiados de la caja chica), juntas en 0,8, ancho de los flejes 0,3 y 0,06 de
  espesor, el listón del medio de la tapa, la placa arriba del cruce de la X, dónde corre la grieta
  (esquiva la placa y cruza cada diagonal una vez), el color coal de la grieta.

Vueltas: 1) 18 bordes con giro inconsistente por pieza y z-fighting tapa/marco: cascos de la misma pieza
con vértices en el mismo lugar (esquinas del marco) que process_model suelda · 2) encimes de 0,003 y la X
y el fleje metidos en las tablas · 3) la grieta pasaba por el cruce de la X (diagonal y brazo compartían
vértices), las booleanas de las astillas dejaban caras degeneradas: recorte 2D · 4) fleje y X metidos
igual (caras de atrás coincidentes donde se cruzan): el fleje 0,01 · 5) la X recortada con la grieta
corrida 0,003 · 6) la grieta era una línea de < 0,01 que no se veía: franja coal; fondo de 60 a 12
triángulos (losa).

Revisión
- 1332 triángulos contra 400 de referencia (calidad primero): ocho fragmentos cerrados (cada uno con sus
  caras de contacto), los flejes escalonados (~290, el perfil que abraza los listones), la X partida en
  piezas convexas en frente y atrás (~200) y la franja de la grieta (~170). Por pieza, el máximo es 340.
- Medidas 6 x 4,06 x 4,12: los flejes sobresalen 0,06 por encima de la tapa, adelante y atrás (+1,5 % / +3 %).
- La franja clara de 0,05 entre el listón de abajo y la primera tabla es la losa del fondo (mismo color
  que las tablas): las paredes arrancan en 0,45 porque en 0,4 la franja de la grieta compartía vértices
  con la del listón.
"""

# ---- medidas (studs) ----
XO, XC, XI = 3.0, 2.85, 2.6        # media longitud: afuera (marco), núcleo (cara de las tablas), adentro
ZO, ZC, ZI = 2.0, 1.85, 1.6        # media profundidad
YB, YT = 0.45, 3.85                # paredes: abajo (sobre el fondo; no en 0,4 = arriba del listón: vértices iguales) y arriba
BW = 0.4                           # ancho de los listones del marco
BR = 0.12                          # cuánto sobresale la X de las tablas (menos que el marco: 0,15)
SW, ST = 0.3, 0.06                 # fleje: ancho y espesor
SX = (-1.5, 1.5)                   # flejes a 1/4 y 3/4 del largo
SEAMS = (1.2, 2.0, 2.8)            # juntas de las tablas en las paredes (alto)
LID_SEAMS = (-0.8, 0.0, 0.8)       # juntas de la tapa (profundidad)
SEAM = 0.06
E = 0.003                          # encime mínimo: dos cascos de una pieza nunca comparten un vértice (process_model
                                   # los suelda y deja bordes con 4 caras: giro inconsistente y z-fighting medidos)
EMB = 0.02                         # la X se mete en las tablas
EMS = 0.01                         # el fleje se mete menos: si no, su cara de atrás coincide con la de la X (medido)

# grieta del frente (x, y), de arriba abajo: esquiva la placa por la derecha y cruza cada diagonal una vez,
# lejos del cruce de la X (si pasa por el cruce, la diagonal y su brazo comparten vértices: medido)
CRACK = [(0.85, 4.3), (1.0, 3.3), (0.7, 2.6), (1.1, 2.0), (0.6, 1.3), (0.95, 0.7), (0.75, -0.3)]


# ---- geometría 2D: recorte de polígonos ----
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def area(poly):
    return 0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def _inter(p, q, a, b):
    d1 = _cross(a, b, p)
    d2 = _cross(a, b, q)
    t = d1 / (d1 - d2)
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def _clean(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= 1e-6:
        out.pop()
    changed = True
    while changed and len(out) >= 3:          # sin vértices alineados (aristas de largo cero al triangular)
        changed = False
        for i in range(len(out)):
            if abs(_cross(out[i - 1], out[i], out[(i + 1) % len(out)])) < 1e-7:
                out.pop(i)
                changed = True
                break
    return out


def clip(subject, clipper):
    """Sutherland-Hodgman: subject (convexo o no) recortado por clipper (convexo)."""
    if area(clipper) < 0:
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
    return _clean(out)


def half(poly, a, b):
    """Lo que queda a la izquierda de la recta a->b."""
    big = 50.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    lx, ly = -uy, ux
    p0 = (a[0] - ux * big, a[1] - uy * big)
    p1 = (a[0] + ux * big, a[1] + uy * big)
    return clip(poly, [p0, p1, (p1[0] + lx * big, p1[1] + ly * big), (p0[0] + lx * big, p0[1] + ly * big)])


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def strip(a, b, w):
    """Rectángulo largo de a a b, de ancho w, estirado 1 stud en cada punta (después se recorta)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    lx, ly = -uy * w / 2, ux * w / 2
    a2, b2 = (a[0] - ux, a[1] - uy), (b[0] + ux, b[1] + uy)
    return [(a2[0] - lx, a2[1] - ly), (b2[0] - lx, b2[1] - ly), (b2[0] + lx, b2[1] + ly), (a2[0] + lx, a2[1] + ly)]


def x_brace(inner, w):
    """La X como piezas convexas que no se enciman: la diagonal 1 entera y la 2 en dos brazos."""
    (x0, y0), (x1, y1) = inner[0], inner[2]
    a1, b1 = (x0, y0), (x1, y1)
    a2, b2 = (x0, y1), (x1, y0)
    d1 = clip(strip(a1, b1, w), inner)
    d2 = clip(strip(a2, b2, w), inner)
    dx, dy = b1[0] - a1[0], b1[1] - a1[1]
    n = (dx * dx + dy * dy) ** 0.5
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    k = 1 + 2 * E / w                                                       # los brazos quedan a E de la diagonal 1
    up = half(d2, (a1[0] + ox * k, a1[1] + oy * k), (b1[0] + ox * k, b1[1] + oy * k))   # brazo de arriba a la izquierda
    down = half(d2, (b1[0] - ox * k, b1[1] - oy * k), (a1[0] - ox * k, a1[1] - oy * k)) # brazo de abajo a la derecha
    return [p for p in (d1, up, down) if len(p) >= 3]


CB = 0.07                          # ancho de la franja de la grieta en cada mitad (coal: se lee a 40 studs)


def shifted(d):
    return [(x + d, y) for x, y in CRACK]


def side_region(sign, d):
    """Lo que queda del lado `sign` (-1 izquierda, +1 derecha) de la grieta corrida d en x."""
    c = shifted(d)
    if sign < 0:
        return [(-4.0, CRACK[-1][1]), (-4.0, CRACK[0][1])] + c
    return [(4.0, CRACK[0][1]), (4.0, CRACK[-1][1])] + c[::-1]


def band(d0, d1):
    """Franja entre la grieta corrida d0 y la corrida d1."""
    return shifted(d0) + shifted(d1)[::-1]


def crack_x(y):
    for (xa, ya), (xb, yb) in zip(CRACK, CRACK[1:]):
        if yb <= y <= ya:
            return xa + (xb - xa) * (ya - y) / (ya - yb)
    raise ValueError(y)


def split_layer(poly, mat, sign):
    """Una capa del frente partida por la grieta: (lo de esta mitad, la franja oscura de la grieta).
    Tablas y marco: franja de 0 a CB, resto desde CB+E. La X (se mete EMB en las tablas): todo corrido E
    más, para que sus caras de la grieta no coincidan con las de las tablas (z-fighting medido)."""
    k = 1 if mat == "wood_mid" else 0
    main = clip(side_region(sign, sign * (CB + (1 + k) * E)), poly)
    strip_ = clip(band(sign * k * E, sign * (CB + k * E)), poly)
    return main, strip_


CHIP = 0.34                         # esquinas astilladas del marco: catetos del corte a 45°


def face_layers(front):
    """Capas de una cara grande (frente o atrás) como polígonos (x, y) con su z (centro, espesor).
    Frente: esquina de arriba a la izquierda astillada; atrás: la de abajo en +X."""
    s = -1 if front else 1
    layers = []
    layers.append((rect(-XC, XC, YB, YT), "wood_light", s * (ZC + ZI) / 2, ZC - ZI))                 # tablas
    zf, df = s * (ZO + ZC) / 2, ZO - ZC
    top, bottom = rect(-XO, XO, 4.0 - BW, 4.0), rect(-XO, XO, 0.0, BW)
    if front:
        top = half(top, (-XO + CHIP, 4.0), (-XO, 4.0 - CHIP))
    else:
        bottom = half(bottom, (XO - CHIP, 0.0), (XO, CHIP))
    for poly in (top, bottom,
                 rect(-XO + E, -XO + BW, BW, 4.0 - BW), rect(XO - BW, XO - E, BW, 4.0 - BW)):
        layers.append((poly, "wood_dark", zf, df))                                                   # marco
    for poly in x_brace(rect(-XO + BW + E, XO - BW - E, BW + E, 4.0 - BW - E), 0.4):
        layers.append((poly, "wood_mid", s * (ZC + BR / 2 - EMB / 2), BR + EMB))                                     # X
    return layers


def strap_profile(front):
    """Perfil (z, y) del fleje de una cara: sube por el listón de abajo, baja a las tablas, sube por el
    de arriba y pasa por encima de la arista hasta donde empieza la tapa (z = -ZC)."""
    o = ZO + ST
    pts = [(-ZO, 0.0), (-ZO, BW), (-ZC + EMS, BW), (-ZC + EMS, 4.0 - BW), (-ZO, 4.0 - BW), (-ZO, 4.0), (-ZC, 4.0),
           (-ZC, 4.0 + ST), (-o, 4.0 + ST), (-o, 4.0 - BW - ST), (-ZC - ST, 4.0 - BW - ST),
           (-ZC - ST, BW + ST), (-o, BW + ST), (-o, 0.0)]
    return pts if front else [(-z, y) for z, y in pts]


def lid_strap_profile():
    """Perfil (z, y) del fleje sobre la tapa: listón del frente, baja a las tablas, listón de atrás."""
    t, p = 4.0, YT                                       # arriba de los listones / arriba de las tablas
    zb0, zb1 = -ZC + BW, ZC - BW
    return [(-ZC, t), (zb0, t), (zb0, p - EMS), (zb1, p - EMS), (zb1, t), (ZC, t),
            (ZC, t + ST), (zb1 - ST, t + ST), (zb1 - ST, p + ST), (zb0 + ST, p + ST), (zb0 + ST, t + ST), (-ZC, t + ST)]


def seams(mk, part, axis, values, box_c, box_s):
    """Juntas pintadas de 0,06: dos cortes por junta y se pintan las caras de la banda.
    box_c/box_s limitan la pintura a la cara de las tablas (no a marco, X ni fleje)."""
    for v in values:
        for k in (-SEAM / 2, SEAM / 2):
            pt = [0.0, 0.0, 0.0]
            nm = [0.0, 0.0, 0.0]
            pt[axis], nm[axis] = v + k, 1.0
            mk.slice(part, tuple(pt), tuple(nm))
        c, s = list(box_c), list(box_s)
        c[axis], s[axis] = v, SEAM + 0.01
        mk.paint(part, "wood_dark", box=(tuple(c), tuple(s)))


def build(mk):
    # ---------------- frente: dos mitades partidas por la grieta ----------------
    for name, sign in (("frag03", -1), ("frag04", 1)):
        p = mk.part(name, (0, 0, 0))
        for poly, mat, zc, depth in face_layers(front=True):
            main, crack = split_layer(poly, mat, sign)
            if len(main) >= 3 and abs(area(main)) > 0.02:
                mk.prism(p, main, depth, mat, plane="xy", center=(0, 0, zc))
            if len(crack) >= 3 and abs(area(crack)) > 0.002:
                mk.prism(p, crack, depth, "coal", plane="xy", center=(0, 0, zc))
        sx = SX[0] if name == "frag03" else SX[1]
        mk.prism(p, strap_profile(front=True), SW, "iron", plane="zy", center=(sx, 0, 0))
        if name == "frag03":
            mk.box(p, (-0.1, 3.2, -ZC - 0.025), (1.3, 0.55, 0.05), "paint_cream")                    # placa
            mk.paint(p, "wood_light", ball=((-XO + CHIP / 2, 4.0 - CHIP / 2, -(ZO + ZC) / 2), 0.05))  # astilla: madera clara
        for v in SEAMS:                                      # juntas, sin pisar la franja de la grieta
            for k in (-SEAM / 2, SEAM / 2):
                mk.slice(p, (0, v + k, 0), (0, 1, 0))
            cx = crack_x(v) - sign * 0.1
            x0, x1 = (cx, 3.5) if sign > 0 else (-3.5, cx)
            mk.paint(p, "wood_dark", box=(((x0 + x1) / 2, v, -ZC), (x1 - x0, SEAM + 0.01, 0.01)))

    # ---------------- atrás: una pieza ----------------
    back = mk.part("frag05", (0, 0, 0))
    for poly, mat, zc, depth in face_layers(front=False):
        mk.prism(back, poly, depth, mat, plane="xy", center=(0, 0, zc))
    for sx in SX:
        mk.prism(back, strap_profile(front=False), SW, "iron", plane="zy", center=(sx, 0, 0))
    mk.paint(back, "wood_light", ball=((XO - CHIP / 2, CHIP / 2, (ZO + ZC) / 2), 0.05))              # astilla: madera clara
    seams(mk, back, 1, SEAMS, (0, 0, ZC), (8.0, 0, 0.01))

    # ---------------- costados ----------------
    for name, s in (("frag06", -1), ("frag07", 1)):
        p = mk.part(name, (0, 0, 0))
        mk.box(p, (s * (XC + XI) / 2, (YB + YT) / 2, 0), (XC - XI, YT - YB, 2 * ZI), "wood_light")       # tablas
        xf, df = s * (XO + XC) / 2, XO - XC
        mk.box(p, (xf, 4.0 - BW / 2, 0), (df, BW, 2 * ZC), "wood_dark")                                # marco
        mk.box(p, (xf, BW / 2, 0), (df, BW, 2 * ZC), "wood_dark")
        for zs in (-1, 1):
            mk.box(p, (xf, 2.0, zs * (ZC - BW / 2 - E / 2)), (df, 4.0 - 2 * BW, BW - E), "wood_dark")
        seams(mk, p, 1, SEAMS, (s * XC, 0, 0), (0.01, 0, 8.0))

    # ---------------- tapa: dos mitades, cada una con su listón del medio ----------------
    for name, s in (("frag01", -1), ("frag02", 1)):
        p = mk.part(name, (0, 0, 0))
        x0, x1 = sorted((s * E, s * XI))                     # a E del medio: los cortes de las juntas no comparten vértices con el listón
        mk.box(p, ((x0 + x1) / 2, YT - (ZC - ZI) / 2, 0), (x1 - x0, ZC - ZI, 2 * ZI), "wood_light")      # tablas
        bx0, bx1 = sorted((0.0, s * XC))
        yb, hb = (YT + 4.0) / 2, 4.0 - YT
        for zs in (-1, 1):
            mk.box(p, ((bx0 + bx1) / 2, yb, zs * (ZC - BW / 2)), (bx1 - bx0, hb, BW), "wood_dark")      # frente y atrás
        mk.box(p, (s * (XC - BW / 2), yb, 0), (BW, hb, 2 * (ZC - BW - E)), "wood_dark")                    # punta
        mk.box(p, (s * 0.15, yb, 0), (0.3, hb, 2 * (ZC - BW - E)), "wood_dark")                            # medio
        mk.prism(p, lid_strap_profile(), SW, "iron", plane="zy", center=(s * 1.5, 0, 0))
        seams(mk, p, 2, LID_SEAMS, (s * XI / 2, YT, 0), (XI + 0.02, 0.01, 0))

    # ---------------- fondo: una losa (no se ve; los marcos de las caras la tapan) ----------------
    bot = mk.part("frag08", (0, 0, 0))
    mk.box(bot, (0, YB / 2, 0), (2 * XC, YB, 2 * ZC), "wood_light")

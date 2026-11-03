"""
Receta de WST_RM_Slaughterhouse, el matadero del rancho (prompt 092, Bloques A + B). De acá sale el
Carnicero arrastrando un gancho.

Brief
- Silueta a 40 studs: galpón chico de tabla y tapajuntas con el hastial al frente, portón doble ancho y
  oscuro, cartel liso sobre el portón y la base de las paredes manchada de oscuro (salpicado de barro y
  sangre vieja, borde ondulado).
- Medidas: 16 (X) x 12 (Z), paredes de 10 (0,6 de espesor; caras de afuera en x = ±8 y z = ±6), techo a dos
  aguas con la cumbrera a lo largo de Z (hastial al frente): abajo del techo de 10 en el alero a 15 en la
  cumbrera (32°), aleros de 0,8. Portón: hueco 6 x 8 (x ±3), dos hojas de 2,97 x 7,8, bisagras en los
  cantos de afuera.
- Adentro: piso de piedra (losa de 0,15) con canaleta de desagüe bajo el riel; riel de hierro a lo largo
  de Z colgado de dos tirantes; cuatro ganchos en carritos (Hooks), dos con medias reses envueltas en
  lona y atadas; tajo de madera con una cuchilla clavada.
- Piezas (convexas, para la colisión de casco): WallFront_L, WallFront_R, WallFront_Top (el hastial y el
  dintel: el portón queda libre), WallBack, WallL, WallR, RoofL, RoofR, Frame (tirantes, cabios, cumbrera,
  riel), Floor, Block, Sign, Hooks, DoorL, DoorR.
- Inferido: hastial al frente, tabla y tapajuntas como el granero y el establo (familia del rancho),
  piedra en el piso, manchas de sangre seca solo en la canaleta, cartel de lona clara con marco oscuro
  (cara lisa para el decal), cruz oscura y bisagras en las hojas, una tabla rota abajo en la hoja derecha.

Vueltas: 1) pasa a la primera (2112); las medias reses parecían capullos (3,1 x 1,1) y las hojas con dos Z
se leían "ZZ" · 2) reses de 4 x 1,6 (cuarto trasero arriba) con dos ataduras; una Z por hoja: juntas
forman la V del portón.

Revisión
- 2072 triángulos contra 2500. Paredes ~900 (tabla y tapajuntas + la mancha ondulada tallada 0,02), techo
  ~170, adentro ~600 (cerchas, riel, 4 carritos con gancho, 2 reses, tajo, piso con canaleta).
- Medidas: 17,89 x 15,67 x 13,6 (paredes 16 x 12 x 10 exactas; suman aleros de 0,8 y el techo sobre la
  cumbrera de 15). Portón: hueco 6 x 8, hojas de 2,97 x 7,79 con el origen al pie del canto de afuera.
- 6 materiales: wood_mid, wood_dark, iron, canvas (lona de las reses y cara del cartel), stone_grey (piso),
  blood_dry (solo el fondo de la canaleta: sin gore).
- Piezas: además de DoorL, DoorR y Hooks (las del prompt), el edificio está partido en piezas convexas
  (WallFront_L/R/Top, WallBack, WallL/R, RoofL/R, Frame, Floor, Block, Sign) para que la colisión de casco
  no tape el portón ni el interior.
- Dudoso: Hooks incluye las reses: su casco ocupa el pasillo del medio entre 3 y 8,7 de alto; conviene
  importarlo sin colisión (CanCollide false) o con caja. El riel quedó en Frame.
"""

import math

BARE, DARK, IRON, CANVAS, STONE, BLOOD = "wood_mid", "wood_dark", "iron", "canvas", "stone_grey", "blood_dry"
RED = BARE                  # la pared de tabla pinta la cara de afuera: acá es madera sin pintar
CREAM = DARK
T = 0.6
B = 1.5                     # tabla (las juntas caen en los bordes del portón, x ±3)
BW, BP = 0.24, 0.12
GAP = 0.05
MAX_SHARE = 1.0             # prop estático: sin tope de fragmentos
ROOF_T, STEP = 0.4, 0.1
WH = 10.0                   # alto de pared
RISE = 5.0                  # cumbrera (abajo del techo) a 15
DW, DH = 3.0, 8.0           # medio ancho y alto del portón


def roof_u(x):
    return WH + (8.0 - abs(x)) * RISE / 8.0


# ---------------------------------------------------------------- geometría 2D
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def clean(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            if abs(_cross(out[i - 1], out[i], out[(i + 1) % len(out)])) < 1e-9:
                out.pop(i)
                changed = True
                break
    return out


def area(poly):
    return abs(0.5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly))))


def v_add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)


def v_unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    return (dx / n, dy / n)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def clip(subject, clipper):
    """Sutherland-Hodgman: subject recortado por clipper (convexo)."""
    sa = 0.5 * sum(clipper[i - 1][0] * clipper[i][1] - clipper[i][0] * clipper[i - 1][1] for i in range(len(clipper)))
    if sa < 0:
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
                    out.append(_seg_line(p, q, a, b))
                out.append(q)
            elif pin:
                out.append(_seg_line(p, q, a, b))
        if not out:
            return []
    return clean(out)


def _seg_line(p, q, a, b):
    d1, d2 = _cross(a, b, p), _cross(a, b, q)
    t = d1 / (d1 - d2)
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def strip2d(a, b, w, ext=1.0):
    """Rectángulo de a a b de ancho w, estirado ext en cada punta."""
    d = v_unit(a, b)
    nx, ny = -d[1] * w / 2, d[0] * w / 2
    a2, b2 = v_add(a, d, -ext), v_add(b, d, ext)
    return [(a2[0] - nx, a2[1] - ny), (b2[0] - nx, b2[1] - ny), (b2[0] + nx, b2[1] + ny), (a2[0] + nx, a2[1] + ny)]


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def intersect(p, d, q, e):
    """Intersección de las rectas p + t d y q + s e."""
    den = d[0] * e[1] - d[1] * e[0]
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)


# ---------------------------------------------------------------- pared de tabla y tapajuntas
GROUND, TOP = "ground", "top"


def y_at(poly, u, top=None):
    """y de un borde de fragmento en u: polilínea [(u, y)...] ordenada en u, GROUND (0) o TOP (techo)."""
    if poly == GROUND:
        return 0.0
    if poly == TOP:
        return top(u)
    for (ua, ya), (ub, yb) in zip(poly, poly[1:]):
        if ub - ua > 1e-9 and ua - 1e-9 <= u <= ub + 1e-9:
            return ya + (yb - ya) * (u - ua) / (ub - ua)
    raise ValueError(f"u={u} fuera de la polilínea {poly[0][0]}..{poly[-1][0]}")


def notch(poly, u0, u1, y):
    """La polilínea baja (o sube) a y entre u0 y u1: el borde de un hueco que la grieta atraviesa."""
    a, b = y_at(poly, u0), y_at(poly, u1)
    return ([p for p in poly if p[0] < u0 - 1e-9] + [(u0, a), (u0, y), (u1, y), (u1, b)]
            + [p for p in poly if p[0] > u1 + 1e-9])


def P3(plane, u, y, w):
    return (w, y, u) if plane == "zy" else (u, y, w)


def S3(plane, su, sy, sw):
    return (sw, sy, su) if plane == "zy" else (su, sy, sw)


class BoardWall:
    """Pared de tablas verticales. plane "zy": paredes de costado (u = z, espesor en x); "xy": hastiales
    (u = x, espesor en z). w_out: plano de la cara de afuera; sgn: hacia dónde es afuera. joints: juntas
    de las tablas (donde van los tapajuntas). frags: {nombre: (u0, u1, borde de abajo, borde de arriba)};
    los bordes son polilíneas (grietas en zigzag de 3-5 quiebres, con los huecos como muescas), GROUND o TOP."""

    def __init__(self, mk, prefix, plane, w_out, sgn, joints, frags, top, breaks=()):
        self.mk, self.prefix, self.plane, self.w_out, self.sgn = mk, prefix, plane, w_out, sgn
        self.j, self.frags, self.top, self.breaks = joints, frags, top, breaks
        self.parts = {}
        self._check()

    def yb(self, poly, u):
        return y_at(poly, u, self.top)

    def outline(self, f):
        u0, u1, bot, tp = f
        pts = [(u0, self.yb(bot, u0))]
        if isinstance(bot, list):
            pts += [p for p in bot if u0 + 1e-9 < p[0] < u1 - 1e-9]
        pts.append((u1, self.yb(bot, u1)))
        pts.append((u1, self.yb(tp, u1)))
        if tp == TOP:
            pts += [(u, self.top(u)) for u in sorted(self.breaks, reverse=True) if u0 < u < u1]
        elif isinstance(tp, list):
            pts += [p for p in reversed(tp) if u0 + 1e-9 < p[0] < u1 - 1e-9]
        pts.append((u0, self.yb(tp, u0)))
        return clean(pts)

    def owner(self, u, y):
        for name, (u0, u1, bot, tp) in self.frags.items():
            if u0 < u < u1 and self.yb(bot, u) < y < self.yb(tp, u):
                return name
        return None

    def _check(self):
        areas = {n: area(self.outline(f)) for n, f in self.frags.items()}
        total = sum(areas.values())
        for n, (u0, u1, bot, tp) in self.frags.items():
            for i in range(21):
                u = u0 + (u1 - u0) * (0.02 + 0.96 * i / 20)
                assert self.yb(tp, u) - self.yb(bot, u) >= 0.4, f"{self.prefix} {n}: angosto en u={u:.2f}"
            assert areas[n] / total <= MAX_SHARE, f"{self.prefix} {n}: {areas[n] / total:.0%} del área"
        u_lo, u_hi = min(f[0] for f in self.frags.values()), max(f[1] for f in self.frags.values())
        for i in range(60):
            u = u_lo + (u_hi - u_lo) * (i + 0.5) / 60
            for k in range(60):
                y = 25.0 * (k + 0.5) / 60
                hits = [n for n, (u0, u1, bot, tp) in self.frags.items()
                        if u0 < u < u1 and self.yb(bot, u) < y < self.yb(tp, u)]
                assert len(hits) <= 1, f"{self.prefix}: se pisan {hits} en ({u:.2f}, {y:.2f})"
        self.share = {n: a / total for n, a in areas.items()}

    def p(self, u, y, w_off):
        """Punto a w_off de la cara de afuera (positivo = hacia afuera)."""
        return P3(self.plane, u, y, self.w_out + self.sgn * w_off)

    def box(self, part, u0, u1, y0, y1, w0, w1, mat, detail=True):
        """Caja de u0..u1, y0..y1, de w0 a w1 medidos desde la cara de afuera (positivo = afuera)."""
        c = self.p((u0 + u1) / 2, (y0 + y1) / 2, (w0 + w1) / 2)
        self.mk.box(part, c, S3(self.plane, u1 - u0, y1 - y0, abs(w1 - w0)), mat, detail=detail)

    def build(self):
        mk = self.mk
        for name, f in self.frags.items():
            part = mk.part(f"{self.prefix}_{name}" if name else self.prefix, (0, 0, 0))
            self.parts[name] = part
            wc = self.w_out - self.sgn * T / 2
            mk.prism(part, self.outline(f), T, BARE, plane=self.plane, center=P3(self.plane, 0, 0, wc))
            mk.paint(part, RED, box=(self.p(0, 15, 0), S3(self.plane, 80, 40, 0.02)))
        self.battens()

    def segments(self, us, y_lo, y_hi):
        """Tramos (y0, y1, dueños en cada u de us) entre y_lo e y_hi, cortados donde cambia algún dueño."""
        probe = list(us) + [sum(us) / len(us)]
        ys = {y_lo, y_hi}
        for (u0, u1, bot, tp) in self.frags.values():
            for u in probe:
                if u0 - 1e-6 <= u <= u1 + 1e-6:
                    uu = min(max(u, u0), u1)
                    ys.add(self.yb(bot, uu))
                    ys.add(self.yb(tp, uu))
        ys = sorted(y for y in ys if y_lo <= y <= y_hi)
        out = []
        for a, b in zip(ys, ys[1:]):
            if b - a < 1e-6:
                continue
            m = (a + b) / 2
            own = tuple(self.owner(u, m) for u in us)
            if any(o is None for o in own):
                continue
            if out and out[-1][2] == own and abs(out[-1][1] - a) < 1e-6:
                out[-1] = (out[-1][0], b, own)
            else:
                out.append((a, b, own))
        return out

    def battens(self):
        for u in self.j[1:-1]:
            top = min(self.top(u - BW / 2), self.top(u + BW / 2)) - 0.08
            for a, b, (ol, orr) in self.segments([u - 0.13, u + 0.13], 0.0, top):
                a2 = 0.02 if a < 0.01 else a + GAP
                b2 = top if b >= top - 1e-6 else b - GAP
                if b2 - a2 <= 0.25:
                    continue
                if ol == orr:
                    self.box(self.parts[ol], u - BW / 2, u + BW / 2, a2, b2, -0.01, BP, DARK)
                else:                    # borde vertical de fragmento: medio tapajuntas para cada uno
                    self.box(self.parts[ol], u - BW / 2, u, a2, b2, -0.01, BP, DARK)
                    self.box(self.parts[orr], u, u + BW / 2, a2, b2, -0.01, BP, DARK)

    def casing(self, u0, u1, y0, y1, wd=0.32, proud=0.15):
        """Marco crema alrededor de un hueco. Cada tipo de pieza se mete distinto en la pared (sus caras de
        atrás nunca son coplanares); las jambas se parten donde la grieta las cruza; dintel y alféizar
        entran 0,04 en el hueco (si no, su cara queda coplanar con la del hueco)."""
        for a0, a1 in ((u0 - wd, u0 + 0.02), (u1 - 0.02, u1 + wd)):
            for a, b, (o,) in self.segments([(a0 + a1) / 2], y0 - 0.02, y1 + 0.02):
                ya = a if a <= y0 else a + GAP
                yb = b if b >= y1 else b - GAP
                self.box(self.parts[o], a0, a1, ya, yb, -0.025, proud - 0.02, CREAM)
        um = (u0 + u1) / 2
        self.box(self.parts[self.owner(um, y1 + 0.15)], u0 - wd - 0.1, u1 + wd + 0.1, y1 - 0.04, y1 + wd, -0.02,
                 proud, CREAM)
        if y0 > 0.1:
            self.box(self.parts[self.owner(um, y0 - 0.15)], u0 - wd - 0.06, u1 + wd + 0.06, y0 - wd, y0 + 0.04,
                     -0.03, proud + 0.04, CREAM)

    def hole(self, uc, y0, y1, jag=()):
        """Tabla que falta (o rota) entre dos tapajuntas: se talla el hueco (se ve adentro)."""
        u0, u1 = uc - B / 2 + 0.13, uc + B / 2 - 0.13
        part = self.parts[self.owner(uc, max(0.3, (y0 + y1) / 2))]
        prof = [(u0, y0), (u1, y0), (u1, y1)] + [(u1 - (u1 - u0) * f, y1 + d) for f, d in jag] + [(u0, y1)]
        w0 = self.w_out - self.sgn * T / 2
        self.mk.carve(part, DARK, prism=dict(profile=prof, depth=T + 0.4, plane=self.plane,
                                             center=P3(self.plane, 0, 0, w0)))

    def chip(self, uc, h, seed=0):
        """Pintura saltada abajo de una tabla (entre tapajuntas): rebaje de 0,03 de borde dentado que
        muestra la madera (wood_mid)."""
        u0, u1 = uc - B / 2 + 0.16, uc + B / 2 - 0.16
        part = self.parts[self.owner(uc, 0.3)]
        hs = [0.0, 0.22, -0.12, 0.3, -0.05, 0.18, -0.2, 0.1]
        n = 5
        top = [(u1 - (u1 - u0) * (i + 0.5) / n, h + hs[(i + seed) % len(hs)]) for i in range(n)]
        prof = [(u0, -0.2), (u1, -0.2), (u1, h - 0.1)] + top + [(u0, h + 0.05)]
        self.mk.carve(part, BARE, prism=dict(profile=prof, depth=0.06, plane=self.plane,
                                             center=P3(self.plane, 0, 0, self.w_out)))


# ---------------------------------------------------------------- paredes
def stain(wall, part_name, u0, u1, seed=0):
    """Mancha oscura al pie: rebaje de 0,02 con borde de arriba ondulado (barro y sangre vieja)."""
    hs = [1.1, 1.35, 0.95, 1.5, 1.2, 0.9, 1.4, 1.05, 1.3, 1.0]
    n = max(3, int((u1 - u0) / 1.1))
    top = [(u1 - (u1 - u0) * (i + 0.5) / n, hs[(i + seed) % len(hs)]) for i in range(n)]
    prof = [(u0 - 0.5, -0.3), (u1 + 0.5, -0.3), (u1 + 0.5, 1.15)] + top + [(u0 - 0.5, 1.15)]
    wall.mk.carve(wall.parts[part_name], DARK, prism=dict(profile=prof, depth=0.04, plane=wall.plane,
                                                          center=P3(wall.plane, 0, 0, wall.w_out)))


def walls(mk):
    jf = [-7.4] + [-7.5 + k * B for k in range(1, 10)] + [7.4]          # juntas del frente y de atrás
    js = [-6.0 + k * B for k in range(9)]                               # juntas de los costados
    top_poly = [(-7.4, WH), (-DW, WH), (-DW, DH), (DW, DH), (DW, WH), (7.4, WH)]
    front = BoardWall(mk, "WallFront", "xy", -6.0, -1, jf, {
        "L": (-7.4, -DW, GROUND, [(-7.4, WH), (-DW, WH)]),
        "R": (DW, 7.4, GROUND, [(DW, WH), (7.4, WH)]),
        "Top": (-7.4, 7.4, top_poly, TOP)}, top=roof_u, breaks=(0.0,))
    front.build()
    stain(front, "L", -7.4, -DW, 0)
    stain(front, "R", DW, 7.4, 3)
    back = BoardWall(mk, "WallBack", "xy", 6.0, 1, jf, {"": (-7.4, 7.4, GROUND, TOP)}, top=roof_u,
                     breaks=(0.0,))
    back.build()
    stain(back, "", -7.4, 7.4, 5)
    sides = []
    for side, s in (("L", -1), ("R", 1)):
        w = BoardWall(mk, f"Wall{side}", "zy", s * 8.0, s, js, {"": (-6.0, 6.0, GROUND, [(-6.0, WH), (6.0, WH)])},
                      top=lambda u: WH)
        w.build()
        stain(w, "", -6.0, 6.0, 2 if s < 0 else 7)
        sides.append(w)
        # esquineros oscuros: de costado y de frente/atrás (siguen el techo)
        part = w.parts[""]
        for zs in (-1, 1):
            zc = 6.0 * zs
            u0, u1 = sorted((zc + zs * 0.1, zc - zs * 0.8))
            w.box(part, u0, u1, 0.02, WH - 0.05, -0.015, 0.15, DARK)
            xa, xb = s * 8.05, s * 7.25
            pts = []
            for x in (xa, xb):
                for z in (zc + zs * 0.12, zc - zs * 0.01):
                    pts += [(x, 0.04, z), (x, roof_u(x) - 0.05, z)]
            mk.hull(part, pts, DARK, detail=True)
    # los nombres de las piezas de una sola parte salen "WallBack_": se renombran al final
    return front, back, sides


# ---------------------------------------------------------------- techo
def roof(mk):
    E = (8.0, WH)
    Pk = (0.0, WH + RISE)
    d = v_unit(E, Pk)
    n = (d[1], -d[0])
    e_ext = v_add(E, d, -0.8)
    o_p = intersect(v_add(E, n, ROOF_T), d, (0.0, 0.0), (0.0, 1.0))
    base = v_add(e_ext, n, ROOF_T)
    L = v_dot((o_p[0] - base[0], o_p[1] - base[1]), d)
    nr = max(1, round(L / 1.35))
    pts, rows = [], []
    for i in range(nr):
        a = v_add(v_add(base, d, L * i / nr), n, STEP)
        b = v_add(base, d, L * (i + 1) / nr)
        pts += [a, b]
        rows.append((a, b))
    prof = clean([e_ext, Pk] + pts[::-1])
    z0, z1 = -6.8, 6.8
    for side, s in (("L", -1), ("R", 1)):
        part = mk.part(f"Roof{side}", (0, 0, 0))
        pr = [(s * x, y) for x, y in prof]
        mk.prism(part, pr if s > 0 else pr[::-1], z1 - z0, BARE, plane="xy", center=(0, 0, 0))
        for i, (a, b) in enumerate(rows):
            c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            mk.paint(part, DARK, box=((s * c[0], c[1], 0), (0.3, 0.3, z1 - z0 + 0.5)))
            if i > 0:
                lip = rows[i - 1][1]
                c2 = ((a[0] + lip[0]) / 2, (a[1] + lip[1]) / 2)
                mk.paint(part, IRON, box=((s * c2[0], c2[1], 0), (0.06, 0.06, z1 - z0 + 0.5)))
        q = v_add(o_p, d, -0.7)
        cap = [(0.0, o_p[1] - 0.02), (0.0, o_p[1] + 0.2), v_add(q, n, 0.16), v_add(q, n, -0.02)]
        mk.hull(part, [(s * x, y, z) for x, y in cap for z in (z0 + 0.005, z1 - 0.005)], DARK, detail=True)
    return d, n


# ---------------------------------------------------------------- estructura y riel
def beam_xy(mk, part, z, a, b, w, h, mat=DARK):
    d = v_unit(a, b)
    nrm = (-d[1], d[0])
    pts = []
    for p in (a, b):
        for k in (-0.5, 0.5):
            q = v_add(p, nrm, k * h)
            for dz in (-w / 2, w / 2):
                pts.append((q[0], q[1], z + dz))
    mk.hull(part, pts, mat)


RAIL_Y = (8.2, 8.45)
RAIL_Z = (-4.6, 5.4)


def frame(mk, d, n):
    part = mk.part("Frame", (0, 0, 0))
    off = 0.27
    for zb in (-2.5, 2.5):
        mk.box(part, (0, 9.7, zb), (14.8, 0.6, 0.5), DARK)                                 # tirante
        for s in (-1, 1):
            a = v_add((7.6, roof_u(7.6)), n, -off)
            p = v_add((0.0, WH + RISE), n, -off)
            beam_xy(mk, part, zb, (s * a[0], a[1]), (s * p[0], p[1]), 0.45, 0.5)          # cabio
        mk.box(part, (0, 8.92, zb), (0.12, 1.0, 0.12), IRON)                               # colgante del riel
    mk.box(part, (0, WH + RISE - 0.586 - 0.22, 0), (0.5, 0.5, 11.96), DARK)               # cumbrera
    mk.box(part, (0, sum(RAIL_Y) / 2, sum(RAIL_Z) / 2), (0.22, RAIL_Y[1] - RAIL_Y[0], RAIL_Z[1] - RAIL_Z[0] - 0.01),
           IRON)                                                                           # riel (toca la pared de atrás)


def hooks(mk):
    part = mk.part("Hooks", (0, 0, 0))
    meat = {1, 2}
    for i, z in enumerate((-3.4, -1.1, 1.3, 3.7)):
        mk.box(part, (0, 8.42, z), (0.42, 0.62, 0.5), IRON)                                # carrito abraza el riel
        mk.box(part, (0, 7.8, z), (0.09, 0.66, 0.09), IRON)                                # vástago
        # gancho en J (de frente): caña, curva y punta
        # (espesores distintos: las caras de cascos encimados nunca quedan coplanares)
        mk.hull(part, [(x, y, z + dz) for x in (-0.05, 0.05) for y in (7.5, 7.0) for dz in (-0.05, 0.05)], IRON)
        mk.hull(part, [(x, y, z + dz) for x, y in ((-0.05, 7.05), (0.05, 7.05), (0.05, 6.86), (0.18, 6.78),
                                                   (0.22, 6.9), (0.1, 6.95)) for dz in (-0.047, 0.047)], IRON)
        mk.hull(part, [(x, y, z + dz) for x, y in ((0.15, 6.82), (0.24, 6.82), (0.34, 7.12), (0.28, 7.15))
                       for dz in (-0.044, 0.044)], IRON)
        if i in meat:                                                                      # media res envuelta en lona
            # cuarto trasero ancho arriba, se afina hacia el pescuezo abajo (media res de ~4 x 1,6)
            rings = ((7.0, 0.38, 0.3), (6.3, 0.8, 0.5), (5.0, 0.72, 0.46), (3.7, 0.45, 0.34), (3.0, 0.22, 0.2))
            pts = []
            for y, rx, rz in rings:
                for k in range(6):
                    t = 2 * math.pi * (k + 0.5) / 6
                    pts.append((0.28 + rx * math.cos(t), y, z + rz * math.sin(t)))
            mk.hull(part, pts, CANVAS)
            for y, rx, rz in ((5.8, 0.82, 0.535), (4.2, 0.62, 0.425)):                    # ataduras (0,05 afuera)
                ring = []
                for k in range(6):
                    t = 2 * math.pi * (k + 0.5) / 6
                    for dy in (-0.05, 0.05):
                        ring.append((0.28 + rx * math.cos(t), y + dy, z + rz * math.sin(t)))
                mk.hull(part, ring, DARK)


# ---------------------------------------------------------------- piso, tajo y cartel
def floor(mk):
    part = mk.part("Floor", (0, 0, 0))
    mk.box(part, (0, 0.075, 0), (14.8, 0.15, 10.8), STONE)                                # toca las paredes
    mk.box(part, (0, 0.07, -5.675), (5.98, 0.14, 0.65), STONE)                             # umbral del portón
    for x in (-3.7, 3.7):                                                                  # juntas de las losas
        for dx in (-0.03, 0.03):
            mk.slice(part, (x + dx, 0, 0), (1, 0, 0))
        mk.paint(part, IRON, box=((x, 0.15, 0), (0.062, 0.02, 12)))
    for z in (-1.8, 1.8):
        for dz in (-0.03, 0.03):
            mk.slice(part, (0, 0, z + dz), (0, 0, 1))
        mk.paint(part, IRON, box=((0, 0.15, z), (16, 0.02, 0.062)))
    # canaleta de desagüe bajo los ganchos, hasta la pared de atrás (sangre seca en el fondo)
    mk.carve(part, BLOOD, points=mk.pts_box((0.28, 0.15, 0.6), (0.44, 0.2, 10.2)))


def rot_pts(pts, pivot, ay, az):
    """Gira puntos locales: primero en z (ladeo), después en y; los lleva al pivote."""
    cy, sy = math.cos(math.radians(ay)), math.sin(math.radians(ay))
    cz, sz = math.cos(math.radians(az)), math.sin(math.radians(az))
    out = []
    for x, y, z in pts:
        x1, y1 = x * cz - y * sz, x * sz + y * cz
        out.append((pivot[0] + x1 * cy + z * sy, pivot[1] + y1, pivot[2] - x1 * sy + z * cy))
    return out


def block(mk):
    part = mk.part("Block", (0, 0, 0))
    c = (-4.6, 0.15, 2.6)
    mk.cyl(part, (c[0], c[1] + 1.15, c[2]), 0.85, 2.3, DARK, sides=8, top=0.94)
    mk.paint(part, BARE, box=((c[0], c[1] + 2.3, c[2]), (2.0, 0.02, 2.0)))                # cara de corte
    # cuchilla clavada y ladeada: hoja de hierro (0,3 adentro del tajo) y mango de madera, en el mismo marco
    pv = (c[0] + 0.15, c[1] + 2.3, c[2] - 0.1)
    box_pts = lambda x0, x1, y0, y1, h: [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (-h, h)]
    mk.hull(part, rot_pts(box_pts(-0.42, 0.42, -0.3, 0.38, 0.035), pv, 30, -12), IRON, detail=True)
    mk.hull(part, rot_pts(box_pts(-1.1, -0.36, 0.2, 0.36, 0.065), pv, 30, -12), BARE, detail=True)


def sign(mk):
    part = mk.part("Sign", (0, 0, 0))
    x0, x1, y0, y1 = -2.6, 2.6, 8.55, 9.75
    z = -6.12 - 0.05                                                     # apoya en los tapajuntas del hastial
    mk.box(part, (0, (y0 + y1) / 2, z), (x1 - x0, y1 - y0, 0.1), CANVAS)
    for xa, xb, ya, yb in ((x0 - 0.12, x0 + 0.12, y0 - 0.12, y1 + 0.12), (x1 - 0.12, x1 + 0.12, y0 - 0.12, y1 + 0.12),
                           (x0 + 0.1, x1 - 0.1, y0 - 0.11, y0 + 0.1), (x0 + 0.1, x1 - 0.1, y1 - 0.1, y1 + 0.11)):
        vert = xb - xa < 1
        deep, back = (0.18, -6.125) if vert else (0.16, -6.13)                    # sin caras coplanares entre sí
        mk.hull(part, [(x, y, zz) for x in (xa, xb) for y in (ya, yb) for zz in (back, -6.12 - deep)], DARK)


# ---------------------------------------------------------------- portón
def door(mk, name, s):
    """Hoja del portón: tablas verticales, cruz oscura y bisagras de pletina en el canto de afuera."""
    xo, xi = s * (DW - 0.02), s * 0.015
    x0, x1 = sorted((xo, xi))
    y0, y1 = 0.17, DH - 0.04
    zf, zb = -5.95, -5.65
    part = mk.part(name, (xo, 0.0, (zf + zb) / 2))
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (zf + zb) / 2), (x1 - x0, y1 - y0, zb - zf), BARE)
    for k in (1, 2, 3):
        x = x0 + (x1 - x0) * k / 4
        for dx in (-0.03, 0.03):
            mk.slice(part, (x + dx, 0, 0), (1, 0, 0))
        mk.paint(part, DARK, box=((x, 4, zf), (0.062, 9, 0.02)))
    for ya, yb in ((y0 + 0.3, y0 + 0.8), (y1 - 0.8, y1 - 0.3)):                          # travesaños
        mk.hull(part, [(x, y, z) for x in (x0 + 0.1, x1 - 0.1) for y in (ya, yb) for z in (zf + 0.01, zf - 0.09)],
                DARK, detail=True)
    for ya, yb in ((y0 + 0.8, y1 - 0.8),):                                               # diagonal (de la bisagra hacia arriba)
        lo = (xo - s * 0.35, ya + 0.1)
        hi = (xi + s * 0.35, yb - 0.1)
        dg = clip(strip2d(lo, hi, 0.38), rect(x0 + 0.17, x1 - 0.17, ya - 0.05, yb + 0.05))
        mk.hull(part, [(x, y, z) for x, y in dg for z in (zf + 0.015, zf - 0.075)], DARK, detail=True)
    for y in (y0 + 0.55, y1 - 0.55):                                                     # bisagras sobre los travesaños
        strap = [(xo + s * 0.05, y - 0.11), (xo - s * 1.5, y - 0.05), (xo - s * 1.62, y), (xo - s * 1.5, y + 0.05),
                 (xo + s * 0.05, y + 0.11)]
        mk.prism(part, strap, 0.04, IRON, plane="xy", center=(0, 0, zf - 0.11), detail=True)
    if s > 0:                                                                            # tabla rota abajo
        cx = x0 + (x1 - x0) * 0.62
        mk.carve(part, DARK, prism=dict(profile=[(cx - 0.3, -0.2), (cx + 0.3, -0.2), (cx + 0.3, 0.35),
                                                 (cx + 0.05, 0.62), (cx - 0.12, 0.4), (cx - 0.3, 0.55)],
                                        depth=1.0, plane="xy", center=(0, 0, (zf + zb) / 2)))


def build(mk):
    walls(mk)
    d, n = roof(mk)
    frame(mk, d, n)
    hooks(mk)
    floor(mk)
    block(mk)
    sign(mk)
    door(mk, "DoorL", -1)
    door(mk, "DoorR", 1)

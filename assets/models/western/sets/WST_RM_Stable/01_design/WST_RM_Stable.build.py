"""
Receta de WST_RM_Stable, el establo del rancho (prompt 091, Bloques A + C). Oleada 2: liberar los
caballos del establo en llamas.

Brief
- Silueta a 40 studs: tinglado largo y bajo de techo a un agua (alto adelante, bajo atrás), frente abierto
  con una fila de seis puertas holandesas claras entre postes oscuros, alero adelante.
- Medidas: 32 (X) x 12 (Z); techo: abajo del techo a 10 en el frente (z = -6) y a 8 atrás (z = 6),
  aleros de 1,5 adelante, 0,6 atrás y 0,5 a los costados. Pared de atrás de 8 (cara de afuera en z = 6),
  testeros (x = ±16) siguiendo el techo. Seis boxes de 5,13 de eje (30,8 / 6) separados por tabiques de
  tablas de 5 de alto y 0,4 de espesor.
- Puertas (StallDoor_1..6, de -X a +X): media puerta de abajo de 4 de alto (y 0,15-4,15), 4,55 de ancho,
  tablas verticales wood_light con Z oscura, bisagras de pletina del lado -X (la izquierda del modelo,
  como el kit). Origen al pie del canto de las bisagras (z = -6, plano del frente).
- Paredes de tabla y tapajuntas wood_mid / wood_dark (la misma pared del granero). Techo de tejuelas
  wood_dark en hileras escalonadas con el escalón en hierro.
- Piezas: Stable_BackWall_frag01..08, Stable_Roof_frag01..08 (4 tramos x adelante/atrás),
  Stable_Partition_1..5_frag01..02, Stable_WallEnd_L/R_frag01..03, fixed_Frame (postes del frente,
  dintel, viga de adelante, cabios), StallDoor_1..6, marcadores _Horse_1..6 (al centro de cada box, en el piso).
- Cada box: pesebre en cuña con pasto contra la pared de atrás y balde de agua colgado (de la pared de atrás).
- Inferido: altos del techo como abajo del techo, eje de 5,13, los testeros como piezas propias de 3
  fragmentos (el prompt no los nombra), media puerta sin hoja de arriba (el caballo se asoma), dintel a 7,5
  y ventilación abierta hasta la viga, pesebres y baldes en la pared de atrás.

Vueltas: 1) índice de los postes corrido en las puertas · 2) 5396 triángulos (pesebre con 3 listones,
balde con zuncho y disco de agua: ~160 por box; pernos de bisagra); z-fighting entre el asa del balde y el
agua, y entre la diagonal de la puerta y los travesaños (recortada justo en su canto) · 3) balde de 6 lados
con el agua pintada arriba, 2 listones, tabiques de 4 tablas, sin pernos; diagonal recortada a 0,17.

Revisión
- 4406 triángulos contra 3500 de referencia (+26 %, calidad primero): pared de atrás ~1340 (tabla y
  tapajuntas + 6 pesebres y 6 baldes pedidos "en cada box"), 6 puertas ~170 (tablas, Z y bisagras: es lo
  que el jugador abre), 5 tabiques ~190. Por pieza, el máximo es ~200.
- Medidas: 33,0 x 10,65 x 14,18 (32 x 12 de paredes más aleros de 0,5 a los costados, 1,5 adelante y 0,6
  atrás; el alto suma el espesor del techo sobre el 10 de adelante). Boxes de 4,63 libres entre postes
  (eje 5,13: 30,8 / 6), tabiques de 5. Puertas 4,57 x 4,0.
- Fragmentos: pared de atrás 8 (el mayor ~13 %), techo 8, testeros 3 (el mayor ~40 %), tabiques 2 (cada
  mitad ~50 %: manda el "frag 2" del prompt, como el fardo). fixed_Frame queda en pie.
- Variante quemada no modelada (misma propuesta que el granero: paleta quemada por TextureID).
- Dudoso: la "puerta holandesa de dos partes" quedó como media puerta (la hoja de abajo de 4) sin hoja de
  arriba: con un solo objeto por puerta, una hoja de arriba abierta chocaba con el tabique al girar, y
  cerrada tapaba al caballo. Los testeros son piezas que el prompt no nombra.
"""

import math

BARE, DARK, LIGHT, HAY, IRON, WATER = "wood_mid", "wood_dark", "wood_light", "hay", "iron", "water"
RED = BARE                  # la pared de tabla del granero pinta la cara de afuera; acá es madera
CREAM = DARK
T = 0.6
B = 4.0 / 3.0
BW, BP = 0.24, 0.12
GAP = 0.05
ROOF_T, STEP = 0.4, 0.1

ZF, ZB = -6.0, 6.0          # frente (plano de los postes) y cara de afuera de la pared de atrás
YF, YB = 10.0, 8.0          # abajo del techo adelante y atrás
P = 30.8 / 6                # eje de los boxes
XP = [-15.4 + k * P for k in range(1, 6)]           # tabiques
XS = [-15.4 + (i + 0.5) * P for i in range(6)]      # centros de los boxes


def y_r(z):
    """Línea de abajo del techo en z."""
    return YF + (z - ZF) * (YB - YF) / (ZB - ZF)


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
            assert areas[n] / total <= 0.45, f"{self.prefix} {n}: {areas[n] / total:.0%} del área"
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
            part = mk.part(f"{self.prefix}_{name}", (0, 0, 0))
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
def back_wall(mk):
    j = [-16.0 + k * B for k in range(25)]
    crack = [(-16.0, 3.6), (-13.1, 4.9), (-10.0, 3.4), (-6.6, 4.8), (-3.5, 3.3), (0.4, 4.7), (3.6, 3.5),
             (6.9, 5.0), (10.1, 3.6), (13.2, 4.8), (16.0, 3.9)]
    frags = {}
    for i, (u0, u1) in enumerate(((-16.0, j[6]), (j[6], j[12]), (j[12], j[18]), (j[18], 16.0))):
        frags[f"frag{i + 1:02d}"] = (u0, u1, GROUND, crack)
    for i, (u0, u1) in enumerate(((-16.0, j[4]), (j[4], j[11]), (j[11], j[17]), (j[17], 16.0))):
        frags[f"frag{i + 5:02d}"] = (u0, u1, crack, TOP)
    wall = BoardWall(mk, "Stable_BackWall", "xy", ZB, 1, j, frags, top=lambda u: YB)
    wall.build()
    wall.hole((j[2] + j[3]) / 2, -0.5, 1.3, jag=((0.4, 0.3),))
    wall.hole((j[20] + j[21]) / 2, -0.5, 0.9, jag=((0.3, -0.15), (0.6, 0.25)))
    zi = ZB - T                                                     # cara de adentro
    for i, x in enumerate(XS):
        # pesebre: cuña oscura contra la pared con pasto arriba
        part = wall.parts[wall.owner(x, 5.2)]
        mk.hull(part, [(x + dx, y, z) for dx in (-1.3, 1.3) for y, z in ((6.0, zi - 1.0), (6.0, zi + 0.02),
                                                                          (4.5, zi + 0.02), (4.6, zi - 0.15))], DARK)
        mk.hull(part, [(x + dx, y, z) for dx in (-1.18, 1.18) for y, z in ((5.95, zi - 0.92), (5.95, zi - 0.05),
                                                                            (6.45, zi - 0.3), (6.35, zi - 0.75))]
                + [(x + 0.4, 6.6, zi - 0.5), (x - 0.5, 6.55, zi - 0.45)], HAY, detail=True)
        for dx in (-0.6, 0.6):                                      # listones del pesebre (salen 0,04)
            mk.hull(part, [(x + dx + sx, y, z) for sx in (-0.07, 0.07)
                           for y, z in ((5.98, zi - 1.04), (6.02, zi - 0.97), (4.62, zi - 0.19), (4.58, zi - 0.13))],
                    LIGHT, detail=True)
        # balde colgado de un clavo en la esquina del box
        bx = x + 1.75
        part = wall.parts[wall.owner(bx, 2.4)]
        r = 0.42
        zc = zi - r * math.cos(math.pi / 8) - 0.02 + 0.04
        mk.cyl(part, (bx, 2.35, zc), r * 0.85, 0.75, BARE, sides=6, top=1.2)       # base: el agua se pinta arriba
        mk.paint(part, WATER, box=((bx, 2.725, zc), (0.3, 0.02, 0.3)))
        mk.hull(part, [(bx + sx, y, z) for sx in (-0.03, 0.03) for y, z in ((2.6, zc - 0.05), (2.6, zc + 0.05),
                                                                          (3.25, zi + 0.02), (3.18, zi + 0.02))],
                IRON, detail=True)                                  # asa al clavo
    return wall


def end_wall(mk, side):
    s = -1 if side == "L" else 1
    z0, z1 = ZF + 0.25, ZB - T                                      # detrás del poste de la esquina, hasta la pared de atrás
    j = [z0] + [ZF + k * B for k in range(1, 9)] + [z1]
    crack = [(z0, 5.2), (-3.0, 6.1), (0.3, 4.8), (3.2, 5.9), (z1, 5.1)]
    frags = {"frag01": (z0, j[4], GROUND, crack), "frag02": (j[4], z1, GROUND, crack), "frag03": (z0, z1, crack, TOP)}
    wall = BoardWall(mk, f"Stable_WallEnd_{side}", "zy", s * 16.0, s, j, frags, top=y_r)
    wall.build()
    return wall


# ---------------------------------------------------------------- tabiques
def partition(mk, k, x):
    """Tabique de tablas horizontales (4 de 1,25), 5 de alto, de la pared de atrás al poste del frente;
    dos fragmentos partidos por una grieta en zigzag."""
    za, zb = ZF + 0.25, ZB - T
    crack = [(-0.6, 0.0), (0.4, 1.4), (-0.9, 2.6), (0.6, 3.9), (-0.2, 5.0)]
    crack = [(z + 0.6 * ((k % 3) - 1), y) for z, y in crack]
    polys = {"frag01": [(za, 0.0)] + crack + [(za, 5.0)],
             "frag02": [(zb, 0.0), (zb, 5.0)] + crack[::-1]}
    for name, poly in polys.items():
        part = mk.part(f"Stable_Partition_{k}_{name}", (0, 0, 0))
        mk.prism(part, clean(poly), 0.4, BARE, plane="zy", center=(x, 0, 0))
        for i in range(1, 4):                                       # juntas de 4 tablas, en las dos caras
            yy = 5.0 * i / 4
            for dy in (-0.03, 0.03):
                mk.slice(part, (0, yy + dy, 0), (0, 1, 0))
            for sx in (-1, 1):
                mk.paint(part, DARK, box=((x + sx * 0.2, yy, 0), (0.02, 0.062, 20)))
        z0 = min(p[0] for p in poly)
        z1 = max(p[0] for p in poly)
        zt0 = za + 0.02 if name == "frag01" else crack[-1][0] + GAP
        zt1 = crack[-1][0] - GAP if name == "frag01" else zb - 0.02
        mk.box(part, (x, 5.06, (zt0 + zt1) / 2), (0.56, 0.16, zt1 - zt0), DARK, detail=True)   # tapa de arriba


# ---------------------------------------------------------------- estructura que queda en pie
def beam_zy(mk, part, x, a, b, w, h, mat=DARK):
    """Viga recta de a=(z, y) a b=(z, y) en x: sección w (x) por h."""
    d = v_unit(a, b)
    nrm = (-d[1], d[0])
    pts = []
    for p in (a, b):
        for k in (-0.5, 0.5):
            q = v_add(p, nrm, k * h)
            for dx in (-w / 2, w / 2):
                pts.append((x + dx, q[1], q[0]))
    mk.hull(part, pts, mat)


def frame(mk):
    part = mk.part("fixed_Frame", (0, 0, 0))
    for x in [-15.7] + XP + [15.7]:
        w = 0.6 if abs(x) > 15 else 0.5
        mk.box(part, (x, (y_r(ZF) - 0.6) / 2, ZF), (w, y_r(ZF) - 0.6, 0.5), DARK)          # poste
    # viga de adelante debajo del techo (sigue la pendiente) y dintel de las puertas
    mk.hull(part, [(x, y, z) for x in (-16.05, 16.05) for z in (ZF - 0.3, ZF + 0.3)
                   for y in (y_r(z) - 0.02, y_r(z) - 0.72)], DARK)
    mk.box(part, (0, 7.75, ZF), (31.98, 0.5, 0.42), DARK)
    for x in [-15.1] + XP + [15.1]:                                   # cabios, 0,02 debajo del techo
        za, zb = ZF - 0.45, ZB - T + 0.2
        beam_zy(mk, part, x, (za, y_r(za) - 0.27), (zb, y_r(zb) - 0.27), 0.36 if abs(x) < 15 else 0.4, 0.5)


# ---------------------------------------------------------------- techo
OVH_F, OVH_B, OVH_X = 1.5, 0.6, 0.5


def shed_profiles():
    """Perfiles (z, y) de las dos mitades del techo (atrás y adelante), con las hileras escalonadas:
    el canto de abajo de cada hilera (hacia atrás, donde baja el agua) sobresale."""
    lo = (ZB + OVH_B, y_r(ZB + OVH_B))
    hi = (ZF - OVH_F, y_r(ZF - OVH_F))
    mid = (0.0, y_r(0.0))
    d = v_unit(lo, hi)
    n = (d[1], -d[0])                                               # normal de afuera (y > 0)
    out = []
    for a, b, first_step in ((lo, mid, True), (mid, hi, False)):
        L = v_dot((b[0] - a[0], b[1] - a[1]), d)
        nr = max(1, round(L / 1.4))
        base = v_add(a, n, ROOF_T)
        pts, rows = [], []
        for i in range(nr):
            p0 = v_add(base, d, L * i / nr)
            if i > 0 or first_step:
                p0 = v_add(p0, n, STEP)
            p1 = v_add(base, d, L * (i + 1) / nr)
            pts += [p0, p1]
            rows.append((p0, p1))
        out.append((clean([a, b] + pts[::-1]), rows))
    return out


def roof(mk):
    bays = [(-16.0 - OVH_X, XP[0]), (XP[0], 0.0), (0.0, XP[-1]), (XP[-1], 16.0 + OVH_X)]
    n = 1
    for prof, rows in shed_profiles():
        for x0, x1 in bays:
            part = mk.part(f"Stable_Roof_frag{n:02d}", (0, 0, 0))
            mk.prism(part, prof, x1 - x0, BARE, plane="zy", center=((x0 + x1) / 2, 0, 0))
            for i, (a, b) in enumerate(rows):
                c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                mk.paint(part, DARK, box=(((x0 + x1) / 2, c[1], c[0]), (x1 - x0 + 0.5, 0.3, 0.3)))
                if i > 0:
                    lip = rows[i - 1][1]
                    c2 = ((a[0] + lip[0]) / 2, (a[1] + lip[1]) / 2)
                    mk.paint(part, IRON, box=(((x0 + x1) / 2, c2[1], c2[0]), (x1 - x0 + 0.5, 0.06, 0.06)))
            n += 1


# ---------------------------------------------------------------- puertas
def stall_door(mk, i):
    xl = XP[i - 2] + 0.25 if i > 1 else -15.4                      # cara del poste de la izquierda
    xr = XP[i - 1] - 0.25 if i < 6 else 15.4
    x0, x1 = xl + 0.03, xr - 0.03
    y0, y1 = 0.15, 4.15
    zf, zb = ZF - 0.125, ZF + 0.125
    part = mk.part(f"StallDoor_{i}", (x0, 0.0, ZF))
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, ZF), (x1 - x0, y1 - y0, zb - zf), LIGHT)
    for k in range(1, 5):                                           # juntas de 5 tablas verticales
        x = x0 + (x1 - x0) * k / 5
        for dx in (-0.03, 0.03):
            mk.slice(part, (x + dx, 0, 0), (1, 0, 0))
        mk.paint(part, DARK, box=((x, 2, zf), (0.062, 5, 0.02)))
        mk.paint(part, DARK, box=((x, 2, zb), (0.062, 5, 0.02)))
    # Z de afuera: dos travesaños y la diagonal (de la bisagra abajo al otro lado arriba)
    rails = ((y0 + 0.55, 0.5), (y1 - 0.55, 0.5))
    for y, h in rails:
        mk.hull(part, [(x, yy, z) for x in (x0 + 0.12, x1 - 0.12) for yy in (y - h / 2, y + h / 2)
                       for z in (zf + 0.01, zf - 0.09)], DARK, detail=True)
    a, b = (x0 + 0.35, y0 + 0.8), (x1 - 0.45, y1 - 0.8)
    diag = clip(strip2d(a, b, 0.42), rect(x0 + 0.17, x1 - 0.17, y0 + 0.75, y1 - 0.75))   # no al ras de los travesaños
    mk.hull(part, [(x, y, z) for x, y in diag for z in (zf + 0.015, zf - 0.075)], DARK, detail=True)
    for y, _ in rails:                                              # bisagras de pletina
        strap = [(x0 - 0.05, y - 0.1), (x0 + 1.25, y - 0.05), (x0 + 1.37, y), (x0 + 1.25, y + 0.05), (x0 - 0.05, y + 0.1)]
        mk.prism(part, strap, 0.04, IRON, plane="xy", center=(0, 0, zf - 0.11), detail=True)
    mk.box(part, (x1 - 0.3, 2.6, zf - 0.04), (0.1, 0.45, 0.1), IRON, detail=True)            # pestillo
    mk.box(part, (x1 - 0.1, 2.9, zf - 0.035), (0.45, 0.08, 0.07), IRON, detail=True)


def build(mk):
    back_wall(mk)
    end_wall(mk, "L")
    end_wall(mk, "R")
    for k, x in enumerate(XP, start=1):
        partition(mk, k, x)
    frame(mk)
    roof(mk)
    for i in range(1, 7):
        stall_door(mk, i)
    for i, x in enumerate(XS, start=1):
        mk.marker(f"_Horse_{i}", (x, 0.0, -0.3))

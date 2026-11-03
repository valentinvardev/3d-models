"""
Receta de WST_CH_Church, la iglesia en ruinas del jefe final (prompt 122, Bloques A + C). Arena del
Predicador: fase 1 campana y púlpito, fase 2 bancos, fase 3 arde y el techo cae por zonas.

Brief
- Silueta a 40 studs: iglesia neogótica de frontera, alta y angosta: zócalo de piedra, tabla y tapajuntas
  crema (vertical: estira la altura), cuatro ventanas ojivales por lado, techo empinado a dos aguas de
  tejuelas oscuras y un campanario cuadrado al frente con el campanario abierto en arcos ojivales, chapitel
  de ocho caras y una cruz de hierro arriba. Un costado con un agujero ancho y el techo agujereado.
- Medidas: nave por dentro 24 (X) x 48 (Z) x 18 al alero; paredes de tabla de 0,6 (caras de afuera en
  x = ±12,6 y z = ±24,6) sobre un zócalo de piedra de 4 de alto y 1,0 de espesor (sale 0,4). Techo: abajo
  en (12,6, 18) y 29,4 en la cumbrera, 30 por afuera (42°), aleros de 1. Campanario de 10 x 10 (x ±5,
  z -24,6 a -14,6) que nace del frente a 18, piso del campanario a 30, arcos hasta 36,5, chapitel a 43,4 y
  cruz a 45.
- Portón: hueco de 8 x 12 con arco de medio punto (arranque a 8): ahí va WST_HC_ChurchDoors (piedra
  alrededor y hojas). Ventanas ojivales de 3 x 9,1 (alféizar 6,5, arranque 13, clave 15,6) con el marco
  oscuro roto y algunas puntas de vidrio. Atrás, un ojo de buey de 6 de diámetro (centro a 22,5), vacío.
- Piezas (prefijo + _fragNN): Church_WallSide_L/R (8: zócalo, 4 abajo y 3 arriba de una grieta en zigzag
  que pasa por las ventanas; en la L el agujero de 6 x ~7), Church_WallBack (8), Church_Front (7: zócalo en
  dos, costados, el tímpano sobre el arco y los dos hastiales), Church_Roof_Zone1..4 (8 cada una: faldón
  izquierdo y derecho, abajo y arriba, dos tramos en Z; la zona 1 recortada contra el campanario, la 2 con
  dos agujeros), fixed_Trusses (cerchas de tijera, tirante y vigas que cargan el campanario, correas),
  BellTower (8: cuatro paredes, piso de base con escalera, piso del campanario, arcos, chapitel con cruz).
- Inferido: estilo neogótico de tabla y tapajuntas, arco del portón, campanario sobre la fachada (no
  delante: así el portón da a la plaza), trampillas alineadas para la cuerda de la campana, cerchas cada
  7,3, adentro madera sin pintar, el agujero del costado en la L entre la 2.a y la 3.a ventana.

Vueltas: 1) aristas de 3 caras en la clave de cada ventana (las dos mitades del arco del marco compartían
la cara), z-fighting entre peldaños y largueros (al ras) y entre zócalo y tablas (caras de adentro al ras)
· 2) arco del marco en una pieza, peldaños más cortos, zócalo 0,02 más grueso hacia adentro · 3) arco
0,02 menos profundo que las jambas · 4) alrededor de los agujeros del techo quedaba un parche claro: la
talla parte las caras de las hileras y sus centros salían de la caja de pintura; ahora una cadena de
cajitas a lo largo de cada hilera. Menos piedras salientes y saltaduras.

Revisión
- 7878 triángulos contra 6000 de referencia (+31 %, calidad primero). Costados ~1800 cada uno (24
  tapajuntas partidos por la grieta, 4 ventanas con marco roto, parteluz y vidrios, zócalo con piedras),
  fondo ~1000 (ojo de buey), campanario ~830, techo ~1500 en 4 zonas, frente ~570, cerchas ~340. Por objeto,
  el máximo es ~410 (el tope del prompt es 5000).
- Medidas: 27,45 x 44,8 x 51,2. Nave 24 x 48 x 18 por dentro (paredes 25,2 x 49,2 por fuera, el zócalo
  26 x 50, aleros de 1). Cumbrera 30, campanario 10 x 10 desde 18, piso del campanario 30, cruz a 44,8.
  Portón: hueco de 8 x 12 de medio punto. Ventanas ojivales 3 x 9,1; ojo de buey de 6.
- Fragmentos: 8 por pieza (frente 7); en las paredes ninguno pasa el 45 % del área (se valida). Los huecos
  son muescas de las grietas: ningún fragmento rodea una ventana, el agujero o el ojo de buey.
- Variante quemada no modelada (misma propuesta que el granero: paleta quemada por TextureID). Se quema
  todo lo de madera; el zócalo es piedra.
- Dudoso: el campanario nace de la fachada a 18 (no delante): el portón queda a la vista de la plaza y la
  cuerda de la campana baja por dos trampillas a la nave. El hueco del portón es de medio punto: el
  portón (WST_HC_ChurchDoors, todavía sin hacer) tiene que calzar ese arco.
"""

import math

CREAM, BARE, DARK, STONE, GLASS, IRON = "paint_cream", "wood_mid", "wood_dark", "stone_grey", "glass", "iron"
TB = 0.6                    # tablas
TS = 1.0                    # zócalo de piedra (sale 0,4 afuera de las tablas)
BASE_H = 4.0
EAVE = 18.0
XO, ZO = 12.6, 24.6         # caras de afuera de las tablas
XI, ZI = 12.0, 24.0         # caras de adentro
E_ = (12.6, 18.0)
P_ = (0.0, 29.4)
ROOF_T, STEP, ROW = 0.45, 0.12, 2.0
TX, TZ0, TZ1 = 5.0, -24.6, -14.6       # campanario: medio ancho y z de adelante/atrás
BW, BP, GAP = 0.26, 0.12, 0.05         # tapajuntas


def roof_u(x):
    return E_[1] + (E_[0] - abs(x)) * (P_[1] - E_[1]) / E_[0]


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


def lancet(u0, u1, spring, steps=4, k=1.0):
    """Arco ojival de u0 a u1 desde la línea de arranque (k = radio / ancho; 1 = equilátero).
    Devuelve los puntos de izquierda a derecha (incluye los arranques)."""
    w = u1 - u0
    r = k * w
    cl, cr = (u0 + r, spring), (u1 - r, spring)        # centro del arco izquierdo (a la derecha) y del derecho
    xm = (u0 + u1) / 2
    apex_y = spring + math.sqrt(r * r - (xm - cl[0]) ** 2)
    a0, a1 = math.pi, math.atan2(apex_y - spring, xm - cl[0])
    left = [(cl[0] + r * math.cos(a0 + (a1 - a0) * i / steps), spring + r * math.sin(a0 + (a1 - a0) * i / steps))
            for i in range(steps + 1)]
    right = [(2 * xm - x, y) for x, y in reversed(left[:-1])]
    return left + right, apex_y


def round_arch(u0, u1, spring, steps=6):
    r = (u1 - u0) / 2
    c = (u0 + r, spring)
    return [(c[0] - r * math.cos(math.pi * i / steps), spring + r * math.sin(math.pi * i / steps)) for i in range(steps + 1)]


# ---------------------------------------------------------------- pared de tabla y tapajuntas (polilíneas)
GROUND, TOP = "ground", "top"


def y_at(poly, u, top=None):
    if poly == TOP:
        return top(u)
    for (ua, ya), (ub, yb) in zip(poly, poly[1:]):
        if ub - ua > 1e-9 and ua - 1e-9 <= u <= ub + 1e-9:
            return ya + (yb - ya) * (u - ua) / (ub - ua)
    raise ValueError(f"u={u} fuera de la polilínea {poly[0][0]}..{poly[-1][0]}")


def insert(poly, u0, u1, shape):
    """Reemplaza el tramo u0..u1 de la polilínea por shape (puntos de u0 a u1): el borde de un hueco."""
    a, b = y_at(poly, u0), y_at(poly, u1)
    return ([p for p in poly if p[0] < u0 - 1e-9] + [(u0, a)] + shape + [(u1, b)]
            + [p for p in poly if p[0] > u1 + 1e-9])


def P3(plane, u, y, w):
    return (w, y, u) if plane == "zy" else (u, y, w)


def S3(plane, su, sy, sw):
    return (sw, sy, su) if plane == "zy" else (su, sy, sw)


class Wall:
    """Pared plana de fragmentos. plane "zy": u = z (espesor en x); "xy": u = x (espesor en z).
    frags: {nombre: (u0, u1, borde de abajo, borde de arriba)}, bordes = polilíneas (u, y) o TOP."""

    def __init__(self, mk, prefix, plane, w_out, sgn, T, frags, top=None, breaks=(), face=CREAM, inner=BARE,
                 joints=(), batten=CREAM, max_share=0.45, names=None):
        self.mk, self.prefix, self.plane, self.w_out, self.sgn, self.T = mk, prefix, plane, w_out, sgn, T
        self.frags, self.top, self.breaks, self.face, self.inner = frags, top, breaks, face, inner
        self.j, self.batten_mat, self.max_share = joints, batten, max_share
        self.parts = {}
        self._check()

    def yb(self, poly, u):
        return y_at(poly, u, self.top)

    def outline(self, f):
        u0, u1, bot, tp = f
        pts = [(u0, self.yb(bot, u0))] + [p for p in bot if u0 + 1e-9 < p[0] < u1 - 1e-9] + [(u1, self.yb(bot, u1))]
        pts.append((u1, self.yb(tp, u1)))
        if tp == TOP:
            pts += [(u, self.top(u)) for u in sorted(self.breaks, reverse=True) if u0 < u < u1]
        else:
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
            for i in range(31):
                u = u0 + (u1 - u0) * (0.01 + 0.98 * i / 30)
                assert self.yb(tp, u) - self.yb(bot, u) >= 0.4, f"{self.prefix} {n}: angosto en u={u:.2f}"
            assert areas[n] / total <= self.max_share, f"{self.prefix} {n}: {areas[n] / total:.0%} del área"
        lo = min(f[0] for f in self.frags.values())
        hi = max(f[1] for f in self.frags.values())
        for i in range(80):
            u = lo + (hi - lo) * (i + 0.5) / 80
            for k in range(90):
                y = 45.0 * (k + 0.5) / 90
                hits = [n for n, (u0, u1, bot, tp) in self.frags.items()
                        if u0 < u < u1 and self.yb(bot, u) < y < self.yb(tp, u)]
                assert len(hits) <= 1, f"{self.prefix}: se pisan {hits} en ({u:.2f}, {y:.2f})"
        self.share = {n: a / total for n, a in areas.items()}

    def p(self, u, y, w_off):
        return P3(self.plane, u, y, self.w_out + self.sgn * w_off)

    def box(self, part, u0, u1, y0, y1, w0, w1, mat, detail=True):
        c = self.p((u0 + u1) / 2, (y0 + y1) / 2, (w0 + w1) / 2)
        self.mk.box(part, c, S3(self.plane, u1 - u0, y1 - y0, abs(w1 - w0)), mat, detail=detail)

    def build(self):
        mk = self.mk
        for name, f in self.frags.items():
            part = mk.part(f"{self.prefix}_{name}", (0, 0, 0))
            self.parts[name] = part
            wc = self.w_out - self.sgn * self.T / 2
            mk.prism(part, self.outline(f), self.T, self.inner, plane=self.plane, center=P3(self.plane, 0, 0, wc))
            if self.face != self.inner:
                mk.paint(part, self.face, box=(self.p(0, 25, 0), S3(self.plane, 120, 60, 0.02)))
        if self.j:
            self.battens()

    def segments(self, us, y_lo, y_hi):
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
        for u in self.j:
            top = (min(self.top(u - BW / 2), self.top(u + BW / 2)) - 0.1) if self.top else 60
            for a, b, (ol, orr) in self.segments([u - 0.14, u + 0.14], 0.0, top):
                a2 = a + GAP
                b2 = top if b >= top - 1e-6 else b - GAP
                if b2 - a2 <= 0.3:
                    continue
                if ol == orr:
                    self.box(self.parts[ol], u - BW / 2, u + BW / 2, a2, b2, -0.01, BP, self.batten_mat)
                else:
                    self.box(self.parts[ol], u - BW / 2, u, a2, b2, -0.01, BP, self.batten_mat)
                    self.box(self.parts[orr], u, u + BW / 2, a2, b2, -0.01, BP, self.batten_mat)

    def chip(self, uc, y0, w, h, seed=0):
        """Pintura saltada (rebaje de 0,03 de borde dentado) que muestra la madera."""
        part = self.parts[self.owner(uc, y0 + h / 2)]
        hs = [0.0, 0.25, -0.15, 0.3, -0.1, 0.2, -0.25, 0.12]
        n = 5
        top = [(uc + w / 2 - w * (i + 0.5) / n, y0 + h + hs[(i + seed) % 8]) for i in range(n)]
        bot = [(uc - w / 2 + w * (i + 0.5) / n, y0 + hs[(i + seed + 3) % 8] * 0.6) for i in range(n)]
        prof = [(uc - w / 2, y0 + 0.1)] + bot + [(uc + w / 2, y0 + 0.2)] + top
        self.mk.carve(part, BARE, prism=dict(profile=prof, depth=0.06, plane=self.plane,
                                            center=P3(self.plane, 0, 0, self.w_out)))


# ---------------------------------------------------------------- ventanas ojivales
WIN_W, WIN_SILL, WIN_SPRING = 3.0, 6.5, 13.0


def window_shapes(uc):
    u0, u1 = uc - WIN_W / 2, uc + WIN_W / 2
    arch, apex = lancet(u0, u1, WIN_SPRING, steps=3)
    lo = [(u0, WIN_SILL), (u1, WIN_SILL)]                               # el de abajo baja al alféizar
    hi = arch                                                           # el de arriba sube por el arco
    return u0, u1, lo, hi, arch, apex


def window_frame(wall, uc, damage=0):
    """Marco oscuro roto adentro del hueco: jambas (partidas en la grieta), arco en dos mitades, alféizar
    afuera, parteluz quebrado y algunas puntas de vidrio."""
    mk = wall.mk
    u0, u1, _, _, arch, apex = window_shapes(uc)
    fw = 0.22
    w0, w1 = -0.18, -0.48                                               # dentro del espesor de la pared
    for ua, ub, probe in ((u0 - 0.01, u0 + fw, u0 - 0.2), (u1 - fw, u1 + 0.01, u1 + 0.2)):
        for a, b, (o,) in wall.segments([probe], WIN_SILL, WIN_SPRING):            # dueño: la pared al lado
            if damage == 1 and ua < uc and b > 10.5:                     # jamba izquierda arrancada arriba
                b = min(b, 10.5)
                if b - a < 0.3:
                    continue
            wall.box(wall.parts[o], ua, ub, a + (0 if a <= WIN_SILL else GAP), b - (0 if b >= WIN_SPRING else GAP),
                     w0, w1, DARK)
    o_up = wall.owner(uc, apex + 0.3)
    # arco del marco en UNA pieza (dos mitades compartían la cara de la clave: aristas de 3 caras, medido);
    # en el roto, la mitad derecha queda cortada apenas pasando la clave
    half = len(arch) // 2
    seg = arch if damage != 2 else arch[:half + 2]
    outer = list(seg)
    inner = [(u + (uc - u) * fw / (WIN_W / 2) * 0.9, y - fw * 0.9) for u, y in seg]
    prof = clean(outer + inner[::-1])
    mk.prism(wall.parts[o_up], prof, abs(w1 - w0) - 0.02, DARK, plane=wall.plane,          # no al ras de las jambas
             center=P3(wall.plane, 0, 0, wall.w_out + wall.sgn * (w0 + w1) / 2), detail=True)
    o_lo = wall.owner(uc, WIN_SILL - 0.3)
    wall.box(wall.parts[o_lo], u0 - 0.3, u1 + 0.3, WIN_SILL - 0.28, WIN_SILL + 0.03, -0.05, 0.25, DARK)   # alféizar
    # parteluz quebrado y vidrios que quedaron
    o_m = wall.owner(u0 - 0.3, WIN_SILL + 1.0)
    top = 9.4 if damage != 2 else 8.2
    pts = [(uc - 0.09, WIN_SILL), (uc + 0.09, WIN_SILL), (uc + 0.09, top - 0.2), (uc + 0.02, top + 0.15),
           (uc - 0.09, top - 0.05)]
    mk.prism(wall.parts[o_m], pts, 0.2, DARK, plane=wall.plane,
             center=P3(wall.plane, 0, 0, wall.w_out + wall.sgn * -0.33), detail=True)
    shards = [((u0 + fw, WIN_SILL), (u0 + fw + 0.7, WIN_SILL), (u0 + fw, WIN_SILL + 1.1)),
              ((uc + 0.09, WIN_SILL), (u1 - fw, WIN_SILL), (u1 - fw, WIN_SILL + 0.6), (uc + 0.5, WIN_SILL + 0.25))]
    if damage == 0:
        shards.append(((u1 - fw, WIN_SPRING - 1.3), (u1 - fw, WIN_SPRING - 0.1), (u1 - fw - 0.6, WIN_SPRING - 0.2)))
    for sh in shards:
        o = wall.owner(sum(p[0] for p in sh) / len(sh), sum(p[1] for p in sh) / len(sh)) or o_lo
        mk.prism(wall.parts[o], list(sh), 0.04, GLASS, plane=wall.plane,
                 center=P3(wall.plane, 0, 0, wall.w_out + wall.sgn * -0.33), detail=True)


# ---------------------------------------------------------------- zócalo de piedra
def stone_base(mk, prefix, name, plane, w_out, sgn, u0, u1, holes=(), seed=0):
    """Zócalo de piedra (1,0 de espesor, sale 0,4): prisma con el borde de arriba irregular y piedras salientes."""
    tops = [4.04, 4.14, 4.06, 4.16, 4.03, 4.11]                       # siempre sobre 4: las tablas apoyan adentro
    n = max(2, int((u1 - u0) / 3.0))
    top = [(u0 + (u1 - u0) * i / n, tops[(i + seed) % 6]) for i in range(n + 1)]
    top[0] = (u0, 4.06)
    top[-1] = (u1, 4.06)
    part = mk.part(f"{prefix}_{name}", (0, 0, 0))
    prof = [(u0, 0.0), (u1, 0.0)] + top[::-1]
    # 0,02 más grueso hacia adentro: su cara de adentro no queda al ras de la de las tablas (z-fighting medido)
    mk.prism(part, clean(prof), TS + 0.02, STONE, plane=plane, center=P3(plane, 0, 0, w_out - sgn * (TS + 0.02) / 2))
    k = seed
    u = u0 + 1.3
    while u < u1 - 1.0:
        if not any(a - 0.6 < u < b + 0.6 for a, b in holes):
            y = 0.6 + (k * 1.37) % 2.6
            w, h = 0.9 + (k % 3) * 0.25, 0.55 + (k % 2) * 0.2
            c = P3(plane, u, y, w_out + sgn * 0.06)
            mk.box(part, c, S3(plane, w, h, 0.2), STONE, rot=(0, 0, 0), detail=True)
        u += 4.2 + (k % 3) * 0.9                                        # pocas piedras salientes: el zócalo ya se lee
        k += 1
    return part


# ---------------------------------------------------------------- paredes de la nave
def side_wall(mk, side):
    s = -1 if side == "L" else 1
    wins = (-18.0, -6.0, 6.0, 18.0)
    if side == "L":
        base = [(-ZO, 9.6), (-21.0, 11.2), (-16.5, 9.0), (-13.0, 11.6), (-9.8, 9.4), (-7.5, 10.4), (-4.5, 9.2),
                (-0.5, 11.0), (2.8, 9.0), (4.5, 10.8), (7.5, 9.6), (11.0, 11.5), (14.2, 9.3), (16.5, 10.2),
                (19.5, 9.4), (22.0, 11.0), (ZO, 9.8)]
    else:
        base = [(-ZO, 10.6), (-21.5, 9.2), (-16.5, 10.9), (-13.4, 9.0), (-10.0, 11.3), (-7.5, 9.7), (-4.5, 10.6),
                (-1.0, 9.0), (2.5, 11.2), (4.5, 9.8), (7.5, 10.5), (10.6, 9.1), (14.0, 11.2), (16.5, 9.6),
                (19.5, 10.4), (22.4, 9.2), (ZO, 10.9)]
    lo, hi = list(base), list(base)
    for uc in wins:
        u0, u1, wl, wh, _, _ = window_shapes(uc)
        lo = insert(lo, u0, u1, wl)
        hi = insert(hi, u0, u1, wh)
    if side == "L":                                                   # agujero de ~6 x 7: bordes desgarrados
        lo = insert(lo, -3.4, 3.2, [(-3.0, 6.9), (-2.2, 5.6), (-1.3, 6.3), (-0.4, 4.9), (0.6, 5.8), (1.5, 4.7),
                                    (2.4, 5.9), (2.9, 7.4)])
        hi = insert(hi, -3.4, 3.2, [(-3.1, 11.9), (-2.3, 12.9), (-1.2, 12.2), (-0.2, 13.4), (0.9, 12.4),
                                    (1.9, 13.1), (2.7, 11.7)])
    bot = [(-ZO, BASE_H), (ZO, BASE_H)]
    topl = [(-ZO, EAVE), (ZO, EAVE)]
    frags = {}
    for i, (u0, u1) in enumerate(((-ZO, -12.0), (-12.0, 0.0), (0.0, 12.0), (12.0, ZO))):
        frags[f"frag{i + 2:02d}"] = (u0, u1, bot, lo)
    for i, (u0, u1) in enumerate(((-ZO, -10.0), (-10.0, 10.0), (10.0, ZO))):
        frags[f"frag{i + 6:02d}"] = (u0, u1, hi, topl)
    joints = [-ZO + 1.0 + 2.0 * k for k in range(25) if -ZO + 1.0 + 2.0 * k < ZO - 0.5]
    wall = Wall(mk, f"Church_WallSide_{side}", "zy", s * XO, s, TB, frags, top=lambda u: EAVE, joints=joints)
    wall.build()
    stone_base(mk, f"Church_WallSide_{side}", "frag01", "zy", s * (XI + TS), s, -25.0, 25.0, seed=2 if s < 0 else 5)
    for k, uc in enumerate(wins):
        window_frame(wall, uc, damage=(k + (0 if s < 0 else 1)) % 3)
    for uc, y0, sd in ((-10.0, 14.5, 3), (13.0, 4.6, 5)):
        if wall.owner(uc, y0 + 0.6):
            wall.chip(uc + s * 0.0, y0, 1.3, 1.1, sd)
    return wall


def front_wall(mk):
    c1 = [(-XI, 9.6), (-9.0, 11.4), (-6.5, 9.4), (-5.0, 10.3), (-4.0, 10.8), (4.0, 10.6), (5.0, 10.0),
          (6.8, 11.2), (9.4, 9.5), (XI, 10.9)]
    arch = round_arch(-4.0, 4.0, 8.0, steps=6)
    center_bot = [(-TX, y_at(c1, -TX)), (-4.0, y_at(c1, -4.0))] + arch + [(4.0, y_at(c1, 4.0)), (TX, y_at(c1, TX))]
    bot = lambda a, b: [(a, BASE_H), (b, BASE_H)]

    def top(u):
        return EAVE if abs(u) < TX - 1e-6 else roof_u(u)
    frags = {
        "frag03": (-XI, -4.0, bot(-XI, -4.0), c1),
        "frag04": (4.0, XI, bot(4.0, XI), c1),
        "frag05": (-TX, TX, center_bot, [(-TX, EAVE), (TX, EAVE)]),
        "frag06": (-XI, -TX, c1, TOP),
        "frag07": (TX, XI, c1, TOP),
    }
    joints = [-11.0 + 2.0 * k for k in range(12)]
    wall = Wall(mk, "Church_Front", "xy", -ZO, -1, TB, frags, top=top, joints=joints)
    wall.build()
    stone_base(mk, "Church_Front", "frag01", "xy", -(ZI + TS), -1, -XI, -4.0, seed=1)
    stone_base(mk, "Church_Front", "frag02", "xy", -(ZI + TS), -1, 4.0, XI, seed=4)
    wall.chip(-8.0, 4.6, 1.4, 1.0, 2)
    wall.chip(9.0, 13.0, 1.2, 1.2, 6)
    return wall


def back_wall(mk):
    rc, rr = 22.5, 3.0
    circ = [(rr * math.cos(math.pi + math.pi * i / 8), rc + rr * math.sin(math.pi + math.pi * i / 8)) for i in range(9)]
    lower_half = [(x, y) for x, y in circ]                                       # de (-3, 22,5) bajando a (3, 22,5)
    upper_half = [(-rr * math.cos(math.pi * i / 8), rc + rr * math.sin(math.pi * i / 8)) for i in range(9)]
    c1 = [(-XI, 9.4), (-8.8, 11.2), (-5.6, 9.2), (-2.0, 11.0), (1.6, 9.3), (5.2, 11.1), (8.6, 9.5), (XI, 10.8)]
    c2 = [(-XI, 17.2), (-8.0, 18.6), (-3.0, 22.5), (3.0, 22.5), (8.2, 18.4), (XI, 17.6)]
    c2_lo = insert(c2, -3.0, 3.0, lower_half[1:-1])
    c2_hi = insert(c2, -3.0, 3.0, upper_half[1:-1])
    bot = lambda a, b: [(a, BASE_H), (b, BASE_H)]
    frags = {
        "frag02": (-XI, -4.0, bot(-XI, -4.0), c1),
        "frag03": (-4.0, 4.0, bot(-4.0, 4.0), c1),
        "frag04": (4.0, XI, bot(4.0, XI), c1),
        "frag05": (-XI, 0.0, c1, c2_lo),
        "frag06": (0.0, XI, c1, c2_lo),
        "frag07": (-XI, 0.0, c2_hi, TOP),
        "frag08": (0.0, XI, c2_hi, TOP),
    }
    joints = [-11.0 + 2.0 * k for k in range(12) if abs(-11.0 + 2.0 * k) > 0.5]
    wall = Wall(mk, "Church_WallBack", "xy", ZO, 1, TB, frags, top=roof_u, breaks=(0.0,), joints=joints)
    wall.build()
    stone_base(mk, "Church_WallBack", "frag01", "xy", ZI + TS, 1, -XI, XI, seed=3)
    # marco del ojo de buey (vacío): aro en dos mitades y una cruz de travesaños, uno partido
    owners = []
    for half, owner_y in ((upper_half, rc + rr + 0.3), (list(reversed(circ)), rc - rr - 0.3)):   # dueño: la pared de afuera
        outer = [(x * 1.004, rc + (y - rc) * 1.004) for x, y in half]
        inner = [(x * 0.88, rc + (y - rc) * 0.88) for x, y in half]
        prof = clean(outer + inner[::-1])
        o = wall.owner(0.3, owner_y)
        owners.append(o)
        mk.prism(wall.parts[o], prof, 0.32, DARK, plane="xy", center=(0, 0, ZO - 0.3), detail=True)
    wall.box(wall.parts[owners[0]], -0.1, 0.1, rc - 0.6, rc + rr * 0.9, -0.2, -0.44, DARK)        # travesaño de arriba
    wall.box(wall.parts[owners[1]], -rr * 0.9, -0.4, rc - 0.1, rc + 0.1, -0.22, -0.42, DARK)      # medio brazo quebrado
    wall.chip(-9.0, 5.0, 1.4, 1.0, 3)
    wall.chip(6.5, 14.0, 1.2, 1.2, 5)
    return wall


# ---------------------------------------------------------------- techo por zonas
def roof_frame():
    d = v_unit(E_, P_)
    n = (d[1], -d[0])
    e_ext = v_add(E_, d, -1.0)
    return d, n, e_ext


def roof_profile(s0, s1, x_cut):
    """Perfil (x, y) del faldón derecho entre s0 y s1 (distancia por la pendiente desde el alero) con las
    hileras de tejuelas, recortado en x >= x_cut (la cumbrera o el campanario)."""
    d, n, e_ext = roof_frame()
    U = lambda s: v_add(e_ext, d, s)
    O = lambda s, off: v_add(v_add(e_ext, d, s), n, off)
    outer = []
    k = int(s0 // ROW)
    while k * ROW < s1 - 1e-6:
        a, b = max(s0, k * ROW), min(s1, (k + 1) * ROW)
        if b - a > 1e-6:
            fa = 1.0 - (a - k * ROW) / ROW
            fb = 1.0 - (b - k * ROW) / ROW
            outer += [O(a, ROOF_T + STEP * fa), O(b, ROOF_T + STEP * fb)]
        k += 1
    prof = [U(s0), U(s1)] + outer[::-1]
    prof = clip(clean(prof), [(x_cut, -10.0), (40.0, -10.0), (40.0, 60.0), (x_cut, 60.0)])
    return prof


def roof_piece(mk, name, side, s0, s1, x_cut, z0, z1, holes=()):
    s = -1 if side == "L" else 1
    part = mk.part(name, (0, 0, 0))
    prof = roof_profile(s0, s1, x_cut)
    pr = [(s * x, y) for x, y in prof]
    mk.prism(part, pr if s > 0 else pr[::-1], z1 - z0, BARE, plane="xy", center=(0, 0, (z0 + z1) / 2))
    d, n, e_ext = roof_frame()
    # Hileras: una cadena de cajitas a lo largo de cada cara de arriba (si un agujero tallado parte la cara,
    # el centro de cada pedazo sigue cayendo sobre esa línea: con una caja sola quedaba un parche claro,
    # medido). Después los escalones en hierro, con cajas chicas en su centro.
    rows, steps = [], []
    for (ax, ay), (bx, by) in zip(prof, prof[1:] + prof[:1]):
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey)
        if L < 1e-6:
            continue
        ux, uy = ex / L, ey / L
        mx, my = (ax + bx) / 2, (ay + by) / 2
        off = (mx - e_ext[0]) * n[0] + (my - e_ext[1]) * n[1]
        if abs(ux * d[0] + uy * d[1]) > 0.97 and off > ROOF_T * 0.5:
            rows.append(((ax, ay), (bx, by), L))
        elif abs(ux * n[0] + uy * n[1]) > 0.97 and off > ROOF_T + 0.01:
            steps.append((mx, my))
    zc, zl = (z0 + z1) / 2, z1 - z0 + 0.5
    for (ax, ay), (bx, by), L in rows:
        k = max(2, int(L / 0.22))
        for i in range(k + 1):
            t = 0.06 + 0.88 * i / k
            mk.paint(part, DARK, box=((s * (ax + (bx - ax) * t), ay + (by - ay) * t, zc), (0.26, 0.26, zl)))
    for mx, my in steps:
        mk.paint(part, IRON, box=((s * mx, my, zc), (0.1, 0.1, zl)))
    for hc_s, hc_z, rad in holes:                                     # agujeros ya abiertos (bordes desgarrados)
        c = v_add(v_add(roof_frame()[2], d, hc_s), n, 0.2)
        jag = [(1.0, 0.0), (0.7, 0.55), (0.85, 0.9), (0.3, 0.75), (0.0, 1.0), (-0.45, 0.7), (-0.9, 0.85),
               (-0.75, 0.3), (-1.0, -0.15), (-0.6, -0.6), (-0.25, -0.95), (0.25, -0.7), (0.7, -0.9), (0.85, -0.4)]
        prof_h = [(px * rad[0], pz * rad[1]) for px, pz in jag]
        ang = math.degrees(math.atan2(n[0], n[1]))
        mk.carve(part, DARK, prism=dict(profile=prof_h, depth=3.0, plane="xz", center=(s * c[0], c[1], hc_z),
                                         rot=(0, 0, -s * ang)))
    return part


S_SPLIT = 8.0
S_EAVE = 0.0


def roof(mk):
    d, n, e_ext = roof_frame()
    s_ridge = (e_ext[0] - 0.0) / -d[0] + 1.5
    s_tower = (e_ext[0] - TX) / -d[0] + 1.5
    zones = [(-ZO - 1.0, -12.0), (-12.0, 0.0), (0.0, 12.0), (12.0, ZO + 1.0)]
    holes = {("R", 0, 1): [(11.0, -8.6, (2.2, 1.6))], ("L", 1, 0): [(4.6, -3.2, (1.7, 1.3))],
             ("L", 0, 1): [(12.5, -9.0, (1.4, 1.0))]}                # (lado, mitad en Z, abajo/arriba)
    for zi, (z0, z1) in enumerate(zones, start=1):
        k = 1
        for side in ("L", "R"):
            if zi == 1:
                spans = [(z0, TZ1, S_EAVE, S_SPLIT, 0.0), (z0, TZ1, S_SPLIT, s_tower, TX),
                         (TZ1, z1, S_EAVE, S_SPLIT, 0.0), (TZ1, z1, S_SPLIT, s_ridge, 0.0)]
            else:
                zm = (z0 + z1) / 2
                spans = [(za, zb, sa, sb, 0.0) for za, zb in ((z0, zm), (zm, z1))
                         for sa, sb in ((S_EAVE, S_SPLIT), (S_SPLIT, s_ridge))]
            for j, (za, zb, sa, sb, xc) in enumerate(spans):
                hz = []
                if zi == 2:
                    hz = holes.get((side, j // 2, j % 2), [])
                roof_piece(mk, f"Church_Roof_Zone{zi}_frag{k:02d}", side, sa, sb, xc, za, zb, holes=hz)
                k += 1


# ---------------------------------------------------------------- cerchas
def beam(mk, part, a, b, w, h, z, mat=DARK):
    d = v_unit(a, b)
    nrm = (-d[1], d[0])
    pts = []
    for p in (a, b):
        for k in (-0.5, 0.5):
            q = v_add(p, nrm, k * h)
            for dz in (-w / 2, w / 2):
                pts.append((q[0], q[1], z + dz))
    mk.hull(part, pts, mat)


def trusses(mk):
    part = mk.part("fixed_Trusses", (0, 0, 0))
    d, n, _ = roof_frame()
    off = 0.42
    under = lambda x: v_add((x, roof_u(x)), n, -off)
    for zt in (-7.3, 0.0, 7.3, 14.6, 21.9):                         # cerchas de tijera
        for s in (-1, 1):
            a, b = under(12.3), under(-0.25)
            beam(mk, part, (s * a[0], a[1]), (s * b[0], b[1]), 0.6, 0.8, zt)                       # par
            beam(mk, part, (s * 11.9, 18.15), (-s * 7.0, roof_u(7.0) - 1.15), 0.5 + (0.06 if s > 0 else 0.0),
                 0.7, zt)                                                                           # tijera
    zt = TZ1                                                         # bajo el campanario: tirante y pares cortados
    mk.box(part, (0, 17.55, zt), (2 * XI - 0.02, 0.9, 0.9), DARK)
    for s in (-1, 1):
        a, b = under(12.3), under(TX + 0.45)
        beam(mk, part, (s * a[0], a[1]), (s * b[0], b[1]), 0.6, 0.8, zt)
        mk.box(part, (s * (TX - 0.4), 17.55, (ZI * -1 + TZ1) / 2 - 0.0), (0.8, 0.9, TZ1 + ZI - 0.02), DARK)  # vigas del campanario
    for s in (-1, 1):                                                # correas
        c = under(7.4)
        mk.box(part, (s * c[0], c[1] - 0.45, 1.0), (0.55, 0.55, 47.96 - 2.0), DARK)
    pk = under(0.0)
    mk.box(part, (0, pk[1] - 0.5, (TZ1 + ZI) / 2), (0.55, 0.55, ZI - TZ1 - 0.02), DARK)           # cumbrera


# ---------------------------------------------------------------- campanario
BELFRY = 30.0


def bell_tower(mk):
    tw = 0.8
    joints_x = [-3.0, -1.0, 1.0, 3.0]
    # paredes de 18 a 30 (frente al ras de la fachada)
    walls = []
    for name, plane, w_out, sgn, u0, u1, joints in (
            ("frag01", "xy", TZ0, -1, -TX, TX, joints_x),
            ("frag02", "xy", TZ1, 1, -TX, TX, joints_x),
            ("frag03", "zy", -TX, -1, TZ0 + tw, TZ1 - tw, [-22.0, -20.0, -18.0, -16.6]),
            ("frag04", "zy", TX, 1, TZ0 + tw, TZ1 - tw, [-22.0, -20.0, -18.0, -16.6])):
        w = Wall(mk, "BellTower", plane, w_out, sgn, tw, {name: (u0, u1, [(u0, EAVE), (u1, EAVE)],
                                                               [(u0, BELFRY - 0.4), (u1, BELFRY - 0.4)])},
                 joints=joints, max_share=1.0)
        w.build()
        walls.append(w)
    # ventana ojival chica al frente (sobre el portón)
    arch, apex = lancet(-0.8, 0.8, 25.0, steps=3)
    prof = [(-0.8, 22.4), (0.8, 22.4)] + arch[::-1]
    mk.carve(walls[0].parts["frag01"], DARK, prism=dict(profile=prof, depth=2.0, plane="xy", center=(0, 0, TZ0)))
    # piso de la base (a 18) con la trampilla de la cuerda y la escalera hasta el campanario
    part = mk.part("BellTower_frag05", (0, 0, 0))
    mk.box(part, (0, EAVE - 0.2, (TZ0 + TZ1) / 2), (2 * (TX - tw) - 0.02, 0.4, TZ1 - TZ0 - 2 * tw - 0.02), BARE)
    mk.carve(part, DARK, points=mk.pts_box((1.6, EAVE - 0.2, -19.4), (1.2, 1.0, 1.2)))
    lx, lz = -2.6, TZ1 - tw - 0.35
    for x in (lx - 0.75, lx + 0.75):
        mk.box(part, (x, (EAVE - 0.05 + BELFRY - 0.1) / 2, lz), (0.22, BELFRY - EAVE - 0.05, 0.22), BARE, detail=True)
    for i in range(11):
        y = EAVE + 0.9 + i * 1.05
        mk.box(part, (lx, y, lz), (1.6, 0.12, 0.14), DARK, detail=True)              # puntas adentro de los largueros
    # piso del campanario (a 30) con alero y trampilla
    part = mk.part("BellTower_frag06", (0, 0, 0))
    mk.box(part, (0, BELFRY - 0.25, (TZ0 + TZ1) / 2), (2 * TX + 0.6, 0.5, TZ1 - TZ0 + 0.6), DARK)
    mk.carve(part, DARK, points=mk.pts_box((lx, BELFRY - 0.25, lz - 0.2), (1.5, 1.0, 1.2)))
    mk.carve(part, DARK, points=mk.pts_box((1.6, BELFRY - 0.25, -19.4), (0.8, 1.0, 0.8)))
    # campanario abierto: postes en las esquinas y cabezales con arco ojival
    part = mk.part("BellTower_frag07", (0, 0, 0))
    zc = (TZ0 + TZ1) / 2
    R = 4.2                                                           # medio ancho del campanario (más angosto que la torre)
    pw = 1.3
    top_y = 36.5
    for sx in (-1, 1):
        for sz in (-1, 1):
            mk.box(part, (sx * (R - pw / 2), (BELFRY + top_y) / 2, zc + sz * (R - pw / 2)), (pw, top_y - BELFRY, pw), CREAM)
    a0, a1 = -(R - pw), R - pw
    arch, apex = lancet(a0, a1, 32.4, steps=4, k=0.6)                 # clave a 35,8 (con 0,8 pasaba el cabezal)
    head = [(a1, 32.4)] + [(a1, top_y), (a0, top_y)] + [(a0, 32.4)] + arch[1:-1]
    for plane, w_out, sgn in (("xy", zc - R, -1), ("xy", zc + R, 1)):
        mk.prism(part, clean(head), 0.5, CREAM, plane="xy", center=(0, 0, w_out - sgn * 0.3))
    head_z = [(zc + u, y) for u, y in head]
    for sx in (-1, 1):
        mk.prism(part, clean(head_z), 0.5, CREAM, plane="zy", center=(sx * (R - 0.3), 0, 0))
    for sx in (-1, 1):                                                # barandas bajas entre postes
        mk.box(part, (sx * (R - 0.3), BELFRY + 1.0, zc), (0.24, 0.2, 2 * (R - pw) + 0.04), DARK, detail=True)
        mk.box(part, (0, BELFRY + 1.0, zc + sx * (R - 0.3)), (2 * (R - pw) + 0.04, 0.2, 0.24), DARK, detail=True)
    # chapitel de ocho caras con cornisa y cruz de hierro
    part = mk.part("BellTower_frag08", (0, 0, 0))
    mk.box(part, (0, top_y + 0.25, zc), (2 * R + 0.8, 0.5, 2 * R + 0.8), DARK)
    ring = [(R * 1.02 * math.cos(2 * math.pi * (k + 0.5) / 8), R * 1.02 * math.sin(2 * math.pi * (k + 0.5) / 8))
            for k in range(8)]
    apex_y = 43.4
    mk.hull(part, [(x, top_y + 0.48, zc + z) for x, z in ring] + [(0, apex_y, zc)], DARK)
    mk.box(part, (0, apex_y + 0.6, zc), (0.28, 1.6, 0.28), IRON)
    mk.box(part, (0, apex_y + 0.95, zc), (1.0, 0.26, 0.24), IRON)


def build(mk):
    side_wall(mk, "L")
    side_wall(mk, "R")
    front_wall(mk)
    back_wall(mk)
    roof(mk)
    trusses(mk)
    bell_tower(mk)

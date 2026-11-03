"""
Receta de WST_RM_Barn, el granero del rancho que arde y colapsa (prompt 090, Bloques A + C).

Brief
- Silueta a 40 studs: granero rojo de techo a la holandesa (gambrel: faldón bajo empinado y faldón alto
  tendido), portón doble corredizo con marco y cruz blancos, puerta del pajar arriba y la viga del pajar
  que asoma bajo la cumbrera. Esquineros blancos.
- Medidas: planta 24 (X) x 32 (Z); paredes de 12 (0,6 de espesor, cara de afuera en x = ±12 y z = ±16);
  techo: alero en (12, 12), quiebre en (8,5, 19), cumbrera de abajo en 23,4 y de afuera en ~24. Alero de
  1 sobre las paredes y 1 sobre los hastiales (z = ±17). Portón: hueco 8 x 10 (x ±4), dos hojas
  corredizas de 4,1 x 10,4 colgadas de un riel de hierro. Pajar: hueco 2,67 x 3,6 (x ±1,333, y 13,2-16,8).
- Paredes de tabla y tapajuntas (board-and-batten): tablas verticales de 4/3 (la cara de afuera
  paint_red, adentro y cortes wood_mid) y tapajuntas wood_dark de 0,24 x 0,12 en cada junta.
- Piezas (prefijo de pieza + _fragNN, como el kit): Barn_WallSide_L/R (8 fragmentos: 4 abajo y 4 arriba
  corridos una tabla, partidos por una grieta en escalera que pasa por las dos ventanas),
  Barn_Gable_Front (8: costados abajo/arriba, dintel, hastial izquierdo/derecho, punta sobre el pajar),
  Barn_Gable_Back (8), Barn_Roof_L/R (8: 4 tramos entre cerchas x faldón bajo/alto), Barn_Loft (6 de
  piso, la escalera y los fardos), fixed_Frame (postes, tirantes, cerchas gambrel, correas, carreras),
  DoorL, DoorR (corredizas, origen abajo al centro de la hoja), HayloftDoor (bisagra en el canto -X).
- Cada fragmento de pared es UN prisma de su contorno: bordes de fragmento como polilíneas (grietas en
  zigzag de 3-5 quiebres que cortan las tablas; los huecos son muescas de la grieta, así ningún
  fragmento rodea una ventana). Sin caras adentro ni cascos encimados. Tapajuntas, esquineros y marcos
  son detalle; los tapajuntas se cortan donde los cruza la grieta y se parten a lo largo en los bordes
  verticales de fragmento (medio para cada uno).
- Inferido: perfil del gambrel, tablas de 4/3, ventanas de 2,67 x 2,4 con alféizar a 5, pajar sobre la
  mitad de adelante (z -15,4 a 1) con escalera a x = -7, cinco fardos, esquineros y marcos de ventana
  crema, la viga del pajar con roldana, hastial de atrás ciego, tablas faltantes y pintura saltada al pie.

Vueltas: 1) 8148 triángulos, techo a franjas anchas que parecía un toldo, z-fighting en alféizares
(coplanares con el piso del hueco), remate de cumbrera (tapas al ras) y carreras (al ras de los postes)
· 2) tejuelas wood_dark con el escalón de cada hilera en hierro (línea fina); grieta escalonada tabla por
tabla que parecía onda cuadrada · 3) grietas como polilíneas en zigzag (Bloque C) y pintura saltada
· 4) pie de los esquineros coplanar con el de la pared: subidos 0,02; menos rebajes.

Revisión
- 7676 triángulos contra 5000 de referencia (calidad primero, +54 %): las cuatro paredes ~4600 (~180
  tapajuntas de 12 triángulos, partidos por los fragmentos: son lo que hace leer "granero de tabla"), el
  interior ~1500 (estructura 732 que queda en pie como esqueleto, pajar 800 con piso, vigas, escalera y
  fardos: la oleada 3 se defiende adentro). Por pieza, el máximo es 188 (muy lejos de 10 000).
- Medidas: 25,84 x 24,07 x 36,45. Paredes 24 x 32 x 12 exactas; el ancho suma los aleros (0,92 por lado)
  y el largo los aleros de los hastiales (1 por punta) más la viga del pajar (asoma 3,45 adelante).
  Cumbrera 24,07 (+0,3 %). Portón: hueco 8 x 10; pajar 2,67 x 3,6 con alféizar a 1,2 del piso del pajar.
- Fragmentos: 8 por pieza (el pajar: 6 de piso, escalera y fardos); ninguno pasa el 45 % del área (se
  valida en la receta) ni baja de 0,4. Las puertas son piezas móviles con origen propio.
- Variante quemada (wood_charred) NO modelada: duplicar las 60 piezas en otro color doblaría el archivo.
  Propuesta: una segunda textura de paleta con la madera y la pintura en wood_charred, que el sistema de
  fuego cambie en el TextureID (decide Valentin; fixed_Frame ya es el esqueleto que queda).
- Dudoso: ventanas altas (alféizar a 5: no se salta ni se dispara por ellas, como en el kit a 3) y
  hastial de atrás sin puerta: el granero se defiende por el portón y la puerta del pajar.
"""

import math

RED, BARE, DARK, CREAM, HAY, IRON = "paint_red", "wood_mid", "wood_dark", "paint_cream", "hay", "iron"
T = 0.6                     # espesor de pared
B = 4.0 / 3.0               # ancho de tabla
BW, BP = 0.24, 0.12         # tapajuntas: ancho y cuánto sale
GAP = 0.05                  # los tapajuntas se cortan en las grietas (se lee la rotura)

E_ = (12.0, 12.0)           # alero (borde de afuera de la pared)
K_ = (8.5, 19.0)            # quiebre del gambrel (abajo del techo)
P_ = (0.0, 23.4)            # cumbrera (abajo del techo)
ROOF_T, STEP = 0.42, 0.11   # espesor del techo y escalón de cada hilada de tejuelas
OVH, OVH_Z = 1.0, 1.0       # alero lateral (a lo largo del faldón) y sobre los hastiales


def roof_u(x):
    """Línea de abajo del techo (y) en x."""
    a = abs(x)
    if a >= K_[0]:
        return E_[1] + (E_[0] - a) * (K_[1] - E_[1]) / (E_[0] - K_[0])
    return K_[1] + (K_[0] - a) * (P_[1] - K_[1]) / K_[0]


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


def cols_side():
    return [-16.0 + k * B for k in range(25)]


def cols_gable():
    return [-11.4] + [-12.0 + k * B for k in range(1, 18)] + [11.4]


# ---------------------------------------------------------------- paredes de costado
def side_wall(mk, side):
    s = -1 if side == "L" else 1
    j = cols_side()
    SILL, HEAD = 5.0, 7.4
    wa, wb = (j[7], j[9]), (j[15], j[17])                     # ventanas: z -6,67..-4 y 4..6,67
    if side == "L":
        base = [(-16.0, 5.0), (-12.6, 6.9), (-9.6, 5.3), (wa[0], 6.3), (wa[1], 6.0), (-1.2, 7.0), (1.8, 5.2),
                (wb[0], 6.2), (wb[1], 6.5), (9.4, 5.1), (12.8, 6.8), (16.0, 5.6)]
    else:
        base = [(-16.0, 6.6), (-13.0, 5.1), (-10.2, 6.8), (wa[0], 5.6), (wa[1], 6.9), (-1.0, 5.3), (2.2, 6.7),
                (wb[0], 5.8), (wb[1], 6.4), (9.8, 5.0), (13.2, 6.6), (16.0, 5.4)]
    lo = notch(notch(base, *wa, SILL), *wb, SILL)
    hi = notch(notch(base, *wb, HEAD), *wa, HEAD)
    frags = {}
    for i, (u0, u1) in enumerate(((-16.0, j[6]), (j[6], j[12]), (j[12], j[18]), (j[18], 16.0))):
        frags[f"frag{i + 1:02d}"] = (u0, u1, GROUND, lo)
    for i, (u0, u1) in enumerate(((-16.0, j[5]), (j[5], j[11]), (j[11], j[19]), (j[19], 16.0))):
        frags[f"frag{i + 5:02d}"] = (u0, u1, hi, TOP)
    wall = BoardWall(mk, f"Barn_WallSide_{side}", "zy", s * 12.0, s, j, frags, top=lambda u: 12.0)
    wall.build()
    for w in (wa, wb):
        wall.casing(w[0], w[1], SILL, HEAD)
    # esquineros crema: de costado (tapan el canto del hastial) y de frente (siguen el techo)
    for zs in (-1, 1):
        zc = 16.0 * zs
        xa, xb = s * 12.05, s * 11.2
        za, zb = zc + zs * 0.12, zc - zs * 0.01
        for a, b, (o,) in wall.segments([zc - zs * 0.4], 0.0, 12.0):
            part = wall.parts[o]
            u0, u1 = sorted((zc + zs * 0.1, zc - zs * 0.9))
            ya = 0.02 if a < 0.01 else a + GAP                   # 0,02 arriba del piso: cara de abajo no coplanar
            yb = 11.95 if b >= 11.99 else b - GAP
            wall.box(part, u0, u1, ya, yb, -0.015, 0.15, CREAM)
            fa = 0.04 if a < 0.01 else a + GAP + 0.03            # el de frente, corrido 0,03: sin caras coplanares
            pts = []
            for x in (xa, xb):
                fb = roof_u(x) - 0.05 if b >= 11.99 else b - GAP - 0.03
                for z in (za, zb):
                    pts += [(x, fa, z), (x, fb, z)]
            mk.hull(part, pts, CREAM, detail=True)
    # tablas que faltan abajo (se ve adentro) y pintura saltada al pie
    col = lambda c: (j[c] + j[c + 1]) / 2
    if side == "L":
        wall.hole(col(3), -0.5, 1.6, jag=((0.3, 0.35), (0.65, -0.1)))
        wall.hole(col(19), -0.5, 1.1, jag=((0.5, 0.4),))
        for c, h, sd in ((10, 1.1, 3), (22, 0.9, 1)):
            wall.chip(col(c), h, sd)
    else:
        wall.hole(col(10), -0.5, 1.9, jag=((0.25, -0.2), (0.6, 0.3)))
        wall.hole(col(21), -0.5, 1.2, jag=((0.4, 0.3),))
        for c, h, sd in ((2, 1.0, 2), (16, 0.9, 6)):
            wall.chip(col(c), h, sd)
    return wall


# ---------------------------------------------------------------- hastiales
def gable_front(mk):
    j = cols_gable()
    c1_l = [(-11.4, 5.0), (-9.2, 6.8), (-6.4, 5.3), (-4.0, 6.4)]
    c2_l = [(-11.4, 12.5), (-8.8, 11.7), (-6.2, 12.9), (-4.0, 12.3)]
    c1_r = [(4.0, 5.6), (6.6, 6.9), (9.0, 5.2), (11.4, 6.3)]
    c2_r = [(4.0, 12.4), (6.4, 13.0), (8.8, 11.8), (11.4, 12.6)]
    hl0, hl1 = j[8], j[10]                                   # pajar: x ±1,333, y 13,2-16,8
    head = [(-4.0, 12.3), (-2.6, 12.9), (hl0, 12.5), (hl0, 13.2), (hl1, 13.2), (hl1, 12.6), (2.7, 12.1), (4.0, 12.4)]
    frags = {
        "frag01": (-11.4, -4.0, GROUND, c1_l),
        "frag02": (-11.4, -4.0, c1_l, c2_l),
        "frag03": (4.0, 11.4, GROUND, c1_r),
        "frag04": (4.0, 11.4, c1_r, c2_r),
        "frag05": (-4.0, 4.0, [(-4.0, 10.0), (4.0, 10.0)], head),
        "frag06": (-11.4, hl0, c2_l + [(-2.6, 12.9), (hl0, 12.5)], TOP),
        "frag07": (hl1, 11.4, [(hl1, 12.6), (2.7, 12.1)] + c2_r, TOP),
        "frag08": (hl0, hl1, [(hl0, 16.8), (hl1, 16.8)], TOP),
    }
    wall = BoardWall(mk, "Barn_Gable_Front", "xy", -16.0, -1, j, frags, top=roof_u, breaks=(-K_[0], 0.0, K_[0]))
    wall.build()
    wall.casing(hl0, hl1, 13.2, 16.8, wd=0.3)
    for c, h, sd in ((-10.0, 0.9, 2), (6.0, 1.0, 0)):
        wall.chip(c, h, sd)
    # riel del portón (hierro, en el dintel) y viga del pajar con roldana (en la punta)
    hdr = wall.parts["frag05"]
    mk.box(hdr, (0, 10.68, -16.235), (17.4, 0.25, 0.25), IRON, detail=True)
    for x in (-8.55, 8.55):                                               # topes del riel
        mk.box(hdr, (x, 10.68, -16.3), (0.12, 0.45, 0.36), IRON, detail=True)
    top = wall.parts["frag08"]
    mk.box(top, (0, 22.05, -17.7), (0.75, 0.75, 3.5), DARK, detail=True)
    mk.box(top, (0, 21.45, -19.0), (0.4, 0.5, 0.46), IRON, detail=True)            # roldana
    mk.cyl(top, (0, 21.45, -19.0), 0.34, 0.22, IRON, axis="x", sides=8, detail=True)
    mk.hull(top, [(x, y, z) for x in (-0.06, 0.06) for y, z in ((21.2, -18.95), (21.2, -19.05), (20.6, -19.08),
                                                                 (20.42, -18.88), (20.6, -18.75))], IRON,
            detail=True)                                                   # gancho
    return wall


def gable_back(mk):
    j = cols_gable()
    c1 = [(-11.4, 5.0), (-8.6, 6.8), (-5.7, 5.2), (-2.6, 6.9), (0.4, 5.4), (3.3, 7.0), (6.2, 5.3), (9.0, 6.6),
          (11.4, 5.4)]
    c2 = [(-11.4, 12.3), (-8.0, 13.1), (-4.5, 12.2), (-1.0, 13.6), (2.4, 12.6), (5.8, 13.4), (8.8, 12.2),
          (11.4, 12.6)]
    spans = [((-11.4, -4.0), GROUND, c1), ((-4.0, 4.0), GROUND, c1), ((4.0, 11.4), GROUND, c1),
             ((-11.4, j[7]), c1, c2), ((j[7], j[13]), c1, c2), ((j[13], 11.4), c1, c2),
             ((-11.4, j[10]), c2, TOP), ((j[10], 11.4), c2, TOP)]
    frags = {f"frag{i + 1:02d}": (u0, u1, bot, tp) for i, ((u0, u1), bot, tp) in enumerate(spans)}
    wall = BoardWall(mk, "Barn_Gable_Back", "xy", 16.0, 1, j, frags, top=roof_u, breaks=(-K_[0], 0.0, K_[0]))
    wall.build()
    wall.hole((j[4] + j[5]) / 2, -0.5, 1.4, jag=((0.4, 0.3),))
    for c, h, sd in ((2.0, 1.0, 4),):
        wall.chip(c, h, sd)
    return wall


# ---------------------------------------------------------------- techo gambrel
def roof_profiles():
    """Perfiles (x, y) del lado derecho: faldón bajo y alto, con las hileras escalonadas.
    Devuelve (bajo, alto, hileras_bajo, hileras_alto, punto de la cumbrera afuera)."""
    d_lo = v_unit(E_, K_)
    n_lo = (d_lo[1], -d_lo[0])
    d_up = v_unit(K_, P_)
    n_up = (d_up[1], -d_up[0])
    e_ext = v_add(E_, d_lo, -OVH)
    o_k = intersect(v_add(K_, n_lo, ROOF_T), d_lo, v_add(K_, n_up, ROOF_T), d_up)
    o_p = intersect(v_add(K_, n_up, ROOF_T), d_up, (0.0, 0.0), (0.0, 1.0))
    base = v_add(e_ext, n_lo, ROOF_T)
    s_k = v_dot((o_k[0] - base[0], o_k[1] - base[1]), d_lo)
    nr = max(1, round(s_k / 1.45))
    lo_out, lo_rows = [], []
    for i in range(nr):
        a = v_add(v_add(base, d_lo, s_k * i / nr), n_lo, STEP)
        b = v_add(base, d_lo, s_k * (i + 1) / nr)
        lo_out += [a, b]
        lo_rows.append((a, b))
    lo = [e_ext, K_] + lo_out[::-1]
    m_p = v_dot((o_p[0] - o_k[0], o_p[1] - o_k[1]), d_up)
    nu = max(1, round(m_p / 1.45))
    up_out, up_rows = [], []
    for i in range(nu):
        a = v_add(o_k, d_up, m_p * i / nu)
        if i > 0:
            a = v_add(a, n_up, STEP)
        b = v_add(o_k, d_up, m_p * (i + 1) / nu)
        up_out += [a, b]
        up_rows.append((a, b))
    up = [K_, P_] + up_out[::-1]
    return clean(lo), clean(up), lo_rows, up_rows, o_p, d_up, n_up


Z_BAYS = [(-16.0 - OVH_Z, -8.0), (-8.0, 0.0), (0.0, 8.0), (8.0, 16.0 + OVH_Z)]


def roof_half(mk, side):
    s = -1 if side == "L" else 1
    lo, up, lo_rows, up_rows, o_p, d_up, n_up = roof_profiles()
    mx = lambda pts: [(s * x, y) for x, y in pts] if s > 0 else [(s * x, y) for x, y in pts][::-1]
    n = 1
    for prof, rows in ((lo, lo_rows), (up, up_rows)):
        for z0, z1 in Z_BAYS:
            part = mk.part(f"Barn_Roof_{side}_frag{n:02d}", (0, 0, 0))
            mk.prism(part, mx(prof), z1 - z0, BARE, plane="xy", center=(0, 0, (z0 + z1) / 2))
            # tejuelas wood_dark; el escalón de cada hilera (mira hacia abajo) en hierro: línea oscura fina
            for i, (a, b) in enumerate(rows):
                c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                mk.paint(part, DARK, box=((s * c[0], c[1], (z0 + z1) / 2), (0.3, 0.3, z1 - z0 + 0.5)))
                if i > 0:                                                    # escalón: de la hilera de abajo a esta
                    lip = rows[i - 1][1]
                    c2 = ((a[0] + lip[0]) / 2, (a[1] + lip[1]) / 2)
                    mk.paint(part, IRON, box=((s * c2[0], c2[1], (z0 + z1) / 2), (0.06, 0.06, z1 - z0 + 0.5)))
            if prof is up:                                                   # cumbrera: tabla de remate
                q = v_add(o_p, d_up, -0.75)
                cap = [(0.0, o_p[1] - 0.02), (0.0, o_p[1] + 0.2), v_add(q, n_up, 0.16), v_add(q, n_up, -0.02)]
                # 0,005 más corta en cada punta: sus tapas no quedan coplanares con las del techo
                mk.hull(part, [(s * x, y, z) for x, y in cap for z in (z0 + 0.005, z1 - 0.005)], DARK, detail=True)
            n += 1


# ---------------------------------------------------------------- estructura que queda en pie
def beam(mk, part, a, b, w, h, mat=DARK, z=None):
    """Viga recta de a a b (puntos (x, y)) en el plano z, sección w (en z) x h (perpendicular)."""
    d = v_unit(a, b)
    nrm = (-d[1], d[0])
    pts = []
    for p in (a, b):
        for k in (-0.5, 0.5):
            q = v_add(p, nrm, k * h)
            for dz in (-w / 2, w / 2):
                pts.append((q[0], q[1], z + dz))
    mk.hull(part, pts, mat)


def frame(mk):
    part = mk.part("fixed_Frame", (0, 0, 0))
    bents = [-15.0, -8.0, 0.0, 8.0, 15.0]
    d_lo, d_up = v_unit(E_, K_), v_unit(K_, P_)
    n_lo, n_up = (d_lo[1], -d_lo[0]), (d_up[1], -d_up[0])
    RH = 0.5
    off = RH / 2 + 0.02                         # cabios: la cara de arriba queda 0,02 debajo del techo
    for zb in bents:
        for s in (-1, 1):
            m = lambda p: (s * p[0], p[1])
            mk.box(part, (s * 11.0, 6.0, zb), (0.8, 12.0, 0.8), DARK)                        # poste
            a = v_add((11.9, roof_u(11.9)), n_lo, -off)                                     # cabio bajo (apoya en la carrera)
            k1 = v_add(v_add(K_, n_lo, -off), d_lo, 0.3)
            beam(mk, part, m(a), m(k1), 0.55, RH, z=zb)
            k2 = v_add(v_add(K_, n_up, -off), d_up, -0.3)                                   # cabio alto
            p = v_add(P_, n_up, -off)
            beam(mk, part, m(k2), m(p), 0.5, RH, z=zb)
            beam(mk, part, (s * 10.75, 8.4), (s * 8.6, 10.55), 0.45, 0.4, z=zb)             # jabalcón
        mk.box(part, (0, 10.8, zb), (21.9, 0.8, 0.7), DARK)                                  # tirante
        mk.box(part, (0, K_[1] - 0.95, zb), (2 * K_[0] + 0.4, 0.6, 0.62), DARK)              # nudillo
    for x in (-4.4, 4.4):                                                                   # postes del portón
        mk.box(part, (x, 5.21, -15.0), (0.8, 10.42, 0.76), DARK)
    for s in (-1, 1):
        mk.box(part, (s * 11.0, 11.75, 0), (0.78, 0.7, 30.76), DARK)                       # carrera (no al ras de los postes)
        mk.box(part, (s * 11.17, 4.0, 0), (0.42, 0.5, 30.7), DARK)                         # cinturones
        mk.box(part, (s * 11.17, 8.0, 0), (0.42, 0.5, 30.7), DARK)
        c = v_add(K_, n_up, -0.72)                                                          # correa del quiebre
        mk.box(part, (s * c[0], c[1], 0), (0.6, 0.6, 30.7), DARK)
    mk.box(part, (0, P_[1] - 0.586 - 0.25, 0), (0.6, 0.6, 30.7), DARK)                     # correa de cumbrera


# ---------------------------------------------------------------- pajar
LOFT_Z = (-15.4, 1.0)


def loft(mk):
    za, zb = LOFT_Z
    xa = 10.6
    # 6 tramos de piso: 3 a lo largo de Z (cortes en juntas de tablas) x 2 (corte en escalera a lo ancho)
    zcuts = [za, -9.4, -3.4, zb]
    stair = [0.4, -0.6, 0.9, -0.3, 0.6, -0.8, 0.2, 0.8, -0.5, 0.5, -0.2, 0.7, -0.7, 0.3]
    board = 1.6
    n = 1
    parts = []
    for i in range(3):
        z0, z1 = zcuts[i], zcuts[i + 1]
        rows = []
        z = z0
        k = int((z0 - za) / board)
        while z < z1 - 1e-6:
            zz = min(z + board, z1)
            rows.append((z, zz, stair[k % len(stair)]))
            z, k = zz, k + 1
        for side in (-1, 1):
            pts = []
            if side < 0:
                pts = [(-xa, z0), (-xa, z1)]
                for a, b, x in reversed(rows):
                    pts += [(x, b), (x, a)]
            else:
                pts = [(xa, z1), (xa, z0)]
                for a, b, x in rows:
                    pts += [(x, a), (x, b)]
            part = mk.part(f"Barn_Loft_frag{n:02d}", (0, 0, 0))
            parts.append((part, side, z0, z1))
            mk.prism(part, clean(pts), 0.4, BARE, plane="xz", center=(0, 11.8, 0))
            for zs in [a for a, _, _ in rows[1:]]:                       # juntas de las tablas (arriba)
                for dz in (-0.03, 0.03):
                    mk.slice(part, (0, 12.0, zs + dz), (0, 0, 1))
                mk.paint(part, DARK, box=((0, 12.0, zs), (30, 0.02, 0.07)))
            for x in (-9.2, -6.2, -3.2, 3.2, 6.2, 9.2):                     # vigas del piso (lejos del corte)
                if (x < 0) == (side < 0):
                    mk.box(part, (x, 11.4, (z0 + z1) / 2), (0.5, 0.4, z1 - z0 - 0.04), DARK, detail=True)
            n += 1
    # escalera apoyada en el borde del pajar
    lad = mk.part(f"Barn_Loft_frag{n:02d}", (0, 0, 0))
    n += 1
    bot, top = (3.75, 0.12), (zb + 0.08, 13.4)
    for x in (-7.8, -6.2):
        beam_z(mk, lad, x, bot, top, 0.24, 0.24, BARE)
    nrung = 11
    for i in range(nrung):
        f = (i + 0.7) / (nrung + 0.4)
        z = bot[0] + (top[0] - bot[0]) * f
        y = bot[1] + (top[1] - bot[1]) * f
        mk.box(lad, (-7.0, y, z), (1.66, 0.14, 0.16), DARK)
    # fardos (un fragmento)
    hb = mk.part(f"Barn_Loft_frag{n:02d}", (0, 0, 0))
    for c, axis in (((-7.5, 12.0, -13.6), "x"), ((-7.5, 12.0, -11.9), "x"), ((-7.5, 13.6, -12.75), "x"),
                    ((6.5, 12.0, -10.0), "z"), ((2.6, 12.0, -14.2), "x")):
        bale(mk, hb, c, axis)


def beam_z(mk, part, x, a, b, w, h, mat):
    """Larguero de a=(z, y) a b=(z, y) en x, sección w (x) por h."""
    d = v_unit(a, b)
    nrm = (-d[1], d[0])
    pts = []
    for p in (a, b):
        for k in (-0.5, 0.5):
            q = v_add(p, nrm, k * h)
            for dx in (-w / 2, w / 2):
                pts.append((x + dx, q[1], q[0]))
    mk.hull(part, pts, mat)


def bale(mk, part, c, axis):
    L, S, CH = 3.0, 1.6, 0.18
    h = S / 2
    sec = [(-h, 0.0), (h, 0.0), (h, S - CH), (h - CH, S), (-h + CH, S), (-h, S - CH)]
    pts = []
    for u in (-L / 2, L / 2):
        for v, y in sec:
            pts.append((c[0] + u, c[1] + y, c[2] + v) if axis == "x" else (c[0] + v, c[1] + y, c[2] + u))
    mk.hull(part, pts, HAY)


# ---------------------------------------------------------------- puertas
def cross_x(mk, part, lo, hi, box2, zf, w):
    """Cruz en el paño lo-hi: diagonal entera (sale 0,06) y la otra en dos brazos (0,05) que se meten
    0,12 debajo de la primera. Las puntas se recortan contra box2 (se meten en el marco)."""
    (xa, ya), (xb, yb) = lo, hi
    mid = ((xa + xb) / 2, (ya + yb) / 2)
    d1 = clip(strip2d((xa, ya), (xb, yb), w), box2)
    mk.hull(part, [(x, y, z) for x, y in d1 for z in (zf + 0.02, zf - 0.06)], CREAM, detail=True)
    for a, b in (((xa, yb), mid), (mid, (xb, ya))):
        d = v_unit((xa, yb), (xb, ya))
        a2 = v_add(a, d, -1.0) if a != mid else v_add(a, d, -0.12)
        b2 = v_add(b, d, 0.12) if b == mid else v_add(b, d, 1.0)
        arm = clip(strip2d(a2, b2, w, ext=0.0), box2)
        mk.hull(part, [(x, y, z) for x, y in arm for z in (zf + 0.025, zf - 0.05)], CREAM, detail=True)


def barn_door(mk, name, x0, x1):
    """Hoja corrediza: tablas rojas, marco y cruz crema, dos colgadores con roldana en el riel."""
    xc = (x0 + x1) / 2
    zf, zb = -16.47, -16.17                 # cara de afuera y de atrás
    y0, y1 = 0.05, 10.45
    part = mk.part(name, (xc, 0, (zf + zb) / 2))
    mk.box(part, (xc, (y0 + y1) / 2, (zf + zb) / 2), (x1 - x0, y1 - y0, zb - zf), RED)
    for k in (1, 2, 3):                                                  # juntas de las tablas
        x = x0 + (x1 - x0) * k / 4
        for dx in (-0.03, 0.03):
            mk.slice(part, (x + dx, 0, 0), (1, 0, 0))
        mk.paint(part, DARK, box=((x, 5, zf), (0.062, 12, 0.02)))
    sw = 0.45
    # marco crema: montantes (salen 0,1), travesaños entre montantes (0,08) y cruz en cada paño (diagonal
    # 0,06, el otro brazo partido 0,05). Cada nivel se mete distinto en la hoja: sin caras coplanares.
    for xa, xb in ((x0, x0 + sw), (x1 - sw, x1)):
        mk.hull(part, [(x, y, z) for x in (xa, xb) for y in (y0, y1) for z in (zf + 0.01, zf - 0.1)], CREAM, detail=True)
    for ya, yb in ((y0 + 0.02, y0 + 0.47), (y1 - 0.47, y1 - 0.02), (5.0, 5.45)):
        mk.hull(part, [(x, y, z) for x in (x0 + sw - 0.02, x1 - sw + 0.02) for y in (ya, yb)
                       for z in (zf + 0.015, zf - 0.08)], CREAM, detail=True)
    for ya, yb in ((y0 + 0.47, 5.0), (5.45, y1 - 0.47)):
        box2 = rect(x0 + sw - 0.04, x1 - sw + 0.04, ya - 0.04, yb + 0.04)
        mid = (xc, (ya + yb) / 2)
        cross_x(mk, part, (x0 + sw, ya), (x1 - sw, yb), box2, zf, 0.4)
    for xh in (x0 + 0.7, x1 - 0.7):                                       # colgadores
        mk.box(part, (xh, 10.3, zf - 0.025), (0.22, 1.3, 0.06), IRON, detail=True)
        mk.box(part, (xh, 10.94, -16.33), (0.22, 0.12, 0.33), IRON, detail=True)
        mk.cyl(part, (xh, 10.96, -16.235), 0.16, 0.16, IRON, axis="z", sides=8, detail=True)


def hayloft_door(mk):
    x0, x1, y0, y1 = -1.45, 1.45, 13.08, 16.92
    zf, zb = -16.47, -16.21                 # por delante del marco crema (sale hasta -16,19)
    part = mk.part("HayloftDoor", (x0, y0, (zf + zb) / 2))
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (zf + zb) / 2), (x1 - x0, y1 - y0, zb - zf), RED)
    for k in (1, 2):
        x = x0 + (x1 - x0) * k / 3
        for dx in (-0.03, 0.03):
            mk.slice(part, (x + dx, 0, 0), (1, 0, 0))
        mk.paint(part, DARK, box=((x, 15, zf), (0.062, 5, 0.02)))
    sw = 0.32
    for xa, xb in ((x0, x0 + sw), (x1 - sw, x1)):
        mk.hull(part, [(x, y, z) for x in (xa, xb) for y in (y0, y1) for z in (zf + 0.01, zf - 0.1)], CREAM, detail=True)
    for ya, yb in ((y0 + 0.02, y0 + 0.34), (y1 - 0.34, y1 - 0.02)):
        mk.hull(part, [(x, y, z) for x in (x0 + sw - 0.02, x1 - sw + 0.02) for y in (ya, yb)
                       for z in (zf + 0.015, zf - 0.08)], CREAM, detail=True)
    a, b = (x0 + sw, y0 + 0.34), (x1 - sw, y1 - 0.34)                     # una diagonal (de la bisagra hacia arriba)
    d1 = clip(strip2d(a, b, 0.34), rect(a[0] - 0.04, b[0] + 0.04, a[1] - 0.04, b[1] + 0.04))
    mk.hull(part, [(x, y, z) for x, y in d1 for z in (zf + 0.02, zf - 0.06)], CREAM, detail=True)
    for y in (13.75, 16.25):                                              # bisagras de pletina
        strap = [(x0 - 0.12, y - 0.1), (x0 + 1.3, y - 0.05), (x0 + 1.42, y), (x0 + 1.3, y + 0.05), (x0 - 0.12, y + 0.1)]
        mk.prism(part, strap, 0.05, IRON, plane="xy", center=(0, 0, zf - 0.125), detail=True)
        mk.cyl(part, (x0 - 0.06, y, zf - 0.05), 0.07, 0.4, IRON, axis="y", sides=6, detail=True)


def build(mk):
    side_wall(mk, "L")
    side_wall(mk, "R")
    gable_front(mk)
    gable_back(mk)
    roof_half(mk, "L")
    roof_half(mk, "R")
    frame(mk)
    loft(mk)
    barn_door(mk, "DoorL", -4.1, 0.0)
    barn_door(mk, "DoorR", 0.0, 4.1)
    hayloft_door(mk)

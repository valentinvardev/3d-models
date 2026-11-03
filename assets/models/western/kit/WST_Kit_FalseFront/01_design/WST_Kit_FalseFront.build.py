"""
Receta de WST_Kit_FalseFront, las falsas fachadas del kit modular (prompt 008, Bloques A + C).

Brief
- Silueta a 40 studs: el remate de la calle. Contorno de arriba bien distinto en cada variante (recto,
  escalonado, arco), cornisa oscura que sobresale 0,4 con ménsulas debajo, y la banda lisa del cartel.
- Grilla: 8 de ancho (calzan una al lado de la otra), 0,6 de espesor (z de -0,3 a +0,3; la cornisa sale
  hasta -0,7 y 0,06 atrás), origen abajo al centro en y = 0 (va arriba de la pared de 10). Las cuatro
  variantes en fila sobre X cada 8 (x = 0, 8, 16, 24), cada una con su origen en su base al centro.
- Tablas: el mismo perfil que WST_Kit_Wall (frente de -0,27 a -0,21 por tabla de 0,8: escalón de 0,06),
  paint_cream recoloreable, junta oscura de 0,06 bajo cada labio. Abajo una tabla de remate wood_dark de
  0,4 que tapa el encuentro con la pared. Atrás wood_mid liso (lo ven los pistoleros desde el techo).
- Cornisa wood_dark: friso (0,45 de alto, 0,06 afuera de las tablas) + tapa con moldura que sale 0,4
  adelante; ménsulas de 0,2 en x = ±1, ±3 (entre módulos vecinos siguen cada 2). Banda del cartel
  6 x 1,6 (y 1,2-2,8), lisa, 0,06 afuera de las tablas, con borde wood_dark de 0,12 pintado (el texto
  va como decal en Studio).
- Variantes: Flat (4 de alto), Stepped (centro 6 en |x| <= 1,8, escalón 4 hasta |x| = 3,2, puntas 3),
  Arched (arco rebajado: 4 en los costados, 5,5 al centro, radio 6,08), Corner (Flat con un retorno de
  2 hacia atrás por el lado +X, esquinero wood_dark y la cornisa que da vuelta).
- Fragmentos: 4 por variante. Las de frente son franjas verticales cortadas en escalera por los
  empalmes (caras de corte wood_light); en la esquina el retorno es el cuarto. Cornisa, friso,
  ménsulas y banda se cortan en el mismo x que las tablas que tapan: ningún fragmento se mete en otro.
- Nombres: <Variante>_fragNN (como WST_Kit_Wall).
- Inferido: tabla de remate abajo, perfil de la cornisa y ménsulas, anchos de los escalones, altura de
  la banda, retorno de la esquina por el lado +X (para la otra esquina haría falta su espejo).

Técnica: todo lo de la base de un fragmento (tablas, friso, tapa, banda) se encima sin cuidado y el
primer `carve` del fragmento (el corte en escalera) lo une: con `use_self` la booleana funde los cascos
y desaparecen las caras coplanares (medido: friso y tapa como detalle daban z-fighting contra las
puntas de las tablas; en la base, cero).

Vueltas: 1) Flat: z-fighting de la tapa contra el tope de las tablas (las dos en y = 4) -> tablas 0,15
más abajo, metidas en la tapa · 2) seguía el z-fighting en las puntas (friso y tapa como detalle contra
las caras de corte) -> todo a la base, la booleana lo une · 3) las cuatro variantes; en la escalonada,
dos prismas de tablas que se tocaban justo en el escalón rompían la booleana (14 bordes con giro
invertido) -> se enciman 0,01 · 4) revisión de capturas (arco con un parche oscuro: es de normales,
ver Revisión).

Revisión
- Triángulos por pieza (con sus 4 fragmentos) contra 300 de referencia: Flat 990, Stepped 1327,
  Arched 1184, Corner 956. Calidad primero: cornisa con friso, tapa moldurada y ménsulas (~80 por
  fragmento), banda con borde, tablas escalonadas con juntas y los cortes en escalera cerrados
  (~40 por fragmento, caras ocultas mientras está entera). Hay menos falsas fachadas que paredes
  (una o dos por edificio). Con cortes rectos en vez de escalera bajaría ~150 por pieza.
- Medidas: 8,000 de ancho (Corner 8,4: retorno, esquinero y la tapa que sale 0,4 al costado),
  alto 4 / 6 / 5,5 / 4, espesor 0,6 + cornisa (z de -0,7 a 0,36; Corner hasta 1,76 por el retorno).
  Apoyadas en y = 0, origen en la base al centro de cada una.
- Fragmentos: 4 por pieza, el mayor 30 % del volumen; ningún fragmento se mete en otro (cornisa y
  banda cortadas en el mismo x que las tablas).
- Avisos aceptados: 1 borde suelto ("wire") en Flat_frag03 y Arched_frag04 (resto de un corte, sin cara).
- Bug de herramienta (no de la receta): process_model deja las normales personalizadas que crea el
  import glTF; después de soldar/disolver/re-triangular decodifican mal. En el GLB final quedan 52 de
  13 284 esquinas con la normal desviada (casi todas en caras de corte ocultas); se ve como un parche
  oscuro en el friso del arco (x = +1,2..1,9). Borrando las normales personalizadas sale limpio.
"""

import math

W = 8.0
ZB = 0.30
PAINT, BARE, SEAM, FRESH = "paint_cream", "wood_mid", "wood_dark", "wood_light"
NK = 8                                    # hiladas 0..7 (hasta 6,0)
SINK = 0.15                               # las tablas terminan 0,15 abajo del tope, adentro de la tapa


def course(k):
    if k == 0:
        return 0.0, 0.4
    return 0.4 + 0.8 * (k - 1), 0.4 + 0.8 * k


def course_at(y):
    return next(k for k in range(NK) if course(k)[0] <= y < course(k)[1] + 1e-6)


def zfront(k, y):
    y0, _ = course(k)
    return -0.31 if k == 0 else -0.27 + 0.06 * (y - y0) / 0.8


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
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 1e-9:
                out.pop(i)
                changed = True
                break
    return out


def profile(ytop, back=ZB, mapz=lambda z: z):
    """Perfil de las hiladas desde y = 0 hasta ytop. mapz pasa la z del frente a otra coordenada (retorno)."""
    pts = []
    for k in range(course_at(ytop - 1e-6) + 1):
        y0, y1 = course(k)
        y1 = min(y1, ytop)
        pts += [(mapz(zfront(k, y0)), y0), (mapz(zfront(k, y1)), y1)]
    return clean(pts + [(back, ytop), (back, 0.0)])


def cap_profile(Y):
    """Tapa de la cornisa (z, y): moldura que sale 0,4 adelante del friso y 0,06 atrás."""
    return [(-0.70, Y), (0.36, Y), (0.36, Y - 0.28), (-0.34, Y - 0.34), (-0.70, Y - 0.14)]


BRACKET = [(-0.32, -0.30), (-0.64, -0.15), (-0.60, -0.42), (-0.46, -0.62), (-0.32, -0.78)]


class Facade:
    """Fachada de frente: fragmentos como intervalos de x por hilada; levels = [(xa, xb, Y)] con el alto
    de la tapa de cada tramo; arch = puntos [(x, Y)] de la tapa si el borde de arriba es curvo."""

    def __init__(self, mk, name, ox, frags, levels, arch=None):
        self.mk, self.name, self.ox, self.frags = mk, name, ox, frags
        self.levels, self.arch = levels, arch
        self.parts = {}
        for fname, iv in frags.items():
            ks = sorted(iv)
            assert ks == list(range(ks[0], ks[-1] + 1)), f"{name} {fname}: hiladas salteadas"
        for k in range(NK):
            spans = sorted(iv[k] for iv in frags.values() if k in iv)
            for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
                assert a1 <= b0 + 1e-6, f"{name} hilada {k}: se pisan"

    def neighbour(self, fname, k, x):
        return any(k in iv and (abs(iv[k][0] - x) < 1e-6 or abs(iv[k][1] - x) < 1e-6)
                   for n, iv in self.frags.items() if n != fname)

    def owners(self, y, xa, xb):
        """Tramos [a, b] de [xa, xb] por fragmento, según la hilada que contiene la altura y."""
        k = course_at(y)
        out = []
        for fname, iv in self.frags.items():
            if k in iv:
                a, b = max(xa, iv[k][0]), min(xb, iv[k][1])
                if b - a > 1e-6:
                    out.append((self.parts[fname], a, b))
        return out

    def build(self):
        mk, ox = self.mk, self.ox
        for fname, iv in self.frags.items():
            ks = sorted(iv)
            k0, k1 = ks[0], ks[-1]
            xmin = min(a for a, _ in iv.values())
            xmax = max(b for _, b in iv.values())
            part = mk.part(f"{self.name}_{fname}", (ox, 0, 0))
            self.parts[fname] = part
            top = 0.0
            for xa, xb, Y in self.levels:                   # un prisma de tablas por tramo de altura
                a, b = max(xa, xmin), min(xb, xmax)
                if b - a > 1e-6:
                    # entre tramos se encima 0,01 (dos caras justo opuestas rompían la booleana)
                    a -= 0.01 if a > xmin + 1e-6 else 0.0
                    b += 0.01 if b < xmax - 1e-6 else 0.0
                    mk.prism(part, profile(Y - SINK), b - a, PAINT, plane="zy", center=(ox + (a + b) / 2, 0, 0))
                    top = max(top, Y)
            ybot, ytop = -0.5, top + 0.5
            for side in (1, -1):                            # corte en escalera de cada lado
                edge = xmax if side > 0 else xmin
                xs = [(iv[k][1] if side > 0 else iv[k][0]) for k in ks]
                if all(abs(x - edge) < 1e-6 for x in xs):
                    continue
                pts = []
                for k, x in zip(ks, xs):
                    if abs(x - edge) < 1e-6:
                        x = edge + side * 0.5
                    y0, y1 = course(k)
                    pts += [(ox + x, ybot if k == k0 else y0), (ox + x, ytop if k == k1 else y1)]
                far = ox + edge + side * 1.0
                pts += [(far, ytop), (far, ybot)]
                mk.carve(part, FRESH, prism=dict(profile=clean(pts), depth=2.0, plane="xy", center=(0, 0, 0)))
            if self.arch:                                   # borde de arriba curvo: la línea de la tapa
                pts = [(ox + x, y) for x, y in self.arch]
                pts += [(ox + self.arch[-1][0] + 1, self.arch[-1][1]), (ox + self.arch[-1][0] + 1, 9.0),
                        (ox + self.arch[0][0] - 1, 9.0), (ox + self.arch[0][0] - 1, self.arch[0][1])]
                mk.carve(part, SEAM, prism=dict(profile=clean(pts), depth=2.0, plane="xy", center=(0, 0, 0)))
            mk.paint(part, SEAM, box=((ox, 0.2, -0.31), (W + 0.2, 0.4, 0.02)))          # tabla de remate
            mk.paint(part, BARE, box=((ox, 5.0, ZB), (W + 0.2, 10.2, 0.02)))            # atrás
            for k in range(1, NK):
                s = course(k)[0]
                if s < top - SINK - 0.05:
                    mk.slice(part, (ox, s - 0.06, 0), (0, 1, 0))
                    if k > 1:
                        mk.paint(part, SEAM, box=((ox, s - 0.03, -0.25), (W + 0.2, 0.062, 0.1)))
            for k in ks:                                    # empalmes del corte
                y0, y1 = course(k)
                for x, d in ((iv[k][0], 1), (iv[k][1], -1)):
                    if abs(abs(x) - W / 2) < 1e-6 or not self.neighbour(fname, k, x):
                        continue
                    mk.slice(part, (ox + x + d * 0.035, 0, 0), (1, 0, 0))
                    mk.paint(part, SEAM, box=((ox + x + d * 0.0175, (y0 + y1) / 2 - 0.005, -0.25), (0.037, y1 - y0 - 0.01, 0.1)))

    # ---- cornisa, ménsulas, banda y desgaste ------------------------------------------------------
    def cornice(self, xa, xb, Y, ends=(0.0, 0.0)):
        """Friso + tapa recta de xa a xb a la altura Y. ends: cuánto sobresale (o se mete) cada punta."""
        mk, ox = self.mk, self.ox
        for part, a, b in self.owners(Y - 0.01, xa, xb):
            ea = ends[0] if abs(a - xa) < 1e-6 else 0.0
            eb = ends[1] if abs(b - xb) < 1e-6 else 0.0
            fa, fb = (a - min(ea, 0.0), b + min(eb, 0.0))
            mk.box(part, (ox + (fa + fb) / 2, Y - 0.525, -0.24), (fb - fa, 0.45, 0.18), SEAM)        # friso (sin extender)
            mk.hull(part, [(ox + x, y, z) for x in (a - ea, b + eb) for z, y in cap_profile(Y)], SEAM)

    def cornice_curve(self, pts):
        """Friso + tapa por tramos rectos sobre una curva [(x, Y), ...] (el arco)."""
        mk, ox = self.mk, self.ox
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for part, a, b in self.owners(min(y0, y1) - 0.01, x0, x1):
                ya = y0 + (y1 - y0) * (a - x0) / (x1 - x0)
                yb = y0 + (y1 - y0) * (b - x0) / (x1 - x0)
                mk.hull(part, [(ox + x, y + dy, z) for x, y in ((a, ya), (b, yb)) for dy in (-0.75, -0.3)
                               for z in (-0.33, -0.15)], SEAM)
                mk.hull(part, [(ox + x, y + dy, z) for x, y in ((a, ya), (b, yb)) for z, dy in cap_profile(0.0)], SEAM)

    def brackets(self, xs, Y):
        mk, ox = self.mk, self.ox
        for x in xs:
            (part, a, b), = self.owners(Y - 0.5, x - 0.1, x + 0.1)
            assert b - a > 0.19, f"{self.name}: la ménsula en {x} cruza un corte"
            mk.prism(part, [(z, Y + y) for z, y in BRACKET], 0.2, SEAM, plane="zy", center=(ox + x, 0, 0))

    def band(self, xa, xb, ya, yb):
        """Banda lisa del cartel, 0,06 afuera de las tablas, con borde oscuro pintado de 0,12."""
        mk, ox = self.mk, self.ox
        for part, a, b in self.owners((ya + yb) / 2, xa, xb):
            mk.box(part, (ox + (a + b) / 2, (ya + yb) / 2, -0.24), (b - a, yb - ya, 0.18), PAINT)
            for y in (ya + 0.12, yb - 0.12):
                mk.slice(part, (ox, y, 0), (0, 1, 0))
            for x in (xa + 0.12, xb - 0.12):
                if a < x < b:
                    mk.slice(part, (ox + x, 0, 0), (1, 0, 0))
            for (cx, cy), (sx, sy) in ((((a + b) / 2, ya + 0.06), (b - a, 0.12)), (((a + b) / 2, yb - 0.06), (b - a, 0.12)),
                                       ((xa + 0.06, (ya + yb) / 2), (0.12, yb - ya)), ((xb - 0.06, (ya + yb) / 2), (0.12, yb - ya))):
                mk.paint(part, SEAM, box=((ox + cx, cy, -0.33), (sx + 0.002, sy + 0.002, 0.02)))

    def notch(self, k, x, side):
        """Esquina rota arriba en la punta de una tabla (side = +1 si la tabla sigue hacia +x)."""
        mk, ox = self.mk, self.ox
        (part, _, _), = self.owners(course(k)[0] + 0.3, x + side * 0.25, x + side * 0.35)
        _, y1 = course(k)
        tri = [(ox + x - side * 0.1, y1 + 0.03), (ox + x + side * 0.5, y1 + 0.03), (ox + x - side * 0.1, y1 - 0.42)]
        mk.carve(part, SEAM, prism=dict(profile=tri, depth=0.4, plane="xy", center=(0, 0, -0.33)))


def strips(b1, b2, b3, nk, lo=-4.0, hi=4.0):
    return {"frag01": {k: (lo, b1[k]) for k in range(nk)}, "frag02": {k: (b1[k], b2[k]) for k in range(nk)},
            "frag03": {k: (b2[k], b3[k]) for k in range(nk)}, "frag04": {k: (b3[k], hi) for k in range(nk)}}


def build(mk):
    # ---------------- FalseFront_Flat: 4 de alto ----------------
    flat = Facade(mk, "FalseFront_Flat", 0.0, strips((-2.3, -1.9, -2.1, -2.1, -1.8, -1.8), (0.3, -0.1, 0.2, 0.2, -0.4, -0.4),
                                                    (2.2, 2.5, 1.9, 1.9, 2.3, 2.3), 6), [(-4, 4, 4.0)])
    flat.build()
    flat.cornice(-4, 4, 4.0)
    flat.brackets((-3, -1, 1, 3), 4.0)
    flat.band(-3, 3, 1.2, 2.8)
    flat.notch(1, -0.1, 1)

    # ---------------- FalseFront_Stepped: puntas 3, escalón 4, centro 6 ----------------
    b1 = (-2.2, -1.9, -2.3, -2.3, -2.4, -2.4)
    b2 = (0.2, -0.2, 0.1, 0.1, -0.3, 0.2, 0.3, 0.3)
    b3 = (2.1, 2.4, 2.2, 2.2, 2.5, 2.5)
    st = Facade(mk, "FalseFront_Stepped", 8.0, {
        "frag01": {k: (-4, b1[k]) for k in range(6)},
        "frag02": {k: (b1[k] if k < 6 else -2.4, b2[k]) for k in range(8)},
        "frag03": {k: (b2[k], b3[k] if k < 6 else 2.5) for k in range(8)},
        "frag04": {k: (b3[k], 4) for k in range(6)},
    }, [(-4, -3.2, 3.0), (-3.2, -1.8, 4.0), (-1.8, 1.8, 6.0), (1.8, 3.2, 4.0), (3.2, 4, 3.0)])
    st.build()
    st.cornice(-4, -3.2, 3.0, ends=(0.0, 0.05))           # la punta se mete 0,05 en el escalón de al lado
    st.cornice(-3.2, -1.8, 4.0, ends=(0.1, 0.05))         # y sobresale 0,1 sobre el escalón de abajo
    st.cornice(-1.8, 1.8, 6.0, ends=(0.1, 0.1))
    st.cornice(1.8, 3.2, 4.0, ends=(0.05, 0.1))
    st.cornice(3.2, 4, 3.0, ends=(0.05, 0.0))
    st.brackets((-2.8, 2.8), 4.0)
    st.brackets((-1, 1), 6.0)
    st.band(-3, 3, 1.2, 2.8)
    st.notch(1, -1.9, 1)

    # ---------------- FalseFront_Arched: arco rebajado, 4 a los costados y 5,5 al centro ----------------
    R, cy = 6.0833, -0.5833
    arch = [(x, cy + math.sqrt(R * R - x * x)) for x in [-4 + 0.8 * i for i in range(11)]]
    ar = Facade(mk, "FalseFront_Arched", 16.0, strips((-2.3, -1.9, -2.1, -2.1, -1.9, -1.9, -1.9, -1.9),
                                                      (0.2, -0.2, 0.1, 0.1, -0.3, 0.3, 0.3, 0.3),
                                                      (2.2, 2.5, 1.9, 1.9, 2.1, 2.1, 2.1, 2.1), 8),
                [(-4, 4, 5.5)], arch=arch)
    ar.build()
    ar.cornice_curve(arch)
    ar.band(-3, 3, 1.2, 2.8)
    ar.notch(4, -1.9, 1)

    # ---------------- FalseFront_Corner: Flat con retorno de 2 hacia atrás por +X ----------------
    co = Facade(mk, "FalseFront_Corner", 24.0, {
        "frag01": {k: (-4, b) for k, b in enumerate((-1.6, -1.2, -1.4, -1.4, -1.25, -1.25))},
        "frag02": {k: (a, b) for k, (a, b) in enumerate(zip((-1.6, -1.2, -1.4, -1.4, -1.25, -1.25),
                                                            (1.3, 0.9, 1.1, 1.1, 1.5, 1.5)))},
        "frag03": {k: (a, 3.5) for k, a in enumerate((1.3, 0.9, 1.1, 1.1, 1.5, 1.5))},
    }, [(-4, 3.5, 4.0)])
    co.build()
    co.cornice(-4, 3.5, 4.0)
    co.brackets((-3, -1, 1, 3), 4.0)
    co.band(-3, 3, 1.2, 2.8)
    co.notch(1, 0.9, 1)
    corner_return(mk, 24.0, 4.0)


def corner_return(mk, ox, Y):
    """Retorno de la esquina (frag04): pared de 0,5 de x = 3,5 a 4,0 que va de z = -0,3 a 1,7, esquinero y
    cornisa que da vuelta. Las tablas miran a +X."""
    part = mk.part("FalseFront_Corner_frag04", (ox, 0, 0))
    X = lambda z: ox + 3.7 - z                                     # z del frente de la pared -> x del retorno
    mk.prism(part, profile(Y - SINK, back=ox + 3.5, mapz=X), 2.0, PAINT, plane="xy", center=(0, 0, 0.7))
    mk.box(part, (ox + 3.77, (Y - 0.7) / 2, 0.045), (0.54, Y - 0.7, 0.81), SEAM)                 # esquinero
    mk.box(part, (ox + 3.925, Y - 0.525, 0.7), (0.21, 0.45, 2.0), SEAM)                          # friso del lado
    mk.box(part, (ox + 3.77, Y - 0.525, -0.24), (0.54, 0.45, 0.18), SEAM)                        # friso del frente
    side = [(4.4, Y), (3.44, Y), (3.44, Y - 0.28), (4.04, Y - 0.34), (4.4, Y - 0.14)]
    mk.hull(part, [(ox + x, y, z) for x, y in side for z in (-0.70, 1.76)], SEAM)               # tapa del lado
    mk.hull(part, [(ox + x, y, z) for x in (3.5, 4.4) for z, y in cap_profile(Y)], SEAM)        # tapa del frente
    mk.prism(part, [(ox + 3.7 - z, Y + y) for z, y in BRACKET], 0.2, SEAM, plane="xy", center=(0, 0, 1.0))
    mk.carve(part, SEAM, prism=dict(profile=[(1.75, 2.03), (1.2, 2.03), (1.75, 1.55)], depth=1.0, plane="zy",
                                    center=(ox + 3.75, 0, 0)))                                  # esquina rota atrás
    mk.paint(part, SEAM, box=((ox + 4.01, 0.2, 0.7), (0.02, 0.4, 2.2)))                          # tabla de remate
    mk.paint(part, BARE, box=((ox + 3.5, 2.0, 0.7), (0.02, 4.2, 2.2)))                           # adentro
    for k in range(1, NK):
        s = course(k)[0]
        if s < Y - SINK - 0.05:
            mk.slice(part, (ox, s - 0.06, 0), (0, 1, 0))
            if k > 1:
                mk.paint(part, SEAM, box=((ox + 3.95, s - 0.03, 0.7), (0.1, 0.062, 2.2)))

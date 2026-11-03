"""
Receta de WST_Kit_Wall, las paredes de tablas del kit modular (prompt 007, Bloques A + C).

Brief
- Silueta a 40 studs: un paño de 8 x 10 con tablas horizontales escalonadas (clapboard) que dan una
  línea de sombra cada 0,8, zócalo oscuro abajo y, según la variante, el hueco de ventana o puerta.
- Grilla del kit: 8 de ancho (X), 10 de alto, 0,6 de espesor (z de -0,3 a +0,3), origen abajo al centro,
  cara de afuera hacia -Z. Las cinco variantes van en fila sobre X cada 8 (se tocan: así se ve que
  calzan), cada una con su origen en su base al centro.
- Hiladas: zócalo 0-0,6 (wood_dark, sobresale a -0,30), tablas de 0,8 desde 0,6 hasta 9,4, tabla de remate
  9,4-10. Así el alféizar (3) y el dintel de la ventana (7) caen en una junta.
- Cada tabla: frente inclinado de -0,27 (abajo) a -0,21 (arriba) => escalón de 0,06 en cada junta.
  Afuera paint_cream (una sola pintura, se recolorea por edificio); adentro wood_mid con juntas
  wood_dark cada 0,8 (pintadas, sin geometría).
- Fragmentos: cada uno es una franja de hiladas (prisma con el perfil de las tablas) recortada en
  escalera: el corte sigue las juntas de las tablas (horizontales) y los empalmes (verticales), así la
  rotura ya se intuye como una diagonal de empalmes. Las caras de corte son wood_light (madera fresca).
  Los empalmes del corte se pintan como línea wood_dark de 0,07.
- Desgaste (distinto en cada variante): una tabla floja y caída (ranura tallada + tabla girada 3°),
  una esquina rota, pintura saltada en el borde de abajo (tallado poco profundo que muestra wood_mid) y
  una tabla reemplazada sin pintar (wood_light).
- Nombres: <Variante>_fragNN (Blender no permite dos objetos con el mismo nombre; en Studio cada
  variante es su propio Model y el prefijo los separa).
- Inferido: perfil exacto del zócalo, alturas de hiladas, posición de las dos ventanas de la doble
  (2,4 de ancho, centros en x = ±1,8: pilares de 1,0 afuera y 1,2 al medio), agujero de la rota en las
  hiladas 2,2-5,4 (3,2 de alto, ~2,9 de ancho), cortes de los fragmentos y nombres con prefijo.

Técnica: cada fragmento es UN prisma (perfil de tablas en zy) recortado con dos cortadores en escalera
(prisma xy no convexo). Así no hay cascos encimados ni caras coplanares adentro, y los dos fragmentos
vecinos comparten exactamente el mismo escalón. Las juntas y empalmes son `slice` + `paint`
(process_model vuelve a unir las caras del mismo color: cuestan casi nada).

Vueltas: 1) Wall_Plain sola: las juntas horizontales no se veían de frente (solo con sombra proyectada),
saltaduras como "agujeros de ratón", tabla reemplazada como placa · 2) las cinco variantes; franja oscura
de 0,06 bajo cada labio (un solo corte por junta sirve afuera y adentro: 936 -> 836 en la lisa) ·
3) saltaduras como franja dentada a lo largo del borde de abajo, tabla reemplazada de empalme a borde,
empalmes sueltos para cortar las hiladas largas · 4) la saltadura que tocaba un corte de fragmento
rompía la malla (booleana coplanar): ahora se valida; tabla reemplazada de la lisa hasta el borde.

Revisión
- Triángulos por pieza (todos sus fragmentos) contra 400 de referencia: Plain 890, Window 966,
  Door 872, DoubleWindow 724, Cracked 782. Calidad primero: ~40 % son las caras de corte en escalera
  (cada fragmento cerrado, Bloque C) y el resto las 13 hiladas escalonadas con sus juntas. Sin las
  juntas de adentro bajaría ~80 por pieza (se dejaron: el saloon se defiende desde adentro).
- Medidas: cada variante 8,000 x 10,000 x 0,600, apoyada en y = 0, origen en su base al centro
  (x = 0, 8, 16, 24, 32). Las hiladas son iguales en todas: calzan entre sí (se ve en la fila).
- Fragmentos: 6 por pieza (4 la rota), el mayor 38,6 % del volumen (antepecho de la doble), ninguno
  menor a 0,57 de espesor. Los cortes al lado de un hueco no lo rodean (la colisión de casco no tapa
  la ventana para saltar).
- Huecos: ventana 3 x 4 con alféizar a 3, puerta 4 x 7,5, dobles de 2,4 x 4. Las caras del hueco son
  wood_light (madera cortada): el marco del kit las tapa.
- El kit de ventanas (WST_Kit_Window) es para el hueco de 3 x 4: los de 2,4 de la doble no tienen
  ventana propia (decide Valentin si suma una variante angosta).
"""

import math

W = 8.0                                  # módulo
ZB = 0.30                                # cara de adentro
PAINT, BARE, SEAM, FRESH = "paint_cream", "wood_mid", "wood_dark", "wood_light"
SEAMS = [0.6 + 0.8 * i for i in range(12)]   # juntas entre hiladas (0,6 ... 9,4)


def course(k):
    """Hilada k: 0 = zócalo, 1..11 = tablas de 0,8, 12 = remate."""
    if k == 0:
        return 0.0, 0.6
    if k == 12:
        return 9.4, 10.0
    return 0.6 + 0.8 * (k - 1), 0.6 + 0.8 * k


def front(k):
    y0, y1 = course(k)
    if k == 0:
        return [(-0.30, 0.0), (-0.30, 0.48), (-0.27, 0.6)]
    return [(-0.27, y0), (-0.225 if k == 12 else -0.21, y1)]


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


def profile(k0, k1):
    pts = []
    for k in range(k0, k1 + 1):
        pts += front(k)
    return clean(pts + [(ZB, course(k1)[1]), (ZB, course(k0)[0])])


class Wall:
    """Una variante: fragmentos definidos como intervalos de x por hilada ({k: (x0, x1)}, x local)."""

    def __init__(self, mk, name, ox, frags):
        self.mk, self.name, self.ox, self.frags = mk, name, ox, frags
        self.parts = {}
        self._check()

    def _check(self):
        for fname, iv in self.frags.items():
            ks = sorted(iv)
            assert ks == list(range(ks[0], ks[-1] + 1)), f"{self.name} {fname}: hiladas salteadas"
            for k, (a, b) in iv.items():
                assert b - a >= 0.3, f"{self.name} {fname} hilada {k}: tramo de {b - a:.2f}"
        for k in range(13):
            spans = sorted(iv[k] for iv in self.frags.values() if k in iv)
            for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
                assert a1 <= b0 + 1e-6, f"{self.name} hilada {k}: se pisan {a0, a1} y {b0, b1}"

    def neighbour(self, fname, k, x):
        return any(k in iv and (abs(iv[k][0] - x) < 1e-6 or abs(iv[k][1] - x) < 1e-6)
                   for n, iv in self.frags.items() if n != fname)

    def build(self):
        mk, ox = self.mk, self.ox
        for fname, iv in self.frags.items():
            ks = sorted(iv)
            k0, k1 = ks[0], ks[-1]
            xmin = min(a for a, _ in iv.values())
            xmax = max(b for _, b in iv.values())
            part = mk.part(f"{self.name}_{fname}", (ox, 0, 0))
            self.parts[fname] = part
            mk.prism(part, profile(k0, k1), xmax - xmin, PAINT, plane="zy", center=(ox + (xmin + xmax) / 2, 0, 0))
            ybot, ytop = course(k0)[0] - 0.5, course(k1)[1] + 0.5
            for side in (1, -1):           # recorte en escalera de cada lado
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
            # zócalo oscuro
            mk.paint(part, SEAM, box=((ox, 0.3, -0.285), (W + 0.2, 0.6, 0.04)))
            # adentro: madera sin pintar. Juntas: franja oscura de 0,06 bajo cada labio, afuera (donde cae
            # la sombra de la tabla de arriba) y adentro; un solo corte por junta sirve para las dos caras
            mk.paint(part, BARE, box=((ox, 5.0, ZB), (W + 0.2, 10.2, 0.02)))
            for s in SEAMS:
                if course(k0)[0] + 0.05 < s <= course(k1)[1] + 0.001:
                    mk.slice(part, (ox, s - 0.06, 0), (0, 1, 0))
                    mk.paint(part, SEAM, box=((ox, s - 0.03, ZB), (W + 0.2, 0.062, 0.02)))
                    if s > 0.7:
                        mk.paint(part, SEAM, box=((ox, s - 0.03, -0.25), (W + 0.2, 0.062, 0.1)))
            # empalmes del corte: línea oscura de 0,07 repartida entre los dos fragmentos
            for k in ks:
                y0, y1 = course(k)
                for x, d in ((iv[k][0], 1), (iv[k][1], -1)):
                    if abs(abs(x) - W / 2) < 1e-6 or not self.neighbour(fname, k, x):
                        continue
                    mk.slice(part, (ox + x + d * 0.035, 0, 0), (1, 0, 0))
                    mk.paint(part, SEAM, box=((ox + x + d * 0.0175, (y0 + y1) / 2 - 0.005, -0.25), (0.037, y1 - y0 - 0.01, 0.1)))

    def owner(self, k, x):
        for fname, iv in self.frags.items():
            if k in iv and iv[k][0] + 0.05 < x < iv[k][1] - 0.05:
                return self.parts[fname]
        raise ValueError(f"{self.name}: nadie cubre la hilada {k} en x={x}")

    # ---- desgaste ----------------------------------------------------------------------------------
    def sag(self, k, xa, xb, deg):
        """Tabla floja: se talla la ranura (se ve el forro oscuro) y se pone la tabla girada."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, (xa + xb) / 2)
        y0, y1 = course(k)
        yc, L = (y0 + y1) / 2, xb - xa
        mk.carve(part, SEAM, points=mk.pts_box((ox + (xa + xb) / 2, yc, -0.31), (L, y1 - y0, 0.38)))
        Lb = L - 0.06
        drop = (Lb / 2) * abs(math.sin(math.radians(deg)))
        prof = [(-0.30, -0.385), (-0.235, 0.385), (-0.11, 0.385), (-0.11, -0.385)]
        mk.prism(part, prof, Lb, PAINT, plane="zy", center=(ox + (xa + xb) / 2, yc - drop - 0.012, 0),
                 rot=(0, 0, deg), detail=True)

    def notch(self, k, x, side):
        """Esquina rota arriba en la punta de una tabla (side = +1 si la tabla sigue hacia +x)."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, x + side * 0.3)
        _, y1 = course(k)
        tri = [(ox + x - side * 0.1, y1 + 0.03), (ox + x + side * 0.55, y1 + 0.03), (ox + x - side * 0.1, y1 - 0.48)]
        mk.carve(part, SEAM, prism=dict(profile=tri, depth=0.4, plane="xy", center=(0, 0, -0.33)))

    def chip(self, k, xa, xb, seed=0):
        """Pintura gastada a lo largo del borde de abajo de una tabla (donde salpica el agua): franja
        chata de borde dentado, tallada poco profunda, que muestra wood_mid."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, (xa + xb) / 2)
        fname = next(f for f in self.frags if self.parts[f] == part)
        for kk in (k - 1, k):                           # sin tocar los cortes del fragmento (booleana coplanar)
            iv = self.frags[fname].get(kk)
            assert iv is None or (iv[0] + 0.05 < xa and xb < iv[1] - 0.05) or xb < iv[0] or xa > iv[1],                 f"{self.name}: la saltadura {k} {xa}..{xb} toca un corte"
        y0, _ = course(k)
        yb = y0 if k == 1 else y0 - 0.1
        n = max(3, int((xb - xa) / 0.3))
        hs = [0.07, 0.15, 0.09, 0.17, 0.06, 0.12, 0.08, 0.16]
        top = [(xb - (xb - xa) * (i + 0.5) / n, y0 + hs[(i + seed) % len(hs)]) for i in range(n)]
        pts = [(xa, yb), (xb, yb), (xb - 0.05, y0 + 0.05)] + top + [(xa + 0.05, y0 + 0.04)]
        mk.carve(part, BARE, prism=dict(profile=[(ox + a, b) for a, b in pts], depth=0.6, plane="xy",
                                        center=(0, 0, -0.537)))

    def joint(self, k, x):
        """Empalme de tablas sin corte de fragmento (rompe la regularidad de las hiladas largas)."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, x)
        y0, y1 = course(k)
        for d in (-0.035, 0.035):
            mk.slice(part, (ox + x + d, 0, 0), (1, 0, 0))
        mk.paint(part, SEAM, box=((ox + x, (y0 + y1) / 2 - 0.005, -0.25), (0.072, y1 - y0 - 0.01, 0.1)))

    def patch(self, k, xa, xb):
        """Tabla reemplazada, sin pintar: un tramo entero de tabla (de empalme a empalme o hasta el borde)."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, (xa + xb) / 2)
        fname = next(f for f in self.frags if self.parts[f] == part)
        iv = self.frags[fname][k]
        y0, y1 = course(k)
        ends = []
        for x, d in ((xa, 1), (xb, -1)):
            if iv[0] + 0.01 < x < iv[1] - 0.01:          # empalme propio si no cae en el borde del tramo
                self.joint(k, x)
                ends.append(x + d * 0.035)
            elif self.neighbour(fname, k, x):            # el empalme del corte ya está pintado
                ends.append(x + d * 0.035)
            else:                                        # borde del módulo o del hueco
                ends.append(x)
        a, b = ends
        for x in (a, b):
            if iv[0] + 0.001 < x < iv[1] - 0.001:      # cortar justo sobre la cara del borde rompe la malla
                mk.slice(part, (ox + x, 0, 0), (1, 0, 0))
        mk.paint(part, FRESH, box=((ox + (a + b) / 2, (y0 + y1) / 2 - 0.035, -0.25), (b - a, y1 - y0 - 0.07, 0.1)))


    def splinters(self, k, x, d, specs):
        """Punta rota de una tabla en el borde del agujero: astillas (pirámides) que salen de la punta x
        hacia d (+1/-1) y se doblan hacia adentro (+z), empujadas desde afuera. specs: (ya, yb, largo, y_punta)."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, x - d * 0.3)
        y0, _ = course(k)
        for i, (ya, yb, ln, yt) in enumerate(specs):
            xb = ox + x - d * (0.05 + 0.02 * i)
            base = [(xb, y0 + yy, zz) for yy in (ya, yb) for zz in (-0.26 + 0.075 * yy, -0.13)]
            mk.hull(part, base + [(ox + x + d * ln, y0 + yt, -0.17 + 0.03 * i)], FRESH, detail=True)

    def hanging(self, k, x, d, length, deg):
        """Tramo de tabla arrancado que quedó colgando de un clavo en la punta x (cuelga hacia d)."""
        mk, ox = self.mk, self.ox
        part = self.owner(k, x - d * 0.3)
        _, y1 = course(k)
        a = math.radians(deg)
        cx = ox + x + d * (length / 2 - 0.2) * math.cos(a)
        cy = y1 - 0.3 - (length / 2 - 0.2) * math.sin(a)
        prof = [(-0.30, -0.36), (-0.25, 0.36), (-0.17, 0.36), (-0.17, -0.36)]
        mk.prism(part, prof, length, PAINT, plane="zy", center=(cx, cy, 0), rot=(0, 0, -d * deg), detail=True)


def full(k0, k1, a=-4.0, b=4.0):
    return {k: (a, b) for k in range(k0, k1 + 1)}


def build(mk):
    # ---------------- Wall_Plain: 6 fragmentos, dos diagonales de empalmes que se cruzan ----------------
    plain = Wall(mk, "Wall_Plain", 0.0, {
        "frag01": {0: (-4, 0.9), 1: (-4, 0.6), 2: (-4, 0.2), 3: (-4, -0.3), 4: (-1.4, -0.7)},
        "frag02": {0: (0.9, 4), 1: (0.6, 4), 2: (0.2, 4), 3: (-0.3, 4), 4: (-0.7, 4), 5: (1.2, 4)},
        "frag03": {4: (-4, -1.4), 5: (-4, -0.6), 6: (-4, -0.2), 7: (-4, 0.4), 8: (-4, 0.1), 9: (-4, -2.0)},
        "frag04": {5: (-0.6, 1.2), 6: (-0.2, 4), 7: (0.4, 4), 8: (0.1, 1.0)},
        "frag05": {9: (-2.0, -0.8), 10: (-4, -0.3), 11: (-4, 0.5), 12: (-4, 0.2)},
        "frag06": {8: (1.0, 4), 9: (-0.8, 4), 10: (-0.3, 4), 11: (0.5, 4), 12: (0.2, 4)},
    })
    plain.build()
    plain.sag(6, -3.7, -1.3, -3)
    plain.notch(10, -0.3, 1)
    for k, a, b in ((1, -3.6, -2.0), (1, 1.4, 3.2), (2, -1.6, -0.6)):
        plain.chip(k, a, b, seed=k + int(a))
    plain.patch(3, 1.1, 4.0)
    for k, x in ((2, 2.6), (5, 2.9), (7, -2.6), (11, 2.4)):
        plain.joint(k, x)

    # ---------------- Wall_Window: hueco 3 x 4 (x ±1,5, y 3-7); antepecho y dintel en trapecio ----------------
    win = Wall(mk, "Wall_Window", 8.0, {
        "frag01": {0: (-4, -2.9), 1: (-4, -2.5), 2: (-4, -2.2), 3: (-4, -1.8), 4: (-4, -1.5), 5: (-4, -1.5),
                   6: (-4, -3.0)},
        "frag02": {0: (-2.9, 2.6), 1: (-2.5, 2.4), 2: (-2.2, 2.0), 3: (-1.8, 1.7)},
        "frag03": {0: (2.6, 4), 1: (2.4, 4), 2: (2.0, 4), 3: (1.7, 4), 4: (1.5, 4), 5: (1.5, 4), 6: (1.5, 4),
                   7: (2.7, 4)},
        "frag04": {6: (-3.0, -1.5), 7: (-4, -1.5), 8: (-4, -1.5), 9: (-4, -1.7), 10: (-4, -2.1), 11: (-4, -2.4),
                   12: (-4, -2.8)},
        "frag05": {9: (-1.7, 1.7), 10: (-2.1, 2.0), 11: (-2.4, 2.3), 12: (-2.8, 2.6)},
        "frag06": {7: (1.5, 2.7), 8: (1.5, 4), 9: (1.7, 4), 10: (2.0, 4), 11: (2.3, 4), 12: (2.6, 4)},
    })
    win.build()
    win.sag(2, -1.6, 0.8, 3)
    win.notch(10, -2.1, -1)
    for k, a, b in ((1, -3.8, -2.95), (1, -1.2, 0.6), (1, 2.75, 3.8)):
        win.chip(k, a, b, seed=int(a * 3))
    win.patch(5, 1.5, 4.0)
    for k, x in ((2, 3.1), (9, -3.0), (11, 3.2)):
        win.joint(k, x)

    # ---------------- Wall_Door: hueco 4 x 7,5 (x ±2); jambas en dos y dintel en dos ----------------
    door = Wall(mk, "Wall_Door", 16.0, {
        "frag01": {**full(0, 4, -4, -2), 5: (-4, -3.1)},
        "frag02": {**full(0, 5, 2, 4), 6: (3.0, 4)},
        "frag03": {5: (-3.1, -2), **full(6, 8, -4, -2), 9: (-4, -2.4), 10: (-4, -2.7), 11: (-4, -3.0), 12: (-4, -3.3)},
        "frag04": {6: (2, 3.0), **full(7, 8, 2, 4), 9: (2.3, 4), 10: (2.6, 4), 11: (2.9, 4), 12: (3.1, 4)},
        "frag05": {9: (-2.4, 0.1), 10: (-2.7, -0.3), 11: (-3.0, 0.4), 12: (-3.3, 0.0)},
        "frag06": {9: (0.1, 2.3), 10: (-0.3, 2.6), 11: (0.4, 2.9), 12: (0.0, 3.1)},
    })
    door.build()
    for f in ("frag05", "frag06"):                                   # el dintel arranca en 7,5
        mk.carve(door.parts[f], FRESH, points=mk.pts_box((16.0, 7.2, 0), (4.0, 0.6, 1.0)))
    door.sag(11, 1.0, 2.8, -3)
    door.notch(10, -0.3, 1)
    for k, a, b in ((1, -3.8, -2.4), (1, 2.3, 3.6)):
        door.chip(k, a, b, seed=int(a * 3))
    door.patch(7, -4.0, -2.0)
    for k, x in ((3, -3.0), (4, 3.0), (9, 3.1)):
        door.joint(k, x)

    # ---------------- Wall_DoubleWindow: dos huecos de 2,4 (x -3,0..-0,6 y 0,6..3,0, y 3-7) ----------------
    dbl = Wall(mk, "Wall_DoubleWindow", 24.0, {
        "frag01": {**full(0, 2), 3: (-3.4, 3.5)},
        "frag02": {3: (-4, -3.4), **full(4, 8, -4, -3.0), 9: (-4, -3.2)},
        "frag03": {**full(4, 8, -0.6, 0.6), 9: (-0.9, 0.7)},
        "frag04": {3: (3.5, 4), **full(4, 8, 3.0, 4)},
        "frag05": {9: (-3.2, -0.9), 10: (-4, -0.2), 11: (-4, 0.4), 12: (-4, 0.0)},
        "frag06": {9: (0.7, 4), 10: (-0.2, 4), 11: (0.4, 4), 12: (0.0, 4)},
    })
    dbl.build()
    dbl.sag(2, 1.0, 3.4, 3)
    dbl.notch(11, 0.4, 1)
    for k, a, b in ((1, -2.6, -1.0), (1, 1.6, 3.2), (2, -0.6, 0.6)):
        dbl.chip(k, a, b, seed=int(a * 3))
    dbl.patch(10, -4.0, -2.0)
    for k, x in ((1, -0.4), (11, 2.2), (12, -2.4)):
        dbl.joint(k, x)

    # ---------------- Wall_Cracked: Wall_Plain ya rota, agujero de ~2,9 x 3,2 a la altura del pecho; 4 fragmentos ----------------
    crk = Wall(mk, "Wall_Cracked", 32.0, {
        "frag01": {0: (-4, 0.5), 1: (-4, 0.2), 2: (-4, -0.2), 3: (-4, -1.1), 4: (-4, -1.6)},
        "frag02": {0: (0.5, 4), 1: (0.2, 4), 2: (-0.2, 4), 3: (0.8, 4), 4: (1.4, 4), 5: (1.5, 4)},
        "frag03": {5: (-4, -1.4), 6: (-4, -0.8), 7: (-4, 0.3), 8: (-4, -0.2), 9: (-4, 0.4), 10: (-4, 0.1),
                   11: (-4, -0.3), 12: (-4, 0.2)},
        "frag04": {6: (0.9, 4), 7: (0.3, 4), 8: (-0.2, 4), 9: (0.4, 4), 10: (0.1, 4), 11: (-0.3, 4), 12: (0.2, 4)},
    })
    crk.build()
    # puntas astilladas en el borde del agujero (izquierda: punta hacia +x; derecha: hacia -x)
    crk.splinters(3, -1.1, 1, [(0.05, 0.45, 0.45, 0.2), (0.35, 0.78, 0.25, 0.6)])
    crk.splinters(4, -1.6, 1, [(0.3, 0.78, 0.6, 0.5)])
    crk.splinters(5, -1.4, 1, [(0.05, 0.5, 0.35, 0.15), (0.4, 0.78, 0.5, 0.7)])
    crk.splinters(6, -0.8, 1, [(0.1, 0.6, 0.4, 0.25)])
    crk.splinters(3, 0.8, -1, [(0.3, 0.78, 0.55, 0.55)])
    crk.splinters(4, 1.4, -1, [(0.05, 0.4, 0.3, 0.1), (0.35, 0.78, 0.45, 0.45)])
    crk.splinters(5, 1.5, -1, [(0.1, 0.55, 0.6, 0.3)])
    crk.splinters(6, 0.9, -1, [(0.05, 0.4, 0.35, 0.1), (0.35, 0.78, 0.25, 0.6)])
    crk.hanging(5, -1.4, 1, 1.5, 32)
    crk.sag(8, 1.2, 3.4, -3)
    for k, a, b in ((1, -3.5, -2.1), (1, 1.0, 2.4), (2, 2.4, 3.6)):
        crk.chip(k, a, b, seed=int(a * 3))
    for k, x in ((2, -2.8), (9, -2.4), (11, 2.6)):
        crk.joint(k, x)

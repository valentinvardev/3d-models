"""
Receta de WST_Train_Wreck, los restos del descarrilamiento a la entrada de Hollow Creek (prompt 076,
Bloques A + B). Versiones rotas de la locomotora, el ténder y el vagón de carga, con las mismas medidas,
colores y ayudas (se importan sus recetas). Cobertura para pelear: los restos arman pasillos y alturas.

Brief
- Silueta a 40 studs: la locomotora acostada sobre su lado derecho con la trompa clavada 30° en la tierra
  y la cola levantada sobre el ténder volcado; chimenea doblada; un vagón de carga cruzado a 35° sobre la
  vía con un boquete; otro vagón acostado al fondo con las ruedas al aire; vía arrancada y durmientes sueltos.
- Medidas: huella de ~60 x 30 (z de -31 a 34, x de -15 a 17), origen al centro de la huella, en el suelo
  (y = 0). Las mismas medidas de los modelos sanos (caldera r 2,15, cabina de 7 x 8, vagón de 30 x 8,5).
- Piezas (todas con el origen en el centro de la huella): Wreck_Locomotive, Wreck_Tender, Wreck_CoalSpill,
  Wreck_Boxcar_A, Wreck_Boxcar_B, Wreck_Rails, Wreck_Debris.
- Técnica: un proxy de mk (XK) que aplica una rotación y traslación a todo lo que se construye; los prismas
  componen la rotación (los aros y medias coronas de la locomotora siguen funcionando). Sin pintura sobre
  piezas giradas (paint usa cajas alineadas): lo quemado y los marcos van como geometría.
- Inferido: lo que no se ve (las ruedas y la pared del lado que apoya en el suelo) no se modela; la
  locomotora pierde la campana y el vidrio del farol; el ténder conserva el bogie de atrás (el de adelante
  es el juego de ruedas de los escombros); el vagón A perdió los bogies (apoya en el suelo: el boquete queda a
  0,5 del suelo y se cruza caminando) y su puerta derecha (está en los escombros); el B conserva los dos bogies.

Vueltas: 1) primera versión: el panel reventado con carve (use_self funde los ~150 cascos de la locomotora:
4997 triángulos, al tope de 5000), la cola de la locomotora flotando a 12 de altura, el vagón A metido
dentro del B, el A sin bogies flotando a 2,95, durmientes cruzados coplanares, piezas sueltas que no tocaban
nada · 2) panel reventado armado sin booleana (tramo de caldera abierto arriba + núcleo de carbón + chapas
dobladas): 3112; la cola apoyada en la punta aplastada del vagón A (sobre sus bogies), el ténder volcado a la
izquierda de la vía, B corrido hasta tocar la punta de atrás de A · 3) perfiles del boquete recalculados para
el vagón sobre bogies (se cruzaban), rampa de tablas rotas para entrar, tablas colgando apoyadas en la pared,
puertas del hogar y de la caja de humo con la bisagra metida en su marco, terrones afuera del montón.

Revisión
- 7384 triángulos contra 7000 (+5 %), todas las piezas bajo 5000: locomotora 3112, vagón A 1510 (bogies 840),
  vagón B 1268 (bogies 840), ténder 654, vía 408, escombros 236, carbón 196.
- Huella 35,8 x 71,0 (pedía ~30 x 60): con 30° de trompa abajo la locomotora de 38 ocupa 33 de largo y su cola
  queda a 12 de altura; para que no flote se apoya en el vagón A, y el A cruzado a 35° más el B acostado
  detrás alargan la huella. Alto 24,4 (la cabina de la locomotora, de costado, arriba de todo).
- La trompa queda 3,8 bajo el suelo (y = 0): "clavada en la tierra".
- El boquete del vagón A va de la solera (2,95) a 8,8 con una rampa de tablas desde el suelo: se entra caminando
  y se sale por el hueco de la puerta perdida.
- Un aviso de "parte encerrada" en el vagón A (un casco chico adentro de otro): no se ve.
"""

import importlib.util
import math
import random
from pathlib import Path

from mathutils import Euler, Matrix, Vector


def _load(mid, folder="transport"):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(f"recipe_{mid}", root / folder / mid / "01_design" / f"{mid}.build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BX = _load("WST_Train_Boxcar")
T, L = BX.T, BX.L
B, bar, pipe, annulus, ring_pts = L.B, L.bar, L.pipe, L.annulus, L.ring_pts


def rot(x=0.0, y=0.0, z=0.0):
    return Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_matrix()


class XK:
    """mk con una transformación rígida p -> R p + t (coordenadas del juego). Se puede anidar."""

    def __init__(self, mk, R, t):
        self.mk, self.R, self.t = mk, R, Vector(t)

    @classmethod
    def place(cls, mk, R, pivot, where):
        """La transformación que lleva el punto local `pivot` a `where` con la rotación R."""
        return cls(mk, R, Vector(where) - R @ Vector(pivot))

    def P(self, p):
        return tuple(self.R @ Vector(p) + self.t)

    def pts_box(self, *a, **k):
        return self.mk.pts_box(*a, **k)

    def pts_cyl(self, *a, **k):
        return self.mk.pts_cyl(*a, **k)

    def pts_ball(self, *a, **k):
        return self.mk.pts_ball(*a, **k)

    def hull(self, part, points, mat, detail=False):
        self.mk.hull(part, [self.P(p) for p in points], mat, detail=detail)

    def box(self, part, center, size, mat, rot=(0, 0, 0), top=(1, 1), shift=(0, 0), detail=False):
        self.hull(part, self.mk.pts_box(center, size, rot, top, shift), mat, detail)

    def cyl(self, part, center, radius, length, mat, axis="y", sides=8, rot=(0, 0, 0), top=1.0, detail=False):
        self.hull(part, self.mk.pts_cyl(center, radius, length, axis, sides, rot, top), mat, detail)

    def ball(self, part, center, radius, mat, scale=(1, 1, 1), rot=(0, 0, 0), subdiv=1, detail=False):
        self.hull(part, self.mk.pts_ball(center, radius, scale, rot, subdiv), mat, detail)

    def _compose(self, center, r):
        m = self.R @ Euler([math.radians(a) for a in r], "XYZ").to_matrix()
        return self.P(center), tuple(math.degrees(a) for a in m.to_euler("XYZ"))

    def prism(self, part, profile, depth, mat, plane="xy", center=(0, 0, 0), rot=(0, 0, 0), detail=False):
        c, r = self._compose(center, rot)
        self.mk.prism(part, profile, depth, mat, plane=plane, center=c, rot=r, detail=detail)

    def carve(self, part, mat, points=None, prism=None):
        if points is not None:
            self.mk.carve(part, mat, points=[self.P(p) for p in points])
        else:
            c, r = self._compose(prism.get("center", (0, 0, 0)), prism.get("rot", (0, 0, 0)))
            self.mk.carve(part, mat, prism=dict(prism, center=c, rot=r))

    def marker(self, name, pos):
        self.mk.marker(name, self.P(pos))


# ---------------- ubicación de cada pieza en la huella ----------------
LOCO_R = rot(x=-30) @ rot(z=-90)               # acostada sobre su derecha y 30° de trompa abajo
LOCO_PIVOT, LOCO_AT = (3.6, 4.0, -6.0), (3.0, 1.45, -17.95)   # la trompa en la tierra, la cola sobre el vagón A
TENDER_R = rot(y=4) @ rot(z=60)                # volcado 60° hacia -X, a la izquierda de la vía
TENDER_PIVOT, TENDER_AT = (-4.0, 2.2, 0.0), (-5.2, 0.0, -5.0)
BOXA_R = rot(y=-35)                            # cruzado sobre la vía; la punta de adelante aplastada bajo la cabina
BOXA_AT = (0.16, 0.0, 13.54)
BOXB_R = rot(x=-90) @ rot(y=90)                # acostado, techo hacia -Z, largo en X
BOXB_PIVOT, BOXB_AT = (4.3, 0.0, 0.0), (0.0, 0.0, 40.4)
DROP = 0.0                                     # el vagón A sigue sobre sus bogies


# ======================= locomotora =======================
def wreck_loco(k, p):
    by, br, wy, wr = L.BOILER_Y, L.BOILER_R, L.WT_Y, L.WT_R
    k.cyl(p, (0, by, (-9.8 - 4.6) / 2), br, 5.2, "gunmetal", axis="z", sides=12)
    k.cyl(p, (0, by, (-1.4 + 1.05) / 2), br - 0.002, 2.45 + 0.04, "gunmetal", axis="z", sides=12)
    arc = [math.radians(a) for a in range(-135, 136, 30)]                                        # chapa sin el lado de arriba
    outer = [((br - 0.01) * math.cos(a), by + (br - 0.01) * math.sin(a)) for a in arc]
    inner = [(0.86 * br * math.cos(a), by + 0.86 * br * math.sin(a)) for a in reversed(arc)]
    k.prism(p, [(x, y) for x, y in outer + inner], 3.3, "gunmetal", plane="xy", center=(0, 0, -3.0), rot=(0, 0, 0))
    k.cyl(p, (0, by, -3.0), 0.88 * br, 3.4, "coal", axis="z", sides=10)                         # el carbón de adentro
    k.hull(p, ring_pts((0, by, 0.98), br - 0.003, "z", 12) + ring_pts((0, wy, 3.02), wr - 0.003, "z", 12), "gunmetal")
    k.cyl(p, (0, wy, (2.95 + 12.2) / 2), wr, 9.25, "gunmetal", axis="z", sides=12)
    for z, y, r in ((-9.25, by, br + 0.05), (0.98, by, br + 0.05), (8.7, wy, wr + 0.05)):
        k.cyl(p, (0, y, z), r, 0.22, "brass", axis="z", sides=12)
    k.cyl(p, (0, by, (L.Z_SMOKE_F + L.Z_SMOKE_B) / 2), L.SMOKE_R, L.Z_SMOKE_B - L.Z_SMOKE_F, "iron", axis="z", sides=12)
    k.cyl(p, (0, by, L.Z_SMOKE_F + 0.1), L.SMOKE_R + 0.06, 0.24, "brass", axis="z", sides=12)
    # puerta de la caja de humo arrancada de una bisagra: colgando torcida
    dk = XK.place(k, rot(y=-50), (1.6, by, L.Z_SMOKE_F + 0.04), (1.6, by, L.Z_SMOKE_F + 0.04))
    dk.cyl(p, (0, by, L.Z_SMOKE_F - 0.06), 1.75, 0.2, "iron", axis="z", sides=12)
    # panel reventado: hueco con el carbón adentro y chapas abiertas hacia afuera
    for a, b, c in (((-1.45, 8.1, -4.3), (-2.9, 8.9, -3.6), (-1.45, 8.15, -2.2)),
                    ((-1.45, 5.1, -4.0), (-3.0, 4.9, -2.6), (-1.45, 5.05, -1.9)),
                    ((-1.6, 6.6, -1.6), (-2.9, 6.9, -0.9), (-1.6, 6.0, -1.65))):
        n = (Vector(b) - Vector(a)).cross(Vector(c) - Vector(a)).normalized() * 0.05
        k.hull(p, [tuple(Vector(q) + n * s) for q in (a, b, c) for s in (-1, 1)], "gunmetal", detail=True)
    # chimenea doblada 40° desde su base (hacia el lado que queda arriba: asoma de la tierra)
    top_sb = by + L.SMOKE_R * L.FLAT
    sk = XK.place(k, rot(z=40), (0, top_sb + 0.3, L.STACK_Z), (0, top_sb + 0.3, L.STACK_Z))
    k.cyl(p, (0, top_sb + 0.05, L.STACK_Z), 1.05, 0.7, "iron", axis="y", sides=10, top=0.72)
    sk.cyl(p, (0, (top_sb + 11.3) / 2 + 0.1, L.STACK_Z), 0.58, 11.3 - top_sb - 0.1, "iron", axis="y", sides=10)
    sk.hull(p, ring_pts((0, 11.25, L.STACK_Z), 0.6, "y", 10) + ring_pts((0, 13.66, L.STACK_Z), 1.58, "y", 10), "iron")
    sk.hull(p, ring_pts((0, 13.62, L.STACK_Z), 1.555, "y", 10) + ring_pts((0, 14.74, L.STACK_Z), 1.08, "y", 10), "iron")
    annulus(sk, p, (0, 14.86, L.STACK_Z), 0.9, 1.2, 0.3, "iron", axis="y", sides=10)
    sk.cyl(p, (0, 14.8, L.STACK_Z), 0.95, 0.06, "coal", axis="y", sides=10)
    # domos (la campana se perdió) y farol sin vidrio
    L.dome(k, p, -5.6, by + br * 0.966, 0.78, 1.25)
    L.dome(k, p, 6.2, wy + wr * 0.966, 0.95, 1.2)
    ly0 = top_sb + 0.4
    k.box(p, (0, top_sb + 0.1, -14.38), (1.2, 0.7, 1.25), "iron")
    k.hull(p, [(x, y, -13.8) for x in (-0.78, 0.78) for y in (ly0, ly0 + 1.5)]
           + [(x, y, L.LAMP_Z) for x in (-0.95, 0.95) for y in (ly0 - 0.06, ly0 + 1.68)], "paint_red")
    k.cyl(p, (0, ly0 + 0.8, L.LAMP_Z + 0.02), 0.62, 0.1, "coal", axis="z", sides=10)
    k.hull(p, [(x, ly0 + 1.6, z) for x in (-1.05, 1.05) for z in (-15.48, -13.7)]
           + [(x, ly0 + 2.0, z) for x in (-0.35, 0.35) for z in (-14.95, -14.25)], "brass")
    # bastidor, cilindros, estribo (el del lado del suelo no se ve)
    for s in (-1, 1):
        B(k, p, s * 1.4, s * 1.72, 2.2, 3.6, -15.25, 18.9, "iron")
        cx = s * L.CYL_X
        k.cyl(p, (cx, L.CYL_Y, L.CYL_Z), L.CYL_R, L.CYL_L, "gunmetal", axis="z", sides=10)
        B(k, p, cx - 0.55, cx + 0.55, L.CYL_Y + 0.5, L.CYL_Y + 1.35, L.CYL_Z - 1.2, L.CYL_Z + 1.2, "gunmetal")
    B(k, p, -2.75, 2.75, 3.0, 5.2, -12.2, -9.63, "iron")
    B(k, p, -3.7, 3.7, 2.1, 3.3, -15.9, -15.2, "paint_red")
    B(k, p, -L.RB_X1, -L.RB_X0, L.RB_Y - 0.25, L.RB_Y, L.RB_Z0, L.Z_CAB_F + 0.05, "wood_dark")
    B(k, p, -1.5, 1.5, 3.2, 5.2, 4.3, 11.1, "gunmetal")
    # quitapiedras aplastado: barras dobladas hacia atrás y hacia un costado
    rnd = random.Random(3)
    for i in range(-5, 6, 2):
        x = 0.6 * i
        zb = L.Z_TIP + abs(x) / 3.5 * 3.1 + 1.4
        a = (x * 0.8, 0.8, zb)
        m = (x * 0.9 + rnd.uniform(-0.5, 0.5), 1.4 + rnd.uniform(0, 0.8), zb + 1.0 + rnd.uniform(0, 0.6))
        b = (x, 2.95, -15.95)
        bar(k, p, a, m, 0.16, 0.16, "paint_red", up=(0, 0, -1), ext=0.06)
        bar(k, p, m, b, 0.16, 0.16, "paint_red", up=(0, 0, -1), ext=0.06)
    bar(k, p, (-3.4, 0.7, -16.4), (1.2, 1.1, L.Z_TIP + 1.6), 0.2, 0.2, "paint_red", ext=0.1)
    bar(k, p, (1.2, 1.1, L.Z_TIP + 1.6), (3.4, 0.9, -16.6), 0.2, 0.2, "paint_red", ext=0.1)
    B(k, p, -3.6, 3.6, 2.8, 3.05, -16.1, -15.85, "paint_red")
    # ruedas del lado de arriba (izquierda), biela de acople doblada, biela motriz suelta
    for z in L.DRIVER_Z:
        L.spoked_wheel(k, p, (-L.RAIL_X, L.DRIVER_R, z), L.DRIVER_R, spokes=10, sides=12, rim_t=0, counter=None)
        k.cyl(p, (-1.2, L.DRIVER_R, z), 0.3, 2.5, "iron", axis="x", sides=8)
    a, b = (-2.94, L.DRIVER_R, L.DRIVER_Z[0] - 1.0), (-2.94, L.DRIVER_R, L.DRIVER_Z[1] - 1.0)
    m = (-3.3, L.DRIVER_R + 0.7, (a[2] + b[2]) / 2)
    bar(k, p, a, m, 0.14, 0.3, "steel_light", ext=0.08)
    bar(k, p, m, b, 0.14, 0.3, "steel_light", ext=0.08)
    for q in (a, b):
        k.cyl(p, (-2.8, q[1], q[2]), 0.25, 0.4, "steel_light", axis="x", sides=8)
    bar(k, p, (-3.11, L.DRIVER_R, b[2]), (-3.6, 0.6, -2.0), 0.14, 0.3, "steel_light", ext=0.1)
    for z in L.PILOT_Z:
        L.spoked_wheel(k, p, (-L.RAIL_X, L.PILOT_R, z), L.PILOT_R, spokes=6, sides=10, tire_t=0.3, rim_t=0, width=0.42,
                       hub_r=0.34)
        k.cyl(p, (-1.4, L.PILOT_R, z), 0.2, 2.2, "iron", axis="x", sides=6)
    B(k, p, -3.0, -2.8, 1.15, 1.75, -14.3, -7.5, "iron")
    B(k, p, -2.98, -1.3, 1.7, 2.15, -11.3, -10.5, "iron")
    # cabina: pared izquierda con ventanas, frente, piso, frente del hogar; techo arrancado a medias
    zf, zb_ = L.Z_CAB_F, L.Z_CAB_B
    B(k, p, -3.3, 3.3, 3.3, L.DECK_Y, zf, zb_, "iron")
    xo, xi = -L.CAB_X, -(L.CAB_X - 0.2)
    B(k, p, xi, xo, L.DECK_Y - 0.02, 7.15, zf, zb_, "paint_red")
    B(k, p, xi, xo, 10.35, L.EAVE_Y, zf, zb_, "paint_red")
    for z0, z1 in ((zf + 0.01, 11.45), (14.15, 15.25), (17.95, zb_ - 0.01)):
        B(k, p, xi - 0.01, xo + 0.005, 7.14, 10.36, z0, z1, "paint_red")
    for z0, z1 in ((zf - 0.04, zf + 0.26), (zb_ - 0.26, zb_ + 0.04)):
        B(k, p, -3.46, -3.59, L.DECK_Y - 0.03, L.EAVE_Y - 0.06, z0, z1, "wood_dark")
    B(k, p, -3.47, -3.57, 7.0, 7.2, zf - 0.02, zb_ + 0.02, "wood_dark")
    B(k, p, -3.47, -3.58, L.EAVE_Y - 0.4, L.EAVE_Y - 0.08, zf - 0.03, zb_ + 0.03, "wood_dark")
    B(k, p, -3.29, 3.29, L.DECK_Y - 0.02, 8.0, zf, zf + 0.2, "paint_red")
    B(k, p, -2.45, 2.45, 9.15, 11.0, zf + 0.01, zf + 0.19, "paint_red")
    B(k, p, -1.9, 1.9, L.DECK_Y - 0.02, wy, zf + 0.18, L.Z_BH - 0.05, "gunmetal")
    hk = XK.place(k, rot(y=-75), (-0.85, 5.05, L.Z_BH - 0.0), (-0.85, 5.05, L.Z_BH - 0.0))
    B(hk, p, -0.9, 0.8, 4.35, 5.75, L.Z_BH - 0.07, L.Z_BH + 0.05, "iron")                       # puerta del hogar abierta
    k.box(p, (0, 5.05, L.Z_BH), (1.5, 1.2, 0.2), "lamp_glow")                                    # brasas
    for i in range(4):                                                                           # quedan 4 chapas del techo
        xa = -L.ROOF_HALF + i * 2 * L.ROOF_HALF / 8
        xb = xa + 2 * L.ROOF_HALF / 8
        ya, yb = L.roof_top(xa), L.roof_top(xb)
        ang = math.atan2(yb - ya, xb - xa)
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        ln = math.hypot(xb - xa, yb - ya) + 0.04
        z0, z1 = (zf - 0.2, zb_ + 0.3) if i % 2 == 0 else (zf - 0.19, zb_ - 2.5 + i)
        k.box(p, (mx + math.sin(ang) * L.ROOF_T / 2, my - math.cos(ang) * L.ROOF_T / 2, (z0 + z1) / 2),
              (ln, L.ROOF_T, z1 - z0), "iron" if i else "wood_charred", rot=(0, 0, math.degrees(ang)))
    bar(k, p, (-0.3, L.roof_top(-0.3) - 0.1, 14.0), (2.6, 9.6, 16.8), 0.9, 0.16, "iron", ext=0.1)   # chapa colgando
    bar(k, p, (-1.0, L.roof_top(-1.0) - 0.1, zf + 0.2), (-0.2, 11.2, zf - 0.6), 0.25, 0.25, "wood_charred")


# ======================= ténder =======================
def wreck_tender(k, p):
    TX, LX, Y0, Y1, ZB, ZL, HZ = T.TANK_X, T.LEG_X, T.TANK_Y0, T.TANK_Y1, T.Z_BUNKER, T.Z_LEG, T.HZ
    u = [(-TX, ZL), (-LX, ZL), (-LX, ZB), (LX, ZB), (LX, ZL), (TX, ZL), (TX, HZ - 0.2), (-TX, HZ - 0.2)]
    k.prism(p, u, Y1 - Y0, "paint_red", plane="xz", center=(0, (Y0 + Y1) / 2, 0))
    for s in (-1, 1):
        for z0, z1 in ((ZL - 0.05, ZL + 0.22), (HZ - 0.45, HZ - 0.14)):
            B(k, p, s * (TX - 0.2), s * (TX + 0.06), Y0 + 0.02, Y1 - 0.02, z0, z1, "wood_dark")
        B(k, p, s * (TX - 0.12), s * (TX + 0.05), Y1 - 0.3, Y1 - 0.08, ZL + 0.2, HZ - 0.43, "wood_dark")
        B(k, p, s * 3.65, s * 4.05, 2.6, Y0 + 0.02, -HZ, HZ, "wood_dark")
    z_end = HZ - 4.5                                                                             # tabla del carbón rota
    k.hull(p, [(-x, y, z) for z in (ZL - 0.02, z_end) for x, y in
               ((TX - 0.14, Y1 - 0.04), (TX - 0.02, Y1 - 0.04), (TX + 0.13, 7.5), (TX + 0.25, 7.5))], "wood_dark")
    k.hull(p, [(x, y, z) for z in (ZL - 0.02, HZ - 0.19) for x, y in
               ((TX - 0.14, Y1 - 0.04), (TX - 0.02, Y1 - 0.04), (TX + 0.13, 7.5), (TX + 0.25, 7.5))], "wood_dark")
    for z0, z1 in ((-HZ, -HZ + 0.45), (HZ - 0.45, HZ)):
        B(k, p, -3.99, 3.99, 2.2, Y0 + 0.005, z0 + 0.005, z1 - 0.005, "paint_red")
    B(k, p, -LX - 0.02, LX + 0.02, Y0 - 0.02, L.DECK_Y, -HZ - 0.02, ZB + 0.02, "iron")
    B(k, p, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, T.TRUCK_Z[1] - 0.45, T.TRUCK_Z[1] + 0.45, "wood_dark")
    k.hull(p, [(x, L.DECK_Y - 0.02, z) for x in (-LX, LX) for z in (ZB - 0.02, ZB - 3.0)]
           + [(x, 5.6, ZB - 0.02) for x in (-LX + 0.4, LX - 0.4)] + [(0, 5.0, ZB - 1.8)], "coal")   # lo que quedó
    T.truck(k, p, T.TRUCK_Z[1])
    k.cyl(p, (0, 6.92, 5.6), 0.78, 0.3, "iron", axis="y", sides=8)                                 # boca del agua


def coal_spill(mk, p):
    rnd = random.Random(11)
    cx, cz = -13.5, -7.0
    pts = [(cx + 4.6 * math.cos(a), -0.3, cz + 3.2 * math.sin(a)) for a in [2 * math.pi * k / 9 for k in range(9)]]
    pts += [(cx + 2.8 * math.cos(a) + rnd.uniform(-0.4, 0.4), 1.1 + rnd.uniform(0, 0.5), cz + 1.9 * math.sin(a))
            for a in [2 * math.pi * k / 6 + 0.3 for k in range(6)]]
    pts += [(cx - 0.6, 2.3, cz + 0.2)]
    mk.hull(p, pts, "coal")
    for i in range(14):
        a = 2 * math.pi * i / 14 + rnd.uniform(-0.2, 0.2)
        rr = rnd.uniform(0.3, 0.6)
        d = rnd.uniform(0.6, 3.8)
        c = (cx + d * math.cos(a), max(0.15, 2.35 - d * 0.5) + 0.05, cz + d * 0.7 * math.sin(a))
        mk.hull(p, [(c[0] + rr * math.cos(b), c[1] + rr * rnd.uniform(-0.5, 0.4), c[2] + rr * math.sin(b))
                    for b in [2 * math.pi * j / 6 + rnd.uniform(-0.3, 0.3) for j in range(6)]]
                + [(c[0], c[1] + rr * 0.85, c[2]), (c[0], -0.1, c[2])], "coal")


# ======================= vagón de carga A: cruzado, punta aplastada, boquete =======================
def wreck_boxcar_a(k, p):
    HZ, WX, WIN, D = BX.HZ, BX.WX, BX.WIN, DROP
    y0, y1 = BX.WALL_Y0 - D, BX.WALL_Y1 - D
    # costado izquierdo entero (puerta trabada)
    B(k, p, -WIN, -WX, y0, y1, -HZ + 3.0, HZ, "paint_red")
    B(k, p, -WIN - 0.02, -WX - 0.05, y0 + 0.45, y1 - 0.2, -HZ + 0.05, -HZ + 3.05, "wood_charred")
    B(k, p, -4.02, -4.16, BX.DOOR_Y0 - D, BX.DOOR_Y1 - D, -3.0, 3.0, "paint_red")
    B(k, p, -4.15, -4.2, BX.DOOR_Y0 - D + 0.01, BX.DOOR_Y1 - D - 0.01, -3.0 + 0.01, -2.72, "wood_dark")
    B(k, p, -4.12, -4.26, 11.42 - D, 11.58 - D, -3.25, 9.2, "iron")
    # costado derecho: hueco de la puerta perdida y un boquete de 3 con tablas astilladas
    hz0, hz1, hy1 = 6.0, 9.0, 8.8
    f = lambda t: y0 + t * (hy1 - y0)                                                            # noqa: E731
    B(k, p, WIN, WX, y0, y1, -HZ, -BX.OPEN_Z, "paint_red")
    B(k, p, WIN, WX, BX.OPEN_Y1 - D, y1 - 0.01, -BX.OPEN_Z, BX.OPEN_Z, "paint_red")
    B(k, p, WIN, WX, y0 + 0.01, BX.FLOOR_Y - D, -BX.OPEN_Z, BX.OPEN_Z, "paint_red")
    k.prism(p, [(z, y) for z, y in [(BX.OPEN_Z, y0), (hz0, y0), (hz0 + 0.35, f(0.2)), (hz0 - 0.1, f(0.42)),
                                     (hz0 + 0.45, f(0.62)), (hz0 + 0.05, f(0.82)), (hz0 + 0.3, hy1), (hz0, y1),
                                     (BX.OPEN_Z, y1)]],
            WX - WIN, "paint_red", plane="zy", center=((WX + WIN) / 2, 0, 0))
    k.prism(p, [(z, y) for z, y in [(hz1, y0), (HZ, y0), (HZ, y1), (hz1, y1), (hz1 - 0.4, hy1 + 0.2), (hz1 + 0.1, f(0.75)),
                                     (hz1 - 0.3, f(0.55)), (hz1 + 0.15, f(0.32)), (hz1 - 0.25, f(0.12))]],
            WX - WIN - 0.004, "paint_red", plane="zy", center=((WX + WIN) / 2, 0, 0))
    jag = [(hz0 - 0.05, y1), (hz0 - 0.05, hy1 + 0.4), (hz0 + 0.5, hy1 - 0.3), (hz0 + 0.9, hy1 + 0.35), (hz0 + 1.4, hy1 - 0.5),
           (hz0 + 1.9, hy1 + 0.2), (hz0 + 2.4, hy1 - 0.35), (hz0 + 2.8, hy1 + 0.3), (hz1 + 0.05, hy1 + 0.15), (hz1 + 0.05, y1)]
    k.prism(p, jag, WX - WIN - 0.008, "paint_red", plane="zy", center=((WX + WIN) / 2, 0, 0))
    for z, y, ang in ((hz0 + 0.7, hy1 - 0.3, 25), (hz1 - 0.6, f(0.45), -35)):                  # tablas colgando
        k.box(p, (WX + 0.04, y, z), (0.1, 1.6, 0.5), "wood_mid", rot=(ang, 0, 0))
    for dz, mat in ((-0.6, "wood_mid"), (0.5, "wood_charred")):                                    # rampa de tablas rotas
        bar(k, p, (WX + 2.6, -0.05, (hz0 + hz1) / 2 + dz), (WIN - 0.2, BX.FLOOR_Y + 0.05, (hz0 + hz1) / 2 + dz * 1.2),
            0.6, 0.12, mat, up=(-0.8, 1, 0))
    for zc in BX.TRUCK_Z:
        B(k, p, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark")
        T.truck(k, p, zc)
    B(k, p, -4.1, 4.1, 2.2, BX.FLOOR_Y - 0.02, HZ - 0.42, BX.SILL_Z, "wood_dark")
    for s in (-1, 1):
        B(k, p, s * 3.72, s * 4.1, 2.6, y0 + 0.06, -HZ + 1.0, HZ - 0.42, "wood_dark")
    # puntas: la de atrás entera con la cruz; la de adelante aplastada hacia adentro y quemada
    k.hull(p, [(x, y, z) for z in (HZ - 0.005, HZ - 0.2) for x, y in
               ((-WIN - 0.01, y0), (WIN + 0.01, y0), (WIN + 0.01, BX.roof_under(WIN) + 0.04 - D),
                (0, BX.roof_under(0) + 0.04 - D), (-WIN - 0.01, BX.roof_under(WIN) + 0.04 - D))], "paint_red")
    for kk, (xa, xb) in enumerate(((-3.6, 3.6), (3.6, -3.6))):
        zc = HZ + 0.05 + 0.035 * kk
        bar(k, p, (xa, 3.3 - D, zc), (xb, 10.95 - D, zc), 0.32, 0.12 + 0.04 * kk, "wood_dark", up=(0, 0, 1))
    k.hull(p, [(-WIN - 0.01, y0, -HZ + 0.1), (WIN + 0.01, y0, -HZ + 0.1), (-WIN - 0.01, y0, -HZ + 0.4),
               (WIN + 0.01, y0, -HZ + 0.4), (-WIN, y1 - 0.4, -HZ + 1.6), (WIN, y1 - 0.9, -HZ + 1.9),
               (-WIN, y1 - 0.4, -HZ + 1.9), (WIN, y1 - 0.9, -HZ + 2.2), (0, y1 + 0.2, -HZ + 1.8)], "wood_charred")
    bar(k, p, (-3.6, 0.4, -HZ + 0.1), (1.2, y1 - 1.6, -HZ + 1.5), 0.32, 0.14, "wood_charred", up=(0, 0, 1))
    # piso, forro de adentro, techo (hundido en la punta aplastada), pasarela
    B(k, p, -WIN, WIN, BX.FLOOR_Y - 0.3 - D, BX.FLOOR_Y - D, -HZ + 0.3, HZ - 0.2, "wood_mid")
    B(k, p, -(WIN - 0.03), -(WIN + 0.002), BX.FLOOR_Y - D, y1 - 0.4, -HZ + 3.2, HZ - 0.25, "wood_mid")   # forro (el
    # costado derecho queda sin forro: es el del boquete y el hueco de la puerta, se cruza caminando)
    rk = XK(k, Matrix.Identity(3), (0, -D, 0))
    for s, dz in ((-1, 0.0), (1, 0.01)):
        ang = math.atan2(BX.RIDGE_Y - BX.EAVE_Y, BX.EAVE_X)
        a = -s * ang
        ln = math.hypot(BX.EAVE_X + 0.06, BX.RIDGE_Y - BX.EAVE_Y)
        mx, my = s * (BX.EAVE_X - 0.06) / 2, (BX.roof_top(BX.EAVE_X) + BX.roof_top(0.06)) / 2
        rk.box(p, (mx + math.sin(a) * BX.ROOF_T / 2, my - math.cos(a) * BX.ROOF_T / 2, (-HZ + 2.6 + HZ + 0.2 - dz) / 2),
               (ln, BX.ROOF_T, HZ + 0.2 - dz + HZ - 2.6), "wood_dark", rot=(0, 0, math.degrees(a)))
    sag = XK.place(k, rot(x=-22), (0, BX.RIDGE_Y - D, -HZ + 2.6), (0, BX.RIDGE_Y - D - 0.05, -HZ + 2.6))
    sag.box(p, (0, BX.RIDGE_Y - D - 0.25, -HZ + 1.25), (8.4, 0.16, 2.9), "wood_charred")
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        B(k, p, x - 0.3, x + 0.3, BX.WALK_Y - 0.12 - D, BX.WALK_Y - D, -HZ + 4.0 + 0.5 * i, HZ + 0.15 - 0.01 * i, "wood_mid")
    for z in (-10.0, 0.0, 10.0, 14.6):
        B(k, p, -1.02, 1.02, BX.roof_top(1.02) - 0.1 - D, BX.WALK_Y - 0.11 - D, z - 0.15, z + 0.15, "wood_dark")
    BX.end_ladder(rk, p, -3.4, -2.5, HZ, 1, detail=False)


# ======================= vagón de carga B: acostado, pasarela rota =======================
def wreck_boxcar_b(k, p):
    HZ, WX, WIN = BX.HZ, BX.WX, BX.WIN
    for s in (-1, 1):
        B(k, p, s * WIN, s * WX, BX.WALL_Y0, BX.WALL_Y1, -HZ, HZ, "paint_red")
        B(k, p, s * 4.02, s * 4.16, BX.DOOR_Y0, BX.DOOR_Y1, -3.0 + 1.5 * (s > 0), 3.0 + 1.5 * (s > 0), "paint_red")
        B(k, p, s * 4.12, s * 4.26, 11.42, 11.58, -3.25, 9.2, "iron")
        B(k, p, s * 3.72, s * 4.1, 2.6, BX.WALL_Y0 + 0.06, -HZ + 0.42, HZ - 0.42, "wood_dark")
        B(k, p, s * 3.95, s * 4.15, BX.EAVE_Y - 0.33, BX.roof_top(4.15) - 0.03, -HZ - 0.06, HZ + 0.06, "wood_dark")
    for d in (-1, 1):
        k.hull(p, [(x, y, z) for z in (d * (HZ - 0.005), d * (HZ - 0.2)) for x, y in
                   ((-WIN - 0.01, BX.WALL_Y0), (WIN + 0.01, BX.WALL_Y0), (WIN + 0.01, BX.roof_under(WIN) + 0.04),
                    (0, BX.roof_under(0) + 0.04), (-WIN - 0.01, BX.roof_under(WIN) + 0.04))], "paint_red")
        for kk, (xa, xb) in enumerate(((-3.6, 3.6), (3.6, -3.6))):
            zc = d * (HZ + 0.05 + 0.035 * kk)
            bar(k, p, (xa, 3.3, zc), (xb, 10.95, zc), 0.32, 0.12 + 0.04 * kk, "wood_dark", up=(0, 0, 1))
        B(k, p, -4.1, 4.1, 2.2, BX.FLOOR_Y - 0.02, d * (HZ - 0.42), d * BX.SILL_Z, "wood_dark")
    BX.roof(k, p, detail=False)
    # pasarela partida: un tramo entero, un hueco y un tramo colgando
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        B(k, p, x - 0.3, x + 0.3, BX.WALK_Y - 0.12, BX.WALK_Y, -HZ - 0.15 + 0.01 * i, 2.0 - 0.6 * i, "wood_mid")
        B(k, p, x - 0.3, x + 0.3, BX.WALK_Y - 0.12, BX.WALK_Y, 6.5 + 0.4 * i, HZ + 0.15 - 0.01 * i, "wood_mid")
    for z in (-14.6, -10.0, -5.0, 0.0, 10.0, 14.6):
        B(k, p, -1.02, 1.02, BX.roof_top(1.02) - 0.1, BX.WALK_Y - 0.11, z - 0.15, z + 0.15, "wood_dark")
    bar(k, p, (-0.66, BX.WALK_Y - 0.06, 1.7), (1.4, BX.WALK_Y + 2.4, 4.4), 0.6, 0.12, "wood_mid", ext=0.05)
    for zc in BX.TRUCK_Z:
        B(k, p, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark")
        T.truck(k, p, zc)


# ======================= vía arrancada =======================
def wreck_rails(mk, p):
    rnd = random.Random(5)
    x0 = -2.0
    gx = L.RAIL_X
    ties = []
    for i in range(20):
        z = -24.0 + 1.0 + 2.0 * i
        if z < -13:
            dx, dz, a, lift = rnd.uniform(-1.6, 1.6), rnd.uniform(-0.6, 0.6), rnd.uniform(-35, 35), 0.0
        else:
            dx, dz, a, lift = rnd.uniform(-0.15, 0.15), rnd.uniform(-0.1, 0.1), rnd.uniform(-5, 5), 0.0
        ties.append((x0 + dx, z + dz, a))
        mk.box(p, (x0 + dx, 0.17 + lift + 0.006 * (i % 3), z + dz), (7.2, 0.35, 0.7), "wood_dark" if i % 3 else "wood_charred",
               rot=(0, a, 0))
    for j, (c, a) in enumerate((((x0 - 6.5, -9.0), 70), ((x0 - 6.9, -9.6), 52), ((x0 + 6.8, -16.5), 15))):  # sueltos
        mk.box(p, (c[0], 0.172 + 0.005 * j, c[1]), (7.2, 0.35, 0.7), "wood_dark", rot=(0, a, 0))
    mk.box(p, (x0 + 6.6, 0.52, -17.0), (7.2, 0.35, 0.7), "wood_charred", rot=(0, 22, 4))
    # riel izquierdo en su lugar hasta z -13; el derecho arrancado y retorcido hacia arriba
    for s in (-1, 1):
        x = x0 + s * gx
        bar(mk, p, (x, 0.53, -12.6), (x, 0.53, 16.0), 0.26, 0.4, "iron", up=(0, 1, 0))
    left = [(x0 - gx, 0.53, -12.6), (x0 - gx - 0.6, 0.7, -16.0), (x0 - gx - 1.8, 0.6, -20.0), (x0 - gx - 2.3, 0.45, -23.5)]
    right = [(x0 + gx, 0.53, -12.6), (x0 + gx + 0.2, 1.4, -15.0), (x0 + gx + 1.2, 3.4, -17.0), (x0 + gx + 3.0, 5.0, -18.2),
             (x0 + gx + 5.0, 5.6, -18.0), (x0 + gx + 6.4, 4.8, -16.9)]
    for pts, tw in ((left, 10), (right, 35)):
        for j, (a, b) in enumerate(zip(pts, pts[1:])):
            ang = math.radians(tw * j)
            bar(mk, p, a, b, 0.26, 0.4, "iron", up=(math.sin(ang), math.cos(ang), 0), ext=0.12)


# ======================= escombros: 8 piezas apoyadas unas en otras =======================
def debris(mk, p):
    # 1-3: tablas sobre el cajón, 4: cajón, 5: juego de ruedas, 6: puerta corrediza del vagón A,
    # 7-8: tablas cruzadas sobre la puerta
    cx, cz = 15.0, 8.0
    mk.box(p, (cx, 1.1, cz), (2.2, 2.2, 2.2), "wood_light", rot=(0, 18, 0))                           # cajón
    for dx, dz in ((-1.0, 0.0), (1.0, 0.0)):
        mk.box(p, (cx + dx * math.cos(math.radians(18)), 1.1, cz - dx * math.sin(math.radians(18))), (0.25, 2.3, 2.3),
               "wood_dark", rot=(0, 18, 0))
    mk.box(p, (cx + 1.6, 1.3, cz + 1.2), (0.5, 0.12, 5.2), "wood_mid", rot=(25, 30, 0))              # tabla apoyada
    mk.box(p, (cx - 1.2, 1.6, cz - 0.6), (0.5, 0.12, 4.6), "wood_charred", rot=(-15, -60, 8))
    mk.box(p, (cx + 0.3, 2.28, cz + 0.2), (0.45, 0.1, 3.4), "paint_red", rot=(0, 75, 0))             # tabla del costado
    # juego de ruedas del ténder, acostado contra el cajón
    wz, wx = cz + 1.5, cx - 0.6
    for s in (-1, 1):
        mk.cyl(p, (wx + s * L.RAIL_X, T.CAR_WHEEL_R, wz), T.CAR_WHEEL_R, 0.38, "gunmetal", axis="x", sides=12,
               rot=(15, 0, 0))
    mk.cyl(p, (wx, T.CAR_WHEEL_R, wz), 0.36, 5.9, "iron", axis="x", sides=8)
    # puerta corrediza del vagón A tirada en el suelo, con dos tablas cruzadas encima
    dx_, dz_ = -11.0, 16.0
    mk.box(p, (dx_, 0.08, dz_), (6.0, 0.16, 8.0), "paint_red", rot=(0, 12, 0))
    mk.box(p, (dx_, 0.19, dz_), (5.4, 0.08, 0.3), "wood_dark", rot=(0, 12, 0))
    mk.box(p, (dx_ + 0.6, 0.3, dz_ - 1.0), (0.5, 0.12, 4.4), "wood_mid", rot=(0, 55, 3))
    mk.box(p, (dx_ - 0.8, 0.3, dz_ + 1.4), (0.5, 0.12, 3.8), "wood_charred", rot=(0, -40, -3))


def build(mk):
    lo = mk.part("Wreck_Locomotive", (0, 0, 0))
    wreck_loco(XK.place(mk, LOCO_R, LOCO_PIVOT, LOCO_AT), lo)
    te = mk.part("Wreck_Tender", (0, 0, 0))
    wreck_tender(XK.place(mk, TENDER_R, TENDER_PIVOT, TENDER_AT), te)
    cs = mk.part("Wreck_CoalSpill", (0, 0, 0))
    coal_spill(mk, cs)
    a = mk.part("Wreck_Boxcar_A", (0, 0, 0))
    wreck_boxcar_a(XK.place(mk, BOXA_R, (0, 0, 0), BOXA_AT), a)
    b = mk.part("Wreck_Boxcar_B", (0, 0, 0))
    wreck_boxcar_b(XK.place(mk, BOXB_R, BOXB_PIVOT, BOXB_AT), b)
    r = mk.part("Wreck_Rails", (0, 0, 0))
    wreck_rails(mk, r)
    d = mk.part("Wreck_Debris", (0, 0, 0))
    debris(mk, d)

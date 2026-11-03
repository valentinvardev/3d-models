"""
Receta de WST_Train_Tender, el ténder de carbón de la 4-4-0 (prompt 070, Bloques A + B). Además de su
modelo, esta receta tiene las ayudas de los vagones (bogie de 4 ruedas, enganche de eslabón y perno,
escalera) que importan el vagón de carga, el furgón de cola, el de pasajeros y los restos: así todo el
tren comparte trocha, rueda y alto de enganche. Las medidas comunes vienen de la locomotora.

Brief
- Silueta a 40 studs: caja roja baja y larga con el tanque en U que abraza el carbón adelante, bordes de
  madera abiertos arriba, un montón de carbón facetado que asoma sobre los bordes, dos bogies negros.
- Medidas: 20 de largo (vigas en z = ±9,65 y los enganches que salen 0,5), 8,5 de ancho (bordes del
  carbón abiertos), 7,5 de alto (borde de las tablas). Rieles en y = 0 (ruedas de 3,0 en x = ±2,43),
  enganche a y = 2,6 (igual que la locomotora), plataforma de palear a 4,0 = piso de la cabina.
  Tanque de 3,2 de alto (3,6 a 6,8), patas de la U de 1,4 de ancho (el carbón entre x = ±2,6).
- Piezas: Body (tanque, bastidor, escalera atrás, freno, tapa del agua), Coal (montón con terrones),
  Wheels (dos bogies, una pieza, origen en el piso), CouplerFront y CouplerBack (origen en la cara de la
  viga, a la altura del enganche: se sueltan). Marcador _CoalPickup en el borde de adelante del montón.
- Inferido: bogies de barras en arco con ruedas lisas (de plato, como los vagones de carga de 1870; las de
  rayos quedan para la locomotora), tapa redonda del agua atrás, freno de mano adelante a la izquierda,
  tablas del carbón inclinadas hacia afuera a lo largo de todo el tanque, eslabón solo en el enganche de
  adelante (el de atrás lo pone el vagón que sigue).

Vueltas: 1) primera versión: z-fighting en las colgaderas de los escalones (base igual que el escalón), en
las grampas del freno contra la cara plana del caño de 6 lados y en las de las agarraderas; ruedas 0,05 sobre
el riel (el cilindro de 12 lados tenía una cara plana abajo: ahora giran 15° y apoyan en un vértice) ·
2) el carbón era una cúpula lisa con puntitas: ahora relleno bajo + 10 terrones grandes + 12 chicos + 4
caídos en la plataforma; los costados eran un paño rojo liso de 18 x 3: listones y zócalo de madera ·
3) terrones chicos flotando (el relleno bajó 0,45) y los caídos anclados al piso.

Revisión
- 2392 triángulos contra 1500 (+59 %): los dos bogies son 840 (la misma pieza en todos los vagones:
  ruedas de 12 lados, cajas de grasa, barras en arco), los enganches 256 (cabeza con boca, perno y
  eslabón: se ven de cerca al saltar entre vagones), el carbón 380 (terrones facetados que pide el prompt).
- Medidas: 20,6 de largo (vigas a ±9,65 + enganche de 0,5 + el eslabón de adelante), 8,5 de ancho, 7,5 de
  alto. Plataforma de palear a 4,0, igual que el piso de la cabina; el carbón arranca a 4,5 adelante y llega
  a 7,3: desde el piso de la cabina se alcanza.
- El enganche de adelante lleva el eslabón; el de atrás, solo la boca y el perno.
"""

import importlib.util
import math
import random
from pathlib import Path


def _load(mid, folder="transport"):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(f"recipe_{mid}", root / folder / mid / "01_design" / f"{mid}.build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L = _load("WST_Train_Locomotive")
B, bar, pipe, annulus, ring_pts = L.B, L.bar, L.pipe, L.annulus, L.ring_pts
RAIL_X, COUPLER_Y, DECK_Y = L.RAIL_X, L.COUPLER_Y, L.DECK_Y

# ---------------- medidas de los vagones (las importan los otros vagones) ----------------
CAR_WHEEL_R = 1.5          # ruedas de 3,0
TRUCK_WB = 4.4             # distancia entre ejes del bogie
BOLSTER_TOP = 2.32         # tope de la traviesa del bogie; el bastidor del vagón apoya ahí

# ---------------- ténder ----------------
HZ = 9.65                  # media longitud hasta la cara de las vigas
TANK_X, LEG_X = 4.0, 2.6   # borde de afuera del tanque y de adentro de las patas
TANK_Y0, TANK_Y1 = 3.6, 6.8
Z_BUNKER = -0.4            # fondo del espacio del carbón (frente del tanque de atrás)
Z_LEG = -8.6               # frente de las patas
TRUCK_Z = (-5.6, 5.6)


# ---------------- ayudas de los vagones ----------------
def truck(mk, part, zc, r=CAR_WHEEL_R, wb=TRUCK_WB, top=BOLSTER_TOP, detail=False):
    """Bogie de 4 ruedas de plato con bastidores de barras en arco, en el plano del riel (x = ±2,43)."""
    for dz in (-wb / 2, wb / 2):
        z = zc + dz
        for s in (-1, 1):
            mk.cyl(part, (s * RAIL_X, r, z), r, 0.38, "gunmetal", axis="x", sides=12, rot=(15, 0, 0), detail=detail)   # rueda (vértice abajo: apoya en y = 0)
            B(mk, part, s * 2.8, s * 3.2, r - 0.36, r + 0.34, z - 0.34, z + 0.34, "iron", detail=detail)          # caja de grasa
        mk.cyl(part, (0, r, z), 0.36, 5.9, "iron", axis="x", sides=8, detail=detail)                              # eje con los cubos
    h = wb / 2
    for s in (-1, 1):
        x = s * 3.0
        B(mk, part, x - 0.08, x + 0.08, r + 0.3, r + 0.52, zc - h - 0.3, zc + h + 0.3, "iron", detail=detail)    # barra de arriba
        low = [(zc - h - 0.25, r - 0.38), (zc - 1.1, r - 0.72), (zc + 1.1, r - 0.72), (zc + h + 0.25, r - 0.38),
               (zc + h + 0.25, r - 0.2), (zc + 1.1, r - 0.54), (zc - 1.1, r - 0.54), (zc - h - 0.25, r - 0.2)]
        mk.prism(part, low, 0.14, "iron", plane="zy", center=(x, 0, 0), detail=detail)                           # barra en arco
        for dz in (-0.75, 0.75):
            B(mk, part, x - 0.1, x + 0.1, r - 0.6, r + 0.5, zc + dz - 0.12, zc + dz + 0.12, "iron", detail=detail)   # columnas
    B(mk, part, -2.95, 2.95, top - 0.42, top, zc - 0.42, zc + 0.42, "iron", detail=detail)                        # traviesa


def coupler(mk, name, z_face, d, link=False, y=COUPLER_Y):
    """Enganche de eslabón y perno: cabeza con boca, perno vertical y (si link) el eslabón asomando.
    d = +1 hacia atrás, -1 hacia adelante. Origen en la cara de la viga, a la altura del enganche."""
    p = mk.part(name, (0, y, z_face))
    zo = lambda k: z_face + d * k                                                                   # noqa: E731
    mk.hull(p, [(x, yy, zo(-0.12)) for x in (-0.3, 0.3) for yy in (y - 0.26, y + 0.26)]
            + [(x, yy, zo(0.22)) for x in (-0.36, 0.36) for yy in (y - 0.3, y + 0.3)], "iron")       # cuerpo
    for sy in (-1, 1):
        mk.hull(p, [(x, y + sy * yy, zo(k)) for x in (-0.4, 0.4) for yy in (0.09, 0.34)
                    for k in (0.18, 0.5)], "iron")                                                     # mordazas
    for sy in (-1, 1):
        mk.slice(p, (0, y + sy * 0.085, 0), (0, 1, 0))
    mk.paint(p, "coal", box=((0, y, zo(0.22)), (0.6, 0.16, 0.02)))                                    # fondo de la boca
    mk.cyl(p, (0, y + 0.12, zo(0.36)), 0.06, 0.82, "iron", axis="y", sides=6)                          # perno
    mk.cyl(p, (0, y + 0.55, zo(0.36)), 0.12, 0.06, "iron", axis="y", sides=6)
    if link:
        annulus(mk, p, (0, y, zo(0.56)), 0.16, 0.27, 0.09, "iron", axis="y", sides=10)
    return p


def ladder(mk, part, x0, x1, y0, y1, z, rungs, mat="iron", standoff=None):
    """Escalera de hierro de dos largueros con travesaños; standoff = z de la pared donde se apoya."""
    for x in (x0, x1):
        bar(mk, part, (x, y0, z), (x, y1, z), 0.1, 0.1, mat, up=(0, 0, 1))
        if standoff is not None:
            for y in (y0 + 0.4, y1 - 0.4):
                B(mk, part, x - 0.04, x + 0.04, y - 0.05, y + 0.05, min(z, standoff) - 0.01, max(z, standoff) + 0.01, mat)
    for k in range(rungs):
        y = y0 + 0.5 + k * (y1 - y0 - 0.9) / max(1, rungs - 1)
        bar(mk, part, (x0, y, z), (x1, y, z), 0.08, 0.08, mat, up=(0, 0, 1), ext=0.02)


# ---------------- ténder ----------------
def coal_height(x, z):
    """Alto del montón de carbón (y) en (x, z)."""
    zs = (-8.4, -6.5, -4.0, -2.0, Z_BUNKER - 0.02)
    hs = (4.55, 6.3, 7.32, 7.15, 6.95)
    if z <= zs[0]:
        g = hs[0]
    elif z >= zs[-1]:
        g = hs[-1]
    else:
        k = next(i for i in range(len(zs) - 1) if zs[i] <= z <= zs[i + 1])
        t = (z - zs[k]) / (zs[k + 1] - zs[k])
        g = hs[k] + (hs[k + 1] - hs[k]) * t
    return DECK_Y + (g - DECK_Y) * (1 - 0.2 * (x / LEG_X) ** 2)


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # tanque de agua en U alrededor del carbón
    u = [(-TANK_X, Z_LEG), (-LEG_X, Z_LEG), (-LEG_X, Z_BUNKER), (LEG_X, Z_BUNKER), (LEG_X, Z_LEG), (TANK_X, Z_LEG),
         (TANK_X, HZ - 0.2), (-TANK_X, HZ - 0.2)]
    mk.prism(body, u, TANK_Y1 - TANK_Y0, "paint_red", plane="xz", center=(0, (TANK_Y0 + TANK_Y1) / 2, 0))
    # molduras: esquineros, faja de arriba y tablas del carbón inclinadas hacia afuera
    for s in (-1, 1):
        for z0, z1 in ((Z_LEG - 0.05, Z_LEG + 0.22), (HZ - 0.45, HZ - 0.14)):
            B(mk, body, s * (TANK_X - 0.2), s * (TANK_X + 0.06), TANK_Y0 + 0.02, TANK_Y1 - 0.02, z0, z1, "wood_dark")
        B(mk, body, s * (TANK_X - 0.12), s * (TANK_X + 0.05), TANK_Y1 - 0.3, TANK_Y1 - 0.08, Z_LEG + 0.2, HZ - 0.43,
          "wood_dark")                                                                              # faja
        B(mk, body, s * (TANK_X - 0.12), s * (TANK_X + 0.04), TANK_Y0 + 0.03, TANK_Y0 + 0.28, Z_LEG + 0.21, HZ - 0.44,
          "wood_dark")                                                                              # zócalo
        for z in (-4.3, 0.0, 4.6):                                                                   # listones: paños
            B(mk, body, s * (TANK_X - 0.1), s * (TANK_X + 0.035), TANK_Y0 + 0.26, TANK_Y1 - 0.28, z - 0.11, z + 0.11,
              "wood_dark")
        z_end = HZ - 0.19 if s > 0 else HZ - 0.75                                                   # una tabla rota atrás
        mk.hull(body, [(s * x, y, z) for z in (Z_LEG - 0.02, z_end) for x, y in
                       ((TANK_X - 0.14, TANK_Y1 - 0.04), (TANK_X - 0.02, TANK_Y1 - 0.04), (TANK_X + 0.13, 7.5),
                        (TANK_X + 0.25, 7.5))], "wood_dark")
        for z in (-4.0, 1.5, 6.5):                                                                   # cartelas
            mk.hull(body, [(s * x, y, zz) for zz in (z - 0.07, z + 0.07)
                           for x, y in ((TANK_X - 0.06, TANK_Y1 - 0.4), (TANK_X + 0.08, TANK_Y1 - 0.4),
                                        (TANK_X + 0.2, 7.3))], "iron")
    B(mk, body, -TANK_X + 0.05, TANK_X - 0.05, TANK_Y1 - 0.05, 7.3, HZ - 0.36, HZ - 0.24, "wood_dark")   # tabla de atrás
    # bastidor de madera, vigas, piso de palear (a la altura del piso de la cabina)
    for s in (-1, 1):
        B(mk, body, s * 3.65, s * 4.05, 2.6, TANK_Y0 + 0.02, -HZ, HZ, "wood_dark")                     # largueros
        B(mk, body, s * 0.6, s * 1.0, 2.6, TANK_Y0 + 0.01, -HZ + 0.3, HZ - 0.3, "wood_dark")           # largueros del medio
    for z0, z1 in ((-HZ, -HZ + 0.45), (HZ - 0.45, HZ)):
        B(mk, body, -3.99, 3.99, 2.2, TANK_Y0 + 0.005, z0 + 0.005, z1 - 0.005, "paint_red")             # vigas
    for zc in TRUCK_Z:
        B(mk, body, -3.7, 3.7, BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark")            # traviesas
    B(mk, body, -LEG_X - 0.02, LEG_X + 0.02, TANK_Y0 - 0.02, DECK_Y, -HZ - 0.02, Z_BUNKER + 0.02, "iron")   # piso
    # tapa del agua atrás, con bisagra
    mk.cyl(body, (0, TANK_Y1 + 0.12, 5.6), 0.78, 0.3, "iron", axis="y", sides=10)
    mk.cyl(body, (0, TANK_Y1 + 0.31, 5.6), 0.86, 0.1, "iron", axis="y", sides=10)
    B(mk, body, -0.25, 0.25, TANK_Y1 + 0.18, TANK_Y1 + 0.38, 6.38, 6.62, "iron")
    # escalera atrás (sube al techo del tanque) y agarraderas
    ladder(mk, body, 2.4, 3.4, 1.4, 7.5, HZ + 0.12, 7, standoff=HZ - 0.2)
    # freno de mano adelante a la izquierda
    pipe(mk, body, (-3.3, DECK_Y - 0.1, Z_LEG - 0.22), (-3.3, 6.2, Z_LEG - 0.22), 0.07, "iron", sides=6)
    annulus(mk, body, (-3.3, 6.2, Z_LEG - 0.22), 0.3, 0.42, 0.08, "iron", axis="y", sides=8)
    for a in (0, 90):
        r = math.radians(a)
        bar(mk, body, (-3.3 - 0.33 * math.cos(r), 6.2, Z_LEG - 0.22 - 0.33 * math.sin(r)),
            (-3.3 + 0.33 * math.cos(r), 6.2, Z_LEG - 0.22 + 0.33 * math.sin(r)), 0.06, 0.06, "iron")
    for y in (4.4, 5.8):
        B(mk, body, -3.36, -3.24, y - 0.05, y + 0.05, Z_LEG - 0.3, Z_LEG + 0.02, "iron")
    # escalones de adelante y agarraderas en las puntas de las patas
    for s in (-1, 1):
        for z in (-HZ + 0.15, -HZ + 0.85):
            B(mk, body, s * 3.72, s * 3.82, 1.27, 2.7, z - 0.05, z + 0.05, "iron")
        B(mk, body, s * 3.5, s * 4.0, 1.25, 1.37, -HZ + 0.05, -HZ + 0.95, "iron")
        bar(mk, body, (s * (LEG_X + 0.25), 4.6, Z_LEG - 0.1), (s * (LEG_X + 0.25), 6.4, Z_LEG - 0.1), 0.08, 0.08, "iron")
        for y in (4.8, 6.2):
            B(mk, body, s * (LEG_X + 0.22), s * (LEG_X + 0.28), y - 0.04, y + 0.04, Z_LEG - 0.15, Z_LEG + 0.02, "iron")

    # carbón: relleno bajo, terrones grandes que arman el montón y terrones chicos; algunos caídos adelante
    coal = mk.part("Coal", (0, 0, 0))
    pts = [(x, DECK_Y - 0.02, z) for x in (-LEG_X - 0.02, LEG_X + 0.02) for z in (-8.45, Z_BUNKER - 0.02)]
    for x in (-LEG_X - 0.02, -1.3, 0.0, 1.3, LEG_X + 0.02):
        for z in (-8.45, -6.5, -4.0, -2.0, Z_BUNKER - 0.02):
            pts.append((x, coal_height(x, z) - 0.45, z))
    mk.hull(coal, pts, "coal")
    rnd = random.Random(7)

    def lump(c, rr, flat=0.75, floor=None):
        ring = [2 * math.pi * k / 7 + rnd.uniform(-0.25, 0.25) for k in range(7)]
        mk.hull(coal, [(c[0] + rr * rnd.uniform(0.7, 1.0) * math.cos(a), c[1] + rr * flat * rnd.uniform(-0.6, 0.5),
                        c[2] + rr * rnd.uniform(0.7, 1.0) * math.sin(a)) for a in ring]
                + [(c[0] + rr * rnd.uniform(-0.3, 0.3), c[1] + rr * flat * rnd.uniform(0.75, 1.0), c[2] + rr * rnd.uniform(-0.3, 0.3))]
                + ([(c[0], floor, c[2])] if floor is not None else []), "coal")

    for x, z, rr in ((-1.2, -6.9, 1.05), (1.1, -6.2, 1.15), (-0.9, -4.3, 1.25), (1.3, -3.4, 1.2), (-1.4, -1.9, 1.1),
                     (0.6, -1.4, 1.15), (0.0, -5.2, 0.95), (-0.9, -7.9, 0.8), (1.0, -8.0, 0.75),
                     (0.1, -6.7, 0.85)):                                                          # terrones grandes
        lump((x, coal_height(x, z) - rr * 0.45, z), rr)
    for x, z, rr in ((-1.9, -7.9, 0.42), (0.3, -8.0, 0.4), (1.9, -7.6, 0.45), (-2.1, -5.4, 0.5), (2.0, -4.8, 0.48),
                     (-0.2, -3.0, 0.55), (2.1, -1.6, 0.42), (-2.0, -3.6, 0.45), (0.4, -6.9, 0.5), (-0.6, -0.9, 0.42),
                     (1.6, -0.8, 0.4), (-1.0, -7.3, 0.38)):                                       # terrones chicos
        lump((x, coal_height(x, z) - 0.45 + rr * 0.2, z), rr, flat=0.9)
    for x, z, rr in ((-0.8, -8.85, 0.32), (0.9, -9.05, 0.28), (0.1, -9.35, 0.24), (1.6, -8.75, 0.3)):   # caídos adelante
        lump((x, DECK_Y + rr * 0.35, z), rr, flat=0.9, floor=DECK_Y - 0.03)
    mk.marker("_CoalPickup", (0, coal_height(0, -8.3), -8.3))

    w = mk.part("Wheels", (0, 0, 0))
    for zc in TRUCK_Z:
        truck(mk, w, zc)
    coupler(mk, "CouplerFront", -HZ, -1, link=True)
    coupler(mk, "CouplerBack", HZ, 1)

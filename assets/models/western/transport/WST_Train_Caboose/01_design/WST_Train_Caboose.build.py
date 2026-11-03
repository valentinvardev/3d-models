"""
Receta de WST_Train_Caboose, el furgón de cola (prompt 073, Bloques A + B). Comparte bogies, enganche y
tablas con el vagón de carga (las ayudas vienen del ténder y del vagón de carga).

Brief
- Silueta a 40 studs: caja roja corta con la cúpula alta en el medio (ventanas en los cuatro lados), techo a
  dos aguas, plataformas abiertas con barandas en las dos puntas, chimenea de la estufa, el farol rojo
  colgando atrás.
- Medidas: 22 de largo (caja de 18 entre z = ±9 y plataformas de 2 hasta z = ±11), 8,5 de ancho (aleros),
  cumbrera del techo a 11,5; cúpula de 6 de largo (z ±3) y 5,2 de ancho con la cumbrera a 14,0 (2,5 sobre
  el techo). Piso de la caja y de las plataformas a 3,5 (como el vagón de carga), enganche a 2,6.
- Piezas: Body (caja, plataformas, barandas, escalera, chimenea, farol), Cupola (origen en la cumbrera del
  techo, al centro), Wheels (dos bogies), CouplerFront (solo adelante: es el último vagón),
  BackLantern_Glow (el vidrio del farol, aparte para apagarlo).
- Inferido: color rojo como el resto del tren, tablas verticales con juntas pintadas, dos ventanas por
  costado, puertas cerradas en las dos puntas, escalera en la punta de adelante a la derecha de la puerta,
  chimenea de la estufa atrás a la izquierda, farol colgado de la baranda de atrás a la derecha con el vidrio
  mirando hacia atrás, sin pasarela en el techo (la cúpula ocupa el medio; el techo igual se camina).

Vueltas: 1) primera versión: 228 bordes no-manifold (los slice de las juntas dejaban vértices iguales en las
caras que se tocaban entre bandas y pilares: la soldadura los unía), parantes de las ventanas y tablas de
la plataforma flotando, sombrerete de la chimenea apoyado justo en el caño, largueros partidos en z = 0 ·
2) pilares metidos 0,01 en las bandas (las juntas se pintan con tolerancia 0,014 para tomar las dos caras),
base debajo de las tablas de la plataforma, colgaderas de los escalones y pilares de la cúpula sin caras
coplanares; escalera de 7 travesaños.

Revisión
- 3780 triángulos contra 1600 (+136 %): bogies 840 y enganche 172 (los mismos del ténder y del vagón de
  carga), cúpula 344 (4 paredes con 6 ventanas, techo, esquineros), Body ~2400: costados con 17 juntas y
  ventanas enmarcadas, dos plataformas con barandas, escalones en las 4 esquinas, puertas con ventanita,
  escalera, chimenea, cajón de herramientas, farol. Es el vagón que más se pasa: si hace falta bajar,
  lo primero son los escalones de las esquinas (~140) y los marcos de ventana (~140).
- Medidas: 23,0 de largo (22 de plataforma a plataforma + el enganche de adelante), 8,5 de ancho, 14,0 de
  alto (cumbrera de la cúpula: 2,5 sobre el techo de 11,5). Piso y plataformas a 3,5, enganche a 2,6.
- Sin enganche atrás: el prompt solo pide CouplerFront (es el último vagón).
"""

import importlib.util
import math
from pathlib import Path


def _load(mid, folder="transport"):
    root = Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location(f"recipe_{mid}", root / folder / mid / "01_design" / f"{mid}.build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BX = _load("WST_Train_Boxcar")
T, L = BX.T, BX.L
B, bar, pipe, annulus = L.B, L.bar, L.pipe, L.annulus

HC, HZ = 9.0, 11.0                    # punta de la caja y punta de las plataformas
WX, WIN = 4.0, 3.8
FLOOR_Y, WALL_Y0 = 3.5, 2.95
RIDGE, EAVE_Y, EAVE_X, ROOF_T = 11.5, 11.15, 4.25, 0.16
WINS = ((-6.6, -4.2), (4.2, 6.6))      # ventanas de los costados (z)
WIN_Y0, WIN_Y1 = 6.4, 9.2
TRUCK_Z = (-7.0, 7.0)
CUP_X, CUP_Z, CUP_RIDGE, CUP_EAVE = 2.6, 3.0, 14.0, 13.78


def top(x, ridge=RIDGE, eave_y=EAVE_Y, eave_x=EAVE_X):
    return ridge - (ridge - eave_y) * abs(x) / eave_x


def gable(mk, part, ridge, eave_y, eave_x, hz, mat="wood_dark", t=ROOF_T, detail=True):
    """Techo a dos aguas de dos losas que se cruzan en la cumbrera."""
    ang = math.atan2(ridge - eave_y, eave_x)
    ln = math.hypot(eave_x + 0.06, ridge - eave_y)
    for s, dz in ((-1, 0.0), (1, 0.01)):
        a = -s * ang
        mx, my = s * (eave_x - 0.06) / 2, (eave_y + top(0.06, ridge, eave_y, eave_x)) / 2
        mk.box(part, (mx + math.sin(a) * t / 2, my - math.cos(a) * t / 2, 0), (ln, t, 2 * (hz - dz)), mat,
               rot=(0, 0, math.degrees(a)), detail=detail)


def wall_x(mk, part, s, x_in, x_out, y0, y1, z0, z1, wins, wy0, wy1, mat="paint_red"):
    """Pared a lo largo de Z con huecos de ventana: banda de abajo, banda de arriba y pilares (sin vértices compartidos)."""
    B(mk, part, s * x_in, s * x_out, y0, wy0, z0, z1, mat)
    B(mk, part, s * x_in, s * x_out, wy1, y1, z0, z1, mat)
    edges = [z0 + 0.01] + [v for w in wins for v in w] + [z1 - 0.01]
    for a, b in zip(edges[0::2], edges[1::2]):                                                      # pilares: se meten 0,01 en
        B(mk, part, s * (x_in + 0.01), s * (x_out - 0.005), wy0 - 0.01, wy1 + 0.01, a, b, mat)      # las bandas, sin tocar sus caras


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    wall_y1 = top(WIN) - ROOF_T + 0.035
    # ---------------- caja: costados con ventanas, puntas a dos aguas ----------------
    for s in (-1, 1):
        wall_x(mk, body, s, WIN, WX, WALL_Y0, wall_y1, -HC, HC, WINS, WIN_Y0, WIN_Y1)
    for d in (-1, 1):
        zo, zi = d * (HC - 0.005), d * (HC - 0.2)
        mk.hull(body, [(x, y, z) for z in (zo, zi) for x, y in
                       ((-WIN - 0.01, WALL_Y0), (WIN + 0.01, WALL_Y0), (WIN + 0.01, top(WIN) - ROOF_T + 0.035),
                        (0, top(0) - ROOF_T + 0.035), (-WIN - 0.01, top(WIN) - ROOF_T + 0.035))], "paint_red")
    # adentro madera; juntas pintadas afuera
    for s in (-1, 1):
        mk.paint(body, "wood_mid", box=((s * (WIN + 0.005), 7.0, 0), (0.016, 8.5, 2 * HC)))
        for z0, z1 in WINS:                                                                        # derrames de las ventanas
            for z in (z0, z1):
                mk.paint(body, "wood_mid", box=((s * 3.9, (WIN_Y0 + WIN_Y1) / 2, z), (0.21, WIN_Y1 - WIN_Y0, 0.004)))
            for y in (WIN_Y0, WIN_Y1):
                mk.paint(body, "wood_mid", box=((s * 3.9, y, (z0 + z1) / 2), (0.21, 0.004, z1 - z0)))
    for d in (-1, 1):
        mk.paint(body, "wood_mid", box=((0, 7.2, d * (HC - 0.2)), (2 * WIN, 8.6, 0.004)))
    for s in (-1, 1):
        BX.seams(mk, body, "z", [k * 1.0 for k in range(-8, 9)], {"x": s * (WX - 0.0025)}, {"y": (6.95, 8.0)}, tol=0.014)
    for d in (-1, 1):
        BX.seams(mk, body, "x", [-2.85, -1.9, 1.9, 2.85], {"z": d * (HC - 0.005)}, {"y": (7.2, 8.6)})

    # ---------------- puertas de las puntas, marcos de ventana, molduras ----------------
    for d in (-1, 1):
        zf = d * (HC + 0.04)
        B(mk, body, -1.0, 1.0, FLOOR_Y + 0.02, 9.4, d * (HC - 0.02), zf, "paint_red", detail=True)    # puerta
        for x0, x1 in ((-1.18, -1.0), (1.0, 1.18)):
            B(mk, body, x0, x1, FLOOR_Y + 0.01, 9.55, d * (HC - 0.03), d * (HC + 0.08), "wood_dark", detail=True)
        B(mk, body, -1.19, 1.19, 9.4, 9.6, d * (HC - 0.03), d * (HC + 0.09), "wood_dark", detail=True)
        B(mk, body, -0.55, 0.55, 7.0, 8.6, d * (HC - 0.01), d * (HC + 0.07), "wood_dark", detail=True)   # ventanita
        B(mk, body, -0.4, 0.4, 7.15, 8.45, d * (HC + 0.06), d * (HC + 0.075), "coal", detail=True)
        B(mk, body, 0.65, 0.85, 6.1, 6.25, d * (HC + 0.03), d * (HC + 0.15), "iron", detail=True)        # picaporte
    for s in (-1, 1):
        for z0, z1 in WINS:
            B(mk, body, s * 3.95, s * 4.14, WIN_Y0 - 0.16, WIN_Y0 + 0.02, z0 - 0.15, z1 + 0.15, "wood_dark", detail=True)
            B(mk, body, s * 3.95, s * 4.1, WIN_Y1 - 0.02, WIN_Y1 + 0.14, z0 - 0.12, z1 + 0.12, "wood_dark", detail=True)
            B(mk, body, s * 3.86, s * 3.98, WIN_Y0 - 0.1, WIN_Y1 + 0.1, (z0 + z1) / 2 - 0.05, (z0 + z1) / 2 + 0.05,
              "wood_dark", detail=True)                                                             # parante de la ventana
        B(mk, body, s * 3.95, s * 4.15, EAVE_Y - 0.3, top(4.15) - 0.03, -HC - 0.06, HC + 0.06, "wood_dark", detail=True)
        for d in (-1, 1):
            B(mk, body, s * 3.95, s * 4.13, 2.58, wall_y1 - 0.02, d * (HC - 0.15), d * (HC + 0.1), "wood_dark", detail=True)
        B(mk, body, s * 3.72, s * 4.1, 2.6, WALL_Y0 + 0.06, -HZ + 0.45, HZ - 0.45, "wood_dark", detail=True)   # larguero

    # ---------------- bastidor, plataformas, barandas, escalones ----------------
    B(mk, body, -WIN, WIN, FLOOR_Y - 0.3, FLOOR_Y, -HC + 0.2, HC - 0.2, "wood_mid", detail=True)        # piso
    for d in (-1, 1):
        B(mk, body, -4.1, 4.1, 2.2, FLOOR_Y - 0.28, d * (HZ - 0.45), d * (HZ + 0.05), "wood_dark", detail=True)   # viga
        B(mk, body, -3.9, 3.9, 3.0, FLOOR_Y - 0.13, d * (HC - 0.1), d * (HZ - 0.4), "wood_dark", detail=True)   # base
        for k in range(4):                                                                           # tablas de la plataforma
            z0 = d * (HC + 0.02 + k * 0.5)
            B(mk, body, -3.98 + 0.01 * (k % 2), 3.98 - 0.01 * (k % 2), FLOOR_Y - 0.14, FLOOR_Y, z0, z0 + d * 0.46,
              "wood_dark", detail=True)
        zr = d * (HZ - 0.15)
        for x in (-3.75, -1.25, 1.25, 3.75):
            B(mk, body, x - 0.05, x + 0.05, FLOOR_Y - 0.05, 6.75, zr - 0.05, zr + 0.05, "iron", detail=True)
        for y in (5.1, 6.7):
            bar(mk, body, (-3.8, y, zr), (3.8, y, zr), 0.09, 0.09, "iron", ext=0.02, detail=True)
        for s in (-1, 1):                                                                            # pasamanos al costado
            bar(mk, body, (s * 3.75, 6.7, zr), (s * 3.75, 6.7, d * (HC + 0.1)), 0.08, 0.08, "iron", ext=0.03, detail=True)
            for z in (d * (HC + 0.4), d * (HZ - 0.38)):                                               # escalón de la esquina
                B(mk, body, s * 3.78, s * 3.88, 1.32, FLOOR_Y - 0.2, z - 0.05, z + 0.05, "iron", detail=True)
            B(mk, body, s * 3.55, s * 4.05, 1.3, 1.42, d * (HC + 0.3), d * (HZ - 0.3), "iron", detail=True)
    for zc in TRUCK_Z:
        B(mk, body, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark", detail=True)
    B(mk, body, -0.6, 0.6, 2.6, FLOOR_Y - 0.29, -HZ + 0.45, HZ - 0.45, "wood_dark", detail=True)        # larguero central
    B(mk, body, -2.6, -0.8, 1.6, 2.6, -2.2, 2.2, "wood_dark", detail=True)                            # cajón de herramientas
    B(mk, body, -2.65, -0.75, 1.55, 1.68, -2.25, 2.25, "iron", detail=True)

    # ---------------- techo, escalera, chimenea ----------------
    gable(mk, body, RIDGE, EAVE_Y, EAVE_X, HC + 1.2)
    for x0, x1 in ((1.45, 2.35),):
        z = -HC - 0.3
        for x in (x0, x1):
            bar(mk, body, (x, FLOOR_Y, z), (x, 12.1, z), 0.1, 0.1, "iron", up=(0, 0, 1), detail=True)
            for y in (5.0, 10.2):
                B(mk, body, x - 0.04, x + 0.04, y - 0.05, y + 0.05, z - 0.02, -HC + 0.02, "iron", detail=True)
        for k in range(7):
            y = FLOOR_Y + 0.6 + k * 1.2
            bar(mk, body, (x0, y, z), (x1, y, z), 0.08, 0.08, "iron", up=(0, 0, 1), ext=0.02, detail=True)
    cx, cz = -1.6, 6.2
    mk.cyl(body, (cx, top(cx) + 0.55, cz), 0.22, 1.5, "iron", axis="y", sides=8, detail=True)          # chimenea
    mk.cyl(body, (cx, top(cx) + 0.12, cz), 0.34, 0.3, "iron", axis="y", sides=8, detail=True)
    mk.cyl(body, (cx, top(cx) + 1.4, cz), 0.42, 0.24, "iron", axis="y", sides=8, top=0.4, detail=True)

    # ---------------- farol rojo colgado de la baranda de atrás ----------------
    lx, lz = 2.6, HZ - 0.15
    bar(mk, body, (lx, 6.7, lz), (lx, 6.25, lz), 0.05, 0.05, "iron", detail=True)                    # gancho
    mk.cyl(body, (lx, 5.65, lz), 0.26, 0.7, "iron", axis="y", sides=8, detail=True)                    # cuerpo
    mk.cyl(body, (lx, 6.08, lz), 0.3, 0.16, "paint_red", axis="y", sides=8, top=0.6, detail=True)      # tapa roja
    mk.cyl(body, (lx, 5.27, lz), 0.3, 0.1, "paint_red", axis="y", sides=8, detail=True)
    g = mk.part("BackLantern_Glow", (0, 0, 0))
    mk.cyl(g, (lx, 5.65, lz + 0.26), 0.17, 0.12, "lamp_glow", axis="z", sides=8)

    # ---------------- cúpula ----------------
    cu = mk.part("Cupola", (0, RIDGE, 0))
    y0 = top(CUP_X) - 0.14
    cy_w0, cy_w1 = 12.2, 13.35
    cup_y1 = top(CUP_X - 0.15, CUP_RIDGE, CUP_EAVE, CUP_X + 0.25) - ROOF_T + 0.03
    for s in (-1, 1):
        wall_x(mk, cu, s, CUP_X - 0.15, CUP_X, y0, cup_y1, -CUP_Z, CUP_Z, ((-2.5, -0.35), (0.35, 2.5)), cy_w0, cy_w1)
    for d in (-1, 1):
        zo, zi = d * CUP_Z, d * (CUP_Z - 0.15)
        B(mk, cu, -CUP_X + 0.16, CUP_X - 0.16, y0 + 0.01, cy_w0, zi, zo - d * 0.005, "paint_red")
        for x0, x1 in ((-CUP_X + 0.17, -1.5), (1.5, CUP_X - 0.17)):
            B(mk, cu, x0, x1, cy_w0 - 0.01, cy_w1 + 0.01, zi + d * 0.005, zo - d * 0.01, "paint_red")
        mk.hull(cu, [(x, y, z) for z in (zi, zo - d * 0.005) for x, y in
                     ((-CUP_X + 0.16, cy_w1), (CUP_X - 0.16, cy_w1), (CUP_X - 0.16, cup_y1),
                      (0, CUP_RIDGE - ROOF_T + 0.03), (-CUP_X + 0.16, cup_y1))], "paint_red")
        mk.paint(cu, "wood_mid", box=((0, 12.6, zi), (2 * CUP_X, 3.0, 0.004)))
    for s in (-1, 1):
        mk.paint(cu, "wood_mid", box=((s * (CUP_X - 0.15), 12.6, 0), (0.004, 3.0, 2 * CUP_Z)))
    gable(mk, cu, CUP_RIDGE, CUP_EAVE, CUP_X + 0.25, CUP_Z + 0.25)
    for s in (-1, 1):
        for d in (-1, 1):
            B(mk, cu, s * (CUP_X - 0.05), s * (CUP_X + 0.07), y0 - 0.02, cup_y1 - 0.02, d * (CUP_Z - 0.1), d * (CUP_Z + 0.07),
              "wood_dark", detail=True)                                                             # esquineros
        B(mk, cu, s * (CUP_X - 0.04), s * (CUP_X + 0.1), cy_w0 - 0.14, cy_w0 + 0.02, -CUP_Z + 0.1, CUP_Z - 0.1, "wood_dark",
          detail=True)                                                                              # alféizar
    for d in (-1, 1):
        B(mk, cu, -1.6, 1.6, cy_w0 - 0.14, cy_w0 + 0.02, d * (CUP_Z - 0.04), d * (CUP_Z + 0.1), "wood_dark", detail=True)

    w = mk.part("Wheels", (0, 0, 0))
    for zc in TRUCK_Z:
        T.truck(mk, w, zc)
    T.coupler(mk, "CouplerFront", -(HZ + 0.05), -1, link=True)

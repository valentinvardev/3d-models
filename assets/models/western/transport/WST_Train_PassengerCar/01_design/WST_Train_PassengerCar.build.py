"""
Receta de WST_Train_PassengerCar, el vagón de pasajeros de 1870 que es la sala de preparación (prompt 074,
Bloques A + B). Se juega adentro: 4 jugadores, Old Hank y el armero.

Brief
- Silueta a 40 studs: vagón largo turquesa con techo de linterna (la franja del medio levantada con
  ventanitas), fila de 8 ventanas por costado con marcos mostaza, tablero crema sin texto arriba de las
  ventanas, plataformas abiertas con techo en las dos puntas.
- Adentro: pasillo de 3 al medio con alfombra roja, bancos de madera con almohadones rojos enfrentados, paredes
  de madera lustrada con molduras oscuras, cielo raso crema, 4 lámparas de aceite colgando al centro,
  portaequipajes de bronce con valijas. A la izquierda, los 10 del medio vacíos (armero y jugadores).
- Medidas: 34 de largo (caja de 30 entre z = ±15 y plataformas de 2), 9 de ancho (aleros a ±4,5; paredes
  a ±4,3), 12 de alto (techo de la linterna). Piso adentro a 3,5; cielo raso de la linterna a 11,0 (7,5 sobre
  el piso). Pasillo x = ±1,5. Ventanas de 1,6 x 2,7 (y 5,8 a 8,5). Enganche a 2,6.
- Piezas: Shell (caja, techo, linterna, plataformas, puertas, bastidor, bogies y cabezas de enganche: el prompt
  no las lista aparte), Interior (12 bancos), LuggageRacks, Lamps + Lamp_Glow_1..4 (vidrios aparte para
  apagarlos), Floor (tablas y alfombra), Windows (los 16 vidrios y los de las puertas). Marcadores _Hank,
  _Spawn_1.._4, _Rack.
- Inferido: "3 pares por lado" = 3 pares de bancos enfrentados por lado (12 bancos); a la izquierda dos pares
  adelante y uno atrás, y la pared del medio sin ventanas (las 8 de ese lado quedan en las dos puntas);
  ventanitas de la linterna pintadas de vidrio sobre la pared (no son pieza aparte); cielo raso crema;
  techo de madera oscura; puertas cerradas con ventana; bogies y cabezas de enganche fijas dentro de Shell;
  Old Hank en el banco de la punta de adelante a la izquierda, mirando al medio.

Vueltas: 1) primera versión: 5512 triángulos (las franjas mostaza de las jambas eran 64 cortes que partían todo
el casco), techo bajo inclinado al revés, cabecera de los bancos de 0,16 cuando miraban a -Z, dos pares no
entraban en los 9,8 de la izquierda (separación 1,6), z-fighting en los esquineros, colgaderas, paredes de
la linterna y asientos de la izquierda (coplanares con su cabecera) · 2) marcos de ventana = alféizar y
dintel mostaza corridos + derrames pintados de mostaza (sin cortes), bancos medidos desde el pasillo,
separación 1,5 (1,76 de piernas), umbral bajo las puertas, sin agarraderas de bronce en las plataformas ·
3) cabezal mostaza de la puerta 0,005 más ancho que sus postes.

Revisión
- 4952 triángulos contra 4000 (+24 %): Shell 2924 (bogies 840 incluidos), bancos 720 (12 bancos de 5 cascos
  con almohadón), lámparas 384 + vidrios 112, portaequipajes 380 (bronce, 4 valijas, 2 bolsos de alfombra,
  partido a la izquierda para dejar lugar al armero), piso 144, vidrios 216.
- Medidas: 35,0 de largo (34 de plataforma a plataforma + cabezas de enganche), 8,99 de ancho, 12,0 de alto.
  Piso adentro a 3,5; cielo raso de la linterna a 11,0 (7,5 sobre el piso); bajo el techo bajo, junto a las
  paredes, el cielo queda a ~9,85 (6,35 sobre el piso). Pasillo de 3, entre bancos enfrentados quedan 1,76.
- La izquierda (x < 0) tiene sus 8 ventanas en las puntas y la pared ciega en z ±5 para el armero (_Rack);
  el armero de 6 de alto llega a 9,5 y el portaequipajes de ese lado se corta en z ±5,3.
- Hecho para jugar adentro: la colisión por casco convexo cerraría el pasillo; en Studio, colisión precisa o
  piezas de colisión aparte. Bogies y cabezas de enganche fijos dentro de Shell (el prompt no los lista).
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


T = _load("WST_Train_Tender")
L = T.L
B, bar, pipe = L.B, L.bar, L.pipe

HC, HZ = 15.0, 16.95                   # punta de la caja y punta de las plataformas
WX, WIN = 4.3, 4.1                     # cara de afuera y de adentro de los costados
EAVE_X, EAVE_Y = 4.5, 9.9              # alero del techo bajo
CL_X0, CL_X1 = 2.2, 2.35               # paredes de la linterna (adentro, afuera)
LOW_Y = 10.5                           # techo bajo en la pared de la linterna
CEIL_Y, TOP_Y = 11.0, 12.0             # cielo raso de la linterna y cumbrera
FLOOR_Y, WALL_Y0, WALL_Y1 = 3.5, 2.9, 9.95
WY0, WY1, WW = 5.8, 8.5, 1.6           # ventanas
AISLE = 1.5
TRUCK_Z = (-11.5, 11.5)
RIGHT_WINS = [-12.6, -9.0, -5.4, -1.8, 1.8, 5.4, 9.0, 12.6]
LEFT_WINS = [-13.3, -10.8, -8.3, -5.8, 5.8, 8.3, 10.8, 13.3]   # el medio (z ±5) queda ciego para el armero
CLERESTORY = [-12.6, -9.0, -5.4, -1.8, 1.8, 5.4, 9.0, 12.6]
LAMP_Z = (-11.25, -3.75, 3.75, 11.25)
DOOR_X, DOOR_Y1 = 1.15, 9.35


def low_roof_top(x):
    return EAVE_Y + (LOW_Y - EAVE_Y) * (EAVE_X - abs(x)) / (EAVE_X - CL_X1)


def wall_x(mk, part, s, z0, z1, wins):
    """Costado con huecos de ventana: bandas enteras y pilares metidos 0,01 (sin vértices compartidos)."""
    B(mk, part, s * WIN, s * WX, WALL_Y0, WY0, z0, z1, "paint_teal")
    B(mk, part, s * WIN, s * WX, WY1, WALL_Y1, z0, z1, "paint_teal")
    edges = [z0 + 0.01] + [v for c in wins for v in (c - WW / 2, c + WW / 2)] + [z1 - 0.01]
    for a, b in zip(edges[0::2], edges[1::2]):
        B(mk, part, s * (WIN + 0.01), s * (WX - 0.005), WY0 - 0.01, WY1 + 0.01, a, b, "paint_teal")


def bench(mk, part, x0, x1, zc, f):
    """Banco de madera con almohadones rojos; f = +1 mira hacia +Z (respaldo del lado -Z)."""
    sx = 1 if x1 > x0 else -1                                                            # x0: pasillo, x1: pared
    zb = zc - f * 0.62                                                                   # borde del respaldo
    B(mk, part, x0 + sx * 0.04, x1, 4.72, 4.92, zc - 0.62, zc + 0.62, "wood_dark")       # asiento
    B(mk, part, x0 + sx * 0.18, x1 - sx * 0.04, 4.9, 5.16, zc - 0.58, zc + 0.56, "cloth_red")   # almohadón
    xa, xb = x0 + sx * 0.04, x1
    mk.hull(part, [(x, y, z) for x in (xa, xb) for y, z in
                   ((4.8, zb), (4.8, zb - f * 0.16), (7.15, zb - f * 0.25), (7.15, zb - f * 0.09))], "wood_dark")  # respaldo
    mk.hull(part, [(x, y, z) for x in (x0 + sx * 0.2, x1 - sx * 0.06) for y, z in
                   ((5.1, zb - f * 0.02), (5.1, zb + f * 0.16), (6.9, zb - f * 0.085), (6.9, zb + f * 0.09))], "cloth_red")
    B(mk, part, x0, x0 + sx * 0.14, FLOOR_Y - 0.02, 5.55, zc - 0.66, zc + 0.66, "wood_dark")   # cabecera del pasillo


def build(mk):
    sh = mk.part("Shell", (0, 0, 0))
    # ================= base (se pinta): costados, puntas, linterna, techo de la linterna =================
    wall_x(mk, sh, 1, -HC, HC, RIGHT_WINS)
    wall_x(mk, sh, -1, -HC, HC, LEFT_WINS)
    lt = low_roof_top(WIN) - 0.17
    for d in (-1, 1):
        prof = [(-4.11, WALL_Y0), (-DOOR_X, WALL_Y0), (-DOOR_X, DOOR_Y1), (DOOR_X, DOOR_Y1), (DOOR_X, WALL_Y0),
                (4.11, WALL_Y0), (4.11, lt + 0.04), (CL_X0 + 0.02, low_roof_top(CL_X0) - 0.13),
                (CL_X0 + 0.02, CEIL_Y + 0.03), (-CL_X0 - 0.02, CEIL_Y + 0.03), (-CL_X0 - 0.02, low_roof_top(CL_X0) - 0.13),
                (-4.11, lt + 0.04)]
        mk.prism(sh, prof, 0.195, "paint_teal", plane="xy", center=(0, 0, d * (HC - 0.1025)))
    for s in (-1, 1):
        B(mk, sh, s * CL_X0, s * CL_X1, LOW_Y - 0.25, CEIL_Y + 0.04, -HZ + 0.03, HZ - 0.03, "paint_teal")
    ring = [(-2.62, CEIL_Y), (2.62, CEIL_Y), (2.62, 11.32), (1.75, 11.74), (0.9, 11.94), (0, TOP_Y), (-0.9, 11.94),
            (-1.75, 11.74), (-2.62, 11.32)]
    mk.hull(sh, [(x, y, z) for x, y in ring for z in (-HZ, HZ)], "wood_dark")
    # pintura: adentro madera lustrada y cielo raso crema; marcos mostaza; ventanitas de la linterna
    for s in (-1, 1):
        mk.paint(sh, "wood_mid", box=((s * (WIN + 0.005), 6.4, 0), (0.025, 7.2, 2 * HC)))
        mk.paint(sh, "paint_cream", box=((s * CL_X0, 10.75, 0), (0.004, 0.8, 2 * HZ)))
    mk.paint(sh, "paint_cream", box=((0, CEIL_Y, 0), (5.3, 0.004, 2 * HZ + 0.1)))
    for d in (-1, 1):
        mk.paint(sh, "wood_mid", box=((0, 6.5, d * (HC - 0.2)), (8.3, 7.4, 0.004)))
        mk.paint(sh, "paint_cream", box=((0, 10.6, d * (HC - 0.2)), (4.5, 0.9, 0.004)))
    for s, wins in ((1, RIGHT_WINS), (-1, LEFT_WINS)):
        for c in wins:
            for e in (c - WW / 2, c + WW / 2):
                mk.paint(sh, "paint_mustard", box=((s * (WIN + WX) / 2, (WY0 + WY1) / 2, e), (0.22, WY1 - WY0, 0.004)))
            for y in (WY0, WY1):
                mk.paint(sh, "paint_mustard", box=((s * (WIN + WX) / 2, y, c), (0.22, 0.004, WW)))
    for y in (10.62, 10.92):
        mk.slice(sh, (0, y, 0), (0, 1, 0))
    for c in CLERESTORY:
        for e in (c - 0.6, c + 0.6):
            mk.slice(sh, (0, 0, e), (0, 0, 1))
        for s in (-1, 1):
            for x in (s * CL_X0, s * CL_X1):
                mk.paint(sh, "glass", box=((x, 10.77, c), (0.004, 0.29, 1.19)))

    # ================= detalle: molduras, letrero, techo bajo, puertas, plataformas, bastidor, bogies =================
    for s in (-1, 1):
        B(mk, sh, s * 4.28, s * 4.36, WY0 - 0.2, WY0 + 0.02, -HC + 0.05, HC - 0.05, "paint_mustard", detail=True)   # alféizar
        B(mk, sh, s * 4.28, s * 4.35, WY1 - 0.02, WY1 + 0.16, -HC + 0.05, HC - 0.05, "paint_mustard", detail=True)  # dintel
        B(mk, sh, s * 4.28, s * 4.34, WALL_Y0 - 0.03, 3.3, -HC + 0.04, HC - 0.04, "paint_mustard", detail=True)     # zócalo
        B(mk, sh, s * 4.28, s * 4.33, 8.88, 9.68, -12.6, 12.6, "paint_mustard", detail=True)                      # marco del letrero
        B(mk, sh, s * 4.3, s * 4.345, 8.95, 9.61, -12.5, 12.5, "paint_cream", detail=True)                         # letrero liso
        for d in (-1, 1):
            B(mk, sh, s * 4.25, s * 4.37, WALL_Y0 - 0.02, WALL_Y1 - 0.04, d * (HC - 0.16), d * (HC + 0.07), "paint_mustard",
              detail=True)                                                                         # esquineros
        # adentro: molduras oscuras
        B(mk, sh, s * 4.0, s * 4.12, WY0 - 0.2, WY0 + 0.02, -HC + 0.2, HC - 0.2, "wood_dark", detail=True)
        B(mk, sh, s * 4.02, s * 4.12, WY1 + 0.05, WY1 + 0.22, -HC + 0.2, HC - 0.2, "wood_dark", detail=True)
        B(mk, sh, s * 4.03, s * 4.12, FLOOR_Y - 0.02, FLOOR_Y + 0.35, -HC + 0.2, HC - 0.2, "wood_dark", detail=True)
        # techo bajo y faldón sobre las plataformas
        ang = math.atan2(LOW_Y - EAVE_Y, EAVE_X - CL_X1)
        a = -s * ang
        ln = math.hypot(EAVE_X - CL_X1 + 0.12, LOW_Y - EAVE_Y)
        mx, my = s * (EAVE_X + CL_X1 - 0.12) / 2, (EAVE_Y + low_roof_top(CL_X1 - 0.12)) / 2
        mk.box(sh, (mx + math.sin(a) * 0.15 / 2, my - math.cos(a) * 0.15 / 2, 0), (ln, 0.15, 2 * HZ - 0.04), "wood_dark",
               rot=(0, 0, math.degrees(a)), detail=True)
    # puertas de las puntas: hoja baja, largueros y travesaño alrededor del vidrio, marco mostaza
    for d in (-1, 1):
        zc = d * (HC - 0.1)
        B(mk, sh, -DOOR_X + 0.01, DOOR_X - 0.01, FLOOR_Y - 0.02, 6.4, zc - 0.06, zc + 0.06, "wood_dark", detail=True)
        for x0, x1 in ((-DOOR_X + 0.02, -0.72), (0.72, DOOR_X - 0.02)):
            B(mk, sh, x0, x1, 6.38, DOOR_Y1 - 0.02, zc - 0.055, zc + 0.055, "wood_dark", detail=True)
        B(mk, sh, -0.73, 0.73, 8.95, DOOR_Y1 - 0.03, zc - 0.05, zc + 0.05, "wood_dark", detail=True)
        for x0, x1 in ((-DOOR_X - 0.18, -DOOR_X + 0.02), (DOOR_X - 0.02, DOOR_X + 0.18)):
            B(mk, sh, x0, x1, FLOOR_Y, DOOR_Y1 + 0.16, d * (HC - 0.01), d * (HC + 0.07), "paint_mustard", detail=True)
        B(mk, sh, -DOOR_X - 0.185, DOOR_X + 0.185, DOOR_Y1 - 0.02, DOOR_Y1 + 0.18, d * (HC - 0.015), d * (HC + 0.075),
          "paint_mustard", detail=True)
        B(mk, sh, 0.8, 0.95, 6.0, 6.15, zc + d * 0.05, zc + d * 0.16, "brass", detail=True)                  # picaporte
        B(mk, sh, -DOOR_X - 0.01, DOOR_X + 0.01, WALL_Y0, FLOOR_Y, d * (HC - 0.21), d * (HC - 0.003), "wood_dark",
          detail=True)                                                                           # umbral
        # plataforma: piso, barandas a los costados del paso, postes del faldón, escalones
        B(mk, sh, -4.3, 4.3, 3.0, FLOOR_Y, d * (HC + 0.005), d * (HZ - 0.02), "wood_dark", detail=True)
        zr = d * (HZ - 0.12)
        for s in (-1, 1):
            B(mk, sh, s * 4.12, s * 4.24, FLOOR_Y - 0.02, low_roof_top(4.18) - 0.05, zr - 0.06, zr + 0.06, "paint_mustard",
              detail=True)                                                                         # poste del faldón
            B(mk, sh, s * 1.25, s * 1.35, FLOOR_Y - 0.02, 6.7, zr - 0.05, zr + 0.05, "iron", detail=True)
            for y in (5.1, 6.65):
                bar(mk, sh, (s * 1.3, y, zr), (s * 4.18, y, zr), 0.08, 0.08, "iron", ext=0.02, detail=True)
            for z in (d * (HC + 0.35), d * (HZ - 0.45)):
                B(mk, sh, s * 3.98, s * 4.08, 1.32, 3.1, z - 0.05, z + 0.05, "iron", detail=True)
            B(mk, sh, s * 3.85, s * 4.35, 1.3, 1.42, d * (HC + 0.25), d * (HZ - 0.35), "iron", detail=True)
        B(mk, sh, -4.25, 4.25, 2.2, 3.02, d * (HZ - 0.45), d * (HZ + 0.03), "wood_dark", detail=True)     # viga de punta
        B(mk, sh, -0.36, 0.36, T.COUPLER_Y - 0.3, T.COUPLER_Y + 0.3, d * (HZ - 0.1), d * (HZ + 0.5), "iron", detail=True)
        B(mk, sh, -0.42, 0.42, T.COUPLER_Y + 0.09, T.COUPLER_Y + 0.34, d * (HZ + 0.18), d * (HZ + 0.55), "iron", detail=True)
    # bastidor, tensores, bogies
    for s in (-1, 1):
        B(mk, sh, s * 3.9, s * 4.32, 2.5, WALL_Y0 + 0.05, -HZ + 0.45, HZ - 0.45, "wood_dark", detail=True)
        B(mk, sh, s * 0.5, s * 1.0, 2.6, 3.21, -HZ + 0.45, HZ - 0.45, "wood_dark", detail=True)
        x = s * 2.2
        pts = [(x, 2.66, -12.0), (x, 1.3, -4.0), (x, 1.3, 4.0), (x, 2.66, 12.0)]
        for a_, b_ in zip(pts, pts[1:]):
            bar(mk, sh, a_, b_, 0.1, 0.1, "iron", ext=0.06, detail=True)
        for z in (-4.0, 4.0):
            B(mk, sh, x - 0.1, x + 0.1, 1.24, 2.62, z - 0.12, z + 0.12, "iron", detail=True)
    B(mk, sh, -4.0, 4.0, 2.62, 3.22, -HC + 0.2, HC - 0.2, "wood_dark", detail=True)                    # bajo piso
    for zc in TRUCK_Z:
        B(mk, sh, -3.8, 3.8, T.BOLSTER_TOP - 0.02, 2.64, zc - 0.45, zc + 0.45, "wood_dark", detail=True)
    for zc in TRUCK_Z:
        T.truck(mk, sh, zc, detail=True)

    # ================= piso y alfombra =================
    fl = mk.part("Floor", (0, 0, 0))
    B(mk, fl, -WIN, WIN, 3.22, 3.36, -HC + 0.2, HC - 0.2, "wood_dark")
    n = 8
    for i in range(n):
        xa = -WIN + 0.02 + i * (2 * WIN - 0.04) / n
        B(mk, fl, xa, xa + (2 * WIN - 0.04) / n - 0.05, 3.3, FLOOR_Y, -HC + 0.21 + 0.01 * (i % 2), HC - 0.21 - 0.01 * (i % 2),
          "wood_mid")
    B(mk, fl, -1.2, 1.2, FLOOR_Y - 0.02, FLOOR_Y + 0.05, -HC + 0.7, HC - 0.7, "cloth_red")              # alfombra
    for d in (-1, 1):
        B(mk, fl, -1.15, 1.15, FLOOR_Y - 0.01, FLOOR_Y + 0.06, d * (HC - 0.75), d * (HC - 0.62), "paint_mustard")  # fleco

    # ================= bancos =================
    it = mk.part("Interior", (0, 0, 0))
    hank = None
    right = [(-10.4,), (0.0,), (10.4,)]
    left = [(-12.4,), (-7.4,), (7.4,)]
    for s, pairs in ((1, right), (-1, left)):
        for (pz,) in pairs:
            for f in (1, -1):
                bench(mk, it, s * AISLE + s * 0.05, s * (WIN - 0.06), pz - f * 1.5, f)
                if s < 0 and pz == -12.4 and f == 1:
                    hank = (s * 2.8, 5.16, pz - 1.5)
    mk.marker("_Hank", hank)
    for k, (x, z) in enumerate(((-1.2, -2.6), (-2.6, -0.9), (-1.2, 0.9), (-2.6, 2.6)), start=1):
        mk.marker(f"_Spawn_{k}", (x, FLOOR_Y, z))
    mk.marker("_Rack", (-WIN, FLOOR_Y, 0))

    # ================= portaequipajes =================
    lr = mk.part("LuggageRacks", (0, 0, 0))
    ry = 9.0
    for s, spans in ((1, [(-14.4, 14.4)]), (-1, [(-14.4, -5.3), (5.3, 14.4)])):
        for z0, z1 in spans:
            for x in (s * 3.35, s * 3.95):
                bar(mk, lr, (x, ry, z0), (x, ry, z1), 0.08, 0.08, "brass", detail=False)
            k = max(2, int((z1 - z0) / 6) + 1)
            for i in range(k):
                z = z0 + 0.15 + i * (z1 - z0 - 0.3) / (k - 1)
                bar(mk, lr, (s * 4.12, ry + 0.75, z), (s * 3.33, ry - 0.02, z), 0.07, 0.07, "brass", ext=0.03)
    bags = [(1, -12.8, "leather", (1.1, 0.5, 0.45)), (1, -6.3, "leather_dark", (0.9, 0.45, 0.4)),
            (1, 3.6, "cloth_brown", None), (1, 9.4, "leather", (1.2, 0.55, 0.5)), (-1, -10.9, "cloth_red", None),
            (-1, -7.2, "leather", (1.0, 0.5, 0.42)), (-1, 11.6, "leather_dark", (1.1, 0.5, 0.45))]
    for s, z, mat, size in bags:
        xc = s * 3.65
        if size:
            sx, sy, sz = size
            B(mk, lr, xc - 0.42, xc + 0.42, ry + 0.02, ry + 0.02 + sy, z - sx / 2, z + sx / 2, mat)
            B(mk, lr, xc - 0.07, xc + 0.07, ry + sy, ry + sy + 0.12, z - 0.14, z + 0.14, "brass")      # manija
        else:                                                                                        # bolso de alfombra
            mk.hull(lr, [(xc + dx, ry + 0.02, z + dz) for dx in (-0.36, 0.36) for dz in (-0.5, 0.5)]
                    + [(xc + dx, ry + 0.5, z + dz) for dx in (-0.3, 0.3) for dz in (-0.42, 0.42)]
                    + [(xc, ry + 0.72, z + dz) for dz in (-0.3, 0.3)], mat)
            bar(mk, lr, (xc, ry + 0.7, z - 0.25), (xc, ry + 0.9, z), 0.06, 0.06, "leather_dark")
            bar(mk, lr, (xc, ry + 0.9, z), (xc, ry + 0.7, z + 0.25), 0.06, 0.06, "leather_dark")

    # ================= lámparas de aceite y sus vidrios =================
    lp = mk.part("Lamps", (0, 0, 0))
    for k, z in enumerate(LAMP_Z, start=1):
        mk.cyl(lp, (0, CEIL_Y - 0.06, z), 0.3, 0.16, "brass", axis="y", sides=8)                     # florón
        bar(mk, lp, (0, CEIL_Y - 0.1, z), (0, 10.25, z), 0.06, 0.06, "brass")                       # vara
        mk.cyl(lp, (0, 10.22, z), 0.62, 0.14, "brass", axis="y", sides=8, top=0.35)                 # pantalla
        mk.cyl(lp, (0, 9.42, z), 0.3, 0.3, "brass", axis="y", sides=8, top=0.75)                    # depósito
        g = mk.part(f"Lamp_Glow_{k}", (0, 0, 0))
        mk.cyl(g, (0, 9.85, z), 0.19, 0.66, "lamp_glow", axis="y", sides=8, top=0.75)               # tubo de vidrio

    # ================= vidrios =================
    wn = mk.part("Windows", (0, 0, 0))
    for s, wins in ((1, RIGHT_WINS), (-1, LEFT_WINS)):
        for c in wins:
            B(mk, wn, s * 4.18, s * 4.22, WY0 - 0.02, WY1 + 0.02, c - WW / 2 - 0.02, c + WW / 2 + 0.02, "glass")
    for d in (-1, 1):
        zc = d * (HC - 0.1)
        B(mk, wn, -0.725, 0.725, 6.39, 8.96, zc - 0.02, zc + 0.02, "glass")

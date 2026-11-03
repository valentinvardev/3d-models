"""
Receta de WST_Train_StockCar, el vagón de ganado (prompt 072, Bloques A + B). Es el vagón de carga
(WST_Train_Boxcar) con otros costados: de ahí importa medidas, techo, pasarela, escaleras y juntas, y del
ténder los bogies y los enganches. Así los dos calzan en el mismo tren (mismas alturas, mismos acoples,
mismos marcadores).

Brief
- Silueta a 40 studs: caja larga de madera clara descolorida con franjas oscuras horizontales que dejan pasar
  la luz (tablillas con aire), parantes y riostras oscuras por fuera en "A" a cada lado de la puerta, el
  mismo techo oscuro con la pasarela clara del vagón de carga, escaleras en dos esquinas, freno atrás.
- Medidas (las del vagón de carga): 30 de largo de caja (paredes de punta en z = ±15, enganches que salen
  0,5), 8,5 de ancho (alero y riel de la puerta), cumbrera a 12, pasarela a 12,22, piso adentro a 3,5,
  enganche a 2,6. Puertas de 6 x 8 (y 3,4 a 11,4) sobre el mismo riel; hueco de 5,8 x 7,75.
- Costados: zócalo de 2,95 a 3,95, 6 tablillas de 0,70 con 7 aires de 0,40 (el pedido) y cabezal de 10,95
  a 11,55. Tablillas en el plano x 3,75-3,90; parantes y riostras por fuera (x 3,88-4,0), debajo del plano
  de la puerta (4,02): la puerta corre sobre ellos sin chocar.
- Piezas: Body (caja, bastidor, techo, pasarela, escaleras, freno, tensores), SlidingDoorL y SlidingDoorR
  (origen arriba al centro, sobre el riel: corren en Z hasta z = 9,2 como en el vagón de carga), Ramp
  (origen en el perno de la bisagra, en el borde de afuera del umbral de la puerta derecha: (3,93, 3,56, 0),
  gira en Z), Wheels (dos bogies), CouplerFront y CouplerBack. Marcadores _Roof, _Gap_Front, _Gap_Back en
  el mismo lugar que en el vagón de carga.
- Se pinta: juntas de las puntas (wood_dark sobre franjas cortadas), tablas cambiadas (wood_mid), juntas
  de la rampa, el adentro en sombra (wood_dark). Las tablillas de los costados no se pintan por fuera: las
  juntas son aire de verdad.
- Inferido: puntas cerradas de tablas verticales con la cruz en X (como el vagón de carga, en madera clara);
  adentro pintado oscuro (madera en sombra: el aire entre tablillas se lee como franja oscura); la rampa va
  guardada parada adentro del hueco de la puerta derecha (6,9 de largo x 5,3 de ancho: bajada llega a
  x = 9,9 con ~30° de pendiente, de 3,5 a 0); para bajarla se abre la puerta y se gira -120° sobre Z (la
  punta de arriba sale hacia +X y baja); los tacos quedan hacia adentro guardada y hacia arriba bajada; una
  tablilla floja caída 0,42 en el costado derecho y tablillas cambiadas en madera media (el desgaste del
  Bloque A); adentro vacío y sin paja (sería el 7.º material); los caballos van en otro modelo (el caballo
  mide 6,0 x 2,45 x 8,55: entran parados a lo largo, dos filas, y pasan por el hueco de 5,8 x 7,75).

Vueltas: 1) primera versión: z-fighting en la cara de abajo del zócalo contra la punta (las dos en y = 2,95)
y en el cabezal de la puerta contra la solera (las dos en x = 4,15) · 2) zócalo a 2,97 y tablillas de la
puerta hasta 4,14; adentro oscuro (las tablillas pasan a la base para pintarles la cara de adentro): el
aire se leía claro porque se veía la cara de adentro del otro costado; las puntas como prisma (el casco
dejaba triángulos y los cortes de las juntas una arista suelta) · 3) la cara de afuera de la rampa lisa en
madera media: entre las tablillas de la puerta se leía como una pared de ladrillos.

Revisión
- 3548 triángulos contra 1600 (+122 %): bogies 840 y enganches 256 (los mismos del ténder y del vagón de
  carga: solos son el 68 % del tope), Body 1860 (el vagón de carga tiene 1686: lo mismo de bastidor, techo,
  pasarela, escaleras, freno y tensores, más 24 tablillas con aire, 8 parantes y 8 riostras), puertas 192
  cada una (tablillas con aire, largueros, riostra, colgadores, manija), rampa 172. Recortar escaleras,
  freno o tensores rompería la familia con el vagón de carga.
- Medidas: idénticas al vagón de carga (8,58 x 13,095 x 31,826): caja de 30, cumbrera a 12,0, pasarela a
  12,22, piso a 3,5, enganche a 2,6, _Roof (0, 12,22, 0), _Gap_Front (0, 12,22, -15,15), _Gap_Back
  (0, 12,22, 15,15).
- La caja es hueca: la colisión por casco convexo la cierra (igual que el vagón de carga). Para meter
  caballos o jugadores adentro, en Studio va con colisión precisa o con piezas de colisión aparte.
- Rampa bajada (calculado, -120° sobre el perno): la cara de abajo pasa a menos de 0,01 del borde de
  afuera de la guía de la puerta (x 4,2, y 3,36) y las hojas de la bisagra la rozan: se lee como que la
  rampa apoya en la guía. La punta queda en x ≈ 9,9, y ≈ 0,1.
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
HZ, SILL_Z, WALL_Y0, WALL_Y1, FLOOR_Y = BX.HZ, BX.SILL_Z, BX.WALL_Y0, BX.WALL_Y1, BX.FLOOR_Y
EAVE_Y, WALK_Y = BX.EAVE_Y, BX.WALK_Y
DOOR_Z, DOOR_Y0, DOOR_Y1, OPEN_Z, OPEN_Y1 = BX.DOOR_Z, BX.DOOR_Y0, BX.DOOR_Y1, BX.OPEN_Z, BX.OPEN_Y1
TRUCK_Z, END_SEAMS, roof_top = BX.TRUCK_Z, BX.END_SEAMS, BX.roof_top

# ---------------- costados de tablillas ----------------
SX0, SX1 = 3.75, 3.90            # plano de las tablillas (adentro, afuera)
PX0, PX1 = 3.88, 4.00            # parantes (la puerta corre en 4,02)
KICK_Y1, HEAD_Y0 = 3.95, 10.95   # zócalo arriba, cabezal abajo
GAP, N_SLATS = 0.40, 6
SLAT_H = (HEAD_Y0 - KICK_Y1 - (N_SLATS + 1) * GAP) / N_SLATS        # 0,70
SLATS = [(KICK_Y1 + GAP + k * (SLAT_H + GAP), KICK_Y1 + GAP + k * (SLAT_H + GAP) + SLAT_H) for k in range(N_SLATS)]
SIDE_Z = HZ - 0.1                # las tablillas entran en la pared de punta
JAMB = (OPEN_Z - 0.02, OPEN_Z + 0.34)   # parante de la puerta
MID = (8.84, 9.16)               # parante del medio de cada mitad
CORNER_Z = HZ - 0.15             # cara de adentro del esquinero

# ---------------- rampa ----------------
HINGE = (3.93, FLOOR_Y + 0.06, 0.0)   # perno: entra 0,01 en el umbral
RAMP_X = (3.80, 3.97)                 # tablero guardado (cara de los tacos, cara de afuera)
RAMP_L, RAMP_W = 6.9, 5.3
RAMP_SEAMS = [-RAMP_W / 2 + k * RAMP_W / 5 for k in range(1, 5)]


def side_wall(mk, body, s):
    """Un costado: zócalo, cabezal, tablillas con aire, umbral y dintel del hueco, parantes y riostras en A."""
    x0, x1 = s * SX0, s * SX1
    halves = ((-SIDE_Z, -OPEN_Z), (OPEN_Z, SIDE_Z))
    # tablillas: (lado, mitad, fila) -> material o ("sag", caída en la punta) para la floja
    swap = {(1, -1, 4): "wood_mid", (-1, 1, 1): "wood_mid", (-1, -1, 5): "wood_mid", (1, 1, 0): "wood_mid"}
    sag = {(1, 1, 2): 0.42}
    for d, (z0, z1) in zip((-1, 1), halves):
        B(mk, body, s * SX0, s * (SX1 + 0.07), WALL_Y0 + 0.02, KICK_Y1, z0, z1, "wood_light")   # zócalo
        B(mk, body, s * SX0, s * (SX1 + 0.07), HEAD_Y0, WALL_Y1, z0, z1, "wood_light")          # cabezal
        for k, (y0, y1) in enumerate(SLATS):
            mat = swap.get((s, d, k), "wood_light")
            drop = sag.get((s, d, k))
            if drop is None:
                B(mk, body, x0, x1, y0, y1, z0, z1, mat)
                continue
            # tablilla floja: entera hasta el parante del medio; la otra mitad, suelta de la punta, cae
            zin, zout, zm = d * OPEN_Z, d * SIDE_Z, d * (MID[0] + MID[1]) / 2
            B(mk, body, x0, x1, y0, y1, min(zin, zm + d * 0.05), max(zin, zm + d * 0.05), mat)
            pts = []
            for x in (x0 + s * 0.01, x1 - s * 0.01):          # más fina: sin caras coplanares en el empalme
                pts += [(x, y0 + 0.01, zm - d * 0.05), (x, y1 - 0.01, zm - d * 0.05),
                        (x, y0 - drop, zout), (x, y1 - drop, zout)]
            mk.hull(body, pts, mat)
    # umbral y dintel del hueco (otro x que el zócalo y el cabezal: sin caras coplanares)
    B(mk, body, s * (SX0 + 0.01), s * (SX1 + 0.06), WALL_Y0 + 0.01, FLOOR_Y, -OPEN_Z - 0.02, OPEN_Z + 0.02, "wood_light")
    B(mk, body, s * (SX0 + 0.01), s * (SX1 + 0.06), OPEN_Y1, WALL_Y1 - 0.01, -OPEN_Z - 0.02, OPEN_Z + 0.02, "wood_light")
    # parantes por fuera
    for d in (-1, 1):
        for za, zb in (JAMB, MID):
            B(mk, body, s * PX0, s * PX1, WALL_Y0 + 0.03, EAVE_Y - 0.29, d * za, d * zb, "wood_dark", detail=True)
    # riostras en A: suben de la puerta y de la punta al parante del medio. Cada una con otro grosor (entre
    # ellas y contra los parantes): se cruzan arriba sin caras coplanares
    for d in (-1, 1):
        top = d * (MID[0] + MID[1]) / 2
        for (xa, xb), zb in (((3.885, 3.99), d * (JAMB[1] + 0.12)), ((3.89, 3.985), d * (CORNER_Z - 0.12))):
            bar(mk, body, (s * (xa + xb) / 2, WALL_Y0 + 0.25, zb), (s * (xa + xb) / 2, HEAD_Y0 + 0.2, top), 0.3, xb - xa,
                "wood_dark", up=(1, 0, 0), detail=True)


def frame(mk, body):
    """Bastidor, cruz de las puntas, traviesas y tensores: los del vagón de carga, iguales."""
    for s in (-1, 1):
        B(mk, body, s * 3.72, s * 4.1, 2.6, WALL_Y0 + 0.06, -HZ + 0.42, HZ - 0.42, "wood_dark", detail=True)        # larguero
        B(mk, body, s * 0.5, s * 1.0, 2.6, FLOOR_Y - 0.29, -HZ + 0.42, HZ - 0.42, "wood_dark", detail=True)        # del medio
        B(mk, body, s * 3.95, s * 4.15, EAVE_Y - 0.33, roof_top(4.15) - 0.03, -HZ - 0.06, HZ + 0.06, "wood_dark", detail=True)  # solera
        for d in (-1, 1):
            B(mk, body, s * 3.95, s * 4.13, 2.58, WALL_Y1 - 0.02, d * (HZ - 0.15), d * (HZ + 0.1), "wood_dark", detail=True)    # esquineros
    for d in (-1, 1):
        B(mk, body, -4.1, 4.1, 2.2, FLOOR_Y - 0.02, d * (HZ - 0.42), d * SILL_Z, "wood_dark", detail=True)         # viga de punta
        for k, (xa, xb) in enumerate(((-3.6, 3.6), (3.6, -3.6))):
            zz = d * (HZ + 0.05 + 0.035 * k)
            bar(mk, body, (xa, 3.3, zz), (xb, 10.95, zz), 0.32, 0.12 + 0.04 * k, "wood_dark", up=(0, 0, 1), detail=True)
        B(mk, body, -3.9, 3.9, 10.9, 11.25, d * (HZ - 0.02), d * (HZ + 0.12), "wood_dark", detail=True)              # cabezal
    for zc in TRUCK_Z:
        B(mk, body, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark", detail=True)          # traviesas
    for s in (-1, 1):
        x = s * 2.0
        pts = [(x, 2.66, -10.0), (x, 1.3, -3.2), (x, 1.3, 3.2), (x, 2.66, 10.0)]
        for a, b in zip(pts, pts[1:]):
            bar(mk, body, a, b, 0.1, 0.1, "iron", ext=0.06, detail=True)
        for z in (-3.2, 3.2):
            B(mk, body, x - 0.1, x + 0.1, 1.24, 2.62, z - 0.12, z + 0.12, "iron", detail=True)


def door(mk, s, name):
    """Puerta corrediza de tablillas (con el mismo aire que el costado), largueros, riostra, colgadores y manija."""
    x0, x1 = s * 4.03, s * 4.14
    d = mk.part(name, (s * 4.09, DOOR_Y1, 0))
    zi = DOOR_Z - 0.26
    B(mk, d, x0, x1, DOOR_Y0 + 0.02, KICK_Y1, -zi - 0.02, zi + 0.02, "wood_light")                  # zócalo
    B(mk, d, x0, x1, HEAD_Y0, DOOR_Y1 - 0.02, -zi - 0.02, zi + 0.02, "wood_light")                  # cabezal
    for k, (y0, y1) in enumerate(SLATS):
        B(mk, d, x0, x1, y0, y1, -zi - 0.02, zi + 0.02, "wood_mid" if (s, k) in ((1, 3), (-1, 1)) else "wood_light")
    mk.paint(d, "wood_dark", box=((x0, 7.4, 0), (0.004, 8.2, 2 * DOOR_Z)))                                        # cara de adentro
    for z0, z1 in ((-DOOR_Z, -zi), (zi, DOOR_Z)):
        B(mk, d, s * 4.02, s * 4.2, DOOR_Y0, DOOR_Y1, z0, z1, "wood_dark", detail=True)                           # largueros
    bar(mk, d, (s * 4.17, DOOR_Y0 + 0.35, -zi + 0.1), (s * 4.17, HEAD_Y0 + 0.2, zi - 0.1), 0.3, 0.07, "wood_dark",
        up=(s, 0, 0), detail=True)                                                                                 # riostra
    for z in (-2.2, 2.2):
        B(mk, d, s * 4.06, s * 4.2, DOOR_Y1 - 0.1, 11.5, z - 0.12, z + 0.12, "iron", detail=True)                  # colgadores
    bar(mk, d, (s * 4.25, 6.6, -DOOR_Z + 0.5), (s * 4.25, 8.0, -DOOR_Z + 0.5), 0.08, 0.08, "iron", detail=True)       # manija
    for y in (6.75, 7.85):                                                                                         # sobre las tablillas
        B(mk, d, s * 4.13, s * 4.27, y - 0.04, y + 0.04, -DOOR_Z + 0.47, -DOOR_Z + 0.53, "iron", detail=True)


def ramp(mk):
    """Rampa guardada parada en el hueco de la puerta derecha. Gira sobre el perno de la bisagra (eje Z),
    apoyado en el borde de afuera del umbral."""
    hx, hy, _ = HINGE
    r = mk.part("Ramp", HINGE)
    xi, xo = RAMP_X
    y0 = FLOOR_Y + 0.01
    B(mk, r, xi, xo, y0, y0 + RAMP_L, -RAMP_W / 2, RAMP_W / 2, "wood_light")                                      # tablero
    for p in RAMP_SEAMS:                                                                                            # juntas de la cara de los tacos
        for k in (-1, 1):
            mk.slice(r, (0, 0, p + k * 0.025), (0, 0, 1))
        mk.paint(r, "wood_dark", box=((xi, y0 + RAMP_L / 2, p), (0.004, RAMP_L, 0.045)))
    mk.paint(r, "wood_mid", box=((xi, y0 + RAMP_L / 2, (RAMP_SEAMS[1] + RAMP_SEAMS[2]) / 2), (0.004, RAMP_L, RAMP_W / 5 * 0.8)))
    # la cara de afuera (la de abajo bajada) va lisa y más oscura: entre las tablillas de la puerta se lee
    # como algo que está detrás, no como otra fila de tablas
    mk.paint(r, "wood_mid", box=((xo, y0 + RAMP_L / 2, 0), (0.004, RAMP_L + 0.1, RAMP_W + 0.1)))
    for k in range(7):                                                                                              # tacos
        y = y0 + 0.55 + k * 0.95
        B(mk, r, xi - 0.12, xi + 0.02, y - 0.09, y + 0.09, -RAMP_W / 2 + 0.12, RAMP_W / 2 - 0.12, "wood_dark", detail=True)
    for z in (-1.9, 1.9):                                                                                           # hojas de la bisagra
        B(mk, r, xo - 0.01, xo + 0.025, y0 - 0.03, y0 + 0.7, z - 0.13, z + 0.13, "iron", detail=True)
    pipe(mk, r, (hx, hy, -2.3), (hx, hy, 2.3), 0.07, "iron", sides=6, detail=True)                                  # perno


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- puntas cerradas (lo único de la base: se cortan y se pintan las juntas) ----------------
    for d in (-1, 1):
        zo, zi = d * (HZ - 0.005), d * (HZ - 0.2)
        wx = SX1 + 0.01
        # prisma (caras enteras, no triángulos): los cortes de las juntas no dejan astillas en la cara de abajo
        mk.prism(body, [(-wx, WALL_Y0), (wx, WALL_Y0), (wx, BX.roof_under(wx) + 0.04), (0, BX.roof_under(0) + 0.04),
                        (-wx, BX.roof_under(wx) + 0.04)], abs(zo - zi), "wood_light", center=(0, 0, (zo + zi) / 2))
        BX.seams(mk, body, "x", END_SEAMS, {"z": d * (HZ - 0.005)}, {"y": (7.4, 9.2)})
    for d, x in ((-1, -1.425), (1, 0.475), (1, 2.375)):                                                # tablas cambiadas
        mk.paint(body, "wood_mid", box=((x, 7.4, d * (HZ - 0.005)), (0.85, 9.2, 0.004)))
    B(mk, body, -SX0 - 0.01, SX0 + 0.01, FLOOR_Y - 0.3, FLOOR_Y, -HZ + 0.19, HZ - 0.19, "wood_mid", detail=True)  # piso

    for s in (-1, 1):
        side_wall(mk, body, s)
        # adentro en sombra: las caras de adentro de las tablillas en madera oscura, así el aire se lee oscuro
        mk.paint(body, "wood_dark", box=((s * (SX0 + 0.005), 7.25, 0), (0.03, 9.0, 2 * HZ)))
    for d in (-1, 1):
        mk.paint(body, "wood_dark", box=((0, 7.5, d * (HZ - 0.2)), (2 * (SX1 + 0.02), 9.6, 0.004)))
    frame(mk, body)

    # ---------------- riel y guía de las puertas (los del vagón de carga) ----------------
    for s in (-1, 1):
        B(mk, body, s * 4.12, s * 4.26, 11.42, 11.58, -DOOR_Z - 0.25, 9.2, "iron", detail=True)
        B(mk, body, s * 3.98, s * 4.2, 3.18, 3.36, -DOOR_Z - 0.25, 9.2, "iron", detail=True)
        for z in (-DOOR_Z - 0.15, 9.1):
            B(mk, body, s * 3.99, s * 4.27, 11.38, 11.62, z - 0.06, z + 0.06, "iron", detail=True)

    # ---------------- techo, pasarela, escaleras, freno (iguales al vagón de carga) ----------------
    BX.roof(mk, body)
    BX.catwalk(mk, body, -HZ - 0.15, HZ + 0.15, (-14.6, -10.0, -5.0, 0.0, 5.0, 10.0, 14.6))
    BX.end_ladder(mk, body, 2.5, 3.4, -HZ, -1)
    BX.end_ladder(mk, body, -3.4, -2.5, HZ, 1)
    zb = HZ + 0.35
    pipe(mk, body, (0, 3.6, zb), (0, 13.05, zb), 0.07, "iron", sides=6, detail=True)
    for y in (4.0, 8.0, 10.8):
        B(mk, body, -0.05, 0.05, y - 0.05, y + 0.05, HZ - 0.03, zb + 0.02, "iron", detail=True)
    annulus(mk, body, (0, 13.05, zb), 0.45, 0.6, 0.09, "iron", axis="y", sides=8, detail=True)
    for a in (0, 90):
        rr = math.radians(a)
        bar(mk, body, (-0.5 * math.cos(rr), 13.05, zb - 0.5 * math.sin(rr)), (0.5 * math.cos(rr), 13.05, zb + 0.5 * math.sin(rr)),
            0.07, 0.07, "iron", detail=True)

    door(mk, -1, "SlidingDoorL")
    door(mk, 1, "SlidingDoorR")
    ramp(mk)

    w = mk.part("Wheels", (0, 0, 0))
    for zc in TRUCK_Z:
        T.truck(mk, w, zc)
    T.coupler(mk, "CouplerFront", -SILL_Z, -1, link=True)
    T.coupler(mk, "CouplerBack", SILL_Z, 1)
    mk.marker("_Roof", (0, WALK_Y, 0))
    mk.marker("_Gap_Front", (0, WALK_Y, -HZ - 0.15))
    mk.marker("_Gap_Back", (0, WALK_Y, HZ + 0.15))

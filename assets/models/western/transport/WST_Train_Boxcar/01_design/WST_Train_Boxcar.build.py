"""
Receta de WST_Train_Boxcar, el vagón de carga de madera (prompt 071, Bloques A + B). Comparte bogies y
enganches con el ténder (de ahí se importan) y las medidas del tren con la locomotora.

Brief
- Silueta a 40 studs: caja roja larga de tablas verticales con techo a dos aguas apenas inclinado, pasarela
  de madera clara arriba al medio, puerta corrediza grande al centro de cada costado con su riel, cruces en
  X en las puntas, escaleras de hierro en dos esquinas opuestas, rueda de freno asomando sobre el techo.
- Medidas: 30 de largo (paredes de punta en z = ±15, enganches que salen 0,5), 8,5 de ancho (alero y riel
  de la puerta), techo con la cumbrera a 12 sobre los rieles y la pasarela de 2 de ancho con la cara de
  arriba a 12,22. Piso adentro a 3,5. Enganche a 2,6 como todo el tren. Puertas de 6 x 8 (y 3,4 a 11,4),
  hueco de 5,8 x 7,75.
- Piezas: Body (caja hueca, bastidor, techo, pasarela, escaleras, freno, tensores), SlidingDoorL y
  SlidingDoorR (origen arriba al centro, sobre el riel: corren en Z, el riel llega hasta z = 9,2),
  Wheels (dos bogies), CouplerFront y CouplerBack (origen en la cara de la viga). Marcadores _Roof (centro
  de la pasarela, arriba), _Gap_Front y _Gap_Back.
- Tablas: las juntas de 0,05 se pintan (wood_dark) sobre franjas cortadas con slice: se leen como las ranuras
  que pide el prompt sin costo de booleanas. Algunas tablas cambiadas en madera sin pintar (wood_mid).
  Adentro, las paredes van pintadas de madera (wood_mid) y el piso de tablas con juntas.
- Inferido: tablas de 1,0; techo de madera oscura a dos aguas (cumbrera 12, alero 11,65); tensores de hierro
  con pendolones bajo el piso (vagón de 1870); escaleras en las puntas (adelante a la derecha, atrás a la
  izquierda); freno atrás al centro; _Gap_* en las puntas de la pasarela (donde se salta de techo a techo).

Vueltas: 1) primera versión: los slice de las juntas cortaban todo el Body (86 680 triángulos crudos, 41
aristas sueltas, 2328 después de limpiar) y z-fighting en las puertas (largueros con la misma base que el
paño, soportes de la manija del ancho de la manija) · 2) todo lo que no se pinta pasa a la etapa de detalle
(bastidor, techo, pasarela, escaleras, freno, tensores): los cortes solo tocan costados y puntas; el piso
de adentro queda liso (detalle) · 3) caras de adentro de las puertas, jambas y dintel en madera sin pintar.

Revisión
- 3186 triángulos contra 1800 (+77 %): bogies 840 y enganches 256 (los mismos del ténder), puertas 368
  (paño con juntas, marco, riostra, colgadores, manija), Body 1690: costados con 23 juntas por lado,
  puntas con cruz en X, escaleras de 7 travesaños (240), freno, tensores con pendolones, riel y guía.
- Medidas: 30 de largo de caja (31,8 con escaleras, freno y enganches), 8,58 de ancho (manijas), cumbrera
  a 12,0, pasarela a 12,22 (0,22 sobre el techo), piso adentro a 3,5, enganche a 2,6.
- Las "ranuras de 0,05" del prompt van pintadas (franjas cortadas con slice), no hundidas: con luz plana se
  leen igual y no cuestan booleanas (regla de tablas del Bloque A).
- La caja es hueca: la colisión por casco convexo la cierra; para entrar a buscar cajas, en Studio va con
  colisión precisa o con piezas de colisión aparte.
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
B, bar, pipe, annulus = L.B, L.bar, L.pipe, L.annulus

# ---------------- medidas del vagón (las importan los restos) ----------------
HZ = 15.0                    # cara de afuera de las paredes de punta
SILL_Z = 15.06               # cara de la viga de punta (donde va el enganche)
WX, WIN = 4.0, 3.8           # cara de afuera y de adentro de los costados
WALL_Y0, WALL_Y1 = 2.95, 11.55
FLOOR_Y = 3.5
RIDGE_Y, EAVE_Y, EAVE_X, ROOF_T = 12.0, 11.65, 4.25, 0.16
WALK_Y = 12.22               # cara de arriba de la pasarela
DOOR_Z, DOOR_Y0, DOOR_Y1 = 3.0, 3.4, 11.4      # puerta de 6 x 8 (z ±3)
OPEN_Z, OPEN_Y1 = 2.9, 11.25                     # hueco
TRUCK_Z = (-10.5, 10.5)
BOARD = 1.0                  # ancho de tabla de los costados
END_SEAMS = [-3.8 + k * 0.95 for k in range(1, 8)]


def roof_top(x):
    return RIDGE_Y - (RIDGE_Y - EAVE_Y) * abs(x) / EAVE_X


def roof_under(x):
    return roof_top(x) - ROOF_T - 0.005


def roof(mk, part, hz=HZ + 0.2, mat="wood_dark", detail=True):
    """Techo a dos aguas: dos losas que se cruzan en la cumbrera (largos distintos: sin caras coplanares)."""
    ang = math.atan2(RIDGE_Y - EAVE_Y, EAVE_X)
    ln = math.hypot(EAVE_X + 0.06, RIDGE_Y - EAVE_Y)
    for s, dz in ((-1, 0.0), (1, 0.01)):
        a = -s * ang
        mx, my = s * (EAVE_X - 0.06) / 2, (roof_top(EAVE_X) + roof_top(0.06)) / 2
        mk.box(part, (mx + math.sin(a) * ROOF_T / 2, my - math.cos(a) * ROOF_T / 2, 0), (ln, ROOF_T, 2 * (hz - dz)), mat,
               rot=(0, 0, math.degrees(a)), detail=detail)


def catwalk(mk, part, z0, z1, saddles, mat="wood_mid", base="wood_dark", detail=True):
    """Pasarela de 3 tablas sobre caballetes, cara de arriba a WALK_Y."""
    for i, x in enumerate((-0.66, 0.0, 0.66)):
        B(mk, part, x - 0.3, x + 0.3, WALK_Y - 0.12, WALK_Y, z0 - (0.01 if i == 1 else 0), z1 + (0.01 if i == 1 else 0), mat,
          detail=detail)
    for z in saddles:
        B(mk, part, -1.02, 1.02, roof_top(1.02) - 0.1, WALK_Y - 0.11, z - 0.15, z + 0.15, base, detail=detail)


def end_ladder(mk, part, x0, x1, zw, d, y0=1.3, y1=12.7, rungs=7, stand=(2.4, 9.0), detail=True):
    """Escalera en la punta: largueros a 0,3 de la pared (zw, hacia d), apoyos en `stand`."""
    z = zw + d * 0.3
    for x in (x0, x1):
        bar(mk, part, (x, y0, z), (x, y1, z), 0.1, 0.1, "iron", up=(0, 0, 1), detail=detail)
        for y in stand:
            B(mk, part, x - 0.04, x + 0.04, y - 0.05, y + 0.05, min(z, zw) - 0.02, max(z, zw) + 0.02, "iron", detail=detail)
    for k in range(rungs):
        y = y0 + 0.45 + k * (y1 - y0 - 0.9) / (rungs - 1)
        bar(mk, part, (x0, y, z), (x1, y, z), 0.08, 0.08, "iron", up=(0, 0, 1), ext=0.02, detail=detail)


def seams(mk, part, axis, positions, face, span, mat="wood_dark", w=0.05, tol=0.004):
    """Juntas pintadas: corta franjas de ancho w en `positions` (sobre el eje `axis`) y pinta las caras que
    caen en el plano `face` (dict: eje -> valor), dentro de `span` (dict: eje -> (centro, largo))."""
    n = {"x": (1, 0, 0), "z": (0, 0, 1)}[axis]
    for p in positions:
        for k in (-1, 1):
            pt = [0.0, 0.0, 0.0]
            pt["xyz".index(axis)] = p + k * w / 2
            mk.slice(part, tuple(pt), n)
        c, sz = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        for ax, v in face.items():
            c["xyz".index(ax)], sz["xyz".index(ax)] = v, tol
        for ax, (cv, ln) in span.items():
            c["xyz".index(ax)], sz["xyz".index(ax)] = cv, ln
        c["xyz".index(axis)], sz["xyz".index(axis)] = p, w * 0.9
        mk.paint(part, mat, box=(tuple(c), tuple(sz)))


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- caja: costados con el hueco de la puerta, puntas a dos aguas, piso ----------------
    for s in (-1, 1):
        for z0, z1 in ((-HZ, -OPEN_Z), (OPEN_Z, HZ)):
            B(mk, body, s * WIN, s * WX, WALL_Y0, WALL_Y1, z0, z1, "paint_red")
        B(mk, body, s * WIN, s * WX, OPEN_Y1, WALL_Y1 - 0.01, -OPEN_Z, OPEN_Z, "paint_red")          # dintel
        B(mk, body, s * WIN, s * WX, WALL_Y0 + 0.01, FLOOR_Y, -OPEN_Z, OPEN_Z, "paint_red")          # bajo la puerta
    for d in (-1, 1):
        zo, zi = d * (HZ - 0.005), d * (HZ - 0.2)
        mk.hull(body, [(x, y, z) for z in (zo, zi) for x, y in
                       ((-WIN - 0.01, WALL_Y0), (WIN + 0.01, WALL_Y0), (WIN + 0.01, roof_under(WIN) + 0.04),
                        (0, roof_under(0) + 0.04), (-WIN - 0.01, roof_under(WIN) + 0.04))], "paint_red")
    B(mk, body, -WIN, WIN, FLOOR_Y - 0.3, FLOOR_Y, -HZ + 0.2, HZ - 0.2, "wood_mid", detail=True)    # piso (adentro: liso)
    # adentro: madera sin pintar; juntas de los costados y de las puntas
    for s in (-1, 1):
        mk.paint(body, "wood_mid", box=((s * WIN, 7.3, 0), (0.004, 9.0, 2 * HZ)))
    for d in (-1, 1):
        mk.paint(body, "wood_mid", box=((0, 7.5, d * (HZ - 0.2)), (2 * WIN, 9.4, 0.004)))
    for s in (-1, 1):                                                                               # jambas y dintel del hueco
        for z in (-OPEN_Z, OPEN_Z):
            mk.paint(body, "wood_mid", box=((s * 3.9, 7.4, z), (0.21, 7.9, 0.004)))
        for y in (OPEN_Y1, FLOOR_Y):
            mk.paint(body, "wood_mid", box=((s * 3.9, y, 0), (0.21, 0.004, 2 * OPEN_Z)))
    seams(mk, body, "z", [-HZ + BOARD * k for k in range(1, 30) if abs(-HZ + BOARD * k) > OPEN_Z + 0.2],
          {"x": WX}, {"y": (7.25, 8.7)})
    seams(mk, body, "z", [-HZ + BOARD * k for k in range(1, 30) if abs(-HZ + BOARD * k) > OPEN_Z + 0.2],
          {"x": -WX}, {"y": (7.25, 8.7)})
    for d in (-1, 1):
        seams(mk, body, "x", END_SEAMS, {"z": d * (HZ - 0.005)}, {"y": (7.4, 9.2)})
    for s, z in ((1, -11.5), (1, 6.5), (1, 12.5), (-1, -8.5), (-1, 4.5), (-1, 9.5)):               # tablas cambiadas
        mk.paint(body, "wood_mid", box=((s * WX, 7.25, z), (0.004, 8.7, BOARD * 0.8)))

    # ---------------- bastidor de madera oscura ----------------
    for s in (-1, 1):
        B(mk, body, s * 3.72, s * 4.1, 2.6, WALL_Y0 + 0.06, -HZ + 0.42, HZ - 0.42, "wood_dark", detail=True)        # larguero
        B(mk, body, s * 0.5, s * 1.0, 2.6, FLOOR_Y - 0.29, -HZ + 0.42, HZ - 0.42, "wood_dark", detail=True)        # del medio
        B(mk, body, s * 3.95, s * 4.15, EAVE_Y - 0.33, roof_top(4.15) - 0.03, -HZ - 0.06, HZ + 0.06, "wood_dark", detail=True)  # solera
        for d in (-1, 1):
            B(mk, body, s * 3.95, s * 4.13, 2.58, WALL_Y1 - 0.02, d * (HZ - 0.15), d * (HZ + 0.1), "wood_dark", detail=True)    # esquineros
    for d in (-1, 1):
        B(mk, body, -4.1, 4.1, 2.2, FLOOR_Y - 0.02, d * (HZ - 0.42), d * SILL_Z, "wood_dark", detail=True)         # viga de punta
        # cruz en X de la punta (una barra más afuera que la otra: sin caras coplanares)
        for k, (xa, xb) in enumerate(((-3.6, 3.6), (3.6, -3.6))):
            zz = d * (HZ + 0.05 + 0.035 * k)
            bar(mk, body, (xa, 3.3, zz), (xb, 10.95, zz), 0.32, 0.12 + 0.04 * k, "wood_dark", up=(0, 0, 1), detail=True)
        B(mk, body, -3.9, 3.9, 10.9, 11.25, d * (HZ - 0.02), d * (HZ + 0.12), "wood_dark", detail=True)              # cabezal
    for zc in TRUCK_Z:
        B(mk, body, -3.7, 3.7, T.BOLSTER_TOP - 0.02, 2.62, zc - 0.45, zc + 0.45, "wood_dark", detail=True)          # traviesas
    # tensores con pendolones bajo el piso
    for s in (-1, 1):
        x = s * 2.0
        pts = [(x, 2.66, -10.0), (x, 1.3, -3.2), (x, 1.3, 3.2), (x, 2.66, 10.0)]
        for a, b in zip(pts, pts[1:]):
            bar(mk, body, a, b, 0.1, 0.1, "iron", ext=0.06, detail=True)
        for z in (-3.2, 3.2):
            B(mk, body, x - 0.1, x + 0.1, 1.24, 2.62, z - 0.12, z + 0.12, "iron", detail=True)

    # ---------------- riel y guía de las puertas ----------------
    for s in (-1, 1):
        B(mk, body, s * 4.12, s * 4.26, 11.42, 11.58, -DOOR_Z - 0.25, 9.2, "iron", detail=True)
        B(mk, body, s * 3.98, s * 4.2, 3.18, 3.36, -DOOR_Z - 0.25, 9.2, "iron", detail=True)
        for z in (-DOOR_Z - 0.15, 9.1):
            B(mk, body, s * 3.99, s * 4.27, 11.38, 11.62, z - 0.06, z + 0.06, "iron", detail=True)                 # topes

    # ---------------- techo, pasarela, escaleras, freno ----------------
    roof(mk, body)
    catwalk(mk, body, -HZ - 0.15, HZ + 0.15, (-14.6, -10.0, -5.0, 0.0, 5.0, 10.0, 14.6))
    end_ladder(mk, body, 2.5, 3.4, -HZ, -1)
    end_ladder(mk, body, -3.4, -2.5, HZ, 1)
    zb = HZ + 0.35
    pipe(mk, body, (0, 3.6, zb), (0, 13.05, zb), 0.07, "iron", sides=6, detail=True)
    for y in (4.0, 8.0, 10.8):
        B(mk, body, -0.05, 0.05, y - 0.05, y + 0.05, HZ - 0.03, zb + 0.02, "iron", detail=True)
    annulus(mk, body, (0, 13.05, zb), 0.45, 0.6, 0.09, "iron", axis="y", sides=8, detail=True)
    for a in (0, 90):
        r = math.radians(a)
        bar(mk, body, (-0.5 * math.cos(r), 13.05, zb - 0.5 * math.sin(r)), (0.5 * math.cos(r), 13.05, zb + 0.5 * math.sin(r)),
            0.07, 0.07, "iron", detail=True)

    # ---------------- puertas corredizas ----------------
    for s, name in ((-1, "SlidingDoorL"), (1, "SlidingDoorR")):
        x0, x1 = s * 4.02, s * 4.16
        d = mk.part(name, (s * 4.09, DOOR_Y1, 0))
        B(mk, d, x0, x1, DOOR_Y0, DOOR_Y1, -DOOR_Z, DOOR_Z, "paint_red")
        xo = s * 4.2
        for z0, z1 in ((-DOOR_Z, -DOOR_Z + 0.28), (DOOR_Z - 0.28, DOOR_Z)):
            B(mk, d, s * 4.15, xo, DOOR_Y0 + 0.01, DOOR_Y1 - 0.01, z0 + 0.01, z1 - 0.01, "wood_dark", detail=True)  # largueros
        for y0, y1 in ((DOOR_Y0 + 0.01, DOOR_Y0 + 0.3), (7.25, 7.55), (DOOR_Y1 - 0.3, DOOR_Y1 - 0.01)):
            B(mk, d, s * 4.152, s * 4.195, y0, y1, -DOOR_Z + 0.27, DOOR_Z - 0.27, "wood_dark", detail=True)         # travesaños
        bar(mk, d, (s * 4.172, DOOR_Y0 + 0.3, -DOOR_Z + 0.35), (s * 4.172, 7.25, DOOR_Z - 0.35), 0.28, 0.035, "wood_dark",
            up=(s, 0, 0), detail=True)                                                                              # riostra
        for z in (-2.2, 2.2):
            B(mk, d, s * 4.06, s * 4.2, DOOR_Y1 - 0.1, 11.5, z - 0.12, z + 0.12, "iron", detail=True)              # colgadores
        bar(mk, d, (s * 4.25, 6.6, -DOOR_Z + 0.5), (s * 4.25, 8.0, -DOOR_Z + 0.5), 0.08, 0.08, "iron", detail=True)   # manija
        for y in (6.75, 7.85):
            B(mk, d, s * 4.18, s * 4.27, y - 0.04, y + 0.04, -DOOR_Z + 0.47, -DOOR_Z + 0.53, "iron", detail=True)
        seams(mk, d, "z", [-DOOR_Z + k * 1.0 for k in range(1, 6)], {"x": x1}, {"y": (7.4, 8.0)})
        mk.paint(d, "wood_mid", box=((x0, 7.4, 0), (0.004, 8.1, 2 * DOOR_Z)))                         # cara de adentro

    w = mk.part("Wheels", (0, 0, 0))
    for zc in TRUCK_Z:
        T.truck(mk, w, zc)
    T.coupler(mk, "CouplerFront", -SILL_Z, -1, link=True)
    T.coupler(mk, "CouplerBack", SILL_Z, 1)
    mk.marker("_Roof", (0, WALK_Y, 0))
    mk.marker("_Gap_Front", (0, WALK_Y, -HZ - 0.15))
    mk.marker("_Gap_Back", (0, WALK_Y, HZ + 0.15))

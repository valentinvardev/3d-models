"""
Receta de WST_Prop_AmmoCrateRailway, el cajón de munición fijo de la compañía del ferrocarril
(prompt 042, Bloques A + B).

Brief
- Silueta a 40 studs: un baúl largo y bajo turquesa desteñido (4 x 2,2 x 2,2) con esquineros de hierro en
  las ocho puntas, un escudo de bronce al frente, asas de soga a los costados y la tapa con su pasador.
  Abierto, se ven tres filas de cajas de cartuchos crema.
- Piezas: Body (cajón con el interior tallado, juntas pintadas, esquineros de abajo que hacen de patas,
  escudo, asas; las cajas de cartuchos como detalle para que la booleana no las corte) y Lid (tapa de
  0,43 con sus esquineros y el pasador), con el origen en la bisagra: arista de atrás de arriba
  (y = 1,75, z = +1,1), eje sobre X; abre 100° (eso lo hace la animación).
- Medidas: cajón 0,02-1,75 (paredes y piso de 0,12), tapa 1,75-2,18; los esquineros sobresalen 0,03 y
  llegan al piso (y = 0) y arriba a 2,2. Origen abajo al centro.
- Inferido: el nombre Body, la altura de la tapa (0,43), esquineros en cubo de 0,28, dos juntas de tablas
  pintadas wood_dark, el pasador de hierro al frente, asas de soga en V colgadas de un taco de hierro,
  3 filas x 3 cajas de cartuchos sobre un falso fondo wood_dark en y = 0,8 (si no, quedan 1,1 abajo del
  borde y con la tapa abierta no se ven), juntas en la tapa, el cajón 0,02 arriba del piso (apoya en los esquineros: si no, la base
  del esquinero coincide con la del cajón).

Vueltas: 1) las cajas de cartuchos quedaban 1,1 abajo del borde (con la tapa abierta no se veían) y la
tapa era una superficie lisa de 4 x 2,2 · 2) falso fondo en y = 0,8 y dos juntas pintadas en la tapa.

Revisión
- 486 triángulos contra 350 de referencia: el interior tallado con su falso fondo y las 9 cajas (~120,
  se ven al abrir: es para lo que sirve el cajón), los 8 esquineros (96) y las asas con su taco (64).
- Ancho 4,22 con las asas (el cajón, 4,0) y profundidad 2,275 con el escudo y el pasador.
- En las capturas (cámara baja) no se ve el interior; las cajas están a 0,45 del borde, a la vista de un
  jugador parado al lado con la tapa abierta.
- Asas de soga en V (3 puntos): low poly; una U redonda suma ~16 por asa.
"""

import math

HX, HZ = 2.0, 1.1
Y0, YL, YT = 0.02, 1.75, 2.18      # base del cajón, borde de la tapa, arriba de la tapa
WALL = 0.12
CAP, CO = 0.28, 0.03               # esquinero: lado y cuánto sobresale


def cap(mk, part, sx, sz, y0, y1, mat="iron"):
    """Esquinero en cubo sobre la arista vertical (sx, sz): sobresale CO en x y en z."""
    x0, x1 = sorted((sx * (HX - CAP + CO), sx * (HX + CO)))
    z0, z1 = sorted((sz * (HZ - CAP + CO), sz * (HZ + CO)))
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat)


def strip(center, t):
    """Perfil 2D de una tira de espesor t a lo largo de una línea central (la soga)."""
    n = len(center)
    left, right = [], []
    for i in range(n):
        a, b = center[max(i - 1, 0)], center[min(i + 1, n - 1)]
        du, dv = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(du, dv)
        nu, nv = -dv / ln, du / ln
        left.append((center[i][0] + nu * t / 2, center[i][1] + nv * t / 2))
        right.append((center[i][0] - nu * t / 2, center[i][1] - nv * t / 2))
    return left + right[::-1]


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    mk.box(body, (0, (Y0 + YL) / 2, 0), (2 * HX, YL - Y0, 2 * HZ), "paint_teal")
    mk.carve(body, "paint_teal", points=mk.pts_box((0, YL, 0), (2 * (HX - WALL), 2 * (YL - Y0 - WALL), 2 * (HZ - WALL))))
    for y in (0.62, 1.2):                                                                  # juntas de tablas
        for k in (-0.025, 0.025):
            mk.slice(body, (0, y + k, 0), (0, 1, 0))
        mk.paint(body, "wood_dark", box=((0, y, 0), (2 * HX + 0.1, 0.048, 2 * HZ + 0.1)))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cap(mk, body, sx, sz, 0.0, 0.3)                                                 # esquineros-patas
    shield = [(-0.3, 1.36), (0.3, 1.36), (0.3, 0.98), (0.2, 0.78), (0.0, 0.66), (-0.2, 0.78), (-0.3, 0.98)]
    mk.prism(body, shield, 0.05, "brass", plane="xy", center=(0, 0, -HZ - 0.02), detail=True)  # escudo
    for s in (-1, 1):                                                                     # asas de soga
        mk.box(body, (s * (HX + 0.04), 1.34, 0), (0.1, 0.12, 0.78), "iron", detail=True)        # taco
        rope = strip([(-0.3, 1.32), (0.0, 0.98), (0.3, 1.32)], 0.08)
        mk.prism(body, rope, 0.08, "rope", plane="zy", center=(s * (HX + 0.07), 0, 0), detail=True)
    yf = 0.8                                                                              # falso fondo: las cajas
    mk.box(body, (0, yf - 0.02, 0), (2 * (HX - WALL) + 0.01, 0.04, 2 * (HZ - WALL) + 0.01), "wood_dark",
           detail=True)                                                                   # quedan a 0,45 del borde
    for i in range(3):                                                                    # cajas de cartuchos
        for j in range(3):
            mk.box(body, (-1.24 + 1.24 * i, yf + 0.25, -0.62 + 0.62 * j), (1.16, 0.5, 0.56), "paint_cream",
                   detail=True)

    lid = mk.part("Lid", (0, YL, HZ))
    mk.box(lid, (0, (YL + YT) / 2, 0), (2 * HX, YT - YL, 2 * HZ), "paint_teal")
    for sx in (-1, 1):
        for sz in (-1, 1):
            cap(mk, lid, sx, sz, YT + 0.02 - 0.3, YT + 0.02)                                # esquineros de arriba
    mk.box(lid, (0, YL - 0.06, -HZ - 0.02), (0.22, 0.32, 0.04), "iron")                    # pasador
    for z in (-0.37, 0.37):                                                               # juntas de la tapa
        for k in (-0.024, 0.024):
            mk.slice(lid, (0, 0, z + k), (0, 0, 1))
        mk.paint(lid, "wood_dark", box=((0, YT, z), (2 * HX - 2 * (CAP - CO), 0.01, 0.046)))

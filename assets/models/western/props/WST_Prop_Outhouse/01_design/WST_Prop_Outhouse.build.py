"""
Receta de WST_Prop_Outhouse, la letrina (prompt 140, Bloques A + B).

Brief
- Lo pidió la sesión del juego (2026-10-30): los dos Outhouse del mapa (3,5 x 8 x 3,5, decor, no se
  rompen) son cajas lisas. Va como prop (`Props/Outhouse.rbxm`), ajustado a esa caja. Era el extra
  `WST_X_Outhouse`.
- Silueta a 40 studs: casilla angosta de tablas verticales con techo de una sola agua y la luna en la
  puerta. La luna es lo que dice "letrina".
- Piezas: Body (origen abajo al centro) y Door (origen en el canto de las bisagras, abajo; bisagras a -X).
  Frente hacia -Z.
- Medidas: planta 3,5 x 3,5; la pared de adelante llega a 7,7 y la de atrás a 6,7; el techo (0,22, alero
  de 0,3) cae hacia +Z y su borde de adelante llega a 8. Postes de 0,25 en las esquinas. Hueco de la puerta
  2,2 x 6,05; puerta de 2,16 x 5,96 x 0,12 con la Z por fuera, luna calada arriba y tirador de hierro.
- Tablas: cada pared es una fila de tablas verticales de ~0,45, una sí y una no 0,04 más afuera (el
  relieve que pide el prompt). Dos tablas cambiadas en wood_light. Adentro, un bloque coal: por la luna se
  ve oscuro.
- Inferido: las alturas de las paredes (para que el techo llegue justo a 8), el ancho de las tablas del
  dintel, la Z con dos travesaños y una diagonal, la luna como medialuna abierta hacia +X.

Revisión (3 vueltas)
- 1) z-fighting en Body: 2 pares. Medido con la misma prueba que el QA: no eran las tablas sino el piso.
  Al unir caras coplanares, la base del bloque oscuro de adentro y las de las tablas quedan en un
  triángulo grande que pisa la base de dos postes. 2) Dintel con la primera tabla salida y 0,002 más bajo:
  no alcanzaba. 3) El bloque de adentro despegado 0,02 del piso: 0 pares.
- 568 triángulos (tope 600). Medidas: 4,1 x 8,0 x 4,1 con el alero; la caja del mapa es 3,5 x 8 x 3,5 y el
  prop se ajusta.
- Avisos esperables: Door queda adentro de la caja de Body (es la puerta), y el tirador es un detalle suelto
  que en la captura se ve pegado a la puerta.
"""

import math

HALF = 1.75          # media planta
T = 0.2              # espesor de pared
POST = 0.25
H_FRONT, H_BACK = 7.7, 6.7
ROOF_T, EAVE = 0.22, 0.3
DOOR_W, DOOR_H = 2.2, 6.05
REPLACED = {("back", 2), ("left", 4)}   # tablas cambiadas (wood_light)


def top_at(z):
    """Alto de la pared en z (el techo cae de adelante a atrás)."""
    return H_FRONT - (z + HALF) / (2 * HALF) * (H_FRONT - H_BACK)


def boards(mk, side, x0, x1, y0, y1, z_out, along="x", phase=0):
    """Una fila de tablas verticales de x0 a x1 (o z, en los costados), del piso a y1 (o a la pendiente).
    `phase` 1 empieza con una tabla salida: así no queda coplanar con la tabla vecina de otra fila."""
    n = max(1, round((x1 - x0) / 0.45))
    w = (x1 - x0) / n
    for i in range(n):
        a, b = x0 + i * w - 0.005, x0 + (i + 1) * w + 0.005
        out = 0.04 if (i + phase) % 2 else 0.0             # una sí y una no, más afuera
        mat = "wood_light" if (side, i) in REPLACED else "wood_mid"
        d = T + out
        if along == "x":
            sgn = 1 if z_out > 0 else -1                   # hacia dónde está afuera
            zc = z_out - sgn * (T / 2) + sgn * out / 2
            mk.box("Body", ((a + b) / 2, (y0 + y1) / 2, zc), (b - a, y1 - y0, d), mat)
        else:
            sgn = 1 if z_out > 0 else -1                   # acá z_out es la x de afuera
            xc = z_out - sgn * (T / 2) + sgn * out / 2
            prof = [(a, 0), (b, 0), (b, top_at(b)), (a, top_at(a))]
            mk.prism("Body", prof, d, mat, plane="zy", center=(xc, 0, 0))


def moon(r=0.3, inner=0.24, shift=0.13, n=10):
    """Medialuna abierta hacia +X (perfil xy): arco de afuera y vuelta por el de adentro, corrido."""
    pts = []
    for i in range(n + 1):
        a = math.radians(55 + i * 250 / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(305 - i * 250 / n)
        pts.append((shift + inner * math.cos(a), inner * math.sin(a)))
    return pts


def build(mk):
    mk.part("Body", (0, 0, 0))
    inner = HALF - POST
    # postes en las esquinas, hasta el techo
    for sx in (-1, 1):
        for sz in (-1, 1):
            z = sz * (HALF - POST / 2)
            mk.box("Body", (sx * (HALF - POST / 2), top_at(z) / 2, z), (POST, top_at(z), POST), "wood_dark")
    # atrás y costados: tablas entre los postes
    boards(mk, "back", -inner, inner, 0, H_BACK + 0.02, HALF, along="x")
    boards(mk, "left", -inner, inner, 0, None, -HALF, along="z")
    boards(mk, "right", -inner, inner, 0, None, HALF, along="z")
    # adelante: una tabla a cada lado del hueco y el dintel arriba
    boards(mk, "frontL", -inner, -DOOR_W / 2, 0, H_FRONT, -HALF, along="x")
    boards(mk, "frontR", DOOR_W / 2, inner, 0, H_FRONT, -HALF, along="x")
    boards(mk, "lintel", -DOOR_W / 2, DOOR_W / 2, DOOR_H, H_FRONT - 0.002, -HALF, along="x", phase=1)
    # adentro, oscuro (lo que se ve por la luna)
    # (despegado 0,02 del piso: si no, al unir caras coplanares su base pisa la de los postes)
    mk.box("Body", (0, (H_BACK - 0.1) / 2 + 0.02, 0), (2 * (HALF - T) - 0.02, H_BACK - 0.1, 2 * (HALF - T) - 0.02),
           "coal")
    # techo de una sola agua, con alero
    z0, z1 = -HALF - EAVE, HALF + EAVE
    roof = [(z0, top_at(z0)), (z1, top_at(z1)), (z1, top_at(z1) + ROOF_T), (z0, top_at(z0) + ROOF_T)]
    mk.prism("Body", roof, 2 * (HALF + EAVE), "wood_dark", plane="zy", center=(0, 0, 0))

    # puerta: origen en el canto de las bisagras (-X), abajo, en el plano de afuera de la pared
    hinge = (-DOOR_W / 2, 0, -HALF + 0.05)
    mk.part("Door", hinge)
    w, h, d = DOOR_W - 0.04, DOOR_H - 0.09, 0.12
    cx, cy, cz = hinge[0] + w / 2 + 0.02, h / 2 + 0.04, hinge[2] + 0.02
    mk.box("Door", (cx, cy, cz), (w, h, d), "wood_mid")
    out = cz - d / 2 - 0.03
    for y in (0.8, 5.35):
        mk.box("Door", (cx, y, out), (w - 0.2, 0.3, 0.06), "wood_dark")
    dx, dy = w - 0.5, 5.35 - 0.8
    # la diagonal sube del lado de las bisagras (-X, abajo) al del tirador (+X, arriba)
    mk.box("Door", (cx, (0.8 + 5.35) / 2, out), (math.hypot(dx, dy), 0.26, 0.06), "wood_dark",
           rot=(0, 0, math.degrees(math.atan2(dy, dx))))
    mk.box("Door", (cx + w / 2 - 0.25, 3.0, out - 0.04), (0.08, 0.35, 0.08), "iron", detail=True)
    mk.carve("Door", "coal", prism=dict(profile=moon(), depth=0.6, plane="xy", center=(cx - 0.06, 4.55, cz)))

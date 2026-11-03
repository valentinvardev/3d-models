"""
Receta de WST_Prop_DynamiteCrate, la caja de dinamita destructible (prompt 128, Bloques A + C).

Brief
- Silueta a 40 studs: cajón chato claro (wood_light) con la tapa levantada adelante (cuña oscura entre
  tapa y frente), franja warning_red y placa crema al frente, sogas en las puntas.
- Medidas: 2,4 (X) x 1,4 (alto, con la tapa cerrada) x 1,6 (Z). Cuerpo 1,0 de alto, tapa 0,4 (tabla
  0,22 + dos travesaños 0,18 arriba). Paredes de 0,4 (lo pide el Bloque C: fragmentos >= 0,4; la caja de
  referencia usa los mismos 0,40).
- Esquinas a cola de milano "sugerida": uniones de dedos en tres franjas (0-0,34, 0,34-0,67, 0,67-1,0);
  las puntas tienen los dedos de abajo y de arriba, el frente y el fondo el del medio. Cada pared es un
  prisma con el perfil dentado y las testas de los dedos van en wood_mid: se ve el encastre alternado.
- Fragmentos (4, origen común en la base): frag01 frente (con franja y placa), frag02 fondo (pared de
  atrás), frag03 las dos puntas + piso + relleno + los 6 cartuchos + sogas (la U con la carga adentro
  queda casi maciza: aproximadamente convexa), frag04 tapa.
- Tapa entreabierta: girada 9° sobre el canto de atrás, el frente queda 0,25 arriba; los 6 cartuchos
  (dynamite_red, a lo largo de Z) asoman 0,05 sobre el borde y se ven por la abertura.
- Inferido: medidas en orden X x alto x Z (como el resto de los prompts); tapa levantada adelante (el
  prompt no dice hacia dónde); relleno oscuro (wood_dark) entre los cartuchos; franja en la franja del
  medio, a todo el ancho; placa encima de la franja; sogas de 3 tramos.

Vueltas: 1) frag03 con el 47,9 % del volumen (tope 45 %) por el relleno macizo; los cartuchos de 6 lados
con un vértice arriba se leían como dientes · 2) falso piso de 0,40 bajo los cartuchos (frag03 40,9 %)
y hexágonos girados 30° (cara plana arriba).

Revisión
- 460 triángulos contra 250 de referencia: los 6 cartuchos (~120), las dos sogas (~72) y las uniones de
  dedos en prismas dentados (~44 por pared). Es lo que la distingue de la caja común a 20 studs.
- Alto 1,65 con la tapa levantada (1,4 cerrada, como pide el prompt); ancho 2,77 con las sogas.
- Volúmenes: frente 17,8 %, fondo 17,4 %, U con la carga 40,9 %, tapa 23,8 %. Mínimos 0,40-1,03.
- Sin grietas en zigzag (el Bloque C las sugiere en superficies grandes): las caras de esta caja son
  chicas y ya están cortadas por los dedos.
"""

import math

L, H_BODY, D = 2.4, 1.0, 1.6
T = 0.4                                  # grosor de las paredes
LID_T, CLEAT_T = 0.22, 0.18
BANDS = (0.0, 0.34, 0.67, 1.0)
LID_ANGLE = 9.0
STICK_R, STICK_L = 0.12, 0.74
STICKS_X = (-0.65, -0.39, -0.13, 0.13, 0.39, 0.65)
STICK_Y = 0.93


def rot_x(p, pivot, deg):
    """Gira p alrededor de un eje paralelo a X que pasa por pivot (positivo: el frente -Z sube)."""
    a = math.radians(deg)
    y, z = p[1] - pivot[1], p[2] - pivot[2]
    return (p[0], pivot[1] + y * math.cos(a) - z * math.sin(a), pivot[2] + y * math.sin(a) + z * math.cos(a))


def tube(mk, part, a, b, r, mat, sides=4):
    ax = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in ax))
    d = [c / n for c in ax]
    ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    un = math.sqrt(sum(c * c for c in u))
    u = [c / un for c in u]
    v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    pts = [tuple(p[i] + r * (math.cos(t) * u[i] + math.sin(t) * v[i]) for i in range(3))
           for p in (a, b) for t in (2 * math.pi * (k + 0.5) / sides for k in range(sides))]
    mk.hull(part, pts, mat, detail=True)


def chain(mk, part, pts, r, mat):
    for a, b in zip(pts, pts[1:]):
        d = [b[i] - a[i] for i in range(3)]
        n = math.sqrt(sum(c * c for c in d))
        e = [c / n * r * 0.8 for c in d]
        tube(mk, part, tuple(a[i] - e[i] for i in range(3)), tuple(b[i] + e[i] for i in range(3)), r, mat)


def long_wall_profile():
    """Frente y fondo vistos de frente (x, y): el dedo del medio llega a la esquina."""
    xi, xo = L / 2 - T, L / 2
    b0, b1, b2, b3 = BANDS
    return [(-xi, b0), (xi, b0), (xi, b1), (xo, b1), (xo, b2), (xi, b2), (xi, b3),
            (-xi, b3), (-xi, b2), (-xo, b2), (-xo, b1), (-xi, b1)]


def end_wall_profile():
    """Puntas vistas de costado (z, y): los dedos de abajo y de arriba llegan a las esquinas."""
    zi, zo = D / 2 - T, D / 2
    b0, b1, b2, b3 = BANDS
    return [(-zo, b0), (zo, b0), (zo, b1), (zi, b1), (zi, b2), (zo, b2), (zo, b3),
            (-zo, b3), (-zo, b2), (-zi, b2), (-zi, b1), (-zo, b1)]


def build(mk):
    zf = -D / 2
    # ---------------- frag01: frente, con franja y placa ----------------
    front = mk.part("frag01", (0, 0, 0))
    mk.prism(front, long_wall_profile(), T, "wood_light", plane="xy", center=(0, 0, zf + T / 2))
    for y in (0.40, 0.60):
        mk.slice(front, (0, y, zf), (0, 1, 0))
    mk.paint(front, "warning_red", box=((0, 0.50, zf), (L + 0.1, 0.20, 0.02)))
    for s in (-1, 1):                                                   # testas de los dedos, a los costados
        mk.paint(front, "wood_mid", box=((s * L / 2, 0.5, zf + T / 2), (0.02, 1.2, T + 0.02)))
    mk.box(front, (0, 0.50, zf - 0.015), (1.0, 0.42, 0.05), "paint_cream", detail=True)   # placa (0,04 afuera)

    # ---------------- frag02: pared de atrás ----------------
    back = mk.part("frag02", (0, 0, 0))
    mk.prism(back, long_wall_profile(), T, "wood_light", plane="xy", center=(0, 0, -zf - T / 2))
    for s in (-1, 1):
        mk.paint(back, "wood_mid", box=((s * L / 2, 0.5, -zf - T / 2), (0.02, 1.2, T + 0.02)))

    # ---------------- frag03: puntas + piso con la carga + sogas ----------------
    u = mk.part("frag03", (0, 0, 0))
    for s in (-1, 1):
        mk.prism(u, end_wall_profile(), T, "wood_light", plane="zy", center=(s * (L / 2 - T / 2), 0, 0))
    # falso piso con el relleno (0,40, entre las puntas): macizo hasta abajo, frag03 era el 47,9 % del volumen
    mk.box(u, (0, STICK_Y - 0.08 - 0.2, 0), (L - 2 * T, 0.4, D - 2 * T), "wood_dark")
    for s in (-1, 1):                                                   # testas de los dedos, adelante y atrás
        for zs in (-1, 1):
            mk.paint(u, "wood_mid", box=((s * (L / 2 - T / 2), 0.5, zs * D / 2), (T + 0.02, 1.2, 0.02)))
    for x in STICKS_X:                                                  # los 6 cartuchos, a lo largo de Z
        mk.cyl(u, (x, STICK_Y, 0), STICK_R, STICK_L, "dynamite_red", axis="z", sides=6, rot=(0, 0, 30),
               detail=True)                                             # cara plana arriba (con vértice se veían dientes)
    for s in (-1, 1):                                                   # sogas en las puntas
        xw, xo = s * L / 2, s * (L / 2 + 0.12)
        chain(mk, u, [(xw - s * 0.05, 0.84, -0.32), (xo, 0.70, -0.24), (xo, 0.70, 0.24), (xw - s * 0.05, 0.84, 0.32)],
              0.05, "rope")

    # ---------------- frag04: tapa entreabierta (levantada adelante, apoyada en el canto de atrás) ----------------
    lid = mk.part("frag04", (0, 0, 0))
    pivot = (0, H_BODY, D / 2)

    def lid_box(center, size, mat):
        pts = [rot_x(p, pivot, LID_ANGLE) for p in mk.pts_box(center, size)]
        mk.hull(lid, pts, mat)

    lid_box((0, H_BODY + LID_T / 2, 0), (L, LID_T, D), "wood_light")
    for x in (-0.82, 0.82):                                             # travesaños de arriba
        lid_box((x, H_BODY + LID_T + CLEAT_T / 2 - 0.01, 0), (0.28, CLEAT_T + 0.02, D), "wood_mid")
    p = rot_x((0, H_BODY + LID_T, 0), pivot, LID_ANGLE)                 # junta de las dos tablas de la tapa
    n = rot_x((0, 0, 1), (0, 0, 0), LID_ANGLE)
    for dz in (-0.03, 0.03):
        q = rot_x((0, H_BODY + LID_T, dz), pivot, LID_ANGLE)
        mk.slice(lid, q, n)
    mk.paint(lid, "wood_dark", box=(p, (L + 0.1, 0.05, 0.05)))      # girar sobre X deja la junta paralela a X

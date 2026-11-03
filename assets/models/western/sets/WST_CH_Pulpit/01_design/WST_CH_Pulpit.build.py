"""
Receta de WST_CH_Pulpit, el púlpito de la iglesia (prompt 124, Bloques A + C + G). Puesto del Predicador en
la fase 1.

Brief
- Silueta: copa alta de madera oscura: pedestal angosto que se abre en ménsula, cajón hexagonal con paneles
  crema, una escalera curva que lo abraza por la izquierda, y arriba un tornavoz hexagonal sobre un poste.
  Atril con un libro grande abierto al frente. Vetas de plata que suben del piso por el pedestal.
- Medidas: cajón de 3 entre caras (apotema 1,5) con el piso a 4 y la baranda a 7,2 (3,2: le llega al pecho
  al Predicador de 6,5); pedestal: plinto de radio 1,4 (0-0,35), fuste de radio 0,75 (hasta 2,9), ménsula
  que se abre hasta el piso. Escalera de 5 escalones de 0,8 (huellas a 0,8 ... 4,0) en arco de radio 1,85 a
  2,95 alrededor del pedestal, de 258° (adelante a la izquierda) a 150° (la entrada, atrás a la izquierda).
  Tornavoz de radio 2,1 a 12 (le pasa la cabeza al Predicador: 4 + 6,5), sobre un poste en la cara de atrás.
- Hexágono con vértices a 0°, 60°... (caras a 30°, 90°... ): la cara de 270° es el frente (-Z) con el
  atril; la de 150°, abierta, es la entrada; la de 90° (atrás) lleva el poste.
- Piezas: frag01 pedestal y piso, frag02 cajón (prisma en C, paneles tallados, moldura, atril y libro),
  frag03 escalera y pasamanos, frag04 poste y tornavoz; Silver_Veins.
- Inferido: orientación del hexágono, lado de la escalera, alto de la baranda, tornavoz a 12, huellas
  wood_mid, libro de tapas leather_dark y hojas crema, vetas en tres caras del pedestal.

Vueltas: 1) aristas de 3-4 caras: los tramos del pasamanos y de las vetas compartían las esquinas de las
uniones (se sueldan); z-fighting entre el piso (mismo radio que el cajón) y el cajón · 2) tramos de grosor
alternado y que se pasan, piso 0,08 adentro, una veta menos; la escalera daba ~47 % del volumen: 1,1 de ancho.

Revisión
- 738 triángulos contra 500 (+48 %, calidad primero): cajón ~240 (prisma en C, 5 paneles crema tallados,
  moldura, atril y libro), escalera ~220 (5 escalones macizos curvos, postes, pasamanos en 4 tramos y
  balaustres), vetas ~130 (dos, del piso al fuste), pedestal 72, tornavoz 62.
- Medidas: 5,15 x 13,2 x 4,98. Piso del púlpito a 4,0, baranda a 7,2 (moldura a 7,42), tornavoz a 11,85-12,45.
- Fragmentos: pedestal ~26 %, cajón ~15 %, escalera ~40 %, tornavoz ~16 % (por volumen, aproximado).
- Dudoso: con colisión de casco el cajón es un prisma macizo hasta 7,2 (el Predicador quedaría parado arriba):
  conviene colisión precisa en frag02 o que el jefe no dependa de la física ahí.
"""

import math

DARK, CREAM, MID, LEATHER, NEON = "wood_dark", "paint_cream", "wood_mid", "leather_dark", "silver_neon"
RO = 1.5 / math.cos(math.radians(30))          # radio a los vértices (apotema 1,5: 3 entre caras)
WALL = 0.2
FLOOR_Y, RAIL_Y = 4.0, 7.2


def hexpt(r, deg, y):
    t = math.radians(deg)
    return (r * math.cos(t), y, r * math.sin(t))


def hex_ring(r, y, start=0.0):
    return [hexpt(r, start + 60 * k, y) for k in range(6)]


def face_frame(face_deg, apo, y):
    """Centro de una cara del hexágono (apotema apo) y sus direcciones (normal, tangente)."""
    t = math.radians(face_deg)
    n = (math.cos(t), 0.0, math.sin(t))
    tg = (-math.sin(t), 0.0, math.cos(t))
    return (apo * n[0], y, apo * n[2]), n, tg


def build(mk):
    # ---- frag01: pedestal (plinto, fuste, ménsula con el piso del púlpito) ----
    part = mk.part("frag01", (0, 0, 0))
    mk.hull(part, hex_ring(1.4, 0.0) + hex_ring(1.3, 0.35), DARK)                         # plinto (con chanfle)
    mk.hull(part, hex_ring(0.75, 0.3) + hex_ring(0.75, 2.95), DARK)                        # fuste
    # el piso queda 0,08 adentro de la cara del cajón: con el mismo radio sus costados eran coplanares (medido)
    mk.hull(part, hex_ring(0.74, 2.9) + hex_ring(RO - 0.08, 3.85) + hex_ring(RO - 0.08, FLOOR_Y), DARK)
    mk.paint(part, MID, box=((0, FLOOR_Y, 0), (4, 0.02, 4)))                                # piso del púlpito
    # ---- frag02: cajón en C (abierto en la cara de 150°), paneles crema tallados, moldura, atril, libro ----
    part = mk.part("frag02", (0, 0, 0))
    ri = RO - WALL / math.cos(math.radians(30))
    outer = [(RO * math.cos(math.radians(a)), RO * math.sin(math.radians(a))) for a in (180, 240, 300, 0, 60, 120)]
    inner = [(ri * math.cos(math.radians(a)), ri * math.sin(math.radians(a))) for a in (120, 60, 0, 300, 240, 180)]
    mk.prism(part, outer + inner, RAIL_Y - 3.85, DARK, plane="xz", center=(0, (RAIL_Y + 3.85) / 2, 0))
    for fd in (210, 270, 330, 30, 90):                                                    # paneles crema (rebaje 0,05)
        c, n, tg = face_frame(fd, 1.5, 5.6)
        pts = []
        for u in (-0.5, 0.5):
            for y in (4.45, 6.75):
                for h in (-0.05, 0.3):
                    pts.append((c[0] + tg[0] * u + n[0] * h, y, c[2] + tg[2] * u + n[2] * h))
        mk.carve(part, CREAM, points=pts)
    ro2, ri2 = RO + 0.1, ri - 0.1                                                         # moldura de arriba
    outer2 = [(ro2 * math.cos(math.radians(a)), ro2 * math.sin(math.radians(a))) for a in (180, 240, 300, 0, 60, 120)]
    inner2 = [(ri2 * math.cos(math.radians(a)), ri2 * math.sin(math.radians(a))) for a in (120, 60, 0, 300, 240, 180)]
    mk.prism(part, outer2 + inner2, 0.24, DARK, plane="xz", center=(0, RAIL_Y + 0.1, 0), detail=True)
    # atril sobre el frente: cuña inclinada hacia el predicador (alta afuera, baja adentro)
    zf, zb = -1.62, -0.78
    mk.hull(part, [(x, y, z) for x in (-0.85, 0.85) for y, z in ((RAIL_Y + 0.15, zf), (RAIL_Y + 0.62, zf),
                                                                  (RAIL_Y + 0.15, zb), (RAIL_Y + 0.3, zb))], DARK,
            detail=True)
    # libro abierto sobre el atril (tapas y dos bloques de hojas arqueadas)
    slope = (0.32) / (zb - zf)
    top = lambda z: RAIL_Y + 0.62 + (z - zf) * -slope
    mk.hull(part, [(x, top(z) + dy, z) for x in (-0.72, 0.72) for z in (zf + 0.04, zb - 0.06) for dy in (-0.01, 0.04)],
            LEATHER, detail=True)
    for s in (-1, 1):
        mk.hull(part, [(s * x, top(z) + y, z) for z in (zf + 0.08, zb - 0.1)
                       for x, y in ((0.03, 0.04), (0.66, 0.04), (0.66, 0.1), (0.3, 0.16), (0.1, 0.17), (0.03, 0.09))],
                CREAM, detail=True)
    # ---- frag03: escalera curva (5 escalones macizos) con pasamanos ----
    part = mk.part("frag03", (0, 0, 0))
    angs = [258.0, 231.0, 204.0, 177.0, 150.0]
    for k, a in enumerate(angs):
        y = 0.8 * (k + 1)
        r_in = 1.85 if k < 4 else 1.49
        pts = []
        # se enciman 0,2° con el vecino (si comparten la cara del corte se sueldan) y el pie de cada uno
        # sube 0,003 (los pies encimados no quedan coplanares)
        for aa in (a - 13.6, a + 13.6):
            for r in (r_in, 2.95):                                   # 1,1 de ancho: la escalera queda en ~40 % del volumen
                for yy in (0.003 * k, y):
                    pts.append(hexpt(r, aa, yy))
        mk.hull(part, pts, DARK)
        mk.paint(part, MID, box=(hexpt(2.4, a, y), (0.9, 0.02, 0.9)))                      # huella
    for k, a in enumerate(angs):                                                           # pasamanos: postes y baranda
        y = 0.8 * (k + 1)
        if k in (0, 4):
            p = hexpt(2.8, a, y)
            mk.box(part, (p[0], y + 1.4, p[2]), (0.22, 2.8, 0.22), DARK, detail=True)
    for k in range(4):
        a0, a1 = angs[k], angs[k + 1]
        y0, y1 = 0.8 * (k + 1) + 2.6, 0.8 * (k + 2) + 2.6
        p0, p1 = hexpt(2.8, a0, y0), hexpt(2.8, a1, y1)
        # tramos de grosor alternado: si comparten las esquinas de la unión, se sueldan (aristas de 4 caras)
        e = 0.08 if k % 2 == 0 else 0.07
        mk.hull(part, [(p[0] + dx, p[1] + dy, p[2] + dz) for p in (p0, p1) for dx in (-e, e)
                       for dy in (-e - 0.01, e + 0.01) for dz in (-e, e)], DARK, detail=True)
        pm = hexpt(2.8, (a0 + a1) / 2, 0.8 * (k + 1))                                      # balaustre del medio
        mk.box(part, (pm[0], 0.8 * (k + 1) + 1.55, pm[2]), (0.12, 3.0, 0.12), DARK, detail=True)
    # ---- frag04: poste en la cara de atrás y tornavoz hexagonal ----
    part = mk.part("frag04", (0, 0, 0))
    mk.box(part, (0, 8.0, 1.5 + 0.17), (0.36, 8.0, 0.36), DARK)                            # poste de 4 a 12
    mk.hull(part, hex_ring(2.1, 11.85) + hex_ring(2.1, 12.15), DARK)                       # tablero (alineado al cajón)
    mk.hull(part, hex_ring(2.25, 12.12) + hex_ring(1.9, 12.45), DARK)                      # cornisa
    mk.hull(part, hex_ring(0.5, 12.42) + [(0, 13.2, 0)], DARK)                             # remate
    mk.paint(part, CREAM, box=((0, 11.85, 0), (4.0, 0.02, 4.0)))                            # cielo crema
    # ---- vetas de plata que suben del piso por el pedestal ----
    part = mk.part("Silver_Veins", (0, 0, 0))
    # (y, corrimiento, afuera): piso -> pie del plinto -> arriba del plinto -> fuste
    for fd, path in ((210, [(0.0, -0.3, 1.0), (0.0, -0.2, 0.05), (0.3, -0.15, 0.0), (0.37, -0.1, 0.0), (1.4, 0.1, 0.0),
                            (2.4, -0.15, 0.0), (3.1, 0.08, 0.0)]),
                     (330, [(0.0, 0.25, 1.1), (0.0, 0.2, 0.05), (0.32, 0.1, 0.0), (0.37, 0.05, 0.0), (1.1, -0.12, 0.0),
                            (2.0, 0.12, 0.0)]),
                     ):
        vein(mk, part, fd, path)


def vein(mk, part, fd, path):
    """Veta sobre una cara del pedestal: (y, corrimiento lateral, distancia afuera por el piso). En el piso
    (y ~0) corre hacia afuera; en el plinto y el fuste sube pegada a la cara (0,03 afuera)."""
    c30 = math.cos(math.radians(30))
    apo = lambda y: ((1.4 - 0.1 * y / 0.35) * c30 if y < 0.355 else 0.75 * c30)          # plinto en talud / fuste
    t = math.radians(fd)
    n = (math.cos(t), 0.0, math.sin(t))
    tg = (-math.sin(t), 0.0, math.cos(t))
    pts3 = []
    for y, u, out in path:
        if out > 0:
            pts3.append(((apo(0.0) + out) * n[0] + tg[0] * u, 0.0, (apo(0.0) + out) * n[2] + tg[2] * u, "floor"))
        else:
            pts3.append((apo(y) * n[0] + tg[0] * u, y, apo(y) * n[2] + tg[2] * u, "face"))
    for j, (a, b) in enumerate(zip(pts3, pts3[1:])):
        w = 0.12 - 0.012 * j                                       # cada tramo más angosto: sin vértices compartidos
        b = (b[0] + (b[0] - a[0]) * 0.06, b[1] + (b[1] - a[1]) * 0.06, b[2] + (b[2] - a[2]) * 0.06, b[3])   # pasa 6 %
        pts = []
        for p in (a, b):
            if p[3] == "floor":
                for s in (-0.5, 0.5):
                    for h in (0.0, 0.04):
                        pts.append((p[0] + tg[0] * s * w, p[1] + h, p[2] + tg[2] * s * w))
            else:
                for s in (-0.5, 0.5):
                    for h in (-0.03, 0.035):
                        pts.append((p[0] + tg[0] * s * w + n[0] * h, p[1], p[2] + tg[2] * s * w + n[2] * h))
        mk.hull(part, pts, NEON)

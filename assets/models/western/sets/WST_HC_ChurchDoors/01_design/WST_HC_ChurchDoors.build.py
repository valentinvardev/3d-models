"""
Receta de WST_HC_ChurchDoors, el portón de la iglesia de Hollow Creek (prompt 121, Bloques A + B).

Brief
- Silueta a 40 studs (desde la plaza): arco de medio punto de dovelas de piedra con clave, jambas de
  sillares trabados, y dos hojas de tablones oscuros con pletinas de hierro y una cruz de hierro cada una;
  encima, dos cadenas en X que pasan por los tiradores y se juntan en un candado grande.
- Calza con WST_CH_Church (ya construida): su hueco es de 8 x 12 de medio punto (arco de 6 tramos, radio 4,
  arranque a 8) en la fachada de tabla (cara de afuera en z = -24,6 de la iglesia, 0,6 de espesor) con el
  zócalo de piedra (1,0, hasta y ~4,1) que sale 0,4. Este modelo va con su origen en (0, 0, -24,6) de la
  iglesia: origen en el piso al centro del umbral, z = 0 en la cara de afuera de las tablas.
- Surround_L / Surround_R / Surround_Arch (stone_grey): jambas de 4 sillares alternados (1,0 y 0,75 de
  ancho, frentes a -0,65 y -0,7), zócalo más ancho y una imposta a 8; arco de 7 dovelas con clave más
  alta. La luz queda en 7,6 x 11,8 (jambas en x = ±3,8, arco de radio 3,8): así la piedra tapa los cortes
  del hueco de la iglesia (radio 4 en polígono de 6 tramos, que por la cuerda baja a 3,86). Atrás llegan a
  z = 0,66 (pasan la cara de adentro de la pared, 0,6). Tres piezas para que el casco convexo no tape el
  paso. Las armellas de las cadenas van en las jambas (quedan al sacar las cadenas).
- DoorL / DoorR: hojas de 3,75 x hasta 11,7 x 0,5 (z 0,08..0,58), cinco tablones wood_mid con juntas
  wood_dark de 0,06 y uno cambiado (wood_dark), tres pletinas de hierro con punta, clavos, una cruz de hierro atornillada (sin talla),
  tirador de argolla y nudos de bisagra. Origen en el canto de afuera (x = ±3,78, z = 0,33): abren hacia
  adentro (+Z).
- Chains: dos cadenas en X (eslabones en rombo de 0,78 cada 0,7, alternados de plano) de las armellas de arriba de
  una jamba a las de abajo de la otra, pasando por los tiradores, y un candado de bronce grande en el cruce.
- Inferido: medidas de jambas, dovelas y clave, luz de 7,6 (para tapar los cortes de la iglesia), espesor
  de las hojas, herraje, colores, recorrido de las cadenas y armellas, candado de bronce, nombres de las
  piezas de piedra.

Vueltas: 1) primera versión: pasa la revisión pero las cadenas costaban 1024 triángulos (el tallado de la
bocallave unía por booleana todos los eslabones encimados) y las armellas eran dos medias argollas (~56 cada
una) · 2) eslabones como detalle (sin booleana) y en rombo de 12 triángulos, armellas en U de un prisma
(1024 -> 436, Surround 208 -> 168) · 3) tablones con juntas oscuras de 0,06 y uno cambiado por hoja (los
cinco alternados claro/oscuro se leían como cebra).

Revisión
- 1520 triángulos contra 800 (+90 %): cadenas 436 (28 eslabones y el candado), hojas 332 cada una
  (tablones con juntas, tres pletinas con clavos, cruz, argolla y bisagras), jambas 168 cada una, arco 84.
  Es la puerta del jefe final (el asedio termina cuando se abren): el herraje y las cadenas son el foco.
- Medidas: 10,48 x 13,22 x 1,55 (imposta a imposta; clave a 13,2). Luz libre 7,6 x 11,8 (prompt 8 x 12:
  -5 % de ancho para que la piedra tape los cortes del hueco de la iglesia).
- Calce con WST_CH_Church: origen en (0, 0, -24,6) de la iglesia. Las jambas (x ±3,8..±5,24) y el arco
  (radio 3,8 a 5,35) cubren el corte de la fachada (x ±4, radio 4 en 6 tramos) y el zócalo que sale 0,4;
  la piedra va de z -0,75 a 0,66 (pasa 0,06 la cara de adentro de la pared). Ninguna cara coincide con una
  de la iglesia (medido sobre su receta: tablas en z 0..0,6, zócalo -0,4..0,62 hasta y ~4,1, cortes en x ±4).
- Las hojas abren hacia adentro sobre el canto de afuera; Chains toca las armellas de las jambas y pasa
  frente a los tiradores: al sacarlo, las armellas quedan.
- Materiales: stone_grey, wood_mid, wood_dark, iron, brass.
"""

import math

from mathutils import Vector

STONE, WOOD, WOOD2, IRON, BRASS = "stone_grey", "wood_mid", "wood_dark", "iron", "brass"
XJ = 3.8                     # cara de adentro de las jambas
SPRING = 8.0
RI, RO = 3.8, 4.95           # intradós y trasdós del arco
ZF, ZB = -0.65, 0.66         # frente y fondo de la piedra
DZ0, DZ1 = 0.08, 0.58        # hojas
STAPLES = {(-1, "hi"): (-4.45, 7.3), (-1, "lo"): (-4.45, 3.2), (1, "hi"): (4.45, 7.3), (1, "lo"): (4.45, 3.2)}


def arc_pt(r, deg, cx=0.0, cy=SPRING):
    return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))


# --------------------------------------------------------------------------------------------- piedra
def jamb(mk, s):
    p = mk.part(f"Surround_{'L' if s < 0 else 'R'}", (s * XJ, 0, 0))
    courses = [(0.0, 0.7, 1.4, ZF - 0.08), (0.7, 2.55, 0.75, ZF), (2.55, 4.45, 1.05, ZF - 0.05), (4.45, 6.25, 0.75, ZF),
               (6.25, 7.75, 1.0, ZF - 0.05)]
    for k, (y0, y1, w, zf) in enumerate(courses):
        e = 0.004 * (k % 2)
        x0, x1 = s * (XJ + 0.003 * (k % 2)), s * (XJ + w)               # caras de adentro alternadas: sin z-fighting
        mk.box(p, ((x0 + x1) / 2, (y0 + y1) / 2 + 0.002, (zf + ZB + e) / 2), (abs(x1 - x0), y1 - y0 + 0.004 + e, ZB + e - zf),
               STONE)
    mk.box(p, (s * (XJ + 0.04 + 0.7), SPRING - 0.05, (ZF - 0.12 + ZB - 0.02) / 2), (1.4, 0.42, ZB - 0.02 - ZF + 0.12), STONE)  # imposta
    for key in ("hi", "lo"):                                                              # armellas de las cadenas
        x, y = STAPLES[(s, key)]
        mk.box(p, (x, y, ZF - 0.03), (0.34, 0.34, 0.1), IRON, detail=True)
        prof = [arc_pt(0.17, a, x, y - 0.12) for a in (20, -40, -90, -140, 200)]          # armella en U, colgando
        prof += [arc_pt(0.09, a, x, y - 0.12) for a in (200, -140, -90, -40, 20)]
        mk.prism(p, prof, 0.07, IRON, plane="xy", center=(0, 0, ZF - 0.08), detail=True)
    return p


def arch(mk):
    p = mk.part("Surround_Arch", (0, SPRING, 0))
    n = 7
    for k in range(n):
        a0, a1 = 180 - 180 * k / n, 180 - 180 * (k + 1) / n
        key = k == n // 2
        ro = RO + (0.4 if key else 0.0)
        zf = ZF - (0.1 if key else 0.05 * (k % 2))
        zb = ZB + 0.004 * (k % 2)
        pts = []
        for a in (a0, a1):
            for r in (RI, ro):
                x, y = arc_pt(r, a)
                if key and r == ro:                                    # clave: más ancha arriba
                    x = x * 1.25
                pts += [(x, y, zf), (x, y, zb)]
        mk.hull(p, pts, STONE)
    return p


# ---------------------------------------------------------------------------------------------- hojas
def leaf(mk, s):
    name = "DoorL" if s < 0 else "DoorR"
    hx = s * (XJ - 0.02)
    zc = (DZ0 + DZ1) / 2
    p = mk.part(name, (hx, 0, zc))
    r = RI - 0.02
    n = 7
    top = [arc_pt(r, 180 - 180 * k / n) for k in range(n + 1)]            # de la izquierda a la derecha
    if s < 0:
        pts = [p_ for p_ in top if p_[0] < -0.03]
        prof = [(hx, 0.03), (-0.03, 0.03), (-0.03, pts[-1][1])] + pts[::-1]
    else:
        pts = [p_ for p_ in top if p_[0] > 0.03]
        prof = [(0.03, 0.03), (hx, 0.03)] + pts[::-1] + [(0.03, pts[0][1])]
    mk.prism(p, prof, DZ1 - DZ0, WOOD, plane="xy", center=(0, 0, zc))
    w = (abs(hx) - 0.03) / 5
    for k in range(1, 5):                                                  # tablones: juntas oscuras de 0,06
        x = hx - s * w * k
        for d in (-0.03, 0.03):
            mk.slice(p, (x + d, 0, 0), (1, 0, 0))
        mk.paint(p, WOOD2, box=((x, 6.0, zc), (0.062, 12.5, 0.7)))
    k = 1 if s < 0 else 3                                                  # un tablón cambiado, más oscuro
    mk.paint(p, WOOD2, box=((hx - s * w * (k + 0.5), 6.0, zc), (w * 0.8, 12.5, 0.7)))
    zf = DZ0                                                               # cara de afuera
    for y in (1.6, 5.1, 8.7):                                              # pletinas con punta y clavos
        x1 = hx - s * 3.2
        prof_s = [(hx, y - 0.18), (x1 + s * 0.3, y - 0.18), (x1, y), (x1 + s * 0.3, y + 0.18), (hx, y + 0.18)]
        mk.prism(p, prof_s, 0.07, IRON, plane="xy", center=(0, 0, zf - 0.03), detail=True)
        for xs in (hx - s * 0.9, hx - s * 2.2):
            mk.hull(p, [(xs + dx, y + dy, zf - 0.06) for dx in (-0.08, 0.08) for dy in (-0.08, 0.08)]
                    + [(xs, y, zf - 0.16)], IRON, detail=True)
        mk.cyl(p, (hx, y, zc), 0.12, 0.55, IRON, sides=6, detail=True)                     # nudo de bisagra
    # cruz de hierro atornillada (sin talla)
    cx, cy, a, b, t = hx - s * 1.95, 6.9, 0.13, 1.35, 0.8
    cross = [(-a, -b), (a, -b), (a, -a + 0.3), (t, -a + 0.3), (t, a + 0.3), (a, a + 0.3), (a, b * 0.75), (-a, b * 0.75),
             (-a, a + 0.3), (-t, a + 0.3), (-t, -a + 0.3), (-a, -a + 0.3)]
    mk.prism(p, [(cx + u, cy + v) for u, v in cross], 0.07, IRON, plane="xy", center=(0, 0, zf - 0.03), detail=True)
    # tirador de argolla en el canto del medio
    tx, ty = s * 0.42, 5.0
    mk.box(p, (tx, ty + 0.12, zf - 0.03), (0.3, 0.36, 0.07), IRON, detail=True)
    for a0, a1, dz in ((-5, 185, 0.0), (175, 365, 0.004)):
        prof_r = [arc_pt(0.27, a0 + (a1 - a0) * i / 3, tx, ty - 0.12) for i in range(4)]
        prof_r += [arc_pt(0.17, a1 - (a1 - a0) * i / 3, tx, ty - 0.12) for i in range(4)]
        mk.prism(p, prof_r, 0.08 - dz, IRON, plane="xy", center=(0, 0, zf - 0.1), detail=True)
    return p


# --------------------------------------------------------------------------------------------- cadenas
def chain_link(mk, part, c, d, k, ln=0.78, wd=0.4, th=0.09):
    """Eslabón macizo en rombo a lo largo de d (12 triángulos); los pares acostados y los impares parados."""
    d = d.normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-3:
        side = Vector((1, 0, 0))
    side.normalize()
    nrm = d.cross(side)
    if k % 2:
        side, nrm = nrm, side
    pts = []
    for i in range(4):
        q = 2 * math.pi * i / 4
        pc = Vector(c) + d * (ln / 2 * math.cos(q)) + side * (wd / 2 * math.sin(q))
        pts += [tuple(pc + nrm * th / 2), tuple(pc - nrm * th / 2)]
    mk.hull(part, pts, IRON, detail=True)


def chains(mk):
    p = mk.part("Chains", (0, 0, 0))
    centre = Vector((0.0, 5.0, DZ0 - 0.2))
    paths = []
    for s, dzc in ((-1, 0.0), (1, 0.07)):
        a = Vector((STAPLES[(s, "hi")][0], STAPLES[(s, "hi")][1] - 0.17, ZF - 0.08))       # en el ojo de la armella
        b = Vector((STAPLES[(-s, "lo")][0], STAPLES[(-s, "lo")][1] - 0.17, ZF - 0.08))
        paths.append([a, centre + Vector((0, 0.15 * s, dzc)), b])
    for path in paths:
        k = 0
        for q0, q1 in zip(path, path[1:]):
            d = q1 - q0
            n = max(2, round(d.length / 0.7))
            for i in range(n):
                c = q0.lerp(q1, (i + 0.5) / n)
                chain_link(mk, p, c, d, k)
                k += 1
    # candado de bronce colgando del cruce
    lx, ly, lz = 0.0, 4.15, centre.z - 0.02
    mk.hull(p, [(lx + dx, ly + dy, lz + dz) for dx in (-0.36, 0.36) for dy in (-0.15, 0.32) for dz in (-0.14, 0.14)]
            + [(lx + dx, ly - 0.36, lz + dz) for dx in (-0.22, 0.22) for dz in (-0.12, 0.12)], BRASS)
    shackle = [arc_pt(0.27, a, lx, ly + 0.42) for a in (0, 45, 90, 135, 180)]
    inner = [arc_pt(0.16, a, lx, ly + 0.42) for a in (180, 135, 90, 45, 0)]
    prof = [(lx + 0.27, ly + 0.2)] + shackle + [(lx - 0.27, ly + 0.2), (lx - 0.16, ly + 0.2)] + inner + [(lx + 0.16, ly + 0.2)]
    mk.prism(p, prof, 0.1, IRON, plane="xy", center=(0, 0, lz))
    mk.carve(p, IRON, points=mk.pts_box((lx, ly + 0.02, lz - 0.14), (0.08, 0.2, 0.1)))       # bocallave
    return p


def build(mk):
    jamb(mk, -1)
    jamb(mk, 1)
    arch(mk)
    leaf(mk, -1)
    leaf(mk, 1)
    chains(mk)

"""
Receta de WST_CH_SermonBoard, los sermones clavados en las paredes (prompt 127, Bloques A + B). Objeto chico
de primer plano: el texto es un decal (también sirven para los "Se busca").

Brief
- Silueta: hoja clara clavada con dos clavos arriba y las esquinas de abajo levantadas; la misma hoja con la
  mitad de abajo arrancada en diagonal; y una pila de tres hojas torcidas.
- Medidas: hoja de 1,2 x 1,6 x 0,02, vertical, con la espalda en el plano de la pared (z = 0) y la cara de
  adelante (-Z) plana para el decal. Esquinas de abajo dobladas 35° hacia adelante en un triángulo de 0,2.
  Clavos: cabeza piramidal de 0,1 que sale 0,045.
- Piezas en fila sobre X (cada una con el origen abajo al centro, en la pared): Paper_Sheet en x = 0,
  Paper_Torn en x = 2, Paper_Stack en x = 4,2.
- La rota: queda la mitad de arriba; el borde va en diagonal de y 0,45 (izquierda) a 1,05 (derecha) con
  dientes chicos. La pila: tres hojas giradas -8°, +5° y -2°, cada una 0,005 metida en la de atrás (se tocan).
- Inferido: cuáles esquinas se doblan (las de abajo: las de arriba están clavadas), ángulo y tamaño del
  doblez, forma del desgarro, giros y corrimientos de la pila, clavos solo en la hoja de adelante de la pila.

Vueltas: 1) pasa a la primera; la pila bajaba 0,025 del piso por el giro de las hojas: subida 0,1.

Revisión
- 140 triángulos contra 100 para las tres piezas (+40 %): ~47 cada una. La hoja: prisma de 6 lados, dos
  esquinas dobladas y dos clavos; la rota: prisma del desgarro dentado y dos clavos; la pila: tres hojas y dos
  clavos. Clavos de cabeza piramidal (6 triángulos) para gastar poco.
- Medidas: hoja 1,2 x 1,6 x 0,02 (con clavos y dobleces sale hasta 0,1 adelante de la pared); fila de 5,57.
- Caras de adelante planas para el decal (el doblez queda afuera de la zona de texto). Sin letras en la
  geometría: el texto lo pone el motor.
"""

import math

PAPER, IRON = "paint_cream", "iron"
W, H, T = 1.2, 1.6, 0.02


def nail(mk, part, x, y, z_front):
    """Cabeza piramidal de 0,1 que sale 0,045 de la cara (se mete 0,005)."""
    b = 0.05
    mk.hull(part, [(x + dx, y + dy, z_front + 0.005) for dx in (-b, b) for dy in (-b, b)]
            + [(x, y, z_front - 0.045)], IRON, detail=True)


def curl(mk, part, ox, corner, a, b, ang=35.0):
    """Esquina doblada: el triángulo (a, corner, b) gira ang grados hacia adelante alrededor de la diagonal a-b.
    Se mete 0,01 en la hoja (si comparte la arista, se sueldan)."""
    ax, ay = a
    bx, by = b
    ux, uy = bx - ax, by - ay
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    cx, cy = corner
    t = (cx - ax) * ux + (cy - ay) * uy
    px, py = ax + ux * t, ay + uy * t                               # pie de la perpendicular en la diagonal
    d = math.hypot(cx - px, cy - py)
    vx, vy = (cx - px) / d, (cy - py) / d
    c2 = (px + vx * d * math.cos(math.radians(ang)), py + vy * d * math.cos(math.radians(ang)),
          -T - d * math.sin(math.radians(ang)))                      # la punta sale hacia -Z
    inset = 0.01
    a2 = (ax - vx * inset, ay - vy * inset)
    b2 = (bx - vx * inset, by - vy * inset)
    pts = []
    for (x, y), z in ((a2, -T), (b2, -T)):
        pts += [(ox + x, y, z), (ox + x, y, z + T)]
    pts += [(ox + c2[0], c2[1], c2[2]), (ox + c2[0] + vx * 0.0, c2[1], c2[2] + T)]
    mk.hull(part, pts, PAPER)


def paper_sheet(mk, ox):
    part = mk.part("Paper_Sheet", (ox, 0, 0))
    c = 0.2
    prof = [(-W / 2 + c, 0.0), (W / 2 - c, 0.0), (W / 2, c), (W / 2, H), (-W / 2, H), (-W / 2, c)]
    mk.prism(part, [(ox + x, y) for x, y in prof], T, PAPER, plane="xy", center=(0, 0, -T / 2))
    curl(mk, part, ox, (W / 2, 0.0), (W / 2 - c, 0.0), (W / 2, c))
    curl(mk, part, ox, (-W / 2, 0.0), (-W / 2, c), (-W / 2 + c, 0.0), ang=22.0)
    for x in (-0.47, 0.47):
        nail(mk, part, ox + x, H - 0.12, -T)


def paper_torn(mk, ox):
    part = mk.part("Paper_Torn", (ox, 0.45, 0))
    tear = [(-W / 2, 0.45), (-0.38, 0.62), (-0.2, 0.55), (0.05, 0.79), (0.25, 0.74), (0.45, 0.98), (W / 2, 1.05)]
    prof = tear + [(W / 2, H), (-W / 2, H)]
    mk.prism(part, [(ox + x, y) for x, y in prof], T, PAPER, plane="xy", center=(0, 0, -T / 2))
    for x in (-0.47, 0.47):
        nail(mk, part, ox + x, H - 0.12, -T)


def paper_stack(mk, ox):
    part = mk.part("Paper_Stack", (ox, 0, 0))
    sheets = [(-8.0, -0.08, 0.05), (5.0, 0.1, 0.0), (-2.0, 0.0, 0.08)]
    for k, (rot, dx, dy) in enumerate(sheets):
        z_back = -0.015 * k                                          # cada una 0,005 adentro de la de atrás
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        cx, cy = ox + dx, H / 2 + dy + 0.1                           # +0,1: giradas, las esquinas no bajan del piso
        corners = [(-W / 2, -H / 2), (W / 2, -H / 2), (W / 2, H / 2), (-W / 2, H / 2)]
        prof = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in corners]
        mk.prism(part, prof, T, PAPER, plane="xy", center=(0, 0, z_back - T / 2))
        if k == 2:
            for x in (-0.47, 0.47):
                xr, yr = x, H / 2 - 0.12
                nail(mk, part, cx + xr * ca - yr * sa, cy + xr * sa + yr * ca, z_back - T)


def build(mk):
    paper_sheet(mk, 0.0)
    paper_torn(mk, 2.0)
    paper_stack(mk, 4.2)

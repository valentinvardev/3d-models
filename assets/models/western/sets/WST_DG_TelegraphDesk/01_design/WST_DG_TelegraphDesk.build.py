"""
Receta de WST_DG_TelegraphDesk, la mesa del telegrafista (prompt 082, Bloques A + B).

Brief
- Oleada 4: el telegrafista manda el mensaje mientras se aguanta en el saloon; la mesa se ve de cerca
  (cámara al lado del operador) y desde el salón. Silueta: una mesa de patas finas con la lámpara
  encendida, dos frascos verdes y la cajita del receptor; arriba, en la pared, el rollo de alambre y el
  aislador verde.
- Medidas: mesa de 4 (X) x 2,5 (Z) x 2,6 de alto, frente hacia -Z (el operador se sienta adelante y mira a
  +Z, la pared atrás en z = 1,3). Origen en la base al centro.
- Piezas: Body (mesa, base del manipulador, receptor, pilas y cables, bloc, pie de la lámpara), Key (la
  palanca del manipulador con su perilla; origen en su eje, gira sobre X), Lamp_Glow (tubo de la lámpara,
  lamp_glow), WallCoil (ménsula de pared con el rollo de alambre y el aislador, y el cable que baja al
  receptor), _Operator (marcador en el piso donde va la silla, z = -2).
- Colores: mesa wood_mid con patas y faldón wood_dark, manipulador y receptor de bronce, pilas glass_green
  con tapas de hierro, bloc paint_cream, rollo de alambre rust (cobre viejo), aislador glass_green.
- Inferido: WallCoil como pieza aparte (va en la pared, no en la mesa), la base del manipulador fija en
  Body y solo la palanca en Key, receptor sobre caja de resonancia, pilas atrás a la izquierda, lámpara
  adelante a la izquierda, bloc al lado del manipulador, marcador en el piso.

Vueltas: 1) 948 tris, z-fighting de los bornes contra la placa del manipulador y de la columna del
receptor contra su palanca · 2) separaciones de 0,01 y menos lados en tapas, collar, bornes y rollo.

Revisión
- 876 triángulos contra 600 (+46 %, calidad primero: se mira en primer plano cuando el telegrafista manda
  el mensaje): Body 576 (manipulador con horquilla, yunque y bornes; receptor con bobinas y armadura;
  pilas con tapa y borne; cables; lámpara), WallCoil 172, Key 72, Lamp_Glow 44, _Operator 12.
- Medidas: mesa 4 x 2,6 x 2,5 (el prompt da 4 x 2,5 x 2,6 alto); con WallCoil llega a 5,48 de alto.
- Key gira sobre X en (0,75, 2,8, -0,44); Lamp_Glow con origen en el centro del tubo.
- Dudoso: WallCoil como pieza aparte (el prompt no la nombra); si va en Body, la colisión de casco de la
  mesa sube hasta la pared por encima de la tapa.
"""

import math

from mathutils import Vector

MID, DARK, BRASS, IRON = "wood_mid", "wood_dark", "brass", "iron"
TOP = 2.6


def bx(mk, part, x0, x1, y0, y1, z0, z1, mat, detail=False):
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), mat, detail=detail)


def ring(c, r, axis_dir, n, phase=0.5):
    a = Vector(axis_dir).normalized()
    u = a.cross(Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = a.cross(u)
    c = Vector(c)
    return [tuple(c + r * (math.cos(2 * math.pi * (i + phase) / n) * u + math.sin(2 * math.pi * (i + phase) / n) * v))
            for i in range(n)]


def wire(mk, part, pts, r=0.03, mat="iron"):
    """Cable en tramos rectos (triangular): cada tramo se mete en el siguiente."""
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        mk.hull(part, ring(a - d * 0.01, r, d, 3) + ring(b + d * 0.01, r, d, 3), mat)


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---------------- mesa ----------------
    bx(mk, body, -2.0, 2.0, TOP - 0.15, TOP, -1.25, 1.25, MID)                       # tapa
    for sx in (-1, 1):                                                                # patas ahusadas
        for sz in (-1, 1):
            x, z = sx * 1.78, sz * 1.03
            mk.hull(body, [(x + dx, 0.0, z + dz) for dx in (-0.09, 0.09) for dz in (-0.09, 0.09)]
                    + [(x + dx, TOP - 0.14, z + dz) for dx in (-0.12, 0.12) for dz in (-0.12, 0.12)], DARK)
    bx(mk, body, -1.72, 1.72, TOP - 0.52, TOP - 0.145, -0.98, 0.98, DARK)            # faldón
    bx(mk, body, -0.7, 0.7, TOP - 0.47, TOP - 0.2, -1.02, -0.97, MID)                 # cajón
    bx(mk, body, -0.07, 0.07, TOP - 0.38, TOP - 0.29, -1.08, -1.0, BRASS)            # tirador
    # ---------------- manipulador: base fija ----------------
    kx, kz = 0.75, -0.62
    bx(mk, body, kx - 0.2, kx + 0.2, TOP - 0.01, TOP + 0.08, kz - 0.38, kz + 0.38, DARK)       # tabla
    bx(mk, body, kx - 0.13, kx + 0.13, TOP + 0.07, TOP + 0.11, kz - 0.3, kz + 0.33, BRASS)      # placa
    for sx in (-1, 1):                                                                         # horquilla del eje
        bx(mk, body, kx + sx * 0.1 - 0.025, kx + sx * 0.1 + 0.025, TOP + 0.1, TOP + 0.26, kz + 0.12, kz + 0.24,
           BRASS)
    mk.cyl(body, (kx, TOP + 0.13, kz - 0.18), 0.04, 0.06, BRASS, sides=6)                      # yunque
    for dz in (0.27, -0.27):                                                                   # bornes
        mk.cyl(body, (kx - 0.15, TOP + 0.14, kz + dz), 0.035, 0.12, BRASS, sides=4)
    # ---------------- receptor sobre su caja de resonancia ----------------
    sx_, sz_ = 1.05, 0.55
    bx(mk, body, sx_ - 0.42, sx_ + 0.42, TOP - 0.01, TOP + 0.42, sz_ - 0.3, sz_ + 0.3, DARK)
    bx(mk, body, sx_ - 0.3, sx_ + 0.3, TOP + 0.41, TOP + 0.45, sz_ - 0.2, sz_ + 0.2, BRASS)
    for dx in (-0.12, 0.12):                                                                   # bobinas
        mk.cyl(body, (sx_ + dx, TOP + 0.58, sz_ + 0.05), 0.09, 0.28, IRON, sides=6)
    bx(mk, body, sx_ - 0.24, sx_ + 0.24, TOP + 0.71, TOP + 0.77, sz_ - 0.02, sz_ + 0.12, BRASS)    # armadura
    bx(mk, body, sx_ + 0.19, sx_ + 0.25, TOP + 0.44, TOP + 0.95, sz_ + 0.025, sz_ + 0.095, BRASS)  # columna
    bx(mk, body, sx_ - 0.26, sx_ + 0.26, TOP + 0.92, TOP + 0.98, sz_ + 0.02, sz_ + 0.1, BRASS)    # palanca de arriba
    # ---------------- pilas de vidrio verde con su tapa de zinc ----------------
    jars = [(-1.45, 0.62), (-0.92, 0.72)]
    for jx, jz in jars:
        mk.cyl(body, (jx, TOP + 0.24, jz), 0.21, 0.5, "glass_green", sides=8)
        mk.cyl(body, (jx, TOP + 0.51, jz), 0.15, 0.06, IRON, sides=6)
        mk.cyl(body, (jx + 0.06, TOP + 0.6, jz), 0.03, 0.14, IRON, sides=4)
    # cables: pila -> pila -> receptor -> manipulador
    wire(mk, body, [(jars[0][0] + 0.06, TOP + 0.66, jars[0][1]), (-1.2, TOP + 0.45, 0.66),
                    (jars[1][0] + 0.06, TOP + 0.66, jars[1][1])])
    wire(mk, body, [(jars[1][0] + 0.06, TOP + 0.66, jars[1][1]), (-0.3, TOP + 0.02, 0.6), (0.3, TOP + 0.02, 0.5),
                    (sx_ - 0.42, TOP + 0.2, sz_)])
    wire(mk, body, [(sx_ - 0.1, TOP + 0.02, sz_ - 0.31), (kx - 0.15, TOP + 0.02, kz + 0.45),
                    (kx - 0.15, TOP + 0.18, kz + 0.27)])
    # ---------------- bloc de telegramas en blanco ----------------
    mk.box(body, (-0.25, TOP + 0.035, -0.55), (0.7, 0.08, 0.95), "paint_cream", rot=(0, 9, 0))
    mk.box(body, (-0.32, TOP + 0.085, -0.52), (0.62, 0.03, 0.42), "paint_cream", rot=(0, -6, 0))   # hoja suelta
    bx(mk, body, 0.12, 0.17, TOP - 0.005, TOP + 0.045, -1.0, -0.4, "wood_light")                   # lápiz
    # ---------------- lámpara de aceite (pie y depósito; el tubo es Lamp_Glow) ----------------
    lx, lz = -1.45, -0.5
    mk.cyl(body, (lx, TOP + 0.03, lz), 0.24, 0.08, BRASS, sides=8)
    mk.cyl(body, (lx, TOP + 0.21, lz), 0.2, 0.3, BRASS, sides=8, top=0.6)
    mk.cyl(body, (lx, TOP + 0.4, lz), 0.11, 0.1, BRASS, sides=6)
    g = mk.part("Lamp_Glow", (lx, TOP + 0.44, lz))
    mk.hull(g, ring((lx, TOP + 0.43, lz), 0.09, (0, 1, 0), 8) + ring((lx, TOP + 0.6, lz), 0.16, (0, 1, 0), 8)
            + ring((lx, TOP + 1.0, lz), 0.075, (0, 1, 0), 8), "lamp_glow")

    # ---------------- palanca del manipulador (gira sobre X en la horquilla) ----------------
    piv = (kx, TOP + 0.2, kz + 0.18)
    k = mk.part("Key", piv)
    mk.cyl(k, piv, 0.04, 0.16, BRASS, axis="x", sides=6)                                       # eje
    mk.hull(k, [(kx + dx, TOP + 0.18 + dy, z) for dx in (-0.035, 0.035) for dy in (-0.025, 0.025)
                for z in (kz + 0.26, kz - 0.3)], BRASS)                                       # palanca
    mk.cyl(k, (kx, TOP + 0.24, kz - 0.3), 0.1, 0.06, "coal", sides=8)                          # perilla
    mk.cyl(k, (kx, TOP + 0.2, kz - 0.3), 0.025, 0.06, BRASS, sides=4)

    # ---------------- en la pared: rollo de alambre y aislador ----------------
    zw = 1.3
    w = mk.part("WallCoil", (0.2, 4.2, zw))
    bx(mk, w, -0.2, 0.6, 4.15, 5.4, zw - 0.12, zw, DARK)                                      # tabla en la pared
    mk.cyl(w, (0.2, 5.05, zw - 0.3), 0.05, 0.4, DARK, axis="z", sides=6)                      # clavija
    r_out, r_in, n = 0.42, 0.27, 4
    for a0, a1 in ((90.4, 269.6), (270.4, 449.6)):                                                    # rollo, en dos mitades
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([(0.2 + r_out * math.cos(math.radians(a)), 4.83 + r_out * math.sin(math.radians(a))) for a in angs]
                + [(0.2 + r_in * math.cos(math.radians(a)), 4.83 + r_in * math.sin(math.radians(a))) for a in reversed(angs)])
        mk.prism(w, prof, 0.16, "rust", plane="xy", center=(0, 0, zw - 0.32))
    # aislador en su perno, a la derecha
    bx(mk, w, 0.55, 1.05, 5.08, 5.2, zw - 0.32, zw - 0.02, DARK)                              # brazo
    mk.cyl(w, (0.95, 5.25, zw - 0.25), 0.03, 0.12, DARK, sides=4)                             # perno
    mk.cyl(w, (0.95, 5.38, zw - 0.25), 0.12, 0.2, "glass_green", sides=8, top=0.6)
    wire(mk, w, [(0.95, 5.36, zw - 0.36), (1.0, 4.4, zw - 0.5), (sx_ + 0.15, TOP + 0.3, sz_ + 0.31)], mat="rust")

    mk.marker("_Operator", (0.0, 0.0, -2.0))

"""
Receta de WST_HC_Graves, las tumbas del cementerio de Hollow Creek (prompt 117, Bloques A + B).

Brief
- Silueta a 40 studs: un montículo largo y bajo de tierra facetada (cerrada), la misma tumba reventada
  desde abajo (borde de tierra levantado, terrones tirados, pozo oscuro y la tapa del cajón asomando en
  diagonal) y una tumba fresca, más alta y oscura, con una pala clavada.
- Tres objetos en fila sobre X cada 6 (Grave_Mound en x = -6, Grave_Open en 0, Grave_Fresh en 6), origen
  de cada uno en el piso al centro de la tumba (prompt). CoffinLid aparte, con el origen de Grave_Open.
- Grave_Mound: casco de tres anillos jitterados (3 x 7 en el piso, 0,8 de alto), facetas ochre con algunas
  sand (las pinta enteras: es lo que pide "faceted dirt").
- Grave_Open: borde de tierra levantado (3,8 x 5,8, 0,65 de alto) con el pozo de 2,5 x 4 de borde
  dentado tallado hasta y = -3 (paredes hide_brown: tierra húmeda); debajo del piso, el forro del pozo
  (el terreno de Studio tiene que tener el hueco). Terrones (ochre y hide_brown) tirados hacia afuera
  apoyados en el borde, y el fondo roto del cajón abajo.
- CoffinLid: tapa de cajón de 6 lados (hombros de 1,7), quebrada en zigzag a 3,4 de largo, con dos
  listones; apoyada en el borde del pozo a 52°, la punta rota adentro.
- Grave_Fresh: montículo de 3 x 6,6 y 1,0 de alto en tierra removida (hide_brown con terrones ochre) y
  una pala (cabo wood_light con manija en D, hoja de hierro) clavada a 20°.
- Inferido: separación, alturas del borde y de la tumba fresca, colores de la tierra removida, forro del
  pozo, fondo del cajón, forma de la tapa y de la pala, origen de CoffinLid (el de la tumba).

Vueltas: 1) primera versión: la tapa del cajón flotaba en el medio del pozo (apoyada en nada), la hoja de
la pala quedaba toda enterrada, el montículo en el origen sin tocar nada (flotante para la revisión), un
terrón suelto y z-fighting entre las piezas de la manija en D · 2) la tapa entera (6,3, quebrada en la
cabeza) apoya el pie en el fondo y descansa en el borde a 45°, pala 0,65 más arriba, tumba abierta en el
origen y las otras a ±6, manija con espesores 0,055/0,06/0,065; la tierra removida pasó de redrock_dark
(se leía roja, como sangre) a hide_brown · 3) pozo de 13 puntos y 6 terrones (598 -> 468), tres terrones
sobre el montículo cerrado (56 -> 116: era una papa lisa).

Revisión
- Triángulos por pieza (tope 250 de referencia): Grave_Mound 116, Grave_Open 468 (+87 %: el borde
  dentado tallado en el borde y en el forro, 6 terrones y el fondo del cajón), CoffinLid 60, Grave_Fresh
  230. La tumba abierta es el foco del cementerio (los muertos salen de ahí).
- Medidas: montículo 3 x 7 x 0,8 (+ terrones); abierta 3,8 x 5,8 con el borde a 0,65 y el pozo de 2,5 x
  4 hasta y = -3 (forro hasta -3,1); fresca 3 x 6,6 x 1,0 con la pala hasta 3,9.
- DUDOSO: el forro del pozo es una caja de 3,3 x 3,15 x 4,9 bajo el piso; en el visor se ve colgando abajo
  de la tumba. En Studio el terreno tiene que tener el hueco (o se deja la tumba sobre un terreno que la
  tape). Con colisión de casco, el pozo queda tapado (se camina por encima).
- CoffinLid lleva el origen de la tumba abierta (0, 0, 0 del set); no es pieza móvil.
"""

import math

from mathutils import Euler, Vector

DIRT, SAND, WET, WOOD, WOOD2, IRON, HANDLE = ("ochre", "sand", "hide_brown", "wood_dark", "wood_mid", "iron",
                                              "wood_light")


def oval(cx, y, cz, rx, rz, n=10, jit=0.0, seed=0, ky=0.0):
    ks = (0.06, -0.04, 0.03, -0.07, 0.05, -0.02, 0.07, -0.05, 0.02, -0.06, 0.04, -0.03)
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        j = 1 + jit * ks[(i + seed) % 12] / 0.07
        # óvalo con los costados casi rectos (superelipse)
        c, s = math.cos(a), math.sin(a)
        e = 0.6
        x = rx * j * math.copysign(abs(c) ** e, c)
        z = rz * j * math.copysign(abs(s) ** e, s)
        out.append((cx + x, y + ky * ks[(i + seed + 5) % 12], cz + z))
    return out


def clump(mk, part, c, r, mat, seed=0):
    mk.ball(part, c, r, mat, scale=(1.0, 0.5, 0.8), rot=(0, 37 * seed, 11 * seed), subdiv=1)


# ---------------------------------------------------------------------------------------------- tumbas
def mound(mk, ox):
    p = mk.part("Grave_Mound", (ox, 0, 0))
    pts = (oval(ox, 0.0, 0, 1.5, 3.5, 12, jit=0.04, seed=0) + oval(ox, 0.5, 0, 1.15, 3.0, 10, jit=0.06, seed=3, ky=0.8)
           + oval(ox, 0.8, 0, 0.6, 2.2, 8, jit=0.08, seed=7, ky=0.6))
    mk.hull(p, pts, DIRT)
    for c in ((ox - 0.7, 0.5, -1.8), (ox + 0.5, 0.75, 0.6), (ox + 0.9, 0.3, 2.4), (ox - 0.3, 0.8, -2.6),
              (ox - 1.0, 0.25, 1.2)):
        mk.paint(p, SAND, ball=(c, 0.5))
    for i, (x, y, z, r) in enumerate(((0.35, 0.84, -1.1, 0.22), (-0.45, 0.84, 1.5, 0.26), (0.9, 0.3, -2.7, 0.24))):
        clump(mk, p, (ox + x, y, z), r, SAND if i == 1 else DIRT, seed=i + 2)                # terrones sueltos
    return p


def open_grave(mk, ox):
    p = mk.part("Grave_Open", (ox, 0, 0))
    rim = (oval(ox, 0.0, 0, 1.9, 2.9, 12, jit=0.05, seed=1) + oval(ox, 0.45, 0, 1.6, 2.55, 10, jit=0.08, seed=4, ky=1.2)
           + oval(ox, 0.65, 0, 1.4, 2.25, 10, jit=0.1, seed=8, ky=1.0))
    mk.hull(p, rim, DIRT)
    mk.box(p, (ox, -1.525, 0), (3.3, 3.15, 4.9), WET)                                # forro del pozo, bajo el piso
    hole = [(-1.25, -2.0), (-0.3, -2.12), (0.6, -1.95), (1.25, -2.05), (1.2, -0.9), (1.32, 0.3), (1.18, 1.3),
            (1.15, 2.0), (0.2, 2.1), (-0.7, 1.94), (-1.28, 2.05), (-1.15, 0.6), (-1.3, -0.7)]
    mk.carve(p, WET, prism=dict(profile=[(ox + x, z) for x, z in hole], depth=5.0, plane="xz", center=(0, -0.5, 0)))
    for c in ((ox - 0.8, 0.5, -2.2), (ox + 1.1, 0.35, 1.9), (ox - 1.4, 0.3, 1.0)):
        mk.paint(p, SAND, ball=(c, 0.45))
    # terrones tirados hacia afuera (apoyados en el borde)
    for i, (x, y, z, r, mat) in enumerate(((-2.0, 0.15, -1.6, 0.42, DIRT), (2.05, 0.18, -0.4, 0.5, WET),
                                           (1.7, 0.12, 2.3, 0.36, DIRT), (-1.6, 0.2, 2.5, 0.45, WET),
                                           (0.4, 0.15, -3.0, 0.4, DIRT), (-0.9, 0.55, 2.05, 0.28, DIRT))):
        clump(mk, p, (ox + x, y, z), r, mat, seed=i)
    # fondo del cajón roto, abajo del pozo
    mk.prism(p, [(ox - 0.85, -1.6), (ox + 0.8, -1.6), (ox + 0.85, 0.6), (ox + 0.3, 0.9), (ox + 0.45, 1.3),
                 (ox - 0.2, 1.45), (ox - 0.85, 1.2)], 0.16, WOOD, plane="xz", center=(0, -2.93, 0), detail=True)
    return p


def coffin_lid(mk, ox):
    p = mk.part("CoffinLid", (ox, 0, 0))
    # tapa de cajón en su plano (u ancho, v largo): pie angosto, hombros, cabeza quebrada en zigzag
    prof = [(-0.5, 0.0), (0.5, 0.0), (0.85, 4.2), (0.66, 5.75), (0.4, 6.05), (0.18, 5.8), (-0.08, 6.3), (-0.35, 5.95),
            (-0.66, 6.1), (-0.85, 4.2)]
    rot = (-45.0, 8.0, 0.0)
    e = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    base = Vector((ox + 0.1, -2.98, -1.65)) + e @ Vector((0, 0.1, 0))   # el pie apoya en el fondo del pozo
    mk.prism(p, prof, 0.2, WOOD2, plane="xz", center=tuple(base), rot=rot)

    def P(u, v, w):
        return tuple(base + e @ Vector((u, w, v)))
    for v in (1.2, 3.6):                                                  # listones de arriba
        mk.hull(p, [P(u, vv, w) for u in (-0.7 + v * 0.03, 0.7 - v * 0.0) for vv in (v - 0.18, v + 0.18)
                    for w in (0.08, 0.24)], WOOD)
    return p


def fresh_grave(mk, ox):
    p = mk.part("Grave_Fresh", (ox, 0, 0))
    pts = (oval(ox, 0.0, 0, 1.5, 3.3, 12, jit=0.06, seed=2) + oval(ox, 0.6, 0, 1.15, 2.8, 10, jit=0.1, seed=5, ky=1.5)
           + oval(ox, 1.0, 0, 0.55, 2.0, 8, jit=0.12, seed=9, ky=1.2))
    mk.hull(p, pts, WET)
    for i, (x, y, z, r) in enumerate(((-0.5, 0.95, -1.2, 0.3), (0.45, 0.85, 0.9, 0.34), (-0.9, 0.5, 2.0, 0.3),
                                      (1.1, 0.35, -2.1, 0.28), (0.1, 1.0, 1.9, 0.25))):
        clump(mk, p, (ox + x, y, z), r, DIRT, seed=i + 3)
    # pala clavada: hoja de hierro adentro de la tierra, cabo con manija en D
    tilt = Euler((math.radians(-20), 0, math.radians(10)), "XYZ").to_matrix()
    root = Vector((ox + 0.2, 1.2, -0.4))

    def S(x, y, z):
        return tuple(root + tilt @ Vector((x, y, z)))
    mk.hull(p, [S(x, y, z) for x in (-0.3, 0.3) for y in (-0.5, 0.15) for z in (-0.03, 0.03)]
            + [S(0.0, -0.75, 0.0)], IRON, detail=True)                                       # hoja (punta enterrada)
    mk.hull(p, [S(x, y, z) for x in (-0.06, 0.06) for y in (0.1, 2.75) for z in (-0.06, 0.06)], HANDLE, detail=True)
    for xa, xb in ((-0.24, -0.12), (0.12, 0.24)):                                             # manija en D
        mk.hull(p, [S(x, y, z) for x in (xa, xb) for y in (2.7, 3.15) for z in (-0.055, 0.055)], HANDLE, detail=True)
    mk.hull(p, [S(x, y, z) for x in (-0.26, 0.26) for y in (3.1, 3.22) for z in (-0.06, 0.06)], HANDLE, detail=True)
    mk.hull(p, [S(x, y, z) for x in (-0.25, 0.25) for y in (2.68, 2.8) for z in (-0.065, 0.065)], HANDLE, detail=True)
    return p


def build(mk):
    mound(mk, -6.0)
    open_grave(mk, 0.0)
    coffin_lid(mk, 0.0)
    fresh_grave(mk, 6.0)

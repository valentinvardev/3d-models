"""
Receta de WST_Prop_Cactus, los cactus del desierto (prompt 133, Bloques A + B). Seis objetos en fila
sobre X, cada uno con el origen en su base (como las balas sueltas: piezas separadas en un archivo).

Brief
- Silueta a 40 studs: el saguaro es LA silueta del Western (columna con brazos que suben), el muerto
  se lee como jaula de costillas inclinada, la tuna como manojo de paletas, el barril como bola con
  costillas y el ocotillo como manojo de varas finas abiertas.
- Facetado de 6-8 lados: las aristas del polígono son las costillas. cactus para la carne; las
  "puntas más claras" van en paint_cream (no hay verde claro en la paleta: la corona clara se lee como
  las flores blancas del saguaro).
- Piezas y medidas: Saguaro_A 12 de alto, tronco r 0,62-0,7 y dos brazos que salen horizontales y
  suben; Saguaro_B 9 de alto, un brazo; Saguaro_Dead 10 de largo, 8 costillas wood_light en ronda
  sobre un tocón wood_dark, inclinado 8°, algunas costillas quebradas más cortas; PricklyPear 6 paletas
  ovaladas planas, 3 de alto, con tres tunas paint_red; BarrelCactus 1,5 x 1,2 con 12 costillas, corona
  clara y seis flores paint_red; Ocotillo 6 de alto, 9 varas abiertas con puntas paint_red.
- Inferido: paint_cream para las puntas claras; grosores; ángulos y alturas de los brazos; colores del
  saguaro muerto (tocón wood_dark); tunas y flores rojas del ocotillo (el prompt solo pide flores en el
  barril); separación entre piezas.

Vueltas: 1) 24 pares coplanares en Saguaro_Dead (las costillas arrancaban en y = 0, igual que la base
del tocón); saguaros de 11,4 y 8,5 (la cúpula y la corona suman ~0,5 sobre el último anillo); las varas
del ocotillo se abrían todas para el mismo lado (con Euler XYZ el giro en Y iba antes que la inclinación)
· 2) costillas desde 0,05, troncos más altos y de un solo tramo (dos casi colineales no cambiaban la
silueta y costaban 28 tris), varas con la dirección calculada a mano.

Revisión
- Triángulos por pieza (tope 200 por pieza): Saguaro_A 250, Saguaro_B 160, Saguaro_Dead 124,
  PricklyPear 192, BarrelCactus 152, Ocotillo 158. El A se pasa por los dos brazos de 3 tramos (el codo
  que sube es la silueta del saguaro).
- Medidas: Saguaro_A 12,0, Saguaro_B 9,0, Saguaro_Dead 9,8 de alto inclinado (10 de largo),
  PricklyPear 3,0, BarrelCactus 1,56 x 1,16 (pedía 1,5 x 1,2: las flores suman 0,06 de alto),
  Ocotillo 6,3.
- Las coronas claras son chicas (0,4 de ancho): de lejos los saguaros se ven verdes enteros. Si la
  "punta más clara" del prompt pide más, haría falta un verde claro en la paleta (decide Valentin).
- Los codos de los brazos muestran un escalón facetado donde los tramos se pasan: es lo que evita que
  el codo abra.
"""

import math

from mathutils import Euler, Vector


def ring(p, d, r, sides, phase=0.5):
    d = Vector(d).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    v = d.cross(u)
    return [tuple(Vector(p) + r * (math.cos(2 * math.pi * (k + phase) / sides) * u
                                   + math.sin(2 * math.pi * (k + phase) / sides) * v)) for k in range(sides)]


def limb(mk, part, pts, radii, sides, mat="cactus", crown="paint_cream", flat_base=False):
    """Tramos rectos de anillo a anillo; cada uno se pasa 0,7 r de la junta (el codo no abre) y los
    radios alternan 1/0,97 (sin caras coplanares ni vértices compartidos). Cierra con cúpula y corona."""
    pts = [Vector(p) for p in pts]
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        d = (b - a).normalized()
        k = 0.97 if i % 2 else 1.0
        a2 = a if (i == 0 and flat_base) else a - d * radii[i] * 0.7
        b2 = b + d * radii[i + 1] * 0.7 if i < n - 1 else b
        ra = radii[i] * k
        da = Vector((0, 1, 0)) if (i == 0 and flat_base) else d
        mk.hull(part, ring(a2, da, ra, sides) + ring(b2, d, radii[i + 1] * k, sides), mat)
    d = (pts[-1] - pts[-2]).normalized()
    r = radii[-1] * (0.97 if (n - 1) % 2 else 1.0)
    top = pts[-1] + d * r * 0.55
    mk.hull(part, ring(pts[-1] - d * 0.02, d, r * 0.995, sides) + ring(top, d, r * 0.62, sides), mat)   # cúpula
    mk.hull(part, ring(top - d * 0.03, d, r * 0.6, sides) + [tuple(top + d * r * 0.28)], crown)        # corona clara


def rot_y(p, deg, c=(0, 0, 0)):
    e = Euler((0, math.radians(deg), 0), "XYZ").to_matrix()
    return tuple(Vector(c) + e @ (Vector(p) - Vector(c)))


def saguaro(mk, name, x0, trunk, arms):
    part = mk.part(name, (x0, 0, 0))
    ys, rs = trunk
    limb(mk, part, [(x0, y, 0) for y in ys], rs, 8, flat_base=True)
    for pts, radii, yaw in arms:
        limb(mk, part, [rot_y((x0 + x, y, z), yaw, (x0, 0, 0)) for x, y, z in pts], radii, 6)


def build(mk):
    # ---------------- saguaros ----------------
    # tronco de un tramo (con dos casi colineales la silueta era la misma y costaba 28 tris más)
    saguaro(mk, "Saguaro_A", 0.0, ((0.0, 11.5), (0.7, 0.62)), [                 # cúpula + corona suman ~0,5: 12
        ([(0.3, 5.0, 0), (1.55, 5.25, 0), (2.15, 6.15, 0), (2.2, 8.9, 0)], (0.44, 0.44, 0.43, 0.41), -15),
        ([(-0.3, 6.2, 0), (-1.35, 6.4, 0), (-1.85, 7.2, 0), (-1.9, 9.7, 0)], (0.42, 0.42, 0.41, 0.39), 25),
    ])
    saguaro(mk, "Saguaro_B", 7.0, ((0.0, 8.55), (0.62, 0.55)), [
        ([(-0.3, 3.8, 0), (-1.3, 4.05, 0), (-1.8, 4.9, 0), (-1.85, 6.6, 0)], (0.4, 0.4, 0.39, 0.37), -20),
    ])

    # ---------------- saguaro muerto: costillas en ronda sobre un tocón, inclinado ----------------
    x0 = 13.0
    dead = mk.part("Saguaro_Dead", (x0, 0, 0))
    mk.hull(dead, ring((x0, 0.0, 0), (0, 1, 0), 0.62, 8) + ring((x0, 0.75, 0), (0, 1, 0), 0.5, 8), "wood_dark")
    lean = Euler((0, 0, math.radians(-8)), "XYZ").to_matrix()
    tops = (10.0, 9.2, 9.8, 7.1, 9.6, 8.4, 9.9, 6.2)              # dos costillas quebradas
    for k, top in enumerate(tops):
        a = math.radians(45 * k + 10)
        c = Vector((0.45 * math.cos(a), 0, 0.45 * math.sin(a)))
        t = Vector((-math.sin(a), 0, math.cos(a)))                  # tangente: la costilla es una tabla
        n = Vector((math.cos(a), 0, math.sin(a)))
        pts = []
        for y in (0.05, top):                                    # arranca dentro del tocón (en 0 era coplanar con su base)
            base = c + Vector((0, y, 0))
            if y > 0.05:
                base = lean @ base
            for dt in (-0.08, 0.08):
                for dn in (-0.06, 0.06):
                    p = base + t * dt + n * dn
                    pts.append((x0 + p.x, max(p.y, 0.0), p.z))
        mk.hull(dead, pts, "wood_light")

    # ---------------- tuna: seis paletas ovaladas planas ----------------
    x0 = 18.0
    pp = mk.part("PricklyPear", (x0, 0, 0))

    def pad(c, w, h, tilt, yaw, base=False, fruits=()):
        e = Euler((0, math.radians(yaw), math.radians(tilt)), "XYZ").to_matrix()
        up, side, nrm = e @ Vector((0, 1, 0)), e @ Vector((1, 0, 0)), e @ Vector((0, 0, 1))
        pts = []
        for k in range(8):
            t = 2 * math.pi * k / 8
            for s in (-0.09, 0.09):
                pts.append(Vector(c) + side * (w / 2 * math.cos(t)) + up * (h / 2 * math.sin(t)) + nrm * s)
        dy = -min(p.y for p in pts) if base else 0.0
        pts = [(x0 + p.x, p.y + dy, p.z) for p in pts]
        mk.hull(pp, pts, "cactus")
        top = Vector(c) + up * (h / 2) + Vector((0, dy, 0))
        for f in fruits:                                            # tunas en el borde de arriba
            fc = top + side * f - up * 0.06
            mk.hull(pp, [(x0 + fc.x + dx, fc.y + dy2, fc.z + dz) for dx, dy2, dz in
                         ((0.1, 0, 0), (-0.1, 0, 0), (0, 0, 0.1), (0, 0, -0.1), (0, 0.22, 0), (0, -0.08, 0))],
                    "paint_red")
        return top

    pad((-0.45, 0.8, 0.0), 1.2, 1.6, 12, 10, base=True)
    pad((0.5, 0.75, 0.15), 1.1, 1.5, -15, -25, base=True)
    pad((-0.75, 1.95, -0.05), 1.0, 1.35, 28, 15, fruits=(0.15,))
    pad((0.8, 1.85, 0.2), 0.95, 1.3, -30, -30)
    pad((-0.1, 2.25, 0.05), 0.9, 1.25, 5, 40, fruits=(-0.2, 0.18))
    pad((0.15, 1.2, -0.45), 0.9, 1.2, -5, 75, base=True)

    # ---------------- cactus barril: 12 costillas, corona clara, flores rojas ----------------
    x0 = 21.5
    bc = mk.part("BarrelCactus", (x0, 0, 0))
    rings = ((0.0, 0.46), (0.42, 0.6), (1.02, 0.58), (1.36, 0.4), (1.5, 0.14))
    mk.hull(bc, [p for y, r in rings for p in ring((x0, y, 0), (0, 1, 0), r, 12)], "cactus")
    mk.paint(bc, "paint_cream", ball=((x0, 1.5, 0), 0.3))           # corona clara (las caras de arriba)
    for k in range(6):
        a = math.radians(60 * k + 15)
        fc = Vector((x0 + 0.31 * math.cos(a), 1.42, 0.31 * math.sin(a)))
        mk.hull(bc, [tuple(fc + Vector(o)) for o in ((0.08, -0.04, 0), (-0.08, -0.04, 0), (0, -0.04, 0.08),
                                                       (0, -0.04, -0.08), (0, 0.14, 0))], "paint_red", detail=True)

    # ---------------- ocotillo: varas finas abiertas desde un pie ----------------
    x0 = 25.0
    oc = mk.part("Ocotillo", (x0, 0, 0))
    mk.hull(oc, ring((x0, 0.0, 0), (0, 1, 0), 0.42, 6) + ring((x0, 0.35, 0), (0, 1, 0), 0.3, 6), "wood_dark")
    stalks = ((0, 6.0, 4), (40, 5.4, 14), (80, 5.0, 20), (125, 5.7, 12), (165, 4.6, 22), (205, 5.9, 9),
              (250, 5.2, 17), (290, 4.8, 24), (330, 5.6, 15))
    for i, (az, length, tilt) in enumerate(stalks):
        t, a = math.radians(tilt), math.radians(az)
        d = Vector((math.sin(t) * math.cos(a), math.cos(t), math.sin(t) * math.sin(a)))   # se abre hacia az
        b0 = Vector((x0 + 0.12 * math.cos(math.radians(az)), 0.15, 0.12 * math.sin(math.radians(az))))
        tip = b0 + d * length
        mk.hull(oc, ring(b0, d, 0.09, 4) + ring(tip, d, 0.045, 4), "cactus")
        if i % 2 == 0:                                              # flores rojas en la punta
            mk.hull(oc, ring(tip - d * 0.25, d, 0.07, 4) + [tuple(tip + d * 0.12)], "paint_red", detail=True)

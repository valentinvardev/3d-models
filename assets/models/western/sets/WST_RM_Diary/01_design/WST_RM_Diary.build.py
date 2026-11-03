"""
Receta de WST_RM_Diary, el diario de cuero abierto (prompt 095, Bloques A + B). Objeto chico de primer
plano: se mira de cerca cuando se junta (los diarios de los mineros que brillaban).

Brief
- Silueta: libro abierto chato, tapas de cuero oscuro que asoman alrededor de dos bloques de páginas
  claras que se hunden hacia el lomo, un lápiz amarillo cruzado arriba y una mancha de plata en el canto.
- Medidas: abierto 0,9 (X) x 0,6 (Z), 0,15 de alto. Tapas de 0,46 x 0,62 x 0,025 con una esquina gastada
  cada una; bloques de páginas de 0,42 x 0,56: finos en el canto (0,075), se arquean hasta 0,135 cerca del
  lomo y se hunden en la canaleta (curva del libro abierto); lomo redondeado abajo.
- Páginas lisas (paint_cream) para el decal: el texto lo pone el motor, como en los carteles.
- Lápiz: cuerpo de 6 lados paint_mustard de 0,4 x 0,045, punta afilada wood_light, cruzado en diagonal
  sobre la página derecha, apoyado (no flota).
- Mancha: rebaje de 0,006 con silver_neon del tamaño de una yema (0,09 x 0,11) que dobla el canto de la
  página derecha (arriba y en el costado del bloque).
- Inferido: lápiz amarillo, una esquina gastada por tapa, dónde va la mancha, la curva de las páginas.

Vueltas: 1) las hojas eran dos bloques con el canto vertical de 0,125: parecían esponjas · 2) hojas finas en
el canto que se arquean hacia el lomo; mancha más chica y ovalada; lápiz apoyado en la loma.

Revisión
- 184 triángulos contra 120 (+53 %, calidad primero: objeto de primer plano). Tapas con esquina gastada
  32, hojas arqueadas 2 x ~28, lomo, lápiz de 6 lados con punta ~40, la mancha tallada ~40 (dobla el canto).
- Medidas: 0,91 x 0,178 x 0,62 (0,9 x 0,6 abierto; el alto suma el lápiz apoyado sobre la loma de 0,135).
- 5 materiales: leather_dark, paint_cream (hojas lisas para el decal), paint_mustard, wood_light, silver_neon.
- Las hojas quedan lisas: el texto va por decal (Bloque A), no como letras en la geometría.
- review_focus.png sale en blanco con este modelo (0,9 studs, dos veces); se revisó con review_material.png.
"""

COVER, PAGE, PENCIL, TIP, SILVER = "leather_dark", "paint_cream", "paint_mustard", "wood_light", "silver_neon"


def build(mk):
    import math
    part = mk.part("WST_RM_Diary", (0, 0, 0))
    # tapas: prisma del contorno (esquina de afuera gastada en diagonal), 0,025 de espesor
    for s in (-1, 1):
        x0, x1 = 0.004 * s, 0.455 * s
        z0, z1 = -0.31, 0.31
        cut = 0.05
        if s > 0:
            outline = [(x0, z0), (x1 - cut, z0), (x1, z0 + cut), (x1, z1), (x0, z1)]
        else:
            outline = [(x0, z1), (x1 + cut, z1), (x1, z1 - cut), (x1, z0), (x0, z0)]
        mk.prism(part, outline, 0.025, COVER, plane="xz", center=(0, 0.0125, 0))
        # bloque de páginas: perfil del libro abierto (se hunde en el lomo), a lo largo de Z
        # hojas finas en el canto (0,075) que se arquean hacia el lomo (0,135) y se hunden en la canaleta
        prof = [(0.01, 0.022), (0.43, 0.022), (0.43, 0.075), (0.3, 0.097), (0.16, 0.125), (0.075, 0.135),
                (0.03, 0.105), (0.012, 0.05)]
        prof = [(s * x, y) for x, y in prof]
        mk.prism(part, prof if s > 0 else prof[::-1], 0.56, PAGE, plane="xy", center=(0, 0, 0))
    # lomo: medio caño abajo, entre las dos tapas
    mk.hull(part, [(x, y, z) for z in (-0.31, 0.31) for x, y in ((-0.03, 0.022), (0.03, 0.022), (0.02, 0.004),
                                                                  (-0.02, 0.004), (0.0, -0.0))], COVER)
    # mancha de plata en el canto de la página derecha: cuña que entra 0,006 arriba y en el costado
    # (huella ovalada: más angosta en las puntas)
    zc, D = -0.12, 0.006
    top_y = lambda x: 0.075 + (0.43 - x) * (0.097 - 0.075) / 0.13           # cara de arriba cerca del canto
    pts = []
    for dz, w in ((-0.045, 0.5), (-0.03, 0.9), (0.0, 1.0), (0.03, 0.9), (0.045, 0.5)):   # óvalo de una yema
        x_in = 0.43 - 0.05 * w
        pts += [(x_in, top_y(x_in) + 0.02, zc + dz), (0.45, top_y(0.43) + 0.02, zc + dz),
                (0.45, 0.075 - 0.022 * w, zc + dz)]
    pts += [(0.43 - 0.045, top_y(0.385) - D, zc), (0.43 - D, top_y(0.43) - D, zc), (0.43 - D, 0.075 - 0.018, zc)]
    mk.carve(part, SILVER, points=pts)

    # lápiz cruzado sobre la página derecha, apoyado en la curva
    a, b = (0.06, 0.154, -0.2), (0.37, 0.124, 0.14)            # apoyado en la loma de las hojas (0,135 cerca del lomo)
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d))
    d = [v / n for v in d]
    side = (-d[2], 0.0, d[0])
    sl = math.hypot(side[0], side[2])
    side = (side[0] / sl, 0.0, side[2] / sl)
    up = (d[1] * side[2] - d[2] * side[1], d[2] * side[0] - d[0] * side[2], d[0] * side[1] - d[1] * side[0])
    if up[1] < 0:
        up = tuple(-v for v in up)
    r = 0.024

    def hexring(c, rr):
        out = []
        for k in range(6):
            t = 2 * math.pi * (k + 0.5) / 6
            out.append(tuple(c[i] + side[i] * rr * math.cos(t) + up[i] * rr * math.sin(t) for i in range(3)))
        return out

    mk.hull(part, hexring(a, r) + hexring(b, r), PENCIL, detail=True)
    tip = tuple(b[i] + d[i] * 0.09 for i in range(3))
    mk.hull(part, hexring(tuple(b[i] - d[i] * 0.005 for i in range(3)), r * 0.97) + [tip], TIP, detail=True)

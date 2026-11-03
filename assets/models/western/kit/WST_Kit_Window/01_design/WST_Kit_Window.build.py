"""
Receta de WST_Kit_Window, las ventanas del kit modular (prompt 010, Bloques A + C).

Brief
- Silueta a 40 studs: marco oscuro con alféizar que sale y dintel con botaguas, cruz de la guillotina
  y cuatro vidrios claros; con postigos turquesa de persiana abiertos a los costados; la rota con un
  solo vidrio y puntas de vidrio en las esquinas.
- Medidas: hueco de 3 x 4 de Wall_Window (alféizar del hueco a y = 3 de la pared). Origen abajo al centro
  del hueco (y = 0 = alféizar del hueco, z = 0 = plano medio de la pared de 0,6). El marco forra el hueco
  (0,06), tapajuntas de 0,41 afuera y adentro, alféizar afuera (sale 0,32, inclinado), repisa adentro,
  dintel con botaguas.
- Guillotina: dos hojas de 0,12 (la de abajo adelante, z de -0,12 a 0; la de arriba atrás, de 0 a 0,12),
  montantes 0,18, travesaños de encuentro superpuestos en y = 1,92-2,08, parteluz de 0,1: la cruz.
  Todo eso es fixed_Frame; los vidrios Pane_1..Pane_4 (1 y 2 arriba, 3 y 4 abajo, de izquierda a derecha)
  son objetos aparte de 0,03, metidos 0,04 en la madera.
- Postigos (ShutterL, ShutterR): 1,83 x 3,9 x 0,12, paint_teal, dos paños de persiana; abiertos contra la
  pared. Pivote en el borde de afuera del tapajuntas (x = ±1,85, z = -0,46): girados 180° tapan justo el
  hueco (se tocan en el centro).
- Rota: el mismo marco con Pane_1 entero y tres puntas de vidrio (Shards) en las esquinas de los otros.
- Fila sobre X: Window_Sash en x = 0, Window_Shutters en x = 8, Window_Broken en x = 16. Nombres con el
  prefijo de la variante (como el resto del kit).
- Inferido: forro, tapajuntas, alféizar, repisa y botaguas; medidas de la guillotina; postigos abiertos
  como pose de reposo y su ancho (1,83 para que cierren); vidrios rotos como un objeto Shards.

Vueltas: 1) primera versión: el marco eran 23 cajas unidas (474 triángulos) y las persianas tocaban
justo los travesaños (caras degeneradas y 22 esquinas con normales desviadas en el GLB) · 2) cada hoja
de guillotina es una tabla con los dos huecos tallados y cada jamba un prisma en "[" (474 -> 384);
persianas encimadas 0,02 en los travesaños (0 normales desviadas).

Revisión
- Triángulos contra 250 por pieza: Sash 432 (marco 384 + 4 vidrios de 12), Shutters 924 (marco 378,
  vidrios 48, dos postigos de ~250 con dos paños de persiana en diente de sierra, bisagras), Broken 430
  (marco, un vidrio y tres puntas). Calidad primero: alféizar, botaguas, guillotina desfasada y persianas
  son lo que hace leer la ventana a 20-40 studs. El marco se repite en todas: ahí está el margen si hace
  falta bajar (sin repisa ni dintel de adentro, ~-60).
- Medidas: marco 4,2 x 5,02 (de y = -0,43, el faldón, a 4,59, el botaguas), z de -0,62 (alféizar) a 0,45
  (repisa). Postigos 1,83 x 3,9; cerrados cubren de x = -1,83 a 1,83 y se tocan en el centro.
- Aviso aceptado: "lowest point -0,43": el origen es el alféizar del hueco, el faldón cuelga abajo.
"""

DARK, GLASS, TEAL, LIGHT, IRON = "wood_dark", "glass", "paint_teal", "wood_light", "iron"
W, H = 3.0, 4.0


def frame(mk, name, cx):
    """Marco fijo con la cruz de la guillotina. Las piezas se enciman 0,01 (la unión las funde)."""
    p = mk.part(name, (cx, 0, 0))
    for s in (-1, 1):                                       # jamba: forro + tapajuntas de los dos lados, un prisma en "["
        jamb = [(1.44, -0.40), (1.855, -0.40), (1.855, -0.29), (1.5, -0.29), (1.5, 0.29), (1.855, 0.29),
                (1.855, 0.40), (1.44, 0.40)]
        mk.prism(p, [(cx + s * x, z) for x, z in jamb], 4.06, DARK, plane="xz", center=(0, 2.03, 0))
    mk.box(p, (cx, 3.97, 0), (2.98, 0.06, 0.6), DARK)                                      # forro de arriba
    mk.box(p, (cx, 4.25, -0.3575), (4.0, 0.52, 0.125), DARK)                               # dintel afuera
    mk.box(p, (cx, 4.2, 0.3475), (3.7, 0.42, 0.105), DARK)                                 # dintel adentro
    mk.box(p, (cx, 4.54, -0.395), (4.2, 0.1, 0.21), DARK, top=(1.0, 0.6), shift=(0, 0.04))  # botaguas
    mk.hull(p, [(cx + x, y, z) for x in (-1.95, 1.95) for y, z in
                ((0.08, -0.04), (0.0, -0.62), (-0.12, -0.62), (-0.12, -0.04))], DARK)      # alféizar inclinado
    mk.box(p, (cx, -0.27, -0.345), (3.4, 0.32, 0.11), DARK)                                # faldón
    mk.box(p, (cx, 0.0, 0.22), (3.6, 0.12, 0.46), DARK)                                    # repisa adentro
    # guillotina: cada hoja es una tabla con los dos huecos de los vidrios tallados (la de abajo adelante,
    # la de arriba atrás); montantes 0,2, parteluz 0,1, travesaños de encuentro superpuestos en y 1,92-2,08
    for z0, z1, ya, yb, ha, hb in ((-0.12, 0.0, 0.0, 2.03, 0.3, 1.92), (0.0, 0.12, 1.97, 3.95, 2.08, 3.77)):
        zc, zt = (z0 + z1) / 2, z1 - z0
        mk.box(p, (cx, (ya + yb) / 2, zc), (2.9, yb - ya, zt), DARK)
        for xa, xb in ((-1.25, -0.05), (0.05, 1.25)):
            mk.carve(p, DARK, points=mk.pts_box((cx + (xa + xb) / 2, (ha + hb) / 2, zc), (xb - xa, hb - ha, zt + 0.1)))
    mk.carve(p, LIGHT, prism=dict(profile=[(cx + 1.6, -0.2), (cx + 1.98, -0.2), (cx + 1.98, 0.1), (cx + 1.75, 0.1)],
                                  depth=0.2, plane="xy", center=(0, 0, -0.6)))             # punta del alféizar gastada
    return p


PANES = {  # (x0, x1, y0, y1, z): cada vidrio metido 0,04 en la madera que lo rodea
    "Pane_1": (-1.29, -0.01, 2.04, 3.81, 0.06), "Pane_2": (0.01, 1.29, 2.04, 3.81, 0.06),
    "Pane_3": (-1.29, -0.01, 0.26, 1.96, -0.06), "Pane_4": (0.01, 1.29, 0.26, 1.96, -0.06),
}


def pane(mk, name, cx, key):
    x0, x1, y0, y1, z = PANES[key]
    p = mk.part(name, (cx, 0, 0))
    mk.box(p, (cx + (x0 + x1) / 2, (y0 + y1) / 2, z), (x1 - x0, y1 - y0, 0.03), GLASS)
    return p


def shutter(mk, name, cx, s):
    """Postigo abierto contra la pared del lado s (-1 izquierda, +1 derecha); pivote en x = s*1,85."""
    hx, zc, T = cx + s * 1.85, -0.46, 0.12                 # la espalda toca el frente del tapajuntas (-0,40)
    p = mk.part(name, (hx, 0, zc))
    a, b = hx + s * 0.02, hx + s * 1.85                     # de la bisagra hacia afuera
    lo, hi = min(a, b), max(a, b)
    y0, y1, ym = 0.1, 4.0, 2.05
    for x in (lo + 0.1, hi - 0.1):
        mk.box(p, (x, (y0 + y1) / 2, zc), (0.2, y1 - y0, T), TEAL)                         # montantes
    for y, h in ((y0 + 0.13, 0.26), (ym, 0.22), (y1 - 0.13, 0.26)):
        mk.box(p, ((lo + hi) / 2, y, zc), (hi - lo - 0.02, h, T), TEAL)                    # travesaños
    for ya, yb in ((y0 + 0.24, ym - 0.09), (ym + 0.09, y1 - 0.24)):                       # dos paños de persiana (se meten 0,02 en los travesaños)
        n = 6
        prof = [(zc + 0.035, ya)]
        for k in range(n):
            yk = ya + (yb - ya) * k / n
            prof += [(zc - 0.045, yk + 0.02), (zc + 0.035, yk + (yb - ya) / n)]
        prof += [(zc + 0.05, yb), (zc + 0.05, ya)]
        mk.prism(p, prof, hi - lo - 0.3, TEAL, plane="zy", center=((lo + hi) / 2, 0, 0))
    for y in (0.6, 3.5):                                                                   # bisagras
        mk.box(p, (hx + s * 0.25, y, zc - 0.07), (0.5, 0.1, 0.03), IRON, detail=True)
        mk.cyl(p, (hx, y, zc), 0.06, 0.22, IRON, axis="y", sides=6, detail=True)       # nudo: toca el tapajuntas
    xo = hi if s > 0 else lo                                                               # canto de afuera
    mk.carve(p, LIGHT, prism=dict(profile=[(xo + s * 0.1, y1 + 0.1), (xo - s * 0.4, y1 + 0.1), (xo + s * 0.1, y1 - 0.45)],
                                  depth=0.4, plane="xy", center=(0, 0, zc)))               # esquina rota arriba
    return p


def build(mk):
    # ---------------- Window_Sash ----------------
    frame(mk, "Window_Sash_fixed_Frame", 0.0)
    for k in PANES:
        pane(mk, f"Window_Sash_{k}", 0.0, k)

    # ---------------- Window_Shutters ----------------
    frame(mk, "Window_Shutters_fixed_Frame", 8.0)
    for k in PANES:
        pane(mk, f"Window_Shutters_{k}", 8.0, k)
    shutter(mk, "Window_Shutters_ShutterL", 8.0, -1)
    shutter(mk, "Window_Shutters_ShutterR", 8.0, 1)

    # ---------------- Window_Broken: un vidrio entero y tres puntas en las esquinas ----------------
    frame(mk, "Window_Broken_fixed_Frame", 16.0)
    pane(mk, "Window_Broken_Pane_1", 16.0, "Pane_1")
    sh = mk.part("Window_Broken_Shards", (16.0, 0, 0))
    shards = [  # (perfil del triángulo dentado en la esquina, z del vidrio)
        ([(0.01, 3.81), (0.75, 3.81), (0.5, 3.55), (0.38, 3.62), (0.01, 3.05)], 0.06),       # Pane_2, arriba a la izquierda
        ([(-1.29, 0.26), (-0.55, 0.26), (-0.8, 0.5), (-0.95, 0.44), (-1.29, 1.1)], -0.06),  # Pane_3, abajo a la izquierda
        ([(1.29, 0.26), (1.29, 0.95), (1.05, 0.62), (0.95, 0.7), (0.55, 0.26)], -0.06),     # Pane_4, abajo a la derecha
    ]
    for prof, z in shards:
        mk.prism(sh, [(16.0 + x, y) for x, y in prof], 0.03, GLASS, plane="xy", center=(0, 0, z))

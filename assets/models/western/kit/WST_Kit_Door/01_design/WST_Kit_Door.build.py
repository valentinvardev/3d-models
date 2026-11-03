"""
Receta de WST_Kit_Door, las puertas del kit modular (prompt 009, Bloques A + C).

Brief
- Silueta a 40 studs: puerta de tablas con la Z oscura y bisagras largas de hierro; puerta de almacén
  turquesa con vidrio arriba; puertas vaivén del saloon a media altura con persianas; marco oscuro con
  dintel y botaguas.
- Medidas: el hueco de Wall_Door es 4 x 7,5. Door_Frame lo forra con jambas de 0,06 (luz 3,88 x 7,44)
  y lo enmarca afuera y adentro con tapajuntas de 0,5 y un dintel con botaguas. Las puertas van adentro
  del forro: 3,84 x 7,38 (0,02 de luz a cada lado y 0,04 abajo), 0,4 de espesor (Bloque C: fragmentos de
  0,4 como mínimo). Las hojas del saloon: 1,93 x 3,5, abajo a 2,0, 0,2 de espesor (no se rompen).
- Orígenes: cada puerta en el pie de su canto de bisagras (x = 0 del canto, y = 0 piso, z = 0 plano
  medio de la puerta cerrada); la bisagra a la izquierda (-X). Para ponerla en Wall_Door: origen en
  x = -1,92 del hueco. Saloon: DoorLeft en su canto de afuera (x = -1,94 del hueco, y = 2,0) y DoorRight en
  x = +1,94. Door_Frame: abajo al centro del hueco (y = 0, z = 0 = plano medio de la pared).
- Fila sobre X: Door_Plank con la bisagra en x = 0, Door_Panel en x = 6, Saloon centrado en x = 14,
  Frame centrado en x = 20.
- Piezas y nombres (prefijo de variante, como el resto del kit): Door_Plank_frag01..04 (tablas
  verticales: 2 + 1 + 1 + 1; los travesaños y la diagonal se cortan donde se separan las tablas),
  Door_Panel_frag01..04 (montante de bisagras, montante de la cerradura, zócalo + tablero + travesaño
  de la cerradura, travesaño de arriba) + Door_Panel_Glass, Door_Saloon_DoorLeft/DoorRight,
  Door_Frame_fixed_Frame.
- Inferido: forro de 0,06 y medidas de las puertas, espesores, alturas de travesaños y Z, forma de la
  curva del saloon (baja hacia el centro), colores de la puerta de saloon (marco wood_mid, persianas
  wood_light sobre fondo wood_dark), tablero inferior wood_mid en la de almacén, picaporte de bronce.

Vueltas: 1) primera versión: el marco con cajas que se tocaban justo (4 bordes con giro invertido) y el
tirador del pestillo del mismo ancho que su base (caras coplanares) · 2) piezas del marco encimadas 0,01,
tirador más angosto; saloon con rebaje rectangular (el que seguía la curva dejaba un triángulo vacío
arriba) y la pintura gastada del zócalo como franja dentada (parecía un montículo).

Revisión
- Triángulos contra 250 por pieza: Plank 400 (4 fragmentos con Z, bisagras de pletina con nudo y
  pestillo), Panel 280 + vidrio 12, Saloon 328 (2 hojas de 164 con 5 listones), Frame 212.
  Calidad primero: el herraje es lo que hace leer cada puerta.
- Medidas: Plank y Panel 3,84 x 7,38 x 0,4 (el herraje sale hasta 0,4 adelante); hojas del saloon
  1,93 x 3,5 (-3,5 % del ancho del prompt por el forro del marco), abajo en y = 2,0; Frame 5,6 x 8,31.
- Fragmentos: Plank 40/20/20/20 % (dos tablas del lado de las bisagras), Panel 24/24/43/10 %; todos de
  0,4 o más de espesor. El vidrio (Glass) se mete 0,05 en el marco: no es fragmento (se rompe como VFX).
- Normales del GLB final: 0 esquinas desviadas.
"""

import math

PLANK, DARK, IRON, LIGHT, TEAL, GLASS, BRASS = "wood_mid", "wood_dark", "iron", "wood_light", "paint_teal", "glass", "brass"
DW, DH, DT = 3.84, 7.38, 0.4         # puerta que se rompe
Y0 = 0.04                             # luz abajo
FZ = -DT / 2                          # cara de afuera de la puerta (-0,2)


def clip_poly(poly, a, b):
    """Recorta un polígono convexo (x, y) entre x = a y x = b (Sutherland-Hodgman en dos planos)."""
    def cut(pts, x0, keep_right):
        out = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            pin = (p[0] >= x0) if keep_right else (p[0] <= x0)
            qin = (q[0] >= x0) if keep_right else (q[0] <= x0)
            if pin:
                out.append(p)
            if pin != qin:
                t = (x0 - p[0]) / (q[0] - p[0])
                out.append((x0, p[1] + t * (q[1] - p[1])))
        return out
    return cut(cut(poly, a, True), b, False)


def door_plank(mk, ox):
    """Puerta de tablas verticales con Z, bisagras de pletina y pestillo. 4 fragmentos por tablas."""
    pw = DW / 5
    groups = [(0, 2), (2, 3), (3, 4), (4, 5)]               # tablas de cada fragmento
    rails = [(1.05, 0.55), (6.25, 0.55)]                    # (y centro, alto) de los travesaños
    diag = [(0.35, 1.05 + 0.1), (0.35, 1.05 + 0.75), (DW - 0.45, 6.25 - 0.1), (DW - 0.45, 6.25 - 0.75)]
    for i, (p0, p1) in enumerate(groups):
        a, b = p0 * pw, p1 * pw
        part = mk.part(f"Door_Plank_frag0{i + 1}", (ox, 0, 0))
        top = DH + Y0 - (0.06 if i == 2 else 0.0)                          # una tabla un poco más corta
        mk.box(part, (ox + (a + b) / 2, (Y0 + top) / 2, 0), (b - a, top - Y0, DT), PLANK)
        for y, h in rails:                                                  # travesaños de la Z (afuera)
            ra, rb = max(a, 0.12), min(b, DW - 0.12)
            mk.box(part, (ox + (ra + rb) / 2, y, FZ - 0.05), (rb - ra, h, 0.12), DARK)
        d = clip_poly(diag, a, b)
        if len(d) >= 3:
            mk.prism(part, [(ox + x, y) for x, y in d], 0.12, DARK, plane="xy", center=(0, 0, FZ - 0.05))
        mk.carve(part, DARK, points=mk.pts_box((ox + a - 0.5, 0, 0), (0.2, 0.2, 0.2)))   # sin efecto: dispara la unión
        for k in range(p0 + 1, p1):                                         # juntas entre tablas del fragmento
            x = k * pw
            for d_ in (-0.025, 0.025):
                mk.slice(part, (ox + x + d_, 0, 0), (1, 0, 0))
            for zc in (FZ, -FZ):
                mk.paint(part, DARK, box=((ox + x, 4, zc), (0.052, 9, 0.02)))
        if i == 1:                                                          # esquina rota abajo
            mk.carve(part, LIGHT, prism=dict(profile=[(ox + a - 0.05, Y0 - 0.05), (ox + a + 0.45, Y0 - 0.05),
                                                      (ox + a - 0.05, Y0 + 0.5)], depth=1.0, plane="xy"))
        if i == 0:                                                          # bisagras de pletina + nudos
            for y, _ in rails:
                strap = [(0.0, y - 0.11), (1.3, y - 0.05), (1.42, y), (1.3, y + 0.05), (0.0, y + 0.11)]
                mk.prism(part, [(ox + x, yy) for x, yy in strap], 0.05, IRON, plane="xy",
                         center=(0, 0, FZ - 0.125), detail=True)
                mk.cyl(part, (ox + 0.0, y, FZ - 0.08), 0.075, 0.42, IRON, axis="y", sides=6, detail=True)
        if i == 3:                                                          # pestillo: tirador y traba
            hx = DW - 0.38
            mk.box(part, (ox + hx, 3.55, FZ - 0.04), (0.1, 0.5, 0.1), IRON, detail=True)
            mk.hull(part, [(ox + hx + dx, 3.55 + dy, FZ - dz) for dx in (-0.035, 0.035)
                           for dy, dz in ((-0.2, 0.05), (0.2, 0.05), (-0.12, 0.2), (0.12, 0.2))], IRON, detail=True)
            mk.box(part, (ox + DW - 0.25, 3.95, FZ - 0.03), (0.42, 0.08, 0.08), IRON, detail=True)


def door_panel(mk, ox):
    """Puerta de almacén: marco turquesa, tablero de madera abajo, vidrio arriba (objeto Glass)."""
    SW, BR, LR0, LR1, TR = 0.55, 0.8, 3.0, 3.5, 6.8          # montantes, zócalo, travesaño de cerradura, arriba
    yt = Y0 + DH
    f1 = mk.part("Door_Panel_frag01", (ox, 0, 0))            # montante de bisagras
    mk.box(f1, (ox + SW / 2, (Y0 + yt) / 2, 0), (SW, DH, DT), TEAL)
    for y in (1.0, 3.9, 6.6):
        mk.cyl(f1, (ox, y, FZ + 0.02), 0.06, 0.36, IRON, axis="y", sides=6, detail=True)
    f2 = mk.part("Door_Panel_frag02", (ox, 0, 0))            # montante de la cerradura
    mk.box(f2, (ox + DW - SW / 2, (Y0 + yt) / 2, 0), (SW, DH, DT), TEAL)
    for z, s in ((FZ, -1), (-FZ, 1)):                         # picaporte de bronce a los dos lados
        mk.box(f2, (ox + DW - 0.3, LR0 + 0.25, z + s * 0.015), (0.14, 0.42, 0.04), BRASS, detail=True)
        mk.ball(f2, (ox + DW - 0.3, LR0 + 0.3, z + s * 0.1), 0.08, BRASS, subdiv=1, detail=True)
    f3 = mk.part("Door_Panel_frag03", (ox, 0, 0))            # zócalo + tablero + travesaño de la cerradura
    ia, ib = SW, DW - SW
    mk.box(f3, (ox + DW / 2, Y0 + BR / 2, 0), (ib - ia, BR, DT), TEAL)
    mk.box(f3, (ox + DW / 2, (LR0 + LR1) / 2, 0), (ib - ia, LR1 - LR0, DT), TEAL)
    pc, pw, ph = (ox + DW / 2, (Y0 + BR + LR0) / 2), ib - ia, LR0 - Y0 - BR
    mk.box(f3, (pc[0], pc[1], 0), (pw, ph + 0.1, 0.2), PLANK)                                      # tablero
    mk.hull(f3, [(pc[0] + sx * w / 2, pc[1] + sy * h / 2, z) for w, h, zz in ((pw - 0.4, ph - 0.4, 0.09), (pw - 0.75, ph - 0.75, 0.15))
                 for z in (-zz, zz) for sx in (-1, 1) for sy in (-1, 1)], PLANK)                   # campo levantado
    chip = [(0.9, -0.1), (2.5, -0.1), (2.42, 0.07), (2.2, 0.12), (1.95, 0.06), (1.7, 0.13), (1.4, 0.07), (1.15, 0.11), (0.95, 0.05)]
    mk.carve(f3, PLANK, prism=dict(profile=[(ox + x, Y0 + y) for x, y in chip], depth=0.3, plane="xy",
                                   center=(0, 0, FZ - 0.115)))                                       # pintura gastada abajo
    f4 = mk.part("Door_Panel_frag04", (ox, 0, 0))            # travesaño de arriba
    mk.box(f4, (ox + DW / 2, (TR + yt) / 2, 0), (ib - ia, yt - TR, DT), TEAL)
    g = mk.part("Door_Panel_Glass", (ox, 0, 0))              # vidrio: se mete 0,05 en el marco
    mk.box(g, (ox + DW / 2, (LR1 + TR) / 2, 0), (ib - ia + 0.1, TR - LR1 + 0.1, 0.06), GLASS)
    for part in (f1, f2, f4):                                 # disparar la unión en las que no tallan
        mk.carve(part, TEAL, points=mk.pts_box((ox - 2, 0, 0), (0.1, 0.1, 0.1)))


def door_saloon(mk, cx):
    """Puertas vaivén: dos hojas con persianas (5 listones salientes) y borde de arriba curvo."""
    LW, Yb, H, T = 1.93, 2.0, 3.5, 0.2
    for name, s in (("Door_Saloon_DoorLeft", -1), ("Door_Saloon_DoorRight", 1)):
        px = cx + s * 1.94                                   # canto de afuera = bisagra
        part = mk.part(name, (px, Yb, 0))
        X = lambda u: px - s * u                             # u = distancia desde la bisagra hacia el centro
        top = lambda u: Yb + H - 0.75 * (u / LW) ** 1.6      # baja hacia el centro
        n = 6
        outline = [(X(0), Yb)] + [(X(LW * i / n), top(LW * i / n)) for i in range(n + 1)] + [(X(LW), Yb)]
        outline = outline if s < 0 else list(reversed(outline))
        mk.prism(part, outline, T, PLANK, plane="xy", center=(0, 0, 0))                    # marco
        inner_a, inner_b, ib0, ib1 = 0.25, LW - 0.25, Yb + 0.4, None
        ib1 = top(inner_b) - 0.3
        win = [(X(inner_a), ib0), (X(inner_b), ib0), (X(inner_b), ib1), (X(inner_a), ib1)]   # travesaño de arriba macizo
        mk.carve(part, DARK, prism=dict(profile=win, depth=0.12, plane="xy", center=(0, 0, -0.07)))   # rebaje
        mk.carve(part, DARK, prism=dict(profile=win, depth=0.12, plane="xy", center=(0, 0, 0.07)))
        span = ib1 - ib0
        for k in range(5):                                   # listones salientes
            y = ib0 + span * (k + 0.5) / 5
            mk.box(part, ((X(inner_a) + X(inner_b)) / 2, y, 0), (inner_b - inner_a + 0.06, span / 5 * 0.55, 0.16), LIGHT,
                   rot=(-18, 0, 0), detail=True)
        for y in (Yb + 0.5, Yb + H - 0.6):                   # bisagras de resorte
            mk.cyl(part, (px, y, 0), 0.07, 0.45, IRON, axis="y", sides=6, detail=True)


def door_frame(mk, cx):
    """Marco fijo: forro del hueco, tapajuntas afuera y adentro, dintel con botaguas."""
    part = mk.part("Door_Frame_fixed_Frame", (cx, 0, 0))
    # las piezas se enciman 0,01 en vez de tocarse justo (caras y bordes que coinciden rompían la unión)
    for s in (-1, 1):
        mk.box(part, (cx + s * 1.97, 3.735, 0), (0.06, 7.47, 0.6), DARK)                  # forro de las jambas
        for z in (-0.345, 0.345):
            mk.box(part, (cx + s * 2.19, 3.76, z), (0.52, 7.52, 0.11), DARK)              # tapajuntas
    mk.box(part, (cx, 7.47, 0), (3.98, 0.06, 0.6), DARK)                                  # forro de arriba
    mk.box(part, (cx, 7.85, -0.3575), (5.4, 0.7, 0.125), DARK)                            # dintel afuera
    mk.box(part, (cx, 7.85, 0.3475), (4.9, 0.7, 0.105), DARK)                             # dintel adentro
    mk.box(part, (cx, 8.25, -0.395), (5.6, 0.12, 0.21), DARK, top=(1.0, 0.6), shift=(0, 0.04))  # botaguas
    mk.carve(part, LIGHT, prism=dict(profile=[(cx - 2.5, -0.1), (cx - 2.1, -0.1), (cx - 2.5, 0.42)], depth=0.3,
                                     plane="xy", center=(0, 0, -0.35)))                    # tapajuntas comido abajo


def build(mk):
    door_plank(mk, 0.0)
    door_panel(mk, 6.0)
    door_saloon(mk, 14.0)
    door_frame(mk, 20.0)

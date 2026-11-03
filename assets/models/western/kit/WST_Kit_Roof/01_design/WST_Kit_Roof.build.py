"""
Receta de WST_Kit_Roof, los techos del kit modular (prompt 012, Bloques A + C).

Brief
- Silueta a 40 studs: techo plano negro con reborde (ahí se paran los pistoleros); techo a dos aguas de
  35° con hileras de tejuelas en franjas alternadas oscuro / medio y cumbrera; hastial triangular de tablas
  con ventilación; chimenea de ladrillo con remate; la versión quemada con agujeros.
- Fila sobre X (cada pieza con su origen abajo al centro, en y = 0 = tope de la pared de 10):
  Roof_Flat x = 0, Roof_Gable x = 12, Roof_Gable_Charred x = 24, Roof_GableEnd x = 40, Roof_Chimney x = 52.
- Roof_Flat (4 fragmentos, franjas de 8 x 2 a lo largo de las juntas del papel): losa de 8 x 8 x 0,4
  (arriba en y = 0,4), papel alquitranado (iron) con juntas coal cada 1, canto wood_dark, un parche y una
  rasgadura. Reborde de 0,6 como pieza fija aparte (Roof_Flat_fixed_Lip), apoyado arriba de la losa en el
  borde de atrás, con el origen en el centro del módulo: girándolo se pone en el borde que dé afuera.
- Roof_Gable (6 fragmentos: 3 por faldón, cortados por las juntas de las hileras): cumbrera a lo largo de
  X (8, calza con el módulo vecino), luz 16 (z de -8 a 8) a 35° (sube 5,60), alero de 0,6 (bajo la pared:
  el borde llega a z = ±8,6). Faldones de 0,4 con 14 hileras de 0,75 escalonadas 0,06, alternando
  wood_dark / wood_mid; abajo entablonado wood_mid; cumbrera y cabeza del alero wood_dark.
- Roof_Gable_Charred: el mismo techo con wood_charred / wood_dark, tres agujeros quemados (bordes coal).
- Roof_GableEnd (4 fragmentos): hastial de tablas de 16 de base y 5,60 de alto (mismo perfil y tabla de
  remate que la falsa fachada, paint_cream), 0,6 de espesor, ventilación con 3 tablillas cerca del vértice.
  Sus bordes siguen la cara de abajo del techo a dos aguas.
- Roof_Chimney (3 fragmentos): 1,6 x 1,6 x 4 de ladrillo (paint_red, juntas stone_grey pintadas cada
  0,35), cornisa de ladrillo, losa de remate stone_grey y boca coal. Se parte por hiladas en escalón.
- Nombres: <Pieza>_fragNN / _fixed_Lip (como el resto del kit).
- Inferido: papel alquitranado en iron, reborde como pieza aparte, alero de 0,6, espesor 0,4 (regla de
  fragmentos), ancho de hilera, ventilación del hastial, cornisa y losa de la chimenea.

Vueltas: 1) al releer antes de construir: el corte en escalón de la chimenea giraba alrededor del origen
del mundo, el giro de los agujeros quemados tenía el signo al revés y cada franja terminaba arriba en el
espesor grueso (el escalón tiene que ser de la franja de arriba) · construida a la primera, revisión de
capturas sin cambios.

Revisión
- Triángulos contra 500 por pieza: Flat 224 + reborde 28, Gable 264, Gable_Charred 428 (agujeros), GableEnd
  416 (tablas en escalera y ventilación), Chimney 360. Todo debajo del tope.
- Medidas: Flat 8 x 0,4 x 8 (reborde hasta 1,08); Gable 8 de largo, 17,7 de luz con los aleros (16 + 0,6 de
  alero por lado + el espesor), alto 6,32 con la cumbrera, y el alero baja a -0,42 (por eso el aviso de
  "lowest point"); GableEnd 16 x 5,60 x 0,61; Chimney 1,94 x 3,97 x 1,94 (cuerpo de 1,6).
- Fragmentos: Flat 4 x 23 %, Gable 6 x ~17 %, GableEnd 33/32/18/17 %, Chimney 35/35/30 %; todos de 0,4 o más.
- La chimenea tiene la base plana en y = 0: se hunde en el techo (atraviesa el faldón).
- Normales del GLB final: 0 esquinas desviadas.
"""

import math

DARK, MID, LIGHT, PAINT, IRON, COAL, CHAR, RED, GREY = (
    "wood_dark", "wood_mid", "wood_light", "paint_cream", "iron", "coal", "wood_charred", "paint_red", "stone_grey")
PITCH = math.radians(35)
RISE = 8 * math.tan(PITCH)                 # 5,6017
EAVE = 8.6                                 # el alero llega a z = ±8,6
T = 0.4                                    # espesor del faldón


def clean(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    return out


# ------------------------------------------------------------------------------------- techo plano
def roof_flat(mk, ox):
    for f in range(4):
        za, zb = -4.0 + 2 * f, -2.0 + 2 * f
        p = mk.part(f"Roof_Flat_frag0{f + 1}", (ox, 0, 0))
        mk.box(p, (ox, 0.2, (za + zb) / 2), (8.0, 0.4, 2.0), IRON)
        mk.paint(p, DARK, box=((ox, 0.2, (za + zb) / 2), (8.2, 0.3, 2.2)))           # cantos de tablas (las caras de costado)
        for zc in ((za + zb) / 2, za + 0.0, zb - 0.0):                                  # juntas del papel cada 1
            for d in (-0.03, 0.03):
                if za < zc + d < zb:
                    mk.slice(p, (ox, 0, zc + d), (0, 0, 1))
            mk.paint(p, COAL, box=((ox, 0.4, zc), (8.2, 0.02, 0.062)))
        if f == 1:                                                                      # parche de papel nuevo
            mk.carve(p, COAL, prism=dict(profile=[(ox - 2.6, -1.7), (ox - 1.2, -1.75), (ox - 1.1, -0.6), (ox - 2.5, -0.55)],
                                         depth=0.06, plane="xz", center=(0, 0.4, 0)))
        elif f == 2:                                                                    # rasgadura: se ve la tabla
            mk.carve(p, MID, prism=dict(profile=[(ox + 1.2, 0.5), (ox + 2.6, 0.7), (ox + 2.2, 1.0), (ox + 1.7, 0.85),
                                                 (ox + 1.4, 1.1)], depth=0.08, plane="xz", center=(0, 0.4, 0)))
        else:
            mk.carve(p, IRON, points=mk.pts_box((ox, -3, 0), (0.1, 0.1, 0.1)))
    lip = mk.part("Roof_Flat_fixed_Lip", (ox, 0, 0))                                    # reborde: girarlo al borde que haga falta
    mk.box(lip, (ox, 0.7, 3.85), (8.0, 0.6, 0.3), MID)
    mk.box(lip, (ox, 1.015, 3.83), (8.0, 0.13, 0.34), DARK)
    mk.carve(lip, MID, points=mk.pts_box((ox, -3, 0), (0.1, 0.1, 0.1)))


# -------------------------------------------------------------------------------- techo a dos aguas
U = (-math.cos(PITCH), math.sin(PITCH))     # hacia la cumbrera, en (z, y), faldón de +z
N = (math.sin(PITCH), math.cos(PITCH))      # normal hacia afuera
E = (EAVE, RISE * (1 - EAVE / 8))           # borde del alero en la cara de abajo
L = EAVE / math.cos(PITCH)                  # largo del faldón por la cara de abajo
W = 0.75                                    # hilera
ROWS = 14


def at(s, t):
    return (E[0] + s * U[0] + t * N[0], E[1] + s * U[1] + t * N[1])


def band(s0, s1, ridge):
    """Perfil (z, y) de una franja del faldón de +z entre s0 y s1 (s desde el alero). ridge: corta en z = 0."""
    pts = [at(s0, 0.0)]
    if ridge:
        pts += [(0.0, at(L, 0.0)[1])]
        t_top = T + 0.06
        pts += [(0.0, at(L, 0.0)[1] + t_top / math.cos(PITCH))]
    else:
        pts += [at(s1, 0.0), at(s1, T)]                          # punta fina de la última hilera
    j1 = int(round(s1 / W)) if not ridge else ROWS
    for j in range(j1 - 1, int(round(s0 / W)) - 1, -1):          # de arriba hacia el alero
        sa, sb = j * W, min((j + 1) * W, L)
        if ridge and j == ROWS - 1:
            pts += [at(sa, T + 0.06)]
            continue
        pts += [at(sb, T), at(sa, T + 0.06)]
    return clean(pts)


def gable(mk, name, ox, mats, holes=()):
    """Techo a dos aguas: 3 franjas por faldón. mats = (hilera par, hilera impar, abajo, bordes de agujeros, cumbrera)."""
    splits = [(0.0, 5 * W, False), (5 * W, 10 * W, False), (10 * W, L, True)]
    n = 0
    for side in (1, -1):                                          # +z primero, después -z (espejado)
        for s0, s1, ridge in splits:
            n += 1
            p = mk.part(f"{name}_frag0{n}", (ox, 0, 0))
            prof = [(side * z, y) for z, y in band(s0, s1, ridge)]
            mk.prism(p, prof, 8.0, mats[0], plane="zy", center=(ox, 0, 0))
            if ridge:                                             # media cumbrera
                yr = at(L, 0)[1] + (T + 0.06) / math.cos(PITCH)
                ys = lambda z: yr - z * math.tan(PITCH)           # superficie del faldón
                mk.hull(p, [(ox + x, y, side * z) for x in (-4, 4) for z, y in
                            ((0.0, yr + 0.16), (0.0, yr - 0.2), (0.42, ys(0.42) - 0.2), (0.42, ys(0.42) + 0.12))],
                        mats[4])
            for j in range(int(round(s0 / W)), int(round(s1 / W)) if not ridge else ROWS):   # hileras alternadas
                if j % 2:
                    zc, yc = at((j + 0.5) * W, T + 0.03)
                    mk.paint(p, mats[1], box=((ox, yc, side * zc), (8.2, 0.12, 0.12)))
            zc, yc = at((s0 + s1) / 2 if not ridge else (s0 + L) / 2, 0.0)
            mk.paint(p, mats[2], box=((ox, yc, side * zc), (8.2, 0.05, 0.05)))              # entablonado de abajo
            if s0 == 0.0:
                zc, yc = at(0.0, T / 2)
                mk.paint(p, DARK if mats[0] != CHAR else CHAR, box=((ox, yc, side * zc), (8.2, 0.3, 0.3)))   # cabeza del alero
            hit = False
            for (hs, hx, hw, hside) in holes:                     # agujeros quemados
                if hside == side and s0 <= hs < s1:
                    zc, yc = at(hs, T / 2)
                    jag = [(-hw, -0.5), (-0.3, -0.62), (0.15, -0.45), (hw, -0.55), (hw * 0.8, 0.0), (hw, 0.5),
                           (0.2, 0.62), (-0.25, 0.4), (-hw, 0.55), (-hw * 0.7, 0.05)]
                    mk.carve(p, mats[3], prism=dict(profile=[(hx + a, b) for a, b in jag], depth=1.4, plane="xz",
                                                    center=(ox, yc, side * zc), rot=(side * 35, 0, 0)))
                    hit = True
            if not hit:
                mk.carve(p, mats[0], points=mk.pts_box((ox, -5, 0), (0.1, 0.1, 0.1)))      # une los cascos


# ------------------------------------------------------------------------------------------- hastial
GE_NK = 8


def ge_course(k):
    return (0.0, 0.4) if k == 0 else (0.4 + 0.8 * (k - 1), 0.4 + 0.8 * k)


def ge_profile(k0, k1):
    pts = []
    for k in range(k0, k1 + 1):
        y0, y1 = ge_course(k)
        zf = (lambda y: -0.31) if k == 0 else (lambda y, y0=y0: -0.27 + 0.06 * (y - y0) / 0.8)
        pts += [(zf(y0), y0), (zf(y1), y1)]
    return clean(pts + [(0.3, ge_course(k1)[1]), (0.3, ge_course(k0)[0])])


def gable_end(mk, ox):
    frags = {
        "frag01": {0: (-8, 0.4), 1: (-8, -0.2), 2: (-8, 0.3), 3: (-8, -3.2)},
        "frag02": {0: (0.4, 8), 1: (-0.2, 8), 2: (0.3, 8), 3: (2.8, 8)},
        "frag03": {3: (-3.2, 0.1), 4: (-8, -0.2), 5: (-8, 0.2), 6: (-8, -0.1), 7: (-8, 0.1)},
        "frag04": {3: (0.1, 2.8), 4: (-0.2, 8), 5: (0.2, 8), 6: (-0.1, 8), 7: (0.1, 8)},
    }
    sil = [(ox - 8, 0.0), (ox, RISE), (ox + 8, 0.0), (ox + 9, -0.6), (ox + 9, 8), (ox - 9, 8), (ox - 9, -0.6)]
    vent = (3.15, 4.05)
    for fname, iv in frags.items():
        ks = sorted(iv)
        k0, k1 = ks[0], ks[-1]
        xmin, xmax = min(a for a, _ in iv.values()), max(b for _, b in iv.values())
        p = mk.part(f"Roof_GableEnd_{fname}", (ox, 0, 0))
        mk.prism(p, ge_profile(k0, k1), xmax - xmin, PAINT, plane="zy", center=(ox + (xmin + xmax) / 2, 0, 0))
        ybot, ytop = ge_course(k0)[0] - 0.5, ge_course(k1)[1] + 0.5
        for side in (1, -1):                                      # corte en escalera
            edge = xmax if side > 0 else xmin
            xs = [(iv[k][1] if side > 0 else iv[k][0]) for k in ks]
            if all(abs(x - edge) < 1e-6 for x in xs):
                continue
            pts = []
            for k, x in zip(ks, xs):
                if abs(x - edge) < 1e-6:
                    x = edge + side * 0.5
                y0, y1 = ge_course(k)
                pts += [(ox + x, ybot if k == k0 else y0), (ox + x, ytop if k == k1 else y1)]
            pts += [(ox + edge + side, ytop), (ox + edge + side, ybot)]
            mk.carve(p, LIGHT, prism=dict(profile=clean(pts), depth=2.0, plane="xy"))
        mk.carve(p, DARK, prism=dict(profile=sil, depth=2.0, plane="xy"))                       # triángulo
        if k1 >= 4:                                                                             # ventilación
            mk.carve(p, COAL, points=mk.pts_box((ox, sum(vent) / 2, -0.25), (1.2, vent[1] - vent[0], 0.3)))
        mk.paint(p, DARK, box=((ox, 0.2, -0.31), (16.2, 0.4, 0.02)))                            # tabla de remate
        mk.paint(p, MID, box=((ox, 3.0, 0.3), (16.2, 6.2, 0.02)))                               # adentro
        for k in range(1, GE_NK):
            s = ge_course(k)[0]
            if ge_course(k0)[0] + 0.05 < s <= ge_course(k1)[1]:
                mk.slice(p, (ox, s - 0.06, 0), (0, 1, 0))
                if k > 1:
                    mk.paint(p, DARK, box=((ox, s - 0.03, -0.25), (16.2, 0.062, 0.1)))
        if k1 >= 4:                                                                             # tablillas de la ventilación
            for i in range(3):
                y = vent[0] + 0.18 + 0.28 * i
                a, b = max(xmin, -0.6), min(xmax, 0.6)
                a = max(a, iv.get(4, (xmin, xmax))[0] if y < 3.6 else iv.get(5, (xmin, xmax))[0])
                b = min(b, iv.get(4, (xmin, xmax))[1] if y < 3.6 else iv.get(5, (xmin, xmax))[1])
                if b - a > 0.05:
                    mk.box(p, (ox + (a + b) / 2, y, -0.18), (b - a, 0.08, 0.16), DARK, rot=(-25, 0, 0), detail=True)


# ------------------------------------------------------------------------------------------ chimenea
def chimney(mk, ox):
    def stair(h, up):
        pts = [(-1.2, h + 0.18), (-0.45, h + 0.18), (-0.45, h - 0.17), (0.3, h - 0.17), (0.3, h + 0.18), (1.2, h + 0.18)]
        far = h + (10 if up else -10)
        return pts + [(1.2, far), (-1.2, far)]                   # local: se gira alrededor del eje de la chimenea

    spans = [(0.0, 1.6), (1.2, 3.0), (2.6, 4.0)]
    cuts = (1.4, 2.8)
    for i, (y0, y1) in enumerate(spans):
        p = mk.part(f"Roof_Chimney_frag0{i + 1}", (ox, 0, 0))
        mk.box(p, (ox, (y0 + min(y1, 3.55)) / 2, 0), (1.6, min(y1, 3.55) - y0, 1.6), RED)
        if i == 2:
            mk.box(p, (ox, 3.675, 0), (1.84, 0.27, 1.84), RED)                                   # cornisa
            mk.box(p, (ox, 3.88, 0), (1.94, 0.18, 1.94), GREY, top=(0.9, 0.9))                  # losa de remate
            mk.carve(p, COAL, points=mk.pts_box((ox, 3.9, 0), (0.8, 0.9, 0.8)))                 # boca
        if i > 0:
            mk.carve(p, RED, prism=dict(profile=stair(cuts[i - 1], False), depth=2.4, plane="xy", rot=(0, 30, 0),
                                        center=(ox, 0, 0)))
        if i < 2:
            mk.carve(p, RED, prism=dict(profile=stair(cuts[i], True), depth=2.4, plane="xy", rot=(0, 30, 0),
                                        center=(ox, 0, 0)))
        for k in range(1, 11):                                                                  # juntas de mortero
            y = 0.35 * k
            if y0 + 0.05 < y < min(y1, 3.5):
                for d in (-0.025, 0.025):
                    mk.slice(p, (ox, y + d, 0), (0, 1, 0))
                mk.paint(p, GREY, box=((ox, y, 0), (1.62, 0.052, 1.62)))


def build(mk):
    roof_flat(mk, 0.0)
    gable(mk, "Roof_Gable", 12.0, (DARK, MID, MID, DARK, DARK))
    gable(mk, "Roof_Gable_Charred", 24.0, (CHAR, DARK, CHAR, COAL, CHAR),
          holes=((2.2, -1.4, 0.9, 1), (6.5, 1.6, 0.7, 1), (4.0, 0.5, 1.1, -1)))
    gable_end(mk, 40.0)
    chimney(mk, 52.0)

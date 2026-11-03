"""
Receta de WST_Kit_Interior, piezas interiores comunes del kit modular (prompt 016, Bloques A + B/C).

Brief
- Silueta a 40 studs (desde la calle se ve el balcón; adentro, el resto): piso de tablas con tonos
  salteados, escalera de tablas con zancas oscuras y baranda, balcón de segundo piso con baranda de
  balaustres y ménsulas, tabique con papel mostaza arriba y friso de madera abajo.
- Fila sobre X, cada pieza con su origen abajo al centro:
  - fixed_Floor_Planks (x = 4): 8 x 8 x 0,4 (arriba en y = 0,4), 16 tablas de 0,5 a lo largo de X, tonos
    wood_mid / wood_light / wood_dark salteados, juntas oscuras.
  - fixed_Stairs (x = 16): 4 de ancho (huellas de 3,7 entre zancas de 0,15), sube 10 en 14 hacia +Z
    (primer escalón en z = -7), 15 escalones de 0,667 x 0,933, losa de abajo inclinada (abierta abajo),
    contrahuellas wood_dark, baranda del lado +X: dos postes, pasamanos y 4 balaustres.
  - Balcony (x = 26, 4 fragmentos): piso de 8 x 4 x 0,4 arriba en y = 10, sale hacia -Z desde la pared
    (z = 0); baranda de 3 al frente y a los costados con balaustres cada 1, dos ménsulas en diagonal a la
    pared. Origen en el piso (y = 0) al centro del borde contra la pared. Fragmentos: cuartos del piso
    (atrás / adelante x izquierda / derecha) con su parte de baranda y su ménsula.
  - Partition (x = 38, 4 fragmentos): tabique de 8 x 10 x 0,3, papel paint_mustard (recoloreable) en las
    dos caras, friso wood_mid hasta 3 con tablas verticales, guardasilla y zócalo wood_dark. Cuadrantes
    separados por dos grietas en zigzag (una a la altura del guardasilla, otra vertical).
- Nombres: fixed_Floor_Planks, fixed_Stairs, <Pieza>_fragNN.
- Inferido: dirección de la escalera y sus medidas de escalón, orígenes de balcón y escalera, baranda y
  ménsulas del balcón, balaustres cada 1, friso, guardasilla y zócalo del tabique, grietas.

Vueltas: 1) primera versión: el piso con el origen en (0,0,0) y sin tocar nada daba "flotante" (error);
el balcón a 1052 por los balaustres unidos a los pasamanos · 2) fila corrida (ninguna pieza en el origen) y
balaustres como detalle (sin caras coplanares, no hace falta unirlos): balcón 808.

Revisión
- Triángulos contra 300 por pieza: Floor_Planks 212, Stairs 386 (15 escalones, zancas, baranda), Balcony
  808 (4 fragmentos con baranda de balaustres en frente y costados, poste de esquina y ménsulas), Partition
  444 (friso de tablas en las dos caras, guardasilla, zócalo, moldura, grietas en zigzag). Calidad primero:
  el balcón se ve desde la calle en todos los edificios de dos plantas.
- Medidas: piso 8 x 0,4 x 8; escalera 4,08 x 10 (13,7 con el pasamanos arriba) x 14,1; balcón 8 x 4, piso
  arriba en 10, baranda hasta 13,05, ménsulas desde 7,3; tabique 8 x 10 x 0,3 (0,42 con el guardasilla).
- Fragmentos: balcón 24/24/26/26 %, tabique 21/18/36/26 %. El tabique de 0,3 queda debajo del 0,4 del
  Bloque C (medida del prompt).
- Aviso aceptado: "floating" del piso: es una pieza suelta en la fila.
- Normales del GLB final: 2 esquinas desviadas en la escalera (bug de process_model, ver el informe).
"""

import math

MID, LIGHT, DARK, MUSTARD, IRON = "wood_mid", "wood_light", "wood_dark", "paint_mustard", "iron"


def clean(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    return out


# ------------------------------------------------------------------------------------------- piso
def floor_planks(mk, ox):
    p = mk.part("fixed_Floor_Planks", (ox, 0, 0))
    mk.box(p, (ox, 0.2, 0), (8.0, 0.4, 8.0), MID)
    tones = [MID, LIGHT, MID, MID, DARK, LIGHT, MID, LIGHT, MID, MID, LIGHT, DARK, MID, LIGHT, MID, MID]
    for i in range(16):
        za, zb = -4 + 0.5 * i, -3.5 + 0.5 * i
        if i:
            for d in (-0.025, 0.025):
                mk.slice(p, (ox, 0, za + d), (0, 0, 1))
        if tones[i] != MID:
            mk.paint(p, tones[i], box=((ox, 0.2, (za + zb) / 2), (8.2, 0.42, 0.44)))
        if i:
            mk.paint(p, DARK, box=((ox, 0.4, za), (8.2, 0.02, 0.052)))                    # junta
    for z, x in ((-2.75, 1.8), (0.25, -2.3), (2.75, 0.6)):                                 # empalmes de tablas
        for d in (-0.03, 0.03):
            mk.slice(p, (ox + x + d, 0, 0), (1, 0, 0))
        mk.paint(p, DARK, box=((ox + x, 0.4, z), (0.062, 0.02, 0.44)))


# ---------------------------------------------------------------------------------------- escalera
def stairs(mk, ox):
    p = mk.part("fixed_Stairs", (ox, 0, 0))
    n, H, D = 15, 10.0, 14.0
    rise, run = H / n, D / n
    z0 = -D / 2
    prof = [(z0, 0.0)]
    for i in range(n):
        prof += [(z0 + run * i, rise * (i + 1)), (z0 + run * (i + 1), rise * (i + 1))]
    prof += [(z0 + D, H - 0.7), (z0 + 1.0, 0.0)]                                          # losa inclinada abajo
    prof = clean(prof)
    mk.prism(p, prof, 3.7, MID, plane="zy", center=(ox, 0, 0))                            # escalones
    for s in (-1, 1):                                                                     # zancas
        zz = [(z0 - 0.05, 0.0), (z0 + 0.6, 0.0), (z0 + D + 0.05, H - 0.9), (z0 + D + 0.05, H + 0.25), (z0 - 0.05, 0.85)]
        mk.prism(p, zz, 0.15, DARK, plane="zy", center=(ox + s * 1.925, 0, 0))
    for i in range(n):                                                                    # contrahuellas
        mk.paint(p, DARK, box=((ox, rise * (i + 0.5), z0 + run * i), (3.72, rise * 0.9, 0.02)))
    # baranda del lado +X: postes, pasamanos y balaustres sobre la zanca
    hx = ox + 1.925
    slope = H / D
    rail = lambda z: (z - z0) * slope + 0.85 + 2.8                                         # 2,8 arriba de la zanca
    for z in (z0 + 0.3, z0 + D - 0.3):
        mk.box(p, (hx, (rail(z) + 0.3 + (z - z0) * slope) / 2, z), (0.3, rail(z) + 0.3 - (z - z0) * slope, 0.3), DARK)
    mk.hull(p, [(hx + dx, rail(z) + dy, z) for dx in (-0.12, 0.12) for dy in (-0.1, 0.1) for z in (z0 + 0.3, z0 + D - 0.3)],
            DARK)                                                                         # pasamanos
    for k in range(1, 5):
        z = z0 + 0.3 + (D - 0.6) * k / 5
        y0 = (z - z0) * slope + 0.7
        mk.box(p, (hx, (y0 + rail(z)) / 2, z), (0.14, rail(z) - y0, 0.14), MID, detail=True)   # balaustres
    mk.carve(p, MID, points=mk.pts_box((ox, -3, 0), (0.1, 0.1, 0.1)))                     # une los cascos


# ------------------------------------------------------------------------------------------- balcón
def balcony(mk, ox):
    Y = 10.0
    for f, (xa, xb, za, zb) in enumerate(((-4, 0, -2, 0), (0, 4, -2, 0), (-4, 0, -4, -2), (0, 4, -4, -2))):
        p = mk.part(f"Balcony_frag0{f + 1}", (ox, 0, 0))
        mk.box(p, (ox + (xa + xb) / 2, Y - 0.2, (za + zb) / 2), (xb - xa, 0.4, zb - za), MID)   # piso
        for k in range(1, 4):                                                                  # juntas del piso (tablas en X)
            z = za + 0.5 * k
            for d in (-0.025, 0.025):
                mk.slice(p, (ox, 0, z + d), (0, 0, 1))
            mk.paint(p, DARK, box=((ox + (xa + xb) / 2, Y, z), (xb - xa + 0.1, 0.02, 0.052)))
        mk.paint(p, DARK, box=((ox + (xa + xb) / 2, Y - 0.2, (za + zb) / 2), (xb - xa + 0.2, 0.3, zb - za + 0.2)))  # cantos
        side = -1 if xa < 0 else 1
        ex = ox + side * 3.8                                                                   # baranda del costado
        rails = [(Y + 2.85, 0.3, 0.3, DARK), (Y + 0.35, 0.2, 0.22, MID)]
        for y, h, w, mat in rails:
            mk.box(p, (ex, y, (za + zb) / 2), (w, h, zb - za), mat)
        for z in [za + 0.5 + k for k in range(int(zb - za)) if za + 0.5 + k < zb]:
            mk.box(p, (ex, Y + 1.6, z), (0.14, 2.5, 0.14), LIGHT, detail=True)
        if za < -2.5:                                                                          # baranda del frente
            for y, h, w, mat in rails:
                mk.box(p, (ox + (xa + xb) / 2, y, -3.8), (xb - xa, h, w), mat)
            for x in [xa + 0.5 + k for k in range(4)]:
                if abs(x - side * 3.8) > 0.2:
                    mk.box(p, (ox + x, Y + 1.6, -3.8), (0.14, 2.5, 0.14), LIGHT, detail=True)
            mk.box(p, (ex, Y + 1.5, -3.8), (0.3, 3.1, 0.3), DARK)                              # poste de esquina
        else:                                                                                  # ménsula a la pared
            bx = ox + side * 3.0
            mk.hull(p, [(bx + dx, y, z) for dx in (-0.12, 0.12) for y, z in
                        ((Y - 0.38, -0.05), (Y - 0.38, -1.9), (Y - 0.62, -1.9), (Y - 2.3, -0.05), (Y - 2.6, -0.05))], DARK)
            mk.box(p, (bx, Y - 1.5, -0.08), (0.3, 2.4, 0.16), DARK)                            # pie contra la pared
        mk.carve(p, MID, points=mk.pts_box((ox, -3, 0), (0.1, 0.1, 0.1)))


# ------------------------------------------------------------------------------------------ tabique
def partition(mk, ox):
    T = 0.3
    vcrack = [(0.6, 10.5), (0.3, 7.0), (0.75, 5.0), (0.4, 3.15), (0.55, -0.5)]           # de arriba abajo
    hcrack = [(-4.5, 3.15), (-1.5, 3.15), (-0.8, 3.6), (0.3, 3.3), (1.4, 3.75), (4.5, 3.4)]  # de izquierda a derecha
    for f, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        p = mk.part(f"Partition_frag0{f + 1}", (ox, 0, 0))
        mk.box(p, (ox, 5.0, 0), (8.0, 10.0, T), MUSTARD)                                     # papel
        mk.box(p, (ox, 1.5, 0), (8.0, 3.0, T + 0.06), MID)                                   # friso
        mk.box(p, (ox, 3.05, 0), (8.0, 0.18, T + 0.12), DARK)                                # guardasilla
        mk.box(p, (ox, 0.15, 0), (8.0, 0.3, T + 0.1), DARK)                                  # zócalo
        mk.box(p, (ox, 9.85, 0), (8.0, 0.3, T + 0.08), DARK)                                 # moldura de arriba
        far_x = -20 if sx > 0 else 20                                                         # talla el otro lado de la vertical
        vp = [(ox + x, y) for x, y in vcrack] + [(ox + far_x, -0.5), (ox + far_x, 10.5)]
        mk.carve(p, LIGHT, prism=dict(profile=vp, depth=1.0, plane="xy"))
        far_y = 20 if sy < 0 else -20                                                         # y el otro lado de la horizontal
        hp = [(ox + x, y) for x, y in hcrack] + [(ox + 4.5, far_y), (ox - 4.5, far_y)]
        mk.carve(p, LIGHT, prism=dict(profile=hp, depth=1.0, plane="xy"))
        if sy < 0:                                                                            # tablas verticales del friso
            for k in range(1, 10):
                x = -4 + 0.8 * k
                for d in (-0.025, 0.025):
                    mk.slice(p, (ox + x + d, 0, 0), (1, 0, 0))
                for z in (-(T + 0.06) / 2, (T + 0.06) / 2):
                    mk.paint(p, DARK, box=((ox + x, 1.6, z), (0.052, 2.5, 0.02)))


def build(mk):
    floor_planks(mk, 4.0)          # ninguna pieza en el origen: son sueltas (si no, la revisión la toma por flotante)
    stairs(mk, 16.0)
    balcony(mk, 26.0)
    partition(mk, 38.0)

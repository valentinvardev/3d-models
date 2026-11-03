"""
Receta de WST_CH_Bell, la campana corrompida del campanario (prompt 123, Bloques A + C + G). Objetivo de la
fase 1 del Predicador: hay que destruirla.

Brief
- Silueta: campana de bronce clásica (corona chata, hombro, cintura angosta y boca que se abre) colgada de
  un cabezal de madera oscura con flejes de hierro, una rueda de madera al costado (+X) y la cuerda que baja.
  La plata viva la recorre: vetas de neón que bajan de la corona y una costra cristalina al frente (-Z).
- Origen: el pivote del yugo (eje de los muñones, a lo largo de X, en y = 0): la campana cuelga debajo.
- Medidas: campana de 3 de alto (corona en y = -0,7, boca en -3,7) y 3 de diámetro en la boca; perfil
  corona 0,62 / hombro 0,98 / cintura 1,06 / bordón 1,42 / boca 1,5; pared de ~0,2 (hueca).
  Cabezal 3,8 x 1,2 x 0,9; muñones de hierro a x = ±1,9..±2,4; rueda de radio 2 en x = 1,75 (plano YZ);
  cuerda de 25 desde el canto de adelante de la rueda (z = -2) hasta y = -25.
- Piezas: frag01..05 (cinco cascos curvos de la campana, cortes en zigzag por altura; dos bandas cada
  uno: hombro-cintura y cintura-boca), frag06 (el badajo), fixed_Yoke (cabezal, muñones, flejes, rueda),
  BellRope (origen arriba), Silver_Veins, Silver_Crust. Todas con el origen del modelo (el pivote);
  BellRope en su punta de arriba.
- Inferido: la rueda del lado +X y la cuerda bajando por adelante, el interior facetado (cada casco es
  convexo: la cara de adentro es una cuerda), dónde caen las vetas y la costra, parches de óxido en caras
  enteras del casco (pintura, sin calcomanías). 7 materiales: el prompt los nombra.

Vueltas: 1) z-fighting: las ramas de las vetas arrancaban en el mismo punto que la veta madre y el lomo
del cabezal terminaba al ras de sus testas · 2) el óxido pintado teñía triángulos enormes del casco (caras
largas del casco convexo) · 3) parches tallados: cinco costaban ~300 triángulos casi sin verse · 4) óxido en
la franja de la boca (pintada: caras angostas) y un parche tallado al frente.

Revisión
- 952 triángulos contra 600 (+59 %, calidad primero): cascos huecos de la campana ~330 (cinco fragmentos de
  dos bandas para conservar cintura y boca, más el parche de óxido), yugo ~270 (cabezal, flejes, muñones y la
  rueda de 12 lados con rayos: el prompt pide la cuerda "desde una rueda"), cuerda 40, vetas ~150, costra
  ~70, badajo 24.
- Medidas: campana 3 de alto (y -0,7 a -3,7) y 3,0 de boca; con cabezal, rueda y cuerda: 4,8 x 26,9 x 4,1.
  El aviso "lowest point -25" es la cuerda (el origen es el pivote del yugo, como pide el prompt).
- Fragmentos: frag01..05 cascos (~20 % cada uno), frag06 el badajo; fixed_Yoke queda; BellRope con origen
  arriba (1,75, 0, -2). Silver_Veins y Silver_Crust son superpuestos (Bloque G).
- 7 materiales (brass, rust, wood_dark, iron, rope, silver_neon, silver_crust): todos nombrados en el prompt.
- El interior de la campana queda facetado en cinco caras planas por banda (cada casco es convexo).
"""

import math

BRASS, RUST, DARK, IRON, ROPE, NEON, CRUST = ("brass", "rust", "wood_dark", "iron", "rope", "silver_neon",
                                              "silver_crust")
# perfil exterior (radio, y) y anillos de adentro
UP_OUT = [(0.62, -0.7), (0.98, -1.05), (1.06, -2.35)]
LO_OUT = [(1.06, -2.33), (1.42, -3.35), (1.5, -3.62), (1.44, -3.7)]
UP_IN = [(0.8, -1.2), (0.86, -2.35)]
LO_IN = [(0.86, -2.33), (1.28, -3.7)]
SEG = 3                                      # segmentos por casco (15 lados en total)
# bordes de los cascos (grados) en cada nivel: zigzag (la grieta baja torcida)
CUTS = [10.0, 82.0, 154.0, 226.0, 298.0]
JAG = {"top": [0, 6, -5, 4, -6], "mid": [-7, -4, 8, -6, 5], "bot": [5, 9, -6, 7, -4]}


def P(r, y, deg):
    t = math.radians(deg)
    return (r * math.cos(t), y, r * math.sin(t))


def arc(r, y, a0, a1, n=SEG):
    return [P(r, y, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def surf_r(y, deg, a0, a1):
    """Radio de la faceta del casco en (y, ángulo): las vetas apoyan sobre la cara plana, no en el vértice."""
    prof = UP_OUT if y > -2.34 else LO_OUT
    for (ra, ya), (rb, yb) in zip(prof, prof[1:]):
        if yb <= y <= ya:
            r = ra + (rb - ra) * (ya - y) / (ya - yb)
            break
    else:
        r = prof[-1][0]
    step = (a1 - a0) / SEG
    k = min(SEG - 1, max(0, int((deg - a0) / step)))
    mid = a0 + step * (k + 0.5)
    return r * math.cos(math.radians(step / 2)) / math.cos(math.radians(deg - mid))


def shard_bounds(k, level):
    a0 = CUTS[k] + JAG[level][k]
    b = CUTS[(k + 1) % 5] + JAG[level][(k + 1) % 5]
    if b <= a0:
        b += 360.0
    return a0, b


def build(mk):
    # ---- cascos de la campana: dos cascos convexos por fragmento (arriba y abajo de la cintura) ----
    shard_parts = []
    for k in range(5):
        part = mk.part(f"frag{k + 1:02d}", (0, 0, 0))
        shard_parts.append(part)
        t0, t1 = shard_bounds(k, "top")
        m0, m1 = shard_bounds(k, "mid")
        b0, b1 = shard_bounds(k, "bot")
        pts = arc(UP_OUT[0][0], UP_OUT[0][1], t0, t1) + arc(UP_OUT[1][0], UP_OUT[1][1], t0 + (m0 - t0) * 0.3,
                                                          t1 + (m1 - t1) * 0.3) + arc(UP_OUT[2][0], UP_OUT[2][1], m0, m1)
        pts += [P(UP_IN[0][0], UP_IN[0][1], a) for a in (t0 + (m0 - t0) * 0.3, t1 + (m1 - t1) * 0.3)]
        pts += [P(UP_IN[1][0], UP_IN[1][1], a) for a in (m0, m1)]
        mk.hull(part, pts, BRASS)
        pts = arc(LO_OUT[0][0], LO_OUT[0][1], m0, m1) + arc(LO_OUT[1][0], LO_OUT[1][1], m0 + (b0 - m0) * 0.8,
                                                          m1 + (b1 - m1) * 0.8)
        pts += arc(LO_OUT[2][0], LO_OUT[2][1], b0, b1) + arc(LO_OUT[3][0], LO_OUT[3][1], b0, b1)
        pts += [P(LO_IN[0][0], LO_IN[0][1], a) for a in (m0, m1)] + [P(LO_IN[1][0], LO_IN[1][1], a) for a in (b0, b1)]
        mk.hull(part, pts, BRASS)

    # óxido: la franja de la boca pintada (caras angostas) y un parche tallado de 0,04 al frente. Pintar una cara
    # del casco teñía triángulos enormes; cinco parches tallados costaban ~300 triángulos casi sin verse (medido)
    for k in range(5):
        mk.paint(shard_parts[k], RUST, box=((0, -3.66, 0), (4.0, 0.1, 4.0)))
    for k, y, frac, size in ((3, -2.2, 0.5, 0.42),):
        m0, m1 = shard_bounds(k, "mid")
        p, rad, tan = frame_at(y, m0 + (m1 - m0) * frac)
        blob = [(1.0, 0.0), (0.55, 0.8), (-0.35, 0.95), (-1.0, 0.25), (-0.7, -0.7), (0.3, -0.9)]
        pts = []
        for u, v in blob:
            for h in (-0.04, 0.2):
                pts.append(tuple(p[i] + tan[i] * u * size + (0, 1, 0)[i] * v * size * 0.8 + rad[i] * h
                                 for i in range(3)))
        mk.carve(shard_parts[k], RUST, points=pts)
    # ---- badajo: vástago y bola, colgado de la corona por dentro ----
    part = mk.part("frag06", (0, 0, 0))
    mk.box(part, (0, -2.1, 0), (0.16, 1.9, 0.16), IRON)
    mk.hull(part, [P(0.32, -3.2, a) for a in range(0, 360, 60)] + [(0, -2.88, 0), (0, -3.52, 0)], IRON)
    # ---- yugo: cabezal, muñones, flejes y rueda ----
    part = mk.part("fixed_Yoke", (0, 0, 0))
    # todo es detalle salvo la llanta de la rueda: la talla de su aro se comería el cabezal y los muñones
    mk.box(part, (0, -0.1, 0), (3.8, 1.2, 0.9), DARK, detail=True)                         # cabezal
    mk.hull(part, [(x, y, z) for x in (-1.88, 1.88) for y, z in ((0.48, -0.3), (0.48, 0.3), (0.62, -0.2), (0.62, 0.2))],
            DARK, detail=True)                                                            # lomo redondeado
    for s in (-1, 1):
        mk.cyl(part, (s * 2.12, 0, 0), 0.16, 0.56, IRON, axis="x", sides=6, detail=True)   # muñones
    for x in (-0.42, 0.42):                                                                # flejes en U sobre la corona
        for z in (-0.48, 0.48):
            mk.box(part, (x, -0.17, z), (0.2, 1.54, 0.07), IRON, detail=True)
        mk.box(part, (x, 0.6, 0), (0.2, 0.08, 1.04), IRON, detail=True)
    # rueda (plano YZ) en la punta +X del cabezal: llanta de 12 lados tallada y tres travesaños
    xw = 1.75
    ring = [(2.0 * math.cos(2 * math.pi * (k + 0.5) / 12), 2.0 * math.sin(2 * math.pi * (k + 0.5) / 12)) for k in range(12)]
    mk.prism(part, ring, 0.22, DARK, plane="zy", center=(xw, 0, 0))
    inner = [(1.72 * math.cos(2 * math.pi * (k + 0.5) / 12), 1.72 * math.sin(2 * math.pi * (k + 0.5) / 12))
             for k in range(12)]
    mk.carve(part, DARK, prism=dict(profile=inner, depth=0.6, plane="zy", center=(xw, 0, 0)))
    for k, ang in enumerate((15, 75, 135)):
        t = math.radians(ang)
        a, b = (1.78 * math.cos(t), 1.78 * math.sin(t)), (-1.78 * math.cos(t), -1.78 * math.sin(t))
        w = 0.16 + 0.01 * k
        nz, ny = -(b[1] - a[1]), b[0] - a[0]
        nl = math.hypot(nz, ny)
        nz, ny = nz / nl * 0.09, ny / nl * 0.09
        mk.hull(part, [(xw + dx, p[1] + s2 * ny, p[0] + s2 * nz) for p in (a, b) for s2 in (-1, 1)
                       for dx in (-w / 2, w / 2)], DARK, detail=True)
    # ---- cuerda: baja 25 desde el canto de adelante de la rueda ----
    top = (xw, 0.0, -2.0)
    part = mk.part("BellRope", top)
    mk.cyl(part, (xw, -12.5, -2.0 - 0.0), 0.11, 25.0, ROPE, sides=6)
    for y in (-22.0,):                                                                      # nudo de agarre abajo
        mk.cyl(part, (xw, y, -2.0), 0.17, 0.3, ROPE, sides=6)
    # ---- plata viva: vetas que bajan de la corona y costra al frente ----
    part = mk.part("Silver_Veins", (0, 0, 0))
    veins = [
        [(-0.75, 95.0), (-1.3, 102.0), (-2.0, 96.0), (-2.7, 104.0), (-3.4, 99.0)],
        [(-0.75, 205.0), (-1.4, 198.0), (-2.2, 206.0), (-3.1, 200.0)],
        [(-0.75, 330.0), (-1.5, 338.0), (-2.4, 331.0)],
        [(-1.3, 102.0), (-1.9, 118.0), (-2.4, 124.0)],                                    # ramas
        [(-1.4, 198.0), (-2.1, 186.0)],
        [(-2.2, 206.0), (-2.9, 218.0)],
    ]
    for vi, path in enumerate(veins):
        for j, ((ya, da), (yb, db)) in enumerate(zip(path, path[1:])):
            w = (0.12 if vi < 3 else 0.09) * (1.0 - 0.18 * j)
            # cada tramo pasa 8 % del siguiente y las ramas arrancan 10 % adentro del tramo: si arrancan en
            # el mismo punto que la veta madre, sus tapas quedan coplanares (medido)
            t0 = 0.1 if (vi >= 3 and j == 0) else 0.0
            ya2, da2 = ya + (yb - ya) * t0, da + (db - da) * t0
            yb2, db2 = yb + (yb - ya) * 0.08, db + (db - da) * 0.08
            vein_segment(mk, part, ya2, da2, yb2, db2, max(0.06, w))
    part = mk.part("Silver_Crust", (0, 0, 0))
    crust(mk, part)


def frame_at(y, deg):
    """Punto sobre la faceta del casco y la base local (radial, tangente) en (y, ángulo). Usa los bordes del
    casco a la altura de la cintura (en el resto el error es de ~0,01: las vetas se meten 0,04)."""
    k = next(i for i in range(5) if _in(deg, *shard_bounds(i, "mid")))
    a0, a1 = shard_bounds(k, "mid")
    d = deg % 360
    if d < a0:
        d += 360
    r = surf_r(y, d, a0, a1)
    t = math.radians(deg)
    return (r * math.cos(t), y, r * math.sin(t)), (math.cos(t), 0.0, math.sin(t)), (-math.sin(t), 0.0, math.cos(t))


def _in(deg, a0, a1):
    d = deg % 360
    return a0 <= d <= a1 or a0 <= d + 360 <= a1


def vein_segment(mk, part, ya, da, yb, db, w):
    pa, ra, ta = frame_at(ya, da)
    pb, rb, tb = frame_at(yb, db)
    pts = []
    for p, rad, tan, ww in ((pa, ra, ta, w), (pb, rb, tb, w * 0.8)):
        for s in (-0.5, 0.5):
            for h in (-0.04, 0.035):                                                       # 0,035 afuera de la faceta
                pts.append(tuple(p[i] + tan[i] * s * ww + rad[i] * h for i in range(3)))
    mk.hull(part, pts, NEON)


def crust(mk, part):
    """Costra de placas cristalinas al frente (-Z = 270°) sobre una cama de neón (las juntas)."""
    plates = [(-2.55, 262.0, 0.32, 0.28), (-2.85, 276.0, 0.36, 0.22), (-3.15, 266.0, 0.3, 0.34),
              (-2.6, 284.0, 0.24, 0.16), (-3.25, 282.0, 0.26, 0.2)]
    bed = []                                                                               # cama: puntos sobre la faceta
    for dy, dt in ((-0.55, -14.0), (-0.55, 14.0), (0.5, -13.0), (0.5, 13.0), (0.0, -19.0), (0.0, 19.0), (0.0, 0.0)):
        p, rad, tan = frame_at(-2.9 + dy, 273.0 + dt)
        for h in (-0.04, 0.05):
            bed.append(tuple(p[i] + rad[i] * h for i in range(3)))
    mk.hull(part, bed, NEON)
    for y, deg, size, height in plates:
        p, rad, tan = frame_at(y, deg)
        up = (0.0, 1.0, 0.0)
        base = []
        for a in range(5):
            t = 2 * math.pi * (a + 0.2) / 5
            u, v = math.cos(t) * size, math.sin(t) * size * 0.8
            base.append(tuple(p[i] + tan[i] * u + up[i] * v + rad[i] * 0.03 for i in range(3)))
        tip = tuple(p[i] + rad[i] * (0.03 + height) + tan[i] * size * 0.25 + up[i] * size * 0.2 for i in range(3))
        ridge = tuple(p[i] + rad[i] * (0.03 + height * 0.7) - tan[i] * size * 0.3 for i in range(3))
        mk.hull(part, base + [tip, ridge], CRUST)

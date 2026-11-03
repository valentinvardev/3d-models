"""
Receta de WST_SB_Bridge, el puente largo de Silver Bend (prompt 108, Bloques A + C).

Brief
- Silueta a 40 studs: tablero de tablas sueltas sobre tres largueros oscuros, un caballete de dos pilotes
  redondos con cruz de San Andrés que baja al agua, y baranda simple con un tramo que falta. El estribo
  es un muro de piedra escalonado que se mete en el río con una solera de madera arriba.
- Módulo: 8 de largo (Z, el cruce) x 7 de ancho (X), tablero arriba en y = 0 (origen del módulo en el
  centro de la cara de arriba del tablero), río 10 abajo (y = -10).
- Tablas: 10 transversales de 7 x 0,25 x 0,75 con luz de 0,05 (z del centro = -3,6 + 0,8 i). Cada una es
  su fragmento (frag01..frag10), con alturas e inclinaciones distintas (±1,5° sobre su largo, ±0,6° de
  punta a punta) y apoyadas en los largueros (la esquina más baja se mete 0,015). Colores wood_light /
  wood_mid alternados sin patrón fijo (alternados perfectos se leen como cebra, porche del kit).
- fixed_Stringers: 3 largueros wood_dark de 0,6 x 0,8 (y -1,05..-0,25) en x = -3,15, 0, 3,15, de punta a
  punta del módulo (z ±4): las tablas sobresalen 0,05 del larguero de afuera.
- fixed_Pile: caballete en la punta +Z, centrado en la junta (z = 4): así el mismo cabezal sostiene las
  puntas de los largueros de este módulo y del siguiente (sale 0,4 del módulo). Cabezal de 7,9 x 0,6 x 0,8,
  dos pilotes de 8 lados (r 0,42 arriba, 0,38 abajo) de 12 de largo con un poco de talud hacia afuera, y
  dos riostras en cruz, una en cada cara de los pilotes.
- fixed_Railing: postes de 0,3 x 0,3 cada 4 (z = ±2) atornillados a la cara de afuera del larguero
  (x 3,45..3,75), pasamanos de 0,35 x 0,25 arriba en 3,5. Del lado +X falta el tramo z -4..-0,6 (punta
  astillada); el poste de z = -2 quedó solo.
- Variantes (mismo archivo, prefijo <Variante>_, origen en el centro del tablero de cada una), armadas en
  fila sobre Z para que se vea cómo calzan: Bridge_Abutment en z = -8 (estribo, lado de la orilla),
  Bridge_Module en z = 0 y Bridge_Module_Damaged en z = 8.
- Bridge_Module_Damaged: faltan las tablas 4, 5 y 9 (quedan 7: frag01..frag07), la tabla 6 está quebrada
  en una punta y la 3 se hunde hacia el hueco; el larguero del medio rajado desde abajo (V tallada con
  astillas) pero en pie.
- Bridge_Abutment: 10 tablas (frag01..frag10), largueros, baranda entera con postes de remate gruesos en
  la punta de la orilla y fixed_Abutment: muro de piedra de 5 hiladas con talud escalonado (juntas y
  lechos en sand), alas de piedra a los costados, solera de madera arriba del muro (sostiene también la
  punta del primer módulo: sale hasta z = 4,4) y durmiente en la punta de la orilla.
- Marcadores: _<Variante>_Hang_1..6 en las dos puntas de cada larguero (módulo y dañado; el estribo está
  sobre tierra).
- Inferido: espaciado y alto de los largueros, caballete centrado en la junta, talud y riostras, la
  baranda abulonada al larguero (el ancho total con postes es 7,5), punta astillada del tramo que falta,
  qué tablas faltan en el dañado, todo el estribo (piedra, alas, soleras, remates), nombres con prefijo
  y marcadores con prefijo (convención de WST_Prop_TelegraphPole).

Vueltas: 1) primera versión: la tabla quebrada del dañado flotaba (la esquina más baja era la que se
tallaba), la rajadura del larguero no se leía y las alas de piedra eran paños lisos · 2) la tabla quebrada
inclinada al revés, V del larguero de 0,64 x 0,7 con astillas de 0,4, hiladas y juntas trabadas también en
las alas, largos y puntas de las tablas apenas distintos (±0,12).

Revisión
- Triángulos por variante (tope 800 por módulo): Bridge_Module 412 (tablas 180, largueros 36, caballete
  92, baranda 104), Bridge_Module_Damaged 444, Bridge_Abutment 794 (el muro con juntas, 458). Total 1650.
- Medidas: módulo de 7,5 de ancho con los postes (tablero 7), 8 de largo más 0,4 del cabezal que pasa la
  junta; tablero arriba en y = 0 (la tabla más alta, +0,04); pilotes hasta y = -13,6 (12 de largo, 3,6 bajo
  el río). El estribo mide 9 de ancho (muro y alas) y su muro baja hasta y = -11.
- Tablas de 0,25 de espesor como pide el prompt: el Bloque C pide fragmentos de 0,4 como mínimo; manda el
  prompt (cada tabla es un fragmento y se rompe de a una).
- La luz de 0,05 entre tablas es la del prompt (el Bloque C pide fragmentos sin luz: acá cada tabla apoya
  en los largueros, no en la vecina).
- DUDOSO, colisión: fixed_Stringers (3 vigas) y fixed_Railing (dos lados) son un objeto cada uno, como
  pide el prompt. Con colisión de casco convexo, el casco de los largueros es una losa que no deja caer
  entre ellos al que pisa una tabla rota, y el de la baranda tapa el tablero. En Studio necesitan
  PreciseConvexDecomposition o partirse por viga y por lado (decide Valentin).
- El caballete sale 0,4 del módulo (centrado en la junta): sostiene las puntas de los dos módulos vecinos.
  El último módulo de la fila queda con un caballete que no sostiene nada (o se apoya en el estribo girado).
"""

import math

from mathutils import Euler, Vector

LIGHT, MID, DARK, IRON, STONE, MORTAR = "wood_light", "wood_mid", "wood_dark", "iron", "stone_grey", "sand"

PL_L, PL_W, PL_T = 7.0, 0.75, 0.25
STR_X = (-3.15, 0.0, 3.15)
STR_W, STR_Y = 0.6, (-1.05, -0.25)
POST_X = 3.6                    # centro de los postes de la baranda (x 3,45..3,75)
RAIL_Y = (3.25, 3.5)
CAP_Y = (-1.65, -1.05)


def plank_z(i):
    return -3.6 + 0.8 * i


def plank(mk, part, cx, cz, mat, rx, rz, length=PL_L, bottom=-0.265):
    """Tabla girada rx (sobre su largo, X) y rz (punta a punta); la esquina más baja queda en `bottom`."""
    e = Euler((math.radians(rx), 0, math.radians(rz)), "XYZ").to_matrix()
    pts = [e @ Vector((sx * length / 2, sy * PL_T / 2, sz * PL_W / 2)) for sx in (-1, 1) for sy in (-1, 1)
           for sz in (-1, 1)]
    dy = bottom - min(p.y for p in pts)
    mk.hull(part, [(cx + p.x, dy + p.y, cz + p.z) for p in pts], mat)
    return dy


LEN_JITTER = (0.0, -0.12, 0.0, 0.08, -0.06, 0.1, -0.1, 0.0, 0.05, -0.08)   # tablas 2 y 7: bajo los postes


def deck(mk, prefix, oz, spec, seed=0):
    """spec: lista de (índice de tabla, color, rx, rz) -> fragmentos en orden. Devuelve {i: parte}.
    Largos y puntas apenas distintos (las tablas bajo los postes, 2 y 7, quedan de 7 justas)."""
    parts = {}
    for n, (i, mat, rx, rz) in enumerate(spec):
        p = mk.part(f"{prefix}_frag{n + 1:02d}", (0, 0, oz))
        dl = LEN_JITTER[(i + seed) % 10] if i not in (2, 7) else 0.0
        dx = LEN_JITTER[(i + seed + 3) % 10] * 0.4 if i not in (2, 7) else 0.0
        plank(mk, p, dx, oz + plank_z(i), mat, rx, rz, length=PL_L + dl)
        parts[i] = p
    return parts


def chip(mk, part, x, z, sx, sz, size=0.45):
    """Esquina comida de una tabla: triángulo tallado en planta (sx, sz = hacia dónde está la esquina)."""
    tri = [(x + sx * 0.1, z + sz * 0.1), (x - sx * size, z + sz * 0.1), (x + sx * 0.1, z - sz * size * 0.7)]
    mk.carve(part, LIGHT, prism=dict(profile=tri, depth=1.0, plane="xz", center=(0, 0, 0)))


def split(mk, part, x0, x1, z):
    """Rajadura a lo largo de una tabla: ranura fina en zigzag, oscura."""
    n = 5
    top = [(x0 + (x1 - x0) * k / n, z + (0.03 if k % 2 else -0.03)) for k in range(n + 1)]
    bot = [(x + 0.02 * (1 if k % 2 else -1), zz - 0.05) for k, (x, zz) in enumerate(top)]
    prof = top + [(x1 + 0.05, z - 0.01)] + list(reversed(bot))
    mk.carve(part, DARK, prism=dict(profile=prof, depth=1.0, plane="xz", center=(0, 0.1, 0)))


def stringers(mk, prefix, oz, cracked=False):
    p = mk.part(f"{prefix}_fixed_Stringers", (0, 0, oz))
    for x in STR_X:
        mk.box(p, (x, sum(STR_Y) / 2, oz), (STR_W, STR_Y[1] - STR_Y[0], 8.0), DARK)
    if cracked:                                          # el del medio, rajado desde abajo
        zc = oz - 0.5
        v = [(zc - 0.34, STR_Y[0] - 0.1), (zc + 0.3, STR_Y[0] - 0.1), (zc + 0.12, -0.74), (zc + 0.16, -0.6),
             (zc + 0.02, -0.36), (zc - 0.04, -0.5), (zc - 0.12, -0.46), (zc - 0.16, -0.72)]
        mk.carve(p, LIGHT, prism=dict(profile=v, depth=0.8, plane="zy", center=(0, 0, 0)))
        # astillas que cuelgan de los bordes de la rajadura
        for z0, z1, tip in ((zc - 0.6, zc - 0.36, (zc - 0.2, STR_Y[0] - 0.42)), (zc + 0.32, zc + 0.56, (zc + 0.12, STR_Y[0] - 0.36))):
            base = [(x, STR_Y[0] + 0.02, z) for x in (-0.24, 0.24) for z in (z0, z1)]
            mk.hull(p, base + [(0.05, tip[1], tip[0])], LIGHT, detail=True)
    return p


def hang_markers(mk, prefix, oz):
    k = 1
    for x in STR_X:
        for z in (-4.0, 4.0):
            mk.marker(f"_{prefix}_Hang_{k}", (x, sum(STR_Y) / 2, oz + z))
            k += 1


def pile_bent(mk, prefix, oz):
    p = mk.part(f"{prefix}_fixed_Pile", (0, 0, oz))
    zc = oz + 4.0
    mk.box(p, (0, sum(CAP_Y) / 2, zc), (7.9, CAP_Y[1] - CAP_Y[0], 0.8), DARK)          # cabezal
    def pile_x(y, s):
        return s * (3.0 + 0.4 * (-1.6 - y) / 12.0)
    for s in (-1, 1):
        pts = []
        for y, r in ((-1.6, 0.42), (-13.6, 0.38)):
            for i in range(8):
                a = 2 * math.pi * (i + 0.5) / 8
                pts.append((pile_x(y, s) + r * math.cos(a), y, zc + r * math.sin(a)))
        mk.hull(p, pts, MID)
    # cruz de San Andrés: una riostra en cada cara de los pilotes
    for zf, s in ((zc - 0.34, -1), (zc + 0.34, 1)):
        a = Vector((pile_x(-2.2, -s) - s * 0.25, -2.2))
        b = Vector((pile_x(-8.6, s) + s * 0.25, -8.6))
        d = (b - a).normalized()
        n = Vector((-d.y, d.x)) * 0.3
        pts = [(q.x, q.y, zf + s * dz) for q in (a + n, a - n, b + n, b - n) for dz in (0.0, 0.2)]
        mk.hull(p, pts, DARK)
    return p


def railing(mk, prefix, oz, missing=True, end_posts=False):
    p = mk.part(f"{prefix}_fixed_Railing", (0, 0, oz))
    for s in (-1, 1):
        for z in (-2.0, 2.0):
            mk.box(p, (s * POST_X, (-1.0 + RAIL_Y[0] + 0.02) / 2, oz + z), (0.3, RAIL_Y[0] + 0.02 + 1.0, 0.3), MID)
        z0 = -0.6 if (missing and s > 0) else -4.0
        mk.box(p, (s * POST_X, sum(RAIL_Y) / 2, oz + (z0 + 4.0) / 2), (0.35, RAIL_Y[1] - RAIL_Y[0], 4.0 - z0), MID,
               top=(0.86, 1.0))
        if end_posts:                                             # remates gruesos en la punta de la orilla
            x = s * 3.7
            mk.box(p, (x, (-1.07 + 4.2) / 2, oz - 4.0), (0.5, 4.2 + 1.07, 0.5), DARK)
            mk.box(p, (x, 4.29, oz - 4.0), (0.6, 0.22, 0.6), DARK, top=(0.4, 0.4))
    if missing:                                                    # punta astillada del pasamanos que quedó
        zz = oz - 0.6
        prof = [(zz - 0.2, RAIL_Y[0] - 0.1), (zz + 0.12, RAIL_Y[0] - 0.1), (zz + 0.12, RAIL_Y[0] + 0.07),
                (zz + 0.02, RAIL_Y[0] + 0.1), (zz + 0.2, RAIL_Y[0] + 0.16), (zz + 0.05, RAIL_Y[1] - 0.06),
                (zz + 0.1, RAIL_Y[1] + 0.1), (zz - 0.2, RAIL_Y[1] + 0.1)]
        mk.carve(p, LIGHT, prism=dict(profile=prof, depth=0.6, plane="zy", center=(POST_X, 0, 0)))
    return p


# ---------------------------------------------------------------------------------------------- estribo
COURSES = [-11.0, -9.2, -7.4, -5.6, -3.8, -1.65]     # hiladas del muro
FACE0, STEP = 5.0, 0.15                               # cara de abajo y retranqueo por hilada


def abutment(mk, prefix, oz):
    p = mk.part(f"{prefix}_fixed_Abutment", (0, 0, oz))
    prof = [(oz + 2.0, COURSES[0])]
    for k in range(5):
        f = oz + FACE0 - STEP * k
        prof += [(f, COURSES[k]), (f, COURSES[k + 1])]
    prof += [(oz + 2.0, COURSES[-1])]
    mk.prism(p, prof, 8.8, STONE, plane="zy", center=(0, 0, 0))                          # muro
    for s in (-1, 1):                                                                     # alas
        wing = [(oz + 2.1, -11.0), (oz + 2.1, -1.62), (oz - 4.0, -1.62), (oz - 4.0, -2.8), (oz + 0.6, -11.0)]
        mk.prism(p, wing, 0.7, STONE, plane="zy", center=(s * 4.15, 0, 0))
    mk.box(p, (0, (CAP_Y[0] - 0.02 + CAP_Y[1]) / 2, oz + 3.39), (7.8, CAP_Y[1] - CAP_Y[0] + 0.02, 1.98), DARK)  # solera del muro
    mk.box(p, (0, sum(CAP_Y) / 2, oz - 3.6), (7.8, CAP_Y[1] - CAP_Y[0], 0.8), DARK)      # durmiente de la orilla
    # juntas: lechos de las hiladas (los retranqueos) y verticales trabadas, en sand
    for k in range(1, 5):
        f = oz + FACE0 - STEP * k
        mk.paint(p, MORTAR, box=((0, COURSES[k], f + STEP / 2), (8.7, 0.02, STEP - 0.01)))
    for k in range(5):
        f = oz + FACE0 - STEP * k
        y0, y1 = COURSES[k], COURSES[k + 1]
        for j in range(4):
            x = -3.3 + 2.2 * j + (0.0 if k % 2 else 1.1)
            if abs(x) > 4.2:
                continue
            for d in (-0.045, 0.045):
                mk.slice(p, (x + d, 0, 0), (1, 0, 0))
            mk.paint(p, MORTAR, box=((x, (y0 + y1) / 2, f), (0.092, y1 - y0 - 0.02, 0.02)))
    # alas: las mismas hiladas en la cara de afuera (lo que se ve desde las orillas)
    for k in range(1, 5):
        for d in (-0.045, 0.045):
            mk.slice(p, (0, COURSES[k] + d, 0), (0, 1, 0))
    zs = set()
    for s in (-1, 1):
        for k in range(1, 5):
            mk.paint(p, MORTAR, box=((s * 4.5, COURSES[k], oz - 1.0), (0.02, 0.092, 6.4)))
        for k in range(5):
            y0, y1 = COURSES[k], (COURSES[k + 1] if k < 4 else -1.62)
            for j in range(4):
                z = -3.0 + 1.9 * j + (0.95 if k % 2 else 0.0)
                if z > 1.7:
                    continue
                zs.add(z)
                mk.paint(p, MORTAR, box=((s * 4.5, (y0 + y1) / 2, oz + z), (0.02, y1 - y0 - 0.1, 0.092)))
    for z in sorted(zs):
        for d in (-0.045, 0.045):
            mk.slice(p, (0, 0, oz + z + d), (0, 0, 1))
    return p


# ---------------------------------------------------------------------------------------------- armado
def build(mk):
    # ---------------- módulo normal ----------------
    pre, oz = "Bridge_Module", 0.0
    spec = [(0, LIGHT, 1.2, 0.3), (1, MID, -0.8, -0.5), (2, MID, 1.5, 0.2), (3, LIGHT, -1.0, 0.6),
            (4, MID, 0.6, -0.3), (5, LIGHT, -1.4, 0.4), (6, LIGHT, 0.9, -0.6), (7, MID, -0.5, 0.5),
            (8, LIGHT, 1.3, -0.2), (9, MID, -1.1, 0.3)]
    parts = deck(mk, pre, oz, spec)
    chip(mk, parts[1], 3.5, oz + plank_z(1) - 0.375, 1, -1)
    chip(mk, parts[6], -3.5, oz + plank_z(6) + 0.375, -1, 1, 0.55)
    split(mk, parts[4], -3.6, -1.6, oz + plank_z(4) + 0.08)
    stringers(mk, pre, oz)
    pile_bent(mk, pre, oz)
    railing(mk, pre, oz)
    hang_markers(mk, pre, oz)

    # ---------------- módulo dañado ----------------
    pre, oz = "Bridge_Module_Damaged", 8.0
    spec = [(0, MID, -1.0, 0.4), (1, LIGHT, 1.1, -0.3), (2, MID, 4.0, 0.8), (5, LIGHT, -1.2, 0.5),
            (6, MID, 1.0, 0.4), (7, LIGHT, -0.7, -0.4), (9, MID, 1.4, 0.2)]
    parts = deck(mk, pre, oz, spec, seed=3)
    zc = oz + plank_z(5)                                        # tabla 6 quebrada en la punta +X
    brk = [(1.2, zc - 0.6), (3.9, zc - 0.6), (3.9, zc + 0.6), (2.5, zc + 0.6), (2.3, zc + 0.22), (2.6, zc + 0.08),
           (2.0, zc - 0.06), (2.25, zc - 0.22), (1.7, zc - 0.42)]
    mk.carve(parts[5], LIGHT, prism=dict(profile=brk, depth=1.0, plane="xz", center=(0, 0, 0)))
    chip(mk, parts[7], -3.5, oz + plank_z(7) - 0.375, -1, -1)
    split(mk, parts[1], 0.6, 2.8, oz + plank_z(1) - 0.05)
    stringers(mk, pre, oz, cracked=True)
    pile_bent(mk, pre, oz)
    railing(mk, pre, oz)
    hang_markers(mk, pre, oz)

    # ---------------- estribo ----------------
    pre, oz = "Bridge_Abutment", -8.0
    spec = [(0, MID, 0.8, -0.3), (1, LIGHT, -1.2, 0.4), (2, MID, 1.0, 0.2), (3, MID, -0.7, -0.5),
            (4, LIGHT, 1.3, 0.3), (5, MID, -1.0, -0.2), (6, LIGHT, 0.5, 0.6), (7, LIGHT, -1.3, -0.4),
            (8, MID, 1.1, 0.3), (9, LIGHT, -0.9, -0.5)]
    parts = deck(mk, pre, oz, spec, seed=6)
    chip(mk, parts[0], 3.5, oz + plank_z(0) - 0.375, 1, -1, 0.5)
    split(mk, parts[7], 1.0, 3.3, oz + plank_z(7))
    stringers(mk, pre, oz)
    railing(mk, pre, oz, missing=False, end_posts=True)
    abutment(mk, pre, oz)

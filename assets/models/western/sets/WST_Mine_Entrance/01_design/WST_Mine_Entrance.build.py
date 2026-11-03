"""
Receta de WST_Mine_Entrance, la boca de la mina en el acantilado (prompt 096, Bloques A + B).

Brief
- Silueta a 40 studs: un paredón de roca roja facetada de 30 x 20 con estratos ocres, una boca negra al
  medio enmarcada por un pórtico de vigas oscuras con un cartel claro arriba, la vía que sale hasta el
  frente, la vagoneta oxidada y el montón gris de escoria al costado. Dos faroles encendidos a los lados.
- Medidas: pórtico de 10 de ancho x 9 de alto (postes de 0,8 en x = ±4,6, viga cabezal de 0,8 a y 8,2-9,0,
  dos riostras en las esquinas); cartel en blanco de 6 x 1,35 sobre dos montantes, encima del cabezal.
  Paredón: 30 (x) x 20 (alto), de z ≈ -1,5 (frente) a 9,5 (atrás), en cinco columnas de roca de alturas
  distintas (13,5 a 20). Adentro, el túnel con el perfil de WST_Mine_Tunnel (8 x 8) y un puntal a z = 4; a
  partir de z = 8 las paredes son coal: la oscuridad de la mina (la transición pasa ahí).
- Piezas: Frame (pórtico, cartel, puntal de adentro y la vía: de z = 11,5 adentro hasta z = -14 con un tope),
  RockFace (el paredón tallado, la losa del piso de adentro y las piedras al pie), Tailings (montón de
  escoria a la derecha de la vía y la vagoneta oxidada cargada de mineral, sobre la vía en z = -9,5),
  Lanterns (ménsulas y armazones de los dos faroles), Lamp_Glow_1 (izquierda) y Lamp_Glow_2 (derecha): el
  vidrio encendido, aparte para prenderlos y apagarlos (como los demás faroles del Western).
- Inferido: la vía va en Frame y la vagoneta en Tailings (el prompt no los asigna), el túnel de 12 de
  hondo con el fondo negro, los estratos, las riostras, el tope al final de la vía, la vagoneta como versión
  simplificada de WST_Vehicle_MineCart y 9 materiales en total (cada objeto usa 1 a 4).

Vueltas: 1) z-fighting en faroles (montantes y base con el piso en y 6,1; brazo y planchuela), en el
labio de la vagoneta (con la tina en y 3,7) y en el entablado contra los montantes del cartel; 2614
triángulos: ruedas de la vagoneta de 8 lados y sin pestaña · 2) el túnel atravesaba el paredón (se veía el
agujero atrás), los estratos eran rayas de torta solo en el frente y las columnas se leían como bloques:
columnas de 14 puntos (frente abombado que se recuesta, tope biselado y cresta), 13 de hondo, túnel de
10,5 con fondo coal desde z = 6, bandas finas en todas las caras de afuera · 3) bandas sin corte propio
pintaban triángulos enteros (faltaban los cortes de 3,55 y 12,0); la escombrera era un cono puntudo:
tronco de cono con tope chato, dos lóbulos y grava suelta · 4) una piedra de grava flotaba al pie y tres
quedaban encerradas en la escombrera.

Revisión
- 2756 triángulos contra 1500 (calidad primero; es la pieza grande que recibe a los jugadores): RockFace
  1204 (cinco columnas, la boca tallada con su túnel y los estratos cortados), Tailings 756 (la vagoneta
  ~420 con mineral, la escombrera y la grava), Frame 552 (pórtico, cartel, puntal de adentro y 24 de vía:
  264 son los durmientes), Lanterns 220, Lamp_Glow 12 + 12.
- Medidas: 30,0 de ancho x 20,9 de alto (cresta del medio); 28,8 de hondo con la vía y la escombrera.
  Pórtico 10 x 9; paso libre de la boca 8,4 x 8,2 (el túnel de adentro 8 x 8).
- El punto más bajo (-0,63) son las piedras y la losa metidas en el piso: a propósito.
- 9 materiales en el modelo (redrock, ochre, stone_grey, coal, wood_dark, wood_light, iron, rust,
  lamp_glow); por objeto, de 1 a 5. El coal es la oscuridad del fondo de la boca.
- Dudoso: la vía va dentro de Frame y la vagoneta dentro de Tailings porque el prompt no les da objeto; si
  la vagoneta tiene que ser la jugable (WST_Vehicle_MineCart), se saca de acá.
"""

import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "mine_tunnel", Path(__file__).resolve().parents[2] / "WST_Mine_Tunnel" / "01_design" / "WST_Mine_Tunnel.build.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
RAILS = T.RAILS

RED, OCHRE, GREY, DARK = "redrock", "ochre", "stone_grey", "coal"
WOOD, PLANK, IRON, RUST = "wood_dark", "wood_light", "iron", "rust"
POST_X, POST_W = 4.6, 0.8
HEAD_Y0, HEAD_Y1 = 8.2, 9.0
RAIL_Z0, RAIL_Z1 = 10.2, -14.0
CART_Z = -9.5


# ---------------- paredón ----------------
# columnas de roca: (x0, x1, alto izq, alto der, frente, fondo, semilla)
COLUMNS = [(-15.0, -8.4, 12.4, 13.9, -0.6, 12.6, 1), (-9.8, -4.0, 15.6, 17.8, -1.6, 13.2, 2),
           (-5.6, 5.8, 19.2, 20.0, 0.2, 13.6, 3), (4.2, 10.2, 18.4, 15.8, -1.3, 13.0, 4), (9.0, 15.0, 15.2, 12.6, -0.7, 12.4, 5)]


def column_pts(x0, x1, h0, h1, zf, zb, seed, base):
    """Columna de roca: frente abombado a media altura, que se recuesta hacia arriba, tope biselado y
    una cresta; la espalda más baja."""
    r = T.Rng(seed)
    xm, hm = (x0 + x1) / 2, max(h0, h1)
    j = [r.u() for _ in range(12)]
    return [
        (x0, base, zf - 0.2 * j[0]), (x1, base, zf - 0.3 * j[1]),                             # pie
        (x0 + 0.3 * j[2], 0.42 * h0, zf - 0.55 - 0.3 * j[3]), (x1 - 0.3 * j[4], 0.5 * h1, zf - 0.45),  # panza
        (xm + (j[5] - 0.5) * 2.0, 0.3 * hm, zf - 0.85 - 0.3 * j[6]),
        (x0 + 0.5, 0.82 * h0, zf + 0.5 + 0.4 * j[7]), (x1 - 0.6, 0.8 * h1, zf + 0.4 + 0.5 * j[8]),   # se recuesta
        (x0 + 1.1, h0, zf + 2.2), (x1 - 1.2, h1, zf + 2.0),                                    # bisel del tope
        (xm + (j[9] - 0.5) * 1.5, hm + 0.3 + 0.5 * j[10], zf + 4.5),                           # cresta
        (x0, base, zb), (x1, base, zb - 0.4 * j[11]), (x0 + 0.6, h0 - 1.6, zb - 1.4), (x1 - 0.6, h1 - 1.4, zb - 1.2),
    ]


def rock_face(mk):
    p = mk.part("RockFace", (0, 0, 0))
    for i, (x0, x1, h0, h1, zf, zb, seed) in enumerate(COLUMNS):
        mk.hull(p, column_pts(x0, x1, h0, h1, zf, zb, seed, 0.006 * (i % 2)), RED)    # bases alternadas: no coplanares
    # hueco del pórtico (los postes quedan 0,05 metidos en la roca) y el túnel
    mk.carve(p, RED, points=[(sx * w, y, z) for sx in (-1, 1) for w, y in ((5.05, -0.35), (4.85, 9.35))
                             for z in (-4.0, 1.1)])
    pc = T.sunk(T.PC, T.FLOOR_CUT)
    fr = T.straight_frame
    mk.carve(p, GREY, points=T.section(fr(0, 0.9), pc) + T.section(fr(0, 6.05), T.jitter(pc, T.J["c"])))
    mk.carve(p, DARK, points=T.section(fr(0, 5.95), T.sunk(T.jitter(T.PC, T.J["c"]), T.FLOOR_CUT - 0.02))
             + T.section(fr(0, 10.5), T.sunk(T.scaled(T.PC, 0.9, 0.9), T.FLOOR_CUT - 0.02)))
    # estratos: cortes apenas inclinados y bandas pintadas solo en el frente
    for y, nx in ((2.7, 0.03), (3.55, 0.03), (5.8, -0.02), (7.4, 0.04), (11.2, -0.03), (12.0, -0.03), (13.6, 0.02),
                  (16.8, 0.0)):
        mk.slice(p, (0, y, 0), (nx, 1, 0))
    # bandas en todas las caras de afuera, sin entrar al túnel (|x| < 4,4 y hasta y 9,4 es la boca)
    for y0, y1, mat in ((2.7, 3.55, OCHRE), (5.8, 7.4, OCHRE), (11.2, 12.0, GREY), (13.6, 16.8, OCHRE)):
        for x0, x1 in ((-20.0, -4.4), (4.4, 20.0)) + (((-4.4, 4.4),) if y0 > 9.4 else ()):
            mk.paint(p, mat, box=(((x0 + x1) / 2, (y0 + y1) / 2, 6.0), (x1 - x0, y1 - y0, 20.0)))
    # piso de tierra adentro del túnel
    T.floor_slab(mk, p, T.rect_xz(-T.FLOOR_HALF, T.FLOOR_HALF, 0.6, 10.4))
    # piedras caídas al pie del paredón
    for i, (x, z, s, mat) in enumerate(((-13.0, -1.6, 1.6, RED), (-11.2, -2.1, 1.0, OCHRE), (-7.4, -2.2, 1.3, RED),
                                        (7.2, -2.0, 1.4, OCHRE), (12.2, -1.8, 1.8, RED), (13.8, -2.6, 0.9, RED),
                                        (-6.1, -1.9, 0.7, OCHRE))):
        T.chunk(mk, p, (x, 0.3 * s, z), (1.6 * s, 1.1 * s, 1.4 * s), 50 + i, rot=(0, 37 * i, 8), mat=mat)


# ---------------- pórtico, cartel y vía ----------------
def frame(mk):
    p = mk.part("Frame", (0, 0, 0))
    for sx in (-1, 1):
        mk.box(p, (sx * POST_X, (HEAD_Y0 + 0.04) / 2, 0), (POST_W, HEAD_Y0 + 0.04, POST_W), WOOD)          # poste
        mk.hull(p, [(sx * x, y, z) for z in (-0.2, 0.2) for x, y in ((4.15, 6.4), (4.15, 6.95), (2.55, 8.25),
                                                                     (3.15, 8.25))], WOOD)              # riostra
    mk.box(p, (0, (HEAD_Y0 + HEAD_Y1) / 2, 0), (10.0, HEAD_Y1 - HEAD_Y0, 0.86), WOOD)                     # cabezal
    # cartel en blanco: dos montantes sobre el cabezal y tres tablas claras, apenas torcido
    for sx in (-1, 1):
        mk.box(p, (sx * 2.4, 10.0, 0.05), (0.3, 2.04, 0.3), WOOD)
    rot = (0, 0, 2.5)
    for i, (y, w) in enumerate(((9.48, 6.0), (9.93, 5.94), (10.38, 6.04))):
        mk.box(p, (0.03 * i, y, -0.15), (w, 0.43, 0.12), PLANK, rot=rot)
    # entablado sobre el cabezal, hacia adentro del corte
    for x in (-3.1, -1.0, 1.0, 3.1):
        mk.box(p, (x, HEAD_Y1 + 0.07, 0.75), (1.5, 0.16, 1.6), WOOD)
    # puntal de adentro y vía
    T.timber_set(mk, p, T.straight_frame(0, 4.0), T.lerp_prof(T.PC, T.jitter(T.PC, T.J["c"]), 0.4))
    T.lagging(mk, p, [(T.straight_frame(0, 6.5), T.CAP_Y1), (T.straight_frame(0, 1.5), T.CAP_Y1)])
    RAILS.straight_track(mk, p, 0.0, RAIL_Z0, RAIL_Z1)
    # tope al final de la vía
    zb = RAIL_Z1 - 0.15
    mk.box(p, (0, 0.95, zb - 0.25), (3.9, 0.55, 0.5), WOOD)
    for sx in (-1, 1):
        mk.box(p, (sx * 1.5, 0.62, zb - 0.25), (0.42, 1.24, 0.42), WOOD)


# ---------------- vagoneta oxidada y escoria ----------------
def cart(mk, p, z0):
    """Vagoneta simplificada de WST_Vehicle_MineCart (misma tina y trocha), cargada de mineral."""
    y0 = RAILS.RAIL_Y1                                   # la vagoneta va sobre la cara del riel
    bot, top = 0.80, 3.20
    tan = math.tan(math.radians(10))
    hx_t, hz_t = 1.70, 2.50
    hx_b, hz_b = hx_t - (top - bot) * tan, hz_t - (top - bot) * tan
    mk.hull(p, [(sx * hx, y0 + y, z0 + sz * hz) for y, hx, hz in ((bot, hx_b, hz_b), (top, hx_t, hz_t))
                for sx in (-1, 1) for sz in (-1, 1)], RUST)
    t = 0.12
    mk.carve(p, IRON, points=[(sx * (hx - t), y0 + y, z0 + sz * (hz - t)) for y, hx, hz in
                               ((bot + 0.14, hx_b + 0.14 * tan, hz_b + 0.14 * tan), (top + 0.4, hx_t + 0.4 * tan, hz_t + 0.4 * tan))
                               for sx in (-1, 1) for sz in (-1, 1)])
    # relleno de mineral hasta casi el borde (las lajas apoyan encima)
    fy0, fy1 = bot + 0.13, top - 0.08
    mk.hull(p, [(sx * (hx_b + (y - bot) * tan - t - 0.005), y0 + y, z0 + sz * (hz_b + (y - bot) * tan - t - 0.005))
                for y in (fy0, fy1) for sx in (-1, 1) for sz in (-1, 1)], GREY, detail=True)
    # labio de hierro
    for s in (-1, 1):
        mk.box(p, (s * (hx_t + 0.02), y0 + top - 0.04, z0), (0.14, 0.16, 2 * hz_t + 0.12), IRON, detail=True)
        mk.box(p, (0, y0 + top - 0.04, z0 + s * (hz_t + 0.02)), (2 * hx_t - 0.1, 0.12, 0.14), IRON, detail=True)
    # mineral: lajas que asoman sobre el borde
    for i, (x, z, s) in enumerate(((-0.7, -1.2, 0.9), (0.6, -0.4, 1.0), (-0.3, 0.8, 0.95), (0.8, 1.4, 0.7), (-0.9, 0.2, 0.7))):
        T.chunk(mk, p, (x, y0 + top - 0.1, z0 + z), (1.3 * s, 0.9 * s, 1.2 * s), 70 + i, rot=(10, 41 * i, -12),
                mat=GREY if i % 2 else OCHRE)
    # bastidor, ejes y ruedas
    for s in (-1, 1):
        mk.box(p, (s * 0.95, y0 + 0.72, z0), (0.22, 0.22, 4.4), "wood_dark", detail=True)
    for az in (-1.55, 1.55):
        mk.cyl(p, (0, y0 + 0.5, z0 + az), 0.08, 3.3, IRON, axis="x", sides=6, detail=True)
        for sx in (-1, 1):
            mk.cyl(p, (sx * 1.47, y0 + 0.5, z0 + az), 0.52, 0.2, IRON, axis="x", sides=8, detail=True)
            mk.box(p, (sx * 1.16, y0 + 0.62, z0 + az), (0.24, 0.3, 0.3), RUST, detail=True)


def tailings(mk):
    p = mk.part("Tailings", (0, 0, 0))
    cart(mk, p, CART_Z)
    # montón de escoria: un tronco de cono bajo (las escombreras tienen el tope chato), dos lóbulos y
    # vetas ocres que bajan por la ladera (cortes inclinados + pintura)
    r = T.Rng(9)
    cx, cz = 9.0, -10.2
    pts = []
    for y, rx, rz, n in ((0.0, 4.8, 4.1, 14), (1.5, 3.4, 2.9, 10), (2.55, 1.9, 1.5, 8)):
        for k in range(n):
            a = 2 * math.pi * (k + 0.3 * r.u()) / n
            f = 1.0 + 0.16 * (r.u() - 0.5)
            pts.append((cx + rx * f * math.cos(a), y + (0.15 * r.u() if y > 0 else 0.0), cz + rz * f * math.sin(a)))
    mk.hull(p, pts, GREY)
    for i, (c, s) in enumerate((((5.4, 0.0, -7.0), 2.0), ((12.4, 0.0, -13.4), 2.2))):
        lob = [(c[0] + s * math.cos(a) * (0.9 + 0.2 * r.u()), 0.0, c[2] + s * 0.8 * math.sin(a)) for a in
               [2 * math.pi * k / 8 for k in range(8)]]
        lob += [(c[0] + 0.5 * s * math.cos(a), 0.55 * s, c[2] + 0.4 * s * math.sin(a)) for a in (0.3, 2.4, 4.4)]
        mk.hull(p, lob, GREY)
    for a_deg, off in ((20, 0.0), (75, 1.2), (140, -0.6), (230, 0.4), (300, -1.0)):
        a = math.radians(a_deg)
        mk.slice(p, (cx + off * math.cos(a + 1.57), 0, cz + off * math.sin(a + 1.57)), (math.sin(a), 0.0, -math.cos(a)))
    for c, rad in (((cx + 3.2, 1.0, cz + 1.4), 1.5), ((cx - 2.6, 1.0, cz - 2.2), 1.7), ((cx + 0.6, 2.5, cz + 0.3), 1.0),
                   ((cx - 3.4, 0.7, cz + 2.0), 1.3)):
        mk.paint(p, OCHRE, ball=(c, rad))
    # grava suelta en la ladera y al pie
    for i, (x, y, z, s) in enumerate(((6.0, 0.2, -12.9, 0.7), (12.6, 0.3, -9.2, 0.8), (8.0, 0.2, -6.0, 0.6),
                                      (13.0, 0.2, -11.8, 0.55), (9.6, 0.25, -14.4, 0.75), (10.8, 1.75, -8.0, 0.5),
                                      (6.9, 1.7, -11.8, 0.55), (9.6, 2.85, -10.4, 0.45), (4.6, 0.15, -9.6, 0.5))):
        T.chunk(mk, p, (x, y, z), (1.3 * s, 0.8 * s, 1.1 * s), 90 + i, rot=(12, 53 * i, 0),
                mat=OCHRE if i % 2 else GREY)


# ---------------- faroles ----------------
def lanterns(mk):
    p = mk.part("Lanterns", (0, 0, 0))
    for k, sx in enumerate((-1, 1)):
        x = sx * POST_X
        zp = -POST_W / 2                                   # cara del poste
        zl = -1.05                                         # el farol cuelga adelante del poste
        # ménsula: brazo de hierro que sale del poste y gancho
        mk.box(p, (x, 7.45, (zp + zl) / 2 - 0.02), (0.1, 0.1, abs(zl - zp) + 0.12), IRON)
        mk.box(p, (x, 7.77, zp + 0.02), (0.22, 0.7, 0.06), IRON)                                    # planchuela
        mk.hull(p, [(x + dx, 7.42, zl + dz) for dx in (-0.03, 0.03) for dz in (-0.03, 0.03)]
                + [(x + dx, 7.1, zl + dz) for dx in (-0.03, 0.03) for dz in (-0.03, 0.03)], IRON)   # gancho
        # farol: base, cuatro montantes, sombrero y asa
        yb, yt = 6.1, 6.82
        mk.box(p, (x, yb + 0.05, zl), (0.56, 0.1, 0.56), IRON)
        for dx in (-0.23, 0.23):
            for dz in (-0.23, 0.23):
                mk.box(p, (x + dx, (yb + 0.02 + yt) / 2, zl + dz), (0.07, yt - yb - 0.02, 0.07), IRON)
        mk.hull(p, [(x + dx, yt - 0.03, zl + dz) for dx in (-0.31, 0.31) for dz in (-0.31, 0.31)]
                + [(x, yt + 0.22, zl)], IRON)
        mk.hull(p, [(x + dx, yt + 0.15, zl) for dx in (-0.05, 0.05)] + [(x + dx, 7.14, zl + dz) for dx in (-0.04, 0.04)
                                                                         for dz in (-0.02, 0.02)], IRON)
        g = mk.part(f"Lamp_Glow_{k + 1}", (x, yb + 0.1, zl))
        mk.box(g, (x, (yb + 0.08 + yt) / 2, zl), (0.42, yt - yb - 0.1, 0.42), "lamp_glow")


def build(mk):
    rock_face(mk)
    frame(mk)
    tailings(mk)
    lanterns(mk)

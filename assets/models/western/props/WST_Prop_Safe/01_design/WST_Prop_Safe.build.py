"""
Receta de WST_Prop_Safe, la caja fuerte de hierro (prompt 041, Bloques A + C).

Brief
- Silueta a 40 studs: un bloque de hierro pesado de 2,6 x 3,2 x 2,4 sobre cuatro patas petisas, aristas
  verticales achaflanadas a 45°, marco rojo alrededor de la puerta con filete de bronce, placa de bronce
  arriba, y en la puerta un dial grande de bronce y un volante de 4 rayos de acero.
- Medidas: patas 0,2 de alto; fondo 0,2-0,5, boca de la puerta 0,5-2,9 (2,4), losa de arriba 2,9-3,2;
  paredes de 0,3 (la boca queda en 2,0 de ancho, el tamaño de la puerta); chaflanes de 0,15 en planta.
- Fragmentos (origen común abajo al centro): frag01 arriba (losa, placa y el filete de arriba), frag02
  pared izquierda, frag03 pared derecha (cada una con su tramo de marco y filete), frag04 atrás + fondo
  (pared de atrás, losa del fondo, patas, los dos estantes y el filete de abajo). La puerta es Door, con
  el origen en la bisagra (+X, adelante: x = 1,0, z = -1,15, abajo de la puerta) y 0,05 hundida.
- Marco rojo: la cara de adelante de cada fragmento y sus chaflanes del frente, pintados (sin calcomanía).
  Filete de bronce de 0,04 que sobresale 0,02 (lo pide el prompt), a 0,055 de la boca.
- Interior hueco con paredes de 0,3 y dos estantes de hierro (y 1,3 y 2,1).
- Inferido: alto de las patas, posición del dial (arriba) y del volante (abajo), las bisagras a la vista,
  la puerta de hierro con el frente achaflanado, estantes de hierro, sin grietas en zigzag (es hierro
  entero hasta que la vuela la dinamita; los cortes siguen las aristas de la caja).

Vueltas: 1) z-fighting en los cuatro fragmentos: el filete metido 0,005 en la cara dejaba sus puntas en
el mismo plano que las caras de arriba y abajo del fragmento · 2) filete apoyado en la cara.

Revisión
- 472 triángulos contra 500 (puerta 200: dial, volante, bisagras; frag04 148: patas, estantes, filete).
- Paredes de 0,3: el prompt las pide así, aunque el Bloque C pide 0,4 de mínimo por fragmento (cada pared
  mide 0,3 x 2,4 x 2,05; la losa y el fondo, 0,3 de alto).
- Profundidad 2,475: el dial y el volante sobresalen 0,075 del frente.
- Los costados quedan lisos (hierro oscuro): la lectura está en el frente rojo, la silueta y las patas.
"""

import math

HX, HZ, C = 1.3, 1.2, 0.15         # media planta y chaflán de las aristas verticales
T = 0.3                            # paredes, losas
Y_FOOT, Y_BOT, Y_TOP, H = 0.2, 0.5, 2.9, 3.2
E = 0.003                          # encime: dos cascos de una pieza nunca comparten vértices
ZF = -HZ                           # cara de adelante
SX = 1.075                         # filete: centro, a 0,055 de la boca (x = 1,0)
SW, SP = 0.04, 0.02                # filete: ancho y espesor, apoyado en la cara (metido, sus puntas coincidían con las
                                   # caras de arriba y abajo del fragmento: z-fighting medido)


# ---- geometría 2D (planta x, z) ----
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _inter(p, q, a, b):
    d1, d2 = _cross(a, b, p), _cross(a, b, q)
    t = d1 / (d1 - d2)
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def clip(subject, clipper):
    """Sutherland-Hodgman con clipper convexo en sentido antihorario."""
    out = list(subject)
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            pin, qin = _cross(a, b, p) >= -1e-9, _cross(a, b, q) >= -1e-9
            if qin:
                if not pin:
                    out.append(_inter(p, q, a, b))
                out.append(q)
            elif pin:
                out.append(_inter(p, q, a, b))
    clean = []
    for p in out:
        if not clean or abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    return clean


def rect(x0, x1, z0, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def footprint(hx=HX, hz=HZ, c=C):
    return [(-hx + c, -hz), (hx - c, -hz), (hx, -hz + c), (hx, hz - c),
            (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c)]


def slab(mk, part, poly, y0, y1, mat="iron"):
    mk.prism(part, poly, y1 - y0, mat, plane="xz", center=(0, (y0 + y1) / 2, 0))


def red_front(mk, part, x0=-HX - 0.01, x1=HX + 0.01):
    """Pinta de rojo la cara de adelante y los chaflanes del frente: centros entre z = -1,205 y -1,04 (deja
    afuera los cantos del filete y la placa, en -1,2075) y arriba de las patas (sus caras de adelante)."""
    mk.paint(part, "paint_red", box=(((x0 + x1) / 2, (Y_FOOT + 0.01 + H + 0.05) / 2, -1.1225),
                                     (x1 - x0, H + 0.04 - Y_FOOT, 0.165)))


def stripe_u(y_bar, y_end):
    """Filete en U (x, y): barra horizontal en y_bar y dos patitas hasta y_end (el borde del fragmento)."""
    a, b = SX + SW / 2, SX - SW / 2
    s = 1 if y_end > y_bar else -1
    y0, y1 = y_bar - s * SW / 2, y_bar + s * SW / 2
    return [(-a, y_end), (-a, y0), (a, y0), (a, y_end), (b, y_end), (b, y1), (-b, y1), (-b, y_end)]


def build(mk):
    zs = ZF - SP / 2                             # centro del filete, apoyado en la cara de adelante

    # ---------------- frag01: losa de arriba, placa, filete de arriba ----------------
    top = mk.part("frag01", (0, 0, 0))
    slab(mk, top, footprint(), Y_TOP, H)
    mk.prism(top, stripe_u(Y_TOP + 0.05, Y_TOP), SP, "brass", plane="xy", center=(0, 0, zs))
    mk.box(top, (0, 3.085, ZF - 0.015), (0.8, 0.15, 0.04), "brass")                              # placa
    red_front(mk, top)

    # ---------------- frag02 / frag03: paredes con su tramo de marco y filete ----------------
    for name, s in (("frag02", -1), ("frag03", 1)):
        p = mk.part(name, (0, 0, 0))
        x0, x1 = sorted((s * (HX + 0.1), s * (HX - T)))
        slab(mk, p, clip(footprint(), rect(x0, x1, -HZ - 0.1, HZ - T)), Y_BOT, Y_TOP)
        mk.box(p, (s * SX, (Y_BOT + Y_TOP) / 2, zs), (SW, Y_TOP - Y_BOT, SP), "brass")
        red_front(mk, p, *sorted((s * (HX + 0.01), s * (HX - T - 0.01))))

    # ---------------- frag04: atrás + fondo, patas, estantes, filete de abajo ----------------
    back = mk.part("frag04", (0, 0, 0))
    slab(mk, back, footprint(), Y_FOOT, Y_BOT)
    inner = footprint(HX - E, HZ - E, C)                                    # metida E: no comparte vértices con la losa
    slab(mk, back, clip(inner, rect(-HX, HX, HZ - T, HZ)), Y_BOT - 0.02, Y_TOP)
    for x in (-0.95, 0.95):
        for z in (-0.85, 0.85):
            mk.box(back, (x, (Y_FOOT + 0.02) / 2, z), (0.42, Y_FOOT + 0.02, 0.42), "iron", top=(1.15, 1.15))
    for y in (1.3, 2.1):
        mk.box(back, (0, y, (-0.85 + HZ - T + 0.02) / 2), (2 * (HX - T - E), 0.06, HZ - T + 0.02 + 0.85), "iron")
    mk.prism(back, stripe_u(Y_BOT - 0.05, Y_BOT), SP, "brass", plane="xy", center=(0, 0, zs))
    red_front(mk, back)

    # ---------------- puerta: bisagra a la derecha, origen en el eje ----------------
    hinge = (HX - T, Y_BOT, ZF + 0.05)
    door = mk.part("Door", hinge)
    zd0, zd1 = ZF + 0.05, ZF + 0.3                                           # frente (hundido 0,05) y atrás
    d = HX - T - E
    mk.hull(door, [(x, y, zd1) for x in (-d, d) for y in (Y_BOT + E, Y_TOP - E)]
            + [(x, y, zd0) for x in (-d + 0.07, d - 0.07) for y in (Y_BOT + 0.07, Y_TOP - 0.07)], "iron")
    mk.cyl(door, (0, 2.15, zd0 - 0.03), 0.24, 0.07, "brass", axis="z", sides=10)                # dial
    mk.cyl(door, (0, 2.15, zd0 - 0.09), 0.08, 0.07, "brass", axis="z", sides=6)                 # perilla del dial
    yw = 1.35                                                                                    # volante
    mk.cyl(door, (0, yw, zd0 - 0.05), 0.1, 0.12, "steel_light", axis="z", sides=6)
    for k, dz in ((0, 0.06), (1, 0.05)):
        mk.box(door, (0, yw, zd0 - 0.06), (0.7, 0.06, dz), "steel_light", rot=(0, 0, 45 + 90 * k))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        mk.box(door, (0.35 * math.cos(a), yw + 0.35 * math.sin(a), zd0 - 0.07), (0.09, 0.09, 0.1), "steel_light")
    for y in (0.95, 2.45):                                                                      # bisagras
        mk.cyl(door, (hinge[0], y, hinge[2]), 0.09, 0.35, "iron", sides=6)

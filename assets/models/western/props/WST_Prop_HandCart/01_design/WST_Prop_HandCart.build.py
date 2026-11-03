"""
Receta de WST_Prop_HandCart, la carretilla de mano para mercadería (prompt 130, Bloques A + B).

Brief
- Silueta a 40 studs: caja chata sobre dos ruedas grandes de rayos (asoman por arriba de la caja), dos
  varas largas hacia adelante con el travesaño de tirar, bolsas claras adentro.
- Medidas: caja 2,5 (X) x 4 (Z), piso a 1,6 (arriba del eje), ruedas de 2,4 de diámetro (eje a 1,2,
  en z = +0,6, un poco atrás del centro), varas de 7,1 de largo que salen 3 studs por delante de la caja.
  Dos patas adelante: en reposo la caja queda horizontal.
- Piezas: Body (todo lo fijo, origen en la base) y Wheels (las dos ruedas y el eje, origen en el eje:
  giran juntas). El vacío raíz ya se llama WST_Prop_HandCart, por eso el cuerpo es "Body", como en los
  vehículos.
- Ruedas: pina de 10 tramos en dos prismas (con dos junturas de 0,4°) y llanta de hierro pintada,
  8 rayos (4 barras que cruzan el cubo), cubo de 6 lados. Más simples que las de la carreta (12 rayos):
  esta es chica.
- Inferido: patas adelante; varas que corren bajo la caja y son las manijas; tablas laterales bajas
  (0,5) y una cabecera adelante (0,8); dos bolsas acostadas y una parada; juntas del piso pintadas.

Vueltas: 1) las bolsas acostadas medían 0,30 de alto dentro de tablas de 0,5: no se veían · 2) bolsas de
radio 0,55 achatadas a 0,75 (~0,8 de alto): asoman sobre el borde.

Revisión
- 632 triángulos contra 300 de referencia: Wheels 332 (cada rueda 160: pina 88, 8 rayos 48, cubo 20,
  más el eje) y Body 300 (tres bolsas con atadura ~130). Una rueda de rayos que se lea como rueda no
  entra en menos; con 8 tramos de pina se vería octogonal a 10 studs.
- Medidas: caja 2,5 x 4 (con tablas 2,48), ruedas 2,4, conjunto 3,4 x 2,77 x 7,1 (las varas salen 3
  adelante de la caja). Origen de Wheels en el eje (0, 1,2, 0,6).
"""

import math

from mathutils import Euler, Vector

AXLE = (0.0, 1.2, 0.6)
R_W = 1.2
X_W = 1.5
FLOOR = (1.35, 1.6)
BED_X, BED_Z = 1.25, 2.0


def _mat(rot):
    return Euler([math.radians(a) for a in rot], "XYZ").to_matrix()


def tube(mk, part, a, b, r, mat, sides=4):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    u = d.cross(Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = d.cross(u)
    mk.hull(part, [tuple(p + r * (math.cos(t) * u + math.sin(t) * v)) for p in (a, b)
                   for t in (2 * math.pi * (k + 0.5) / sides for k in range(sides))], mat)


def wheel(mk, part, hub, radius, n=5, bars=4, hub_len=0.4, width=0.22):
    """Rueda con el eje en X: pina en dos prismas con llanta pintada, `bars` barras (2 rayos cada una), cubo."""
    def W(a, b, d):                                      # (z, y) del plano de la rueda, d a lo largo del eje
        return (hub[0] + d, hub[1] + b, hub[2] + a)

    r_out, r_in, gap = radius, radius - 0.2, 0.4
    for a0, a1 in ((gap, 180 - gap), (180 + gap, 360 - gap)):
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([(r_out * math.cos(math.radians(a)), r_out * math.sin(math.radians(a))) for a in angs]
                + [(r_in * math.cos(math.radians(a)), r_in * math.sin(math.radians(a))) for a in reversed(angs)])
        mk.prism(part, prof, width, "wood_mid", plane="zy", center=hub)
        for i in range(n):                               # llanta: caras de afuera de la pina
            m, h = (angs[i] + angs[i + 1]) / 2, (angs[i + 1] - angs[i]) / 2
            rr = r_out * math.cos(math.radians(h))
            mk.paint(part, "iron", ball=(W(rr * math.cos(math.radians(m)), rr * math.sin(math.radians(m)), 0), 0.05))
    L = r_in + 0.05
    for k in range(bars):
        a = math.radians(180 / bars * k + 90 / bars)
        c, s = math.cos(a), math.sin(a)
        mk.hull(part, [W(t * c - w * s, t * s + w * c, d) for t in (-L, L) for w in (-0.065, 0.065)
                       for d in (-0.05, 0.05)], "wood_mid")
    mk.hull(part, [W(0.22 * math.cos(math.radians(60 * k + 30)), 0.22 * math.sin(math.radians(60 * k + 30)), d)
                   for k in range(6) for d in (-hub_len / 2, hub_len / 2)], "wood_dark")


def sack(mk, part, base, axis, length, r):
    """Bolsa: casco de 4 anillos de 5 puntos a lo largo de `axis`, achatada contra lo que la sostiene."""
    ax = Vector(axis).normalized()
    up = Vector((0, 1, 0))
    if abs(ax.dot(up)) > 0.9:                            # parada: la sección es redonda
        u, v, flat = Vector((1, 0, 0)), Vector((0, 0, 1)), 1.0
    else:
        u, v, flat = ax.cross(up).normalized(), up, 0.75
    c = Vector(base)
    pts = []
    for s, k in ((0.0, 0.8), (0.25, 1.0), (0.75, 0.95), (1.0, 0.6)):
        for j in range(5):
            a = 2 * math.pi * j / 5 + 1.5 * math.pi
            off = 0.0 if flat == 1.0 else r * flat           # acostada: el punto de abajo toca el piso
            pts.append(tuple(c + ax * (s * length) + u * (r * k * math.cos(a)) + v * (r * k * flat * math.sin(a) + off)))
    mk.hull(part, pts, "canvas")
    tip = c + ax * (length + 0.14) + (v * r * flat if flat != 1.0 else Vector())
    tube(mk, part, tuple(c + ax * (length - 0.05) + (v * r * flat if flat != 1.0 else Vector())), tuple(tip), 0.11,
         "rope")


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    # ---- piso con dos juntas pintadas (tablas a lo largo) ----
    mk.box(body, (0, sum(FLOOR) / 2, 0), (2 * BED_X, FLOOR[1] - FLOOR[0], 2 * BED_Z), "wood_mid")
    for x in (-0.42, 0.42):
        mk.slice(body, (x - 0.03, 0, 0), (1, 0, 0))
        mk.slice(body, (x + 0.03, 0, 0), (1, 0, 0))
        mk.paint(body, "wood_dark", box=((x, FLOOR[1], 0), (0.06, 0.02, 2 * BED_Z + 0.1)))
    # ---- tablas laterales bajas y cabecera ----
    for s in (-1, 1):
        # 0,01 adentro del borde del piso y encimadas 0,01 en él: ni caras coplanares ni vértices que se suelden
        mk.box(body, (s * (BED_X - 0.07), FLOOR[1] + 0.245, 0), (0.12, 0.51, 2 * BED_Z - 0.02), "wood_light")
    mk.box(body, (0, FLOOR[1] + 0.395, -BED_Z + 0.075), (2 * BED_X - 0.26, 0.81, 0.12), "wood_light")
    # ---- varas: corren bajo la caja y salen adelante como manijas; travesaño para tirar ----
    for s in (-1, 1):
        mk.box(body, (s * 1.0, 1.4 - 0.005, -1.45), (0.2, 0.2, 7.1), "wood_dark")
        mk.box(body, (s * 1.0, 0.65, -1.6), (0.18, 1.3, 0.18), "wood_dark")         # patas (se meten 0,005 en la vara)
    mk.cyl(body, (0, 1.4, -4.88), 0.09, 2.36, "wood_dark", axis="x", sides=6)      # travesaño
    # ---- bolsas ----
    # gordas (0,8 de alto): con 0,3 quedaban escondidas detrás de las tablas de 0,5 (vuelta 1)
    sack(mk, body, (-0.8, FLOOR[1], 1.15), (1, 0, 0.1), 1.5, 0.55)
    sack(mk, body, (-0.5, FLOOR[1], -1.8), (0.15, 0, 1), 1.5, 0.52)
    sack(mk, body, (0.62, FLOOR[1] - 0.02, -1.0), (0, 1, 0), 1.05, 0.38)

    # ---- ruedas y eje (giran juntas, origen en el eje) ----
    w = mk.part("Wheels", AXLE)
    for s in (-1, 1):
        wheel(mk, w, (s * X_W, AXLE[1], AXLE[2]), R_W)
    mk.cyl(w, AXLE, 0.1, 2 * X_W + 0.3, "iron", axis="x", sides=6)

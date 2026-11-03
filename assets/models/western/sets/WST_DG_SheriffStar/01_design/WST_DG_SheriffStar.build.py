"""
Receta de WST_DG_SheriffStar, la estrella del sheriff en primer plano (prompt 084, Bloques A + B).

Brief
- Cierre de Dusty Gulch: "la estrella del sheriff cae al polvo", vista a pantalla completa. Tiene que leerse
  como una placa de metal pesada y gastada: estrella de seis puntas con bolitas, brazos facetados con una
  cresta al medio que agarra la luz, anillo en relieve y la placa del centro lisa (para el decal).
- Medidas: 0,45 de punta a punta (centro de las bolitas a 0,2, bolitas de 0,027), 0,06 de espesor (de la
  espalda en z = 0 al frente del anillo en z = -0,06). Frente hacia -Z, una punta para arriba.
- Pieza: Body (el vacío raíz ya lleva el id). Origen en el centro de la estrella, en la espalda: es un
  objeto que cae y gira, no se apoya (por eso el punto más bajo no está en y = 0).
- Construcción: cada brazo es un casco (espalda en forma de cometa, cresta del centro a la punta y bordes
  más bajos) con la espalda a una profundidad distinta (0,0015 por brazo) y las muescas corridas 0,003 hacia
  su eje: así ningún brazo comparte vértices ni caras con el vecino. El anillo es dos medias coronas; la
  placa del centro queda 0,006 más baja que el anillo, sobre un disco gunmetal que hace de surco.
- Daño: el brazo de arriba a la derecha doblado 10° hacia el frente (gira sobre la línea de sus muescas),
  una abolladura tallada en el brazo de abajo y el roce de una bala en diagonal sobre el brazo de abajo a la
  izquierda y el anillo, tallado en gunmetal (más hondo donde pegó primero).
- Alfiler atrás: bisagra, aguja gunmetal y gancho.
- Inferido: origen en el centro, espesores de cada capa, qué brazo se dobla, dónde van la abolladura y el
  roce (lejos de la placa, para no tapar el decal), forma del alfiler.

Vueltas: 1) 884 tris: la abolladura y el roce unían en una booleana todos los cascos; el roce mordía la
bolita de la punta; el alfiler asomaba por los costados de frente · 2) en la base solo los dos brazos
dañados y el anillo (lo demás, detalle), roce corrido hacia adentro, alfiler más arriba: 546.

Revisión
- 546 triángulos contra 200 (calidad primero: se ve a pantalla completa). Bolitas 6 x 20, anillo ~100,
  placa y surco ~90, brazos facetados ~85, alfiler ~40, tallas ~100. Con bolitas octaédricas bajaría ~70
  pero a pantalla completa se ven cuadradas.
- Medidas: 0,40 x 0,45 x 0,086 (de punta a punta 0,45 en vertical; en horizontal, entre bolitas, 0,40,
  como toda estrella de seis puntas con una punta arriba; el espesor pasa de 0,06 por el alfiler de atrás
  y el brazo doblado).
- Aviso aceptado: el punto más bajo no está en y = 0 (origen en el centro a propósito).
- Dudoso: el roce de bala solo marca las partes altas (cresta y anillo), como un roce real; de lejos es
  una mancha oscura, no una raya continua.
"""

import math

from mathutils import Matrix, Vector

STEEL, DARK = "steel_light", "gunmetal"
R_TIP, R_IN = 0.2, 0.2 / math.sqrt(3)
BALL = 0.027
ANGLES = [90 + 60 * k for k in range(6)]          # 90 arriba, 150, 210, 270 abajo, 330, 30
BENT = 5                                          # el de 30° (arriba a la derecha)
CARVED = (2, 3)                                   # brazos con roce (210°) y abolladura (270°)


def v2(a_deg, r):
    a = math.radians(a_deg)
    return Vector((r * math.cos(a), r * math.sin(a)))


def arm_points(k):
    """Puntos (juego) de un brazo y el centro de su bolita."""
    th = ANGLES[k]
    u = v2(th, 1.0)
    v = Vector((-u.y, u.x))
    zb = -0.0015 * k                                  # espalda: cada brazo a otra profundidad
    nl = v2(th + 30, R_IN) - v * 0.003
    nr = v2(th - 30, R_IN) + v * 0.003
    tip = u * R_TIP
    pts = []
    for p2, z in ((Vector((0, 0)), zb), (nl, zb), (tip, zb), (nr, zb)):             # espalda
        pts.append((p2.x, p2.y, z))
    for p2, z in ((nl, -0.02), (nr, -0.02), (tip, -0.026)):                         # bordes
        pts.append((p2.x, p2.y, z))
    for p2, z in ((u * 0.012, -0.05), (u * 0.17, -0.036)):                          # cresta (no en el centro exacto)
        pts.append((p2.x, p2.y, z))
    ball = (tip.x, tip.y, -0.016)
    hinge = ((nl.x, nl.y, -0.01), (nr.x, nr.y, -0.01))
    return pts, ball, hinge


def bend(points, hinge, deg):
    a, b = Vector(hinge[0]), Vector(hinge[1])
    rot = Matrix.Rotation(math.radians(deg), 3, (b - a).normalized())
    return [tuple(rot @ (Vector(p) - a) + a) for p in points]


def build(mk):
    p = mk.part("Body", (0, 0, 0))
    for k in range(6):
        pts, ball, hinge = arm_points(k)
        if k == BENT:                                   # el doblado: la punta se viene 10° hacia -Z
            tip_z = {s: bend([ball], hinge, s * 10)[0][2] for s in (-1, 1)}
            s = min(tip_z, key=tip_z.get)
            pts = bend(pts, hinge, s * 10)
            ball = bend([ball], hinge, s * 10)[0]
        mk.hull(p, pts, STEEL, detail=k not in CARVED)             # solo lo que se talla queda en la base
        mk.ball(p, ball, BALL, STEEL, scale=(1, 1, 0.85), subdiv=0, detail=True)
    # anillo en relieve: dos medias coronas (con juntas de 0,4° para no compartir vértices)
    r_out, r_in, n = 0.094, 0.072, 6
    for a0, a1 in ((0.4, 179.6), (180.4, 359.6)):
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([tuple(v2(a, r_out)) for a in angs] + [tuple(v2(a, r_in)) for a in reversed(angs)])
        mk.prism(p, prof, 0.032, STEEL, plane="xy", center=(0, 0, -0.044))
    mk.cyl(p, (0, 0, -0.038), 0.074, 0.016, DARK, axis="z", sides=12, detail=True)  # surco alrededor de la placa
    mk.cyl(p, (0, 0, -0.047), 0.066, 0.014, STEEL, axis="z", sides=12, detail=True) # placa (para el decal)
    # abolladura en el brazo de abajo
    u = v2(ANGLES[3], 1.0)
    vv = Vector((-u.y, u.x))
    c = u * 0.125 + vv * 0.014
    mk.carve(p, STEEL, points=mk.pts_ball((c.x, c.y, -0.052), 0.028, scale=(1, 1, 0.75), subdiv=1))
    # roce de bala: en diagonal sobre el brazo de abajo a la izquierda y el anillo, más hondo al principio
    p1, p2 = Vector((-0.14, -0.07)), Vector((-0.065, 0.06))
    n_ = Vector((-(p2 - p1).y, (p2 - p1).x)).normalized() * 0.007
    cut = []
    for q, zin in ((p1, -0.022), (p2, -0.052)):
        for w in (n_, -n_):
            cut += [(q.x + w.x, q.y + w.y, zin), (q.x + w.x * 2.2, q.y + w.y * 2.2, -0.09)]
    mk.carve(p, DARK, points=cut)
    # alfiler atrás
    mk.box(p, (-0.085, 0.06, 0.009), (0.035, 0.035, 0.026), STEEL, detail=True)    # bisagra
    mk.cyl(p, (0.005, 0.06, 0.018), 0.008, 0.2, DARK, axis="x", sides=6, detail=True)  # aguja
    mk.box(p, (0.095, 0.06, 0.01), (0.03, 0.04, 0.028), STEEL, detail=True)        # gancho

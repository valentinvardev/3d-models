"""
Receta de WST_Mine_GasPocket, la ampolla de roca con gas que revienta con un tiro o fuego (prompt 106,
Bloques A + C).

Brief
- Lo que se lee: una ampolla de roca oscura hinchada en la pared, partida en gajos por grietas que brillan
  amarillo enfermizo (paint_mustard: el VFX la ilumina) y que se juntan en un cráter en la punta. Avisa
  que se puede reventar.
- Medidas: 3 de ancho (x) x 2,5 de alto (y), sobresale 1,5 de la pared (la espalda en z = 0, el frente
  hacia -Z). Origen en el centro de la espalda (se apoya en la pared, como las lajas de WST_Mine_SilverVein).
- Fragmentos (4, origen común): gajos cortados por planos que pasan por el eje, con caras de contacto
  exactas (los dos vecinos usan los mismos puntos). Sin booleanas: cada gajo trae el chanfle de su borde
  (los puntos del corte están 0,16 adentro de la superficie y los de al lado, corridos medio ancho de
  grieta), así entre dos gajos queda un surco en V; en el fondo del surco va una tira paint_mustard metida
  (no pegada encima), que es de uno de los dos gajos. Las cuatro grietas bajan a un cráter en la punta.
  La grieta de abajo a la izquierda es la mayor (0,15 de medio ancho): ahí va _GasVent.
- Inferido: el origen en la espalda, los ángulos de las grietas, el cráter de la punta, las grietas como
  cortes rectos que van del borde a la punta (zigzaguear el corte rompería la regla de gajos convexos
  sin huecos), el color de la roca.

Vueltas: 1) con surcos tallados (booleanas, 8 cortadores por gajo) daba 1156 triángulos y bordes rotos
donde las cuatro grietas se juntan en la punta · 2) sin booleanas: el chanfle en V sale de los puntos del
casco y la grieta es una tira metida en el fondo; los tramos de la tira compartían vértices (se soldaban) y
la pieza del cráter era plana · 3) tramos estirados 0,04 con profundidad alternada, tira que no arranca al
ras de la pared (coplanar con la espalda) y sin la pieza del cráter.

Revisión
- 372 triángulos contra 300 (+24 %): cuatro gajos de ~60 y cuatro tiras de grieta de ~36. Menos que eso
  deja la ampolla redonda sin facetas.
- Medidas: 2,99 x 2,49, sobresale 1,48. Gajos (medidos) de 24,5 a 25,4 % del volumen cada uno.
- Dudoso (Valentin): las grietas son rectas y radiales (del borde a la punta), no en zigzag: con gajos
  convexos y caras de contacto exactas, un corte en zigzag deja huecos o encimes. Si se prefiere zigzag,
  se pierde la regla de casco convexo por gajo.
"""

import math

from mathutils import Vector

ROCK, ROCK2, GLOW = "stone_grey", "redrock_dark", "paint_mustard"
RX, RY, RZ = 1.5, 1.25, 1.5
CRACKS = [(28.0, 0.09), (118.0, 0.09), (212.0, 0.15), (300.0, 0.1)]      # ángulo y medio ancho en la superficie
DEPTH = 0.16                                                             # fondo de la V
RINGS = (0.0, 28.0, 55.0, 74.0)
N_RING = 4


def dome(theta, phi):
    t, p = math.radians(theta), math.radians(phi)
    return Vector((RX * math.cos(p) * math.cos(t), RY * math.cos(p) * math.sin(t), -RZ * math.sin(p)))


def normal(p):
    n = Vector((p.x / RX ** 2, p.y / RY ** 2, p.z / RZ ** 2))
    if n.length < 1e-9:
        return Vector((0, 0, -1))
    n.normalize()
    if abs(p.z) < 1e-6:                                  # en la espalda, el borde: hacia afuera en el plano de la pared
        n = Vector((n.x, n.y, 0)).normalized()
    return n


def bump(theta, phi):
    return 0.05 * math.sin(3.1 * math.radians(theta) + 1.3) * math.sin(2 * math.radians(phi))


def boundary(theta, phi):
    """Punto del corte: sobre el meridiano theta, DEPTH adentro de la superficie."""
    p = dome(theta, phi)
    return p - normal(p) * DEPTH


def crater():
    return Vector((0.0, 0.0, -RZ + DEPTH + 0.06))


def half_angle(w, phi):
    return math.degrees(w / max(0.25, RX * math.cos(math.radians(phi))))


def sector_points(k):
    t0, w0 = CRACKS[k]
    t1, w1 = CRACKS[(k + 1) % 4]
    if t1 < t0:
        t1 += 360.0
    pts = []
    for phi in RINGS:
        a0, a1 = t0 + half_angle(w0, phi), t1 - half_angle(w1, phi)
        for i in range(N_RING + 1):
            th = a0 + (a1 - a0) * i / N_RING
            p = dome(th, phi)
            pts.append(tuple(p * (1.0 + (bump(th, phi) if phi > 0 else 0.0))))
        pts.append(tuple(boundary(t0, phi)))
        pts.append(tuple(boundary(t1, phi)))
    pts.append(tuple(crater()))
    pts.append((0.0, 0.0, 0.0))
    return pts


def glow_strip(mk, part, theta, w):
    """Tira mustard en el fondo de la V, de la espalda hasta el borde del cráter. Cada tramo se estira 0,04 sobre el
    siguiente y alterna 0,006 de profundidad (sin vértices compartidos ni caras coplanares)."""
    side = Vector((-math.sin(math.radians(theta)), math.cos(math.radians(theta)), 0))
    for i in range(len(RINGS) - 1):
        pts = []
        e = 0.006 * (i % 2)
        for j, phi in enumerate((RINGS[i], RINGS[i + 1])):
            p = dome(theta, phi + (0.6 if (i == 0 and j == 0) else 0.0))     # no al ras de la pared (coplanar)
            if j == 1 and i < len(RINGS) - 2:
                p = dome(theta, phi + math.degrees(0.04 / RZ))
            n = normal(p)
            for d in (DEPTH - 0.012 - e, DEPTH * 0.45 + e):
                ww = w * 0.5 * (1 - d / DEPTH) + 0.012
                pts += [tuple(p - n * d + side * ww), tuple(p - n * d - side * ww)]
        mk.hull(part, pts, GLOW)


def build(mk):
    for k in range(4):
        p = mk.part(f"frag{k + 1:02d}", (0, 0, 0))
        mk.hull(p, sector_points(k), ROCK2)
        mk.paint(p, ROCK, ball=(tuple(dome(CRACKS[k][0] + 45, 45) * 1.02), 0.32))
        glow_strip(mk, p, CRACKS[k][0], CRACKS[k][1])       # cada gajo lleva la tira de su borde izquierdo
    a = dome(CRACKS[2][0], 40) - normal(dome(CRACKS[2][0], 40)) * 0.05
    mk.marker("_GasVent", tuple(a))

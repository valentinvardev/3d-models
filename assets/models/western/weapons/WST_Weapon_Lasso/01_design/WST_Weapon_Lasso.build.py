"""
Receta de WST_Weapon_Lasso, el lazo enrollado en la mano (prompt 032, Bloques A + F).

Brief
- Silueta a 30 studs: un rollo de soga de 1,1 de diámetro con las vueltas abiertas en abanico abajo, la
  mano (cuero) arriba y el lazo corredizo de 0,9 colgando debajo con el nudo (honda) a la vista.
- Medidas: 4 vueltas de soga de 0,08 de grosor, sección de 8 lados, 1,1 de diámetro por fuera; lazo de
  0,9; nudo de 0,15. El rollo está en el plano XY (de frente se ve redondo), como pide el prompt.
- Piezas: Coil (4 vueltas + la vuelta de cuero donde agarra la mano; origen = la mano) y Noose (lazo +
  honda + el tramo que sube al rollo; origen en el nudo, de donde cuelga). Marcadores _Grip (la mano) y
  _Noose (el nudo).
- Cada vuelta es un anillo de 12 tramos (cascos de dos octógonos que se encastran 0,5°): las caras de dos
  tramos vecinos nunca son paralelas porque cambia la dirección del tramo.

Inferido (el prompt no lo dice o no cierra)
- "Plano XY, mirando al costado": se siguió el plano XY (de frente y de atrás se ve el aro, que es lo que
  ve la cámara en tercera persona). Si tiene que verse redondo de costado, es girar 90° sobre Y.
- El lazo cuelga debajo del rollo (su nudo encima de la vuelta de abajo, un poco adelante y girado 25°):
  alto total ~1,9. Las vueltas se abren en abanico (giradas -6°..+6°) para que se lean separadas.
- La mano agarra una vuelta de cuero con tres vueltas de la tira encima (segundo nivel de detalle).

Vueltas: 1) primera versión: con el octógono girado 10° por tramo y 2° de encastre, cada unión hacía un
bulto (se leía como caña de bambú); los bordes de la vuelta de cuero tenían la tapa en el mismo plano que
la vuelta (z-fighting) · 2) octógonos sin giro y 0,5° de encastre: uniones limpias; bordes 0,007 afuera ·
3) vuelta de cuero más grande (era un taquito) con tres vueltas de la tira.

Revisión
- 1864 triángulos contra 300 de referencia (calidad primero): cuatro vueltas redondas de soga de 8 lados
  no entran en 300 (una sola vuelta de 12 x 8 ya son 192 como malla continua, y con cascos por tramo, 336
  por las tapas de adentro). Con 10 tramos por vuelta baja a ~1500, pero el lazo se ve decagonal.
- Alto 1,94: 1,1 del rollo + 0,9 del lazo colgando debajo, como pide el prompt. Con el arma en la mano
  (unos 2,3 del piso) el lazo queda a ~0,4 del suelo.
"""

import math

from mathutils import Euler, Vector

ROPE_R = 0.04
COIL_R = 0.51                       # radio al centro de la soga: 2 x (0,51 + 0,04) = 1,1 por fuera
SEGS = 12


def loop(mk, part, center, radius, rot, mat="rope", segs=SEGS, twist=0.0, overlap=0.5, arc=(0.0, 360.0)):
    """Anillo de soga en el plano XY local (girado `rot`, grados), por tramos de cascos octogonales."""
    m = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    c = Vector(center)
    a0, a1 = arc
    step = (a1 - a0) / segs
    for k in range(segs):
        ring = []
        for th in (a0 + step * k - overlap, a0 + step * (k + 1) + overlap):
            t = math.radians(th)
            n = m @ Vector((math.cos(t), math.sin(t), 0))
            b = m @ Vector((0, 0, 1))
            p = c + n * radius
            for j in range(8):
                ph = math.radians(twist * k + 45 * j)
                ring.append(tuple(p + (n * math.cos(ph) + b * math.sin(ph)) * ROPE_R))
        mk.hull(part, ring, mat)


def rope(mk, part, a, b, mat="rope", twist=0.0):
    """Tramo recto de soga de a a b."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    pts = []
    for p in (a, b):
        for j in range(8):
            ph = math.radians(twist + 45 * j)
            pts.append(tuple(p + (u * math.cos(ph) + v * math.sin(ph)) * ROPE_R))
    mk.hull(part, pts, mat)


def build(mk):
    # ---------------- rollo: 4 vueltas que salen de la mano y se abren en abanico ----------------
    coil = mk.part("Coil", (0, 0, 0))
    turns = [  # (radio, corrimiento x, z, giro sobre X (abanico adelante/atrás), giro en el plano)
        (0.51, -0.02, -0.06, -6.0, -4.0),
        (0.50, 0.0, -0.02, -2.0, -1.0),
        (0.52, 0.025, 0.02, 2.0, 2.5),
        (0.495, 0.01, 0.06, 6.0, 5.0),
    ]
    for r, dx, dz, tilt, spin in turns:
        # el anillo cuelga de la mano: el centro queda r debajo del punto de arriba (0, 0.01, dz)
        m = Euler((math.radians(tilt), 0, math.radians(spin)), "XYZ").to_matrix()
        top = Vector((dx, 0.01, dz))
        center = top - m @ Vector((0, r, 0))
        loop(mk, coil, tuple(center), r, (tilt, 0, spin))
    for x0, x1, ry, rz in ((-0.10, 0.10, 0.072, 0.142), (-0.105, -0.07, 0.08, 0.152), (0.07, 0.105, 0.08, 0.152),
                           (-0.02, 0.025, 0.079, 0.15)):                         # vuelta de cuero y tres vueltas de la tira
        wrap = []
        for x in (x0, x1):
            for j in range(8):
                t = math.radians(22.5 + 45 * j)
                wrap.append((x, 0.012 + ry * math.cos(t), rz * math.sin(t)))
        mk.hull(coil, wrap, "leather")
    mk.marker("_Grip", (0, 0, 0))

    # ---------------- lazo corredizo con su honda ----------------
    knot = Vector((0.04, -1.0, -0.10))
    noose = mk.part("Noose", tuple(knot))
    nr = 0.45 - ROPE_R                                                          # 0,9 por fuera
    m = Euler((0, math.radians(25), math.radians(-5)), "XYZ").to_matrix()
    center = knot - m @ Vector((0, nr, 0))
    loop(mk, noose, tuple(center), nr, (0, 25, -5))
    mk.ball(noose, tuple(knot), 0.075, "rope", scale=(1.0, 1.15, 0.9), subdiv=1)        # honda
    rope(mk, noose, knot, knot + Vector((-0.03, 0.12, 0.05)), twist=10.0)              # sube al rollo
    mk.marker("_Noose", tuple(knot))

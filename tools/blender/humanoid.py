"""
Base común de los humanoides del Western para las recetas de la fábrica (`import humanoid as hu`).

Las medidas son las del Bloque D del documento de prompts con H = 5,2 (los caminantes A-D comparten
todas las articulaciones, así las animaciones R15 y los overlays de plata sirven para todos).
Las formas, en coordenadas del juego (studs, Y arriba, frente en -Z).

Lo sacado del caminante A (receta de referencia: enemies/WST_Enemy_Walker_A/01_design/).
"""

import math

from mathutils import Euler, Vector

# articulaciones (Bloque D, H = 5,2)
ANKLE, KNEE, HIP, WAIST = 0.26, 1.30, 2.444, 2.86
ELBOW, WRIST, SHOULDER, NECK = 3.016, 2.184, 3.952, 4.16
SH_X, EL_X, WR_X, LEG_X = 0.80, 0.93, 1.05, 0.30
ARM_Z = -0.10                       # brazos un poco adelante (hombros caídos)
NECK_P = (0.0, NECK, -0.10)


def ring(y, cx, cz, w, d, ch=0.28):
    """Octógono horizontal (ancho w en x, profundidad d en z) a la altura y."""
    a, b, ca, cb = w / 2, d / 2, w / 2 * (1 - ch), d / 2 * (1 - ch)
    return [(cx + x, y, cz + z) for x, z in
            ((-ca, -b), (ca, -b), (a, -cb), (a, cb), (ca, b), (-ca, b), (-a, cb), (-a, -cb))]


def round_ring(y, cx, cz, w, d, n=10):
    """Polígono de n lados (elipse) a la altura y: más redondo que el octógono."""
    return [(cx + w / 2 * math.cos(2 * math.pi * (i + 0.5) / n), y, cz + d / 2 * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def about(points, pivot, rot):
    e = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    p = Vector(pivot)
    return [tuple(p + e @ (Vector(q) - p)) for q in points]


def head_space(forward=0.15, tilt=-10):
    """Devuelve (head, hp): llevan puntos al espacio de la cabeza adelantada y caída alrededor del cuello."""
    def head(pts):
        return about([(x, y, z - forward) for x, y, z in pts], NECK_P, (tilt, 0, 0))

    def hp(p):
        return head([p])[0]
    return head, hp


def limb(mk, part, top, bottom, wt, dt, wb, db, mat, over=0.05, detail=False):
    (x1, y1, z1), (x2, y2, z2) = top, bottom
    mk.hull(part, ring(y1 + over, x1, z1, wt, dt) + ring(y2 - over, x2, z2, wb, db), mat, detail=detail)


def arm_joints(s):
    """Hombro, codo y muñeca del lado s (-1 izquierda, +1 derecha)."""
    return (s * SH_X, SHOULDER, ARM_Z), (s * EL_X, ELBOW, ARM_Z), (s * WR_X, WRIST, ARM_Z)


def leg_joints(s):
    return (s * LEG_X, HIP, 0), (s * LEG_X, KNEE, 0), (s * LEG_X, ANKLE, 0)


def hand(mk, part, s, mat="skin_dead", nails="skin_dead_dark", broken_finger=False):
    """Mano grande y redondeada: mitón de 3 anillos, pulgar, uñas sucias pintadas; dedo roto opcional."""
    wx = s * WR_X + s * 0.02
    mk.hull(part, round_ring(WRIST + 0.05, wx, ARM_Z, 0.21, 0.35) + round_ring(WRIST - 0.20, wx + s * 0.01, ARM_Z, 0.22, 0.37)
            + round_ring(WRIST - 0.46, wx + s * 0.02, ARM_Z, 0.17, 0.29), mat)
    mk.box(part, (wx - s * 0.07, WRIST - 0.15, ARM_Z - 0.19), (0.10, 0.23, 0.10), mat, rot=(-15, 0, 0))
    mk.paint(part, nails, box=((wx, WRIST - 0.46, ARM_Z), (0.4, 0.08, 0.5)))
    if broken_finger:   # un dedo doblado al revés, saliendo del mitón hacia atrás
        mk.box(part, (wx + s * 0.02, WRIST - 0.40, ARM_Z + 0.17), (0.07, 0.16, 0.07), mat, rot=(35, 0, 0))


def eyes(mk, hp, mat="bone"):
    part = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(part, hp((s * 0.19, 4.74, -0.60)), 0.08, mat, scale=(1.0, 0.8, 0.8), subdiv=0)
    return part


def zombie_face(mk, hd, head, hp, jaw_w=0.29, teeth_up=5, teeth_down=4):
    """Cuencas y boca talladas, dientes de detalle apoyados en la boca (Bloque H)."""
    for s in (-1, 1):
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball((s * 0.19, 4.74, -0.74), 0.15, scale=(1.0, 0.75, 0.9), subdiv=0)))
    mouth = [(-0.22, 4.46), (-0.13, 4.52), (0.13, 4.53), (0.24, 4.47), (0.18, 4.38), (-0.17, 4.39)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.85, -0.50)]))
    for i in range(teeth_up):
        x = -0.15 + 0.3 / max(teeth_up - 1, 1) * i
        mk.hull(hd, head([(x - 0.032, 4.56, -0.66), (x + 0.032, 4.56, -0.66), (x - 0.02, 4.47, -0.66),
                          (x + 0.02, 4.47, -0.66), (x - 0.03, 4.56, -0.45), (x + 0.03, 4.56, -0.45),
                          (x, 4.48, -0.45)]), "bone", detail=True)
    for i in range(teeth_down):
        x = -0.11 + 0.22 / max(teeth_down - 1, 1) * i
        mk.hull(hd, head([(x - 0.032, 4.36, -0.66), (x + 0.032, 4.36, -0.66), (x - 0.02, 4.44, -0.66),
                          (x + 0.02, 4.44, -0.66), (x - 0.03, 4.36, -0.45), (x + 0.03, 4.36, -0.45),
                          (x, 4.43, -0.45)]), "bone", detail=True)


def cranium(mk, hd, head, width=0.94, cheek=0.80):
    """Cráneo de 5 anillos de 10 lados (mejillas hundidas bajo los pómulos), ceja, nariz y mandíbula caída."""
    k = width / 0.94
    mk.hull(hd, head(round_ring(4.28, 0, -0.17, 0.66 * k, 0.62) + round_ring(4.52, 0, -0.21, cheek * k, 0.82)
                     + round_ring(4.80, 0, -0.25, 0.94 * k, 0.90) + round_ring(5.02, 0, -0.26, 0.84 * k, 0.84)
                     + round_ring(5.16, 0, -0.26, 0.56 * k, 0.60)), "skin_dead")
    mk.hull(hd, head(mk.pts_box((0, 4.87, -0.66), (0.84 * k, 0.12, 0.18), top=(0.9, 0.8))), "skin_dead")
    mk.hull(hd, head([(0, 4.82, -0.68), (0, 4.62, -0.84), (-0.09, 4.60, -0.68), (0.09, 4.60, -0.68),
                      (0, 4.58, -0.71), (-0.05, 4.72, -0.70), (0.05, 4.72, -0.70)]), "skin_dead")
    mk.hull(hd, head([(-0.29, 4.44, -0.60), (0.29, 4.44, -0.60), (-0.30, 4.46, -0.18), (0.30, 4.46, -0.18),
                      (-0.21, 4.18, -0.70), (0.21, 4.18, -0.70), (-0.24, 4.22, -0.16), (0.24, 4.22, -0.16),
                      (0, 4.15, -0.72)]), "skin_dead")

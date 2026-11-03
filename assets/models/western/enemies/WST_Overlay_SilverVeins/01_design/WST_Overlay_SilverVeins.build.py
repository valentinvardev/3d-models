"""
Receta de WST_Overlay_SilverVeins, la plata viva en vetas (prompt 052, Bloques A + G).

Brief
- Lo que se lee a 40 studs: vetas celestes que trepan por el lado izquierdo de la cara, bajan por el
  cuello y aparecen en el pecho abierto, y corren por el antebrazo y la mano derechos (más una rama
  corta en el antebrazo izquierdo). El brillo y el pulso los pone el motor (Neon).
- Calza con el cuerpo de los caminantes (humanoid.py, H = 5,2): cada pieza Silver_<BodyPart> tiene el
  origen de su pieza R15 (Head en el cuello, UpperTorso en la cintura, brazos en hombro, codo y muñeca)
  y las vetas se proyectan sobre la superficie del caminante A con rayos desde afuera (radiales al eje
  de la cabeza, del cuello o del miembro). Cada veta: secciones triangulares de 0,08-0,10 de ancho que
  se afinan hasta una punta, 0,012 por fuera de la piel en los bordes y 0,03 en la cresta.
- La piel que comparten A, C y D (cabeza, cuello, antebrazos al aire, manos) es la misma: las vetas
  calzan en los tres. En B (mangas largas, blusa de cuello alto) quedan adentro de la ropa.
- "Nunca sobre tela entera": donde la veta pasa por debajo de la ropa va enterrada (no se ve) y vuelve a
  salir por la rotura. Silver_UpperTorso: del costado derecho del cuello baja por adelante del cuello,
  entra bajo el cuello de la camisa y aparece en el fondo de la rotura del pecho (z = -0,19 en A y C),
  ramificada entre las costillas.
- Inferido: A no tiene mordida en el hombro derecho ni piel en el brazo derecho (la manga llega al
  codo): la veta del torso arranca en el costado derecho del cuello y Silver_RightUpperArm corre bajo
  la manga y asoma en el codo. Ramas: 3 en la cara (hacia la cuenca, la ceja y la oreja).

Vueltas: 1) primera versión · 2-5) caras coplanares dentro del overlay: el final de cada tramo se
achica 20 % hacia el centro de su sección y sube 0,004 (achicar hacia la cresta lo dejaba en el plano de
la cara lateral), y las ramas van con el piso 0,004 más afuera que el tronco (en el fondo plano de la
rotura compartían el plano).

Revisión
- 260 triángulos contra 400: 6 piezas, 16 vetas de 2-5 tramos (8 triángulos cada tramo, 4 la punta).
- Revisado montado sobre A, C y D (script que junta los .blend y corre la revisión de z-fighting sobre el
  conjunto): sin coplanares con el cuerpo, nada flota, las vetas siguen la piel. En D el pecho queda bajo
  la pechera; en B (no probado: mangas y cuello alto) las vetas de brazos y cuello quedan adentro de la ropa.
- Silver_RightUpperArm casi no se ve: en los cuatro caminantes el brazo está tapado por la manga, y la
  regla "nunca sobre tela entera" deja la veta enterrada; asoma solo en el codo.
- La veta del torso no arranca en una mordida del hombro derecho (A no la tiene): arranca en el costado
  derecho del cuello.
"""

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

head, hp = hu.head_space()
ring, round_ring = hu.ring, hu.round_ring


class _Probe:
    """Hace de `mk` para hu.cranium: junta los cascos en vez de construirlos."""

    def __init__(self, mk):
        self.hulls = []
        self.pts_box, self.pts_ball = mk.pts_box, mk.pts_ball

    def hull(self, part, points, mat, detail=False):
        if not detail:
            self.hulls.append([tuple(p) for p in points])


class Surface:
    """Superficie de una pieza del caminante (cascos convexos en coordenadas del juego). `outward(p)` da la
    dirección hacia afuera aproximada; snap(p) tira un rayo desde afuera y devuelve (punto, normal)."""

    def __init__(self, hulls, outward):
        bm = bmesh.new()
        for pts in hulls:
            bmesh.ops.convex_hull(bm, input=[bm.verts.new(q) for q in pts], use_existing_faces=False)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        self.bvh, self.outward = BVHTree.FromBMesh(bm), outward
        bm.free()

    def snap(self, p):
        p = Vector(p)
        d = self.outward(p).normalized()
        loc, n, _, _ = self.bvh.ray_cast(p + d * 0.6, -d)
        if loc is None:
            raise ValueError(f"el rayo no toca la superficie cerca de {tuple(round(k, 3) for k in p)}")
        return loc, (n if n.dot(d) > 0 else -n)


def radial_from_axis(a, b):
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()

    def out(p):
        v = Vector(p) - a
        return v - ax * v.dot(ax)
    return out


def fixed(normal):
    """snap para tramos enterrados o apoyados en un plano conocido: devuelve el punto tal cual."""
    return lambda p: (Vector(p), Vector(normal).normalized())


def vein(mk, part, snap, path, widths, base=0.012, ridge=0.03, xform=lambda pts: pts, branch=False):
    """Veta que sigue la superficie: secciones triangulares (dos bordes y una cresta) unidas por cascos
    que se encastran 0,012 en el siguiente; un ancho 0 es una punta. Para no dejar caras coplanares, el
    final que se mete en el tramo siguiente se achica 20 % hacia el centro de la sección y sube 0,004, y
    una rama (`branch`) va con el piso 0,004 más afuera y arranca achicada 25 % hacia su cresta, adentro
    del tronco."""
    if branch:              # el piso de la rama 0,004 más afuera que el del tronco: no comparten plano
        base += 0.004
    cs = [snap(p) for p in path]
    secs = []
    for i, (c, n) in enumerate(cs):
        t = cs[min(i + 1, len(cs) - 1)][0] - cs[max(i - 1, 0)][0]
        t = (t - n * t.dot(n)).normalized()
        side = n.cross(t).normalized()
        w = widths[i]
        if w <= 0:
            secs.append([c + n * (base + ridge) / 2])
            continue
        l, nl = snap(c - side * w / 2)
        r, nr = snap(c + side * w / 2)
        secs.append([l + nl * base, r + nr * base, c + n * ridge])
    if branch and len(secs[0]) == 3:
        secs[0] = [secs[0][2] + (q - secs[0][2]) * 0.75 for q in secs[0]]
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        if i + 1 < len(secs) - 1:
            ca, cb = sum(a, Vector()) / len(a), sum(b, Vector()) / len(b)
            fwd = (cb - ca).normalized() * 0.012
            if len(b) == 3:     # hacia el centro de la sección y 0,002 hacia afuera: ni el piso ni los costados coinciden
                lift = (b[2] - (b[0] + b[1]) / 2).normalized() * 0.004
                b = [cb + (q - cb) * 0.80 + fwd + lift for q in b]
        mk.hull(part, xform([tuple(q) for q in a + b]), "silver_neon")


def limb_point(a, b, y, phi, r):
    """Punto a la altura y sobre el eje a-b, a radio r y ángulo phi (0 = +x, -90 = adelante, -z)."""
    import math
    a, b = Vector(a), Vector(b)
    t = (y - a.y) / (b.y - a.y)
    c = a.lerp(b, t)
    return (c.x + r * math.cos(math.radians(phi)), y, c.z + r * math.sin(math.radians(phi)))


def build(mk):
    # ---------------- cabeza: del cuello por el lado izquierdo de la cara hasta la sien ----------------
    probe = _Probe(mk)
    hu.cranium(probe, None, lambda pts: list(pts))
    face = Surface(probe.hulls, lambda p: Vector((p.x, 0, p.z + 0.25)))
    sh = mk.part("Silver_Head", hu.NECK_P)
    trunk = [(-0.24, 4.24, -0.50), (-0.30, 4.40, -0.50), (-0.36, 4.56, -0.45), (-0.40, 4.72, -0.42),
             (-0.41, 4.86, -0.40), (-0.37, 4.98, -0.44)]
    vein(mk, sh, face.snap, trunk, (0.10, 0.09, 0.08, 0.07, 0.055, 0.0), xform=head)
    vein(mk, sh, face.snap, [(-0.36, 4.56, -0.45), (-0.33, 4.59, -0.55), (-0.31, 4.62, -0.60)], (0.05, 0.045, 0.0), xform=head, branch=True)  # a la cuenca
    vein(mk, sh, face.snap, [(-0.40, 4.74, -0.42), (-0.38, 4.84, -0.55), (-0.33, 4.90, -0.66)], (0.05, 0.04, 0.0), xform=head, branch=True)   # a la ceja
    vein(mk, sh, face.snap, [(-0.41, 4.84, -0.40), (-0.44, 4.87, -0.33), (-0.45, 4.89, -0.27)], (0.045, 0.035, 0.0), xform=head, branch=True)  # hacia la oreja (arriba del hueco de A)

    # ---------------- torso: costado derecho del cuello -> bajo la camisa -> fondo de la rotura ----------------
    neck_c, neck_axis = Vector((0, 4.12, -0.14)), Vector((0, 0.9397, -0.3420))
    neck = Surface([mk.pts_cyl((0, 4.12, -0.14), 0.17, 0.42, rot=(-20, 0, 0), sides=10)],
                   radial_from_axis(neck_c, neck_c + neck_axis))
    ut = mk.part("Silver_UpperTorso", (0, hu.WAIST, 0))

    def neck_or_buried(p):
        return neck.snap(p) if Vector(p).y > 3.95 else fixed((0, 0, -1))(p)
    vein(mk, ut, neck_or_buried, [(0.16, 4.24, -0.24), (0.13, 4.12, -0.26), (0.09, 4.00, -0.25), (0.06, 3.86, -0.23)],
         (0.10, 0.09, 0.085, 0.08))
    rip = fixed((0, 0, -1))
    floor = -0.19 - 0.012                                                     # fondo de la rotura: z = -0,19 (A y C)
    vein(mk, ut, rip, [(0.06, 3.86, floor - 0.01), (0.03, 3.70, floor), (0.0, 3.56, floor), (-0.05, 3.42, floor),
                       (-0.09, 3.33, floor)], (0.09, 0.085, 0.075, 0.06, 0.0), base=0.0, ridge=0.02)
    vein(mk, ut, rip, [(0.0, 3.56, floor), (0.06, 3.50, floor), (0.11, 3.41, floor)], (0.05, 0.04, 0.0), base=0.0, ridge=0.018, branch=True)
    vein(mk, ut, rip, [(-0.04, 3.45, floor), (-0.09, 3.50, floor), (-0.12, 3.58, floor)], (0.045, 0.035, 0.0), base=0.0, ridge=0.018, branch=True)

    # ---------------- brazo derecho: bajo la manga, asoma en el codo; antebrazo y mano hasta los nudillos ----------------
    shR, elR, wrR = hu.arm_joints(1)
    ua = mk.part("Silver_RightUpperArm", shR)
    vein(mk, ua, fixed((1, 0, 0)), [(elR[0] + 0.115, 3.30, -0.12), (elR[0] + 0.125, 3.08, -0.11),
                                    (elR[0] + 0.14, 2.93, -0.11)], (0.09, 0.09, 0.085), base=0.0, ridge=0.02)
    fore = Surface([ring(hu.ELBOW + 0.05, elR[0], hu.ARM_Z, 0.26, 0.26) + ring(hu.WRIST - 0.05, wrR[0], hu.ARM_Z, 0.21, 0.21)],
                   radial_from_axis(elR, wrR))
    la = mk.part("Silver_RightLowerArm", elR)
    fpath = [limb_point(elR, wrR, y, phi, 0.12) for y, phi in ((2.97, 5), (2.78, -20), (2.58, -35), (2.40, -20), (2.22, 0))]
    vein(mk, la, fore.snap, fpath, (0.085, 0.08, 0.07, 0.06, 0.055))
    vein(mk, la, fore.snap, [limb_point(elR, wrR, y, phi, 0.12) for y, phi in ((2.58, -35), (2.48, -65), (2.38, -85))],
         (0.045, 0.04, 0.0), branch=True)
    wx = hu.WR_X + 0.02
    hand = Surface([round_ring(hu.WRIST + 0.05, wx, hu.ARM_Z, 0.21, 0.35) + round_ring(hu.WRIST - 0.20, wx + 0.01, hu.ARM_Z, 0.22, 0.37)
                    + round_ring(hu.WRIST - 0.46, wx + 0.02, hu.ARM_Z, 0.17, 0.29)],
                   radial_from_axis((wx, hu.WRIST, hu.ARM_Z), (wx + 0.02, hu.WRIST - 0.46, hu.ARM_Z)))
    hd = mk.part("Silver_RightHand", wrR)
    hpath = [limb_point((wx, hu.WRIST, hu.ARM_Z), (wx + 0.02, hu.WRIST - 0.46, hu.ARM_Z), y, phi, 0.12)
             for y, phi in ((2.22, 0), (2.08, -8), (1.96, -15))]
    vein(mk, hd, hand.snap, hpath + [limb_point((wx, hu.WRIST, hu.ARM_Z), (wx + 0.02, hu.WRIST - 0.46, hu.ARM_Z), 1.81, -40, 0.12)],
         (0.055, 0.05, 0.045, 0.0))
    vein(mk, hd, hand.snap, [limb_point((wx, hu.WRIST, hu.ARM_Z), (wx + 0.02, hu.WRIST - 0.46, hu.ARM_Z), y, phi, 0.12)
                             for y, phi in ((1.96, -15), (1.88, 5), (1.81, 20))], (0.04, 0.035, 0.0), branch=True)

    # ---------------- antebrazo izquierdo: una rama corta que sale de debajo de la manga ----------------
    shL, elL, wrL = hu.arm_joints(-1)
    lfore = Surface([ring(2.67, -0.99, hu.ARM_Z, 0.22, 0.24) + ring(hu.WRIST - 0.05, wrL[0], hu.ARM_Z, 0.20, 0.21)],
                    radial_from_axis((-0.99, 2.62, hu.ARM_Z), wrL))
    ll = mk.part("Silver_LeftLowerArm", elL)
    vein(mk, ll, lfore.snap, [limb_point((-0.99, 2.62, hu.ARM_Z), wrL, y, phi, 0.11)
                              for y, phi in ((2.60, -120), (2.47, -108), (2.36, -98), (2.27, -92))],
         (0.06, 0.055, 0.045, 0.0), base=0.015)

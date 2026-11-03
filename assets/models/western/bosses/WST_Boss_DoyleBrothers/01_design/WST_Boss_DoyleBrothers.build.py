"""
Receta de WST_Boss_DoyleBrothers, los hermanos Doyle (prompt 060, Bloques A + D + H + G). Dos personajes.

Brief
- Se leen como hermanos (pelo y barba pelirrojos, la misma piel con pecas, pañuelo rojo y sombrero
  marrón emparchado) y como opuestos (forma): el Bruto es un ropero de espalda ancha con el hacha al
  hombro; el Tirador, flaco y alto de proporciones, guardapolvo de lona hasta medio muslo, dos
  cartucheras cruzadas, coleta larga y el pañuelo tapándole la nariz.
- LOS DOS EN UN SOLO GLB (límite de la herramienta): la fábrica arma un archivo por id y Blender no
  admite dos objetos con el mismo nombre, así que cada pieza lleva el prefijo del hermano
  ("Brute_Head", "Shooter_Acc_Hat"...). Al importar, el programador saca el prefijo y arma un rig por
  hermano. Cada hermano está corrido en x para revisarlos juntos: el Bruto en x = -2,1 y el Tirador en
  x = +1,5 (los orígenes de las piezas incluyen ese corrimiento). Para separarlos en dos ids alcanza con
  llamar a una sola de las funciones brute()/shooter() con dx = 0 y sin prefijo.
- Bruto: H = 6,6 (k = 1,269). Articulaciones del Bloque D: tobillo 0,33 · rodilla 1,65 · cadera 3,102 ·
  cintura 3,63 · codo 3,828 · muñeca 2,772 · hombro 5,016 · cuello 5,28. Torso 1,45 veces el ancho del
  caminante escalado (pecho 2,36): hombros x = ±1,30, codos ±1,47, muñecas ±1,62, caderas ±0,48, brazos
  en z = -0,16. Cuello corto: los trapecios suben hasta 5,26.
- Tirador: H = 5,6 (k = 1,077). Articulaciones: tobillo 0,28 · rodilla 1,40 · cadera 2,632 · cintura
  3,08 · codo 3,248 · muñeca 2,352 · hombro 4,256 · cuello 4,48. Miembros 0,85 de grosor: hombros
  x = ±0,80, codos ±0,94, muñecas ±1,07, caderas ±0,30, brazos en z = -0,08.
- Piezas de cada uno (con su prefijo): las 15 de R15, Eyes, Acc_Hat, Silver_Eyes, Silver_Neck,
  Silver_LeftHand, Silver_RightHand; el Bruto Acc_Axe (centro del puño derecho), el Tirador Acc_Rifle
  (el cubo de 0,1 en el agarre de la mano derecha).
- Tallado: cuencas, boca, mordida en el antebrazo izquierdo del Bruto, pantalón roto, parches de los
  sombreros (tallados poco profundos en cuero), pecas (cubitos tallados). Pintado: sangre en la barba.
- Inferido: el Bruto lleva el hacha apoyada en el hombro derecho (el puño agarra el mango abajo y el
  cabezal queda atrás del hombro: con 3,2 de mango, colgando atravesaría el piso); pantalones
  cloth_blue; el Tirador lleva camisa cloth_black (contra la lona del guardapolvo), la perilla asoma
  debajo del pañuelo y la pluma del sombrero es feather_black.

Vueltas: 1) primera versión · 2) errores: tapas de abajo del pantalón y del guardapolvo a la misma altura
(2,56) y de la solapa y la espalda (3,02); cartuchos flotando 0,026 (la cartuchera no seguía el quiebre
del pecho en 3,80: un punto más); jirones, pluma y perilla flotando · 3) tramos de la cartuchera alineados
(el punto nuevo caía en la recta: coplanares) · 4) paneles del chaleco del Bruto que siguen las esquinas
de la camisa (a 0,2 del borde se metían adentro y el chaleco se leía como dos tiradores); la manga
arrancada pasa al brazo como un muñón de tela con cinco jirones (en el torso quedaba adentro de la camisa).

Revisión
- Bruto 2552 y Tirador 2460 triángulos, contra 3200 cada uno.
- Medidas: Bruto 6,6 de alto sin sombrero; Tirador 5,6. El GLB mide 6,76 de ancho porque están lado a lado.
- Dudoso: los dos en un solo GLB con prefijo (ver arriba): decide Valentin si pasan a dos ids
  (WST_Boss_DoyleBrute / WST_Boss_DoyleShooter) o si el programador saca el prefijo al importar.
  El hacha va al hombro y no colgando del puño como el resto de las armas de los jefes. Las pecas son
  cubitos tallados de 0,035: a distancia de juego no se ven.
"""

import math

from mathutils import Vector

import humanoid as hu

ring, round_ring, about = hu.ring, hu.round_ring, hu.about
TAN8 = math.tan(math.radians(8))


class Shift:
    """Envuelve el kit: todas las coordenadas son locales al hermano (centro en x = 0) y los nombres
    llevan su prefijo."""

    def __init__(self, mk, dx, prefix):
        self.mk, self.dx, self.prefix = mk, dx, prefix
        self.pts_box, self.pts_cyl, self.pts_ball = mk.pts_box, mk.pts_cyl, mk.pts_ball

    def s(self, p):
        return (p[0] + self.dx, p[1], p[2])

    def part(self, name, origin):
        return self.mk.part(self.prefix + name, self.s(origin))

    def hull(self, part, points, mat, detail=False):
        self.mk.hull(part, [self.s(p) for p in points], mat, detail=detail)

    def box(self, part, center, size, mat, **kw):
        self.mk.box(part, self.s(center), size, mat, **kw)

    def cyl(self, part, center, radius, length, mat, **kw):
        self.mk.cyl(part, self.s(center), radius, length, mat, **kw)

    def ball(self, part, center, radius, mat, **kw):
        self.mk.ball(part, self.s(center), radius, mat, **kw)

    def prism(self, part, profile, depth, mat, plane="xy", center=(0, 0, 0), rot=(0, 0, 0), detail=False):
        self.mk.prism(part, profile, depth, mat, plane=plane, center=self.s(center), rot=rot, detail=detail)

    def carve(self, part, mat, points=None, prism=None):
        if points is not None:
            self.mk.carve(part, mat, points=[self.s(p) for p in points])
        else:
            pr = dict(prism)
            pr["center"] = self.s(pr.get("center", (0, 0, 0)))
            self.mk.carve(part, mat, prism=pr)

    def paint(self, part, mat, box=None, ball=None):
        if box is not None:
            self.mk.paint(part, mat, box=(self.s(box[0]), box[1]))
        else:
            self.mk.paint(part, mat, ball=(self.s(ball[0]), ball[1]))

    def bevel(self, part, **kw):
        self.mk.bevel(part, **kw)

    def marker(self, name, pos):
        self.mk.marker(self.prefix + name, self.s(pos))


def make_head(k, neck_p, fwd, tilt):
    """Espacio de la cabeza del caminante (H = 5,2, cuello en 4,16) -> la de un hermano."""
    def head(pts):
        return about([(x * k, neck_p[1] + (y - 4.16) * k, neck_p[2] + (z + 0.10) * k - fwd) for x, y, z in pts],
                     neck_p, (tilt, 0, 0))

    def hp(p):
        return head([p])[0]
    return head, hp


def rod(m, part, a, b, r, mat, sides=6, detail=False):
    A, B = Vector(a), Vector(b)
    d = (B - A).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u)
    pts = [tuple(P + r * (math.cos(t) * u + math.sin(t) * v)) for P in (A, B)
           for t in [2 * math.pi * (i + 0.5) / sides for i in range(sides)]]
    m.hull(part, pts, mat, detail=detail)


def strap(m, part, path, w, mat, back=0.12, detail=False):
    """Correa por puntos del frente; ancho perpendicular en xy, grosor hacia +z (o -z con back < 0)."""
    for i in range(len(path) - 1):
        (x0, y0, z0), (x1, y1, z1) = path[i], path[i + 1]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        ex, ey = dx / ln * 0.02, dy / ln * 0.02
        pts = []
        for (x, y, z), e in (((x0, y0, z0), -1), ((x1, y1, z1), 1)):
            for s in (-1, 1):
                for dz in (0.0, back):
                    pts.append((x + s * nx + e * ex, y + s * ny + e * ey, z + dz))
        m.hull(part, pts, mat, detail=detail)


def neck_veins(m, part, base, r, tilt, branches):
    """Vetas sobre un cuello cilíndrico inclinado `tilt` grados. branches: (t0, a0, t1, a1, w0, w1)."""
    cy, sz = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def P(t, a, off):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        rr = r + off
        return (base[0] + rr * ca, base[1] + cy * t - rr * sa * sz, base[2] + sz * t + rr * sa * cy)
    for k, (t0, a0, t1, a1, w0, w1) in enumerate(branches):
        out, dep = 0.02 + 0.007 * (k % 3), -0.05 - 0.006 * k
        t0, t1 = t0 - 0.008 * k, t1 + 0.006 * k
        pts = []
        for t, a, w in ((t0, a0, w0), (t1, a1, w1)):
            da = math.degrees(w / 2 / r)
            pts += [P(t, a - da, out), P(t, a + da, out), P(t, a - da, dep), P(t, a + da, dep)]
        m.hull(part, pts, "silver_neon")


def hand_veins(m, part, s, hx, z, rings, branches):
    """Vetas en el dorso de la mano (la cara de afuera del mitón). rings: (y, w) del mitón."""
    def X(y):
        for (ya, wa), (yb, wb) in zip(rings, rings[1:]):
            if yb <= y <= ya:
                return wa + (wb - wa) * (ya - y) / (ya - yb)
        return rings[-1][1]
    for k, ((y0, z0), (y1, z1), w0, w1) in enumerate(branches):
        out, dep = 0.02 + 0.006 * (k % 3), -0.04 - 0.005 * k
        y0, y1 = y0 + 0.006 * k, y1 - 0.005 * k
        pts = []
        for y, zz, w in ((y0, z0, w0), (y1, z1, w1)):
            xo = X(y) / 2 * 0.97
            for off in (out, dep):
                for sw in (-1, 1):
                    pts.append((s * (abs(hx) + xo + off), y, z + zz + sw * w / 2))
        m.hull(part, pts, "silver_neon")


def mitten(m, part, s, hx, z, rings, thumb):
    m.hull(part, [p for y, w, d in rings for p in round_ring(y, s * abs(hx) + s * 0.01 * (rings[0][0] - y), z, w, d)],
           "skin_dead")
    (ty, tz, tw, th) = thumb
    m.box(part, (s * abs(hx) - s * tw * 0.7, ty, z - tz), (tw, th, tw), "skin_dead", rot=(-15, 0, 0))
    m.paint(part, "skin_dead_dark", box=((s * abs(hx), rings[-1][0], z), (0.8, 0.10, 0.9)))


def freckles(m, part, head, spots):
    for x, y in spots:
        m.carve(part, "skin_dead_dark", points=head(m.pts_box((x, y, -0.80), (0.035, 0.035, 0.40))))


# ======================================================================================
def brute(mk, dx=-2.1, prefix="Brute_"):
    m = Shift(mk, dx, prefix)
    H = 6.6
    K = H / 5.2
    ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
    ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
    SH_X, ARM_Z, LEG_X = 1.30, -0.16, 0.48

    def arm_x(y):
        return SH_X + (SHOULDER - y) * TAN8
    EL_X, WR_X = arm_x(ELBOW), arm_x(WRIST)
    NECK_P = (0.0, NECK, -0.14)
    head, hp = make_head(K, NECK_P, 0.16, -8)

    def shirt_front(y):
        if y <= 4.40:
            return -0.53 - 0.16 * (y - 3.56) / 0.84
        return -0.69 + 0.25 * (y - 4.40) / 0.60

    # ---------------- torso: camisa roja sin mangas, chaleco de cuero, pañuelo ----------------
    ut = m.part("UpperTorso", (0, WAIST, 0))
    top = [(-0.60, 5.00, -0.44), (0.60, 5.00, -0.44), (-1.18, 4.86, -0.32), (1.18, 4.94, -0.32),
           (-1.18, 4.88, 0.34), (1.18, 4.96, 0.34), (-0.50, 5.26, -0.18), (0.50, 5.28, -0.18),
           (-0.50, 5.24, 0.32), (0.50, 5.26, 0.32)]
    hump = [(-0.60, 4.80, 0.66), (0.60, 4.84, 0.66), (0.0, 4.92, 0.70)]
    m.hull(ut, ring(3.56, 0, 0.02, 1.86, 1.10) + ring(4.40, 0, -0.04, 2.36, 1.30) + top + hump, "cloth_red")
    m.hull(ut, [(x, y, max(z, -0.40)) for x, y, z in ring(3.50, 0, 0.02, 1.94, 1.18) + ring(4.40, 0, -0.04, 2.44, 1.38)]
           + [(-1.22, 4.90, -0.30), (1.22, 4.98, -0.30), (-1.22, 4.92, 0.38), (1.22, 5.00, 0.38),
              (-0.54, 5.20, 0.36), (0.54, 5.22, 0.36), (-0.64, 4.82, 0.72), (0.64, 4.86, 0.72), (0.0, 4.96, 0.76)],
           "leather")                                                                             # chaleco: espalda
    for s in (-1, 1):
        drop = 0.08 if s < 0 else 0.0
        m.hull(ut, [(s * x, y, shirt_front(y) - 0.04) for x, y in ((0.44, 3.52), (0.36, 4.40), (0.34, 4.96),
                                                                    (0.67, 3.52), (0.85, 4.40), (0.60, 4.96))]
               + [(s * 0.97, 3.52, -0.416), (s * 1.22, 4.40, -0.548), (s * 1.22, 4.90 - drop, -0.36),
                  (s * 0.70, 3.52, -0.10), (s * 0.80, 4.40, -0.10), (s * 0.60, 4.90, -0.10)], "leather")   # paneles
    m.cyl(ut, (0, 5.18, -0.12), 0.38, 0.42, "skin_dead", rot=(-20, 0, 0), sides=10)              # cuello corto
    m.cyl(ut, (0, 5.12, -0.14), 0.43, 0.18, "cloth_red", rot=(-20, 0, 0), sides=10)              # pañuelo
    m.hull(ut, [(-0.34, 5.08, -0.52), (0.34, 5.08, -0.52), (0.04, 4.62, shirt_front(4.62) - 0.07),
                (-0.30, 5.08, -0.42), (0.30, 5.08, -0.42), (0.04, 4.64, shirt_front(4.64) - 0.03)], "cloth_red")
    m.ball(ut, (0.36, 5.10, -0.44), 0.07, "cloth_red", subdiv=0)                                   # nudo
    # ---------------- cadera ----------------
    lt = m.part("LowerTorso", (0, HIP, 0))
    m.hull(lt, ring(3.02, 0, 0, 1.70, 1.00) + ring(3.70, 0, 0.02, 1.86, 1.12), "cloth_blue")
    m.hull(lt, ring(3.38, 0, 0.02, 1.96, 1.22) + ring(3.54, 0, 0.02, 1.96, 1.22), "leather_dark")   # cinturón
    m.box(lt, (0, 3.46, -0.60), (0.28, 0.22, 0.06), "brass")
    m.carve(lt, "leather_dark", points=m.pts_box((0, 3.46, -0.65), (0.15, 0.10, 0.08)))
    for s in (-1, 1):
        zf = -0.585 if s < 0 else -0.58
        m.hull(lt, [(x, y, z) for x, y in ((s * 0.44, 3.70), (s * 0.98, 3.70), (s * 0.98, 3.56), (s * 0.48, 3.50))
                    for z in (zf, -0.40)], "leather")
    # ---------------- piernas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = m.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(m, ul, (x, HIP, 0), (x, KNEE, 0), 0.82, 0.84, 0.64, 0.66, "cloth_blue", over=0.06)
        ll = m.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(m, ll, (x, KNEE, 0), (x, 0.80, 0), 0.64, 0.66, 0.58, 0.60, "cloth_blue", over=0.06)
        m.hull(ll, ring(0.96, x, 0.0, 0.64, 0.68) + ring(0.26, x, 0.0, 0.58, 0.64), "leather_dark")
        if side == "Left":
            m.carve(ll, "skin_dead", points=m.pts_box((x - 0.04, 1.40, -0.30), (0.26, 0.24, 0.14), rot=(0, 0, -18)))
        ft = m.part(f"{side}Foot", (x, ANKLE, 0))
        m.hull(ft, [(x + d, y, z) for d in (-0.30, 0.30) for y, z in ((0.07, 0.30), (0.44, 0.28), (0.40, -0.16))]
               + [(x + d, y, z) for d in (-0.27, 0.27) for y, z in ((0.07, -0.66), (0.26, -0.60))], "leather_dark")
        m.hull(ft, [(x + d, y, z) for d in (-0.31, 0.31) for y in (0.0, 0.08) for z in (0.32, -0.68)], "coal")
    # ---------------- brazos pelados enormes, puños enormes ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        ua = m.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        m.hull(ua, round_ring(5.10, s * arm_x(5.10), ARM_Z, 0.62, 0.66) + round_ring(4.80, s * (arm_x(4.80) + 0.03), ARM_Z, 0.84, 0.86)
               + round_ring(4.30, s * (arm_x(4.30) + 0.02), ARM_Z, 0.78, 0.80) + round_ring(3.76, s * arm_x(3.76), ARM_Z, 0.62, 0.66),
               "skin_dead")
        # muñón de la manga arrancada: tela roja sobre el deltoide y jirones colgando
        m.hull(ua, round_ring(5.14, s * arm_x(5.14), ARM_Z, 0.68, 0.72) + round_ring(4.80, s * (arm_x(4.80) + 0.03), ARM_Z, 0.90, 0.92),
               "cloth_red")
        cx = s * (arm_x(4.80) + 0.03)
        for k, a in enumerate((-110, -60, -10, 40, 90)):
            a = a if s > 0 else 180 - a
            ar = math.radians(a)
            m.prism(ua, [(-0.09, 0), (0.09, 0), (0.0, -0.16 - 0.05 * (k % 2))], 0.03, "cloth_red", plane="xy",
                    center=(cx + 0.435 * math.cos(ar), 4.82, ARM_Z + 0.445 * math.sin(ar)),
                    rot=(0, -math.degrees(ar) + 90, 0), detail=True)
        la = m.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        m.hull(la, round_ring(3.88, s * arm_x(3.88), ARM_Z, 0.64, 0.68) + round_ring(3.50, s * (arm_x(3.50) + 0.02), ARM_Z, 0.74, 0.74)
               + round_ring(2.84, s * arm_x(2.84), ARM_Z, 0.52, 0.56), "skin_dead")
        if side == "Left":   # mordida en el antebrazo
            m.carve(la, "blood_dry", points=m.pts_ball((s * (arm_x(3.30) + 0.36), 3.30, ARM_Z - 0.10), 0.13,
                                                       scale=(1, 1.4, 1), subdiv=0))
        m.paint(la, "skin_dead_dark", ball=((s * (arm_x(3.60) + 0.30), 3.60, ARM_Z + 0.20), 0.18))
        hd = m.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        mitten(m, hd, s, WR_X + 0.04, ARM_Z, ((2.85, 0.46, 0.68), (2.42, 0.50, 0.74), (1.98, 0.40, 0.58)),
               (2.58, 0.36, 0.20, 0.42))
        sv = m.part(f"Silver_{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hand_veins(m, sv, s, WR_X + 0.04, ARM_Z, ((2.85, 0.46), (2.42, 0.50), (1.98, 0.40)),
                   (((2.84, 0.05), (2.46, 0.02), 0.07, 0.05), ((2.47, 0.02), (2.12, -0.12), 0.05, 0.03),
                    ((2.48, 0.03), (2.16, 0.16), 0.05, 0.03)))
    # ---------------- cabeza: barba enorme, nariz rota ----------------
    hd = m.part("Head", NECK_P)
    m.hull(hd, head(round_ring(4.28, 0, -0.18, 0.80, 0.68) + round_ring(4.52, 0, -0.21, 0.90, 0.86)
                    + round_ring(4.80, 0, -0.25, 0.96, 0.92) + round_ring(5.02, 0, -0.26, 0.88, 0.88)
                    + round_ring(5.16, 0, -0.26, 0.58, 0.62)), "skin_dead")
    for s in (-1, 1):
        m.hull(hd, head([(s * 0.03, 4.85, -0.72), (s * 0.44, 4.91, -0.59), (s * 0.03, 4.95, -0.68),
                         (s * 0.44, 4.98, -0.55), (s * 0.03, 4.88, -0.46), (s * 0.42, 4.95, -0.42)]), "skin_dead")   # ceja
        m.hull(hd, head(m.pts_box((s * 0.48, 4.70, -0.22), (0.09, 0.24, 0.16), top=(1, 0.7))), "skin_dead")       # orejas
    m.hull(hd, head([(-0.04, 4.84, -0.70), (-0.02, 4.74, -0.80), (0.08, 4.62, -0.88), (-0.06, 4.58, -0.72),
                     (0.14, 4.58, -0.72), (0.06, 4.56, -0.80), (0.04, 4.70, -0.72)]), "skin_dead")   # nariz rota, torcida
    # barba tupida que baja sobre el pañuelo, bigote, pelo
    m.hull(hd, head([(s * 0.48, 4.72, z) for s in (-1, 1) for z in (-0.40, -0.12)]
                    + [(s * 0.47, 4.40, -0.56) for s in (-1, 1)] + [(s * 0.40, 4.14, -0.70) for s in (-1, 1)]
                    + [(s * 0.22, 3.94, -0.78) for s in (-1, 1)] + [(0, 3.86, -0.80), (0, 4.10, -0.20)]
                    + [(s * 0.30, 4.30, -0.14) for s in (-1, 1)]), "hair_red")
    for s in (-1, 1):
        m.hull(hd, head([(0, 4.60, -0.86), (s * 0.20, 4.58, -0.84), (s * 0.34, 4.48, -0.76), (s * 0.30, 4.42, -0.80),
                         (0, 4.52, -0.90), (0, 4.58, -0.70)]), "hair_red")                     # bigote
    cap = [p for y, w, d in ((4.56, 0.92, 0.86), (4.80, 1.00, 0.96), (5.00, 0.92, 0.92))
           for p in round_ring(y, 0, -0.25, w, d, n=12) if p[2] > -0.24]
    m.hull(hd, head(cap + [(0, 4.48, 0.06)]), "hair_red")                                          # pelo
    for s in (-1, 1):
        m.carve(hd, "skin_dead_dark", points=head(m.pts_ball((s * 0.19, 4.75, -0.75), 0.15, scale=(1.0, 0.72, 0.9),
                                                              subdiv=0)))
    mouth = [(-0.18, 4.42), (0.18, 4.42), (0.15, 4.26), (-0.15, 4.26), (0, 4.23)]
    m.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-1.0, -0.56)]))
    for i in range(4):
        x = -0.11 + 0.073 * i
        m.hull(hd, head([(x - 0.03, 4.26, -0.70), (x + 0.03, 4.26, -0.70), (x - 0.02, 4.35, -0.70),
                         (x + 0.02, 4.35, -0.70), (x - 0.03, 4.26, -0.54), (x + 0.03, 4.26, -0.54),
                         (x, 4.34, -0.54)]), "bone", detail=True)
    freckles(m, hd, head, ((-0.24, 4.64), (-0.15, 4.70), (0.17, 4.69), (0.26, 4.63)))
    m.paint(hd, "blood_dry", ball=(hp((0.10, 4.10, -0.76)), 0.14))
    eyes = m.part("Eyes", NECK_P)
    se = m.part("Silver_Eyes", NECK_P)
    for s in (-1, 1):
        m.ball(eyes, hp((s * 0.19, 4.75, -0.61)), 0.08 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)
        m.ball(se, hp((s * 0.19, 4.75, -0.61)), 0.08 * K + 0.012, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)
    sn = m.part("Silver_Neck", (0, WAIST, 0))
    neck_veins(m, sn, (0, 5.18, -0.12), 0.38, -20, ((-0.06, 20, 0.16, 30, 0.10, 0.07), (0.14, 30, 0.24, 55, 0.06, 0.04),
                                                    (-0.06, 160, 0.16, 150, 0.09, 0.06), (0.14, 150, 0.24, 125, 0.05, 0.03)))
    # sombrero de copa redonda, golpeado y emparchado
    base = hp((0, 5.00, -0.26))
    hat = m.part("Acc_Hat", base)
    brim = [(0.86 * math.cos(2 * math.pi * i / 16), 0.84 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    m.hull(hat, head([(x, 4.98 - 0.05 * abs(z) / 0.84, z - 0.26) for x, z in brim]
                     + [(x, 5.02 - 0.05 * abs(z) / 0.84, z - 0.26) for x, z in brim]), "cloth_brown")
    crown = (round_ring(4.99, 0, -0.26, 0.94, 0.98, n=12) + round_ring(5.26, 0, -0.26, 0.92, 0.96, n=12)
             + [(x * (0.9 if x > 0 else 1.0), y - (0.06 if x > 0.2 else 0.0), z)
                for x, y, z in round_ring(5.42, 0, -0.26, 0.78, 0.84, n=12)] + round_ring(5.50, 0, -0.26, 0.44, 0.50, n=8))
    m.hull(hat, head(crown), "cloth_brown")
    m.hull(hat, head(round_ring(5.03, 0, -0.26, 0.975, 1.015, n=12) + round_ring(5.10, 0, -0.26, 0.97, 1.01, n=12)),
           "leather_dark")
    m.carve(hat, "leather", points=head(m.pts_box((-0.30, 5.28, -0.62), (0.22, 0.18, 0.20), rot=(0, 30, 0))))   # parche
    # hacha de leñador apoyada en el hombro derecho
    grip = (WR_X + 0.04, WRIST - 0.36, ARM_Z)
    ax = m.part("Acc_Axe", grip)
    g = Vector(grip)
    top = Vector((WR_X - 0.11, 5.15, 0.95))
    u = (top - g).normalized()
    bottom = g - u * 0.22
    rod(m, ax, tuple(bottom), tuple(top), 0.065, "wood_mid", sides=8, detail=True)                 # mango de 3,2
    rod(m, ax, tuple(bottom - u * 0.02), tuple(bottom + u * 0.08), 0.085, "wood_mid", sides=8, detail=True)   # tope
    b = Vector((0, -u.z, u.y)).normalized()                                                        # filo, hacia atrás
    t = u.cross(b).normalized()
    hc = top - u * 0.18

    def AX(pb, pu, pt):
        return tuple(hc + b * pb + u * pu + t * pt)
    m.hull(ax, [AX(pb, pu, pt) for pb in (-0.24, 0.12) for pu in (-0.15, 0.15) for pt in (-0.075, 0.075)], "iron")   # ojo y nuca
    m.hull(ax, [AX(0.10, pu, pt) for pu in (-0.15, 0.15) for pt in (-0.06, 0.06)]
           + [AX(0.58, pu, pt) for pu in (-0.32, 0.30) for pt in (-0.015, 0.015)], "iron")         # hoja abierta
    m.bevel(ax, width=0.016, angle=35, mat="steel_light")
    return m


# ======================================================================================
def shooter(mk, dx=1.5, prefix="Shooter_"):
    m = Shift(mk, dx, prefix)
    H = 5.6
    K = H / 5.2
    ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.25 * H, 0.47 * H, 0.55 * H
    ELBOW, WRIST, SHOULDER, NECK = 0.58 * H, 0.42 * H, 0.76 * H, 0.80 * H
    SH_X, ARM_Z, LEG_X = 0.80, -0.08, 0.30

    def arm_x(y):
        return SH_X + (SHOULDER - y) * TAN8
    EL_X, WR_X = arm_x(ELBOW), arm_x(WRIST)
    NECK_P = (0.0, NECK, -0.08)
    head, hp = make_head(K, NECK_P, 0.12, -6)

    def shirt_front(y):
        if y <= 3.80:
            return -0.33 - 0.04 * (y - 3.04) / 0.76
        return -0.37 + 0.10 * (y - 3.80) / 0.42

    # ---------------- torso: camisa negra, dos cartucheras cruzadas, guardapolvo abierto ----------------
    ut = m.part("UpperTorso", (0, WAIST, 0))
    m.hull(ut, ring(3.04, 0, 0.0, 1.06, 0.66) + ring(3.80, 0, -0.01, 1.30, 0.72)
           + [(-0.36, 4.22, -0.27), (0.36, 4.22, -0.27), (-0.70, 4.18, -0.22), (0.70, 4.22, -0.22),
              (-0.70, 4.20, 0.20), (0.70, 4.24, 0.20), (-0.28, 4.32, 0.14), (0.28, 4.32, 0.14),
              (-0.36, 4.06, 0.40), (0.36, 4.08, 0.40)], "cloth_black")
    # guardapolvo: espalda, costados, solapas
    m.hull(ut, [(x, y, max(z, -0.22)) for x, y, z in ring(3.02, 0, 0.02, 1.16, 0.78) + ring(3.80, 0, 0.0, 1.40, 0.84)]
           + [(-0.76, 4.22, -0.22), (0.76, 4.26, -0.22), (-0.76, 4.24, 0.24), (0.76, 4.28, 0.24),
              (-0.30, 4.36, 0.20), (0.30, 4.36, 0.20), (-0.40, 4.08, 0.46), (0.40, 4.10, 0.46)], "canvas")
    for s in (-1, 1):
        m.hull(ut, [(s * 0.40, 3.03, shirt_front(3.03) - 0.07), (s * 0.44, 3.80, shirt_front(3.80) - 0.07),
                    (s * 0.30, 4.30, -0.32), (s * 0.66, 3.03, -0.24), (s * 0.72, 3.80, -0.28), (s * 0.74, 4.22, -0.24),
                    (s * 0.50, 3.03, -0.08), (s * 0.55, 3.80, -0.08), (s * 0.45, 4.24, -0.08)], "canvas")
        m.hull(ut, [(s * 0.44, 3.82, shirt_front(3.82) - 0.07), (s * 0.32, 4.26, -0.33), (s * 0.62, 4.10, -0.33),
                    (s * 0.46, 3.84, shirt_front(3.84) - 0.10), (s * 0.34, 4.24, -0.36), (s * 0.60, 4.08, -0.36)],
               "canvas", detail=True)                                                           # vuelta de la solapa
    # cartucheras en X sobre la camisa
    for s in (-1, 1):
        off = 0.05 if s > 0 else 0.062
        path = [(x, y, shirt_front(y) - off) for x, y in ((s * 0.34, 4.20), (s * 0.30, 3.98), (s * 0.17, 3.80),
                                                         (-s * 0.10, 3.50), (-s * 0.40, 3.06))]
        strap(m, ut, path, 0.13, "leather_dark" if s > 0 else "leather", back=0.08)
        for i in range(5):
            tt = 0.12 + 0.17 * i
            a, b = Vector(path[1]), Vector(path[4])
            c = a.lerp(b, tt)
            z = shirt_front(c.y) - off - 0.02
            rod(m, ut, (c.x, c.y - 0.02, z), (c.x, c.y + 0.10, z), 0.025, "brass", sides=5, detail=True)
    m.cyl(ut, (0, 4.38, -0.10), 0.16, 0.36, "skin_dead", rot=(-15, 0, 0), sides=8)               # cuello
    m.cyl(ut, (0, 4.30, -0.11), 0.21, 0.12, "canvas", rot=(-15, 0, 0), sides=10)                 # cuello del guardapolvo
    # ---------------- cadera ----------------
    lt = m.part("LowerTorso", (0, HIP, 0))
    m.hull(lt, ring(2.56, 0, 0, 0.94, 0.58) + ring(3.14, 0, 0.0, 1.06, 0.64), "cloth_blue")
    m.hull(lt, ring(2.84, 0, 0, 1.04, 0.66) + ring(2.96, 0, 0, 1.04, 0.66), "leather_dark")      # cinturón
    m.box(lt, (0, 2.90, -0.33), (0.16, 0.13, 0.04), "brass")
    m.hull(lt, [(x, y, max(z, -0.20)) for x, y, z in ring(2.58, 0, 0.04, 1.30, 0.90) + ring(3.12, 0, 0.02, 1.18, 0.82)],
           "canvas")                                                                              # guardapolvo atrás
    for s in (-1, 1):
        m.hull(lt, [(s * 0.40, 3.11, -0.40), (s * 0.44, 2.59, -0.44), (s * 0.66, 3.11, -0.28), (s * 0.72, 2.59, -0.32),
                    (s * 0.50, 3.11, -0.10), (s * 0.52, 2.59, -0.10)], "canvas")
    # ---------------- piernas: faldones del guardapolvo hasta medio muslo ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = m.part(f"{side}UpperLeg", (x, HIP, 0))
        hu.limb(m, ul, (x, HIP, 0), (x, KNEE, 0), 0.46, 0.48, 0.38, 0.40, "cloth_blue", over=0.06)
        m.hull(ul, [(s * a, y, z) for a, y, z in ((0.03, 2.70, 0.46), (0.36, 2.70, 0.47), (0.64, 2.70, 0.30),
                                                  (0.70, 2.70, -0.10), (0.46, 2.70, -0.44), (0.03, 1.94, 0.58),
                                                  (0.40, 1.92, 0.60), (0.74, 1.94, 0.40), (0.80, 1.96, -0.12),
                                                  (0.54, 1.98, -0.50), (0.20, 2.70, 0.05), (0.20, 1.94, 0.10))],
               "canvas")
        hem = [(0.08, 1.94, 0.58), (0.34, 1.925, 0.60), (0.60, 1.935, 0.48), (0.78, 1.95, 0.22), (0.79, 1.96, -0.10)]
        for i in range(len(hem) - 1):
            (x0, y0, z0), (x1, y1, z1) = hem[i], hem[i + 1]
            ang = -math.degrees(math.atan2(z1 - z0, s * (x1 - x0)))
            m.prism(ul, [(-0.10, 0), (0.10, 0), (0.02, -0.12 - 0.04 * (i % 2))], 0.03, "canvas", plane="xy",
                    center=(s * (x0 + x1) / 2, (y0 + y1) / 2 + 0.02, (z0 + z1) / 2), rot=(0, ang, 0), detail=True)
        ll = m.part(f"{side}LowerLeg", (x, KNEE, 0))
        hu.limb(m, ll, (x, KNEE, 0), (x, 0.80, 0), 0.38, 0.40, 0.34, 0.36, "cloth_blue", over=0.06)
        m.hull(ll, ring(0.96, x, 0.0, 0.42, 0.46) + ring(0.24, x, 0.0, 0.38, 0.44), "leather_dark")
        if side == "Right":
            m.carve(ll, "skin_dead", points=m.pts_box((x + 0.02, 1.20, -0.18), (0.16, 0.20, 0.12), rot=(0, 0, 15)))
        ft = m.part(f"{side}Foot", (x, ANKLE, 0))
        m.hull(ft, [(x + d, y, z) for d in (-0.20, 0.20) for y, z in ((0.06, 0.22), (0.36, 0.20), (0.32, -0.12))]
               + [(x + d, y, z) for d in (-0.15, 0.15) for y, z in ((0.06, -0.56), (0.18, -0.50))]
               + [(x, 0.06, -0.62), (x, 0.14, -0.58)], "leather_dark")
        m.hull(ft, [(x + d, y, z) for d in (-0.21, 0.21) for y in (0.0, 0.07) for z in (0.24, -0.50)]
               + [(x, 0.0, -0.64), (x, 0.07, -0.64)], "coal")
    # ---------------- brazos flacos con mangas del guardapolvo ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        ua = m.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        m.hull(ua, round_ring(4.34, s * arm_x(4.34), ARM_Z, 0.32, 0.36) + round_ring(4.16, s * arm_x(4.16), ARM_Z, 0.42, 0.44)
               + round_ring(3.20, s * arm_x(3.20), ARM_Z, 0.36, 0.38), "canvas")
        la = m.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        m.hull(la, round_ring(3.32, s * arm_x(3.32), ARM_Z, 0.36, 0.38) + round_ring(2.56, s * arm_x(2.56), ARM_Z, 0.30, 0.32),
               "canvas")
        m.hull(la, round_ring(2.66, s * arm_x(2.66), ARM_Z, 0.38, 0.40, n=8) + round_ring(2.46, s * arm_x(2.46), ARM_Z, 0.38, 0.40, n=8),
               "canvas")                                                                          # puño
        hd = m.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        mitten(m, hd, s, WR_X + 0.02, ARM_Z, ((2.42, 0.22, 0.36), (2.14, 0.24, 0.40), (1.86, 0.18, 0.31)),
               (2.24, 0.20, 0.10, 0.24))
        sv = m.part(f"Silver_{side}Hand", (s * WR_X, WRIST, ARM_Z))
        hand_veins(m, sv, s, WR_X + 0.02, ARM_Z, ((2.42, 0.22), (2.14, 0.24), (1.86, 0.18)),
                   (((2.40, 0.04), (2.14, 0.01), 0.05, 0.04), ((2.15, 0.01), (1.94, -0.09), 0.04, 0.025),
                    ((2.16, 0.02), (1.96, 0.11), 0.035, 0.02)))
    rf = m.part("Acc_Rifle", (WR_X + 0.02, WRIST - 0.26, ARM_Z))
    m.box(rf, (WR_X + 0.02, WRIST - 0.26, ARM_Z), (0.1, 0.1, 0.1), "iron")
    # ---------------- cabeza: coleta, perilla, pañuelo sobre la nariz ----------------
    hd = m.part("Head", NECK_P)
    m.hull(hd, head(round_ring(4.30, 0, -0.18, 0.66, 0.62) + round_ring(4.52, 0, -0.21, 0.78, 0.80)
                    + round_ring(4.80, 0, -0.25, 0.90, 0.88) + round_ring(5.02, 0, -0.26, 0.84, 0.84)
                    + round_ring(5.16, 0, -0.26, 0.56, 0.60)), "skin_dead")
    m.hull(hd, head([(-0.25, 4.44, -0.56), (0.25, 4.44, -0.56), (-0.26, 4.46, -0.18), (0.26, 4.46, -0.18),
                     (-0.16, 4.16, -0.66), (0.16, 4.16, -0.66), (-0.20, 4.20, -0.16), (0.20, 4.20, -0.16),
                     (0, 4.12, -0.70)]), "skin_dead")                                               # mandíbula fina
    for s in (-1, 1):
        m.hull(hd, head([(s * 0.03, 4.85, -0.70), (s * 0.42, 4.90, -0.58), (s * 0.03, 4.93, -0.66),
                         (s * 0.42, 4.96, -0.54), (s * 0.03, 4.87, -0.45), (s * 0.40, 4.93, -0.40)]), "skin_dead")
        m.hull(hd, head(m.pts_box((s * 0.45, 4.72, -0.22), (0.08, 0.22, 0.15), top=(1, 0.7))), "skin_dead")
    m.hull(hd, head([(0, 4.84, -0.70), (0, 4.66, -0.82), (-0.08, 4.62, -0.70), (0.08, 4.62, -0.70),
                     (0, 4.60, -0.74)]), "skin_dead")                                               # nariz
    for s in (-1, 1):
        m.carve(hd, "skin_dead_dark", points=head(m.pts_ball((s * 0.18, 4.76, -0.74), 0.14, scale=(1.0, 0.72, 0.9),
                                                              subdiv=0)))
    freckles(m, hd, head, ((-0.31, 4.73), (-0.06, 4.81), (0.07, 4.80), (0.31, 4.72)))
    # pañuelo sobre la nariz: envuelve la cara de abajo y cae en punta adelante
    m.hull(hd, head([(s * x, y, z) for s in (-1, 1) for x, y, z in ((0.40, 4.66, -0.54), (0.42, 4.64, -0.20),
                                                                     (0.34, 4.30, -0.64), (0.36, 4.24, -0.16),
                                                                     (0.18, 4.66, -0.84), (0.20, 4.20, -0.74))]
                    + [(0, 4.68, -0.88), (0, 4.04, -0.80)]), "cloth_red")
    m.hull(hd, head([(-0.20, 4.20, -0.76), (0.20, 4.20, -0.76), (0, 3.96, -0.80), (-0.16, 4.20, -0.70),
                     (0.16, 4.20, -0.70), (0, 3.98, -0.74)]), "cloth_red")                          # punta
    m.hull(hd, head([(-0.06, 4.16, -0.68), (0.06, 4.16, -0.68), (0, 3.80, -0.68), (-0.05, 4.16, -0.58),
                     (0.05, 4.16, -0.58)]), "hair_red")                                             # perilla
    cap = [p for y, w, d in ((4.56, 0.82, 0.84), (4.80, 0.94, 0.92), (5.00, 0.88, 0.88))
           for p in round_ring(y, 0, -0.25, w, d, n=12) if p[2] > -0.24]
    m.hull(hd, head(cap + [(0, 4.50, 0.06)]), "hair_red")                                          # pelo
    m.hull(hd, head([(-0.07, 4.80, 0.22), (0.07, 4.80, 0.22), (-0.06, 4.70, 0.30), (0.06, 4.70, 0.30),
                     (-0.04, 3.70, 0.52), (0.04, 3.70, 0.52), (0, 3.62, 0.50)]), "hair_red")        # coleta
    m.hull(hd, head(m.pts_cyl((0, 4.66, 0.27), 0.08, 0.06, axis="y", sides=6)), "leather_dark")    # atadura
    eyes = m.part("Eyes", NECK_P)
    se = m.part("Silver_Eyes", NECK_P)
    for s in (-1, 1):
        m.ball(eyes, hp((s * 0.18, 4.76, -0.61)), 0.075 * K, "bone", scale=(1.0, 0.8, 0.8), subdiv=0)
        m.ball(se, hp((s * 0.18, 4.76, -0.61)), 0.075 * K + 0.012, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)
    sn = m.part("Silver_Neck", (0, WAIST, 0))
    neck_veins(m, sn, (0, 4.38, -0.10), 0.16, -15, ((-0.10, 15, 0.08, 25, 0.06, 0.045), (0.07, 25, 0.16, 50, 0.04, 0.03),
                                                    (-0.10, 165, 0.08, 155, 0.06, 0.045), (0.07, 155, 0.16, 130, 0.04, 0.03)))
    # sombrero de ala angosta con pluma y parche
    base = hp((0, 5.00, -0.26))
    hat = m.part("Acc_Hat", base)
    brim = [(0.66 * math.cos(2 * math.pi * i / 16), 0.66 * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    m.hull(hat, head([(x, y, z - 0.26) for x, z in brim for y in (4.98, 5.02)]), "cloth_brown")
    crown = (round_ring(4.99, 0, -0.26, 0.90, 0.94, n=12) + round_ring(5.30, 0, -0.26, 0.86, 0.92, n=12)
             + [(x * (0.75 if z < -0.42 else 1.0), y, z) for x, y, z in round_ring(5.46, 0, -0.25, 0.70, 0.82, n=12)])
    m.hull(hat, head(crown), "cloth_brown")
    m.hull(hat, head(round_ring(5.03, 0, -0.26, 0.935, 0.975, n=12) + round_ring(5.10, 0, -0.26, 0.93, 0.97, n=12)),
           "leather_dark")
    m.carve(hat, "leather", points=head(m.pts_box((0.30, 5.26, -0.58), (0.18, 0.16, 0.20), rot=(0, -30, 0))))   # parche
    m.prism(hat, [(0.0, 0.0), (0.05, 0.10), (0.06, 0.36), (0.02, 0.52), (-0.02, 0.36), (-0.03, 0.10)], 0.02,
            "feather_black", plane="zy", center=hp((0.455, 5.05, -0.14)), rot=(-25, 0, -15), detail=True)   # pluma
    return m


def build(mk):
    brute(mk)
    shooter(mk)

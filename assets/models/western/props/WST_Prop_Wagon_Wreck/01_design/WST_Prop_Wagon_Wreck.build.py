"""
Receta de WST_Prop_Wagon_Wreck, la carreta de carga abandonada (prompt 129, Bloques A + C).

Brief
- Silueta a 40 studs: caja larga ladeada hacia atrás a la izquierda, lona clara rota sobre arcos (un
  hueco grande arriba a la derecha y el fondo caído), una rueda acostada al lado, la lanza en el piso y
  carga desparramada atrás. Es contenedor de loot y cobertura.
- Medidas: caja 10 (Z) x 5 (X), piso arriba a 2,6 como la carreta del jugador; tablas laterales de 1,4;
  arcos elípticos de 2,3 x 3,0 (tope de la lona a ~7,3). Ruedas del estilo de WST_Vehicle_Wagon:
  12 rayos sueltos (6 barras que cruzan el cubo), pinas de madera con llanta de hierro; 3,2 adelante y
  3,8 atrás. Dos junturas de 0,4° entre las mitades de la pina (las juntas de las pinas reales).
- Inclinación: la rueda de atrás a la izquierda se rompió. La caja gira sobre el perno rey (adelante al
  centro, el eje delantero queda horizontal con sus dos ruedas en el piso): 11° de rolido a la izquierda
  y THETA de cabeceo atrás, calculado para que la rueda trasera derecha siga apoyada. Total ~12°.
  La punta del eje trasero izquierdo, quebrada, baja hasta el piso.
- Fragmentos (8, origen común): frag01-02 el piso partido por una grieta en zigzag, frag03 tabla
  izquierda (con el muñón izquierdo del arco quebrado), frag04 tabla derecha (con un tablón roto y el
  muñón derecho), frag05 tabla de adelante, frag06-08 los tres arcos que quedan, cada uno con su paño de
  lona. Quedan en pie: fixed_Frame (largueros, ejes, perno, lanza), fixed_WheelFL/FR/BR, fixed_WheelBroken
  (la acostada) y fixed_Cargo (cajón y bolsas).
- Inferido: el eje de giro (perno rey) y el reparto del 12° en rolido + cabeceo; arcos a z -3,8/-1,2/1,4
  y el quebrado en 4,0; cómo está rota la lona (paño 1 entero, paño 2 solo la izquierda y una tira
  baja a la derecha con jirones, paño 3 caído atrás a la izquierda); tablón roto a la derecha; lanza en
  el piso; cajón volcado con la tapa corrida y dos bolsas; sin pintura mostaza (para no confundirla con
  la carreta del jugador); nombres fixed_* de lo que no se rompe.

Vueltas: 1) frag06 con 6 aristas no-manifold y 12 de giro inconsistente: la lona arrancaba justo en la
cara del arco 1 y sus vértices se soldaban con los del arco; fixed_Frame con 2 pares coplanares
(largueros y cabezal de atrás terminaban en 2,2) · 2) lona 0,02 más allá del arco, cabezal a 2,18,
rueda trasera 0,004 más alta (la pina inclinada bajaba del piso) · 3) bolsas apoyadas exacto (bajaban
0,0024: centro = radio vertical).

Revisión
- 1572 triángulos contra 900 de referencia: las 4 ruedas son 772 (196 cada una: pina en dos prismas con
  llanta pintada 104, 6 barras = 12 rayos 72, cubo 20). Los 12 rayos sueltos los pide el estilo de la
  carreta del jugador; con menos rayos o rueda maciza dejarían de ser "la misma rueda". El resto, 800:
  arcos con lona y jirones 348, tablas 176, armazón 128, carga 120.
- Medidas: caja 5 x 10 como pide el prompt; el conjunto mide 10,3 x 7,2 x 17,7 porque suma la rueda
  acostada, la lanza en el piso (5,8 hacia adelante) y la carga (2,5 hacia atrás).
- Fragmentos: piso 27,7 % y 22,2 %, tablas 14 %, tabla de adelante 4,7 %, arcos 4,5-7,2 %. Mínimos
  0,40-2,96. Los arcos con su lona NO son convexos (un arco es una U): con colisión de casco rebotan como
  medio tambor. Es escombro de un segundo; si molesta, pasarlos a fixed_ (decide Valentin).
- La lona es plana entre arcos (un prisma por paño): no hay forma barata de hacerla colgar sin que los
  vértices de los tramos se suelden. Rotura con jirones triangulares y paños que faltan.
"""

import math

from mathutils import Euler, Vector

A, BH, Y0 = 2.3, 3.0, 4.0          # arcos: medio ancho, alto sobre la tabla, base
PHI = 11.0                         # rolido (izquierda abajo)
K = (0.0, 2.2, -3.5)               # perno rey
HUB_B = (3.0, 1.9, 3.5)            # rueda trasera derecha (local, caja derecha)
HUB_F = 3.0
R_F, R_B = 1.6, 1.9
HOOPS_Z = (-3.8, -1.2, 1.4)
SNAP_Z = 4.0


def _mat(rot):
    return Euler([math.radians(a) for a in rot], "XYZ").to_matrix()


def _theta():
    """Cabeceo que deja la rueda trasera derecha apoyada (su centro a 1,9)."""
    lo, hi = 0.0, 15.0
    for _ in range(40):
        mid = (lo + hi) / 2
        y = K[1] + (_mat((mid, 0, PHI)) @ (Vector(HUB_B) - Vector(K))).y
        lo, hi = (mid, hi) if y > HUB_B[1] + 0.004 else (lo, mid)   # +0,004: la pina inclinada no baja del piso
    return (lo + hi) / 2


THETA = _theta()
ROT = (THETA, 0.0, PHI)
_E = _mat(ROT)


def T(p):
    """Local de la caja (derecha) -> mundo (ladeada sobre el perno rey)."""
    return tuple(Vector(K) + _E @ (Vector(p) - Vector(K)))


def TT(pts):
    return [T(p) for p in pts]


def ell(t, add):
    a = math.radians(t)
    return ((A + add) * math.cos(a), Y0 + (BH + add) * math.sin(a))


def band(t0, t1, add_in, add_out, n, hang_right=False, hang_left=False):
    """Perfil (x, y) de un arco elíptico grueso de t0 a t1 grados; la lona puede bajar por el costado."""
    ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
    inner = [ell(t, add_in) for t in ts]
    outer = [ell(t, add_out) for t in reversed(ts)]
    if hang_right:
        inner = [(A + add_in, 3.6)] + inner
        outer = outer + [(A + add_out, 3.6)]
    if hang_left:
        inner = inner + [(-(A + add_in), 3.6)]
        outer = [(-(A + add_out), 3.6)] + outer
    return inner + outer


def bprism(mk, part, profile, depth, mat, plane, center, detail=False):
    mk.prism(part, profile, depth, mat, plane=plane, center=T(center), rot=ROT, detail=detail)


def bbox(mk, part, center, size, mat, detail=False):
    mk.hull(part, TT(mk.pts_box(center, size)), mat, detail=detail)


def tube(mk, part, a, b, r, mat, sides=4, detail=False):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    u = d.cross(Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = d.cross(u)
    pts = [tuple(p + r * (math.cos(t) * u + math.sin(t) * v)) for p in (a, b)
           for t in (2 * math.pi * (k + 0.5) / sides for k in range(sides))]
    mk.hull(part, pts, mat, detail=detail)


def wheel(mk, part, hub, radius, plane, rot=(0, 0, 0), missing=(), hub_len=0.62, width=0.32):
    """Rueda de 12 rayos: dos mitades de pina (prismas) con llanta pintada, 6 barras, cubo."""
    E = _mat(rot)
    to3 = {"zy": lambda a, b, d: (d, b, a), "xz": lambda a, b, d: (a, d, b)}[plane]

    def W(a, b, d):
        return tuple(Vector(hub) + E @ Vector(to3(a, b, d)))

    r_out, r_in, gap, n = radius, radius - 0.26, 0.4, 6
    for a0, a1 in ((gap, 180 - gap), (180 + gap, 360 - gap)):
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([(r_out * math.cos(math.radians(a)), r_out * math.sin(math.radians(a))) for a in angs]
                + [(r_in * math.cos(math.radians(a)), r_in * math.sin(math.radians(a))) for a in reversed(angs)])
        mk.prism(part, prof, width, "wood_mid", plane=plane, center=hub, rot=rot)
        for i in range(n):                                          # llanta de hierro: caras de afuera
            m, h = (angs[i] + angs[i + 1]) / 2, (angs[i + 1] - angs[i]) / 2
            rr = r_out * math.cos(math.radians(h))
            mk.paint(part, "iron", ball=(W(rr * math.cos(math.radians(m)), rr * math.sin(math.radians(m)), 0), 0.06))
    L = r_in + 0.06
    for k in range(6):                                              # 6 barras = 12 rayos
        if k in missing:
            continue
        c, s = math.cos(math.radians(30 * k)), math.sin(math.radians(30 * k))
        mk.hull(part, [W(t * c - w * s, t * s + w * c, d) for t in (-L, L) for w in (-0.08, 0.08)
                       for d in (-0.06, 0.06)], "wood_mid")
    mk.hull(part, [W(0.3 * math.cos(math.radians(60 * k + 30)), 0.3 * math.sin(math.radians(60 * k + 30)), d)
                   for k in range(6) for d in (-hub_len / 2, hub_len / 2)], "wood_dark")


def build(mk):
    # ---------------- piso partido por una grieta en zigzag ----------------
    crack = [(2.5, 0.35), (1.6, 0.85), (0.6, 0.2), (-0.5, 0.9), (-1.5, 0.3), (-2.5, 0.7)]
    f1 = mk.part("frag01", (0, 0, 0))
    bprism(mk, f1, [(-2.5, -5.0), (2.5, -5.0)] + crack, 0.4, "wood_mid", "xz", (0, 2.4, 0))
    f2 = mk.part("frag02", (0, 0, 0))
    bprism(mk, f2, list(reversed(crack)) + [(2.5, 5.0), (-2.5, 5.0)], 0.4, "wood_mid", "xz", (0, 2.4, 0))

    # ---------------- tablas laterales: tres tablones alternados (claro, medio hundido 0,03, claro) ----------------
    planks = ((2.6, 3.075), (3.065, 3.54), (3.53, 4.0))           # se enciman 0,01
    for name, s in (("frag03", -1), ("frag04", 1)):
        p = mk.part(name, (0, 0, 0))
        for i, (y0, y1) in enumerate(planks):
            inset = 0.03 if i == 1 else 0.0                         # el del medio, hundido de los dos lados
            mat = "wood_mid" if i == 1 else "wood_light"
            if s == 1 and i == 1:                                   # tablón del medio roto a la derecha
                # (z de arranque abajo, arriba), (z de punta abajo, arriba): puntas quebradas en diagonal
                for (a_lo, a_hi), (b_lo, b_hi) in (((-5.0, -5.0), (0.15, -0.2)), ((1.35, 1.75), (5.0, 5.0))):
                    pts = [(x, y, z) for x in (s * (2.1 + inset), s * (2.5 - inset))
                           for y, za, zb in ((y0, a_lo, b_lo), (y1, a_hi, b_hi)) for z in (za, zb)]
                    mk.hull(p, TT(pts), mat)
            else:
                bbox(mk, p, (s * 2.3, (y0 + y1) / 2, 0), (0.4 - 2 * inset, y1 - y0, 10.0), mat)
        # muñón del arco quebrado (en z = 4,0)
        t0, t1 = (0, 52) if s == 1 else (138, 180)
        bprism(mk, p, band(t0, t1, -0.2, 0.2, 2), 0.4, "wood_dark", "xy", (0, 0, SNAP_Z))

    # ---------------- tabla de adelante ----------------
    f5 = mk.part("frag05", (0, 0, 0))
    bbox(mk, f5, (0, 2.9, -4.8), (4.2, 0.6, 0.4), "wood_light")
    bbox(mk, f5, (0, 3.49, -4.795), (4.16, 0.6, 0.35), "wood_mid")     # más angosto en todo: sin caras coplanares

    # ---------------- arcos con su lona ----------------
    for i, z in enumerate(HOOPS_Z):
        h = mk.part(f"frag{6 + i:02d}", (0, 0, 0))
        bprism(mk, h, band(0, 180, -0.2, 0.2, 6), 0.4, "wood_dark", "xy", (0, 0, z))
        if i == 0:                                                  # paño 1: entero, de la boca al arco 2
            z0, z1 = -4.02, HOOPS_Z[1]                          # 0,02 más allá del arco: si arranca en su cara, los vértices se sueldan (no-manifold)
            bprism(mk, h, band(0, 180, 0.2, 0.26, 6, hang_right=True, hang_left=True), z1 - z0, "canvas",
                   "xy", (0, 0, (z0 + z1) / 2))
        elif i == 1:                                                # paño 2: arrancado arriba a la derecha
            z0, z1 = HOOPS_Z[1], HOOPS_Z[2]
            bprism(mk, h, band(98, 180, 0.2, 0.26, 3, hang_left=True), z1 - z0, "canvas", "xy",
                   (0, 0, (z0 + z1) / 2))
            bprism(mk, h, band(0, 26, 0.2, 0.26, 1, hang_right=True), z1 - z0, "canvas", "xy",
                   (0, 0, (z0 + z1) / 2))
            ex, ey = ell(98, 0.23)                                  # jirones que cuelgan del borde roto
            for zc, w, drop in ((-0.7, 0.5, 0.9), (0.0, 0.42, 0.6), (0.75, 0.55, 1.1)):
                bprism(mk, h, [(zc - w / 2, ey + 0.05), (zc + w / 2, ey + 0.05), (zc + 0.08, ey - drop)],
                       0.06, "canvas", "zy", (ex + 0.02, 0, 0), detail=True)
        else:                                                       # paño 3: caído atrás, solo la izquierda
            z0, z1 = HOOPS_Z[2], SNAP_Z - 0.2
            bprism(mk, h, band(122, 180, 0.2, 0.26, 2, hang_left=True), z1 - z0, "canvas", "xy",
                   (0, 0, (z0 + z1) / 2))
            ex, ey = ell(122, 0.23)
            for zc, w, drop in ((1.9, 0.6, 0.8), (2.8, 0.5, 1.2)):
                bprism(mk, h, [(zc - w / 2, ey + 0.05), (zc + w / 2, ey + 0.05), (zc - 0.1, ey - drop)],
                       0.06, "canvas", "zy", (ex + 0.03, 0, 0), detail=True)

    # ---------------- lo que queda en pie ----------------
    fr = mk.part("fixed_Frame", (0, 0, 0))
    for x in (-1.5, 1.5):                                           # largueros bajo el piso
        bbox(mk, fr, (x, 2.0, 0), (0.35, 0.4, 10.0), "wood_dark")
    bbox(mk, fr, (0, 1.94, 3.5), (5.0, 0.48, 0.42), "wood_dark")   # cabezal de atrás (tope 2,18: no coplanar con los largueros)
    bbox(mk, fr, (0.8, 1.9, 3.5), (4.8, 0.22, 0.22), "iron")       # eje de atrás (quebrado a la izquierda)
    tube(mk, fr, T((-1.5, 1.9, 3.5)), (-2.45, 0.15, 3.95), 0.13, "iron")   # punta quebrada, clavada en el piso
    mk.hull(fr, TT(mk.pts_cyl((0, 2.025, -3.5), 0.25, 0.35, sides=6)), "iron")  # perno rey (toca el piso)
    mk.box(fr, (0, 1.78, -3.5), (5.6, 0.36, 0.42), "wood_dark")    # cabezal del tren delantero (horizontal)
    mk.box(fr, (0, R_F, -3.5), (2 * HUB_F + 0.4, 0.22, 0.22), "iron")     # eje de adelante
    tube(mk, fr, (0, 1.5, -3.75), (0.5, 0.19, -9.3), 0.17, "wood_dark")   # lanza en el piso
    mk.box(fr, (0.5, 0.11, -9.25), (2.6, 0.22, 0.22), "wood_dark", rot=(0, 8, 0))   # balancín

    wheel(mk, mk.part("fixed_WheelFL", (0, 0, 0)), (-HUB_F, R_F, -3.5), R_F, "zy")
    wheel(mk, mk.part("fixed_WheelFR", (0, 0, 0)), (HUB_F, R_F, -3.5), R_F, "zy")
    wheel(mk, mk.part("fixed_WheelBR", (0, 0, 0)), T(HUB_B), R_B, "zy", rot=ROT)
    wheel(mk, mk.part("fixed_WheelBroken", (0, 0, 0)), (-4.8, 0.16, 5.4), R_B, "xz", rot=(0, 15, 0),
          missing=(2,), hub_len=0.32)

    # ---------------- carga volcada atrás ----------------
    cg = mk.part("fixed_Cargo", (0, 0, 0))
    cx, cz, yaw = -0.6, 7.2, 25.0
    E = _mat((0, yaw, 0))

    def C(p):
        return tuple(Vector((cx, 0, cz)) + E @ Vector(p))

    mk.hull(cg, [C(p) for p in mk.pts_box((0, 0.7, 0), (1.4, 1.4, 1.4))], "wood_light")
    mk.hull(cg, [C(p) for p in mk.pts_box((0.25, 1.46, -0.1), (1.5, 0.14, 1.5), rot=(0, 12, -6))], "wood_mid")

    def sack(c, length, r, ang):
        Es = _mat((0, ang, 0))
        pts = []
        for s, k in ((-0.5, 0.55), (-0.25, 1.0), (0.25, 1.0), (0.5, 0.7)):
            for j in range(5):
                a = 2 * math.pi * j / 5 + 1.5 * math.pi          # un punto justo abajo: apoya en el piso
                pts.append(C(tuple(Vector(c) + Es @ Vector((s * length, r * k * 0.72 * math.sin(a),
                                                            r * k * math.cos(a))))))
        mk.hull(cg, pts, "canvas")
        tip = C(tuple(Vector(c) + Es @ Vector((0.5 * length + 0.12, 0, 0))))
        base = C(tuple(Vector(c) + Es @ Vector((0.5 * length - 0.05, 0, 0))))
        tube(mk, cg, base, tip, 0.13, "rope")

    sack((1.12, 0.3315, 0.1), 1.3, 0.46, 80)        # apoyada contra el cajón (centro = radio vertical 0,72 r)
    sack((-0.3, 0.3027, -1.05), 1.2, 0.42, 10)      # delante del cajón

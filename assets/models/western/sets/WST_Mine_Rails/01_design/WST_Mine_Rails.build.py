"""
Receta de WST_Mine_Rails, los rieles de trocha angosta de la mina (prompt 102, Bloques A + B).

Brief
- Silueta a 40 studs: dos barras de hierro oscuro sobre una escalera de durmientes de madera oscura.
  Lo que identifica cada pieza es su trazado (recta, curva, Y, tope, rampa), no el detalle del riel.
- Medidas: trocha 3,0 entre centros de riel (x = ±1,5: calza con las ruedas de WST_Vehicle_MineCart,
  marcador _RailGauge); riel de 0,12 x 0,3 (y 0,19-0,50, metido 0,01 en los durmientes); durmientes
  3,8 x 0,2 x 0,5 (y 0-0,2). La cara de arriba del riel queda a y = 0,5: la vagoneta (y = 0 en el riel)
  va 0,5 por encima del piso de estas piezas.
- Convención de las puntas: todas las piezas entran por z = +4 (x = 0) yendo hacia -Z, como la punta de
  atrás de Rail_Straight; el origen es el de una Rail_Straight que compartiera esa entrada. Las puntas
  cortan el riel en un plano vertical (la rampa también): dos piezas cualesquiera calzan exacto.
- Durmientes: paso 8/7 = 1,143 (≈ 1,2 del prompt) con medio paso en cada punta, así la junta entre
  piezas mantiene el paso. En las curvas, el entero más cercano (Rail_Curve 1,178).
- Piezas (un objeto cada una; en el archivo van en fila sobre X, cada una con su origen):
  Rail_Straight (8), Rail_Curve (90° a la derecha, radio 12 en el eje, sale en (12, -8) hacia +X),
  Rail_Switch (Y simétrica: dos Rail_Curve espejadas que salen en (±12, -8); agujas que nacen del riel
  de afuera y corazón donde se cruzan los rieles de adentro), SwitchLever (palanca de cambio con
  contrapeso, origen en su eje sobre la caja del cambio), Rail_Bumper (recta de 8 con tope de madera
  apuntalado al final; ocupa hasta z = -5), Rail_Ramp (sube 2 en 8, sobre dos largueros y dos postes).
- Inferido: la sección rectangular del riel (sin patín: no se ve a 40 studs y en la curva costaba el
  doble), la altura 0,5 de la cara del riel, la convención de puntas y orígenes, la Y como dos curvas de
  90° (es la única forma de que sus salidas calcen con Rail_Curve), los durmientes largos compartidos
  donde las ramas de la Y todavía se pisan, la palanca de cambio a la izquierda de la entrada, el largo
  del tope (8, como la recta, para reemplazarla al final de una vía) y la estructura de la rampa.

Vueltas: 1) z-fighting: las franjas rojas del tope del mismo alto que la viga, postes, solera y durmiente
con la base en y = 0, travesaño de la rampa del ancho de los postes; los postes de la rampa bajaban a
-0,01 · 2) las ayudas aceptan detail=True (los túneles tallan la roca y el cortador se comía la vía).

Revisión
- Triángulos contra 150 por pieza: Rail_Straight 108; Rail_Curve 360 (18,85 de largo: 16 durmientes y dos
  rieles de 10 tramos); Rail_Switch 684 + SwitchLever 92 (son dos curvas de 90° superpuestas: 26
  durmientes, cuatro rieles, agujas y corazón); Rail_Bumper 268 (viga, postes, puntales, soleras, chapa y
  franjas de peligro: lo que se lee como tope); Rail_Ramp 212 (dos largueros y dos caballetes que la
  sostienen). Ninguna pieza gasta en detalle que no se vea: el riel es una barra.
- Calce con la vagoneta: riel de x = 1,44 a 1,56; la pestaña de la rueda (x 1,39-1,44, baja hasta y 0,42)
  roza la cara de adentro del riel, no lo atraviesa.
- Agujas 0,012 más bajas y 0,02 más angostas que el riel de stock donde se enciman (no coplanares); el
  riel de afuera de la rama derecha se corta 0,17 a cada lado del corazón.
- Durmientes de la Y: compartidos y alargados (hasta 8) mientras las dos ramas se pisan; después, cada
  rama los suyos. Queda un hueco de un paso entre los dos grupos (z ≈ -2,9) donde los rieles no tienen
  durmiente: aceptado, no se nota a la altura de juego.
- Las piezas no se tocan entre sí en el archivo (fila sobre X): cada una es una pieza suelta del kit.
"""

import math

GAUGE = 3.0
HALF = GAUGE / 2
RAIL_W = 0.12
RAIL_Y0, RAIL_Y1 = 0.19, 0.50            # barra del riel; la cara de arriba es la de la vagoneta
TIE_L, TIE_W, TIE_H = 3.8, 0.5, 0.2
TIE_STEP = 8 / 7
ENTRY = 4.0                              # todas las piezas entran por z = +4
R_CURVE = 12.0
TIE_MAT, RAIL_MAT = "wood_dark", "iron"

# irregularidad fija de los durmientes (giro en grados, corrimiento a lo largo, largo extra)
JIT = [(1.5, 0.03, 0.06), (-1.0, -0.02, -0.08), (2.5, 0.0, 0.1), (-2.0, 0.04, 0.0), (0.5, -0.03, -0.05),
       (-2.8, 0.02, 0.08), (1.8, -0.04, -0.1), (-0.6, 0.01, 0.04), (2.2, 0.03, -0.06)]


# ---------------- ayudas que usan otras recetas de la mina (túneles, boca, galería) ----------------
def tie_positions(length, step=TIE_STEP):
    """Posiciones a lo largo de un tramo: el entero de durmientes más cercano, medio paso en las puntas."""
    n = max(1, round(length / step))
    st = length / n
    return [st * (i + 0.5) for i in range(n)]


def tie(mk, part, center, yaw, k=0, left=TIE_L / 2, right=TIE_L / 2, y0=0.0, jitter=True, detail=False):
    """Durmiente sobre el piso y0: `yaw` en grados (0 = cruzado a la vía que va hacia -Z).
    left/right: medio largo a cada lado del eje (para los durmientes recortados de la Y)."""
    dy, ds, dl = JIT[k % len(JIT)] if jitter else (0, 0, 0)
    a = math.radians(yaw + dy)
    off = (right - left) / 2
    cx = center[0] + off * math.cos(a) + ds * math.sin(a)
    cz = center[1] - off * math.sin(a) + ds * math.cos(a)
    mk.box(part, (cx, y0 + TIE_H / 2, cz), (left + right + dl, TIE_H, TIE_W), TIE_MAT, rot=(0, yaw + dy, 0), detail=detail)


def straight_track(mk, part, x, z0, z1, y0=0.0, ties=True, first_k=0, detail=False):
    """Vía recta a lo largo de Z, de z0 a z1 (z0 > z1), centrada en x, sobre el piso y0.
    detail=True cuando la pieza tiene tallados (túneles): si no, el cortador se la come."""
    L = z0 - z1
    if ties:
        for k, s in enumerate(tie_positions(L)):
            tie(mk, part, (x, z0 - s), 0.0, k + first_k, y0=y0, detail=detail)
    for sx in (-HALF, HALF):
        mk.box(part, (x + sx, y0 + (RAIL_Y0 + RAIL_Y1) / 2, (z0 + z1) / 2), (RAIL_W, RAIL_Y1 - RAIL_Y0, L), RAIL_MAT,
               detail=detail)


def arc_point(c, r, phi_deg, turn):
    """Punto (x, z) del arco de radio r alrededor de c; phi = cuánto se avanzó desde la entrada (grados).
    turn = +1: dobla a la derecha (el centro queda a +X de la entrada); -1: a la izquierda."""
    p = math.radians(phi_deg)
    return (c[0] - turn * r * math.cos(p), c[1] - r * math.sin(p))


def arc_band(c, r, w, a0, a1, n, turn):
    """Contorno (x, z) de una banda de ancho w sobre el arco de radio r, de a0 a a1 grados."""
    outer = [arc_point(c, r + w / 2, a0 + (a1 - a0) * i / n, turn) for i in range(n + 1)]
    inner = [arc_point(c, r - w / 2, a0 + (a1 - a0) * i / n, turn) for i in range(n + 1)]
    return outer + inner[::-1]


def rail_arc(mk, part, c, r, a0, a1, turn, y0=0.0, top=RAIL_Y1, seg_deg=9.0, w=RAIL_W, detail=False):
    n = max(1, round(abs(a1 - a0) / seg_deg))
    yb = y0 + RAIL_Y0
    yt = y0 + top
    mk.prism(part, arc_band(c, r, w, a0, a1, n, turn), yt - yb, RAIL_MAT, plane="xz",
             center=(0, (yb + yt) / 2, 0), detail=detail)


def curve_track(mk, part, c, R, a0, a1, turn, y0=0.0, ties=True, first_k=0, seg_deg=9.0, detail=False):
    """Vía curva: eje de radio R alrededor de c, de a0 a a1 grados (rieles a R ± 1,5)."""
    L = math.radians(a1 - a0) * R
    if ties:
        for k, s in enumerate(tie_positions(L)):
            phi = a0 + math.degrees(s / R)
            tie(mk, part, arc_point(c, R, phi, turn), -turn * phi, k + first_k, y0=y0, detail=detail)
    for o in (-HALF, HALF):
        rail_arc(mk, part, c, R - turn * o, a0, a1, turn, y0=y0, seg_deg=seg_deg, detail=detail)


# ---------------- choque entre durmientes (rectángulos en planta) ----------------
def _corners(center, yaw, left, right):
    a = math.radians(yaw)
    ux, uz = math.cos(a), -math.sin(a)          # eje largo del durmiente (yaw 0 = +X)
    vx, vz = math.sin(a), math.cos(a)
    cx, cz = center
    pts = []
    for l, w in ((-left, -TIE_W / 2), (right, -TIE_W / 2), (right, TIE_W / 2), (-left, TIE_W / 2)):
        pts.append((cx + ux * l + vx * w, cz + uz * l + vz * w))
    return pts


def _overlap(p, q, margin=0.06):
    for poly in (p, q):
        for i in range(4):
            a, b = poly[i], poly[(i + 1) % 4]
            nx, nz = b[1] - a[1], a[0] - b[0]
            pa = [nx * x + nz * z for x, z in p]
            qa = [nx * x + nz * z for x, z in q]
            ln = math.hypot(nx, nz)
            if max(pa) + margin * ln < min(qa) or max(qa) + margin * ln < min(pa):
                return False
    return True


# ---------------- piezas ----------------
def rail_straight(mk, ox):
    p = mk.part("Rail_Straight", (ox, 0, 0))
    straight_track(mk, p, ox, ENTRY, -ENTRY)


def rail_curve(mk, ox):
    p = mk.part("Rail_Curve", (ox, 0, 0))
    curve_track(mk, p, (ox + R_CURVE, ENTRY), R_CURVE, 0.0, 90.0, +1)


def rail_switch(mk, ox):
    """Y simétrica: rama derecha (centro CR) y rama izquierda (centro CL), radio 12 en el eje."""
    p = mk.part("Rail_Switch", (ox, 0, 0))
    CR, CL = (ox + R_CURVE, ENTRY), (ox - R_CURVE, ENTRY)
    r_in, r_out = R_CURVE - HALF, R_CURVE + HALF
    # rieles de adentro (cada uno es el riel "de stock" de su lado): enteros
    rail_arc(mk, p, CR, r_in, 0, 90, +1)
    rail_arc(mk, p, CL, r_in, 0, 90, -1)
    # rieles de afuera: nacen como aguja contra el riel de stock del otro lado (más bajos 0,012 al
    # principio, así no quedan coplanares), y el de la rama derecha se corta en el corazón.
    s_tip = 0.95                                         # ahí la aguja ya está a 0,08 del riel de stock
    blade_end = math.degrees(2.2 / r_out)
    tip = math.degrees(s_tip / r_out)
    for c, turn in ((CR, +1), (CL, -1)):
        rail_arc(mk, p, c, r_out, tip, blade_end + 0.4, turn, top=RAIL_Y1 - 0.012, w=0.10)   # aguja
    # corazón: los dos rieles de afuera se cruzan en x = ox, z = 4 - sqrt(13,5² - 12²)
    zf = ENTRY - math.sqrt(r_out ** 2 - R_CURVE ** 2)
    phi_f = math.degrees(math.asin((ENTRY - zf) / r_out))
    gap = math.degrees(0.17 / r_out)
    rail_arc(mk, p, CL, r_out, blade_end, 90, -1)                                       # entero
    rail_arc(mk, p, CR, r_out, blade_end, phi_f - gap, +1)                              # cortado en el corazón
    rail_arc(mk, p, CR, r_out, phi_f + gap, 90, +1)
    # durmientes: cada rama los suyos donde ya no se pisan; antes, durmientes largos compartidos
    branch = []
    L = math.radians(90) * R_CURVE
    for k, s in enumerate(tie_positions(L)):
        phi = math.degrees(s / R_CURVE)
        rc = arc_point(CR, R_CURVE, phi, +1)
        lc = arc_point(CL, R_CURVE, phi, -1)
        right = _corners(rc, -phi, TIE_L / 2, TIE_L / 2)
        left = _corners(lc, phi, TIE_L / 2, TIE_L / 2)
        branch.append((k, phi, rc, lc, _overlap(right, left)))
    first = next(i for i, b in enumerate(branch) if not b[4] and all(not bb[4] for bb in branch[i:]))
    shared = []
    for k, s in enumerate(tie_positions(8.0 * 2)):
        z = ENTRY - s
        dz = ENTRY - z
        if dz > r_in:
            break
        xr = R_CURVE - math.sqrt(r_in ** 2 - dz ** 2)      # riel de adentro de la rama derecha
        half = xr + 0.45
        rect = _corners((ox, z), 0.0, half, half)
        clash = any(_overlap(rect, _corners(b[2], -b[1], TIE_L / 2, TIE_L / 2)) for b in branch[first:])
        if clash:
            break
        shared.append((k, z, half))
    for k, z, half in shared:
        left = half + (1.9 if k < 2 else 0.0)            # los dos primeros sostienen la caja del cambio
        tie(mk, p, (ox, z), 0.0, k, left=left, right=half, jitter=False)
    for k, phi, rc, lc, _ in branch[first:]:
        tie(mk, p, rc, -phi, k)
        tie(mk, p, lc, phi, k + 3)
    # caja del cambio sobre los dos primeros durmientes (lado izquierdo) y varilla a las agujas
    z0, z1 = shared[0][1], shared[1][1]
    sz = (z0 + z1) / 2
    mk.box(p, (ox - 2.95, TIE_H + 0.24, sz), (0.5, 0.5, 0.9), "iron")
    mk.box(p, (ox - 2.95, TIE_H + 0.52, sz), (0.36, 0.08, 0.5), "rust")                  # tapa de la caja
    rod_z = ENTRY - s_tip - 0.25
    mk.box(p, (ox - 0.6, RAIL_Y0 + 0.12, rod_z), (4.9, 0.08, 0.08), "rust")
    return p, (ox - 2.95, TIE_H + 0.56, sz)


def switch_lever(mk, pivot):
    """Palanca de cambio de piso: eje a lo largo de Z sobre la caja; tirada 22° hacia -X; contrapeso."""
    lv = mk.part("SwitchLever", pivot)
    px, py, pz = pivot
    a = math.radians(22)
    top = (px - 1.45 * math.sin(a), py + 1.45 * math.cos(a), pz)
    mk.cyl(lv, (px, py, pz), 0.09, 0.62, "iron", axis="z", sides=6)                     # eje
    mk.hull(lv, [(px + dx, py + dy, pz + dz) for dx, dy in ((-0.05, -0.02), (0.05, -0.02)) for dz in (-0.05, 0.05)]
            + [(top[0] + dx, top[1] + dy, pz + dz) for dx, dy in ((-0.04, 0.0), (0.04, 0.0)) for dz in (-0.04, 0.04)],
            "iron")                                                                         # brazo
    w = (px - 0.55 * math.sin(a), py + 0.55 * math.cos(a), pz)
    mk.box(lv, w, (0.36, 0.3, 0.34), "rust", rot=(0, 0, 22))                              # contrapeso
    mk.cyl(lv, (top[0], top[1] + 0.05, pz), 0.07, 0.24, "wood_mid", axis="y", sides=6,
           rot=(0, 0, 22))                                                                  # mango
    mk.cyl(lv, (top[0] - 0.02, top[1] - 0.25, pz), 0.24, 0.05, "warning_red", axis="z", sides=8)  # disco de señal


def rail_bumper(mk, ox):
    p = mk.part("Rail_Bumper", (ox, 0, 0))
    straight_track(mk, p, ox, ENTRY, -3.2, ties=False)
    for k, s in enumerate(tie_positions(8.0)):
        tie(mk, p, (ox, ENTRY - s), 0.0, k)
    zb = -3.15                                               # cara del tope (donde pega la vagoneta)
    # viga del tope (madera clara: se lee contra el durmiente oscuro), chapa de hierro y franja roja
    mk.box(p, (ox, 1.32, zb - 0.32), (3.9, 0.62, 0.62), "wood_mid")
    mk.box(p, (ox, 1.32, zb - 0.015), (2.2, 0.34, 0.05), "iron")
    for sx in (-1, 1):
        mk.box(p, (ox + sx * 1.52, 1.32, zb - 0.01), (0.8, 0.56, 0.04), "warning_red")
        # postes (en los rieles) y puntales hacia atrás, sobre una solera
        mk.box(p, (ox + sx * HALF, 1.005, zb - 0.32), (0.42, 1.91, 0.42), "wood_dark")      # metido en durmiente y solera
        mk.box(p, (ox + sx * HALF, 0.202, zb - 1.05), (0.44, 0.396, 1.9), "wood_dark")       # solera (0,004 sobre el piso: no coplanar con el durmiente)
        mk.hull(p, [(ox + sx * HALF + dx, y, z) for dx in (-0.17, 0.17)
                    for y, z in ((1.3, zb - 0.6), (1.6, zb - 0.6), (0.38, zb - 1.8), (0.38, zb - 1.45))], "wood_dark")
    for sx in (-1, 1):                                        # pernos de la chapa
        mk.cyl(p, (ox + sx * 0.75, 1.32, zb - 0.05), 0.07, 0.07, "rust", axis="z", sides=6)


def rail_ramp(mk, ox):
    """Sube 2 en 8: de y = 0 en z = +4 a y = 2 en z = -4."""
    p = mk.part("Rail_Ramp", (ox, 0, 0))
    rise = 2.0

    def h(z):
        return (ENTRY - z) / 8.0 * rise

    a = math.degrees(math.atan2(rise, 8.0))
    for k, s in enumerate(tie_positions(8.0)):
        z = ENTRY - s
        dy, ds, dl = JIT[k % len(JIT)]
        mk.box(p, (ox, h(z) + TIE_H / 2, z), (TIE_L + dl, TIE_H, TIE_W), TIE_MAT, rot=(a, dy, 0))
    for sx in (-HALF, HALF):
        prof = [(ENTRY, RAIL_Y0), (ENTRY, RAIL_Y1), (-ENTRY, RAIL_Y1 + rise), (-ENTRY, RAIL_Y0 + rise)]
        mk.prism(p, prof, RAIL_W, RAIL_MAT, plane="zy", center=(ox + sx, 0, 0))
    # dos largueros bajo los durmientes y dos caballetes (poste + travesaño)
    for sx in (-1.05, 1.05):
        prof = [(3.75, 0.0), (3.75, h(3.75) + 0.012), (-3.95, h(-3.95) + 0.012),     # metido 0,015 en los durmientes
                (-3.95, h(-3.95) - 0.45), (2.15, 0.0)]
        mk.prism(p, prof, 0.4, "wood_mid", plane="zy", center=(ox + sx, 0, 0))
    for zc in (-0.6, -3.5):
        top = h(zc) - 0.4
        mk.box(p, (ox, top - 0.17, zc), (3.3, 0.36, 0.42), "wood_dark")                     # travesaño
        for sx in (-1, 1):
            mk.box(p, (ox + sx * 1.35, (top - 0.28) / 2, zc), (0.4, top - 0.28, 0.4), "wood_dark")


def build(mk):
    rail_switch_part, pivot = rail_switch(mk, -26.0)
    switch_lever(mk, pivot)
    rail_ramp(mk, -8.0)
    rail_straight(mk, 0.0)
    rail_bumper(mk, 6.0)
    rail_curve(mk, 12.0)

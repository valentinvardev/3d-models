"""
Receta de WST_DG_JailInterior, la celda de la cárcel (prompt 081, Bloques A + B).

Brief
- Se recorre por adentro: el jugador ve el frente de barrotes desde la oficina (-Z) y el interior de la
  celda (+Z). Silueta a 40 studs: una reja negra de 8 x 9 con dos flejes y la puerta con la cerradura
  grande; adentro el catre colgado de cadenas con la manta clara y el balde; afuera el escritorio con la
  pila de afiches y el aro de llaves.
- Medidas: frente de 8 (x de -4 a 4) x 9 de alto en z = 0 (marco de planchuela, barrotes de 0,12 cada 0,6,
  flejes a y = 3 y 6,5). Puerta (CellDoor) de 2,86 (x de 0,67 a 3,53) entre el poste de la cerradura
  (x = 0,45-0,65) y el de las bisagras (3,75-4): origen en el eje de las bisagras, abajo (3,64, 0, 0), afuera
  del poste; gira sobre Y. Celda de 6 de
  fondo (pared de atrás implícita en z = 6).
- Piezas: CellFront (marco, barrotes fijos, flejes, pernos de las bisagras, cerradero), CellDoor,
  CellDoor_Broken (la misma puerta arrancada: abierta 80° hacia la oficina y colgando 5° de la bisagra de
  arriba, la de abajo rota, dos barrotes doblados hacia afuera y el fleje de abajo arrancado; puesta 7 a la
  derecha para que no se pise con la sana, origen en su eje de bisagras), Bunk (catre de 3 tablas colgado
  de dos cadenas a la pared, manta de lona), Bucket (balde de madera con zunchos), Desk (escritorio con
  cajonera y la pila de afiches en blanco), Keys (aro con tres llaves, apoyado en el escritorio).
- Colores: hierro en reja, cadenas y llaves (una de bronce), madera del catre, balde y escritorio, lona en
  la manta, crema en los afiches; la bocallave tallada en coal.
- Inferido: nombres CellFront, Bunk, Bucket y Desk; puerta a la derecha con las bisagras contra la pared;
  fondo de la celda 6; catre de 6 x 2 a 1,8; escritorio de 4 x 2 x 2,6 (como el del telégrafo);
  disposición de la muestra; posición de la variante rota.

Vueltas: 1) 2308 tris: la bocallave tallada unía en una booleana todos los barrotes de la puerta (664) y
el hueco del balde, zunchos y asa; el eje de las bisagras quedaba adentro del poste (pernos escondidos) ·
2) poste de la cerradura en 0,45 y eje en 3,64; en puerta y balde solo la pieza tallada queda en la base
(el resto, detalle): 1408 · 3) z-fighting de ménsulas del catre y faldón del escritorio · 4) las llaves
flotaban a y = 5,2 (altura sumada dos veces).

Revisión
- 1408 triángulos contra 1200 (+17 %): CellFront 260, CellDoor 254, CellDoor_Broken 208, Keys 204 (aro y
  tres llaves de primer plano: es objeto con nombre), Desk 168, Bunk 160, Bucket 154.
- Medidas: frente 8 x 9 x 0,24 (la cerradura sale 0,32 hacia la oficina); puerta de 2,86 x 8,4; celda de
  6 de fondo (catre de 6 x 2 a 1,8 contra z = 6); escritorio 4 x 2,6 x 2.
- CellDoor gira sobre Y en (3,64, 0, 0). CellDoor_Broken tiene el mismo origen corrido 7 en X: para
  usarla se pone su origen en el eje de la celda. Su punta de la cerradura apoya en el piso.
- Colisión: CellFront es una placa (los barrotes cada 0,6 no dejan pasar a nadie).
- Dudoso: la puerta rota en un objeto aparte al costado (no superpuesta a la sana para que no se pisen).
"""

import math

from mathutils import Euler, Vector

HX = 3.64                                  # eje de las bisagras (afuera del poste)
BANDS = ((2.85, 3.15), (6.35, 6.65))
IRON, MID, DARK = "iron", "wood_mid", "wood_dark"
BROKEN_DX = 7.0
TOP_HINGE_Y = 7.25


def bpts(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def ring(c, r, axis_dir, n, phase=0.5):
    a = Vector(axis_dir).normalized()
    u = a.cross(Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = a.cross(u)
    c = Vector(c)
    return [tuple(c + r * (math.cos(2 * math.pi * (i + phase) / n) * u + math.sin(2 * math.pi * (i + phase) / n) * v))
            for i in range(n)]


def cyl_pts(c, r, h, n=8):
    x, y, z = c
    return ring((x, y - h / 2, z), r, (0, 1, 0), n) + ring((x, y + h / 2, z), r, (0, 1, 0), n)


def tube(mk, part, a, b, r, mat, sides=4, detail=False):
    a, b = Vector(a), Vector(b)
    mk.hull(part, ring(a, r, b - a, sides) + ring(b, r, b - a, sides), mat, detail)


# ---------------------------------------------------------------- frente fijo
LATCH = (0.45, 0.65)                       # poste de la cerradura
DOOR_X0, DOOR_X1 = 0.67, 3.53              # hoja: parante de la cerradura a parante de las bisagras


def build_front(mk):
    f = mk.part("CellFront", (0, 0, 0))
    mk.hull(f, bpts(-4.0, 4.0, 0.0, 0.2, -0.12, 0.12), IRON)                     # solera
    mk.hull(f, bpts(-4.0, 4.0, 8.75, 9.0, -0.12, 0.12), IRON)                    # dintel
    for x0, x1 in ((-4.0, -3.75), LATCH, (3.75, 4.0)):                            # postes
        mk.hull(f, bpts(x0 + 0.002, x1 - 0.002, 0.18, 8.77, -0.1, 0.1), IRON)
    for k in range(7):                                                           # barrotes
        x = -3.45 + 0.6 * k
        mk.hull(f, bpts(x - 0.06, x + 0.06, 0.19, 8.76, -0.06, 0.06), IRON)
    for y0, y1 in BANDS:                                                          # flejes
        mk.hull(f, bpts(-3.76, LATCH[0] + 0.01, y0, y1, -0.11, 0.11), IRON)
    for y0 in (0.85, 6.5):                                                        # pernos de las bisagras
        mk.hull(f, cyl_pts((HX, y0 + 0.21, 0), 0.1, 0.42), IRON)
        mk.hull(f, bpts(HX, 3.8, y0 + 0.05, y0 + 0.37, -0.04, 0.04), IRON)
    mk.hull(f, bpts(LATCH[0] + 0.03, LATCH[1] + 0.02, 3.75, 4.2, -0.2, -0.08), IRON)   # cerradero


# ---------------------------------------------------------------- puerta (sana y rota)
def door_shapes(broken):
    """Cascos de la puerta cerrada, en coordenadas del frente (eje de bisagras en x = HX).
    El primero es la cerradura (la única pieza que se talla)."""
    s = [bpts(DOOR_X0 + 0.03, DOOR_X0 + 0.68, 3.55, 4.45, -0.32, -0.07)]        # cerradura
    s.append(bpts(DOOR_X1 - 0.2, DOOR_X1, 0.25, 8.65, -0.09, 0.09))               # parante de bisagras
    s.append(bpts(DOOR_X0, DOOR_X0 + 0.2, 0.25, 8.65, -0.09, 0.09))               # parante de la cerradura
    s.append(bpts(DOOR_X0 + 0.18, DOOR_X1 - 0.18, 8.43, 8.63, -0.08, 0.08))       # travesaños
    s.append(bpts(DOOR_X0 + 0.18, DOOR_X1 - 0.18, 0.27, 0.47, -0.08, 0.08))
    for k in range(4):                                                            # barrotes
        x = DOOR_X0 + 0.5 + 0.6 * k
        if broken and k in (1, 2):                                                # doblados hacia la oficina
            bow = -0.45 if k == 1 else -0.32
            ym = 4.4 if k == 1 else 4.9
            s.append([(x + dx, y, z + dz) for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)
                      for (y, z) in ((0.45, 0.0), (ym, bow))])
            s.append([(x + dx, y, z + dz) for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)
                      for (y, z) in ((ym - 0.02, bow), (8.45, 0.0))])
        else:
            s.append(bpts(x - 0.06, x + 0.06, 0.45, 8.45, -0.06, 0.06))
    for i, (y0, y1) in enumerate(BANDS):                                          # flejes
        if broken and i == 0:
            s.append(bpts(DOOR_X0 + 0.18, DOOR_X0 + 0.78, y0, y1, -0.1, 0.1))      # quedó un pedazo
            continue
        s.append(bpts(DOOR_X0 + 0.18, DOOR_X1 - 0.18, y0, y1, -0.1, 0.1))
    for y0 in (1.29, 6.94):                                                       # bisagras
        if broken and y0 < 2:                                                     # la de abajo, arrancada
            s.append(bpts(DOOR_X1 - 0.02, DOOR_X1 + 0.2, y0 + 0.08, y0 + 0.3, -0.04, 0.04))
            continue
        s.append(cyl_pts((HX, y0 + 0.24, 0), 0.1, 0.46))
        s.append(bpts(DOOR_X1 - 0.08, HX, y0 + 0.04, y0 + 0.42, -0.04, 0.04))
    return s


def build_doors(mk):
    d = mk.part("CellDoor", (HX, 0, 0))
    shapes = door_shapes(False)
    mk.hull(d, shapes[0], IRON)                                                   # base: solo la cerradura
    for pts in shapes[1:]:
        mk.hull(d, pts, IRON, detail=True)                                        # (si no, la talla une todo)
    kx = DOOR_X0 + 0.32
    keyhole = [(kx - 0.05, 3.95), (kx + 0.05, 3.95), (kx + 0.03, 4.08), (kx + 0.07, 4.12), (kx + 0.07, 4.2),
               (kx + 0.03, 4.24), (kx - 0.03, 4.24), (kx - 0.07, 4.2), (kx - 0.07, 4.12), (kx - 0.03, 4.08)]
    mk.carve(d, "coal", prism=dict(profile=keyhole, depth=0.2, plane="xy", center=(0, 0, -0.32)))

    # rota: la misma puerta, abierta 80° hacia la oficina y colgando 5° de la bisagra de arriba
    hinge = Vector((HX, TOP_HINGE_Y, 0.0))
    tilt = Euler((0, 0, math.radians(5)), "XYZ").to_matrix()
    swing = Euler((0, math.radians(-80), 0), "XYZ").to_matrix()
    off = Vector((BROKEN_DX, 0, 0))

    def T(p):
        q = Vector(p) - hinge
        q = swing @ (tilt @ q)
        return tuple(q + hinge + off)

    b = mk.part("CellDoor_Broken", (HX + BROKEN_DX, 0, 0))
    for pts in door_shapes(True):
        mk.hull(b, [T(p) for p in pts], IRON)


# ---------------------------------------------------------------- catre, balde, escritorio, llaves
def build_bunk(mk):
    zw = 6.0                                                                     # pared de atrás
    b = mk.part("Bunk", (-0.5, 0, zw))
    x0, x1, y = -3.5, 2.5, 1.8
    for k, (za, zb) in enumerate(((4.0, 4.64), (4.68, 5.32), (5.36, 5.998))):    # tablas con juntas de 0,04
        mk.hull(b, bpts(x0 + 0.003 * k, x1 - 0.003 * k, y - 0.15, y, za, zb), MID)
    mk.hull(b, bpts(x0, x1, y - 0.42, y - 0.14, zw - 1.98, zw - 1.82), DARK)       # larguero de adelante
    mk.hull(b, bpts(x0, x1, y - 0.42, y - 0.14, zw - 0.2, zw - 0.004), DARK)       # listón contra la pared
    for x in (x0 + 0.35, x1 - 0.35):                                             # ménsulas de hierro
        mk.hull(b, bpts(x - 0.05, x + 0.05, y - 1.1, y - 0.145, zw - 0.15, zw - 0.002) +
                bpts(x - 0.05, x + 0.05, y - 0.32, y - 0.145, zw - 1.0, zw - 0.9), IRON)
    for x in (x0 + 0.15, x1 - 0.15):                                             # cadenas a la pared
        tube(mk, b, (x, y - 0.05, zw - 1.9), (x, y + 2.4, zw - 0.01), 0.05, IRON, sides=4)
    # manta de lona: tendida sobre dos tercios y caída por el frente, con el rollo de la almohada
    mk.hull(b, bpts(-3.3, 0.6, y - 0.005, y + 0.12, zw - 1.98, zw - 0.15), "canvas")
    mk.hull(b, [(x, yy, z) for x in (-3.2, 0.5) for (yy, z) in ((y + 0.1, zw - 1.9), (y - 0.7, zw - 2.05),
                                                               (y - 0.7, zw - 2.15), (y + 0.04, zw - 2.08))], "canvas")
    mk.cyl(b, (1.75, y + 0.22, zw - 1.0), 0.24, 1.6, "canvas", axis="z", sides=6)


def build_bucket(mk):
    bx_, bz = 3.0, 5.0
    k = mk.part("Bucket", (bx_, 0, bz))
    mk.cyl(k, (bx_, 0.4, bz), 0.38, 0.8, MID, sides=8, top=1.18)
    mk.carve(k, DARK, points=cyl_pts((bx_, 0.7, bz), 0.37, 0.4))                  # adentro, oscuro
    for y, r in ((0.15, 0.42), (0.66, 0.465)):                                   # zunchos
        mk.cyl(k, (bx_, y, bz), r, 0.08, IRON, sides=8, detail=True)
    a, b_ = (bx_ - 0.44, 0.7, bz), (bx_ + 0.44, 0.7, bz)                          # asa caída hacia atrás
    tube(mk, k, a, (bx_ - 0.3, 0.9, bz + 0.38), 0.03, IRON, detail=True)
    tube(mk, k, (bx_ - 0.32, 0.9, bz + 0.38), (bx_ + 0.32, 0.9, bz + 0.38), 0.03, IRON, detail=True)
    tube(mk, k, (bx_ + 0.3, 0.9, bz + 0.38), b_, 0.03, IRON, detail=True)


DESK = (-1.5, -4.5)


def build_desk(mk):
    dx, dz = DESK
    d = mk.part("Desk", (dx, 0, dz))
    mk.hull(d, bpts(dx - 2.0, dx + 2.0, 2.45, 2.6, dz - 1.0, dz + 1.0), MID)       # tapa
    mk.hull(d, bpts(dx + 0.4, dx + 1.85, 0.0, 2.46, dz - 0.9, dz + 0.9), DARK)     # cajonera
    for x in (dx - 1.8, ):                                                        # patas del otro lado
        for z in (dz - 0.8, dz + 0.8):
            mk.hull(d, bpts(x - 0.1, x + 0.1, 0.0, 2.46, z - 0.1, z + 0.1), DARK)
    mk.hull(d, bpts(dx - 1.75, dx + 0.42, 1.5, 2.455, dz + 0.8, dz + 0.88), DARK)   # faldón de atrás
    for y0, y1 in ((0.15, 0.95), (1.05, 1.65), (1.75, 2.3)):                      # cajones (frente a -Z)
        mk.hull(d, bpts(dx + 0.5, dx + 1.75, y0, y1, dz - 0.95, dz - 0.89), MID)
        mk.hull(d, bpts(dx + 1.06, dx + 1.19, (y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05, dz - 1.02, dz - 0.94),
                "brass")
    # pila de afiches en blanco y dos sueltos encima
    mk.box(d, (dx - 0.9, 2.66, dz + 0.1), (0.95, 0.14, 1.25), "paint_cream", rot=(0, 4, 0))
    mk.box(d, (dx - 0.8, 2.74, dz + 0.05), (0.95, 0.03, 1.25), "paint_cream", rot=(0, -14, 0))
    mk.box(d, (dx - 1.25, 2.612, dz - 0.25), (0.95, 0.03, 1.25), "paint_cream", rot=(0, 28, 0))


def build_keys(mk):
    kx, ky, kz = DESK[0] + 0.5, 2.6, DESK[1] - 0.2
    k = mk.part("Keys", (kx, ky, kz))
    r_out, r_in, n = 0.24, 0.19, 4
    for a0, a1 in ((2, 178), (182, 358)):                                         # aro en dos mitades
        angs = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        prof = ([(kx + r_out * math.cos(math.radians(a)), kz + r_out * math.sin(math.radians(a))) for a in angs]
                + [(kx + r_in * math.cos(math.radians(a)), kz + r_in * math.sin(math.radians(a))) for a in reversed(angs)])
        mk.prism(k, prof, 0.05, IRON, plane="xz", center=(0, ky + 0.02, 0))
    for i, (ang, mat, ln) in enumerate(((-20, IRON, 0.75), (35, "brass", 0.6), (100, IRON, 0.7))):
        a = math.radians(ang)
        u = Vector((math.cos(a), 0, math.sin(a)))
        v = Vector((-u.z, 0, u.x))
        base = Vector((kx, 0.0, kz)) + u * 0.2                                    # la altura va en y0
        y0 = ky + 0.005 + 0.002 * i
        bow = [tuple(base + u * (0.12 + 0.11 * math.cos(t)) + v * (0.11 * math.sin(t)) + Vector((0, y, 0)))
               for t in (2 * math.pi * j / 6 for j in range(6)) for y in (y0, y0 + 0.05)]
        mk.hull(k, bow, mat)                                                      # ojo
        sh = [tuple(base + u * t + v * w + Vector((0, y, 0))) for t in (0.2, 0.22 + ln) for w in (-0.035, 0.035)
              for y in (y0 + 0.005, y0 + 0.045)]
        mk.hull(k, sh, mat)                                                       # caña
        bit = [tuple(base + u * t + v * w + Vector((0, y, 0))) for t in (0.08 + ln, 0.22 + ln)
               for w in (0.03, 0.17) for y in (y0 + 0.006, y0 + 0.044)]
        mk.hull(k, bit, mat)                                                      # paletón


def build(mk):
    build_front(mk)
    build_doors(mk)
    build_bunk(mk)
    build_bucket(mk)
    build_desk(mk)
    build_keys(mk)

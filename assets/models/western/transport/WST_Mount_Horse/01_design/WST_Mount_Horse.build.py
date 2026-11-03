"""
Receta de WST_Mount_Horse, el caballo del jugador (prompt 027, Bloques A + E).

Brief
- Silueta que se lee a 40 studs: cuello a 45° con crin negra, cabeza larga en cuña con orejas
  paradas, barril hondo con la cruz y la grupa a la misma altura, patas finas con "medias" negras y
  cascos que se abren, cola negra que cae hasta el corvejón, montura con cuerno y respaldo alto.
- Medidas: 8,0 de la nariz a la base de la cola, 4,4 en la cruz, 2,0 de ancho de barril.
  Cascos delanteros en z = -1,35 y traseros en z = +2,05 (el origen queda bajo el centro de masa).
  Rodilla a 1,30, corvejón a 1,55, vientre a 2,25, lomo a 4,15, cruz y grupa a 4,40.
- Piezas y orígenes: Torso (origen del modelo), Neck (base del cuello, en la cruz), Head (nuca),
  Tail (base de la cola), patas de arriba en el hombro / la babilla, patas de abajo en la rodilla /
  el corvejón (el casco va en la de abajo). Cada pieza se mete 0,1 o más en la vecina.
- Accesorios en su lugar: Acc_Saddle, Acc_Saddlebags y Acc_LeatherArmor (estas dos ocultas por
  defecto en el juego), Reins y el marcador _Seat arriba del asiento.
- Color pintado en las caras (nada pegado encima): lucero blanco en la frente. Tallado: ollares y
  boca. Las correas de la cabezada, la crin y el flequillo son volumen modelado.
- Los mismos ejes y medidas los usa WST_Mount_ZombieHorse (importa las constantes de esta receta).
- Inferido (el prompt no lo dice): largo del cuello (2,2) y de la cabeza (2,2), cabeza 40° bajo la
  horizontal, separación de patas (0,50 adelante, 0,55 atrás), estribos de madera a 2,2 de altura
  (donde caen los pies de un jugador sentado), cascos en coal para que no cambien con el pelaje.

Vueltas: 1) silueta y accesorios · 2) grupa redonda (casco de 12 lados), corvejón atrás, antebrazo
más grueso, quijada y mentón; z-fighting en la cola (tapas de las puntas a la misma altura) y en el
torso (dos cascos con la misma sección en z = 0) · 3) z-fighting del corvejón (anillos de igual ancho)
y de la pechera (tramos que compartían vértices y bordes a la misma altura: placas alternadas) ·
4) placas del cuello más finas, ojos de 20 triángulos · 5) riendas pegadas al costado del cuello
(antes bajaban en V por debajo del pescuezo) · 6) base de las orejas 0,16 más adentro: flotaban
0,06 sobre la cabeza (lo tapaba la testera; en el caballo zombi, más flaco, saltó como "floating").

Revisión
- 2726 triángulos contra 1800 de referencia. Lo visible por defecto (sin alforjas ni armadura) es
  ~2330: la cabeza (~720) se lleva el gasto porque es el foco (cabezada, lucero, ollares y boca
  tallados); la montura con cuerno, fuste, estribos y cincha ~320. Ninguna pieza pasa de 750.
- Ancho total 2,45 (no 2,0): el barril mide 2,0; lo de afuera son los estribos y la pechera.
- Largo total 8,55: de la nariz (z = -5,14) a la base de la cola (z = 2,90) son 8,04; la cola cae
  0,5 más atrás.
- La armadura de cuero va en tres piezas, para que en el rig cada una siga a lo suyo (decidido sin
  Valentin el 2026-10-29, al riggear): Acc_LeatherArmor (pechera, va al Torso; origen el del modelo),
  Acc_LeatherArmor_Neck (placas del cuello, origen en la base del cuello) y Acc_LeatherArmor_Head
  (testera, origen en la nuca). La mejora muestra todas las Acc_LeatherArmor*.
- Reins va de la cabeza a la montura y queda soldada al cuello: con la cabeza en movimiento, las
  puntas se separan un poco del freno y del cuerno. Origen de Reins: el del modelo.
"""

import math

from mathutils import Vector

# ---------------- esqueleto (lo comparte el caballo zombi) ----------------
FRONT_Z, HIND_Z = -1.35, 2.05            # línea de las patas (cascos)
FX, HX = 0.50, 0.55                      # medio ancho entre patas delanteras / traseras
SHOULDER = 2.95                          # pivote de la pata delantera (hombro-codo)
KNEE = 1.30                              # rodilla
STIFLE = 2.95                            # pivote de la pata trasera (babilla)
HOCK = 1.55                              # corvejón
NECK_B = Vector((0.0, 3.75, -1.75))      # base del cuello (pivote de Neck)
ND = Vector((0.0, math.sin(math.radians(45)), -math.cos(math.radians(45))))    # eje del cuello, 45°
NU = Vector((0.0, math.cos(math.radians(45)), math.sin(math.radians(45))))     # hacia la cresta
NECK_LEN = 2.2
POLL = NECK_B + ND * NECK_LEN            # nuca (pivote de Head)
HEAD_ANG = 40
HD = Vector((0.0, -math.sin(math.radians(HEAD_ANG)), -math.cos(math.radians(HEAD_ANG))))  # hacia la nariz
HU = Vector((0.0, math.cos(math.radians(HEAD_ANG)), -math.sin(math.radians(HEAD_ANG))))  # hacia la frente
TAIL_B = (0.0, 4.05, 2.90)               # base de la cola

# secciones del torso: (z, abajo, arriba, ancho). Dos cascos (adelante y atrás) para que el lomo baje.
TORSO_FRONT = [(-2.12, 2.80, 3.62, 1.05), (-1.80, 2.42, 4.02, 1.55), (-1.15, 2.26, 4.40, 1.86),
               (-0.40, 2.22, 4.18, 2.00), (0.20, 2.25, 4.15, 1.995)]
TORSO_BACK = [(-0.15, 2.235, 4.155, 1.99), (0.80, 2.42, 4.21, 1.97), (1.60, 2.78, 4.40, 1.92),
              (2.30, 2.95, 4.30, 1.80), (2.75, 3.08, 4.12, 1.52), (3.02, 3.30, 3.90, 0.95)]
# secciones del cuello: (t sobre el eje, corrimiento hacia la cresta, ancho, alto)
NECK_SECS = [(-0.40, 0.05, 1.15, 1.80), (0.40, 0.05, 1.05, 1.55), (1.30, 0.0, 0.86, 1.16),
             (2.05, -0.05, 0.74, 0.98), (2.40, -0.10, 0.66, 0.86)]
# secciones de la cabeza: (s sobre el eje, corrimiento hacia la frente, ancho, alto)
HEAD_BACK = [(-0.25, 0.00, 0.64, 0.86), (0.25, -0.04, 0.80, 1.10), (0.80, 0.03, 0.72, 0.92),
             (1.10, 0.05, 0.62, 0.76)]
HEAD_FRONT = [(1.00, 0.05, 0.64, 0.79), (1.45, 0.06, 0.54, 0.64), (1.92, 0.03, 0.56, 0.62),
              (2.20, 0.00, 0.44, 0.46)]


def lerp(a, b, t):
    return a + (b - a) * t


def interp(table, key):
    """Interpola una tabla de secciones [(clave, *valores)] en `key` (fuera del rango, el extremo)."""
    if key <= table[0][0]:
        return table[0][1:]
    for lo, hi in zip(table, table[1:]):
        if key <= hi[0]:
            t = (key - lo[0]) / (hi[0] - lo[0])
            return tuple(lerp(a, b, t) for a, b in zip(lo[1:], hi[1:]))
    return table[-1][1:]


def vsec(z, yb, yt, w, n=10, egg=0.22, grow=0.0):
    """Sección vertical (plano x-y) en z: óvalo más angosto arriba (la cruz y el lomo)."""
    yc, hh = (yb + yt) / 2 + 0.0, (yt - yb) / 2 + grow
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        s = math.sin(a)
        k = 1 - egg * s if s > 0 else 1 + 0.08 * s
        out.append(((w / 2 + grow) * math.cos(a) * k, yc + hh * s, z))
    return out


def torso_table():
    return sorted(TORSO_FRONT + TORSO_BACK[1:])


def torso_pt(z, deg, off=0.0, egg=0.22):
    """Punto de la superficie del torso en z, a `deg` grados (90 = lomo, 0 = costado derecho), corrido `off`."""
    yb, yt, w = interp(torso_table(), z)
    a = math.radians(deg)
    s = math.sin(a)
    k = 1 - egg * s if s > 0 else 1 + 0.08 * s
    return ((w / 2 * k + off) * math.cos(a), (yb + yt) / 2 + ((yt - yb) / 2 + off) * s, z)


def asec(c, up, w, h, n=10, phase=0.5):
    """Anillo perpendicular a un eje del plano y-z: ancho w en x, alto h sobre `up`."""
    c, up = Vector(c), Vector(up)
    return [tuple(c + Vector((w / 2 * math.cos(2 * math.pi * (i + phase) / n), 0, 0))
                  + up * (h / 2 * math.sin(2 * math.pi * (i + phase) / n))) for i in range(n)]


def neck_pt(t, o=0.0, x=0.0):
    return tuple(NECK_B + ND * t + NU * o + Vector((x, 0, 0)))


def head_pt(s, o=0.0, x=0.0):
    return tuple(POLL + HD * s + HU * o + Vector((x, 0, 0)))


def neck_ring(t, grow=0.0, n=10):
    o, w, h = interp(NECK_SECS, t)
    return asec(neck_pt(t, o), NU, w + 2 * grow, h + 2 * grow, n)


def head_ring(table, s, grow=0.0, n=10):
    o, w, h = interp(table, s)
    return asec(head_pt(s, o), HU, w + 2 * grow, h + 2 * grow, n, phase=0.0)


def head_half(s):
    """Medio ancho y medio alto de la cabeza en s (las dos tablas juntas)."""
    o, w, h = interp(HEAD_BACK if s < 1.05 else HEAD_FRONT, s)
    return o, w / 2, h / 2


def hring(y, cx, cz, w, d, n=8):
    """Anillo horizontal (patas)."""
    return [(cx + w / 2 * math.cos(2 * math.pi * (i + 0.5) / n), y, cz + d / 2 * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def strap(mk, part, pts, w, t, mat, side=(1, 0, 0), detail=False):
    """Correa por una polilínea: cada tramo es un casco de ancho w y espesor t (t sobre `side`)."""
    side = Vector(side).normalized()
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = (b - a).normalized()
        across = d.cross(side).normalized() * (w / 2)
        th = side * (t / 2)
        a2, b2 = a - d * 0.02, b + d * 0.02
        mk.hull(part, [tuple(p + sa * across + st * th) for p in (a2, b2) for sa in (-1, 1) for st in (-1, 1)],
                mat, detail=detail)


# ---------------- piezas compartidas con el caballo zombi ----------------
def front_leg(mk, side, s, coat, sock, hoof, thin=1.0):
    x = s * FX
    up = mk.part(f"Front{side}UpperLeg", (x, SHOULDER, FRONT_Z))
    mk.hull(up, hring(3.35, x, FRONT_Z - 0.06, 0.56 * thin, 0.80 * thin) + hring(2.45, x, FRONT_Z + 0.02, 0.52 * thin, 0.64 * thin)
            + hring(1.80, x, FRONT_Z + 0.02, 0.36 * thin, 0.44), coat)
    mk.hull(up, hring(1.84, x, FRONT_Z + 0.02, 0.36 * thin, 0.44) + hring(1.20, x, FRONT_Z + 0.01, 0.34, 0.38), coat)
    lo = mk.part(f"Front{side}LowerLeg", (x, KNEE, FRONT_Z))
    lower_leg(mk, lo, x, FRONT_Z, 1.40, sock, hoof)
    return up, lo


def back_leg(mk, side, s, coat, sock, hoof, thin=1.0):
    x = s * HX
    up = mk.part(f"Back{side}UpperLeg", (x, STIFLE, HIND_Z - 0.10))
    mk.hull(up, hring(3.45, x, HIND_Z - 0.10, 0.62 * thin, 1.05 * thin) + hring(2.60, x, HIND_Z + 0.03, 0.52 * thin, 0.78 * thin)
            + hring(1.65, x, HIND_Z + 0.27, 0.34, 0.44), coat)
    lo = mk.part(f"Back{side}LowerLeg", (x, HOCK, HIND_Z + 0.25))
    mk.hull(lo, hring(1.76, x, HIND_Z + 0.23, 0.37, 0.49) + hring(1.34, x, HIND_Z + 0.18, 0.28, 0.40)
            + [(x, 1.60, HIND_Z + 0.56), (x, 1.48, HIND_Z + 0.53)], sock)                        # punta del corvejón
    lower_leg(mk, lo, x, HIND_Z + 0.08, 1.38, sock, hoof)
    return up, lo


def lower_leg(mk, part, x, z, top, sock, hoof):
    """Caña, menudillo, cuartilla y casco (el casco se abre hacia abajo y apunta adelante)."""
    mk.hull(part, hring(top, x, z, 0.30, 0.34) + hring(0.58, x, z + 0.02, 0.23, 0.27), sock)          # caña
    mk.hull(part, hring(0.66, x, z + 0.03, 0.30, 0.36) + hring(0.42, x, z + 0.0, 0.30, 0.36)
            + hring(0.30, x, z - 0.10, 0.26, 0.28), sock)                                           # menudillo y cuartilla
    mk.hull(part, hring(0.34, x, z - 0.12, 0.30, 0.30) + hring(0.0, x, z - 0.16, 0.42, 0.50), hoof)     # casco


def build(mk):
    # ---------------- torso ----------------
    torso = mk.part("Torso", (0, 0, 0))
    mk.hull(torso, [p for z, yb, yt, w in TORSO_FRONT for p in vsec(z, yb, yt, w)], "hide_brown")
    mk.hull(torso, [p for z, yb, yt, w in TORSO_BACK[:4] for p in vsec(z, yb, yt, w)], "hide_brown")
    mk.hull(torso, [p for z, yb, yt, w in TORSO_BACK[2:] for p in vsec(z, yb, yt, w, n=12)], "hide_brown")   # grupa redonda

    # ---------------- cuello y crin ----------------
    neck = mk.part("Neck", tuple(NECK_B))
    mk.hull(neck, neck_ring(-0.40) + neck_ring(0.40) + neck_ring(1.30), "hide_brown")
    mk.hull(neck, neck_ring(1.20) + neck_ring(2.05) + neck_ring(2.40), "hide_brown")
    crest = []
    for i in range(12):
        t = -0.15 + 2.45 * i / 11
        o, w, h = interp(NECK_SECS, t)
        crest.append((t, o + h / 2))
    outer = []
    for i, (t, c) in enumerate(crest):
        outer.append(neck_pt(t, c + (0.24 if i % 2 == 0 else 0.14)))
    inner = [neck_pt(t, c - 0.18) for t, c in reversed(crest)]
    mane = [(p[2], p[1]) for p in outer + inner]
    mk.prism(neck, mane, 0.24, "hide_black", plane="zy", center=(0, 0, 0))

    # ---------------- cabeza ----------------
    head = mk.part("Head", tuple(POLL))
    mk.hull(head, [p for s, *_ in HEAD_BACK for p in head_ring(HEAD_BACK, s)], "hide_brown")
    mk.hull(head, [p for s, *_ in HEAD_FRONT for p in head_ring(HEAD_FRONT, s)], "hide_brown")
    # quijada redonda, abajo y atrás
    mk.hull(head, asec(head_pt(0.05, -0.32), HU, 0.84, 0.78, 10) + asec(head_pt(0.58, -0.30), HU, 0.76, 0.66, 10), "hide_brown")
    # labio de abajo y mentón, debajo de la boca
    mk.hull(head, asec(head_pt(1.78, -0.20), HU, 0.42, 0.22, 8) + asec(head_pt(2.10, -0.20), HU, 0.36, 0.20, 8), "hide_brown")
    # orejas paradas, apenas abiertas
    for s in (-1, 1):
        base = [head_pt(0.02 + dz, 0.24, s * 0.20 + dx) for dz, dx in ((-0.10, -0.07), (-0.10, 0.07), (0.10, 0.07), (0.10, -0.07))]
        tip = head_pt(-0.02, 0.92, s * 0.30)
        mk.hull(head, base + [tip, head_pt(0.04, 0.80, s * 0.30)], "hide_brown")
    # flequillo negro entre las orejas
    mk.hull(head, [head_pt(-0.05, 0.42, -0.10), head_pt(-0.05, 0.42, 0.10), head_pt(0.10, 0.50, 0.0),
                   head_pt(0.45, 0.42, -0.06), head_pt(0.45, 0.42, 0.06), head_pt(0.20, 0.30, 0.0)], "hide_black",
            detail=True)
    # cejas: el ojo queda debajo de un alero
    for s in (-1, 1):
        mk.hull(head, [head_pt(0.48, 0.30, s * 0.30), head_pt(0.78, 0.30, s * 0.28),
                       head_pt(0.55, 0.38, s * 0.40), head_pt(0.72, 0.36, s * 0.38),
                       head_pt(0.62, 0.18, s * 0.41)], "hide_brown")
    # lucero blanco: cortes a los costados y a lo largo, pintado en las caras de adelante
    for xs in (-0.12, 0.12):
        mk.slice(head, (xs, 0, 0), (1, 0, 0))
    mk.slice(head, head_pt(0.42), tuple(HD))
    for i in range(18):
        s = 0.45 + 0.1 * i
        o, hw, hh = head_half(min(s, 2.15))
        mk.paint(head, "hide_white", box=(head_pt(s, o + hh * 0.95), (0.24, 0.16, 0.16)))
    # ollares y boca tallados
    for s in (-1, 1):
        mk.carve(head, "coal", points=mk.pts_ball(head_pt(2.13, 0.06, s * 0.16), 0.07, scale=(0.8, 1.2, 1.0), subdiv=0))
    mk.carve(head, "coal", points=[head_pt(s, -0.14 + dy, x) for s in (1.80, 2.30) for x in (-0.30, 0.30) for dy in (-0.015, 0.015)])
    # ojos oscuros, metidos en la cara
    for s in (-1, 1):
        mk.ball(head, head_pt(0.62, 0.14, s * 0.35), 0.10, "coal", scale=(0.7, 1.0, 1.2), subdiv=0, detail=True)
    # cabezada de cuero: muserola, testera, carrilleras, frontalera y anillas del freno
    mk.hull(head, head_ring(HEAD_FRONT, 1.50, grow=0.03) + head_ring(HEAD_FRONT, 1.62, grow=0.03), "leather", detail=True)
    mk.hull(head, head_ring(HEAD_BACK, 0.02, grow=0.03) + head_ring(HEAD_BACK, 0.13, grow=0.03), "leather", detail=True)
    for s in (-1, 1):
        pts = []
        for ss in (0.08, 0.60, 1.10, 1.56):
            o, hw, hh = head_half(ss)
            pts.append(head_pt(ss, o - 0.05, s * (hw + 0.012)))
        strap(mk, head, pts, 0.09, 0.05, "leather", detail=True)
        o, hw, hh = head_half(1.86)
        mk.cyl(head, head_pt(1.86, -0.14, s * (hw + 0.03)), 0.08, 0.04, "iron", axis="x", sides=6, detail=True)
    o, hw, hh = head_half(0.28)
    mk.hull(head, [head_pt(0.24 + ds, o + hh * k, x) for ds in (0.0, 0.09) for k, x in
                   ((0.62, -hw - 0.01), (0.62, hw + 0.01), (1.04, -0.15), (1.04, 0.15))], "leather", detail=True)

    # ---------------- cola ----------------
    tail = mk.part("Tail", TAIL_B)
    tx, ty, tz = TAIL_B
    mk.hull(tail, hring(ty + 0.08, 0, tz - 0.08, 0.30, 0.30) + hring(ty - 0.35, 0, tz + 0.22, 0.30, 0.30), "hide_black")
    mk.hull(tail, hring(ty - 0.25, 0, tz + 0.20, 0.34, 0.32) + hring(3.0, 0, tz + 0.34, 0.42, 0.36)
            + hring(2.05, 0, tz + 0.36, 0.48, 0.34), "hide_black")
    for i, (dx, dz, y) in enumerate(((-0.14, 0.30, 1.50), (0.10, 0.42, 1.42), (0.02, 0.26, 1.62), (0.18, 0.30, 1.70))):
        mk.hull(tail, hring(2.12 + 0.05 * i, dx * 0.6, tz + 0.34, 0.20, 0.20, n=6) + [(dx, y, tz + dz)], "hide_black")

    # ---------------- patas ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        front_leg(mk, side, s, "hide_brown", "hide_black", "coal")
        back_leg(mk, side, s, "hide_brown", "hide_black", "coal")

    # ---------------- montura ----------------
    saddle = mk.part("Acc_Saddle", (0, 4.15, -0.15))
    # mandil rojo debajo, se ve el borde
    zs = (-0.98, -0.45, 0.10, 0.62)
    mk.hull(saddle, [torso_pt(z, d, 0.07) for z in zs for d in range(14, 167, 19)], "paint_red")
    # faldones de cuero
    zs = (-0.80, -0.30, 0.20, 0.50)
    mk.hull(saddle, [torso_pt(z, d, 0.12) for z in zs for d in range(26, 155, 16)], "leather")
    # arzón, asiento hundido y respaldo alto
    mk.hull(saddle, [(x, y, z) for x, y, z in
                     [(-0.36, 4.40, -0.88), (0.36, 4.40, -0.88), (-0.24, 4.70, -0.80), (0.24, 4.70, -0.80),
                      (-0.40, 4.40, -0.50), (0.40, 4.40, -0.50), (-0.18, 4.66, -0.60), (0.18, 4.66, -0.60)]], "leather")
    mk.hull(saddle, [(x, y, z) for x in (-0.42, 0.42) for y, z in ((4.36, -0.60), (4.36, 0.40), (4.47, -0.30), (4.47, 0.15))]
            + [(x, 4.46, z) for x in (-0.30, 0.30) for z in (-0.62, 0.42)], "leather")
    mk.hull(saddle, [(x, y, z) for x, y, z in
                     [(-0.46, 4.38, 0.28), (0.46, 4.38, 0.28), (-0.46, 4.38, 0.52), (0.46, 4.38, 0.52),
                      (-0.38, 4.82, 0.50), (0.38, 4.82, 0.50), (-0.30, 4.84, 0.62), (0.30, 4.84, 0.62)]], "leather_dark")
    # cuerno
    mk.cyl(saddle, (0, 4.80, -0.80), 0.065, 0.30, "leather_dark", sides=8)
    mk.cyl(saddle, (0, 4.96, -0.81), 0.15, 0.07, "leather_dark", sides=8)
    # cincha por debajo de la panza
    zc = -0.62
    mk.hull(saddle, vsec(zc - 0.07, *interp(torso_table(), zc), grow=0.03) + vsec(zc + 0.07, *interp(torso_table(), zc), grow=0.03),
            "leather_dark")
    # aciones (fenders) y estribos de madera
    for s in (-1, 1):
        top = torso_pt(-0.20, 40, 0.14)
        tx_ = s * top[0]
        mk.hull(saddle, [(tx_ + s * dx, y, z) for dx, y in ((0.0, 3.95), (0.06, 3.95), (0.22, 2.62), (0.28, 2.62))
                         for z in (-0.40, -0.02)], "leather")
        sx = tx_ + s * 0.25
        stir = [(-0.22, 0.0), (0.22, 0.0), (0.18, 0.32), (0.10, 0.36), (0.10, 0.08), (-0.10, 0.08), (-0.10, 0.36), (-0.18, 0.32)]
        mk.prism(saddle, [(-0.21 + a, 2.24 + b) for a, b in stir], 0.16, "wood_mid", plane="zy", center=(sx, 0, 0))
        mk.box(saddle, (sx, 2.58, -0.21), (0.10, 0.10, 0.22), "leather")
    mk.marker("_Seat", (0, 4.50, -0.10))

    # ---------------- riendas: del freno al cuerno, por los costados del cuello ----------------
    reins = mk.part("Reins", (0, 0, 0))
    for s in (-1, 1):
        o, hw, hh = head_half(1.86)
        bit = head_pt(1.86, -0.14, s * (hw + 0.05))
        mid1 = neck_pt(1.95, -0.02, s * 0.44)          # suben pegadas al costado del cuello
        mid2 = neck_pt(1.00, 0.22, s * 0.54)
        horn = (s * 0.07, 4.78, -0.80)
        strap(mk, reins, [bit, mid1, mid2, horn], 0.07, 0.04, "leather", side=(0, 1, 0))

    # ---------------- alforjas (mejora, ocultas por defecto) ----------------
    bags = mk.part("Acc_Saddlebags", (0, 4.20, 0.90))
    mk.hull(bags, [torso_pt(z, d, 0.05) for z in (0.80, 0.98) for d in range(30, 151, 15)], "leather_dark")
    for s in (-1, 1):
        it, ib = torso_pt(0.9, 42, -0.03), torso_pt(0.9, -14, -0.03)       # apoyada contra el barril
        ot, ob = (it[0] + 0.30, it[1] + 0.02), (ib[0] + 0.32, ib[1])
        pts = []
        for z in (0.62, 1.18):
            pts += [(s * it[0], it[1], z), (s * ib[0], ib[1], z), (s * ot[0], ot[1], z), (s * ob[0], ob[1], z)]
        pts += [(s * (ib[0] + 0.16), ib[1] - 0.10, z) for z in (0.70, 1.10)]   # fondo abombado
        mk.hull(bags, pts, "leather_dark")

        def outer(y):
            return lerp(ob[0], ot[0], (y - ob[1]) / (ot[1] - ob[1]))

        # tapa con punta y hebilla, 0,04 por fuera de la bolsa
        ym = lerp(ob[1], ot[1], 0.45)
        fl = []
        for z in (0.58, 1.22):
            fl += [(s * (ot[0] - 0.05), ot[1] + 0.04, z), (s * (ot[0] + 0.04), ot[1] + 0.04, z),
                   (s * (outer(ym) + 0.04), ym, z), (s * (outer(ym) - 0.03), ym, z)]
        fl += [(s * (outer(ym - 0.16) + 0.04), ym - 0.16, 0.90), (s * (outer(ym - 0.16) - 0.03), ym - 0.16, 0.90)]
        mk.hull(bags, fl, "leather")
        mk.box(bags, (s * (outer(ym - 0.08) + 0.05), ym - 0.08, 0.90), (0.06, 0.13, 0.13), "brass", detail=True)

    # ---------------- armadura de cuero (mejora, oculta por defecto) ----------------
    armor = mk.part("Acc_LeatherArmor", (0, 0, 0))
    # pechera: placas encadenadas en arco que cruzan el pecho (abajo pegada al torso, arriba al cuello)
    def pey(phi, low, th=0.0, dy=0.0):
        z0, ax, az, y = (-1.55, 0.86, 0.70, 2.82 - dy) if low else (-1.66, 0.80, 0.96, 3.46 + dy)
        a = math.radians(phi)
        return (math.sin(a) * (ax + th), y, z0 - math.cos(a) * (az + th))

    phis = [-80, -54, -27, 0, 27, 54, 80]
    for i, (p0, p1) in enumerate(zip(phis, phis[1:])):
        dy = 0.015 * (i % 2)                       # placas alternadas: los bordes no quedan coplanares
        mk.hull(armor, [pey(p, low, th, dy) for p in (p0 - 1.5, p1 + 1.5) for low in (True, False)
                        for th in (0.0, 0.09 + dy)], "leather")
    for p in (-40, 0, 40):
        a, b = pey(p, True, 0.09), pey(p, False, 0.09)
        mk.cyl(armor, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2), 0.06, 0.08, "iron", axis="z",
               sides=6, rot=(0, -p, 0), detail=True)
    # protector del cuello: 3 placas encimadas sobre la cresta (pieza aparte: sigue al cuello en el rig)
    armor = mk.part("Acc_LeatherArmor_Neck", tuple(NECK_B))
    for i, (t0, t1) in enumerate(((0.35, 1.05), (0.95, 1.65), (1.55, 2.20))):
        pts = []
        for t in (t0, t1):
            o, w, h = interp(NECK_SECS, t)
            lift = 0.04 * (2 - i)
            for deg in (48, 70, 90, 110, 132):
                a = math.radians(deg)
                r = 0.27 if deg == 90 else (0.13 if deg in (70, 110) else 0.05)
                pts.append(neck_pt(t, o + (h / 2 + r + lift) * math.sin(a), (w / 2 + r + lift) * math.cos(a)))
            pts.append(neck_pt(t, o + h * (0.08 + 0.07 * i)))         # el fondo de la placa, dentro del cuello
        mk.hull(armor, pts, "leather")
    # testera: placa de la frente con tachas de hierro (pieza aparte: sigue a la cabeza en el rig)
    armor = mk.part("Acc_LeatherArmor_Head", tuple(POLL))
    plate = []
    for ss in (0.36, 0.95, 1.45):
        o, hw, hh = head_half(ss)
        plate += [head_pt(ss, o + hh * 0.951 + 0.05, x * hw * 0.309) for x in (-1, 1)]       # cara de adelante
        plate += [head_pt(ss, o + hh * 0.588 + 0.05, x * (hw * 0.809 + 0.03)) for x in (-1, 1)]  # costados
        plate += [head_pt(ss, o + hh * 0.60)]                                                   # adentro
    mk.hull(armor, plate, "leather")
    for ss in (0.55, 0.90, 1.25):
        o, hw, hh = head_half(ss)
        mk.cyl(armor, head_pt(ss, o + hh * 0.951 + 0.06), 0.05, 0.06, "iron", axis="y", sides=6, rot=(-HEAD_ANG, 0, 0),
               detail=True)

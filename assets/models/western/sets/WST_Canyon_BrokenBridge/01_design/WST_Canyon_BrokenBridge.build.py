"""
Receta de WST_Canyon_BrokenBridge, el puente de caballetes roto del cañón (prompt 088, Bloques A + C).
El camino va por el fondo del barranco, a lo largo de Z, y pasa por DEBAJO del puente (que cruza a lo largo
de X). Lo que se cayó del medio quedó sobre el camino y lo tapa: se vuela con dinamita, como el derrumbe.

Brief
- Silueta a 40 studs (vista desde el camino, llegando por -Z): dos tramos de tablero de madera muy arriba
  (14) sobre caballetes de cuatro patas con cruces en X, cortados en el medio, con tablas y un larguero
  colgando de cada punta rota; abajo, cruzado sobre el camino, un enredo de dos caballetes caídos, tramos
  de tablero y largueros, de 5 de alto, que no deja pasar.
- Medidas: tablero de 32 a lo largo de X (x ±16,3: las vigas llegan a la cara de afuera del sombrero) y 6
  de ancho (tablas en z ±3, durmientes en z ±3,3), cara de arriba a 14. Caballetes cada 8 en x = ±8 y ±16
  (el del medio, x = 0, es el que se cayó): solera 0-0,5, patas hasta el sombrero (12,0-12,6), 4 largueros
  (12,57-13,42), durmientes cada 1,25 (13,40-13,82), 6 tablas a lo largo (13,80-14,0). Hueco del medio:
  el tablero se cortó entre |x| 3,55 y 4,95 (puntas desparejas).
- Piezas fijas: fixed_Bents (los 4 caballetes en pie, en un objeto), fixed_DeckLeft y fixed_DeckRight (cada
  tramo con sus tablas colgando y su larguero colgado). Cruces y riostra de los caballetes por la cara de
  afuera: hacia el camino las patas quedan limpias (x = ±7,75).
- Escombros: frag01..frag08 sobre el camino entre los caballetes de x = ±8 (x ±7,7, z ±4, alto 5,2).
  frag01 y frag02 son los dos caballetes caídos (las dos mitades del caballete del medio, que se partió al
  caer: abajo con su solera, arriba con su sombrero), parados de canto a lo ancho del camino e inclinados
  hacia atrás; frag03 y frag04, dos tramos del tablero caído (largueros, durmientes y tablas) apuntalándolos
  desde atrás; frag05 y frag06, largueros rotos apoyados en diagonal contra el frente de cada caballete;
  frag07, tablas amontonadas al pie (lado de la ruta); frag08, un pedazo de larguero con dos durmientes.
- Puntas rotas con astillas en madera clara (wood_light: la madera fresca del corte), tablas alternadas
  wood_light / wood_mid (regla de tablas del Bloque A), estructura en wood_dark, durmientes wood_mid.
- _ChargeSpot: al pie de los escombros, al centro, del lado de la ruta (-Z).
- Inferido: caballetes de dos pisos (riostra horizontal a media altura y una cruz por piso), así los dos
  "caballetes caídos" del prompt son las dos mitades del del medio y se mantiene "cada 8"; durmientes y
  tablas a lo largo (sin rieles: el prompt no los pide y el viaje es a caballo); escombros apoyados de
  canto (no tirados planos) para que el frente no sea una rampa; sin suelo (lo pone el cañón).

Vueltas (cada una medida con un script de encimes por islas convexas, contacto y espacio libre): 1) primera
versión: las cruces de los caballetes salían de 0,42 de espesor (ancho y espesor cambiados: el modelo medía
33,08 de largo), el tramo de atrás de la derecha se metía 0,08 en la pata del caballete de x = 8 y los
escombros medían 9,5 de fondo · 2) caballetes caídos más adelante, tramos más parados, piernas más cortas:
8,6 de fondo, 5,14 de alto · 3) las astillas parecían puntas de lápiz (dos puntas simétricas): pasan a un
quiebre sesgado con una astilla larga en una esquina; los dos caballetes caídos se veían como dos portones
alineados: más diferencia de inclinación (64° y 54°) y de giro (5° y -7°); una tabla colgando más por tramo
· 4) el caballete caído de la izquierda quedaba a 0,008 del de x = -8 y el tramo de la derecha llegaba a
z 4,77: corridos y acortados · 5) las tablas del frente se metían 0,14 en los caballetes caídos: más
angostas (0,8) y más derechas; el tramo de la derecha más parado (49°).

Revisión
- 1992 triángulos contra 2500 (80 %): fixed_Bents 528 (4 caballetes de 132), fixed_DeckLeft y
  fixed_DeckRight 324 cada uno, escombros 804 (caballetes caídos 144 y 132, tramos 192 y 180, largueros 36
  y 36, tablas 36, pedazo de larguero 48), marcador 12. 4 materiales (wood_dark, wood_mid, wood_light; iron
  solo en el marcador).
- Medidas: 32,84 x 14,0 x 8,6 (tablero de 32,6 con las cruces de afuera de los caballetes de punta; 8,6 de
  fondo por las soleras de los caballetes). Cara de arriba del tablero a 14,0.
- Escombros: x -7,66 a 7,69, y 0 a 5,16, z -4,03 a 4,05 (15,35 x 5,16 x 8,08 contra 16 x 5 x 8): el ancho lo
  manda el hueco entre las patas de los caballetes en pie (x ±7,75); los llenan de punta a punta.
- Fragmentos (volumen del casco sobre el total de escombros, ancho mínimo): frag01 18,8 % / 0,72, frag02
  17,6 % / 0,72, frag03 30,3 % / 1,43, frag04 25,9 % / 1,43, frag05 2,1 % / 0,50, frag06 2,1 % / 0,50,
  frag07 1,3 % / 0,61, frag08 2,0 % / 0,90. Todos con origen en (0, 0, 0), en su lugar final.
- Encimes entre fragmentos: solo los apoyos (0,0001 a 0,005 de volumen, 0,005-0,01 de penetración): los
  tramos contra la cara de atrás de los caballetes caídos y los largueros contra las cruces del frente.
  Ningún fragmento toca lo fijo (el más cerca, frag06, a 0,04 de la pata de x = 8). Los apoyos son de canto
  o de arista, no caras compartidas: es un montón de maderas, no un sólido partido (Bloque C pide caras de
  contacto planas para lo que es un solo objeto). frag07 y frag08 apoyan en el suelo, sin tocar a otro.
- Espacio libre con los escombros volados: entre las patas de los caballetes de x = ±8 hay 15,5 (15,4 a la
  altura de las soleras, x ±7,7); en todo ese ancho no hay nada por debajo de y = 9,79 (la punta del larguero
  colgado de la derecha; el de la izquierda llega a 9,91, las tablas colgando a 11,2-12,2); bajo los tramos
  enteros (|x| > 4,6) el techo es la cara de abajo de los largueros, 12,57; en el medio (x -2,07 a 2,95) no
  hay nada arriba. Un jinete (asiento del caballo a 4,5, ~9 con el jinete) pasa con 0,8 de aire en el peor
  punto, y sin techo por el medio.
- _ChargeSpot en (0, 0,05, -4,05): al pie de las tablas del frente, al centro.
- La colisión de los tramos caídos (casco convexo) es una losa inclinada a 45-49° apoyada contra los
  caballetes caídos (64° y 54°): el frente que ve la ruta son los caballetes, más parados que una rampa.
"""

import math

from mathutils import Matrix, Vector

# ---------------- medidas del puente ----------------
PLANK_Y0 = 13.80                  # tablas 13,80-14,00: la cara de arriba del tablero a 14
TIE_Y0, TIE_Y1 = 13.40, 13.82
STR_Y0, STR_Y1 = 12.57, 13.42
CAP_Y0, CAP_Y1 = 12.00, 12.60
SILL_Y1 = 0.50
GIRT_Y = (6.0, 6.4)
END_X = 16.3
BENT_X = (-16.0, -8.0, 8.0, 16.0)
STRINGER_Z = (-2.35, -0.85, 0.85, 2.35)
PLANK_Z = (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)
TIE_STEP = 1.25

# puntas rotas de cada tramo: |x| donde termina cada larguero y cada tabla; colgados (índice, ángulo, largo)
DECK = {
    -1: dict(stringers=(4.25, 4.9, 3.65, 4.55), dangle=(1, 72.0, 2.7),
             planks=(3.95, 4.6, 4.2, 3.55, 4.75, 4.05), hang={1: (62.0, 3.0), 3: (48.0, 2.2), 4: (76.0, 2.6)}),
    1: dict(stringers=(4.6, 3.8, 4.45, 4.95), dangle=(3, 66.0, 2.9),
            planks=(4.3, 3.7, 4.65, 4.0, 3.6, 4.4), hang={0: (64.0, 2.8), 3: (79.0, 2.4), 5: (55.0, 2.5)}),
}


# ---------------- geometría ----------------
def V(*a):
    return Vector(a[0] if len(a) == 1 else a)


def bar_pts(p0, p1, w, h, side):
    """Barra de sección w (en `side`) x h de p0 a p1: 8 puntos."""
    p0, p1 = V(p0), V(p1)
    d = (p1 - p0).normalized()
    s = V(side)
    s = (s - d * s.dot(d)).normalized()
    t = d.cross(s).normalized()
    return [p + s * i * w / 2 + t * j * h / 2 for p in (p0, p1) for i in (-1, 1) for j in (-1, 1)]


def splinter_pts(end, d, u, v, hw, hh, k=0):
    """Punta quebrada de una barra, en madera fresca: un trozo con la cara del quiebre sesgada (cada esquina
    sale distinto) y una astilla larga en una esquina. Base metida 0,04 en la barra y 0,02 más fina."""
    end, d, u, v = V(end), V(d).normalized(), V(u).normalized(), V(v).normalized()
    base = [end - d * 0.04 + u * i * (hw - 0.02) + v * j * (hh - 0.02) for i in (-1, 1) for j in (-1, 1)]
    reach = ((0.62, 0.36, 0.2, 0.06), (0.1, 0.55, 0.3, 0.18), (0.24, 0.08, 0.66, 0.4))[k % 3]
    corners = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    tip = [end + d * r + u * i * (hw - 0.02) * (0.55 if r > 0.5 else 1.0) + v * j * (hh - 0.02) * (0.55 if r > 0.5 else 1.0)
           for r, (i, j) in zip(reach, corners)]
    return base + tip


class Piece:
    """Cascos (puntos, material) que se pueden mover antes de emitir: para apoyar los escombros."""

    def __init__(self):
        self.hulls = []

    def add(self, pts, mat):
        self.hulls.append(([V(p) for p in pts], mat))

    def points(self):
        return [p for pts, _ in self.hulls for p in pts]

    def move(self, dv):
        dv = V(dv)
        self.hulls = [([p + dv for p in pts], m) for pts, m in self.hulls]
        return dv

    def emit(self, mk, name):
        part = mk.part(name, (0, 0, 0))
        for pts, mat in self.hulls:
            mk.hull(part, [tuple(p) for p in pts], mat)


class Axes:
    """Ejes de una pieza inclinada: ex a lo ancho (X), eu sube `tilt` grados hacia +Z (rise=1) o -Z (rise=-1),
    en = ex x eu (con rise=1, la normal de la cara de atrás). Girado `yaw` grados sobre Y."""

    def __init__(self, o, tilt, rise=1, yaw=0.0):
        t = math.radians(tilt)
        r = Matrix.Rotation(math.radians(yaw), 3, "Y")
        self.o = V(o)
        self.ex = r @ Vector((1, 0, 0))
        self.eu = r @ Vector((0, math.sin(t), rise * math.cos(t)))
        self.en = self.ex.cross(self.eu).normalized()

    def p(self, a, b, c):
        return self.o + self.ex * a + self.eu * b + self.en * c

    def box(self, pc, a0, a1, b0, b1, c0, c1, mat):
        pc.add([self.p(a, b, c) for a in (a0, a1) for b in (b0, b1) for c in (c0, c1)], mat)

    def bar(self, pc, ab0, ab1, w, c0, c1, mat):
        """Barra en el plano (a, b) de ab0 a ab1, ancho w en el plano y espesor c0..c1."""
        (a0, b0), (a1, b1) = ab0, ab1
        dl = math.hypot(a1 - a0, b1 - b0)
        qa, qb = -(b1 - b0) / dl * w / 2, (a1 - a0) / dl * w / 2
        pc.add([self.p(a + sa * qa, b + sa * qb, c) for a, b in ((a0, b0), (a1, b1)) for sa in (-1, 1) for c in (c0, c1)],
               mat)

    def splinter(self, pc, ab_end, ab_dir, w, c0, c1, k=0):
        (a, b), (da, db) = ab_end, ab_dir
        n = math.hypot(da, db)
        da, db = da / n, db / n
        d = self.ex * da + self.eu * db
        u = self.ex * -db + self.eu * da
        pc.add(splinter_pts(self.p(a, b, (c0 + c1) / 2), d, u, self.en, w / 2, (c1 - c0) / 2, k), "wood_light")

    def ground(self, pc):
        """Apoya la pieza en y = 0 moviendo pieza y ejes juntos."""
        self.o += pc.move((0, -min(p.y for p in pc.points()), 0))


# ---------------- lo que queda en pie ----------------
def bent(pc, x):
    """Caballete de dos pisos en x: solera, 4 patas (las de afuera abiertas), sombrero, riostra a media altura y
    una cruz por piso, las dos por la cara de afuera (lejos del camino)."""
    s = 1 if x > 0 else -1

    def out(c0, c1):                    # (x del centro, espesor) de una tabla de c0 a c1 desde el plano del caballete
        return x + s * (c0 + c1) / 2, c1 - c0

    pc.add(bar_pts((x, SILL_Y1 / 2, -4.3), (x, SILL_Y1 / 2, 4.3), 0.6, SILL_Y1, (1, 0, 0)), "wood_dark")         # solera
    yc = (CAP_Y0 + CAP_Y1) / 2
    pc.add(bar_pts((x, yc, -3.45), (x, yc, 3.45), 0.6, CAP_Y1 - CAP_Y0, (1, 0, 0)), "wood_dark")                  # sombrero
    for z in (-1.3, 1.3):
        pc.add(bar_pts((x, SILL_Y1 - 0.05, z), (x, CAP_Y0 + 0.03, z), 0.5, 0.5, (1, 0, 0)), "wood_dark")
    for sz in (-1, 1):
        pc.add(bar_pts((x, SILL_Y1 - 0.05, sz * 3.75), (x, CAP_Y0 + 0.03, sz * 2.95), 0.5, 0.5, (1, 0, 0)), "wood_dark")
    gx, gt = out(0.235, 0.395)                                                                     # riostra
    pc.add(bar_pts((gx, sum(GIRT_Y) / 2, -3.75), (gx, sum(GIRT_Y) / 2, 3.75), gt, GIRT_Y[1] - GIRT_Y[0], (1, 0, 0)),
           "wood_dark")
    for (y0, z0w), (y1, z1w) in (((0.75, 3.7), (5.85, 3.35)), ((6.55, 3.35), (11.8, 2.95))):      # una cruz por piso
        for k, sz in enumerate((-1, 1)):
            cx, ct = out(*((0.23, 0.39), (0.245, 0.42))[k])
            pc.add(bar_pts((cx, y0, sz * z0w), (cx, y1, -sz * z1w), 0.42, ct, (0, 0, 1)), "wood_dark")


def deck(s):
    """Tramo de tablero de x = s*16,3 hasta las puntas rotas, con sus tablas colgando y su larguero colgado."""
    pc, cfg = Piece(), DECK[s]
    ym = (STR_Y0 + STR_Y1) / 2
    for i, (z, e) in enumerate(zip(STRINGER_Z, cfg["stringers"])):
        pc.add(bar_pts((s * END_X, ym, z), (s * e, ym, z), 0.5, STR_Y1 - STR_Y0, (0, 0, 1)), "wood_dark")
        if cfg["dangle"][0] == i:                                                              # larguero colgado
            _, ang, ln = cfg["dangle"]
            a = math.radians(ang)
            p0 = V(s * e + s * 0.12, STR_Y0 + 0.36, z)
            d = V(-s * math.cos(a), -math.sin(a), 0)
            p1 = p0 + d * ln
            pc.add(bar_pts(p0, p1, 0.48, 0.82, (0, 0, 1)), "wood_dark")
            pc.add(splinter_pts(p1, d, (0, 0, 1), d.cross(V(0, 0, 1)), 0.24, 0.41, i), "wood_light")
        else:
            pc.add(splinter_pts((s * e, ym, z), (-s, 0, 0), (0, 0, 1), (0, 1, 0), 0.25, 0.425, i), "wood_light")
    x = END_X - 0.3
    while x > max(cfg["stringers"]) - 0.05:                                                     # durmientes
        pc.add(bar_pts((s * x, (TIE_Y0 + TIE_Y1) / 2, -3.3), (s * x, (TIE_Y0 + TIE_Y1) / 2, 3.3), 0.6, TIE_Y1 - TIE_Y0,
                       (1, 0, 0)), "wood_mid")
        x -= TIE_STEP
    for i, (z, e) in enumerate(zip(PLANK_Z, cfg["planks"])):                                    # tablas a lo largo
        mat = "wood_light" if i % 2 == 0 else "wood_mid"
        pc.add(bar_pts((s * END_X, PLANK_Y0 + 0.1, z), (s * e, PLANK_Y0 + 0.1, z), 0.96, 0.2, (0, 0, 1)), mat)
        if i in cfg["hang"]:                                                                   # tabla colgando
            ang, ln = cfg["hang"][i]
            a = math.radians(ang)
            p0 = V(s * e + s * 0.06, PLANK_Y0 + 0.08, z)
            p1 = p0 + V(-s * math.cos(a), -math.sin(a), 0) * ln
            pc.add(bar_pts(p0, p1, 0.94, 0.19, (0, 0, 1)), mat)
    return pc


# ---------------- escombros ----------------
C_FRONT = -0.17                   # cara de adelante de las cruces de un caballete caído
C_BACK = 0.5                      # cara de atrás de sus patas


def fallen_bent(lower, o, tilt, yaw, legs):
    """Medio caballete caído, parado de canto a lo ancho del camino e inclinado hacia atrás. lower: la mitad de
    abajo (solera, cruz y riostra arriba); si no, la de arriba (sombrero abajo y cruz). legs: largo de cada
    pata rota (de -X a +X)."""
    ax, pc = Axes(o, tilt, 1, yaw), Piece()
    if lower:
        ax.box(pc, -4.0, 4.0, -0.5, 0.03, -0.05, 0.55, "wood_dark")                            # solera
        feet, tops = (-3.65, -1.3, 1.3, 3.65), (-3.35, -1.3, 1.3, 3.35)
    else:
        ax.box(pc, -3.4, 3.4, -0.6, 0.03, -0.05, 0.55, "wood_dark")                            # sombrero
        feet, tops = (-2.95, -1.3, 1.3, 2.95), (-3.3, -1.3, 1.3, 3.3)
    for k, (a0, a1, ln) in enumerate(zip(feet, tops, legs)):
        a_end = a0 + (a1 - a0) * ln / 5.0
        ax.bar(pc, (a0, 0.0), (a_end, ln), 0.5, 0.0, C_BACK, "wood_dark")
        ax.splinter(pc, (a_end, ln), (a_end - a0, ln), 0.5, 0.0, C_BACK, k)
    top = min(legs) - 0.3
    ax.bar(pc, (feet[0] + 0.1, 0.35), (tops[3] - 0.15, top - 0.25), 0.42, -0.15, 0.005, "wood_dark")   # cruz
    ax.bar(pc, (feet[3] - 0.1, 0.35), (tops[0] + 0.15, top - 0.25), 0.42, C_FRONT, -0.01, "wood_dark")
    if lower:
        ax.box(pc, tops[0] - 0.2, tops[3] + 0.2, top - 0.45, top - 0.05, -0.16, 0.003, "wood_dark")    # riostra
    ax.ground(pc)
    return pc, ax


def raft(o, tilt, yaw, length, stringers, ties, planks):
    """Tramo de tablero caído: largueros a lo largo de la pendiente, durmientes cruzados y las tablas que
    quedaron encima. Sube hacia -Z: se apoya contra el caballete caído de adelante."""
    ax, pc = Axes(o, tilt, -1, yaw), Piece()
    for k, a in enumerate(stringers):
        ax.box(pc, a - 0.25, a + 0.25, 0.0, length, 0.0, 0.85, "wood_dark")
        ax.splinter(pc, (a, 0.0), (0.0, -1.0), 0.5, 0.0, 0.85, k)
    for b in ties:
        ax.box(pc, -3.3, 3.3, b - 0.3, b + 0.3, 0.83, 1.25, "wood_mid")
    for k, (a, b0, b1) in enumerate(planks):
        ax.box(pc, a - 0.48, a + 0.48, b0, b1, 1.23, 1.43, "wood_light" if k % 2 == 0 else "wood_mid")
    ax.ground(pc)
    return pc


def lean_against(pc, front, gap=-0.01):
    """Corre `pc` a lo largo de Z hasta tocar la cara de atrás (C_BACK) del caballete caído `front` (penetra 0,01)."""
    m = min((p - front.o).dot(front.en) - C_BACK for p in pc.points())
    pc.move((0, 0, -(m - gap) / front.en.z))


def leaning_stringer(ax, ab0, ab1, k):
    """Larguero roto acostado sobre la cara de adelante de un caballete caído (en sus ejes), con el pie en el suelo."""
    pc = Piece()
    c1 = C_FRONT + 0.005
    ax.bar(pc, ab0, ab1, 0.85, c1 - 0.5, c1, "wood_dark")
    (a0, b0), (a1, b1) = ab0, ab1
    ax.splinter(pc, ab1, (a1 - a0, b1 - b0), 0.85, c1 - 0.5, c1, k)
    ax.splinter(pc, ab0, (a0 - a1, b0 - b1), 0.85, c1 - 0.5, c1, k + 1)
    low = min(p.y for p in pc.points())
    pc.move(ax.eu * (-low / ax.eu.y))               # se desliza sobre la cara hasta apoyar en el suelo
    return pc


def plank_pile():
    """Tablas del tablero amontonadas al pie, del lado de la ruta (tres, cruzadas)."""
    pc = Piece()
    pc.add(box_pts((0.2, 0.1, -3.56), (3.8, 0.2, 0.8), 1.5, 0.0), "wood_light")
    pc.add(box_pts((-0.35, 0.29, -3.55), (3.4, 0.2, 0.78), -2.0, 0.0), "wood_mid")
    pc.add(box_pts((0.95, 0.36, -3.55), (2.6, 0.2, 0.75), 1.0, 7.0), "wood_light")
    return pc


def box_pts(c, size, yaw, roll):
    """Puntos de una caja girada `yaw` sobre Y y `roll` sobre Z (grados)."""
    r = Matrix.Rotation(math.radians(yaw), 3, "Y") @ Matrix.Rotation(math.radians(roll), 3, "Z")
    hx, hy, hz = (s / 2 for s in size)
    return [V(c) + r @ Vector((i * hx, j * hy, k * hz)) for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)]


def stringer_chunk():
    """Pedazo de larguero acostado con dos durmientes rotos cruzados encima."""
    pc = Piece()
    pc.add(box_pts((4.4, 0.25, -3.42), (2.8, 0.5, 0.85), -5.0, 0.0), "wood_dark")
    pc.add(splinter_pts((5.8, 0.25, -3.54), (1, 0, -0.087), (0, 0, 1), (0, 1, 0), 0.42, 0.25, 2), "wood_light")
    pc.add(box_pts((3.75, 0.68, -3.37), (0.6, 0.42, 1.1), 9.0, 0.0), "wood_mid")
    pc.add(box_pts((5.05, 0.69, -3.47), (0.6, 0.42, 1.0), -14.0, 0.0), "wood_mid")
    return pc


def build(mk):
    # ---------------- en pie ----------------
    bents = Piece()
    for x in BENT_X:
        bent(bents, x)
    bents.emit(mk, "fixed_Bents")
    deck(-1).emit(mk, "fixed_DeckLeft")
    deck(1).emit(mk, "fixed_DeckRight")

    # ---------------- escombros ----------------
    fa, axa = fallen_bent(True, (-3.65, 0, -2.45), 64.0, 5.0, (4.25, 4.45, 3.75, 4.35))
    fb, axb = fallen_bent(False, (4.1, 0, -2.2), 54.0, -7.0, (4.4, 3.8, 4.7, 4.05))
    ra = raft((-3.9, 0, 4.0), 45.0, 5.0, 4.6, (-2.35, -0.85, 0.85, 2.35), (0.55, 1.8, 3.05, 4.25),
              [(-2.5, 0.2, 4.4), (-0.5, 0.4, 4.5), (1.5, 0.1, 3.5), (2.5, 0.8, 4.45)])
    lean_against(ra, axa)
    rb = raft((4.0, 0, 4.0), 49.0, -7.0, 3.95, (-2.35, -0.85, 0.85, 2.35), (0.5, 1.6, 2.65, 3.6),
              [(-1.5, 0.2, 3.8), (0.5, 0.5, 3.85), (2.5, 0.3, 3.3)])
    lean_against(rb, axb)
    sa = leaning_stringer(axa, (-3.3, -0.6), (1.1, 4.0), 0)
    sb = leaning_stringer(axb, (3.1, -0.6), (-1.3, 4.1), 1)
    frags = [fa, fb, ra, rb, sa, sb, plank_pile(), stringer_chunk()]
    for i, pc in enumerate(frags):
        pc.emit(mk, f"frag{i + 1:02d}")
    front = min(p.z for pc in frags for p in pc.points() if abs(p.x) < 1.5)
    mk.marker("_ChargeSpot", (0.0, 0.05, round(front - 0.15, 2)))

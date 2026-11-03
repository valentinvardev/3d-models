"""
Receta de WST_Prop_Barrel, el barril de madera destructible (prompt 018, Bloques A + C).

Brief
- Silueta a 40 studs: panza (2,2) más ancha que las puntas (1,9), tres aros de hierro oscuros sobre la
  madera, canto de la tapa. Es lo que dice "barril" aunque esté en negro.
- Medidas: 3,0 de alto; sección de 10 lados (vértices cada 36°, una duela mirando al frente); anillos en
  y = 0 (r 0,95), 1,0 y 2,0 (r 1,10), 3,0 (r 0,95): tres tramos verticales para la panza.
  Aros a 15/50/85 % (y 0,45, 1,5, 2,55), 0,15 de alto y 0,04 afuera. Tapa hundida 0,1 con tapón.
- Fragmentos (6, origen común en la base): frag01-04 = la pared en cuatro gajos cortados por las juntas
  de las duelas (frente y atrás 3 duelas, derecha e izquierda 2), cada uno con sus tramos de aro;
  frag05 = tapa; frag06 = fondo. Los gajos son macizos (porción de torta): convexos y > 0,4 en todo.
- Juntas de las duelas: chanflán de un segmento color wood_dark en las aristas verticales (las "10
  ranuras poco profundas" del prompt, como tira oscura de ~0,06). Las tablas de la tapa: tiras pintadas.
- Variante Barrel_Water (mismo archivo, a la derecha en +X): sin tapa, agua 0,3 abajo del canto
  (objeto Barrel_Water_Water aparte, se oculta al romperse, como en el bebedero); frag01-04 + frag05 fondo.
- Inferido: gajos macizos en vez de cáscara (convexos, el interior no se ve); cortes por las juntas
  (3-2-3-2 duelas) en vez de cuartos exactos; una grieta en zigzag tallada en una duela del frente y un
  canto mellado (desgaste "hecho con geometría" del Bloque A); nombres de la variante con prefijo
  Barrel_Water_ y su origen en su propia base.

Vueltas: 1) 842 tris y z-fighting en los cuatro gajos: la punta de cada tramo de aro caía justo en el
plano de corte (6 pares por gajo) · 2) aros con un casco de puntos de afuera (cierra por la cuerda, sin
cara en el corte) y los aros de las puntas a 16 y 81 % para que su cuerda no se meta en la tapa ni en el
fondo (en los gajos de 3 duelas llega a r 0,62 < 0,80): 746.

Revisión
- 746 triángulos el barril (+632 la variante) contra 300 de referencia (calidad primero). Medido con la
  receta: el chanflán de las juntas cuesta ~220 (524 sin él), los huecos de tapa y fondo ~130 y los aros
  en relieve ~130. Las juntas son lo que dice "duelas" a 20 studs y los aros son la silueta; sin chanflán
  quedaría alternar colores de duela, que se ve a caramelo. Se aceptó el exceso.
- Aros a 16/50/81 % en vez de 15/50/85 %: 0,03 y 0,13 de diferencia, para no pisar la tapa ni el fondo.
- Medidas: 2,28 de ancho (2,2 de panza + aros), 3,0 de alto. Gajos de 17-26 % del volumen, mínimo 1,07;
  tapa y fondo 0,40-0,46 de grosor.
- La variante usa prefijo Barrel_Water_ y su origen en su base (x = 3,6); el agua es objeto aparte y se
  oculta al romperse, como el bebedero. Sin decisión del vault sobre cómo nombrar variantes: dudoso.
"""

import math

H = 3.0
R_END, R_BELLY = 0.95, 1.10
Y_BELLY = (1.0, 2.0)
RINGS = (0.0, 1.0, 2.0, 3.0)
LID_INSET, LID_T = 0.1, 0.4
R_CAP = 0.80                      # tapa y fondo (radio de vértice), adentro del canto
BOT_T = 0.4
HOOPS = (0.48, 1.5, 2.42)        # 16/50/81 %: el aro de cada punta queda fuera de la franja de la tapa y el fondo
HOOP_H, HOOP_PROUD = 0.15, 0.04
WATER_DROP = 0.3
# gajos cortados por las juntas (vértices cada 36°; 270° = frente, -Z): frente, derecha, atrás, izquierda
WALLS = ((216, 324), (324, 396), (36, 144), (144, 216))
WATER_X = 3.6                     # la variante, al lado


def radius(y):
    if y <= Y_BELLY[0]:
        return R_END + (R_BELLY - R_END) * y / Y_BELLY[0]
    if y >= Y_BELLY[1]:
        return R_END + (R_BELLY - R_END) * (H - y) / (H - Y_BELLY[1])
    return R_BELLY


def pt(x0, r, deg, y):
    a = math.radians(deg)
    return (x0 + r * math.cos(a), y, r * math.sin(a))


def cap_pts(x0, r, y0, y1):
    """Prisma de 10 lados alineado con las duelas (tapa, fondo y los cortadores de sus huecos)."""
    return [pt(x0, r, a, y) for a in range(0, 360, 36) for y in (y0, y1)]


def tube(mk, part, a, b, r, mat, sides=6, detail=True):
    """Cilindro de a a b (puntos del juego): mechas, sogas."""
    ax = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in ax))
    d = [c / n for c in ax]
    ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    un = math.sqrt(sum(c * c for c in u))
    u = [c / un for c in u]
    v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    pts = []
    for p in (a, b):
        for k in range(sides):
            t = 2 * math.pi * (k + 0.5) / sides
            pts.append(tuple(p[i] + r * (math.cos(t) * u[i] + math.sin(t) * v[i]) for i in range(3)))
    mk.hull(part, pts, mat, detail=detail)


def crack(mk, part, x0, deg, y0, y1, depth=0.16):
    """Grieta en zigzag a lo largo de la veta de una duela (prisma tallado)."""
    a = math.radians(deg)
    rr = radius((y0 + y1) / 2) * math.cos(math.radians(18))
    center = (x0 + rr * math.cos(a), 0, rr * math.sin(a))
    phi = math.degrees(math.atan2(math.cos(a), math.sin(a)))      # +Z local -> normal de la duela
    left, right = [], []
    for i in range(5):
        y = y0 + (y1 - y0) * i / 4
        dx = 0.07 if i % 2 else -0.05
        w = 0.035 if 0 < i < 4 else 0.01
        left.append((dx - w, y))
        right.append((dx + w, y))
    mk.carve(part, "coal", prism=dict(profile=left + right[::-1], depth=depth, plane="xy",
                                      center=center, rot=(0, phi, 0)))


def barrel(mk, prefix="", x0=0.0, wall="wood_mid", seam="wood_dark", hoop="iron", lid_mat="wood_mid",
           lid_seam="wood_dark", bung="wood_light", water=False, band=None, cracked=False, chipped=False):
    """Arma el barril en x0. Devuelve los nombres de las piezas: walls (frente, der, atrás, izq), lid, bottom."""
    out = {"walls": []}
    nfrag = 0

    def frag():
        nonlocal nfrag
        nfrag += 1
        return mk.part(f"{prefix}frag{nfrag:02d}", (x0, 0, 0))

    top_cut = H - WATER_DROP - 0.08 if water else H - LID_INSET - LID_T
    for a0, a1 in WALLS:
        p = frag()
        out["walls"].append(p)
        pts = []
        for y in RINGS:
            pts += [pt(x0, radius(y), a, y) for a in range(a0, a1 + 1, 36)] + [(x0, y, 0.0)]
        mk.hull(p, pts, wall)
        mk.bevel(p, width=0.03, angle=30, mat=seam)                          # juntas de las duelas
        mk.carve(p, wall if not water else "wood_dark", points=cap_pts(x0, R_CAP, top_cut, H + 0.2))   # hueco de la tapa
        mk.carve(p, wall, points=cap_pts(x0, R_CAP, -0.2, BOT_T))           # hueco del fondo
        if band:
            mat, y0, y1 = band
            mk.slice(p, (x0, y0, 0), (0, 1, 0))
            mk.slice(p, (x0, y1, 0), (0, 1, 0))
            # pinta todo lo que cae en la franja, también las caras de corte (ocultas con el barril entero):
            # `paint` elige por el centro de cada triángulo y los del corte no se separan bien de las duelas
            mk.paint(p, mat, box=((x0, (y0 + y1) / 2, 0), (4, y1 - y0, 4)))
        for yc in HOOPS:                                                     # tramos de los aros
            # solo puntos de afuera: el casco cierra por la cuerda (adentro del gajo) y no deja una
            # cara en el plano de corte (coplanar con la del gajo: z-fighting medido en la vuelta 1)
            hp = [pt(x0, radius(y) + HOOP_PROUD, a, y) for y in (yc - HOOP_H / 2, yc + HOOP_H / 2)
                  for a in range(a0, a1 + 1, 36)]
            mk.hull(p, hp, hoop, detail=True)

    if cracked:                                                              # duela rajada adelante a la derecha
        crack(mk, out["walls"][0], x0, 306, 0.66, 1.36)
    if chipped:                                                              # canto mellado a la derecha
        mk.carve(out["walls"][1], wall, points=mk.pts_box((x0 + 0.98, 3.0, -0.12), (0.32, 0.26, 0.42),
                                                           rot=(0, 15, 38)))

    if not water:
        lid = frag()
        out["lid"] = lid
        ly0, ly1 = H - LID_INSET - LID_T, H - LID_INSET
        mk.hull(lid, cap_pts(x0, R_CAP, ly0, ly1), lid_mat)
        for z in (-0.27, 0.27):                                              # juntas de las tablas de la tapa
            mk.slice(lid, (x0, ly1, z - 0.03), (0, 0, 1))
            mk.slice(lid, (x0, ly1, z + 0.03), (0, 0, 1))
            mk.paint(lid, lid_seam, box=((x0, ly1, z), (2, 0.04, 0.06)))
        mk.cyl(lid, (x0 + 0.42, ly1 + 0.01, 0.0), 0.13, 0.1, bung, sides=8, detail=True)   # tapón

    bot = frag()
    out["bottom"] = bot
    mk.hull(bot, cap_pts(x0, R_CAP, 0.0, BOT_T), wall)

    if water:
        w = mk.part(f"{prefix}Water", (x0, 0, 0))
        mk.hull(w, cap_pts(x0, R_CAP, top_cut, H - WATER_DROP), "water")
        out["water"] = w
    return out


def build(mk):
    barrel(mk, cracked=True, chipped=True)
    barrel(mk, prefix="Barrel_Water_", x0=WATER_X, water=True)

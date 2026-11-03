"""
Receta de WST_HC_CemeteryFence, los cercos del cementerio de Hollow Creek (prompt 118, Bloques A + C).

Brief
- Silueta a 40 studs: reja de hierro de barrotes con punta de lanza entre pilares de piedra; portón doble
  de hierro bajo un arco con cartel; cerco de estacas de madera blanqueada con huecos.
- Tres módulos en fila sobre X cada 10 (prefijo <Variante>_, origen en la base al centro de cada uno,
  frente -Z): Fence_Iron en x = 0, Fence_Gate en x = 10, Fence_Picket en x = 20.
- Fence_Iron (8 x 4): pilares stone_grey de 0,8 x 4,4 con remate en punta en x = ±3,6
  (Fence_Iron_fixed_Posts, quedan en pie); entre ellos 13 barrotes de hierro de 0,14 cada 0,5 (y 0,25 a
  3,62) con punta de lanza hasta 4,05, y dos travesaños (y 0,45-0,6 y 3,2-3,35) que se meten 0,05 en los
  pilares. 3 fragmentos cortados entre barrotes (x = ±1,25).
- Fence_Gate (8 x 7,1): pilares de 1 x 5,4 con capitel (Fence_Gate_PostL / _PostR); arco de hierro
  elíptico (3,3 x 1,6) que arranca en los capiteles a 5,4, con un travesaño abajo, cuatro barrotes y el
  cartel liso (gunmetal con marco de hierro) en la clave (Fence_Gate_Arch, todo arriba de 5,3: no tapa el
  paso). Hojas Fence_Gate_GateL / _GateR de 3,05 x ~4,2: bastidor de hierro, travesaño de arriba que sube
  hacia el centro, 5 barrotes con punta y dos nudos de bisagra; origen en el canto de afuera (bisagra).
- Fence_Picket (8 x 3): postes de madera oscura en x = ±3,8 (Fence_Picket_fixed_Posts), dos largueros
  wood_mid atrás, estacas de 0,4 x 0,12 cada 0,6 con punta, blanqueadas y gastadas (paint_cream; dos
  reemplazadas en wood_light). Faltan dos, una está rota a media altura y otra torcida. 3 fragmentos.
- Inferido: medidas de pilares, travesaños, barrotes y estacas, forma del arco y del cartel, alto de las
  hojas, colores del cerco de madera, cuáles faltan, nombres de pilares, arco y hojas (con prefijo).

Vueltas: 1) primera versión: z-fighting entre el marco del cartel y el arco (misma cara de adelante), entre
los barrotes de las hojas y sus travesaños (los dos de 0,12) y entre las puntas del travesaño de arriba de
cada hoja y los montantes; estacas a ras de los largueros · 2) marco 0,01 más adelante, barrotes de las
hojas de 0,1, travesaño de arriba 0,02 adentro de cada canto, estacas metidas 0,01 en los largueros.

Revisión
- Triángulos por módulo (tope 250 de referencia): Fence_Iron 482 (13 barrotes con punta de lanza de 26
  cada uno: es lo que pide "cada 0,5"), Fence_Gate 780 (dos hojas de ~270 con 5 lanzas, bastidor y
  bisagras; arco con cartel ~170; pilares 68), Fence_Picket 284. Es la entrada del cementerio.
- Medidas: reja 8 x 4,05 (pilares hasta 4,96); portón 8,45 x 7,0 (paso libre de 6,2 x 5,28 bajo el
  travesaño del arco); cerco de estacas 8 x 3,3 (postes).
- Fragmentos: 3 por reja y por cerco (cortes entre barrotes / estacas, ~33 % cada uno). Los barrotes son
  de 0,14 (el Bloque C pide fragmentos de 0,4: cada fragmento mide 2 x 4 x 0,14; manda el material).
- Colisión: el arco del portón está entero arriba de 5,28 y los pilares van aparte, así que el casco no
  tapa el paso. Las hojas giran sobre el canto de afuera (bisagra).
- Materiales: iron, stone_grey, gunmetal (cartel), wood_dark, wood_mid, paint_cream, wood_light.
"""

import math

IRON, STONE, PLATE, LIGHT, MID, DARK, CREAM = "iron", "stone_grey", "gunmetal", "wood_light", "wood_mid", "wood_dark", "paint_cream"


def spear(mk, part, x, y0, y1, z=0.0, w=0.14):
    """Barrote de y0 a y1 con punta de lanza encima (dos cascos que se enciman)."""
    mk.box(part, (x, (y0 + y1) / 2, z), (w, y1 - y0, w), IRON)
    pts = [(x + dx, y1 - 0.05, z + dz) for dx in (-0.06, 0.06) for dz in (-0.06, 0.06)]
    pts += [(x + dx, y1 + 0.13, z) for dx in (-0.17, 0.17)] + [(x, y1 + 0.13, z + dz) for dz in (-0.05, 0.05)]
    pts += [(x, y1 + 0.43, z)]
    mk.hull(part, pts, IRON)


def stone_post(mk, part, x, w, h, cap=True):
    mk.box(part, (x, h / 2, 0), (w, h, w), STONE)
    if cap:
        mk.box(part, (x, h + 0.1, 0), (w + 0.2, 0.22, w + 0.2), STONE)
        mk.box(part, (x, h + 0.38, 0), (w * 0.9, 0.36, w * 0.9), STONE, top=(0.15, 0.15))


# -------------------------------------------------------------------------------------------------- reja
def fence_iron(mk, ox):
    pre = "Fence_Iron"
    posts = mk.part(f"{pre}_fixed_Posts", (ox, 0, 0))
    for s in (-1, 1):
        stone_post(mk, posts, ox + s * 3.6, 0.8, 4.4)
    cuts = [-3.25, -1.25, 1.25, 3.25]
    pickets = [-3.0 + 0.5 * i for i in range(13)]
    for f in range(3):
        a, b = cuts[f], cuts[f + 1]
        p = mk.part(f"{pre}_frag0{f + 1}", (ox, 0, 0))
        for y0, y1 in ((0.45, 0.6), (3.2, 3.35)):
            mk.box(p, (ox + (a + b) / 2, (y0 + y1) / 2, 0), (b - a, y1 - y0, 0.12), IRON)
        for x in pickets:
            if a < x < b:
                top = 3.62 - (0.25 if (f == 1 and abs(x) < 0.1) else 0.0)          # uno doblado más bajo
                spear(mk, p, ox + x, 0.25, top)
    return posts


# ------------------------------------------------------------------------------------------------ portón
GATE_W = 3.1                 # medio ancho del paso (cara de adentro de los pilares)
ARCH_Y = 5.4


def gate_leaf(mk, name, ox, side):
    """side = -1 hoja izquierda (bisagra en x = -3,08), +1 derecha."""
    hx = ox + side * (GATE_W - 0.02)
    p = mk.part(name, (hx, 0, 0))
    X = lambda u: hx - side * u                                   # noqa: E731  (u desde la bisagra hacia el centro)
    L = GATE_W - 0.045                                            # ancho de la hoja (luz de 0,05 al medio)

    def top(u):
        return 3.75 + 0.45 * (u / L) ** 1.5
    for u, w in ((0.08, 0.16), (L - 0.08, 0.16)):                 # montantes
        h = top(u) + 0.05
        mk.box(p, (X(u), (0.2 + h) / 2, 0), (w, h - 0.2, 0.14), IRON)
    mk.box(p, (X(L / 2), 0.38, 0), (L - 0.2, 0.14, 0.12), IRON)                       # travesaño de abajo
    mk.box(p, (X(L / 2), 1.75, 0), (L - 0.2, 0.12, 0.12), IRON)                       # del medio
    n = 6
    upper = [(X(0.02 + (L - 0.04) * i / n), top(0.02 + (L - 0.04) * i / n)) for i in range(n + 1)]   # sin tocar los cantos
    lower = [(x, y - 0.14) for x, y in reversed(upper)]
    prof = upper + lower
    if side > 0:
        prof = list(reversed(prof))
    mk.prism(p, prof, 0.12, IRON, plane="xy", center=(0, 0, 0))                      # travesaño de arriba
    for k in range(5):                                                                # barrotes con punta
        u = 0.55 + 0.5 * k
        spear(mk, p, X(u), 0.3, top(u) + 0.1, w=0.1)
    for y in (0.7, 3.3):                                                             # nudos de bisagra
        mk.cyl(p, (hx, y, 0.0), 0.1, 0.4, IRON, sides=6, detail=True)
    return p


def fence_gate(mk, ox):
    pre = "Fence_Gate"
    for name, s in (("PostL", -1), ("PostR", 1)):
        p = mk.part(f"{pre}_{name}", (ox + s * 3.6, 0, 0))
        stone_post(mk, p, ox + s * 3.6, 1.0, ARCH_Y - 0.1, cap=False)
        mk.box(p, (ox + s * 3.6, ARCH_Y + 0.0, 0), (1.25, 0.24, 1.25), STONE)                # capitel
        mk.box(p, (ox + s * 3.6, ARCH_Y + 0.31, 0), (1.0, 0.4, 1.0), STONE, top=(0.2, 0.2))
    arch = mk.part(f"{pre}_Arch", (ox, 0, 0))
    a, b, t = 3.3, 1.6, 0.16
    angs = [-0.04 + (math.pi + 0.08) * i / 10 for i in range(11)]
    outer = [(ox + a * math.cos(q), ARCH_Y + b * math.sin(q)) for q in angs]
    inner = [(ox + (a - t) * math.cos(q), ARCH_Y + (b - t) * math.sin(q)) for q in reversed(angs)]
    mk.prism(arch, outer + inner, 0.14, IRON, plane="xy", center=(0, 0, 0))
    mk.box(arch, (ox, ARCH_Y + 0.02, 0), (2 * a - 0.1, 0.14, 0.12), IRON)                      # travesaño
    for xb in (-2.2, -1.2, 1.2, 2.2):                                                          # barrotes
        yt = ARCH_Y + (b - t) * math.sqrt(max(0.0, 1 - (xb / (a - t)) ** 2)) + 0.05
        mk.box(arch, (ox + xb, (ARCH_Y + yt) / 2, 0), (0.1, yt - ARCH_Y, 0.1), IRON)
    mk.box(arch, (ox, ARCH_Y + 1.15, -0.03), (2.4, 0.8, 0.1), IRON)                            # marco del cartel
    mk.box(arch, (ox, ARCH_Y + 1.15, -0.1), (2.2, 0.62, 0.08), PLATE)                          # cartel liso
    gate_leaf(mk, f"{pre}_GateL", ox, -1)
    gate_leaf(mk, f"{pre}_GateR", ox, 1)


# ----------------------------------------------------------------------------------------- cerco de estacas
def picket(mk, part, x, mat, h=2.9, lean=0.0, broken=False):
    w, t, z = 0.4, 0.12, -0.19
    if broken:
        prof = [(-w / 2, 0.15), (w / 2, 0.15), (w / 2, 1.3), (0.05, 1.55), (-0.08, 1.38), (-w / 2, 1.6)]
    else:
        prof = [(-w / 2, 0.15), (w / 2, 0.15), (w / 2, h - 0.25), (0.0, h), (-w / 2, h - 0.25)]
    mk.prism(part, prof, t, mat, plane="xy", center=(x, 0, z), rot=(0, 0, lean))


def fence_picket(mk, ox):
    pre = "Fence_Picket"
    posts = mk.part(f"{pre}_fixed_Posts", (ox, 0, 0))
    for s in (-1, 1):
        mk.box(posts, (ox + s * 3.8, 1.6, 0), (0.4, 3.2, 0.4), DARK)
        mk.box(posts, (ox + s * 3.8, 3.25, 0), (0.46, 0.1, 0.46), DARK, top=(0.3, 0.3))
    cuts = [-3.65, -1.2, 1.2, 3.65]
    xs = [-3.3 + 0.6 * i for i in range(12)]
    missing = {-2.1, 1.5}
    for f in range(3):
        a, b = cuts[f], cuts[f + 1]
        p = mk.part(f"{pre}_frag0{f + 1}", (ox, 0, 0))
        for y in (0.75, 2.3):                                                          # largueros, atrás
            mk.box(p, (ox + (a + b) / 2, y, -0.02), (b - a, 0.22, 0.24), MID)
        for i, x in enumerate(xs):
            if not (a < x < b) or any(abs(x - m) < 1e-6 for m in missing):
                continue
            mat = LIGHT if i in (3, 9) else CREAM
            picket(mk, p, ox + x, mat, h=2.9 + (0.06 if i % 3 == 0 else 0.0) - (0.05 if i % 4 == 1 else 0.0),
                   lean=(-6.0 if abs(x - 0.3) < 1e-6 else 0.0), broken=abs(x + 0.9) < 1e-6)
    return posts


def build(mk):
    fence_iron(mk, 0.0)
    fence_gate(mk, 10.0)
    fence_picket(mk, 20.0)

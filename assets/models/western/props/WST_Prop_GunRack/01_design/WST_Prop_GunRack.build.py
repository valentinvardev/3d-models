"""
Receta de WST_Prop_GunRack, el armero del vagón de preparación (prompt 075, Bloques A + B).

Brief
- Silueta que se lee a 40 studs (de adentro del vagón, más cerca): mueble oscuro de tres pisos
  contra la pared con fondo de tablas claras: arriba 4 sombreros vaqueros de colores distintos,
  al medio 4 revólveres colgados con el caño para abajo, abajo 4 chalecos en perchas; cartel liso arriba.
- Medidas: 8 (x) x 6 (y) x 1,2 (z, fondo en +Z); estante de sombreros a 4,35; clavijas de los
  revólveres a 3,95; barral de las perchas a 2,70; cartel 2,8 x 0,48 sobre la cornisa (arriba a 6,0).
- Piezas: Body (mueble, fondo de tablas, estantes, clavijas, barral, cartel), Hat_1..4 (origen en la
  base, sobre el estante), Revolver_1..4 (origen en la clavija que pasa por el guardamonte),
  Vest_1..4 (origen en el gancho de la percha). Ítems a 1,9 entre centros.
- Revólver simple (~200 triángulos): el mismo perfil y tamaño que WST_Weapon_Revolver (1,3 de largo),
  caño, armazón, tambor, martillo, guardamonte de bronce y cacha de madera, de costado al frente.
- Fondo de tablas verticales wood_mid con alma oscura atrás: las juntas se ven como líneas de verdad.
- Inferido: el mueble se apoya en el piso (origen abajo) y no cuelga; sombreros parados en el
  estante con una clavija que entra por atrás en la copa; colores: Hat_1 marrón con cinta negra,
  Hat_2 negro con cinta roja, Hat_3 lona con cinta marrón, Hat_4 marrón con cinta roja; chalecos
  alternados cuero / paño marrón; 9 materiales (el prompt nombra 6 colores y los revólveres suman metal).

Vueltas: 1) primera versión: las bocas de los revólveres (2,93) chocaban con el barral de las perchas
(2,95) y un listón cruzaba los chalecos; el cartel pasaba de 6,0 · 2) barral a 2,70, sin listón,
cornisa que vuela 0,02 (sus puntas eran coplanares con los laterales) · 3) ala vaquera: costados
levantados 22° como placas planas (con el ala plana se leían como sombreros de ciudad).

Revisión
- 2304 triángulos contra 1500 de referencia. El prompt pide 12 objetos sueltos y cerrados (se sacan
  del mueble) y revólveres de ~400 cada uno (eso solo serían 1600); acá cada revólver es 188, cada
  sombrero ~176, cada chaleco 114 y el mueble 392.
- Medidas 8,04 x 6,02 x 1,24: la cornisa vuela 0,02 por lado y el marco del cartel llega a 6,02.
- La pieza fija se llama Body (como en los otros props con piezas sueltas); el prompt no le da nombre.
"""

import math

W, H, D = 8.0, 6.0, 1.2
BACK = 0.48                      # cara de adelante del fondo
SLOTS = (-2.85, -0.95, 0.95, 2.85)
HAT_SHELF, PEG_Y, ROD_Y = 4.35, 3.95, 2.70          # el barral queda debajo de las bocas de los revólveres (2,93)


def ring(cx, y, cz, rx, rz, n=10, front=1.0):
    """Anillo horizontal; `front` achica la mitad de adelante (-z) para pellizcar la copa."""
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        z = rz * math.sin(a)
        k = front if z < 0 else 1.0
        out.append((cx + rx * math.cos(a) * k, y, cz + z))
    return out


def hat(mk, name, c, crown, band):
    x, y, z = c
    part = mk.part(name, c)
    # ala vaquera: centro plano y los costados levantados 22° como placas planas (un casco con puntos fuera de
    # un plano se rellena y el ala se vería como una cuña gruesa)
    rx, rz, x0, tilt = 0.62, 0.52, 0.30, math.tan(math.radians(22))

    def edge(xa):
        return rz * math.sqrt(max(0.0, 1 - (xa / rx) ** 2))

    def brim_pts(lo, hi, lift):
        pts = [(xa, edge(xa) * k) for xa in (lo, hi) for k in (-1, 1)]
        pts += [(rx * math.cos(a), rz * math.sin(a)) for a in [2 * math.pi * i / 16 for i in range(16)]
                if lo <= rx * math.cos(a) <= hi]
        return [(x + xa, y + dy + lift(xa), z + za) for xa, za in pts for dy in (-0.01, 0.04)]

    mk.hull(part, brim_pts(-x0 - 0.02, x0 + 0.02, lambda xa: 0.0), crown)
    for sgn in (-1, 1):
        lo, hi = (x0, rx) if sgn > 0 else (-rx, -x0)
        mk.hull(part, brim_pts(lo, hi, lambda xa: max(0.0, abs(xa) - x0) * tilt), crown)
    mk.hull(part, ring(x, y + 0.03, z, 0.34, 0.30) + ring(x, y + 0.32, z, 0.33, 0.28)
            + ring(x, y + 0.48, z, 0.27, 0.21, front=0.7), crown)                                          # copa pellizcada
    mk.hull(part, ring(x, y + 0.035, z, 0.36, 0.32) + ring(x, y + 0.15, z, 0.355, 0.315), band)            # cinta
    return part


def revolver(mk, name, peg):
    """Revólver colgado de la clavija por el guardamonte: caño hacia abajo, de costado al frente (-z)."""
    px, py, pz = peg
    ug, vg = 0.145, 0.07                    # punto del guardamonte donde pasa la clavija (u hacia la boca, v arriba del arma)
    part = mk.part(name, peg)

    def wpt(u, v, w=0.0):
        return (px - (v - vg), py - (u - ug), pz + w)

    def prof(points):
        return [wpt(u, v)[:2] for u, v in points]

    mk.cyl(part, wpt(0.885, 0.395), 0.06, 0.56, "gunmetal", axis="y", sides=8)                     # caño
    mk.cyl(part, wpt(0.81, 0.325, 0.0), 0.034, 0.42, "gunmetal", axis="y", sides=6)               # funda de la varilla
    frame = [(0.60, 0.49), (0.60, 0.16), (0.10, 0.12), (0.03, 0.16), (0.03, 0.44), (0.13, 0.49)]
    mk.prism(part, prof(frame), 0.15, "gunmetal", plane="xy", center=(0, 0, pz))                  # armazón
    mk.cyl(part, wpt(0.37, 0.31), 0.135, 0.30, "gunmetal", axis="y", sides=8)                     # tambor
    mk.prism(part, prof([(0.10, 0.40), (0.0, 0.40), (-0.10, 0.58), (-0.06, 0.62), (0.06, 0.48)]), 0.08,
             "gunmetal", plane="xy", center=(0, 0, pz))                                            # martillo
    guard = [(0.26, 0.14), (0.25, 0.04), (0.20, -0.02), (0.10, -0.02), (0.05, 0.04), (0.05, 0.14),
             (0.10, 0.14), (0.105, 0.05), (0.13, 0.025), (0.19, 0.025), (0.21, 0.05), (0.21, 0.14)]
    mk.prism(part, prof(guard), 0.06, "brass", plane="xy", center=(0, 0, pz))                     # guardamonte
    grip = [(0.10, 0.17), (0.0, 0.17), (-0.035, 0.07), (-0.085, -0.06), (-0.135, -0.135), (-0.095, -0.195),
            (0.025, -0.195), (0.06, -0.06), (0.095, 0.05)]
    mk.prism(part, prof(grip), 0.13, "wood_mid", plane="xy", center=(0, 0, pz))                   # cacha
    return part


def vest(mk, name, hook, mat):
    hx, hy, hz = hook
    part = mk.part(name, hook)
    top = hy - 0.30                                                     # línea de los hombros
    mk.hull(part, [(hx + x, y, hz + dz) for x, y in ((-0.56, top - 0.02), (0.56, top - 0.02), (0.0, hy - 0.12))
                   for dz in (-0.03, 0.03)], "wood_mid")                # percha
    mk.box(part, (hx, hy - 0.04, hz), (0.04, 0.18, 0.04), "gunmetal")   # gancho sobre el barral
    out = [(-0.66, 0.12), (-0.66, 0.92), (-0.50, 1.22), (-0.46, 1.50), (-0.18, 1.55), (0.0, 0.82), (0.18, 1.55),
           (0.46, 1.50), (0.50, 1.22), (0.66, 0.92), (0.66, 0.12), (0.12, 0.0), (0.0, 0.10), (-0.12, 0.0)]
    y0 = top - 1.55
    mk.prism(part, [(hx + x, y0 + y) for x, y in out], 0.14, mat, plane="xy", center=(0, 0, hz))
    mk.box(part, (hx, y0 + 1.18, hz + 0.07), (0.40, 0.75, 0.04), "cloth_black")                  # forro que se ve en el escote
    mk.box(part, (hx, y0 + 0.45, hz - 0.075), (0.035, 0.75, 0.02), "cloth_black")                # abertura del frente
    for y in (0.30, 0.52, 0.74):
        mk.hull(part, [(hx + 0.10 + dx, y0 + y + dy, hz - 0.07) for dx in (-0.04, 0.04) for dy in (-0.04, 0.04)]
                + [(hx + 0.10, y0 + y, hz - 0.12)], "brass")                                    # botones
    return part


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    hx, hz = W / 2, D / 2
    # ---------------- fondo de tablas verticales con alma oscura ----------------
    mk.box(body, (0, 2.95, 0.555), (W - 0.36, 5.10, 0.07), "wood_dark")
    n = 8
    for i in range(n):
        x0 = -hx + 0.20 + i * (W - 0.40) / n
        mk.box(body, (x0 + (W - 0.40) / n / 2, 2.95, 0.525), ((W - 0.40) / n - 0.05, 5.20, 0.09), "wood_mid")
    # ---------------- mueble: laterales, zócalo, cornisa, estantes ----------------
    for s in (-1, 1):
        mk.box(body, (s * (hx - 0.10), 2.70, 0), (0.20, 5.40, D), "wood_dark")                     # laterales
    mk.box(body, (0, 0.15, 0.02), (W - 0.40, 0.30, D - 0.06), "wood_dark")                         # zócalo
    mk.box(body, (0, 5.45, 0), (W + 0.04, 0.12, D + 0.04), "wood_dark")                            # cornisa (vuela 0,02)
    mk.box(body, (0, 5.32, -0.02), (W - 0.12, 0.14, D - 0.08), "wood_dark")
    mk.box(body, (0, HAT_SHELF - 0.05, -0.02), (W - 0.40, 0.10, D - 0.12), "wood_dark")           # estante de los sombreros
    for x in SLOTS:
        mk.cyl(body, (x, HAT_SHELF + 0.30, 0.22), 0.05, 0.56, "wood_dark", axis="z", sides=6)     # clavija del sombrero
        mk.cyl(body, (x, PEG_Y, 0.26), 0.04, 0.48, "wood_dark", axis="z", sides=6)                # clavija del revólver
    mk.cyl(body, (0, ROD_Y, 0.15), 0.05, W - 0.38, "wood_dark", axis="x", sides=8)                # barral de las perchas
    # ---------------- cartel liso arriba ----------------
    mk.box(body, (0, 5.74, 0.05), (2.80, 0.48, 0.10), "wood_mid")
    mk.box(body, (0, 5.74, 0.08), (2.96, 0.56, 0.08), "wood_dark")                                 # marco (atrás, asoma 0,08)

    # ---------------- ítems ----------------
    for i, (x, crown, band) in enumerate(zip(SLOTS, ("cloth_brown", "cloth_black", "canvas", "cloth_brown"),
                                             ("cloth_black", "paint_red", "cloth_brown", "paint_red"))):
        hat(mk, f"Hat_{i + 1}", (x, HAT_SHELF, -0.06), crown, band)
        revolver(mk, f"Revolver_{i + 1}", (x, PEG_Y, 0.10))
        vest(mk, f"Vest_{i + 1}", (x, ROD_Y + 0.06, 0.15), "leather" if i % 2 == 0 else "cloth_brown")

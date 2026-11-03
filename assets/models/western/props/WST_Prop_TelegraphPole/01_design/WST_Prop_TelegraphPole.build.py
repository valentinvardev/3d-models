"""
Receta de WST_Prop_TelegraphPole, el poste de telégrafo (prompt 132, Bloques A + C).

Brief
- Silueta a 40 studs: palo alto y fino con una cruceta ancha arriba (una T), cuatro puntitos verdes
  (aisladores) sobre la cruceta y dos riostras en diagonal debajo.
- Medidas: 16 de alto; poste de 8 lados con 0,6 entre caras (r de vértice 0,325), punta en tronco de
  cono (sombrerete). Cruceta 5 (X) x 0,4 x 0,4 a y 14,7-15,1, apoyada en la cara del frente del poste.
  Aisladores glass_green (campana de 0,34) sobre clavijas de madera en x = ±1,05 y ±2,15. Marcadores
  _Wire_1.._Wire_4 en la garganta de cada aislador (de -X a +X).
- Fragmentos (3, origen común): frag01 el tramo de abajo (de 0 a ~5,33 = 1/3), frag02 el de arriba,
  frag03 la cruceta con riostras, clavijas y aisladores. El quiebre a 1/3 es un zigzag: dos tallados con
  el mismo perfil, uno saca lo de arriba del frag01 y el otro lo de abajo del frag02 (sin luz ni
  encimado). Una mella de madera clara al frente, justo en el quiebre, avisa dónde se va a partir.
- Variante TelegraphPole_Leaning (mismo archivo, x = 7): el mismo poste inclinado 12° hacia +Z (a lo
  largo de la línea, así la cruceta queda horizontal); la base se talla plana en el piso.
  Piezas TelegraphPole_Leaning_frag01..03 y marcadores _TelegraphPole_Leaning_Wire_1..4.
- Inferido: qué es cada fragmento (el prompt dice "se parte a 1/3; la cruceta aparte"); riostras de
  madera con la cruceta; sombrerete; mella; hacia dónde se inclina la variante; nombres de la variante.

Vueltas: 1) 370 tris, 128 en los cuatro aisladores (campana de 3 anillos) · 2) aisladores como tronco de
cono de 6 lados: 322.

Revisión
- 322 triángulos el poste (+334 la variante, +96 de los 8 marcadores, que se borran al importar) contra
  200 de referencia: los dos tallados del quiebre en zigzag y la mella (~60), la cruceta con riostras,
  clavijas y aisladores (164).
- frag02 (el tramo de arriba) es el 55,5 % del volumen: el Bloque C pide <= 45 %, pero el prompt fija el
  quiebre a 1/3 del alto, así que el tramo de arriba siempre es ~2/3 del poste. Se respetó el prompt;
  para cumplir el 45 % el quiebre tendría que estar a ~0,45 del alto (decide Valentin).
- Medidas: 16 de alto, cruceta 5 de ancho, poste 0,6 entre caras. La variante mide 15,7 de alto.
"""

import math

from mathutils import Euler, Vector

H = 16.0
R = 0.3 / math.cos(math.radians(22.5))     # 8 lados con 0,6 entre caras
SNAP = H / 3
ARM_Y, ARM_H, ARM_Z = 14.9, 0.4, (-0.7, -0.3)
INS_X = (-2.15, -1.05, 1.05, 2.15)
LEAN = 12.0
LEAN_X = 7.0
ZIG = [(-0.45, 0.18), (-0.22, -0.14), (0.0, 0.22), (0.22, -0.12), (0.45, 0.16)]


def build_pole(mk, prefix, x0, lean):
    E = Euler((math.radians(lean), 0, 0), "XYZ").to_matrix()
    base = Vector((x0, 0, 0))

    def P(p):
        return tuple(base + E @ Vector(p))

    def PP(pts):
        return [P(p) for p in pts]

    rot = (lean, 0, 0)

    def prism_cut(part, profile, mat):
        mk.carve(part, mat, prism=dict(profile=profile, depth=1.2, plane="xy", center=P((0, 0, 0)), rot=rot))

    zig = [(x, SNAP + dy) for x, dy in ZIG]
    gouge = PP(mk.pts_box((0, SNAP, -0.33), (0.34, 0.3, 0.3), rot=(45, 0, 0)))

    # ---- tramo de abajo ----
    lo = mk.part(f"{prefix}frag01", (x0, 0, 0))
    mk.hull(lo, PP(mk.pts_cyl((0, (SNAP + 0.5) / 2, 0), R, SNAP + 0.5, sides=8)), "wood_mid")
    prism_cut(lo, zig + [(0.45, SNAP + 1.0), (-0.45, SNAP + 1.0)], "wood_light")
    mk.carve(lo, "wood_light", points=gouge)
    if lean:                                                       # base plana en el piso
        mk.carve(lo, "wood_mid", points=mk.pts_box((x0, -0.5, 0), (2, 1.0, 4)))

    # ---- tramo de arriba con el sombrerete ----
    up = mk.part(f"{prefix}frag02", (x0, 0, 0))
    y0, y1 = SNAP - 0.5, H - 0.2
    mk.hull(up, PP(mk.pts_cyl((0, (y0 + y1) / 2, 0), R, y1 - y0, sides=8)), "wood_mid")
    mk.hull(up, PP(mk.pts_cyl((0, H - 0.11, 0), R * 0.999, 0.22, sides=8, top=0.4)), "wood_mid")
    prism_cut(up, zig[::-1] + [(-0.45, SNAP - 1.0), (0.45, SNAP - 1.0)], "wood_light")
    mk.carve(up, "wood_light", points=gouge)

    # ---- cruceta con riostras, clavijas y aisladores ----
    arm = mk.part(f"{prefix}frag03", (x0, 0, 0))
    zc = (ARM_Z[0] + ARM_Z[1]) / 2
    mk.hull(arm, PP(mk.pts_box((0, ARM_Y, zc), (5.0, ARM_H, ARM_Z[1] - ARM_Z[0]))), "wood_mid")
    for s in (-1, 1):                                              # riostras: de la cruceta a la cara del poste
        top, bot = ARM_Y - ARM_H / 2 + 0.03, ARM_Y - 1.25
        pts = [(s * xx + dx, y, z) for y, xx in ((top, 1.6), (bot, 0.1)) for dx in (-0.06, 0.06)
               for z in (-0.44, -0.3)]
        mk.hull(arm, PP(pts), "wood_dark")
    top = ARM_Y + ARM_H / 2
    for i, x in enumerate(INS_X):
        mk.hull(arm, PP(mk.pts_box((x, top + 0.12, zc), (0.12, 0.3, 0.12))), "wood_dark")   # clavija
        # campana como tronco de cono de 6 lados: a 15 de altura no se distingue un perfil de 3 anillos
        # (costaba 32 tris cada uno, vuelta 1)
        mk.hull(arm, PP(mk.pts_cyl((x, top + 0.335, zc), 0.17, 0.33, sides=6, top=0.45)), "glass_green", detail=True)
        name = f"_{prefix}Wire_{i + 1}" if prefix else f"_Wire_{i + 1}"
        mk.marker(name, P((x, top + 0.33, zc)))


def build(mk):
    build_pole(mk, "", 0.0, 0.0)
    build_pole(mk, "TelegraphPole_Leaning_", LEAN_X, LEAN)

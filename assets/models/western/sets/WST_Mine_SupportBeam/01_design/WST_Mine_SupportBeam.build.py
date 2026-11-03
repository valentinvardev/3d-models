"""
Receta de WST_Mine_SupportBeam, el puntal que se derrumba y un jugador sostiene (prompt 101, Bloques A + C).

Brief
- Lo que se lee: un puntal de túnel (el de WST_Mine_Tunnel) con el poste izquierdo partido: el sombrero
  cuelga en diagonal desde el poste derecho hasta 5 de alto a la izquierda, con dos piedras encima a
  punto de caer; el poste partido muestra la astilla clara (madera fresca) en la rotura.
- Medidas: el puntal de las puntas de los túneles (perfil PC): poste derecho de y 0 a 6,65 apoyado contra
  la pared (centro x 3,62 abajo, 3,10 arriba), sombrero de 0,6 x 0,6 x 6,97. El sombrero gira 13,8° sobre
  su punta derecha (pivote en x 3,2, y 6,9): la punta izquierda queda con la cara de abajo a y ≈ 5,0. Al
  sostenerlo vuelve a horizontal (y 6,6-7,2), la posición del puntal sano.
- Piezas: CapBeam (origen en el pivote), fixed_PostRight (queda en pie; lleva la chapa de hierro de la
  unión), frag01 muñón de abajo del poste izquierdo (hasta ~2,0, con la rotura en zigzag), frag02 el pedazo
  de arriba (astillado abajo, patea 0,45 hacia adentro y queda apoyado bajo la punta del sombrero),
  frag03 y frag04 las dos piedras sobre el sombrero. Marcador _HoldPoint bajo la punta, a 4,5.
- Inferido: el ángulo exacto (cara de abajo de la punta a 5,0), el pivote sobre el poste derecho, el pedazo
  de arriba apoyado y no tirado en el piso, el lugar de las piedras, la chapa de hierro, el origen del
  modelo en el piso al centro del túnel (como WST_Mine_Tunnel).

Vueltas: 1) el muñón no tocaba nada (el piso es del túnel): una astilla larga del lado de adentro sube
0,75 y se clava en el pedazo de arriba · 2) piedras más grandes (a 40 studs eran puntitos).

Revisión
- ~200 triángulos contra 300: el modelo es eso (cuatro vigas, dos piedras, la chapa). No se agregó detalle
  que no pida el prompt.
- Medidas: 7,8 de ancho (el puntal de los túneles), 7,3 de alto con las piedras; la cara de abajo de la
  punta del sombrero a 5,0; _HoldPoint a 4,5. Fragmentos (medidos): muñón 24,4 %, pedazo de arriba 29,5 %,
  piedras 29,7 % y 16,5 % del volumen; el lado más chico de todos, 0,60 (los postes).
- El punto más bajo (-0,05) es el pie de los postes, metido en el piso del túnel (como en WST_Mine_Tunnel).
- Al sostenerlo, CapBeam gira -13,8° sobre su pivote y queda donde va el sombrero del puntal sano.
"""

import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "mine_tunnel", Path(__file__).resolve().parents[2] / "WST_Mine_Tunnel" / "01_design" / "WST_Mine_Tunnel.build.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

WOOD, FRESH, IRON = "wood_dark", "wood_light", "iron"
ROCK, ROCK2 = "stone_grey", "redrock_dark"
W = T.TIMBER                                       # 0,6
PIVOT = (3.2, 6.9)
CAP_L, CAP_R = T.wall_x(T.PC, T.CAP_Y0, -1) - 0.15, T.wall_x(T.PC, T.CAP_Y0, 1) + 0.15
TH = math.radians(13.8)


def rot_pivot(x, y):
    """Punto del sombrero en reposo -> caído (giro de TH alrededor del pivote, la punta izquierda baja)."""
    dx, dy = x - PIVOT[0], y - PIVOT[1]
    c, s = math.cos(TH), math.sin(TH)
    return PIVOT[0] + dx * c - dy * s, PIVOT[1] + dx * s + dy * c


def cap_top(x):
    """Altura de la cara de arriba del sombrero caído en x."""
    return T.CAP_Y1 - (PIVOT[0] - x) * math.tan(TH) + (T.CAP_Y1 - PIVOT[1]) * (1 / math.cos(TH) - 1)


def build(mk):
    # ---------------- poste derecho (queda en pie) ----------------
    pr = mk.part("fixed_PostRight", (0, 0, 0))
    T.timber_set(mk, pr, T.straight_frame(0, 0.0), T.PC, 0, posts=(1,), cap=False)
    mk.box(pr, (3.42, 6.3, -0.33), (0.75, 0.62, 0.05), IRON)                       # chapa de la unión
    for y in (6.12, 6.5):
        mk.cyl(pr, (3.42, y, -0.37), 0.07, 0.06, IRON, axis="z", sides=6)

    # ---------------- sombrero caído (pivote en su punta derecha) ----------------
    cb = mk.part("CapBeam", (PIVOT[0], PIVOT[1], 0))
    pts = []
    for x in (CAP_L, CAP_R):
        for y in (T.CAP_Y0, T.CAP_Y1):
            px, py = rot_pivot(x, y)
            for z in (-W / 2 - 0.02, W / 2 + 0.02):
                pts.append((px, py, z))
    mk.hull(cb, pts, WOOD)
    # rajadura a lo largo de la cara (franja oscura tallada poco profunda, del lado de la punta caída)
    a, b = rot_pivot(-2.4, 6.98), rot_pivot(0.4, 7.02)
    mk.carve(cb, "wood_charred", prism=dict(profile=[(a[0], a[1] - 0.03), (b[0], b[1] - 0.02), (b[0], b[1] + 0.02),
                                                     (a[0], a[1] + 0.04)], depth=0.06, plane="xy",
                                            center=(0, 0, -W / 2 - 0.02)))

    # ---------------- poste izquierdo partido ----------------
    xb = T.wall_x(T.PC, 0.6, -1) + (W / 2 - 0.06)          # centro abajo (como en el puntal sano)
    xt = T.wall_x(T.PC, T.CAP_Y0, -1) + (W / 2 - 0.06)
    lean = (xt - xb) / T.CAP_Y0

    def xc(y):
        return xb + lean * y

    yb = 2.0
    # (x local, y sobre yb): una astilla larga del lado de adentro sube 0,75 y se clava en el pedazo de arriba
    zig = [(0.3, 0.0), (0.22, 0.75), (0.05, 0.1), (-0.12, 0.32), (-0.3, 0.05)]
    stub = [(xc(-0.05) - 0.3, -0.05), (xc(-0.05) + 0.3, -0.05)] + [(xc(yb) + dx, yb + dy) for dx, dy in zig]
    f1 = mk.part("frag01", (0, 0, 0))
    mk.prism(f1, stub, W, WOOD, plane="xy", center=(0, 0, 0))
    mk.paint(f1, FRESH, box=((xc(yb), yb + 0.4, 0), (0.8, 0.9, 0.7)))
    # pedazo de arriba: astillado abajo (el negativo del muñón, más largo), corrido 0,45 hacia adentro y
    # apoyado contra la cara de abajo del sombrero caído
    kick = 0.45
    top_y = cap_top(xc(4.9) + kick) - W / math.cos(TH) + 0.03
    up = [(xc(yb + 0.35) + kick + dx, yb + 0.35 + dy) for dx, dy in [(-0.3, 0.08), (-0.14, -0.22), (0.0, 0.12),
                                                                      (0.14, -0.3), (0.3, 0.02)]]
    up += [(xc(top_y) + 0.3, top_y - 0.1), (xc(top_y) - 0.3, top_y + 0.06)]
    f2 = mk.part("frag02", (0, 0, 0))
    mk.prism(f2, up, W, WOOD, plane="xy", center=(0, 0, 0.02))
    mk.paint(f2, FRESH, box=((xc(yb) + kick, yb + 0.3, 0), (0.8, 0.5, 0.7)))

    # ---------------- piedras sobre el sombrero ----------------
    for name, x, size, seed, mat in (("frag03", -1.6, (1.55, 0.95, 1.15), 301, ROCK), ("frag04", 0.6, (1.15, 0.8, 1.0), 302, ROCK2)):
        f = mk.part(name, (0, 0, 0))
        y = cap_top(x) + size[1] * 0.3
        T.chunk(mk, f, (x, y, 0.05), size, seed, rot=(0, 30, math.degrees(TH)), mat=mat, detail=False)

    tip = rot_pivot(CAP_L + 0.5, T.CAP_Y0)
    mk.marker("_HoldPoint", (tip[0] + 0.2, 4.5, 0))

"""
Receta de WST_Kit_Porch, el porche del kit modular (prompt 011, Bloques A + C).

Brief
- Silueta a 40 studs: vereda de tablas levantada 1, techo de una sola agua con hileras de tejuelas
  escalonadas y viga oscura adelante, columna cuadrada con ménsulas, baranda de balaustres, escalones y
  palenque (poste + tronco) adelante.
- Módulo de 8 de ancho x 6 de fondo, delante de la pared (hacia -Z). Las piezas del porche se muestran
  armadas en x = 0: el fondo del porche (z = 0) es la cara de la pared. Baranda en x = 12 y palenque en
  x = 22, sueltos.
- Orígenes (inferidos, el prompt solo fija el de la columna): Porch_Floor y Porch_Roof comparten origen
  en el piso bajo el centro del porche (x = 0, y = 0, z = -3): con el mismo CFrame quedan armados.
  Porch_Step: en el piso, al centro de su borde de atrás (z = -6,1, contra el faldón). Porch_Column: en
  su base (prompt). Porch_Railing y Porch_HitchRail: abajo al centro (Bloque A).
- Porch_Floor (6 fragmentos, 2 tablas cada uno): 12 tablas de 8 x 0,5 x 0,4 a lo largo de X (arriba en
  y = 1,0), wood_mid con tablas wood_light salteadas, sobre 4 largueros wood_dark (x = ±1, ±3) que van en Z, y
  faldón wood_dark adelante. Una tabla rota con agujero.
- Porch_Roof (4 fragmentos, franjas de 2 en X): una sola agua de 10 (contra la pared) a 9 (adelante),
  8 x 6,5; 13 hileras de tejuelas wood_dark de 0,5 con escalón de 0,06; entablonado wood_mid abajo
  (se ve desde el porche), cabios cada 2 que apoyan en un listón contra la pared y viga adelante
  (z -6,0..-5,45, abajo en y = 8,27). Dos tejuelas faltantes.
- Porch_Column (3 fragmentos): poste 0,5 x 0,5, basa y capitel wood_dark, dos ménsulas
  triangulares arriba hacia ±X debajo de la viga. Se parte a 1/3 y 2/3 con cortes en zigzag (cara wood_light).
- Porch_Step (2 fragmentos): 3 de ancho, dos escalones (huellas a 0,7 y 0,4: la de abajo de 0,4 por la
  regla de fragmentos de 0,4), zancas oscuras.
- Porch_Railing (4 fragmentos): 8 x 3, pasamanos wood_dark de 0,4 x 0,3, travesaño de abajo, 10 balaustres
  wood_light cada 0,8 (uno roto y uno que falta). Cortes en x = -1,6, 0, 1,6 (entre balaustres).
- Porch_HitchRail (2 fragmentos): dos postes redondos y un tronco de 8; el tronco se parte en zigzag al medio.
- Nombres: <Pieza>_fragNN (como el resto del kit).
- Inferido: orígenes del piso, techo, escalón; espesores (tablas 0,4 por la regla de fragmentos),
  largueros, listón, ménsulas triangulares, alturas de los escalones, colores de baranda y palenque.
- Contradicción del prompt: la columna "9 de alto, del piso del porche al techo" no entra: con el piso a
  1,0 y el techo a 9 adelante (más la viga que pide), la columna va de 1,0 a 8,27 = 7,27. Decide Valentin
  si prefiere otro alto de techo.

Vueltas: 1) primera versión: la columna con chanflán sobre cajas encimadas (poste, capitel, ménsulas)
dejaba un borde con giro invertido y bordes abiertos -> sin chanflán · 2) tablas del piso claras salteadas
(alternadas perfectas se leían como cebra) · 3) baranda apoyada en y = 0 (el travesaño de abajo
flotaba 0,25 sobre el piso).

Revisión
- Triángulos contra 400 por pieza: Floor 668 (6 fragmentos con largueros y faldón), Roof 758 (13 hileras
  escalonadas, entablonado, cabios, listón y viga, en 4 fragmentos), Column 194, Step 48, Railing 368,
  HitchRail 248. Calidad primero: piso y techo se ven de cerca (se pelea en el porche y desde los techos).
- Medidas: piso 8 x 1 x 6,1 (faldón 0,1 adelante); techo 8 x 6,5, de 10 a 9 (más 0,06 de escalón);
  columna 7,27 (ver la contradicción arriba); escalones 3 x 1,2; baranda 8 x 3 (apoya en y = 0);
  palenque 8 x 3.
- Fragmentos: con 2 fragmentos (escalón 64/36, palenque 50/50) la regla del 45 % no se puede cumplir;
  el resto queda por debajo (el mayor, 37 % en la columna). Todos de 0,4 o más.
- Normales del GLB final: 0 esquinas desviadas.
"""

import math

MID, LIGHT, DARK, IRON = "wood_mid", "wood_light", "wood_dark", "iron"


def Y(z):
    """Superficie del techo (sin escalones): 10 contra la pared (z = 0), 9 adelante (z = -6,5)."""
    return 10.0 + z / 6.5


DECK = 0.35                                   # tejuela + entablonado
BEAM = (-6.0, -5.45)                          # z de la viga de adelante
BEAM_BOT = Y(sum(BEAM) / 2) - DECK - 0.5      # 8,27: la columna llega hasta acá


def clean(pts):
    out = []
    for p in pts:
        if not out or abs(out[-1][0] - p[0]) > 1e-6 or abs(out[-1][1] - p[1]) > 1e-6:
            out.append(p)
    return out


# ---------------------------------------------------------------------------------------------- piso
def porch_floor(mk):
    org = (0, 0, -3)
    for f in range(6):
        za, zb = -6.0 + f, -5.0 + f                         # del frente (f = 0) hacia la pared
        p = mk.part(f"Porch_Floor_frag0{f + 1}", org)
        mk.box(p, (0, 0.8, (za + zb) / 2), (8.0, 0.4, 1.0), MID)                         # dos tablas
        for x in (-3, -1, 1, 3):
            mk.box(p, (x, 0.31, (za + zb) / 2), (0.3, 0.62, 1.0), DARK)                 # largueros
        if f == 0:
            mk.box(p, (0, 0.515, -6.025), (8.0, 0.93, 0.15), DARK)                      # faldón
        if f == 2:                                                                       # tabla rota
            hole = [(1.0, -4.05), (1.9, -4.05), (1.75, -3.75), (1.5, -3.85), (1.25, -3.62), (1.05, -3.8)]
            mk.carve(p, DARK, prism=dict(profile=hole, depth=1.0, plane="xz", center=(0, 0.8, 0)))
        elif f == 4:                                                                     # canto comido
            mk.carve(p, LIGHT, prism=dict(profile=[(-2.6, -1.1), (-1.7, -1.1), (-2.0, -0.9), (-2.4, -0.95)],
                                          depth=0.2, plane="xz", center=(0, 1.0, 0)))
        else:                                                                            # sin efecto: une los cascos
            mk.carve(p, DARK, points=mk.pts_box((0, -2, 0), (0.1, 0.1, 0.1)))
        mk.slice(p, (0, 0, (za + zb) / 2), (0, 0, 1))                                    # junta entre las dos tablas
        light = ("back", None, "front", "back", None, "front")[f]                        # tablas claras salteadas
        if light:
            zc = (zb + (za + zb) / 2) / 2 if light == "back" else (za + (za + zb) / 2) / 2
            mk.paint(p, LIGHT, box=((0, 0.8, zc), (8.2, 0.42, 0.5)))
        else:                                                                            # junta oscura si son iguales
            for d in (-0.03, 0.03):
                mk.slice(p, (0, 0, (za + zb) / 2 + d), (0, 0, 1))
            mk.paint(p, DARK, box=((0, 1.0, (za + zb) / 2), (8.2, 0.02, 0.062)))


# --------------------------------------------------------------------------------------------- techo
def porch_roof(mk):
    org = (0, 0, -3)
    top = [(0.0, Y(0.0))]
    for i in range(13):
        z0, z1 = -0.5 * i, -0.5 * (i + 1)
        top += [(z0, Y(z0)), (z1, Y(z1) + 0.06)]
    shingles = clean(top + [(-6.5, Y(-6.5) - 0.12), (0.0, Y(0.0) - 0.12)])
    deck = [(0.0, Y(0.0) - 0.10), (-6.5, Y(-6.5) - 0.10), (-6.5, Y(-6.5) - DECK), (0.0, Y(0.0) - DECK)]
    for f in range(4):
        a, b = -4.0 + 2 * f, -2.0 + 2 * f
        cx = (a + b) / 2
        p = mk.part(f"Porch_Roof_frag0{f + 1}", org)
        mk.prism(p, shingles, b - a, DARK, plane="zy", center=(cx, 0, 0))               # tejuelas
        mk.prism(p, deck, b - a, MID, plane="zy", center=(cx, 0, 0))                    # entablonado
        rz0, rz1 = -0.25, BEAM[1]                                                        # cabio: del listón a la viga
        mk.hull(p, [(cx + dx, Y(z) - DECK + 0.02 - dy, z) for dx in (-0.12, 0.12) for z in (rz0 - 0.02, rz1 + 0.02)
                    for dy in (0.0, 0.34)], DARK)
        mk.box(p, (cx, Y(-0.12) - DECK - 0.24, -0.13), (b - a, 0.5, 0.26), DARK)         # listón contra la pared
        bz = sum(BEAM) / 2
        mk.box(p, (cx, BEAM_BOT + 0.26, bz), (b - a, 0.52, BEAM[1] - BEAM[0]), DARK)    # viga
        if f == 1:                                                                       # tejuelas que faltan
            mk.carve(p, MID, points=[(x, Y(z) + dy, z) for x in (-1.3, -0.7) for z in (-2.6, -3.5) for dy in (-0.11, 0.3)])
        elif f == 3:
            mk.carve(p, MID, points=[(x, Y(z) + dy, z) for x in (2.6, 3.1) for z in (-4.6, -5.1) for dy in (-0.11, 0.3)])
        else:
            mk.carve(p, DARK, points=mk.pts_box((cx, 20, 0), (0.1, 0.1, 0.1)))


# ------------------------------------------------------------------------------------------ columna
def porch_column(mk, cx, cz):
    base = 1.0                                     # arriba del piso del porche
    Hc = BEAM_BOT - base
    h1, h2 = Hc / 3, 2 * Hc / 3
    org = (cx, base, cz)

    def zig(h, up):
        pts = [(u, h + d) for u, d in ((-0.6, 0.1), (-0.3, -0.12), (-0.08, 0.14), (0.12, -0.1), (0.32, 0.12), (0.6, -0.06))]
        far = h + (20 if up else -20)
        return pts + [(0.6, far), (-0.6, far)]

    def cut(p, h, up):
        mk.carve(p, LIGHT, prism=dict(profile=zig(h, up), depth=1.2, plane="xy", center=(cx, base, cz), rot=(0, 35, 0)))

    spans = [(0.0, h1 + 0.4), (h1 - 0.4, h2 + 0.4), (h2 - 0.4, Hc)]
    for i, (y0, y1) in enumerate(spans):
        p = mk.part(f"Porch_Column_frag0{i + 1}", org)
        mk.box(p, (cx, base + (y0 + y1) / 2, cz), (0.5, y1 - y0, 0.5), MID)            # poste
        if i == 0:
            mk.box(p, (cx, base + 0.15, cz), (0.7, 0.3, 0.7), DARK, top=(0.86, 0.86))     # basa
        if i == 2:
            mk.box(p, (cx, base + Hc - 0.13, cz), (0.68, 0.26, 0.68), DARK)              # capitel
            for s in (-1, 1):                                                            # ménsulas
                tri = [(cx + s * 0.24, base + Hc), (cx + s * 1.0, base + Hc), (cx + s * 0.24, base + Hc - 0.76)]
                mk.prism(p, tri, 0.2, DARK, plane="xy", center=(0, 0, cz))
        if i > 0:
            cut(p, h1 if i == 1 else h2, False)
        if i < 2:
            cut(p, h1 if i == 0 else h2, True)


# --------------------------------------------------------------------------------------- escalones
def porch_step(mk):
    org = (0, 0, -6.1)
    for i, (h, za, zb) in enumerate(((0.7, -6.7, -6.1), (0.4, -7.3, -6.7))):
        p = mk.part(f"Porch_Step_frag0{i + 1}", org)
        mk.box(p, (0, h / 2, (za + zb) / 2), (3.0, h, zb - za), MID)
        mk.slice(p, (0, 0, (za + zb) / 2), (0, 0, 1))
        mk.paint(p, LIGHT, box=((0, h, (za * 3 + zb) / 4), (3.2, 0.02, (zb - za) / 2)))   # tabla de adelante de la huella
        for s in (-1, 1):
            mk.paint(p, DARK, box=((s * 1.5, h / 2, (za + zb) / 2), (0.02, h + 0.1, 1.0)))  # zancas
        mk.paint(p, DARK, box=((0, h / 2, za), (3.2, h + 0.1, 0.02)))                      # contrahuella
        if i == 0:                                                                          # canto gastado
            mk.carve(p, MID, prism=dict(profile=[(-0.5, -6.8), (0.6, -6.8), (0.4, -6.6), (-0.3, -6.62)],
                                        depth=0.12, plane="xz", center=(0, h, 0)))


# ----------------------------------------------------------------------------------------- baranda
def porch_railing(mk, ox):
    cuts = [-4.0, -1.6, 0.0, 1.6, 4.0]
    balusters = [-3.6 + 0.8 * k for k in range(10)]
    for f in range(4):
        a, b = cuts[f], cuts[f + 1]
        p = mk.part(f"Porch_Railing_frag0{f + 1}", (ox, 0, 0))
        mk.box(p, (ox + (a + b) / 2, 2.85, 0), (b - a, 0.3, 0.4), DARK, top=(1.0, 0.7))   # pasamanos
        mk.box(p, (ox + (a + b) / 2, 0.15, 0), (b - a, 0.3, 0.3), MID)                    # travesaño de abajo, apoyado en el piso
        for x in balusters:
            if not a < x < b or abs(x + 1.2) < 1e-6:          # el de x = -1,2 falta
                continue
            if abs(x + 0.4) < 1e-6:                            # roto: muñón abajo y astilla arriba
                mk.hull(p, [(ox + x + dx, y, dz) for dx in (-0.1, 0.1) for dz in (-0.1, 0.1) for y in (0.25, 1.3)]
                        + [(ox + x + 0.05, 1.75, 0.0)], LIGHT)
                mk.hull(p, [(ox + x + dx, y, dz) for dx in (-0.1, 0.1) for dz in (-0.1, 0.1) for y in (2.75, 2.3)]
                        + [(ox + x - 0.04, 2.0, 0.02)], LIGHT)
                continue
            mk.box(p, (ox + x, 1.5, 0), (0.2, 2.5, 0.2), LIGHT)                         # balaustre
        mk.carve(p, MID, points=mk.pts_box((ox + a + 0.5, 3.0, -0.2), (0.35, 0.1, 0.12), rot=(0, 0, 8)))  # canto gastado


# ---------------------------------------------------------------------------------------- palenque
def hitch_rail(mk, ox):
    for f, s in enumerate((-1, 1)):
        p = mk.part(f"Porch_HitchRail_frag0{f + 1}", (ox, 0, 0))
        mk.cyl(p, (ox + s * 3.5, 1.5, 0), 0.25, 3.0, MID, sides=8, top=0.85)              # poste
        x0, x1 = (ox - 4.0, ox + 0.6) if s < 0 else (ox - 0.6, ox + 4.0)
        mk.cyl(p, ((x0 + x1) / 2, 2.55, 0), 0.22, x1 - x0, MID, axis="x", sides=8)        # tronco
        # quebradura en zigzag que cruza el tronco de abajo arriba; cada mitad talla el lado del otro
        crack = [(-0.3, 2.1), (0.05, 2.38), (-0.12, 2.5), (0.2, 2.62), (0.0, 2.72), (0.3, 3.0)]
        side = 1.5 if s < 0 else -1.5
        prof = [(ox + u, y) for u, y in crack] + [(ox + side, 3.0), (ox + side, 2.1)]
        mk.carve(p, LIGHT, prism=dict(profile=prof, depth=1.0, plane="xy"))
        mk.paint(p, LIGHT, box=((ox + s * 4.0, 2.55, 0), (0.02, 0.5, 0.5)))              # punta del tronco aserrada
        mk.paint(p, LIGHT, box=((ox + s * 3.5, 3.0, 0), (0.6, 0.02, 0.6)))               # tope del poste


def build(mk):
    porch_floor(mk)
    porch_roof(mk)
    porch_column(mk, 3.0, sum(BEAM) / 2)
    porch_step(mk)
    porch_railing(mk, 12.0)
    hitch_rail(mk, 22.0)

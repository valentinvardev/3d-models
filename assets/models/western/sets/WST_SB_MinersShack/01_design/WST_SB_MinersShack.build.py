"""
Receta de WST_SB_MinersShack, la casilla del minero pobre de Silver Bend (prompt 110, Bloques A + C).

Brief
- Silueta a 40 studs: caja baja de tablas verticales sin pintar, torcida (fuera de escuadra), con techo de
  una sola agua que baja hacia atrás y vuela adelante sobre un porchecito, un parche de chapa oxidada y el
  caño de la estufa saliendo del techo. Puerta de tablas con Z y ventana con cortina de lona.
- Planta 12 (X) x 10 (Z), paredes de 0,4. Frente (-Z) de 8 de alto, atrás 6,66; los costados siguen el
  techo (pendiente 0,14, ~8°). Más baja que el kit (10): lado pobre.
- Torcida 2° fuera de escuadra: todo se corre en X con la altura (x += y * tan 2°, 0,28 arriba): frente y
  fondo son paralelogramos y los costados se inclinan 2° (corte en vez de giro: las esquinas no se abren).
- Tablas verticales de 0,8: el color de cada tabla (wood_mid / wood_light, alguna wood_dark) marca las
  juntas (Bloque A, alternar colores); adentro se ve la misma tabla.
- Paredes (8 fragmentos cada una, por columnas de tablas y una quebradura en zigzag a media altura):
  WallFront_frag01..08 (puerta de 4 x 7,5 del kit en x -3,6..0,4, ventana de 2,4 x 2,4 en x 2..4,4 y
  3,4..5,8; ningún fragmento rodea un hueco), WallBack_, WallLeft_, WallRight_frag01..08.
- Techo: Roof_frag01..06, 16 tablas de 0,81 que bajan por la pendiente (largos disparejos ±0,15, una de
  cada dos hundida 0,025 arriba y abajo, colores mezclados), alero de 1,8 adelante (cubre el porche) y
  0,5 atrás y a los costados. Parche de chapa acanalada rust sobre el fragmento 4; caño de estufa de hierro
  con collarín y sombrerete sobre el fragmento 1.
- Door: puerta de tablas estilo Door_Plank (5 tablas, Z oscura, bisagras de pletina, pestillo), 3,96 x
  7,42, origen en el pie del canto de las bisagras (izquierda) en el plano medio de la pared.
- Porch: tarima de 6 x 0,3 x 2,2 delante de la puerta (tres tablas). CrateSeat: cajón de 1,3 x 1,2 x 1,3
  para sentarse. Dos jabalcones en las paredes sostienen el alero.
- Ventana: cortina de lona colgada de una varilla por adentro, corrida 2/3 (se ve desde afuera).
- Inferido: altura de atrás (6,66), alero del porche, ventana en el frente, tamaños de puerta (la del kit)
  y ventana, tablas verticales, cortes de fragmentos, chapa y caño sobre el techo, nombres (WallFront_...,
  Roof_..., Door, Porch, CrateSeat), sin piso (tierra).

Vueltas: 1) primera versión: pasa la revisión, pero las quebraduras en zigzag no se veían (fragmentos con
luz cero: solo las marcaba el contorno de Blender) y el parche de chapa (1,5 x 3, rust casi del mismo
valor que wood_mid) se perdía · 2) el fragmento de arriba de cada quebradura sale 0,06 hacia afuera (el
escalón marca la grieta en las cuatro paredes, sin triángulos extra) y la chapa pasó a 2,2 x 4,2 con
canaletas de 0,1 sobre el fragmento 5.

Revisión
- 1982 triángulos contra 1200 (+65 %): son 38 fragmentos cerrados (32 de pared + 6 de techo, ~1240 entre
  todos) más la puerta con su herraje (176), el cajón (118), la chapa acanalada y el caño. Cada tabla de
  color distinto suma sus bordes; las juntas van por color (un corte por junta), no con franjas oscuras.
- Medidas: 13,1 x 10,0 x 12,9 con el techo (alero de 1,8 adelante); caja de paredes 12 x 10, frente 8 y
  atrás 6,66 de alto. La torcedura baja el pie de las paredes de costado 0,007 bajo y = 0.
- Puerta: hueco de 4 x 7,5 del kit (deja un dintel de 0,5: la pared es de 8); hoja de 3,96 x 7,42 con
  luz de 0,02, origen en el pie de las bisagras. El jugador (2 x 5) pasa con 2 de sobra.
- Fragmentos: 8 por pared y 6 de techo, todos de 0,4 de espesor como mínimo; los de pared siguen las
  juntas de las tablas y ninguno rodea la puerta o la ventana. Los de arriba de cada quebradura salen
  0,06 (el escalón): siguen en contacto con el de abajo en 0,34 de los 0,4.
- Adentro: las mismas tablas (mismos colores), la cortina en su varilla y el caño que asoma 0,15 bajo el
  techo. Sin piso (va sobre el terreno).
- Materiales: 6 (wood_mid, wood_light, wood_dark, rust, canvas, iron).
"""

import math

MID, LIGHT, DARK, RUST, CANVAS, IRON = "wood_mid", "wood_light", "wood_dark", "rust", "canvas", "iron"
K = math.tan(math.radians(2.0))      # fuera de escuadra
T = 0.4                              # espesor de pared
XO, ZO = 6.0, 5.0                    # medio ancho y medio fondo (cara de afuera)
H_FRONT, H_BACK = 8.0, 6.66
SL = 0.14                            # pendiente del techo
BW = 0.8                             # ancho de tabla
DOOR = (-3.6, 0.4, 7.5)
WIN = (2.0, 4.4, 3.4, 5.8)


def SH(p):
    return (p[0] + K * p[1], p[1], p[2])


def yr(z):
    """Cara de abajo del techo."""
    return H_FRONT - SL * (z + ZO)


def H(mk, part, pts, mat, detail=False):
    mk.hull(part, [SH(p) for p in pts], mat, detail)


def B(mk, part, c, s, mat, detail=False, rot=(0, 0, 0)):
    H(mk, part, mk.pts_box(c, s, rot), mat, detail)


def colors(n, seed):
    pat = (MID, LIGHT, MID, MID, LIGHT, DARK, LIGHT, MID, LIGHT, LIGHT, MID, MID, LIGHT, MID, DARK, MID, LIGHT)
    return [pat[(i * 7 + seed * 3) % len(pat)] for i in range(n)]


def zig(u0, u1, h0, h1, amp, phase=0):
    """Quebradura de u0 a u1: vértices cada 0,4 (en las juntas y el medio de las tablas), alto de h0 a h1."""
    n = max(2, round((u1 - u0) / 0.4))
    pts = []
    for i in range(n + 1):
        t = i / n
        d = amp * (1 if (i + phase) % 2 else -1) * (0.5 if i in (0, n) else 1.0)
        pts.append((u0 + (u1 - u0) * t, h0 + (h1 - h0) * t + d))
    return pts


class Wall:
    """Una pared en 2D (u a lo largo, v arriba). kind: 'front'/'back' (u = x, corte en el plano) o 'left'/'right'
    (u = z, inclinada 2°)."""

    def __init__(self, mk, name, kind, top, seed):
        self.mk, self.name, self.kind, self.top, self.seed = mk, name, kind, top, seed
        self.n = 0
        if kind in ("front", "back"):
            self.zc = (-ZO + T / 2) if kind == "front" else (ZO - T / 2)
            self.u0, self.u1 = -XO, XO
        else:
            self.xc = (-XO + T / 2) if kind == "left" else (XO - T / 2)
            self.u0, self.u1 = -ZO + T, ZO - T
        self.cols = colors(int(round((self.u1 - self.u0) / BW)) + 1, seed)

    def board(self, u):
        return int((u - self.u0) // BW)

    def frag(self, poly, out=0.0):
        """out: cuánto sale el fragmento hacia afuera (el de arriba de una quebradura: el escalón la marca)."""
        mk = self.mk
        self.n += 1
        p = mk.part(f"{self.name}_frag{self.n:02d}", (0, 0, 0))
        sgn = -1 if self.kind in ("front", "left") else 1
        if self.kind in ("front", "back"):
            prof = [(u + K * v, v) for u, v in poly]
            mk.prism(p, prof, T, MID, plane="xy", center=(0, 0, self.zc + sgn * out))
        else:
            mk.prism(p, poly, T, MID, plane="zy", center=(self.xc + sgn * out, 0, 0), rot=(0, 0, -2.0))
        us = [u for u, _ in poly]
        vs = [v for _, v in poly]
        ua, ub, va, vb = min(us), max(us), min(vs), max(vs)
        vc = (va + vb) / 2
        # juntas: un corte por junta; el color de cada tabla las marca
        j0 = math.ceil((ua - self.u0) / BW - 1e-6)
        j1 = math.floor((ub - self.u0) / BW + 1e-6)
        for j in range(j0, j1 + 1):
            s = self.u0 + j * BW
            if ua + 1e-6 < s < ub - 1e-6:
                if self.kind in ("front", "back"):
                    mk.slice(p, (s, 0, 0), (1, -K, 0))
                else:
                    mk.slice(p, (0, 0, s), (0, 0, 1))
        for b in range(self.board(ua + 1e-6), self.board(ub - 1e-6) + 1):
            col = self.cols[b]
            if col == MID:
                continue
            uc = self.u0 + (b + 0.5) * BW
            if self.kind in ("front", "back"):
                mk.paint(p, col, box=((uc + K * vc, vc, self.zc), (0.6, vb - va + 0.2, 0.6)))
            else:
                mk.paint(p, col, box=((self.xc + K * vc, vc, uc), (0.6, vb - va + 0.2, 0.6)))
        return p

    def column(self, u0, u1, h0, h1, amp=0.35, phase=0):
        """Columna de tablas partida por una quebradura: dos fragmentos (abajo y arriba)."""
        zz = zig(u0, u1, h0, h1, amp, phase)
        bot = [(u0, 0.0), (u1, 0.0)] + list(reversed(zz))
        top = zz + [(u1, self.top(u1)), (u0, self.top(u0))]
        return self.frag(bot), self.frag(top, out=0.06)


def walls(mk):
    out = {}
    # ---------------- frente: puerta, ventana ----------------
    w = Wall(mk, "WallFront", "front", lambda u: H_FRONT, seed=0)
    a_bot, a_top = w.column(-XO, DOOR[0], 4.6, 3.8)                        # 01, 02: izquierda de la puerta
    hdr = w.frag([(DOOR[0], DOOR[2]), (DOOR[1], DOOR[2]), (DOOR[1], H_FRONT), (DOOR[0], H_FRONT)])   # 03: dintel
    w.column(DOOR[1], WIN[0], 3.6, 4.4, phase=1)                           # 04, 05: entre puerta y ventana
    under = w.frag([(WIN[0], 0.0), (WIN[1], 0.0), (WIN[1], WIN[2]), (WIN[0], WIN[2])])            # 06
    over = w.frag([(WIN[0], WIN[3]), (WIN[1], WIN[3]), (WIN[1], H_FRONT), (WIN[0], H_FRONT)])     # 07
    right = w.frag([(WIN[1], 0.0), (XO, 0.0), (XO, H_FRONT), (WIN[1], H_FRONT)])                  # 08
    out["front"] = dict(a_top=a_top, hdr=hdr, under=under, over=over, right=right)
    # ---------------- fondo ----------------
    w = Wall(mk, "WallBack", "back", lambda u: H_BACK, seed=1)
    for (u0, u1, h0, h1, ph) in ((-6.0, -2.8, 3.2, 3.9, 0), (-2.8, 0.4, 3.6, 2.9, 1), (0.4, 3.6, 3.1, 3.8, 0),
                                 (3.6, 6.0, 3.7, 3.3, 1)):
        w.column(u0, u1, h0, h1, phase=ph)
    # ---------------- costados (u = z, de adelante hacia atrás) ----------------
    for name, kind, seed, hs in (("WallLeft", "left", 2, ((4.2, 3.6), (3.5, 4.0), (3.8, 3.2), (3.4, 3.0))),
                                 ("WallRight", "right", 3, ((3.7, 4.3), (4.1, 3.4), (3.3, 3.7), (3.6, 2.9)))):
        w = Wall(mk, name, kind, lambda u: yr(u) + 0.03, seed=seed)
        cuts = [-4.6, -2.2, 0.2, 2.6, 4.6]
        for i in range(4):
            w.column(cuts[i], cuts[i + 1], hs[i][0], hs[i][1], phase=i % 2)
    return out


# --------------------------------------------------------------------------------------------- techo
ROOF_Z = (-ZO - 1.8, ZO + 0.5)
ROOF_X = (-XO - 0.5, XO + 0.5)
NB = 16
RW = (ROOF_X[1] - ROOF_X[0]) / NB
GROUPS = [(0, 3), (3, 6), (6, 9), (9, 11), (11, 14), (14, 16)]
ROOF_COLS = (MID, DARK, LIGHT, MID, MID, LIGHT, DARK, MID, LIGHT, MID, DARK, LIGHT, MID, MID, LIGHT, DARK)
ENDS = (0.1, -0.12, 0.05, 0.15, -0.05, 0.0, 0.12, -0.15, 0.08, -0.02, 0.14, -0.1, 0.0, 0.1, -0.08, 0.05)


def roof(mk):
    parts = []
    for g, (b0, b1) in enumerate(GROUPS):
        p = mk.part(f"Roof_frag{g + 1:02d}", (0, 0, 0))
        for b in range(b0, b1):
            xa, xb = ROOF_X[0] + b * RW, ROOF_X[0] + (b + 1) * RW
            if b > b0:
                xa -= 0.004                                       # se mete en la vecina del mismo fragmento
            rec = 0.025 if b % 2 else 0.0                         # una de cada dos, hundida arriba y abajo
            za = ROOF_Z[0] - ENDS[b]
            zb = ROOF_Z[1] + ENDS[(b + 5) % NB]
            pts = [(x, yr(z) + dy, z) for x in (xa, xb) for z in (za, zb) for dy in (rec, 0.4 - rec)]
            H(mk, p, pts, ROOF_COLS[b])
        parts.append(p)
    # chapa acanalada oxidada sobre las tablas 11-13 (fragmento 5)
    xc, zc, L, Wd = (ROOF_X[0] + 11 * RW + ROOF_X[0] + 14 * RW) / 2 + 0.05, 0.6, 4.2, 2.2
    prof = []
    n = 8
    for i in range(2 * n + 1):
        x = -Wd / 2 + Wd * i / (2 * n)
        prof.append((x, 0.1 if i % 2 else 0.0))
    prof += [(x, y - 0.045) for x, y in reversed(prof)]
    th = math.degrees(math.atan(SL))
    yc = yr(zc) + 0.4 - 0.005
    mk.prism(parts[4], prof, L, RUST, plane="xy", center=(xc + K * yc, yc, zc), rot=(th, 0, 0))
    # caño de estufa que sale por el fragmento 1, con collarín
    px, pz = ROOF_X[0] + 1.5 * RW, 3.0
    yt = yr(pz) + 0.4
    for c, r, ln, top in (((px, yt + 1.0, pz), 0.24, 3.1, 1.0), ((px, yt + 0.02, pz), 0.4, 0.3, 0.8),
                          ((px, yt + 2.6, pz), 0.45, 0.3, 0.25)):
        mk.hull(parts[0], [SH(q) for q in mk.pts_cyl(c, r, ln, sides=8, top=top)], IRON, detail=True)
    return parts


# --------------------------------------------------------------------------------------------- puerta
def door(mk):
    u0, u1, v0, v1 = DOOR[0] + 0.02, DOOR[1] - 0.02, 0.04, DOOR[2] - 0.04
    zc = -ZO + T / 2
    zf = zc - 0.15                                                 # cara de afuera de la puerta
    p = mk.part("Door", SH((u0, 0.0, zc)))
    mk.prism(p, [(u + K * v, v) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))], 0.3, MID, plane="xy",
             center=(0, 0, zc))
    pw = (u1 - u0) / 5
    for j in range(1, 5):
        mk.slice(p, (u0 + j * pw, 0, 0), (1, -K, 0))
    for j in (1, 3):                                               # tablas claras
        uc = u0 + (j + 0.5) * pw
        mk.paint(p, LIGHT, box=((uc + K * 3.7, 3.7, zc), (pw * 0.7, 8.0, 0.5)))
    for y in (1.1, 6.3):                                           # travesaños
        B(mk, p, ((u0 + u1) / 2, y, zf - 0.05), (u1 - u0 - 0.24, 0.55, 0.12), DARK, detail=True)
    diag = [(u0 + 0.35, 1.25), (u0 + 0.35, 1.95), (u1 - 0.35, 6.15), (u1 - 0.35, 5.45)]
    H(mk, p, [(u, v, zf - dz) for u, v in diag for dz in (-0.01, 0.1)], DARK, detail=True)
    for y in (1.1, 6.3):                                           # bisagras de pletina + nudos
        strap = [(u0, y - 0.12, 0), (u0 + 1.5, y - 0.06, 0), (u0 + 1.62, y, 0), (u0 + 1.5, y + 0.06, 0), (u0, y + 0.12, 0)]
        H(mk, p, [(u, v, zf - 0.105 - dz) for u, v, _ in strap for dz in (0.0, 0.06)], IRON, detail=True)
        H(mk, p, mk.pts_cyl((u0 - 0.02, y, zf - 0.05), 0.08, 0.5, sides=6), IRON, detail=True)
    B(mk, p, (u1 - 0.4, 3.6, zf - 0.04), (0.1, 0.55, 0.1), IRON, detail=True)              # tirador
    B(mk, p, (u1 - 0.25, 4.05, zf - 0.035), (0.45, 0.09, 0.09), IRON, detail=True)         # pestillo
    return p


# --------------------------------------------------------------------------------------- porche y cajón
def porch(mk, out):
    p = mk.part("Porch", (0, 0, 0))
    x0, x1, z0, z1 = -4.6, 1.4, -ZO - 2.2, -ZO
    mk.box(p, ((x0 + x1) / 2, 0.15, (z0 + z1) / 2), (x1 - x0, 0.3, z1 - z0), MID)
    for zc in (z0 + 0.733, z0 + 1.467):
        mk.slice(p, (0, 0, zc), (0, 0, 1))
    mk.paint(p, LIGHT, box=(((x0 + x1) / 2, 0.15, z0 + 1.1), (6.2, 0.4, 0.7)))
    mk.carve(p, DARK, prism=dict(profile=[(x0 - 0.1, z0 - 0.1), (x0 + 0.7, z0 - 0.1), (x0 + 0.45, z0 + 0.2),
                                          (x0 + 0.2, z0 + 0.15), (x0 - 0.1, z0 + 0.45)], depth=1.0, plane="xz",
                                 center=(0, 0.15, 0)))                    # esquina rota
    c = mk.part("CrateSeat", (0, 0, 0))
    cx, cz, s, h = 0.55, -ZO - 1.25, 1.3, 1.2
    mk.box(c, (cx, 0.3 + h / 2, cz), (s, h, s), LIGHT)
    for y in (0.3 + 0.16, 0.3 + h - 0.16):
        mk.slice(c, (0, y, 0), (0, 1, 0))
    for x in (cx - s / 2 + 0.16, cx + s / 2 - 0.16):
        mk.slice(c, (x, 0, 0), (1, 0, 0))
    for z in (cz - s / 2 + 0.16, cz + s / 2 - 0.16):
        mk.slice(c, (0, 0, z), (0, 0, 1))
    for y in (0.3 + 0.08, 0.3 + h - 0.08):                         # marco oscuro arriba y abajo
        mk.paint(c, DARK, box=((cx, y, cz), (s + 0.1, 0.15, s + 0.1)))
    for sx in (-1, 1):                                             # esquineros
        for sz in (-1, 1):
            mk.paint(c, DARK, box=((cx + sx * (s / 2 - 0.08), 0.3 + h / 2, cz + sz * (s / 2 - 0.08)), (0.161, h, 0.161)))
    # jabalcones del alero, en las paredes del frente
    for part, x in ((out["a_top"], -5.4), (out["right"], 5.4)):
        z1 = -ZO - 1.4
        pts = [(x + dx, y, z) for dx in (-0.13, 0.13) for (y, z) in ((5.9, -ZO + 0.05), (6.25, -ZO + 0.05),
                                                                     (yr(z1) + 0.05, z1), (yr(z1) + 0.05, z1 + 0.4))]
        H(mk, part, pts, DARK, detail=True)
    # cortina de lona por adentro de la ventana, colgada de una varilla
    over = out["over"]
    zi = -ZO + T                                                   # cara de adentro
    H(mk, over, mk.pts_box(((WIN[0] + WIN[1]) / 2, WIN[3] + 0.17, zi + 0.055), (WIN[1] - WIN[0] + 0.5, 0.1, 0.12)),
      DARK, detail=True)
    folds = []
    n = 8
    for i in range(n + 1):
        x = WIN[0] - 0.1 + 1.75 * i / n
        folds.append((x, zi + 0.06 + (0.07 if i % 2 else 0.0)))
    prof = folds + [(x, z + 0.05) for x, z in reversed(folds)]
    yc = (WIN[2] + 0.1 + WIN[3] + 0.2) / 2
    mk.prism(over, [(x + K * yc, z) for x, z in prof], WIN[3] + 0.2 - WIN[2] - 0.1, CANVAS, plane="xz",
             center=(0, yc, 0), detail=True)


def build(mk):
    out = walls(mk)
    roof(mk)
    door(mk)
    porch(mk, out["front"])

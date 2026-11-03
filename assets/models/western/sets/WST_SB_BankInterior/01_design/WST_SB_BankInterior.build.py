"""
Receta de WST_SB_BankInterior, el interior del banco del lado rico de Silver Bend (prompt 111, Bloques A + C).

Brief
- Silueta a 40 studs (adentro se ve de más cerca): mostrador oscuro largo con tres ventanillas en arco de
  barrotes de bronce; atrás, un muro de piedra con la puerta redonda de la bóveda (gris metal, rueda de
  rayos de bronce, bulones alrededor); escritorio con lámpara verde; banco de espera de tablas.
- Armado como en el banco (origen de cada pieza en su base): mostrador en el centro (x ±8, z ±1), muro de
  la bóveda atrás (z 7..8), estantes con la plata detrás del muro (z 9..10,2), escritorio a la izquierda
  entre los dos (centro x -5,5, z 4), banco de espera adelante (z -6,5). El frente de todo mira a -Z.
- TellerCounter (6 fragmentos): cuerpo de 16 x 2,75 x 2 (wood_dark) con dos tableros rehundidos por tramo
  (wood_mid), tapa wood_mid de 0,2 con vuelo hacia el cliente, y arriba un paramento de 1,6 (hasta 4,55)
  con una ventanilla en arco por tramo (1,2 de ancho, 5 barrotes brass de 0,1 que arrancan 0,15 sobre el
  apoyo: la ranura del dinero). frag01..03: cuerpo partido en tres por quebraduras verticales en zigzag;
  frag04..06: los tres paramentos (cada uno con su ventanilla entera). Del lado del cajero, un nicho por
  tramo.
- Vault: muro de stone_grey de 12 x 10 x 1 con juntas sand, partido en cuatro piezas que no rodean el
  hueco (Vault_Wall_L, _R, _Top, _Sill: el casco convexo de cada una deja libre un paso de 2,8 x 5,5),
  aro de gunmetal de 3,15 a 3,6 que forra el hueco. VaultDoor: disco de 6 x 1 (gunmetal, 20 lados) con
  escalón al frente, 12 bulones brass, rueda de 5 rayos con perillas y aro, bisagras a la derecha (+X):
  origen en el eje de la bisagra (x 3,3, y 3,6, z 6,75). Modelada cerrada (como las puertas del kit).
- Vault_Shelves: estante de hierro y madera de 5,2 x 5,5 con lingotes silver_crust (0,6 x 0,3 x 0,3,
  troncos de pirámide) en pilas de 4 + 3 sobre tres estantes. Silver_Bars_Glow: láminas silver_neon de
  0,05 entre el estante y la pila y entre las dos capas, metidas 0,04 del borde (vetas que brillan).
- Desk_Banker: escritorio de dos cajoneras (cajones rehundidos con tiradores brass del lado del banquero,
  +Z), tablero wood_dark, lámpara de banquero (pie brass, pantalla glass_green, tubo lamp_glow abajo),
  dos libros mayores cerrados y uno abierto (tapas leather_dark, hojas paint_cream).
- Benches_Waiting (3 fragmentos): banco de 8 x 3,45 x 1,6, asiento de tres tablas a 1,5, respaldo
  inclinado, travesaño, tres caballetes y apoyabrazos. Los cortes del asiento, el respaldo y el
  travesaño caen en x distintos (tablas quebradas a distinta altura).
- Inferido: alto del mostrador (2,95 + paramento hasta 4,55 = los 4,5 del prompt), ventanillas, nichos,
  tableros, el muro partido en cuatro, aro, alto del hueco (sill de 0,45), bisagra y puerta cerrada,
  estante y pilas, láminas de brillo, lámpara y libros, medidas del banco de espera, armado del set,
  nombres de las piezas sin nombre en el prompt.

Vueltas: 1) primera versión: z-fighting entre las puntas del aro de la bóveda y el corte del muro (las dos
en x = ±1,4), y en el banco de espera entre el tope del caballete y el travesaño (y 3,45) y entre el
apoyabrazos y su poste (z -7,3) · 2) el aro termina 0,003 antes del corte, caballete hasta 3,4, poste 0,05
atrás; ventanillas de 1,2 a 1,44 con seis barrotes (se veían chicas en el paramento) y láminas de brillo
de 0,08 (las de 0,05 no se veían bajo las pilas).

Revisión
- 3994 triángulos contra 3000 (+33 %): mostrador 874 (6 fragmentos con tableros, nichos y 18 barrotes),
  muro de la bóveda 824 (cuatro piezas, aro y juntas de sillares), puerta 792 (disco de 20 lados, 12
  bulones, rueda con aro), estante 600 (42 lingotes de 12), escritorio 448, banco 312, brillo 144. La
  puerta y la plata son el foco de la defensa del banco.
- Medidas: mostrador 16 x 4,6 (cornisa) x 2,2 (con el vuelo de la tapa); muro 12 x 10 x 1 con la puerta de
  6 x 1 (centro a 3,6, umbral a 0,45); estante 5,2 x 5,5 x 1,2; escritorio 5 x 2,9 x 2,6; banco 8 x 3,45 x
  1,6. Lingotes 0,6 x 0,3 x 0,3.
- Fragmentos: mostrador 6 (cuerpo en tres, ~32 % cada uno; paramentos ~2 %), banco 3 (~33 %). Las
  quebraduras del cuerpo van en zigzag por los montantes, sin cruzar tableros ni nichos.
- El muro de la bóveda no es destructible (no lo pide); va en cuatro piezas para que la colisión de casco
  no tape el hueco: queda un paso de 2,8 x 5,5 (el jugador mide 2 x 5).
- Materiales: 13 (el prompt mismo pide piedra, gunmetal, brass, silver_crust, silver_neon, lamp_glow y
  verde; se suman madera oscura y media, sand de juntas, hierro, cuero y hojas). Por pieza, 7 como mucho
  (el escritorio).
- DUDOSO: la puerta está cerrada en su posición de origen (como las puertas del kit): la plata y su brillo
  solo se ven al abrirla (girar ~100° sobre el eje de la bisagra). La cara de atrás del muro (adentro de la
  bóveda) va lisa, sin juntas.
"""

import math

DARK, MID, BRASS, STONE, MORTAR, GUN = "wood_dark", "wood_mid", "brass", "stone_grey", "sand", "gunmetal"
IRON, SILVER, NEON, GREEN, GLOW, LEATHER, PAGE = ("iron", "silver_crust", "silver_neon", "glass_green", "lamp_glow",
                                                  "leather_dark", "paint_cream")


def arc(c, r, a0, a1, n):
    return [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ------------------------------------------------------------------------------------------------ mostrador
CX = (-8.0, 8.0)
BODY_Y, TOP_Y, SCR_Y = 2.75, 2.95, 4.5
ZB = (-1.0, 1.0)
CUTS = (-2.67, 2.67)


def zig_cut(x, amp=0.15, phase=0):
    ys = [0.0, 0.6, 1.2, 1.75, 2.3, BODY_Y]
    return [(x + (amp if (i + phase) % 2 else -amp) * (0.0 if i in (0, len(ys) - 1) else 1.0), y)
            for i, y in enumerate(ys)]


def counter(mk):
    left = zig_cut(CUTS[0])
    right = zig_cut(CUTS[1], phase=1)
    polys = [
        [(CX[0], 0.0)] + left + [(CX[0], BODY_Y)],                  # de la punta a la quebradura izquierda
        left + list(reversed(right)),                                # entre las dos quebraduras
        right + [(CX[1], BODY_Y), (CX[1], 0.0)],                     # de la quebradura derecha a la punta
    ]
    spans = [(CX[0], CUTS[0]), (CUTS[0], CUTS[1]), (CUTS[1], CX[1])]
    for i, (poly, (xa, xb)) in enumerate(zip(polys, spans)):
        p = mk.part(f"TellerCounter_frag0{i + 1}", (0, 0, 0))
        mk.prism(p, poly, ZB[1] - ZB[0], DARK, plane="xy", center=(0, 0, 0))
        mk.box(p, ((xa + xb) / 2, (BODY_Y + TOP_Y) / 2 - 0.005, -0.05), (xb - xa, TOP_Y - BODY_Y + 0.01, 2.2), MID)  # tapa
        w = xb - xa
        for k in (-1, 1):                                                       # tableros rehundidos
            cx = (xa + xb) / 2 + k * w / 4
            mk.carve(p, MID, points=mk.pts_box((cx, 1.45, ZB[0]), (w / 2 - 0.75, 1.7, 0.1)))
        mk.carve(p, MID, points=mk.pts_box(((xa + xb) / 2, 1.6, ZB[1]), (w - 0.9, 1.4, 1.2)))   # nicho del cajero
    for i, (xa, xb) in enumerate(spans):                                         # paramentos con ventanilla
        p = mk.part(f"TellerCounter_frag0{i + 4}", (0, 0, 0))
        xc = (xa + xb) / 2
        mk.box(p, (xc, (TOP_Y + SCR_Y) / 2, 0.15), (xb - xa, SCR_Y - TOP_Y, 0.25), DARK)
        mk.box(p, (xc, SCR_Y + 0.025, 0.15), (xb - xa - 0.004, 0.15, 0.4), DARK, top=(1.0, 0.8))   # cornisa
        r = 0.72
        win = [(xc - r, 3.15), (xc + r, 3.15)] + arc((xc, 3.55), r, 0, 180, 8)
        mk.carve(p, MID, prism=dict(profile=win, depth=0.6, plane="xy", center=(0, 0, 0.15)))
        for dx in (-0.55, -0.33, -0.11, 0.11, 0.33, 0.55):                       # barrotes
            top = 3.55 + math.sqrt(r * r - dx * dx) + 0.05
            mk.box(p, (xc + dx, (3.45 + top) / 2, 0.15), (0.1, top - 3.45, 0.1), BRASS, detail=True)
        mk.box(p, (xc, 3.45, 0.15), (2 * r + 0.1, 0.1, 0.13), BRASS, detail=True)        # travesaño: abajo queda la ranura
    return


# -------------------------------------------------------------------------------------------------- bóveda
VZ = (7.0, 8.0)
VC = (0.0, 3.6)
R_HOLE, R_IN, R_OUT = 3.4, 3.15, 3.6
XS = 1.4


def x_angle(r, xs=XS):
    return math.degrees(math.acos(xs / r))


def vault_wall(mk):
    wall_pieces = {}
    oz = sum(VZ) / 2
    a = x_angle(R_HOLE)
    regions = {
        "L": arc(VC, R_HOLE, 180 + a, 180 - a, 10) + [(-XS, 10.0), (-6.0, 10.0), (-6.0, 0.0), (-XS, 0.0)],
        "R": arc(VC, R_HOLE, -a, a, 10)[::-1] + [(XS, 0.0), (6.0, 0.0), (6.0, 10.0), (XS, 10.0)],
        "Top": arc(VC, R_HOLE, a, 180 - a, 8) + [(-XS, 10.0), (XS, 10.0)],
        "Sill": arc(VC, R_HOLE, 180 + a, 360 - a, 8) + [(XS, 0.0), (-XS, 0.0)],
    }
    ranges = {"L": (180, 180), "R": (0, 0), "Top": (90, 90), "Sill": (270, 270)}
    for name, poly in regions.items():
        p = mk.part(f"Vault_Wall_{name}", (0, 0, oz))
        mk.prism(p, poly, VZ[1] - VZ[0], STONE, plane="xy", center=(0, 0, oz))
        # aro de gunmetal que forra el hueco (se mete en la piedra; su cara de adentro queda en R_IN)
        c = ranges[name][0]
        xs = XS + (0.003 if name in ("L", "R") else -0.003)       # el aro termina 0,003 antes del corte del muro
        ao, ai = x_angle(R_OUT, xs), x_angle(R_IN, xs)
        span = {"L": (180 - ao, 180 + ao, 180 - ai, 180 + ai), "R": (-ao, ao, -ai, ai),
                "Top": (ao, 180 - ao, ai, 180 - ai), "Sill": (180 + ao, 360 - ao, 180 + ai, 360 - ai)}[name]
        n = 10 if name in ("L", "R") else 8
        ring = arc(VC, R_OUT, span[0], span[1], n) + arc(VC, R_IN, span[3], span[2], n)
        mk.prism(p, ring, 1.18, GUN, plane="xy", center=(0, 0, oz - 0.11), detail=True)
        # juntas de sillares en la cara de adelante
        for y in (1.25, 2.5, 3.75, 5.0, 6.25, 7.5, 8.75):
            for d in (-0.04, 0.04):
                mk.slice(p, (0, y + d, 0), (0, 1, 0))
            mk.paint(p, MORTAR, box=((0, y, VZ[0]), (12.2, 0.082, 0.02)))
        for k, y0 in enumerate((0.0, 1.25, 2.5, 3.75, 5.0, 6.25, 7.5, 8.75)):
            for xj in (-4.8, -2.4, 2.4, 4.8) if k % 2 == 0 else (-3.6, 3.6):
                for d in (-0.04, 0.04):
                    mk.slice(p, (xj + d, 0, 0), (1, 0, 0))
                mk.paint(p, MORTAR, box=((xj, y0 + 0.625, VZ[0]), (0.082, 1.16, 0.02)))
        wall_pieces[name] = p
    # placas de las bisagras en el muro (a la derecha del hueco)
    for y in (2.0, 5.2):
        mk.box(wall_pieces["R"], (3.75, y, VZ[0] - 0.05), (0.7, 0.9, 0.12), GUN, detail=True)
    return wall_pieces


PIV = (3.3, VC[1], 6.75)


def vault_door(mk):
    p = mk.part("VaultDoor", PIV)
    zf = 6.85                                                                   # cara de adelante
    mk.cyl(p, (VC[0], VC[1], zf + 0.5), 3.0, 1.0, GUN, axis="z", sides=20)
    mk.cyl(p, (VC[0], VC[1], zf - 0.04), 2.35, 0.1, GUN, axis="z", sides=20, top=1.02)   # escalón al frente
    for i in range(12):                                                         # bulones
        a = 2 * math.pi * (i + 0.5) / 12
        c = (VC[0] + 2.68 * math.cos(a), VC[1] + 2.68 * math.sin(a), zf - 0.05)
        mk.cyl(p, c, 0.15, 0.12, BRASS, axis="z", sides=6, top=1.4, detail=True)
    # rueda: eje, cubo, cinco rayos con perillas y aro
    zw = zf - 0.55
    mk.cyl(p, (VC[0], VC[1], zf - 0.3), 0.16, 0.55, BRASS, axis="z", sides=8, detail=True)
    mk.cyl(p, (VC[0], VC[1], zw), 0.38, 0.3, BRASS, axis="z", sides=8, detail=True)
    for i in range(5):
        a = math.radians(90 + 72 * i)
        u = (math.cos(a), math.sin(a))
        pts = [(VC[0] + u[0] * r - u[1] * w, VC[1] + u[1] * r + u[0] * w, zw + dz)
               for r in (0.3, 1.45) for w in (-0.07, 0.07) for dz in (-0.07, 0.07)]
        mk.hull(p, pts, BRASS, detail=True)
        mk.ball(p, (VC[0] + u[0] * 1.55, VC[1] + u[1] * 1.55, zw), 0.18, BRASS, subdiv=0, detail=True)
    for a0, a1, dz in ((-2, 182, 0.0), (178, 362, 0.004)):                       # aro en dos mitades
        prof = arc(VC, 1.22, a0, a1, 6) + arc(VC, 1.06, a1, a0, 6)
        mk.prism(p, prof, 0.13 - dz, BRASS, plane="xy", center=(0, 0, zw), detail=True)
    # bisagras: brazo desde la puerta al eje y nudos
    for y in (2.0, 5.2):
        mk.box(p, (2.85, y, PIV[2] + 0.08), (1.1, 0.7, 0.2), GUN, detail=True)
        mk.cyl(p, (PIV[0], y, PIV[2]), 0.24, 1.0, GUN, axis="y", sides=8, detail=True)
    return p


# ------------------------------------------------------------------------------------- estantes y plata
SH_Z = (9.0, 10.2)
SH_X = 2.6
SHELVES = (0.4, 1.9, 3.4, 4.9)


def ingot(mk, part, x, y, z, along_z=True):
    size = (0.3, 0.3, 0.6) if along_z else (0.6, 0.3, 0.3)
    top = (0.73, 0.87) if along_z else (0.87, 0.73)
    mk.box(part, (x, y + 0.15, z), size, SILVER, top=top)


def shelves(mk):
    p = mk.part("Vault_Shelves", (0, 0, sum(SH_Z) / 2))
    g = mk.part("Silver_Bars_Glow", (0, 0, sum(SH_Z) / 2))
    zc = sum(SH_Z) / 2
    for sx in (-1, 1):
        for z in SH_Z:
            mk.box(p, (sx * (SH_X - 0.08), 2.75, z + (0.08 if z == SH_Z[0] else -0.08)), (0.16, 5.5, 0.16), IRON)
    for y in SHELVES:
        mk.box(p, (0, y + 0.06, zc), (2 * SH_X - 0.1, 0.12, SH_Z[1] - SH_Z[0] - 0.02), DARK)
    for y in SHELVES[:3]:
        base = y + 0.12
        for sx in (-1, 1):
            cx = sx * 1.3
            mk.box(g, (cx, base + 0.035, zc), (1.2, 0.08, 0.52), NEON)                    # bajo la pila
            for k in range(4):
                ingot(mk, p, cx - 0.51 + 0.34 * k, base + 0.07, zc)
            mk.box(g, (cx, base + 0.07 + 0.335, zc), (0.95, 0.08, 0.44), NEON)             # entre capas
            for k in range(3):
                ingot(mk, p, cx - 0.34 + 0.34 * k, base + 0.07 + 0.37, zc)
    return p


# ------------------------------------------------------------------------------------------- escritorio
def desk(mk, ox, oz):
    p = mk.part("Desk_Banker", (ox, 0, oz))
    mk.box(p, (ox, 2.8, oz), (5.0, 0.2, 2.6), DARK)                                         # tablero
    for sx in (-1, 1):                                                                     # cajoneras
        x = ox + sx * 1.7
        mk.box(p, (x, 1.355, oz), (1.5, 2.71, 2.4), MID)
        for k, (y0, y1) in enumerate(((0.25, 1.05), (1.15, 1.85), (1.95, 2.55))):
            mk.carve(p, DARK, points=mk.pts_box((x, (y0 + y1) / 2, oz + 1.2), (1.2, y1 - y0, 0.08)))
            mk.box(p, (x, (y0 + y1) / 2, oz + 1.2), (0.36, 0.1, 0.12), BRASS, detail=True)
    mk.box(p, (ox, 1.755, oz - 1.0), (2.0, 1.91, 0.16), MID)                                # panel de adelante
    mk.carve(p, DARK, points=mk.pts_box((ox, 1.75, oz - 1.08), (1.5, 1.4, 0.06)))
    # lámpara de banquero
    lx, lz = ox - 1.6, oz + 0.55
    mk.cyl(p, (lx, 2.945, lz), 0.32, 0.1, BRASS, sides=8, top=0.8, detail=True)
    mk.box(p, (lx, 3.42, lz), (0.1, 0.9, 0.1), BRASS, detail=True)
    shade = arc((0, 0), 0.32, 0, 180, 4)
    mk.prism(p, [(z, 3.82 + y) for z, y in shade], 1.0, GREEN, plane="zy", center=(lx, 0, lz), detail=True)
    mk.box(p, (lx, 3.81, lz), (0.86, 0.06, 0.24), GLOW, detail=True)
    # libros mayores: dos cerrados apilados y uno abierto
    def book(cx, cy, cz, w, d, h, rot=0.0):
        mk.box(p, (cx, cy + h / 2, cz), (w, h - 0.04, d), PAGE, rot=(0, rot, 0), detail=True)
        for yy in (cy + 0.025, cy + h - 0.025):
            mk.box(p, (cx, yy, cz), (w + 0.06, 0.05, d + 0.06), LEATHER, rot=(0, rot, 0), detail=True)
    book(ox + 1.7, 2.895, oz - 0.3, 1.0, 1.3, 0.24, rot=8)
    book(ox + 1.68, 3.13, oz - 0.32, 0.9, 1.2, 0.2, rot=-5)
    mk.box(p, (ox + 0.1, 2.92, oz + 0.3), (1.9, 0.05, 1.3), LEATHER, rot=(0, -10, 0), detail=True)    # libro abierto
    for s in (-1, 1):
        mk.box(p, (ox + 0.1 + s * 0.46, 2.995, oz + 0.3 + s * 0.08), (0.86, 0.1, 1.22), PAGE,
               rot=(0, -10, s * 3), detail=True)
    return p


# ----------------------------------------------------------------------------------------- banco de espera
def bench(mk, oz):
    cuts = {"seat": (-1.25, 1.35), "back": (-1.45, 1.15), "rail": (-1.35, 1.25)}
    for f in range(3):
        p = mk.part(f"Benches_Waiting_frag0{f + 1}", (0, 0, oz))
        def span(key):
            c = cuts[key]
            return ((-4.0, c[0]), (c[0], c[1]), (c[1], 4.0))[f]
        a, b = span("seat")
        mk.box(p, ((a + b) / 2, 1.375, oz - 0.1), (b - a, 0.25, 1.3), MID)                 # asiento
        for zc in (oz - 0.32, oz + 0.12):                                               # juntas de las tablas
            for d in (-0.03, 0.03):
                mk.slice(p, (0, 0, zc + d), (0, 0, 1))
            mk.paint(p, DARK, box=(((a + b) / 2, 1.5, zc), (b - a + 0.1, 0.02, 0.062)))
        a, b = span("back")
        pts = [(x, y, oz + 0.62 + (y - 1.55) * 0.14 + dz) for x in (a, b) for y in (1.55, 3.1) for dz in (-0.07, 0.07)]
        mk.hull(p, pts, MID)                                                                 # respaldo
        a, b = span("rail")
        mk.box(p, ((a + b) / 2, 3.3, oz + 0.82), (b - a, 0.3, 0.3), DARK)                    # travesaño de arriba
        x = (-3.7, 0.0, 3.7)[f]                                                              # caballete
        mk.box(p, (x, 0.63, oz - 0.6), (0.24, 1.26, 0.24), DARK)
        mk.hull(p, [(x + dx, y, oz + 0.62 + (y - 1.55) * 0.14 + 0.12 + dz) for dx in (-0.12, 0.12)
                    for y in (0.0, 3.4) for dz in (-0.12, 0.12)], DARK)
        mk.box(p, (x, 0.35, oz + 0.05), (0.2, 0.2, 1.4), DARK)
        if f != 1:                                                                           # apoyabrazos
            mk.box(p, (x, 2.2, oz - 0.05), (0.24, 0.14, 1.5), DARK)
            mk.box(p, (x, 1.825, oz - 0.65), (0.2, 0.69, 0.2), DARK)


def build(mk):
    counter(mk)
    vault_wall(mk)
    vault_door(mk)
    shelves(mk)
    desk(mk, -5.5, 4.0)
    bench(mk, -6.5)

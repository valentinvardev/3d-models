"""
Receta de WST_RM_Corral, los módulos de corral del rancho (prompt 094, Bloques A + C). Grilla de 8.

Brief
- Silueta a 40 studs: cerca de troncos partidos (tres travesaños irregulares, claros y gastados) entre
  postes más oscuros con la punta cortada en bisel; portón con Z; esquina en L; manga alta de tablas.
- Módulos en fila sobre X, cada uno con su origen abajo al centro (o en su esquina): Corral_Rail en
  x = 0, Corral_Gate en x = 10, Corral_Corner en x = 18 (esquina; las dos tiradas van hacia +X y +Z),
  Corral_Chute en x = 34.
- Encadenado: cada módulo trae sus postes de punta (como los paneles de corral), centrados a 0,25 de la
  punta del módulo (x = ±3,75, 0,5 de ancho). Dos módulos seguidos dejan dos postes juntos que se tocan
  (no encimados: dos postes en el mismo lugar titilarían).
- Corral_Rail: 8 de largo, 3,2 de alto, tres travesaños de sección irregular (0,42 x 0,41, Bloque C:
  fragmento de 0,4 como mínimo) a 0,85 / 1,85 / 2,8; frag01..03 = los travesaños; fixed_PostL/R.
- Corral_Gate: portón de 6,85 x 2,7 con dos largueros, cuatro tablas, la Z oscura, bisagras y pasador;
  objeto Gate con el origen en el eje de las bisagras (canto -X, junto al poste izquierdo). fixed_PostL/R.
- Corral_Corner: poste de esquina en el origen y dos tiradas de 8 (hacia +X y +Z) con poste en la punta;
  frag01..06 = los travesaños; fixed_Post, fixed_PostX, fixed_PostZ.
- Corral_Chute: manga de 8 x 3 entre ejes de pared (postes de 0,45 a z = ±1,5; 1,75 libres), paredes de 5
  tablas de 0,4 (Bloque C) hasta 4,55 con luz entre tablas, postes de 5,3,
  travesaños de arriba que atan los postes; frag01..04 (dos por pared); fixed_Post1..4.
- Inferido: postes encadenables a ±3,75, sección de los travesaños, alturas, la tirada de la esquina de 8
  y su sentido, luz de la manga (2,4 libres), tablas de la manga, colores del portón (Z wood_dark).

Vueltas: 1) tablas de la manga de 0,2 (bajo el mínimo de fragmento) y z-fighting: la pletina de la bisagra
al ras del canto del portón y el travesaño de la manga al ras de las caras de los postes · 2) tablas de 0,4,
pletina corrida 0,02, travesaño 0,05 más corto.

Revisión
- Triángulos por módulo contra 200: Rail 104, Gate 184 (postes + portón), Corner 156, Chute 192.
- Medidas: Rail 8 x 3,2 (postes de 3,2 con bisel; travesaños de 0,42 x 0,41), Gate 8 x 3,45 (portón 6,85 x
  2,7 de y 0,35 a 3,05), Corner 8 + 8 en L, Chute 8 x 3,45 x 5,3 (3 entre ejes de pared, 1,75 libres).
- Fragmentos: Rail 3 (los travesaños), Corner 6, Chute 4 (dos por pared, tablas de 0,4); los postes son
  fixed_. El portón (Gate) es una pieza móvil con origen en el eje de las bisagras.
- Dudoso: los postes de punta van en cada módulo (a ±3,75): encadenados quedan postes dobles que se tocan.
  Si se prefiere poste simple, sacar fixed_PostR y usar la esquina o un poste suelto para cerrar.
  La manga mide 3,45 por fuera (3 entre ejes) para dejar 1,75 libres con tablas de 0,4.
"""

import math

LIGHT, MID, DARK, IRON = "wood_light", "wood_mid", "wood_dark", "iron"
H = 3.2
PX = 3.75                       # centro de los postes de punta
PW = 0.5
RAIL_Y = (0.85, 1.85, 2.8)
SECTIONS = [                    # secciones de troncos partidos (z, y), ~0,42 x 0,41, distintas
    [(0.21, 0.0), (0.08, 0.2), (-0.17, 0.16), (-0.21, -0.1), (0.03, -0.21)],
    [(0.2, 0.06), (-0.05, 0.21), (-0.21, 0.02), (-0.1, -0.2), (0.15, -0.17)],
    [(0.21, -0.05), (0.12, 0.18), (-0.13, 0.2), (-0.21, -0.04), (0.0, -0.21)],
]


def post(mk, part, x, z, h=H, r=0.27, slant=(1, 0)):
    """Poste de 6 lados con la punta cortada en bisel (para que escurra el agua)."""
    pts = []
    for k in range(6):
        t = 2 * math.pi * (k + 0.5) / 6
        dx, dz = r * math.cos(t), r * math.sin(t)
        pts.append((x + dx, 0.0, z + dz))
        pts.append((x + dx, h - 0.18 * (dx * slant[0] + dz * slant[1]) / r - 0.0, z + dz))
    mk.hull(part, pts, MID)


def rail_x(mk, part, x0, x1, y, z, sec, mat=LIGHT, sag=0.0):
    """Travesaño a lo largo de X (prisma de la sección), con caída opcional en el medio (grados)."""
    mk.prism(part, [(zz, yy) for zz, yy in sec], x1 - x0, mat, plane="zy", center=((x0 + x1) / 2, y, z),
             rot=(0, 0, sag))


def rail_z(mk, part, z0, z1, y, x, sec, mat=LIGHT):
    mk.prism(part, [(xx, yy) for xx, yy in sec], z1 - z0, mat, plane="xy", center=(x, y, (z0 + z1) / 2))


# ---------------------------------------------------------------- módulos
def corral_rail(mk, ox):
    for name, x, sl in (("fixed_PostL", -PX, (1, 0.3)), ("fixed_PostR", PX, (-1, 0.3))):
        part = mk.part(f"Corral_Rail_{name}", (ox, 0, 0))
        post(mk, part, ox + x, 0.0, slant=sl)
    for i, y in enumerate(RAIL_Y):
        part = mk.part(f"Corral_Rail_frag{i + 1:02d}", (ox, 0, 0))
        sag = (-1.2 if i == 1 else 0.0)                                  # el del medio, apenas caído
        rail_x(mk, part, ox - PX - 0.12, ox + PX + 0.12, y, 0.0, SECTIONS[i], sag=sag)
        if i == 2:                                                       # punta rajada (madera clara adentro)
            mk.carve(part, DARK, prism=dict(profile=[(ox + 1.2, y + 0.06), (ox + 2.9, y + 0.02), (ox + 1.2, y - 0.02)],
                                            depth=1.0, plane="xy", center=(0, 0, 0)))


def corral_gate(mk, ox):
    for name, x, sl in (("fixed_PostL", -PX, (1, 0.3)), ("fixed_PostR", PX, (-1, 0.3))):
        part = mk.part(f"Corral_Gate_{name}", (ox, 0, 0))
        post(mk, part, ox + x, 0.0, h=H + 0.25, r=0.3, slant=sl)
    x0 = ox - PX + PW / 2 + 0.05                                         # canto de las bisagras
    x1 = ox + PX - PW / 2 - 0.1
    y0, y1 = 0.35, 3.05
    part = mk.part("Gate", (x0, 0, 0))
    for xa, xb in ((x0, x0 + 0.32), (x1 - 0.32, x1)):                   # largueros
        mk.box(part, ((xa + xb) / 2, (y0 + y1) / 2, 0), (xb - xa, y1 - y0, 0.24), LIGHT)
    for y in (0.55, 1.35, 2.15, 2.85):                                   # tablas (entran 0,02 en los largueros)
        mk.box(part, ((x0 + x1) / 2, y, 0), (x1 - x0 - 0.6, 0.3, 0.2), LIGHT)
    a, b = (x0 + 0.3, 0.6), (x1 - 0.3, 2.85)                              # Z: diagonal de la bisagra abajo al pasador arriba
    d = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*d)
    nx, ny = -d[1] / n * 0.14, d[0] / n * 0.14
    mk.hull(part, [(p[0] + k * nx, p[1] + k * ny, z) for p in (a, b) for k in (-1, 1) for z in (-0.1, -0.2)], DARK)
    for y in (0.75, 2.6):                                                # bisagras (pletina + gozne al poste)
        mk.box(part, (x0 + 0.47, y, -0.13), (0.88, 0.14, 0.05), IRON, detail=True)   # no al ras del canto
        mk.box(part, (x0 - 0.06, y, 0.0), (0.16, 0.22, 0.16), IRON, detail=True)
    mk.box(part, (x1 - 0.12, 1.95, -0.14), (0.5, 0.12, 0.08), IRON, detail=True)   # pasador


def corral_corner(mk, ox):
    part = mk.part("Corral_Corner_fixed_Post", (ox, 0, 0))
    post(mk, part, ox, 0.0, h=H + 0.15, r=0.32, slant=(0.7, 0.7))
    part = mk.part("Corral_Corner_fixed_PostX", (ox, 0, 0))
    post(mk, part, ox + 8.0 - 0.25, 0.0, slant=(-1, 0.3))
    part = mk.part("Corral_Corner_fixed_PostZ", (ox, 0, 0))
    post(mk, part, ox, 8.0 - 0.25, slant=(0.3, -1))
    n = 1
    for i, y in enumerate(RAIL_Y):                                       # tirada hacia +X
        part = mk.part(f"Corral_Corner_frag{n:02d}", (ox, 0, 0))
        rail_x(mk, part, ox + 0.12, ox + 7.75 + 0.12, y, 0.0, SECTIONS[(i + 1) % 3])
        n += 1
    for i, y in enumerate(RAIL_Y):                                       # tirada hacia +Z (0,12 más arriba: no se cruzan)
        part = mk.part(f"Corral_Corner_frag{n:02d}", (ox, 0, 0))
        rail_z(mk, part, 0.12, 7.75 + 0.12, y + 0.12 * (1 if i < 2 else -1), ox, SECTIONS[(i + 2) % 3])
        n += 1


def corral_chute(mk, ox):
    zs = (-1.5, 1.5)
    k = 1
    for z in zs:
        for x in (-PX, PX):
            part = mk.part(f"Corral_Chute_fixed_Post{k}", (ox, 0, 0))
            mk.box(part, (ox + x, 2.65, z), (0.45, 5.3, 0.45), MID)
            if z > 0:                                                    # travesaño de arriba que ata la manga
                mk.box(part, (ox + x, 5.09, 0), (0.4, 0.34, 3.4), DARK)   # (no al ras de punta ni caras del poste)
            k += 1
    planks = [(0.35, 0.95), (1.25, 1.85), (2.15, 2.75), (3.05, 3.65), (3.95, 4.55)]
    n = 1
    for z in zs:
        zi = z - (0.225 + 0.2) * (1 if z > 0 else -1)                    # tablas de 0,4 (Bloque C) adentro de los postes
        for group in (planks[:2], planks[2:]):
            part = mk.part(f"Corral_Chute_frag{n:02d}", (ox, 0, 0))
            for j, (y0, y1) in enumerate(group):
                chip = 0.25 if (n + j) % 3 == 0 else 0.0                 # una punta comida
                mk.hull(part, [(ox + xx, y, zi + dz) for xx in (-PX - 0.2, PX + 0.2 - chip) for y in (y0, y1)
                               for dz in (-0.2, 0.2)]
                        + [(ox + PX + 0.2, y0, zi + dz) for dz in (-0.2, 0.2)], LIGHT)
            n += 1


def build(mk):
    corral_rail(mk, 0.0)
    corral_gate(mk, 10.0)
    corral_corner(mk, 18.0)
    corral_chute(mk, 34.0)

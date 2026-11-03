"""
Receta de WST_HC_Tombstones, las lápidas del cementerio de Hollow Creek (prompt 116, Bloques A + C).

Brief
- Silueta a 40 studs: ocho marcadores que se distinguen por el contorno: piedra redonda, piedra cuadrada
  con cornisa, cruz de piedra, piedra rota, piedra ojival torcida, dos cruces de tablas (una derecha y
  otra torcida) y una tabla con la punta redonda. Se repiten mucho: el contorno es lo que tiene que leerse.
- Ocho objetos en fila sobre X cada 3 (prefijo <Variante>_, origen en la base de cada una, frente -Z),
  cada uno en 2 fragmentos partidos por una rajadura en zigzag de 3-5 quiebres; el fragmento de arriba
  sale 0,03 hacia adelante (el escalón marca la rajadura sin luz entre fragmentos).
- Cara de adelante lisa en el centro (para la calcomanía del epitafio); el liquen ochre va en manchas
  rehundidas 0,03 (carve) en los bordes y arriba, nunca en el centro de la cara.
- Medidas: Tombstone_Round 2 x 3 x 0,4 (arco de radio 1). Tombstone_Square 1,9 x 2,6 x 0,45 con cornisa de
  2,1 x 0,25 x 0,55. Tombstone_Cross 3 de alto (fuste de 0,5, brazos de 1,6 a 2,0..2,45) sobre un dado
  de 1 x 0,4 x 0,6. Tombstone_Broken: la redonda sin la mitad de arriba en diagonal (alto 2,1 de un lado,
  1,0 del otro). Tombstone_Leaning 1,8 x 2,8 x 0,4 ojival, girada 15° de costado y hundida para que el
  canto alto toque el piso. Cruces de tablas: fuste de 0,45 x 3,5 x 0,35 y travesaño de 1,8 x 0,4 x 0,3
  clavado adelante; B torcida 12° y con el travesaño chueco. WoodMarker 0,9 x 2,4 x 0,4, punta redonda.
- Inferido: medidas de todas salvo la redonda y las cruces de 3 y 3,5, formas de la cuadrada, ojival y
  rota, dado de la cruz, cortes, espesor 0,35-0,45 (fragmentos >= 0,35: las tablas de 0,4 se ven gruesas
  en una cruz), escalón de la rajadura, nombres y separación.

Vueltas: 1) primera versión: pasa la revisión; el travesaño torcido de la cruz B giraba alrededor de la base
(se salía del fuste) y la ojival no cerraba en punta (arcos a 62°) -> giro alrededor del cruce y arcos a
72,1° · 2) manchas de liquen más irregulares (eran hexágonos casi regulares: se leían como calcomanías).

Revisión
- Triángulos por pieza (tope 120 de referencia): Round 172, Square 120, Cross 126, Broken 132, Leaning
  136, WoodCross_A 64, WoodCross_B 64, WoodMarker 72. Las piedras se pasan por las manchas de liquen
  rehundidas (~20 cada una, son el detalle que pide el prompt) y el arco de 8 tramos de la redonda.
- Medidas: Round 2 x 3 x 0,4; Square 2,1 x 2,83 x 0,55 (con cornisa); Cross 1,6 x 3 (dado de 1 x 0,6);
  Broken 2 x 2,1; Leaning 1,8 x 2,89 girada 15° (enterrada 0,49 del lado bajo); cruces de 3,5; WoodMarker
  0,9 x 2,4. Las de piedra salen 0,03 más gruesas arriba por el escalón de la rajadura.
- Fragmentos: 2 por pieza (el Bloque C pide <= 45 %: con dos es imposible, igual que el poste de atar).
  Las cruces de tablas son de 0,35 de espesor (el Bloque C pide 0,4; con 0,4 la cruz se ve de viga).
- Cara de adelante: el centro queda libre para el epitafio en todas (el liquen va en bordes y puntas). En
  la cruz de piedra el lugar libre es el fuste debajo de los brazos (0,5 de ancho).
- Materiales: stone_grey, ochre, wood_light, wood_mid (el travesaño, para separarlo del fuste).
"""

import math

STONE, LICHEN, WOOD, WOOD2 = "stone_grey", "ochre", "wood_light", "wood_mid"
STEP = 0.03          # el de arriba sale hacia adelante


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def crack(xl, yl, xr, yr, n=4, amp=0.12, phase=0):
    """Rajadura de (xl, yl) a (xr, yr) con n tramos en zigzag."""
    pts = []
    for i in range(n + 1):
        t = i / n
        d = 0.0 if i in (0, n) else amp * (1 if (i + phase) % 2 else -1)
        pts.append((xl + (xr - xl) * t, yl + (yr - yl) * t + d))
    return pts


def two_frags(mk, name, ox, bottom, top, depth, mat, oy=0.0, rot=(0, 0, 0), lichen=(), zc=0.0):
    """bottom/top: perfiles (x, y) locales. Devuelve las dos piezas. lichen: [(frag, polígono)]."""
    parts = []
    for i, prof in enumerate((bottom, top)):
        p = mk.part(f"{name}_frag0{i + 1}", (ox, 0, 0))
        mk.prism(p, prof, depth, mat, plane="xy", center=(ox, oy, zc - (STEP if i else 0.0)), rot=rot)
        parts.append(p)
    for k, poly in lichen:
        z = zc - (STEP if k else 0.0) - depth / 2
        mk.carve(parts[k], LICHEN, prism=dict(profile=poly, depth=0.06, plane="xy", center=(ox, oy, z), rot=rot))
    return parts


def blob(cx, cy, r, n=7, seed=0):
    """Mancha irregular (radios de 0,45 a 1,15 r, más ancha que alta)."""
    ks = (1.15, 0.55, 0.95, 0.45, 1.05, 0.7, 0.9, 0.5)
    return [(cx + r * 1.2 * ks[(i + seed) % 8] * math.cos(2 * math.pi * i / n),
             cy + r * 0.75 * ks[(i + seed) % 8] * math.sin(2 * math.pi * i / n)) for i in range(n)]


# -------------------------------------------------------------------------------------------- piedras
def tomb_round(mk, ox):
    w, h, r = 1.0, 3.0, 1.0
    c = crack(-w, 1.05, w, 1.55, n=4)
    bottom = [(-w, 0.0), (w, 0.0)] + c[::-1]
    top = c + [(w, h - r)] + arc(0, h - r, r, 0, 180, 8)[1:-1] + [(-w, h - r)]
    lich = [(1, blob(-0.62, 2.45, 0.32, seed=1)), (0, blob(0.7, 0.35, 0.28, seed=4)), (1, blob(0.45, 2.75, 0.2, seed=2))]
    two_frags(mk, "Tombstone_Round", ox, bottom, top, 0.4, STONE, lichen=lich)


def tomb_square(mk, ox):
    w, h = 0.95, 2.6
    c = crack(-w, 1.4, w, 0.9, n=4, phase=1)
    bottom = [(-w, 0.0), (w, 0.0)] + c[::-1]
    top = c + [(w, h), (-w, h)]
    parts = two_frags(mk, "Tombstone_Square", ox, bottom, top, 0.45, STONE,
                      lichen=[(1, blob(0.62, 2.3, 0.26, seed=3)), (0, blob(-0.62, 0.45, 0.3, seed=6))])
    mk.box(parts[1], (ox, h + 0.1, -STEP), (2.1, 0.25, 0.55), STONE, top=(0.9, 0.85))       # cornisa


def tomb_cross(mk, ox):
    sw, ay0, ay1, aw, h = 0.25, 2.0, 2.45, 0.8, 3.0
    c = crack(-sw, 1.15, sw, 1.4, n=3)
    bottom = [(-sw, 0.35), (sw, 0.35)] + c[::-1]
    top = c + [(sw, ay0), (aw, ay0), (aw, ay1), (sw, ay1), (sw, h), (-sw, h), (-sw, ay1), (-aw, ay1), (-aw, ay0),
               (-sw, ay0)]
    parts = two_frags(mk, "Tombstone_Cross", ox, bottom, top, 0.4, STONE,
                      lichen=[(1, blob(0.62, 2.22, 0.14, n=5, seed=2)), (1, blob(0.0, 2.85, 0.13, n=5, seed=5))])
    mk.box(parts[0], (ox, 0.2, 0), (1.0, 0.4, 0.6), STONE, top=(0.85, 0.85))                  # dado


def tomb_broken(mk, ox):
    w = 1.0
    c = crack(-w, 0.75, w, 0.45, n=4, phase=1)
    bottom = [(-w, 0.0), (w, 0.0)] + c[::-1]
    jag = [(w, 1.0), (0.62, 1.22), (0.75, 1.45), (0.3, 1.62), (0.12, 1.95), (-0.25, 1.88), (-0.5, 2.1), (-0.75, 2.02)]
    top = c + jag + [(-w, 1.95)]
    two_frags(mk, "Tombstone_Broken", ox, bottom, top, 0.4, STONE,
              lichen=[(0, blob(0.55, 0.2, 0.22, seed=1)), (1, blob(-0.6, 1.6, 0.28, seed=7))])


def tomb_leaning(mk, ox):
    w, h = 0.9, 2.8
    c = crack(-w, 1.3, w, 0.95, n=4)
    bottom = [(-w, 0.0), (w, 0.0)] + c[::-1]
    # ojival: dos arcos que se juntan en punta
    r = 1.3
    right = arc(w - r, h - 1.15, r, 0, 72.1, 4)
    left = [(-x, y) for x, y in reversed(right)]
    top = c + [(w, h - 1.15)] + right[1:] + left[1:-1] + [(-w, h - 1.15)]
    ang = 15.0
    drop = -w * math.sin(math.radians(ang)) - 0.02                       # canto alto en el piso, el otro enterrado
    two_frags(mk, "Tombstone_Leaning", ox, bottom, top, 0.4, STONE, oy=drop, rot=(0, 0, ang),
              lichen=[(1, blob(0.5, 2.0, 0.24, seed=2)), (0, blob(-0.55, 0.55, 0.3, seed=5))])


# -------------------------------------------------------------------------------------------- maderas
def wood_cross(mk, name, ox, lean=0.0, arm_tilt=0.0):
    sw, h, t = 0.225, 3.5, 0.35
    c = crack(-sw, 1.0, sw, 1.25, n=3, amp=0.1)
    bottom = [(-sw, 0.0), (sw, 0.0)] + c[::-1]
    top = c + [(sw, h - 0.12), (0.05, h), (-sw, h - 0.05)]                       # punta cortada en diagonal
    rot = (0, 0, lean)
    parts = two_frags(mk, name, ox, bottom, top, t, WOOD, rot=rot)
    # travesaño clavado adelante (en la pieza de arriba), con las puntas despuntadas
    ay, aw = 2.45, 0.9
    arm = [(-aw, ay - 0.2), (aw - 0.08, ay - 0.2), (aw, ay - 0.05), (aw - 0.06, ay + 0.2), (-aw + 0.1, ay + 0.2),
           (-aw, ay + 0.06)]
    e, a = math.radians(lean), math.radians(lean + arm_tilt)
    cx, cy = -ay * math.sin(e), ay * math.cos(e)                         # el cruce, girado con el fuste
    arm_local = [(x * math.cos(a) - (y - ay) * math.sin(a) + cx, x * math.sin(a) + (y - ay) * math.cos(a) + cy)
                 for x, y in arm]
    mk.prism(parts[1], arm_local, 0.3, WOOD2, plane="xy", center=(ox, 0, -t / 2 - STEP - 0.13))
    return parts


def wood_marker(mk, ox):
    w, h, r = 0.45, 2.4, 0.45
    c = crack(-w, 0.95, w, 1.2, n=3, amp=0.1, phase=1)
    bottom = [(-w, 0.0), (w, 0.0)] + c[::-1]
    top = c + [(w, h - r)] + arc(0, h - r, r, 0, 180, 6)[1:-1] + [(-w, h - r)]
    parts = two_frags(mk, "WoodMarker", ox, bottom, top, 0.4, WOOD)
    mk.carve(parts[1], WOOD2, prism=dict(profile=[(0.18, h + 0.1), (0.05, h - 0.55), (0.12, h - 0.6), (0.3, h + 0.1)],
                                        depth=1.0, plane="xy", center=(ox, 0, 0)))   # raja en la punta


def build(mk):
    tomb_round(mk, 0.0)
    tomb_square(mk, 3.0)
    tomb_cross(mk, 6.0)
    tomb_broken(mk, 9.0)
    tomb_leaning(mk, 12.0)
    wood_cross(mk, "WoodCross_A", 15.0)
    wood_cross(mk, "WoodCross_B", 18.0, lean=-12.0, arm_tilt=7.0)
    wood_marker(mk, 21.0)

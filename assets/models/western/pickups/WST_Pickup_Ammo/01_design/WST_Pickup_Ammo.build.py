"""
Receta de WST_Pickup_Ammo, las cajas de munición que se juntan del piso (prompt 036, Bloques A + B).

Brief
- Tres variantes en fila sobre X, cada una con el origen en el centro de su base: Ammo_Revolver,
  Ammo_Rifle, Ammo_Shotgun. Se leen a 40 studs por el color de la caja (crema, mostaza, turquesa), la
  tapa abierta parada atrás y la fila de balas que asoma por la boca.
- Medidas (ancho X x alto x profundidad, la convención de los prompts): revólver 0,5 x 0,3 x 0,35;
  rifle 0,75 x 0,3 x 0,35; escopeta 0,55 x 0,35 x 0,45. Boca tallada (paredes de 0,035, 0,06 de hondo).
  La tapa (del tamaño de la boca) gira 110° sobre la arista de atrás de arriba y queda inclinada atrás.
- Balas paradas, metidas en el fondo: revólver 6 balas de bronce de 6 lados (vaina corta y punta roma);
  rifle 5 balas largas en punta, de bronce; escopeta 4 cartuchos rojos con el culote de bronce arriba.
- Franja pintada alrededor (roja en el revólver, hierro en el rifle) con dos cortes; etiqueta crema lisa
  en el frente del rifle y de la escopeta (pintada, sin texto).
- Balas y tapa van como detalle: se agregan después de tallar la boca (si están en la base, la booleana
  las corta: medido) y cada color es su propio casco.
- Inferido: cómo se lee "abierta" (boca tallada, tapa a 110°, balas paradas), las alturas de franja y
  etiqueta, los culotes de la escopeta hacia arriba.

Vueltas: 1) caja maciza con las balas apoyadas arriba: no se leía abierta · 2) boca tallada, pero con
las balas en la base la booleana las cortó (quedaban las puntas flotando) · 3) balas y tapa como
detalle, un casco por color; las balas del rifle, todas de bronce (la punta de plomo pedía otro casco).

Revisión
- Triángulos por variante contra 120 de referencia (calidad primero): revólver 190, rifle 184, escopeta
  214. La caja con su boca, franja o etiqueta y tapa son ~55; el resto son las balas (6 x 22, 5 x 22,
  4 x 40), que son lo que hace que se lea munición. Con conos en vez de balas el revólver baja a ~120,
  pero se ven púas.
"""

import math

WALL, DEPTH = 0.035, 0.06          # caja abierta: paredes y hondura de la boca


def ring(c, y, r, sides=6):
    return [(c[0] + r * math.cos(2 * math.pi * i / sides), y, c[2] + r * math.sin(2 * math.pi * i / sides))
            for i in range(sides)]


def lid_points(x0, w, h, d, t=0.03, open_deg=110):
    """Tapa abierta: placa de w x d x t girada open_deg sobre la arista de atrás de arriba (metida 0,01)."""
    f = math.radians(open_deg)
    hz, hy = d / 2 - 0.01, h - 0.01                 # bisagra
    dz, dy = -math.cos(f), math.sin(f)              # de la bisagra al borde de adelante
    tz, ty = math.sin(f), math.cos(f)               # espesor
    return [(x, hy + a * dy + b * ty, hz + a * dz + b * tz)
            for x in (x0 - w / 2, x0 + w / 2) for a in (0.0, d) for b in (0.0, t)]


def box_body(mk, part, x0, w, h, d, mat):
    """Caja con la boca tallada y la tapa abierta (detalle)."""
    mk.box(part, (x0, h / 2, 0), (w, h, d), mat)
    mk.carve(part, mat, points=mk.pts_box((x0, h - DEPTH + 0.1, 0), (w - 2 * WALL, 0.2, d - 2 * WALL)))
    mk.hull(part, lid_points(x0, w, h, d), mat, detail=True)


def band(mk, part, x0, w, d, y0, y1, mat):
    for y in (y0, y1):
        mk.slice(part, (0, y, 0), (0, 1, 0))
    mk.paint(part, mat, box=((x0, (y0 + y1) / 2, 0), (w + 0.02, y1 - y0 - 0.002, d + 0.02)))


def label(mk, part, x0, w, d, y0, y1):
    """Etiqueta crema lisa en el frente."""
    for x in (x0 - w / 2, x0 + w / 2):
        mk.slice(part, (x, 0, 0), (1, 0, 0))
    for y in (y0, y1):
        mk.slice(part, (0, y, 0), (0, 1, 0))
    mk.paint(part, "paint_cream", box=((x0, (y0 + y1) / 2, -d / 2), (w - 0.002, y1 - y0 - 0.002, 0.01)))


def build(mk):
    # ---------------- revólver: caja crema con franja roja, 6 balas de bronce ----------------
    x0, w, h, d = -0.85, 0.5, 0.3, 0.35
    p = mk.part("Ammo_Revolver", (x0, 0, 0))
    box_body(mk, p, x0, w, h, d, "paint_cream")
    band(mk, p, x0, w, d, 0.11, 0.19, "cloth_red")
    for i in range(6):
        c = (x0 - 0.2 + 0.08 * i, 0, -0.04)
        mk.hull(p, ring(c, h - DEPTH - 0.02, 0.034) + ring(c, h + 0.035, 0.032) + [(c[0], h + 0.08, c[2])],
                "brass", detail=True)

    # ---------------- rifle: caja mostaza, franja de hierro, etiqueta, 5 balas largas en punta ----------------
    x0, w, h, d = 0.0, 0.75, 0.3, 0.35
    p = mk.part("Ammo_Rifle", (x0, 0, 0))
    box_body(mk, p, x0, w, h, d, "paint_mustard")
    band(mk, p, x0, w, d, 0.03, 0.08, "iron")
    label(mk, p, x0, 0.42, d, 0.12, 0.25)
    for i in range(5):
        c = (x0 - 0.26 + 0.13 * i, 0, -0.04)
        mk.hull(p, ring(c, h - DEPTH - 0.02, 0.04) + ring(c, h + 0.09, 0.036) + [(c[0], h + 0.17, c[2])],
                "brass", detail=True)

    # ---------------- escopeta: caja turquesa, etiqueta, 4 cartuchos con el culote arriba ----------------
    x0, w, h, d = 0.9, 0.55, 0.35, 0.45
    p = mk.part("Ammo_Shotgun", (x0, 0, 0))
    box_body(mk, p, x0, w, h, d, "paint_teal")
    label(mk, p, x0, 0.34, d, 0.08, 0.27)
    for i in range(4):
        c = (x0 - 0.195 + 0.13 * i, 0, -0.06)
        mk.hull(p, ring(c, h - DEPTH - 0.02, 0.056) + ring(c, h + 0.05, 0.056), "cloth_red", detail=True)
        mk.hull(p, ring(c, h + 0.045, 0.062) + ring(c, h + 0.1, 0.062), "brass", detail=True)   # culote, más ancho

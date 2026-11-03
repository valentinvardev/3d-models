"""
Receta de WST_CH_Pew, los bancos de la iglesia (prompt 125, Bloques A + C). Fase 2 del Predicador: los bancos
son cobertura rompible.

Brief
- Silueta: banco largo de madera con dos cabeceras macizas de canto curvo (bajas adelante, altas atrás),
  asiento de tabla y respaldo macizo apenas reclinado con una tapa oscura arriba.
- Medidas: 8 (X) x 3,4 (alto del respaldo, 3,5 con la tapa) x 2,2 (Z); asiento arriba a 1,8; respaldo de
  0,2 a 3,35, macizo hasta abajo (cobertura agachado). El frente (donde uno se sienta mirando) es -Z: en la
  iglesia se gira 180° para mirar al altar.
- Variantes en fila sobre X: Pew en x = 0, Pew_Toppled en x = 10 (caído sobre el respaldo), Pew_Broken en
  x = 20 (partido al medio con las puntas astilladas; la mitad derecha corrida y girada 7°).
- Fragmentos (4 por banco): frag01 cabecera izquierda, frag02 cabecera derecha, frag03 asiento (en el
  partido: mitad izquierda de asiento y respaldo), frag04 respaldo con su tapa (en el partido: mitad derecha).
- Inferido: perfil de la cabecera, inclinación del respaldo (3,6°), tapa wood_dark, juntas del respaldo, cómo
  cae el volcado y cómo se separa el partido, astillas wood_light.

Vueltas: 1) restos de una prueba con error de sintaxis y astillas del partido que arrancaban en el aire ·
2) limpio: pasa sin errores.

Revisión
- 488 triángulos en el archivo con los tres bancos (~160 por banco) contra 250 "para el modelo entero": el
  tope parece pensado por banco (las variantes van en el mismo archivo). Cabeceras de 8 lados con canto
  curvo convexo (cada una un casco), asiento, respaldo con dos juntas y tapa; el partido suma los zigzag de
  asiento y respaldo y cuatro astillas.
- Medidas: cada banco 8 x 3,5 (con la tapa) x 2,28; asiento a 1,8. Fila de 28,5 en X.
- Fragmentos: respaldo ~37 % del volumen, cabeceras ~24 % cada una, asiento ~15 %; en el partido, cada mitad
  de asiento + respaldo ~26 %.
- El volcado apoya en la tapa y en los cantos de atrás de las cabeceras (respaldo reclinado: queda 0,08
  arriba del piso).
"""

import math

WOOD, DARK, FRESH = "wood_mid", "wood_dark", "wood_light"
END = [(-1.1, 0.0), (1.1, 0.0), (1.1, 3.4), (0.7, 3.5), (0.2, 3.35), (-0.4, 2.95), (-0.9, 2.5), (-1.1, 2.3)]  # (z, y)


def make_tf(off, rot_x=0.0, yaw=0.0, pivot=(0.0, 0.0, 0.0)):
    """Transformación de un banco: giro en X (volcado), giro en Y alrededor de pivot y corrimiento."""
    cx, sx = math.cos(math.radians(rot_x)), math.sin(math.radians(rot_x))
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))

    def tf(p):
        x, y, z = p
        y, z = y * cx - z * sx, y * sx + z * cx
        x, z = x - pivot[0], z - pivot[2]
        x, z = x * cy + z * sy, -x * sy + z * cy
        x, z = x + pivot[0], z + pivot[2]
        return (x + off[0], y + off[1], z + off[2])
    return tf


def box_pts(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def end_panel(mk, name, tf, xa, xb):
    part = mk.part(name, tf((0, 0, 0)))
    mk.hull(part, [tf((x, y, z)) for z, y in END for x in (xa, xb)], WOOD)
    return part


def back_pts(x0, x1, y0=0.2, y1=3.35):
    """Respaldo reclinado: abajo z 0,65-0,9, arriba 0,85-1,1."""
    return [(x, y, z) for x in (x0, x1) for y, z in ((y0, 0.65), (y0, 0.9), (y1, 0.85), (y1, 1.1))]


def back_z(y, face):
    """z de la cara de adelante (face=0) o de atrás (face=1) del respaldo a la altura y."""
    t = (y - 0.2) / 3.15
    return (0.65 if face == 0 else 0.9) + 0.2 * t


def whole_pew(mk, prefix, tf):
    end_panel(mk, f"{prefix}_frag01", tf, -4.0, -3.7)
    end_panel(mk, f"{prefix}_frag02", tf, 3.7, 4.0)
    part = mk.part(f"{prefix}_frag03", tf((0, 0, 0)))                                 # asiento
    mk.hull(part, [tf(p) for p in box_pts(-3.72, 3.72, 1.6, 1.8, -1.05, 0.67)], WOOD)
    part = mk.part(f"{prefix}_frag04", tf((0, 0, 0)))                                 # respaldo y tapa
    mk.hull(part, [tf(p) for p in back_pts(-3.72, 3.72)], WOOD)
    mk.hull(part, [tf(p) for p in box_pts(-3.74, 3.74, 3.33, 3.5, 0.8, 1.18)], DARK, detail=True)
    for y in (2.45, 2.95):                                                            # juntas de las tablas
        for dy in (-0.03, 0.03):
            p0, p1 = tf((0, y + dy, 0)), tf((0, y + dy + 1.0, 0))
            mk.slice(part, p0, tuple(p1[i] - p0[i] for i in range(3)))
        for face in (0, 1):
            mk.paint(part, DARK, box=(tf((0, y, back_z(y, face))), size_tf(tf, (7.6, 0.062, 0.08))))


def size_tf(tf, size):
    """Tamaño de una caja de pintura después de girar (los giros de 90° cambian ejes)."""
    o = tf((0, 0, 0))
    ex = [abs(tf((size[0], 0, 0))[i] - o[i]) + abs(tf((0, size[1], 0))[i] - o[i]) + abs(tf((0, 0, size[2]))[i] - o[i])
          for i in range(3)]
    return tuple(max(0.02, e) for e in ex)


def broken_pew(mk, prefix, ox):
    left = make_tf((ox, 0, 0))
    right = make_tf((ox + 0.35, 0, -0.15), yaw=7.0, pivot=(4.0, 0.0, 0.0))
    end_panel(mk, f"{prefix}_frag01", left, -4.0, -3.7)
    end_panel(mk, f"{prefix}_frag02", right, 3.7, 4.0)
    # punta astillada: zigzag en X a lo largo de Z (asiento) y de Y (respaldo)
    seat_jag = [(-0.05, -1.05), (-0.45, -0.6), (0.1, -0.2), (-0.35, 0.25), (0.05, 0.67)]   # (x, z)
    back_jag = [(0.0, 0.2), (-0.4, 0.9), (0.15, 1.6), (-0.3, 2.3), (0.1, 2.9), (-0.2, 3.35)]  # (x, y)
    for k, (tf, side) in enumerate(((left, -1), (right, 1))):
        part = mk.part(f"{prefix}_frag{k + 3:02d}", tf((0, 0, 0)))
        sj = [(x + side * 0.12, z) for x, z in seat_jag]
        bj = [(x + side * 0.12, y) for x, y in back_jag]
        if side < 0:
            seat = [(-3.72, -1.05)] + sj + [(-3.72, 0.67)]
            back = [(-3.72, 0.2)] + bj + [(-3.72, 3.35)]
        else:
            seat = [(3.72, 0.67)] + sj[::-1] + [(3.72, -1.05)]
            back = [(3.72, 3.35)] + bj[::-1] + [(3.72, 0.2)]
        yaw = 7.0 if side > 0 else 0.0
        # asiento y respaldo como prismas alrededor de su centro (giran con la mitad)
        sc = (sum(x for x, _ in seat) / len(seat), 1.7, sum(z for _, z in seat) / len(seat))
        mk.prism(part, [(x - sc[0], z - sc[2]) for x, z in seat], 0.2, WOOD, plane="xz", center=tf(sc), rot=(0, yaw, 0))
        bc = (sum(x for x, _ in back) / len(back), sum(y for _, y in back) / len(back), 0.875)
        mk.prism(part, [(x - bc[0], y - bc[1]) for x, y in back], 0.25, WOOD, plane="xy", center=tf(bc),
                 rot=(0, yaw, 0))
        xa, xb = (-3.74, -0.75) if side < 0 else (0.75, 3.74)                           # tapa, más corta que la rotura
        mk.hull(part, [tf(p) for p in box_pts(xa, xb, 3.33, 3.5, 0.75, 1.13)], DARK, detail=True)
        # astillas: arrancan 0,15 adentro de la tabla, junto a la punta del zigzag, y salen 0,45 por la rotura
        jb = -0.3 + side * 0.12                                                        # punta del respaldo a y 2,3
        js = -0.45 + side * 0.12                                                       # punta del asiento a z -0,6
        for (xb, yb, zb, w, h), xt, yt, zt in (((jb + side * 0.15, 2.3, 0.875, 0.06, 0.1), jb - side * 0.45, 2.5, 0.9),
                                               ((js + side * 0.15, 1.7, -0.6, 0.05, 0.08), js - side * 0.5, 1.74, -0.52)):
            mk.hull(part, [tf((xb, yb + dy, zb + dz)) for dy in (-h, h) for dz in (-w, w)] + [tf((xt, yt, zt))],
                    FRESH, detail=True)


def build(mk):
    whole_pew(mk, "Pew", make_tf((0, 0, 0)))
    whole_pew(mk, "Pew_Toppled", make_tf((10.0, 1.18, 0), rot_x=90.0))
    broken_pew(mk, "Pew_Broken", 20.0)

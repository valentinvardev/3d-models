"""
Receta de WST_Mount_ZombieHorse, el caballo de los jinetes zombis (prompt 064, Bloques A + E + G).

Brief
- Mismo esqueleto que WST_Mount_Horse: importa sus constantes (pivotes, largos, ángulos) y sus patas,
  así comparten animaciones. 8 de largo, 4,4 en la cruz y en la grupa.
- Silueta que se lee a 40 studs: el mismo caballo pero en los huesos: barril 0,85 de ancho y ijares
  recogidos, cruz y espinazo filosos, puntas de cadera que salen, crin y cola en mechones con huecos,
  costillas blancas en el flanco izquierdo, dientes al aire.
- Superficie: pelo hide_black con peladas skin_dead (talladas poco profundas, no calcomanías),
  hueco de las costillas tallado (skin_dead_dark) con 4 costillas bone adentro, labios arrancados
  (encías blood_dry) con dientes, cuencas talladas con los ojos de plata adentro, oreja izquierda rota.
- Tack podrido: Acc_Saddle de leather_dark con el respaldo y un faldón quebrados, mandil rojo roto en
  zigzag, un solo estribo (el ación izquierdo cortado); Reins cortadas, colgando del freno y del cuerno.
- Plata viva (G): Silver_Eyes (en las cuencas) y Silver_Veins (vetas que salen del hueco de las
  costillas, pasan por el hombro y suben por el cuello, del tronco grueso a las puntas finas).
- Inferido: cantidad y lugar de las peladas (5), mechones de la crin (5) y de la cola (3), qué estribo
  falta, por dónde van las vetas.

Vueltas: 1) primera versión: 3896 triángulos, z-fighting en la cola y los dientes, orejas flotando
0,1 sobre la cabeza (la cabeza flaca es más baja; arreglado también en el caballo), 4 bordes abiertos
en el lomo (los dos cascos del torso casi tangentes rompían la booleana) · 2) cascos del lomo
cruzados con decisión, espinazo como cresta con nudos bajos (las púas sueltas parecían un dragón),
peladas más grandes y alargadas, muserola 0,05 afuera (coplanar con el puente de la caña nasal) ·
3) puntas de cadera con la base en el plano tangente (asomaba un cuadrado oscuro), menos tallados ·
4) filas de dientes separadas: se leía un bloque blanco; ahora dientes en zigzag con la encía oscura entre las filas.

Revisión
- 3686 triángulos contra 1800 de referencia (el doble). Todo se ve por defecto (no hay accesorios
  ocultos). El gasto está en lo que pide el prompt y se lee a distancia: cabeza 924 (cuencas, labios
  arrancados con dos filas de dientes e incisivos, ollares), torso 744 (hueco de costillas tallado,
  4 costillas, puntas de cadera, espinazo, peladas), montura rota 528, vetas 204. Si hay que bajarlo
  para muchos caballos en pantalla: sacar ollares, una pelada y la grieta del faldón da ~3300.
- Ancho 1,74: el barril flaco (0,85 × 2,0) más el estribo derecho.
- Mismo esqueleto que el caballo verificado: las patas se construyen con las funciones del caballo y
  los pivotes salen de sus constantes.
- Las vetas van en dos piezas para el rig (decidido sin Valentin el 2026-10-29, al riggear): Silver_Veins
  (costillas, hombro y cruz; va al Torso) y Silver_Veins_Neck (cuello, cresta y garganta; va al Neck).
- Reins cruza Torso/Neck/Head en un objeto y queda soldada al cuello, como en el caballo.
"""

import importlib.util
import math
from pathlib import Path

from mathutils import Vector

_spec = importlib.util.spec_from_file_location(
    "horse_recipe", Path(__file__).resolve().parents[2] / "WST_Mount_Horse" / "01_design" / "WST_Mount_Horse.build.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

NECK_B, ND, NU, POLL, HD, HU, TAIL_B = H.NECK_B, H.ND, H.NU, H.POLL, H.HD, H.HU, H.TAIL_B
THIN = 0.85
EGG = 0.36                               # más angosto arriba que el caballo: cruz y lomo filosos
# los dos cascos del lomo se cruzan con decisión (si se tocan casi tangentes, la booleana deja agujeros)
TORSO_FRONT = [(z, yb, yt, w * THIN) for z, yb, yt, w in H.TORSO_FRONT[:-1]] + [(0.30, 2.30, 4.10, 1.95 * THIN)]
TORSO_BACK = [(-0.40, 2.25, 4.10, 1.95 * THIN), (0.80, 2.60, 4.21, 1.95 * THIN), (1.60, 2.95, 4.40, 1.86 * THIN),
              (2.30, 3.05, 4.30, 1.74 * THIN), (2.75, 3.15, 4.12, 1.46 * THIN), (3.02, 3.32, 3.90, 0.92 * THIN)]
NECK_SECS = [(t, o, w * THIN, h * 0.88) for t, o, w, h in H.NECK_SECS]
HEAD_BACK = [(s, o, w * 0.92, h * 0.95) for s, o, w, h in H.HEAD_BACK]
HEAD_FRONT = [(s, o, w * 0.92, h * 0.95) for s, o, w, h in H.HEAD_FRONT]
neck_pt, head_pt, interp, asec, hring, lerp = H.neck_pt, H.head_pt, H.interp, H.asec, H.hring, H.lerp


def ttable():
    return sorted(TORSO_FRONT + TORSO_BACK[1:])


def tpt(z, deg, off=0.0):
    """Punto y normal de la superficie del torso flaco en z, a `deg` grados (90 lomo, 180 flanco izquierdo)."""
    yb, yt, w = interp(ttable(), z)
    a = math.radians(deg)
    s, c = math.sin(a), math.cos(a)
    k = 1 - EGG * s if s > 0 else 1 + 0.08 * s
    hw, hh = w / 2 * k, (yt - yb) / 2
    p = Vector(((hw + off) * c, (yb + yt) / 2 + (hh + off) * s, z))
    return p, Vector((c / hw, s / hh, 0)).normalized()


def nsurf(t, ang, off=0.0):
    """Punto y normal del cuello en t, a `ang` grados alrededor del eje (90 cresta, 180 costado izquierdo)."""
    o, w, h = interp(NECK_SECS, t)
    a = math.radians(ang)
    c = Vector(neck_pt(t, o))
    p = c + Vector(((w / 2 + off) * math.cos(a), 0, 0)) + NU * ((h / 2 + off) * math.sin(a))
    return p, (Vector((math.cos(a) / (w / 2), 0, 0)) + NU * (math.sin(a) / (h / 2))).normalized()


def neck_ring(t, n=10):
    o, w, h = interp(NECK_SECS, t)
    return asec(neck_pt(t, o), NU, w, h, n)


def head_half(s):
    o, w, h = interp(HEAD_BACK if s < 1.05 else HEAD_FRONT, s)
    return o, w / 2, h / 2


def frame(n):
    n = Vector(n).normalized()
    t1 = n.cross(Vector((0, 1, 0)))
    if t1.length < 0.2:
        t1 = n.cross(Vector((1, 0, 0)))
    t1.normalize()
    return n, t1, n.cross(t1).normalized()


def bald(mk, part, p, n, r, seed=0, depth=0.09, stretch=1.6):
    """Pelada: un tallado poco profundo, irregular y alargado; el fondo y las paredes toman skin_dead."""
    n, t1, t2 = frame(n)
    p = Vector(p)
    pts = []
    for i in range(6):
        a = 2 * math.pi * i / 6 + seed
        rr = r * (0.70 + 0.30 * ((i * 3 + seed * 5) % 4) / 3)
        ring = (t1 * math.cos(a) * stretch + t2 * math.sin(a)) * rr
        pts += [tuple(p + n * 0.10 + ring), tuple(p - n * depth + ring * 0.8)]
    mk.carve(part, "skin_dead", points=pts)


def vein(mk, part, path, w0, w1, thick=0.07, tip=True):
    """Veta de plata: tramos que siguen la superficie (puntos con normal), del tronco grueso a una punta.
    tip=False termina con el ancho w1, para seguirla en otra pieza."""
    n_seg = len(path) - 1
    for i in range(n_seg):
        (a, na), (b, nb) = path[i], path[i + 1]
        wa = lerp(w0, w1, i / n_seg)
        wb = lerp(w0, w1, (i + 1) / n_seg) if (i < n_seg - 1 or not tip) else 0.02
        d = (b - a).normalized()
        pts = []
        for p, nn, w in ((a - d * 0.02, na, wa), (b + d * 0.02, nb, wb)):
            across = d.cross(nn).normalized() * (w / 2)
            pts += [tuple(p + sa * across + st * nn * (thick / 2)) for sa in (-1, 1) for st in (-1, 1)]
        mk.hull(part, pts, "silver_neon")


def build(mk):
    # ---------------- torso flaco ----------------
    torso = mk.part("Torso", (0, 0, 0))
    mk.hull(torso, [p for z, yb, yt, w in TORSO_FRONT for p in H.vsec(z, yb, yt, w, egg=EGG)], "hide_black")
    mk.hull(torso, [p for z, yb, yt, w in TORSO_BACK[:4] for p in H.vsec(z, yb, yt, w, egg=EGG)], "hide_black")
    mk.hull(torso, [p for z, yb, yt, w in TORSO_BACK[2:] for p in H.vsec(z, yb, yt, w, n=12, egg=EGG)], "hide_black")
    # puntas de la cadera y espinazo filoso
    for s in (-1, 1):
        p, n = tpt(1.35, 90 - s * 52)
        n, t1, t2 = frame(n)                        # base en el plano tangente: hundida, no asoma
        base = [tuple(p - n * 0.12 + t1 * a + t2 * b) for a, b in ((-0.16, -0.13), (0.16, -0.13), (-0.12, 0.12), (0.12, 0.12))]
        mk.hull(torso, base + [tuple(p + n * 0.16 + Vector((0, 0.04, 0)))], "hide_black")
    ridge = [tpt(lerp(0.55, 2.60, i / 10), 90)[0] for i in range(11)]          # vértebras: cresta con nudos bajos
    prof = [(p.z, p.y + (0.07 if i % 2 else 0.03)) for i, p in enumerate(ridge)] + [(p.z, p.y - 0.12) for p in reversed(ridge)]
    mk.prism(torso, prof, 0.11, "hide_black", plane="zy", center=(0, 0, 0))
    # hueco de las costillas en el flanco izquierdo: borde de cuero roto en zigzag
    hole = ([(-0.62 + 0.187 * i, 3.70 - (0.10 if i % 2 else 0.0)) for i in range(7)]
            + [(0.52, 3.40), (0.46, 3.10)]
            + [(0.50 - 0.187 * i, 2.84 + (0.10 if i % 2 else 0.0)) for i in range(7)]
            + [(-0.66, 3.10), (-0.58, 3.40)])
    mk.carve(torso, "skin_dead_dark", prism=dict(profile=hole, depth=0.76, plane="zy", center=(-0.86, 0, 0)))
    for zr in (-0.42, -0.14, 0.14, 0.40):
        pts = []
        for deg, dz in ((140, -0.06), (178, 0.02), (214, 0.10)):
            for off in (-0.11, -0.26):
                p, _ = tpt(zr + dz, deg, off)
                pts += [tuple(p + Vector((0, 0, -0.045))), tuple(p + Vector((0, 0, 0.045)))]
        mk.hull(torso, pts, "bone", detail=True)
    # peladas
    for z, deg, r, seed in ((0.45, 14, 0.30, 1), (2.15, 140, 0.24, 2)):
        p, n = tpt(z, deg)
        bald(mk, torso, p, n, r, seed)

    # ---------------- cuello: crin rala en mechones ----------------
    neck = mk.part("Neck", tuple(NECK_B))
    mk.hull(neck, neck_ring(-0.40) + neck_ring(0.40) + neck_ring(1.30), "hide_black")
    mk.hull(neck, neck_ring(1.20) + neck_ring(2.05) + neck_ring(2.40), "hide_black")
    for i, (t0, t1) in enumerate(((-0.10, 0.28), (0.48, 0.80), (1.00, 1.24), (1.52, 1.92), (2.08, 2.30))):
        prof = []
        for j in range(4):
            t = lerp(t0, t1, j / 3)
            o, w, h = interp(NECK_SECS, t)
            prof.append(neck_pt(t, o + h / 2 + (0.20 if j in (1, 3) else 0.06) - 0.02 * (i % 2)))
        for t in (t1, t0):
            o, w, h = interp(NECK_SECS, t)
            prof.append(neck_pt(t, o + h / 2 - 0.16))
        mk.prism(neck, [(p[2], p[1]) for p in prof], 0.14 + 0.03 * (i % 2), "hide_black", plane="zy",
                 center=(0.03 * (1 - 2 * (i % 2)), 0, 0))
    p, n = nsurf(1.10, 12)
    bald(mk, neck, p, n, 0.20, 4, stretch=1.8)

    # ---------------- cabeza: labios arrancados, cuencas, oreja rota ----------------
    head = mk.part("Head", tuple(POLL))
    mk.hull(head, [p for s, *_ in HEAD_BACK for p in H.head_ring(HEAD_BACK, s)], "hide_black")
    mk.hull(head, [p for s, *_ in HEAD_FRONT for p in H.head_ring(HEAD_FRONT, s)], "hide_black")
    mk.hull(head, asec(head_pt(0.05, -0.30), HU, 0.74, 0.72, 10) + asec(head_pt(0.55, -0.30), HU, 0.64, 0.58, 10), "hide_black")
    mk.hull(head, asec(head_pt(1.78, -0.20), HU, 0.40, 0.22, 8) + asec(head_pt(2.10, -0.20), HU, 0.34, 0.20, 8), "hide_black")
    for s in (-1, 1):                                    # pómulos filosos
        mk.hull(head, [head_pt(0.45, 0.22, s * 0.28), head_pt(0.82, 0.22, s * 0.26), head_pt(0.55, 0.30, s * 0.37),
                       head_pt(0.75, 0.28, s * 0.35), head_pt(0.62, 0.08, s * 0.38), head_pt(1.00, -0.05, s * 0.29)], "hide_black")
    # oreja derecha entera, izquierda rota (punta arrancada, borde en escalón)
    base = [head_pt(0.02 + dz, 0.22, 0.20 + dx) for dz, dx in ((-0.10, -0.07), (-0.10, 0.07), (0.10, 0.07), (0.10, -0.07))]
    mk.hull(head, base + [head_pt(-0.02, 0.92, 0.30), head_pt(0.04, 0.80, 0.30)], "hide_black")
    base = [head_pt(0.02 + dz, 0.22, -0.20 + dx) for dz, dx in ((-0.10, -0.07), (-0.10, 0.07), (0.10, 0.07), (0.10, -0.07))]
    mk.hull(head, base + [head_pt(-0.06, 0.66, -0.29), head_pt(0.06, 0.58, -0.27), head_pt(0.0, 0.62, -0.31)], "hide_black")
    mk.paint(head, "skin_dead_dark", ball=(head_pt(0.0, 0.64, -0.29), 0.10))
    # cuencas y ollares
    for s in (-1, 1):
        mk.carve(head, "skin_dead_dark", points=mk.pts_ball(head_pt(0.62, 0.14, s * 0.36), 0.13, scale=(0.8, 1.0, 1.2), subdiv=0))
        mk.carve(head, "coal", points=mk.pts_ball(head_pt(2.13, 0.06, s * 0.15), 0.065, scale=(0.8, 1.2, 1.0), subdiv=0))
    # labios arrancados: costados y frente; las paredes son encía
    for s in (-1, 1):
        lens = [(1.58, -0.14), (1.95, -0.01), (2.40, -0.01), (2.40, -0.28), (1.95, -0.29)]
        mk.carve(head, "blood_dry", points=[head_pt(ss, o, s * x) for ss, o in lens for x in (0.165, 0.50)])
    mk.carve(head, "blood_dry", points=[head_pt(ss, o, x) for ss in (2.06, 2.50) for o in (-0.27, -0.02) for x in (-0.17, 0.17)])
    # dientes: una tira en zigzag por fila (costados) y los incisivos adelante
    for s in (-1, 1):
        up_ = [(1.66, 0.03), (2.22, 0.03)] + [(2.22 - 0.093 * i, -0.125 if i % 2 == 0 else -0.06) for i in range(7)]
        lo_ = [(1.70, -0.30), (2.22, -0.30)] + [(2.22 - 0.087 * i, -0.165 if i % 2 == 0 else -0.225) for i in range(7)]
        for prof, depth, cx in ((up_, 0.08, 0.175), (lo_, 0.07, 0.168)):     # filas con espesor distinto: no coplanares
            pts2 = [head_pt(ss, o) for ss, o in prof]
            mk.prism(head, [(p[2], p[1]) for p in pts2], depth, "bone", plane="zy", center=(s * cx, 0, 0), detail=True)
    inc_up = [(-0.14, 0.02), (0.14, 0.02)] + [(0.14 - 0.035 * i, -0.125 if i % 2 == 0 else -0.07) for i in range(9)]
    inc_lo = [(-0.13, -0.31), (0.13, -0.31)] + [(0.13 - 0.0325 * i, -0.165 if i % 2 == 0 else -0.22) for i in range(9)]
    for prof, depth in ((inc_up, 0.12), (inc_lo, 0.10)):
        mk.prism(head, prof, depth, "bone", plane="xy", center=head_pt(2.13), rot=(-H.HEAD_ANG, 0, 0), detail=True)
    # restos de la cabezada: muserola y anillas del freno (de ahí cuelgan las riendas cortadas)
    # (el casco de la cara puentea el hueco de la caña nasal: la muserola va 0,05 afuera para no quedar coplanar)
    mk.hull(head, H.head_ring(HEAD_FRONT, 1.32, grow=0.05) + H.head_ring(HEAD_FRONT, 1.42, grow=0.05), "leather_dark", detail=True)
    for s in (-1, 1):
        mk.cyl(head, head_pt(1.50, -0.14, s * 0.27), 0.08, 0.04, "iron", axis="x", sides=6, detail=True)

    eyes = mk.part("Silver_Eyes", tuple(POLL))
    for s in (-1, 1):
        mk.ball(eyes, head_pt(0.62, 0.14, s * 0.27), 0.085, "silver_neon", scale=(0.8, 1.0, 1.2), subdiv=0)

    # ---------------- cola rala: muñón y tres mechones con huecos ----------------
    tail = mk.part("Tail", TAIL_B)
    tx, ty, tz = TAIL_B
    mk.hull(tail, hring(ty + 0.08, 0, tz - 0.08, 0.26, 0.26) + hring(ty - 0.35, 0, tz + 0.20, 0.24, 0.24), "hide_black")
    for i, (dx, dz, y_end, w) in enumerate(((-0.09, 0.30, 1.75, 0.14), (0.07, 0.38, 2.30, 0.12), (0.02, 0.26, 1.45, 0.11))):
        mk.hull(tail, hring(ty - 0.24 - 0.05 * i, dx * 0.4, tz + 0.18, w, w, n=6) + hring(lerp(ty - 0.28, y_end, 0.6), dx, tz + dz, w * 0.9, w * 0.8, n=6)
                + [(dx * 1.4, y_end, tz + dz + 0.03)], "hide_black")

    # ---------------- patas (las del caballo, flacas) ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        up, _ = H.front_leg(mk, side, s, "hide_black", "hide_black", "coal", thin=0.88)
        up2, _ = H.back_leg(mk, side, s, "hide_black", "hide_black", "coal", thin=0.88)
        if side == "Right":
            bald(mk, up, (s * H.FX + 0.17, 2.15, H.FRONT_Z), (1, 0, -0.3), 0.15, 6, depth=0.06)
        else:
            bald(mk, up2, (s * H.HX - 0.24, 2.75, H.HIND_Z + 0.08), (-1, 0, 0.2), 0.17, 7, depth=0.06)

    # ---------------- montura podrida ----------------
    saddle = mk.part("Acc_Saddle", (0, 4.15, -0.15))
    mk.hull(saddle, [tuple(tpt(z, d, 0.07)[0]) for z in (-0.98, -0.45, 0.10, 0.62) for d in range(8, 173, 18)], "paint_red")
    mk.hull(saddle, [tuple(tpt(z, d, 0.12)[0]) for z in (-0.80, -0.30, 0.20, 0.50) for d in range(26, 155, 16)], "leather_dark")
    mk.hull(saddle, [(-0.34, 4.38, -0.88), (0.34, 4.38, -0.88), (-0.22, 4.68, -0.80), (0.22, 4.68, -0.80),
                     (-0.38, 4.38, -0.50), (0.38, 4.38, -0.50), (-0.17, 4.64, -0.60), (0.17, 4.64, -0.60)], "leather_dark")
    mk.hull(saddle, [(x, y, z) for x in (-0.40, 0.40) for y, z in ((4.34, -0.60), (4.34, 0.40), (4.45, -0.30), (4.45, 0.15))]
            + [(x, 4.44, z) for x in (-0.28, 0.28) for z in (-0.62, 0.42)], "leather_dark")
    mk.hull(saddle, [(-0.44, 4.36, 0.28), (0.44, 4.36, 0.28), (-0.44, 4.36, 0.52), (0.44, 4.36, 0.52),
                     (-0.36, 4.78, 0.50), (0.36, 4.78, 0.50), (-0.28, 4.80, 0.62), (0.28, 4.80, 0.62)], "leather_dark")
    mk.cyl(saddle, (0, 4.78, -0.80), 0.06, 0.30, "leather_dark", sides=6)
    mk.cyl(saddle, (0, 4.94, -0.81), 0.13, 0.06, "leather_dark", sides=6)
    # roturas: el mandil en zigzag, un pedazo del respaldo, la esquina de un faldón, una grieta en el asiento
    torn = [(-1.2, 3.0), (0.9, 3.0)] + [(0.9 - 0.2625 * i, 3.40 if i % 2 == 0 else 3.58) for i in range(9)]
    mk.carve(saddle, "paint_red", prism=dict(profile=torn, depth=3.0, plane="zy", center=(0, 0, 0)))
    mk.carve(saddle, "wood_dark", points=mk.pts_box((0.36, 4.80, 0.56), (0.30, 0.34, 0.40), rot=(0, 0, 35)))
    mk.carve(saddle, "coal", points=[(x, y, z) for x in (-1.4, -0.75) for y, z in ((3.55, 0.65), (3.55, 0.20), (3.95, 0.65))])
    # ación derecho con su estribo; el izquierdo cortado. El estribo va 0,25 más afuera y 0,14 más arriba que en el
    # caballo, donde cae el pie del jinete zombie montado (ZombieRider_Ride, 2026-10-29): el ación baja abierto.
    for s in (-1, 1):
        top, _ = tpt(-0.20, 40, 0.14)
        tx_ = s * top.x
        out, up = (0.25, 0.14) if s > 0 else (0.0, 0.0)
        bottom = 2.62 + up if s > 0 else 3.20
        mk.hull(saddle, [(tx_ + s * dx, y, z) for dx, y in ((0.0, 3.95), (0.06, 3.95), (0.18 + out, bottom), (0.24 + out, bottom))
                         for z in (-0.38, -0.04)], "leather_dark", detail=True)
        if s > 0:
            sx = tx_ + 0.21 + out
            stir = [(-0.22, 0.0), (0.22, 0.0), (0.18, 0.32), (0.10, 0.36), (0.10, 0.08), (-0.10, 0.08), (-0.10, 0.36), (-0.18, 0.32)]
            mk.prism(saddle, [(-0.21 + a, 2.24 + up + b) for a, b in stir], 0.16, "wood_dark", plane="zy", center=(sx, 0, 0), detail=True)
            mk.box(saddle, (sx, 2.58 + up, -0.21), (0.10, 0.10, 0.22), "leather_dark", detail=True)
        else:
            for k in range(3):                           # punta deshilachada
                z0 = -0.38 + 0.115 * k
                mk.prism(saddle, [(z0, bottom + 0.02), (z0 + 0.11, bottom + 0.02), (z0 + 0.05, bottom - 0.16)], 0.05,
                         "leather_dark", plane="zy", center=(tx_ - 0.21, 0, 0), detail=True)
    mk.marker("_Seat", (0, 4.48, -0.10))

    # ---------------- riendas cortadas, colgando ----------------
    reins = mk.part("Reins", (0, 0, 0))
    bl, br = Vector(head_pt(1.50, -0.14, -0.30)), Vector(head_pt(1.50, -0.14, 0.30))
    H.strap(mk, reins, [bl, bl + Vector((-0.04, -0.45, 0.10)), bl + Vector((-0.06, -0.95, 0.22))], 0.07, 0.04, "leather_dark")
    p1, _ = nsurf(1.85, 0, 0.06)
    H.strap(mk, reins, [br, p1, p1 + Vector((0.05, -0.55, 0.12))], 0.07, 0.04, "leather_dark")
    p2, _ = tpt(-1.25, 160, 0.10)
    H.strap(mk, reins, [Vector((-0.07, 4.78, -0.80)), Vector((-0.42, 4.55, -0.95)), p2, p2 + Vector((-0.06, -0.50, 0.05))],
            0.07, 0.04, "leather_dark")

    # ---------------- plata viva: vetas del hueco de las costillas al cuello ----------------
    # dos piezas, partidas en la base del cuello, para que en el rig cada tramo siga a lo suyo: Silver_Veins va
    # al Torso y Silver_Veins_Neck al Neck. El tramo del cuello es 0,02 más grueso: donde se enciman no quedan
    # caras coplanares.
    veins = mk.part("Silver_Veins", (0, 0, 0))
    veins_n = mk.part("Silver_Veins_Neck", tuple(NECK_B))
    trunk = [tpt(-0.66, 176), tpt(-1.00, 170), tpt(-1.42, 164), nsurf(0.35, 188), nsurf(0.95, 182), nsurf(1.55, 176),
             nsurf(2.10, 184)]
    vein(mk, veins, trunk[:4], 0.13, 0.10, tip=False)
    vein(mk, veins_n, trunk[3:], 0.10, 0.06, thick=0.09)
    vein(mk, veins, [tpt(-1.00, 170), tpt(-1.14, 150), tpt(-1.28, 132)], 0.08, 0.04)          # hacia la cruz
    vein(mk, veins, [tpt(-0.66, 202), tpt(-0.98, 214), tpt(-1.22, 226)], 0.09, 0.04)          # hacia el codo
    vein(mk, veins_n, [nsurf(0.95, 182), nsurf(1.18, 156), nsurf(1.34, 138)], 0.08, 0.04)     # hacia la cresta
    vein(mk, veins_n, [nsurf(1.55, 176), nsurf(1.78, 204), nsurf(1.95, 220)], 0.07, 0.03)     # hacia la garganta
    vein(mk, veins, [tpt(-0.66, 160), tpt(-0.30, 142), tpt(0.10, 136), tpt(0.45, 130)], 0.08, 0.03)  # sobre el hueco, hacia atrás

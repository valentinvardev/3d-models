"""
Receta de WST_Weapon_Dynamite, dinamita: cartucho suelto y atado de tres (prompt 026, Bloques A + F).

Brief
- Dos variantes en el mismo archivo, una al lado de la otra sobre X (como las balas sueltas): el cartucho
  en x = -0,3 y el atado en x = +0,3. Cada cuerpo con el origen en su centro, eje largo en Z y la mecha
  saliendo por +Z.
- Silueta a 30 studs: un cilindro rojo gordo con una banda crema al medio y una mecha clara doblada para
  arriba con la punta quemada. El atado: tres cartuchos en triángulo, dos vueltas de hilo y una mecha
  gruesa retorcida.
- Medidas: cartucho 0,55 x 0,15 de diámetro, 8 lados; mecha 0,3 en 3 tramos doblando 40° en total;
  mecha del atado 0,4 en 4 tramos, de sección cuadrada girada en cada tramo (se lee retorcida).
- Piezas: Stick, Fuse_Stick, Bundle, Fuse_Bundle. La mecha lleva el origen donde sale del cartucho (para
  acortarla mientras se quema). Marcadores _Fuse_Stick y _Fuse_Bundle en la punta de cada mecha.
- Banda crema cortada con `slice` y pintada: queda al ras, lisa para la calcomanía, sin cajita encima.
- Chanflán solo en los bordes de las puntas (ángulo 50: los 45° entre caras del octógono no se tocan).

Inferido (el prompt no lo dice)
- Nombres: Blender no deja dos objetos "Fuse" ni dos "_Fuse" en el mismo archivo; van con el sufijo de la
  variante (Fuse_Stick, _Fuse_Stick...). Los cuerpos se llaman Stick y Bundle.
- Punta de la mecha quemada (coal) para que se lea dónde va la chispa; la mecha dobla hacia arriba (+Y).
- Grosor de la mecha 0,05 (cartucho) y 0,06 (atado): más fina no se ve a distancia.

Vueltas: 1) primera versión: la punta quemada pintada con una bola solo teñía la cara del extremo (no se
veía de costado); el atado tenía tres bocas talladas tapadas por las hebras (~80 triángulos que nadie ve) ·
2) punta quemada de 0,045 cortada con `slice` y pintada; bocas del atado sacadas; z-fighting entre tramos
de la mecha: con el mismo marco, las caras a ±X de dos tramos seguidos quedaban en el mismo plano ·
3) los tramos de la mecha con una arista (no una cara) en ±X.

Revisión
- Cartucho 190 triángulos (118 + mecha 72) y atado 468 (364 + mecha 104) contra 120 por variante: el
  chanflán de las puntas (lo que agarra luz al girar en el aire), la banda cortada para la calcomanía y la
  mecha retorcida. Sin chanflanes el atado baja a ~250 y se ve de caños.
- Los dos cuerpos están separados a propósito (dos variantes en un archivo); la revisión no los marca como
  flotando porque cada uno tiene su origen propio.
- Nombres con sufijo de variante: si Valentin prefiere dos archivos (WST_Weapon_Dynamite_Stick y
  WST_Weapon_Dynamite_Bundle, cada uno con Fuse y _Fuse), la receta se parte en dos sin cambiar la forma.
"""

import math

from mathutils import Vector

STICK_X, BUNDLE_X = -0.3, 0.3
L, R = 0.55, 0.075


def frame(d):
    """Dos vectores perpendiculares a d (dirección de un tramo)."""
    d = Vector(d).normalized()
    up = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    return u, d.cross(u).normalized()


def tube(mk, part, a, b, r, mat, sides=6, phase=0.0, ext=0.0):
    """Tramo de cuerda de a a b (casco de dos anillos), estirado `ext` en cada punta para cubrir el codo."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    a, b = a - d * ext, b + d * ext
    u, v = frame(d)
    pts = []
    for c in (a, b):
        for i in range(sides):
            t = phase + 2 * math.pi * (i + 0.5) / sides
            pts.append(tuple(c + u * (r * math.cos(t)) + v * (r * math.sin(t))))
    mk.hull(part, pts, mat)


def bend(start, seg, angles):
    """Polilínea que sale por +Z y dobla hacia +Y: un ángulo (grados) por tramo."""
    pts = [Vector(start)]
    for ang in angles:
        a = math.radians(ang)
        pts.append(pts[-1] + Vector((0, math.sin(a), math.cos(a))) * seg)
    return pts


def burnt(mk, part, pts, r):
    """Punta quemada: corta la mecha a 0,045 de la punta y pinta ese tramo de carbón."""
    tip, prev = pts[-1], pts[-2]
    d = (tip - prev).normalized()
    cut = tip - d * 0.045
    mk.slice(part, tuple(cut), tuple(d))
    mk.paint(part, "coal", ball=(tuple(tip - d * 0.01), r + 0.03))


def stick_body(mk, part, x, y, sides=8):
    mk.cyl(part, (x, y, 0), R, L, "dynamite_red", axis="z", sides=sides)


def build(mk):
    # ---------------- variante 1: cartucho ----------------
    stick = mk.part("Stick", (STICK_X, 0, 0))
    stick_body(mk, stick, STICK_X, 0)
    mk.bevel(stick, width=0.014, angle=50)
    for z in (-0.06, 0.06):                                                    # banda crema al ras
        mk.slice(stick, (STICK_X, 0, z), (0, 0, 1))
    mk.paint(stick, "paint_cream", box=((STICK_X, 0, 0), (0.3, 0.3, 0.12)))
    mk.carve(stick, "coal", points=mk.pts_cyl((STICK_X, 0, L / 2), 0.03, 0.04, axis="z", sides=6))  # boca de la mecha

    base = (STICK_X, 0, L / 2 - 0.03)
    fuse = mk.part("Fuse_Stick", base)
    pts = bend(base, 0.11, (0, 20, 40))
    for k in range(3):
        tube(mk, fuse, pts[k], pts[k + 1], 0.025, "rope", sides=6, phase=-math.pi / 6, ext=0.006)  # arista en X: sin caras paralelas entre tramos
    burnt(mk, fuse, pts, 0.025)
    mk.marker("_Fuse_Stick", tuple(pts[-1]))

    # ---------------- variante 2: atado de tres ----------------
    bundle = mk.part("Bundle", (BUNDLE_X, 0, 0))
    ring_r = 0.083                                                             # se encastran 0,006
    centers = [(BUNDLE_X + ring_r * math.cos(math.radians(a)), ring_r * math.sin(math.radians(a)), 0)
               for a in (90, 210, 330)]
    for cx, cy, _ in centers:
        stick_body(mk, bundle, cx, cy)
    mk.bevel(bundle, width=0.012, angle=50)
    for z in (-0.06, 0.06):
        mk.slice(bundle, (BUNDLE_X, 0, z), (0, 0, 1))
    mk.paint(bundle, "paint_cream", box=((BUNDLE_X, 0, 0), (0.5, 0.5, 0.12)))
    for zc in (-0.17, 0.17):                                                   # dos vueltas de hilo
        ring = []
        for cx, cy, _ in centers:
            for k in range(4):
                a = math.atan2(cy, cx - BUNDLE_X) + math.radians(-60 + 40 * k)
                rr = R + 0.012
                for dz in (-0.018, 0.018):
                    ring.append((cx + rr * math.cos(a), cy + rr * math.sin(a), zc + dz))
        mk.hull(bundle, ring, "rope", detail=True)

    joint = (BUNDLE_X, 0, L / 2 + 0.07)
    fb = mk.part("Fuse_Bundle", joint)
    for cx, cy, _ in centers:                                                  # tres hebras que se juntan
        tube(mk, fb, (cx, cy, L / 2 - 0.02), joint, 0.018, "rope", sides=5, ext=0.01)
    pts = bend(joint, 0.1, (5, 20, 35, 45))
    for k in range(4):                                                         # mecha retorcida
        tube(mk, fb, pts[k], pts[k + 1], 0.032, "rope", sides=4, phase=math.radians(25 * k), ext=0.018)
    burnt(mk, fb, pts, 0.032)
    mk.marker("_Fuse_Bundle", tuple(pts[-1]))

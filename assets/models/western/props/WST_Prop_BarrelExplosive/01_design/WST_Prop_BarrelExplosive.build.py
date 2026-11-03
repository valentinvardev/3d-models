"""
Receta de WST_Prop_BarrelExplosive, el barril de pólvora (prompt 019, Bloques A + C).

Brief
- Tiene que distinguirse del barril común solo por silueta y color (el brillo es VFX y en celular puede
  ir reducido). A 40 studs: barril casi todo rojo de advertencia con las puntas oscuras, una placa clara
  al frente, un cartucho de dinamita que asoma del costado derecho (+X) y una mecha arriba.
- Misma forma, medidas y fragmentos que WST_Prop_Barrel: se importa barrel() de su receta (2,2 de panza,
  1,9 en las puntas, 3,0 de alto, 10 lados, aros a 16/50/81 %, tapa hundida 0,1; frag01-04 la pared en
  gajos por las juntas, frag05 tapa, frag06 fondo).
- Diferencias: duelas wood_dark (más oscuras que el común), juntas y tablas de la tapa en iron, franja
  warning_red pintada entre el aro de abajo y el de arriba (el borde del color queda bajo los aros),
  placa paint_cream 0,8 x 0,6 al frente (para la calavera o "XXX" en calcomanía), cartucho de dinamita
  atado con dos vueltas de soga en +X, mecha de 3 tramos enroscada que sale del tapón.
- Piezas: la placa va con frag01 (gajo del frente, centrado en -Z), la dinamita con frag02 (gajo de +X),
  la mecha con frag05 (tapa).
- Inferido: la franja cubre todo lo que hay entre los aros de las puntas (el prompt dice "around the whole
  middle between the hoops"); placa a la altura del tramo de arriba; dinamita 1,0 x 0,26 (agrandada para
  leerse, con la faja crema del cartucho del arma); tapón de hierro; sin grieta ni canto mellado (el
  peligro no se mezcla con desgaste).

Vueltas: 1) 1012 tris; placa 0,11 afuera; cartucho vertical con 0,045 de luz arriba (la panza se angosta)
· 2) ataduras como cajas de 0,34 que sobresalían 0,04 a cada lado (se leían como repisas): ahora anillos
de soga alrededor del cartucho; mechas de 4 lados; cartucho inclinado con la panza · 3) se sacó el
repintado de las caras de corte (dejaba un triángulo rojo a medias).

Revisión
- 992 triángulos contra 350 de referencia: 746 del cuerpo compartido con el barril (ver su receta) y ~250
  de lo que lo hace peligroso (cartucho con faja y ataduras, dos mechas, placa).
- Las caras de corte dentro de la franja quedan rojas: `paint` elige por el centro de cada triángulo y los
  triángulos del corte no se separan de las duelas con cajas ni bolas (margen medido de 0,03). Solo se ven
  cuando explota.
- Alto 3,25 con la mecha (el cuerpo mide 3,0). Ancho 2,47 con el cartucho.
- A 96 px se distingue del común por color (rojo con puntas oscuras) y silueta (cartucho al costado,
  mecha arriba, placa clara).
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "barrel_base", Path(__file__).resolve().parents[2] / "WST_Prop_Barrel" / "01_design" / "WST_Prop_Barrel.build.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

BAND = ("warning_red", B.HOOPS[0], B.HOOPS[2])     # el borde del color cae debajo de los aros de las puntas
STICK_R = 0.13


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def chain(mk, part, pts, r, mat, sides=4):
    """Cuerda de tramos rectos; cada tramo se pasa r*0,8 de la junta para que la curva no abra."""
    for a, b in zip(pts, pts[1:]):
        d = [b[i] - a[i] for i in range(3)]
        n = sum(c * c for c in d) ** 0.5
        e = [c / n * r * 0.8 for c in d]
        B.tube(mk, part, tuple(a[i] - e[i] for i in range(3)), tuple(b[i] + e[i] for i in range(3)), r, mat,
               sides=sides)


def build(mk):
    parts = B.barrel(mk, wall="wood_dark", seam="iron", hoop="iron", lid_mat="wood_dark", lid_seam="iron",
                     bung="iron", band=BAND)
    front, right, _, _ = parts["walls"]

    # ---- placa de advertencia al frente (tramo de arriba, entre el aro del medio y el de arriba) ----
    zf = -B.R_BELLY * 0.951                        # cara de la duela del frente en la panza
    mk.box(front, (0, 1.96, zf - 0.045 + 0.085), (0.8, 0.6, 0.17), "paint_cream", detail=True)   # 0,045 afuera

    # ---- cartucho de dinamita atado en +X, sobre la junta de las dos duelas, inclinado con la panza ----
    y0, y1 = 1.5, 2.5
    a = (B.radius(y0) + STICK_R - 0.04, y0, 0.0)
    b = (B.radius(y1) + STICK_R - 0.04, y1, 0.0)
    B.tube(mk, right, a, b, STICK_R, "dynamite_red", sides=8)
    B.tube(mk, right, lerp(a, b, 0.36), lerp(a, b, 0.64), STICK_R + 0.012, "paint_cream", sides=8)   # faja
    for t in (0.17, 0.83):                                                              # dos vueltas de soga
        B.tube(mk, right, lerp(a, b, t - 0.045), lerp(a, b, t + 0.045), STICK_R + 0.03, "rope", sides=8)
    chain(mk, right, [b, (b[0] - 0.04, y1 + 0.16, 0.06)], 0.04, "rope")                # mecha corta

    # ---- mecha de la tapa: sale del tapón y se enrosca en 3 tramos ----
    top = B.H - B.LID_INSET
    chain(mk, parts["lid"], [(0.42, top + 0.02, 0.0), (0.47, top + 0.2, -0.06), (0.36, top + 0.3, -0.18),
                             (0.20, top + 0.26, -0.12)], 0.05, "rope")

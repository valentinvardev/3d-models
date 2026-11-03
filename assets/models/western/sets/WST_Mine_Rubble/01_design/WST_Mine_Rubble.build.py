"""
Receta de WST_Mine_Rubble, los escombros del techo que quedan como cobertura (prompt 107, Bloques A + B).
El Capataz derrumba partes del techo y los escombros forman coberturas nuevas.

Brief
- Silueta a 40 studs: montones de lajas angulosas grises y rojo oscuro sobre una pollera de polvo claro;
  el bajo se lee como cobertura para agacharse, el alto como pared, y el de la viga tiene un tirante roto
  clavado en diagonal.
- Medidas (origen abajo al centro de cada pieza): Rubble_Low 6 x 2,5 x 3 (x, alto, z), Rubble_High
  5 x 4,5 x 3, Rubble_Beam 5 x 3 x 3,5 con la viga de 0,6 que sale a 30° hasta ~4,6 de alto,
  FallingChunk una laja convexa de ~3 x 2,3 x 2,6.
- Construcción: cada montón es un núcleo gris chico (casco bajo) que tapa los huecos entre las lajas, 6-8 lajas
  (cajas con las esquinas metidas al azar, como las de WST_Mine_Tunnel) apoyadas encima y a los costados,
  y una pollera de polvo (sand) de 0,2 que asoma 0,15 alrededor. Colisión de casco convexo: cada montón es
  aproximadamente convexo.
- Inferido: las alturas exactas de cada laja, el reparto de colores, la pollera de polvo, el largo de la
  viga y su astilla, el origen de la laja que cae en su base.

Vueltas: 1) el núcleo rojo era más grande que las lajas: los montones se leían como bultos rojos con dos
o tres piedras encima · 2) núcleo gris al 70 %, lajas más grandes; el alto medía 6,1 x 5,05 x 3,8 ·
3) lajas del alto acercadas al centro y la de arriba más baja; pollera de polvo más chica.

Revisión
- Triángulos por pieza contra 400: Rubble_Low 214, Rubble_High 230, Rubble_Beam 220, FallingChunk 18.
- Medidas con la pollera de polvo: Low 6,34 x 2,50 x 3,18; High 5,57 x 4,48 x 3,19 (las piedras solas,
  ~5,1 de ancho: el 11 % de más en x es la pollera chata); Beam 5,82 x 3,93 x 3,89 con la viga;
  FallingChunk 3,29 x 2,50 x 3,26.
- FallingChunk no toca nada (cae del techo): el aviso de "pieza suelta" es esperado. Su origen está en la
  base (Bloque A); en Studio el centro de masa lo calcula el motor.
- El punto más bajo (-0,21) son lajas metidas en el piso.
"""

import importlib.util
import math
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "mine_tunnel", Path(__file__).resolve().parents[2] / "WST_Mine_Tunnel" / "01_design" / "WST_Mine_Tunnel.build.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

ROCK, ROCK2, DUST, WOOD, FRESH = "stone_grey", "redrock_dark", "sand", "wood_dark", "wood_light"


def dust(mk, part, ox, w, d, seed):
    """Pollera de polvo: anillo irregular en el piso y otro más chico a 0,2."""
    r = T.Rng(seed)
    pts = []
    for k in range(12):
        a = 2 * math.pi * (k + 0.3 * r.u()) / 12
        f = 0.92 + 0.16 * r.u()
        pts.append((ox + w / 2 * f * math.cos(a), 0.0, d / 2 * f * math.sin(a)))
        pts.append((ox + w / 2 * 0.8 * f * math.cos(a), 0.18 + 0.06 * r.u(), d / 2 * 0.8 * f * math.sin(a)))
    mk.hull(part, pts, DUST)


def core(mk, part, ox, w, h, d, seed):
    """Núcleo chico y achatado, gris (tapa lo que se vería entre las lajas sin verse como un bulto)."""
    r = T.Rng(seed)
    pts = []
    for y, s in ((0.1, 0.92), (h * 0.55, 0.72), (h * 0.92, 0.32)):
        for k in range(8):
            a = 2 * math.pi * (k + 0.4 * r.u()) / 8
            pts.append((ox + w / 2 * s * math.cos(a) * (0.9 + 0.2 * r.u()), y, d / 2 * s * math.sin(a) * (0.9 + 0.2 * r.u())))
    mk.hull(part, pts, ROCK)


def pile(mk, name, ox, w, h, d, slabs, seed, grow=1.1, pull=1.0):
    p = mk.part(name, (ox, 0, 0))
    dust(mk, p, ox, w + 0.3, d + 0.3, seed)
    core(mk, p, ox, w * 0.72, h * 0.78, d * 0.66, seed + 1)
    for i, (c, size, rot) in enumerate(slabs):
        size = tuple(v * grow for v in size)
        T.chunk(mk, p, (ox + c[0] * pull, c[1], c[2] * pull), size, seed * 10 + i, rot=rot, mat=ROCK2 if i % 3 == 1 else ROCK, detail=False)
    return p


def build(mk):
    # bajo: cobertura para agacharse
    pile(mk, "Rubble_Low", 0.0, 6.0, 2.5, 3.0, [
        ((-1.9, 0.6, -0.4), (2.0, 1.2, 1.8), (6, 20, -8)), ((0.2, 0.7, 0.5), (2.4, 1.3, 1.9), (-5, -15, 6)),
        ((2.2, 0.55, -0.2), (1.8, 1.1, 1.7), (8, 40, 10)), ((-0.6, 1.6, -0.3), (2.0, 1.0, 1.6), (12, 60, -14)),
        ((1.2, 1.7, 0.1), (1.6, 0.9, 1.4), (-10, 10, 12)), ((-2.4, 0.4, 0.9), (1.1, 0.8, 1.0), (0, 30, 4)),
        ((2.6, 0.35, 1.0), (1.0, 0.7, 0.9), (4, 70, -6))], 3, grow=1.02, pull=0.95)
    # alto: cobertura completa
    pile(mk, "Rubble_High", 8.0, 5.0, 4.5, 3.0, [
        ((-1.4, 0.8, -0.3), (2.2, 1.6, 2.0), (6, 15, -6)), ((1.3, 0.8, 0.3), (2.2, 1.6, 2.0), (-6, -20, 8)),
        ((-0.2, 2.0, 0.1), (2.6, 1.6, 2.1), (10, 45, 4)), ((-1.2, 3.2, -0.2), (1.8, 1.3, 1.6), (-8, 70, -12)),
        ((0.9, 3.3, 0.2), (1.7, 1.3, 1.5), (14, -30, 10)), ((0.0, 3.75, 0.0), (1.4, 1.0, 1.3), (5, 20, -18)),
        ((-2.1, 0.4, 0.9), (1.0, 0.8, 1.0), (0, 30, 4)), ((2.1, 0.45, -0.9), (1.1, 0.9, 1.0), (4, 70, -6))], 7,
        grow=0.95, pull=0.72)
    # con la viga rota: montón de 5 x 3 y un tirante que sale a 30°
    p = pile(mk, "Rubble_Beam", 15.0, 5.0, 3.0, 3.5, [
        ((-1.5, 0.7, -0.2), (2.0, 1.4, 1.9), (6, 25, -6)), ((1.0, 0.75, 0.5), (2.2, 1.5, 2.0), (-6, -20, 8)),
        ((-0.1, 1.9, 0.0), (2.2, 1.2, 1.9), (12, 50, 4)), ((1.6, 1.8, -0.6), (1.4, 1.0, 1.3), (-10, 20, 12)),
        ((-1.9, 0.4, 1.1), (1.0, 0.8, 1.0), (0, 30, 4)), ((2.0, 0.4, -1.2), (1.0, 0.7, 1.0), (4, 70, -6))], 11)
    a = math.radians(30)
    L = 5.2
    x0, y0, z0 = 15.0 - 1.6, 0.9, 0.3                       # pie de la viga, adentro del montón
    x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
    t = 0.3
    mk.hull(p, [(x, y + dy, z0 + dz) for x, y in ((x0, y0), (x1 - 0.25, y1 - 0.15)) for dy in (-t, t) for dz in (-t, t)],
            WOOD, detail=True)
    # punta astillada: dos astillas claras que salen de la cara del corte
    for i, (dy, dz, ln) in enumerate(((0.12, -0.1, 0.5), (-0.14, 0.12, 0.32))):
        base = [(x1 - 0.32, y1 - 0.15 + dy + sy * 0.12, z0 + dz + sz * 0.12) for sy in (-1, 1) for sz in (-1, 1)]
        tip = (x1 - 0.32 + ln * math.cos(a), y1 - 0.15 + dy + ln * math.sin(a), z0 + dz)
        mk.hull(p, base + [tip], FRESH, detail=True)
    # la laja que cae del techo
    f = mk.part("FallingChunk", (21.5, 0, 0))
    mk.hull(f, T.chunk_pts((21.5, 1.15, 0.0), (3.0, 2.3, 2.6), 905, rot=(8, 25, -6)), ROCK)
    mk.paint(f, ROCK2, ball=((22.4, 1.9, -0.9), 1.0))

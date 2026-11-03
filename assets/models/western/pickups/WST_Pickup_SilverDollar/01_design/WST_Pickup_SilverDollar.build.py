"""
Receta de WST_Pickup_SilverDollar, el dólar de plata que cae como moneda (prompt 138, Bloques A + B).

Brief
- Lo pidió la sesión del juego (2026-10-29): la moneda del drop de plata, que el juego hace girar sobre Y
  encima del piso. Tiene que leerse a 30 studs como "moneda": disco plano con borde que brilla y una
  estrella en relieve en cada cara. Muchas a la vez: barata.
- Una sola pieza, Coin, parada de canto: caras hacia -Z y +Z, origen en el centro exacto.
- Disco de 10 lados, 1,2 de diámetro (radio a los vértices 0,6) y 0,16 de espesor, en steel_light.
  Bordes de las caras con chanflán de 0,05 en silver_crust: es el borde que agarra la luz al girar.
- Estrella de cinco puntas de 0,6 de punta a punta en cada cara, 0,04 sobre la cara (detalle: entra
  0,02 en el disco para no dejar caras coplanares), en silver_crust.
- Inferido: el chanflán como borde (el relieve con escalón no entraba en 150 triángulos), el radio
  interior de la estrella (0,4 del exterior, la proporción clásica).

Revisión (1 vuelta)
- 148 triángulos (tope 150). Medidas: 1,141 x 1,2 x 0,24 (con las dos estrellas).
- El aviso de "no apoya en el piso" es esperable: el origen va en el centro porque el juego la hace girar.
- Contraste bajo entre steel_light y silver_crust: el borde se lee por la geometría, y el brillo del
  drop lo pone el VFX del loot.
"""

import math

R = 0.6           # radio a los vértices del decágono
T = 0.16          # espesor
STAR_R = 0.3      # 0,6 de punta a punta
STAR_PROUD = 0.04
STAR_SINK = 0.02


def star(r_out, r_in):
    """Perfil de una estrella de cinco puntas con una punta hacia arriba (+Y)."""
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def build(mk):
    coin = mk.part("Coin", (0, 0, 0))
    mk.cyl(coin, (0, 0, 0), R, T, "steel_light", axis="z", sides=10)
    mk.bevel(coin, width=0.05, angle=60, mat="silver_crust")
    depth = STAR_PROUD + STAR_SINK
    for side in (-1, 1):
        z = side * (T / 2 + STAR_PROUD - depth / 2)
        mk.prism(coin, star(STAR_R, STAR_R * 0.4), depth, "silver_crust", plane="xy", center=(0, 0, z),
                 detail=True)

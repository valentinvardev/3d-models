"""
Receta de WST_Item_Coffee, el jarro enlozado de café (prompt 039, Bloques A + B).

Brief
- Silueta a 40 studs: jarro de campamento gris azulado de 8 lados, borde de hierro oscuro enrollado, asa
  en C a la derecha (+X) y la boca abierta con el café negro adentro (se ve desde arriba y de 3/4).
- Medidas: 0,4 de alto, 0,38 de diámetro (r 0,195 a los vértices: 0,36 entre caras planas). Café 0,05
  abajo del borde. Paredes de ~0,025, el borde de hierro 0,03 de alto y 0,01 afuera. Origen abajo al
  centro.
- Una pieza (Body): cuerpo y borde en la base (la boca se talla de los dos), el café es el fondo del hueco
  pintado coal, el asa como detalle (no la toca la booleana).
- Inferido: el nombre Body, el borde levantado (enrollado, como los jarros enlozados), el asa del mismo
  enlozado que el cuerpo, el espesor de las paredes.

Vueltas: 1) pasa la revisión a la primera; el café (6 triángulos coal en y = 0,35) se verificó leyendo
las caras del GLB, porque en las capturas de costado casi no se ve.

Revisión
- 142 triángulos contra 120 de referencia: la boca tallada (paredes por dentro y el café) y el borde
  levantado. Sin la boca no se lee "lleno de café".
- Ancho 0,51 con el asa (el jarro, 0,38).
- Asa en C de 4 tramos rectos (low poly duro, como pide el Bloque A); redondearla con 6 tramos suma 16.
"""

import math

R, H = 0.195, 0.4
RIM = 0.03                         # alto del borde de hierro
COFFEE = H - 0.05                  # superficie del café


def strip(center, t):
    """Perfil (x, y) de una tira de espesor t a lo largo de una línea central (el asa en C)."""
    n = len(center)
    left, right = [], []
    for i in range(n):
        a, b = center[max(i - 1, 0)], center[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln, dx / ln
        left.append((center[i][0] + nx * t / 2, center[i][1] + ny * t / 2))
        right.append((center[i][0] - nx * t / 2, center[i][1] - ny * t / 2))
    return left + right[::-1]


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    mk.cyl(body, (0, (H - RIM + 0.01) / 2, 0), R, H - RIM + 0.01, "paint_slate", sides=8)          # cuerpo
    mk.cyl(body, (0, H - RIM / 2, 0), R + 0.01, RIM, "iron", sides=8)                               # borde enrollado
    mk.carve(body, "paint_slate", points=mk.pts_cyl((0, COFFEE + 0.1, 0), R - 0.025, 0.2, sides=8))  # boca
    mk.paint(body, "coal", box=((0, COFFEE, 0), (0.5, 0.01, 0.5)))                                  # café
    mk.paint(body, "iron", box=((0, H - RIM / 2 + 0.002, 0), (0.6, RIM - 0.002, 0.6)))             # borde por dentro
    handle = [(R - 0.02, 0.31), (R + 0.11, 0.29), (R + 0.11, 0.12), (R - 0.02, 0.10)]
    mk.prism(body, strip(handle, 0.045), 0.06, "paint_slate", plane="xy", detail=True)            # asa en C

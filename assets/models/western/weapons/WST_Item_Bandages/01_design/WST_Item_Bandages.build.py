"""
Receta de WST_Item_Bandages, el rollo de vendas (prompt 037, Bloques A + B).

Brief
- Silueta a 40 studs: un rollo octogonal de lona acostado (eje en X) con el agujero del centro a la vista
  y la punta suelta que cuelga por delante hasta el piso; un alfiler de gancho de acero la sujeta.
- Medidas: 0,45 de diámetro (0,434 entre caras planas, 0,47 entre vértices), 0,3 de ancho; la punta
  suelta mide ~0,35 (cae en curva desde la mitad del frente y se apoya 0,1 en el piso), 0,26 de ancho.
  Origen abajo del rollo.
- Una pieza (Body): rollo (base, con el agujero tallado), punta y alfiler como detalle (no los toca la
  booleana del agujero). Alfiler: lazo en U de 0,2 x 0,06 con el cierre a la derecha.
- Inferido: el nombre Body (el objeto raíz ya se llama como el id), el agujero del centro (r 0,06) para
  que se lea "rollo", el rollo acostado, por dónde cae la punta y el alfiler sobre ella.

Vueltas: 1) la punta era una placa en L con ángulo recto (se leía como una escuadra de metal) y el
alfiler una barra con cabeza (un perno) · 2) punta que cae en curva (5 puntos) y alfiler en U con cierre.

Revisión
- 144 triángulos contra 100 de referencia: rollo con agujero ~64, punta en curva ~36, alfiler ~40. El
  agujero y la curva son lo que hace que se lea venda y no un bloque; el alfiler lo pide el prompt.
- Profundidad 0,64 con la punta apoyada en el piso.
"""

import math

R = 0.235                      # radio a los vértices del octógono
RF = R * 0.9239                # a las caras planas (0,217): el rollo apoya en una cara plana
W = 0.3
T = 0.025                      # espesor de la tela suelta


def strip(center, t):
    """Perfil (z, y) de una tira de espesor t a lo largo de una línea central: la tela que cae en curva."""
    n = len(center)
    left, right = [], []
    for i in range(n):
        a, b = center[max(i - 1, 0)], center[min(i + 1, n - 1)]
        dz, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dz, dy)
        nz, ny = -dy / ln, dz / ln
        left.append((center[i][0] + nz * t / 2, center[i][1] + ny * t / 2))
        right.append((center[i][0] - nz * t / 2, center[i][1] - ny * t / 2))
    return left + right[::-1]


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    mk.cyl(body, (0, RF, 0), R, W, "canvas", axis="x", sides=8)
    mk.carve(body, "canvas", points=mk.pts_cyl((0, RF, 0), 0.06, W + 0.1, axis="x", sides=8))      # agujero del rollo
    # punta suelta: sale de la cara de adelante a media altura, se despega en curva y se apoya en el piso
    zf = -RF - T / 2 + 0.004
    drape = [(zf, 0.30), (zf - 0.015, 0.17), (zf - 0.05, 0.06), (zf - 0.11, T / 2), (zf - 0.2, T / 2)]
    mk.prism(body, strip(drape, T), 0.26, "canvas", plane="zy", center=(0, 0, 0), detail=True)
    # alfiler de gancho sobre la tela, a la vista de frente: lazo en U de 0,2 y cierre
    zp = zf - T / 2 - 0.01
    loop = [(-0.1, 0.17), (0.07, 0.17), (0.07, 0.23), (-0.1, 0.23), (-0.1, 0.21), (0.05, 0.21), (0.05, 0.19), (-0.1, 0.19)]
    mk.prism(body, loop, 0.02, "steel_light", plane="xy", center=(0, 0, zp + 0.002), detail=True)
    mk.box(body, (0.085, 0.2, zp), (0.05, 0.08, 0.035), "steel_light", detail=True)           # cierre

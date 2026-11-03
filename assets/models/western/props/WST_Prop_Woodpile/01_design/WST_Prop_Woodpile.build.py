"""
Receta de WST_Prop_Woodpile, la pila de leña detrás de las casas (prompt 139, Bloques A + B).

Brief
- Lo pidió la sesión del juego (2026-10-30): los dos Woodpile del mapa (4 x 2 x 6, cobertura agachado) son
  cajas lisas. Va como prop (`Props/Woodpile.rbxm`), ajustado a esa caja.
- Silueta a 40 studs: una pila baja de leños en tres hileras que se angostan hacia arriba, con las puntas
  claras (corte) a la vista en los dos extremos, estacas en las esquinas y un tocón con el hacha clavada.
- Una sola pieza, Pile, con el origen abajo al centro. Planta 4 (X) x 6 (Z), 2 de alto.
- Leños a lo largo de Z: hexágonos de radio 0,31 (6 + 5 + 4), con el largo variando ±0,1. Tres son
  rajados (cuña triangular) para que se vea la madera partida. Corteza wood_dark, cuñas wood_mid, puntas
  wood_light.
- Tocón de 1 x 1,1 en la esquina +X, -Z con el hacha clavada (cabeza iron, mango wood_light).
- Inferido: los leños miden 4,6 y no 6 (el tocón tiene que entrar en la planta; el prompt quedó
  corregido), las estacas son de 2 de alto (no 2,2: la caja mide 2), el anillo oscuro de las puntas no
  va (el chanflán con color costaba un triángulo por borde en 15 leños).

Revisión (3 vueltas)
- 1) Leños a 0,62 entre centros: el QA marcaba piezas sueltas (los hexágonos apenas se tocaban o
  quedaban a 0,024). 2) A 0,56 quedaban 4 sueltos: el hexágono tiene la cara, no el vértice, hacia ±X.
  3) A 0,52 (menos que 0,537 entre caras) se encastran todos; estacas subidas 0,01.
- 364 triángulos (tope 400). Medidas: 3,54 x 2,0 x 5,99; el prop se ajusta a la caja del mapa.
- El aviso de "no apoya en el piso" (-0,04) son las esquinas de las estacas inclinadas: quedan enterradas.
- Entre hileras se ven huecos triangulares oscuros en las puntas: se leen como sombra entre leños.
"""

import math

LOG_R = 0.31
STEP = 0.52                 # entre centros: menos que el ancho entre caras del hexágono (0,537), se encastran
Z0, Z1 = -1.6, 3.0          # puntas de los leños: el frente (-Z) deja lugar al tocón
ROWS = [(0.27, 6), (0.71, 5), (1.15, 4)]  # cada hilera en la canaleta de la de abajo, encastrada
SPLIT = {(0, 2), (1, 4), (2, 1)}          # (hilera, leño) que van rajados
JITTER = [0.08, -0.05, 0.1, -0.09, 0.03, -0.1, 0.06, -0.02, 0.09, -0.07, 0.04, -0.08, 0.1, -0.04, 0.05]


def wedge(r):
    """Cuña de un leño partido en tres: el triángulo con la corteza afuera (perfil en el plano xy)."""
    return [(0, -r * 0.55), (r * 0.95, r * 0.45), (-r * 0.95, r * 0.45)]


def build(mk):
    mk.part("Pile", (0, 0, 0))
    k = 0
    for row, (y, n) in enumerate(ROWS):
        for i in range(n):
            x = (i - (n - 1) / 2) * STEP
            a, b = Z0 + JITTER[k] * 0.6, Z1 + JITTER[k]
            k += 1
            if (row, i) in SPLIT:
                mk.prism("Pile", wedge(LOG_R * 1.05), b - a, "wood_mid", plane="xy", center=(x, y, (a + b) / 2))
            else:
                mk.cyl("Pile", (x, y, (a + b) / 2), LOG_R, b - a, "wood_dark", axis="z", sides=6)
    # las puntas de corte, claras, en los dos extremos
    mk.paint("Pile", "wood_light", box=((0, 1, Z0), (4.2, 2.2, 0.3)))
    mk.paint("Pile", "wood_light", box=((0, 1, Z1), (4.2, 2.2, 0.3)))

    # estacas en las esquinas de los lados X
    edge = (ROWS[0][1] - 1) / 2 * STEP + LOG_R      # el borde de la hilera de abajo
    for sx in (-1, 1):
        for z in (Z0 + 0.3, Z1 - 0.3):
            mk.box("Pile", (sx * (edge + 0.03), 0.86, z), (0.14, 1.7, 0.16), "wood_dark", rot=(0, 0, sx * -4))

    # tocón con el hacha clavada; el mango cae hacia -X, sobre la pila
    mk.cyl("Pile", (1.3, 0.55, -2.4), 0.5, 1.1, "wood_mid", axis="y", sides=7)
    mk.paint("Pile", "wood_light", box=((1.3, 1.1, -2.4), (1.1, 0.06, 1.1)))
    tilt = 50
    head = (1.28, 1.16, -2.4)
    mk.box("Pile", head, (0.1, 0.3, 0.46), "iron", rot=(0, 0, -tilt), detail=True)
    hx = head[0] - math.sin(math.radians(tilt)) * 0.6
    hy = head[1] + math.cos(math.radians(tilt)) * 0.6
    mk.cyl("Pile", (hx, hy, -2.4), 0.05, 1.2, "wood_light", axis="y", sides=5, rot=(0, 0, tilt), detail=True)

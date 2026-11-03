"""
Receta de WST_Item_Rounds, las balas sueltas para las animaciones de recarga (prompt 003, Bloques A + F).

Brief
- Seis piezas en fila sobre X (0,3 entre centros), cada una con el origen en su centro y el eje largo en Z
  (punta hacia -Z): RevolverRound, RevolverCasing, RifleRound, RifleCasing, ShotgunShell, ShotgunShellSpent.
- Se ven en la mano en primer plano (recarga): culote con pestaña, casquillos vacíos huecos de verdad,
  vainas de escopeta con el engarce cerrado o abierto. Chanflán fino en el bronce para que brille.
- Medidas del prompt (ya agrandadas 1,4x). 6 lados en balas y casquillos, 8 en las vainas de escopeta.

Vueltas: 1) con chanflanes y 8 lados: 2268 triángulos, once veces el tope, en piezas que se ven chicas:
   detalle que nadie ve · 2) sin chanflanes, 6 lados, tramos de la vaina encimados (bordes rotos) ·
3) `top` achica el extremo de atrás en un cilindro en Z: punta del rifle, hombro y engarce estaban al revés ·
4) hombro del rifle encimado con radios distintos (anillos idénticos se soldaban: bordes rotos).

Revisión
- 730 triángulos contra 200 de referencia (calidad primero): seis piezas de ~120, con culote de pestaña,
  casquillos huecos tallados y engarces. Sin chanflanes (a este tamaño no se notan).
- Los avisos de "floating" son esperables: son seis objetos separados en fila, no un modelo armado.
"""

import math

GAP = 0.3
SIDES = 6          # balas y casquillos: los 6 lados del prompt (a este tamaño no se nota más)
SHELL_SIDES = 8    # vainas de escopeta, más gordas


def round_x(i):
    return -0.75 + GAP * i


def case(mk, part, x, z0, z1, r, sides=SIDES):
    mk.cyl(part, (x, 0, (z0 + z1) / 2), r, z1 - z0, "brass", axis="z", sides=sides)


def rim(mk, part, x, z_back, r):
    mk.cyl(part, (x, 0, z_back - 0.007), r, 0.014, "brass", axis="z", sides=SIDES)


def build(mk):
    # ---- revólver: vaina recta 0,12 + bala de plomo de punta redonda 0,05 (largo total 0,17) ----
    x = round_x(0)
    rr = mk.part("RevolverRound", (x, 0, 0))
    case(mk, rr, x, -0.035, 0.078, 0.025)
    rim(mk, rr, x, 0.085, 0.031)
    mk.cyl(rr, (x, 0, -0.05), 0.024, 0.03, "stone_grey", axis="z", sides=SIDES)
    mk.ball(rr, (x, 0, -0.064), 0.024, "stone_grey", scale=(1, 1, 0.9))

    x = round_x(1)
    rc = mk.part("RevolverCasing", (x, 0, 0))
    case(mk, rc, x, -0.035, 0.078, 0.025)
    rim(mk, rc, x, 0.085, 0.031)
    mk.carve(rc, "coal", points=mk.pts_cyl((x, 0, -0.01), 0.018, 0.08, axis="z", sides=SIDES))      # boca abierta

    # ---- rifle: vaina con cuello (cuerpo, hombro, cuello) + bala en punta 0,06 (largo total 0,26) ----
    def rifle_case(part, x):
        case(mk, part, x, -0.01, 0.12, 0.0275)
        mk.cyl(part, (x, 0, -0.024), 0.0185, 0.036, "brass", axis="z", sides=SIDES, top=0.027 / 0.0185)  # hombro: se encima 0,004
        # con el cuerpo y el cuello, con radios distintos (anillos iguales se sueldan y rompen bordes)
        case(mk, part, x, -0.075, -0.035, 0.016)                                                 # cuello
        rim(mk, part, x, 0.127, 0.031)

    x = round_x(2)
    fr = mk.part("RifleRound", (x, 0, 0))
    rifle_case(fr, x)
    mk.cyl(fr, (x, 0, -0.105), 0.017 * 0.25, 0.06, "stone_grey", axis="z", sides=SIDES, top=4.0)  # bala, punta adelante

    x = round_x(3)
    fc = mk.part("RifleCasing", (x, 0, 0))
    rifle_case(fc, x)
    mk.carve(fc, "coal", points=mk.pts_cyl((x, 0, -0.07), 0.011, 0.07, axis="z", sides=SIDES))      # boca abierta

    # ---- escopeta: vaina de papel roja 0,22 + culote de bronce 0,05 con pestaña ----
    def shell(part, x, spent):
        mk.cyl(part, (x, 0, -0.02), 0.045, 0.19, "cloth_red", axis="z", sides=SHELL_SIDES)       # papel
        if spent:
            mk.cyl(part, (x, 0, -0.124), 0.045 * 1.12, 0.024, "cloth_red", axis="z", sides=SHELL_SIDES, top=1 / 1.12)  # boca abierta (se encima 0,003: si se tocan justo, la booleana rompe bordes)
        else:
            mk.cyl(part, (x, 0, -0.124), 0.045 * 0.82, 0.024, "cloth_red", axis="z", sides=SHELL_SIDES, top=1 / 0.82)  # engarce cerrado
        mk.cyl(part, (x, 0, 0.09), 0.0475, 0.05, "brass", axis="z", sides=SHELL_SIDES)             # culote
        rim(mk, part, x, 0.122, 0.054)

    x = round_x(4)
    ss = mk.part("ShotgunShell", (x, 0, 0))
    shell(ss, x, spent=False)
    mk.carve(ss, "coal", points=mk.pts_cyl((x, 0, -0.14), 0.012, 0.02, axis="z", sides=SIDES))      # centro del engarce

    x = round_x(5)
    sp = mk.part("ShotgunShellSpent", (x, 0, 0))
    shell(sp, x, spent=True)
    mk.carve(sp, "coal", points=mk.pts_cyl((x, 0, -0.08), 0.04, 0.14, axis="z", sides=SIDES))       # vaina vacía, hollín

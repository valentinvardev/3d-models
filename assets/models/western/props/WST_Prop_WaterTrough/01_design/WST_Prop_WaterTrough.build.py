"""
Receta de WST_Prop_WaterTrough, el bebedero de caballos (prompt 131, Bloques A + C). Es la debilidad
del Carnicero: tiene que leerse "lleno de agua" de lejos.

Brief
- Silueta a 40 studs: cajón largo y bajo de tablones sobre dos patas en X, con el agua turquesa como la
  mancha de color más grande vista desde arriba; esquineros de hierro oscuros en las cuatro esquinas.
- Medidas: 6 (X) x 2 (Z) x 1,8 de alto. Cajón de y 0,6 a 1,8 con paredes de 0,4 (fragmentos >= 0,4);
  adentro 5,2 x 1,2; agua hasta y 1,5 (0,3 abajo del borde): desde arriba el agua es el 52 % del
  rectángulo y cada tira de borde es más angosta que ella.
- Fragmentos (4, origen común): frag01 pared de adelante, frag02 pared de atrás (cada una tres tablones
  alternados wood_mid / wood_light con el del medio hundido 0,02, y sus dos esquineros), frag03 punta
  izquierda con la mitad izquierda del piso, frag04 la derecha (cada una un prisma en L). Water aparte
  (el volumen de agua: se oculta al romperse). fixed_Legs: las dos patas en X, quedan en pie.
- Variante WaterTrough_Pump (mismo archivo, en x = 8): el mismo bebedero con una bomba de hierro sobre
  un poste en la punta derecha, el pico sobre el agua; la palanca es WaterTrough_Pump_Handle con el
  origen en su pivote (arriba de la bomba); la bomba es WaterTrough_Pump_fixed_Pump.
- Inferido: largo en X (el lado largo mira al frente); paredes de 0,4; patas en X debajo del cajón
  (dos tablas cruzadas lado a lado, 0,6 de alto); esquineros de alto casi completo; una grieta en
  zigzag tallada en el tablón de arriba del frente; diseño de la bomba (de jarra, con poste de madera);
  nombres de la variante con prefijo WaterTrough_Pump_ (igual que el barril).

Vueltas: 1) 16 pares coplanares en la bomba (brida y cuerpo arrancaban en 1,28); la grieta tallada en
el frente costaba 92 triángulos · 2) grieta abierta desde el canto: seguía en 80, porque `carve` corre la
booleana con use_self sobre toda la base y recorta los tablones y esquineros encimados; brida octogonal
de r 0,27 = 0,499 entre caras, a 0,0006 de las caras del poste de 0,5 · 3) sin grieta, brida r 0,30.

Revisión
- 220 triángulos el bebedero (dentro de 250); la variante con bomba 388 (bomba 128, palanca 40).
- Medidas: 6,08 x 1,8 x 2,08 con los esquineros (6 x 2 sin ellos). Fragmentos 30-32 % las paredes
  largas, 19 % cada punta con su mitad de piso; mínimos 0,44 y 1,2.
- DUDOSO, agua poco visible de costado: con el agua 0,3 abajo del canto (lo pide el prompt) y paredes
  de 0,4, a 15° de elevación se ven 0,08 de los 1,2 de agua (0,3 / tan 15° = 1,12 tapado); a 27° (cámara
  típica a 20 studs) se ven 0,6. Desde arriba sí es la mancha más grande (52 %). Con el agua a 0,15 del
  canto, a 15° se verían 0,64. Decide Valentin: es la debilidad del Carnicero.
- Sin grieta en zigzag: la que se probó costaba 80 triángulos por la booleana.
"""

import math

L, W, H = 6.0, 2.0, 1.8
T = 0.4
Y_BOT = 0.6                      # fondo del cajón (arriba de las patas)
WATER_Y = H - 0.3
PUMP_X = 8.0


def crack(mk, part, x, y_top, z, depth=0.12):
    """Rajadura en zigzag que baja desde el canto de arriba de una cara que mira a -Z.
    Abierta arriba: un agujero cerrado en medio de la cara costaba 92 triángulos (vuelta 1)."""
    left = [(x - 0.05, y_top + 0.06), (x - 0.03, y_top - 0.1), (x + 0.02, y_top - 0.2), (x - 0.005, y_top - 0.32)]
    right = [(x + 0.005, y_top - 0.32), (x + 0.045, y_top - 0.2), (x, y_top - 0.1), (x + 0.06, y_top + 0.06)]
    mk.carve(part, "coal", prism=dict(profile=left + right, depth=depth, plane="xy", center=(0, 0, z)))


def tube(mk, part, a, b, r, mat, sides=6):
    ax = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in ax))
    d = [c / n for c in ax]
    ref = (0, 1, 0) if abs(d[1]) < 0.9 else (1, 0, 0)
    u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    un = math.sqrt(sum(c * c for c in u))
    u = [c / un for c in u]
    v = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]
    mk.hull(part, [tuple(p[i] + r * (math.cos(t) * u[i] + math.sin(t) * v[i]) for i in range(3))
                   for p in (a, b) for t in (2 * math.pi * (k + 0.5) / sides for k in range(sides))], mat)


def trough(mk, prefix="", x0=0.0, cracked=False):
    xi, zi = L / 2 - T, W / 2 - T                  # adentro: 2,6 y 0,6
    planks = ((Y_BOT, 1.005), (0.995, 1.405), (1.395, H))
    # ---- paredes largas: tres tablones, esquineros de hierro ----
    for k, s in ((1, -1), (2, 1)):
        p = mk.part(f"{prefix}frag{k:02d}", (x0, 0, 0))
        for i, (y0, y1) in enumerate(planks):
            inset = 0.02 if i == 1 else 0.0
            mat = "wood_light" if i == 1 else "wood_mid"
            mk.box(p, (x0, (y0 + y1) / 2, s * (W / 2 - T / 2)), (L - 2 * inset, y1 - y0, T - 2 * inset), mat)
        for e in (-1, 1):                         # una caja por esquina: asoma 0,04 por el frente y por la punta
            mk.box(p, (x0 + e * (L / 2 - 0.145 + 0.04), 1.2, s * (W / 2 - 0.145 + 0.04)), (0.29, 1.1, 0.29), "iron")
        if cracked and s == -1:
            crack(mk, p, x0 + 1.6, H, -W / 2)
    # ---- puntas con la mitad del piso: un prisma en L cada una ----
    for k, s in ((3, -1), (4, 1)):
        p = mk.part(f"{prefix}frag{k:02d}", (x0, 0, 0))
        prof = [(s * L / 2, Y_BOT), (0, Y_BOT), (0, Y_BOT + T), (s * xi, Y_BOT + T), (s * xi, H), (s * L / 2, H)]
        mk.prism(p, [(x0 + a, b) for a, b in prof], 2 * zi, "wood_mid", plane="xy", center=(0, 0, 0))
    # ---- agua (se oculta al romperse) ----
    w = mk.part(f"{prefix}Water", (x0, 0, 0))
    mk.box(w, (x0, (Y_BOT + T + WATER_Y) / 2, 0), (2 * xi, WATER_Y - Y_BOT - T, 2 * zi), "water")
    # ---- patas en X: dos tablas cruzadas, lado a lado ----
    legs = mk.part(f"{prefix}fixed_Legs", (x0, 0, 0))
    for e in (-1, 1):
        xc = x0 + e * 2.2
        for dx, sgn in ((-0.07, 1), (0.07, -1)):
            pts = [(xc + dx + ox, y, sgn * z + oz) for ox in (-0.07, 0.07)
                   for y, z in ((0.0, -0.92), (Y_BOT, 0.92)) for oz in (-0.12, 0.12)]
            mk.hull(legs, pts, "wood_dark")


def build(mk):
    trough(mk)          # sin grieta: tallarla costaba 80 tris (la booleana recorta los tablones encimados)
    trough(mk, prefix="WaterTrough_Pump_", x0=PUMP_X)
    # ---- bomba de jarra sobre un poste, el pico sobre el agua ----
    px = PUMP_X + L / 2 + 0.45
    pump = mk.part("WaterTrough_Pump_fixed_Pump", (PUMP_X, 0, 0))
    mk.box(pump, (px, 0.65, 0), (0.5, 1.3, 0.5), "wood_dark")                      # poste
    mk.cyl(pump, (px, 1.79, 0), 0.22, 0.98, "iron", sides=8)                         # cuerpo (arranca dentro de la brida)
    mk.cyl(pump, (px, 2.34, 0), 0.29, 0.14, "iron", sides=8)                         # tapa ancha
    mk.cyl(pump, (px, 1.33, 0), 0.30, 0.1, "iron", sides=8)                          # brida (con 0,27 quedaba coplanar con el poste)
    tube(mk, pump, (px - 0.1, 2.02, 0), (PUMP_X + L / 2 - 0.55, 1.95, 0), 0.09, "iron")  # pico sobre el agua (0,06 sobre el canto)
    mk.box(pump, (px + 0.22, 2.48, 0), (0.12, 0.2, 0.14), "iron")                   # horquilla del pivote
    pivot = (px + 0.24, 2.5, 0)
    hd = mk.part("WaterTrough_Pump_Handle", pivot)
    tube(mk, hd, (pivot[0] - 0.05, pivot[1] - 0.02, 0), (px + 1.25, 3.0, 0), 0.055, "iron")
    mk.ball(hd, (px + 1.27, 3.01, 0), 0.09, "iron", subdiv=0)                        # mango

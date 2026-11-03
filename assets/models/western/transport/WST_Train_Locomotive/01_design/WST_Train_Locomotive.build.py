"""
Receta de WST_Train_Locomotive, la 4-4-0 americana de 1870 (prompt 069, Bloques A + B). Es la pieza más
vista del Chapter y la referencia de estilo del tren: el ténder, los vagones, los restos y las vías
importan de acá las medidas comunes (trocha, alto de enganche, piso) y las ayudas (ruedas, anillos, barras).

Brief
- Silueta que se lee a 40 studs: chimenea de diamante alta y negra adelante, caldera larga con domos de
  bronce, quitapiedras rojo en cuña, cuatro ruedas motrices grandes de rayos rojos con bielas de acero,
  cabina roja de techo curvo atrás. De frente: farol de caja con el vidrio encendido sobre la puerta redonda.
- Medidas: 38 de largo (punta del quitapiedras z = -19 a espalda de la cabina z = +19), 8,5 de ancho
  (cilindros), 15 de alto (borde de la chimenea). Rieles en y = 0, trocha 4,6: la banda de las ruedas en
  x = ±2,43. Caldera de 16 lados, r 2,15 a y 6,6; el anillo de atrás sube (wagon top) a r 2,4. Ruedas
  motrices de 5,5 (ejes en z 0,8 y 7,6), ruedas del bogie de 2,9 (ejes en z -13,2 y -8,6). Cabina de
  7 x 8 (z 11 a 19), piso a 4,0, techo curvo con la cumbrera a 12 (a la altura de los techos de los vagones:
  en el túnel de 15,5 se pasa agachado). Estribos de 1,2 de ancho a 5,85.
- Piezas y orígenes: Boiler, Frame, Cab (origen en el piso, centro); Headlamp_Glow y Firebox_Glow (vidrios
  aparte para apagarlos); FireboxDoor (origen en la bisagra, a su izquierda = -X); Throttle (origen en la
  base de la palanca; gira 60° hacia atrás sobre X); DriveWheels (origen en el eje delantero); PilotWheels
  (origen en el centro del bogie). Marcadores _CoalTarget, _ThrottleGrip, _Coupler.
- Tallado/pintado: sin booleanas; los huecos (boca de la chimenea, ventanas, puerta del hogar) salen de armar
  las piezas alrededor. La boca de la chimenea se pinta coal adentro del aro.
- Inferido: wagon top, orden de domos (arena, campana, vapor), farol de caja rojo con techo de bronce,
  bielas en steel_light (7 materiales: el séptimo es el acero de las bielas y cruceta), manivelas adelante,
  biela motriz a la rueda de atrás, techo de chapa (iron) con frentes de madera, asientos y palanca de
  cambio en la cabina, una barra del quitapiedras doblada y otra que falta.

Vueltas: 1) primera versión: z-fighting en los esquineros de la cabina (base en 3,98 igual que los paños),
las colgaderas del escalón de adelante (tope en 3,3 igual que la viga), las agarraderas de la espalda y la
montura contra el fondo de la caja de humo (z -9,6 los dos); bordes no-manifold donde la punta del frente
curvo coincidía con el costado; caño de la torreta flotando 0,008 · 2) arreglos; farol de 1,2 a 1,9 de
ancho (el prompt pide "big box headlamp" y se leía chico), techo con 0,6 de caída en vez de 0,38 ·
3) piso de tablas sobre chapa (era chapa negra entera) y palanca más visible (acero con bocha de bronce de
0,24, pivote 0,08 más afuera para que la bocha no toque la placa).

Revisión
- 9024 triángulos contra 6000 de referencia (+50 %). Las ruedas son 3824: 4 motrices de 16 lados con
  llanta de hierro, aro rojo, 14 rayos con aire, contrapeso y manivela (678 c/u) y 4 del bogie de 8 rayos;
  es el rasgo que identifica la locomotora de costado. Caldera 2200 (16 lados, 6 zunchos, 3 domos, campana,
  farol, chimenea de diamante con boca), cabina 1600 (paños con molduras, techo de chapas en arco, frente del
  hogar con relojes, nivel, regulador y palanca de cambio). Ninguna pieza pasa de 2800 (tope 5000).
- Medidas: 38,48 de largo (el techo vuela 0,3 atrás y 0,2 adelante de la cabina de 38), 8,43 de ancho
  (cilindros), 15,01 de alto (borde de la chimenea).
- 8 materiales en vez de 6: steel_light (bielas, cruceta, palanca: el acero pulido es la firma de una 4-4-0)
  y coal (la boca de la chimenea, pintada).
- Medidas que usan las otras piezas del tren: rieles con la cabeza en y = 0 y centro en x = ±2,43, enganche
  a y = 2,6, piso de la cabina a 4,0 (la plataforma del ténder va a la misma altura).
- DriveWheels gira entera alrededor del eje delantero solo si el giro es falso (lo dice el prompt); las
  bielas van en la misma pieza.
"""

import math

from mathutils import Vector

# ---------------- medidas del tren (las importan el ténder, los vagones, los restos y las vías) ----------------
GAUGE = 4.6
RAIL_HEAD = 0.26
RAIL_X = GAUGE / 2 + RAIL_HEAD / 2   # 2,43: centro del riel = plano de la banda de las ruedas
COUPLER_Y = 2.6                      # centro del enganche de todo el tren
DECK_Y = 4.0                         # piso de la cabina = plataforma del ténder

# ---------------- locomotora ----------------
Z_TIP, Z_BACK = -19.0, 19.0
BOILER_Y, BOILER_R = 6.6, 2.15
WT_Y, WT_R = 6.85, 2.4               # anillo de atrás más alto (wagon top)
SMOKE_R, Z_SMOKE_F, Z_SMOKE_B = 2.3, -14.9, -9.6
Z_CONE_A, Z_CONE_B = 1.0, 3.0
Z_CAB_F, Z_CAB_B, CAB_X = 11.0, 19.0, 3.5
Z_BH = 12.2                          # fin de la caldera; la placa del frente del hogar va de 12,18 a 12,42
EAVE_Y, ROOF_Y, ROOF_HALF, ROOF_K, ROOF_T = 11.4, 12.0, 3.85, 0.04, 0.18
DRIVER_R, DRIVER_Z = 2.75, (0.8, 7.6)
PILOT_R, PILOT_Z = 1.45, (-13.2, -8.6)
CYL_X, CYL_Y, CYL_Z, CYL_R, CYL_L = 3.35, 3.6, -10.9, 0.85, 3.0
STACK_Z = -12.3
RB_X0, RB_X1, RB_Y, RB_Z0 = 2.05, 3.25, 5.85, -9.5
CRANK = 1.0
XHEAD_Z = -6.4
FLAT = math.cos(math.pi / 16)        # la cara de arriba de un cilindro de 16 lados queda a r * FLAT
DOOR = (-0.75, 0.75, 4.45, 5.65)     # boca del hogar (x0, x1, y0, y1)
THR_PIVOT = (1.3, 7.1, 12.7)
LAMP_Z = -15.35


# ---------------- ayudas (las usan las otras recetas del tren) ----------------
def B(mk, part, x0, x1, y0, y1, z0, z1, mat, detail=False):
    """Caja por sus límites (más fácil de leer y de no dejar caras coplanares)."""
    mk.box(part, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mat,
           detail=detail)


def bar(mk, part, a, b, w, h, mat, up=(0, 1, 0), ext=0.0, detail=False):
    """Barra de sección w x h de a a b (un casco de 8 puntos)."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    a, b = a - d * ext, b + d * ext
    s = d.cross(Vector(up))
    if s.length < 1e-6:
        s = d.cross(Vector((0, 0, 1)))
    s.normalize()
    u = s.cross(d).normalized()
    pts = [tuple(p + s * sx * w / 2 + u * sy * h / 2) for p in (a, b) for sx in (-1, 1) for sy in (-1, 1)]
    mk.hull(part, pts, mat, detail=detail)


def pipe(mk, part, a, b, r, mat, sides=8, detail=False):
    """Caño redondo de a a b."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    ref = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    v = d.cross(u)
    pts = [tuple(p + u * r * math.cos(2 * math.pi * (i + 0.5) / sides) + v * r * math.sin(2 * math.pi * (i + 0.5) / sides))
           for p in (a, b) for i in range(sides)]
    mk.hull(part, pts, mat, detail=detail)


def ring_pts(c, r, axis="z", sides=16, phase=0.5):
    """Anillo de puntos con la misma fase que mk.cyl (para cascos que empalman con cilindros)."""
    cx, cy, cz = c
    out = []
    for i in range(sides):
        a = 2 * math.pi * (i + phase) / sides
        u, v = r * math.cos(a), r * math.sin(a)
        out.append((cx + u, cy + v, cz) if axis == "z" else (cx + u, cy, cz + v) if axis == "y" else (cx, cy + v, cz + u))
    return out


def annulus(mk, part, c, r_in, r_out, w, mat, axis="x", sides=16, a0=0.0, over=1.2, detail=False):
    """Corona (llanta, aro, borde) como dos medias coronas encimadas 1,2°: sin vértices compartidos."""
    cx, cy, cz = c
    plane, cu, cv, cen = {"x": ("zy", cz, cy, (cx, 0, 0)), "y": ("xz", cx, cz, (0, cy, 0)),
                          "z": ("xy", cx, cy, (0, 0, cz))}[axis]
    n = sides // 2
    d = math.radians(over)
    for k, base in enumerate((a0, a0 + math.pi)):
        angs = [base - d + (math.pi + 2 * d) * i / n for i in range(n + 1)]
        outer = [(cu + r_out * math.cos(a), cv + r_out * math.sin(a)) for a in angs]
        inner = [(cu + r_in * math.cos(a), cv + r_in * math.sin(a)) for a in reversed(angs)]
        mk.prism(part, outer + inner, w - 0.004 * k, mat, plane=plane, center=cen, detail=detail)


def spoked_wheel(mk, part, hub, r, spokes=14, sides=16, tire_t=0.36, rim_t=0.24, width=0.46, hub_r=0.6,
                 tire="iron", body="paint_red", counter=None):
    """Rueda de rayos en el plano y-z (eje en x): llanta de hierro, aro y rayos pintados con aire entre ellos.
    counter = ángulo (rad, en el plano z-y) del contrapeso; la manivela va del lado opuesto."""
    hx, hy, hz = hub
    out = 1 if hx >= 0 else -1
    annulus(mk, part, hub, r - tire_t, r, width, tire, "x", sides)
    r_spoke = r - tire_t + 0.04
    if rim_t > 0:
        annulus(mk, part, hub, r - tire_t - rim_t, r - tire_t + 0.03, width - 0.1, body, "x", sides, a0=math.pi / 2)
        r_spoke = r - tire_t - rim_t + 0.05
    for i in range(spokes):
        a = 2 * math.pi * (i + 0.5) / spokes
        c, s = math.cos(a), math.sin(a)
        tang = Vector((0, c, -s))
        pts = []
        for rr, wt in ((hub_r - 0.08, 0.09 * r / 2.75 + 0.02), (r_spoke, 0.06 * r / 2.75 + 0.015)):
            p = Vector((hx, hy + rr * s, hz + rr * c))
            pts += [tuple(p + tang * sa * wt + Vector((sx * 0.11, 0, 0))) for sa in (-1, 1) for sx in (-1, 1)]
        mk.hull(part, pts, body)
    mk.cyl(part, hub, hub_r, width - 0.06, body, axis="x", sides=10)
    mk.cyl(part, (hx + out * (width / 2 + 0.03), hy, hz), hub_r * 0.55, 0.16, tire, axis="x", sides=8)
    if counter is not None:
        prof = []
        for k in range(7):
            a = counter - math.radians(48) + math.radians(96) * k / 6
            prof.append((hz + (r_spoke - 0.02) * math.cos(a), hy + (r_spoke - 0.02) * math.sin(a)))
        for k in range(5):
            a = counter + math.radians(40) - math.radians(80) * k / 4
            prof.append((hz + 1.25 * math.cos(a), hy + 1.25 * math.sin(a)))
        mk.prism(part, prof, 0.3, body, plane="zy", center=(hx, 0, 0))


def roof_top(x):
    return ROOF_Y - ROOF_K * x * x


def roof_under(x):
    return roof_top(x) - ROOF_T - 0.01


def dome(mk, p, z, base_y, r, h, mat="brass"):
    """Domo de bronce: pollera que sale de la caldera, cuerpo y tapa redondeada (tres cascos)."""
    mk.hull(p, ring_pts((0, base_y - 0.45, z), r * 1.34, "y", 12) + ring_pts((0, base_y + 0.28, z), r * 1.02, "y", 12), mat)
    mk.cyl(p, (0, base_y + 0.2 + (h - 0.2) / 2, z), r, h - 0.2, mat, axis="y", sides=12)
    mk.hull(p, ring_pts((0, base_y + h - 0.04, z), r * 0.995, "y", 12) + ring_pts((0, base_y + h + 0.3, z), r * 0.86, "y", 12)
            + ring_pts((0, base_y + h + 0.52, z), r * 0.55, "y", 12) + ring_pts((0, base_y + h + 0.62, z), r * 0.18, "y", 12),
            mat)
    return base_y + h + 0.62


# ---------------- caldera, caja de humo, chimenea, domos, campana, farol ----------------
def build_boiler(mk):
    p = mk.part("Boiler", (0, 0, 0))
    zf = Z_SMOKE_B - 0.2
    mk.cyl(p, (0, BOILER_Y, (zf + Z_CONE_A + 0.05) / 2), BOILER_R, Z_CONE_A + 0.05 - zf, "gunmetal", axis="z", sides=16)
    mk.hull(p, ring_pts((0, BOILER_Y, Z_CONE_A - 0.02), BOILER_R - 0.003)
            + ring_pts((0, WT_Y, Z_CONE_B + 0.02), WT_R - 0.003), "gunmetal")                       # anillo cónico
    mk.cyl(p, (0, WT_Y, (Z_CONE_B - 0.05 + Z_BH) / 2), WT_R, Z_BH - Z_CONE_B + 0.05, "gunmetal", axis="z", sides=16)
    for z in (-9.25, -3.6):                                                                        # zunchos de bronce
        mk.cyl(p, (0, BOILER_Y, z), BOILER_R + 0.05, 0.22, "brass", axis="z", sides=16)
    mk.cyl(p, (0, BOILER_Y, Z_CONE_A - 0.02), BOILER_R + 0.05, 0.24, "brass", axis="z", sides=16)
    for z in (Z_CONE_B + 0.04, 8.7, 10.75):
        mk.cyl(p, (0, WT_Y, z), WT_R + 0.05, 0.22, "brass", axis="z", sides=16)
    B(mk, p, -1.5, 1.5, 3.2, 5.2, 4.3, 11.1, "gunmetal")                                          # hogar entre las ruedas

    # caja de humo y puerta redonda
    mk.cyl(p, (0, BOILER_Y, (Z_SMOKE_F + Z_SMOKE_B) / 2), SMOKE_R, Z_SMOKE_B - Z_SMOKE_F, "iron", axis="z", sides=16)
    mk.cyl(p, (0, BOILER_Y, Z_SMOKE_F + 0.1), SMOKE_R + 0.06, 0.24, "brass", axis="z", sides=16)   # aro del frente
    mk.cyl(p, (0, BOILER_Y, Z_SMOKE_F - 0.06), 1.75, 0.24, "iron", axis="z", sides=16)             # puerta
    for y in (7.45, 5.75):                                                                         # bisagras de la puerta
        B(mk, p, -0.2, 1.68, y - 0.11, y + 0.11, Z_SMOKE_F - 0.26, Z_SMOKE_F - 0.15, "iron")
        B(mk, p, 1.6, 1.98, y - 0.14, y + 0.14, Z_SMOKE_F - 0.2, Z_SMOKE_F + 0.03, "iron")
    mk.cyl(p, (0, BOILER_Y, Z_SMOKE_F - 0.3), 0.14, 0.24, "brass", axis="z", sides=8)              # manija de dardo
    B(mk, p, -0.42, 0.42, BOILER_Y - 0.06, BOILER_Y + 0.06, Z_SMOKE_F - 0.44, Z_SMOKE_F - 0.34, "brass")

    # chimenea de diamante
    top_sb = BOILER_Y + SMOKE_R * FLAT
    mk.cyl(p, (0, top_sb + 0.05, STACK_Z), 1.05, 0.7, "iron", axis="y", sides=12, top=0.72)         # base
    mk.cyl(p, (0, (top_sb + 0.3 + 11.3) / 2, STACK_Z), 0.58, 11.3 - top_sb - 0.3, "iron", axis="y", sides=12)
    mk.hull(p, ring_pts((0, 11.25, STACK_Z), 0.6, "y", 12) + ring_pts((0, 13.66, STACK_Z), 1.58, "y", 12), "iron")
    mk.cyl(p, (0, 13.66, STACK_Z), 1.64, 0.22, "iron", axis="y", sides=12)                        # cinta del diamante
    mk.hull(p, ring_pts((0, 13.62, STACK_Z), 1.555, "y", 12) + ring_pts((0, 14.74, STACK_Z), 1.08, "y", 12), "iron")
    annulus(mk, p, (0, 14.86, STACK_Z), 0.9, 1.2, 0.3, "iron", axis="y", sides=12)                 # boca
    mk.paint(p, "coal", box=((0, 14.74, STACK_Z), (1.9, 0.02, 1.9)))                              # hollín adentro

    # domos, silbato, campana
    dome(mk, p, -5.6, BOILER_Y + BOILER_R * FLAT, 0.78, 1.25)                                      # arenero
    top = dome(mk, p, 6.2, WT_Y + WT_R * FLAT, 0.95, 1.2)                                          # domo de vapor
    mk.cyl(p, (0.0, top + 0.12, 6.2), 0.1, 0.4, "brass", axis="y", sides=6)                        # silbato
    mk.cyl(p, (0.0, top + 0.48, 6.2), 0.18, 0.36, "brass", axis="y", sides=8)
    mk.cyl(p, (0.0, top + 0.70, 6.2), 0.08, 0.14, "brass", axis="y", sides=6)
    bz, by = -1.9, BOILER_Y + BOILER_R * FLAT
    B(mk, p, -0.92, 0.92, by - 0.2, by + 0.16, bz - 0.36, bz + 0.36, "iron")                       # pie de la campana
    for s in (-1, 1):
        B(mk, p, s * 0.72, s * 0.88, by + 0.1, by + 1.55, bz - 0.1, bz + 0.1, "iron")              # horquilla
    mk.cyl(p, (0, by + 1.34, bz), 0.09, 1.7, "iron", axis="x", sides=6)                            # muñón
    mk.hull(p, ring_pts((0, by + 0.27, bz), 0.6, "y", 12) + ring_pts((0, by + 0.8, bz), 0.4, "y", 12), "brass")
    mk.hull(p, ring_pts((0, by + 0.76, bz), 0.415, "y", 12) + ring_pts((0, by + 1.18, bz), 0.41, "y", 12)
            + ring_pts((0, by + 1.36, bz), 0.3, "y", 12) + ring_pts((0, by + 1.42, bz), 0.12, "y", 12), "brass")

    # farol de caja sobre el frente de la caja de humo
    B(mk, p, -0.6, 0.6, top_sb - 0.25, top_sb + 0.45, -15.0, -13.75, "iron")                      # ménsula
    ly0 = top_sb + 0.4
    mk.hull(p, [(x, y, -13.8) for x in (-0.78, 0.78) for y in (ly0, ly0 + 1.5)]
            + [(x, y, LAMP_Z) for x in (-0.95, 0.95) for y in (ly0 - 0.06, ly0 + 1.68)], "paint_red")
    mk.hull(p, [(x, ly0 + 1.6, z) for x in (-1.05, 1.05) for z in (-15.48, -13.7)]
            + [(x, ly0 + 2.2, z) for x in (-0.35, 0.35) for z in (-14.95, -14.25)], "brass")                # techo
    mk.cyl(p, (0, ly0 + 2.4, -14.6), 0.15, 0.5, "iron", axis="y", sides=6)                          # chimenea del farol
    mk.cyl(p, (0, ly0 + 2.68, -14.6), 0.27, 0.1, "iron", axis="y", sides=6)
    annulus(mk, p, (0, ly0 + 0.8, LAMP_Z - 0.03), 0.62, 0.82, 0.14, "brass", axis="z", sides=12)   # aro del vidrio

    # pasamanos a los dos lados de la caldera
    for s in (-1, 1):
        y = 7.95
        bar(mk, p, (s * 1.98, y, -14.4), (s * 1.98, y, 0.9), 0.12, 0.12, "iron", ext=0.05)
        bar(mk, p, (s * 1.98, y, 0.9), (s * 2.38, y, 3.2), 0.12, 0.12, "iron", ext=0.05)
        bar(mk, p, (s * 2.38, y, 3.2), (s * 2.38, y, 10.7), 0.12, 0.12, "iron", ext=0.05)
        for z, x0, x1 in ((-13.0, 1.98, 1.75), (-7.0, 1.98, 1.55), (-1.0, 1.98, 1.55), (5.0, 2.38, 2.0), (9.6, 2.38, 2.0)):
            bar(mk, p, (s * x0, y, z), (s * x1, y, z), 0.1, 0.1, "iron", ext=0.03)
    return p


def build_glows(mk):
    g = mk.part("Headlamp_Glow", (0, 0, 0))
    ly = BOILER_Y + SMOKE_R * FLAT + 0.4 + 0.8
    mk.cyl(g, (0, ly, LAMP_Z), 0.64, 0.1, "lamp_glow", axis="z", sides=12)
    f = mk.part("Firebox_Glow", (0, 0, 0))
    x0, x1, y0, y1 = DOOR
    B(mk, f, x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, 12.0, 12.3, "lamp_glow")


# ---------------- bastidor, quitapiedras, cilindros, estribos ----------------
def build_frame(mk):
    f = mk.part("Frame", (0, 0, 0))
    for s in (-1, 1):
        B(mk, f, s * 1.4, s * 1.72, 2.2, 3.6, -15.25, 18.9, "iron")                               # largueros
    B(mk, f, -3.7, 3.7, 2.1, 3.3, -15.9, -15.2, "paint_red")                                       # viga del frente
    for s in (-1, 1):
        B(mk, f, s * 3.62, s * 3.79, 2.05, 3.35, -15.95, -15.15, "iron")                           # puntas de la viga
    B(mk, f, -3.2, 3.2, 2.0, 3.32, 18.4, 18.99, "wood_dark")                                       # viga de atrás
    B(mk, f, -0.38, 0.38, COUPLER_Y - 0.32, COUPLER_Y + 0.32, 18.6, 19.0, "iron")                  # bolsillo del enganche

    # quitapiedras: barras inclinadas en cuña
    yb, yt, zt = 0.35, 2.95, -15.95

    def zb(x):
        return Z_TIP + abs(x) / 3.5 * (-15.9 - Z_TIP)

    for i in range(-5, 6):
        x = 0.6 * i
        if i == 4:
            continue                                                                                # una barra que falta
        a = (x, yb + 0.08, zb(x) + 0.06)
        b = (x, yt, zt)
        if i == -3:
            a = (x + 0.22, yb + 0.25, zb(x) + 0.2)                                                 # una doblada
        bar(mk, f, a, b, 0.16, 0.16, "paint_red", up=(0, 0, -1))
    for s in (-1, 1):
        bar(mk, f, (0, yb, Z_TIP), (s * 3.55, yb, -15.85), 0.2, 0.2, "paint_red", ext=0.05)        # cantos de abajo
    B(mk, f, -3.6, 3.6, 2.8, 3.05, -16.1, -15.85, "paint_red")                                     # travesaño de arriba
    bar(mk, f, (0, yb + 0.02, Z_TIP - 0.02), (0, yt - 0.1, zt - 0.05), 0.24, 0.12, "iron", up=(0, 0, -1))  # lomo de hierro

    # bogie: largueros de afuera, cajas de grasa, traviesa y pivote
    for s in (-1, 1):
        B(mk, f, s * 2.8, s * 3.0, 1.15, 1.75, -14.3, -7.5, "iron")
        for z in PILOT_Z:
            B(mk, f, s * 2.75, s * 3.1, 1.05, 1.85, z - 0.35, z + 0.35, "iron")
    B(mk, f, -2.98, 2.98, 1.7, 2.15, -11.3, -10.5, "iron")
    B(mk, f, -0.6, 0.6, 2.1, 3.05, -11.2, -10.6, "iron")

    # cilindros, cajas de vapor, montura y caños de vapor
    B(mk, f, -2.75, 2.75, 3.0, 5.2, -12.2, -9.63, "iron")
    for s in (-1, 1):
        cx = s * CYL_X
        mk.cyl(f, (cx, CYL_Y, CYL_Z), CYL_R, CYL_L, "gunmetal", axis="z", sides=10)
        for zz in (CYL_Z - CYL_L / 2 - 0.02, CYL_Z + CYL_L / 2 + 0.02):
            mk.cyl(f, (cx, CYL_Y, zz), CYL_R + 0.06, 0.2, "brass", axis="z", sides=10)
        B(mk, f, cx - 0.55, cx + 0.55, CYL_Y + 0.5, CYL_Y + 1.35, CYL_Z - 1.2, CYL_Z + 1.2, "gunmetal")
        B(mk, f, cx - 0.62, cx + 0.62, CYL_Y + 1.32, CYL_Y + 1.46, CYL_Z - 1.28, CYL_Z + 1.28, "brass")
        pipe(mk, f, (s * 1.85, 6.1, -11.0), (s * 3.3, CYL_Y + 1.25, -11.0), 0.2, "iron")
        # vástago, cruceta, guías y yugo
        pipe(mk, f, (cx, CYL_Y, CYL_Z + CYL_L / 2), (cx, CYL_Y, XHEAD_Z), 0.09, "steel_light", sides=6)
        B(mk, f, s * (CYL_X - 0.3), s * (CYL_X + 0.15), CYL_Y - 0.24, CYL_Y + 0.24, XHEAD_Z - 0.35, XHEAD_Z + 0.35,
          "steel_light")
        for dy in (0.31, -0.31):
            B(mk, f, s * (CYL_X - 0.12), s * (CYL_X + 0.12), CYL_Y + dy - 0.06, CYL_Y + dy + 0.06,
              CYL_Z + CYL_L / 2 + 0.05, -4.2, "steel_light")
        B(mk, f, s * 1.6, s * 3.6, CYL_Y - 0.6, CYL_Y + 0.6, -4.3, -4.0, "iron")

        # estribo a lo largo de la caldera (se camina): tablas y canto de hierro
        B(mk, f, s * RB_X0, s * RB_X1, RB_Y - 0.25, RB_Y, RB_Z0, Z_CAB_F + 0.05, "wood_dark")
        B(mk, f, s * (RB_X1 - 0.06), s * (RB_X1 + 0.05), RB_Y - 0.42, RB_Y + 0.05, RB_Z0 - 0.02, Z_CAB_F + 0.04, "iron")
        for z in (-8.0, -3.0, 2.0, 7.0):
            B(mk, f, s * 1.8, s * 2.15, RB_Y - 0.4, RB_Y - 0.22, z - 0.12, z + 0.12, "iron")
        # escalones: del frente (sobre la viga) y de la cabina
        B(mk, f, s * 2.9, s * 3.75, 3.28, 3.4, -15.85, -15.0, "iron")
        for z in (-15.72, -15.28):
            B(mk, f, s * 3.42, s * 3.5, 1.32, 3.36, z - 0.05, z + 0.05, "iron")
        B(mk, f, s * 3.25, s * 3.65, 1.3, 1.42, -15.85, -15.15, "iron")
        for z in (17.75, 18.6):
            B(mk, f, s * 3.18, s * 3.28, 1.2, 3.35, z - 0.06, z + 0.06, "iron")
        for y in (1.25, 2.35):
            B(mk, f, s * 2.95, s * 3.55, y, y + 0.12, 17.6, 18.75, "iron")
    return f


# ---------------- cabina ----------------
def build_cab(mk):
    c = mk.part("Cab", (0, 0, 0))
    zf, zb = Z_CAB_F, Z_CAB_B
    B(mk, c, -3.3, 3.3, 3.3, DECK_Y - 0.08, zf, zb, "iron")                                        # chapa del piso
    for i in range(7):                                                                              # tablas con juntas de chapa
        xa = -3.28 + i * 6.56 / 7
        B(mk, c, xa, xa + 6.56 / 7 - 0.07, DECK_Y - 0.12, DECK_Y, zf + 0.02, zb - (0.01 if i % 2 else 0.03), "wood_dark")
    wy0, wy1 = 7.15, 10.35
    wins = ((11.45, 14.15), (15.25, 17.95))
    for s in (-1, 1):
        xo, xi = s * CAB_X, s * (CAB_X - 0.2)
        B(mk, c, xi, xo, DECK_Y - 0.02, wy0, zf, zb, "paint_red")                                  # paño bajo
        B(mk, c, xi, xo, wy1, EAVE_Y, zf, zb, "paint_red")                                          # friso
        edges = [zf] + [v for w in wins for v in w] + [zb]
        for z0, z1 in zip(edges[0::2], edges[1::2]):
            B(mk, c, s * (CAB_X - 0.18), s * (CAB_X - 0.02), wy0, wy1, z0, z1, "paint_red")         # pilares
        # molduras de madera oscura
        B(mk, c, s * 3.47, s * 3.56, DECK_Y - 0.01, DECK_Y + 0.42, zf - 0.01, zb + 0.01, "wood_dark")   # zócalo
        B(mk, c, s * 3.47, s * 3.57, wy0 - 0.15, wy0 + 0.05, zf - 0.02, zb + 0.02, "wood_dark")         # alféizar
        B(mk, c, s * 3.47, s * 3.58, EAVE_Y - 0.4, EAVE_Y - 0.08, zf - 0.03, zb + 0.03, "wood_dark")   # alero
        for z0, z1 in ((zf - 0.04, zf + 0.26), (zb - 0.26, zb + 0.04)):
            B(mk, c, s * 3.46, s * 3.59, DECK_Y - 0.03, EAVE_Y - 0.06, z0, z1, "wood_dark")           # esquineros
        for w0, w1 in wins:
            for z0, z1 in ((w0 - 0.1, w0 + 0.02), (w1 - 0.02, w1 + 0.1)):
                B(mk, c, s * 3.485, s * 3.545, wy0 + 0.03, wy1 + 0.02, z0, z1, "wood_dark")           # jambas
            B(mk, c, s * 3.48, s * 3.55, wy1 - 0.05, wy1 + 0.08, w0 - 0.14, w1 + 0.14, "wood_dark")   # dintel
        # agarraderas de la espalda
        bar(mk, c, (s * 3.4, 5.0, 19.12), (s * 3.4, 10.0, 19.12), 0.1, 0.1, "iron")
        for y in (5.2, 9.8):
            B(mk, c, s * 3.36, s * 3.44, y - 0.06, y + 0.06, 18.98, 19.14, "iron")

    # frente: recorte alrededor de la caldera, ventanitas a los costados
    R = WT_R + 0.02
    top = [(x, roof_under(x) + 0.05) for x in (2.45, 1.6, 0.8, 0.0, -0.8, -1.6, -2.45)]
    arc = [(R * math.cos(a), WT_Y + R * math.sin(a)) for a in [math.pi * (1 - i / 8) for i in range(9)]]
    prof = [(2.45, WT_Y)] + top + [(-2.45, WT_Y)] + arc
    mk.prism(c, prof, 0.2, "paint_red", plane="xy", center=(0, 0, zf + 0.1))
    for s in (-1, 1):
        B(mk, c, s * 1.88, s * 2.47, DECK_Y - 0.02, 6.6, zf + 0.01, zf + 0.19, "paint_red")
        B(mk, c, s * 2.45, s * 3.29, DECK_Y - 0.02, 8.0, zf, zf + 0.2, "paint_red")
        B(mk, c, s * 2.46, s * 2.62, 8.0, 10.2, zf + 0.01, zf + 0.19, "paint_red")
        B(mk, c, s * 3.12, s * 3.28, 8.0, 10.2, zf + 0.01, zf + 0.19, "paint_red")
        mk.hull(c, [(s * x, y, z) for x in (2.457, 3.29) for z in (zf, zf + 0.2)
                    for y in (10.2, roof_under(x) + 0.05)], "paint_red")
        B(mk, c, s * 2.4, s * 3.35, 7.88, 8.06, zf - 0.08, zf + 0.02, "wood_dark")                  # alféizar del frente

    # techo curvo de chapa: tablas en arco (las facetas son la curva), frentes de madera
    n = 8
    for i in range(n):
        xa = -ROOF_HALF + i * 2 * ROOF_HALF / n
        xb = xa + 2 * ROOF_HALF / n
        ya, yb = roof_top(xa), roof_top(xb)
        ang = math.atan2(yb - ya, xb - xa)
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        ln = math.hypot(xb - xa, yb - ya) + 0.04
        z0, z1 = (zf - 0.2, zb + 0.3) if i % 2 == 0 else (zf - 0.19, zb + 0.29)
        mk.box(c, (mx + math.sin(ang) * ROOF_T / 2, my - math.cos(ang) * ROOF_T / 2, (z0 + z1) / 2),
               (ln, ROOF_T, z1 - z0), "iron", rot=(0, 0, math.degrees(ang)))
    xs = [-3.88 + 7.76 * k / 10 for k in range(11)]
    fascia = [(x, roof_top(x) + 0.03) for x in xs] + [(x, roof_top(x) - 0.32) for x in reversed(xs)]
    mk.prism(c, fascia, 0.1, "wood_dark", plane="xy", center=(0, 0, zf - 0.23))
    mk.prism(c, fascia, 0.1, "wood_dark", plane="xy", center=(0, 0, zb + 0.32))

    # frente del hogar: bloque, placa de la caldera con la boca, relojes, nivel, cuadrante del regulador
    B(mk, c, -1.9, 1.9, DECK_Y - 0.02, WT_Y, zf + 0.18, Z_BH - 0.05, "gunmetal")
    segs = [a for a in [math.radians(-22 + 224 * k / 14) for k in range(15)]]
    up = [(R * math.cos(a), WT_Y + R * math.sin(a)) for a in segs]
    mk.hull(c, [(x, y, z) for x, y in up for z in (Z_BH - 0.02, Z_BH + 0.22)], "gunmetal")
    x0, x1, y0, y1 = DOOR
    ys = up[0][1]
    B(mk, c, -1.9, x0, DECK_Y - 0.02, ys + 0.01, Z_BH - 0.03, Z_BH + 0.21, "gunmetal")
    B(mk, c, x1, 1.9, DECK_Y - 0.02, ys + 0.01, Z_BH - 0.03, Z_BH + 0.21, "gunmetal")
    B(mk, c, x0 - 0.01, x1 + 0.01, DECK_Y - 0.02, y0, Z_BH - 0.04, Z_BH + 0.2, "gunmetal")
    B(mk, c, x0 - 0.01, x1 + 0.01, y1, ys + 0.02, Z_BH - 0.04, Z_BH + 0.2, "gunmetal")
    for s in (-1, 1):
        B(mk, c, s * 0.86, s * 1.06, 4.5, 4.7, Z_BH + 0.15, Z_BH + 0.3, "iron")                    # hojas de bisagra
    zf_bh = Z_BH + 0.22
    for x, y, r in ((-0.65, 8.3, 0.3), (0.65, 8.3, 0.3), (0.0, 8.55, 0.34)):
        mk.cyl(c, (x, y, zf_bh + 0.05), r, 0.14, "brass", axis="z", sides=10)                      # relojes
        mk.cyl(c, (x, y, zf_bh + 0.135), r - 0.08, 0.04, "steel_light", axis="z", sides=10)
    pipe(mk, c, (-1.45, 6.55, zf_bh + 0.12), (-1.45, 7.95, zf_bh + 0.12), 0.08, "steel_light", sides=6)   # nivel
    for y in (6.5, 8.0):
        mk.cyl(c, (-1.45, y, zf_bh + 0.06), 0.13, 0.16, "brass", axis="z", sides=6)
    pipe(mk, c, (-0.85, 8.95, zf_bh + 0.07), (0.85, 8.95, zf_bh + 0.07), 0.1, "brass", sides=6)           # caño de la torreta
    px, py, pz = THR_PIVOT
    B(mk, c, px - 0.12, px + 0.12, py - 0.2, py + 0.2, zf_bh - 0.04, pz - 0.02, "brass")             # ménsula del regulador
    sector = [(zf_bh - 0.02, py - 0.15), (zf_bh - 0.02, py + 1.32)]
    sector += [(pz + 1.32 * math.cos(math.radians(a)), py + 1.32 * math.sin(math.radians(a))) for a in (85, 70, 55, 40, 28)]
    sector += [(pz + 0.35 * math.cos(math.radians(28)), py + 0.35 * math.sin(math.radians(28)))]
    mk.prism(c, sector, 0.08, "brass", plane="zy", center=(px - 0.22, 0, 0))

    # palanca de cambio (a la derecha), asientos
    jx = 2.3
    quad = [(13.8, DECK_Y - 0.02)] + [(13.0 + math.cos(math.radians(a)), DECK_Y + math.sin(math.radians(a)))
                                      for a in (40, 70, 90, 110, 140)] + [(12.2, DECK_Y - 0.02)]
    mk.prism(c, quad, 0.08, "iron", plane="zy", center=(jx - 0.06, 0, 0))
    bar(mk, c, (jx + 0.07, DECK_Y - 0.05, 13.0), (jx + 0.07, 7.0, 13.9), 0.12, 0.12, "iron", up=(1, 0, 0))
    B(mk, c, jx - 0.01, jx + 0.15, 6.9, 7.25, 13.82, 14.02, "brass")
    for s in (-1, 1):
        B(mk, c, s * 2.4, s * 3.28, DECK_Y - 0.02, 5.85, 15.5, 17.7, "wood_dark")
        B(mk, c, s * 2.36, s * 3.29, 5.83, 5.97, 15.45, 17.75, "wood_dark")
    return c


def build_moving(mk):
    # puerta del hogar: bisagra a su izquierda (-X), abre 90° hacia la cabina
    x0, x1, y0, y1 = DOOR
    hinge = (x0 - 0.1, (y0 + y1) / 2, Z_BH + 0.29)
    d = mk.part("FireboxDoor", hinge)
    B(mk, d, x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, Z_BH + 0.23, Z_BH + 0.35, "iron")
    for y in (y0 + 0.15, y1 - 0.15):
        mk.cyl(d, (x0 - 0.13, y, Z_BH + 0.29), 0.08, 0.3, "iron", axis="y", sides=6)                # nudillos
    bar(mk, d, (x1 - 0.12, y0 + 0.3, Z_BH + 0.43), (x1 - 0.12, y1 - 0.3, Z_BH + 0.43), 0.09, 0.09, "brass")
    for y in (y0 + 0.3, y1 - 0.3):
        B(mk, d, x1 - 0.17, x1 - 0.07, y - 0.05, y + 0.05, Z_BH + 0.33, Z_BH + 0.45, "brass")
    for k in range(3):                                                                              # rejilla del tiro
        B(mk, d, -0.45, 0.25, y0 + 0.35 + 0.17 * k, y0 + 0.43 + 0.17 * k, Z_BH + 0.34, Z_BH + 0.39, "brass")

    # regulador: la palanca, con el origen en su base
    px, py, pz = THR_PIVOT
    t = mk.part("Throttle", THR_PIVOT)
    mk.cyl(t, THR_PIVOT, 0.18, 0.4, "iron", axis="x", sides=8)
    bar(mk, t, (px, py, pz), (px, py + 1.62, pz), 0.15, 0.17, "steel_light", up=(0, 0, 1))
    bar(mk, t, (px + 0.11, py + 0.35, pz), (px + 0.11, py + 1.45, pz), 0.07, 0.07, "iron", up=(0, 0, 1))
    for y in (py + 0.35, py + 1.45):
        B(mk, t, px + 0.05, px + 0.13, y - 0.04, y + 0.04, pz - 0.03, pz + 0.03, "iron")
    mk.ball(t, (px, py + 1.8, pz), 0.24, "brass", subdiv=1)

    # ruedas motrices con bielas (una pieza, origen en el eje delantero)
    w = mk.part("DriveWheels", (0, DRIVER_R, DRIVER_Z[0]))
    pins = []
    for z in DRIVER_Z:
        for s in (-1, 1):
            spoked_wheel(mk, w, (s * RAIL_X, DRIVER_R, z), DRIVER_R, spokes=14, counter=0.0)
            pc = (DRIVER_R, z - CRANK)
            mk.cyl(w, (s * (RAIL_X + 0.25), pc[0], pc[1]), 0.3, 0.36, "paint_red", axis="x", sides=8)   # manivela
            reach = 3.02 if z == DRIVER_Z[0] else 3.32
            mk.cyl(w, (s * (2.8 + reach) / 2, pc[0], pc[1]), 0.15, reach - 2.8, "steel_light", axis="x", sides=6)
            pins.append((s, pc))
        mk.cyl(w, (0, DRIVER_R, z), 0.3, 4.6, "iron", axis="x", sides=8)                          # eje
    for s in (-1, 1):
        (_, a), (_, b) = [pp for pp in pins if pp[0] == s]
        bar(mk, w, (s * 2.94, a[0], a[1]), (s * 2.94, b[0], b[1]), 0.12, 0.3, "steel_light", up=(0, 1, 0))  # biela de acople
        for y_, z_ in (a, b):
            mk.cyl(w, (s * 2.94, y_, z_), 0.25, 0.13, "steel_light", axis="x", sides=8)
        bar(mk, w, (s * 3.11, CYL_Y, XHEAD_Z), (s * 3.11, b[0], b[1]), 0.14, 0.3, "steel_light", up=(0, 1, 0))  # biela motriz
        mk.cyl(w, (s * 3.11, CYL_Y, XHEAD_Z), 0.24, 0.15, "steel_light", axis="x", sides=8)
        mk.cyl(w, (s * 3.11, b[0], b[1]), 0.28, 0.15, "steel_light", axis="x", sides=8)

    # ruedas del bogie
    pw = mk.part("PilotWheels", (0, PILOT_R, sum(PILOT_Z) / 2))
    for z in PILOT_Z:
        for s in (-1, 1):
            spoked_wheel(mk, pw, (s * RAIL_X, PILOT_R, z), PILOT_R, spokes=8, sides=12, tire_t=0.3, rim_t=0,
                         width=0.42, hub_r=0.34)
        mk.cyl(pw, (0, PILOT_R, z), 0.2, 5.9, "iron", axis="x", sides=8)


def build(mk):
    build_boiler(mk)
    build_glows(mk)
    build_frame(mk)
    build_cab(mk)
    build_moving(mk)
    mk.marker("_CoalTarget", (0, (DOOR[2] + DOOR[3]) / 2, Z_BH + 0.3))
    mk.marker("_ThrottleGrip", (THR_PIVOT[0], THR_PIVOT[1] + 1.8, THR_PIVOT[2]))
    mk.marker("_Coupler", (0, COUPLER_Y, Z_BACK))

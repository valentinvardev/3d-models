"""
Receta de WST_Prop_OilLamp, la lámpara de aceite colgante (prompt 136, Bloques A + C). Muerte ambiental:
se suelta de la cadena, cae y revienta.

Brief
- Silueta a 40 studs: un punto de luz (la llama Neon) bajo una pantalla ancha clara, colgando de una
  línea de cadena. Lo que se lee es la pantalla (1,1 de ancho) y el brillo.
- Medidas (de abajo arriba, base de la lámpara en y = 0): depósito de bronce en jarrón (0,68 de ancho,
  0,48 de alto) con collar; tubo de vidrio abombado (0,44 x 0,71); pantalla reflectora de hojalata
  (steel_light) en cono ancho de 1,1, con un remate y la argolla de colgar; tres varillas de bronce del
  collar a la pantalla (el armazón que la sostiene). Cadena de 2 studs (6 eslabones planos, alternados
  90°) hasta un gancho de techo a y 3,8.
- Piezas: frag01 pantalla con remate y argolla, frag02 tubo de vidrio, frag03 depósito con collar y
  varillas (los 3 del cuerpo, origen común en la base); Lamp_Glow la llama, adentro del vidrio, con el
  origen en su base; Chain con el origen en el gancho (pivote); fixed_Hook la chapa del techo.
- Variante OilLamp_Wall (x = 2,5): el mismo cuerpo colgado de una ménsula de hierro con chapa a la pared
  (la pared en +Z): OilLamp_Wall_fixed_Bracket, OilLamp_Wall_frag01..03, OilLamp_Wall_Lamp_Glow.
- Inferido: forma de cada parte; las varillas; la pantalla arriba del tubo (no alrededor); el origen
  del modelo en la base de la lámpara (Bloque A) y no en el techo; la chapa del gancho como fixed_Hook;
  la variante de pared como lámpara de ménsula; nombres de la variante.

Vueltas: 1) pasa la revisión (las varillas se corrigieron antes de construir: rozaban la panza del vidrio).

Revisión
- 340 triángulos (cuerpo 244, cadena 72, gancho 24) contra 200; la variante de pared 292. El cuerpo
  tiene tres materiales bien separados (bronce, vidrio, hojalata) y el armazón de varillas, que es lo
  que la hace lámpara y no un frasco.
- La llama queda encerrada en el vidrio (aviso "enclosed" esperado, como los ojos en las cuencas); en la
  captura no se ve porque Blender pinta el vidrio opaco, en Studio el vidrio es Glass.
- Medidas: 3,88 de alto con el gancho; pantalla 1,02 de ancho. Fragmentos: pantalla 39 %, vidrio 23 %,
  depósito 38 %; mínimos 0,41-0,67.
- Origen del modelo en la base de la lámpara (Bloque A); para colgarla se usa el pivote de Chain (el
  gancho, a y 3,8).
"""

import math

from mathutils import Vector

CHAIN_TOP = 3.8
HANGER_Y = 1.72


def rings(c, prof, sides=8):
    """Puntos de anillos (y, r) alrededor del eje vertical que pasa por c."""
    return [(c[0] + r * math.cos(2 * math.pi * (k + 0.5) / sides), c[1] + y, c[2] + r * math.sin(2 * math.pi * (k + 0.5) / sides))
            for y, r in prof for k in range(sides)]


def bar(mk, part, a, b, w, mat):
    """Varilla de sección cuadrada de a a b."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    u = d.cross(Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))).normalized()
    v = d.cross(u)
    mk.hull(part, [tuple(p + (su * u + sv * v) * w / 2) for p in (a, b) for su in (-1, 1) for sv in (-1, 1)], mat)


def lamp_body(mk, prefix, x0):
    c = (x0, 0.0, 0.0)
    # ---- depósito de bronce con collar y varillas ----
    font = mk.part(f"{prefix}frag03", c)
    mk.hull(font, rings(c, ((0.0, 0.08), (0.12, 0.22), (0.3, 0.34), (0.48, 0.24))), "brass")
    mk.hull(font, rings(c, ((0.46, 0.2), (0.56, 0.2))), "brass")                        # collar
    for k in range(3):                                                                  # varillas del armazón
        a = math.radians(120 * k + 90)
        # del borde del collar justo hasta la pantalla: más adentro rozaban la panza del vidrio (r 0,22)
        bar(mk, font, (x0 + 0.2 * math.cos(a), 0.5, 0.2 * math.sin(a)),
            (x0 + 0.42 * math.cos(a), 1.27, 0.42 * math.sin(a)), 0.045, "brass")
    # ---- tubo de vidrio ----
    glass = mk.part(f"{prefix}frag02", c)
    mk.hull(glass, rings(c, ((0.56, 0.14), (0.72, 0.22), (0.92, 0.2), (1.27, 0.12))), "glass")
    # ---- pantalla de hojalata con remate y argolla ----
    shade = mk.part(f"{prefix}frag01", c)
    mk.hull(shade, rings(c, ((1.27, 0.55), (1.52, 0.2))), "steel_light")
    mk.hull(shade, rings(c, ((1.5, 0.11), (1.66, 0.07)), sides=6), "brass")              # remate
    mk.box(shade, (x0, HANGER_Y - 0.02, 0), (0.05, 0.16, 0.14), "iron")                 # argolla
    # ---- llama (adentro del vidrio) ----
    glow = mk.part(f"{prefix}Lamp_Glow", (x0, 0.6, 0))
    mk.hull(glow, [(x0, 0.6, 0)] + rings(c, ((0.7, 0.07),), sides=6) + [(x0, 0.93, 0)], "lamp_glow")


def build(mk):
    lamp_body(mk, "", 0.0)
    # ---- cadena de 2 studs: eslabones planos alternados ----
    ch = mk.part("Chain", (0, CHAIN_TOP, 0))
    n = 6
    step = (CHAIN_TOP - HANGER_Y) / n
    for i in range(n):
        yc = HANGER_Y + step * (i + 0.5)
        size = (0.14, step + 0.06, 0.05) if i % 2 == 0 else (0.05, step + 0.06, 0.14)
        mk.box(ch, (0, yc, 0), size, "iron")
    # ---- gancho de techo ----
    hk = mk.part("fixed_Hook", (0, 0, 0))
    mk.box(hk, (0, CHAIN_TOP + 0.04, 0), (0.34, 0.08, 0.34), "iron")
    mk.box(hk, (0, CHAIN_TOP - 0.04, 0), (0.06, 0.12, 0.16), "iron")

    # ---- variante de pared: el mismo cuerpo colgado de una ménsula ----
    x0 = 2.5
    lamp_body(mk, "OilLamp_Wall_", x0)
    br = mk.part("OilLamp_Wall_fixed_Bracket", (x0, 0, 0))
    mk.box(br, (x0, 1.75, 0.67), (0.3, 0.95, 0.06), "iron")                            # chapa a la pared
    mk.box(br, (x0, HANGER_Y + 0.13, 0.3), (0.08, 0.1, 0.78), "iron")                  # brazo
    bar(mk, br, (x0, 1.35, 0.64), (x0, HANGER_Y + 0.1, 0.18), 0.07, "iron")              # tornapunta
    mk.box(br, (x0, HANGER_Y + 0.05, -0.05), (0.06, 0.12, 0.1), "iron")                 # gancho al final del brazo

"""
Receta de WST_Boss_Preacher_TrueForm, la verdadera forma de Ezekiel Crane (prompt 063, Bloques A + D + H + G).
Jefe final, fase 3: el cuerpo casi entero de plata viva con los restos de la levita negra.

Brief
- Silueta a 40 studs: un gigante blanco plateado (7,8) de hombros anchos y brazos larguísimos (las puntas
  de los dedos le llegan a la rodilla), una aureola de 7 púas de cristal detrás de la cabeza, el pecho
  abierto con un corazón de neón entre costillas de cristal, la levita negra abierta y hecha jirones,
  la mano derecha convertida en tres garras y la cruz de hierro arrastrada atrás desde esa mano.
- Es el mismo personaje que WST_Boss_Preacher: la cabeza se arma con los mismos puntos de la cara humana
  (cráneo, mandíbula fina, pómulos, nariz, boca de labios finos con la comisura derecha rota), escalada
  con K = 1,5 en vez de 1,25; la levita es la misma cloth_black y el pelo gris lacio queda del lado
  izquierdo. La paleta de plata es la del Predicador (silver_crust y silver_neon).
- Escala: H = 7,8 (k = 1,5). Miembros alargados (prompt): cadera 0,50 H (3,90), rodilla 0,275 H
  (2,145), tobillo 0,05 H (0,39), cintura 0,57 H (4,446), hombro 0,76 H (5,928), cuello 0,80 H (6,24),
  codo 0,56 H (4,368), muñeca 0,37 H (2,886). Hombros 1,3 veces los del humano: SH_X 0,95 -> 1,24;
  codos ±1,46, muñecas ±1,67 (8° hacia afuera), caderas ±0,44, brazos en z = -0,08. Va a la ficha.
- Piezas (origen): las 15 de R15 en su articulación; Eyes (cuello, como Head); Silver_Heart (centro del
  corazón, (0; 5,30; -0,39): late escalándose sobre sí mismo y el rig lo suelda a UpperTorso porque cae
  adentro de su caja); Acc_IronCross (el agarre, dentro del puño derecho: el rig la suelda a RightHand);
  _Grip (el puño derecho sobre la barra larga), _Grip2 (0,95 más arriba por la barra, la izquierda al
  animar), _Tip (centro de la punta de arriba).
- Plata: cada segmento es un núcleo de silver_neon cubierto de placas de cristal silver_crust con
  cresta (0,06-0,14 afuera); las juntas entre placas son las vetas de neón. En la cabeza: casco de
  costra pintado, media máscara de plata sobre la mitad derecha de la cara con tres grietas talladas en
  neón, y racimos de cristal en hombros, espalda, antebrazo derecho, rodillas y pies.
- Tallado: cuencas, boca, grietas de la máscara, el pecho abierto (paredes skin_dead_dark). Pintado: la
  costra del cráneo (plano inclinado que deja la carne en la cara de abajo), las paredes de las cuencas.
- Inferido (el prompt no lo dice):
  - La cruz va en la mano derecha tomada por el pie de la barra larga (0,62 del extremo), con la cabeza
    apoyada en el piso detrás del jefe (arrastrada, 39° bajo la horizontal y abierta 12° hacia afuera).
    Con el brazo colgando no hay otra forma: parada atravesaría el antebrazo, colgando atravesaría el
    piso. Así no toca el cuerpo, el puño la cierra de verdad, la relación mano-cruz sirve para levantarla
    a dos manos (_Grip2) y el código o el rig la sueldan a RightHand. La costra de plata sube desde el
    pie, que queda en el puño: la plata del jefe se está comiendo la cruz.
  - La cruz: latina, travesaño a 3,30 del pie (brazo de arriba = brazos de los costados = 1,20), las
    cuatro puntas ensanchadas (0,64 × 0,44), un rombo en el cruce, bandas y puntas de óxido.
  - Toda la plata va dentro de las 15 piezas: es el cuerpo, no un overlay que se saca (Bloque G). La
    única pieza Silver_ es el corazón. En Studio, una pieza con vetas de neón y placas es una sola
    MeshPart: las vetas no brillan salvo que se separen (dudoso, ver Revisión).
  - Carne: la mandíbula, la boca, el mentón, la mejilla izquierda y la mano izquierda (prompt); el resto
    de la cabeza es costra. Ojos de neón en cuencas oscuras, para que brillen contra la plata.
  - Restos de la levita: atrás y los hombros enteros hasta la mitad de la espalda, deshilachada en tiras
    que llegan a 4,48 (arriba de la cintura); dos paneles de adelante abiertos y rotos; en LowerTorso,
    una falda de jirones atrás y a los costados que termina en 3,86 (arriba de la cadera); los faldones
    siguen en los muslos (cortados en la cadera, como en la forma humana) hasta 2,78, quemados (la
    iglesia arde en la fase 3).
  - Pies de cristal con tres garras, sin botas. Sin pelo (ver Revisión).
  - Postura (Bloque H): hombro derecho 0,1 más bajo (carga la cruz), espalda alta redondeada, cuello
    20° adelante, la cabeza adelantada y caída 10°.

Vueltas: 1) primera versión, 5430 triángulos; titilaban las puntas de los 8 miembros (la tapa de las placas
en el plano de la tapa del núcleo), la falda contra la tapa de LowerTorso (4,506), los dos faldones cruzados
en x = 0 y jirones vecinos a la misma altura (4,65); aristas sueltas donde una grieta tocaba el borde de la
máscara; hombros 3,225 (1,37 veces los del humano); atrás, el panel cortado en 5,0 con jirones largos sobre la
faja clara se leía como una boca con dientes; neón corrido en la cara interna de brazos y muslos; la máscara
no se distinguía del casco de costra · 2) placas 0,015 más allá de las tapas, falda en 4,491, faldones hasta
135°, jirones alternados ±0,007, crestas del deltoide 0,06-0,10 (hombros 3,174), espalda entera hasta 4,62 con
ruedo corto, dos tiras por hombro adelante, placas bajas en la cara interna, la máscara baja hasta el mentón,
sin pelo, costillas en gancho · 3) el neón rodeaba al corazón (cyan sobre cyan): placas bajas a los costados
del hueco y costillas en diagonal; palma de la garra de 0,42 a 0,36 con nudillos de cristal (reconstrucción:
el faldón en 4,00 caía en la tapa del muslo, va en 3,99) · 4) palma de pentágonos girados (de frente era una
caja), racimo de cristales en el pie de la cruz en vez del collar, la grieta que dejaba una arista suelta en
el cruce de los dos cascos de la máscara pasa a ser una rama de la otra · 5) línea de costra 4,80 + 0,6·x: el
ojo izquierdo queda adentro de la costra (antes la línea lo cortaba) · 6) corazón de 0,594 a 0,70 de ancho (el
icosaedro llega a 0,894 r en x), hueco 0,04 más ancho para que lata, costado derecho de la cabeza en costra
hasta z = -0,80 (reconstrucción: las costillas en x = 0,36 quedaban coplanares con la pared nueva, van en 0,44).

Revisión
- 5816 triángulos contra 6000 (97 %): UpperTorso 1248, Head 1126, Acc_IronCross 840 (chanflanes, bandas de
  óxido, costra), miembros 196-268 (núcleo y placas). Ninguna pieza pasa de 1300. 10 colores.
- Alto 7,83 sin la aureola (H 7,8), 8,50 con ella. Cabeza 1,59 (1/5 de H). Hombros 3,174 de borde a borde
  de los brazos: 1,35 veces los 2,358 del humano por las crestas de las placas (las articulaciones, 0,95 ->
  1,24, son 1,30 veces). Ancho 5,25 (mano izquierda a la punta del brazo de la cruz), fondo 4,67.
- Cruz: 4,50 de hierro (4,61 con la costra del pie), brazos 2,40, barras 0,35 (travesaño 0,344, para que sus
  caras no caigan en el plano de las del palo), puntas 0,64 × 0,44; 38,4° bajo la horizontal y 12° hacia afuera;
  la punta de arriba a 0,019 del piso. Corazón 0,70 × 0,70 (0,75 de alto con las púas), 0,60 de fondo.
- Rig: los orígenes en su articulación; solapes de 0,15-0,18 en codo, rodilla, cadera y cintura, 0,12-0,18
  en la muñeca. La levita de UpperTorso termina en 4,471 (cintura 4,446), los faldones de los muslos en 2,755
  (rodilla 2,145).
- Aceptado / dudoso:
  - La cruz apoya en el piso en reposo: en un idle que baje la mano hay que levantarla con la muñeca
    (anim_preview la va a marcar). Otra relación mano-cruz es cambiar `yaw` y el ángulo en iron_cross().
  - Las vetas de neón van dentro de cada pieza: en Studio una MeshPart tiene un solo Material, así que se ven
    cyan pero no brillan salvo que se separen en piezas Silver_<Segmento>. Corazón y ojos sí son puro neón.
  - Tobillo: la canilla termina 0,045 arriba de la articulación (0,435) y el pie sube hasta 0,56 adentro de
    ella; el solape es 0,125, pero en el caminante la canilla tapa el tobillo. Si al animar asoma, la sección
    de abajo de LowerLeg pasa de ANKLE + 0.06 a ANKLE - 0.03.
  - Los jirones de la falda de LowerTorso llegan a 3,83, dentro del solape de la pieza (0,07 bajo la cadera),
    como la levita del humano. Los faldones siguen en los muslos, cortados en la cadera (el prompt los pone
    solo en UpperTorso y LowerTorso).
  - Sin pelo: el gris (A8A39A) tiene el mismo valor que la costra (B9C3CC) y se leía como más costra.
"""

import math

from mathutils import Euler, Vector

import humanoid as hu

H = 7.8
K = H / 5.2                               # 1,5 (el humano usa 1,25): la misma cara, más grande
XW = 0.92                                 # cara angosta, como el humano
ANKLE, KNEE, HIP, WAIST = 0.05 * H, 0.275 * H, 0.50 * H, 0.57 * H
ELBOW, WRIST, SHOULDER, NECK = 0.56 * H, 0.37 * H, 0.76 * H, 0.80 * H
SH_X, ARM_Z, LEG_X = 1.24, -0.08, 0.44
TAN8 = math.tan(math.radians(8))
EL_X, WR_X = SH_X + (SHOULDER - ELBOW) * TAN8, SH_X + (SHOULDER - WRIST) * TAN8
NECK_P = (0.0, NECK, -0.10)
HEAD_FWD, HEAD_TILT = 0.14, -10

ring, round_ring, about = hu.ring, hu.round_ring, hu.about


def rnd(i):
    """Número fijo entre 0 y 1 para variar las placas sin azar."""
    return (math.sin(i * 12.9898 + 78.233) * 43758.5453) % 1.0


def head(pts):
    """Espacio de la cabeza del caminante (H = 5,2) -> verdadera forma: escala k, adelanta y baja 10°."""
    return about([(x * K * XW, y * K, z * K - HEAD_FWD) for x, y, z in pts], NECK_P, (HEAD_TILT, 0, 0))


def hp(p):
    return head([p])[0]


def hvec(v):
    """Una dirección del espacio de la cabeza llevada al mundo (escala y caída)."""
    e = Euler((math.radians(HEAD_TILT), 0, 0), "XYZ").to_matrix()
    return tuple(e @ Vector((v[0] * K * XW, v[1] * K, v[2] * K)))


def hnormal(n):
    """Una normal del espacio de la cabeza llevada al mundo (inversa transpuesta de la escala)."""
    e = Euler((math.radians(HEAD_TILT), 0, 0), "XYZ").to_matrix()
    return tuple((e @ Vector((n[0] / (K * XW), n[1] / K, n[2] / K))).normalized())


def arm_x(y):
    return SH_X + (SHOULDER - y) * TAN8


# ---- superficies por secciones (y, cx, cz, w, d) y placas de cristal -------------------
def sp(sec, a, off):
    """Punto de la elipse de la sección, en el ángulo a (0 = +x, 90 = atrás, 270 = frente), off afuera."""
    y, cx, cz, w, d = sec
    r = math.radians(a)
    return (cx + (w / 2 + off) * math.cos(r), y, cz + (d / 2 + off) * math.sin(r))


def interp(secs, y):
    for s0, s1 in zip(secs, secs[1:]):
        if y <= s1[0] or s1 is secs[-1]:
            t = (y - s0[0]) / (s1[0] - s0[0])
            return tuple(a + (b - a) * t for a, b in zip(s0, s1))


def plate(mk, part, secs, y0, y1, a0, a1, peak=0.10, edge=0.03, inner=-0.05, shift=0.0, tilt=0.0,
          mat="silver_crust", warp=None, detail=False):
    """Placa de cristal: base hundida en el núcleo, bordes `edge` afuera y una cresta `peak` (facetas)."""
    pts = []
    for y in (y0, y1):
        S = interp(secs, y)
        for a in (a0, a1):
            pts += [sp(S, a, inner), sp(S, a, edge)]
    am = (a0 + a1) / 2 + shift * (a1 - a0)
    for t, da in ((0.28, -tilt), (0.72, tilt)):
        pts.append(sp(interp(secs, y0 + (y1 - y0) * t), am + da * (a1 - a0), peak))
    if warp:
        pts = [warp(p) for p in pts]
    mk.hull(part, pts, mat, detail=detail)


def crystal_limb(mk, part, secs, rows, cols, seed, a0=0.0, skip=None, low=None, seam=0.06, peak=(0.07, 0.12),
                 sides=10, mirror=False):
    """Segmento de plata: núcleo de neón y placas en ladrillo; las juntas son las vetas.
    skip(a, fila) saltea placas y low(a, fila) las deja bajas (lado de adentro), por ángulo en la convención
    del lado derecho; mirror lo espeja para el izquierdo. Las placas de las puntas pasan 0,015 la tapa del
    núcleo: si terminan en el mismo plano, titilan (medido en la vuelta 1)."""
    mk.hull(part, [p for s in secs for p in round_ring(s[0], s[1], s[2], s[3], s[4], n=sides)], "silver_neon")
    ylo, yhi = secs[0][0], secs[-1][0]
    for i in range(rows):
        y0 = ylo + (yhi - ylo) * i / rows + (seam / 2 if i else -0.015)
        y1 = ylo + (yhi - ylo) * (i + 1) / rows + (-seam / 2 if i < rows - 1 else 0.015)
        S = interp(secs, (y0 + y1) / 2)
        gap = math.degrees(seam / 2 / ((S[3] + S[4]) / 4))
        for j in range(cols):
            b0 = a0 + 360 / cols * (j + 0.5 * (i % 2))
            b1 = b0 + 360 / cols
            mid = ((b0 + b1) / 2) % 360
            if skip and skip(mid, i):
                continue
            flat = bool(low and low(mid, i))
            if mirror:
                b0, b1 = 180 - b1, 180 - b0
            k = seed * 37 + i * 7 + j
            pk = 0.035 if flat else peak[0] + (peak[1] - peak[0]) * rnd(k)
            plate(mk, part, secs, y0, y1, b0 + gap, b1 - gap, peak=pk, edge=0.015 if flat else 0.03,
                  shift=0.3 * (rnd(k + 3) - 0.5), tilt=0.15 * (rnd(k + 5) - 0.5))


def frame(d):
    D = Vector(d).normalized()
    up = Vector((0, 1, 0)) if abs(D.y) < 0.9 else Vector((1, 0, 0))
    u = D.cross(up).normalized()
    return D, u, D.cross(u)


def shard(mk, part, base, d, length, w, mat="silver_crust", detail=False, sink=0.08, spin=0.0, th=None):
    """Cristal de punta: sección en rombo hundida `sink`, se ensancha al 32 % y termina en punta."""
    B = Vector(base)
    D, u, v = frame(d)
    c, s = math.cos(math.radians(spin)), math.sin(math.radians(spin))
    u, v = u * c + v * s, v * c - u * s
    th = w if th is None else th
    pts = []
    for t, k in ((-sink, 0.75), (length * 0.32, 1.0)):
        P = B + D * t
        pts += [tuple(P + u * (w / 2 * k)), tuple(P - u * (w / 2 * k)), tuple(P + v * (th / 2 * k)),
                tuple(P - v * (th / 2 * k))]
    pts.append(tuple(B + D * length))
    mk.hull(part, pts, mat, detail=detail)


def flap(mk, part, a, b, c, n, th=0.03, mat="cloth_black", detail=True):
    """Jirón triangular a-b-c con espesor th a lo largo de n."""
    N = Vector(n).normalized() * (th / 2)
    mk.hull(part, [tuple(Vector(p) + k * N) for p in (a, b, c) for k in (-1, 1)], mat, detail=detail)


def hem(mk, part, secs, y, a0, a1, n, off, ln, seed=0, warp=None, mats=("cloth_black",)):
    """Ruedo deshilachado: n jirones que cuelgan desde y entre los ángulos a0 y a1 (la punta, a ln)."""
    step = (a1 - a0) / n
    for i in range(n):
        aa, ab = a0 + step * i, a0 + step * (i + 1)
        ta = aa + step * (0.3 + 0.4 * rnd(seed + i))
        L = ln * (0.55 + 0.45 * rnd(seed + i + 11))
        top = interp(secs, y + 0.03 + 0.007 * (i % 2))                   # vecinos a distinta altura: no coplanares
        pts = [sp(top, aa - step * 0.06, off), sp(top, ab + step * 0.06, off), sp(interp(secs, y - L), ta, off)]
        if warp:
            pts = [warp(p) for p in pts]
        r = math.radians(ta)
        flap(mk, part, *pts, n=(math.cos(r), 0, math.sin(r)), mat=mats[i % len(mats)])


# ======================================================================================
T_SECS = [(4.36, 0.0, 0.02, 1.40, 0.90), (4.85, 0.0, 0.0, 1.62, 1.00), (5.30, 0.0, -0.02, 1.86, 1.12),
          (5.74, 0.0, 0.03, 2.00, 1.12)]


def tw(p):
    """Hombro derecho 0,1 más bajo (Bloque H; carga la cruz): se aplica a todo lo del UpperTorso."""
    x, y, z = p
    k = min(max(x / 1.0, 0.0), 1.0) * min(max((y - 5.3) / 0.7, 0.0), 1.0)
    return (x, y - 0.10 * k, z)


def torso_top(g=0.0):
    """Hombros que caen hacia el cuello, cuello de la levita y espalda alta redondeada."""
    pts = []
    for s in (-1, 1):
        pts += [(s * (0.98 + g), 5.98 + g, -0.28 - g), (s * (0.98 + g), 5.98 + g, 0.30 + g),
                (s * 0.52, 6.16 + g, -0.26 - g), (s * 0.52, 6.20 + g, 0.34 + g), (s * 0.44, 5.62, 0.66 + g)]
    return pts + [(0.0, 6.22 + g, -0.24 - g), (0.0, 6.26 + g, 0.34 + g), (0.0, 5.74, 0.72 + g)]


def upper_torso(mk):
    ut = mk.part("UpperTorso", (0, WAIST, 0))
    core = [p for s in T_SECS for p in round_ring(s[0], 0, s[2], s[3], s[4], n=14)] + torso_top()
    mk.hull(ut, [tw(p) for p in core], "silver_neon")
    # levita: espalda y hombros enteros hasta 4,62, 0,09 afuera del núcleo, ruedo deshilachado
    back = []
    for y in (4.62, 4.85, 5.30, 5.74):
        S = interp(T_SECS, y)
        back += [sp(S, a, 0.09) for a in range(-20, 201, 20)] + [sp(S, a, -0.15) for a in (-20, 200)]
    mk.hull(ut, [tw(p) for p in back + torso_top(0.09)], "cloth_black")
    hem(mk, ut, T_SECS, 4.62, -20, 200, 10, 0.075, 0.15, seed=3, warp=tw)
    # adelante, la levita abierta y rota: de cada hombro cuelgan dos tiras hasta el borde del pecho
    # (el pecho descubierto queda entre 232° y 308°)
    for s, strips in ((-1, ((190, 211, 4.60), (214, 232, 4.76))), (1, ((308, 326, 4.70), (329, 350, 4.60)))):
        for k, (fa0, fa1, yb) in enumerate(strips):
            pts = []
            for y in (yb, 4.85, 5.30, 5.74):
                S = interp(T_SECS, max(y, yb))
                pts += [sp(S, a, 0.075) for a in (fa0, (fa0 + fa1) / 2, fa1)] + [sp(S, a, -0.15) for a in (fa0, fa1)]
            pts += [(s * 1.03, 6.03, -0.33)] if (fa0 + fa1) / 2 in (200.5, 339.5) else [(s * 0.60, 6.20, -0.31)]
            mk.hull(ut, [tw(p) for p in pts], "cloth_black")
            hem(mk, ut, T_SECS, yb, fa0, fa1, 2, 0.06, 0.14, seed=40 + 5 * s + k, warp=tw)
        ea, sgn = (strips[1][1], 1) if s < 0 else (strips[0][0], -1)    # borde rasgado hacia el pecho
        for k, y in enumerate((4.98, 5.30, 5.62)):
            pts3 = [sp(interp(T_SECS, y + 0.17), ea - sgn * 3, 0.068), sp(interp(T_SECS, y - 0.10), ea - sgn * 3, 0.068),
                    sp(interp(T_SECS, y + 0.02 * k), ea + sgn * (6 + 3 * (k % 2)), 0.068)]
            r = math.radians(ea)
            flap(mk, ut, *[tw(p) for p in pts3], n=(math.cos(r), 0, math.sin(r)))
    # placas de cristal: el pecho descubierto y una faja baja que asoma debajo de la levita
    def front_plate(y0, y1, a0, a1, k, peak=None):
        plate(mk, ut, T_SECS, y0, y1, a0, a1, peak=peak or (0.08 + 0.05 * rnd(k)), inner=-0.07,
              shift=0.35 * (rnd(k + 3) - 0.5), tilt=0.12 * (rnd(k + 5) - 0.5), warp=tw, detail=True)
    for k, (y0, y1, a0, a1) in enumerate(((4.40, 4.84, 234.0, 256.5), (4.40, 4.865, 258.5, 283.0),
                                          (4.40, 4.86, 285.0, 306.0), (5.76, 5.99, 234.0, 266.0),
                                          (5.79, 5.99, 268.0, 306.0))):
        front_plate(y0, y1, a0, a1, 10 + k)
    # costados del hueco, debajo de las costillas: placas bajas, así el neón no rodea al corazón
    for a0, a1, cuts in ((233.5, 242.0, ((4.89, 5.27), (5.31, 5.74))), (298.0, 306.5, ((4.89, 5.36), (5.40, 5.74)))):
        for k, (y0, y1) in enumerate(cuts):
            front_plate(y0, y1, a0, a1, 20 + k + int(a0), peak=0.045 + 0.01 * k)
    for j in range(9):                                                    # faja baja: atrás y a los costados
        a0 = 308 + 31.8 * j
        plate(mk, ut, T_SECS, 4.38, 4.80, a0 + 1.5, a0 + 31.8 - 1.5, peak=0.035, edge=0.015, inner=-0.07,
              shift=0.3 * (rnd(90 + j) - 0.5), warp=tw, detail=True)
    # pecho abierto: hueco tallado, paredes de carne oscura; el corazón va en su propia pieza
    cav = []
    for z, kx, ky in ((-1.15, 0.44, 0.46), (-0.10, 0.37, 0.39)):          # 0,04 de aire alrededor del corazón
        cav += [(kx * math.cos(2 * math.pi * (i + 0.5) / 10), 5.31 + ky * math.sin(2 * math.pi * (i + 0.5) / 10), z)
                for i in range(10)]
    mk.carve(ut, "skin_dead_dark", points=cav)
    # costillas de cristal: salen de la pared del hueco, pasan por encima del borde y bajan en diagonal
    # sobre el pecho hasta meterse bajo la levita (abiertas, como una caja torácica reventada)
    for s in (-1, 1):
        for k, y in enumerate((5.06, 5.34, 5.62)):
            a = Vector((s * 0.44, y, -0.22))                               # adentro de la pared (0,36-0,39):
            b = Vector((s * 0.45, y, -0.66))                               # a 0,36 la cara quedaba coplanar con ella
            c = Vector((s * (0.68 + 0.02 * (k % 2)), y - 0.17 - 0.02 * k, -0.45))
            for p0, p1, w0, w1 in ((a, b, 0.10, 0.10), (b + (a - b) * 0.15, c, 0.10, 0.06)):
                D = (p1 - p0).normalized()
                v = Vector((0, 1, 0)) - D * D.y                            # alto de la costilla: vertical
                v.normalize()
                u = D.cross(v)                                            # espesor: hacia afuera del pecho
                pts = [tuple(p0 + v * (w0 / 2) * i + u * (0.045 * j)) for i in (-1, 1) for j in (-1, 1)]
                pts += [tuple(p1 + v * (w1 / 2) * i + u * (0.035 * j)) for i in (-1, 1) for j in (-1, 1)]
                mk.hull(ut, [tw(p) for p in pts], "silver_crust", detail=True)
    # cuello de costra, 20° hacia adelante
    mk.cyl(ut, (0, 6.27, -0.16), 0.25, 0.64, "silver_crust", rot=(-20, 0, 0), sides=10)
    # racimos de cristal que revientan la levita: trapecios y omóplatos
    for s in (-1, 1):
        b = tw((s * 0.70, 6.10, 0.06))
        for d, ln in (((s * 0.25, 1.0, 0.35), 0.58), ((s * 0.50, 0.8, 0.55), 0.44), ((s * 0.08, 0.7, 0.85), 0.34)):
            shard(mk, ut, b, d, ln, 0.18, sink=0.14, detail=True)
        b = tw((s * 0.64, 5.42, 0.47))
        for d, ln in (((s * 0.45, 0.5, 1.0), 0.44), ((s * 0.15, 0.9, 0.8), 0.32)):
            shard(mk, ut, b, d, ln, 0.16, sink=0.14, detail=True)
    return ut


def heart(mk):
    c = Vector((0.0, 5.30, -0.39))
    sh = mk.part("Silver_Heart", tuple(c))
    # icosaedro: en x llega a 0,894 r y en y a 0,85 r; la escala lo deja en 0,70 × 0,70 (prompt), 0,60 de fondo,
    # con la punta de atrás 0,008 metida en la pared del hueco (toca, no flota)
    mk.ball(sh, tuple(c), 0.35, "silver_neon", scale=(1.12, 1.18, 0.85), subdiv=1)
    for d, ln in (((0.4, 1.0, -0.3), 0.20), ((-0.5, 0.8, -0.4), 0.18), ((0.6, -0.5, -0.6), 0.17),
                  ((-0.3, -0.9, -0.5), 0.16), ((0.05, 0.2, -1.0), 0.17)):
        D = Vector(d).normalized()
        shard(mk, sh, tuple(c + D * 0.24), tuple(D), ln, 0.11, mat="silver_neon", sink=0.06)


L_SECS = [(HIP - 0.06, 0.0, 0.0, 1.30, 0.86), (WAIST + 0.06, 0.0, 0.02, 1.40, 0.90)]


def lower_torso(mk):
    lt = mk.part("LowerTorso", (0, HIP, 0))
    mk.hull(lt, [p for s in L_SECS for p in round_ring(s[0], 0, s[2], s[3], s[4], n=12)], "silver_neon")
    for j in range(3):                                                    # adelante: placas (pasan las tapas)
        plate(mk, lt, L_SECS, L_SECS[0][0] - 0.015, L_SECS[1][0] + 0.015, 218 + 34.7 * j + 2, 218 + 34.7 * (j + 1) - 2,
              peak=0.08 + 0.04 * rnd(50 + j), shift=0.3 * (rnd(53 + j) - 0.5))
    # falda de la levita: atrás y a los costados, de la cintura (debajo de la tapa del núcleo) a 3,95,
    # jirones hasta ~3,84 (arriba de la cadera)
    pts = []
    for y in (3.95, WAIST + 0.045):
        S = interp(L_SECS, y)
        pts += [sp(S, a, 0.08) for a in range(-36, 217, 21)] + [sp(S, a, -0.12) for a in (-36, 216)]
    mk.hull(lt, pts, "cloth_black")
    hem(mk, lt, L_SECS, 3.95, -36, 216, 9, 0.065, 0.12, seed=60)


def coat_tail(mk, ul, secs, s):
    """Faldón de la levita sobre el muslo (afuera y atrás), cortado en la cadera, ruedo quemado.
    Los dos faldones no se cruzan atrás (en la vuelta 1 se pisaban en x = 0) y el izquierdo termina 0,03 más abajo."""
    x = s * LEG_X
    yb = 3.0 if s > 0 else 2.97
    top, bot = interp(secs, HIP + 0.09), interp(secs, yb)                # 3,99: ni los jirones (3,98) ni el núcleo (4,00)
    angs = [-50 + 26.4 * i for i in range(8)]                             # -50 (afuera adelante) .. 135 (adentro atrás)
    angs = [a if s > 0 else 180 - a for a in angs]
    pts = [sp(top, a, 0.08) for a in angs] + [sp(bot, a, 0.26) for a in angs]
    pts += [sp(top, a, -0.10) for a in (angs[0], angs[-1])] + [(x, yb, 0.0)]
    mk.hull(ul, pts, "cloth_black")
    a0, a1 = (-50, 135) if s > 0 else (45, 230)
    S = [(2.5, bot[1], bot[2], bot[3] + 0.36, bot[4] + 0.36), (3.2, bot[1], bot[2], bot[3] + 0.36, bot[4] + 0.36)]
    hem(mk, ul, S, yb, a0, a1, 6, 0.06, 0.24, seed=70 + s, mats=("cloth_black", "wood_charred"))


def legs(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        x = s * LEG_X
        ul = mk.part(f"{side}UpperLeg", (x, HIP, 0))
        secs = [(KNEE - 0.06, x, 0.0, 0.48, 0.52), (3.20, x, -0.02, 0.60, 0.64), (HIP + 0.10, x, 0.0, 0.66, 0.70)]
        crystal_limb(mk, ul, secs, 2, 6, 5 + (s > 0), a0=-30, mirror=s < 0, peak=(0.07, 0.12),
                     skip=lambda a, i: i == 1 and (a >= 320 or a <= 150), low=lambda a, i: abs(a - 180) < 35)
        coat_tail(mk, ul, secs, s)
        shard(mk, ul, (x, 2.30, -0.22), (0, -0.35, -1.0), 0.30, 0.20, sink=0.12, detail=True)     # rodilla
        ll = mk.part(f"{side}LowerLeg", (x, KNEE, 0))
        secs = [(ANKLE + 0.06, x, 0.02, 0.34, 0.38), (1.55, x, 0.02, 0.48, 0.52), (KNEE + 0.08, x, 0.0, 0.44, 0.48)]
        crystal_limb(mk, ll, secs, 2, 5, 7 + (s > 0), a0=-18, mirror=s < 0, peak=(0.06, 0.11))
        ft = mk.part(f"{side}Foot", (x, ANKLE, 0))
        mk.hull(ft, [(x + d, y, z) for d in (-0.22, 0.22) for y, z in ((0.0, 0.30), (0.50, 0.20), (0.50, -0.14),
                                                                     (0.0, -0.62), (0.22, -0.56))]
                + [(x, 0.30, -0.66), (x, 0.56, 0.0)], "silver_crust")
        for k, dx in enumerate((-0.14, 0.0, 0.14)):                      # garras de cristal
            shard(mk, ft, (x + dx, 0.11, -0.50), (dx * 0.5, -0.10, -1.0), 0.42 - 0.08 * abs(k - 1), 0.16, sink=0.12)


def flesh_hand(mk, hd):
    """La mano izquierda es lo último de carne: la del humano, más grande, con la plata trepando al dorso."""
    s, hx, W = -1, -(WR_X + 0.02), WRIST
    mk.hull(hd, round_ring(W + 0.06, hx, ARM_Z, 0.24, 0.38) + round_ring(W - 0.22, hx + s * 0.012, ARM_Z, 0.27, 0.43)
            + round_ring(W - 0.40, hx + s * 0.018, ARM_Z, 0.24, 0.41), "skin_dead")
    for dz, ln in ((-0.10, 0.54), (0.10, 0.46)):                         # dos bloques de dedos largos
        mk.hull(hd, [(hx + s * 0.018 + dx, y, ARM_Z + dz + d) for dx in (-0.08, 0.08)
                     for y, w in ((W - 0.34, 0.09), (W - 0.34 - ln, 0.065)) for d in (-w, w)], "skin_dead")
    mk.box(hd, (hx - s * 0.10, W - 0.24, ARM_Z - 0.21), (0.10, 0.27, 0.10), "skin_dead", rot=(-15, 0, 0))   # pulgar
    for k, ((y0, dz0), (y1, dz1), w0, w1) in enumerate((((W + 0.03, 0.02), (W - 0.24, -0.03), 0.06, 0.045),
                                                         ((W - 0.12, -0.01), (W - 0.36, 0.09), 0.045, 0.03))):
        pts = []
        for y, dz, w in ((y0 - 0.004 * k, dz0, w0), (y1, dz1, w1)):
            half = 0.128 if y > W - 0.22 else 0.132
            for off in (0.016 + 0.004 * k, -0.03):
                pts += [(hx + s * (half + off), y, ARM_Z + dz + sw * w / 2) for sw in (-1, 1)]
        mk.hull(hd, pts, "silver_neon", detail=True)                    # vetas que bajan por el dorso
    for dz, ln in ((-0.09, 0.20), (0.08, 0.15)):
        shard(mk, hd, (hx + s * 0.08, W + 0.03, ARM_Z + dz), (s * 0.35, -1.0, 0.0), ln, 0.10, sink=0.08, detail=True)


def claw_hand(mk, hd):
    """Mano derecha de cristal: palma que cierra la barra de la cruz, pulgar y tres garras de 0,8."""
    hx, W = WR_X + 0.02, WRIST
    def jring(y, cx, w, d, rot):                                          # pentágonos girados: facetas de cristal
        return [(cx + w / 2 * math.cos(math.radians(rot + 72 * i)), y, ARM_Z + d / 2 * math.sin(math.radians(rot + 72 * i)))
                for i in range(5)]
    mk.hull(hd, jring(W + 0.06, hx, 0.30, 0.38, 10) + jring(W - 0.20, hx + 0.01, 0.38, 0.50, 46)
            + jring(W - 0.40, hx + 0.015, 0.30, 0.42, 82), "silver_crust")
    shard(mk, hd, (hx - 0.13, W - 0.10, ARM_Z - 0.10), (0.15, -0.55, -0.6), 0.32, 0.14, sink=0.10)    # pulgar
    for dz, ln in ((-0.10, 0.20), (0.06, 0.16)):                         # nudillos de cristal
        shard(mk, hd, (hx + 0.12, W - 0.30, ARM_Z + dz), (1.0, 0.25, 0.1), ln, 0.12, sink=0.10)
    for k, dx in enumerate((-0.12, 0.0, 0.12)):
        p0 = Vector((hx + dx, W - 0.34, ARM_Z - 0.12))
        p1 = Vector((hx + dx * 1.25, W - 0.78, ARM_Z - 0.25 + 0.02 * k))
        p2 = Vector((hx + dx * 1.4, W - 1.13 + 0.04 * abs(k - 1), ARM_Z - 0.50))
        for a, b, w0, w1 in ((p0, p1, 0.17, 0.13), (p0 + (p1 - p0) * 0.85, p2, 0.13 * 0.8, 0.0)):
            D, u, v = frame(b - a)
            pts = [tuple(a + u * (w0 / 2) * i) for i in (-1, 1)] + [tuple(a + v * (w0 / 2) * i) for i in (-1, 1)]
            pts += ([tuple(b + u * (w1 / 2) * i) for i in (-1, 1)] + [tuple(b + v * (w1 / 2) * i) for i in (-1, 1)]
                    if w1 else [tuple(b)])
            mk.hull(hd, pts, "silver_crust")


def arms(mk):
    for side, s in (("Left", -1), ("Right", 1)):
        ua = mk.part(f"{side}UpperArm", (s * SH_X, SHOULDER, ARM_Z))
        secs = [(ELBOW - 0.07, s * arm_x(ELBOW - 0.07), ARM_Z, 0.42, 0.44), (5.50, s * arm_x(5.50), ARM_Z, 0.52, 0.54),
                (SHOULDER + 0.11, s * arm_x(SHOULDER + 0.11), ARM_Z, 0.48, 0.52)]
        crystal_limb(mk, ua, secs, 2, 5, 1 + (s > 0), a0=-36, mirror=s < 0, peak=(0.06, 0.10),
                     low=lambda a, i: abs(a - 180) < 40)
        la = mk.part(f"{side}LowerArm", (s * EL_X, ELBOW, ARM_Z))
        secs = [(WRIST - 0.05, s * arm_x(WRIST - 0.05), ARM_Z, 0.34, 0.36),
                (ELBOW + 0.08, s * arm_x(ELBOW + 0.08), ARM_Z, 0.44, 0.46)]
        crystal_limb(mk, la, secs, 2, 5, 3 + (s > 0), mirror=s < 0, peak=(0.06, 0.11))
        hd = mk.part(f"{side}Hand", (s * WR_X, WRIST, ARM_Z))
        if s > 0:
            for y, ln in ((3.35, 0.44), (3.72, 0.38), (4.05, 0.30)):   # hojas de cristal en el antebrazo derecho
                shard(mk, la, (arm_x(y) + 0.13, y, ARM_Z + 0.09), (0.55, 0.45, 0.70), ln, 0.15, sink=0.12, detail=True)
            claw_hand(mk, hd)
        else:
            flesh_hand(mk, hd)


# ---- cabeza -------------------------------------------------------------------------------
CR = ((4.26, -0.18, 0.62, 0.60), (4.52, -0.21, 0.72, 0.80), (4.80, -0.25, 0.92, 0.90), (5.02, -0.26, 0.86, 0.86),
      (5.16, -0.26, 0.58, 0.62))
CR_SECS = [(y, 0.0, cz, w, d) for y, cz, w, d in CR]


def face_z(x, y, off=0.0):
    """z del frente del cráneo (espacio del caminante) en (x, y), off hacia adelante."""
    _, _, cz, w, d = interp(CR_SECS, y)
    return cz - (d / 2) * math.sqrt(max(0.0, 1 - (x / (w / 2)) ** 2)) - off


def head_and_halo(mk):
    hd = mk.part("Head", NECK_P)
    # la cara del Predicador humano: cráneo largo, mandíbula fina, pómulos, cejas, nariz fina, orejas
    mk.hull(hd, head([p for y, cz, w, d in CR for p in round_ring(y, 0, cz, w, d)]), "skin_dead")
    mk.hull(hd, head([(-0.22, 4.40, -0.58), (0.22, 4.40, -0.58), (-0.26, 4.44, -0.16), (0.26, 4.44, -0.16),
                      (-0.14, 4.10, -0.64), (0.14, 4.10, -0.64), (-0.18, 4.14, -0.16), (0.18, 4.14, -0.16),
                      (0, 4.04, -0.68)]), "skin_dead")
    for s in (-1, 1):
        mk.hull(hd, head([(s * 0.26, 4.66, -0.62), (s * 0.44, 4.68, -0.50), (s * 0.34, 4.58, -0.56),
                          (s * 0.30, 4.66, -0.44), (s * 0.44, 4.62, -0.36)]), "skin_dead")
        mk.hull(hd, head([(s * 0.03, 4.86, -0.70), (s * 0.44, 4.90, -0.58), (s * 0.03, 4.94, -0.66),
                          (s * 0.44, 4.96, -0.54), (s * 0.03, 4.88, -0.45), (s * 0.42, 4.93, -0.40)]), "skin_dead")
        mk.hull(hd, head(mk.pts_box((s * 0.46, 4.70, -0.22), (0.08, 0.24, 0.15), top=(1, 0.7))), "skin_dead")
    mk.hull(hd, head([(0, 4.84, -0.66), (0, 4.62, -0.86), (-0.07, 4.58, -0.60), (0.07, 4.58, -0.60),
                      (0, 4.57, -0.70)]), "skin_dead")
    # media máscara de plata sobre la mitad derecha (frente, ojo, pómulo, nariz), borde quebrado
    up = [(-0.06, y, face_z(-0.06, y, 0.05)) for y in (4.86, 5.00, 5.10)]
    up += [(x, y, face_z(x, y, 0.05)) for x in (0.20, 0.36) for y in (5.00, 5.10)]
    up += [(0.20, 4.93, -0.68), (0.44, 4.95, -0.60), (0.48, 4.86, face_z(0.48, 4.86, 0.05)),
           (0.50, 4.76, -0.30), (0.46, 4.76, -0.58), (-0.04, 4.84, -0.30), (0.30, 4.90, -0.20)]
    lo = [(0.03, 4.88, -0.72), (0.03, 4.64, -0.90), (0.03, 4.54, -0.76), (0.11, 4.56, -0.68),
          (0.30, 4.62, -0.67), (0.48, 4.67, -0.55), (0.49, 4.56, -0.40), (0.40, 4.50, -0.61),
          (0.24, 4.49, -0.67), (0.44, 4.80, -0.62), (0.22, 4.86, -0.72), (0.50, 4.80, -0.32),
          (0.05, 4.70, -0.35), (0.35, 4.60, -0.25)]
    jaw = [(0.03, 4.51, -0.71), (0.26, 4.49, -0.65), (0.31, 4.45, -0.30), (0.03, 4.03, -0.72), (0.17, 4.08, -0.68),
           (0.22, 4.15, -0.30), (0.03, 4.45, -0.35), (0.05, 4.10, -0.42), (0.25, 4.30, -0.62)]
    mk.hull(hd, head(up), "silver_crust")
    mk.hull(hd, head(lo), "silver_crust")
    mk.hull(hd, head(jaw), "silver_crust")                               # la máscara baja hasta el mentón
    # cuencas hondas (la derecha atraviesa la máscara), boca de labios finos con la comisura derecha rota
    sockets = []
    for s in (-1, 1):
        c = (s * 0.19, 4.76, -0.76)
        sockets.append(c)
        mk.carve(hd, "skin_dead_dark", points=head(mk.pts_ball(c, 0.17, scale=(1.0, 0.75, 1.0), subdiv=0)))
    mouth = [(-0.13, 4.36), (0.15, 4.37), (0.20, 4.33), (0.14, 4.30), (-0.13, 4.31)]
    mk.carve(hd, "blood_dry", points=head([(x, y, z) for x, y in mouth for z in (-0.90, -0.52)]))
    for i in range(5):
        x = -0.10 + 0.05 * i
        mk.hull(hd, head([(x - 0.022, 4.37, -0.62), (x + 0.022, 4.37, -0.62), (x - 0.015, 4.33, -0.62),
                          (x + 0.015, 4.33, -0.62), (x - 0.02, 4.37, -0.50), (x + 0.02, 4.37, -0.50),
                          (x, 4.335, -0.50)]), "bone", detail=True)
    # grietas de la máscara, talladas: el neón asoma por adentro
    cracks = ([(0.24, 4.69), (0.31, 4.61), (0.27, 4.555), (0.33, 4.48), (0.25, 4.41)],
              [(0.30, 4.62), (0.38, 4.65), (0.44, 4.60)],
              [(0.07, 4.82), (0.13, 4.73), (0.09, 4.62)])
    for cr in cracks:
        for (x0, y0), (x1, y1) in zip(cr, cr[1:]):
            dx, dy = x1 - x0, y1 - y0
            n = math.hypot(dx, dy)
            px, py = -dy / n * 0.016, dx / n * 0.016
            pts = []
            for x, y in ((x0 - dx / n * 0.01, y0 - dy / n * 0.01), (x1 + dx / n * 0.01, y1 + dy / n * 0.01)):
                zf = min(face_z(min(abs(x), 0.44), y, 0.0), -0.55)
                for sx in (-1, 1):
                    pts += [(x + sx * px, y + sx * py, zf - 0.30), (x + sx * px, y + sx * py, zf + 0.03)]
            mk.carve(hd, "silver_neon", points=head(pts))
    # costra: todo lo de arriba de un plano inclinado (la carne queda en la cara de abajo y la mejilla
    # izquierda), la nuca y el costado derecho detrás de la máscara
    pc = hp((0, 4.80, -0.26))                                             # el ojo izquierdo queda adentro de la costra
    n = hnormal((-0.6, 1.0, 0.0))
    mk.slice(hd, pc, n)
    mk.paint(hd, "silver_crust", ball=(tuple(Vector(pc) + Vector(n) * 30.0), 30.0))
    mk.paint(hd, "silver_crust", box=((0.0, 7.1, 0.06), (2.0, 1.8, 0.70)))                     # nuca
    mk.paint(hd, "silver_crust", box=((0.51, 6.9, -0.50), (0.62, 1.5, 0.60)))                  # costado derecho
    for c in sockets:                                                     # las paredes de las cuencas, oscuras
        mk.paint(hd, "skin_dead_dark", ball=(hp(c), 0.17 * K * 0.999))
    # placas de cristal en la coronilla y la frente izquierda
    for k, (y0, y1, a0, a1) in enumerate(((4.90, 5.06, 200, 236), (4.70, 4.95, 160, 196), (5.05, 5.17, 128, 176),
                                          (5.05, 5.17, 180, 228), (5.05, 5.17, -24, 24), (4.92, 5.08, 100, 140))):
        plate(mk, hd, CR_SECS, y0, y1, a0, a1, peak=0.05 + 0.025 * rnd(80 + k), edge=0.02, inner=-0.04,
              shift=0.3 * (rnd(83 + k) - 0.5), warp=lambda p: hp(p), detail=True)
    mk.hull(hd, head(round_ring(5.10, 0, -0.26, 0.56, 0.60, n=6) + round_ring(5.18, 0, -0.26, 0.50, 0.54, n=6)
                     + [(0.05, 5.27, -0.30)]), "silver_crust", detail=True)
    # aureola: 7 púas de cristal que salen de atrás de la cabeza
    C = Vector((0.0, 4.80, 0.10))
    for th, L in zip((-72, -48, -24, 0, 24, 48, 72), (0.74, 0.86, 0.96, 1.0, 0.96, 0.86, 0.74)):
        r = math.radians(th)
        d = Vector((math.sin(r), math.cos(r), 0.30)).normalized()
        b = C + d * 0.20
        bw, tw_ = Vector(hp(tuple(b))), Vector(hp(tuple(b + d * (L / K))))
        shard(mk, hd, tuple(bw), tuple(tw_ - bw), (tw_ - bw).length, 0.18, sink=0.20, th=0.10, detail=True)
    # la costra baja por la mejilla izquierda
    for p, d, ln, w in (((-0.37, 4.61, -0.47), (-0.4, -1.0, -0.3), 0.26, 0.12),
                        ((-0.24, 4.64, -0.60), (-0.3, -1.0, -0.5), 0.20, 0.10)):
        shard(mk, hd, hp(p), hvec(d), ln, w, sink=0.08, detail=True)

    eyes = mk.part("Eyes", NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.76, -0.66)), 0.11, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=1)


# ---- la cruz de hierro (fase 3) ---------------------------------------------------------------
def iron_cross(mk):
    yaw = math.radians(12)
    G = Vector((WR_X + 0.02, WRIST - 0.30, ARM_Z))                      # el puño derecho cierra acá la barra
    SG, LEN, SC, ARM = 0.62, 4.5, 3.30, 1.20                              # agarre, largo, travesaño, brazo
    FL, FW, FT, B = 0.38, 0.64, 0.44, 0.175                               # punta ensanchada, media barra
    sy, cy = math.sin(yaw), math.cos(yaw)
    u = Vector((cy, 0.0, -sy))                                            # el travesaño, horizontal

    def axes(g):
        d = Vector((sy * math.cos(g), -math.sin(g), cy * math.cos(g)))   # del pie a la punta: abajo y atrás
        return d, d.cross(u)

    lo, hi = math.radians(20), math.radians(70)
    for _ in range(60):                                                   # la punta de arriba apoya en el piso
        g = (lo + hi) / 2
        d, n = axes(g)
        ymin = min((G + (LEN - SG) * d + a * u + b * n).y for a in (-FW / 2, FW / 2) for b in (-FT / 2, FT / 2))
        lo, hi = (g, hi) if ymin > 0.004 else (lo, g)
    d, n = axes(g)

    def P(s, a=0.0, b=0.0):
        return G + (s - SG) * d + a * u + b * n

    cr = mk.part("Acc_IronCross", tuple(G))
    mk.hull(cr, [tuple(P(s, a, b)) for s in (0.30, LEN - 0.30) for a in (-B, B) for b in (-B, B)], "iron")
    mk.hull(cr, [tuple(P(SC + e, a, b)) for e in (-0.172, 0.172) for a in (-ARM + 0.30, ARM - 0.30)
                 for b in (-0.172, 0.172)], "iron")
    for s_in, s_out in ((FL, 0.0), (LEN - FL, LEN)):                     # pie y punta ensanchados
        mk.hull(cr, [tuple(P(s_in, a, b)) for a in (-0.18, 0.18) for b in (-0.18, 0.18)]
                + [tuple(P(s_out, a, b)) for a in (-FW / 2, FW / 2) for b in (-FT / 2, FT / 2)], "iron")
    for a_in, a_out in ((-(ARM - FL), -ARM), (ARM - FL, ARM)):           # brazos ensanchados
        mk.hull(cr, [tuple(P(SC + e, a_in, b)) for e in (-0.18, 0.18) for b in (-0.18, 0.18)]
                + [tuple(P(SC + e, a_out, b)) for e in (-FW / 2, FW / 2) for b in (-FT / 2, FT / 2)], "iron")
    mk.hull(cr, [tuple(P(SC + e, a, b)) for e, a in ((0.34, 0), (-0.34, 0), (0, 0.34), (0, -0.34))
                 for b in (-0.22, 0.22)], "iron")                         # rombo del cruce
    mk.bevel(cr, width=0.025, angle=35)
    mk.carve(cr, "iron", points=mk.pts_box(tuple(P(SC) + Vector((0, 60, 0))), (0.1, 0.1, 0.1)))   # une los cascos
    # óxido: bandas en las barras y las cuatro puntas
    for s0, s1 in ((1.05, 1.24), (1.92, 2.16), (3.78, 3.96)):
        mk.slice(cr, tuple(P(s0)), tuple(d))
        mk.slice(cr, tuple(P(s1)), tuple(d))
        mk.paint(cr, "rust", ball=(tuple(P((s0 + s1) / 2)), 0.27))
    for a0, a1 in ((-0.66, -0.50), (0.30, 0.44)):
        mk.slice(cr, tuple(P(SC, a0)), tuple(u))
        mk.slice(cr, tuple(P(SC, a1)), tuple(u))
        mk.paint(cr, "rust", ball=(tuple(P(SC, (a0 + a1) / 2)), 0.26))
    for c in (P(0.10), P(LEN - 0.10), P(SC, -ARM + 0.10), P(SC, ARM - 0.10)):
        mk.paint(cr, "rust", ball=(tuple(c), 0.33))
    # costra de plata que sube desde el pie: un racimo en la punta y cristales que trepan por la barra
    for k, (s, ang, ln, ax) in enumerate(((0.06, 30, 0.32, -0.5), (0.10, 150, 0.28, -0.4), (0.04, 265, 0.30, -0.6),
                                          (0.20, 330, 0.22, 0.3), (0.95, 200, 0.30, 0.55), (1.05, 320, 0.26, 0.55),
                                          (1.22, 90, 0.20, 0.55), (1.38, 230, 0.16, 0.55), (1.52, 20, 0.12, 0.55))):
        r = math.radians(ang)
        radial = u * math.cos(r) + n * math.sin(r)
        shard(mk, cr, tuple(P(s) + radial * 0.13), tuple(radial + d * ax), ln, 0.15 - 0.008 * k, sink=0.10, detail=True)
    for (s0, a0), (s1, a1) in (((0.86, 0.02), (1.30, -0.05)), ((1.28, -0.05), (1.70, 0.03))):   # veta de neón
        mk.hull(cr, [tuple(P(s, B + off, a + e)) for s, a in ((s0, a0), (s1, a1)) for off in (0.018, -0.03)
                     for e in (-0.03, 0.03)], "silver_neon", detail=True)
    mk.marker("_Grip", tuple(G))
    mk.marker("_Grip2", tuple(P(SG + 0.95)))
    mk.marker("_Tip", tuple(P(LEN)))


def build(mk):
    upper_torso(mk)
    heart(mk)
    lower_torso(mk)
    legs(mk)
    arms(mk)
    head_and_halo(mk)
    iron_cross(mk)

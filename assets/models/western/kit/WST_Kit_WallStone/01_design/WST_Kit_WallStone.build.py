"""
Receta de WST_Kit_WallStone, la pared de piedra de la cárcel (prompt 017, Bloques A + C).

Brief
- Silueta a 40 studs: paño macizo de piedras irregulares grises (alguna ocre) con juntas claras de
  mortero hundidas; la variante con rejas tiene una ventanita alta con tres barrotes.
- Medidas: 8 x 10 x 1,0 (z de -0,5 a 0,5), origen abajo al centro, frente a -Z. Las dos variantes en fila
  sobre X cada 8 (Wall_Stone en x = 0, Wall_Stone_Barred en x = 8): calzan una al lado de la otra.
- Hiladas fijas de 0,75 a 1,05 con juntas en y = 6,5 y 8,0, así la ventana de la variante (2 x 1,5, abajo
  en 6,5) cae entre hiladas, con antepecho abajo y dintel largo arriba.
- Cada piedra es un casco de 8 puntos que atraviesa el muro (se ve de los dos lados: adentro de la celda
  también): atrás ocupa su lugar entero en el aparejo y adelante se achica 0,05 por lado, así entre dos
  piedras queda un surco en V real de 0,1 de boca (atrás se meten 0,01 una en otra: se tocan sin caras
  coplanares; sin mortero aparte). Sus esquinas se corren 0 a 0,06 en z: caras facetadas.
- 8 fragmentos grandes (lo que rompe el Sheriff): 4 filas de hiladas (0-2,9, 2,9-5,6, 5,6-8,0, 8,0-10) x 2,
  cortados por juntas en escalera (cada hilada corta en una junta propia cerca del corte de su fila).
- Wall_Stone_Barred: el mismo aparejo con el hueco de 2 x 1,5 (x de -1 a 1, y de 6,5 a 8,0) y tres barrotes
  de hierro (x = -0,55, 0, 0,55) metidos en el antepecho y tocando el dintel; cada barrote va con el
  fragmento de su lado.
- Nombres: <Variante>_fragNN.
- Inferido: juntas en V sin mortero de otro color, proporción de piedras ocre (1 de cada 8), alturas de hiladas y anchos de
  piedras (secuencia fija, no azar), filas de fragmentos.

Vueltas: 1) piedras sobre un núcleo de mortero por hilada: 2400 triángulos por variante (la unión parte
cada cara del núcleo alrededor de cada piedra) y los núcleos de hiladas vecinas, que se tocaban justo,
daban bordes con giro invertido · 2) sin núcleo: piedras de 8 puntos con la cara de adelante achicada, surco
en V entre vecinas (744 / 768); dos piedras quedaban "flotantes" (el borde de atrás facetado no tocaba a la
vecina) -> atrás se meten 0,01 una en otra, sin salirse del módulo · 3) menos piedras ocre (manchones).

Revisión
- Triángulos: 744 (Wall_Stone) + 768 (Wall_Stone_Barred) = 1512 contra 600 para el modelo entero. Calidad
  primero: ~55 piedras de 12 triángulos por variante; es la pared que rompe el Sheriff y se usa solo en la
  cárcel (pocas instancias). Con piedras de 1,6 a 2,6 bajaría a ~500 por variante pero se pierde el aparejo.
- Medidas: cada variante 8,000 x 10,000 x 1,000, apoyada en y = 0; calzan entre sí (las caras de atrás no
  salen del módulo).
- Fragmentos: 8 por variante, de 8,9 a 16,4 % del volumen, trozos de ~4 x 2-2,9 (lo que pide el Sheriff:
  1,5 a 3 por lado en la mayoría; los de las filas bajas llegan a 4,5 de ancho).
- La cara de adentro (celda) muestra las piedras facetadas sin surco (las piedras se tocan atrás).
- Normales del GLB final: 0 esquinas desviadas.
"""

GREY, OCHRE, IRON = "stone_grey", "ochre", "iron"
EDGES = [0.0, 1.0, 1.85, 2.9, 3.7, 4.65, 5.6, 6.5, 7.25, 8.0, 9.0, 10.0]     # juntas entre hiladas
ROWS = [(0, 2), (3, 5), (6, 8), (9, 10)]                                     # hiladas de cada fila de fragmentos
SPLIT = {0: 0.5, 1: 0.1, 2: -0.3, 3: 0.75, 4: 0.35, 5: 1.05, 6: 0.25, 7: 0.0, 8: 0.4, 9: 1.45, 10: -0.6}   # corte por hilada
G = 0.025                                                                     # media junta


class Seq:
    """Secuencia fija (sin azar): mismo aparejo en cada construcción."""
    def __init__(self, seed):
        self.s = seed

    def next(self):
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return self.s / 2147483648


def joints(a, b, seq):
    """Juntas entre a y b con piedras de 1,1 a 2,0 (la última se ajusta)."""
    xs = [a]
    while b - xs[-1] > 2.0:
        w = 1.1 + 0.9 * seq.next()
        if b - (xs[-1] + w) < 0.8:
            w = (b - xs[-1]) / 2
        xs.append(xs[-1] + w)
    xs.append(b)
    return xs


def stone(mk, part, x0, x1, y0, y1, mat, seq, ox):
    """Piedra que atraviesa el muro: atrás del tamaño de su lugar en el aparejo, adelante achicada 0,05 por
    lado: con la vecina forma un surco en V (solo se tocan por el borde de atrás). Esquinas corridas en z
    (0 a 0,06) para que las caras queden facetadas."""
    pts = []
    for sx, x in ((1, x0), (-1, x1)):
        for sy, y in ((1, y0), (-1, y1)):
            pts += [(ox + x + sx * 2 * G, y + sy * 2 * G, -0.5 + 0.06 * seq.next()),
                    (ox + min(4.0, max(-4.0, x - sx * 0.01)), min(10.0, max(0.0, y - sy * 0.01)),
                     0.5 - 0.06 * seq.next())]                    # atrás se mete 0,01 en la vecina (no fuera del módulo)
    mk.hull(part, pts, mat)


def wall(mk, name, ox, opening=None):
    seq = Seq(7)
    parts = {}
    for r, (k0, k1) in enumerate(ROWS):
        for side in (0, 1):
            parts[(r, side)] = mk.part(f"{name}_frag0{2 * r + side + 1}", (ox, 0, 0))
    for k in range(len(EDGES) - 1):
        y0, y1 = EDGES[k], EDGES[k + 1]
        r = next(i for i, (a, b) in enumerate(ROWS) if a <= k <= b)
        sx = SPLIT[k]
        spans = [(-4.0, sx, 0), (sx, 4.0, 1)]
        if opening and opening[2] <= y0 < opening[3]:                         # hiladas del hueco
            spans = [(-4.0, opening[0], 0), (opening[1], 4.0, 1)]
        for a, b, side in spans:
            p = parts[(r, side)]
            xs = joints(a, b, seq)
            if opening and abs(y0 - opening[3]) < 1e-6 and side == 0:        # dintel largo sobre el hueco
                xs = joints(a, opening[0] - 0.3, seq) + [b]
            for x0, x1 in zip(xs, xs[1:]):
                stone(mk, p, x0, x1, y0, y1, OCHRE if seq.next() < 0.12 else GREY, seq, ox)
    if opening:                                                               # barrotes
        for bx in (-0.55, 0.0, 0.55):
            side = 0 if bx <= SPLIT[7] + 1e-6 else 1
            p = parts[(2, side)]
            mk.cyl(p, (ox + bx, (opening[2] - 0.15 + opening[3]) / 2, 0), 0.06, opening[3] - opening[2] + 0.15, IRON,
                   sides=6, detail=True)


def build(mk):
    wall(mk, "Wall_Stone", 0.0)
    wall(mk, "Wall_Stone_Barred", 8.0, opening=(-1.0, 1.0, 6.5, 8.0))

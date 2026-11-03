"""
Receta de WST_Prop_HayBale, los fardos de paja (prompt 135, Bloques A + C). Arden.

Brief
- Silueta a 40 studs: ladrillo amarillo con los cantos blandos, dos hilos oscuros que lo ciñen y
  mechones de paja que asoman en las puntas.
- Medidas: 3 (X) x 1,6 x 1,6; sección de 6 lados (los dos cantos de arriba achaflanados 0,18: se lee
  blando sin chanflanes); hilos de soga de 0,12 a x = ±0,75 (pintados con cortes: en relieve costaban
  28 más cada uno); dos mechones facetados (cuñas romas) por punta.
- Fragmentos (2 por fardo, origen común): las dos mitades, cortadas a lo ancho por la mitad; cada una
  con su hilo y sus mechones.
- Variantes (mismo archivo): HayBale_Burnt (x = 4,5): la mitad de arriba wood_charred (paja, hilo y
  mechones); HayBale_Stack (x = 10): 4 fardos en dos capas cruzadas (abajo a lo largo de X, arriba a lo
  largo de Z), 3,2 de alto: cubre a un jugador agachado. 8 fragmentos (2 por fardo).
- Inferido: dónde se parte (al medio); sección de 6 lados; hilos pintados; la pila en capas cruzadas;
  nombres de las variantes con prefijo.

Vueltas: 1) 144 tris por fardo (sección de 8 lados partida por los cortes del hilo); en el quemado
quedaban triángulos amarillos arriba (la cara de arriba caía justo en el borde de la caja de pintura);
mechones tetraédricos chicos que se leían como puntitos · 2) sección de 6 lados; mechones más grandes:
se leían como púas; la caja arrancaba en 0,75 y pintaba astillas de abajo (dientes negros) · 3) mechones
como cuñas romas, pintura del quemado exacta de 0,8 a 1,7.

Revisión
- 120 triángulos por fardo (60 por mitad) contra 80: el hilo pintado parte las 6 caras largas en tres
  (+24 por mitad) y los dos mechones suman 16. Sin hilo ni mechones no se lee "fardo". La pila: 480.
- Medidas: 3,0 x 1,6 x 1,6 (con mechones 3,34 de largo); la pila 3,2 de alto.
- Con 2 fragmentos por fardo cada mitad es el 50 % (el Bloque C pide <= 45 %): manda el "Frag 2" del
  prompt.
"""

L, S, CH = 3.0, 1.6, 0.18


def bale(mk, names, c, axis="x", burnt=False, origin=None):
    """Fardo en c (base al centro) con su largo en `axis`; dos mitades con los nombres dados."""
    def P(u, y, v):                      # u a lo largo, v a lo ancho (local) -> mundo
        return (c[0] + u, c[1] + y, c[2] + v) if axis == "x" else (c[0] + v, c[1] + y, c[2] + u)

    h = S / 2
    # 6 lados: achaflanado solo arriba (los cantos de abajo apoyan y no se ven; con 8 costaba 16 tris más)
    octo = [(-h, 0), (h, 0), (h, S - CH), (h - CH, S), (-h + CH, S), (-h, S - CH)]
    tufts = {1: ((0.3, 0.5), (-0.3, 1.05)), -1: ((-0.25, 0.55), (0.3, 1.1))}
    for name, side in zip(names, (-1, 1)):
        part = mk.part(name, origin or (c[0], 0, c[2]))         # en la pila, todos con el origen de la pila
        u0, u1 = (-L / 2, 0.0) if side < 0 else (0.0, L / 2)
        mk.hull(part, [P(u, y, v) for u in (u0, u1) for v, y in octo], "hay")
        ue = side * L / 2
        for v, y in tufts[side]:                                       # mechones: cuñas romas en la punta
            # (en las vueltas 1 y 2 eran tetraedros: chicos se leían como puntitos, grandes como púas)
            base = [P(ue - side * 0.03, y + dy, v + dv) for dy, dv in ((-0.14, -0.22), (-0.16, 0.2), (0.14, 0.24), (0.16, -0.18))]
            tip = [P(ue + side * 0.17, y + dy, v + dv) for dy, dv in ((-0.04, -0.12), (0.06, 0.14))]
            mk.hull(part, base + tip, "hay")
        ub = side * 0.75                                               # hilo de soga
        for du in (-0.06, 0.06):
            mk.slice(part, P(ub + du, 0, 0), (1, 0, 0) if axis == "x" else (0, 0, 1))
        size = (0.12, S + 0.2, S + 0.2) if axis == "x" else (S + 0.2, S + 0.2, 0.12)
        mk.paint(part, "rope", box=(P(ub, S / 2, 0), size))
        if burnt:                                                      # mitad de arriba quemada
            mk.slice(part, P(0, S / 2, 0), (0, 1, 0))
            # de 0,8 a 1,7: la cara de arriba quedaba en el borde, y arrancando en 0,75 agarraba astillas de abajo
            mk.paint(part, "wood_charred", box=(P(0, 1.25, 0), (L + 1, 0.9, L + 1)))


def build(mk):
    bale(mk, ("frag01", "frag02"), (0, 0, 0))
    bale(mk, ("HayBale_Burnt_frag01", "HayBale_Burnt_frag02"), (4.5, 0, 0), burnt=True)
    x0 = 10.0
    n = 1
    for c, axis in (((x0, 0, -S / 2), "x"), ((x0, 0, S / 2), "x"),
                    ((x0 - S / 2 + 0.1, S, 0.05), "z"), ((x0 + S / 2 + 0.1, S, 0.05), "z")):
        bale(mk, (f"HayBale_Stack_frag{n:02d}", f"HayBale_Stack_frag{n + 1:02d}"), c, axis, origin=(x0, 0, 0))
        n += 2

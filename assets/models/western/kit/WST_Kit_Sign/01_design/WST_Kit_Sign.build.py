"""
Receta de WST_Kit_Sign, los carteles en blanco del kit modular (prompt 014, Bloques A + C).

Brief
- Silueta a 40 studs: tablero claro con marco oscuro (el texto va como decal en Studio): la banda chata
  de la fachada, el cartel colgado de una ménsula de hierro con cadenas, el cartel en poste y la flecha.
- Técnica: el tablero es un prisma wood_dark y el campo se talla 0,05 con material paint_cream: queda el
  borde de 0,15 en relieve y el campo plano para el decal. Los que se leen de los dos lados (colgado,
  poste, flecha) tienen campo en las dos caras. Cada tablero se parte en 2 por una grieta diagonal en
  zigzag (dos cortadores complementarios, caras de corte wood_light).
- Fila sobre X:
  - Sign_Band (x = 0): 6 x 1,6 x 0,2, mira a -Z. Origen abajo al centro de la cara de atrás (z = 0): se
    apoya plano en la falsa fachada.
  - Sign_Hanging (x = 6): fixed_Bracket de hierro en L (placa contra la pared, brazo de 3,5 hacia -Z y
    tornapunta), origen en la pared a la altura del brazo (y = 2 en la fila). Tablero de 3 x 1,2 x 0,15
    perpendicular a la pared (se lee desde la calle por los dos lados), colgado de dos cadenas de dos
    eslabones (cada cadena va con su mitad del tablero). Origen del tablero = pivote arriba al centro.
  - Sign_Post (x = 11): fixed_Post de 0,3 x 4 y tablero de 2,5 x 1 x 0,15 arriba (y 3-4) delante del poste.
  - Sign_Arrow (x = 16): fixed_Post igual y flecha de 3 x 0,8 x 0,15 con punta a +X y cola en V.
  Poste y tablero comparten el origen abajo al centro del poste.
- Nombres: <Pieza>_fragNN, <Pieza>_fixed_Bracket / _fixed_Post.
- Inferido: espesores (los del prompt: 0,2 y 0,15; quedan por debajo del mínimo de 0,4 del Bloque C para
  fragmentos, se respetó el prompt), ménsula y cadenas, alto del cartel en el poste (la tabla al tope del
  poste de 4), dirección de la flecha, desgaste (una esquina comida por tablero).

Vueltas: 1) al releer: las esquinas comidas estaban del lado del fragmento equivocado (el tallado no
hacía nada) · construida a la primera; capturas sin cambios.

Revisión
- Triángulos contra 150 por pieza: Band 76, Hanging 210 (ménsula 54 + tablero con cadenas 156), Post 148
  (poste 40 + tablero 108), Arrow 196 (poste 40 + flecha 156). Calidad primero: los campos tallados en las
  dos caras y la cola en V de la flecha.
- Medidas: Band 6 x 1,6 x 0,2; Hanging: tablero 3 x 1,2 x 0,15 colgado 0,45 bajo el brazo de 3,5; Post y
  Arrow: poste 0,3 x 4,1 (con la punta), tablero/flecha arriba de y = 3 / 3,2 a 4.
- Fragmentos: 2 por tablero (la regla del 45 % no se puede cumplir con 2: Band 51/49); espesores de 0,2
  y 0,15 como pide el prompt (menos que el mínimo de 0,4 del Bloque C).
- Normales del GLB final: 0 esquinas desviadas.
"""

DARK, PAINT, MID, LIGHT, IRON = "wood_dark", "paint_cream", "wood_mid", "wood_light", "iron"


def inset(poly, d):
    """Achica un polígono convexo-ish hacia su centro una distancia aproximada d (para el campo)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        dx, dy = cx - x, cy - y
        n = (dx * dx + dy * dy) ** 0.5
        out.append((x + dx / n * d * 1.25, y + dy / n * d * 1.25))
    return out


def board_xy(mk, part, outline, field, z0, z1, faces):
    """Tablero de frente (plano xy) entre z0 y z1; field: contorno del campo; faces: 'front' y/o 'back'."""
    mk.prism(part, outline, z1 - z0, DARK, plane="xy", center=(0, 0, (z0 + z1) / 2))
    for f in faces:
        zc = z0 if f == "front" else z1
        mk.carve(part, PAINT, prism=dict(profile=field, depth=0.1, plane="xy", center=(0, 0, zc)))


def crack_cut(mk, part, pts, far, plane="xy", center=(0, 0, 0), depth=1.0):
    """Talla todo lo que queda del lado `far` (x lejano) de la grieta pts (de arriba abajo)."""
    prof = pts + [(far, pts[-1][1]), (far, pts[0][1])]
    mk.carve(part, LIGHT, prism=dict(profile=prof, depth=depth, plane=plane, center=center))


def two_frags(mk, name, origin, build_board, crack, plane="xy", center=(0, 0, 0)):
    """Arma el tablero dos veces y talla cada mitad del lado de la otra."""
    for i, far in enumerate((crack[0][0] + 20, crack[0][0] - 20)):
        p = mk.part(f"{name}_frag0{i + 1}", origin)
        build_board(p, i)
        crack_cut(mk, p, crack, far, plane, center)


def build(mk):
    # ---------------- Sign_Band: banda chata para la falsa fachada ----------------
    bx = 0.0
    out = [(bx - 3, 0.0), (bx + 3, 0.0), (bx + 3, 1.6), (bx - 3, 1.6)]
    field = [(bx - 2.85, 0.15), (bx + 2.85, 0.15), (bx + 2.85, 1.45), (bx - 2.85, 1.45)]

    def band(p, i):
        board_xy(mk, p, out, field, -0.2, 0.0, ("front",))
        if i == 1:                                   # frag01 es la mitad izquierda, frag02 la derecha
            mk.carve(p, MID, prism=dict(profile=[(bx + 3.1, 1.25), (bx + 3.1, 1.7), (bx + 2.6, 1.7)], depth=1.0, plane="xy"))
    two_frags(mk, "Sign_Band", (bx, 0, 0), band,
              [(bx + 0.6, 1.8), (bx + 0.35, 1.1), (bx + 0.05, 1.2), (bx - 0.4, -0.2)])

    # ---------------- Sign_Hanging: ménsula de hierro, cadenas y tablero perpendicular a la pared ----------------
    hx, arm_y = 6.0, 2.0
    br = mk.part("Sign_Hanging_fixed_Bracket", (hx, arm_y, 0))
    mk.box(br, (hx, arm_y - 0.35, -0.03), (0.3, 1.3, 0.06), IRON)                                   # placa contra la pared
    mk.box(br, (hx, arm_y + 0.06, -1.78), (0.12, 0.12, 3.5), IRON)                                  # brazo
    mk.hull(br, [(hx + dx, y, z) for dx in (-0.04, 0.04) for y, z in
                 ((arm_y - 0.9, -0.05), (arm_y - 0.8, -0.05), (arm_y + 0.02, -1.35), (arm_y + 0.02, -1.5))], IRON)  # tornapunta
    mk.carve(br, IRON, points=mk.pts_box((hx, -3, 0), (0.1, 0.1, 0.1)))                             # une los cascos
    top = arm_y - 0.45
    hout = [(-0.2, top), (-3.2, top), (-3.2, top - 1.2), (-0.2, top - 1.2)]                         # (z, y)
    hfield = [(-0.35, top - 0.15), (-3.05, top - 0.15), (-3.05, top - 1.05), (-0.35, top - 1.05)]
    hcrack = [(-1.45, top + 0.1), (-1.7, top - 0.45), (-1.95, top - 0.4), (-2.2, top - 1.3)]

    def hanging(p, i):
        mk.prism(p, hout, 0.15, DARK, plane="zy", center=(hx, 0, 0))
        for xc in (hx - 0.075, hx + 0.075):                                                          # campo en las dos caras
            mk.carve(p, PAINT, prism=dict(profile=hfield, depth=0.1, plane="zy", center=(xc, 0, 0)))
        cz = -0.7 if i == 0 else -2.7                                                                # su cadena
        mk.box(p, (hx, arm_y - 0.1, cz), (0.05, 0.26, 0.13), IRON, detail=True)
        mk.box(p, (hx, arm_y - 0.34, cz), (0.13, 0.27, 0.05), IRON, detail=True)
        if i == 1:
            mk.carve(p, MID, prism=dict(profile=[(-3.3, top - 0.8), (-3.3, top - 1.3), (-2.8, top - 1.3)], depth=1.0,
                                        plane="zy", center=(hx, 0, 0)))
    for i, far in enumerate((-20.0, 20.0)):                                                         # frag01 = lado de la pared
        p = mk.part(f"Sign_Hanging_frag0{i + 1}", (hx, top, -1.7))
        hanging(p, i)
        crack_cut(mk, p, hcrack, far, plane="zy", center=(hx, 0, 0))

    # ---------------- Sign_Post y Sign_Arrow: poste fijo y tablero arriba ----------------
    def post(name, px):
        p = mk.part(f"{name}_fixed_Post", (px, 0, 0))
        mk.box(p, (px, 2.0, 0), (0.3, 4.0, 0.3), MID)
        mk.box(p, (px, 4.05, 0), (0.3, 0.1, 0.3), MID, top=(0.4, 0.4))                             # punta achaflanada
        mk.carve(p, LIGHT, points=mk.pts_box((px, 0.15, -0.15), (0.4, 0.3, 0.12), rot=(0, 0, 20)))   # base comida
        return p

    px = 11.0
    post("Sign_Post", px)
    pout = [(px - 1.25, 3.0), (px + 1.25, 3.0), (px + 1.25, 4.0), (px - 1.25, 4.0)]
    pfield = [(px - 1.1, 3.15), (px + 1.1, 3.15), (px + 1.1, 3.85), (px - 1.1, 3.85)]

    def postboard(p, i):
        board_xy(mk, p, pout, pfield, -0.3, -0.15, ("front", "back"))
        if i == 0:
            mk.carve(p, MID, prism=dict(profile=[(px - 1.35, 3.6), (px - 1.35, 4.1), (px - 0.9, 4.1)], depth=1.0, plane="xy"))
    two_frags(mk, "Sign_Post", (px, 0, 0), postboard,
              [(px + 0.45, 4.1), (px + 0.2, 3.65), (px - 0.05, 3.72), (px - 0.3, 2.9)])

    ax = 16.0
    post("Sign_Arrow", ax)
    y0, y1, ym = 3.2, 4.0, 3.6
    aout = [(ax - 1.5, y0), (ax + 0.95, y0), (ax + 1.5, ym), (ax + 0.95, y1), (ax - 1.5, y1), (ax - 1.25, ym)]
    afield = [(ax - 1.2, y0 + 0.15), (ax + 0.88, y0 + 0.15), (ax + 1.28, ym), (ax + 0.88, y1 - 0.15), (ax - 1.2, y1 - 0.15),
              (ax - 1.03, ym)]

    def arrow(p, i):
        board_xy(mk, p, aout, afield, -0.3, -0.15, ("front", "back"))
        if i == 1:
            mk.carve(p, MID, prism=dict(profile=[(ax + 1.0, y0 - 0.1), (ax + 1.35, y0 - 0.1), (ax + 1.0, y0 + 0.3)], depth=1.0,
                                        plane="xy"))
    two_frags(mk, "Sign_Arrow", (ax, 0, 0), arrow,
              [(ax + 0.35, y1 + 0.1), (ax + 0.15, ym + 0.05), (ax - 0.1, ym + 0.12), (ax - 0.35, y0 - 0.1)])

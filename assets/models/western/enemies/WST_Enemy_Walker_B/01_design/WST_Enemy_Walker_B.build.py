"""
Receta de WST_Enemy_Walker_B, la caminante "mujer del pueblo" (prompt 005, Bloques A + D + H).

Brief
- Silueta a 40 studs: cabeza caída hacia adelante con rodete deshecho, chal rojo en los hombros (el
  acento de color), pollera acampanada hasta arriba de la rodilla con ruedo en zigzag, botas.
- Mismo cuerpo que el caminante A (humanoid.py: H = 5,2, articulaciones del Bloque D). Hombros un poco
  más angostos y caídos; las articulaciones no cambian.
- Piezas: las 15 de R15 con el origen en su articulación, más Eyes. Sin sombrero (prompt).
- Tallado: cuencas, boca, mordida que arranca un pedazo del cuello, blusa rota en el hombro izquierdo,
  agujero de la media, manchas de tierra en la pollera. Pintado: sangre en mentón y cuello, uñas.
Vueltas: 1) primera versión · 2) pelo en una sola cúpula (el cráneo asomaba entre dos capas y parecía
   un casco), picos del ruedo 0,02 adentro (flotaban), manchas de tierra 60 % más grandes · 3) rodete atrás y arriba (quedaba adentro del pelo).

Revisión
- 2276 triángulos contra 1800 de referencia (calidad primero): ruedo en zigzag (12 picos), flecos del
  chal, cordones y los tallados de la cara, el cuello y la media.
- Avisos de "floating" en los picos del ruedo y flecos: están apoyados en la tela; la revisión los ve sueltos
  por milímetros. Se ven bien en las capturas.
- Inferido (sin concepto): forma del chal (espalda y hombros con dos puntas adelante), cordones como
  tres tiras, el agujero de la media en la canilla izquierda.
"""

import humanoid as hu

head, hp = hu.head_space()


def build(mk):
    # ---------------- pollera (LowerTorso) ----------------
    lt = mk.part("LowerTorso", (0, hu.HIP, 0))
    mk.hull(lt, hu.ring(2.92, 0, 0, 1.04, 0.58) + hu.ring(2.40, 0, 0.02, 1.24, 0.80) + hu.round_ring(1.44, 0, 0.03, 1.56, 1.10, n=12),
            "cloth_brown")                                                                 # pollera acampanada
    mk.hull(lt, hu.ring(2.76, 0, 0, 1.10, 0.64) + hu.ring(2.90, 0, 0, 1.10, 0.64), "leather_dark")    # pretina
    for i in range(12):                                                                    # ruedo en zigzag
        a = 6.2832 * (i + 0.5) / 12
        x, z = 0.76 * __import__("math").cos(a), 0.03 + 0.53 * __import__("math").sin(a)   # 0,02 adentro: encima la pollera
        mk.prism(lt, [(-0.13, 0), (0.13, 0), (0.0, -0.13 - 0.05 * (i % 3))], 0.03, "cloth_brown", plane="xy",
                 center=(x, 1.47, z), rot=(0, -__import__("math").degrees(a) + 90, 0), detail=True)
    for c, r in (((0.35, 1.90, -0.42), 0.16), ((-0.45, 1.65, -0.30), 0.13), ((0.20, 2.10, 0.42), 0.15)):
        mk.carve(lt, "ochre", points=mk.pts_ball(c, r, scale=(1, 1, 0.5), subdiv=0))       # tierra

    # ---------------- torso: blusa, chal rojo, cuello mordido ----------------
    ut = mk.part("UpperTorso", (0, hu.WAIST, 0))
    top = [(-0.64, 3.86, -0.28), (-0.64, 3.86, 0.16), (0.66, 3.96, -0.28), (0.66, 3.96, 0.16),
           (-0.28, 4.00, -0.24), (0.28, 4.05, -0.24), (-0.28, 4.00, 0.12), (0.28, 4.05, 0.12)]
    hump = [(-0.36, 3.68, 0.38), (0.36, 3.72, 0.38), (0.0, 3.78, 0.42)]
    mk.hull(ut, hu.ring(2.82, 0, 0, 0.98, 0.54) + hu.ring(3.40, 0, 0.02, 1.20, 0.64) + top + hump, "paint_cream")
    mk.cyl(ut, (0, 4.10, -0.12), 0.20, 0.24, "paint_cream", rot=(-20, 0, 0), sides=10)     # cuello alto de la blusa
    mk.cyl(ut, (0, 4.20, -0.17), 0.16, 0.30, "skin_dead", rot=(-20, 0, 0), sides=10)       # cuello
    # chal: espalda y hombros, 0,04 por fuera, con dos puntas que cuelgan adelante
    mk.hull(ut, [(x, y, z) for x, y, z in ((-0.70, 3.88, -0.06), (0.70, 3.98, -0.06), (-0.70, 3.88, 0.22),
                                           (0.70, 3.98, 0.22), (-0.42, 3.72, 0.44), (0.42, 3.76, 0.44),
                                           (0.0, 3.82, 0.48), (-0.55, 3.45, 0.40), (0.55, 3.45, 0.40),
                                           (-0.30, 4.06, 0.0), (0.30, 4.10, 0.0))], "cloth_red")
    for s in (-1, 1):
        mk.hull(ut, [(s * 0.34, 4.02, -0.30), (s * 0.66, 3.94 + 0.05 * (s > 0), -0.30), (s * 0.66, 3.94 + 0.05 * (s > 0), -0.02),
                     (s * 0.30, 3.30, -0.40), (s * 0.46, 3.24, -0.38), (s * 0.40, 3.40, -0.30)], "cloth_red")   # puntas
        mk.prism(ut, [(-0.08, 0), (0.08, 0), (0.0, -0.15)], 0.03, "cloth_red", plane="xy",
                 center=(s * 0.38, 3.25, -0.40), detail=True)
    for x in (-0.45, -0.15, 0.15, 0.45):                                                   # flecos del chal atrás
        mk.prism(ut, [(-0.08, 0), (0.08, 0), (0.0, -0.16)], 0.03, "cloth_red", plane="xy",
                 center=(x, 3.45, 0.43), rot=(15, 0, 0), detail=True)
    mk.carve(ut, "skin_dead", points=mk.pts_box((-0.55, 3.86, -0.22), (0.26, 0.20, 0.16), rot=(0, 0, 20)))  # blusa rota
    mk.carve(ut, "blood_dry", points=mk.pts_ball((0.17, 4.18, -0.24), 0.09, scale=(1, 1.3, 1), subdiv=0))  # mordida
    mk.paint(ut, "blood_dry", ball=((0.15, 4.02, -0.26), 0.10))

    # ---------------- cabeza: rodete deshecho, cara de muerta ----------------
    hd = mk.part("Head", hu.NECK_P)
    hu.cranium(mk, hd, head, width=0.90)
    hu.zombie_face(mk, hd, head, hp)
    mk.hull(hd, head(hu.round_ring(4.70, 0, -0.02, 0.96, 0.72) + hu.round_ring(4.95, 0, -0.18, 1.00, 0.94)
                     + hu.round_ring(5.10, 0, -0.22, 0.92, 0.90) + hu.round_ring(5.24, 0, -0.22, 0.60, 0.64)),
            "hair_dark")                                                                   # pelo: una cúpula sobre el cráneo
    mk.ball(hd, hp((0.08, 5.16, 0.30)), 0.22, "hair_dark", scale=(1, 0.85, 1), subdiv=1)    # rodete corrido, asoma atrás
    for s, x, z in ((-1, -0.40, -0.36), (1, 0.44, -0.20), (-1, -0.18, 0.20)):              # mechones sueltos
        mk.hull(hd, head([(x, 5.02, z), (x + s * 0.07, 5.02, z + 0.06), (x + s * 0.03, 4.50, z - 0.04),
                          (x + s * 0.06, 4.62, z + 0.02)]), "hair_dark")
    for s in (-1, 1):
        mk.hull(hd, head(mk.pts_box((s * 0.45, 4.70, -0.22), (0.08, 0.22, 0.15), top=(1, 0.7))), "skin_dead")  # orejas
    mk.paint(hd, "blood_dry", ball=(hp((-0.10, 4.22, -0.70)), 0.08))
    hu.eyes(mk, hp)

    # ---------------- brazos: mangas largas de la blusa ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        sh, el, wr = hu.arm_joints(s)
        ua = mk.part(f"{side}UpperArm", sh)
        hu.limb(mk, ua, (sh[0], sh[1] + 0.10, sh[2]), el, 0.38, 0.40, 0.32, 0.32, "paint_cream")
        la = mk.part(f"{side}LowerArm", el)
        hu.limb(mk, la, el, wr, 0.30, 0.30, 0.25, 0.25, "paint_cream")
        hu.limb(mk, la, (wr[0], wr[1] + 0.10, wr[2]), wr, 0.29, 0.29, 0.29, 0.29, "paint_cream", over=0.02)   # puño
        hd_ = mk.part(f"{side}Hand", wr)
        hu.hand(mk, hd_, s, broken_finger=(side == "Left"))

    # ---------------- piernas: medias negras, botas con cordones ----------------
    for side, s in (("Left", -1), ("Right", 1)):
        hip, knee, ankle = hu.leg_joints(s)
        ul = mk.part(f"{side}UpperLeg", hip)
        hu.limb(mk, ul, hip, knee, 0.44, 0.46, 0.34, 0.36, "cloth_black")
        ll = mk.part(f"{side}LowerLeg", knee)
        hu.limb(mk, ll, knee, (hip[0], 0.72, 0), 0.32, 0.34, 0.24, 0.26, "cloth_black")
        mk.hull(ll, hu.ring(0.86, hip[0], 0, 0.36, 0.38) + hu.ring(0.22, hip[0], 0, 0.32, 0.36), "leather_dark")  # caña
        mk.hull(ll, hu.ring(0.82, hip[0], 0, 0.40, 0.42) + hu.ring(0.90, hip[0], 0, 0.40, 0.42), "leather_dark")
        for y in (0.40, 0.55, 0.70):                                                       # cordones
            mk.box(ll, (hip[0], y, -0.185), (0.16, 0.03, 0.03), "canvas", detail=True)
        if side == "Left":                                                                 # agujero en la media
            mk.carve(ll, "skin_dead", points=mk.pts_box((hip[0], 1.08, -0.16), (0.18, 0.22, 0.12), rot=(0, 0, 15)))
        ft = mk.part(f"{side}Foot", ankle)
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.15, 0.15) for y, z in
                     ((0.04, 0.18), (0.32, 0.16), (0.28, -0.14), (0.04, -0.44), (0.16, -0.42))], "leather_dark")
        mk.hull(ft, [(hip[0] + x, y, z) for x in (-0.16, 0.16) for y, z in
                     ((0.0, 0.19), (0.05, 0.19), (0.0, -0.46), (0.05, -0.46))], "coal")          # suela

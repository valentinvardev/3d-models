"""
Receta de WST_Weapon_Knife, el cuchillo global (prompt 034, Bloques A + F).

Brief
- Forma base neutra (sirve para cualquier mundo, sin estética del oeste). Silueta a 30 studs: hoja recta de
  punta recortada (clip point) más larga que el mango, guarda chata cruzada y pomo plano.
- Medidas: hoja 0,75 x 0,16 de alto en la base x 0,03 de grueso, con una sola faceta de afilado a lo largo
  del filo; guarda 0,3 de ancho; mango 0,5 con 3 anillos bajos; pomo plano. Largo total 1,33.
- Orientación: punta hacia -Z, filo abajo (-Y), lomo arriba. Origen = centro del mango.
- Piezas: Blade y Handle (con la guarda y el pomo). Las dos fijas: origen en el del modelo. Marcadores
  _Grip (centro del mango) y _Tip (punta).
- Materiales (3): steel_light (hoja) · gunmetal (guarda, pomo) · leather_dark (mango).
- La hoja es un solo casco convexo: lomo y costados planos (x = ±0,015) y la faceta del afilado que baja del
  "bisel" (0,05 arriba del filo) hasta el filo (±0,002). La línea del bisel la da el cambio de cara.

Inferido (el prompt no lo dice)
- El recorte de la punta es recto (no cóncavo): la hoja entera queda convexa y más neutra.
- Los anillos del mango son tres canaletas bajas (0,007) entre cuatro tramos.

Vueltas: 1) primera versión: la punta se leía de lanza (recorte corto y punta alta) y el mango tenía 748
triángulos (octógono con esquinas a 56°: el chanflán de 50° le tocaba todos los bordes largos) · 2) recorte
recto desde 0,72 hasta la punta en y = 0 (se lee clip point), faceta del filo más alta (0,062), esquinas del
mango a 45° · 3) cuero del mango como detalle sin chanflán (588 -> 300): la mano lo tapa.

Revisión
- 358 triángulos contra 250 de referencia (calidad primero): el chanflán de guarda y pomo, y las canaletas.
- La hoja es un solo casco (34 triángulos): la línea del afilado es el cambio de cara, sin otro material
  (el prompt pide la hoja de un solo metal para las skins).
"""

BLADE_BASE, TIP_Z = -0.26, -1.04
HALF_T = 0.015


def ring_xy(z, hw, hh, k=0.4):
    """Octágono estirado en Y (sección del mango) a la altura z, con esquinas a 45° (el chanflán no las toca)."""
    cx = cy = min(hw, hh) * k
    return [(x, y, z) for x, y in ((-hw + cx, -hh), (hw - cx, -hh), (hw, -hh + cy), (hw, hh - cy),
                                   (hw - cx, hh), (-hw + cx, hh), (-hw, hh - cy), (-hw, -hh + cy))]


def build(mk):
    # ---------------- hoja: lomo, recorte de la punta, panza y la faceta del filo ----------------
    blade = mk.part("Blade", (0, 0, 0))
    spine = [(BLADE_BASE, 0.07), (-0.72, 0.07)]                                       # el recorte baja recto a la punta
    edge = [(BLADE_BASE, -0.09), (-0.70, -0.09), (-0.88, -0.07), (-0.98, -0.035)]
    bevel = [(z, y + 0.062) for z, y in edge[:3]] + [(-0.97, 0.0)]
    pts = [(s * HALF_T, y, z) for z, y in spine + bevel for s in (-1, 1)]
    pts += [(s * 0.002, y, z) for z, y in edge for s in (-1, 1)]
    pts.append((0.0, 0.0, TIP_Z))                                                     # punta
    mk.hull(blade, pts, "steel_light")
    mk.marker("_Tip", (0.0, 0.0, TIP_Z))

    # ---------------- mango: cuatro tramos y tres anillos bajos, guarda y pomo ----------------
    hd = mk.part("Handle", (0, 0, 0))
    cuts = [-0.25, -0.13, 0.01, 0.15, 0.25]
    for k in range(4):
        z0, z1 = cuts[k], cuts[k + 1]
        a, b = (z0 + 0.01 if k else z0), (z1 - 0.01 if k < 3 else z1)
        # cuero como detalle (sin chanflán): la mano lo tapa casi todo y el chanflán duplicaba sus triángulos
        mk.hull(hd, ring_xy(a, 0.039, 0.056) + ring_xy(b, 0.039, 0.056), "leather_dark", detail=True)
        if k < 3:                                                                       # canaleta entre tramos
            mk.hull(hd, ring_xy(z1 - 0.015, 0.032, 0.048) + ring_xy(z1 + 0.015, 0.032, 0.048), "leather_dark",
                    detail=True)
    mk.box(hd, (0, 0, -0.27), (0.064, 0.30, 0.04), "gunmetal")                        # guarda chata
    mk.hull(hd, ring_xy(0.245, 0.044, 0.062) + ring_xy(0.29, 0.04, 0.056), "gunmetal")  # pomo plano
    mk.bevel(hd, width=0.008, angle=50)
    mk.marker("_Grip", (0, 0, 0))

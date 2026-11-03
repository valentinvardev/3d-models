"""
Receta de WST_Kit_Trim, molduras y esquineros del kit modular (prompt 013, Bloques A + B).

Brief
- Silueta a 40 studs: líneas oscuras que ordenan la fachada: el esquinero vertical en las esquinas,
  la faja entre plantas y la cornisa escalonada.
- Piezas fijas (no se rompen), en fila sobre X, cada una con su origen:
  - fixed_Trim_Corner (x = 0): dos tablas wood_dark en L de 0,15 de espesor, 0,6 x 0,6 de planta, 10 de
    alto. Origen en la base de la esquina del edificio (donde se cruzan las dos caras de afuera); la L
    abraza la esquina de adelante a la derecha: una tabla sobre la cara del frente (mira a -Z) y otra
    sobre la del costado (mira a +X). Para las otras esquinas se gira 90°.
  - fixed_Trim_Belt (x = 6): faja de 8 x 0,4 x 0,15, lomo inclinado para que escurra el agua.
  - fixed_Trim_Cornice (x = 16): moldura de 8 x 0,6 x 0,5 con perfil escalonado (filete, media caña en
    dos escalones, corona) y el escalón del medio en wood_mid para que el perfil se lea.
  Faja y cornisa: origen abajo al centro de la cara de atrás (z = 0 = superficie de la pared); salen
  hacia -Z.
- Inferido: espesor de las tablas del esquinero, orientación de la L y origen en la esquina, origen de
  faja y cornisa en la cara de atrás, perfil de la cornisa, desgaste (una punta comida abajo en el
  esquinero).

Vueltas: 1) construida a la primera; capturas sin cambios.

Revisión
- Triángulos contra 80 por pieza: Corner 24, Belt 16, Cornice 32.
- Medidas: Corner 0,6 x 10 x 0,6 (la tabla del costado se mete 0,005 en la del frente: 0,605); Belt 8 x 0,4 x
  0,15; Cornice 8 x 0,6 x 0,5.
- Avisos aceptados: "floating" de Belt y Cornice: son piezas sueltas en la fila, no tocan a nada.
- Normales del GLB final: 0 esquinas desviadas.
"""

DARK, MID, LIGHT = "wood_dark", "wood_mid", "wood_light"
T = 0.15


def build(mk):
    # ---------------- esquinero en L ----------------
    c = mk.part("fixed_Trim_Corner", (0, 0, 0))
    mk.box(c, ((-0.6 + T + T) / 2, 5.0, -T / 2), (0.6, 10.0, T), DARK)          # tabla del frente: x -0,45..0,15
    mk.box(c, (T / 2, 5.0, (0.6 - T) / 2 - 0.0), (T, 10.0, 0.6 - T + 0.01), DARK)  # tabla del costado: z -0,01..0,45
    mk.carve(c, LIGHT, prism=dict(profile=[(-0.5, -0.1), (-0.15, -0.1), (-0.5, 0.35)], depth=0.5, plane="xy",
                                  center=(0, 0, -0.1)))                           # punta comida abajo

    # ---------------- faja ----------------
    b = mk.part("fixed_Trim_Belt", (6.0, 0, 0))
    mk.prism(b, [(0.0, 0.0), (-0.15, 0.0), (-0.15, 0.3), (-0.06, 0.4), (0.0, 0.4)], 8.0, DARK, plane="zy",
             center=(6.0, 0, 0))

    # ---------------- cornisa ----------------
    k = mk.part("fixed_Trim_Cornice", (16.0, 0, 0))
    prof = [(0.0, 0.0), (-0.12, 0.0), (-0.12, 0.14), (-0.21, 0.2), (-0.29, 0.31), (-0.37, 0.4), (-0.5, 0.45),
            (-0.5, 0.6), (0.0, 0.6)]
    mk.prism(k, prof, 8.0, DARK, plane="zy", center=(16.0, 0, 0))
    mk.paint(k, MID, box=((16.0, 0.255, -0.25), (8.2, 0.09, 0.06)))              # escalón de la media caña

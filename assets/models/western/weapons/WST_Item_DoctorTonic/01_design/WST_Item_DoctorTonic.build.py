"""
Receta de WST_Item_DoctorTonic, el tónico del doctor (prompt 038, Bloques A + B).

Brief
- Silueta a 40 studs: frasco de remedio de vidrio verde, alto y rectangular con las aristas verticales
  achaflanadas, hombro corto, cuello con labio y corcho claro; etiqueta crema grande en el frente (-Z) y
  un hilo atado al cuello con una etiquetita de papel apoyada en el hombro.
- Medidas: 0,7 de alto con el corcho, 0,28 x 0,18 (chaflanes de 0,03). Cuerpo hasta 0,48, hombro hasta
  0,56, cuello r 0,045 con labio r 0,056, corcho r 0,04 hasta 0,7. Origen abajo al centro.
- Una pieza (Body). La etiqueta va pintada (cuatro cortes) sobre la cara plana del frente: es coplanar,
  no una calcomanía encima. El cuello va en 6 lados.
- Inferido: el nombre Body, las alturas de hombro y cuello, el labio del pico, el hilo de soga y la
  etiquetita sobre el hombro del frente (si cuelga derecho, choca con el hombro).

Vueltas: 1) el hilo salía como corona de dientes: el hombro (r ~0,05 en y = 0,566) lo atravesaba ·
2) hilo más arriba, pero seguía: cuello y labio en un solo casco convexo hacen un cono (el anillo de
0,045 en 0,60 quedaba adentro) · 3) cuello y labio en dos cascos.

Revisión
- 146 triángulos contra 120 de referencia: el labio separado del cuello y la etiquetita del hombro.
- Una sola pieza, como pide el Bloque B: en Studio vidrio, corcho y etiquetas son el mismo MeshPart, así
  que el frasco no puede llevar Glass con transparencia sin volver transparentes el corcho y las
  etiquetas. Si se quiere vidrio de verdad, separar Bottle y el resto (decide Valentin).
"""

import math

W, D, C = 0.28, 0.18, 0.03         # ancho, profundidad, chaflán de las aristas verticales
Y_BODY, Y_SHOULDER = 0.48, 0.56


def section(y, w=W, d=D, c=C):
    """Sección del frasco: rectángulo con las cuatro esquinas cortadas a 45°."""
    x, z = w / 2, d / 2
    return [(x - c, y, -z), (x, y, -z + c), (x, y, z - c), (x - c, y, z),
            (-x + c, y, z), (-x, y, z - c), (-x, y, -z + c), (-x + c, y, -z)]


def ring(y, r, sides=6):
    return [(r * math.cos(2 * math.pi * i / sides), y, r * math.sin(2 * math.pi * i / sides)) for i in range(sides)]


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    mk.hull(body, section(0.0) + section(Y_BODY) + ring(Y_SHOULDER, 0.05), "glass_green")         # cuerpo y hombro
    mk.hull(body, ring(Y_SHOULDER - 0.01, 0.045) + ring(0.615, 0.045), "glass_green")              # cuello
    mk.hull(body, ring(0.60, 0.056) + ring(0.635, 0.056), "glass_green")   # labio (otro casco: en uno solo el
    #                                                                        cuello sale cónico y atraviesa el hilo)
    mk.cyl(body, (0, 0.665, 0), 0.04, 0.07, "wood_light", sides=6, top=1.12)                        # corcho
    mk.cyl(body, (0, 0.583, 0), 0.058, 0.024, "rope", sides=6)                                      # hilo atado (solo sobre el cuello)
    # etiquetita de papel apoyada en el hombro del frente
    p0z, p0y = -D / 2, Y_BODY
    dz, dy = 0.04 / math.hypot(0.04, 0.08), 0.08 / math.hypot(0.04, 0.08)
    nz, ny = -dy, dz
    tag = [(x, p0y + dy * s + ny * o, p0z + dz * s + nz * o)
           for x in (-0.02, 0.06) for s in (0.008, 0.075) for o in (-0.002, 0.012)]
    mk.hull(body, tag, "paint_cream")
    # etiqueta grande del frente: pintada sobre la cara plana
    for x in (-0.1, 0.1):
        mk.slice(body, (x, 0, 0), (1, 0, 0))
    for y in (0.11, 0.37):
        mk.slice(body, (0, y, 0), (0, 1, 0))
    mk.paint(body, "paint_cream", box=((0, 0.24, -D / 2), (0.198, 0.258, 0.01)))

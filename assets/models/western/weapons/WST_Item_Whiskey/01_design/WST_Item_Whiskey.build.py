"""
Receta de WST_Item_Whiskey, la botella de whisky (prompt 040, Bloques A + B).

Brief
- Silueta a 40 studs: botella ámbar alta de 8 lados con hombro cuadrado y cuello corto, etiqueta crema
  que envuelve el frente y corcho claro arriba. Es "la misma botella que la molotov": la forma vive en
  bottle() para que WST_Weapon_WhiskeyMolotov la importe (como el barril explosivo importa barrel()).
- Medidas (las del prompt de la molotov): 0,75 de alto con el corcho, 0,28 de ancho (r 0,145 a los
  vértices: 0,268 entre caras planas), 8 lados con una cara plana al frente. Cuerpo hasta 0,48, hombro
  hasta 0,53 (30° de caída: "cuadrado"), cuello r 0,045, labio r 0,055 hasta 0,665, corcho hasta 0,75.
  Origen abajo al centro.
- Una pieza (Body). Etiqueta pintada (dos cortes) sobre las tres caras del frente: la cara plana sola
  mide 0,11 de ancho, angosta para leerse.
- Inferido: el nombre Body, las alturas de hombro, cuello y labio, la etiqueta pintada en vez de 0,01
  afuera (sin calcomanías, construccion.md), el corcho asomando 0,085 sobre el labio.

Vueltas: 1) pasa la revisión a la primera (cuello y labio en cascos separados desde el principio: en
el tónico, un solo casco los volvía un cono).

Revisión
- 120 triángulos contra 120.
- Una sola pieza (Bloque B): vidrio, corcho y etiqueta son el mismo MeshPart en Studio; el material Glass
  con transparencia no se puede usar sin volver transparentes el corcho y la etiqueta (igual que el
  tónico). Decide Valentin si se separa Bottle.
- Para la molotov: importar bottle() de esta receta y poner el trapo encima de Y_LIP1.
"""

R = 0.145
Y_BODY, Y_SHOULDER = 0.48, 0.53
NECK_R, LIP_R = 0.045, 0.055
Y_LIP0, Y_LIP1 = 0.635, 0.665


def bottle(mk, part, x0=0.0, z0=0.0, glass="glass_amber", label="paint_cream"):
    """Botella cuadrada de whisky del Western (whisky y molotov). Base en y = 0, centro en (x0, z0).
    Deja el labio en Y_LIP1: el corcho o el trapo van encima."""
    c = (x0, 0, z0)
    mk.hull(part, mk.pts_cyl((x0, Y_BODY / 2, z0), R, Y_BODY, sides=8)
            + mk.pts_cyl((x0, Y_SHOULDER, z0), 0.06, 0.0001, sides=8), glass)                    # cuerpo y hombro
    mk.cyl(part, (x0, (Y_SHOULDER - 0.02 + Y_LIP0 + 0.01) / 2, z0), NECK_R, Y_LIP0 + 0.01 - (Y_SHOULDER - 0.02),
           glass, sides=6)                                                                        # cuello
    mk.cyl(part, (x0, (Y_LIP0 + Y_LIP1) / 2, z0), LIP_R, Y_LIP1 - Y_LIP0, glass, sides=6)          # labio
    if label:
        for y in (0.14, 0.38):
            mk.slice(part, (0, y, 0), (0, 1, 0))
        mk.paint(part, label, box=((c[0], 0.26, c[2] - 0.12), (0.32, 0.238, 0.16)))               # tres caras del frente
    return c


def build(mk):
    body = mk.part("Body", (0, 0, 0))
    bottle(mk, body)
    mk.cyl(body, (0, (Y_LIP1 - 0.015 + 0.75) / 2, 0), 0.04, 0.75 - (Y_LIP1 - 0.015), "wood_light", sides=6, top=1.1)  # corcho

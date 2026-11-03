"""
Receta de WST_Overlay_SilverEyes, la plata viva en los ojos (prompt 006, Bloques A + G).

Brief
- Lo que se tiene que leer a 40 studs: dos puntos celestes que brillan adentro de las cuencas y dos
  lágrimas de luz que bajan por las mejillas. El brillo y el pulso los pone el motor (Neon).
- Calza con la cabeza de los caminantes (humanoid.py, H = 5,2): las dos piezas con el origen en el
  cuello (hu.NECK_P), igual que Head, y la geometría en el espacio de la cabeza caída (hu.head_space).
- Silver_Eyes: los ojos de hu.eyes (bolitas subdiv=0 en hp((±0,19; 4,74; −0,60)), radio 0,08,
  escala 1 × 0,8 × 0,8) con radio 0,095: envuelven 0,012-0,015 al ojo de la base, así no titilan si el
  motor deja los dos a la vista, y siguen adentro de la cuenca.
- Silver_Tears: una tira por ojo, 0,05 de ancho que se afina hasta la punta, 0,25 de largo. Baja desde
  el borde de abajo del ojo, abriéndose hacia afuera para no cruzar la boca (la comisura está en
  x = ±0,24). Sigue la cara: cada sección se proyecta sobre la cabeza del caminante A (rayo desde el
  frente contra los cascos de hu.cranium) y queda 0,01 por fuera en los bordes y 0,025 en la cresta.
- Inferido: el recorrido de las lágrimas (hacia afuera, para esquivar la boca) y el radio de los ojos.

Vueltas: 1) primera versión (80 triángulos; la punta de la lágrima caía sobre la comisura) ·
2) lágrima de 3 secciones en vez de 4 y la punta 0,06 más afuera (x = ±0,30): 64 triángulos.

Revisión
- 64 triángulos contra 60: los ojos son la misma bolita de 20 triángulos de la base (40) y cada lágrima
  son dos tramos (8 + 4). Con menos tramos la lágrima deja de seguir el valle entre pómulo y mandíbula.
- Revisado montado sobre los caminantes A y B (script de revisión que junta los dos .blend): sin
  z-fighting con Head ni Eyes, sin partes flotando, la lágrima sigue la mejilla y termina afuera de la
  boca. En B (cabeza 0,90 de ancho) queda unos 0,005 más afuera: no se nota.
- Los avisos de "floating" de la revisión sola son esperables: el overlay no toca nada sin el caminante.
"""

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import humanoid as hu

head, hp = hu.head_space()


class _Probe:
    """Hace de `mk` para hu.cranium: junta los cascos en vez de construirlos, para medir la cara."""

    def __init__(self, mk):
        self.hulls = []
        self.pts_box, self.pts_ball, self.pts_cyl = mk.pts_box, mk.pts_ball, mk.pts_cyl

    def hull(self, part, points, mat, detail=False):
        if not detail:
            self.hulls.append([tuple(p) for p in points])

    def carve(self, *a, **k):
        pass

    def paint(self, *a, **k):
        pass


def face_surface(mk, width=0.94):
    """BVH de la cabeza del caminante sin girar (coordenadas del juego, antes de head())."""
    probe = _Probe(mk)
    hu.cranium(probe, None, lambda pts: list(pts), width=width)
    bm = bmesh.new()
    for pts in probe.hulls:
        vs = [bm.verts.new(p) for p in pts]
        bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bvh = BVHTree.FromBMesh(bm)
    bm.free()

    def hit(x, y):
        loc, n, _, _ = bvh.ray_cast(Vector((x, y, -3.0)), Vector((0, 0, 1)))
        if loc is None:
            raise ValueError(f"el rayo no toca la cara en ({x}, {y})")
        n = n if n.z < 0 else -n
        return loc, n
    return hit


def tear_strip(mk, part, hit, path, widths, base=0.010, ridge=0.025):
    """Tira en relieve que sigue la cara: secciones triangulares (dos bordes y una cresta) unidas por
    cascos que se encastran 0,01; la última sección es una punta."""
    secs = []
    for i, (x, y) in enumerate(path):
        a = Vector(path[max(i - 1, 0)])
        b = Vector(path[min(i + 1, len(path) - 1)])
        t = (b - a).normalized()
        side = Vector((-t.y, t.x))
        c, nc = hit(x, y)
        w = widths[i]
        if w <= 0:
            secs.append([c + nc * (base + ridge) / 2])
            continue
        l, nl = hit(x - side.x * w / 2, y - side.y * w / 2)
        r, nr = hit(x + side.x * w / 2, y + side.y * w / 2)
        secs.append([l + nl * base, r + nr * base, c + nc * ridge])
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        if i + 1 < len(secs) - 1:   # el final de este tramo se mete 0,01 en el siguiente, apenas más fino
            nxt = secs[i + 2]
            cb = sum(b, Vector()) / len(b)
            cn = sum(nxt, Vector()) / len(nxt)
            fwd = (cn - cb).normalized() * 0.01
            b = [cb + (p - cb) * 0.92 + fwd for p in b]
        mk.hull(part, head([tuple(p) for p in a + b]), "silver_neon")


def build(mk):
    eyes = mk.part("Silver_Eyes", hu.NECK_P)
    for s in (-1, 1):
        mk.ball(eyes, hp((s * 0.19, 4.74, -0.60)), 0.095, "silver_neon", scale=(1.0, 0.8, 0.8), subdiv=0)

    tears = mk.part("Silver_Tears", hu.NECK_P)
    hit = face_surface(mk)
    for s in (-1, 1):
        path = [(s * 0.200, 4.690), (s * 0.238, 4.570), (s * 0.300, 4.455)]
        tear_strip(mk, tears, hit, path, widths=(0.05, 0.042, 0.0))

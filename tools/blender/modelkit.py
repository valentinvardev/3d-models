"""
modelkit: construir modelos del Western por código en Blender, con las reglas del proyecto puestas.

Cada modelo tiene su receta en assets/models/western/<carpeta>/<Id>/01_design/<Id>.build.py con
`def build(mk):` y la corre tools/blender/build_model.py. La receta usa solo esta API.
Cómo construir bien (método, recetas por tipo, revisión): .claude/skills/fabrica-modelos/.

COORDENADAS DEL JUEGO (las de los prompts): 1 unidad = 1 stud, Y arriba, el frente del modelo mira
a -Z, la derecha del personaje es +X. modelkit las pasa a Blender por dentro.

Formas (todas cerradas; `mat` es un token de la paleta: "wood_mid", "skin_dead"...):
  mk.part(name, origin)                  pieza (objeto) con su origen = su pivote o articulación
  mk.box(part, center, size, mat, rot=(0,0,0), top=(1,1), shift=(0,0), detail=False)
        caja; `top` escala la cara de arriba (x, z) y `shift` la corre: troncos, cuñas, inclinaciones
  mk.cyl(part, center, radius, length, mat, axis="y", sides=8, rot=(0,0,0), top=1.0, detail=False)
  mk.ball(part, center, radius, mat, scale=(1,1,1), rot=(0,0,0), subdiv=1, detail=False)
  mk.hull(part, points, mat, detail=False)        volumen convexo que envuelve los puntos
  mk.prism(part, profile, depth, mat, plane="xy", center=(0,0,0), rot=(0,0,0), detail=False)
        perfil 2D (convexo o no) extruido: alas de sombrero, gatillos, harapos en zigzag
  mk.marker(name, pos)                   cubito de 0,05 para puntos de enganche (_Muzzle, _Grip...)

Cada pieza tiene dos etapas. BASE (lo de arriba sin detail): se puede redondear, tallar y pintar.
DETALLE (detail=True): se agrega al final, sin tocar; para lo que va adentro de un hueco tallado
(ojos en las cuencas, dientes en la boca, costillas en una rotura) o encima sin mezclarse.

Acabado de la base, en este orden al cerrar:
  mk.smooth(part, level=1)               subdivide (Catmull-Clark) y deja las caras planas: formas
                                         orgánicas redondeadas y facetadas (cabezas, manos, frutas)
  mk.bevel(part, width=0.012, angle=35, mat=None)
        chanflán de un segmento en los bordes más vivos que `angle`: los bordes agarran luz (armas,
        herramientas, armazones). Con `mat`, las caras del chanflán toman ese color (filo gastado).
        Selectivo: en piezas que mandan, no en todo.
  mk.carve(part, mat, points=... | prism=dict(profile=, depth=, plane=, center=, rot=))
        talla un hueco con un cortador (booleana): las paredes del hueco toman `mat`
        (cuencas oscuras, boca roja, la mordida que arranca un pedazo, una rotura)
  mk.slice(part, point, normal)          corta la base con un plano: crea bordes para pintar con límite nítido
  mk.paint(part, mat, box=(center, size) | ball=(center, radius))
        pinta las caras de la base cuyo centro cae en la zona: color SIN geometría encima
        (mejillas, sangre, venas, suciedad). Nunca cajitas pegadas como calcomanías.
Puntos para cortadores y cascos: mk.pts_box(...), mk.pts_cyl(...), mk.pts_ball(...) (mismos
argumentos que box/cyl/ball, sin part ni mat). Otras ayudas: mk.zigzag(a, b, teeth, depth, side),
mk.mirror(points).
"""

import math
import re
from pathlib import Path

import bmesh
import bpy
from mathutils import Euler, Vector

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "assets" / "models" / "Prompts de modelos - Western.md"


def read_palette():
    pal = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([a-z_]+)` \| `([0-9A-F]{6})` \|", line)
        if m:
            pal[m.group(1)] = m.group(2)
    return pal


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_blender(p):
    """Juego (x, y arriba, z con el frente en -Z) -> Blender (x, y, z arriba), igual que el import glTF."""
    x, y, z = p
    return Vector((x, -z, y))


def _rotate(points, rot):
    """Rota puntos (juego) por ángulos en grados (x, y, z) alrededor del origen."""
    if not any(rot):
        return [Vector(p) for p in points]
    e = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    return [e @ Vector(p) for p in points]


def _apply_modifiers(ob):
    """Aplica los modificadores de ob reemplazando su malla por la evaluada."""
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = new
    bpy.data.meshes.remove(old)


class Kit:
    def __init__(self, model_id):
        self.id = model_id
        self.palette = read_palette()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.root = bpy.data.objects.new(model_id, None)
        bpy.context.scene.collection.objects.link(self.root)
        self._objs, self._origin = {}, {}
        self._bm = {}       # (part, "base" | "detail") -> bmesh
        self._mats = {}     # (part, stage) -> [material]
        self._fin = {}      # part -> {"smooth": n, "carve": [...], "slice": [...], "paint": [...]}

    # ---- materiales --------------------------------------------------------
    def _material(self, token):
        if token not in self.palette:
            raise ValueError(f"'{token}' no está en la paleta: {sorted(self.palette)}")
        hx = self.palette[token]
        name = f"{token}_{hx}"
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name)
            rgb = [_srgb_to_linear(int(hx[k:k + 2], 16) / 255) for k in (0, 2, 4)]
            mat.diffuse_color = (*rgb, 1.0)
            bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
            bsdf.inputs["Roughness"].default_value = 1.0
        return mat

    def _mat_index(self, part, stage, token):
        mats = self._mats[(part, stage)]
        mat = self._material(token)
        if mat not in mats:
            mats.append(mat)
        return mats.index(mat)

    # ---- piezas -------------------------------------------------------------
    def part(self, name, origin=(0, 0, 0)):
        if name in self._objs:
            raise ValueError(f"la pieza '{name}' ya existe")
        ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        bpy.context.scene.collection.objects.link(ob)
        ob.parent = self.root
        ob.location = to_blender(origin)
        self._objs[name] = ob
        self._origin[name] = to_blender(origin)
        for stage in ("base", "detail"):
            self._bm[(name, stage)] = bmesh.new()
            self._mats[(name, stage)] = []
        self._fin[name] = {"smooth": 0, "bevel": None, "carve": [], "slice": [], "paint": []}
        return name

    def _local(self, part, p):
        return to_blender(p) - self._origin[part]

    # ---- puntos de formas (para cascos y cortadores) --------------------------
    @staticmethod
    def pts_box(center, size, rot=(0, 0, 0), top=(1, 1), shift=(0, 0)):
        sx, sy, sz = (s / 2 for s in size)
        pts = [(ix * sx * kx + dx, y, iz * sz * kz + dz)
               for y, kx, kz, dx, dz in ((-sy, 1, 1, 0, 0), (sy, top[0], top[1], shift[0], shift[1]))
               for ix in (-1, 1) for iz in (-1, 1)]
        c = Vector(center)
        return [tuple(c + p) for p in _rotate(pts, rot)]

    @staticmethod
    def pts_cyl(center, radius, length, axis="y", sides=8, rot=(0, 0, 0), top=1.0):
        pts = [(r * math.cos(2 * math.pi * (i + 0.5) / sides), y, r * math.sin(2 * math.pi * (i + 0.5) / sides))
               for y, r in ((-length / 2, radius), (length / 2, radius * top)) for i in range(sides)]
        base = {"y": (0, 0, 0), "x": (0, 0, -90), "z": (90, 0, 0)}[axis]
        c = Vector(center)
        return [tuple(c + p) for p in _rotate(_rotate(pts, base), rot)]

    @staticmethod
    def pts_ball(center, radius, scale=(1, 1, 1), rot=(0, 0, 0), subdiv=1):
        tmp = bmesh.new()
        bmesh.ops.create_icosphere(tmp, subdivisions=subdiv, radius=radius)
        pts = [(v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]) for v in tmp.verts]
        tmp.free()
        c = Vector(center)
        return [tuple(c + p) for p in _rotate(pts, rot)]

    # ---- formas ---------------------------------------------------------------
    def _hull_into(self, bm, points, to_local):
        verts = [bm.verts.new(to_local(p)) for p in points]
        res = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
        # puntos repetidos o interiores: quedan sueltos y pueden venir dos veces en las listas
        loose = list({v for v in res["geom_interior"] + res["geom_unused"] if isinstance(v, bmesh.types.BMVert)})
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        return [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]

    def hull(self, part, points, mat, detail=False):
        stage = "detail" if detail else "base"
        faces = self._hull_into(self._bm[(part, stage)], points, lambda p: self._local(part, p))
        mi = self._mat_index(part, stage, mat)
        for f in faces:
            f.material_index = mi

    def box(self, part, center, size, mat, rot=(0, 0, 0), top=(1, 1), shift=(0, 0), detail=False):
        self.hull(part, self.pts_box(center, size, rot, top, shift), mat, detail)

    def cyl(self, part, center, radius, length, mat, axis="y", sides=8, rot=(0, 0, 0), top=1.0, detail=False):
        self.hull(part, self.pts_cyl(center, radius, length, axis, sides, rot, top), mat, detail)

    def ball(self, part, center, radius, mat, scale=(1, 1, 1), rot=(0, 0, 0), subdiv=1, detail=False):
        self.hull(part, self.pts_ball(center, radius, scale, rot, subdiv), mat, detail)

    @staticmethod
    def _prism_points(profile, depth, plane, center, rot):
        h = depth / 2
        to3 = {"xy": lambda a, b, d: (a, b, d), "zy": lambda a, b, d: (d, b, a),
               "xz": lambda a, b, d: (a, d, b)}.get(plane)
        if to3 is None:
            raise ValueError("plane: xy, zy o xz")
        c = Vector(center)
        front = [tuple(c + p) for p in _rotate([to3(a, b, -h) for a, b in profile], rot)]
        back = [tuple(c + p) for p in _rotate([to3(a, b, h) for a, b in profile], rot)]
        return front, back

    def _prism_into(self, bm, front, back, to_local):
        vf = [bm.verts.new(to_local(p)) for p in front]
        vb = [bm.verts.new(to_local(p)) for p in back]
        faces = [bm.faces.new(vf), bm.faces.new(list(reversed(vb)))]
        n = len(front)
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new((vf[i], vb[i], vb[j], vf[j])))
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        return faces

    def prism(self, part, profile, depth, mat, plane="xy", center=(0, 0, 0), rot=(0, 0, 0), detail=False):
        stage = "detail" if detail else "base"
        front, back = self._prism_points(profile, depth, plane, center, rot)
        faces = self._prism_into(self._bm[(part, stage)], front, back, lambda p: self._local(part, p))
        mi = self._mat_index(part, stage, mat)
        for f in faces:
            f.material_index = mi

    def marker(self, name, pos):
        self.part(name, (0, 0, 0))
        self.box(name, pos, (0.05, 0.05, 0.05), "iron")

    # ---- acabado de la base ------------------------------------------------------
    def smooth(self, part, level=1):
        self._fin[part]["smooth"] = level

    def bevel(self, part, width=0.012, angle=35, mat=None):
        self._fin[part]["bevel"] = (width, angle, mat)

    def carve(self, part, mat, points=None, prism=None):
        if (points is None) == (prism is None):
            raise ValueError("carve: pasar points= o prism=")
        self._fin[part]["carve"].append((mat, points, prism))

    def slice(self, part, point, normal):
        self._fin[part]["slice"].append((point, normal))

    def paint(self, part, mat, box=None, ball=None):
        if (box is None) == (ball is None):
            raise ValueError("paint: pasar box=(center, size) o ball=(center, radius)")
        self._fin[part]["paint"].append((mat, box, ball))

    # ---- ayudas para puntos --------------------------------------------------
    @staticmethod
    def zigzag(a, b, teeth, depth, side=(0, -1, 0)):
        """Puntos de a a b con `teeth` dientes de `depth` hacia `side` (vector, juego)."""
        a, b, s = Vector(a), Vector(b), Vector(side).normalized()
        pts = []
        for i in range(2 * teeth + 1):
            p = a.lerp(b, i / (2 * teeth))
            if i % 2 == 1:
                p = p + s * depth
            pts.append(tuple(p))
        return pts

    @staticmethod
    def mirror(points):
        return [(-p[0], p[1], p[2]) for p in points]

    # ---- cierre --------------------------------------------------------------
    def _finish_part(self, name):
        ob, fin = self._objs[name], self._fin[name]
        base = self._bm[(name, "base")]
        if not base.faces and not self._bm[(name, "detail")].faces:
            raise ValueError(f"la pieza '{name}' quedó vacía")
        bmesh.ops.recalc_face_normals(base, faces=base.faces)
        base.to_mesh(ob.data)
        base.free()
        for m in self._mats[(name, "base")]:
            ob.data.materials.append(m)

        if fin["smooth"]:
            mod = ob.modifiers.new("Smooth", "SUBSURF")
            mod.levels = mod.render_levels = fin["smooth"]
            _apply_modifiers(ob)

        if fin["bevel"]:
            width, angle, mat = fin["bevel"]
            mod = ob.modifiers.new("Chamfer", "BEVEL")
            mod.width, mod.segments = width, 1
            mod.limit_method, mod.angle_limit = "ANGLE", math.radians(angle)
            mod.use_clamp_overlap = True
            if mat:
                m = self._material(mat)
                if m.name not in ob.data.materials:
                    ob.data.materials.append(m)
                mod.material = list(ob.data.materials).index(ob.data.materials[m.name])
            _apply_modifiers(ob)

        cutters = []
        for i, (mat, points, prism) in enumerate(fin["carve"]):
            cme = bpy.data.meshes.new(f"_cut_{name}_{i}")
            cbm = bmesh.new()
            if points is not None:
                self._hull_into(cbm, points, lambda p: self._local(name, p))
            else:
                front, back = self._prism_points(prism["profile"], prism["depth"], prism.get("plane", "xy"),
                                                 prism.get("center", (0, 0, 0)), prism.get("rot", (0, 0, 0)))
                self._prism_into(cbm, front, back, lambda p: self._local(name, p))
            bmesh.ops.recalc_face_normals(cbm, faces=cbm.faces)
            cbm.to_mesh(cme)
            cbm.free()
            cme.materials.append(self._material(mat))
            cob = bpy.data.objects.new(cme.name, cme)
            bpy.context.scene.collection.objects.link(cob)
            cob.location = ob.location.copy()     # el cortador está en coordenadas locales de la pieza
            cutters.append(cob)
            mod = ob.modifiers.new(f"Carve{i}", "BOOLEAN")
            mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cob
            mod.material_mode = "TRANSFER"
            mod.use_self = True                    # la base son varios cascos que se cruzan: sin esto, la booleana se come el volumen (medido con el caminante A)
        if cutters:
            bpy.context.view_layer.update()
            _apply_modifiers(ob)
            for cob in cutters:
                me = cob.data
                bpy.data.objects.remove(cob)
                bpy.data.meshes.remove(me)

        bm = bmesh.new()
        bm.from_mesh(ob.data)
        for point, normal in fin["slice"]:
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=self._local(name, point),
                                   plane_no=to_blender(normal), clear_inner=False, clear_outer=False)
        if fin["paint"]:
            bm.faces.ensure_lookup_table()
            for mat, box, ball in fin["paint"]:
                m = self._material(mat)
                if m.name not in ob.data.materials:
                    ob.data.materials.append(m)
                mi = list(ob.data.materials).index(ob.data.materials[m.name])
                for f in bm.faces:
                    c = f.calc_center_median()
                    if box is not None:
                        bc = self._local(name, box[0])
                        sx, sy, sz = box[1]
                        half = Vector((sx, sz, sy)) / 2   # tamaño del juego (x, y, z) -> Blender (x, z, y)
                        inside = all(abs(c[k] - bc[k]) <= half[k] for k in range(3))
                    else:
                        inside = (c - self._local(name, ball[0])).length <= ball[1]
                    if inside:
                        f.material_index = mi

        detail = self._bm[(name, "detail")]
        if detail.faces:
            remap = []
            for m in self._mats[(name, "detail")]:
                if m.name not in ob.data.materials:
                    ob.data.materials.append(m)
                remap.append(list(ob.data.materials).index(ob.data.materials[m.name]))
            tmp = bpy.data.meshes.new("_detail")
            bmesh.ops.recalc_face_normals(detail, faces=detail.faces)
            detail.to_mesh(tmp)
            n_before = len(bm.faces)
            bm.from_mesh(tmp)
            bm.faces.ensure_lookup_table()
            for f in bm.faces[n_before:]:
                f.material_index = remap[f.material_index] if f.material_index < len(remap) else 0
            bpy.data.meshes.remove(tmp)
        detail.free()

        bm.to_mesh(ob.data)
        bm.free()
        for p in ob.data.polygons:
            p.use_smooth = False
        ob.data.update()
        return sum(len(p.vertices) - 2 for p in ob.data.polygons)

    def finish(self):
        stats = {name: self._finish_part(name) for name in list(self._objs)}
        bpy.context.view_layer.update()
        return stats

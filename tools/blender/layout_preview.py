"""
Capturas de un modelo del pueblo armado con tools/roblox/town.py (lee su layout; no modifica nada).

  "%LOCALAPPDATA%\\Programs\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python-exit-code 1 -P tools/blender/layout_preview.py -- <layout.json> [<layout.json> ...] ^
      [--out <png>] [--res 640]

Cada pieza del layout trae "src": [<Id del modelo>, <nodo>]: se trae ese objeto de 02_blend/<Id>.blend
(la malla limpia, la misma que se subió) y se pone con el CFrame y el tamaño del layout. Las piezas sin
malla ("block") salen como cajas de su color. Con varios layouts, cada uno se corre a su "at" (el centro de
su caja en el mapa), así se ve el edificio con su porche, techo y columnas.

Coordenadas: el juego es Y arriba y frente en -Z; en Blender un punto del juego (x, y, z) es (x, -z, y).
Deja <out> (por defecto, al lado del primer layout: <nombre>.preview.png) con cuatro vistas: frente,
3/4 desde arriba, 3/4 del otro lado y atrás. El frente sale del "front" del primer layout.
"""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "assets" / "models" / "western"
sys.path.insert(0, str(REPO / "vendor" / "skills" / "el4cteo-blender-skills" / "skills" / "blender-asset-qa" / "scripts"))
import review_shots  # noqa: E402

TO_BLENDER = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def game_point(v):
    return Vector((v.x, v.z, -v.y))


_sources = {}


def source(model_id, node):
    """El objeto `node` de 02_blend/<Id>.blend, sin linkear a la escena; y el centro de su caja en el juego."""
    key = (model_id, node)
    if key not in _sources:
        hits = list(MODELS.glob(f"*/{model_id}/02_blend/{model_id}.blend"))
        if not hits:
            raise SystemExit(f"falta 02_blend de {model_id}")
        with bpy.data.libraries.load(str(hits[0]), link=False) as (src, dst):
            if node not in src.objects:
                raise SystemExit(f"{model_id}: no tiene el objeto {node}")
            dst.objects = [node]
        ob = dst.objects[0]
        mw = ob.matrix_world.copy()
        pts = [game_point(mw @ v.co) for v in ob.data.vertices]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        _sources[key] = (ob, mw, (lo + hi) / 2, hi - lo)
    return _sources[key]


def cframe(cf, at):
    m = Matrix.Identity(4)
    for i in range(3):
        for j in range(3):
            m[i][j] = cf[3 + i * 3 + j]
        m[i][3] = cf[i] + at[i]
    return m


def block_material(color):
    name = "block_%02x%02x%02x" % tuple(color)
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (color[0] / 255, color[1] / 255, color[2] / 255, 1)
    return mat


def place(layout, at, names):
    for i, p in enumerate(layout["parts"]):
        cf = cframe(p["cframe"], at)
        if p.get("src"):
            ob, mw, center, size = source(*p["src"])
            k = [p["size"][a] / max(size[a], 1e-6) for a in range(3)]
            scale = Matrix.Diagonal((k[0], k[1], k[2], 1))
            m = TO_BLENDER @ cf @ scale @ Matrix.Translation(-center) @ TO_BLENDER.inverted() @ mw
            new = bpy.data.objects.new(f"{layout['name']}_{i:03d}_{p['name']}", ob.data)
            new.matrix_world = m
        else:
            mesh = bpy.data.meshes.new(f"block_{i}")
            s = [v / 2 for v in p["size"]]
            vs = [(x * s[0], y * s[1], z * s[2]) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
            faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
            mesh.from_pydata(vs, [], faces)
            mesh.materials.append(block_material(p.get("color", [128, 128, 128])))
            new = bpy.data.objects.new(f"{layout['name']}_{i:03d}_{p['name']}", mesh)
            new.matrix_world = TO_BLENDER @ cf
        bpy.context.scene.collection.objects.link(new)
        names.append(new.name)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = ("--out", "--res", "--front", "--list")
    out = args[args.index("--out") + 1] if "--out" in args else None
    res = int(args[args.index("--res") + 1]) if "--res" in args else 640
    paths = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in opts)]
    if "--list" in args:  # un archivo con un layout por línea (para el pueblo entero)
        paths += Path(args[args.index("--list") + 1]).read_text(encoding="utf-8").split()
    if not paths:
        raise SystemExit(__doc__)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    names = []
    layouts = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    for layout in layouts:
        place(layout, layout.get("at", [0, 0, 0]), names)
    f = layouts[0].get("front", [0, 0, -1])
    if "--front" in args:  # hacia dónde mira la primera vista, en ejes del juego: "0,0,-1"
        f = [float(v) for v in args[args.index("--front") + 1].split(",")]
    front = Vector((f[0], -f[2], f[1])).normalized()
    side = Vector((-front.y, front.x, 0))
    views = [tuple(front + Vector((0, 0, 0.12))), tuple(front + side * 0.9 + Vector((0, 0, 0.6))),
             tuple(front - side * 0.9 + Vector((0, 0, 0.25))), tuple(-front + Vector((0, 0, 0.3)))]
    out = out or str(Path(paths[0]).with_suffix("").with_suffix(".preview.png"))
    r = review_shots.run(objects=names, out=out, views=views, mode="material", res=res)
    for p in r["views"]:
        Path(p).unlink(missing_ok=True)
    print("@@JSON@@" + json.dumps({"sheet": r["sheet"], "parts": len(names)}))


main()

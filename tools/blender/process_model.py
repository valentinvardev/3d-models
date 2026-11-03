"""
Lleva un modelo de Claude Design hasta un GLB listo para el Import 3D de Studio.

  "%LOCALAPPDATA%\\Programs\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python-exit-code 1 -P tools/blender/process_model.py -- WST_Prop_Crate [--no-render]

Lee   assets/models/western/<carpeta>/<Id>/01_design/<Id>.glb (o .obj)   el original: nunca se toca
Deja  02_blend/<Id>.blend      archivo de trabajo: limpio, con los materiales de la paleta (editable)
      03_export/<Id>.glb       para Studio: atlas de paleta y girado 180°
      review_*.png             hojas de capturas; la primera vista es el frente del modelo
      report.json              qué pasó y qué falló

Cada paso sale de medir la caja (ver "Medido" y "Aprendido con los pilotos" en
assets/models/Prompts de modelos - Western.md):

  1. Importar y soldar: Claude Design exporta cada triángulo con sus propios vértices.
  2. Unir caras coplanares del mismo material y re-triangular: saca las astillas (caja: 1182 -> 524).
  3. Revisar con qa_check del pack de Blender (perfil roblox) y contra el TRIANGLE BUDGET del prompt.
  4. Guardar 02_blend.
  5. Atlas de paleta: una textura y un material; cada cara apunta al cuadrito de su color.
     Studio ignora los colores de material del glTF y parte cada material en un MeshPart.
  6. Girar 180° sobre la vertical: el importador toma +Z del glTF como frente. Exportar GLB.

Usa solo scripts revisados del pack de Blender (tabla en vendor/skills/README.md).
"""

import json
import math
import re
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "assets" / "models" / "Prompts de modelos - Western.md"
MODELS = REPO / "assets" / "models" / "western"
PALETTE_DIR = MODELS / "_palette"
VENDOR = REPO / "vendor" / "skills" / "el4cteo-blender-skills" / "skills"

# Carpeta según el prefijo del id (tabla del paso 4 de "Cómo usar" del documento)
FOLDERS = [
    (("WST_Weapon_", "WST_Item_"), "weapons"),
    (("WST_Pickup_",), "pickups"),
    (("WST_Prop_",), "props"),
    (("WST_NPC_",), "npcs"),
    (("WST_Enemy_", "WST_Overlay_"), "enemies"),
    (("WST_Boss_",), "bosses"),
    (("WST_Mount_", "WST_Vehicle_", "WST_Train_"), "transport"),
    (("WST_Kit_",), "kit"),
    (("WST_DG_", "WST_Canyon_", "WST_Bg_", "WST_RM_", "WST_Mine_", "WST_SB_", "WST_Track_", "WST_HC_", "WST_CH_"), "sets"),
]

# Tokens que en Studio piden otro Material además del color (Neon, Glass, Metal)
STUDIO_MATERIAL = {"silver_neon": "Neon", "lamp_glow": "Neon", "glass": "Glass", "glass_amber": "Glass",
                   "glass_green": "Glass", "water": "Glass", "gunmetal": "Metal", "steel_light": "Metal",
                   "silver_crust": "Metal"}

ATLAS_SIZE, ATLAS_CELL = 512, 64
WELD_DIST = 1e-4
DISSOLVE_ANGLE = math.radians(0.5)

sys.path.insert(0, str(VENDOR / "blender-asset-qa" / "scripts"))
sys.path.insert(0, str(VENDOR / "blender-export-pipelines" / "scripts"))
import export_asset  # noqa: E402
import qa_check  # noqa: E402
import review_shots  # noqa: E402


# ---- entrada -------------------------------------------------------------------

def model_dir(model_id):
    for prefixes, folder in FOLDERS:
        if model_id.startswith(prefixes):
            return MODELS / folder / model_id
    raise SystemExit(f"{model_id}: prefijo sin carpeta (ver FOLDERS)")


def read_palette():
    """token -> hex, en el orden de la tabla "Paleta propuesta" del documento."""
    tokens = []
    for line in DOC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([a-z_]+)` \| `([0-9A-F]{6})` \|", line)
        if m:
            tokens.append((m.group(1), m.group(2)))
    if not tokens or len(tokens) > (ATLAS_SIZE // ATLAS_CELL) ** 2:
        raise SystemExit(f"paleta inválida en el documento: {len(tokens)} tokens")
    return tokens


def read_budget(model_id):
    lines = DOC.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.strip() == f"MODEL: {model_id}":
            m = re.match(r"^TRIANGLE BUDGET: <= (\d+) triangles (.+?)\.", lines[i + 1])
            if m:
                return int(m.group(1)), m.group(2)
    return None, None


def import_source(src):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if src.suffix == ".glb":
        res = bpy.ops.import_scene.gltf(filepath=str(src))
    else:
        res = bpy.ops.wm.obj_import(filepath=str(src), forward_axis="NEGATIVE_Z", up_axis="Y")
    if res != {"FINISHED"}:
        raise SystemExit(f"no se pudo importar {src}")
    bpy.context.view_layer.update()


# ---- 1 y 2: soldar, unir caras coplanares, re-triangular -----------------------

def clean_meshes():
    stats = {}
    for ob in [o for o in bpy.data.objects if o.type == "MESH"]:
        if ob.data.users > 1:
            ob.data = ob.data.copy()
        me = ob.data
        # El import glTF crea normales personalizadas por esquina. Después de soldar y re-triangular se
        # decodifican mal y llegaban al GLB de Studio: medido el 2026-10-28, 52 esquinas en FalseFront
        # (algunas invertidas, parche oscuro) y 33 en el revólver. Los modelos son de caras planas: fuera.
        if "custom_normal" in me.attributes:
            me.attributes.remove(me.attributes["custom_normal"])
        before = sum(len(p.vertices) - 2 for p in me.polygons)
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD_DIST)
        bmesh.ops.dissolve_limit(bm, angle_limit=DISSOLVE_ANGLE, use_dissolve_boundaries=False,
                                 verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
        bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
        # caras vecinas con el giro invertido (revólver: 14 bordes en Body)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = False
        stats[ob.name] = {"tris_before": before, "tris": len(me.polygons)}
    return stats


def check_materials(palette):
    """Cada material tiene que ser <token>_<HEX> de la paleta. Devuelve errores y tokens por objeto."""
    hexes = dict(palette)
    errors, used = [], {}
    for ob in [o for o in bpy.data.objects if o.type == "MESH"]:
        toks = []
        for slot in ob.material_slots:
            name = slot.material.name if slot.material else ""
            m = re.match(r"^([a-z_]+?)_([0-9A-F]{6})(\.\d+)?$", name)
            if not m or m.group(1) not in hexes:
                errors.append(f"{ob.name}: material fuera de la paleta: {name!r}")
                toks.append(None)
            else:
                if hexes[m.group(1)] != m.group(2):
                    errors.append(f"{ob.name}: {name!r} no coincide con la paleta ({hexes[m.group(1)]})")
                toks.append(m.group(1))
        used[ob.name] = toks
    return errors, used


def size_studs():
    """Medidas en ejes de Roblox (X, alto, profundidad); el glTF importado tiene Z de Blender arriba."""
    obs = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("_")]
    pts = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    d = [round(h - l, 3) for l, h in zip(lo, hi)]
    return {"x": d[0], "y_alto": d[2], "z": d[1], "piso_blender_z": round(lo[2], 4)}


# ---- 5: atlas de paleta ----------------------------------------------------------

def build_palette_image(palette):
    cols = ATLAS_SIZE // ATLAS_CELL
    img = bpy.data.images.new("WST_Palette", ATLAS_SIZE, ATLAS_SIZE, alpha=False)
    px = [0.0] * (ATLAS_SIZE * ATLAS_SIZE * 4)
    for i, (_, hx) in enumerate(palette):
        r, g, b = (int(hx[k:k + 2], 16) / 255 for k in (0, 2, 4))
        cx, cy = i % cols, i // cols
        for y in range(ATLAS_CELL):
            row = (ATLAS_SIZE - 1 - (cy * ATLAS_CELL + y)) * ATLAS_SIZE  # fila 0 de la grilla arriba
            for x in range(ATLAS_CELL):
                o = (row + cx * ATLAS_CELL + x) * 4
                px[o:o + 4] = (r, g, b, 1.0)
    img.pixels.foreach_set(px)
    PALETTE_DIR.mkdir(parents=True, exist_ok=True)
    img.filepath_raw = str(PALETTE_DIR / "WST_Palette.png")
    img.file_format = "PNG"
    img.save()
    centers = {}
    for i, (tok, hx) in enumerate(palette):
        cx, cy = i % cols, i // cols
        centers[tok] = ((cx * ATLAS_CELL + ATLAS_CELL / 2) / ATLAS_SIZE,
                        1 - (cy * ATLAS_CELL + ATLAS_CELL / 2) / ATLAS_SIZE)
    (PALETTE_DIR / "palette.json").write_text(json.dumps(
        {"size": ATLAS_SIZE, "cell": ATLAS_CELL,
         "tokens": {t: {"hex": h, "uv": [round(c, 5) for c in centers[t]]} for t, h in palette}},
        indent=1), encoding="utf-8")
    return img, centers


def apply_atlas(img, centers, used_tokens):
    mat = bpy.data.materials.new("WST_Palette")
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 1.0
    # triangulito dentro de la celda (25 % del lado): sin área cero y lejos de los bordes
    h = (ATLAS_CELL * 0.25) / ATLAS_SIZE
    tri = [(-h, -h), (h, -h), (0.0, h)]
    for ob in [o for o in bpy.data.objects if o.type == "MESH"]:
        me = ob.data
        toks = used_tokens[ob.name]
        uv = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
        me.uv_layers.active = uv
        for poly in me.polygons:
            tok = toks[poly.material_index] if poly.material_index < len(toks) else None
            cu, cv = centers.get(tok, (0.0, 0.0))
            for k, li in enumerate(poly.loop_indices):
                du, dv = tri[k % 3]
                uv.data[li].uv = (cu + du, cv + dv)
        me.materials.clear()
        me.materials.append(mat)
        for poly in me.polygons:
            poly.material_index = 0


# ---- 6: girar 180° para Studio ---------------------------------------------------

def rotate_for_studio():
    """Gira todo 180° sobre la vertical. La rotación queda en la malla y cada objeto conserva su
    origen (rotado) sin rotación propia: así el pivote de las piezas móviles llega a Studio."""
    rot = Matrix.Rotation(math.pi, 4, "Z")
    obs = list(bpy.data.objects)
    world = {ob.name: ob.matrix_world.copy() for ob in obs}

    def depth(ob):
        d, p = 0, ob.parent
        while p:
            d, p = d + 1, p.parent
        return d

    for ob in sorted(obs, key=depth):
        m = world[ob.name]
        new_world = Matrix.Translation(rot @ m.translation)
        if ob.type == "MESH":
            ob.data.transform(new_world.inverted() @ rot @ m)
            ob.data.update()
        ob.matrix_world = new_world
    bpy.context.view_layer.update()


# ---- principal --------------------------------------------------------------------

def process(model_id, render=True):
    """Corre los pasos 1 a 6 sobre 01_design/<Id>.glb (u .obj). Devuelve el reporte; también lo escribe."""
    folder = model_dir(model_id)
    src = next((folder / "01_design" / f"{model_id}{ext}" for ext in (".glb", ".obj")
                if (folder / "01_design" / f"{model_id}{ext}").exists()), None)
    if src is None:
        raise SystemExit(f"falta {folder / '01_design' / (model_id + '.glb')}")
    report = {"id": model_id, "source": str(src.relative_to(REPO)), "errors": [], "warnings": []}

    palette = read_palette()
    import_source(src)
    report["objects_imported"] = sorted(o.name for o in bpy.data.objects)

    # 1 y 2
    stats = clean_meshes()
    mat_errors, used = check_materials(palette)
    report["errors"] += mat_errors
    for name, toks in used.items():
        stats[name]["colors"] = sorted({t for t in toks if t})
        special = sorted({STUDIO_MATERIAL[t] for t in toks if t in STUDIO_MATERIAL})
        if special:
            stats[name]["studio_material"] = special
    report["objects"] = stats
    total = sum(s["tris"] for s in stats.values())
    report["tris"] = {"before": sum(s["tris_before"] for s in stats.values()), "after": total}

    # 3: presupuesto, medidas y revisión
    limit, scope = read_budget(model_id)
    if limit is None:
        report["warnings"].append("no encontré el TRIANGLE BUDGET del prompt")
    elif scope in ("for the whole model", "in total") or scope.startswith("in total"):
        ok = total <= limit
        report["budget"] = {"limit": limit, "scope": scope, "pass": ok}
        if not ok:
            report["warnings"].append(f"{total} triángulos > tope {limit}")
    else:
        report["budget"] = {"limit": limit, "scope": scope, "pass": None,
                            "note": "el tope no es del modelo entero: revisar a mano"}
    report["size_studs"] = size_studs()
    pieces = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("_")]
    qa = qa_check.run(objects=pieces, profile="roblox", uv=False)
    accepted = [w for w in qa["warnings"] if w.startswith("hidden back-to-back faces")]
    # Una pieza móvil (origen propio = su pivote) puede no tocar a las demás: el cilindro del
    # revólver gira dentro del armazón. Pasa a aviso para revisarlo en la captura.
    movers = {o.name for o in bpy.data.objects if o.type == "MESH" and o.matrix_world.translation.length > 1e-6}
    qa_errors, qa_warnings = [], [w for w in qa["warnings"] if w not in accepted]
    for e in qa["errors"]:
        m = re.match(r"^floating/detached part in (\S+) ", e)
        if m and m.group(1) in movers:
            qa_warnings.append(f"{e} — pieza móvil: revisar en la captura que no se vea separada")
        else:
            qa_errors.append(e)
    report["qa"] = {"pass": not qa_errors, "errors": qa_errors, "warnings": qa_warnings,
                    "accepted": f"{len(accepted)} contactos entre piezas (esperados en destructibles y piezas encastradas)"}
    report["errors"] += qa_errors
    report["warnings"] += qa_warnings

    # 4
    (folder / "02_blend").mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / "02_blend" / f"{model_id}.blend"))

    # capturas: el frente del modelo mira a +Y de Blender hasta el giro del paso 6
    if render:
        views = [(0, 1, 0.15), (1, 1, 0.6), (1, 0, 0.15), (0, -1, 0.15)]
        report["renders"] = []
        for mode in ("material", "random", "wire"):
            out = folder / f"review_{mode}.png"
            res = review_shots.run(objects=pieces, out=str(out), views=views, mode=mode, res=512)
            for p in res["views"]:
                Path(p).unlink(missing_ok=True)
            report["renders"].append(out.name)

    # 5 y 6
    img, centers = build_palette_image(palette)
    apply_atlas(img, centers, used)
    rotate_for_studio()
    (folder / "03_export").mkdir(exist_ok=True)
    roots = [o.name for o in bpy.data.objects if o.parent is None]
    exp = export_asset.run(preset="roblox_gltf", objects=roots, out=str(folder / "03_export" / f"{model_id}.glb"),
                           no_anim=True)
    f = exp["files"][0]
    report["export"] = {"file": str(Path(f["file"]).relative_to(REPO)), "ok": f["ok"], "kb": f["kb"],
                        "summary": f.get("summary")}
    if not f["ok"]:
        report["errors"].append("falló la exportación")
    elif f.get("summary", {}).get("tris") != total:
        report["warnings"].append(f"el GLB tiene {f['summary'].get('tris')} triángulos, se esperaban {total}")

    report["pass"] = not report["errors"]
    (folder / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    try:  # el visor 3D lee el índice de modelos; si falla, el modelo igual quedó procesado
        sys.path.insert(0, str(REPO / "tools" / "viewer"))
        import build_index
        build_index.build()
    except Exception as e:  # noqa: BLE001
        report["warnings"].append(f"no se actualizó el índice del visor: {e}")
    print("@@JSON@@" + json.dumps({k: report[k] for k in ("id", "pass", "tris", "budget", "size_studs", "errors", "warnings")
                                   if k in report}, ensure_ascii=False))
    return report


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args:
        raise SystemExit(__doc__)
    report = process(args[0], render="--no-render" not in args)
    if not report["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

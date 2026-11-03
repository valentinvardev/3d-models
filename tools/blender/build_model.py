"""
Construye un modelo desde su receta y lo pasa por process_model (limpieza, revisión, capturas, atlas, GLB).

  "%LOCALAPPDATA%\\Programs\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python-exit-code 1 -P tools/blender/build_model.py -- <Id> [--no-render]

Receta: assets/models/western/<carpeta>/<Id>/01_design/<Id>.build.py, con `def build(mk):` (API en
modelkit.py). Deja 01_design/<Id>.glb, el mismo archivo y formato que entrega Claude Design, y sigue
como si viniera de ahí. Si en 01_design ya hay un GLB de Claude Design, lo guarda como
<Id>.claude-design.glb antes de escribir (nunca lo pisa).
"""

import importlib.util
import json
import struct
import sys
from pathlib import Path

import bpy

sys.dont_write_bytecode = True  # que la receta no deje __pycache__ en 01_design
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelkit  # noqa: E402
import process_model  # noqa: E402


def glb_generator(path):
    with open(path, "rb") as f:
        f.read(12)
        n, _ = struct.unpack("<II", f.read(8))
        return json.loads(f.read(n)).get("asset", {}).get("generator", "")


def build(model_id, render=True):
    folder = process_model.model_dir(model_id)
    design = folder / "01_design"
    recipe = design / f"{model_id}.build.py"
    if not recipe.exists():
        raise SystemExit(f"falta la receta {recipe}")

    spec = importlib.util.spec_from_file_location(f"recipe_{model_id}", recipe)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    kit = modelkit.Kit(model_id)
    mod.build(kit)
    tris = kit.finish()

    glb = design / f"{model_id}.glb"
    if glb.exists() and "THREE" in glb_generator(glb):
        keep = design / f"{model_id}.claude-design.glb"
        if keep.exists():
            raise SystemExit(f"ya existe {keep.name}: moverlo a mano antes de construir")
        glb.rename(keep)
    for ob in bpy.data.objects:
        ob.select_set(True)
    res = bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True,
                                    export_yup=True, export_apply=True, export_materials="EXPORT",
                                    export_animations=False, export_cameras=False, export_lights=False)
    if res != {"FINISHED"}:
        raise SystemExit("falló la exportación del GLB de la receta")
    print("@@JSON@@" + json.dumps({"built": model_id, "parts": len(tris), "tris_raw": sum(tris.values())}))

    report = process_model.process(model_id, render=render)
    report["built_from"] = str(recipe.relative_to(process_model.REPO))
    report["tris_raw_by_part"] = tris
    (folder / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    return report


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args:
        raise SystemExit(__doc__)
    report = build(args[0], render="--no-render" not in args)
    if not report["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

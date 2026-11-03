"""
Capturas de revisión de un modelo ya construido (lee 02_blend/<Id>.blend; no modifica nada).

  "%LOCALAPPDATA%\\Programs\\Blender Foundation\\Blender 5.2\\blender.exe" -b --factory-startup ^
      --python-exit-code 1 -P tools/blender/review_model.py -- <Id> [--focus Head,Eyes,UpperTorso]

Deja en la carpeta del modelo:
  review_focus.png   primer plano de las piezas de --focus (la zona que el jugador mira: cara, frente
                     del arma, la parte que se rompe), cuatro vistas: frente, 3/4, costado, 3/4 opuesto
  review_small.png   el modelo entero a 96 px de alto, como se ve a ~40 studs en un celular:
                     frente, 3/4, costado y espalda. Si la silueta no se lee acá, no se lee en el juego.
El frente del modelo (-Z del juego) mira a +Y de Blender en 02_blend: la primera vista es siempre el frente.
"""

import sys
from pathlib import Path

import bpy

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "vendor" / "skills" / "el4cteo-blender-skills" / "skills" / "blender-asset-qa" / "scripts"))
import process_model  # noqa: E402
import review_shots  # noqa: E402

FRONT, FRONT34, SIDE, BACK34, BACK = (0, 1, 0.15), (0.8, 1, 0.35), (1, 0.1, 0.15), (-0.8, 1, 0.2), (0, -1, 0.15)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args:
        raise SystemExit(__doc__)
    model_id = args[0]
    focus = args[args.index("--focus") + 1].split(",") if "--focus" in args else []
    folder = process_model.model_dir(model_id)
    blend = folder / "02_blend" / f"{model_id}.blend"
    if not blend.exists():
        raise SystemExit(f"falta {blend}: construir o procesar el modelo primero")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    meshes = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("_")]
    out = {}
    if focus:
        missing = [f for f in focus if f not in bpy.data.objects]
        if missing:
            raise SystemExit(f"no existen: {missing}; piezas: {meshes}")
        r = review_shots.run(objects=focus, out=str(folder / "review_focus.png"),
                             views=[FRONT, FRONT34, SIDE, BACK34], mode="material", res=640)
        out["focus"] = r["sheet"]
        for p in r["views"]:
            Path(p).unlink(missing_ok=True)
    r = review_shots.run(objects=meshes, out=str(folder / "review_small.png"),
                         views=[FRONT, FRONT34, SIDE, BACK], mode="material", res=96)
    out["small"] = r["sheet"]
    for p in r["views"]:
        Path(p).unlink(missing_ok=True)
    print("@@JSON@@" + str(out))


main()

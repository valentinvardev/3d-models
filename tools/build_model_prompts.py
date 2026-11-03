"""
Arma un .txt listo para pegar en Claude Design por cada modelo del documento de prompts,
numerados en orden de producción, y crea la carpeta 01_design de cada uno.

  py -I tools/build_model_prompts.py

Lee   assets/models/Prompts de modelos - Western.md   (la fuente: los .txt no se editan a mano)
Deja  assets/models/western/_prompts/NNN_<Id>.txt     Bloque A + bloques de su tipo + prompt + dónde guardarlo
      assets/models/western/_prompts/NNN_<Id>_concepto.txt   si el modelo tiene imagen de concepto:
                                                     el prompt para el generador de imágenes (va primero)
      assets/models/western/_prompts/_INDICE.md       número, id, nombre y carpeta de cada uno

Las rutas salen de la carpeta desde donde se corre: si el repo cambia de lugar, volver a correrlo.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "assets" / "models" / "Prompts de modelos - Western.md"
MODELS = REPO / "assets" / "models" / "western"
OUT = MODELS / "_prompts"

# Misma tabla que tools/blender/process_model.py (paso 4 de "Cómo usar" del documento)
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

# Orden de producción: los tres pilotos y el tramo de Dusty Gulch ("Orden de producción recomendado"
# del documento). Lo demás sigue el orden del documento.
FIRST = [
    "WST_Prop_Crate", "WST_Weapon_Revolver", "WST_Item_Rounds", "WST_Enemy_Walker_A", "WST_Enemy_Walker_B",
    "WST_Overlay_SilverEyes", "WST_Kit_Wall", "WST_Kit_FalseFront", "WST_Kit_Door", "WST_Kit_Window",
    "WST_Kit_Porch", "WST_Kit_Roof", "WST_Kit_Trim", "WST_Kit_Sign", "WST_Kit_Barricade", "WST_Kit_Interior",
    "WST_Kit_WallStone", "WST_Prop_Barrel", "WST_Prop_BarrelExplosive", "WST_Prop_CrateLarge",
    "WST_NPC_OldHank", "WST_Weapon_HanksWidow", "WST_Enemy_Runner", "WST_Enemy_DeadGunslinger",
    "WST_Boss_Sheriff", "WST_Weapon_Dynamite", "WST_Mount_Horse",
]


def folder_for(model_id):
    for prefixes, folder in FOLDERS:
        if model_id.startswith(prefixes):
            return MODELS / folder / model_id
    raise SystemExit(f"{model_id}: prefijo sin carpeta")


def code_block_after(lines, i):
    j = next(k for k in range(i + 1, len(lines)) if lines[k].strip() == "```")
    k = next(k for k in range(j + 1, len(lines)) if lines[k].strip() == "```")
    return "\n".join(lines[j + 1:k])


def concept_block_after(lines, i):
    """Segundo bloque de la sección si empieza con CONCEPT IMAGE; None si no hay o si antes viene otro título."""
    j = next(k for k in range(i + 1, len(lines)) if lines[k].strip() == "```")
    k = next(k for k in range(j + 1, len(lines)) if lines[k].strip() == "```")
    for m in range(k + 1, len(lines)):
        if lines[m].startswith("#"):
            return None
        if lines[m].strip() == "```":
            body = []
            for n in range(m + 1, len(lines)):
                if lines[n].strip() == "```":
                    break
                body.append(lines[n])
            return "\n".join(body) if body and body[0].startswith("CONCEPT IMAGE") else None
    return None


def main():
    lines = DOC.read_text(encoding="utf-8").splitlines()
    blocks = {}
    models = []  # (id, nombre, letras de bloques, prompt)
    for i, line in enumerate(lines):
        b = re.match(r"^### Bloque ([A-H]) ", line)
        if b:
            blocks[b.group(1)] = code_block_after(lines, i)
            continue
        h = re.match(r"^#{3,4} `(WST_[A-Za-z_]+)` — (.+)$", line)
        if h:
            meta = next((ln for ln in lines[i + 1:i + 8] if ln.startswith("- **Bloques:**")), None)
            if meta is None:
                raise SystemExit(f"{h.group(1)}: falta la línea de Bloques")
            letters = re.findall(r"\b([A-H])\b", meta.split("·")[0])
            models.append((h.group(1), h.group(2).strip(), letters, code_block_after(lines, i),
                           concept_block_after(lines, i)))

    by_id = {m[0]: m for m in models}
    missing = [m for m in FIRST if m not in by_id]
    if missing:
        raise SystemExit(f"en FIRST pero no en el documento: {missing}")
    ordered = [by_id[m] for m in FIRST] + [m for m in models if m[0] not in FIRST]

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    index = ["# Prompts para Claude Design, en orden", "",
             "Generado por `tools/build_model_prompts.py` desde `assets/models/Prompts de modelos - Western.md`. "
             "No editar a mano: cambiar el documento y volver a correr el script.", "",
             "Cada archivo se pega entero en una conversación nueva de Claude Design. Al final, Claude Design "
             "te escribe la carpeta: copiala en la barra de direcciones del Explorador y guardá ahí el GLB.", "",
             "Si hay un `NNN_<Id>_concepto.txt`, va primero: se pega en un generador de imágenes y la imagen "
             "se adjunta en Claude Design junto con el prompt.", "",
             "| # | Id | Modelo | Concepto | Carpeta |", "|---|---|---|---|---|"]
    width = len(str(len(ordered)))
    for n, (model_id, name, letters, prompt, concept) in enumerate(ordered, 1):
        design = folder_for(model_id) / "01_design"
        design.mkdir(parents=True, exist_ok=True)
        save = "\n".join([
            "SAVE LOCATION — every time you deliver the file (the first version and every new version), "
            "end your reply with these two lines, copied exactly, each on its own line with nothing else on it:",
            f"Carpeta: {design}",
            f"Archivo: {model_id}.glb",
        ])
        text = "\n\n".join([blocks[letter] for letter in letters] + [prompt, save]) + "\n"
        num = str(n).zfill(max(3, width))
        (OUT / f"{num}_{model_id}.txt").write_text(text, encoding="utf-8", newline="\n")
        if concept:
            (OUT / f"{num}_{model_id}_concepto.txt").write_text(concept + "\n", encoding="utf-8", newline="\n")
        index.append(f"| {num} | `{model_id}` | {name} | {'sí' if concept else ''} | `{design}` |")
    (OUT / "_INDICE.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(ordered)} prompts en {OUT}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # la consola de Windows no es UTF-8
    sys.exit(main())

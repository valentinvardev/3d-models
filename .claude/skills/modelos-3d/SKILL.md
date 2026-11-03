---
name: modelos-3d
description: Modelos 3D low poly del juego de oleadas en Roblox — props del kit western (barriles, cajas, carretas, carteles), armas, piezas destructibles prefragmentadas, vehículos, enemigos y jefes — desde concepto hasta MeshPart en Studio. Usala para crear, exportar, importar o arreglar cualquier modelo o malla.
---

# Modelos 3D

**Antes:** `vendor/skills/REGLAS.md`, `vault/06 Producción/Pipeline y roles con IA.md` y `Estilo visual.md` (el GDD dice que los modelos salen de Claude Design exportados en OBJ, y que los personajes animados necesitan un rig aparte), y la nota del Chapter.

## Oficio que se toma de afuera

| Para | Leer | Origen |
| --- | --- | --- |
| Props de bordes duros low poly programados (armas, cajas, carretas) | `references/hard-surface-route.md`, `references/kiln-route.md`, `scripts/kiln_to_roblox.mjs` | `vendor/skills/syphodev-roblox-ai-skills/skills/roblox-3d-model/` |
| Pasar una malla a Studio: decimate, UV, bake, export, import | `scripts/mesh_pipeline.py`, `export_for_studio.py`, `references/studio_import.lua`, `references/traps.md` | ídem |
| Props simples en lote y pasto | `scripts/tier3_props.py`, `grass_clump.py` | ídem |
| Licencias de modelos de IA | `references/licences.md` | ídem |
| Modelos como código Luau sobre EditableMesh (opcional) | `README.md`, `BRIEF.md` | `vendor/skills/roclicks-skills/meshlab/` (con `MESHLAB_NOSTUD=1`, sin bevel) |
| Correr Blender por script: reglas de bpy (API de datos antes que operadores), `run_in_blender.py`, diferencias de API | `blender-core/SKILL.md`, `references/bpy-patterns.md`, `references/api-changes-5x.md` | `vendor/skills/el4cteo-blender-skills/skills/` |
| Revisar una malla antes de exportar: z-fighting, partes sueltas, normales, n-gons, escala | `blender-asset-qa/SKILL.md`, `scripts/qa_check.py --profile roblox` | ídem |
| Presupuesto: triángulos, materiales, draw calls | `blender-game-optimization/SKILL.md`, `scripts/mesh_stats.py --budget mobile` | ídem |
| Exportar a Studio y specs de Roblox (MeshPart, R15, accesorios, texturas) | `blender-export-pipelines/SKILL.md`, `references/roblox.md`, `scripts/export_asset.py --preset roblox` | ídem |
| Arreglar modelos a mano: bordes duros, segmentos de cilindros según tamaño en pantalla, topología | `blender-hardsurface-modeling/SKILL.md` | ídem |
| Recetas de punta a punta (prop, personaje) | `blender-workflow-recipes/SKILL.md` | ídem |

## Lo que acá es distinto

- **No** se usa la ruta orgánica de SyphoDev: sube los conceptos a un Space público de Hugging Face (Hi3DGen) y da mallas suaves de 6-10 mil caras, no low poly.
- **Kiln** es un paquete npm sin release, que se ejecuta con `npx`. Antes del primer uso: fijar la versión exacta, revisar el paquete y pedir OK.
- **Destructibles:** cada pieza del kit modular sale prefragmentada (los fragmentos son parte del modelo), con un presupuesto de partes que entre en `Environment.segmentBudget`.
- **Archivos fuente** (`.obj`, `.glb`, `.blend`, conceptos) en `assets/models/`. Ids de mesh subidos: a la ficha si dependen del mundo.
- **Blender 5.2.3 LTS** es el que se usa: `%LOCALAPPDATA%\Programs\Blender Foundation\Blender 5.2\blender.exe`. El 4.4 sigue en `C:\Program Files\Blender Foundation\Blender 4.4\` pero no se usa. Nunca con `--enable-autoexec` ni abriendo `.blend` ajenos sin revisar. Python es `py`.
- **Pack de Blender (el4cteo):** se corren solo los scripts revisados (tabla en `vendor/skills/README.md`), así: `py -I vendor/skills/el4cteo-blender-skills/skills/blender-core/scripts/run_in_blender.py --blend <archivo.blend> <script.py> -- <args>`. Elige solo el Blender más nuevo. Para ver un modelo: `blender-asset-qa/scripts/review_shots.py` deja una hoja de capturas en PNG que se abre con Read.
- **El pack trabaja en metros** (1 stud ≈ 0,28 m) **y nuestros prompts en studs** (1 unidad = 1 stud). Qué tamaño llega a Studio con `--preset roblox` se mide con la primera pieza; hasta entonces, no se exporta el lote.
- **Frente:** el pack modela con el frente hacia −Y de Blender, y su `roblox.md` dice que los cuerpos de avatar van hacia +Z en Roblox; la convención del proyecto es frente = −Z. Se resuelve midiendo en la galería, no leyendo.
- **Dos caminos para un modelo:** Claude Design (pegar el prompt, guardar el GLB en `01_design/`) o **la fábrica** (receta en Blender con `tools/blender/modelkit.py`; skill `fabrica-modelos`). Los dos terminan en `process_model.py` y en el visor (`tools/viewer/`). La fábrica dio mejor resultado en personajes porque el agente ve sus capturas y corrige.
- **Prompts para Claude Design:** `assets/models/western/_prompts/NNN_<Id>.txt`, generados con `py -I tools/build_model_prompts.py` desde `assets/models/Prompts de modelos - Western.md`. Si se cambia el documento, se vuelven a generar; nunca se editan los `.txt` a mano.
- **Personajes:** Claude Design arma bien la estructura R15 pero, sin dirección de arte, salen maniquíes. Van con imagen de concepto (`NNN_<Id>_concepto.txt`, primero al generador de imágenes y después adjunta en Claude Design), uno por conversación, y con el Bloque H si son muertos. Blender ajusta proporciones; el carácter no se arregla en Blender.
- **Procesar un modelo de Claude Design:** guardarlo en `assets/models/western/<carpeta>/<Id>/01_design/<Id>.glb` y correr `"%LOCALAPPDATA%\Programs\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P tools/blender/process_model.py -- <Id>`. Hace todos los pasos de abajo y deja `02_blend/`, `03_export/<Id>.glb` (para Import 3D, opción glTF), las hojas `review_*.png` (la primera vista es el frente) y `report.json` (triángulos contra el tope del prompt, medidas, revisión). Mirar siempre las hojas antes de pasar a Studio.
- **Lo que llega de Claude Design** (GLB de three.js): cada triángulo con sus propios vértices y triangulado con astillas largas. Limpieza en Blender: soldar (`bmesh.ops.remove_doubles`, 1e-4), unir caras coplanares del mismo material (`bmesh.ops.dissolve_limit`, 0,5°, `delimit={"MATERIAL"}`), re-triangular (`triangulate`, BEAUTY) y sombreado plano. En la caja bajó 1182 → 524 triángulos sin cambio visible. Lo aprendido de cada pieza va a "Aprendido con los pilotos" en `assets/models/Prompts de modelos - Western.md`.
- **Ejes al importar el GLB en Blender:** el frente del modelo (−Z en Roblox) queda hacia **+Y** de Blender. Las vistas `front` de `review_shots.py` miran desde −Y: el frente del modelo sale en la vista `back`.
- **Import en Studio (medido con la caja, 2026-10-28):** el importador acepta Roblox model, OBJ y glTF (no FBX), así que se exporta **GLB** (`export_asset.py --preset roblox_gltf`). Una unidad glTF = 1 stud. Los colores de material no llegan (todo gris) y cada material sale como MeshPart aparte: por eso se exporta con el **atlas de paleta** (`assets/models/western/_palette/`). El frente llega girado 180° (glTF usa +Z como frente): se gira el modelo 180° sobre la vertical en Blender antes de exportar.
- **Sin UVs:** con colores planos y un MeshPart por color, `qa_check.py --profile roblox` marca "no UV map" como error; en ese caso se corre con `--no-uv`. Con el atlas de paleta, las UVs existen y no hace falta.
- Medir escala y orientación con una pieza en Studio antes de exportar el resto (frente = −Z, medido, no supuesto).

## Cerrar

- [ ] Una pieza importada, medida (tamaño en studs, orientación, pivote) y vista en captura antes de hacer el lote.
- [ ] Exportada como `.rbxm` a `assets/gallery/` y revisada en el sandbox con `gallery`, al lado de `_ReferenciaJugador` (2 × 5 × 1 studs, el tamaño de un jugador). La galería gira cada pieza para que su frente (−Z) te mire: si muestra la espalda o el costado, el frente del modelo está mal.
- [ ] Cantidad de triángulos acorde al presupuesto y a celular.
- [ ] Fuente en `assets/models/`, id en la ficha, la nota enlaza el modelo.

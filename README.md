# 3d-models

Sistema para hacer modelos 3D low poly y animaciones R15 **por código** y llevarlos a Roblox, con las skills de Claude Code que lo manejan. Salió del juego co-op de oleadas *Dead Man's Rail* (Chapter 1, Western), donde hizo los personajes, enemigos, jefes, armas, props y el pueblo.

La idea central: un agente escribe la receta de cada modelo en Python (`bpy`), la construye en Blender sin interfaz, **mira sus propias capturas y mide**, corrige y repite. Las animaciones se escriben como datos (poses por articulación) y se revisan con números antes de subirlas.

## Qué hay

| Carpeta | Qué es |
| --- | --- |
| `.claude/skills/fabrica-modelos/` | La fábrica: elegir de la cola, leer el prompt, escribir la receta, construir, revisar con números y capturas, cerrar. Con `references/construccion.md` y `revision.md` |
| `.claude/skills/modelos-3d/` | El rol de modelos: los dos caminos (Claude Design o la fábrica), limpieza, atlas de paleta, import en Studio |
| `.claude/skills/animacion/` | El rol de animación: spec de poses, construir, revisar, subir |
| `tools/blender/` | `modelkit.py` (la API de las recetas), `humanoid.py`, `build_model.py`, `process_model.py` (limpieza, revisión, atlas, GLB para Studio), `review_model.py`, `layout_preview.py`, `dirt_texture.py` |
| `tools/roblox/` | Rig R15 de piezas rígidas, animaciones (`anim_r15.luau`, `anim_build.luau`, `anim_ik.py`, `anim_preview.py`, `anim_sheet.py`), armas en la mano (`held.py`), armado de `.rbxm` y subida con Open Cloud (`opencloud.py`). **`tools/roblox/README.md` tiene la cadena entera y lo aprendido** |
| `tools/viewer/` | Visor 3D en el navegador: modelo final u original, medidas, triángulos contra el tope, piezas, pivotes, marcadores, jugador de referencia, capturas y animaciones. Se actualiza solo cada 2 s |
| `tools/model_queue.py`, `tools/build_model_prompts.py` | La cola de la fábrica (estados `pendiente`, `construido`, `rehacer`, `aprobado`…) y el generador de prompts numerados |
| `assets/models/Prompts de modelos - Western.md` | La especificación de todos los modelos del Western y "Aprendido con los pilotos" |
| `assets/models/western/**/01_design/*.build.py` | Las 139 recetas del Western: sirven de referencia de técnica y de estilo |
| `assets/models/western/_palette/`, `_estado.json` | El atlas de paleta (colores planos en una textura) y el estado de la cola |
| `assets/models/rbx/README.md` | El contrato del rig R15 y de las armas al llegar a Roblox |
| `assets/animation/western/` | Los specs de los clips (`<Clip>.json`) y los rigs (`*.rig.json`) |
| `vendor/skills/el4cteo-blender-skills/` | Los tres scripts de ese pack que usan `process_model` y `review_model` (QA, capturas y export) y su helper `_bpyx.py`, con su licencia MIT |
| `vendor/skills/REGLAS.md` | Las reglas que mandan sobre cualquier skill externa (nada de `--enable-autoexec`, instaladores ni `~/.claude`) |

## Lo que no está

- **Lo generado:** GLB, `.blend`, capturas `review_*.png`, `report.json`, los `.rbxm` y `.poses.json` de las animaciones, los prompts numerados (`_prompts/`) y el índice del visor (`models.json`). Todo sale de nuevo de las recetas y los specs (ver `.gitignore`).
- **El resto de los packs externos** de `vendor/skills/`: las skills nombran archivos de ahí para leer (técnica), pero no se redistribuyen. Están en la tabla de créditos.
- **El vault y el `CLAUDE.md` del juego:** las skills nombran notas del juego (pilares, decisiones como D022) y su `CLAUDE.md`. Acá quedan como referencia; lo que hace falta para construir está en las skills, en `tools/roblox/README.md` y en el documento de prompts.

## Requisitos

- **Blender 5.2 LTS** (en Windows: `%LOCALAPPDATA%\Programs\Blender Foundation\Blender 5.2\blender.exe`). Siempre en segundo plano y **nunca con `--enable-autoexec`**.
- **Python 3** (`py` en Windows, siempre con `-I`). `review_shots.py` usa numpy (viene con Blender).
- **Lune**, para construir rigs y animaciones (`.rbxm`).
- Una API key de Open Cloud solo para subir a Roblox: se lee de `ROBLOX_API_KEY` o de `~/.roblox/open-cloud-key.txt`, nunca del repo.

## Cómo se usa

Todo desde la raíz del repo.

```bash
# Primero: los prompts numerados y su índice, desde el documento de prompts
# (la cola los necesita; llevan rutas de tu máquina, por eso no se versionan)
py -I tools/build_model_prompts.py

# La cola: qué falta, qué sigue
py -I tools/model_queue.py list
py -I tools/model_queue.py next

# Construir un modelo desde su receta
"$LOCALAPPDATA/Programs/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 \
  -P tools/blender/build_model.py -- <Id>

# Procesar un GLB de Claude Design (guardado en 01_design/<Id>.glb)
"$LOCALAPPDATA/Programs/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 \
  -P tools/blender/process_model.py -- <Id>

# Visor
py -I tools/viewer/build_index.py
py -m http.server 8765 --bind 127.0.0.1
# → http://127.0.0.1:8765/tools/viewer/?id=<Id>

# Animaciones
lune run tools/roblox/anim_build.luau assets/animation/western/<rig>/*.json
py -I tools/roblox/anim_preview.py <rig.json> <Clip>.poses.json
# → http://127.0.0.1:8765/tools/viewer/?id=<Id>&anim=<Clip>&sheet=8

# Subir a Roblox
py -I tools/roblox/opencloud.py animation <Clip>.rbxm <Clip>
```

Convención de coordenadas en las recetas: studs, Y arriba, frente en −Z, derecha en +X (la de Roblox).

## Procedencia

Copiado de la rama `models-prompting-western` del repo del juego (sobre el commit `2464544`, con los cambios en disco hasta el 2026-10-30).

## Créditos y licencias

| Pack | Qué se usa | Licencia |
| --- | --- | --- |
| [EL4CTEO/blender-skills](https://github.com/EL4CTEO/blender-skills) | Tres scripts y su helper, incluidos en `vendor/` (QA, capturas, export) | MIT (`vendor/skills/el4cteo-blender-skills/LICENSE`) |
| [SyphoDev-yt/roblox-ai-skills](https://github.com/SyphoDev-yt/roblox-ai-skills), del canal de YouTube de SyphoDev | La convención de ángulos de las articulaciones y recetas de poses (no se incluye código) | Licencia propia gratuita: pide nombrar al canal de YouTube de SyphoDev como fuente |
| [hildlabs/openrig-studio](https://github.com/hildlabs/openrig-studio) | Cómo interpola Roblox los keyframes y los umbrales de revisión (no se incluye código) | MIT |
| [majidmanzarpour/blender-game-skills](https://github.com/majidmanzarpour/blender-game-skills) | El método de la fábrica: fases con capturas comparadas, silueta antes que detalle | MIT |
| [Guilherme-M-Mateus/keyframe-coach](https://github.com/Guilherme-M-Mateus/keyframe-coach) | Cuadrúpedos: fases y tiempos de apoyo | MIT |
| [zriptic/roclicks-skills](https://github.com/zriptic/roclicks-skills) | Referencia de lecciones de Roblox | MIT |

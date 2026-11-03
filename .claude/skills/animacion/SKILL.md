---
name: animacion
description: Animaciones del juego de oleadas en Roblox — recargas, finishers y ejecuciones cuerpo a cuerpo, culatazo, inspeccionar, ataques con anticipación de enemigos y jefes, poses de cinemáticas con avatares R15 — desde un spec de poses hasta la animación en Studio. Usala para crear, revisar o arreglar animaciones, o para preparar un encargo a un animador externo.
---

# Animación

**Antes:** `vendor/skills/REGLAS.md`, [[Pilar - Animaciones de foco]] y [[Pilar - Historia corta y saltable]] (cinemáticas con los avatares de los jugadores, R15, proporciones extremas). El GDD dice que la animación es el rol más probable de tercerizar: si el pedido es para afuera, el entregable es un brief, no la animación.

## Oficio que se toma de afuera

| Para | Leer | Origen |
| --- | --- | --- |
| Spec de poses FK → Blender sin interfaz → contact sheet / GIF → KeyframeSequence | `SKILL.md`, `references/pose-recipes.md`, `references/traps.md`, los `example-*.json` | `vendor/skills/syphodev-roblox-ai-skills/skills/roblox-animation/` |
| Render y conversión | `scripts/anim_render.py`, `to_roblox.py`, `upload_animation.py` | ídem |
| Cómo interpola Roblox, medido en Studio: easing por tramo, `CubicV2` sin invertir, nlerp contra vectores de rotación. Corrige trampas de SyphoDev | `docs/how-it-works.md` (tabla "Matching Roblox playback"), `prompts/system.md`, `src/core/rig.js` (límites de las 15 articulaciones) | `vendor/skills/hildlabs-openrig-studio/` |
| Cuadrúpedos (caballo, toro): fases, tiempo apoyado, "dos pelotas que rebotan". Presupuestos de cuadros | `skills/keyframe-coach/references/legs.md`, `principles.md` | `vendor/skills/guilherme-m-mateus-keyframe-coach/` |

## Cómo se hace acá (personajes de la fábrica)

Los personajes son R15 de **piezas rígidas** (el origen de cada pieza en su articulación). Las animaciones se escriben como **datos** y se revisan con números y en el visor: `tools/roblox/README.md` tiene la cadena entera y lo aprendido. Decisión: [[D022 - Rig y animaciones de personajes por código]].

- **Spec:** `assets/animation/western/<rig>/<Clip>.json`.
- **Construir:** `lune run tools/roblox/anim_build.luau`, que escribe `.rbxm` y poses.
- **Revisar con números:** `py -I tools/roblox/anim_preview.py`, que mide piso, pie apoyado, loop y giros, y deja el GLB del visor.
- **Revisar a ojo:** la hoja de contacto en `tools/viewer/?id=<Id>&anim=<Clip>&sheet=8`.
- **Subir:** `py -I tools/roblox/opencloud.py animation`.
- **Rig:** `tools/roblox/rig_build.luau`, que arma el `.rbxm` del contrato de `assets/models/rbx/README.md`.
- **Lo que se reutiliza:** de SyphoDev, solo la convención de ángulos y las recetas de poses. Su `anim_render.py` pide un `.blend` bajado y `--enable-autoexec`, y acá no se usa.

## Lo que acá es distinto

- **Nunca `--enable-autoexec`.** La skill lo usa en cada comando de Blender sobre un rig bajado de internet, y eso ejecuta cualquier Python que traiga el `.blend`. Solo se usa un rig propio o uno revisado línea por línea. Si un paso no funciona sin autoexec, frená y preguntá.
- **R15 siempre**, probado con avatares de proporciones extremas (muy alto, muy bajo, accesorios grandes).
- **Dos perspectivas:** lo que el jugador ve de sí mismo (recarga, inspeccionar, finishers) se revisa en primera y en tercera persona ([[D011 - Primera y tercera persona con una tecla]]). Si hay viewmodel en primera persona, las animaciones de armas se duplican: confirmar antes de animar.
- **Prioridad del GDD:** recarga y ejecuciones cuerpo a cuerpo primero; inspeccionar después.
- **Anticipación:** todo ataque enemigo tiene una pose de telegraph que dura al menos `telegraphSeconds`.
- Specs, `.blend` y renders en `assets/animation/`. Ids subidos a la ficha.
- Blender 4.4 está en `C:\Program Files\Blender Foundation\Blender 4.4\blender.exe` y el 5.2 en `%LOCALAPPDATA%\Programs\Blender Foundation\Blender 5.2\blender.exe`; ffmpeg está instalado; Python es `py -I`; Lune corre la conversión.
- **Subir a Roblox** lo hace Claude (decisión de Valentin del 2026-10-28) con la API key que guarda él en `~/.roblox/open-cloud-key.txt`. Claude nunca la escribe ni la imprime.

## Cerrar

- [ ] Contact sheet o GIF revisado antes de subir.
- [ ] Probada en Studio en Play, en las dos perspectivas si es del jugador.
- [ ] Si es un encargo: brief con referencias, duración, eventos (frame del impacto, de la anticipación) y rig.

---
name: fabrica-modelos
description: Fábrica de modelos 3D del Western — construir, verificar y revisar los modelos del Chapter 1 con la herramienta del repo (recetas en Blender con modelkit), uno por uno desde la cola, hasta dejarlos listos para Studio. Usala cuando Valentin pida "corré la fábrica", "construí el próximo modelo", "rehacé X", "seguí con los modelos", o cuando haya que construir, mejorar o revisar cualquier modelo del Western por código, aunque sea uno solo. Pensada para correr sola en un workspace aparte y retomar donde quedó.
---

# Fábrica de modelos

Construye los modelos del Western **por código** (recetas `bpy` con `tools/blender/modelkit.py`), los pasa por el mismo proceso que lo que sale de Claude Design (limpieza, revisión, atlas de paleta, GLB para Studio) y los deja para que Valentin los apruebe en el visor. Probado con el caminante A (2026-10-28): salió mejor que la versión de Claude Design porque acá **el agente ve sus capturas y corrige con números**.

Lo que manda sobre esta skill: `CLAUDE.md`, `vendor/skills/REGLAS.md` y la skill `modelos-3d`. Las reglas de diseño de cada modelo están en su prompt; esta skill dice **cómo** construirlo.

## Antes de arrancar (una vez por sesión)

1. Blender 5.2: `"%LOCALAPPDATA%\Programs\Blender Foundation\Blender 5.2\blender.exe"` (en Git Bash: `"$LOCALAPPDATA/Programs/Blender Foundation/Blender 5.2/blender.exe"`). Nunca con `--enable-autoexec`. Python es `py`, siempre con `-I`.
2. `py -I tools/model_queue.py list`: cuántos quedan y qué está para rehacer, fallado o bloqueado.
3. Si cambió `assets/models/Prompts de modelos - Western.md` desde la última corrida: `py -I tools/build_model_prompts.py` (regenera los prompts numerados).
4. Leé `references/construccion.md` (cómo construir bien) y `references/revision.md` (cuándo un modelo está terminado). Son la mitad del trabajo: no los saltees.

## El ciclo, por modelo

1. **Elegir.** `py -I tools/model_queue.py next` da el id, el archivo del prompt y las notas. Si el estado es `rehacer`, las notas de Valentin son lo primero que se resuelve.
2. **Leer.**
   - El prompt (`assets/models/western/_prompts/NNN_<Id>.txt`): es la especificación. Medidas, piezas, nombres, orígenes, colores y tope de triángulos salen de ahí.
   - La imagen de concepto si hay (`01_design/concept.*`): abrila con Read. Es la dirección de arte.
   - "Aprendido con los pilotos" del documento de prompts.
   - Una receta terminada del mismo tipo como referencia de estilo y de técnica. Hoy: `enemies/WST_Enemy_Walker_A/01_design/WST_Enemy_Walker_A.build.py` para humanoides.
3. **Brief.** Arriba de la receta, en el docstring: la silueta que se tiene que leer a 40 studs (3-5 rasgos), las medidas que vas a usar, las piezas con su origen, qué se talla y qué se pinta, y qué es **inferido** (lo que el prompt no dice).
4. **Receta.** `assets/models/western/<carpeta>/<Id>/01_design/<Id>.build.py` con `def build(mk):`. Solo la API de `modelkit` (docstring de `tools/blender/modelkit.py`). Coordenadas del juego: studs, Y arriba, frente en −Z, derecha en +X.
5. **Construir.**
   ```
   "$LOCALAPPDATA/Programs/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 -P tools/blender/build_model.py -- <Id>
   ```
   Deja `01_design/<Id>.glb`, `02_blend/`, `03_export/<Id>.glb`, `review_*.png` y `report.json`, y actualiza el índice del visor.
6. **Revisar** siguiendo `references/revision.md`: los números de `report.json`, las capturas (`review_material.png` y `review_random.png`) y las de `tools/blender/review_model.py -- <Id> --focus <piezas>`, que deja el primer plano y el modelo chiquito a distancia de juego. Escribí cada problema como **medida** ("la cabeza 12 % chica", "el brazo 0,06 afuera del torso"), corregí la receta y volvé al paso 5.
7. **Cerrar.**
   - **Si pasa toda la revisión:** `py -I tools/model_queue.py set <Id> construido "<tris>/<tope>, <n> vueltas, inferido: ..."`.
   - **Si después de 6 vueltas no converge:** `set <Id> falló "<qué no se pudo y por qué, con números>"`.
   - Nunca marques `aprobado`: eso lo hace Valentin en el visor.
   - Anotá en la sección "Revisión" del docstring de la receta lo que quedó aceptado y por qué.
8. **Seguir** con el próximo.

## Puntos de control

- **Cada 5 modelos construidos:** agregá un bloque a `assets/models/western/_revision.md` con fecha, ids, triángulos contra el tope, lo inferido, lo dudoso y los links del visor (`http://127.0.0.1:8765/tools/viewer/?id=<Id>`). Valentin revisa en tanda desde ahí. Después seguí, salvo que te hayan pedido frenar.
- **Si falta una decisión de diseño** (el prompt contradice al vault, una medida no está, algo se puede hacer de dos formas que cambian el juego): no inventes. `set <Id> bloqueado "<la pregunta concreta, con las opciones>"`, sumá la pregunta al "Abierto" del documento de prompts y seguí con el próximo.
- **Calidad antes que tope** (Valentin, 2026-10-28): el tope de triángulos del prompt es una referencia. Si el modelo queda mejor pasándolo, se pasa, y se anota cuánto y por qué en la receta y en la nota de la cola. Nunca se recorta detalle visible para entrar. Límite técnico: menos de 10 000 triángulos por pieza.
- **Armas:** sin techo de calidad mientras sigan siendo low poly. Referencia: el lenguaje de las armas estilizadas de juegos conocidos (proporciones exageradas, chanflanes que agarran luz, materiales bien separados, mecánica legible), sin copiar ningún modelo.
- **Si una herramienta falla dos veces seguidas** por la misma causa: frená y reportá. No hay que tocar `modelkit` ni `process_model` para que un modelo pase. Si la herramienta tiene un bug real, arreglalo con cuidado, verificá con el caminante A y la caja que siguen dando lo mismo, y anotalo en el reporte.

## Para mirar los modelos (Valentin o vos)

```
py -m http.server 8765 --bind 127.0.0.1        (desde la raíz del repo)
http://127.0.0.1:8765/tools/viewer/?id=<Id>
```

El visor muestra el GLB final (con el atlas) o el original, medidas, triángulos contra el tope, revisión, piezas, pivotes, marcadores, jugador de referencia, capturas y animaciones (las del GLB y las de `western/_animations/` que apunten a piezas con el mismo nombre).

## Reglas duras

- No se toca `src/`, ni el vault (salvo el "Abierto" del documento de prompts y "Aprendido con los pilotos"), ni los GLB de Claude Design (`build_model` los guarda como `<Id>.claude-design.glb`, nunca los pisa).
- Solo se corren scripts revisados del vendor (tabla en `vendor/skills/README.md`) y las herramientas de `tools/`.
- No se sube nada a Roblox ni se toca Studio desde esta skill. Importar en Studio es el paso siguiente y lo decide Valentin.
- No se commitea salvo que Valentin lo pida en esa sesión. El trabajo queda en disco y la cola (`_estado.json`) permite retomar.
- Respuestas y notas en castellano rioplatense; identificadores en inglés.

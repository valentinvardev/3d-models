# Prompts de modelos 3D — Western (Dead Man's Rail)

> Un prompt por cada modelo 3D que pide el Chapter 1, sacados del vault (`vault/04 Chapters/Chapter 1 - Dead Man's Rail/`, `Estilo visual.md`, `Pipeline y roles con IA.md`, sistemas). Cada prompt dice forma, medidas en studs, piezas separadas, materiales con hex, presupuesto de triángulos y lo que el modelo tiene que permitir en el juego (romperse, animarse, recolorearse).
>
> Los prompts están en inglés porque los generadores 3D responden mejor así; lo de alrededor, en castellano.

## Cómo usar este documento

1. **Una conversación por modelo** (o por familia del kit, cuando el prompt lo dice). El contexto de un rifle contamina la caja que pidas después.
2. **Pegar en este orden:** Bloque A (estilo, siempre) + el bloque de su tipo (B a G, lo indica cada modelo) + el prompt del modelo. **Ya están armados** en `western/_prompts/NNN_<Id>.txt`, numerados en orden de producción y con la carpeta donde guardar el GLB al final (índice en `_prompts/_INDICE.md`). Se generan desde este documento con `py -I tools/build_model_prompts.py`: si cambiás algo acá, volvé a correrlo.
3. **Iterar con palabras, no volver a generar:** "bajá la culata 0,2 studs", "el sombrero más ancho". Las variantes se piden en el mismo hilo.
4. **Exportar en GLB** si Claude Design lo ofrece (un solo archivo que guarda nombres de piezas, materiales y pivotes); si no, **OBJ + MTL** (los dos archivos: los colores viven en el `.mtl`). Guardarlo sin tocar en `assets/models/western/<carpeta>/<Id>/01_design/<Id>.glb`, con la carpeta según el prefijo del id:

   | Prefijo del id | Carpeta |
   |---|---|
   | `WST_Weapon_`, `WST_Item_` | `weapons` |
   | `WST_Pickup_` | `pickups` |
   | `WST_Prop_` | `props` |
   | `WST_NPC_` | `npcs` |
   | `WST_Enemy_`, `WST_Overlay_` | `enemies` |
   | `WST_Boss_` | `bosses` |
   | `WST_Mount_`, `WST_Vehicle_`, `WST_Train_` | `transport` |
   | `WST_Kit_` | `kit` |
   | `WST_DG_`, `WST_Canyon_`, `WST_Bg_`, `WST_RM_`, `WST_Mine_`, `WST_SB_`, `WST_Track_`, `WST_HC_`, `WST_CH_` | `sets` |

   `01_design/` es el original: nunca se edita. Blender trabaja en `02_blend/` y exporta a `03_export/`.
5. **Antes del lote, la pieza de medición:** `WST_Prop_Crate`. Importarla, verla en la galería del sandbox al lado de `_ReferenciaJugador` (2 × 5 × 1 studs), medir tamaño, frente (−Z) y pivote, y **anotar acá abajo, en "Medido"**, el factor de escala real y hacia dónde quedó el frente. Recién después, el resto.
6. Al subir un mesh, su id va a la ficha del Western si depende del mundo.

### Medido

| Fecha | Pieza | Escala de import real | Frente | Pivote | Notas |
|---|---|---|---|---|---|
| 2026-10-28 | `WST_Prop_Crate` (GLB de `03_export`, colores en materiales) | **1 unidad glTF = 1 stud** (3,000 × 3,000 × 3,000 exactos) | **Llegó girado 180°: frente en +Z.** El importador toma +Z del glTF como frente (convención glTF) y lo lleva al −Z de Roblox. Arreglo: girar 180° sobre la vertical en Blender antes de exportar | En la base, al centro (`WorldPivot` en el piso de la caja) | El importador ofrece Roblox model, OBJ y glTF (no FBX). Envuelve todo en un modelo `Scene`, cada pieza es un Model y **cada material un MeshPart aparte** (`Mesh_0`, `Mesh_02`…): 14 MeshParts. **Los colores no llegan:** todo en gris `Plastic` (`a3a2a5`) y el nombre del material se pierde. Las partes llegan sin anclar ni soldar |
| 2026-10-28 | `WST_Prop_Crate` (GLB con atlas de paleta y girado 180° en Blender) | 1:1 (3,000 × 3,000 × 3,000, apoyada en y = 0) | **−Z, correcto** (`frag02` en z = −1,30; izquierda `frag04` en x = −1,30) | El origen de cada nodo glTF queda como `WorldPivot` del Model que envuelve cada pieza; cada MeshPart tiene el pivote en su centro | **Funciona:** 6 MeshParts (una por pieza), colores bien vía `TextureID`. El importador sube la textura de paleta por su cuenta en cada import (`rbxassetid://109907631550747` esta vez): con muchos modelos conviene apuntarlos todos a un solo asset. Siguen sin anclar ni soldar |

### Aprendido con los pilotos

**Caja (`WST_Prop_Crate`, 2026-10-27):**

- **Claude Design exporta GLB con three.js:** nombres de piezas y materiales exactos (con su hex), colores bien convertidos, medidas exactas en studs.
- **Llega en "sopa de triángulos":** cada triángulo con sus propios vértices, por el sombreado plano. Blender suelda vértices y quedan piezas cerradas; no hace falta pedirlo en el prompt.
- **Triangula con astillas largas.** Blender une las caras coplanares del mismo material y re-triangula: 1182 → 524 triángulos (−56 %) sin cambio visible.
- **El tope de triángulos no estaba dentro del texto pegado.** Ahora cada prompt arranca con `MODEL` y `TRIANGLE BUDGET`, y el Bloque A dice qué detalle se saca primero si no entra.
- **Las ranuras hundidas entre tablas** cuestan triángulos y desaparecen con luz plana (Claude Design tuvo que oscurecerles el fondo). Ahora se piden líneas finas coplanares en madera oscura.
- **Claude Design no ve su propio render** (la captura le sale en blanco). Para iterar, subile la hoja de capturas que genera Blender (`review_shots.py`).
- **La regla del 45 %** solo se cumple por volumen cuando cada pieza es una cara entera; quedó aclarado en el Bloque C.
- **Ejes:** al importar el GLB en Blender, el frente (−Z en Roblox) queda hacia +Y de Blender, al revés de la convención del pack de Blender (−Y). Las exportaciones lo vuelven a −Z; falta confirmarlo en Studio.
- **El tope de la caja era irreal:** 250 no alcanza para 6 piezas cerradas con marco; quedó en 350.
- **En Studio (medido):** se exporta GLB (el importador no ofrece FBX). Los colores de material no llegan, así que cada modelo sale con el **atlas de paleta** (una textura de 512 × 512 con un cuadrito por color, en `western/_palette/`): pasó de 14 MeshParts grises a 6 con color. El frente llega girado 180° (glTF usa +Z como frente): se gira el modelo en Blender antes de exportar, y los prompts siguen en la convención de Roblox (frente = −Z).
- **Pivotes:** el origen de cada objeto en Blender llega como `WorldPivot` del Model que envuelve esa pieza. Para las piezas móviles (martillo, palanca, puertas) alcanza con poner el origen del objeto en su eje de giro antes de exportar.

**Revólver (`WST_Weapon_Revolver`, 2026-10-28):**

- Claude Design respetó los pivotes: cada pieza móvil llegó con el origen en su eje (cilindro en su centro, martillo en la base, gatillo arriba).
- Faltaban las piezas de la recarga (tapa y varilla pegadas al armazón): ahora el Bloque F pide como pieza aparte todo lo que se mueve al recargar o inspeccionar, y hay un modelo de balas sueltas (`WST_Item_Rounds`).
- Traía 14 bordes con caras invertidas: el script recalcula las normales.

**Caminantes (`WST_Enemy_Walker`, 2026-10-28):**

- Estructura perfecta: las 15 piezas R15 con sus nombres y el origen en cada articulación, a las alturas pedidas.
- **Aspecto de maniquí:** rectos, limpios, cabeza chica, cara plana. Agrandar cabeza y manos y bajar la cabeza en Blender mejoró poco: el carácter tiene que venir del modelado.
- **Ropa coplanar:** chaleco sobre camisa y chaparreras sobre pantalón en el mismo plano (10 zonas que titilan).
- Cambios: proporciones estilizadas en el Bloque D (cabeza 1/5, manos grandes, actitud modelada en torso y cabeza), capas de ropa separadas 0,03, Bloque H con la dirección de "muerto", un caminante por conversación y una **imagen de concepto** como referencia.

**Caminante A por la fábrica (`WST_Enemy_Walker_A`, 2026-10-28):**

- Construido por código (`01_design/WST_Enemy_Walker_A.build.py`, `tools/blender/modelkit.py`) en 6 vueltas mirando las capturas: se lee como zombie (cabeza caída, boca abierta, cuencas, costillas, daño) donde la versión de Claude Design era un maniquí.
- **Calcomanías:** pegar cajitas de color encima de la superficie se ve como superposición. Ahora los huecos se tallan (`carve`: cuencas, boca, rotura del pecho, mordida que arranca un pedazo) y el color se pinta en las caras (`paint`); ojos y dientes van adentro como detalle.
- **Booleanas:** necesitan `use_self` (sin él se comen el volumen) y suben los triángulos un 30 %: el tope de los caminantes pasó de 1500 a 1800 (1766 en el A).
- **Pintar caras grandes** tiñe la cara entera: mejor la forma (mejillas hundidas con el cráneo) o cortar antes.
- La skill de la fábrica (`.claude/skills/fabrica-modelos/`) junta el método y la revisión.

## Supuestos de los prompts (propuestas, no están decididas en el vault)

El vault deja abiertos varios puntos que un prompt hiperespecífico necesita fijar. Los prompts usan estas propuestas; si se cambia una, se cambia el bloque común y listo.

| Tema | Qué asumen los prompts | Dónde está abierto |
|---|---|---|
| Paleta | La tabla de abajo (atardecer: ocres, rojos, turquesa; plata viva azul frío) | `Estilo visual.md` → "¿Valores exactos de la paleta?" |
| Texturas o colores planos | **Colores planos**, un material por color, con el hex en el nombre del material (`wood_mid_7E5A3A`). Sin texturas ni UVs | `Estilo visual.md` → "¿Texturas o colores planos?" |
| "Contornos simples" | Siluetas limpias y bordes duros, caras planas; sin outlines ni bisel | `Estilo visual.md` |
| Proporciones de personajes | Humanoides para **rig R15 segmentado** (15 piezas rígidas, sin skinning), estilizado sin ser caricatura, compatible con las animaciones R15 de los jugadores | `Estilo visual.md`, `Pipeline y roles con IA.md` → "¿quién hace el rig?" |
| Escala | 1 unidad = 1 stud. Humano adulto = 5–5,4 studs. Vehículos y edificios a ≈ 2,8 studs por metro real, comprimidos donde el juego lo pide | — (medir con la pieza de medición) |
| Presupuesto de triángulos | Tabla de abajo, pensada para celular. Tope duro de Roblox: 20 000 por MeshPart; techo de trabajo: < 10 000 | `Estilo visual.md` → "¿Números del presupuesto?" |
| Fragmentos de los destructibles | Máximo 8 por pieza; el modelo *es* sus fragmentos | `Set dressing del Western.md` → presupuesto sin números |
| Texto en carteles | **Nunca en la geometría.** Tablero liso; el texto va como Decal o SurfaceGui en Studio (así cada pueblo cambia nombres) | — |
| Primera persona | No se modela viewmodel todavía: el mismo modelo sirve para tercera persona y para el piso | `D011` → "¿hay viewmodel?" |

### Cómo llega el color a Studio (decisión pendiente)

Los prompts piden **materiales nombrados con su hex**, que sirve para los dos caminos:

- **A. Un MeshPart por color:** se separa cada material en su propio MeshPart y se le pone el `Color` leído del nombre. Simple, pero multiplica partes (un enemigo de 15 piezas × 3 colores = 45 partes; con 45 enemigos vivos, ~2000 partes).
- **B. Atlas de paleta (recomendado):** un script de Blender colapsa las UVs de cada material sobre su cuadrito de color en una textura de paleta compartida (`WST_Palette.png`, 256 × 256) y une todo en un mesh por pieza. Una sola textura para todo el Chapter, menos partes, mejor en celular. Falta escribir ese script (`tools/`).

## Paleta propuesta

Los prompts solo pueden usar estos tokens. Material de Studio sugerido: `SmoothPlastic`, salvo donde se indica.

| Token | Hex | Uso |
|---|---|---|
| `sand` | `D9A86C` | Arena, polvo, adobe |
| `ochre` | `C4893F` | Roca clara, estratos, cuero claro |
| `redrock` | `A8452E` | Roca roja de cañón y mesas |
| `redrock_dark` | `6E2A1F` | Sombra de roca, estrato oscuro |
| `stone_grey` | `8C8273` | Piedra de cimientos, lápidas, cárcel |
| `wood_light` | `A7804F` | Madera nueva o al sol |
| `wood_mid` | `7E5A3A` | Madera estándar |
| `wood_dark` | `4E3524` | Vigas, molduras, madera vieja |
| `wood_charred` | `2B211C` | Madera quemada (variantes de incendio) |
| `paint_red` | `9C3B2E` | Pintura roja gastada (granero, fachadas) |
| `paint_teal` | `4F8C8A` | Pintura turquesa gastada |
| `paint_mustard` | `C9A23F` | Pintura mostaza gastada |
| `paint_cream` | `E3D6BC` | Pintura crema, papel, etiquetas |
| `paint_slate` | `6E7F8C` | Pintura gris azulada, enlozado |
| `iron` | `3B3A3A` | Hierro negro, aros, bisagras, rieles |
| `rust` | `7B4A2E` | Hierro oxidado |
| `brass` | `B8893A` | Bronce, latón, casquillos |
| `gunmetal` | `5A5E63` | Acero de armas (Studio: `Metal`) |
| `steel_light` | `A3A7AB` | Acero pulido, niquelado (Studio: `Metal`) |
| `leather` | `6B3F24` | Cuero |
| `leather_dark` | `3F2516` | Cuero oscuro, botas |
| `rope` | `C2A36B` | Soga, cuerda |
| `canvas` | `CDBB97` | Lona, vendas, bolsas |
| `cloth_red` | `8E2A22` | Pañuelos, camisas rojas |
| `cloth_black` | `1F1C1B` | Levitas, sombreros negros |
| `cloth_blue` | `3E5468` | Jean, overoles |
| `cloth_white` | `D8D0BE` | Camisas blancas sucias |
| `cloth_brown` | `6A4A32` | Chalecos, sacos, sombreros marrones |
| `skin_a` | `E0B08A` | Piel viva clara |
| `skin_b` | `B07850` | Piel viva media |
| `skin_c` | `6E4630` | Piel viva oscura |
| `hair_grey` | `A8A39A` | Pelo y barba canosos |
| `hair_dark` | `2E241D` | Pelo oscuro |
| `hair_red` | `8A3A1E` | Pelo pelirrojo (Doyle) |
| `skin_dead` | `9AA08C` | Piel de muerto, gris verdosa |
| `skin_dead_dark` | `6E7363` | Sombras y moretones de muerto |
| `blood_dry` | `5A1E18` | Sangre seca |
| `bone` | `E6DCC3` | Hueso, marfil, cráneos |
| `hide_brown` | `6A4430` | Pelaje de caballo bayo, toro |
| `hide_black` | `2A2220` | Pelaje negro |
| `hide_white` | `D9D0C0` | Pelaje blanco, manchas |
| `feather_black` | `2A2626` | Plumas de buitre |
| `vulture_skin` | `B5554A` | Cabeza pelada del buitre |
| `hay` | `D8B65A` | Fardos, paja |
| `cactus` | `7A9A5B` | Cactus, plantas secas |
| `coal` | `1C1A19` | Carbón, hollín |
| `warning_red` | `D2301F` | Pintura de peligro (barriles explosivos) |
| `dynamite_red` | `B3261E` | Papel de la dinamita |
| `glass` | `9FC7C9` | Vidrio de ventanas (Studio: `Glass`) |
| `glass_amber` | `8A5A22` | Botellas de whisky (Studio: `Glass`) |
| `glass_green` | `3F6B4A` | Botellas de tónico (Studio: `Glass`) |
| `water` | `5E8F96` | Superficie de agua quieta (Studio: `Glass`) |
| `lamp_glow` | `FFC46B` | Llama y vidrio encendido de faroles (Studio: `Neon`) |
| `silver_neon` | `7FE6FF` | Plata viva: vetas que laten (Studio: `Neon`, brillo por script) |
| `silver_crust` | `B9C3CC` | Plata viva: costras y placas (Studio: `Metal`) |

## Presupuesto de triángulos propuesto

| Tipo | Tris | Referencia |
|---|---|---|
| Pickups e ítems chicos | 40–200 | Esquirlas, munición, vendas |
| Armas de mano | 300–900 | Revólver, rifles |
| Props chicos | 50–300 | Cactus, lápidas, cajas |
| Props medianos | 300–1 200 | Carreta, bebedero, caja fuerte |
| Piezas del kit (todos sus fragmentos) | 150–600 | Pared, porche, techo |
| Piezas únicas grandes | 1 500–6 000, en objetos de ≤ 5 000 | Granero, locomotora, iglesia |
| Enemigos humanoides | 1 200–2 000 | Hay hasta 45 vivos (`Scaling.maxAliveEnemies`) |
| Jefes | 3 000–5 000 | El Predicador en su forma final: 6 000 |
| Criaturas | 400–2 200 | Buitre 400, caballo 1 800, toro 2 200 |

Cuenta de destructibles: con 8 fragmentos por pieza y `Environment.segmentBudget.maxDestructibles = 60`, un tramo suma como mucho 480 partes de destructibles activos, dentro de `maxParts = 5000`. Los escombros sueltos los limita `Environment.maxActiveDebris = 150`.

---

## Bloques comunes

Copiar tal cual. El bloque A va siempre; después, el del tipo de modelo.

### Bloque A — Estilo (todos los modelos)

```
STYLE — Western world "Dead Man's Rail" for a Roblox co-op game, mobile-first.
- Low-poly, faceted, hard-edged. Flat-shaded faces: no smoothing, no bevels, no subdivision, no sculpted detail.
- Readable at 40 studs on a phone screen: exaggerate the 2-3 shapes that identify the object; drop any detail smaller than 0.15 studs.
- Stylized but grounded: proportions about 1.15x chunkier than real life. No cartoon squash, no Roblox studs, no blocky "classic Roblox" look, no cute style.
- Weathered frontier at sunset: sun-bleached paint, sagging boards, chipped corners and dents made with geometry (a cut corner, a tilted plank), never with textures.
- COLOR: flat colors only, one material per color. No textures, no image maps, no vertex colors, no gradients, no UVs needed.
  Name every material <token>_<HEX> using ONLY these tokens:
  sand_D9A86C ochre_C4893F redrock_A8452E redrock_dark_6E2A1F stone_grey_8C8273
  wood_light_A7804F wood_mid_7E5A3A wood_dark_4E3524 wood_charred_2B211C
  paint_red_9C3B2E paint_teal_4F8C8A paint_mustard_C9A23F paint_cream_E3D6BC paint_slate_6E7F8C
  iron_3B3A3A rust_7B4A2E brass_B8893A gunmetal_5A5E63 steel_light_A3A7AB
  leather_6B3F24 leather_dark_3F2516 rope_C2A36B canvas_CDBB97
  cloth_red_8E2A22 cloth_black_1F1C1B cloth_blue_3E5468 cloth_white_D8D0BE cloth_brown_6A4A32
  skin_a_E0B08A skin_b_B07850 skin_c_6E4630 hair_grey_A8A39A hair_dark_2E241D hair_red_8A3A1E
  skin_dead_9AA08C skin_dead_dark_6E7363 blood_dry_5A1E18 bone_E6DCC3
  hide_brown_6A4430 hide_black_2A2220 hide_white_D9D0C0 feather_black_2A2626 vulture_skin_B5554A
  hay_D8B65A cactus_7A9A5B coal_1C1A19 warning_red_D2301F dynamite_red_B3261E
  glass_9FC7C9 glass_amber_8A5A22 glass_green_3F6B4A water_5E8F96 lamp_glow_FFC46B
  silver_neon_7FE6FF silver_crust_B9C3CC
  Use at most 6 materials per model (characters and creatures: up to 12) unless the prompt says otherwise.
- UNITS: 1 unit = 1 Roblox stud. Scale reference: an adult player is 5 studs tall, 2 wide, 1 deep. Y is up.
- ORIENTATION: the FRONT of the object faces -Z. Origin/pivot at the bottom center of the object, on the ground plane (y = 0), unless the prompt says otherwise.
- GEOMETRY: every object is a closed (watertight) mesh with outward normals; no internal faces, no duplicate or zero-area faces, no floating loose vertices.
- NO text, letters, numbers or logos in the geometry. Where a sign is needed, model a blank board; text is added later in the engine.
- REFERENCE IMAGE: if a concept image is attached, it is the art direction. Match its silhouette, proportions, costume, damage and attitude as closely as the geometry rules allow; translate its colors to the nearest palette tokens. Where the image and these rules disagree on technical points (names, pieces, origins, budget), the rules win.
- BUDGET: quality comes first. The model's TRIANGLE BUDGET is a reference, counted after merging coplanar faces of the same material: stay near it, spend triangles where the player looks, and go over it when that clearly improves the model (say how much and why). Never spend triangles on detail nobody sees. Technical ceiling: under 10,000 triangles per object.
- BOARDS AND PLANKS: show plank seams as thin (0.06) coplanar strips in a darker wood material, or by alternating wood_light / wood_mid per plank. Do not cut recessed grooves unless the prompt asks for them: they cost triangles and vanish under flat light.
- TOPOLOGY: build flat faces from clean quads and strips; avoid long sliver triangles.
- OUTPUT: one GLB file (if GLB is not available: OBJ + MTL). Object names and material names exactly as specified. Report the final triangle count per object.
```

### Bloque B — Prop estático

```
TYPE: static prop.
- One object named exactly as the model Id, unless the prompt lists sub-objects.
- It will use convex-hull collision: if the overall shape has big concavities (fences, wagons, frames), split it into the listed sub-objects so each one is roughly convex.
```

### Bloque C — Destructible prefragmentado

```
TYPE: pre-fragmented destructible. The model IS its fragments: there is no separate intact mesh.
- Build it as N separate closed meshes named frag01 ... fragNN (N is given in the prompt, never more than 8). They fit together with zero gaps and zero overlaps; assembled, they read as one intact object.
- Cut lines follow how the object is built: plank seams, board edges, brick courses, plus 1-2 jagged diagonal cracks (zig-zag of 3-5 vertices) across large surfaces, so the intact piece already looks "cracked and ready to fall".
- Each fragment roughly convex (hull collision), at least 0.4 studs in its smallest dimension, none larger than 45% of the whole by volume.
- Fragments that touch share flat contact faces. Those faces are hidden while the object is intact; that is expected, keep them (each fragment must be closed on its own).
- Fragments stay in their final position (do not center each one); all share the model origin.
- Parts that must stay standing after the break (frames, posts, stringers) are separate objects named fixed_<Name> and do not count as fragments.
```

### Bloque D — Personaje humanoide (rig R15)

```
TYPE: humanoid character for a Roblox R15 rig — rigid segmented, NO skinning, NO bones.
- Exactly 15 body objects named: Head, UpperTorso, LowerTorso, LeftUpperArm, LeftLowerArm, LeftHand, RightUpperArm, RightLowerArm, RightHand, LeftUpperLeg, LeftLowerLeg, LeftFoot, RightUpperLeg, RightLowerLeg, RightFoot.
- The character faces -Z, so its RIGHT side is +X and its LEFT side is -X.
- PROPORTIONS: stylized with character, built to read on a phone at 30 studs. Big head: the Head is 1/5 of H tall and wide enough to read the face. Big chunky hands (1.4x realistic, a mitten block plus a thumb block). Feet 1.2x. Forearms and shins clearly thinner than upper arms and thighs; chest broader than the hips. Not cute and not chibi: adults with heavy, readable shapes.
- Pose: I-pose for the LIMBS. Arms hanging straight down 8 degrees away from the body, palms toward the thighs, feet parallel and slightly apart. Attitude (a slump, a jutting chin, a pot belly, a proud chest) is modeled INTO the torso and head segments, never by bending the limbs, so the rig still works.
- Joint heights as a fraction of total height H (feet to top of head, without hat): ankle 0.05, knee 0.25, hip 0.47, waist split between LowerTorso and UpperTorso 0.55, elbow 0.58 (arms down), wrist 0.42 (arms down), shoulder 0.76, neck 0.80. Each segment ends at its joint.
- Adjacent segments overlap 0.1 studs and end in a rounded or cuffed shape (sleeve cuff, boot top, belt, collar) so a 90-degree bend shows no gap.
- Each body segment's ORIGIN (object/node position) sits on the joint it rotates around (UpperArm at the shoulder, LowerLeg at the knee, Head at the neck...); LowerTorso's origin is at the hip line.
- Clothing, hair, beards and gear are built onto the segment they move with (sleeve on the arm, holster on LowerTorso, beard on Head). Anything that would cross a joint (coat tails, skirts) stops above the next joint or is split at it.
- CLOTHING LAYERS: every layer worn over another (vest over shirt, chaps over trousers, apron over clothes, shawl over blouse) sits at least 0.03 studs proud of the layer under it. Never coplanar: coplanar layers flicker in the engine.
- Hats and anything worn or held that should be removable are SEPARATE objects named Acc_<Name>, already in place on the body.
- FACE: big readable features made with geometry: heavy brow ridge, wedge nose, cheekbones, a clear mouth shape and jaw. The eyes are two flat insets on the Head (0.12-0.15 studs each, readable from far away), a separate object named Eyes, so they can be swapped or recolored.
```

### Bloque E — Criatura (rig propio)

```
TYPE: creature for a custom rig — rigid segmented, NO skinning, NO bones.
- Split into exactly the objects listed in the prompt, named exactly. Each split falls at a joint; adjacent pieces overlap 0.1 studs with rounded ends so rotations up to 60 degrees show no gaps.
- Each piece's ORIGIN (object/node position) sits on the joint it rotates around (a leg at its hip or knee, the head at the neck, a wing at the shoulder); Torso/Body keeps the model origin.
- Neutral rest pose as described in the prompt, facing -Z.
- Origin on the ground plane, under the center of mass.
```

### Bloque F — Arma o ítem de mano

```
TYPE: handheld item for a Roblox Tool, seen in third person and lying on the ground.
- The muzzle / tip points toward -Z. Origin at the center of the main grip, where the right hand closes.
- Moving parts are separate objects with the names given (they will be animated). Each moving part's ORIGIN (object/node position) sits exactly on its pivot point or hinge axis, with its geometry offset from that origin. Static parts and markers keep their origin at the model origin.
- RELOAD AND INSPECT ARE ANIMATED: everything that moves when the weapon is loaded, cocked, opened or inspected is its own object (gates, ejector rods, levers, bolts, breech blocks, hinged barrels, magazines, cranks). Leave a clear gap or seam around each so it can move without showing holes.
- Add tiny marker cubes (0.05 studs) named exactly as the prompt lists (_Muzzle, _Grip, _Grip2, _Eject, ...). They mark attachment points and get deleted after import.
- Readability: about 1.25x real size relative to a 5-stud player. Thin parts (trigger guards, hammers, barrel walls, sights) at least 0.06 studs thick.
- Skins will recolor by material: keep the main metal, the detail metal and the grip/stock as three distinct materials, even if two share a color.
```

### Bloque G — Plata viva (overlay)

```
LIVING SILVER overlay (the parasite silver of this world).
- Separate objects named Silver_<Where> that sit ON TOP of the base model; the base model stays complete without them.
- Veins: material silver_neon_7FE6FF. Thin raised branching strips 0.06-0.12 studs wide, 0.03 studs proud of the surface, branching like roots or lightning, following the surface they sit on; thicker trunk near the source, thinning to points.
- Crust: material silver_crust_B9C3CC, with silver_neon_7FE6FF seams. Angular crystalline plates and shard clusters 0.1-0.4 studs proud, like jagged mineral growth, never smooth or blobby.
- The glow and the pulse are done in the engine; the geometry only defines where the silver is.
```

### Bloque H — Muerto (enemigos humanos y jefes infectados)

Va después del Bloque D. Sale de la primera tanda de caminantes: técnicamente perfectos y con aspecto de maniquí (rectos, limpios, cara plana).

```
UNDEAD DIRECTION: townsfolk killed and moved by a parasite silver. They must read as dead from 40 studs on a phone, even standing still, without any animation.
- POSTURE IN THE SHAPES (limbs stay in I-pose): UpperTorso modeled hunched, shoulders rolled forward and slumped with one side 0.1 studs lower than the other, upper back rounded; the neck stump angled forward 20 degrees. The Head geometry juts forward from the neck joint (chin about 0.15 studs ahead of the neck) and tilts down 10 degrees.
- FACE: deep eye sockets (a skin_dead_dark_6E7363 recess) with the Eyes insets sitting inside them; sunken cheeks; a slack open jaw showing a row of 4-6 jagged bone_E6DCC3 teeth; the lip torn back on one side.
- SKIN: skin_dead_9AA08C with skin_dead_dark_6E7363 patches (bruises, swollen veins as flat insets 0.01 proud) and blood_dry_5A1E18 around the mouth and on wounds.
- DAMAGE: choose 3-4 per character, never the same set on two variants: a bite with a missing chunk (a concave notch) on a forearm, shoulder or neck; a sleeve torn off ending in 3-5 triangular tatters; the shirt ripped open showing 3 rib ridges (bone_E6DCC3 strips on skin_dead_dark); a missing ear; a broken finger bent the wrong way inside the hand block; a trouser leg torn to the knee showing a thin shin; a lost boot.
- CLOTHES: torn hems as zig-zag triangle edges (3-5 points), dirt patches (ochre_C4893F or sand_D9A86C flat insets), missing buttons, a dangling strap. Never a clean straight hem.
- LIMITS: no exposed organs, no dismemberment beyond fingers and ears, no gore beyond dry blood (Roblox rules).
```

---

## Inventario

`Primer uso` es el tramo donde aparece primero según las notas de fase. Ids con prefijo `WST_` y, donde existe, el id de la ficha.

| Sección | Modelos | Prompts |
|---|---|---|
| [1. Armas e ítems de mano](#1-armas-e-ítems-de-mano) | Revólver, La Viuda de Hank, rifle de palanca, escopeta de doble caño, rifle de caza, dinamita, molotov, lazo, farol de mano | 10 |
| [2. Pickups, consumibles y loot](#2-pickups-consumibles-y-loot) | Esquirlas de plata, munición por familia, consumibles, contenedores | 10 |
| [3. NPCs](#3-npcs) | Old Hank, telegrafista, minero atrapado, comerciantes, buhonero | 8 |
| [4. Enemigos](#4-enemigos) | Caminante (4 cuerpos + 3 overlays de plata), corredor, minero hinchado, pistolero, jinete, toro, buitre | 13 |
| [5. Jefes](#5-jefes) | Sheriff, Carnicero, Capataz, Hermanos Doyle, maquinista, Predicador (2 formas) | 7 (8 modelos) |
| [6. Transporte](#6-transporte) | Caballo, carreta, Gatling, vagoneta, tren completo, restos del descarrilamiento | 14 |
| [7. Kit modular de edificios](#7-kit-modular-de-edificios) | Paredes, fachadas, puertas, ventanas, porches, techos, carteles, barricadas | 12 familias |
| [8. Piezas únicas por tramo](#8-piezas-únicas-por-tramo) | Vagón, Dusty Gulch, cañón, Red Mesa, mina, Silver Bend, vías, Hollow Creek, iglesia | 50 |
| [9. Props por categoría](#9-props-por-categoría) | Barriles, cajas, carretas, bebederos, postes de telégrafo, cactus, lápidas, cercas | 12 |
| [10. Extras propuestos](#10-extras-propuestos-no-están-en-el-vault) | No están en el vault: confirmar antes de hacer | 8 (sin prompt todavía) |

### Orden de producción recomendado

1. **Medición:** `WST_Prop_Crate`.
2. **Vagón + Dusty Gulch** (es el primer tramo y enseña casi todas las mecánicas): `WST_Weapon_Revolver`, `WST_Enemy_Walker` (cuerpo A) + `WST_Overlay_SilverEyes`, el kit modular, barriles, cajas, `WST_NPC_OldHank`, `WST_Weapon_HanksWidow`, `WST_Enemy_Runner`, `WST_Enemy_DeadGunslinger`, `WST_Boss_Sheriff`, `WST_Weapon_Dynamite`, `WST_Mount_Horse`.
3. Después, en el orden del recorrido: viaje → Red Mesa → mina → Silver Bend → tren → Hollow Creek → iglesia.

---

## 1. Armas e ítems de mano

Fuente: `Armas y consumibles del Western.md`. Ficha: `Weapons`.

### `WST_Weapon_Revolver` — Revólver (secundaria del Western)

- **Bloques:** A + F · **Tris:** ≤ 800 · **Primer uso:** vagón · **Ficha:** `Revolver`
- **Recarga:** acción simple, bala por bala por la tapa de carga (el vault pide recarga por bala, cancelable, y el duelo es "fan the hammer", que solo existe en acción simple). Para la animación: se abre la tapa, la varilla expulsa el casquillo, entra una bala, el cilindro gira una recámara. Las balas sueltas son `WST_Item_Rounds`.
- Es la base de las skins (acabados que se adaptan a la forma) y la forma que se desbloquea al completar el Chapter: tiene que leerse como "revólver del oeste" en cualquier mundo.

```
MODEL: WST_Weapon_Revolver
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Single-action frontier revolver, 1870s cavalry style, generic (no brand marks).
Size: 1.3 studs long along Z (barrel tip at -Z), 0.55 tall, 0.2 wide.
Separate objects:
- Body: frame, 0.6-stud octagonal barrel (8-sided) with a blade front sight, the ejector rod housing (a tube under the barrel on the right +X side; the rod itself is a separate object), the opening in the frame behind the cylinder where the LoadingGate sits, trigger guard.
- Cylinder: 6 deep flutes, 0.3 long, 0.27 diameter; rear face shows 6 chamber holes. Origin on its own rotation axis (parallel to the barrel). It only rotates: it is fixed in the frame and never swings out (single action, loaded one round at a time through the gate).
- LoadingGate: small hinged gate on the right side (+X) of the frame, just behind the cylinder, covering one chamber; origin on its hinge along the gate's lower edge; it swings open outward and down 90 degrees.
- EjectorRod: the rod inside the ejector housing, with a small round head at its front; origin at its front end; it slides straight back 0.3 studs to push a casing out of the chamber aligned with the gate.
- Hammer: tall spur, pivot at its base (cocks back 35 degrees). It is fanned with the other hand in the duel: keep the spur big and readable.
- Trigger: thin curved blade, pivot at its top.
- Grip: plow-handle grip, two wooden side panels with a metal backstrap, angled 105 degrees from the barrel line.
Materials: gunmetal_5A5E63 (frame, barrel, cylinder) as main metal; steel_light_A3A7AB (hammer, front sight, ejector rod, 4 screw heads as tiny cubes) as detail metal; brass_B8893A (trigger guard and backstrap); wood_mid_7E5A3A (grip panels).
Markers: _Muzzle at the barrel tip center; _Grip at the center of the grip; _Eject at the loading gate; _Chamber at the center of the chamber aligned with the open gate (where a round goes in and a casing comes out).
Avoid overlapping coplanar faces inside Body (they flicker in the engine).
Silhouette priority: long thin octagonal barrel, fat round cylinder, curved grip. Must read as "western revolver" from 30 studs.
```

### `WST_Weapon_HanksWidow` — La Viuda de Hank (revólver único)

- **Bloques:** A + F · **Tris:** ≤ 800 · **Primer uso:** Dusty Gulch, oleada 3 · **Ficha:** `HanksWidow`
- Arma única: una sola por partida, cae al piso y la agarra quien llegue. Tiene que distinguirse del revólver base de un vistazo. El look (niquelado, cachas de hueso con muescas, cinta negra) es propuesta.

```
MODEL: WST_Weapon_HanksWidow
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Unique heirloom revolver "The Widow", same construction and part names as the standard frontier revolver, but clearly different at a glance:
Size: 1.55 studs long (longer 0.85-stud barrel), 0.58 tall, 0.21 wide.
Separate objects: Body, Cylinder, LoadingGate, EjectorRod, Hammer, Trigger, Grip, Ribbon (LoadingGate and EjectorRod built and pivoted exactly like the standard revolver: it reloads the same way).
- Body and Cylinder: nickel finish (steel_light_A3A7AB as main metal), with a raised scroll band (a 0.02-proud wavy strip) along both sides of the frame in brass_B8893A.
- Cylinder: 6 flutes, pivot on its axis. Hammer pivot at base. Trigger pivot at top.
- Grip: bone_E6DCC3 ivory panels with 6 small notches cut into the bottom edge of the right panel (tally marks of a long career).
- Ribbon: a short black mourning ribbon (cloth_black_1F1C1B) tied around the bottom of the grip, two tails 0.25 long hanging down.
Detail metal: gunmetal_5A5E63 for screws, sight, ejector rod.
Markers: _Muzzle, _Grip, _Eject, _Chamber (same places as a standard revolver).
```

### `WST_Weapon_LeverRifle` — Rifle de palanca

- **Bloques:** A + F · **Tris:** ≤ 900 · **Primer uso:** tiendas y mapa · **Ficha:** `LeverRifle`

```
MODEL: WST_Weapon_LeverRifle
TRIANGLE BUDGET: <= 900 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Lever-action repeating rifle, 1873 style, generic.
Size: 3.2 studs long along Z (muzzle at -Z), 0.65 tall at the stock, 0.2 wide.
Separate objects:
- Body: round 1.6-stud barrel with a tubular magazine running under it to 0.3 from the muzzle, front sight blade, buckhorn rear sight, receiver with a side loading gate on the right (+X), straight wooden forend, wooden buttstock with a crescent metal buttplate.
- Lever: loop lever under the receiver, finger loop big enough to read from far away; pivot at its front end; it swings down 50 degrees.
- Bolt: the bolt on top of the receiver that slides back 0.25 studs when the lever opens; origin at its front end.
- LoadingGate: the spring cover of the side loading gate on the right (+X) of the receiver, where rounds are pushed in one by one; origin on its front hinge; it pushes inward 15 degrees.
- Hammer: pivot at its base.
- Trigger: pivot at its top.
Materials: gunmetal_5A5E63 (barrel, magazine tube, lever) main metal; brass_B8893A (receiver, buttplate, forend cap) — a brass "yellow" receiver is the identifying feature; steel_light_A3A7AB (sights, screws) detail metal; wood_mid_7E5A3A (stock and forend).
Markers: _Muzzle at the barrel tip; _Grip at the wrist of the stock behind the lever; _Grip2 under the middle of the forend; _Eject on top of the receiver; _Load at the side loading gate (where each round goes in).
```

### `WST_Weapon_DoubleBarrel` — Escopeta de doble caño

- **Bloques:** A + F · **Tris:** ≤ 800 · **Primer uso:** tiendas y mapa · **Ficha:** `DoubleBarrel`
- Recarga por bala, cancelable: los caños se abren.

```
MODEL: WST_Weapon_DoubleBarrel
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Side-by-side double-barrel coach shotgun with two external hammers, generic.
Size: 2.7 studs long along Z (muzzles at -Z), 0.6 tall at the stock, 0.28 wide.
Separate objects:
- Stock: wooden buttstock and wrist, metal action block with the hinge pin at its front top.
- Barrels: two barrels side by side joined by a flat top rib, wooden forend underneath; 1.4 studs long; pivot exactly on the hinge pin so they break open downward 40 degrees showing 2 chamber holes.
- HammerL, HammerR: two big curled hammers on top of the action, pivots at their bases.
- Triggers: two triggers in one guard, one object, pivot at the top.
Materials: gunmetal_5A5E63 (barrels) main metal; iron_3B3A3A (action, hinge, trigger guard) detail metal; wood_dark_4E3524 (stock and forend).
- Extractor: the small extractor plate at the rear face of the barrels that pushes the two shells out a little when they open; origin at its front; it slides back 0.08 studs.
Markers: _Muzzle centered between the two muzzles; _Grip at the wrist; _Grip2 under the forend; _Eject at the open breech; _ChamberL and _ChamberR at the center of each chamber mouth (where each shell goes in and comes out).
Silhouette priority: two fat parallel barrels and the two hammer ears.
```

### `WST_Weapon_HuntingRifle` — Rifle de caza (francotirador)

- **Bloques:** A + F · **Tris:** ≤ 900 · **Primer uso:** tiendas y mapa · **Ficha:** `HuntingRifle`

```
MODEL: WST_Weapon_HuntingRifle
TRIANGLE BUDGET: <= 900 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Long single-shot falling-block buffalo rifle with a long period brass telescope sight, generic.
Size: 3.7 studs long along Z (muzzle at -Z), 0.7 tall including the scope, 0.22 wide.
Separate objects:
- Body: heavy octagonal 2.0-stud barrel, receiver, wooden forend and buttstock with a straight wrist.
- Lever: under-lever that doubles as trigger guard; pivot at its front; swings down 45 degrees.
- BreechBlock: the falling block that drops down inside the receiver when the lever opens, exposing the chamber; origin at its top front edge; it slides down 0.2 studs.
- Hammer: side hammer on the right (+X), pivot at its base.
- Scope: thin long brass tube (0.09 diameter, 1.9 long) running along the top of the barrel from the receiver almost to the muzzle, on two small mounts; slightly wider eyepiece at the rear.
Materials: gunmetal_5A5E63 main metal; brass_B8893A (scope, buttplate); iron_3B3A3A detail metal; wood_mid_7E5A3A stock.
Markers: _Muzzle, _Grip at the wrist, _Grip2 under the forend, _Eject at the breech, _Chamber at the chamber mouth exposed by the BreechBlock, _Scope at the rear end of the scope.
```

### `WST_Weapon_Dynamite` — Dinamita (cartucho y atado)

- **Bloques:** A + F · **Tris:** ≤ 120 por variante · **Primer uso:** Dusty Gulch · **Ficha:** `Dynamite`
- Pedir las dos variantes en el mismo hilo. La chispa de la mecha es VFX.

```
MODEL: WST_Weapon_Dynamite
TRIANGLE BUDGET: <= 120 triangles per variant. Hard cap: see the BUDGET rule in STYLE.
Variant 1 — WST_Weapon_Dynamite_Stick: one dynamite stick.
- Cylinder 0.55 studs long, 0.15 diameter, 8-sided, wrapped in dynamite_red_B3261E paper with a thin paint_cream_E3D6BC paper band around the middle (blank, for a decal).
- Fuse: separate object Fuse, a 0.3-long cord (rope_C2A36B) coming out of one end and bending 40 degrees, 3 segments.
- Origin at the center of the stick. Stick axis along Z, fuse end at +Z. Marker _Fuse at the fuse tip.
Variant 2 — WST_Weapon_Dynamite_Bundle: three sticks tied in a triangle bundle with two loops of twine (rope_C2A36B), one longer shared fuse (0.4) twisted from the three, separate object Fuse, marker _Fuse at its tip.
```

### `WST_Weapon_WhiskeyMolotov` — Molotov de whisky

- **Bloques:** A + F · **Tris:** ≤ 200 · **Primer uso:** Red Mesa (en el mapa) · **Ficha:** `WhiskeyMolotov`

```
MODEL: WST_Weapon_WhiskeyMolotov
TRIANGLE BUDGET: <= 200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Whiskey bottle turned into a fire bomb.
- Bottle: square-shouldered frontier whiskey bottle, 0.75 studs tall, 0.28 wide, 8-sided body, short neck. Material glass_amber_8A5A22. A blank paper label on the front (-Z) face in paint_cream_E3D6BC, slightly proud (0.01).
- Rag: separate object, a torn cloth rag (cloth_red_8E2A22) stuffed in the neck, one tail 0.3 long hanging over the shoulder of the bottle.
- Origin at the center of the bottle body. Bottle upright (Y). Marker _Fuse at the tip of the rag tail.
```

### `WST_Weapon_Lasso` — Lazo

- **Bloques:** A + F · **Tris:** ≤ 300 · **Primer uso:** tiendas y mapa · **Ficha:** `Lasso`
- El lazo lanzado (la soga en el aire) es una cuerda dibujada en el motor; esto es el rollo en la mano y en el piso.

```
MODEL: WST_Weapon_Lasso
TRIANGLE BUDGET: <= 300 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Coiled lariat rope held in one hand.
- Coil: 4 overlapping loops of rope (rope_C2A36B), 1.1 studs diameter, rope thickness 0.08, 8-sided rope cross-section, loops slightly offset so they read as separate turns. Coil plane is vertical (XY), facing the side.
- Noose: separate object, a running loop 0.9 diameter hanging from the bottom of the coil with the small honda knot visible (a lump 0.15).
- A wrap of leather_6B3F24 where the hand holds the coil (top of the coil).
- Origin at the hand wrap. Markers: _Grip at the wrap, _Noose at the knot.
```

### `WST_Item_Lantern` — Farol de mano (mina)

- **Bloques:** A + F · **Tris:** ≤ 250 · **Primer uso:** mina · Fuente: `Fase 3 - La mina de plata.md` (faroles con aceite limitado)
- Si los faroles terminan siendo fijos y no de mano, sirve igual como prop colgado.

```
MODEL: WST_Item_Lantern
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Hand-held kerosene barn lantern.
- Body: round tin base (iron_3B3A3A), glass globe (glass_9FC7C9) protected by 4 vertical wire guards, vented top cap, big wire bail handle arching over the top.
- Flame: separate object, a small teardrop flame inside the globe, material lamp_glow_FFC46B.
- Oil level window: none (oil is shown in the UI).
- Size: 0.9 studs tall without the handle, 0.5 wide; handle adds 0.4.
- Origin at the top of the handle (where the hand holds it). Markers: _Grip at the handle top, _Light at the flame center.
```

### `WST_Weapon_Knife` — Cuchillo global (lo usa el Western, no es suyo)

- **Bloques:** A + F · **Tris:** ≤ 250 · **Primer uso:** vagón (arma de quien no agarró el revólver)
- El cuchillo es **equipamiento global** (`Equipamiento base.md`): va a todos los mundos y tiene formas y skins propias. Este prompt es una forma base neutra; no lleva estética del oeste a propósito.

```
MODEL: WST_Weapon_Knife
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Neutral combat knife, the default shape of a cross-world knife (must fit any setting, from western to cyberpunk).
- Blade: straight clip-point blade 0.75 studs long, 0.16 tall at the base, 0.03 thick, with a single faceted edge bevel line.
- Guard: small flat crossguard 0.3 wide.
- Handle: 0.5-stud handle with 3 shallow grip rings, flat pommel.
Separate objects: Blade, Handle (guard included in Handle).
Materials: steel_light_A3A7AB (blade) main metal; gunmetal_5A5E63 (guard, pommel) detail metal; leather_dark_3F2516 (handle).
Tip points to -Z. Markers: _Grip at the handle center, _Tip at the blade tip.
```

---

## 2. Pickups, consumibles y loot

Fuentes: `Looting.md`, `Tiendas y economía del Western.md`, `Armas y consumibles del Western.md`. El brillo y el color por rareza son VFX, no geometría.

### `WST_Pickup_SilverShard` — Esquirla de plata (moneda)

- **Bloques:** A + B + G · **Tris:** ≤ 80 por variante · **Primer uso:** Dusty Gulch
- Cae de cada enemigo y se junta sola: muchas en pantalla a la vez, tiene que ser barata.

```
MODEL: WST_Pickup_SilverShard
TRIANGLE BUDGET: <= 80 triangles per variant. Hard cap: see the BUDGET rule in STYLE.
Currency drop: a shard of living silver. Make 3 variants in the same file: Shard_A, Shard_B, Shard_C.
- Each: a small cluster of 2-4 angular crystal spikes growing from a common base, 0.45-0.6 studs tall, 0.35 wide. Hexagonal or irregular 5-6 sided prisms with sharp pointed tips, tilted 10-25 degrees from each other.
- Outer faces silver_crust_B9C3CC; one inner sliver per cluster (a thin separate object named Core inside the cluster, poking out at the tips) in silver_neon_7FE6FF.
- Origin at the base center. Each variant under 80 triangles.
```

### `WST_Pickup_Ammo` — Munición por familia

- **Bloques:** A + B · **Tris:** ≤ 120 por variante · Fuente: familias de `Armas y munición.md` (pistola/revólver, rifle, escopeta, especial)

```
MODEL: WST_Pickup_Ammo
TRIANGLE BUDGET: <= 120 triangles per variant. Hard cap: see the BUDGET rule in STYLE.
Ammo pickups, 3 variants in one file, each a separate object:
- Ammo_Revolver: small paper cartridge box 0.5 x 0.3 x 0.35 studs (paint_cream_E3D6BC with a cloth_red_8E2A22 band), lid flipped open showing a row of 6 brass_B8893A cartridge tops (6-sided, simple).
- Ammo_Rifle: longer box 0.75 x 0.3 x 0.35 (paint_mustard_C9A23F with an iron_3B3A3A band), open, showing 5 longer pointed cartridges.
- Ammo_Shotgun: box 0.55 x 0.35 x 0.45 (paint_teal_4F8C8A), open, showing 4 fat shells: cloth_red_8E2A22 hulls with brass_B8893A heads.
Blank labels only (no text). Origin at the bottom center of each box.
```

### `WST_Item_Rounds` — Balas sueltas (para las animaciones de recarga)

- **Bloques:** A + F · **Tris:** ≤ 200 en total · **Primer uso:** vagón (recargar el revólver) · Fuente: recarga por bala en revólver y escopeta, recarga táctica y en vacío (`Armas y munición.md`)
- La mano mete una bala y la varilla o el extractor sacan un casquillo vacío: por eso cada familia tiene la bala entera y el casquillo.

```
MODEL: WST_Item_Rounds
TRIANGLE BUDGET: <= 200 triangles in total. Hard cap: see the BUDGET rule in STYLE.
Single loose rounds held by the hand during reload animations. Six separate objects in one file, laid out in a row along X with 0.3 studs between them, each with its ORIGIN at its own center and its long axis along Z (tip toward -Z):
- RevolverRound: brass_B8893A case 0.12 long, 0.05 diameter, with a lead bullet (stone_grey_8C8273) 0.05 long on the front; 6-sided.
- RevolverCasing: the same case without the bullet, open front (a short hollow ring of geometry, closed mesh), rim at the back.
- RifleRound: brass_B8893A bottle-neck case 0.2 long, 0.055 diameter, lead bullet 0.06 long; 6-sided.
- RifleCasing: the same case, empty.
- ShotgunShell: cloth_red_8E2A22 paper hull 0.22 long, 0.09 diameter, brass_B8893A head 0.05 long with a rim; 8-sided; crimped front shown as a slightly narrower end.
- ShotgunShellSpent: the same shell with the front opened (flared) and the hull darkened (cloth_red_8E2A22 with a coal_1C1A19 ring at the mouth).
Oversized about 1.4x real so they read in the hand from a third-person camera.
```

### `WST_Item_Bandages` — Vendas

- **Bloques:** A + B · **Tris:** ≤ 100 · **Ficha:** `Bandages`

```
MODEL: WST_Item_Bandages
TRIANGLE BUDGET: <= 100 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A rolled cloth bandage, 0.45 diameter, 0.3 wide (canvas_CDBB97), with the loose end unrolled 0.3 and hanging, plus a small tin safety pin (steel_light_A3A7AB) on the roll. 8-sided roll. Origin at the bottom of the roll.
```

### `WST_Item_DoctorTonic` — Tónico del doctor

- **Bloques:** A + B · **Tris:** ≤ 120 · **Ficha:** `DoctorTonic`

```
MODEL: WST_Item_DoctorTonic
TRIANGLE BUDGET: <= 120 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Patent-medicine bottle: tall rectangular bottle with beveled corners, 0.7 studs tall, 0.28 x 0.18, glass_green_3F6B4A, short neck with a cork (wood_light_A7804F). A blank paint_cream_E3D6BC label on the front (-Z) and a tied string with a tiny blank paper tag around the neck. Origin at the bottom center.
```

### `WST_Item_Coffee` — Café

- **Bloques:** A + B · **Tris:** ≤ 120 · **Ficha:** `Coffee`

```
MODEL: WST_Item_Coffee
TRIANGLE BUDGET: <= 120 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Enamel camp mug full of black coffee: 0.4 tall, 0.38 diameter, 8-sided, paint_slate_6E7F8C body, iron_3B3A3A rim, C-shaped handle on the right (+X). Coffee surface inside in coal_1C1A19, 0.05 below the rim. Origin at the bottom center.
```

### `WST_Item_Whiskey` — Whisky

- **Bloques:** A + B · **Tris:** ≤ 120 · **Ficha:** `Whiskey`

```
MODEL: WST_Item_Whiskey
TRIANGLE BUDGET: <= 120 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The same square-shouldered whiskey bottle as the molotov (0.75 tall, glass_amber_8A5A22, blank paint_cream_E3D6BC label), sealed with a cork (wood_light_A7804F) instead of a rag. No liquid inside. Origin at the bottom center.
```

### `WST_Prop_Crate` — Caja de madera (PIEZA DE MEDICIÓN)

- **Bloques:** A + C · **Fragmentos:** 6 · **Tris:** ≤ 350 · Fuente: contenedores de loot ("patear un cajón")
- Es la primera pieza a importar y medir.

```
MODEL: WST_Prop_Crate
TRIANGLE BUDGET: <= 350 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Wooden supply crate, a loot container that is kicked open.
Size: exactly 3 x 3 x 3 studs (a cube, so scale and orientation are easy to measure).
- Built from horizontal planks (3 per side, 0.08 grooves between them), dark corner battens on all 12 edges (wood_dark_4E3524), planks in wood_light_A7804F.
- One diagonal brace on the front (-Z) face only, from bottom-left to top-right, so the front is identifiable.
- A small blank stencil plate on the front face (paint_cream_E3D6BC, 0.9 x 0.5, 0.02 proud).
- Fragments (6): frag01 lid, frag02 front face, frag03 back face, frag04 left face, frag05 right face, frag06 bottom. Each face keeps its own battens.
Origin at the bottom center.
```

### `WST_Prop_CrateLarge` — Cajón grande

- **Bloques:** A + C · **Fragmentos:** 8 · **Tris:** ≤ 400

```
MODEL: WST_Prop_CrateLarge
TRIANGLE BUDGET: <= 400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Large freight crate, 6 long (X) x 4 tall x 4 deep studs. Same construction as the 3-stud crate (wood_light planks, wood_dark battens, X brace on the front -Z face and on the back), plus two iron_3B3A3A strap bands wrapping around at 1/4 and 3/4 of the length, and a blank stencil plate on the front.
Fragments (8): lid in two halves, front in two halves split along a crack, back, left, right, bottom. Straps stay with the fragment they lie on.
Origin at the bottom center. Usable as crouch cover (4 tall hides a crouching player).
```

### `WST_Prop_Safe` — Caja fuerte

- **Bloques:** A + C · **Fragmentos:** 4 + puerta · **Tris:** ≤ 500 · Fuente: "las cajas fuertes con dinamita o ganzúa"

```
MODEL: WST_Prop_Safe
TRIANGLE BUDGET: <= 500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Heavy iron floor safe, 2.6 wide x 3.2 tall x 2.4 deep studs, on 4 short squat feet.
- Body: iron_3B3A3A box with rounded-looking (chamfered 45-degree) vertical edges, a paint_red_9C3B2E painted front frame with a thin brass_B8893A pinstripe border (0.02 proud strips), a blank brass name plate above the door.
- Door: separate object Door, front panel 2.0 x 2.4 inset 0.05, big round combination dial (brass) and a 4-spoke handle wheel (steel_light_A3A7AB). Hinge on the right (+X) edge; pivot on the hinge axis.
- Interior: hollow behind the door, 0.3-thick walls, two shelves.
- When blown with dynamite, the door flies off and the body cracks: fragments (4) for the body are frag01 top, frag02 left wall, frag03 right wall, frag04 back+bottom.
Origin at the bottom center. Front (-Z) is the door.
```

### `WST_Prop_AmmoCrateRailway` — Caja de munición fija de la compañía

- **Bloques:** A + B · **Tris:** ≤ 350 · Fuente: "cajas de munición fijas en los pueblos liberados"

```
MODEL: WST_Prop_AmmoCrateRailway
TRIANGLE BUDGET: <= 350 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Fixed ammunition chest of the railroad company, bolted to the ground in liberated towns.
Size: 4 long (X) x 2.2 tall x 2.2 deep studs.
- Wooden chest (paint_teal_4F8C8A, faded) with iron_3B3A3A corner caps, two side rope handles (rope_C2A36B), and a hinged lid.
- Lid: separate object Lid, hinge along the back top edge (+Z), opens 100 degrees.
- On the front (-Z): a blank brass_B8893A emblem plate shaped like a shield (the company logo goes on as a decal).
- Inside: 3 rows of cartridge boxes (simple blocks, paint_cream_E3D6BC) visible when open.
Origin at the bottom center.
```

---

## 3. NPCs

Personajes vivos. Bloque D (rig R15). Piel viva: elegir `skin_a`, `skin_b` o `skin_c`; los comerciantes pueden tener varias versiones.

### `WST_NPC_OldHank` — Old Hank

- **Bloques:** A + D · **Tris:** ≤ 2 200 · **Primer uso:** vagón · Fuente: `Fase 0`, `Fase 1`, `Tutorial del Western.md`, `D015`
- Guía del tutorial (formato A). Lo arrastra un caminante, está mordido y muere entregando La Viuda: el revólver va enfundado como accesorio separado.

```
MODEL: WST_NPC_OldHank
TRIANGLE BUDGET: <= 2200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Old Hank, a veteran bounty hunter in his sixties, warm and tough. Height H = 5.3 studs (slight stoop is done by animation, model him upright).
- Head: long weathered face, deep brow, big hooked nose wedge, long grey drooping mustache and a short grey beard (hair_grey_A8A39A) on the Head object, skin_b_B07850 skin, grey hair to the collar at the back.
- UpperTorso: faded cloth_red_8E2A22 shirt under an open cloth_brown_6A4A32 vest; a leather_6B3F24 bandolier of brass_B8893A cartridge loops across the chest from his left shoulder to his right hip; cloth_black_1F1C1B neckerchief.
- LowerTorso: gun belt with a holster on his right hip (+X), belt buckle as a small brass rectangle.
- Arms: shirt sleeves rolled to the elbow (rolled cuff hides the elbow joint), weathered forearms, leather_dark_3F2516 fingerless gloves.
- Legs: cloth_blue_3E5468 trousers tucked into tall leather_dark_3F2516 boots with spurs (small rowel discs) on the Foot objects.
- Short duster coat: cloth_brown/canvas_CDBB97 coat that ends at mid-thigh, split at the hip line between LowerTorso and the UpperLegs so the legs move freely.
Accessories (separate objects):
- Acc_Hat: battered wide-brim hat (canvas_CDBB97, crown dented, brim 1.8 studs wide, one side curled up), with a leather band.
- Acc_HanksWidow: the nickel revolver with bone grip sitting in the holster, only the grip and cylinder visible above the holster.
- Acc_BiteWound: a torn sleeve patch with blood_dry_5A1E18 on the left forearm, hidden by default, shown after he is bitten.
Eyes: separate object, small, hair_dark_2E241D.
```

### `WST_NPC_Telegraphist` — Telegrafista

- **Bloques:** A + D · **Tris:** ≤ 1 600 · **Primer uso:** Dusty Gulch, oleada 4 (defensa en el saloon)

```
MODEL: WST_NPC_Telegraphist
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Small-town telegraph operator, nervous and thin, around 30. H = 5.0 studs.
- Head: clean-shaven, thin face, round wire spectacles (iron_3B3A3A thin frames, glass_9FC7C9 lenses) as part of the Head, slicked dark hair (hair_dark_2E241D).
- UpperTorso: cloth_white_D8D0BE shirt with a cloth_black bow tie and a cloth_brown_6A4A32 vest.
- Arms: white sleeves with black arm garters (bands) above the elbows.
- LowerTorso and legs: grey-brown trousers (cloth_brown_6A4A32), leather_dark shoes.
Accessories: Acc_Visor: a paint_teal_4F8C8A eyeshade visor: a band around the head with a flat brim angled down in front (solid, not transparent).
Skin: skin_a_E0B08A. Eyes: separate object.
```

### `WST_NPC_TrappedMiner` — Minero atrapado

- **Bloques:** A + D · **Tris:** ≤ 1 600 · **Primer uso:** mina (evento de rescate)

```
MODEL: WST_NPC_TrappedMiner
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Trapped silver miner, alive but exhausted, 40s. H = 5.2 studs.
- Head: stubble beard, soot smudges (coal_1C1A19 patches as flat insets) on cheeks and forehead, skin_c_6E4630.
- UpperTorso: canvas_CDBB97 work shirt, cloth_blue_3E5468 bib overalls with suspenders over the shoulders.
- Arms: sleeves rolled, one forearm wrapped in a dirty bandage (canvas).
- Legs: overalls tucked into heavy leather_dark boots.
Accessories: Acc_Hat: soft felt miner's hat (cloth_brown_6A4A32) with a tin candle holder clipped to the front (iron_3B3A3A) holding a short candle stub; Acc_Pickaxe: a pickaxe (iron head, wood_mid handle 2.6 long) held in his right hand.
Eyes: separate object.
```

### `WST_NPC_Storekeeper` — Almacenero (almacén general)

- **Bloques:** A + D · **Tris:** ≤ 1 600 · **Primer uso:** Dusty Gulch liberado · Fuente: tienda humana del Western

```
MODEL: WST_NPC_Storekeeper
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
General store owner, plump and friendly, 50s. H = 5.1 studs, belly 1.2x wider than the default torso.
- Head: round face, mutton-chop sideburns, bald top with grey sides (hair_grey), small round spectacles on the nose, skin_a_E0B08A.
- UpperTorso: cloth_white shirt, paint_mustard_C9A23F vest, long canvas_CDBB97 shop apron from chest to the hip line (the part below the hip is split onto the UpperLegs).
- Arms: black sleeve garters, a pencil behind the right ear (on Head).
- Legs: dark trousers, leather_dark shoes.
Eyes: separate object. No hat.
```

### `WST_NPC_Gunsmith` — Armero (armería)

- **Bloques:** A + D · **Tris:** ≤ 1 600 · **Primer uso:** Dusty Gulch liberado

```
MODEL: WST_NPC_Gunsmith
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Gunsmith, lean and precise, 40s. H = 5.2 studs.
- Head: neat short beard (hair_dark), a jeweler's loupe flipped up on a headband (iron_3B3A3A ring with glass lens) on the Head, skin_c_6E4630.
- UpperTorso: cloth_white shirt, leather_6B3F24 work apron with two front pockets holding small tools (wedges).
- Arms: rolled sleeves, oil stains (coal patches) on the hands.
- LowerTorso: gun belt with an empty holster on the right.
- Legs: cloth_brown trousers, leather_dark boots.
Accessories: Acc_Hat: flat-crown low hat (cloth_black). Eyes: separate object.
```

### `WST_NPC_Blacksmith` — Herrero (establo y herrería)

- **Bloques:** A + D · **Tris:** ≤ 1 800 · **Primer uso:** Red Mesa liberado · Fuente: mejoras del caballo

```
MODEL: WST_NPC_Blacksmith
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Blacksmith, huge and calm, 40s. H = 5.6 studs, shoulders 1.3x wider than the default torso, thick forearms.
- Head: thick dark beard (hair_dark), bald head, soot on the brow, skin_b_B07850.
- UpperTorso: sleeveless canvas undershirt, heavy leather_dark_3F2516 apron from the chest down to the hip line (continued on the UpperLegs).
- Arms: bare muscular arms, leather_dark long gloves up to mid-forearm.
- Legs: cloth_brown trousers, heavy boots.
Accessories: Acc_Hammer: a short sledge hammer (iron head 0.6 long, wood_mid handle 1.6) held in the right hand; Acc_Horseshoe: an iron horseshoe held in the left hand.
Eyes: separate object.
```

### `WST_NPC_Bartender` — Barman

- **Bloques:** A + D · **Tris:** ≤ 1 600 · Fuente: barman (rumores y bonus temporales)

```
MODEL: WST_NPC_Bartender
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Saloon bartender, slick and talkative, 30s. H = 5.2 studs.
- Head: big waxed handlebar mustache (hair_dark) with curled tips, hair parted in the middle and slicked, skin_a_E0B08A.
- UpperTorso: cloth_white shirt, plain paint_red_9C3B2E vest with 3 brass_B8893A buttons (tiny cubes), cloth_black bow tie.
- Arms: white sleeves with black garters; a canvas bar towel draped over the left shoulder (on UpperTorso).
- Legs: black trousers, black shoes.
Accessories: Acc_Glass: a short whiskey glass held in the right hand (glass_9FC7C9). Eyes: separate object. No hat.
```

### `WST_NPC_Peddler` — Buhonero (vendedor ambulante)

- **Bloques:** A + D · **Tris:** ≤ 1 800 · Fuente: vendedor ambulante del Western ("buhonero con carreta"); su carreta está en Transporte

```
MODEL: WST_NPC_Peddler
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Traveling peddler, eccentric and theatrical, 60s, thin. H = 5.3 studs.
- Head: long thin face, pointed grey goatee (hair_grey), bushy eyebrows, skin_a_E0B08A.
- UpperTorso: patched long-tailed frock coat (cloth_brown_6A4A32 with 3 square patches in paint_mustard and paint_teal), cloth_red cravat, a watch chain (brass) across the vest.
- The coat tails stop at the hip line and continue on the UpperLegs (split at the joint).
- Arms: coat sleeves with turned-back cuffs; fingerless gloves.
- Legs: plain cloth_blue trousers, worn leather boots.
Accessories: Acc_Hat: battered tall top hat (cloth_black, crown 1.1 tall, slightly bent, with a feather in the band); Acc_Bottle: a tonic bottle held up in the right hand.
Eyes: separate object.
```

---

## 4. Enemigos

Fuente: `Enemigos del Western.md`, `Historia y la plata viva.md`. Los enemigos **no son de plata**: son gente del pueblo movida por ella; cuanto más se avanza, más plata llevan. Son Humanoids R15 (`D018`), con animaciones en el cliente.

- **Élites por dificultad** (rojo = más rápido, negro = blindado, verde = explota) **no son modelos nuevos**: son el mismo modelo recoloreado + aura (VFX). Por eso todo enemigo separa la ropa en materiales propios: se cambian los colores de los materiales, no la malla.
- **Rasgos de muerto comunes a todos:** piel `skin_dead`, ojeras y labios en `skin_dead_dark`, ropa rasgada con bordes en zigzag, una herida de mordida o de bala con `blood_dry`, sin vísceras expuestas (low poly y apto para Roblox).

### Caminantes (`Walker`): cuatro cuerpos, cuatro conversaciones

- Los cuatro comparten medidas y articulaciones (H = 5,2 y las alturas del Bloque D), así las animaciones y los overlays de plata sirven para todos. Cada uno se hace en **su propia conversación**: en la primera tanda se pidieron los cuatro juntos y cada uno salió con poco detalle.
- **Primero la imagen de concepto:** el segundo bloque de cada caminante va a un generador de imágenes; la imagen se adjunta en Claude Design junto con el prompt (Bloque A dice cómo usarla).
- Primera tanda (2026-10-28, en `enemies/WST_Enemy_Walker/`): estructura perfecta, aspecto de maniquí. Agrandar cabeza y manos en Blender mejoró poco; de ahí salieron el Bloque D nuevo y el Bloque H.

### `WST_Enemy_Walker_A` — Caminante A: hombre del pueblo

- **Bloques:** A + D + H · **Tris:** ≤ 1 800 · **Primer uso:** Dusty Gulch · **Ficha:** `Walker`

```
MODEL: WST_Enemy_Walker_A
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Walker body, shared by the four Walker variants (A, B, C and D are made in separate conversations with these exact numbers so animations and overlays fit all of them): H = 5.2 studs, average build, joint heights exactly as in the TYPE rules.
Walker_A, the townsman: cloth_white_D8D0BE shirt with the RIGHT sleeve torn off at the elbow in tatters; cloth_brown_6A4A32 vest missing two buttons, 0.03 proud of the shirt; two leather_dark_3F2516 suspender straps; cloth_blue_3E5468 trousers with the left leg torn to the knee showing a thin shin; bare left foot (boot lost) and a leather_dark_3F2516 right boot.
Damage: a bite with a missing chunk on the left forearm; the shirt ripped open at the chest showing 3 rib ridges; a missing left ear.
Acc_Hat: a crushed cloth_black_1F1C1B bowler hat with a dent, sitting crooked.
Every clothing color is its own material (elites recolor them).
```

```
CONCEPT IMAGE — paste into an image generator, then attach the image to the Claude Design conversation.
Stylized low-poly 3D game character concept, flat-shaded faceted polygons with hard edges, no textures, muted sunset-desert palette, Western horror tone. Two views of the same character side by side on a plain light grey background: orthographic FRONT view and THREE-QUARTER view, full body, neutral standing pose with the arms hanging straight down. Chunky stylized proportions: big head (one fifth of the body height), big blocky hands, thin forearms and shins, hunched rolled-forward shoulders, neck and head jutting forward.
Character: an undead 1870s frontier townsman zombie. Grey-green dead skin with bruises, deep dark eye sockets with small dull eyes, slack open jaw with jagged yellowed teeth, dry blood around the mouth. Dirty off-white shirt with the right sleeve torn off at the elbow in ragged tatters, ripped open at the chest showing ribs; brown vest missing buttons; suspenders; faded blue trousers with one leg torn to the knee; the left boot lost (bare grey foot); a crushed black bowler hat sitting crooked; a bite wound with a missing chunk on the left forearm; a missing ear.
Not cute, not chibi, not realistic. No text, no logos, no weapons, no scenery.
```

### `WST_Enemy_Walker_B` — Caminante B: mujer del pueblo

- **Bloques:** A + D + H · **Tris:** ≤ 1 800 · **Primer uso:** Dusty Gulch · **Ficha:** `Walker`

```
MODEL: WST_Enemy_Walker_B
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Walker body, shared by the four Walker variants (A, B, C and D are made in separate conversations with these exact numbers so animations and overlays fit all of them): H = 5.2 studs, average build, joint heights exactly as in the TYPE rules.
Walker_B, the townswoman: paint_cream_E3D6BC high-collar long-sleeve blouse torn open at the left shoulder; a cloth_red_8E2A22 shawl over the shoulders in tatters (on UpperTorso, 0.03 proud); an A-line cloth_brown_6A4A32 skirt modeled on LowerTorso, ending just above the knee joint line with a zig-zag hem; cloth_black_1F1C1B stockings on the legs with a hole showing a thin shin; laced leather_dark_3F2516 boots. Hair: hair_dark_2E241D bun half undone, with 3 loose strands as wedges (on Head).
Damage: a bite with a missing chunk on the right side of the neck; a broken finger on the left hand; dirt patches on the skirt. No hat.
Every clothing color is its own material (elites recolor them).
```

```
CONCEPT IMAGE — paste into an image generator, then attach the image to the Claude Design conversation.
Stylized low-poly 3D game character concept, flat-shaded faceted polygons with hard edges, no textures, muted sunset-desert palette, Western horror tone. Two views of the same character side by side on a plain light grey background: orthographic FRONT view and THREE-QUARTER view, full body, neutral standing pose with the arms hanging straight down. Chunky stylized proportions: big head (one fifth of the body height), big blocky hands, thin forearms and shins, hunched rolled-forward shoulders, neck and head jutting forward.
Character: an undead 1870s frontier townswoman zombie. Grey-green dead skin, deep dark eye sockets, slack jaw with jagged teeth, dry blood on the chin. Dark hair in a half-undone bun with loose strands; a high-collar cream blouse torn open at one shoulder; a tattered red shawl; a brown A-line skirt ending above the knees with a ragged zig-zag hem; torn dark stockings; laced boots; a bite wound on the neck.
Not cute, not chibi, not realistic, not sexualized. No text, no logos, no weapons, no scenery.
```

### `WST_Enemy_Walker_C` — Caminante C: peón de rancho

- **Bloques:** A + D + H · **Tris:** ≤ 1 800 · **Primer uso:** Red Mesa · **Ficha:** `Walker`

```
MODEL: WST_Enemy_Walker_C
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Walker body, shared by the four Walker variants (A, B, C and D are made in separate conversations with these exact numbers so animations and overlays fit all of them): H = 5.2 studs, average build, joint heights exactly as in the TYPE rules.
Walker_C, the ranch hand: canvas_CDBB97 work shirt ripped open down the chest showing 3 rib ridges, sleeves rolled, the left one torn; cloth_red_8E2A22 neckerchief; leather_6B3F24 chaps over cloth_blue_3E5468 trousers (chaps 0.03 proud) on the UpperLegs and LowerLegs; worn leather_dark_3F2516 boots.
Damage: a broken finger on the right hand; a missing right ear; a bite with a missing chunk on the right shoulder.
Acc_Hat: a sweat-stained cloth_brown_6A4A32 cowboy hat with a bite torn out of the brim.
Every clothing color is its own material (elites recolor them).
```

```
CONCEPT IMAGE — paste into an image generator, then attach the image to the Claude Design conversation.
Stylized low-poly 3D game character concept, flat-shaded faceted polygons with hard edges, no textures, muted sunset-desert palette, Western horror tone. Two views of the same character side by side on a plain light grey background: orthographic FRONT view and THREE-QUARTER view, full body, neutral standing pose with the arms hanging straight down. Chunky stylized proportions: big head (one fifth of the body height), big blocky hands, thin forearms and shins, hunched rolled-forward shoulders, neck and head jutting forward.
Character: an undead ranch-hand cowboy zombie. Grey-green dead skin, deep dark eye sockets, slack jaw with jagged teeth, a missing ear. Canvas work shirt ripped open showing ribs, rolled sleeves; red neckerchief; brown leather chaps over blue trousers; worn boots; a sweat-stained cowboy hat with a torn brim; a bite on the shoulder.
Not cute, not chibi, not realistic. No text, no logos, no weapons, no scenery.
```

### `WST_Enemy_Walker_D` — Caminante D: minero

- **Bloques:** A + D + H · **Tris:** ≤ 1 800 · **Primer uso:** mina · **Ficha:** `Walker`

```
MODEL: WST_Enemy_Walker_D
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Walker body, shared by the four Walker variants (A, B, C and D are made in separate conversations with these exact numbers so animations and overlays fit all of them): H = 5.2 studs, average build, joint heights exactly as in the TYPE rules.
Walker_D, the miner: canvas_CDBB97 shirt with rolled sleeves; cloth_blue_3E5468 bib overalls (0.03 proud) with the right strap snapped and dangling; soot (coal_1C1A19 flat insets) on the face and hands; heavy leather_dark_3F2516 boots; the right overall leg torn to the knee.
Damage: a bite with a missing chunk on the left shoulder; a broken finger; the lower lip torn away showing the teeth.
Acc_Hat: a soft cloth_brown_6A4A32 felt miner's hat with an iron_3B3A3A tin candle holder on the front, no candle.
Every clothing color is its own material (elites recolor them).
```

```
CONCEPT IMAGE — paste into an image generator, then attach the image to the Claude Design conversation.
Stylized low-poly 3D game character concept, flat-shaded faceted polygons with hard edges, no textures, muted sunset-desert palette, Western horror tone. Two views of the same character side by side on a plain light grey background: orthographic FRONT view and THREE-QUARTER view, full body, neutral standing pose with the arms hanging straight down. Chunky stylized proportions: big head (one fifth of the body height), big blocky hands, thin forearms and shins, hunched rolled-forward shoulders, neck and head jutting forward.
Character: an undead 1870s silver miner zombie. Grey-green dead skin smeared with black soot, deep dark eye sockets, slack jaw with jagged teeth, the lower lip torn away. Canvas shirt with rolled sleeves; blue bib overalls with one strap snapped and dangling; heavy boots; one trouser leg torn to the knee; a soft felt miner's hat with a tin candle holder; a bite wound on the shoulder.
Not cute, not chibi, not realistic. No text, no logos, no weapons, no scenery.
```

### `WST_Overlay_SilverEyes` — Variante: brillo en los ojos

- **Bloques:** A + G · **Tris:** ≤ 60 · **Primer uso:** Dusty Gulch · **Ficha:** variante `SilverEyes` · Se pide en la misma conversación del Caminante A, con el cuerpo ya aprobado

```
MODEL: WST_Overlay_SilverEyes
TRIANGLE BUDGET: <= 60 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Living-silver overlay for the Walker head (H = 5.2 studs body). Build it on the Walker_A body already in this conversation, so it fits that exact head.
- Silver_Eyes: two replacement eye insets exactly the size and position of the base Eyes object, in silver_neon_7FE6FF.
- Silver_Tears: two thin vein lines (0.05 wide) running down from each eye 0.25 studs onto the cheeks, like glowing tear tracks, silver_neon_7FE6FF.
Only these two objects. Origin and position: the same as the Walker Head.
```

### `WST_Overlay_SilverVeins` — Variante: vetas en la piel

- **Bloques:** A + G · **Tris:** ≤ 400 · **Primer uso:** Red Mesa · **Ficha:** variante `SilverVeins` · Se pide en la misma conversación del Caminante A, con el cuerpo ya aprobado

```
MODEL: WST_Overlay_SilverVeins
TRIANGLE BUDGET: <= 400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Living-silver overlay for the Walker body (H = 5.2 studs), on top of the SilverEyes overlay. Build it on the Walker_A body already in this conversation, so it fits that exact body.
Vein objects, one per body part they sit on, named Silver_<BodyPart>:
- Silver_Head: veins climbing from the neck up the left side of the face to the temple, branching 3 times.
- Silver_UpperTorso: a vein trunk from the bite wound area on the right shoulder spreading over the collarbone and down the chest under torn clothing.
- Silver_RightUpperArm, Silver_RightLowerArm, Silver_RightHand: veins running down the right arm to the knuckles, getting thinner.
- Silver_LeftLowerArm: a short branch on the left forearm.
Veins only on visible skin and through tears in the clothing, never on top of intact cloth. Positions match the Walker body parts exactly.
```

### `WST_Overlay_SilverCrust` — Variante: costras de plata

- **Bloques:** A + G · **Tris:** ≤ 600 · **Primer uso:** Hollow Creek · **Ficha:** variante `SilverCrust` · Se pide en la misma conversación del Caminante A, con el cuerpo ya aprobado
- El vault no cierra si las costras son de caminantes comunes o solo de jefes; este overlay sirve para los dos casos.

```
MODEL: WST_Overlay_SilverCrust
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Living-silver overlay for the Walker body (H = 5.2 studs), heaviest stage, on top of SilverVeins. Build it on the Walker_A body already in this conversation, so it fits that exact body.
Crust objects (silver_crust_B9C3CC with silver_neon_7FE6FF seams between plates), named Silver_<BodyPart>_Crust:
- Silver_Head_Crust: angular crystal plates covering the left half of the scalp and left cheek, 3 short shard spikes (0.3) growing up from the left temple.
- Silver_UpperTorso_Crust: plates over the right shoulder and shoulder blade, breaking through the clothing, with a cluster of 4 shards (0.4) on the shoulder top.
- Silver_RightLowerArm_Crust: a crystalline sleeve wrapping the right forearm, jagged at both ends.
- Silver_LeftUpperLeg_Crust: one plate patch on the outer left thigh.
Every crust piece follows the body surface and ends inside its own segment (never crosses a joint).
```

### `WST_Enemy_Runner` — Corredor

- **Bloques:** A + D + H · **Tris:** ≤ 1 400 · **Primer uso:** Dusty Gulch, oleada 2 · **Ficha:** `Runner`
- Rápido y frágil, flanquea: la silueta tiene que ser distinta del caminante (flaco, piernas largas, sin sombrero).

```
MODEL: WST_Enemy_Runner
TRIANGLE BUDGET: <= 1400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Undead runner: a fast, fragile infected young man, lean and long-limbed. H = 5.4 studs, but torso and limbs 0.8x as thick as the Walker; legs 5% longer (hip at 0.50 H).
- Head: gaunt, jaw slightly open (modeled open), hair_dark long messy hair, skin_dead_9AA08C, Eyes object dark.
- UpperTorso: shirt (cloth_white) ripped open and hanging in strips, ribs suggested by 3 shallow horizontal ridges, bite wound on the neck.
- Arms: bare, long, fingers modeled as 2 claw-like blocks per hand (thumb + fingers).
- Legs: torn cloth_blue trousers cut off below the knee, barefoot with long toes as 1 wedge per foot.
No hat, no accessories. Separate clothing materials for elite recolors.
```

### `WST_Enemy_BloatedMiner` — Minero hinchado

- **Bloques:** A + D + H + G · **Tris:** ≤ 1 800 · **Primer uso:** mina · **Ficha:** `BloatedMiner`
- Explota al morir: la panza agrietada que deja escapar luz de plata es el aviso visible (`Pilar - Animaciones de foco`: nada pega sin anticipación).

```
MODEL: WST_Enemy_BloatedMiner
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Bloated dead miner that explodes on death. H = 5.4 studs; UpperTorso and LowerTorso hugely distended: belly 3.2 studs wide and 2.6 deep, the overall silhouette like a barrel on legs. Arms and legs normal thickness, so the belly reads.
- Skin: skin_dead_9AA08C stretched and shiny over the belly, with deep cracks (zig-zag grooves 0.05 deep) across the belly and chest.
- Clothing: cloth_blue overalls burst open at the sides, one suspender snapped and hanging, canvas shirt torn over the belly.
- Head: small for the body, puffy cheeks, Eyes dark.
- Acc_Hat: miner's felt hat with tin candle holder.
Living silver (G): Silver_Cracks: neon silver_neon_7FE6FF fill inside each belly crack (the light leaking out); Silver_Pustules: 5 crystal pustules (silver_crust with neon tips, 0.25) on the belly and one on the neck.
```

### `WST_Enemy_DeadGunslinger` — Pistolero muerto

- **Bloques:** A + D + H · **Tris:** ≤ 1 700 · **Primer uso:** Dusty Gulch, oleada 3 (en un techo) · **Ficha:** `DeadGunslinger`
- Dispara desde techos y ventanas: silueta de cowboy recortada contra el cielo (sombrero ancho y abrigo).
- El vault no dice qué arma suelta. Lleva el modelo del arma de jugador como accesorio, así lo que cae es exactamente lo que tenía en la mano.

```
MODEL: WST_Enemy_DeadGunslinger
TRIANGLE BUDGET: <= 1700 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Dead gunslinger, a desiccated outlaw who still aims. H = 5.4 studs, gaunt.
- Head: skull-like face with skin_dead stretched tight, sunken cheeks, thin long hair (hair_grey), lower face covered by a cloth_red bandana mask tied behind the head, Eyes dark.
- UpperTorso: cloth_black shirt, leather_6B3F24 vest with a bullet hole and blood_dry around it, cartridge belt across the chest.
- Duster coat: canvas_CDBB97 dusty long coat ending at mid-thigh, split at the hip line onto the UpperLegs; torn and frayed hem.
- LowerTorso: gun belt with two holsters (both sides).
- Legs: dark trousers, leather_dark boots with spurs.
Accessories: Acc_Hat: wide flat-brim black hat (cloth_black, brim 2.0 wide), with a bullet hole; Acc_Weapon: an empty placeholder cube 0.1 at the right hand grip point (the actual player rifle/revolver model is attached in the engine).
```

### `WST_Enemy_ZombieRider` — Jinete zombie (jinete)

- **Bloques:** A + D + H · **Tris:** ≤ 1 600 · **Primer uso:** viaje a Red Mesa · **Ficha:** `ZombieRider`
- El jinete. El caballo zombie va en Transporte (`WST_Mount_ZombieHorse`), con el mismo esqueleto que el caballo del jugador.

```
MODEL: WST_Enemy_ZombieRider
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Undead rider: a dead cattle rustler who chases the group on horseback. H = 5.3 studs. Model him standing in I-pose like every humanoid (the riding pose is an animation).
- Head: skin_dead, missing lower jaw skin showing bone_E6DCC3 teeth on one side, Eyes dark.
- UpperTorso: tattered poncho (paint_mustard with cloth_red stripes as 2 raised bands) over a canvas shirt, ending at the hip line.
- Legs: leather chaps (leather_6B3F24) over cloth_blue trousers, boots with big spurs.
Accessories: Acc_Hat: sombrero-like wide hat with a tall crown (canvas_CDBB97, brim 2.2 wide, torn at the edge); Acc_Lasso: a coiled rope at the right hip.
```

### `WST_Enemy_ZombieBull` — Toro zombie

- **Bloques:** A + E + G · **Tris:** ≤ 2 200 · **Primer uso:** Red Mesa, presión final · **Ficha:** `ZombieBull`
- Embiste en línea recta y rompe paredes: cabeza y hombros enormes, cuernos que se leen de lejos. Se lo escucha antes de verlo (mugidos raros).

```
MODEL: WST_Enemy_ZombieBull
TRIANGLE BUDGET: <= 2200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Undead longhorn bull that charges and smashes walls. Body length 10 studs (nose to tail base), 5.8 studs tall at the shoulder hump, 3.4 wide. Horns span 6.5 studs tip to tip, curving forward and up.
Rest pose: standing square on four straight legs, head forward and slightly down toward -Z.
Objects (exact names): Torso, Neck, Head, Tail, FrontLeftUpperLeg, FrontLeftLowerLeg, FrontRightUpperLeg, FrontRightLowerLeg, BackLeftUpperLeg, BackLeftLowerLeg, BackRightUpperLeg, BackRightLowerLeg (hooves included in the lower legs). Left = -X, Right = +X.
- Massive shoulder hump and neck, thin hindquarters (the front is 1.6x the back), the silhouette of a battering ram.
- Hide: hide_brown_6A4430 with hide_white_D9D0C0 patches, torn open on the flank showing 4 bone_E6DCC3 ribs (no organs inside, just a dark skin_dead_dark cavity).
- Head: broad flat forehead (the impact surface) with a cracked bone plate, one broken horn tip, a rusty iron nose ring.
- Living silver (G): Silver_Veins spreading from the torn flank over the shoulders; Silver_Eyes in the eye sockets.
```

### `WST_Enemy_Vulture` — Buitre zombie

- **Bloques:** A + E · **Tris:** ≤ 400 · **Primer uso:** Hollow Creek · **Ficha:** `Vultures`
- Atacan en bandada (muchos a la vez): barato. El viento de Hollow Creek los arrastra.

```
MODEL: WST_Enemy_Vulture
TRIANGLE BUDGET: <= 400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Undead vulture, attacks in flocks. Wingspan 5 studs (oversized for readability), body 1.6 long, 0.9 tall.
Rest pose: wings fully spread flat and horizontal (like a T-pose), legs tucked, head forward toward -Z.
Objects (exact names): Body, Head (includes the long bare neck), WingLeftInner, WingLeftOuter, WingRightInner, WingRightOuter, Tail.
- Feathers: feather_black_2A2626 with jagged ragged trailing edges (5-7 long finger feathers at each wingtip, as one fan-shaped mesh with notches).
- Bare head and neck in vulture_skin_B5554A, hooked beak in bone_E6DCC3, a white ruff collar (hide_white) at the base of the neck.
- Holes in the wings (2 per wing, cut-through gaps) and exposed bone_E6DCC3 wing bones on the left inner wing.
- Eyes: silver_neon_7FE6FF tiny insets (separate object Silver_Eyes).
```

---

## 5. Jefes

Fuentes: nota de cada fase y `Jefes.md`. Todos humanoides en R15 escalado (el animador trabaja con un solo tipo de rig). El vault no da alturas: las de abajo son propuesta.

### `WST_Boss_Sheriff` — El Sheriff infectado

- **Bloques:** A + D + H + G · **Tris:** ≤ 3 500 · **Primer uso:** Dusty Gulch (mini-jefe) · **Ficha:** `Sheriff`
- Sale de la cárcel rompiendo la pared, dispara la escopeta, llama ayudantes; al 50% **pierde la placa** y carga. Cierre: "la estrella del sheriff cae al polvo". La placa es un objeto aparte.

```
MODEL: WST_Boss_Sheriff
TRIANGLE BUDGET: <= 3500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The infected Sheriff, a big imposing lawman turned undead. H = 6.2 studs, broad chest (torso 1.25x the default width), thick arms.
- Head: heavy jaw, long drooping walrus mustache (hair_grey), skin_dead_9AA08C, one cheek torn showing teeth, Eyes object.
- UpperTorso: cloth_white shirt, long cloth_black vest, a string tie; the vest's left chest has a mounting spot for the badge.
- Long frock coat (cloth_brown) ending at mid-thigh, split at the hip line onto the UpperLegs.
- LowerTorso: double gun belt, big brass buckle, a shotgun shell belt.
- Legs: dark trousers, tall boots with spurs.
Accessories (separate):
- Acc_Badge: a 6-pointed sheriff star (steel_light_A3A7AB, ball tips on each point, 0.45 across, 0.05 thick, blank center) pinned on the left chest. It must look good in close-up: allow 120 triangles for it alone.
- Acc_Hat: tall cattleman hat (cloth_black, brim 2.1 wide, pinched crown).
- Acc_Shotgun: a sawed-off double-barrel shotgun (short 0.9 barrels, iron/wood_dark) held in the right hand, with _Muzzle marker.
- Acc_Shackles: a broken pair of iron shackles hanging from the left wrist (he breaks out of his own jail).
Living silver (G): Silver_Eyes (the Dusty Gulch stage), plus thin Silver_Neck veins under the collar.
```

### `WST_Boss_Butcher` — El Carnicero del rancho

- **Bloques:** A + D + H + G · **Tris:** ≤ 3 800 · **Primer uso:** Red Mesa (mini-jefe) · **Ficha:** `Butcher`
- Sale del matadero arrastrando un gancho; lo lanza para atrapar y arrastrar; al 50% se prende fuego (VFX). La cadena lanzada es una cuerda del motor; el modelo trae el gancho y un tramo corto de cadena.

```
MODEL: WST_Boss_Butcher
TRIANGLE BUDGET: <= 3800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The ranch Butcher, a hulking infected slaughterman. H = 7.0 studs, enormous: torso 1.5x the default width, thick neck, huge forearms, short legs relative to the body (hip at 0.43 H).
- Head: small bald head on a thick neck, heavy brow, flat nose, skin_dead with skin_dead_dark mottling, Eyes object.
- UpperTorso: bare arms, a stained canvas undershirt under a long leather_dark_3F2516 butcher apron covered in blood_dry_5A1E18 splashes (as flat raised patches), apron continues on the UpperLegs below the hip line.
- Arms: bare and massive, rope tied around the right wrist, leather_dark gauntlet on the left forearm.
- Legs: rubber-looking boots (leather_dark), trousers.
Accessories (separate):
- Acc_Hook: a big iron meat hook (iron_3B3A3A, hook 1.2 tall, 0.12 thick, sharp point), with a 1.5-stud length of chain (6 chunky links as one mesh) attached to its top ring, held in the right hand. Markers: _HookTip at the point, _ChainEnd at the free end of the chain.
- Acc_Cleaver: a cleaver hanging from the apron belt on the left.
Living silver (G): Silver_Veins on both forearms and the left side of the neck (the Red Mesa stage), Silver_Eyes.
```

### `WST_Boss_Foreman` — El Capataz (jefe mediano)

- **Bloques:** A + D + H + G · **Tris:** ≤ 4 200 · **Primer uso:** mina · **Ficha:** `Foreman`
- Tira dinamita y derrumba el techo. Es la mina, el origen: más plata que los mini-jefes anteriores.

```
MODEL: WST_Boss_Foreman
TRIANGLE BUDGET: <= 4200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The mine Foreman, a brutal overseer consumed by the silver at its source. H = 6.4 studs, heavy-set, barrel chest.
- Head: thick graying mutton chops (hair_grey), bald top, a scar across the nose, Eyes object.
- UpperTorso: canvas shirt with rolled sleeves, leather_6B3F24 vest, a dynamite bandolier across the chest: 10 dynamite sticks (dynamite_red) in leather loops, from right shoulder to left hip.
- Pocket watch chain (brass) across the vest. Suspenders.
- Legs: cloth_blue heavy work trousers, steel-toed boots (iron caps).
Accessories (separate):
- Acc_Hat: hard felt miner's hat with a lit-candle holder (candle flame as a lamp_glow_FFC46B tiny teardrop, object Acc_Hat_Flame).
- Acc_Dynamite: a single dynamite stick in the right hand with fuse up (_Fuse marker).
- Acc_Whistle: a brass whistle on a chain on the chest.
Living silver (G): Silver_Veins over both arms, neck and face (left half); Silver_Crust: a crystal growth bursting through the back of the right shoulder (4 shards up to 0.6 long) and a crust plate on the left forearm.
```

### `WST_Boss_DoyleBrothers` — Hermanos Doyle (dos modelos)

- **Bloques:** A + D + H · **Tris:** ≤ 3 200 cada uno · **Primer uso:** Silver Bend (mini-jefe) · **Ficha:** `DoyleBrothers`
- Dos a la vez: uno cuerpo a cuerpo y otro a distancia; si muere uno, el otro entra en furia. Tienen que leerse como hermanos (mismo pelo, mismo pañuelo) y como opuestos (forma).
- El vault no fija la plata en Silver Bend; esta propuesta usa vetas como en Red Mesa.

```
MODEL: WST_Boss_DoyleBrothers
TRIANGLE BUDGET: <= 3200 triangles for each character. Hard cap: see the BUDGET rule in STYLE.
The Doyle Brothers, two outlaw brothers, infected. Make two separate characters in the same style; shared family traits: hair_red_8A3A1E hair and beards, the same freckled skin_dead_9AA08C skin, matching cloth_red bandanas, matching patched cloth_brown hats.
Doyle_Brute (melee): H = 6.6 studs, wide and heavy (torso 1.45x default width), short neck, huge fists.
- Big bushy red beard, broken nose. Plaid shirt done as flat color (cloth_red) with sleeves torn off, leather vest, bandana around the neck.
- Acc_Axe: a woodsman's felling axe (iron head, wood_mid handle 3.2 long) in the right hand. Acc_Hat: battered round-crown hat.
Doyle_Shooter (ranged): H = 5.6 studs, wiry and tall-looking (limbs 0.85x thickness).
- Thin long red ponytail and a goatee, bandana pulled over the nose. Long canvas duster to mid-thigh (split at the hip), two crossed bandoliers.
- Acc_Rifle: placeholder cube 0.1 at the right-hand grip (the player lever rifle model is attached in the engine). Acc_Hat: narrow-brim hat with a feather.
Both: Silver_Eyes and Silver_Veins on the hands and neck (separate objects, G block).
```

### `WST_Boss_Engineer` — El maquinista infectado

- **Bloques:** A + D + H + G · **Tris:** ≤ 3 400 · **Primer uso:** tren (mini-jefe) · **Ficha:** `Engineer`
- Aparece detrás de la caldera con la pala; palada de carbón en abanico, barrido que empuja al borde, vapor, furia al 50% en llamas. Muere sobre la palanca.

```
MODEL: WST_Boss_Engineer
TRIANGLE BUDGET: <= 3400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The infected locomotive engineer. H = 6.0 studs, stocky, long strong arms.
- Head: soot-blackened face (coal_1C1A19 patches over skin_dead), white goggles-tan around the eyes where the goggles were, thick dark mustache, Eyes object.
- UpperTorso: cloth_blue_3E5468 bib overalls over a canvas shirt, cloth_red neckerchief, a leather_dark tool belt.
- Arms: sleeves rolled, heavy leather_dark gauntlet gloves to mid-forearm, burn scars as skin_dead_dark patches.
- Legs: overalls, heavy boots.
Accessories (separate):
- Acc_Cap: plain paint_slate_6E7F8C engineer's cap with a puffy crown and a short visor.
- Acc_Goggles: brass_B8893A round goggles pushed up on the cap, glass_9FC7C9 lenses.
- Acc_Shovel: a coal shovel (iron blade 0.9 wide, 1.1 long, slightly scooped; wood_mid handle 3.0 long with a D-grip), held in both hands. Markers: _Grip (D-grip), _Grip2 (middle of the handle), _Blade (center of the blade).
Living silver (G): Silver_Veins on the neck and both forearms; Silver_Eyes.
```

### `WST_Boss_Preacher` — El Predicador (forma humana)

- **Bloques:** A + D + H + G · **Tris:** ≤ 4 500 · **Primer uso:** iglesia · **Ficha:** `Preacher`
- Ezekiel Crane: toca la campana desde el púlpito (fase 1), baja con revólveres dobles (fase 2), blande una cruz de hierro con la iglesia ardiendo (fase 3). "Casi hecho de plata".

```
MODEL: WST_Boss_Preacher
TRIANGLE BUDGET: <= 4500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Ezekiel Crane, the Preacher of Hollow Creek, servant of the living silver. H = 6.5 studs, tall and gaunt (limbs 0.85x thickness, long neck).
- Head: hollow cheeks, deep-set eyes, long straight grey hair (hair_grey) to the shoulders, clean-shaven, thin lips, skin_dead pale. Eyes object.
- UpperTorso: cloth_black frock coat buttoned high, cloth_white shirt collar with a black string tie; a small iron cross pendant on a chain on the chest.
- Coat tails end at mid-thigh, split at the hip line onto the UpperLegs; frayed and scorched hem.
- Arms: long sleeves, long thin fingers (fingers as 2 blocks per hand, extended), a rosary of silver beads wrapped around the left wrist.
- Legs: black trousers, black boots.
Accessories (separate):
- Acc_Hat: flat-crowned wide-brim preacher hat (cloth_black, brim 2.0 wide, perfectly flat).
- Acc_Bible: a thick black book held in the left hand, brass corners.
- Acc_RevolverL, Acc_RevolverR: two long-barrel revolvers with silver_crust frames and silver_neon inlay lines along the barrel (phase 2), each with a _Muzzle marker. Hidden until phase 2.
Living silver (G): heavy Silver_Veins over the face (both sides, converging on the forehead like a crown), the neck and both hands; Silver_Crust plates on the knuckles.
```

### `WST_Boss_Preacher_TrueForm` — El Predicador, verdadera forma

- **Bloques:** A + D + H + G · **Tris:** ≤ 6 000 · **Primer uso:** iglesia (reveal)
- **Decidido sin Valentin (2026-10-29, a revisar):** la verdadera forma es la forma "casi hecha de plata", como asume el prompt. Es la que encaja con "está casi hecho de ella" en la historia. Además, `Preacher_Transform` ya cambia a este modelo en `Swap` para la fase 3.

```
MODEL: WST_Boss_Preacher_TrueForm
TRIANGLE BUDGET: <= 6000 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The Preacher's true form, revealed: a body almost entirely made of living silver, still wearing the remains of his coat. Same R15 part names and I-pose. H = 7.8 studs (he grows), elongated limbs, shoulders 1.3x the human form.
- 70% of the body is silver_crust_B9C3CC crystalline plates with silver_neon_7FE6FF seams; the remaining skin_dead flesh shows only on the lower face and the left hand.
- Head: the face is a cracked silver mask on the right half; a halo-like crown of 7 thin silver shards (0.6-1.0 long) radiating from the back of the head. Eyes: silver_neon.
- UpperTorso: the black coat torn open; the ribcage is open in the middle of the chest, crystal ribs framing a separate object Silver_Heart: a faceted neon core (0.7 across, silver_neon) that will pulse like a heartbeat.
- Arms: the right forearm ends in long crystalline claw-fingers (3 shards, 0.8 long).
- Coat remnants: tattered cloth_black strips hanging from the shoulders and hips (on UpperTorso and LowerTorso, stopping above the joints).
Accessories: Acc_IronCross: the phase-3 weapon — a heavy wrought-iron cross 4.5 studs tall, 2.4 wide arms, square 0.35 bars, flared tips, rusted (iron/rust), with silver_crust growth creeping up from the foot. Held by the long bar. Markers: _Grip, _Grip2, _Tip (top end).
```

---

## 6. Transporte

Fuente: `Transporte del Western.md`, `Tramo - El tren.md`, `D002`, `D003`. El caballo y la carreta no usan ruedas físicas (raycasts): las ruedas se separan solo para girarlas visualmente. Marcadores `_Seat` donde se suelda cada jugador.

### `WST_Mount_Horse` — Caballo del jugador

- **Bloques:** A + E · **Tris:** ≤ 1 800 · **Primer uso:** salida de Dusty Gulch
- Las mejoras visibles (alforjas, armadura de cuero) son accesorios; las herraduras no se ven, se muestran en la UI.

```
MODEL: WST_Mount_Horse
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Riding horse for a player, Western quarter horse. Length 8 studs (nose to tail base), 4.4 studs at the withers, 2.0 wide.
Rest pose: standing square, legs straight, neck at 45 degrees, head forward toward -Z.
Objects (exact names): Torso, Neck, Head, Tail, FrontLeftUpperLeg, FrontLeftLowerLeg, FrontRightUpperLeg, FrontRightLowerLeg, BackLeftUpperLeg, BackLeftLowerLeg, BackRightUpperLeg, BackRightLowerLeg (hooves in the lower legs). Left = -X, Right = +X.
- Coat: hide_brown_6A4430 (bay) with hide_black_2A2220 mane (on Neck), tail, and lower legs (black "socks"); a hide_white blaze on the face. Keep the three coat colors as separate materials (recolor to black or paint horse).
- Head: bridle and bit in leather_6B3F24 built onto the Head; reins as a separate object Reins (two thin straps from the bit to the saddle horn).
Accessories (separate, in place):
- Acc_Saddle: western saddle with a horn, high cantle, stirrups (wood/leather) and a paint_red saddle blanket underneath.
- Acc_Saddlebags: upgrade "Saddlebags": two leather_dark bags hanging on both sides behind the saddle, buckled flaps. Hidden by default.
- Acc_LeatherArmor: upgrade "Leather Armor": a hardened leather_6B3F24 chest plate (peytral) across the chest, a neck guard of 3 overlapping leather plates on top of the neck, and a forehead plate (chanfron) with iron studs. Hidden by default.
Markers: _Seat at the top of the saddle seat (rider hip point).
```

### `WST_Mount_ZombieHorse` — Caballo zombie

- **Bloques:** A + E + G · **Tris:** ≤ 1 800 · **Primer uso:** viaje a Red Mesa · Lleva al `WST_Enemy_ZombieRider`; en el tren, los muertos suben desde estos caballos.

```
MODEL: WST_Mount_ZombieHorse
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Undead horse ridden by zombie riders. EXACTLY the same object names, proportions and joint positions as the player horse (8 long, 4.4 at the withers) so it reuses its animations.
- Emaciated: torso thinner (0.85x), hip bones and spine ridge sharp, 4 bone_E6DCC3 ribs exposed through torn hide on the left flank (dark skin_dead_dark cavity, no organs).
- Coat: hide_black_2A2220 patchy with skin_dead_9AA08C bald patches; mane and tail thin and ragged with gaps.
- Head: skin pulled back from the teeth (bone teeth visible), one ear torn.
- Tack: a rotted saddle (leather_dark, cracked, torn blanket) as Acc_Saddle, broken reins hanging as Reins.
- Living silver (G): Silver_Eyes; Silver_Veins spreading from the exposed ribs over the shoulder and up the neck.
Marker: _Seat on the saddle.
```

### `WST_Vehicle_Wagon` — Carreta para 4

- **Bloques:** A + B · **Tris:** ≤ 1 800 · **Primer uso:** viaje a Red Mesa (con 4 jugadores) · Fuente: "un jugador maneja la carreta mientras otros disparan"; baúl compartido
- Abierta (sin lona) para que los pasajeros disparen. La tiran dos caballos `WST_Mount_Horse`. La misma carreta, cargada, es la de la escolta de Red Mesa.

```
MODEL: WST_Vehicle_Wagon
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Open buckboard wagon for 4 players: 1 driver + 3 shooters. Bed 10 long (Z) x 5 wide x 1.0 thick, bed floor at 2.6 studs above ground. Front (-Z) has the driver's bench.
Objects (exact names):
- Body: plank bed with 1.6-tall side boards (players shoot over them), a raised driver's bench at the front (bench seat at 3.8 high, with a footboard), a hand brake lever on the right (+X) side of the bench, a tongue (draw pole) 6 long sticking out forward with a doubletree for 2 horses.
- WheelFL, WheelFR (front, 3.2 diameter), WheelBL, WheelBR (back, 3.8 diameter): wooden spoked wheels (12 spokes modeled as separate bars with open gaps between them, not a solid disc), iron_3B3A3A tire rims; pivot at each hub.
- Chest: a separate iron-banded wooden chest (the shared trunk) at the back of the bed, 3 x 1.6 x 1.6, Lid as a separate object (hinge at the back).
Materials: wood_mid, wood_dark (frame, axles), iron, paint_mustard faded on the side boards.
Markers: _Seat_Driver on the bench (left of center), _Seat_1, _Seat_2, _Seat_3 standing spots in the bed, _Hitch at the end of the tongue.
Variant WST_Vehicle_Wagon_AmmoLoad (same file, separate object Load): a load of 6 stacked ammunition crates and 2 powder kegs lashed with rope in the bed (Red Mesa escort).
```

### `WST_Vehicle_GatlingWagon` — Carreta con ametralladora Gatling (mejora final)

- **Bloques:** A + F · **Tris:** ≤ 1 500 (solo el arma y su montaje) · **Ficha:** `GatlingWagon`
- Es un agregado sobre `WST_Vehicle_Wagon`, no otra carreta.

```
MODEL: WST_Vehicle_GatlingWagon
TRIANGLE BUDGET: <= 1500 triangles for the gun and its mount. Hard cap: see the BUDGET rule in STYLE.
Gatling gun on a swivel mount, to be bolted to the back of the buckboard wagon.
Objects (exact names):
- Mount: an iron pedestal (1.2 tall) with a heavy round swivel base (1.4 diameter) bolted to a wooden plate.
- Body: the gun carriage: a brass_B8893A breech housing (box 1.0 x 0.8 x 1.2) with a crank on the right (+X) side and a hopper on top where the magazine seats.
- Magazine: the top-mounted gravity magazine (a vertical box 0.3 x 0.9 x 0.5) as its own object, lifted out and swapped on reload; origin at its bottom center.
- Barrels: a cluster of 6 barrels (gunmetal, 2.8 long) around a central axis, held by 2 round iron plates; pivot on the cluster's central axis (they spin).
- Crank: the side crank handle, pivot at its axle.
Muzzle toward -Z. Markers: _Muzzle at the barrel cluster center front, _Seat_Gunner behind the breech, _Mount at the bottom of the pedestal.
```

### `WST_Vehicle_PeddlerWagon` — Carreta del buhonero

- **Bloques:** A + B · **Tris:** ≤ 1 600 · Fuente: vendedor ambulante del Western ("buhonero con carreta")

```
MODEL: WST_Vehicle_PeddlerWagon
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Traveling peddler's covered wagon that opens into a shop.
Size: body 9 long x 5 wide, roof top at 8 studs. Front (-Z) has a small driver's bench.
Objects (exact names):
- Body: a box wagon with an arched wooden roof (not canvas), faded paint_teal side panels with paint_mustard trim, a stovepipe chimney on the roof, a back door, and hooks along the eaves with hanging pots, pans and bottles (simple shapes).
- Counter: the right (+X) side panel, hinged at its bottom edge, folds down to become a counter (pivot on the hinge). When up, it is flush with the wall.
- Awning: a single-color paint_red canvas awning above the counter, with a scalloped front edge, hinged at the roof edge.
- WheelFL, WheelFR, WheelBL, WheelBR: spoked wooden wheels (3.2 / 3.8 diameter), pivots at the hubs.
- SignBoard: blank board on top of the roof, 5 x 1.2 (text added in the engine).
Marker: _Shopkeeper standing spot next to the counter.
```

### `WST_Vehicle_MineCart` — Vagoneta

- **Bloques:** A + B · **Tris:** ≤ 600 · **Primer uso:** mina · Fuente: "un jugador empuja o maneja mientras otros disparan"; huida de la mina (`D003`)

```
MODEL: WST_Vehicle_MineCart
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Mine ore cart for two players: one drives/brakes, one shoots.
Size: tub 5 long (Z) x 3.4 wide x 2.4 tall (tub top at 3.2 above the rail tops), riding on rails with 3.0-stud gauge (wheel centers 3.0 apart in X).
Objects (exact names):
- Body: riveted iron tub (iron_3B3A3A with rust_7B4A2E patches), wider at the top than the bottom (tapered 10 degrees), a wooden frame underneath, a push bar at the back (+Z), a hand brake lever on the left (-X) back corner.
- Brake: the brake lever, pivot at its base.
- WheelFront, WheelBack: each an axle with 2 small flanged iron wheels (1.0 diameter), pivot on the axle.
Markers: _Seat_Driver (standing spot at the back inside the tub), _Seat_1 (front inside the tub), _RailGauge on the left wheel contact point.
```

### Tren

Por `D002`, el tren **no se mueve**: se mueve el escenario. Los vagones se pelean por arriba: techos caminables, ancho cómodo, pasarela. Escala ≈ 2,8 studs por metro. Una conversación por modelo, con la locomotora como referencia de estilo para el resto.

#### `WST_Train_Locomotive` — Locomotora

- **Bloques:** A + B · **Tris:** ≤ 6 000 en objetos de ≤ 5 000 · **Primer uso:** cinemática inicial; tren · Fuente: "llegar a la locomotora y echarle carbón"; "tira de la palanca"; "muere sobre la palanca"

```
MODEL: WST_Train_Locomotive
TRIANGLE BUDGET: <= 6000 triangles in total, at most 5000 per object. Hard cap: see the BUDGET rule in STYLE.
1870s American 4-4-0 steam locomotive (generic, no brand or number). Length 38 studs (cowcatcher tip to cab back), 8.5 wide, 15 tall to the top of the smokestack. Rails at y = 0, gauge 4.6 studs.
Objects (exact names):
- Boiler: long cylinder boiler (16-sided) in gunmetal with brass_B8893A bands, a tall diamond (funnel) smokestack in iron, a steam dome and a sand dome in brass, a bell on top (brass), a big box headlamp on the front with a lamp_glow lens (separate object Headlamp_Glow).
- Frame: the frame, cylinders, a red-painted (paint_red) cowcatcher (pilot) of slanted bars at the front, steps, running boards along both sides of the boiler (players walk on them, 1.2 wide).
- Cab: wooden cab (paint_red with wood_dark trim and a rounded roof) at the back, open at the back, 7 wide x 8 deep, windows on both sides, roof walkable. Inside: the boiler backhead with gauges (round brass discs), and a firebox door at floor level.
- FireboxDoor: separate, hinged on its left side, opens 90 degrees; behind it a lamp_glow glowing interior (object Firebox_Glow).
- Throttle: separate object — the big throttle lever ("the lever") on the backhead, right side, 1.8 long with a round grip; pivot at its base; swings 60 degrees back.
- DriveWheels: 4 big driving wheels (5.5 diameter, red-spoked) connected by side rods; one object, pivot at the center of the front axle (spin is faked).
- PilotWheels: 4 small front truck wheels, one object.
Markers: _CoalTarget at the firebox door, _ThrottleGrip, _Coupler at the back.
```

#### `WST_Train_Tender` — Ténder de carbón

- **Bloques:** A + B · **Tris:** ≤ 1 500

```
MODEL: WST_Train_Tender
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Coal tender behind the 4-4-0 locomotive. 20 long x 8.5 wide x 7.5 tall, rails at y = 0.
Objects: Body (paint_red sides with wood_dark trim, a water tank wrapping a coal bunker, a ladder at the back), Coal (a heaped pile of coal_1C1A19 in the open front bunker, faceted chunks, top reachable from the cab floor), Wheels (two 4-wheel trucks, one object), CouplerFront, CouplerBack.
Marker: _CoalPickup at the coal pile front edge.
```

#### `WST_Train_Boxcar` — Vagón de carga

- **Bloques:** A + B · **Tris:** ≤ 1 800 · Fuente: "combate sobre los techos y entre vagones"; "vagón de carga para reabastecerse"; "vagones desenganchables"

```
MODEL: WST_Train_Boxcar
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Wooden freight boxcar. Body 30 long x 8.5 wide; roof at 12 studs above the rails; a 2-wide wooden catwalk (running board) along the roof center, 0.2 above the roof. Rails at y = 0.
Objects (exact names):
- Body: vertical board siding (paint_red faded, 0.05 grooves), wood_dark frame, X-braced ends, iron ladders at two diagonal corners going to the roof, brake wheel on a post at one end of the roof.
- SlidingDoorL, SlidingDoorR: one big sliding door on each side, 6 wide x 8 tall, on an iron rail; they slide along Z.
- Wheels: two 4-wheel trucks, one object.
- CouplerFront, CouplerBack: separate link-and-pin couplers (they detach).
Interior: hollow, floor at 3.5 above the rails, so the door opening shows the inside (empty, for supply crates placed in the engine).
Markers: _Roof center of the catwalk; _Gap_Front, _Gap_Back at the coupler ends (where players jump between cars).
```

#### `WST_Train_StockCar` — Vagón de ganado (caballos)

- **Bloques:** A + B · **Tris:** ≤ 1 600
- **Decidido sin Valentin (2026-10-29, a revisar):** sí van. Por `D003`, los caballos de Dusty Gulch se pierden en la mina, pero "en Silver Bend se recupera transporte" (`D003` y [[Fase 4 - Silver Bend]]). Esos caballos son los que suben al tren, como dice §Estructura. Si se decide que no, el vagón igual sirve de decorado en la estación.

```
MODEL: WST_Train_StockCar
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Livestock car: same frame, size and roof/catwalk as the boxcar (30 x 8.5, roof at 12), but the sides are horizontal slats with 0.4 gaps between them (you can see horses inside), wood_light faded, one sliding door per side, a ramp object (Ramp, hinged at the door bottom). Objects: Body, SlidingDoorL, SlidingDoorR, Ramp, Wheels, CouplerFront, CouplerBack.
```

#### `WST_Train_Caboose` — Furgón de cola

- **Bloques:** A + B · **Tris:** ≤ 1 600

```
MODEL: WST_Train_Caboose
TRIANGLE BUDGET: <= 1600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Caboose at the end of the train. 22 long x 8.5 wide, roof at 11.5, with a raised cupola (6 long, 2.5 taller) in the middle with windows on all sides. Open platforms with railings at both ends, ladder to the roof, a red lantern (lamp_glow lens) hanging at the back. Objects: Body, Cupola, Wheels, CouplerFront, BackLantern_Glow.
```

#### `WST_Train_PassengerCar` — Vagón de preparación (escena de arranque)

- **Bloques:** A + B · **Tris:** ≤ 4 000 · **Primer uso:** vagón (countdown de 20 s) · Fuente: `Fase 0`, `Escena de arranque.md`
- Se juega **adentro**: hasta 4 jugadores + Old Hank, el armero y espacio para lucir cosméticos. Las lámparas se apagan al final.

```
MODEL: WST_Train_PassengerCar
TRIANGLE BUDGET: <= 4000 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
1870s wooden passenger car used as the playable preparation room. Exterior 34 long x 9 wide x 12 tall; interior floor at 3.5 above the rails, interior ceiling 7.5 above the floor (clerestory roof: a raised center strip with small windows).
Objects (exact names):
- Shell: exterior (paint_teal faded with paint_mustard trim and a blank paint_cream name panel along the side), interior walls in polished wood_mid with wood_dark trim, 8 windows per side (glass separate object Windows), doors at both ends onto open platforms.
- Interior: aisle 3 wide down the middle; 3 pairs of wooden benches with red (cloth_red) cushions on each side, but the middle 10 studs of the car are left EMPTY on one side for the gun rack and players to gather.
- LuggageRacks: overhead brass racks along both walls with a few suitcases and carpet bags.
- Lamps: 4 oil lamps hanging from the ceiling center, each with a separate glowing glass object Lamp_Glow_1..4 (lamp_glow), so they can be turned off.
- Floor: wood planks, a long cloth_red runner rug in the aisle.
Markers: _Hank at the end bench (where Old Hank sits), _Spawn_1.._Spawn_4 in the empty middle area, _Rack at the wall where the gun rack goes.
```

#### `WST_Prop_GunRack` — Armero del vagón

- **Bloques:** A + B · **Tris:** ≤ 1 500 · Fuente: "armero con revólveres, chalecos y sombreros"
- **Pendiente:** el vault no dice si los chalecos son cosmético o equipo. Acá son de exhibición; si se pueden vestir, se modelan aparte como ropa de avatar.

```
MODEL: WST_Prop_GunRack
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Wall-mounted outfitting rack inside the passenger car, 8 wide x 6 tall x 1.2 deep, against a wall (its back at +Z, front facing -Z).
- A wooden cabinet frame (wood_dark) with: a top shelf with 4 hats on pegs (cowboy hat shapes in cloth_brown, cloth_black, canvas, paint_red band variants), a middle row of 4 revolvers hanging on pegs by their trigger guards (objects Revolver_1..4, simple 400-tri versions of the frontier revolver), a bottom row of 4 leather vests on hangers (leather_6B3F24, cloth_brown alternating).
- Each revolver, hat and vest is a separate object (they disappear when taken): Revolver_1..4, Hat_1..4, Vest_1..4.
- A small blank sign board on top.
```

#### `WST_Train_Wreck` — Restos del descarrilamiento (Hollow Creek)

- **Bloques:** A + B · **Tris:** ≤ 7 000 en objetos de ≤ 5 000 · **Primer uso:** Hollow Creek (oleada 1: "supervivencia entre los restos del tren")
- Cobertura para pelear: los restos arman pasillos y alturas.

```
MODEL: WST_Train_Wreck
TRIANGLE BUDGET: <= 7000 triangles in total, at most 5000 per object. Hard cap: see the BUDGET rule in STYLE.
Wreck of the derailed train at the entrance of Hollow Creek, built from damaged versions of the same locomotive and boxcar designs (same colors and details), as separate objects:
- Wreck_Locomotive: the 4-4-0 lying on its right side, 30 degrees nose-down into the dirt, smokestack bent 40 degrees, cowcatcher crumpled, a burst panel on the boiler showing coal_1C1A19 inside, cab roof torn half off.
- Wreck_Tender: tipped 60 degrees, coal spilled in a heap (object Wreck_CoalSpill) beside it.
- Wreck_Boxcar_A: upright but jackknifed 35 degrees across the track, one end crushed, siding boards splintered (jagged plank ends) leaving a 3-wide hole you can walk through.
- Wreck_Boxcar_B: on its side, roof facing -Z, catwalk broken.
- Wreck_Rails: a 40-stud piece of track with rails peeled up and twisted, ties scattered.
- Wreck_Debris: 8 loose pieces (planks, a wheel set, a crate) as one object.
Charred areas use wood_charred_2B211C. Origin at the center of the whole wreck footprint; overall footprint about 60 x 30 studs.
```

---

## 7. Kit modular de edificios

Fuente: `Set dressing del Western.md`. Fachadas, techos, porches, carteles, ventanas y puertas **intercambiables y prefragmentadas**. Cada tramo combina piezas, colores desgastados y props desde listas del Chapter: por eso las paredes pintadas usan **un solo material de pintura** (`paint_cream` en el prompt) que el builder recolorea por edificio.

**Grilla del kit** (todas las piezas la respetan):

| Medida | Valor | Por qué |
|---|---|---|
| Ancho de módulo | 8 studs | 4 jugadores de ancho |
| Alto de planta | 10 studs | Puerta de 7,5 + dintel + viga |
| Espesor de pared | 0,6 studs | Fragmentos de al menos 0,4 |
| Puerta | 4 × 7,5 | Jugador de 5 con sombrero |
| Ventana | 3 × 4, alféizar a 3 studs | Se puede saltar por encima (`Movimiento`: vault sobre ventanas) |
| Baranda y cercas | 3 studs | Cobertura agachado y se salta por encima |
| Piso del porche | 1 stud sobre el suelo | Un escalón |

Una conversación por familia: se pide la primera pieza, se mide y después las variantes en el mismo hilo.

### `WST_Kit_Wall` — Paredes de tablas (familia)

- **Bloques:** A + C · **Fragmentos:** 6 · **Tris:** ≤ 400 por pieza

```
MODEL: WST_Kit_Wall
TRIANGLE BUDGET: <= 400 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Modular wooden wall pieces for western buildings. All pieces: 8 wide (X) x 10 tall (Y) x 0.6 thick (Z), origin at the bottom center, outside face toward -Z.
- Siding: horizontal clapboard boards 0.8 tall each with 0.06 overlapping steps; one painted material paint_cream_E3D6BC (recolored per building) on the outside, bare wood_mid on the inside face.
- Trim: wood_dark corner boards are NOT part of the wall (separate trim piece); a wood_dark sill board along the bottom.
- Wear: 2 boards per piece slightly tilted or missing a corner; paint chipped at the bottom edge (cut corners showing wood_mid).
Pieces (one per object group, each with its own frag01..frag06):
1. Wall_Plain: solid wall.
2. Wall_Window: with a window opening 3 wide x 4 tall, sill at 3, centered.
3. Wall_Door: with a door opening 4 wide x 7.5 tall, centered.
4. Wall_DoubleWindow: two window openings, 2.4 wide each.
5. Wall_Cracked: Wall_Plain already broken: a ragged 3 x 3 hole at chest height with splintered board ends (pre-broken state, fewer fragments: 4).
Fragments follow board seams and run diagonally through the openings; no fragment includes both sides of an opening.
```

### `WST_Kit_WallBrick` — Paredes de ladrillo (banco, hotel)

- **Bloques:** A + C · **Fragmentos:** 8 · **Tris:** ≤ 600 por pieza · **Primer uso:** Silver Bend (lado rico)

```
MODEL: WST_Kit_WallBrick
TRIANGLE BUDGET: <= 600 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Same 8 x 10 x 0.8 module and the same 4 variants (Plain, Window, Door, DoubleWindow), but brick: paint_red_9C3B2E brick color with brick courses suggested by 0.04-deep horizontal grooves every 0.5 studs and staggered vertical joints every 3rd course (no individual brick meshes). stone_grey_8C8273 lintels over openings and a stone_grey base course (0.8 tall).
Fragments (8) follow the brick courses in stair-step cracks.
```

### `WST_Kit_WallStone` — Pared de piedra (cárcel)

- **Bloques:** A + C · **Fragmentos:** 8 · **Tris:** ≤ 600 · **Primer uso:** Dusty Gulch (el Sheriff sale de la cárcel **rompiendo la pared**)

```
MODEL: WST_Kit_WallStone
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Jail wall of rough stacked stone blocks with mortar, 8 x 10 x 1.0.
- Irregular rectangular stones (stone_grey_8C8273, some ochre_C4893F) in uneven courses, mortar lines as 0.05 grooves, each stone face slightly angled for a faceted look.
- Variant Wall_Stone_Barred: a small high window 2 x 1.5 at 6.5 high with 3 iron bars.
Fragments (8) follow stone joints; the back wall that the Sheriff smashes must break into big satisfying chunks (each 1.5-3 studs).
```

### `WST_Kit_FalseFront` — Falsas fachadas

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 300 por pieza
- Los pistoleros disparan **desde los techos**: detrás de la falsa fachada hay techo plano caminable, y la fachada es la cobertura.

```
MODEL: WST_Kit_FalseFront
TRIANGLE BUDGET: <= 300 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Western false-front parapets that sit on top of a wall row, making the building look taller. Width 8 per module (they tile), thickness 0.6, origin at the bottom center, sitting at y = 0 of the piece (placed on top of the 10-tall wall).
- FalseFront_Flat: 4 tall rectangle with a projecting wood_dark cornice (0.4 out) at the top.
- FalseFront_Stepped: center rises 6 tall, sides step down to 4 and 3 (stepped silhouette).
- FalseFront_Arched: a shallow arch top, 4 tall at the sides, 5.5 at the center.
- FalseFront_Corner: corner end piece that returns 2 studs back along the side.
Same painted clapboard as the walls (paint_cream_E3D6BC recolorable), wood_dark cornice and trim. A blank sign band area 6 x 1.6 on the front face (slightly proud), where the store name decal goes.
Fragments (4) per piece.
```

### `WST_Kit_Door` — Puertas

- **Bloques:** A + C · **Tris:** ≤ 250 por pieza · Fuente: "puertas que se rompen de un disparo"; Dusty Gulch oleada 4 "rompen ventanas y puertas" + forcejeo para sostener la puerta

```
MODEL: WST_Kit_Door
TRIANGLE BUDGET: <= 250 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Doors that fit the 4 x 7.5 opening. Origin at the bottom of the hinge edge (pivot), door closed in the plane z = 0.
- Door_Plank: vertical plank door (wood_mid) with a Z-brace (wood_dark), iron strap hinges on the left (-X) and a simple latch; frag 4 (planks split vertically, the brace breaks in the middle).
- Door_Panel: store door with a lower wood panel and an upper glass window (glass separate object Glass, breaks as VFX), paint_teal frame; frag 4.
- Door_Saloon: swinging batwing saloon doors: two separate leaves DoorLeft and DoorRight, each 2 wide x 3.5 tall, mounted with their bottom at 2.0 above the floor, louvered (5 horizontal slats as raised bars), curved top edge; pivot at each outer edge. Not fragmented (they swing).
- Door_Frame: a wood_dark door frame with lintel to place in Wall_Door (fixed_Frame, not destructible).
```

### `WST_Kit_Window` — Ventanas

- **Bloques:** A + C · **Tris:** ≤ 250 por pieza

```
MODEL: WST_Kit_Window
TRIANGLE BUDGET: <= 250 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Window units for the 3 x 4 opening. Origin at the bottom center of the opening.
- Window_Sash: double-hung window: wood_dark frame (fixed_Frame), 4 glass panes as separate objects Pane_1..Pane_4 (glass_9FC7C9, they shatter as VFX), a muntin cross (part of fixed_Frame).
- Window_Shutters: same window plus two outside wooden shutters (ShutterL, ShutterR, paint_teal recolorable, louvered), pivot at their outer edges.
- Window_Broken: frame with 1 pane left and jagged glass shards (3 sharp triangles) stuck in the corners.
```

### `WST_Kit_Porch` — Porche (familia)

- **Bloques:** A + C · **Tris:** ≤ 400 por pieza · Fuente: el Sheriff en furia **rompe columnas del porche**

```
MODEL: WST_Kit_Porch
TRIANGLE BUDGET: <= 400 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Covered boardwalk porch modules that attach in front of the walls (toward -Z). Module 8 wide x 6 deep.
- Porch_Floor: planks running along X on joists, top at 1.0 above ground, front edge with a fascia board; frag 6 (plank groups).
- Porch_Step: 3 wide steps down from the porch floor to the ground (2 steps); frag 2.
- Porch_Column: square post 0.5 x 0.5, 9 tall (from the porch floor to the porch roof), with two small diagonal corner brackets at the top; frag 3 (snaps at 1/3 and 2/3 height with splintered ends). Origin at its base.
- Porch_Roof: a shed roof 8 x 6.5, sloping from 10 high at the wall to 9 high at the front, wood shingle rows as stepped strips (wood_dark), with a front beam; frag 4. When its columns break it falls.
- Porch_Railing: 8 long x 3 tall railing with a top rail, bottom rail and vertical balusters every 0.8; frag 4.
- Porch_HitchRail: a hitching rail 8 long x 3 tall in front of the porch (two posts and a log rail), frag 2.
```

### `WST_Kit_Roof` — Techos

- **Bloques:** A + C · **Tris:** ≤ 500 por pieza

```
MODEL: WST_Kit_Roof
TRIANGLE BUDGET: <= 500 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Roof pieces that sit on the 8-wide wall modules.
- Roof_Flat: a flat tar-and-plank roof 8 x 8 module, top at 0.4, with a low 0.6 lip on the edges that face out; walkable (gunmen stand here behind false fronts); frag 4.
- Roof_Gable: a gable roof section 8 long along the ridge, span 16 (8 per side), pitch 35 degrees, wood shingle rows as stepped strips (wood_dark / wood_mid alternating rows); frag 6 (3 per slope).
- Roof_GableEnd: the triangular gable wall (clapboard, paint_cream recolorable) to close a gable, 16 wide at the base; frag 4.
- Roof_Chimney: a brick chimney stack (paint_red brick grooves) 1.6 x 1.6 x 4; frag 3.
Charred variant (same file): Roof_Gable_Charred with holes and wood_charred_2B211C material (for after a fire).
```

### `WST_Kit_Trim` — Molduras y esquinas

- **Bloques:** A + B · **Tris:** ≤ 80 por pieza

```
MODEL: WST_Kit_Trim
TRIANGLE BUDGET: <= 80 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Non-destructible trim that hides the joints between modules.
- Trim_Corner: a wood_dark corner board 0.6 x 0.6 x 10 (two boards in an L), origin at its base.
- Trim_Belt: a horizontal belt course board 8 long x 0.4 tall x 0.15 deep for between floors.
- Trim_Cornice: a molded cornice strip 8 long x 0.6 x 0.5 (stepped profile).
All named fixed_<Name>.
```

### `WST_Kit_Sign` — Carteles

- **Bloques:** A + C · **Fragmentos:** 2 · **Tris:** ≤ 150 por pieza
- El texto ("SALOON", "GENERAL STORE", "JAIL"…) va como decal en Studio.

```
MODEL: WST_Kit_Sign
TRIANGLE BUDGET: <= 150 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Blank wooden signboards (text added in the engine as decals). All boards: a flat front face (paint_cream_E3D6BC, recolorable) inside a wood_dark raised border 0.15 wide.
- Sign_Band: 6 x 1.6 x 0.2 board that mounts flat on a false front.
- Sign_Hanging: 3 x 1.2 x 0.15 board hanging from an L-shaped iron bracket (fixed_Bracket) by two short chains; the board swings: pivot at the top center.
- Sign_Post: a board 2.5 x 1 on top of a 4-tall post (for roads and the station).
- Sign_Arrow: a pointed arrow-shaped board 3 x 0.8 on a post.
Each board breaks in 2 fragments along a diagonal crack.
```

### `WST_Kit_Barricade` — Barricadas improvisadas

- **Bloques:** A + C · **Fragmentos:** 3–6 · **Tris:** ≤ 300 por pieza · Fuente: narrativa ambiental ("barricadas improvisadas"); defensa con tiempo

```
MODEL: WST_Kit_Barricade
TRIANGLE BUDGET: <= 300 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Improvised barricades made by desperate townsfolk.
- Barricade_Window: 3-4 rough planks nailed diagonally and crossed over the 3 x 4 window opening (mounts on the outside face of Wall_Window), bent nails as tiny wedges; frag 3 (each plank).
- Barricade_Door: 5 planks nailed across the 4 x 7.5 door opening, uneven lengths; frag 5.
- Barricade_Street: a free-standing street barricade 8 wide x 3 tall: an overturned table, 2 crates, a wagon wheel and a sack pile wedged together (crouch cover); frag 6.
Materials: wood_light (fresh planks), wood_mid, canvas sacks, iron nails.
```

### `WST_Kit_Interior` — Piezas interiores comunes

- **Bloques:** A + B/C · **Tris:** ≤ 300 por pieza

```
MODEL: WST_Kit_Interior
TRIANGLE BUDGET: <= 300 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Interior modular pieces in the same 8-stud grid.
- Floor_Planks: 8 x 8 plank floor, 0.4 thick (not destructible, fixed_).
- Stairs: a straight wooden staircase rising 10 studs over 14 deep, 4 wide, with a simple railing on one side (fixed_).
- Balcony: an upper-floor exterior balcony 8 wide x 4 deep with railing and two support brackets, floor at 10; frag 4 (for saloon and hotel second floors).
- Partition: an interior wall 8 x 10 x 0.3 with wallpaper paint (paint_mustard recolorable) above a wood_mid wainscot at 3 high; frag 4.
```

---

## 8. Piezas únicas por tramo

Lo que no sale del kit: los lugares que nombran las fases y los objetos con los que se juega. Los edificios comunes (almacén, armería, establo de Dusty Gulch, casas de mineros) se arman con el kit.

### Dusty Gulch

#### `WST_DG_Station` — Estación de tren

- **Bloques:** A + B · **Tris:** ≤ 2 500 · Fuente: "estación vacía, calle silenciosa: falsa calma"

```
MODEL: WST_DG_Station
TRIANGLE BUDGET: <= 2500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Small frontier railway depot. Footprint 24 long (X) x 10 deep. A raised wooden platform 40 long x 8 deep, 1.2 high along the track side (+Z). A small depot building (16 x 8, one floor, board-and-batten siding in paint_mustard recolorable, wood_dark trim, a bay window facing the track for the station agent) with a wide overhanging roof covering the platform on brackets. A bench on the platform, a hand cart with luggage, a hanging blank station-name sign (Sign_Hanging style). Objects: Platform, Building, Roof, Bench, HandCart, Sign.
```

#### `WST_DG_WaterTower` — Tanque de agua del ferrocarril

- **Bloques:** A + B · **Tris:** ≤ 1 200

```
MODEL: WST_DG_WaterTower
TRIANGLE BUDGET: <= 1200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Railway water tower. A wooden barrel-shaped tank (wood_mid staves suggested by vertical grooves, 3 iron hoops) 8 diameter x 7 tall, on a timber trestle 10 tall (4 legs with X bracing), a conical shingle roof, and a swing-down spout (separate object Spout, pivot at its base) on the track side. A ladder up one leg. Origin at the center of the base.
```

#### `WST_DG_SaloonInterior` — Interior del saloon

- **Bloques:** A + C · **Tris:** ≤ 2 500 en total · Fuente: Dusty Gulch oleada 4, "aguantar en el saloon"

```
MODEL: WST_DG_SaloonInterior
TRIANGLE BUDGET: <= 2500 triangles in total. Hard cap: see the BUDGET rule in STYLE.
Saloon interior set, separate objects:
- BarCounter: a long bar 16 long x 4 tall x 2 deep, wood_dark top with a brass foot rail along the front, paneled front; frag 6.
- BackBar: a back wall shelf unit 12 wide x 7 tall with shelves of bottles (glass_amber / glass_green simple shapes) and a big blank mirror area (paint_slate flat panel) in the middle; frag 6.
- Table_Round: round card table 3.5 diameter on a single pedestal, with a few cards and chips (flat bits); frag 3.
- Chair: wooden saloon chair with a spindle back; frag 3.
- Chandelier: a wagon-wheel chandelier hanging from a chain with 6 oil lamps (each lamp glass a separate object Lamp_Glow_1..6, lamp_glow), pivot at the top of the chain (it can fall: environmental kill).
```

#### `WST_DG_JailInterior` — Celda de la cárcel

- **Bloques:** A + B · **Tris:** ≤ 1 200

```
MODEL: WST_DG_JailInterior
TRIANGLE BUDGET: <= 1200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Jail cell set: an iron bar cell front 8 wide x 9 tall (vertical bars 0.12 thick every 0.6, two horizontal bands), with a barred door (separate object CellDoor, 3 wide, pivot at its hinge, a big lock box); a wall-mounted plank bunk with a canvas blanket; a bucket; a desk with a blank wanted-poster pile and a ring of keys (object Keys). The cell door looks torn open in variant CellDoor_Broken (bent bars, hanging by one hinge).
```

#### `WST_DG_TelegraphDesk` — Mesa del telégrafo

- **Bloques:** A + B · **Tris:** ≤ 600 · Fuente: oleada 4, "mientras el telegrafista manda un mensaje"

```
MODEL: WST_DG_TelegraphDesk
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Telegraph operator's desk: a wooden desk 4 x 2.5 x 2.6 tall with: a brass telegraph key (separate object Key, its lever pivots), a sounder box, two glass battery jars (glass_green) with wires, a pad of blank telegram forms, an oil lamp (Lamp_Glow separate). A wall-mounted wire coil and insulator above the desk. Marker _Operator at the chair position.
```

#### `WST_DG_StoreShelves` — Estanterías (almacén y armería)

- **Bloques:** A + C · **Tris:** ≤ 800 por pieza

```
MODEL: WST_DG_StoreShelves
TRIANGLE BUDGET: <= 800 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Shop interior pieces:
- Shelves_General: a wall shelving unit 8 wide x 8 tall x 1.5 deep with cans, sacks (canvas), jars and folded cloth as simple shapes; frag 4.
- Counter_Store: a shop counter 8 x 3.5 x 2 with a brass cash register (blank), a scale and a glass display top; frag 4.
- GunDisplay_Wall: a wall rack 8 x 5 holding 4 long guns horizontally on pegs (simple 300-tri silhouettes of the lever rifle, double barrel, hunting rifle) and a row of revolvers; each gun a separate object Gun_1..Gun_6.
```

#### `WST_DG_SheriffStar` — Estrella del sheriff (cinemática)

- **Bloques:** A + B · **Tris:** ≤ 200 · Fuente: cierre de Dusty Gulch, "la estrella del sheriff cae al polvo" (primer plano)
- Versión de primer plano del `Acc_Badge` del Sheriff, para la escena de cierre.

```
MODEL: WST_DG_SheriffStar
TRIANGLE BUDGET: <= 200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Close-up hero version of the sheriff's 6-pointed star badge: 0.45 across, 0.06 thick, each point ending in a small ball, a raised inner ring and a blank center plate (for a decal). Slightly bent (one point bent 10 degrees), a dent and a bullet scratch groove. Material steel_light_A3A7AB with gunmetal in the grooves. Pin on the back. Up to 200 triangles: this one is seen full screen.
```

### Viaje a Red Mesa (cañón)

#### `WST_Canyon_Wall` — Paredes del cañón

- **Bloques:** A + B · **Tris:** ≤ 1 500 por módulo · Fuente: "a caballo por un cañón"; "corredores bajan por las laderas"

```
MODEL: WST_Canyon_Wall
TRIANGLE BUDGET: <= 1500 triangles per module. Hard cap: see the BUDGET rule in STYLE.
Modular red-rock canyon wall that tiles along a road. Module 32 long (X) x 30 tall x 12 deep; the left and right ends (x = -16 and x = +16) have matching profiles so modules connect seamlessly.
- Layered sandstone strata: horizontal bands 2-4 tall alternating redrock_A8452E, ochre_C4893F, redrock_dark_6E2A1F, with each band slightly stepped in or out (0.3-1.0) for a faceted, eroded look.
- The lower 8 studs slope at 55 degrees (a scree slope enemies can run down), the upper part near-vertical with 2 ledges.
- Variants (same file): Canyon_Wall_A (straight), Canyon_Wall_B (with a side gully runners can come down), Canyon_Wall_C (inner corner 30 degrees).
Origin at the bottom center of the road-facing edge; road side toward -Z.
```

#### `WST_Canyon_Rockslide` — Derrumbe que bloquea el camino

- **Bloques:** A + C · **Fragmentos:** 8 · **Tris:** ≤ 1 200 · Fuente: "rocas que caen… despejar con dinamita"

```
MODEL: WST_Canyon_Rockslide
TRIANGLE BUDGET: <= 1200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A rockslide blocking the canyon road, cleared with dynamite. A pile of 8 large angular boulders (each 2.5-5 studs, faceted, redrock / ochre / redrock_dark) heaped against each other, 16 wide x 7 tall x 8 deep, too high to ride over. Each boulder is a fragment (frag01..frag08), roughly convex. A marker _ChargeSpot at the base center of the pile where the dynamite goes.
```

#### `WST_Canyon_Boulders` — Rocas sueltas

- **Bloques:** A + B · **Tris:** ≤ 150 por roca

```
MODEL: WST_Canyon_Boulders
TRIANGLE BUDGET: <= 150 triangles per rock. Hard cap: see the BUDGET rule in STYLE.
6 loose desert boulder variants in one file (Boulder_S1, S2 ~1.5 studs; M1, M2 ~3.5; L1, L2 ~7), angular faceted low-poly rocks, flat-ish bottoms, strata hint (one band of a second color) on the larger ones. Colors from redrock, ochre, redrock_dark, sand.
```

#### `WST_Canyon_BrokenBridge` — Puente roto del cañón

- **Bloques:** A + C · **Fragmentos:** 6-8 · **Tris:** ≤ 2 500 · Fuente: "rocas que caen o un puente roto; hay que bajar, despejar con dinamita y volver a montar"
- **Decidido sin Valentin (2026-10-29, a revisar):** el puente no se cruza por arriba. El camino del cañón va por el fondo del barranco y pasa por debajo, y lo que se derrumbó del medio cayó sobre el camino y lo tapa. Es el mismo obstáculo que el derrumbe (`WST_Canyon_Rockslide`): se baja del caballo, se vuela con dinamita y se sigue. El viaje usa uno de los dos.

```
MODEL: WST_Canyon_BrokenBridge
TRIANGLE BUDGET: <= 2500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A wooden railway-style trestle bridge over a dry ravine, broken in the middle, whose fallen middle blocks the canyon road that runs along the ravine floor UNDER the bridge; the debris is cleared with dynamite. Span 32 long (along X) x 6 wide deck, deck at 14 above the ravine floor. Timber trestle bents (4 legs with X bracing) every 8 studs. The middle 8 studs have collapsed: deck planks hanging down at angles from both broken ends, a broken stringer dangling. The road runs along Z through the middle of the span, so the collapsed section fell onto it: two knocked-over bents lying across the road, broken stringers and deck planks heaped against them, a tangle 16 wide (along X) x 5 tall x 8 deep, too high to ride over. Each fallen piece group is a fragment (frag01..frag06 to frag08), roughly convex. The standing parts leave the road clear (no bent stands in the middle 8 studs) and stay after the blast: fixed_DeckLeft, fixed_DeckRight (each with its hanging planks and dangling stringer), fixed_Bents (all standing bents, one object). The collapsed debris is frag01..frag0N. Marker _ChargeSpot at the base center of the debris on the route side (-Z), where the dynamite goes.
```

#### `WST_Bg_Mesa` — Mesas de fondo

- **Bloques:** A + B · **Tris:** ≤ 300 por pieza

```
MODEL: WST_Bg_Mesa
TRIANGLE BUDGET: <= 300 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Background skyline silhouettes (never reached by players): 4 variants of flat-topped mesas and buttes, 60-150 studs wide and 40-80 tall, extremely simple faceted shapes with 2-3 strata bands (redrock / ochre / redrock_dark), sheer sides and a talus slope at the base. Under 300 triangles each.
```

### Red Mesa (rancho)

#### `WST_RM_Barn` — Granero (arde y colapsa)

- **Bloques:** A + C · **Fragmentos:** 8 por pieza · **Tris:** ≤ 5 000 en total · Fuente: defensa en el granero (oleada 3); cierre "el granero colapsa entre llamas"

```
MODEL: WST_RM_Barn
TRIANGLE BUDGET: <= 5000 triangles in total. Hard cap: see the BUDGET rule in STYLE.
Big ranch barn that burns and collapses. Footprint 24 wide (X) x 32 long (Z), walls 12 tall, gambrel roof peaking at 24. Front gable faces -Z with big double sliding doors 8 x 10 and a hayloft door above.
Built as big destructible pieces, each with up to 8 fragments:
- Barn_WallSide_L, Barn_WallSide_R: vertical board-and-batten walls (paint_red_9C3B2E faded, wood_dark battens), 2 small windows each.
- Barn_Gable_Front (with DoorL, DoorR as separate sliding doors and HayloftDoor hinged), Barn_Gable_Back.
- Barn_Roof_L, Barn_Roof_R: gambrel roof halves, wood shingles as stepped strips.
- Barn_Loft: interior hayloft floor at 12 with a ladder, hay bales on it.
- fixed_Frame: the heavy timber frame (posts and beams) that stays standing as a charred skeleton after the collapse.
Charred material variant for every piece (wood_charred_2B211C). White trim (paint_cream) X-braces on the big doors.
```

#### `WST_RM_Stable` — Establo (rescate de caballos)

- **Bloques:** A + C · **Tris:** ≤ 3 500 · Fuente: oleada 2, "liberar los caballos del establo en llamas"

```
MODEL: WST_RM_Stable
TRIANGLE BUDGET: <= 3500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Long wooden horse stable, 32 long (X) x 12 deep, shed roof sloping from 10 to 8. Open front (-Z) with 6 stalls, each 5 wide, separated by plank partitions 5 tall.
- Each stall has a Dutch half-door (StallDoor_1..StallDoor_6, two-part doors: bottom half 4 tall, pivot on the left edge) that players open to free the horse.
- Walls: board-and-batten wood_mid, roof shingles wood_dark. Hay racks and water buckets in each stall.
- Destructible pieces: back wall frag 8, roof frag 8, partitions frag 2 each. Charred variant for all pieces.
Markers: _Horse_1.._Horse_6 at the center of each stall.
```

#### `WST_RM_Slaughterhouse` — Matadero

- **Bloques:** A + B · **Tris:** ≤ 2 500 · Fuente: "el Carnicero sale del matadero arrastrando un gancho"

```
MODEL: WST_RM_Slaughterhouse
TRIANGLE BUDGET: <= 2500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Small slaughterhouse building: 16 x 12, walls 10, gable roof. Front (-Z) has a wide double door 6 x 8 (DoorL, DoorR separate, pivots at their outer edges) that the Butcher bursts through. Siding wood_mid, stained dark at the bottom (wood_dark band). Inside: an overhead iron rail with 4 hanging meat hooks on trolleys (Hooks object), sides of meat wrapped in canvas hanging from 2 of them (simple wrapped shapes, no gore), a chopping block with a cleaver, a drain channel in the floor. A blank sign over the door.
```

#### `WST_RM_WaterMill` — Molino de agua

- **Bloques:** A + B · **Tris:** ≤ 2 500 · Fuente: oleada 3, "se carga el molino de agua para apagar el fuego"

```
MODEL: WST_RM_WaterMill
TRIANGLE BUDGET: <= 2500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Ranch water mill on a creek. A stone-base mill house (12 x 10, stone_grey base 3 tall, wood_mid upper walls, shingle roof) with a big wooden overshot waterwheel on its side.
Objects (exact names):
- MillHouse: the building.
- Wheel: waterwheel 12 diameter, 3 wide, 16 buckets, iron hub; pivot on its axle (it rotates, faster as it "charges").
- Flume: an elevated wooden water chute on trestles bringing water to the top of the wheel, 16 long, with a water surface (water_5E8F96).
- SluiceLever: a big wooden lever on the flume that opens the gate; pivot at its base.
- Pipe: a wooden pipe/trough line running 20 studs from the mill toward the barn, ending in a spout (marker _WaterOut).
```

#### `WST_RM_Corral` — Corrales y portones

- **Bloques:** A + C · **Fragmentos:** 3 · **Tris:** ≤ 200 por módulo

```
MODEL: WST_RM_Corral
TRIANGLE BUDGET: <= 200 triangles per module. Hard cap: see the BUDGET rule in STYLE.
Ranch corral fencing in the 8-stud grid.
- Corral_Rail: 8 long split-rail fence, 3 rails, posts at the ends, 3.2 tall; frag 3 (rails break).
- Corral_Gate: 8-wide swinging gate with Z-brace, pivot at the left post (separate object Gate).
- Corral_Corner: a corner post with rails in an L.
- Corral_Chute: a narrow cattle chute section 8 long x 3 wide with high plank walls 5 tall.
Wood: wood_light weathered, wood_mid posts.
```

#### `WST_RM_Diary` — Diario de minero (narrativa)

- **Bloques:** A + B · **Tris:** ≤ 120 · Fuente: "diarios sobre mineros que brillaban" (Red Mesa)
- **Pendiente:** el vault no dice si son coleccionables o notas en el mapa. Sirve igual como prop.

```
MODEL: WST_RM_Diary
TRIANGLE BUDGET: <= 120 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A worn leather journal lying open, 0.9 x 0.6 open, 0.15 thick: leather_dark covers, paint_cream pages (blank, for a decal), a pencil on top, a faint silver_neon_7FE6FF smudge (fingerprint-sized flat inset) on one page edge.
```

### Mina de plata

Perfil `Mine`: cámara más cerrada, combate cercano, oscuridad. Las vetas de plata **marcan el camino**: tienen que verse en la oscuridad.

#### `WST_Mine_Entrance` — Boca de la mina

- **Bloques:** A + B · **Tris:** ≤ 1 500

```
MODEL: WST_Mine_Entrance
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Mine portal set into a red rock cliff face. A timber-framed entrance 10 wide x 9 tall (heavy square timbers 0.8, a header beam with a blank plank sign above), the rock face around it (a 30 x 20 rock wall chunk, faceted redrock/ochre). Rails run out of the entrance. A rusty ore cart and a pile of tailings (grey-ochre gravel heap) outside. Two hanging lanterns (Lamp_Glow_1, _2). Objects: Frame, RockFace, Tailings, Lanterns.
```

#### `WST_Mine_Elevator` — Montacargas

- **Bloques:** A + B · **Tris:** ≤ 1 800 · Fuente: "se baja en un montacargas que cruje" (cinemática)

```
MODEL: WST_Mine_Elevator
TRIANGLE BUDGET: <= 1800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Mine shaft elevator (cage) for 4 players + cinematic.
Objects (exact names):
- Headframe: a timber headframe tower 18 tall over a square shaft opening 9 x 9, with a big pulley wheel at the top.
- Pulley: the pulley wheel (5 diameter, spoked), pivot on its axle.
- Cage: the cage platform 8 x 8 with plank floor, iron corner posts, a half-height railing on 3 sides, a top frame with the cable attachment. Origin at the center of the cage floor.
- CageGate: a sliding mesh gate on the open side (iron lattice as crossing bars), slides along X.
- Cable: two iron cables from the cage top to the pulley.
- ShaftWalls: a 9 x 9 x 30-deep shaft lining with horizontal timber cribbing every 4 studs.
```

#### `WST_Mine_Tunnel` — Túneles (familia modular)

- **Bloques:** A + B · **Tris:** ≤ 1 200 por módulo

```
MODEL: WST_Mine_Tunnel
TRIANGLE BUDGET: <= 1200 triangles per module. Hard cap: see the BUDGET rule in STYLE.
Modular mine tunnels, interior spaces (players are inside). Grid: tunnel cross-section 8 wide x 8 tall at the center; modules 16 long; ends at z = -8 and z = +8 share the same profile so modules connect seamlessly. Origin at the floor center.
- Rock shell: rough faceted rock (redrock_dark / stone_grey / ochre in irregular patches), 1.5 thick, irregular cross-section (not a perfect arch), floor flat with packed dirt (ochre_C4893F).
- Timber sets: every 4 studs a timber frame (two posts + a cap beam, wood_dark, 0.6 square) following the tunnel shape.
- Rails embedded in the floor along the center (3.0 gauge, iron rails on wood ties).
Pieces: Tunnel_Straight, Tunnel_Curve90 (inner radius 12), Tunnel_T, Tunnel_Narrow (6 wide x 7 tall, no rails, for close combat), Tunnel_End (dead end with a collapse).
```

#### `WST_Mine_Gallery` — Galería amplia

- **Bloques:** A + B · **Tris:** ≤ 4 000

```
MODEL: WST_Mine_Gallery
TRIANGLE BUDGET: <= 4000 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A large mine gallery (open cave chamber worked by miners), 40 x 40 floor, ceiling 20-24 high, irregular faceted rock walls. Two tunnel openings that match the 8 x 8 tunnel profile on opposite sides. Wooden scaffolding along one wall (two levels at 6 and 12 high, with ladders and a walkway: platforms enemies and players can use). Rails crossing the gallery on a low trestle. A few support pillars of stacked timber cribbing (4 x 4). Objects: Shell, Scaffolding, RailTrestle, Pillars.
```

#### `WST_Mine_Shaft` — Pozo vertical (los caminantes trepan)

- **Bloques:** A + B · **Tris:** ≤ 800 · Fuente: "caminantes que trepan por los pozos"

```
MODEL: WST_Mine_Shaft
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A vertical shaft opening in the floor of a tunnel or gallery: a 6 x 6 hole with a low timber collar (0.8 tall), going 30 studs down, lined with timber cribbing every 4 studs, a wooden ladder on one side (rungs every 1.2), a broken windlass over it. The walls must have climbable-looking hand holds (protruding cribbing ends). Origin at the center of the opening, at floor level.
```

#### `WST_Mine_SupportBeam` — Viga que se sostiene (derrumbe)

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 300 · Fuente: "sostener una viga con forcejeo mientras pasan los compañeros"

```
MODEL: WST_Mine_SupportBeam
TRIANGLE BUDGET: <= 300 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A collapsing tunnel support set that a player holds up. A timber frame matching the tunnel profile (two posts + cap beam), where the left post has snapped: the cap beam sags down on the left side to 5 studs high.
- CapBeam: separate object, pivot at its right end (it rotates up when held).
- PostRight: fixed_PostRight.
- PostLeftBroken: 2 fragments (splintered top and bottom stub).
- Rubble: loose rocks on top of the cap beam, 2 fragments that fall when released.
Marker _HoldPoint under the sagging end of the cap beam, at 4.5 high.
```

#### `WST_Mine_Rails` — Rieles (mina)

- **Bloques:** A + B · **Tris:** ≤ 150 por pieza

```
MODEL: WST_Mine_Rails
TRIANGLE BUDGET: <= 150 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Narrow-gauge mine rail pieces, gauge 3.0 between rail centers, rail height 0.3, wooden ties 3.8 long every 1.2.
Pieces: Rail_Straight (8 long), Rail_Curve (90 degrees, radius 12), Rail_Switch (Y split with a switch lever object SwitchLever, pivot at base), Rail_Bumper (end stop with a timber bumper), Rail_Ramp (rising 2 over 8).
iron_3B3A3A rails, wood_dark ties. Ends match exactly.
```

#### `WST_Mine_SilverVein` — Vetas de plata en la roca

- **Bloques:** A + B + G · **Tris:** ≤ 400 por pieza · Fuente: "las vetas de plata brillan y marcan el camino"; laten, más fuerte cerca de los jugadores

```
MODEL: WST_Mine_SilverVein
TRIANGLE BUDGET: <= 400 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Rock wall patches with living silver veins, to place on tunnel walls as path markers.
- Vein_Wall_A: a 6 x 4 faceted rock patch (redrock_dark / stone_grey), 0.5 thick, with a branching Silver_Veins object (silver_neon) running across it horizontally like a glowing root system, thick trunk 0.2 to thin points, pointing in one clear direction (along +X) so it reads as an arrow.
- Vein_Wall_B: same with a vertical branching pattern.
- Vein_Floor: a 3 x 3 floor patch with veins radiating from a small crystal cluster (Silver_Crust, 3 shards 0.5).
- Vein_Cluster: a free-standing crystal cluster 2 tall (Silver_Crust plates with silver_neon seams) growing out of a rock lump.
```

#### `WST_Mine_SilverHeart` — Corazón de plata de la galería central

- **Bloques:** A + B + G · **Tris:** ≤ 3 000 · Fuente: jefe del Capataz "en la galería central de plata"; "se descubre que la plata está viva y late"

```
MODEL: WST_Mine_SilverHeart
TRIANGLE BUDGET: <= 3000 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The heart of the silver: centerpiece of the central silver gallery. A huge geode-like growth bursting from the gallery wall and floor, 16 wide x 12 tall x 8 deep.
- Outer shell: cracked rock (redrock_dark / stone_grey) split open like a geode.
- Inner mass: dense silver_crust_B9C3CC crystal growth (hundreds of shards simplified into 30-40 big faceted prisms, 1-4 studs long) with silver_neon seams.
- Silver_Core: a separate object, a large faceted neon heart-like mass (3 across, silver_neon) deep in the center, visible through the crystal gaps — it pulses.
- Silver_Roots: 6 thick neon vein trunks spreading from the base across the floor and up the walls for 10-15 studs (separate object).
Origin at the floor center of the growth.
```

#### `WST_Mine_ExplosivesDepot` — Depósito de explosivos

- **Bloques:** A + C · **Tris:** ≤ 1 500 · Fuente: el Capataz "enciende la mecha de un depósito de explosivos: hay que apagarla o escapar"

```
MODEL: WST_Mine_ExplosivesDepot
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Powder magazine niche carved in the rock: a timber-framed alcove 8 wide x 7 tall x 6 deep, with a heavy plank door (DoorL, DoorR, hinged), inside: stacked dynamite crates (WST_Prop_DynamiteCrate style, 8 of them) and 3 powder kegs, a warning board (blank, warning_red border).
- Fuse: a separate object, a long fuse cord (rope_C2A36B, 0.06 thick) running from the stack 20 studs along the floor and wall, as a smooth path of segments, with markers _FuseStart (far end) and _FuseEnd (at the stack).
- Crates and kegs: frag 8 in total (they blow).
```

#### `WST_Mine_GasPocket` — Bolsa de gas

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 300 · Fuente: "bolsas de gas que explotan con disparos o fuego"
- El gas es VFX; esto es la roca que lo contiene y que tiene que avisar que se puede reventar.

```
MODEL: WST_Mine_GasPocket
TRIANGLE BUDGET: <= 300 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A swollen rock blister on a tunnel wall that holds explosive gas. 3 wide x 2.5 tall, bulging 1.5 out of the wall, faceted, with a network of cracks; the cracks are filled with a sickly glow — use paint_mustard_C9A23F as an inset material (it will be lit by VFX). Fragments (4) split along the cracks. Marker _GasVent at the biggest crack.
```

#### `WST_Mine_Rubble` — Escombros que forman cobertura

- **Bloques:** A + B · **Tris:** ≤ 400 por pieza · Fuente: el Capataz "derrumba partes del techo; los escombros forman nuevas coberturas"

```
MODEL: WST_Mine_Rubble
TRIANGLE BUDGET: <= 400 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Fallen-ceiling rubble piles used as new cover. 3 variants: Rubble_Low (6 x 2.5 x 3, crouch cover), Rubble_High (5 x 4.5 x 3, full cover), Rubble_Beam (a rubble pile with a broken timber beam sticking out at 30 degrees). Angular rock chunks, stone_grey / redrock_dark, plus dust (sand) at the base. Also a FallingChunk variant: a single 3-stud angular rock that falls from the ceiling (convex).
```

### Silver Bend

#### `WST_SB_Bridge` — Puente largo de madera (se rompe por pasos)

- **Bloques:** A + C · **Tris:** ≤ 800 por módulo · Fuente: `Fase 4 - Silver Bend.md` (contador de cruces, cada jugador rompe X piezas; si alguien cae, se cuelga de un escalón, tablón o pilar que quedó en pie)
- La pieza más importante del tramo. Cada tablón es un fragmento; largueros y pilotes quedan en pie para colgarse.

```
MODEL: WST_SB_Bridge
TRIANGLE BUDGET: <= 800 triangles per module. Hard cap: see the BUDGET rule in STYLE.
Modular long wooden bridge over a wide river, built from repeating modules that break plank by plank.
Module: 8 long (Z, along the crossing) x 7 wide (X); deck top at 0 (the module origin is at the deck top center); river surface 10 below.
- Planks: 10 transverse deck planks per module, each 7 long x 0.75 wide x 0.25 thick, 0.05 gaps between them, slightly uneven heights and tilts (weathered wood_light / wood_mid alternating). EACH PLANK IS ITS OWN FRAGMENT: frag01..frag10 (this module may exceed the 8-fragment rule; it's the exception).
- fixed_Stringers: 3 long beams under the planks (wood_dark, 0.6 x 0.8), running the full 8 length — they stay after the planks fall and are what a falling player hangs from.
- fixed_Pile: a pile bent at one end of the module: 2 round timber piles going down into the water (12 long) with a cross cap and X bracing.
- fixed_Railing: simple railing on both sides, 3.5 tall (posts every 4, one top rail); one side has a missing section.
Variants: Bridge_Module (normal), Bridge_Module_Damaged (3 planks already missing and one stringer cracked but standing), Bridge_Abutment (the stone-and-timber end that meets the riverbank, 8 long).
Markers: _Hang_1 .. _Hang_6 at both ends of each of the 3 stringers (where a falling player grabs).
```

#### `WST_SB_Dock` — Muelles

- **Bloques:** A + C · **Tris:** ≤ 600 por módulo · Fuente: "llegada a pie en los muelles" (lado pobre)

```
MODEL: WST_SB_Dock
TRIANGLE BUDGET: <= 600 triangles per module. Hard cap: see the BUDGET rule in STYLE.
River dock modules: 8 x 8 plank deck on round piles, deck 3 above the water; planks along X; mooring bollards and coiled rope; frag 6. Variants: Dock_Straight, Dock_End (with a ladder down to the water), Dock_Shack (a tiny fishing shack 6 x 6 on the dock). A small rowboat (separate object Rowboat, 8 long) tied to Dock_End.
```

#### `WST_SB_MinersShack` — Casa de mineros

- **Bloques:** A + C · **Tris:** ≤ 1 200 · **Fragmentos:** 8 por pared

```
MODEL: WST_SB_MinersShack
TRIANGLE BUDGET: <= 1200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Poor miner's cabin, 12 x 10, walls 8 tall (lower than the kit: poor side), shed roof of mismatched boards and a patch of rusty corrugated iron (rust), a stovepipe, one door (Door_Plank style) and one window with a canvas curtain, a tiny porch with a crate seat. Walls in unpainted gray-brown wood (wood_mid / wood_light mixed boards), visibly crooked (2 degrees out of square). Each wall is a destructible piece with 8 fragments; roof 6 fragments.
```

#### `WST_SB_BankInterior` — Banco: interior y bóveda

- **Bloques:** A + C · **Tris:** ≤ 3 000 · Fuente: oleada 3, "defender el banco: los muertos son atraídos por la plata"

```
MODEL: WST_SB_BankInterior
TRIANGLE BUDGET: <= 3000 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Bank interior set:
- TellerCounter: a long counter 16 x 4.5 x 2 with brass teller bars (vertical bars in arched windows) on top, 3 teller windows; frag 6.
- Vault: the vault room front: a stone_grey wall 12 wide x 10 tall with a huge round vault door (VaultDoor, 6 diameter, 1 thick, gunmetal/brass, with a big spoked wheel and bolts around the edge), hinged on its right side (pivot), inside the vault: shelves with stacked silver bars (silver_crust, 0.6 x 0.3 x 0.3 each) — the stacks have faint neon seams (Silver_Bars_Glow object) since the silver is what attracts the dead.
- Desk_Banker: a big desk with a green banker's lamp (lamp_glow), ledgers.
- Benches_Waiting: a long bench; frag 3.
```

#### `WST_SB_Forge` — Herrería (recuperar el transporte)

- **Bloques:** A + B · **Tris:** ≤ 1 500 · Fuente: "recuperar transporte en el establo/herrería"

```
MODEL: WST_SB_Forge
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Blacksmith forge set: a brick forge hearth 4 x 3 x 3 with a hood and chimney, glowing coals (Coals_Glow, lamp_glow), a big leather bellows (separate object Bellows, hinged), an anvil on a tree-stump base, a quench barrel with water, a tool rack with tongs and hammers, a row of horseshoes on pegs, a wagon wheel leaning on the wall.
```

### Vías y escenario que se mueve (tren)

Por `D002`, el escenario corre alrededor del tren quieto: todo tile es **sin costura en los dos extremos** (z = ±32) para repetirse.

#### `WST_Track_Tile` — Tramo de vías y terreno

- **Bloques:** A + B · **Tris:** ≤ 800 por tile

```
MODEL: WST_Track_Tile
TRIANGLE BUDGET: <= 800 triangles per tile. Hard cap: see the BUDGET rule in STYLE.
Seamless scrolling track tiles, 64 long (Z), ends at z = -32 and z = +32 match exactly.
- Track_Plain: a ballast bed (raised gravel strip 10 wide, 1 tall, stone_grey / ochre faceted) with two iron rails (gauge 4.6) on wood ties every 2, plus 24 studs of desert ground on each side (sand with small rock bumps).
- Track_Cut: the same but running through a shallow rock cut: low redrock walls 6 tall on both sides, 14 apart.
- Track_Embankment: the track on a raised embankment 6 high with slopes.
Variants of the ground use only sand / ochre / redrock with 3-6 low rocks and 1-2 cactus spots (empty markers _Cactus for placing cactus props).
```

#### `WST_Track_Tunnel` — Túnel del tren

- **Bloques:** A + B · **Tris:** ≤ 1 500 · Fuente: "túneles: hay que agacharse en los techos"
- La altura libre se mide contra la altura agachado del jugador (hoy `Movement` no la define): **medir antes de exportar**.

```
MODEL: WST_Track_Tunnel
TRIANGLE BUDGET: <= 1500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Train tunnel for the scrolling scenery: a stone-and-timber portal on a rock cliff, and seamless interior tiles.
- Tunnel_Portal: the entrance face, 64 long tile where the last 20 studs enter a rock cliff (40 tall); portal arch of cut stone (stone_grey) with a keystone.
- Tunnel_Inner: interior tile 64 long, rough rock, dark, with timber arches every 8.
Clearance: the inside ceiling at the track centerline is exactly 15.5 above the rail tops (car roofs are at 12: a standing player hits the ceiling, a crouching player passes). Width 14.
```

#### `WST_Track_Trestle` — Puente de caballetes del tren

- **Bloques:** A + B · **Tris:** ≤ 1 200

```
MODEL: WST_Track_Trestle
TRIANGLE BUDGET: <= 1200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Seamless 64-long timber trestle bridge tile carrying the track over a ravine: deck at track height, timber bents every 8 studs going 30 down to a dry riverbed, X-bracing, a walkway plank on one side. Ends match the plain track tile. Variant Trestle_Start (with the ground rising to meet it at one end).
```

### Hollow Creek

Noche, faroles, relámpagos secos, tormenta de plata. Los objetos de luz traen su vidrio aparte (`lamp_glow`) para prenderlos y apagarlos.

#### `WST_HC_Tombstones` — Lápidas y cruces

- **Bloques:** A + C · **Fragmentos:** 2 · **Tris:** ≤ 120 por pieza · Fuente: cementerio; "lápidas" está en la lista de props

```
MODEL: WST_HC_Tombstones
TRIANGLE BUDGET: <= 120 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Graveyard markers, one file, separate objects, all with a blank face for epitaph decals and each breaking in 2 fragments:
- Tombstone_Round (2 x 3 x 0.4, rounded top), Tombstone_Square, Tombstone_Cross (stone cross 3 tall), Tombstone_Broken (half missing), Tombstone_Leaning (tilted 15 degrees).
- WoodCross_A, WoodCross_B (two weathered planks nailed in a cross, 3.5 tall, one leaning), WoodMarker (a single plank with a rounded top).
Stone in stone_grey with ochre lichen patches (flat insets); wood in wood_light faded.
```

#### `WST_HC_Graves` — Tumbas (los muertos excavan)

- **Bloques:** A + B · **Tris:** ≤ 250 por pieza · Fuente: oleada 2, "cementerio con muertos que excavan"

```
MODEL: WST_HC_Graves
TRIANGLE BUDGET: <= 250 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
- Grave_Mound: a closed grave mound 3 x 7, 0.8 tall, faceted dirt (ochre / sand).
- Grave_Open: the same grave burst open from below: dirt thrown outward in clumps, a ragged hole 2.5 x 4 going 3 deep, a broken coffin lid (separate object CoffinLid) sticking out at an angle.
- Grave_Fresh: a filled grave with a shovel stuck in it.
Origin at the ground-level center of the grave.
```

#### `WST_HC_CemeteryFence` — Cerca y portón del cementerio

- **Bloques:** A + C · **Fragmentos:** 3 · **Tris:** ≤ 250 por módulo

```
MODEL: WST_HC_CemeteryFence
TRIANGLE BUDGET: <= 250 triangles per module. Hard cap: see the BUDGET rule in STYLE.
Cemetery fencing: Fence_Iron (8 long wrought-iron fence, 4 tall, spear-tip pickets every 0.5, two rails, stone_grey posts at the ends; frag 3), Fence_Gate (iron double gate under an arch with a blank plate on top; GateL, GateR separate, pivot at outer edges), Fence_Picket (8 long wooden picket fence, 3 tall, some pickets missing; frag 3).
```

#### `WST_HC_Bonfire` — Fogata (punto de luz y refugio)

- **Bloques:** A + B · **Tris:** ≤ 250 · Fuente: oleada 3, "encender fogatas/faroles como puntos de luz y refugio"

```
MODEL: WST_HC_Bonfire
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A bonfire players light: a ring of 8 stones (stone_grey) 4 diameter, logs stacked in a teepee 2.5 tall inside (wood_mid, ends wood_charred), unlit by default. Embers object (Embers_Glow, lamp_glow, small chunks at the base) hidden by default. Marker _Fire at the center top of the logs.
```

#### `WST_HC_LampPost` — Farol de calle

- **Bloques:** A + C · **Fragmentos:** 3 · **Tris:** ≤ 200 · Fuente: "de noche, con faroles"

```
MODEL: WST_HC_LampPost
TRIANGLE BUDGET: <= 200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Street oil lamp on a post: a 9-tall wooden post (wood_dark) with a crossbar near the top (a ladder rest), a four-sided lantern with glass panes on top (frame iron, panes glass, flame separate object Lamp_Glow, lamp_glow). Frag 3 (post snaps in two, lantern head). Marker _Light at the flame.
```

#### `WST_HC_ChurchDoors` — Portón de la iglesia

- **Bloques:** A + B · **Tris:** ≤ 800 · Fuente: "asedio final en la plaza mientras se abren las puertas de la iglesia"

```
MODEL: WST_HC_ChurchDoors
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The church's great double doors, seen from the plaza: an arched doorway 8 wide x 12 tall in a stone_grey surround, two heavy plank doors (DoorL, DoorR) with iron strap hinges and iron studs, pivots at their outer edges, opening inward. Chains wrapped across the doors with a big padlock (separate object Chains, removed when they open). No carving: a simple iron cross shape bolted on each door.
```

### Iglesia en ruinas (jefe final)

Construcción final "grande e imponente". Arena del jefe: entran 4 jugadores, un jefe de hasta 7,8 studs y hordas. Fase 1: campana y púlpito; fase 2: bancos como cobertura rompible; fase 3: arde y el techo se derrumba por zonas.

#### `WST_CH_Church` — Iglesia (cáscara)

- **Bloques:** A + C · **Tris:** ≤ 6 000 en objetos de ≤ 5 000

```
MODEL: WST_CH_Church
TRIANGLE BUDGET: <= 6000 triangles in total, at most 5000 per object. Hard cap: see the BUDGET rule in STYLE.
Ruined frontier church, the final building of the world: imposing and tall. Nave interior 24 wide (X) x 48 long (Z) x 18 tall to the eaves, steep gable roof to 30, a square bell tower on the front (-Z) end rising to 45 with an open belfry and a steeple.
Built as destructible pieces (up to 8 fragments each):
- Church_WallSide_L, Church_WallSide_R: stone_grey rubble base 4 tall, then white-washed boards (paint_cream faded, peeling), 4 tall arched windows per side with broken frames and a few remaining glass pieces (glass), one side already partly collapsed (a ragged 6-wide hole).
- Church_WallBack: the apse wall behind the altar, with a big round window frame (empty).
- Church_Front: the facade with the doorway (doors are WST_HC_ChurchDoors).
- Church_Roof_Zone1..Zone4: the nave roof split into 4 zones along Z, each zone collapses separately (8 fragments each); holes already open in zone 2.
- fixed_Trusses: the heavy roof trusses (scissor trusses, wood_dark) that stay as a skeleton.
- BellTower: the tower (frag 8), with a ladder inside and a belfry floor at 30.
Charred variant for all wood pieces (phase 3 fire).
```

#### `WST_CH_Bell` — La campana (hay que destruirla)

- **Bloques:** A + C · **Fragmentos:** 6 · **Tris:** ≤ 600 · Fuente: fase 1, "toca la campana y llama hordas. Hay que destruir la campana"
- El vault no dice con qué se destruye (disparos, dinamita).

```
MODEL: WST_CH_Bell
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The church bell, a boss-fight objective. Bronze bell 3 tall, 3 diameter at the lip (brass_B8893A with rust_7B4A2E patches), hung from a wooden yoke (wood_dark) on a headstock with iron straps; a long bell rope (rope) hanging 25 studs down from a wheel to the floor below.
- Living silver grows over the bell: Silver_Veins crawl from the crown down the sides; a Silver_Crust patch on one side (it has been corrupted).
- Fragments (6): the bell body breaks in 5 big jagged curved shards + the clapper. fixed_Yoke stays.
- BellRope separate (pivot at the top).
Origin: the pivot point of the yoke (the bell swings).
```

#### `WST_CH_Pulpit` — Púlpito

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 500

```
MODEL: WST_CH_Pulpit
TRIANGLE BUDGET: <= 500 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Raised wooden pulpit, the Preacher's phase-1 position: a hexagonal box pulpit (3 across) raised on a pedestal so its floor is at 4 high, with curved stairs (5 steps) up its side, a sounding board canopy above it on a post, a lectern top with a big open book. Dark wood (wood_dark) with paint_cream inner panels. Silver veins (Silver_Veins object) creeping up the pedestal from the floor. Frag 4.
```

#### `WST_CH_Pew` — Bancos de iglesia (cobertura rompible)

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 250 · Fuente: fase 2, "los bancos son cobertura rompible"

```
MODEL: WST_CH_Pew
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Church pew, 8 long x 3.4 tall (backrest) x 2.2 deep, seat at 1.8; solid plank back (so it works as crouch cover), solid end panels with a simple curved top, wood_mid. Variants (same file): Pew (intact), Pew_Toppled (on its back), Pew_Broken (split in half, ends splintered). Each pew: frag 4.
```

#### `WST_CH_Altar` — Altar y cruz

- **Bloques:** A + B · **Tris:** ≤ 800

```
MODEL: WST_CH_Altar
TRIANGLE BUDGET: <= 800 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
The altar end of the nave: a raised platform 16 wide x 8 deep x 1.5 high with 3 steps, a plain wooden altar table with a torn white cloth (cloth_white, blood_dry stains), candlesticks (brass, candle flames as Candle_Glow objects), and a huge iron cross (8 tall, wrought iron, square bars 0.5, flared tips) mounted on the back wall — the same design as the Preacher's weapon, at a bigger scale. Silver_Crust growth spreading from the foot of the cross across the platform (separate object).
```

#### `WST_CH_SermonBoard` — Sermones pegados (narrativa)

- **Bloques:** A + B · **Tris:** ≤ 100 · Fuente: "sermones del Predicador pegados en las paredes desde Dusty Gulch"
- El texto es decal: esto es solo el papel y los clavos. Sirve también para los carteles de "Se busca".

```
MODEL: WST_CH_SermonBoard
TRIANGLE BUDGET: <= 100 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Pinned paper notices for decals: Paper_Sheet (1.2 x 1.6, 0.02 thick, slightly curled corners, paint_cream) with 2 nail heads (iron); Paper_Torn (same, bottom half torn off diagonally); Paper_Stack (3 overlapping sheets at different angles). Each sheet has a flat front face for a decal.
```

---

## 9. Props por categoría

La lista del vault: barriles (algunos explosivos), cajas, carretas, bebederos, postes de telégrafo, cactus, lápidas, cercas. Las cajas están en la sección 2, las lápidas en Hollow Creek y las cercas en Red Mesa y Hollow Creek.

### `WST_Prop_Barrel` — Barril

- **Bloques:** A + C · **Fragmentos:** 6 · **Tris:** ≤ 300

```
MODEL: WST_Prop_Barrel
TRIANGLE BUDGET: <= 300 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Wooden barrel, 2.2 diameter at the belly, 1.9 at the ends, 3.0 tall; 10-sided cross-section with 3 vertical segments for the bulge; staves suggested by 10 shallow vertical grooves (no separate stave meshes); 3 iron_3B3A3A hoops (at 15%, 50%, 85% height, 0.15 tall, 0.04 proud); lid inset 0.1 with a small bung; wood_mid.
Fragments (6): 4 vertical quarter slices of the wall (each keeps its hoop segments), the lid, the bottom.
Variant Barrel_Water: an open-top barrel with a water surface (water) 0.3 below the rim.
```

### `WST_Prop_BarrelExplosive` — Barril explosivo

- **Bloques:** A + C · **Fragmentos:** 6 · **Tris:** ≤ 350 · Fuente: "barriles explosivos marcados con brillo" (el brillo es VFX)
- Tiene que distinguirse del barril común **solo por la silueta y el color**, sin depender del brillo (el brillo puede estar reducido en celular).

```
MODEL: WST_Prop_BarrelExplosive
TRIANGLE BUDGET: <= 350 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Explosive powder keg, same size and fragment layout as the plain barrel (2.2 belly, 3.0 tall, 6 fragments) but clearly dangerous:
- A wide warning_red_D2301F painted band around the whole middle between the hoops.
- A blank warning plate (paint_cream, 0.8 x 0.6) on the front (-Z), for a skull/"XXX" decal.
- A short coiled fuse (3 segments) sticking out of the lid bung, and a stick of dynamite strapped to the side with twine (+X side).
- Hoops in iron, wood_dark staves (darker than the plain barrel).
```

### `WST_Prop_DynamiteCrate` — Caja de dinamita

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 250 · Fuente: "explosivos colocados a propósito (barriles, cajas de dinamita)"

```
MODEL: WST_Prop_DynamiteCrate
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Small dynamite crate 2.4 x 1.4 x 1.6, dovetailed corners suggested by notches, wood_light, rope handles at the ends, lid slightly ajar showing 6 dynamite sticks (dynamite_red) inside, a warning_red stripe on the front and a blank stencil plate. Frag 4.
```

### `WST_Prop_Wagon_Wreck` — Carreta abandonada (contenedor de loot)

- **Bloques:** A + C · **Fragmentos:** 8 · **Tris:** ≤ 900 · Fuente: contenedores ("carretas")

```
MODEL: WST_Prop_Wagon_Wreck
TRIANGLE BUDGET: <= 900 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
An abandoned broken freight wagon, a loot container and cover: the bed 10 x 5 sitting tilted 12 degrees because the back-left wheel is broken off and lies flat beside it; a torn canvas cover on 3 remaining hoops (one hoop snapped); a spilled crate and sacks at the back. Same wheel style as the player wagon. Frag 8 (bed boards, side boards, hoops).
```

### `WST_Prop_HandCart` — Carretilla de mano

- **Bloques:** A + B · **Tris:** ≤ 300

```
MODEL: WST_Prop_HandCart
TRIANGLE BUDGET: <= 300 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Two-wheeled wooden hand cart (handcart for goods), bed 4 x 2.5, two spoked wheels 2.4 diameter, long pull handles, a few sacks in it. Wheels separate (Wheels, pivot on the axle).
```

### `WST_Prop_WaterTrough` — Bebedero (debilidad del Carnicero)

- **Bloques:** A + C · **Fragmentos:** 4 · **Tris:** ≤ 250 · Fuente: Red Mesa; **"Debilidad: los bebederos de agua"** del Carnicero

```
MODEL: WST_Prop_WaterTrough
TRIANGLE BUDGET: <= 250 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Wooden water trough for horses, 6 long x 2 wide x 1.8 tall, on two short X-legs, planks with iron corner bands, filled with water: a separate object Water (water_5E8F96 flat surface 0.3 below the rim). It must read clearly as "full of water" from a distance (the water surface is the biggest color area seen from above).
Frag 4 (two side walls, two end+bottom pieces); the Water object is hidden when it breaks.
Variant WaterTrough_Pump: the same with a cast-iron hand pump at one end (Handle separate, pivot at its base).
```

### `WST_Prop_TelegraphPole` — Poste de telégrafo

- **Bloques:** A + C · **Fragmentos:** 3 · **Tris:** ≤ 200

```
MODEL: WST_Prop_TelegraphPole
TRIANGLE BUDGET: <= 200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Telegraph pole, 16 tall, round 8-sided pole (wood_mid, 0.6 diameter), one crossarm (5 wide) near the top with 4 glass insulators (glass_green) on wooden pegs, two diagonal braces under the crossarm. Markers _Wire_1.._Wire_4 at each insulator (the wires are drawn in the engine). Frag 3 (the pole snaps at 1/3 height; crossarm separate). Variant TelegraphPole_Leaning (tilted 12 degrees).
```

### `WST_Prop_Cactus` — Cactus

- **Bloques:** A + B · **Tris:** ≤ 200 por pieza

```
MODEL: WST_Prop_Cactus
TRIANGLE BUDGET: <= 200 triangles per piece. Hard cap: see the BUDGET rule in STYLE.
Desert cacti, separate objects in one file, faceted 6-8 sided, vertical ribs as faceted edges, cactus_7A9A5B with lighter tops:
- Saguaro_A: 12 tall, trunk + 2 arms curving up.
- Saguaro_B: 9 tall, trunk + 1 arm.
- Saguaro_Dead: 10 tall, dried skeleton (wood_light ribs, hollow look), leaning.
- PricklyPear: a clump of 6 flat oval pads 3 tall.
- BarrelCactus: squat 1.5 tall, 1.2 wide, a ring of tiny red-orange (paint_red) flowers on top.
- Ocotillo: 6 tall cluster of thin spiny stalks.
```

### `WST_Prop_HitchingPost` — Poste para atar caballos

- **Bloques:** A + C · **Fragmentos:** 2 · **Tris:** ≤ 100

```
MODEL: WST_Prop_HitchingPost
TRIANGLE BUDGET: <= 100 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Single hitching post 3.5 tall with an iron ring, and a variant HitchRail_Short (2 posts + rail, 4 long). wood_mid. Frag 2.
```

### `WST_Prop_HayBale` — Fardos de paja (arden)

- **Bloques:** A + C · **Fragmentos:** 2 · **Tris:** ≤ 80

```
MODEL: WST_Prop_HayBale
TRIANGLE BUDGET: <= 80 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Rectangular hay bale 3 x 1.6 x 1.6 (hay_D8B65A), two twine bands (rope), faceted loose straw tufts at the ends. Variants: HayBale_Stack (4 bales stacked, cover 3.2 tall), HayBale_Burnt (wood_charred top half). Frag 2 per bale.
```

### `WST_Prop_OilLamp` — Lámpara de aceite colgante (muerte ambiental)

- **Bloques:** A + C · **Tris:** ≤ 200 · Fuente: muertes ambientales: "lámparas de aceite"

```
MODEL: WST_Prop_OilLamp
TRIANGLE BUDGET: <= 200 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Hanging oil lamp: a brass lamp body with a glass chimney (glass), a tin reflector shade, hanging from a 2-stud chain (Chain, separate) from a ceiling hook. Flame separate (Lamp_Glow). The lamp detaches from the chain, falls and bursts: Lamp body frag 3. Pivot of the chain at the hook.
Variant OilLamp_Wall: a wall sconce version with a bracket (for interiors and the passenger car).
```

### `WST_Prop_Sacks` — Bolsas y costales

- **Bloques:** A + C · **Fragmentos:** 2 · **Tris:** ≤ 120

```
MODEL: WST_Prop_Sacks
TRIANGLE BUDGET: <= 120 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
Burlap sacks (canvas) tied at the top: Sack_Upright (1.2 x 2 x 1), Sack_Lying, Sack_Pile (5 sacks, 3 tall, crouch cover). A blank stencil patch on each (for "FLOUR"/"FEED" decals). Frag 2 per sack.
```

### `WST_Pickup_SilverDollar` — Dólar de plata (la moneda que cae)

- **Bloques:** A + B · **Tris:** ≤ 150 · **Primer uso:** Dusty Gulch
- Lo pidió la sesión del juego (2026-10-29, feedback de Valentin al jugar): una moneda de la época para el drop de plata, que el juego hace girar sobre el piso (`assets/models/rbx/Loot/Coin.rbxm`). Se suma a la esquirla, no la reemplaza.
- Parada de canto y con la cara hacia −Z, para que al girar sobre Y muestre las dos caras.

```
MODEL: WST_Pickup_SilverDollar
TRIANGLE BUDGET: <= 150 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A frontier silver dollar coin, exaggerated so it reads at 30 studs while it spins on the ground.
- One object named Coin, standing on its edge: the faces look toward -Z and +Z, origin at the exact center of the coin.
- Diameter 1.2 studs, thickness 0.16. A 10-sided disc (faceted, no smoothing).
- Rim: both face edges chamfered about 0.05, the chamfer in silver_crust_B9C3CC so the edge catches the light.
- Both faces: a raised five-pointed star in the center (0.6 across, 0.04 proud). The star reads as the "coin" at distance; no text, no portrait.
- Colors: body steel_light_A3A7AB; rim chamfer and star silver_crust_B9C3CC.
```

### `WST_Prop_Woodpile` — Pila de leña

- **Bloques:** A + B · **Tris:** ≤ 400 · **Primer uso:** Dusty Gulch
- Lo pidió la sesión del juego (2026-10-30): el mapa tiene dos `Woodpile` de 4 × 2 × 6 (cobertura, no se rompen) que hoy son cajas lisas.
- Va como prop (`assets/models/rbx/Props/Woodpile.rbxm`), ajustado a esa caja: lo largo de los leños en Z.

```
MODEL: WST_Prop_Woodpile
TRIANGLE BUDGET: <= 400 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A stacked pile of split firewood behind a western house, low crouch cover. Footprint 4 (X) x 6 (Z), 2 tall.
- One object named Pile, origin at the base center.
- Split logs 4.6 long running along Z (the -Z end of the footprint is left for the chopping block), stacked in three rows that get narrower going up (bottom row 6 logs across 4, then 5, then 4), each log ~0.62 thick, slightly irregular (some 0.1 longer or shorter, a few split in wedges so the split face shows).
- Log ends visible at both Z ends: end grain wood_light_A7804F with a darker ring; bark wood_dark_4E3524; split faces wood_mid_7E5A3A.
- Two short stakes (0.2 x 2.2) at each end of the X sides holding the pile, wood_dark. A chopping block (stump 1 x 1 x 1.1) with an axe stuck in it at the +X, -Z corner, inside the footprint.
- Colors: bark wood_dark_4E3524, split faces wood_mid_7E5A3A, end grain wood_light_A7804F, axe head iron_3B3A3A, axe handle wood_light.
```

### `WST_Prop_Outhouse` — Letrina

- **Bloques:** A + B · **Tris:** ≤ 600 · **Primer uso:** Dusty Gulch
- Era un extra propuesto (`WST_X_Outhouse`, sección 10); la sesión del juego lo pidió el 2026-10-30. El mapa tiene dos `Outhouse` de 3,5 × 8 × 3,5 (decor, no se rompen): se ajusta a esa caja y sin fragmentos. Si algún día se rompe, hace falta fragmentarla.

```
MODEL: WST_Prop_Outhouse
TRIANGLE BUDGET: <= 600 triangles for the whole model. Hard cap: see the BUDGET rule in STYLE.
A wooden frontier outhouse: narrow plank booth with a slanted roof and a door with a crescent moon cut-out. Must read as "outhouse" at 40 studs.
- Footprint 3.5 x 3.5, total height 8 (front wall 8, back wall 7: single-slope roof falling to +Z). Origin at the base center. Front toward -Z.
- Body: vertical boards (0.45 wide, 0.08 relief between boards) on all four walls, wall thickness 0.2, corner posts 0.25 x 0.25.
- Door (separate object Door, origin on its hinge edge at the bottom, hinge on -X): 2.2 x 6, Z-brace on the outside, crescent moon cut-out (0.5 tall) through the door near the top, iron handle.
- Roof (part of Body): planks overhanging 0.3 on all sides, wood_dark edge.
- Colors: boards wood_mid_7E5A3A with a few wood_light_A7804F replaced boards, posts and roof edge wood_dark_4E3524, moon cut-out shows dark inside (coal_1C1A19 back face), handle iron_3B3A3A.
```

---

## 10. Extras propuestos (no están en el vault)

Set dressing típico del oeste que ayuda a que "ningún pueblo se vea igual", pero que **el vault no pide**. Confirmar antes de producir; si se aprueban, van a la lista de props del Chapter en `Set dressing del Western.md`.

| Id | Qué | Por qué |
|---|---|---|
| `WST_X_Tumbleweed` | Planta rodadora (bola de ramas secas, 2,5 de diámetro, ≤ 150 tris) | Movimiento ambiental en la falsa calma de Dusty Gulch y el viento de Hollow Creek |
| `WST_X_CowSkull` | Cráneo de vaca (≤ 120 tris) | Narrativa ambiental de rancho y desierto |
| `WST_X_RanchGate` | Arco de entrada del rancho: dos postes de 12, travesaño y cartel colgante liso | Marca la llegada a Red Mesa |
| `WST_X_RanchDetails` | Hierros de marcar con su fogón, pozo con malacate | Variedad de Red Mesa |
| `WST_X_Windmill` | Molino de viento de rancho (torre de 18, rueda de aspas aparte) | Silueta alta de Red Mesa |
| ~~`WST_X_Outhouse`~~ | Letrina de madera: pasó a `WST_Prop_Outhouse` (pedida por la sesión del juego, 2026-10-30) | Variedad y humor (`Social y humor.md`) |
| `WST_X_Gallows` | Horca de madera en la plaza | Hollow Creek "pueblo maldito"; revisar tono y normas de Roblox antes |
| `WST_X_Piano` | Piano vertical del saloon (frag 6) | Saloon reconocible; se puede romper en la defensa |

---

## Lo que no es un modelo 3D (va a otro rol)

| Qué | Rol | Por qué no está acá |
|---|---|---|
| Carteles de "Se busca", sermones, nombres de negocios, epitafios | Texturas / UI (decals) | Los modelos traen el tablero o papel liso |
| Sangre seca en paredes y pisos | Texturas (decals) | Superficies planas |
| Brillo de barriles explosivos, auras de élite, rareza del loot | VFX | `Highlight`, partículas y luces |
| Latido de la plata viva | VFX + scripter | Material `Neon` + brillo por script |
| Fuego, humo, gas, chispas, vapor del maquinista, polvo | VFX | Partículas y flipbooks |
| Lazo lanzado, cadena del gancho del Carnicero, cables del telégrafo | Scripter / VFX | Cuerdas dibujadas en el motor (`RopeConstraint`, `Beam`) |
| Élites por color | Scripter | Recolor de los materiales del modelo base |
| Terreno: desierto, río de Silver Bend | Builder | `Terrain` de Roblox |
| Mapa ferroviario de la cinemática | Cinemáticas / UI | No está definido si es 2D o 3D |
| Lobby del Western ("un pueblo del oeste") | Builder | Se arma con el kit y los props de acá |
| Ropa vestible del vagón (chalecos, sombreros) | Modelos 3D, después | Depende de si son cosmético o equipo (abierto) |
| Viewmodel de primera persona | Modelos 3D + animación, después | `D011`: abierto si hay viewmodel |

## Abierto

- **Paleta, color plano, escala, triángulos y fragmentos:** todo lo de "Supuestos" es propuesta hasta que Valentin lo apruebe; al aprobarse, se pasa a `vault/06 Producción/Estilo visual.md`.
- **Camino del color a Studio:** un MeshPart por color o atlas de paleta (recomendado). Si es atlas, falta el script de Blender que colapsa UVs por material.
- **Rig:** los prompts asumen R15 segmentado sin skinning para humanoides y rig propio segmentado para criaturas. Falta decidir quién arma el rig y con qué (`Pipeline y roles con IA.md`).
- **Verdadera forma del Predicador:** decidido sin Valentin (2026-10-29, a revisar): es la forma "casi hecha de plata". Se produce.
- **Plata en Silver Bend** (Hermanos Doyle): el vault no la fija; los prompts usan vetas.
- **Vagón de ganado:** decidido sin Valentin (2026-10-29, a revisar): van en el tren los caballos que se recuperan en Silver Bend. Se produce.
- **Puente roto del cañón:** decidido sin Valentin (2026-10-29, a revisar): no se cruza. El camino pasa por debajo, y los escombros que lo tapan se vuelan con dinamita, como el derrumbe.
- **Qué arma suelta cada enemigo armado:** los prompts dejan un marcador y usan los modelos de armas de jugador.
- **Altura agachado:** no está en `Movement`; la altura del túnel del tren (15,5) hay que medirla contra el personaje agachado.
- **Escala real del import** (studs por unidad del OBJ y hacia dónde queda el frente): medir con `WST_Prop_Crate` y anotar en "Medido".

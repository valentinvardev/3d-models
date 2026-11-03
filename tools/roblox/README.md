# tools/roblox: rig R15, animaciones y subida a Roblox

Lo que lleva un personaje de la fábrica al juego. Decisión: `vault/07 Decisiones/D022 - Rig y animaciones de personajes por código.md`.

## Animaciones (no hace falta Studio)

1. **Spec:** `assets/animation/western/<rig>/<Clip>.json`, con poses por articulación en ángulos semánticos. La convención está en el encabezado de `anim_r15.luau`.
2. **Construir:** `lune run tools/roblox/anim_build.luau assets/animation/western/<rig>/*.json`. Deja al lado de cada spec el `<Clip>.rbxm` (lo que se sube) y `<Clip>.poses.json` (las poses exactas).
3. **Revisar con números:** `py -I tools/roblox/anim_preview.py <rig.json> <Clip>.poses.json ...`. Mide:
   - piso: nada adentro más de 0,05; en un clip parado, nada flotando más de 0,08;
   - pie apoyado, que da el `walkAnimationSpeed`;
   - cierre del loop;
   - giros de más de 1600 °/s en miembros y en el objeto en la mano, o de 2400 °/s en el cuerpo, medidos a 60 fps.

   Además deja el GLB en `assets/models/western/_animations/`.
4. **Revisar a ojo:** `http://127.0.0.1:8765/tools/viewer/?id=<Id>&anim=<Clip>&sheet=8` arma una hoja de 8 cuadros, de costado y en 3/4.

   Sin navegador: `py -I tools/roblox/anim_sheet.py <rig.json> <Clip>.poses.json <salida.png> [N]` dibuja la misma hoja con las cajas de cada pieza. Es una silueta aproximada, pero alcanza para juzgar poses.
5. **Escribir caminatas y apuntados con números:** `tools/roblox/anim_ik.py` (solo cálculo). `leg()` da cadera, rodilla y tobillo para que el tobillo caiga en un punto. `aim()` y `reach()` hacen lo mismo con brazo y muñeca hacia una dirección o un punto.
6. **Subir:** `py -I tools/roblox/opencloud.py animation <Clip>.rbxm <Clip>`. El id queda en `assets/models/western/_roblox.json` y va a la ficha.

Aprendido escribiendo los clips del caminante (2026-10-28):

- **Lo que se queda quieto, se nombra.** Una articulación que un key no nombra se interpola desde el key anterior que la tiene, con el ritmo de ese key. Si las piernas tienen que esperar, van en el key.
- **La cadera rebota.** Con un `"ease"` propio en `Root` (`out` después del apoyo, `in` antes del siguiente), la cadera sube rápido después del apoyo y cae tarde. Con un ritmo lineal, el pie que carga se hunde a mitad de la pisada.
- **Al inclinar la pelvis se mueven las piernas.** Inclinarla hacia adelante (Root pitch +) tira las piernas para atrás y baja el pie de adelante.
- **Boca abajo, "adelante" es el piso.** Un brazo con swing positivo o la cara adelantada se meten en el suelo. El brazo estirado más allá de la cabeza va con swing > 180, y el cuello con pitch negativo.
- **Un pie rígido no pasa de plano a estirado sin clavarse.** Se arrodilla sobre rodillas y puntas, con el pie vertical.
- **Caminata exacta (agente de enemigos):** el punto de apoyo (talón, planta, punta) retrocede una distancia fija por key, y el tobillo sale de `anim_ik.leg()`. Así el `walkAnimationSpeed` queda exacto.
- **Keys solo de piernas:** un key intermedio que nombra solo las piernas, calculado con la cadera interpolada en ese instante, mantiene los pies en el piso sin cambiar el ritmo de la cadera.
- **Pies plantados con el torso girado:** el `twist` de la cadera es −`Root.turn`.
- **Arma soldada a la mano de un enemigo:** un brazo levantado al frente se apunta a los costados con `twist`; `spread` solo lo hace rodar sobre su eje.
- **`smooth` en tramos cortos:** 94° en 0,1 s da 1985 °/s, porque el cuadro del medio se lleva el 70 % del movimiento.
- **Boca arriba, "atrás" es el piso:** brazos con swing negativo y spread ~85. Boca abajo con sombrero de ala ancha: cuello en −80 y girado 50.
- **Hincharse con `pos`:** separar las piezas sin pasar el solape entre ellas (cintura +0,05 con un solape de 0,07).

Aprendido con los jefes (34 clips, 2026-10-28):
- **Un objeto que se mete en el piso:** se busca el peor cuadro y ahí se inserta un key que nombra solo el brazo, con la pose interpolada corregida (doblar el codo o subir el hombro). Se cierra con uno a tres keys.
- **Caer de rodillas:** con tres a cinco keys intermedios, en los que la punta del pie se desliza en línea recta y el pie gira de 0 a 80°, el pie se mete 0,06 en el piso en vez de 0,5.
- **Orientar algo soldado a la mano:** la muñeca en tres ejes más un término de dirección, con peso 30, para dejar algo vertical. Si la muñeca gira más de 100° entre dos keys, se le da al menos 0,15 s en lineal.
- **Medir lo que promete el `_intent`:** la patada del Carnicero medía 3,1 de alto cuando buscaba 1,4.
- **Boca arriba con algo en la espalda:** se rueda el cuerpo 20° con `Root.lean`. El brazo de arriba necesita swing −55 para tocar el piso.
- **Tranco de la caminata:** el apoyo recorre unas cinco veces D, y eso tiene que entrar en la pierna del rig (al Predicador D 0,7 no le alcanzó; 0,62 sí).
- **Armas dobles:** marcador `Fire` con valor `R` o `L`.
- **Hoja de contacto de un jefe de 7 studs:** la escala de `anim_sheet.py` lo corta; hace falta S = 24.

Aprendido con la verdadera forma del Predicador (8 clips con una cruz de 4,5 soldada a la mano, 2026-10-29):
- **El piso de `anim_preview` usa la caja de reposo de cada accesorio.** Para un arma larga en diagonal no sirve: con la mano girada, las esquinas de la caja quedan hasta un stud por debajo del arma real. Daba −0,25 a −1,01 con la cruz en −0,002.
  - También tapa el `walkAnimationSpeed`, porque el criterio de pie apoyado usa lo más bajo del cuadro.
  - Se mide con el arma armada en cajas orientadas, sacadas de la receta.
- **Regularización contra posición:** con `reg` 0,002 y peso 10, la izquierda quedaba a 0,24–0,44 de `_Grip2`. Con `reg` 0,0003 y peso 30, a 0,00–0,14.
- **Ramas de Euler:** el mismo objetivo dio `spread` 186 en un key y 3 en el siguiente: un giro de 180° en 0,12 s, a 3001 °/s. Se arregla con un término de continuidad (ángulo de cuaternión contra el brazo del key anterior).
- **Interpolar hombro, codo y muñeca por separado mete la cabeza del arma en el piso** a mitad de tramo (−0,24 a −0,77). Va un key que nombre solo el brazo en el peor cuadro, resuelto hacia la dirección que mezclan los dos keys vecinos.
- **Caer de cara pivotando en las rodillas:** un key cada ~0,1 s (a 9, 22, 48, 72 y 90°), cada uno apoyado. La peor penetración pasa de −0,29 a −0,049.
- **Un Hit solo del torso, tocado sobre la caminata**, hunde el arma hasta 0,37 durante los fundidos, porque la pelvis va 0,2–0,28 más baja.
- **Marcadores en un loop:** no en t = 0 (el Scrape de la caminata va en 0,2).
- **Escala de la hoja:** con la cruz arriba, el jefe mide 13 studs. Hay que ajustar la escala al clip (15–25 px por stud).
- **Marcadores en el `rig.json`:** traen `origin` (0,0,0), así que `pose_at` los ubica mal. Se miden por la caja del marcador.

Aprendido con Old Hank y Walker_Emerge (10 clips, 2026-10-28):
- **Revisar los picos más finos que 30 fps:** un pico de 1951 °/s del Draw recién apareció a 120 fps. Desde ahora `anim_preview` mide la velocidad a 60 fps, lo que dibuja Roblox.
- **Empalmes entre clips:** se miden con FK, como distancia entre el último cuadro de uno y el primero del otro. Downed → GetUp → Idle y Aim ↔ Fire dan 0.
- **Disparar sobre un apuntado en loop:** el Fire va en Action2 y sale y vuelve a la pose del Aim. El cilindro termina a 60°, que con 6 recámaras se ve igual que el 0.
- **Dos personajes en un clip (Grabbed):** se arma con el otro rig puesto al lado, en una hoja de los dos juntos. La posición relativa entre los dos HRP va al código.
- **Salir de abajo del piso (Emerge):** la alarma de piso salta a propósito y se explica en el `_intent`. La hoja de contacto se arma recortando lo que queda bajo el piso.
- **Lo que se pone o se saca del cuerpo en un marcador va en el spec:**
  - `"attach": {"Grab": ["Body"]}` y `"detach": {"Release": ["Body"]}`. Así el chequeo de piso no cuenta el arma antes de agarrarla ni después de soltarla, y lo mismo con el sombrero (`"detach": {"HatOff": ["Acc_Hat"]}`).
  - `anim_build` ignora estos campos.
  - Antes daban −0,89 y −0,21 falsos.
- **"Parado":** el chequeo de flotar sigue tratando como parado todo clip que no se llame Death o Fall.
- **Agarre de un NPC:** `rightGrip` en el `rig.json` es el centro del hueco del puño, medido en los cortes de la malla de la mano. `rig_build` arma RightGripAttachment y LeftGripAttachment solo con posición.

Aprendido con los clips del jugador (agacharse y rodar, 4 clips, 2026-10-30):
- **La caja de la canilla del R15 por defecto baja 0,107 por debajo del tobillo.** Con el pie plano y la canilla inclinada más de ~25°, su esquina entra más de 0,05 en el piso. Agachado: el pie de atrás en punta, y en la caminata el pie plano solo ~0,08 s por paso.
- **Con el muslo alto (~95°), el `twist` o el `spread` de la cadera rolan el pie** y lo meten en el piso. Root sin `lean` en la caminata, para que `anim_ik.leg` no role el pie.
- **El `walkAnimationSpeed` es la mediana de pocos tramos:** en CrouchWalk, 6. Si se cambia el ciclo, entran tramos del talón que despega y baja: con 0,53 s daba 7,4 en vez de 8. Se verifica la suela a 120 fps.
- **Rodar en el lugar:** en cada key se corre la Root para que lo más bajo toque el piso y el centro de masa no se mueva en el plano. Para la cabeza, voltereta sobre el hombro y no derecha: la caja de la cabeza sobresale del torso.
- **Cintura, cuello y brazos sin key en t = 0:** el clip arranca desde lo que suena abajo (el Hold), y el fundido de entrada (≥ 0,05) lo lleva. Un arma larga en la mano va paralela al eje de la vuelta; si no, entra 1,0 en el piso.
- **Un marcador tiene que caer en un key** (`anim_r15` lo exige). En un loop, no en t = 0.

## Objetos en la mano: sostener, equipar, inspeccionar (D024)

Todo lo que se sostiene (armas y consumibles) lleva tres clips:
- `<Objeto>_Hold`: loop, prioridad Idle. Solo brazos, cintura y cuello.
- `<Objeto>_Equip`: Action. Los revólveres giran en el dedo solo acá.
- `<Objeto>_Inspect`: Action. Lo trae frente a la cara y lo muestra de los dos lados.

Son los clips de tercera persona: lo que ven los compañeros. En primera persona hay un viewmodel por código, que hace su propia versión (D024, híbrido). Se escriben sobre el R15 por defecto del jugador (`assets/animation/western/player/PlayerR15.rig.json`, medido en Studio).

1. **Rig y vista previa:** `py -I tools/roblox/held.py <ItemId> [--grip x,y,z]` hace dos cosas:
   - Escribe `assets/animation/western/held/<Id corto>.rig.json`: el jugador con el objeto en la mano, el `_Grip` sobre el `RightGripAttachment`, sin rotación.
   - Crea el modelo `WST_Held_<Id corto>` en el visor.
2. **Specs:** `assets/animation/western/held/<objeto>/<Clip>.json`, con `"props"`: la raíz cuelga de `RightHand`, las piezas que se mueven cuelgan de la raíz. Se animan con `rot`, `pos` y `pivot` (ver `anim_r15.luau`). Referencia: `held/revolver/`.
3. **Construir, revisar y subir:** igual que cualquier clip, con el rig de `held/`. Hoja de contacto: `?id=WST_Held_<Id corto>&anim=<Clip>&sheet=8`.

Para que el revólver quede nivelado con el brazo al frente, el objeto compensa: `rot` x = −(swing del hombro + swing del codo). Las vueltas van con keys cada ≤ 120°, porque Roblox interpola por el camino corto. El último key repite la pose de sostener con la misma orientación más o menos 360° × n.

Aprendido con los 13 objetos (2026-10-28):
- **Poses por objetivo:** se dice dónde queda el objeto y hacia dónde mira, y hombro, codo y muñeca se resuelven con FK más una búsqueda (Nelder-Mead). La rotación de la raíz es `conj(q_mano)·q_objeto`. Los generadores están en el scratchpad de la sesión (`held/`).
- **La mano que acciona un mecanismo (palanca):** la raíz lleva `pos` para que el arma no se mueva aunque la mano baje.
- **Armas largas en el R15 por defecto:** el torso va de perfil (Waist −40, Neck +38). Con Waist −20, la izquierda queda a 0,59 del `_Grip2`.
- **Lo que cuelga de la mano (farol, lazo):** brazo casi estirado. Con el codo doblado, el antebrazo (1 stud de grueso) atraviesa lo que cuelga.
- **Giros de más de ~150° entre keys:** necesitan un key intermedio. Sin él, el caño de la Viuda pasaba por la cabeza.
- **La mano del R15 por defecto** es una losa de 0,98 × 0,32 × 1,03. Hay que elegir la muñeca para que la mano quede detrás del objeto visto desde afuera (en el rifle de palanca, el cajón pasó de 0 % a 84 % visible).
- **Herramienta:** `held.py` pone la articulación de la raíz en el agarre (donde gira el Motor6D del juego) y cada marcador en la pieza que lo contiene. El `_Grip2` de la escopeta va en `Barrels`.

Aprendido con las recargas (14 clips, 2026-10-28; rigs en `held/Weapon_*_Reload.rig.json`, con la bala en la mano izquierda):
- **Brazo izquierdo en dos pasadas:** primero con una preferencia fuerte por una pose cómoda, después afinando desde ahí. Así la solución no salta entre keys: el paso de la tapa a la varilla bajó de 119° a 42°.
- **La bala no se desliza en los dedos:** su `rot`/`pos` se calcula desde la pose de mundo que se quiere y solo cambia en el key de entrada.
- **Palanca que la mano no alcanza:** se reparte el recorrido. El arma sube el 55 % y la mano hace el resto.
- **Clip por bala:** empieza y termina en la misma pose, y el cilindro avanza 60°, así que el loop no se nota.
- **Costuras:** se verifican con FK contra el `Hold` (0,00° y 0,0000 studs).
- **Si un clip mueve una articulación que el `Hold` no nombra** (`LeftWrist` en el revólver), va en 0 explícito en el primer y el último key.
- **Límites de los chequeos:**
  - `anim_preview` medía a 30 fps y no veía los picos de los tramos `smooth` cortos: `DoubleBarrel_ReloadEnd` daba limpio a 30 fps y 2033 °/s a 120.
  - Ahora mide a 60 fps, que es lo que dibuja Roblox, y suma la raíz del objeto en la mano. Los mecanismos (martillo, portón de carga) no se miden, porque saltan a propósito.
  - El chequeo de `_Grip2` salta siempre en una recarga, porque la mano suelta la caña a propósito.

Aprendido con cuchillo, tiros, consumibles y culatazos (13 clips, 2026-10-28):
- **El easing cúbico triplica el pico de velocidad:** con `in`, `out` y `smooth`, el pico llega a 3× la media.
  - Un cambio de 100° con easing necesita ≥ 0,19 s; en lineal, 0,063 s.
  - En golpes y tiros, el amague y el golpe van lineales.
- **Cerca de la cara:**
  - **Se mide contra un cilindro:** la caja de la cabeza exagera las esquinas hasta 0,24. El antebrazo y el objeto se miden contra un cilindro de r 0,58 con bordes de 0,15; la mano, contra la caja.
  - **Para tomar, el objeto se corre en la mano:** con la mano del R15 por defecto, cualquier cosa agarrada a menos de ~0,5 de la cara mete la mano en la cara. La raíz se corre por su eje con `pos = rot·(0, s, 0)`: 0,4–0,5 en el whisky.
- **Alcance del R15 por defecto:** 1,86 del hombro al agarre, porque el brazo cuelga 0,5 afuera de la articulación. Un trabajo a dos manos (vendar) solo entra si el punto queda a ≤ 1,3 de los dos hombros.
- **Soltar por arriba del hombro:** el punto de suelta va a ≥ 1,25 a la derecha del centro de la cabeza. A 1,0, la mano roza la cabeza justo después de soltar.
- **Revoleo (lazo):** se gira la raíz, cuya articulación está en el agarre, con la mano quieta. Da un arco exacto, con keys cada ≤ 75°.
- **Culatazo con armas largas:**
  - Los límites de choque van relativos al `Hold`, que ya mete el antebrazo 0,4 en el torso.
  - Para girarlas ~150°, el arma rota 15–35° en la mano.
  - La izquierda se resuelve después, arrancando de la solución del key anterior. Así se evitan saltos de 1800–3000 °/s.
- **Duración de un consumible:** es el `useSeconds` de la ficha, porque el servidor aplica el efecto cuando se cumple. No se acelera con `AdjustSpeed`: duplica las velocidades.

**Contrato para el código del juego (rol scripter):**
- **Raíz:** el objeto es un modelo cuya raíz se llama como `root` en su `rig.json` (`Body`) y lleva un Attachment `_Grip`.
- **Piezas que se mueven solas** (Cylinder, Hammer, LoadingGate…): cuelgan de la raíz por un Motor6D. Su Part1 es la pieza, con C0 y C1 en el origen de la pieza. El resto va soldado.
- **Al equipar:** se crea un Motor6D con `Part0 = RightHand` del personaje y `Part1 = raíz`.
  - `C0 = CFrame.new(RightGripAttachment.Position)` del avatar, sin rotación (escala con el avatar).
  - `C1 = CFrame.new(_Grip.Position)`.
  - No se usa la soldadura `RightGrip` de un Tool, porque una soldadura no se anima.
- **Clips:** `Hold` en loop mientras está en la mano. `Equip` al equipar; el arma no dispara hasta el marcador `Ready`. `Inspect` con F, o manteniendo el slot en celular; se corta al disparar, recargar, usar o cambiar.
- **Nombres:** las animaciones se aplican por nombre de pieza (`Body`, `Cylinder`…), así que el modelo tiene que llegar con esos nombres.

**Un NPC con un arma en la mano** (Old Hank con La Viuda):
- **Rig para animar:** `py -I tools/roblox/held.py <ItemId> --body <04_roblox/NPC.rig.json> --drop <pieza enfundada> --name <NPC>`. El `rig.json` del NPC lleva `"rightGrip"`, el punto donde cierra el puño en sus coordenadas.
- **Rig del juego:** `rig_build` convierte el `rightGrip` en `RightGripAttachment`, y su espejo en `LeftGripAttachment`. El juego usa el mismo contrato que con el jugador.

**Armarlos para el juego:** `lune run tools/roblox/held_build.luau <objeto.rig.json> <held.rig.json> <Id de la ficha> assets/models/rbx/{Weapons|Consumables}/<Id>.rbxm`.
- `objeto.rig.json` es el de `04_roblox/` del objeto: `rig_data.py glb`, más los ids leídos con `studio_nodes.luau`.
- Del `held.rig.json` salen la raíz, el agarre y el `tree`. Solo entran las piezas del `tree`: la dinamita en la mano es `Stick`, no `Bundle`.
- El `_Grip` va siempre en la raíz. En los revólveres el marcador está en la pieza `Grip`, y se pasa a la raíz.
- Las balas y vainas de la recarga están en `assets/models/rbx/Weapons/Rounds.rbxm` (`overlay_build.luau` sin cuerpo): cada una centrada en su origen.

## Overlays de plata

`lune run tools/roblox/overlay_build.luau <overlay.rig.json> <Nombre> assets/models/rbx/Overlays/<Nombre>.rbxm <WST_Enemy_Walker_A.rig.json>`
- Cada pieza se llama como la parte que cubre (`Silver_RightLowerArm` → `RightLowerArm`; `Silver_Tears` → `Head`, por caja). El nombre original queda en el atributo `Piece`.
- Cada pieza lleva un `Weld` "Fit" con `Part0` vacío y C0 respecto de esa parte en el cuerpo de referencia. El juego pone `Fit.Part0 = enemigo[pieza.Name]`.
- La referencia es el caminante A, porque los prompts de los overlays los hacen sobre ese cuerpo.
- Sin colisión y sin rayos, para que el headshot siga dando en la `Head` real.

## Pueblo, props y loot (modelos estáticos)

```
py -I tools/roblox/town.py loot                                       Loot/Coin.rbxm
py -I tools/roblox/town.py town [<id> ...] --map <ruta a DustyGulch.json>   Town/DustyGulch/<id>.rbxm
py -I tools/roblox/town.py props [<tipo> ...]                         Props/<tipo>.rbxm
```

- **Base:** `town.py` arma cada modelo con las mallas ya subidas del kit (los `rig.json` con ids) y las cajas del mapa. El mapa es de la sesión del juego (`src/shared/Maps/DustyGulch.json`): se pasa con `--map` si no está en este checkout.
- **Layout:** escribe un layout por modelo en `assets/models/western/_town/` (la misma ruta que el rbxm). `prop_build.luau` lo convierte en rbxm sin calcular nada.
- **Contrato con el juego** (acordado el 2026-10-29/30):
  - Model con `PrimaryPart` = `Root`, una Part invisible en el origen, que es el centro de la caja de la pieza del mapa. El modelo ya viene orientado.
  - Cada MeshPart cuelga de `Root` por un `Weld` "Fit".
  - Sin colisión, rayos, toques ni masa. La colisión y los rayos los da la pieza del mapa, que el juego deja transparente y nunca marca `"visible": false`.
  - Los rompibles (columnas, techos de porche, barriles, cajones) no se salen de su caja: si se salen, `town.py` no escribe el rbxm.
  - Los props vienen parados, con la base al ras del piso de su caja. El juego les aplica solo el yaw de la pieza.
- **Ajustar el kit a las cajas:** el kit es de 8 de ancho, así que un lado de largo L lleva n módulos estirados a L/n (n se elige en la receta del edificio, para que la puerta quede al medio).
  - La pared va con la cara de afuera al ras de la caja; los costados, entre el frente y el fondo.
  - Las ventanas y puertas del kit van en los huecos con el mismo frame: `y = 3` sobre la pared para las ventanas y el pie del hueco para la puerta.
  - Las piezas del porche se acomodan para que la pared del kit (z = 0) coincida con el borde de atrás de la caja.
- **Terminaciones sin subir imágenes:**
  - La pared del kit es crema por fuera y madera por dentro. Dada vuelta (`flip`), queda de madera cruda.
  - Ladrillo y piedra son otros kits (`KITS`).
  - Los carteles son un SurfaceGui sobre una tapa invisible; el texto también va en el atributo `Text`.
- **Captura:** `blender -b --factory-startup --python-exit-code 1 -P tools/blender/layout_preview.py -- <layouts...> [--list <archivo>] [--front x,y,z] [--out png]`.
  - Trae cada pieza de `02_blend/<Id>.blend` (la malla limpia, la misma que se subió) y la pone con el CFrame y el tamaño del layout.
  - Con varios layouts, los pone en su `"at"`: un edificio con porche y columnas, o el pueblo entero (`--list`, unos 3800 objetos, ~30 s).

Medido el 2026-10-30:
- **Lune escribe `TextLabel.Font` como `FontFace`, y falla:** hay que asignar `label.FontFace = roblox.Font.fromEnum(...)`.
- **Un Model subido puede traer las piezas con otro nombre:** `WST_Prop_Crate` llegó con `Mesh_0..Mesh_5`. `rig_data ids` lo detecta, porque falta la pieza. Si centro y tamaño coinciden en orden, se renombra en el `studio.txt`.
- **Para ver si una malla subida tiene UV sin meter nada en el juego:** `AssetService:CreateEditableMeshAsync(Content.fromUri(id))` y `GetUVs()`.
- **Subir una imagen sin Asset Delivery:** se mete en un GLB (un cuadrado con la imagen de textura; `tools/blender/dirt_texture.py`) y se sube como Model. El importador crea la imagen: es el `TextureID` de la MeshPart, que se lee en Studio. Para confirmar que sirve como Texture: `ContentProvider:PreloadAsync` sobre una Texture creada fuera del juego.
- **Texture en Lune:** se escribe `t.Texture = "rbxassetid://…"` y queda guardada como `TextureContent`, que es lo que lee Studio. Al leerla de vuelta, Lune falla con "missing default value" (también con `ColorMapContent`). Se verifica serializando a XML.

## Rig (contrato de `assets/models/rbx/README.md` del juego)

1. **Datos:** `py -I tools/roblox/rig_data.py glb <Id> <Nombre>` escribe `04_roblox/<Id>.rig.json` con los orígenes y las cajas de cada pieza, sacados del GLB de 03_export.
2. **Subir el GLB:** `py -I tools/roblox/opencloud.py model <Id>`. Roblox crea las MeshParts con la textura, como el importador.
3. **Ids:** pegar `tools/roblox/studio_nodes.luau` en `execute_luau`, con los assetId de `assets/models/western/_roblox.json` en `ASSETS`. Carga los Models con `InsertService:LoadAsset` sin meterlos en el juego e imprime una línea por pieza. Esas líneas van a `04_roblox/<Id>.studio.txt`, y `py -I tools/roblox/rig_data.py ids <Id> <ruta .studio.txt>` verifica centro y tamaño contra el GLB a 0,01 y suma los ids al `rig.json`.
4. **Armar:** `lune run tools/roblox/rig_build.luau <rig.json> assets/models/rbx/Enemies/<Nombre>.rbxm`. El `Nombre` es el `name` del `rig.json` y es el id de la ficha (`Butcher`, no `Carnicero`). Old Hank va a `assets/models/rbx/NPCs/`.

   Sin ids arma un maniquí de cajas con el mismo esqueleto, que sirve para probar animaciones en Studio.

   Cada accesorio se suelda a la pieza R15 cuya caja queda más cerca de su origen. Si el origen cae adentro de dos cajas, gana la del centro más cercano. Cuando el origen del modelo no sirve, el nodo del `rig.json` lleva `"weldTo": "<Pieza>"`. Por ejemplo, la Viuda de Old Hank va a `LowerTorso`, la funda, porque su origen cae entre el torso y el brazo. El lazo del jinete zombie también va a `LowerTorso`: su origen cuelga del cinto, 0,025 afuera de la caja de la cadera, y caía en `UpperTorso`.

   **Varios personajes en un GLB** (los Hermanos Doyle, `Brute_*` y `Shooter_*`): `rig_data.py glb <Id> <Nombre> <prefijo>` escribe `04_roblox/<Id>.<Nombre>.rig.json` con los nodos de ese prefijo, sin él, y corridos para que la cadera quede en x = z = 0. El corrimiento queda en `source`. El Model se sube una vez y se lee una vez en Studio; `rig_data.py ids <Id> <studio.txt> <Nombre>` toma de ahí lo suyo.

   `rig_data.py glb` conserva el `weldTo` de cada nodo al regenerar el `rig.json` (desde el 2026-10-29; antes se perdía). Los ids de Studio no se conservan: si cambió el GLB, hay que subirlo y leerlos de nuevo.

Medido en Studio el 2026-10-28:
- `Humanoid:BuildRigFromAttachments()` no crea las juntas en modo Edit, por eso `rig_build` arma los Motor6D.
- Un `.rbxm` armado con Lune se deserializa con mallas y textura correctas: 34/34 en el caminante A.
- **El `WeldConstraint` que escribe Lune no guarda el desplazamiento:** en Studio el sombrero y los ojos quedaban en el centro de la cabeza. Por eso `rig_build` suelda con `Weld` y C0 explícito.
- **Lo subido llega sin articulaciones:** `LoadAsset` devuelve cada nodo como un Model `<Pieza>_Node` con `WorldPivot` en 0. Las articulaciones salen siempre del GLB.
- `SerializationService` se colgó con un modelo del workspace; con un clon tarda menos de un segundo.
- `HumanoidRootPart` sin colisión, como pide el contrato del juego. La colisión la dan el torso y la cabeza.
- **`BreakJointsOnDeath` viene en `true`** (el default del Humanoid): al morir se rompen los Motor6D y el clip de muerte no se ve. El juego lo apaga en todos los enemigos al aparecer (commit 97efda8 de la sesión del juego), así que `rig_build` lo deja como está. Al probar un clip de muerte por fuera del juego, hay que apagarlo a mano.

## Criaturas (esqueleto propio)

Cuerpos que no son R15: el toro zombie (`ZombieBull`), el buitre (`Vultures`) y los caballos (`Horse` y `ZombieHorse`, con el mismo esqueleto para compartir clips). La cadena es la misma (rig → clip → revisión → subida); lo que cambia es que el árbol de articulaciones sale del `rig.json`.

**Formato:** un campo `"skeleton"` en `04_roblox/<Id>.rig.json`, al lado de `"nodes"`. Ejemplo (toro, recortado):

```json
"skeleton": {
 "tree": {"Torso": "HumanoidRootPart", "Neck": "Torso", "Head": "Neck", "Tail": "Torso",
          "FrontLeftUpperLeg": "Torso", "FrontLeftLowerLeg": "FrontLeftUpperLeg", "...": "..."},
 "joints": {"Torso": [0, 3.82, 1.2]},
 "hrpSize": [2, 2, 4],
 "collide": ["Torso", "Neck", "Head"],
 "ground": ["FrontLeftLowerLeg", "FrontRightLowerLeg", "BackLeftLowerLeg", "BackRightLowerLeg"]
}
```

- `tree`: de quién cuelga cada pieza, como el `tree` de `held.py`. La raíz cuelga de `HumanoidRootPart`. Lo que no está en el árbol va soldado.
- `joints`: dónde está la articulación cuando no es el `origin` de la pieza. Hace falta en la raíz, porque la fábrica le deja el origen del modelo, en el piso.
- `hrpSize`: tamaño del `HumanoidRootPart`, que va centrado en la articulación de la raíz. Sin este campo, 2×2×1 como el R15.
- `collide`: las piezas que colisionan. Sin este campo, la raíz y `Head`.
- `ground`: las piezas que pisan. De acá sale el `walkAnimationSpeed`.
- `air: true`: la criatura vuela. Así `anim_preview` no chequea el piso.
- `weldTo`: `{ "<extra>": "<pieza>" }`, a qué pieza va soldado un extra cuando el centro de su caja no alcanza para elegir. Se guarda en `skeleton`, así que sobrevive a regenerar el `rig.json`.
  - Un extra que cruza una articulación queda bien de un lado solo. Si se ve, se parte en la receta: en el caballo, la armadura de cuero en `Acc_LeatherArmor` (pecho), `_Neck` y `_Head`; en el caballo zombie, las vetas en `Silver_Veins` (torso) y `Silver_Veins_Neck`.

`rig_data.py glb` conserva `skeleton` (y `rightGrip`) al regenerar el `rig.json`: antes lo pisaba entero.

**Comandos:**
1. **Armar:** `lune run tools/roblox/rig_build.luau <rig.json> assets/models/rbx/Enemies/<Nombre>.rbxm`. Si el `rig.json` trae `skeleton`, usa `buildCreature`. Un rig sin `skeleton` sale byte a byte igual que antes: se comprobó con los 13 R15.
2. **Spec:** `assets/animation/western/<criatura>/<Clip>.json` con `"rig": "<ruta del rig.json desde la raíz del repo>"`.
   - Las articulaciones se llaman como la pieza que mueven y llevan `rot` (grados, `CFrame.Angles` en los ejes de reposo del padre), `pos` y `pivot`, como las piezas de un objeto en la mano.
   - `anim_build` saca el árbol del `rig.json` y anida las Poses desde `HumanoidRootPart`.
   - `"air": true` en el spec pisa el del rig, para un clip en el piso de una criatura que vuela.
3. **Construir y revisar:** `anim_build`, `anim_preview` y `anim_sheet` con el `rig.json` de `04_roblox/`, igual que un R15.
   - La hoja de una criatura tiene tres filas (costado, 3/4 y frente) y escala propia: 19,4 px por stud el toro, 43,5 el buitre.
   - `anim_ik.py` sigue siendo solo para R15.

**Signos** (en los ejes del padre, con +X a la derecha y −Z al frente):
- `rot` x +: sube lo que está adelante de la articulación (la nariz, el pecho). En algo que cuelga (la cola del toro), lleva la punta hacia adelante; en la cola del buitre, que va horizontal hacia atrás, la baja.
- `rot` y +: gira a su izquierda.
- `rot` z +: en un ala derecha la sube y en una izquierda la baja.
  - Alas del buitre: `[ataque, ∓barrido, ±alzada]`, con + para la derecha.
  - Ala izquierda arriba: z −. Barrer hacia atrás: y + en la izquierda e y − en la derecha.

**Contrato para el código del juego:**
- **Modelo:** Model con `Humanoid` (RigType R15, `Animator`, `AutomaticScalingEnabled = false`) y `HumanoidRootPart` como `PrimaryPart`, transparente y sin colisión. Lleva una parte `Head`. Sin scripts.
- **Articulaciones:** cada Motor6D se llama como su Part1 y va adentro de ella, con dos Attachments `<Pieza>RigAttachment` donde están C0 y C1.
- **Soldaduras:** la plata (`Silver_*`) va con `Weld` y C0 explícito, sin masa ni colisión.
- **`HipHeight`** = altura del HRP − la mitad de su alto, la misma cuenta que el R15. Toro: 3,82 − 1 = 2,82; buitre: 0,45 − 0,3 = 0,15. Con eso, el piso por HipHeight queda en y = 0,000, donde está lo más bajo (las pezuñas, la panza del buitre).
- **`RequiresNeck = false`:** no hay cuello R15. El toro tiene una pieza `Neck`, pero su Motor6D une `Torso` → `Neck`. **No está medido en Studio.**

**Los dos rigs (2026-10-29):**

| | Toro (`ZombieBull.rbxm`) | Buitre (`Vultures.rbxm`, Model `Vultures`) |
|---|---|---|
| Raíz | `Torso` en (0; 3,82; 1,2): el centro de su caja | `Body` en (0; 0,45; 0): el centro de su caja |
| Resto del árbol | `Neck` (0; 3,9; −2) → `Head` (0; 3,3; −3,65)<br>`Tail` (0; 3,75; 4,65)<br>patas de arriba (±1; 3,3; −1,35) y (±0,8; 3,35; 3,55)<br>patas de abajo (±1; 1,55; −1,35) y (±0,8; 1,65; 3,55) | `Head` (0; 0,62; −0,62)<br>`Tail` (0; 0,5; 0,7)<br>`Wing*Inner` (±0,3; 0,62; −0,1) → `Wing*Outer` (±1,4; 0,62; −0,05) |
| HRP | 2×2×4, adentro del torso, a lo largo entre las patas | 0,6×0,6×1,2, adentro del cuerpo: no agranda el blanco |
| HipHeight | 2,82 | 0,15 |
| Colisionan | `Torso`, `Neck` (la giba: tronco, como los dos torsos del R15) y `Head` (los cuernos rompen la pared en la carga) | `Body` y `Head`, como el torso y la cabeza del R15. Al morir cae y queda en el piso; las alas (5 de envergadura) y la cola no, para no trabarse en techos y postes |
| Soldado | `Silver_Veins` → `Torso`, `Silver_Eyes` → `Head` | `Silver_Eyes` → `Head` |

**Los caballos (2026-10-29):** `assets/models/rbx/Mounts/Horse.rbxm` y `ZombieHorse.rbxm`, con el mismo esqueleto: los clips `Horse_*` sirven para los dos.
- **Raíz:** `Torso` en (0; 3,3; 0,45), redondeado igual en los dos (el centro de la caja da 3,31 y 3,34).
- **Resto del árbol:**
  - `Neck` en (0; 3,75; −1,75), a 45°, y `Head` en la nuca (0; 5,31; −3,31).
  - `Tail` en (0; 4,05; 2,90).
  - Patas de arriba en (±0,5; 2,95; −1,35) y (±0,55; 2,95; 1,95); de abajo en (±0,5; 1,30; −1,35) y (±0,55; 1,55; 2,30).
- **HRP:** 1,5×1,5×3,5, adentro del barril. HipHeight 2,55. Colisionan `Torso`, `Neck` y `Head`.
- **Soldado (`weldTo`):** montura, alforjas y pechera → `Torso`; riendas y `_Neck` → `Neck`; `_Head` → `Head`. En el zombie, `Silver_Veins` → `Torso`, `Silver_Veins_Neck` → `Neck` y `Silver_Eyes` → `Head`.
- **`_Seat`:** Attachment en `Acc_Saddle`, en (0; 4,5; −0,1). En el zombie, a 4,48. El jinete se suelda ahí.
- Roblox reusa la malla cuando es idéntica: las patas de abajo del caballo y del zombie tienen el mismo MeshId.

**Aprendido (2026-10-29):**
- **El origen de un extra no sirve para elegir la pieza:** el de `Silver_Veins` está en el piso, en (0, 0, 0), y por origen iba a la pata delantera izquierda. Las criaturas sueldan por el centro de la caja del extra, y así va a `Torso`.
- **Pezuñas quietas con el torso en movimiento:** cada pata de arriba lleva la inversa del torso.
  - `rot` = ángulos de Rᵀ y `pos` = Rᵀ·(off − p) − off, con `off` = articulación de la pata − articulación del torso y p el `pos` del torso.
  - La pata queda en su pose de reposo y lo que se corre es su punta de arriba, que entra 1,5 en la panza.
  - En `Bull_Idle` (el lomo sube 0,11, cabecea 1,3° y se balancea 1,4°), la pezuña se aleja 0,0013 como mucho. Es el error de interpolar `pos` lineal mientras la rotación va por slerp.
- **La pieza `Neck` del toro no es la articulación `Neck` del R15:** `anim_r15` mira primero si el spec es de una criatura. Si no, le pedía `pitch` en vez de `rot`.
- **`walkAnimationSpeed` de un cuadrúpedo:** se sigue el centro del fondo de la caja de cada pieza de `ground`. Cuenta como apoyado si queda a menos de 0,06 del punto más bajo.
  - Un trote sintético (la pata barre 20° en 0,5 s, a 3,3 de la cadera) da 2,30 studs/s; lo esperado era L·ω = 2,30.
- **Aleteo:** el ala de adentro baja 72° en 0,45 s con `smooth` y da 470 °/s de pico. Es 3 veces la media (160 °/s), como dice la regla del easing cúbico.
  - En el aletazo, la punta del ala va de −0,77 a +0,90 respecto del reposo y queda 0,20 por debajo de la panza.
- **Chequeo de los `.rbxm` de criaturas:**
  - Juntas a 0.
  - Cada Motor6D dentro de su Part1, con sus `RigAttachment` en el lugar de C0 y C1.
  - Todo llega al HRP por juntas.
  - Motor6D y colisión iguales a los del `rig.json`.
  - Sin `WeldConstraint` ni scripts.
  - Lo más bajo y el piso por HipHeight en 0.
  - Se probó rompiendo una copia a propósito en 5 casos (C0 corrido, HipHeight +0,3, un WeldConstraint, HRP con colisión, la cola sin Motor6D), y los marcó todos.
- **Medido en Studio (2026-10-29):**
  - Los dos aparecen vivos con `RequiresNeck = false`.
  - El toro camina apoyado con MoveTo y el buitre vuela con AlignPosition.
  - Rearmados en Edit y con la animación avanzada a mano (`Animator:StepAnimations`), cada pieza cae donde la pone `anim_preview`: el toro a 0,001 y el buitre a 0,01.
- **Nombre del buitre:** el `name` del `rig.json` es el id de la ficha (`Vultures`, no `Vulture`), como en todos los rigs. El Model adentro de `Vultures.rbxm` se llama igual.

Aprendido con los clips del toro (7) y del buitre (5), 2026-10-29:
- **Una caja grande manda en las poses:** la cabeza del toro mide 6,24 de ancho por los cuernos.
  - Tumbada de costado, entraría 3 en el piso: en la muerte va casi derecha, con el cuello torcido.
  - Rolarla −16° la metía 0,26 en el piso donde la malla tiene aire bajo el cuerno.
- **Pata derecha en reposo, rodilla muy sensible:** acortar la pata 0,03 pide 25° de rodilla.
  - Resolver la rodilla desde la altura de la pezuña en el vuelo daba 1750–1868 °/s.
  - Dando la rodilla como un arco y resolviendo solo la pata de arriba para el avance, bajó a 1413.
  - Para alcanzar más lejos, la pata de arriba se corre por el −Y del torso hasta 0,45, entrando en la panza.
- **Galope con suspensión:** el punto más bajo sube a +0,128 y salta "FLOTA". Bajar el cuerpo 0,03 en la suspensión lo deja en +0,053 sin perder el cabeceo de ±4°.
  - El `walkAnimationSpeed` del galope sale de solo 3–4 tramos por ciclo: la caña inclinada sube el fondo de la caja fuera de la franja de 0,06. Da bien (39,9 contra 40 del diseño).
- **Windup que empalma exacto con un loop:** termina en el primer cuadro del galope, con las traseras juntas a mitad de su apoyo. Así no necesita paso de atrás.
- **El marcador del golpe va a mitad del barrido, no al final:** al final de la cornada el cuerno ya está atrás de la cabeza.
- **Alas finas:** con placas de 0,06–0,08, la penetración entre cajas siempre da ~0,03 y no distingue la bisagra de un cruce. Hay que medir los segmentos que atraviesan el plano medio de la otra placa.
- **Plegar un ala:** la de afuera, doblada abajo y barrida atrás, mete su borde en la de adentro (0,185 con 26° de barrido; 0,43 plegada 55°).
  - Bajándola con `pos` (−0,05 doblada, −0,11 plegada) pasa por debajo y da 0.
  - `pos` y `rot` van en la misma Pose y se interpolan juntas: para bajar antes de barrer hace falta un key intermedio (el extremo con `in`, el intermedio con `out`).
- **Cadáver que vuela:** el clip da vuelta el cuerpo y el HRP queda derecho, así la pose final es siempre la misma y apoya en 0. Dado vuelta, −Y es arriba.
- **Fundidos entre un loop y un Action:** si las poses difieren 37°, entrar sin fundido da 2243 °/s, con 0,05 da 1819, con 0,1 da 1203 y con 0,15 da 846.
- **Un volador se juzga desde abajo:** a 40 studs en un celular el buitre mide 14 px por stud y se lee por la silueta (una cruz volando, una flecha en la picada). `anim_sheet` no tiene vista desde abajo; el agente la armó aparte.
Aprendido con los clips del caballo (6), 2026-10-29:
- **El casco trasero no es la esquina de su caja:** la caja de la caña va 0,41 más atrás que el talón (es la punta del corvejón). Con la caña inclinada 20°, la esquina queda 0,14 por debajo del casco real. Para apoyar se usa `min(malla, caja + 0,04)`.
- **Vuelo que baja de más:** corregirlo doblando la rodilla daba 2052 °/s al final del vuelo. Subiendo la pata por el eje del torso (con `pos`, sin rotar) baja a 841 °/s.
- **Galope a 30 studs/s:**
  - Ciclo de 0,46 s, con apoyo del 27 % adelante y del 24 % atrás.
  - Para que la suspensión no salte FLOTA, la mano se corrió a 0,43 del ciclo: con 0,40 daba 0,096 y con 0,43 da 0,062.
- **Pararse de manos:** el torso gira alrededor de un punto P cerca de las caderas, con `pos = P + d − J − R·(P − J)`.
- **Arrodillarse:**
  - La búsqueda libre salta de rama: la rodilla pasa de −5° a −64° en un key, 1795 °/s. Newton con objetivo de rodilla elige la rodilla al revés.
  - Lo estable es dar la rodilla en una curva suave y resolver el apoyo: queda en ≤ 700 °/s.
- **Un clip para dos rigs:** las riendas del zombie bajan hasta 3,18 (3,97 en el caballo). `Death` lo metía −0,108 en el piso hasta que cuello y cabeza se resolvieron contra las cajas de los dos.
- **Fundidos entre andares:** sin fundido, Walk → Gallop da 6510 °/s; con 0,15 s, 1468.
  - Un fundido más largo hunde más los cascos: Gallop → Walk da −0,16 con 0,15 s y −0,28 con 0,3 s. El fundido mezcla poses, no es IK; conviene 0,15 s en todo cambio de andar.
- **Dónde se cambia de andar:** la media geométrica de las velocidades de diseño (4,84 · 12 · 30) da 7,6 y 19. Pero el tope de 1600 °/s baja el cambio de trote a galope a ~17 (el trote a 19 iría a 1,58× y daría 1661 °/s).
- **En el trote, el cabeceo empuja los cascos al piso:** con ±0,8° de cabeceo las manos entraban −0,037; sin cabeceo, −0,009. El rebote se lee con el lomo subiendo y bajando.

Aprendido con el jinete zombie (7 clips montados, 2026-10-29):
- **Soldar un jinete:** Weld con Part0 la montura, C0 = `_Seat.CFrame * CFrame.new(D)`, Part1 el HRP y C1 = `HumanoidRootPart.RootRigAttachment.CFrame`. Así la Root queda en `_Seat + D` con cualquier avatar (jinete zombie: D = (0; 0,10; 0)). Mientras va soldado, `PlatformStand` para que el Humanoid no pelee con la soldadura.
- **Piernas contra el barril, con la malla:** la canilla del jinete mide ±0,17 y su caja ±0,24; contra la malla queda afuera (+0,031) y con la caja daría −0,022.
  - La caja del Torso del caballo (1,86 de ancho hasta el lomo) la atraviesa cualquier jinete con las piernas abiertas: no sirve como medida.
  - Para optimizar sirven los cortes en z de la malla del barril (~0,1 ms por punto).
- **Pies sobre una superficie (el asiento, en el salto):** conviene escribir las piernas a mano y resolver solo la altura de la Root. La IK de tres marcas del pie daba giros de cadera de ±90 a 150°.
- **Keys solo de piernas:** se escriben densos (cada ~0,06 s) y en lineal cuando la cadera va en smooth.
  - Un solo key smooth en el medio dejaba el pie a −0,25.
  - Con `out` en la cadera, las rodillas pasaban de 1700 °/s.
- **Torso inclinado ≥ 50°:** una mano con objetivo cerca del cuerpo da el hombro para atrás y el codo plegado (2408 °/s). Conviene apuntar por dirección desde el hombro.
- **Caer de la montura a otro piso:** el clip supone el piso 4,58 debajo del HRP. Para seguir con `GetUp`, el código corre el HRP (−2,3; −2,089; 0,3) en el mismo cuadro en que corta `Fall`.

Aprendido con los Hermanos Doyle (17 clips R15), 2026-10-29:
- **Hacha soldada con el mango a lo largo del antebrazo** (22° del +Y de la mano, filo hacia atrás en reposo):
  - Con la mano como viene, un hachazo para adelante pega con la nuca del hacha.
  - Se arregla con la muñeca en twist 180° (la mano de caja se ve igual) y swing ~95. Así el filo encabeza el golpe, la muñeca queda fija en todo el Chop y solo se mueve el hombro.
  - Con los 7 ángulos libres, el solver daba brazos retorcidos.
- **Exactamente 180° entre dos keys** (muñeca de (95, 0, 180) a (0, 0, 0)): Roblox elige el camino al azar. Hace falta un key a mitad, en lineal. Antes daba 2018 °/s.
- **Caída rígida pivotando en los talones:** la cadera se interpola en línea recta, por la cuerda del arco, y los pies se hunden r·(1 − cos(Δ/2)). Con r ≈ 3,1, keys cada 28° los metían 0,09 y cada ~13°, 0,03.
- **Subir un rifle con las dos manos:** interpolar hombro, codo y muñeca por separado despega la izquierda 0,16 del `_Grip2`.
  - La solución es un key intermedio con el agarre interpolado en el mundo y los dos brazos resueltos de nuevo.
  - Así baja a 0,093.
- **Girar un arma en la mano:** sobre el agarre, que es la articulación de `Body`, sin `pos`. Con `pivot` y `pos` sobre el aro de la palanca, Roblox interpola el CFrame entero y el aro se corre del puño (0,20 con keys cada 90°).
- **Un Hit que no suelte un arma de dos manos:** nombrar brazos y arma con los valores de la guardia. Si se mueven solo cintura y cuello, la izquierda queda a 0,020 del `_Grip2`.
- **Límites de `anim_preview` con un NPC armado:**
  - El chequeo de `_Grip2` usa un punto 0,158 por debajo del centro de la mano, medido en el jugador. En el tirador marca 0,10 cuando el agarre real (el espejo de `rightGrip`) está a 0,02. Arreglarlo pide que `held.py --body` guarde el `rightGrip` en el rig combinado.
  - Una caja de reposo grande en la mano (el hacha, 3,05 × 1,85) tapa el pie apoyado y no sale el `walkAnimationSpeed`. Se mide con un rig de dibujo con el hacha en cajitas.

Aprendido con los NPCs del pueblo (12 clips R15 para 7 cuerpos), 2026-10-29:
- **Choques contra la malla, en las dos direcciones:** cascos convexos de cada pieza, en Python puro (alcanza para cientos de vértices). Con el codo pegado al costado, el antebrazo que cruza por delante se mete 0,30–0,46 en la panza en los 7 cuerpos. Las cajas no lo ven.
  - El castigo de choque del solver tiene que usar todos los vértices: con uno de cada tres veía 0,0007 donde había 0,027 (se salteaba los del codo).
- **Un agachado para cuerpos de distinto tamaño:** bajar la cadera D corre el pie D·(1 − k/k₀). Resuelto en la escala del medio (k₀ = 1,039), los pies quedan entre −0,039 y +0,038 en los 7. Resuelto en el más chico, el más grande flota 0,06.
- **Un Action encima de un Idle:**
  - Nombrar solo cuello y brazos sirve parado, apoyado y sentado.
  - Sobre un Idle muy inclinado las manos se hunden: Talk entraba 0,29–0,33 en el mostrador. Nombrando la cintura (2°) y subiendo las manos 0,3 baja a 0,06.
  - Un clip que arranca con el brazo en reposo, encima de alguien sentado en el piso, mete la mano 0,52 en el piso: ahí no se usa.
- **Martillazo:**
  - El slerp toma el camino corto: de cargado atrás al golpe pasa por abajo y el martillo entra 0,29 en el muslo. Con keys de maza vertical y maza adelante, el arco pasa por arriba.
  - Cargar con la mano a la altura del hombro no se puede (el codo llega al tope de 150°). Se carga con la mano arriba y afuera: hombro 158°, codo 130°.
  - Con `out` en el rebote el pico daba 1592–1993 °/s; con tramos lineales, 1362.
- **Objetos con el eje en el Y de la mano (botella, vaso):** la muñeca no los deja derechos por arriba de la cabeza. Hay que limitar el eje a ~50° de la vertical, o quedan dados vuelta.
- **Lo que va en la derecha apunta adonde apuntan los dedos:** gesticular con la palma arriba hacía que el pico le apuntara al que escucha. Con los dedos 37° o más bajo la horizontal, no.
- **La mano que no se mueve, fija en el mundo:** si su objetivo sigue a la cabeza que gira, la visera la barre a la vuelta (0,10; fija en el mundo, 0,04).
- **Keys correctores en el peor cuadro:**
  - Sirven para brazos: manos que se pisaban, de 0,11 a 0,03; el pico en el piso, de −0,31 a −0,045.
  - Para pies, no: corregir cuadro por cuadro empeora los vecinos (de 0,12 a 0,30). Lo que sirve son keys solo de piernas en todo el tramo, con el tobillo interpolado y subido lo justo.
- **Gestos chicos no se leen de lejos:** una llave de telégrafo de 0,16 son 2 px a 40 studs. Se exageró a 0,32.
- **Sentado o tirado con el HRP de parado:** el clip baja la cadera con `Root.pos` (telegrafista (0; −1,03; +0,15), minero (0; −2,16; +0,45)). El HRP no se mueve y el código no tiene que correrlo.
- **Límites:**
  - El piso de `anim_preview` usa la caja de reposo del accesorio: el pico del minero (2,73 × 1,14) da −0,184 y −0,081 donde la malla da −0,014 y −0,045.
  - `anim_sheet` dibuja los accesorios como cajas (el pico parece una losa), no dibuja muebles, no tiene vista de frente y no muestra un clip encima de otro. El agente armó `sheet2.py` con todo eso (scratchpad `npcs/`).
  - Medir el castigo de choques contra los 7 cuerpos con todos los vértices es lento: Cower tardó 10–15 min por corrida.

- **Herramientas que faltan** (armadas en el scratchpad de la sesión y no pasadas a `tools/`):
  - una hoja con la malla real y los colores (la caja de la cabeza del toro tapa todo en `anim_sheet`), con muebles y vista de frente;
  - vistas desde abajo y desde arriba;
  - medición de choques entre piezas, contra la malla;
  - simulación de fundidos y de un clip encima de otro;
  - pies que patinan fuera de las caminatas.

## Efectos (D025)

1. **Texturas:** `py -I tools/vfx/textures.py` las genera en `assets/vfx/textures/`.
2. **Subirlas:** con `upload_image` del MCP de Studio, que baja cada imagen de una URL http y la sube con la cuenta logueada en Studio. No usa la API key.
   - Se sirve solo esa carpeta, un rato: `py -I -m http.server 8766 --bind 127.0.0.1 --directory assets/vfx/textures`. Se cierra apenas termina la subida.
   - Los ids van a `assets/vfx/textures/_ids.json`, por nombre (`"flame": "rbxassetid://…"`).
3. **Armar:** `lune run tools/roblox/vfx_build.luau` escribe `assets/vfx/rbx/WesternVFX.rbxm`: una carpeta `VFX` con un Attachment por efecto, que el módulo Emit de roclicks reproduce. Avisa qué texturas no tienen id.

Medido en Studio el 2026-10-28:
- El `.rbxm` se deserializa con los 10 efectos y sus capas.
- Las 7 texturas cargan, son de tipo Image y quedaron a nombre del usuario 117522482.
  - `ContentProvider:PreloadAsync` con el id como texto da `Failure`. Con un Decal que usa ese id da `Success`.
- **No revisado a la vista:** en el place "Experiencia sin título", `screen_capture` con `camera_position` no mostró la escena que se armó, porque aparecían terreno y agua que no existen en esa zona. La revisión cuadro por cuadro queda para el sandbox, en Play, con `Capture`.

## Subida (Open Cloud)

- **Key:** Assets API, Read + Write. La crea Valentin y la guarda en `~/.roblox/open-cloud-key.txt` (o en `ROBLOX_API_KEY`). El script nunca la imprime.
- **Formatos:** un Model acepta `.glb` y llega como paquete. Una Animation acepta `.rbxm`. Studio no sube animaciones por código: `CreateAssetAsync` acepta Model, Mesh, Image, Plugin y Audio.
- **Sin duplicados:** cada subida crea un asset nuevo. `opencloud.py` no vuelve a subir un archivo que no cambió (compara el hash).

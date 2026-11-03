# Construir un modelo que se vea profesional

El método viene de `vendor/skills/majidmanzarpour-blender-game-skills` (fases con capturas comparadas, silueta antes que detalle) y de `vendor/skills/el4cteo-blender-skills/skills/blender-hardsurface-modeling` (booleanas, densidad de facetas), adaptado a nuestro low poly de colores planos. Lo medido con el caminante A está marcado **(medido)**.

## Fases (no saltar de la 1 a la 3)

1. **Silueta.** Solo las masas grandes, a la medida del prompt, con cada pieza en su origen (pivote o articulación). Construir y mirar el frente y el costado: ¿se lee como lo que es, en negro, a 96 px (`review_small.png`)? Las medidas (alto, ancho, alturas de articulaciones) tienen que estar a ±5 % del prompt antes de seguir.
2. **Formas.** Lo que cambia la silueta de cerca: capas de ropa, actitud modelada en torso y cabeza, la forma de la cara, cuñas y chanfles. Volver a mirar: ¿la silueta de la fase 1 sigue igual?
3. **Detalle.** Huecos tallados, color pintado y piezas de detalle (ojos, dientes, remaches, costillas). Solo el detalle que sobrevive a 30-40 studs.
4. **Limpieza.** Nada flotando, nada coplanar, revisión que pasa. Triángulos cerca del tope; si hacen falta más para que se vea bien, se usan y se anota por qué.

Después de cada fase: construir, mirar, anotar las diferencias como medidas, corregir. Lo que no se ve en la captura no está terminado.

## API de modelkit en la práctica

- **Formas cerradas:** `box` (con `top` y `shift` para troncos y cuñas), `cyl`, `ball`, `hull` (el casco convexo de una lista de puntos, la más versátil) y `prism` (un perfil 2D no convexo, extruido). Los anillos de puntos (`ring` de 8 lados, `round_ring` de 10-12) se arman en la receta, como en el caminante A.
- **Formas no convexas:** se juntan varios cascos dentro de la misma pieza, que **se meten 0,02-0,05 uno en otro**. Nunca se tocan apenas ni quedan separados.
- **`detail=True`:** lo que va adentro de un hueco tallado o encima sin mezclarse (ojos, dientes, hebillas, tiradores, harapos). No lo afectan `smooth`, `carve` ni `paint`.
- **`carve(part, mat, points=… | prism=…)`:** talla un hueco real y las paredes toman `mat`. Sirve para cuencas, bocas, mordidas, roturas, muescas y ranuras.
  - Cortadores con `subdiv=0` y pocos puntos: cada booleana suma triángulos **(medido: unos 30 % más en la cabeza)**.
  - `use_self` va siempre activado. Sin él, con varios cascos cruzados, la booleana se come el volumen **(medido: desapareció el cráneo)**.
  - El cortador sale de la superficie hacia afuera, con margen.
- **`paint(part, mat, box=… | ball=…)`:** tiñe las caras de la base cuyo **centro** cae en la zona, sin geometría encima.
  - Una cara grande se tiñe entera **(medido: un triángulo oscuro gigante en la mejilla)**. Pintar solo donde las caras ya son chicas, o cortar antes con `slice` para crear bordes.
  - Si la mancha tiene que ser chica en una cara grande, mejor tallarla poco profunda o resolverla con la forma.
- **`slice(part, point, normal)`:** agrega bordes, por ejemplo para una banda de color (cinturón, puño de bota) sin otra pieza encima.
- **`smooth(part, level=1)`:** redondea con caras planas. Multiplica los triángulos por ~4, así que se usa solo en piezas chicas u orgánicas clave. Para redondear barato, anillos de 10-12 lados.

## Recetas por tipo

**Humanoide R15** (`Walker_A` es la referencia):
- **Articulaciones:** las alturas del Bloque D como constantes arriba de la receta. Cada pieza R15 lleva el origen en su articulación.
- **Brazos y piernas:** `limb()` de anillo a anillo, con 0,05 de solape en cada punta. Puños, botas y cinturón tapan las uniones.
- **Cabeza** (1/5 de H): cráneo de 4-5 `round_ring`, más ceja, nariz y mandíbula como cascos.
  - Cuencas y boca **talladas**.
  - Ojos en su propia pieza (`Eyes`), como bolitas `subdiv=0` adentro de las cuencas.
  - Dientes de detalle **apoyados en la pared de la boca**: se extienden hacia adentro, si no flotan **(medido)**.
- **Actitud:** se modela en `UpperTorso` y `Head`, por ejemplo girando todos los puntos de la cabeza alrededor del cuello. Brazos y piernas quedan rectos.
- **Manos:** mitón de 3 `round_ring` más el pulgar.
- **Ropa:** cada capa 0,03-0,04 por fuera de la de abajo. Un chaleco abierto se arma como espalda entera más dos paneles de adelante; con dos mitades queda una franja en la espalda **(medido)**.
- **Accesorios** (`Acc_Hat`…): pieza propia, con el origen en su base y tocando la cabeza.

**Criatura:** igual que el humanoide, con las piezas y los orígenes del prompt. La pose de reposo es la del prompt.

**Arma o ítem:**
- **Origen y frente:** el origen en el centro de la empuñadura y el caño hacia −Z.
- **Piezas móviles:** cada una lleva el origen en su eje (`part(name, origin=eje)`) y la geometría alrededor. Todo lo que se mueve al recargar es pieza propia, con un hueco o costura visible.
- **Marcadores:** con `mk.marker("_Muzzle", pos)`.

**Destructible:** cada fragmento es una pieza `fragNN`, convexa (un `hull` o una `box`), de al menos 0,4 de grosor. Los cortes siguen la construcción (tablas, ladrillos, grietas en zigzag con `prism`) y no hay huecos entre fragmentos. Lo que queda en pie es `fixed_<Name>`.

**Kit modular:** la grilla del documento (módulo de 8, planta de 10, puerta de 4 × 7,5). Las puntas tienen que calzar exacto con el módulo vecino.

## Lo que hace que se vea profesional

- **Silueta:** exagerar los 2-3 rasgos que identifican el modelo y cuidar la asimetría (un hombro más bajo, el sombrero torcido). Si a 96 px no se reconoce, no hay detalle que lo salve.
- **Valores:** áreas grandes vecinas con contraste de claro y oscuro (camisa clara contra chaleco oscuro). Un color saturado solo en el foco (pañuelo rojo, sangre en la boca). Hasta 12 colores en personajes.
- **Tres niveles de detalle en el foco** (cara, frente del arma): forma grande, forma secundaria, detalle chico. El resto, dos niveles.
- **Profundidad real:** lo hundido se talla y lo que sobresale se modela. Nunca cajitas de color pegadas encima, que se leen como calcomanías y titilan.
- **Facetas parejas:** formas orgánicas con anillos de 10-12 lados, duras con 6-8. Nada de astillas largas; `process_model` une las caras coplanares del mismo color.
- **Contacto:** todo toca o se mete un poco en lo que lo sostiene. Nada flota ni queda coplanar con otra pieza.
- **Piezas apiladas** (tramos de un cilindro, vaina y culote, caño y anillo): se encimar 0,003-0,01 y con radios apenas distintos. Si dos tramos se tocan justo en un anillo igual, la soldadura de `process_model` los une y quedan bordes rotos **(medido: vainas de rifle y escopeta)**.
- **`top` en cilindros:** achica el extremo +eje (en `axis="z"`, el de atrás, +Z). Para una punta adelante (bala, cono hacia -Z): radio chico y `top` > 1.
- **Presupuesto:** la calidad manda; el tope del prompt es una referencia. Gastar los triángulos donde se mira (cara, manos, frente) y no en la espalda ni abajo. Si el modelo mejora pasándose, se pasa y se anota.
- **Chanflanes** (`mk.bevel`): un segmento a 45° en los bordes que mandan (armazón, caño, cilindro, bordes de armas y herramientas) para que agarren luz. Selectivos y exagerados: en todos los bordes se lee como un contorno dibujado.

## Lo que encontraron los agentes en paralelo (2026-10-28)

- **Vértices compartidos dentro de una pieza:** `process_model` suelda los vértices iguales de cascos distintos. Dos cajas que se tocan en una esquina dejan bordes con cuatro caras. Hay que encimarlas 0,003-0,004 o meter un casco en el otro, y nunca dejar dos cascos metidos a la misma profundidad: sus caras quedan coplanares y el QA lo marca como z-fighting. Para el QA es coplanar todo lo que difiere menos de ~2,6°.
- **Booleanas con caras coplanares:** un chanflán o un tallado sobre caras coplanares dentro de una pieza rompe bordes (no-manifold). Las formas finas y cóncavas, como un gatillo, van con `detail=True`. Para encontrar al culpable, construir salteando una forma por vez.
- **`carve`** corta todo lo que hay en la base dentro del cortador. Lo que va adentro de un hueco (balas en una caja, dientes) va con `detail=True`.
- **`paint`** toma también las caras de costado de lo que sobresale poco: hay que acotar la caja de pintura en profundidad.
- **Un casco convexo se traga las cinturas** (cuellos de botella, gargantas): van en cascos separados. Un perfil de ancho variable (martillos enrulados, volutas, colas) va con un `prism` del contorno.
- **`bevel(angle=50)`** solo toca bordes de 90°: las secciones tienen que tener esquinas a 45°. Con 56°, el mango del cuchillo pasó de 300 a 748 triángulos.
- **Aros con agujero de verdad:** un prisma del contorno más `carve(prism=…)` del agujero.
- **Rebaje barato:** un `carve` de 0,008 con el mismo material da un segundo nivel de detalle en superficies grandes.
- **Grietas en fragmentos:** recortar cada capa en 2D contra cada lado de la grieta y extruir con `prism`. Está en la receta de `WST_Prop_CrateLarge`.
- **Telas y sogas que cuelgan:** `strip()`, un perfil desplazado a lo largo de una línea, extruido con `prism`. En tramos de tela, anchos alternados ±6 %; en soga, octógono con una arista hacia el eje.
- **Lo que se sostiene en la mano (D024):** lleva el marcador `_Grip` donde cierra la mano, y `_Grip2` donde va la izquierda si es de dos manos. Su pieza raíz se llama `Body`.
- **Ropa por capas (NPCs):**
  - **Estructura:** el torso es una serie de niveles (y, cx, cz, w, d). Cada capa crece g y se recorta con sus propios planos (sacos abiertos, pecheras, delantales). La espalda va 0,012 más afuera que los paneles de adelante.
  - **Correas sobre la superficie:** dos tramos seguidos tienen que doblar más de 3° y alternar 0,004 de espesor.
  - **Parches y bolsillos:** van con una grilla de 3×3 puntos. Con 4 esquinas, el torso convexo los atraviesa por el medio.
- **Cara viva (NPCs):**
  - **Rasgos:** la ceja sigue la curva de la frente, y el ojo lleva blanco e iris.
  - **Expresión:** la da la altura del párpado de detalle (4,735 cansado, 4,758 relajado, 4,79 bien abierto).
  - **Boca:** tallada con un prisma sobre un volumen propio de boca y mentón.
  - **Bigote:** 0,16 por delante de la barba.
  - **Anteojos:** el vidrio es opaco en Studio, así que va solo como reflejo o media luna.
- **Personajes de otra altura:** una escala uniforme K = H / 5,2 deja reusar las articulaciones del Bloque D.
- **Accesorios en la cabeza inclinada:** van con `hp(centro)` y `rot=(HEAD_TILT, 0, 0)`, o como casco de puntos pasados por `head()`.
- **Recipiente abierto (tina, caja):** un casco más un `carve` del casco interior. Las paredes salen unidas y el adentro toma el material del tallado.
- **Anillos (llantas, pinas):** dos medios anillos con `prism`, encimados 1° y con 0,004 de diferencia de ancho.
- **Tablas con junta real:** cajas separadas 0,05 sobre un alma oscura metida 0,03 por las dos caras.
- **Manchas irregulares:** primero `slice` con planos en diagonal, después `paint`.
- **Detalle sobre curvas:** funciones que devuelven punto y normal sobre la sección. Las correas son cadenas de cascos con la normal como espesor.
- **Reusar entre recetas:** una receta importa otra por ruta con `importlib`. El caballo zombi usa el esqueleto del caballo y la carreta del buhonero usa la rueda.
- **Placas que se doblan:** un casco plano por faceta. Los listones sobre un techo en arco van sobre la cuerda, no sobre la curva.
- **`bevel` en cilindros:** `angle` tiene que pasar el ángulo entre caras (10 lados = 36°, así que 40).
- **Piezas de un personaje con rig:** lo que cruza varias piezas (riendas, armaduras, vetas) se parte por pieza para que siga la animación.
- **Quiebres:**
  - **En zigzag sin luz:** dos `carve` complementarios con el mismo perfil de `prism`.
  - **En un sólido simple:** un plano en diagonal (dos cascos convexos) y el tramo de arriba corrido 0,02-0,03.
  - **Fragmento en L:** un solo `prism` con perfil en L.
- **Pared de tablones:** el tablón del medio va hundido 0,02-0,03 de los dos lados. Si no, las caras interiores titilan.
- **Rueda de rayos:**
  - La pina va en dos medias coronas (`prism`).
  - La llanta se pinta con bolas chicas en el centro de cada cara.
  - Los rayos son barras que cruzan el cubo: 6 barras dan 12 rayos, ~196 triángulos.
- **Juntas de duelas:** `bevel(angle=30, mat=oscuro)` sobre 10 lados.
- **Codos (cactus, ramas):** cada tramo se pasa 0,7 r de la junta, con radios alternados 1 / 0,97.
- **Capas agrandando puntos:** la capa tiene que crecer también en y en los anillos de arriba y de abajo. Si no, las tapas quedan coplanares (en el BloatedMiner fueron 43 pares).
- **Cortadores:** entran al menos 0,05 en la superficie. Si terminan pegados a una cara, dejan bordes abiertos.
- **Apoyar algo sobre una superficie curva** (vetas, lágrimas, tirantes, placas): rayos desde afuera contra los cascos de `humanoid.py`. Las manchas chicas, como el tizne, van como un tallado de 0,012 que sigue la cara, no pintadas.
- **Tiras de cascos encadenados:** el final que se encastra en el tramo siguiente se achica 20 % y sube 0,004.
- **Formas planas no convexas** (un ala con un mordisco, una placa partida): un prisma con el contorno, sin booleana.
- **Overlays:** se revisan montados sobre su caminante, no solos, y con la cabeza caída se mira también la vista de frente.
- **Unión gratis:** si una pieza tiene al menos un `carve`, la booleana con `use_self` une todos los cascos de la base y deja de haber z-fighting entre ellos. Un `carve` sin efecto (el cortador lejos) dispara la unión.
- **Fragmentos en escalera** (paredes de ladrillo o piedra): un prisma con el perfil de las hiladas, recortado por dos cortadores en escalera. Los vecinos comparten el mismo escalón: sin huecos ni solapes.
- **Juntas baratas:** `slice` más `paint`. Un solo corte sirve para la cara de afuera y la de adentro.
- **Surco en V entre piedras:** cada piedra es un casco de 8 puntos con la cara de adelante achicada 0,05 por lado, sin núcleo de mortero (de 2400 a 750 triángulos por pared).
- **La cara de corte de un fragmento,** en el color de la madera fresca: queda oculta mientras la pieza está entera y se ve al romperse.
- **Filas de variantes:** ninguna en el origen. Una pieza suelta con origen en (0,0,0) que no toca nada se marca como flotante.
- **Torcer un edificio sin abrir esquinas:** cortar los perfiles 2D del frente y del fondo (x += y · tan θ) y girar los costados.
- **Huecos en piezas fijas:** partirlas en piezas que no rodeen el hueco, así el casco convexo de colisión deja pasar.
- **Calzar en el hueco de otro modelo:** el intradós, más chico que la cuerda del polígono del otro (r · cos(180 / 2n)).
- **`ball` con subdiv=1** ya es el icosaedro de 20 caras: con subdiv=0 no baja.
- **Piezas acostadas o inclinadas:** un proxy de transformación que envuelve `mk` y aplica rotación y traslación a todo (`XK` en la receta de `WST_Train_Wreck`). Reusa sin cambios las ayudas de otra receta.
- **Ruedas de 12 lados:** girarlas 15° para que apoyen en un vértice. Si no, quedan 0,05 arriba del riel.
- **Medidas de juego** (despeje del túnel, alto de pisos): se calculan en la receta para que den exactas, no se miden después.
- **Tapajuntas, molduras y herrajes:** como detalle a 0,001 de la pared, no en la base. En la base va solo lo que se talla. Un casco metido en una pared abre un agujero y la llena de astillas (+150 triángulos por abertura en la estación).
- **Fondo de un hueco tallado** (vidrio, tablero): se pinta con una caja fina a la profundidad del fondo, sin una caja aparte.
- **Rocas con grietas reales:** intersección de semiespacios (celda de Voronoi, planos tangentes a un elipsoide girado y piso). Los vértices se calculan con tríos de planos y van a `hull` (derrumbe, rocas, mesas).
- **Estratos:** un prisma por estrato, cada uno con sus propios quiebres en x. Si caen en las mismas x, se lee como pared de ladrillos.
- **Franja de grieta entre fragmentos:** arrancarla 0,01 del lado que se tira. Si comparte la cara del corte, la booleana deja bordes invertidos.
- **Fragmentos de pared como polilíneas:** cada fragmento es un solo prisma de su contorno, y las ventanas y agujeros son muescas de la grieta. Así ningún fragmento rodea un hueco. La grieta en zigzag de 3-5 quiebres sale ~1000 triángulos más barata que una escalera tabla por tabla.
- **Pintar caras que después se tallan:** si una talla parte la cara, el centro de cada pedazo se sale de la caja de pintura. Una cadena de cajitas a lo largo de la línea lo resuelve.
- **Un prop que se recorre por adentro** (matadero, establo) va partido en piezas convexas, así la colisión no tapa puertas ni interiores.

# Revisión: cuándo un modelo está terminado

Un modelo está **construido** solo cuando pasan las tres partes. Cada problema se escribe como medida y se corrige en la receta; lo que se acepta sin corregir va a la sección "Revisión" del docstring de la receta con el motivo.

## 1. Números (`report.json`)

- [ ] `pass: true`: sin errores de revisión (z-fighting, caras invertidas, partes flotando que no sean móviles, materiales fuera de la paleta).
- [ ] Triángulos: el tope del prompt es referencia, no techo (calidad primero). Si se pasa, el exceso está justificado en la receta (qué mejora). Si queda por debajo del 50 %, revisar si falta detalle en el foco. Menos de 10 000 por pieza.
- [ ] Medidas (`size_studs`) a ±5 % de las del prompt (alto, ancho, largo).
- [ ] Nombres de piezas exactos a los del prompt (`objects`), ni uno más ni uno menos, sin `.001`.
- [ ] Avisos de "enclosed" o "floating": cada uno, mirado en la captura y resuelto o explicado (una pieza móvil puede no tocar; un ojo adentro de una cuenca, no).

## 2. Capturas

Generar el primer plano y la distancia de juego:

```
"$LOCALAPPDATA/Programs/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 -P tools/blender/review_model.py -- <Id> --focus <piezas del foco>
```

Abrir con Read `review_material.png` (las cuatro vistas: frente, 3/4, costado, espalda), `review_focus.png`, `review_small.png` y `review_random.png` (un color por pieza: delata lo que flota o lo que está en la pieza equivocada).

- [ ] **Frente:** la primera vista es el frente del modelo. Si muestra la espalda, el frente está mal.
- [ ] **Distancia de juego:** a 96 px (`review_small.png`) se reconoce qué es, y en un personaje, qué variante es.
- [ ] **Proporciones:** las del prompt y las de la imagen de concepto si hay. Las diferencias, como medidas.
- [ ] **Foco con tres niveles de detalle:** en una cara, forma de la cabeza, rasgos (ceja, nariz, mandíbula) y detalle (dientes, ojos, sangre).
- [ ] **Sin calcomanías:** ningún parche de color pegado encima ni caras coplanares de dos colores. El color va pintado o es la pared de un hueco tallado.
- [ ] **Superficies:** sin astillas ni triángulos gigantes teñidos, facetas parejas y lo orgánico redondeado.
- [ ] **Contacto:** nada flota y las uniones de R15 están tapadas (puños, botas, cinturón, cuello).
- [ ] **Valores:** se distinguen las áreas grandes vecinas y el acento de color está en el foco.
- [ ] **Lo que pide el prompt está y se ve:** contar los daños, accesorios, marcadores y piezas móviles. Si el prompt pide tres daños, se ven tres.
- [ ] **Con imagen de concepto:** compararla lado a lado con `review_material.png` y anotar las desviaciones.

## 3. Coherencia con el resto

- [ ] **Escala:** al lado del jugador de referencia (2 × 5 × 1, en el visor) tiene sentido. Una puerta deja pasar al jugador y un enemigo humano mide como él.
- [ ] **Familia:** si hay un modelo hermano terminado (otro caminante, otra arma), comparten proporciones, densidad de facetas y paleta. No parecen de juegos distintos.
- [ ] **Studio:** los nombres y orígenes que pide el sistema que lo va a usar (R15, `fragNN`, `_Muzzle`, `Acc_`) están, porque así lo exige el prompt.

## Cuándo frenar

Seis vueltas como máximo. Si después de seis una medida sigue fuera o un ítem no pasa, el modelo queda `falló` con el detalle. Es mejor un fallo bien explicado que un modelo mediocre marcado como construido.

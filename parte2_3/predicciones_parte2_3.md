# Predicciones — Partes 2 y 3 (Luis)

Escritas el 2026-10-10 a las 15:10, **antes** de compilar y de correr cualquier experimento.
Todavía no he visto los resultados ni las predicciones de mi compañera.

Equipo en el que voy a medir: Intel Core i5-12450H (12.ª gen), 8 núcleos físicos
(4 de rendimiento con Hyper-Threading + 4 de eficiencia sin HT), 12 hilos lógicos.
Corre dentro de WSL2 (Ubuntu), así que pmax = 12.

---

## Parte 2a — El Ts honesto (amdahl, fp = 1.00, fila p = 1)

**Predicción:** t_seq y t_par (p = 1) van a ser casi iguales. Espero que la versión OpenMP con
un hilo sea un poco más lenta, entre 0 % y 3 %, porque igual tiene que crear la región
paralela y combinar el `reduction`, pero eso es muy poco comparado con 400 000 unidades de
~1 µs (~0.4 s de trabajo). El trabajo de cada unidad es exactamente el mismo código en las
dos versiones.

---

## Parte 2b — Sumar N números

**Pregunta de la guía:** ¿a partir de qué N la versión paralela empieza a ganarle a la secuencial?

Razonamiento:
- La suma secuencial con `-O2` no se vectoriza (es una reducción de `double` y sin
  `-ffast-math` el compilador no puede reordenar las sumas). Cada suma depende de la anterior,
  así que calculo ~4 ciclos por elemento → a ~4 GHz es **~1 ns por número**.
- Abrir un `parallel for` con 12 hilos (despertarlos, repartir, combinar el `reduction` y la
  barrera final) cuesta del orden de **2 a 5 µs** cada vez.
- La paralela gana cuando el trabajo que ahorra, N·1 ns·(1 − 1/p), supera ese overhead
  fijo: N ≈ (3 a 5 µs) / (1 ns · 0.92), es decir, **N ≈ 3 000 a 8 000 números**.

**Predicción concreta con los tamaños del programa (16, 1024, 65 536, 1 048 576, 16 777 216):**
- N = 16 y N = 1024: la paralela pierde. Con N = 16 la secuencial tarda ~20 ns y la paralela
  unos µs → **la paralela va a ser entre 100 y 300 veces más lenta** con p = 12.
- N = 1024: todavía pierde (~1 µs de trabajo contra ~3 µs de overhead), S ≈ 0.3–0.5.
- **N = 65 536: aquí ya gana**, espero S ≈ 4–6 con p = 12.
- N = 1 M (8 MB, cabe en los 12 MB de L3): S ≈ 6–8 con p = 12.
- N = 16 M (128 MB, no cabe en caché, sale de RAM): S más bajo que con 1 M, ≈ 4–6, porque
  todos los núcleos comparten el ancho de banda de memoria.
- No espero llegar a S = 12 en ningún caso: tengo 4 núcleos de eficiencia más lentos, los
  hilos de Hyper-Threading comparten núcleo y con un solo hilo el turbo sube más la frecuencia.

---

## Parte 3 — Desbalance de carga

**Pregunta de la guía:** con p = 4 y `static`, ¿qué fracción del trabajo total le toca al último
hilo? ¿Qué speedup esperas?

El costo de la iteración i es `1 + 2000·i/W` (crece como una recta de ~1 a ~2001).
El trabajo total es el área bajo la recta ≈ W·1001.

Con `static` y p = 4, el último hilo recibe las iteraciones de 3W/4 a W. Su trabajo es el
área del trapecio:

- costo promedio en ese bloque = 1 + 2000·0.875 = 1751
- trabajo = (W/4)·1751 = 437.75·W
- fracción = 437.75 / 1001 ≈ **0.437 ≈ 7/16 del trabajo total**

Como el tiempo paralelo lo marca el hilo más cargado:
**S(p=4, static) ≈ 1 / 0.437 ≈ 2.3** (en vez de 4).

En general (despreciando el +1): fracción del último hilo = (2p − 1)/p², así que
S_static ≈ p² / (2p − 1):

| p | fracción último hilo | S static predicho |
|---|---|---|
| 2 | 3/4 = 0.75 | 1.33 |
| 4 | 7/16 = 0.44 | 2.29 |
| 8 | 15/64 = 0.23 | 4.27 |
| 12 | 23/144 = 0.16 | 6.26 (en el mejor caso) |

**Predicción para pmax = 12:**
- `static`: menos que el 6.26 del modelo, **S ≈ 4.5–5.5**, porque el último bloque (el más
  caro) le puede caer a un núcleo de eficiencia o a un hilo que comparte núcleo por HT.
- `dynamic` (bloques de 64): reparte bien, **S ≈ 7–9**. No llega a 12 por los núcleos E, el HT y
  el turbo.
- `guided`: casi igual a `dynamic`, **S ≈ 7–8.5**. Los bloques grandes del inicio son las
  iteraciones baratas y los pequeños del final son las caras, así que también balancea.
- **Gana `dynamic`** (o empata con `guided`) y le saca a `static` alrededor de **1.6× en S(12)**.

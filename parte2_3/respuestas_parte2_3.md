# Lab 12 — Partes 2 y 3 + reto (Luis)

Todo lo de esta carpeta se midió en mi equipo. Las predicciones están en
[predicciones_parte2_3.md](predicciones_parte2_3.md), escritas antes de compilar y correr.

**Dónde está cada cosa:** los CSV y gráficas oficiales de estas partes (`suma.csv`,
`desb_*.csv`, `suma_con_S_E.csv`, `desbalance_con_S_E.csv`, `suma_speedup.png`,
`desbalance_*.png`) están en [`../results/`](../results/), junto con los de las Partes 1 y 4.
Todo lo demás (repeticiones, experimentos extra, reto, capturas) está en esta carpeta. Las
capturas muestran `tee parte2_3/...` porque al medir los archivos se guardaron aquí; después
se movieron a `results/` sin cambios.

**Versión del código:** las Partes 2 y 3 se midieron con el `lab12_speedup.c` **original del
starter**. La versión del repo (modificada en las Partes 1 y 4: validación de argumentos,
`omp_set_dynamic(0)` y `parallel` + `for nowait` + `barrier`) da los mismos resultados en
desbalance y en la suma con N grande. En la suma con N chico la versión del repo es un poco más
lenta por la barrera extra. Ver la sección [Verificación con el código del repo](#verificación-con-el-código-del-repo)
al final.

## Datos del equipo

| | |
|---|---|
| CPU | Intel Core i5-12450H (12.ª gen, Alder Lake-H) |
| Núcleos físicos / lógicos | 8 / 12 |
| Rendimiento / eficiencia | 4 núcleos P (Golden Cove, con Hyper-Threading → 8 hilos) + 4 núcleos E (Gracemont, sin HT → 4 hilos) |
| Hyper-Threading | Sí, solo en los núcleos P |
| Caché | L2 1.25 MB por núcleo P, 2 MB compartida por el grupo de 4 núcleos E (7 MB en total); L3 12 MB compartida |
| RAM | 2 × 8 GB DDR4-3200, doble canal (51.2 GB/s teóricos) |
| Entorno | Windows 11 + WSL2 (Ubuntu 24.04), gcc 13.3, `-O2 -fopenmp`, pmax = 12 |

Ojo: dentro de WSL, `lscpu` dice "6 cores × 2 threads" (captura `01_lscpu.png`). Es la vista
virtualizada de Hyper-V: los 12 vCPU se ven idénticos, así que **ni Linux ni OpenMP saben cuáles
caen en núcleos P o E**. El dato real (8 núcleos, 12 lógicos) sale del lado de Windows
(`01b_cpu_windows.png`).

**Condiciones de medición:** laptop conectada a la corriente (batería al 100 %). Durante las
corridas había apps abiertas (Spotify, Edge, Cursor, VS Code), que sumaban un ~10–15 % de CPU.
Por eso, además de la corrida oficial (la de las capturas), repetí cada experimento 5 veces
más (`repeticiones/`). Con **p ≤ 8 las corridas varían menos de ±5 %**. Con **p = 9–12 varían
mucho**: se están usando los 12 hilos lógicos y cualquier proceso de fondo le quita CPU a un hilo.

---

## Parte 2a — El Ts honesto

Datos (`amdahl_fp100.csv`, fila p = 1): t_seq = 1.521067 s, t_par = 1.478568 s.

**1. ¿Cuál es más rápido y por cuánto?**
En la corrida oficial, la versión OpenMP con 1 hilo salió **2.8 % más rápida**
((1.521067 − 1.478568) / 1.521067 = 0.028). No tiene sentido que agregar OpenMP acelere el
mismo trabajo, así que lo repetí 5 veces (`repeticiones/amdahl_fp100_p1_5corridas.csv`):

| corrida | t_seq | t_par (p=1) | diferencia t_par vs t_seq |
|---|---|---|---|
| oficial | 1.5211 | 1.4786 | −2.8 % |
| r1 | 1.4820 | 1.5290 | +3.2 % |
| r2 | 1.4933 | 1.5186 | +1.7 % |
| r3 | 1.5014 | 1.4892 | −0.8 % |
| r4 | 1.4713 | 1.4894 | +1.2 % |
| r5 | 1.4874 | 1.4694 | −1.2 % |

La mediana de la diferencia es **≈ +0.2 %**: con este trabajo (~1.5 s) las dos versiones son
**iguales dentro del ruido de medición (±3 %)**. El overhead de abrir una región paralela con un hilo
(~0.4 µs, ver abajo) es insignificante comparado con 1.5 s.

Pero con trabajo pequeño la cosa cambia por completo. En `suma.csv`, con N = 16, la secuencial
tarda 5 ns y la OpenMP con 1 hilo tarda 389 ns, es decir, **78 veces más lenta**. Con N = 1024,
1015 ns contra 1532 ns: **51 % más lenta**. Esos ~0.4–0.5 µs de diferencia son el costo fijo de
la región paralela aunque haya un solo hilo.

En el equipo de Nina (i7-1165G7, `results/amdahl_fp100.csv`) pasa lo mismo: t_seq = 0.673 s
y t_par(p = 1) = 0.671 s, es decir, 0.3 % de diferencia. Eso es menos que la resolución de su
reloj (en Windows nativo todos sus tiempos son múltiplos de 1 ms), así que las dos versiones
también son iguales en su máquina.

*Predicción:* dije que OpenMP con 1 hilo sería 0–3 % más lento. Para amdahl acerté en que la
diferencia es despreciable (salió 0 % ± 3 %). Lo que no predije es que con trabajo pequeño esa
misma diferencia llega a 78×.

**2. Si alguien usa como Ts el programa paralelo con 1 hilo, ¿el speedup sale inflado o desinflado?**
**Inflado.** T1 paralelo incluye el overhead de OpenMP, así que es ≥ Ts real, y dividir entre un
número más grande da un S más grande. Es tramposo porque compara contra una versión
secuencial artificialmente lenta que nadie usaría: un usuario real compararía contra el mejor
programa secuencial.
Ejemplo con mis datos (suma, N = 1024, p = 2): S honesto = 1015 / 1443 = **0.70** (la paralela
pierde), mientras que S con T1 paralelo = 1532 / 1443 = **1.06** (parece que gana). El "truco"
convierte una pérdida en una ganancia.

---

## Parte 2b — Sumar N números

Datos: `suma.csv` (oficial, gráfica `suma_speedup.png`), 5 repeticiones en `repeticiones/` y un
experimento extra con tamaños intermedios para la pregunta 6 (`extra/`, gráfica
`extra_suma_umbral.png`).

| N | Ts | S p=1 | S p=2 | S p=4 | S p=8 | S p=12 |
|---|---|---|---|---|---|---|
| 16 | 5 ns | 0.013 | 0.005 | 0.003 | 0.001 | 0.0002 |
| 1 024 | 1.0 µs | 0.66 | 0.70 | 0.52 | 0.24 | 0.03 |
| 65 536 | 72 µs | 0.98 | 1.90 | **3.29** | 2.64 | 1.15 |
| 1 048 576 | 1.25 ms | 1.01 | 2.01 | **3.63** | 1.55* | 0.57* |
| 16 777 216 | 20.9 ms | 1.01 | 2.01 | 3.76 | **4.52** | 3.21 |

\* Valores muy variables. En las 6 corridas, N = 1 M con p = 8 dio entre 1.5 y 5.2 (mediana 3.9),
y con p = 12 entre 0.6 y 3.1 (mediana 1.5).

**3. Con N = 16 y p = pmax, ¿cuánto vale S?**
S = 0.000000005 / 0.000021736 = **0.00023**: la versión paralela es **≈ 4 300 veces más
lenta** (5 ns contra 21.7 µs). En las 6 corridas quedó entre 2 800× y 6 700× más lenta.

*Predicción:* dije entre 100 y 300 veces. Ese rango calza con p = 2 (218×) y p = 4 (342×), pero
con p = 12 me quedé corto por más de 10×. Subestimé cuánto cuesta despertar y sincronizar 12
hilos dentro de una máquina virtual (WSL2) con otros programas usando CPU.

**4. Modelo de dos fases (16 números, p = 4 → Tp = 5 sumas, S = 3). ¿Qué supuesto no se cumple? ¿Qué fuga es?**
El modelo supone que **repartir el trabajo, sincronizar y combinar resultados es gratis o
cuesta lo mismo que una suma** (cada paso del árbol cuesta 1). En mi máquina, con N = 16 y
p = 4, Tp = 1708 ns. La suma secuencial cuesta ~0.3 ns por número, así que esos 1708 ns
equivalen a **~5 000 sumas, no a 5**. Casi todo ese tiempo es comunicación y sincronización
entre hilos. Es la fuga **η_c (comunicación y sincronización)**.

**5. ¿Qué hace OpenMP en cada `parallel for` además de sumar? ¿En qué se va el tiempo con N = 16?**
1. Despertar a los hilos del pool (en Linux es un `futex`; dentro de WSL2, despertar otro vCPU
   pasa por el hipervisor).
2. Calcular qué bloque le toca a cada hilo (`schedule(static)`).
3. Que cada hilo cree e inicialice su copia privada de `s`.
4. La suma en sí. Con N = 16 y p = 12, cada hilo suma 1 o 2 números (~1 ns).
5. Combinar las `s` privadas en la `s` compartida (el `reduction`, con operaciones atómicas o un
   lock sobre una línea de caché que va saltando entre núcleos).
6. La barrera implícita al final: todos esperan al más lento.
7. Volver a dormir o a esperar activamente al siguiente `parallel for`.

Con N = 16 el paso 4 es prácticamente 0 y **todo el tiempo se va en los pasos 1, 5 y 6**.
Restando la parte útil (Ts/p), el costo fijo de la región crece con p:

| p | 1 | 2 | 4 | 8 | 12 |
|---|---|---|---|---|---|
| overhead ≈ Tp − Ts/p (N = 16) | 0.4 µs | 1.1 µs | 1.7 µs | 3.7 µs | 21.7 µs |

Medí además cuánto cuesta **una sola barrera**, comparando el código original
(`parallel for`, una barrera) con la versión del repo (`parallel` + `for nowait` + `barrier`
explícita + la barrera implícita al cerrar `parallel`, o sea dos barreras). Con N = 16, la
barrera extra suma **+0.17 µs (p = 1), +0.4 µs (p = 2), +0.65 µs (p = 4), +0.8 µs (p = 8) y
+11.5 µs (p = 12)**. Cada punto de sincronización cuesta del orden de 1 µs y crece con p: eso
es η_c medido directamente.

El salto en p = 12 pasa porque se usan los 12 hilos lógicos. Si cualquier otro proceso
(Spotify, el navegador o el propio WSL) necesita CPU, a uno de los 12 hilos lo sacan y la
barrera tiene que esperarlo.

**6. ¿A partir de qué N conviene la paralela? ¿Qué regla práctica sale?**
Medí tamaños intermedios (`extra/lab12_umbral.c`, que es el mismo programa con otros
`tamanos[]`; 3 corridas, mediana):

| N | S p=2 | S p=4 | S p=8 | S p=12 |
|---|---|---|---|---|
| 2 048 | 0.95 | 0.95 | 0.58 | 0.13 |
| **4 096** | **1.35** | **1.50** | **1.13** | 0.21 |
| 8 192 | 1.56 | 2.21 | 1.75 | 0.74 |
| 16 384 | 1.74 | 2.82 | 2.22 | **1.13** |
| 65 536 | 1.88 | 3.37 | 3.24 | 1.53 |

- Con p = 2, 4 y 8, la paralela empieza a ganar entre **N ≈ 2 000 y 4 000** (Ts ≈ 2–4 µs).
- Con p = 12 recién gana desde **N ≈ 16 000** (Ts ≈ 19 µs), y nunca por mucho.

*Predicción:* dije entre 3 000 y 8 000 → **acerté para p = 2–8**. Para p = 12 el umbral es ~4 veces
más alto de lo que esperaba.

**Regla práctica:** un `parallel for` vale la pena cuando el trabajo que se reparte es mucho
mayor que su costo fijo. Aquí el costo fijo es de 1–4 µs, así que hace falta del orden de
**≥ 10 µs de trabajo por región** (en esta suma, unos miles de números por hilo). Además, **más hilos
no es mejor**: el costo fijo crece con p, y con N = 65 536 el mejor tiempo y la mejor efectividad F
salieron con **p = 4**, no con 12.

**7. Con N grande, ¿llega S a p? ¿Qué recurso compartido limita? ¿Encaja en las cuatro fugas?**
No. Con N = 16.7 M el máximo es **S = 4.52 con p = 8** (mediana de 6 corridas: 4.0), y con p = 12
baja a 3.2.

- El arreglo pesa 16.7 M × 8 B = 134 MB, no cabe en la L3 (12 MB) y hay que leerlo de RAM cada vez.
- Con p = 8: 134 MB / 4.63 ms ≈ **29 GB/s**, el 57 % de los 51.2 GB/s teóricos de mi RAM (DDR4-3200
  en doble canal). En la práctica ese es el techo de lo que el controlador de memoria entrega a
  todos los núcleos juntos.
- La secuencial lee a 134 MB / 20.9 ms ≈ 6.4 GB/s, porque la limita la cadena de sumas
  dependientes y no la memoria. Por eso el techo de S ≈ 29 / 6.4 ≈ **4.5**: justo lo medido.

El recurso compartido es el **ancho de banda de memoria (bus y controlador de RAM)**. **No encaja
bien en ninguna de las cuatro fugas**: no hay parte secuencial, ni sincronización, ni desbalance,
ni trabajo redundante. Los núcleos se estorban porque compiten por el mismo recurso de hardware.
Como mucho se podría estirar η_c, pensando en la memoria como canal de comunicación, pero es
una pérdida distinta.

*Predicción:* para N = 16 M dije S ≈ 4–6 por el ancho de banda, y acerté. Para N = 65 536 y N = 1 M
con p = 12 esperaba S de 4–8, pero salió 1.15 y 0.57: no anticipé que con 12 hilos el overhead
y el ruido pesaran tanto aun con N grande.

---

## Parte 3 — Desbalance de carga

Datos: `desb_static.csv`, `desb_dynamic.csv`, `desb_guided.csv` (oficiales, gráficas
`desbalance_speedup.png` y `desbalance_eficiencia.png`) + 5 repeticiones de cada uno (gráfica
`extra_desbalance_variabilidad.png`, con la mediana de las 6 corridas y el rango mín–máx).

| p | S static | S dynamic | S guided | mediana 6 corridas: static / dynamic / guided |
|---|---|---|---|---|
| 2 | 1.46 | 1.80 | 2.01 | 1.38 / 1.93 / 2.02 |
| 4 | 2.51 | 3.93 | 4.06 | 2.43 / 3.77 / 4.01 |
| 8 | 4.58 | 8.00 | 5.79 | 4.35 / 7.15 / 7.44 |
| 12 | 3.74 | 7.49 | 4.46 | 3.95 / 8.03 / 8.04 |

**Cálculo a mano de S, E, C y F (dos filas):**

*static, p = 4:* Ts = 0.159815 s, Tp = 0.063611 s
- S = 0.159815 / 0.063611 = **2.512**
- E = 2.512 / 4 = **0.628**
- C = 4 × 0.063611 = **0.2544 hilo·s**
- F = S / C = 2.512 / 0.2544 = **9.87 s⁻¹**

*dynamic, p = 4:* Ts = 0.153325 s, Tp = 0.039029 s
- S = 0.153325 / 0.039029 = **3.928**
- E = 3.928 / 4 = **0.982**
- C = 4 × 0.039029 = **0.1561 hilo·s**
- F = 3.928 / 0.1561 = **25.16 s⁻¹**

Con los mismos 4 hilos, `dynamic` paga un 39 % menos de hilo-segundos y tiene **2.5 veces
más efectividad**. Coincide con lo que da `graficar.py` (`desbalance_con_S_E.csv`).

**1. Compara S(pmax) de los tres schedules. ¿Cuál gana y por cuánto?**
En la corrida oficial **gana `dynamic` con S(12) = 7.49**, contra 4.46 de `guided` y 3.74 de
`static`: **2.0× sobre static** y 1.7× sobre guided.
Pero el `guided` oficial es un caso atípico. En las otras 5 corridas, guided con p = 12 dio entre
6.7 y 10.0, y la mediana de las 6 es **8.04, igual que dynamic (8.03)**. Lo que se sostiene es:
**dynamic ≈ guided ≈ 8, ambos ≈ 2 veces static (≈ 4)**. El mejor valor medido fue dynamic con
p = 10: S = 9.72 (E = 0.97).

*Predicción:* static 4.5–5.5 (medido 3.7, mediana 4.0, un poco abajo), dynamic 7–9 (7.5, mediana 8.0 ✓),
guided 7–8.5 (mediana 8.0 ✓) y dynamic 1.6× mejor que static (salió 2.0×).

**2. Fracción del trabajo del hilo más cargado con static (p = 2 y p = 4), S predicho contra medido.**
El costo de la iteración i es c(i) = 1 + 2000·i/W, una recta que va de 1 a ~2001. El trabajo
total es el área bajo la recta: W·(1 + 2001)/2 ≈ **1000.5·W**.
Con static, el último hilo recibe el último bloque, que es el más caro. Su trabajo es un trapecio
de base W/p cuyas alturas son el costo al inicio y al final del bloque.

- **p = 2:** bloque [W/2, W), costo promedio = (1001 + 2001)/2 = 1501 → trabajo = (W/2)·1501 = 750.5·W
  → fracción = 750.5 / 1000.5 = **0.750** → S = 1/0.750 = **1.33**
- **p = 4:** bloque [3W/4, W), costo promedio = (1501 + 2001)/2 = 1751 → trabajo = (W/4)·1751 = 437.75·W
  → fracción = 437.75 / 1000.5 = **0.4375 = 7/16** → S = 1/0.4375 = **2.29**
- En general: fracción = (2p − 1)/p² y S_static = p²/(2p − 1). Lo verifiqué sumando el costo
  exacto de las 40 000 iteraciones: 0.7499 y 0.4374.

| | S predicho | S medido (vs Ts) | S medido (vs Tp con 1 hilo) | mediana 6 corridas |
|---|---|---|---|---|
| p = 2 | 1.33 | 1.46 | 1.34 | 1.38 |
| p = 4 | 2.29 | 2.51 | 2.30 | 2.43 |

El modelo del trapecio **predice casi exacto**. En la corrida oficial el Ts de static salió
alto (S(p=1) = 1.09, ruido en esa medición de Ts). Comparando contra Tp con 1 hilo da
1.34 y 2.30, prácticamente igual al modelo. Las medianas quedan un 4–6 % por encima. Una causa
probable es el turbo: cuando los primeros hilos terminan y quedan esperando, el último queda
casi solo en el chip y el procesador le sube la frecuencia, así que termina un poco antes de
lo que dice el modelo.

**3. En static, ¿qué hacen los primeros hilos mientras el último termina? ¿Cómo se ve en la eficiencia?**
Terminan su bloque barato y se quedan **parados en la barrera implícita del `parallel for`**:
primero esperan activamente, gastando CPU sin hacer nada útil, y después se duermen. Ese tiempo
ocioso se paga igual en el costo C = p·Tp.
En la gráfica de eficiencia, static cae enseguida (E = 0.73 con p = 2 y 0.63 con p = 4) y se
queda en una meseta de ~0.55–0.6 hasta p = 8. El modelo dice E = p/(2p − 1) → 0.667, 0.571, 0.533:
**tiende a 0.5, o sea que la mitad de los hilo-segundos se pierden esperando**. dynamic y
guided se mantienen en E ≈ 0.9–1.0 hasta p = 8 (medianas de 6 corridas: 0.89 y 0.93 con p = 8).
Con p = 12, static paga C = 12 × 0.0428 = 0.51 hilo·s para un trabajo de 0.16 s: **3.2 veces
más hilo-segundos que la secuencial**.

**4. Si dynamic es mejor aquí, ¿por qué no usarlo siempre?**
Porque repartir en tiempo de ejecución cuesta. Cada vez que un hilo termina un bloque de 64
iteraciones tiene que tomar el siguiente de un **contador compartido** (una operación atómica
sobre una línea de caché que salta entre núcleos), y además se pierde la localidad de los
bloques contiguos.
- Aquí no importa: cada bloque de 64 iteraciones cuesta ~64 × 1000 iteraciones internas
  (~decenas de µs), y en total son solo 625 repartos.
- En la suma de la Parte 2 cada iteración cuesta ~1 ns: un bloque de 64 son ~64 ns de trabajo,
  menos que lo que cuesta pedir el bloque cuando varios hilos compiten por el contador. El
  costo de repartir sería tan grande o más que el trabajo, el mismo problema de granularidad
  que vimos con N pequeño (fuga η_c).

Regla: `static` cuando las iteraciones cuestan parecido (cero costo de repartir) y
`dynamic`/`guided` solo cuando el costo varía **y** cada bloque tiene trabajo de sobra para
pagar el reparto. `guided` es un punto intermedio: hace pocos repartos al inicio (bloques
grandes) y bloques chicos al final para balancear.

**5. Con núcleos P y E, ¿por qué un static con iteraciones de costo idéntico también podría quedar desbalanceado?**
static da **el mismo número de iteraciones** a cada hilo y supone que todos los hilos avanzan
igual de rápido. En mi i5-12450H eso no se cumple:
- Un **núcleo E** (Gracemont, hasta 3.3 GHz, menor IPC) avanza más lento que un **núcleo P**
  (Golden Cove, hasta 4.4 GHz).
- Dos hilos en el **mismo núcleo P por Hyper-Threading** comparten las unidades de ejecución, así
  que cada uno avanza más lento que un hilo solo en su núcleo.

El hilo que cae en el núcleo más lento se vuelve el último en llegar a la barrera y los demás
lo esperan: es un desbalance (η_b) que no viene del algoritmo sino del hardware. En WSL2 es
peor, porque los 12 vCPU se ven idénticos (`lscpu`) y ni OpenMP ni Linux pueden saber cuál cae
en un núcleo E: lo decide el planificador de Windows.
Se nota en mis datos: hasta p ≈ 8 las curvas son estables, y de p = 9 en adelante (cuando ya
se usan sí o sí núcleos E e hilos HT compartiendo núcleo) S se vuelve muy variable. Por ejemplo,
dynamic con p = 11 dio entre 4.4 y 10.7. En la suma (static, costo idéntico), N = 1 M con p = 8
dio entre 1.5 y 5.2. dynamic compensa esto mejor porque el hilo lento simplemente toma menos
bloques.

---

## Aporte a la síntesis (Partes 2 y 3)

| Parte | Fuga principal | Número medido que lo demuestra |
|---|---|---|
| 2a | η_c (overhead fijo de la región paralela) | suma N = 16: OpenMP con 1 hilo 389 ns contra 5 ns secuencial (78×); en amdahl es invisible (0 % ± 3 %) |
| 2b, N chico | **η_c** (despertar hilos, reduction, barrera) | N = 16, p = 12: Tp = 21.7 µs contra Ts = 5 ns → S = 0.00023; overhead de 0.4 µs (p = 1) a 21.7 µs (p = 12) |
| 2b, N grande | **ninguna de las 4**: ancho de banda de memoria | N = 16.7 M: S máx = 4.5 con p = 8, techo de ~29 GB/s de RAM |
| 3 | **η_b** (desbalance) | static p = 4: E = 0.63 contra 0.98 de dynamic; fracción del último hilo 7/16 → S = 2.29 predicho contra 2.30 medido (vs T1 paralelo) |

**Lo que no encaja en las cuatro fugas** (de mis partes):
- **Ancho de banda de memoria compartido** (2.7): limita S ≈ 4.5 con N grande.
- **Núcleos heterogéneos P/E e Hyper-Threading** (3.5): parece η_b, pero no viene del
  reparto del trabajo sino de que los "hilos" no son iguales.
- **Turbo boost**: un hilo solo corre a más frecuencia que 8 hilos juntos, y el último hilo de
  static se acelera cuando los demás terminan. Por eso static quedó un poco por encima del modelo.
- **Ruido del sistema operativo y la virtualización** con p = 12: otros procesos le quitan
  CPU a un hilo y la barrera espera (S de dynamic con p = 12 entre 4.9 y 11.2 en 6 corridas).
- **Caché** (reto): puede hacer que la paralela sea *más* eficiente que la secuencial (E > 1),
  una "fuga" en sentido contrario.

---

## Reto opcional (+10): speedup superlineal (S > p)

Archivo: `reto/lab12_speedup.c`. Solo cambia `exp_suma()`, y cada cambio tiene un comentario
"RETO" que explica qué se cambió y por qué. Gráfica: `extra_reto_superlineal.png`. Captura de las
5 corridas: `evidencia/08_reto_5corridas.png`. CSV: `reto/reto_suma_r1..r5.csv`.

**Por qué el programa original no puede dar S > p:** la suma original hace `s += a[i]` con un solo
acumulador. Cada suma espera a la anterior, así que un núcleo procesa ~1 número por ns
(≈ 8 GB/s) y no lo limita la memoria: le da igual si los datos vienen de L2, L3 o RAM.

**Los S > p falsos que sí aparecieron con el código original.** En desbalance hubo corridas
con S > p. Por ejemplo, guided r3 dio S = 10.06 con p = 10 y S = 7.34 con p = 7, y la dynamic
oficial dio S = 7.49 con p = 7. Son falsos:
- Cada corrida mide su Ts una sola vez al inicio, y ese Ts varió hasta un 10 % entre corridas
  (de 0.140 a 0.155 s).
- Las corridas con S > p son justo las que tuvieron un Ts alto (guided r3: 0.155 s), y como todos
  los S de esa corrida dividen entre ese Ts, quedan todos inflados.
- Al repetir, la mediana de las 6 corridas queda **por debajo de p** en todos los casos.
- Los casos de S apenas encima de p (2.01–2.05 con p = 2) están dentro del ±5 % de ruido.

Justo eso advierte la pista 2: un S > p que desaparece al repetir no cuenta.

**Qué cambié:**
1. `sumar_rapido()`: 4 acumuladores vectoriales AVX2 (16 sumas independientes en vuelo). Ahora
   un núcleo consume datos tan rápido que **sí importa de qué caché vienen**. Se usa **la misma
   función en la secuencial y en la paralela**: si solo se optimizara la paralela, el Ts sería
   tramposo (2a.2) y el S > p sería falso.
2. `tamanos[]` de 1 MB a 32 MB, para pasar por los límites de L2 (1.25 MB por núcleo P) y L3 (12 MB).
3. Bloques contiguos alineados a 16 doubles (equivalente a `schedule(static)`) y `aligned_alloc`
   para las cargas vectoriales.

**Resultado (5 corridas, N = 262 144 doubles = 2 MB):**

| corrida | S (p = 2) | S (p = 4) |
|---|---|---|
| 1 | 2.34 | 4.44 |
| 2 | 3.61 | 5.80 |
| 3 | 2.57 | 6.74 |
| 4 | 2.28 | 6.22 |
| 5 | 2.80 | 5.03 |
| **mediana** | **2.57 > 2** | **5.80 > 4** |

**S > p en las 5 corridas** (E = 1.29 con p = 2 y E = 1.45 con p = 4).

**Revisé que no fuera el mismo artefacto de arriba:**
- Aquí el Ts es estable: 62.9–65.2 µs en las 5 corridas (±2 %).
- Si en vez de Ts uso la versión paralela con 1 hilo (T1 par / Tp), igual sale S > p:
  4.62, 5.65, 6.84, 6.18 y 5.31 con p = 4.

El efecto se repite y no depende de una medición de Ts mala.

**Por qué pasa:**
- Con 1 hilo, el arreglo de 2 MB **no cabe en la L2 de un núcleo (1.25 MB)**. En cada una de las
  190 repeticiones se lee desde L3: 2 MB / 64.4 µs ≈ **33 GB/s**.
- El mismo código con 1 MB, que sí cabe en L2, va a 1 MB / 17.6 µs ≈ **60 GB/s**: la L2 es ~1.8×
  más rápida que la L3 para este núcleo.
- Con p = 4, cada hilo suma 512 KB, que **se quedan en la L2 de su núcleo** entre repeticiones:
  512 KB / 10.9 µs ≈ **48 GB/s por hilo**.
- Entonces S ≈ p × (velocidad desde L2 / velocidad desde L3) − overhead ≈ 4 × 1.5–1.8 menos el
  overhead de la región ≈ **5.8**. Al repartir no solo se divide el trabajo: **también cambia
  dónde viven los datos**. En total hay más caché rápida (una L2 por núcleo) que la que tiene
  un solo hilo.

Cuando el arreglo crece (8–32 MB), ni los pedazos caben en L2 o el total no cabe en L3, y el
efecto desaparece (E < 1). Con p = 8 tampoco aparece, porque los hilos HT comparten la L2 de su
núcleo y los núcleos E comparten una L2 entre 4.

---

## Verificación con el código del repo

En las Partes 1 y 4 se usó una versión modificada de `lab12_speedup.c` (la que está en la raíz
del repo). Para descartar que la diferencia de código afecte la comparación entre partes, corrí
una vez `suma` y los 3 schedules de `desbalance` con **esa versión** en mi equipo
(`scripts/09_verificar_codigo_repo.sh`, resultados en `verificacion_codigo_repo/`) y comparé
contra el rango de mis 6 corridas con el código original:

| Experimento | Puntos dentro del rango (±5 %) | Conclusión |
|---|---|---|
| desbalance static | 12 / 12 | igual |
| desbalance dynamic | 12 / 12 | igual |
| desbalance guided | 12 / 12 | igual |
| suma, N ≥ 65 536 | 13 / 15 (los 2 de afuera son con p = 12, que ya era ruidoso) | igual |
| suma, N = 16 y 1 024 | 3 / 10 (los 3 de adentro son con p ≥ 8, donde el rango era muy amplio) | **la versión del repo es más lenta** |

La diferencia con N chico tiene una explicación concreta. La versión del repo cambia
`#pragma omp parallel for` por `#pragma omp parallel { #pragma omp for nowait ... #pragma omp barrier }`.
La región `parallel` igual termina con su barrera implícita, así que **quedan dos barreras por
suma en vez de una**. Con N = 16 y 1 024, donde casi todo el tiempo ya es overhead, esa barrera
extra suma entre 0.1 y 1 µs con p ≤ 8 (~11–12 µs con p = 12). Con N grande ese costo se pierde
frente al trabajo útil.

Conclusión: los resultados de las Partes 2 y 3 valen igual con cualquiera de las dos versiones,
salvo la suma con N ≤ 1 024, donde la versión del repo agrega el costo de una barrera más
(ver 2b.5).

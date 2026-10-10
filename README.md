# PCAM y OpenMP: simulación N-Body

Nina Nájera Marakovits, 231088.

Se simula gravedad en dos dimensiones con semilla 42, integración Euler semiimplícita, paso temporal 0.001, constante gravitacional 0.001 y suavizado cuadrático 0.0001. Las masas se generan entre 1 y 2 y las posiciones entre -1 y 1. La versión secuencial y la directa calculan N por N interacciones. La optimizada calcula cada pareja una sola vez.

## Compilación y ejecución

Se requiere C++17, GCC con OpenMP y Python 3 para automatizar experimentos.

```sh
g++ -O2 -std=c++17 -fopenmp src/nbody_seq.cpp -o build/nbody_seq
g++ -O2 -std=c++17 -fopenmp src/nbody_parallel.cpp -o build/nbody_parallel
g++ -O2 -std=c++17 -fopenmp src/nbody_optimized.cpp -o build/nbody_optimized
./build/nbody_parallel --n 5000 --steps 10 --threads 8 --schedule dynamic --chunk 64
```

Crear primero la carpeta build. En Windows se puede añadir .exe a los ejecutables. Chunk 0 solicita el valor predeterminado del runtime. Para static significa bloques contiguos sin tamaño explícito; para dynamic y guided el mínimo predeterminado es 1.

```sh
python scripts/benchmark.py
python scripts/check.py
python scripts/render_evidence.py
```

El benchmark compila, ejecuta 63 mediciones y escribe results.csv con cada repetición y summary.csv con promedios, speedup y eficiencia. Mantiene N=5000, pasos=10 y tres repeticiones para cada configuración. Incluye las nueve configuraciones obligatorias en ambas versiones paralelas y añade chunk 32 para comparar tres tamaños explícitos. Las ejecuciones se realizan una después de otra.

## Diseño PCAM

- Partición: en la directa cada cuerpo es una tarea que lee las posiciones de todos los demás. En la optimizada cada fila del triángulo superior agrupa parejas; su trabajo disminuye al aumentar el índice.
- Comunicación: se comparten posiciones y masas en lectura. Cada hilo escribe sus propias fuerzas en la directa. La optimizada usa un vector privado de fuerzas por hilo y combina los vectores en orden de índice de hilo.
- Aglomeración: se agrupan cuerpos con chunks 8, 32 y 64 para medir el costo de asignación frente al balance de carga.
- Mapeo: schedule runtime permite comparar static, dynamic y guided con los mismos datos y el mismo cálculo.

Todos los ciclos de distribución OpenMP llevan nowait. Las barreras explícitas separan lectura de posiciones, combinación de fuerzas y actualización. La región paralela persiste durante todos los pasos. OpenMP exige una sincronización al finalizar la región paralela; no existe nowait para eliminarla. La última fase ya termina con una barrera explícita y no depende de esa sincronización obligatoria de cierre.

La versión optimizada evita carreras con acumuladores privados y utiliza memoria adicional proporcional a N por hilos. No usa atomic ni critical. Una barrera impide combinar fuerzas antes de terminar todas las parejas. Otra impide modificar posiciones mientras todavía se leen. La combinación se hace por cuerpo, con un solo escritor para cada resultado.

## Medición y corrección

Se usa omp_get_wtime. El tiempo incluye las reservas de fuerzas y la región paralela; excluye generar entradas, imprimir y ejecutar la referencia secuencial de validación. El checksum pondera posiciones y velocidades por el índice del cuerpo. La diferencia máxima compara las cuatro componentes del estado con la referencia, fuera del intervalo medido. Una diferencia mayor que 1e-9 devuelve código 2. Entradas inválidas devuelven código 1.

Los resultados guardan hilos solicitados y reales, procesadores disponibles y máximo de hilos informado por OpenMP. Speedup usa siempre el promedio secuencial; eficiencia divide el speedup entre los hilos reales. Las pequeñas diferencias de la optimizada provienen del orden de suma de punto flotante. El scheduling dinámico puede cambiar ese orden entre ejecuciones.

## Evidencia

evidence contiene los registros originales de compilación y ejecución en archivos txt y su representación en PNG. Las imágenes se generan a partir de las salidas reales sin editar los valores. Son imágenes de registros, no capturas del escritorio: el entorno de ejecución no dispone de acceso a la pantalla. La compilación se registra con sus comandos y códigos de salida. sequential, parallel y optimized corresponden a la primera repetición de sus configuraciones en results.csv. hardware conserva la salida optimizada con la información OpenMP.

El informe en LaTeX se encuentra en informe.tex en la raíz y está excluido de Git. La portada acepta logo.png si está disponible. El PDF compilado se entrega como report.pdf.

Repositorio: https://github.com/Ninaswiftie09/Paralela_Tareas/tree/Laboratorio_PCAM_OpenMP_NBody

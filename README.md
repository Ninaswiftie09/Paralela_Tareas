# Lab 12: speedup y eficiencia

El programa base contiene los cuatro experimentos de la guía en C con OpenMP. Se prepararon las partes 1 y 4 para Nina: Amdahl con problema fijo y Gustafson con problema creciente. Las partes 2 y 3 corresponden a la otra mitad: granularidad de sumas y desbalance de carga. El reporte y la síntesis final se integran después con los datos de ambos integrantes.

## Compilar

En Linux o WSL:

```sh
make
./lab12
```

En Windows con GCC y OpenMP:

```powershell
mingw32-make
./lab12.exe
```

La ejecución sin argumentos muestra el uso y devuelve código 1. En macOS se puede usar `make CC=gcc-14` o `make CC=clang` con libomp instalado. Se requiere Python 3 y matplotlib para las gráficas.

## Ejecutar las partes 1 y 4

```sh
python scripts/run_my_experiments.py
python scripts/check_results.py
python scripts/analyze_models.py
```

En Linux se puede sustituir python por python3. El primer comando compila con O2, ejecuta las cinco fracciones de Amdahl con W=400000 y Gustafson con 100000 unidades paralelas por hilo y 20000 unidades secuenciales. Se prueban de 1 a 8 hilos. Cada tiempo se mide cinco veces con omp_get_wtime y se toma la mediana. La fracción secuencial dentro del tiempo paralelo corresponde a la misma repetición que produjo la mediana total.

La salida estándar conserva las siete columnas originales. Los registros log guardan las cinco muestras y sus resultados numéricos sin mezclarlas con el CSV. Se comprueba que el resultado paralelo coincide con la referencia sin OpenMP dentro de una tolerancia relativa de 1e-10 y que el número real de hilos coincide con el solicitado en Amdahl y Gustafson. Las comprobaciones numéricas y la escritura de muestras quedan fuera del intervalo medido. La comprobación del número de hilos forma parte de la llamada paralela medida.

La referencia secuencial no contiene pragmas OpenMP. La versión paralela usa reduction, ciclos con nowait y barreras explícitas antes del cierre de cada región. OpenMP exige sincronizar al cerrar una región paralela; esa sincronización de cierre no se puede quitar. El experimento de suma conserva la creación y cierre de la región en cada suma para poder medir ese costo.

Los archivos generados quedan en results. Los seis CSV originales son amdahl_fp100.csv, amdahl_fp95.csv, amdahl_fp90.csv, amdahl_fp75.csv, amdahl_fp50.csv y gustafson.csv. Los CSV con S, E, C y F usan el tiempo secuencial puro como referencia. Los archivos amdahl_summary.csv, amdahl_models.csv y gustafson_models.csv añaden las tablas y comparaciones de modelos. samples.csv conserva las muestras originales que se comprobaron contra cada mediana.

Las gráficas disponibles son amdahl_speedup.png, amdahl_eficiencia.png, amdahl_modelo.png, gustafson_speedup.png, gustafson_eficiencia.png y gustafson_modelo.png. Los modelos son referencias ideales y no ajustes a los datos. El modelo escalado usa la fracción secuencial medida dentro de Tp, por lo que puede diferir del speedup medido cuando la velocidad efectiva de los hilos cambia.

## Comandos de la otra mitad

Antes de ejecutar cada experimento se deben registrar sus predicciones. En Linux o WSL:

```sh
./lab12 suma > suma.csv
./lab12 desbalance static > desb_static.csv
./lab12 desbalance dynamic > desb_dynamic.csv
./lab12 desbalance guided > desb_guided.csv
python3 graficar.py suma.csv 'desb_*.csv'
```

En Windows, cambiar el ejecutable a lab12.exe y usar python. Conviene usar `cmd /c` para redirigir si la versión de PowerShell escribe archivos con una codificación distinta de UTF-8. El graficador reconoce comodines y también CSV UTF-8 con BOM.

## Validar y medir

```sh
python scripts/check_program.py
```

La prueba verifica entradas inválidas, casos pequeños, fracciones extremas y los tres schedules de desbalance. No sustituye las corridas completas de las partes 2 y 3.

El equipo usado tiene un Intel Core i7-1165G7, 4 núcleos físicos, 8 procesadores lógicos y Hyper-Threading. No tiene núcleos de rendimiento y eficiencia separados. Los datos se guardan en hardware.json y environment.json. Se comprobó que estaba conectado a corriente antes de iniciar las corridas. La afinidad, la frecuencia, la temperatura y las aplicaciones de fondo no se controlaron. El entorno fue Windows nativo con TDM GCC 10.3.0. La guía sugiere WSL en Windows; solo estaba instalada la distribución de Docker y no se utilizó como entorno de medición.

Para repetir con mayor control, conectar la laptop a corriente, cerrar las aplicaciones y evitar usarla mientras corre. No ejecutar las pruebas al mismo tiempo que los experimentos. El tiempo medido en esta instalación de OpenMP tiene resolución aproximada de milisegundos; los problemas completos duran lo suficiente para obtener tiempos positivos, pero no conviene interpretar diferencias de una milésima como una mejora segura.

Falta ejecutar las partes 2 y 3, integrar los datos y gráficas de ambos integrantes, elaborar el reporte con respuestas numeradas y dos cálculos manuales, y preparar el ZIP final. El reto de speedup superlineal es opcional y no se ejecutó.

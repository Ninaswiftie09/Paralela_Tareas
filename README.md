# Laboratorio 12: speedup y eficiencia

## Integrantes

Nina Nájera Marakovits y Luis Palacios.

## Organización

La implementación compartida está en lab12_speedup.c. Las variantes de umbral y reto incluyen esa implementación y solo seleccionan los tamaños y la suma AVX2. Los ciclos distribuidos llevan nowait y barreras explícitas. OpenMP conserva la sincronización obligatoria al cerrar cada región paralela. No se utiliza una barrera implícita de ciclo para resolver las dependencias.

Los resultados originales se conservan en results y parte2_3. Nina midió Amdahl y Gustafson con un i7-1165G7 de 4 núcleos y 8 hilos, en Windows y GCC 10.3. Luis midió suma y desbalance con un i5-12450H de 4 núcleos P y 4 E, 12 hilos lógicos, en WSL2 y GCC 13.3. No se comparan tiempos absolutos entre equipos.

Las mediciones de Luis usaron el programa inicial. Los archivos de provenance conservan esas versiones como texto histórico sin comentarios y registran sus hashes. Esos archivos no son los ejecutables actuales. Las nuevas corridas utilizan el código unificado y quedan en build/reproduced, sin reemplazar los CSV originales. La sincronización cambió respecto al programa inicial y puede modificar los tiempos, especialmente para sumas pequeñas.

## Compilar

Linux y WSL usan make. Windows con GCC usa mingw32-make. En macOS se puede usar make CC=gcc-14 o clang con libomp. Se requiere Python y matplotlib.

```sh
python scripts/build_variants.py
python scripts/check_program.py
python scripts/check_results.py
python scripts/validate_project.py
```

El primer comando compila el programa principal y las dos variantes en build. El reto comprueba AVX2 antes de ejecutar y usa reserva alineada compatible con Windows y Linux. La función de suma del reto es la misma en la referencia y en los bloques paralelos.

## Repetir experimentos

```sh
python scripts/run_experiments.py --parts nina --pmax 8
python scripts/run_experiments.py --parts luis --pmax 12
python scripts/run_experiments.py --parts all --pmax 8 --output build/another_run
```

Se usa la mediana de cinco repeticiones. La referencia secuencial no contiene OpenMP. Para tamaños pequeños se repite la suma muchas veces y se divide entre ese número de repeticiones. Los logs guardan las muestras de Amdahl y Gustafson y su comparación numérica. Conectar la laptop a corriente, cerrar aplicaciones y evitar usarla durante las corridas. Los datos históricos no tuvieron un aislamiento completo del sistema.

El script graficar.py calcula S=Ts/Tp, E=S/p, C=p*Tp y F=S/C. analyze_models.py genera las comparaciones con los modelos a partir de los datos originales. Las diez salidas originales, las métricas y las siete gráficas principales están completas en results. Las gráficas de modelos y los experimentos adicionales se conservan junto con ellas.

## Empaquetar resultados

```sh
python scripts/armar_resultados_zip.py
```

El ZIP contiene los CSV y PNG de ambos equipos, las fuentes compartidas y la información de procedencia. Se pueden agregar archivos adicionales con la opción --include, repetida por cada archivo. El ZIP está excluido de Git.

Los resultados guardados del reto tienen S mayor que p en cinco corridas para 2 y 4 hilos con un arreglo de 2 MiB. Ese efecto no se garantiza en otro equipo. Las diferencias de caché son una explicación posible; no se registraron afinidad ni contadores de hardware para demostrar una causa exclusiva.

## Entrega

```sh
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia_windows.ps1
python scripts/armar_entrega.py
```

El primer comando se ejecuta en el equipo de Nina. Guarda en evidencia/nina las capturas de los datos del equipo, la compilación, Amdahl y Gustafson, sin modificar results. El segundo arma la carpeta entrega con reporte_lab12.pdf, evidencia_lab12.pdf, resultados_lab12.zip y el lab12_speedup.c del reto, y avisa si falta algo. El archivo del reto que se entrega es docs/reto/lab12_speedup.c, la versión con la que se midió, con los comentarios que pide la guía.

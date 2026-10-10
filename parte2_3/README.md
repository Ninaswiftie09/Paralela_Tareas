# Datos históricos de suma, desbalance y reto

Se midieron con Intel Core i5-12450H, 4 núcleos P y 4 E, 12 hilos lógicos, WSL2 Ubuntu 24.04 y GCC 13.3.

Los CSV oficiales están en results. Las repeticiones adicionales, las capturas y los tamaños intermedios permanecen en esta carpeta. Los datos originales corresponden al programa inicial. provenance conserva las fuentes históricas como texto y sus hashes.

Los archivos C de extra y reto ahora seleccionan variantes de la implementación compartida de la raíz. Los scripts de corridas escriben en build/reproduced y no reemplazan la evidencia original. Usar el script run_experiments.py de la raíz para repetir suma y desbalance con el código actual.

La mediana de la diferencia porcentual entre OpenMP con un hilo y la referencia fue 1.23 por ciento en cinco corridas adicionales de Amdahl. La variación del desbalance también superó 5 por ciento con hasta 8 hilos. El speedup se calcula siempre con la referencia secuencial pura de cada corrida. Los casos superlineales del reto se repitieron cinco veces, pero no se midieron afinidad ni contadores de caché.

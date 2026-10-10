# Lab 12 — Partes 2 y 3 + reto (Luis)

Medido en: Intel i5-12450H (4P+4E, 12 hilos), WSL2 Ubuntu 24.04, gcc 13.3 `-O2 -fopenmp`, pmax = 12,
con el `lab12_speedup.c` **original del starter** (ver la sección de verificación en las respuestas).

## Entregables oficiales (en `../results/`)

| Archivo | Qué es |
|---|---|
| `suma.csv`, `desb_static.csv`, `desb_dynamic.csv`, `desb_guided.csv` | 4 de los 10 CSV originales |
| `suma_con_S_E.csv`, `desbalance_con_S_E.csv` | Generados por `graficar.py` |
| `suma_speedup.png`, `desbalance_speedup.png`, `desbalance_eficiencia.png` | 3 de las 7 gráficas |

## En esta carpeta

| Archivo / carpeta | Qué es |
|---|---|
| `predicciones_parte2_3.md` | Predicciones, escritas **antes** de correr nada |
| `respuestas_parte2_3.md` | Datos del equipo, cálculos a mano, respuestas 2a/2b/3, aporte a la síntesis, reto y verificación |
| `evidencia_parte2_3.pdf` | Capturas (lscpu, make, cada corrida) + gráficas, listo para unir al PDF de evidencia |
| `evidencia/` | Las mismas capturas en PNG |
| `amdahl_fp100_luis.csv` | amdahl fp = 1.00 en mi equipo, solo para la 2a (el oficial de la Parte 1 está en `results/`) |
| `repeticiones/` | 5 corridas extra de suma y de cada schedule + 5 de amdahl p = 1 (para medir el ruido) |
| `extra/` | `lab12_umbral.c` (mismo programa con N intermedios) + CSV, para la pregunta 2.6 |
| `reto/` | **Entregable del reto:** `lab12_speedup.c` modificado (S > p) + 5 corridas `reto_suma_r*.csv` |
| `verificacion_codigo_repo/` | suma y desbalance corridos con el `lab12_speedup.c` del repo, para comparar con el original |
| `extra_*.png` | Gráficas extra: variabilidad del desbalance, umbral de la suma, reto |
| `scripts/` | Scripts para reproducir todo (corridas con captura, gráficas extra, PDF de evidencia) |

## Reproducir (en WSL, desde la raíz del repo)

    make
    bash parte2_3/scripts/04_suma.sh                       # -> results/suma.csv
    for s in static dynamic guided; do bash parte2_3/scripts/05_desb_$s.sh; done
    cd results && python3 ../graficar.py suma.csv && python3 ../graficar.py 'desb_*.csv' && cd ..
    cd parte2_3 && python3 scripts/graficas_extra.py && python3 scripts/armar_evidencia.py

Nota: el `lab12_speedup.c` de la raíz es la versión modificada del repo. Para repetir las
mediciones exactamente como se hicieron, usen el original del starter.

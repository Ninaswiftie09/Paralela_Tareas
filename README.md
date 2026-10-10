# Lab 12: speedup y eficiencia

## Integrantes:
    - Nina Nájera Marakovits - 231088
    - Luis Palacios

## Reparto

| Parte | Quién | Equipo | Dónde |
|---|---|---|---|
| 1 — Amdahl | Nina | i7-1165G7 (4 núcleos / 8 hilos, sin P/E), Windows nativo, TDM-GCC 10.3, pmax = 8 | `results/amdahl_*`, `scripts/` |
| 2 — Ts honesto y granularidad | Luis | i5-12450H (4P + 4E / 12 hilos), WSL2 Ubuntu, gcc 13.3, pmax = 12 | `results/suma*`, `parte2_3/` |
| 3 — Desbalance | Luis | i5-12450H | `results/desb*`, `parte2_3/` |
| 4 — Gustafson | Nina | i7-1165G7 | `results/gustafson*`, `scripts/` |
| Reto (S > p) | Luis | i5-12450H | `parte2_3/reto/` |

## Estructura

    lab12_speedup.c, Makefile, graficar.py   código (versión modificada en las Partes 1 y 4)
    scripts/                                  corridas y validación de las Partes 1 y 4 + armar_resultados_zip.py
    results/                                  los 10 CSV oficiales, los *_con_S_E.csv y las 7 gráficas
    parte2_3/                                 predicciones, respuestas, evidencia, extras y reto de las Partes 2 y 3

## Estado de los entregables

**resultados_lab12.zip**: listo para generar con `python scripts/armar_resultados_zip.py`
(los 10 CSV + 4 `*_con_S_E.csv` desde `results/`).

**7 gráficas de graficar.py**: completas en `results/`
(`amdahl_speedup`, `amdahl_eficiencia`, `suma_speedup`, `desbalance_speedup`, `desbalance_eficiencia`,
`gustafson_speedup`, `gustafson_eficiencia`).

**lab12_speedup.c del reto**: listo en `parte2_3/reto/lab12_speedup.c` (comentado) + 5 corridas.

**evidencia_lab12.pdf**
- [x] Partes 2 y 3: `parte2_3/evidencia_parte2_3.pdf` (lscpu, make, suma, los 3 desbalance, gráficas, reto)
- [ ] Partes 1 y 4: capturas de los datos del equipo de Nina, de su compilación y de las corridas de `amdahl` y `gustafson`
- [ ] Unir todo en un solo PDF

**reporte_lab12.pdf**
- [x] Partes 2 y 3: `parte2_3/respuestas_parte2_3.md` (equipo, predicciones contra lo medido, cálculos a mano, respuestas 2a/2b/3, aporte a la síntesis, reto)
- [ ] Partes 1 y 4: predicciones, tabla de la Parte 1, cálculo a mano de S/E/C/F, respuestas 1.1–1.8 y 4.1–4.5, los dos modelos
- [ ] Síntesis conjunta (fuga por parte con el número medido + lo que no encaja en las cuatro)
- [ ] Datos de los dos equipos en el reporte

## Ojo al juntar el informe

- **Son dos equipos distintos.** Cada parte se interpreta con el equipo en que se midió (ver tabla
  de arriba). Ejemplo: la pregunta 3.5 (núcleos P/E) aplica al i5-12450H; el i7-1165G7 no tiene
  núcleos E.
- **Dos versiones del código.** Las Partes 2 y 3 se midieron con el `lab12_speedup.c` original del
  starter; las Partes 1 y 4 con la versión modificada de la raíz. Se verificó que dan los mismos
  resultados en desbalance y en la suma con N grande. En la suma con N ≤ 1024 la versión
  modificada es algo más lenta por una barrera extra (sección "Verificación" de
  `parte2_3/respuestas_parte2_3.md`).
- **2a usa `amdahl_fp100.csv`.** Las respuestas usan el de Luis (`parte2_3/amdahl_fp100_luis.csv`)
  para que sea el mismo equipo que la suma, y comparan con el de Nina (`results/amdahl_fp100.csv`).
  En los dos equipos sale ~0 % de diferencia.
- **Resolución del reloj.** En Windows nativo los tiempos de las Partes 1 y 4 son múltiplos de 1 ms.
- **Predicciones.** Cada uno escribió las suyas por separado antes de medir. Las de Luis están en
  `parte2_3/predicciones_parte2_3.md`.

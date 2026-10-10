# Pregunta 2.6: ubicar el N a partir del cual la suma paralela le gana a la secuencial.
cd "$(dirname "$0")/../extra"
gcc -O2 -Wall -fopenmp -o lab12_umbral lab12_umbral.c
for i in 1 2 3; do ./lab12_umbral suma > umbral_r$i.csv 2>/dev/null; echo "umbral r$i $(date +%T)"; done

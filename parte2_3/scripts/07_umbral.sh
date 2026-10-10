mkdir -p "$(dirname "$0")/../../build/reproduced"
cd "$(dirname "$0")/../extra"
gcc -O2 -Wall -fopenmp -o lab12_umbral lab12_umbral.c -lm
for i in 1 2 3; do ./lab12_umbral suma > ../../build/reproduced/umbral_r$i.csv 2>/dev/null; echo "umbral r$i $(date +%T)"; done

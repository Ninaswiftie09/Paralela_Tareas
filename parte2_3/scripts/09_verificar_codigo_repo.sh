set -e
cd "$(dirname "$0")/../.."
mkdir -p build/reproduced/verification
cd build/reproduced/verification
cp ../../../lab12_speedup.c lab12_speedup_repo.c
gcc -O2 -std=c11 -Wall -Wextra -Werror -fopenmp lab12_speedup_repo.c -o lab12_repo -lm
export OMP_DYNAMIC=FALSE
./lab12_repo suma > suma_repo.csv 2>/dev/null
for s in static dynamic guided; do ./lab12_repo desbalance $s > desb_${s}_repo.csv 2>/dev/null; done
echo listo

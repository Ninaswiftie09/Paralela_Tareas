. "$(dirname "$0")/_comun.sh"
cd parte2_3/reto
cmd 'gcc -O2 -Wall -fopenmp -o lab12_reto lab12_speedup.c'
for i in 1 2 3 4 5; do
  ./lab12_reto suma > reto_suma_r$i.csv 2>/dev/null
  echo "corrida $i ($(date +%T)):  N=262144 ->  $(grep '^suma,262144,[24],' reto_suma_r$i.csv | awk -F, '{printf "p=%s S=%.2f   ", $3, $5/$6}')"
done

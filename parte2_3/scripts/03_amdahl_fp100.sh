. "$(dirname "$0")/_comun.sh"
mkdir -p build/reproduced
cmd 'date'
cmd './lab12 amdahl 400000 1.00 | tee parte2_3/amdahl_fp100_luis.csv'
cmd 'date'

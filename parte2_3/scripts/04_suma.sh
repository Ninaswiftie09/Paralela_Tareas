. "$(dirname "$0")/_comun.sh"
mkdir -p build/reproduced
cmd 'date'
cmd './lab12 suma | tee build/reproduced/suma.csv'
cmd 'date'

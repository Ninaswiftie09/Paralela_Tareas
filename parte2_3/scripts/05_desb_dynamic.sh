. "$(dirname "$0")/_comun.sh"
mkdir -p build/reproduced
cmd 'date'
cmd './lab12 desbalance dynamic | tee build/reproduced/desb_dynamic.csv'
cmd 'date'

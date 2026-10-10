. "$(dirname "$0")/_comun.sh"
mkdir -p build/reproduced
cmd 'date'
cmd './lab12 desbalance static | tee build/reproduced/desb_static.csv'
cmd 'date'

. "$(dirname "$0")/_comun.sh"
mkdir -p build/reproduced
cmd 'date'
cmd './lab12 desbalance guided | tee build/reproduced/desb_guided.csv'
cmd 'date'

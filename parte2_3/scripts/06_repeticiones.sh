cd "$(dirname "$0")/../.."
mkdir -p build/reproduced/repeticiones
for i in 1 2 3 4 5; do
  for s in static dynamic guided; do ./lab12 desbalance $s > build/reproduced/repeticiones/desb_${s}_r$i.csv 2>/dev/null; done
  ./lab12 suma > build/reproduced/repeticiones/suma_r$i.csv 2>/dev/null
  echo "ronda $i lista $(date +%T)"
done

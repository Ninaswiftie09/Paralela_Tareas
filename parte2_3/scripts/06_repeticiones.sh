# 5 corridas extra de cada experimento para ver qué tanto varían los resultados.
cd "$(dirname "$0")/../.."
mkdir -p parte2_3/repeticiones
for i in 1 2 3 4 5; do
  for s in static dynamic guided; do ./lab12 desbalance $s > parte2_3/repeticiones/desb_${s}_r$i.csv 2>/dev/null; done
  ./lab12 suma > parte2_3/repeticiones/suma_r$i.csv 2>/dev/null
  echo "ronda $i lista $(date +%T)"
done

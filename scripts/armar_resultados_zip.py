"""Arma resultados_lab12.zip con lo que pide la entrega:
los 10 CSV originales (5 amdahl, 1 suma, 3 desbalance, 1 gustafson) y los *_con_S_E.csv.
Uso (desde la raíz del repo):  python scripts/armar_resultados_zip.py
"""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
originales = [f'amdahl_fp{fp}.csv' for fp in (100, 95, 90, 75, 50)] + \
             ['suma.csv', 'desb_static.csv', 'desb_dynamic.csv', 'desb_guided.csv', 'gustafson.csv']
con_s_e = sorted(p.name for p in RESULTS.glob('*_con_S_E.csv'))
faltan = [n for n in originales if not (RESULTS / n).is_file()]
if faltan or len(con_s_e) != 4:
    raise SystemExit(f'Faltan archivos en results/: {faltan or ""} con_S_E encontrados: {con_s_e}')
destino = ROOT / 'resultados_lab12.zip'
with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
    for nombre in originales + con_s_e:
        z.write(RESULTS / nombre, nombre)
print(f'{destino.name}: {len(originales)} CSV originales + {len(con_s_e)} *_con_S_E.csv')

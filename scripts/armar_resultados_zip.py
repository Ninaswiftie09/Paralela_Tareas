import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--include', type=Path, action='append', default=[])
args = parser.parse_args()
RESULTS = ROOT / 'results'
originales = [f'amdahl_fp{fp}.csv' for fp in (100, 95, 90, 75, 50)] + \
             ['suma.csv', 'desb_static.csv', 'desb_dynamic.csv', 'desb_guided.csv', 'gustafson.csv']
con_s_e = sorted(p.name for p in RESULTS.glob('*_con_S_E.csv'))
faltan = [n for n in originales if not (RESULTS / n).is_file()]
if faltan or len(con_s_e) != 4:
    raise SystemExit(f'Faltan archivos en results/: {faltan or ""} con_S_E encontrados: {con_s_e}')
destino = ROOT / 'resultados_lab12.zip'
files = []
for directory in ['results', 'parte2_3', 'provenance']:
    files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and p.suffix in ['.csv', '.png', '.json', '.txt', '.c'])
files += [ROOT / 'lab12_speedup.c', ROOT / 'Makefile', ROOT / 'graficar.py']
for path in args.include:
    if not path.is_file():
        raise SystemExit('File not found: ' + str(path))
with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(set(files)):
        z.write(path, path.relative_to(ROOT).as_posix())
    for path in args.include:
        z.write(path, path.name)
print(f'{destino.name}: {len(set(files)) + len(args.include)} files')

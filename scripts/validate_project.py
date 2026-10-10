import csv
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
count = 0
for path in list((ROOT / 'results').glob('*.csv')) + list((ROOT / 'parte2_3').rglob('*.csv')):
    rows = list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))
    if not rows or 't_seq' not in rows[0]:
        continue
    for row in rows:
        ts, tp, p = float(row['t_seq']), float(row['t_par']), int(row['p'])
        assert ts > 0 and tp > 0 and p > 0, path
        s = ts / tp
        for key, expected in [('S', s), ('E', s / p), ('C', p * tp), ('F', s / (p * tp))]:
            if key in row:
                assert math.isclose(float(row[key]), expected, rel_tol=0.005, abs_tol=0.00051), (path, key)
        count += 1
for p in [2, 4]:
    speedups = []
    for path in sorted((ROOT / 'parte2_3/reto').glob('reto_suma_r*.csv')):
        row = next(r for r in csv.DictReader(path.open()) if int(r['N']) == 262144 and int(r['p']) == p)
        speedups.append(float(row['t_seq']) / float(row['t_par']))
    assert len(speedups) == 5 and all(s > p for s in speedups)
    print(f'Historical challenge p={p}: median S={statistics.median(speedups):.6f}')
for path in [ROOT / 'lab12_speedup.c'] + list((ROOT / 'parte2_3').rglob('*.c')):
    source = path.read_text(encoding='utf-8')
    assert '/*' not in source and '//' not in source, path
    assert '#pragma omp parallel for' not in source, path
    assert all('nowait' in line for line in source.splitlines() if '#pragma omp for' in line), path
print(f'Validated {count} measurement rows, challenge repetitions and shared C source rules')

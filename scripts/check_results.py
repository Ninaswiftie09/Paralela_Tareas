import csv
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
samples = []
rows_checked = 0
max_error = 0
for path in sorted(RESULTS.glob('amdahl_fp*.csv')) + [RESULTS / 'gustafson.csv']:
    records = []
    for line in path.with_suffix('.log').read_text(encoding='utf-8').splitlines():
        if line.startswith('sample,'):
            _, kind, ns, np, p, repeat, elapsed, seq, value = line.split(',')
            row = dict(experiment=path.stem, kind=kind, ns=int(ns), np=int(np), p=int(p), repeat=int(repeat), elapsed=float(elapsed), sequential_phase=float(seq), value=float(value))
            records.append(row)
            samples.append(row)
    for row in csv.DictReader(path.open(newline='')):
        p = int(row['p'])
        np = 100000 * p if row['modo'] == 'gustafson' else int(400000 * float(row['param'].split('=')[1]) + 0.5)
        ns = 20000 if row['modo'] == 'gustafson' else 400000 - np
        sequential = [r for r in records if r['kind'] == 'sequential' and r['ns'] == ns and r['np'] == np]
        parallel = [r for r in records if r['kind'] == 'parallel' and r['ns'] == ns and r['np'] == np and r['p'] == p]
        assert len(sequential) == len(parallel) == 5
        assert {r['repeat'] for r in sequential} == {1, 2, 3, 4, 5}
        assert {r['repeat'] for r in parallel} == {1, 2, 3, 4, 5}
        assert abs(statistics.median(r['elapsed'] for r in sequential) - float(row['t_seq'])) <= 5.01e-7
        median = statistics.median(r['elapsed'] for r in parallel)
        assert abs(median - float(row['t_par'])) <= 5.01e-7
        median_run = next(r for r in parallel if r['elapsed'] == median)
        assert abs(median_run['sequential_phase'] - float(row['t_parte_seq'])) <= 5.01e-7
        assert float(row['t_seq']) > 0 and float(row['t_par']) > 0
        for r in parallel:
            error = abs(r['value'] - sequential[0]['value']) / max(1, abs(sequential[0]['value']))
            assert error <= 1e-10
            max_error = max(max_error, error)
        rows_checked += 1
with (RESULTS / 'samples.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=samples[0].keys())
    writer.writeheader()
    writer.writerows(samples)
print(f'Validated {rows_checked} median rows and {len(samples)} original repetitions; maximum relative numerical error: {max_error:.3g}')

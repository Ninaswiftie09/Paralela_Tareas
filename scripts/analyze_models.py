import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
def read(name):
    with (RESULTS / name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

amdahl = read('amdahl_con_S_E.csv')
groups = defaultdict(list)
for row in amdahl:
    groups[row['param']].append(row)
table = []
models = []
for param, rows in sorted(groups.items(), reverse=True):
    fp = float(param.split('=')[1])
    indexed = {int(r['p']): r for r in rows}
    pmax = max(indexed)
    fastest = min(rows, key=lambda r: float(r['t_par']))
    best_f = max(rows, key=lambda r: float(r['F']))
    actual = float(indexed[pmax]['S'])
    ideal = 1 / (1 - fp + fp / pmax)
    inferred = (1 - 1 / actual) / (1 - 1 / pmax)
    table.append(dict(fp=fp, S_p2=indexed[2]['S'], S_p4=indexed[4]['S'], S_pmax=actual, E_pmax=indexed[pmax]['E'], p_max_effectiveness=best_f['p'], p_min_time=fastest['p'], predicted_S_pmax=ideal, inferred_fp=inferred, limit_speedup='infinite' if fp == 1 else 1 / (1 - fp)))
    for p, row in indexed.items():
        models.append(dict(fp=fp, p=p, measured_speedup=float(row['S']), predicted_speedup=1 / (1 - fp + fp / p)))
with (RESULTS / 'amdahl_summary.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=table[0].keys())
    writer.writeheader()
    writer.writerows(table)
with (RESULTS / 'amdahl_models.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=models[0].keys())
    writer.writeheader()
    writer.writerows(models)
fig, ax = plt.subplots(figsize=(8, 5))
for fp in [1.00, 0.95, 0.90, 0.75, 0.50]:
    rs = sorted([r for r in models if r['fp'] == fp], key=lambda r: r['p'])
    line, = ax.plot([r['p'] for r in rs], [r['measured_speedup'] for r in rs], 'o-', label=f'fp={fp:.2f} medido')
    ax.plot([r['p'] for r in rs], [r['predicted_speedup'] for r in rs], '--', color=line.get_color(), alpha=0.7)
ax.set(xlabel='Hilos', ylabel='Speedup', title='Amdahl: medición y modelo ideal en líneas discontinuas')
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(RESULTS / 'amdahl_modelo.png', dpi=160)
plt.close(fig)
gustafson = read('gustafson_con_S_E.csv')
for row in gustafson:
    p = int(row['p'])
    s = float(row['t_parte_seq']) / float(row['t_par'])
    row['s'] = s
    row['scaled_prediction'] = p - s * (p - 1)
    row['fixed_fp083_prediction'] = 1 / (0.17 + 0.83 / p)
    row['prediction_difference'] = float(row['S']) - row['scaled_prediction']
with (RESULTS / 'gustafson_models.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=gustafson[0].keys())
    writer.writeheader()
    writer.writerows(gustafson)
fig, ax = plt.subplots(figsize=(8, 5))
ps = [int(r['p']) for r in gustafson]
ax.plot(ps, [float(r['S']) for r in gustafson], 'o-', label='Medido')
ax.plot(ps, [r['scaled_prediction'] for r in gustafson], 's--', label='Modelo escalado con s medido')
ax.plot(ps, [r['fixed_fp083_prediction'] for r in gustafson], '^--', label='Modelo fijo con fp=0.83')
ax.set(xlabel='Hilos', ylabel='Speedup', title='Problema creciente y modelos de speedup')
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(RESULTS / 'gustafson_modelo.png', dpi=160)
plt.close(fig)
print('Generated comparison tables and model plots')

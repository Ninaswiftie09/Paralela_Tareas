import csv
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
RESULTS = ROOT / 'results'
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
exe = BUILD / ('lab12.exe' if os.name == 'nt' else 'lab12')
command = ['gcc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fopenmp', 'lab12_speedup.c', '-o', str(exe), '-lm']
compilation = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
(RESULTS / 'compilation.txt').write_text(' '.join(command) + '\n' + compilation.stdout + compilation.stderr + 'Exit code: 0\n', encoding='utf-8')
environment = os.environ.copy()
environment['OMP_DYNAMIC'] = 'FALSE'
pmax = 8
metadata = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), platform=platform.platform(), cpu_identifier=platform.processor(), logical_processors=os.cpu_count(), requested_pmax=pmax, compiler=subprocess.check_output(['gcc', '--version'], text=True).splitlines()[0], repetitions=5, statistic='median', execution_environment='native Windows GCC' if os.name == 'nt' else 'native GCC', power_and_background_activity='not controlled by runner')
(RESULTS / 'environment.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
experiments = [(f'amdahl_fp{int(fp * 100)}', ['amdahl', '400000', f'{fp:.2f}', str(pmax)]) for fp in [1.00, 0.95, 0.90, 0.75, 0.50]]
experiments.append(('gustafson', ['gustafson', '100000', '20000', str(pmax)]))
for name, args in experiments:
    print('Running:', ' '.join(args), flush=True)
    with (RESULTS / f'{name}.csv').open('w', encoding='utf-8', newline='') as out, (RESULTS / f'{name}.log').open('w', encoding='utf-8') as err:
        err.write('Command: ' + ' '.join([str(exe)] + args) + '\n')
        err.flush()
        subprocess.run([str(exe)] + args, cwd=ROOT, env=environment, stdout=out, stderr=err, check=True)
    with (RESULTS / f'{name}.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != pmax or any(float(r['t_seq']) <= 0 or float(r['t_par']) <= 0 for r in rows):
        raise RuntimeError('Incomplete or zero-duration results: ' + name)
    print('Finished:', name, flush=True)
subprocess.run([sys.executable, str(ROOT / 'graficar.py')] + [str(RESULTS / f'{name}.csv') for name, _ in experiments], cwd=RESULTS, check=True)
print('Finished all assigned experiments', flush=True)

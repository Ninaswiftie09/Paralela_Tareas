import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--parts', choices=['nina', 'luis', 'all'], default='all')
parser.add_argument('--pmax', type=int, default=os.cpu_count() or 1)
parser.add_argument('--output', type=Path, default=ROOT / 'build/reproduced')
args = parser.parse_args()
if args.pmax < 1:
    parser.error('pmax must be positive')
args.output.mkdir(parents=True, exist_ok=True)
exe = ROOT / 'build' / ('lab12.exe' if os.name == 'nt' else 'lab12')
exe.parent.mkdir(exist_ok=True)
subprocess.run(['gcc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fopenmp', str(ROOT / 'lab12_speedup.c'), '-o', str(exe), '-lm'], check=True)
experiments = []
if args.parts in ['nina', 'all']:
    experiments += [(f'amdahl_fp{fp}', ['amdahl', '400000', str(fp / 100), str(args.pmax)]) for fp in [100, 95, 90, 75, 50]]
    experiments += [('gustafson', ['gustafson', '100000', '20000', str(args.pmax)])]
if args.parts in ['luis', 'all']:
    experiments += [('suma', ['suma', str(args.pmax)])]
    experiments += [(f'desb_{s}', ['desbalance', s, '40000', str(args.pmax)]) for s in ['static', 'dynamic', 'guided']]
for name, options in experiments:
    print('Running', name, flush=True)
    with (args.output / f'{name}.csv').open('w', encoding='utf-8', newline='') as out, (args.output / f'{name}.log').open('w', encoding='utf-8') as err:
        subprocess.run([str(exe)] + options, stdout=out, stderr=err, check=True)
subprocess.run([sys.executable, str(ROOT / 'graficar.py')] + [str((args.output / f'{name}.csv').resolve()) for name, _ in experiments], cwd=args.output, check=True)

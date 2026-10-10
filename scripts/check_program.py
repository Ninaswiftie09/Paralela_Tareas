import csv
import io
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / 'build' / ('lab12.exe' if sys.platform == 'win32' else 'lab12')
for args in [[], ['unknown'], ['amdahl', '0'], ['amdahl', '10x'], ['amdahl', '10', 'nan'], ['amdahl', '10', '1.1'], ['amdahl', '10', '0.9', '0'], ['gustafson', '-1'], ['desbalance', 'bad'], ['suma', '0']]:
    result = subprocess.run([str(EXE)] + args, capture_output=True, text=True)
    assert result.returncode == 1, args
for args in [['amdahl', '10000', '1', '2'], ['amdahl', '10000', '0', '2'], ['amdahl', '10000', '0.9', '2'], ['gustafson', '10000', '2000', '2']] + [['desbalance', s, '10000', '2'] for s in ['static', 'dynamic', 'guided']]:
    result = subprocess.run([str(EXE)] + args, capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout)))
    assert len(rows) == 2
    assert [int(row['p']) for row in rows] == [1, 2]
source = (ROOT / 'lab12_speedup.c').read_text(encoding='utf-8')
assert '/*' not in source and '//' not in source
assert all('nowait' in line for line in source.splitlines() if '#pragma omp for' in line)
print('Passed 10 invalid-input cases, 7 small experiments and explicit loop synchronization checks')

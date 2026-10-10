from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
BUILD.mkdir(exist_ok=True)
for name, source in [('lab12', 'lab12_speedup.c'), ('lab12_umbral', 'parte2_3/extra/lab12_umbral.c'), ('lab12_reto', 'parte2_3/reto/lab12_speedup.c')]:
    exe = BUILD / (name + ('.exe' if os.name == 'nt' else ''))
    subprocess.run(['gcc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fopenmp', str(ROOT / source), '-o', str(exe), '-lm'], check=True)
    print('Compiled', name)

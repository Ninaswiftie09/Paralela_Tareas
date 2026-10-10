import pathlib
import re
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
suffix = ".exe" if sys.platform == "win32" else ""
count = 0
for n, steps in [(1, 2), (2, 3), (17, 4), (101, 3)]:
    for mode in ["seq", "parallel", "optimized"]:
        for schedule in ["static", "dynamic", "guided"]:
            for chunk in [0, 8, 32, 64]:
                command = [str(root / "build" / f"nbody_{mode}{suffix}"), "--n", str(n), "--steps", str(steps), "--threads", "8", "--schedule", schedule, "--chunk", str(chunk)]
                output = subprocess.check_output(command, text=True)
                error = float(re.search(r"Max difference: (.*)", output).group(1))
                assert error <= 1e-9
                count += 1
for args in [["--n", "0"], ["--steps", "-1"], ["--schedule", "invalid"], ["--chunk", "-1"], ["--n"], ["--n", "5x"], ["--unknown", "2"]]:
    result = subprocess.run([str(root / "build" / f"nbody_parallel{suffix}")] + args, capture_output=True)
    assert result.returncode == 1
source = (root / "src" / "nbody.hpp").read_text()
assert all("nowait" in line for line in source.splitlines() if "#pragma omp for" in line)
assert "#pragma omp single" not in source
print(f"Passed {count} numerical configurations and 7 invalid-input checks; all OpenMP loops use nowait")

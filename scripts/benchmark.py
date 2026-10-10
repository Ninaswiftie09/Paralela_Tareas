import csv
import json
import pathlib
import platform
import re
import subprocess
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
EVIDENCE = ROOT / "evidence"
BUILD.mkdir(exist_ok=True)
EVIDENCE.mkdir(exist_ok=True)
suffix = ".exe" if platform.system() == "Windows" else ""
compile_log = []
for name in ["seq", "parallel", "optimized"]:
    command = ["g++", "-O2", "-std=c++17", "-fopenmp", "-Wall", "-Wextra", "-pedantic", f"src/nbody_{name}.cpp", "-o", f"build/nbody_{name}{suffix}"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    compile_log.extend(["$ " + " ".join(command), result.stdout + result.stderr, "Exit code: 0"])
(EVIDENCE / "compile.txt").write_text("\n".join(compile_log), encoding="utf-8")
configs = [(2, "static", 0), (4, "static", 0), (8, "static", 0), (8, "static", 8), (8, "static", 32), (8, "static", 64), (8, "dynamic", 8), (8, "dynamic", 32), (8, "dynamic", 64), (8, "guided", 0)]
rows = []
for mode in ["seq", "parallel", "optimized"]:
    for threads, schedule, chunk in ([(1, "sequential", 0)] if mode == "seq" else configs):
        for repeat in range(1, 4):
            command = [f"./build/nbody_{mode}{suffix}", "--n", "5000", "--steps", "10", "--threads", str(threads), "--schedule", "static" if mode == "seq" else schedule, "--chunk", str(chunk)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
            output = result.stdout
            value = lambda label: re.search(re.escape(label) + r": ([^\n]+)", output).group(1).strip()
            rows.append(dict(mode=value("Mode"), n=5000, steps=10, seed=42, threads_requested=threads, threads_used=int(value("Threads used")), schedule=schedule, chunk=chunk, repeat=repeat, elapsed_seconds=float(value("Elapsed").split()[0]), checksum=float(value("Checksum")), max_difference=float(value("Max difference")), processors=int(value("Processors reported by OpenMP")), max_threads=int(value("Max threads reported by OpenMP"))))
            if repeat == 1 and (mode == "seq" or (threads == 8 and schedule == "dynamic" and chunk == 64)):
                name = {"seq": "sequential", "parallel": "parallel", "optimized": "optimized"}[mode]
                (EVIDENCE / f"{name}.txt").write_text("$ " + " ".join(command) + "\n" + output + "Exit code: 0\n", encoding="utf-8")
            print(mode, threads, schedule, chunk, repeat, rows[-1]["elapsed_seconds"], flush=True)
with (ROOT / "results.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
groups = defaultdict(list)
for row in rows:
    groups[(row["mode"], row["threads_used"], row["schedule"], row["chunk"])].append(row["elapsed_seconds"])
baseline = sum(groups[("sequential", 1, "sequential", 0)]) / 3
summary = []
for (mode, threads, schedule, chunk), times in groups.items():
    average = sum(times) / len(times)
    summary.append(dict(mode=mode, threads=threads, schedule=schedule, chunk=chunk, runs=len(times), mean_seconds=average, min_seconds=min(times), max_seconds=max(times), speedup=baseline / average, efficiency=baseline / average / threads))
with (ROOT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)
(EVIDENCE / "hardware.txt").write_text((EVIDENCE / "optimized.txt").read_text(encoding="utf-8"), encoding="utf-8")
(BUILD / "metrics.json").write_text(json.dumps(dict(summary=summary, max_difference=max(r["max_difference"] for r in rows), platform=platform.platform(), compiler=subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]), indent=2), encoding="utf-8")

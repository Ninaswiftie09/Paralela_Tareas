#!/usr/bin/env python3
"""Gráficas extra (no son parte de las 7 obligatorias):
  extra_desbalance_variabilidad.png  mediana de 6 corridas + rango mín–máx por schedule
  extra_suma_umbral.png              S vs N con tamaños intermedios (mediana de 3 corridas)
Uso (desde parte2_3/):  python3 scripts/graficas_extra.py
"""
import csv
import glob
import statistics as st
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "axes.edgecolor": MUTED, "axes.labelcolor": TEXT, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "font.size": 10,
})


def speedups(archivos, clave):
    d = defaultdict(list)
    for a in archivos:
        for r in csv.DictReader(open(a)):
            d[clave(r)].append(float(r["t_seq"]) / float(r["t_par"]))
    return d


# ---------- desbalance: mediana y rango de 6 corridas ----------
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ps = list(range(1, 13))
ax.plot(ps, ps, color=MUTED, ls="--", lw=1)
ax.text(12.15, 12, "ideal", color=MUTED, va="center")
modelo = [p * p / (2 * p - 1) for p in ps]
ax.plot(ps, modelo, color=MUTED, ls=":", lw=1.5)
ax.text(12.15, modelo[-1], "modelo static\np²/(2p−1)", color=MUTED, va="center", fontsize=8)
for color, s in zip(SERIES, ["static", "dynamic", "guided"]):
    d = speedups([f"../results/desb_{s}.csv"] + sorted(glob.glob(f"repeticiones/desb_{s}_r*.csv")),
                 lambda r: int(r["p"]))
    med = [st.median(d[p]) for p in ps]
    ax.fill_between(ps, [min(d[p]) for p in ps], [max(d[p]) for p in ps], color=color, alpha=0.15, lw=0)
    ax.plot(ps, med, "o-", color=color, lw=2, ms=6, mec="white", mew=1.5, label=s)
ax.set_xlabel("Hilos (p)")
ax.set_ylabel("Speedup S = Ts / Tp")
ax.set_xticks(ps)
ax.set_xlim(0.5, 13.6)
ax.set_title("desbalance: mediana de 6 corridas (banda = mín–máx)", color=TEXT, loc="left")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig("extra_desbalance_variabilidad.png", dpi=150)
print("  -> extra_desbalance_variabilidad.png")

# ---------- suma: umbral con tamaños intermedios ----------
d = speedups(sorted(glob.glob("extra/umbral_r*.csv")), lambda r: (int(r["p"]), int(r["N"])))
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.axhline(1, color=MUTED, ls="--", lw=1)
ax.text(1024 * 0.93, 1.06, "S = 1 (empata con la secuencial)", color=MUTED, fontsize=8)
for color, p in zip(SERIES, [1, 2, 4, 8, 12]):
    ns = sorted(n for (q, n) in d if q == p)
    med = [st.median(d[(p, n)]) for n in ns]
    ax.plot(ns, med, "o-", color=color, lw=2, ms=6, mec="white", mew=1.5, label=f"p = {p}")
    ax.text(ns[-1] * 1.12, med[-1], f"p={p}", color=TEXT, va="center", fontsize=8)
ax.set_xscale("log", base=2)
ax.set_xlim(800, 100000)
ax.set_xlabel("N (cantidad de números, escala log)")
ax.set_ylabel("Speedup S = Ts / Tp")
ax.set_title("suma: ¿desde qué N gana la paralela? (mediana de 3 corridas)", color=TEXT, loc="left")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig("extra_suma_umbral.png", dpi=150)
print("  -> extra_suma_umbral.png")

# ---------- reto: eficiencia E = S/p (E > 1 <=> S > p) en 5 corridas ----------
d = speedups(sorted(glob.glob("reto/reto_suma_r*.csv")), lambda r: (int(r["p"]), int(r["N"])))
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.axhline(1, color=MUTED, ls="--", lw=1)
ax.text(2097152 * 1.05, 1.03, "E = 1  (S = p)", color=MUTED, fontsize=8)
ax.axvspan(1.25 * 2**20 / 8, 12 * 2**20 / 8, color=GRID, alpha=0.5, lw=0)
ax.text(1.3 * 2**20 / 8, 1.72, "no cabe en L2 de 1 núcleo P (1.25 MB)\npero sí en L3 (12 MB)", color=MUTED, fontsize=8)
for color, p in zip(SERIES[1:], [2, 4, 8]):
    ns = sorted(n for (q, n) in d if q == p)
    E = [[s / p for s in d[(p, n)]] for n in ns]
    ax.fill_between(ns, [min(e) for e in E], [max(e) for e in E], color=color, alpha=0.15, lw=0)
    ax.plot(ns, [st.median(e) for e in E], "o-", color=color, lw=2, ms=6, mec="white", mew=1.5, label=f"p = {p}")
ax.set_xscale("log", base=2)
ax.set_xticks([131072 * 2**k for k in range(6)])
ax.set_xticklabels(["1 MB", "2 MB", "4 MB", "8 MB", "16 MB", "32 MB"])
ax.set_xlabel("Tamaño del arreglo (N doubles × 8 bytes)")
ax.set_ylabel("Eficiencia E = S / p")
ax.set_title("reto: S > p con suma AVX2 (mediana de 5 corridas, banda = mín–máx)", color=TEXT, loc="left")
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig("extra_reto_superlineal.png", dpi=150)
print("  -> extra_reto_superlineal.png")

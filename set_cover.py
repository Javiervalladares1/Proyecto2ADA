"""
Set Cover Problem - Proyecto #2
Análisis y Diseño de Algoritmos, UVG 2026
Ihan Marroquin, Javier Valladares, Ian Cumes
"""

import time
import random
import math
import csv
from pathlib import Path

# Outputs se guardan junto al script (no en el CWD)
OUTPUT_DIR = Path(__file__).resolve().parent


def set_cover_dp(n, sets):
    """Bitmask DP. Retorna (mínimo de conjuntos, índices elegidos). O(2^n * m)."""
    full = (1 << n) - 1
    cover = [sum(1 << e for e in s) for s in sets]

    INF = float('inf')
    dp = [INF] * (1 << n)
    parent = [-1] * (1 << n)
    dp[0] = 0

    for mask in range(1, 1 << n):
        for i, cm in enumerate(cover):
            if cm & mask:
                prev = mask & ~cm
                if dp[prev] + 1 < dp[mask]:
                    dp[mask] = dp[prev] + 1
                    parent[mask] = i

    if dp[full] == INF:
        return -1, []

    chosen = []
    mask = full
    while mask:
        i = parent[mask]
        chosen.append(i)
        mask &= ~cover[i]
    return dp[full], chosen


def set_cover_greedy(n, sets):
    """Greedy: en cada paso elige el conjunto con mayor cobertura nueva. O(n^2 * m)."""
    uncovered = set(range(n))
    sets_as_sets = [set(s) for s in sets]
    available = set(range(len(sets)))
    chosen = []

    while uncovered:
        best = max(available, key=lambda i: len(sets_as_sets[i] & uncovered))
        if not sets_as_sets[best] & uncovered:
            return -1, []
        uncovered -= sets_as_sets[best]
        chosen.append(best)
        available.remove(best)

    return len(chosen), chosen


def generate_random_instance(n, m, seed=42):
    """Instancia aleatoria; el último conjunto cubre U para garantizar factibilidad."""
    random.seed(seed)
    universe = list(range(n))
    sets = []
    for _ in range(m - 1):
        size = random.randint(1, max(1, n // 2))
        sets.append(random.sample(universe, size))
    sets.append(universe[:])
    return n, sets


def generate_adversarial_instance(k):
    """
    Instancia donde greedy usa k conjuntos pero el óptimo solo necesita 2.
    Construcción por capas: capa i tiene 2^i elementos (i = 1..k).
    Greedy escoge cada capa entera porque siempre es el conjunto con mayor
    cobertura nueva; el óptimo parte cada capa en dos mitades (A y B).
    """
    layers = []
    elem = 0
    for i in range(1, k + 1):
        size = 2 ** i
        layers.append(list(range(elem, elem + size)))
        elem += size
    n = elem  # n = 2^(k+1) - 2

    sets = [layer[:] for layer in layers]  # k conjuntos trampa

    A, B = [], []
    for layer in layers:
        half = len(layer) // 2
        A.extend(layer[:half])
        B.extend(layer[half:])
    sets.append(A)
    sets.append(B)

    return n, sets


def verify_solution(n, sets, chosen):
    covered = set()
    for i in chosen:
        covered.update(sets[i])
    return covered == set(range(n))


def correctness_check():
    print("=" * 60)
    print("VERIFICACIÓN DE CORRECTITUD")
    print("=" * 60)

    n = 6
    sets = [[0, 1, 2, 3], [0, 1, 4], [2, 3, 5]]
    dp_c, dp_s = set_cover_dp(n, sets)
    gr_c, gr_s = set_cover_greedy(n, sets)

    print(f"\nU = {list(range(n))}, conjuntos = {sets}")
    print(f"DP     -> {dp_c} conjuntos, verificado: {verify_solution(n, sets, dp_s)}")
    print(f"Greedy -> {gr_c} conjuntos, verificado: {verify_solution(n, sets, gr_s)}")
    print(f"Greedy usó {gr_c - dp_c} conjunto(s) extra.\n")


def run_benchmark():
    print("=" * 75)
    print("BENCHMARK — instancias aleatorias")
    print("=" * 75)

    cases = [(5, 8), (6, 10), (7, 12), (8, 14), (9, 16),
             (10, 18), (11, 20), (12, 22), (13, 24), (14, 26),
             (15, 28), (16, 30), (17, 32), (18, 34)]

    header = f"{'n':>4} {'m':>4} | {'DP (s)':>11} {'Greedy (s)':>12} | {'OPT':>5} {'Gr':>5} {'Ratio':>7}"
    print(header)
    print("-" * len(header))

    results = []
    for n, m in cases:
        _, sets = generate_random_instance(n, m)

        t0 = time.perf_counter()
        dp_c, _ = set_cover_dp(n, sets)
        dp_t = time.perf_counter() - t0

        t0 = time.perf_counter()
        gr_c, _ = set_cover_greedy(n, sets)
        gr_t = time.perf_counter() - t0

        ratio = gr_c / dp_c if dp_c > 0 else float('nan')
        results.append((n, m, dp_t, gr_t, dp_c, gr_c, ratio))
        print(f"{n:>4} {m:>4} | {dp_t:>11.6f} {gr_t:>12.6f} | {dp_c:>5} {gr_c:>5} {ratio:>7.3f}")

    large_cases = [(20, 40), (30, 60), (50, 100), (100, 200), (200, 400), (500, 1000)]
    print("\nGREEDY — entradas grandes (DP inviable)")
    print(f"{'n':>6} {'m':>6} | {'Greedy (s)':>12} {'Conjuntos':>10}")
    print("-" * 40)

    large = []
    for n, m in large_cases:
        _, sets = generate_random_instance(n, m)
        t0 = time.perf_counter()
        gc, _ = set_cover_greedy(n, sets)
        gt = time.perf_counter() - t0
        large.append((n, m, gt, gc))
        print(f"{n:>6} {m:>6} | {gt:>12.6f} {gc:>10}")

    return results, large


def run_adversarial_benchmark():
    print("\n" + "=" * 75)
    print("BENCHMARK ADVERSARIAL — donde greedy se aleja del óptimo")
    print("=" * 75)
    print(f"{'k':>3} {'n':>5} | {'DP':>5} {'Greedy':>7} {'Ratio':>7} | {'Greedy (s)':>12}")
    print("-" * 60)

    adv = []
    # k <= 3 son comparables con DP (n <= 14). k >= 4 solo greedy.
    for k in [2, 3]:
        n, sets = generate_adversarial_instance(k)
        t0 = time.perf_counter()
        dp_c, _ = set_cover_dp(n, sets)
        dp_t = time.perf_counter() - t0
        t0 = time.perf_counter()
        gr_c, _ = set_cover_greedy(n, sets)
        gr_t = time.perf_counter() - t0
        ratio = gr_c / dp_c
        adv.append((k, n, dp_c, gr_c, ratio, gr_t))
        print(f"{k:>3} {n:>5} | {dp_c:>5} {gr_c:>7} {ratio:>7.3f} | {gr_t:>12.6f}")

    # Para k >= 4 el óptimo es 2 por construcción (A ∪ B cubren U).
    for k in [4, 5, 6, 7, 8]:
        n, sets = generate_adversarial_instance(k)
        t0 = time.perf_counter()
        gr_c, _ = set_cover_greedy(n, sets)
        gr_t = time.perf_counter() - t0
        ratio = gr_c / 2
        adv.append((k, n, 2, gr_c, ratio, gr_t))
        print(f"{k:>3} {n:>5} | {2:>5}* {gr_c:>7} {ratio:>7.3f} | {gr_t:>12.6f}")

    print("\n* Óptimo conocido por construcción (A y B cubren U).")
    return adv


def save_csv(results, large, adv):
    files = [
        ("benchmark_results.csv",
         ["n", "m", "dp_time_s", "greedy_time_s", "dp_optimal", "greedy_sets", "ratio"],
         results),
        ("benchmark_large.csv",
         ["n", "m", "greedy_time_s", "greedy_sets"],
         large),
        ("benchmark_adversarial.csv",
         ["k", "n", "optimal", "greedy_sets", "ratio", "greedy_time_s"],
         adv),
    ]
    print()
    for name, header, rows in files:
        path = OUTPUT_DIR / name
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        print(f"Guardado: {path}")


def plot_results(results, large, adv):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("\n[!] matplotlib/numpy no disponibles. Instala con: pip install matplotlib numpy")
        return

    ns = np.array([r[0] for r in results])
    dp_t = np.array([r[2] for r in results])
    gr_t = np.array([r[3] for r in results])
    ratios = [r[6] for r in results]

    # Figura 1: tiempos y calidad en instancias aleatorias
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Set Cover — Comparación empírica (instancias aleatorias)", fontsize=14, fontweight='bold')

    ax1 = axes[0]
    ax1.scatter(ns, dp_t, color='steelblue', label='DP (Bitmask)', zorder=5, s=60)
    ax1.scatter(ns, gr_t, color='tomato', label='Greedy', zorder=5, s=60)
    x_fit = np.linspace(ns.min(), ns.max(), 200)

    mask_dp = dp_t > 0
    if mask_dp.sum() >= 2:
        c_dp = np.polyfit(ns[mask_dp], np.log(dp_t[mask_dp]), 1)
        ax1.plot(x_fit, np.exp(np.polyval(c_dp, x_fit)), '--', color='steelblue',
                 alpha=0.6, label=f'Regresión DP: e^({c_dp[0]:.3f}·n)')

    mask_gr = gr_t > 1e-9
    if mask_gr.sum() >= 3:
        c_gr = np.polyfit(ns[mask_gr], gr_t[mask_gr], 2)
        ax1.plot(x_fit, np.polyval(c_gr, x_fit), '--', color='tomato',
                 alpha=0.6, label='Regresión Greedy: grado 2')

    ax1.set_xlabel("Tamaño del universo (n)")
    ax1.set_ylabel("Tiempo (s)")
    ax1.set_title("Tiempos de ejecución")
    ax1.set_yscale('log')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.scatter(ns, ratios, color='mediumpurple', zorder=5, s=60, label='Ratio greedy/óptimo')
    ax2.axhline(1.0, color='gray', linestyle='--', alpha=0.7, label='Óptimo (ratio = 1)')
    hn = [math.log(n) + 0.5772 for n in ns]
    ax2.plot(ns, hn, ':', color='orange', alpha=0.8, label='Cota Hₙ ≈ ln(n)')
    ax2.set_xlabel("Tamaño del universo (n)")
    ax2.set_ylabel("Ratio greedy / óptimo")
    ax2.set_title("Calidad de la solución greedy (instancias aleatorias)")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path1 = OUTPUT_DIR / "benchmark_plot.png"
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    print(f"Guardado: {path1}")
    plt.close()

    # Figura 2: greedy en entradas grandes + caso adversarial
    fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
    fig2.suptitle("Set Cover — Escalabilidad y caso adversarial", fontsize=14, fontweight='bold')

    ax3 = axes2[0]
    ln = np.array([r[0] for r in large])
    lt = np.array([r[2] for r in large])
    ax3.scatter(ln, lt, color='darkorange', s=80, zorder=5, label='Greedy (n grande)')
    if len(ln) >= 3:
        c = np.polyfit(ln, lt, 2)
        x_fit2 = np.linspace(ln.min(), ln.max(), 300)
        ax3.plot(x_fit2, np.polyval(c, x_fit2), '--', color='darkorange',
                 alpha=0.7, label='Regresión grado 2')
    ax3.set_xlabel("Tamaño del universo (n)")
    ax3.set_ylabel("Tiempo (s)")
    ax3.set_title("Greedy — entradas grandes")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    ax4 = axes2[1]
    adv_n = np.array([row[1] for row in adv])
    adv_ratio = np.array([row[4] for row in adv])
    ax4.scatter(adv_n, adv_ratio, color='crimson', s=70, zorder=5, label='Ratio greedy/óptimo')
    hn_adv = [math.log(n) + 0.5772 for n in adv_n]
    ax4.plot(adv_n, hn_adv, ':', color='orange', alpha=0.8, label='Cota Hₙ ≈ ln(n)')
    ax4.set_xlabel("Tamaño del universo (n)")
    ax4.set_ylabel("Ratio greedy / óptimo")
    ax4.set_title("Caso adversarial — el ratio crece con n")
    ax4.set_xscale('log')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    path2 = OUTPUT_DIR / "adversarial_plot.png"
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    print(f"Guardado: {path2}")
    plt.close()


if __name__ == "__main__":
    correctness_check()
    results, large = run_benchmark()
    adv = run_adversarial_benchmark()
    save_csv(results, large, adv)
    plot_results(results, large, adv)

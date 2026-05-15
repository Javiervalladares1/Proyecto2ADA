"""
Set Cover Problem - Proyecto #2
Análisis y Diseño de Algoritmos, UVG 2026
Ihan Marroquin, Javier Valladares, Ian Cumes
"""

import time
import random
import csv


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


def save_csv(results, large):
    with open("benchmark_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "m", "dp_time_s", "greedy_time_s", "dp_optimal", "greedy_sets", "ratio"])
        w.writerows(results)

    with open("benchmark_large.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "m", "greedy_time_s", "greedy_sets"])
        w.writerows(large)

    print("\nArchivos: benchmark_results.csv, benchmark_large.csv")


if __name__ == "__main__":
    correctness_check()
    results, large = run_benchmark()
    save_csv(results, large)

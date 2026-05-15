"""
Set Cover Problem - Proyecto #2
Análisis y Diseño de Algoritmos, UVG 2026
Ihan Marroquin, Javier Valladares, Ian Cumes
"""


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
                prev = mask & ~cm  # elementos que quedan sin cubrir
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


if __name__ == "__main__":
    # Contraejemplo clásico: greedy es subóptimo
    n = 6
    sets = [[0, 1, 2, 3], [0, 1, 4], [2, 3, 5]]

    dp_count, dp_chosen = set_cover_dp(n, sets)
    gr_count, gr_chosen = set_cover_greedy(n, sets)

    print(f"Universo: {list(range(n))}")
    print(f"Conjuntos: {sets}")
    print(f"DP     -> {dp_count} conjuntos, índices {dp_chosen}")
    print(f"Greedy -> {gr_count} conjuntos, índices {gr_chosen}")

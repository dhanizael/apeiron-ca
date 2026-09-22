"""Newton Tahap-B makro (v0): pemulihan J(ρ) — fundamental diagram Rule 184.

Ruang hipotesis: piecewise-linear ≤ max_segments segmen, breakpoint pada GRID.
Seleksi MDL: error_bits + model_bits (spec §6.1 parsimoni eksplisit — bukan
akurasi semata). measure_flow = pengamatan Newton atas window (bukan pemberian
engine): mobil menyeberang edge (i→i+1) iff s_i=1, s_{i+1}=0, t_{i+1}=1.
"""
import itertools
import math

GRID = [round(0.05 * k, 2) for k in range(1, 20)]  # 0.05..0.95
PARAM_BITS = 32  # a,b tiap segmen (float32)
BP_BITS = 8      # indeks grid breakpoint


def _r(state: int, n: int, mask: int) -> int:
    """Vektor bit i ← state[i+1]."""
    return ((state >> 1) | (state << (n - 1))) & mask


def measure_flow(states: list[int], n: int) -> float:
    mask = (1 << n) - 1
    crossings = 0
    for s, t in zip(states, states[1:]):
        crossed = s & ~_r(s, n, mask) & _r(t, n, mask) & ~t & mask
        crossings += crossed.bit_count()
    return crossings / ((len(states) - 1) * n)


def _fit_segment(pts: list[tuple[float, float]]):
    m = len(pts)
    if m == 0:
        return (0.0, 0.0, 0.0)
    if m == 1:
        return (pts[0][1], 0.0, 0.0)
    mx = sum(x for x, _ in pts) / m
    my = sum(y for _, y in pts) / m
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return (my, 0.0, sum((y - my) ** 2 for _, y in pts))
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    a = my - b * mx
    sse = sum((y - (a + b * x)) ** 2 for x, y in pts)
    return (a, b, sse)


def fit_pw_linear(xs: list[float], ys: list[float], max_segments: int = 3,
                  grid: list[float] | None = None) -> dict:
    pts = sorted(zip(xs, ys))
    n = len(pts)
    best = None
    grid = grid or GRID
    for k in range(1, max_segments + 1):
        for bps in itertools.combinations(grid, k - 1):
            cuts = [0.0, *bps, 1.0]
            segs, sse = [], 0.0
            for lo, hi in zip(cuts, cuts[1:]):
                seg_pts = [(x, y) for x, y in pts if lo <= x < hi or (hi >= 1.0 and x == 1.0)]
                a, b, e = _fit_segment(seg_pts)
                sse += e
                segs.append((lo, hi, a, b))
            model_bits = k * 2 * PARAM_BITS + (k - 1) * BP_BITS
            err_bits = n * math.log2(max(sse, 1e-12) / n + 1e-9)
            mdl = err_bits + model_bits
            if best is None or mdl < best["mdl"]:
                best = {
                    "segments": segs, "mdl": mdl, "model_bits": model_bits,
                    "sse": sse, "n_segments": k,
                }
    return best


def predict(model: dict, x: float) -> float:
    for lo, hi, a, b in model["segments"]:
        if lo <= x < hi or (hi >= 1.0 and x <= 1.0):
            return a + b * x
    _, _, a, b = model["segments"][-1]
    return a + b * x

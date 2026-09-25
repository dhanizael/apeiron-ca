"""Figur README (log 026): SVG murni-stdlib, lahir dari run deterministik.

F1: spacetime gerbang AND (law 22126, run 11 — dua setoran → emit → restore).
F2: trajektori populasi perpetuum (law 19631, laut difus, 20k).
Setiap figur = eksperimen asli + visualisasi; satu perintah, tanpa dependensi.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(ROOT / "experiments" / "m2"))
sys.path.insert(0, str(ROOT / "experiments" / "m4"))

from semesta import ca, io  # noqa: E402
from state_surgery import write_snapshot  # noqa: E402

N = 16384
ENGINE = str(ROOT / "engine" / "target" / "release" / "engine")
OUTDIR = ROOT / "figures"

COLORS = {0: "#ffffff", 1: "#a8d5ba", 2: "#4f9d69", 3: "#1e5c3a",
          4: "#14342b", 5: "#0c1f1a", 6: "#0c1f1a", 7: "#0c1f1a", 8: "#000000"}
SERIES = {1: "#1e5c3a", 2: "#4f9d69", 3: "#b5651d", 4: "#8e44ad", 5: "#c0392b"}


def run_gate11():
    """Run (1,1) gerbang AND — persis gate.py (law 22126, m=6, kr=2)."""
    law = ca.random_table_rich(4, 22126)
    P = 8000
    cells = [0] * N
    cells[P], cells[P + 1] = 6, 2
    cells[P - 10] = 1
    cells[P - 14] = 1
    d = OUTDIR / "_work" / "gate11"
    (d / "w").mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess.run([ENGINE, "run", "--n", str(N), "--k", "4", "--seed", "20001",
                    "--steps", "60", "--window", "60",
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    return [ca.unpack_cells(x, N, 4) for x in
            io.read_window(d / "w" / "window.bin", N, m["window_states"], 4)]


def spacetime_svg(states, p0, p1, path):
    """SVG spacetime: sumbu-x sel [p0..p1), sumbu-y waktu ke bawah."""
    rows = [s[p0:p1] for s in states]
    w, h = p1 - p0, len(rows)
    cell = 10
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*cell}" '
           f'height="{h*cell}" shape-rendering="crispEdges">']
    for t, row in enumerate(rows):
        for i, v in enumerate(row):
            svg.append(f'<rect x="{i*cell}" y="{t*cell}" width="{cell}" '
                       f'height="{cell}" fill="{COLORS.get(v, "#000000")}"/>')
    svg.append("</svg>")
    Path(path).write_text("\n".join(svg))


def run_perpetuum():
    """Run perpetuum 19631 (laut difus, seed 21001) → trajektori populasi."""
    law = ca.random_table_rich(4, 19631)
    cells = [(0 if ca.Rng(21001).next_u64() % 2 == 0 else 1) for _ in range(N)]
    d = OUTDIR / "_work" / "perp"
    (d / "w").mkdir(parents=True, exist_ok=True)
    (d / "rule.bin").write_bytes(bytes(law))
    write_snapshot(d / "init.bin", cells, 4)
    subprocess.run([ENGINE, "run", "--n", str(N), "--k", "4", "--seed", "21001",
                    "--steps", "20000", "--window", "6000",
                    "--rule-table", str(d / "rule.bin"),
                    "--init-state", str(d / "init.bin"), "--threads", "1",
                    "--outdir", str(d / "w")], check=True, capture_output=True)
    m = io.read_manifest(d / "w" / "manifest.json")
    raw = io.read_window(d / "w" / "window.bin", N, m["window_states"], 4)
    states = [ca.unpack_cells(x, N, 4) for x in raw[::24]]
    trajs = {}
    for s in states:
        for v in s:
            trajs[v] = trajs.get(v, 0) + 1
    series = {v: [] for v in sorted(trajs) if trajs[v] > 200}
    for s in states:
        cnt = {}
        for v in s:
            cnt[v] = cnt.get(v, 0) + 1
        for v in series:
            series[v].append(cnt.get(v, 0))
    return series


def population_svg(series, path):
    """SVG garis multi-spesies (trajektori populasi, dinormalisasi sumbu-y)."""
    w, h, pad = 900, 300, 30
    tmax = max(len(v) for v in series.values())
    ymax = max(max(v) for v in series.values())
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" font-family="monospace">']
    svg.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')
    for gy in range(5):
        y = pad + gy * (h - 2 * pad) / 4
        svg.append(f'<line x1="{pad}" y1="{y}" x2="{w-pad}" y2="{y}" '
                   f'stroke="#e0e0e0" stroke-width="1"/>')
    for v, traj in series.items():
        pts = " ".join(
            f"{pad + i*(w-2*pad)/(tmax-1):.1f},"
            f"{h-pad - (val/ymax)*(h-2*pad):.1f}" for i, val in enumerate(traj))
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{SERIES.get(v, "#555")}" '
                   f'stroke-width="2"/>')
        ylab = h - pad - (traj[-1] / ymax) * (h - 2 * pad)
        svg.append(f'<text x="{w-pad+4}" y="{ylab+4:.1f}" font-size="12" '
                   f'fill="{SERIES.get(v, "#555")}">v{v}</text>')
    svg.append(f'<text x="{pad}" y="{pad-10}" font-size="13" fill="#333">'
               f'perpetuum 19631 — populations p_v(t), t = 14 000 … 20 000</text>')
    svg.append("</svg>")
    Path(path).write_text("\n".join(svg))


def main() -> int:
    OUTDIR.mkdir(exist_ok=True)
    states = run_gate11()
    spacetime_svg(states, 7980, 8045, OUTDIR / "gate_spacetime.svg")
    print("gate_spacetime.svg")
    series = run_perpetuum()
    population_svg(series, OUTDIR / "perpetuum_populations.svg")
    print("perpetuum_populations.svg:", {v: len(t) for v, t in series.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())

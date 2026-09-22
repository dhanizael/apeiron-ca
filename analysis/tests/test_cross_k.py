"""K1′ lintas implementasi untuk keluarga flow k-bit: Rust ≡ Python, bit-identical."""
import subprocess

from semesta import ca, io


def _run_flow(engine_bin, tmp_path, n, k, seed, steps, W):
    raw = ca.random_table(k, seed + 1)
    table = ca.clip_table(raw, k)
    rule_bin = tmp_path / "rule.bin"
    rule_bin.write_bytes(bytes(table))
    out = tmp_path / "run"
    subprocess.run(
        [engine_bin, "run", "--n", str(n), "--k", str(k), "--uniform",
         "--seed", str(seed), "--steps", str(steps), "--window", str(W),
         "--rule-table", str(rule_bin), "--threads", "1", "--outdir", str(out)],
        check=True, capture_output=True,
    )
    m = io.read_manifest(out / "manifest.json")
    assert m["k"] == k and m["rule"] == "flow-table"
    assert int(m["rule_fnv"], 16) == ca.table_fnv(table)
    return ca.from_seed_uniform(n, k, seed), table, io.read_window(out / "window.bin", n, m["window_states"], k)


def test_rust_python_flow_k4(engine_bin, tmp_path):
    n, k, seed, steps, W = 256, 4, 21, 300, 32
    cells, table, states = _run_flow(engine_bin, tmp_path, n, k, seed, steps, W)
    for _ in range(steps):
        cells = ca.step_flow(cells, k, table)
    assert ca.pack_cells(cells, k) == states[-1], "state akhir Rust ≠ Python (k=4)"


def test_rust_python_flow_k2(engine_bin, tmp_path):
    n, k, seed, steps, W = 256, 2, 33, 300, 32
    cells, table, states = _run_flow(engine_bin, tmp_path, n, k, seed, steps, W)
    for _ in range(steps):
        cells = ca.step_flow(cells, k, table)
    assert ca.pack_cells(cells, k) == states[-1], "state akhir Rust ≠ Python (k=2)"


def test_python_conservation_k_bits():
    for k in (2, 4, 8):
        table = ca.clip_table(ca.random_table(k, 11), k)
        cells = ca.from_seed_uniform(256, k, 11)
        s0 = sum(cells)
        for _ in range(50):
            cells = ca.step_flow(cells, k, table)
            assert sum(cells) == s0, f"konservasi rusak k={k}"

"""K1 dua arah: evolusi Python referensi ≡ engine Rust, bit-identical."""
import subprocess

from semesta import ca, io


def test_rust_python_bit_identical(engine_bin, tmp_path):
    n, cars, seed, steps, W = 4096, 2048, 99, 2000, 32
    out = tmp_path / "run"
    subprocess.run(
        [engine_bin, "run", "--n", str(n), "--cars", str(cars), "--seed", str(seed),
         "--steps", str(steps), "--window", str(W), "--outdir", str(out)],
        check=True, capture_output=True,
    )
    m = io.read_manifest(out / "manifest.json")
    assert m["rule_id"] == 184 and m["n_cells"] == n
    states = io.read_window(out / "window.bin", n, W + 1)
    st = ca.from_seed_exact(n, cars, seed)
    chain = [st]
    for _ in range(steps):
        st = ca.step_rule184(st, n)
        chain.append(st)
    assert chain[-(W + 1):] == states, "window Rust ≠ evolusi Python"
    snap = io.read_snapshot(out / "final.bin")
    assert snap["state"] == chain[-1], "final.bin ≠ akhir rantai Python"
    assert snap["fnv"] == int(m["fnv_final"], 16)

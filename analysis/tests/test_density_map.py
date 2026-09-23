import sys
from pathlib import Path
ROOT = Path("/home/dabroli/Projects/#explorations/0and1")
sys.path.insert(0, str(ROOT / "analysis")); sys.path.insert(0, str(ROOT / "experiments" / "m4"))
from density_map import load_v6_final, saturation
from semesta import ca

def test_load_v6_final():
    F = load_v6_final()
    assert f"{ca.table_fnv(F):016x}".startswith("078681c4")

def test_saturation():
    rows = [{"policy": "u", "level": l, "ratio_free_flow": r} for l, r in
            [(0.1, 1.0), (0.25, 0.99), (0.5, 0.95), (1.0, 0.9)]]
    assert saturation(rows, "u") == 0.5
    rows2 = [{"policy": "u", "level": l, "ratio_free_flow": 1.0} for l in (0.1, 0.25, 0.5, 1.0)]
    assert saturation(rows2, "u") is None

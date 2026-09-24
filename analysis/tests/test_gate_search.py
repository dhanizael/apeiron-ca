"""Gate search — filter aljabar pada tabel sintetis yang diketahui."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m2"))

from gate_search import SZ, gate_configs, idx


def test_gate_configs_synthetic():
    law = [0] * SZ
    law[idx(0, 1, 0)] = 1          # (6) travel
    m, kr = 5, 3
    law[idx(0, m, kr)] = 0         # (1) idle (sudah 0)
    law[idx(0, 1, m)] = 1          # (2) deposit l=0
    law[idx(1, 1, m)] = 1          # (2) deposit l=1
    law[idx(0, m + 1, kr)] = 0     # (3) pasca-1 stabil
    law[idx(0, m + 2, kr)] = 2     # (4) emit
    law[idx(m, kr, 0)] = 0         # (5) penjaga stabil
    cfgs = gate_configs(law)
    assert (m, kr) in cfgs
    # rusak satu kondisi → gagal
    law[idx(0, m, kr)] = 1
    assert (m, kr) not in gate_configs(law)

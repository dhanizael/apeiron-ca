import pytest

from newton import flowrecover
from semesta import ca


def _pairs_from_table(k, table, n, seed, steps):
    cells = ca.from_seed_uniform(n, k, seed)
    out = []
    for _ in range(steps):
        nxt = ca.step_flow(cells, k, table)
        out.append((list(cells), list(nxt)))
        cells = nxt
    return out


def test_field_conservative_telescoping():
    table = ca.clip_table(ca.random_table(2, 3), 2)
    cells = ca.from_seed_uniform(64, 2, 3)
    nxt = ca.step_flow(cells, 2, table)
    f = flowrecover.derive_field(list(cells), list(nxt), 2)
    assert f is not None
    n = len(cells)
    recon = [cells[i] - f[i] + f[(i - 1) % n] for i in range(n)]
    assert recon == list(nxt)


def test_recover_table_exact_k2_full_coverage():
    k, n = 2, 256
    table = ca.clip_table(ca.random_table(k, 9), k)
    pairs = _pairs_from_table(k, table, n, 9, 40)
    rec = flowrecover.recover_table(pairs, k)
    assert rec["unconstrained"] == 0  # init acak menutup semua 64 entri
    assert rec["table"] == table


def test_recover_table_k4_partial_coverage_honest():
    k, n = 4, 256
    table = ca.clip_table(ca.random_table(k, 11), k)
    pairs = _pairs_from_table(k, table, n, 11, 8)
    rec = flowrecover.recover_table(pairs, k)
    assert rec["observed"] > 0
    for idx, v in enumerate(rec["table"]):
        if v is not None:
            assert v == table[idx]  # semua entri teramati HARUS eksak
    assert rec["unconstrained"] == 4096 - rec["observed"]


def test_ambiguous_when_no_zero_flow_edge():
    # semua sel = 7 (k=4): tak ada c=0 / r=15 → konstanta tak terkunci (FM-E)
    cells = [7] * 32
    nxt = [7] * 32
    assert flowrecover.derive_field(cells, nxt, 4) is None


def test_conflict_detected():
    table = ca.clip_table(ca.random_table(2, 5), 2)
    pairs = _pairs_from_table(2, table, 64, 5, 20)
    s, t = pairs[3]
    bad = list(t)
    bad[7] = (bad[7] + 1) % 4
    pairs2 = pairs[:3] + [(s, bad)] + pairs[4:]
    with pytest.raises(ValueError):
        flowrecover.recover_table(pairs2, 2)


def test_unpack_cells_roundtrip():
    cells = ca.from_seed_uniform(32, 4, 2)
    packed = ca.pack_cells(cells, 4)
    assert ca.unpack_cells(packed, 32, 4) == cells


def test_generator_rich_is_slack_rich_vs_poor():
    # hipotesis slack (log 006): generator lama (0..255→clip) = slack-miskin;
    # generator rich (uniform [0,cap]) = slack kaya
    for seed in (1, 2, 3):
        poor = ca.slack_fraction(ca.clip_table(ca.random_table(4, seed), 4), 4)
        rich = ca.slack_fraction(ca.random_table_rich(4, seed), 4)
        assert rich > poor, f"seed={seed}: rich {rich:.3f} vs poor {poor:.3f}"
        assert rich > 0.3


def test_rich_table_respects_capacity():
    k = 4
    t = ca.random_table_rich(k, 7)
    for i, v in enumerate(t):
        assert 0 <= v <= ca.cap_of(i, k)

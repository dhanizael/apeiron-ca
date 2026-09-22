import pytest

from newton import macro, meter, oracle, verify
from semesta import ca


def test_gate_micro_true_and_false():
    n = 128
    s = ca.from_seed_exact(n, 64, 5)
    states = [s, ca.step_rule184(s, n)]
    assert verify.gate_micro(184, states, n)
    assert not verify.gate_micro(110, states, n)


def test_gate_macro():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    assert verify.gate_macro(m, xs, ys)
    assert not verify.gate_macro(m, xs, [y + 0.5 for y in ys])


def test_grade_micro_exact():
    manifest = {"rule_id": 184}
    g = oracle.grade_micro(184, manifest)
    assert g["exact"] is True
    g2 = oracle.grade_micro(110, manifest)
    assert g2["exact"] is False and g2["ground_truth"] == 184


def test_grade_macro_eps():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    ho = [(0.25, min(0.25, 0.75)), (0.75, min(0.75, 0.25))]
    g = oracle.grade_macro(m, ho, eps=0.02)
    assert g["pass"] is True and g["mae"] < 0.02
    g2 = oracle.grade_macro(m, [(0.25, 0.9)], eps=0.02)
    assert g2["pass"] is False


def test_meter_emits_curve():
    curve = meter.log([
        {"t": 1000, "bits": 8, "what": "micro_rule_table"},
        {"t": 1000, "bits": 200, "what": "macro_pw_linear"},
    ])
    assert len(curve) == 2 and curve[0]["t"] == 1000
    assert all(set(e) >= {"t", "bits", "what"} for e in curve)


def test_meter_rejects_malformed():
    with pytest.raises(ValueError):
        meter.log([{"bits": 3}])

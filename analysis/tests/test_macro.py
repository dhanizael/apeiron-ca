from newton import macro
from semesta import ca


def _window(n, cars, seed, warmup, length):
    s = ca.from_seed_exact(n, cars, seed)
    for _ in range(warmup):
        s = ca.step_rule184(s, n)
    out = [s]
    for _ in range(length - 1):
        s = ca.step_rule184(s, n)
        out.append(s)
    return out


def test_flow_free_traffic():
    # ρ = 0.3 < 1/2 → semua mobil jalan → J ≈ ρ
    n = 512
    states = _window(n, cars=153, seed=4, warmup=600, length=300)
    J = macro.measure_flow(states, n)
    assert abs(J - 153 / n) < 0.02


def test_flow_jammed():
    # ρ = 0.8 > 1/2 → J ≈ 1-ρ
    n = 512
    states = _window(n, cars=410, seed=4, warmup=600, length=300)
    J = macro.measure_flow(states, n)
    assert abs(J - (1 - 410 / n)) < 0.02


def test_recovers_fundamental_diagram_exact():
    xs = [0.1 * k for k in range(1, 10)]  # 0.1..0.9
    ys = [min(x, 1 - x) for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    for x in (0.25, 0.55):
        assert abs(macro.predict(m, x) - min(x, 1 - x)) < 1e-6
    assert m["n_segments"] == 2  # MDL: 2 segmen cukup, 3 boros


def test_mdl_prefers_simplest():
    xs = [0.1 * k for k in range(1, 10)]
    ys = [0.5 * x for x in xs]
    m = macro.fit_pw_linear(xs, ys)
    assert m["n_segments"] == 1


def test_holds_out_prediction_within_eps():
    # data terukur (dengan transit finite) → prediksi held-out akurat
    n = 512
    pts = []
    for k in range(1, 10):
        rho = 0.1 * k
        states = _window(n, cars=round(rho * n), seed=17, warmup=600, length=300)
        pts.append((rho, macro.measure_flow(states, n)))
    train = [(x, y) for x, y in pts if x not in (0.2, 0.7)]
    hold = [(x, y) for x, y in pts if x in (0.2, 0.7)]
    m = macro.fit_pw_linear([x for x, _ in train], [y for _, y in train])
    for x, y in hold:
        assert abs(macro.predict(m, x) - y) < 0.02

from semesta import ca


def test_single_car_moves_right():
    n = 64
    s = 1 << 4
    s1 = ca.step_rule184(s, n)
    assert s1 == 1 << 5
    s2 = ca.step_rule184(s1, n)
    assert s2 == 1 << 6


def test_jam_1100_to_1010():
    n = 64
    s = (1 << 10) | (1 << 11)
    t = ca.step_rule184(s, n)
    assert t == (1 << 10) | (1 << 12)


def test_popcount_conserved():
    n = 256
    s = ca.from_seed_exact(n, 100, 9)
    assert s.bit_count() == 100
    for _ in range(300):
        s = ca.step_rule184(s, n)
        assert s.bit_count() == 100


def test_step_rule_agrees_184():
    n = 128
    s = ca.from_seed_exact(n, 60, 3)
    assert ca.step_rule(s, n, 184) == ca.step_rule184(s, n)


def test_rng_mirror_selfconsistent():
    r = ca.Rng(42)
    vals = [r.next_u64() for _ in range(3)]
    r2 = ca.Rng(42)
    assert [r2.next_u64() for _ in range(3)] == vals

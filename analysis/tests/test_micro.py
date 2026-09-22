import pytest

from newton import micro
from semesta import ca


def _stream(rule_id, n=128, cars=64, seed=5, length=20):
    s = ca.from_seed_exact(n, cars, seed)
    out = [s]
    for _ in range(length - 1):
        s = ca.step_rule(s, n, rule_id)
        out.append(s)
    return out


@pytest.mark.parametrize("rule_id", [184, 110, 90, 30, 51])
def test_recovers_known_rule(rule_id):
    states = _stream(rule_id)
    rec = micro.recover(states, 128)
    assert rule_id in rec["verified"]
    assert len(rec["verified"]) >= 1


def test_unique_when_coverage_complete():
    # init acak ρ=0.5 hampir pasti menutup 8 neighborhood dalam 20 pasangan
    states = _stream(184)
    rec = micro.recover(states, 128)
    assert len(rec["candidates"]) == 1
    assert rec["candidates"][0] == 184


def test_ambiguity_reported_honestly():
    # init kosong → hanya neighborhood 000 teramati → banyak aturan konsisten
    n = 64
    states = [0, 0, 0]
    rec = micro.recover(states, n)
    assert len(rec["candidates"]) > 1  # jujur: tidak mengklaim unik


def test_contradiction_detected():
    states = _stream(184, n=64, cars=32)
    bad = states[-1] ^ 1  # corrupt 1 bit
    states_bad = states[:-1] + [bad]
    with pytest.raises(micro.ContradictionError):
        micro.constraints(states_bad, 64)


def test_verified_reproduces_whole_window():
    states = _stream(184, n=256, cars=128, seed=11, length=12)
    rec = micro.recover(states, 256)
    r = rec["verified"][0]
    assert micro.verify_rule(r, states, 256)

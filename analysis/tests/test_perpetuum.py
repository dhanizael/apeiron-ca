"""Perpetuum — definisi terbekukan (amplitudo-ekor, koeksistensi, tak-statis)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "m2"))

from perpetuum import amplitude_last_third, perpetuum_verdict, pop_trajectories


def test_amplitude_last_third():
    # naik-transien lalu datar → amplitudo ekor kecil
    assert amplitude_last_third([0, 5, 100, 100, 100, 100]) < 0.05
    # berdenyut terus → amplitudo ekor besar
    assert amplitude_last_third([50, 90, 50, 90, 50, 90, 50, 90, 50]) > 0.3


def test_perpetuum_verdict():
    # dua spesies berdenyut berlawanan → PERPETUUM + predasi
    n = 60
    states = []
    for i in range(n):
        n1, n2 = (30, 10) if i % 2 == 0 else (10, 30)  # populasi bergantian
        states.append([1] * n1 + [2] * n2)
    trajs, rings = pop_trajectories(states, 2)
    v = perpetuum_verdict(trajs, rings, 2)
    assert v["perpetuum"] is True
    assert v["predation"] is not None and v["predation"]["rho"] <= -0.5
    # konstanta sempurna → bukan perpetuum (statis + amplitudo 0)
    states2 = [[1] * 40 for _ in range(60)]
    trajs2, rings2 = pop_trajectories(states2, 2)
    v2 = perpetuum_verdict(trajs2, rings2, 2)
    assert v2["perpetuum"] is False
    # transien: meledak awal lalu mati → amplitudo ekor kecil → bukan
    states3 = [[2] * 40] + [[0] * 40 for _ in range(59)]
    trajs3, rings3 = pop_trajectories(states3, 2)
    v3 = perpetuum_verdict(trajs3, rings3, 2)
    assert v3["perpetuum"] is False

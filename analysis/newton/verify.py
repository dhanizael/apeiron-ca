"""Gerbang verifier eksak (spec §6.3) — mencegah konfabulasi."""
from newton import macro, micro


def gate_micro(rule_id: int, states: list[int], n: int) -> bool:
    return micro.verify_rule(rule_id, states, n)


def gate_macro(model: dict, xs: list[float], ys: list[float],
               max_mae_train: float = 0.01) -> bool:
    if not xs:
        return False
    mae = sum(abs(macro.predict(model, x) - y) for x, y in zip(xs, ys)) / len(xs)
    return mae <= max_mae_train

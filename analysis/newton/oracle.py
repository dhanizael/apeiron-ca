"""Oracle (spec §7 Tiang 3): grading eksak vs ground truth."""
from newton import macro


def grade_micro(recovered: int, manifest: dict) -> dict:
    truth = manifest["rule_id"]
    return {"recovered": recovered, "ground_truth": truth, "exact": recovered == truth}


def grade_macro(model: dict, holdout: list[tuple[float, float]], eps: float = 0.02) -> dict:
    errs = [abs(macro.predict(model, x) - y) for x, y in holdout]
    mae = sum(errs) / len(errs)
    return {
        "mae": mae,
        "eps": eps,
        "pass": mae < eps,
        "holdout": [
            {"rho": x, "j_measured": y, "j_predicted": macro.predict(model, x)}
            for x, y in holdout
        ],
    }

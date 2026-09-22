"""Pembaca file seam (snapshot/window/manifest) — mirror format engine v1."""
import json
import struct
from pathlib import Path

MAGIC = 0x30444E31304C4D30


def read_manifest(path) -> dict:
    return json.loads(Path(path).read_text())


def read_snapshot(path) -> dict:
    b = Path(path).read_bytes()
    if len(b) < 34:
        raise ValueError("snapshot terlalu pendek")
    magic, version, rule_id, n_cells, step, fnv = struct.unpack_from("<QHIIQQ", b, 0)
    if magic != MAGIC:
        raise ValueError(f"magic salah: {magic:#x}")
    if version != 1:
        raise ValueError(f"versi {version} tidak didukung")
    nw = (n_cells + 63) // 64
    words = struct.unpack_from(f"<{nw}Q", b, 34)
    state = 0
    for w in reversed(words):
        state = (state << 64) | w
    return {"rule_id": rule_id, "n": n_cells, "step": step, "fnv": fnv, "state": state}


def read_window(path, n: int, count: int) -> list[int]:
    b = Path(path).read_bytes()
    nw = (n + 63) // 64
    expect = nw * 8 * count
    if len(b) != expect:
        raise ValueError(f"window.bin {len(b)} byte, harap {expect}")
    states = []
    for s in range(count):
        words = struct.unpack_from(f"<{nw}Q", b, s * nw * 8)
        st = 0
        for w in reversed(words):
            st = (st << 64) | w
        states.append(st)
    return states

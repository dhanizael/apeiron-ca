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
    magic, version = struct.unpack_from("<QH", b, 0)
    if magic != MAGIC:
        raise ValueError(f"magic salah: {magic:#x}")
    if version == 1:
        rule_id, n_cells, step, fnv = struct.unpack_from("<IIQQ", b, 10)
        k = 1
        words_off = 34
    elif version == 2:
        k, _reserved, rule_id, n_cells, step, fnv = struct.unpack_from("<BBIIQQ", b, 10)
        words_off = 36
    else:
        raise ValueError(f"versi {version} tidak didukung")
    if k not in (1, 2, 4, 8):
        raise ValueError(f"k {k} tidak didukung")
    nw = (n_cells * k + 63) // 64
    words = struct.unpack_from(f"<{nw}Q", b, words_off)
    state = 0
    for w in reversed(words):
        state = (state << 64) | w
    return {
        "version": version, "k": k, "rule_id": rule_id, "n": n_cells,
        "step": step, "fnv": fnv, "state": state,
    }


def read_window(path, n: int, count: int, k: int = 1) -> list[int]:
    b = Path(path).read_bytes()
    nw = (n * k + 63) // 64
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

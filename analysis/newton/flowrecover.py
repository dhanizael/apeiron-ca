"""Pemulihan hukum mikro keluarga flow via aljabar teleskop konservasi.

dᵢ = vᵢ − newᵢ = fᵢ − fᵢ₋₁ → medan aliran f terpulihkan via prefix-sum ring,
nyaris pasti hingga SATU konstanta aditif; konstanta terkunci oleh edge
aliran-nol (c=0 atau r=2^k−1 → F=0 pasti, semantik clip). Entri tabel diisi
dari tiap neighborhood teramati; konflik antar-pasangan = kegagalan keras.
Entri tak teramati dilaporkan jujur sebagai None (FM-F); pasangan tanpa edge
aliran-nol dilaporkan ambigu (FM-E) — tidak mengarang.
"""


def _cap(l: int, c: int, r: int, max_cell: int) -> int:
    return min(c, max_cell - r)


def derive_field(cells_prev: list[int], cells_next: list[int], k: int) -> list[int] | None:
    """Medan aliran f per edge dari SATU pasangan state, atau None bila tak
    ada edge aliran-nol untuk mengunci konstanta (FM-E). Raise ValueError
    bila data melanggar konservasi/kapasitas (korup)."""
    n = len(cells_prev)
    max_cell = (1 << k) - 1
    d = [cells_prev[i] - cells_next[i] for i in range(n)]
    if sum(d) != 0:
        raise ValueError("konservasi rusak: Σd ≠ 0")
    refs = [i for i in range(n)
            if cells_prev[i] == 0 or cells_prev[(i + 1) % n] == max_cell]
    if not refs:
        return None  # FM-E: konstanta tak terkunci
    for ref in refs:
        # f_ref = 0; jalan maju: f_i = f_{i−1} + d_i (ring) → f[ref+step] = Σ_{j=1..step} d[ref+j]
        f = [0] * n
        acc = 0
        ok = True
        for step in range(n):
            i = (ref + step) % n
            if step > 0:
                acc += d[i]
            f[i] = acc
            cap_i = _cap(cells_prev[i], cells_prev[i], cells_prev[(i + 1) % n], max_cell)
            if f[i] < 0 or f[i] > cap_i:
                ok = False
                break
        if not ok:
            continue
        # verifikasi akhir: rekonstruksi harus persis
        recon = [cells_prev[i] - f[i] + f[(i - 1) % n] for i in range(n)]
        if recon == list(cells_next):
            return f
    return None


def recover_table(pairs: list[tuple[list[int], list[int]]], k: int) -> dict:
    """Pulihkan tabel F dari pasangan state. Entri tak teramati = None.
    Konflik antar-pasangan → ValueError (kegagalan keras)."""
    size = 1 << (3 * k)
    table: list[int | None] = [None] * size
    observed = 0
    pairs_used = 0
    pairs_ambiguous = 0
    for s, t in pairs:
        f = derive_field(s, t, k)
        if f is None:
            pairs_ambiguous += 1
            continue
        pairs_used += 1
        n = len(s)
        max_cell = (1 << k) - 1
        for i in range(n):
            idx = ((s[(i - 1) % n] & max_cell) << (2 * k)) | ((s[i] & max_cell) << k) | (s[(i + 1) % n] & max_cell)
            val = f[i]
            if table[idx] is None:
                table[idx] = val
                observed += 1
            elif table[idx] != val:
                raise ValueError(f"konflik entri {idx}: {table[idx]} vs {val}")
    return {
        "table": table,
        "observed": observed,
        "unconstrained": size - observed,
        "pairs_used": pairs_used,
        "pairs_ambiguous": pairs_ambiguous,
    }

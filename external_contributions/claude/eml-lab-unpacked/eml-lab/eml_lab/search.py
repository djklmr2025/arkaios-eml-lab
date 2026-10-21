"""Exhaustive (up to a leaf bound) enumeration of REAL-DOMAIN EML expressions, deduplicated by function values.

Definition of the search class (this is what 'exhaustive' means here):
  * trees over leaves {1, x, y} and the node eml(a,b) = exp(a) - ln(b);
  * an expression is kept only if, at EVERY sample point, every ln argument is > 0 (real domain) and the value is finite
    and below 1e250 in float64;
  * two expressions with the same value vector on the sample points are considered the same function; only the first
    (= fewest leaves) is kept. This is exact for minimal-size search IF the sample points separate the functions.
LIMITS (be explicit when reporting results):
  * equivalence is tested on a finite point set (hash of the rounded value vector) -> not a proof; candidates must be
    verified on a dense grid (scripts/06_search.py --verify does this in arbitrary precision);
  * float64 overflow can discard valid formulas that need huge exponentials;
  * enumeration is complete only up to `nmax` leaves (K = 2*nmax-1);
  * the meet-in-the-middle step (find_mitm) only covers top-level splits E(a,b) with BOTH a and b in the tables, i.e. both
    parts <= nmax leaves: for leaves > nmax+1 it is NOT exhaustive.
"""
import numpy as np, time

POINTS = {
    # first pass of the review: too narrow, produced false 'global' formulas (e.g. x-y valid only for y < e)
    'narrow': [(-1.7, 0.6), (0.9, -2.3), (2.4, 1.3), (-0.4, -1.1), (1.1, 0.35), (-3.1, 2.2), (0.3, 0.8)],
    'wide':   [(-4.3, 1.9), (3.7, -2.6), (4.8, 3.9), (-1.9, -4.4), (1.1, 0.35), (-0.4, 0.8), (2.2, -4.9), (-5.1, -0.7)],
}

class Tables:
    def __init__(self, nmax, points='wide', log=print):
        np.seterr(all='ignore')
        self.pts = np.array(POINTS[points]); self.m = len(self.pts); self.nmax = nmax
        self.X, self.Y = self.pts[:, 0], self.pts[:, 1]
        self.R = np.random.default_rng(1).integers(1, 2 ** 61, size=self.m, dtype=np.int64)
        self.vecs = {1: np.array([np.ones(self.m), self.X, self.Y])}
        self.back = {1: [('1',), ('x',), ('y',)]}
        self.hashes = {1: self.H(self.vecs[1])}
        seen = np.sort(self.hashes[1].copy())
        t0 = time.time(); self.counts = {1: 3}
        for n in range(2, nmax + 1):
            newV, newB, newH = [], [], []
            for i in range(1, n):
                j = n - i
                A, B = self.vecs[i], self.vecs[j]
                Bi = np.nonzero((B > 0).all(axis=1))[0]; logB = np.log(B[Bi])
                expA = np.exp(A); Ai = np.nonzero(np.isfinite(expA).all(axis=1))[0]; expA = expA[Ai]
                if len(Ai) == 0 or len(Bi) == 0: continue
                ch = max(1, int(3e6 // (len(Bi) * self.m)))
                for s in range(0, len(Ai), ch):
                    e = expA[s:s + ch]
                    V = (e[:, None, :] - logB[None, :, :]).reshape(-1, self.m)
                    ia = np.repeat(Ai[s:s + ch], len(Bi)); ib = np.tile(Bi, len(e))
                    good = np.isfinite(V).all(axis=1) & (np.abs(V).max(axis=1) < 1e250)
                    V, ia, ib = V[good], ia[good], ib[good]
                    if len(V) == 0: continue
                    h = self.H(V); u, idx = np.unique(h, return_index=True)
                    keep = ~self._has(u, seen); u, idx = u[keep], idx[keep]
                    if newH:
                        q = np.sort(np.concatenate(newH)); k2 = ~self._has(u, q); u, idx = u[k2], idx[k2]
                    if len(u) == 0: continue
                    newV.append(V[idx]); newH.append(u)
                    newB.append(np.stack([np.full(len(idx), i), ia[idx], np.full(len(idx), j), ib[idx]], axis=1))
            if newV:
                self.vecs[n] = np.concatenate(newV); self.hashes[n] = np.concatenate(newH); self.back[n] = np.concatenate(newB)
                seen = np.sort(np.concatenate([seen, self.hashes[n]]))
            else:
                self.vecs[n] = np.zeros((0, self.m)); self.hashes[n] = np.zeros(0, dtype=np.int64); self.back[n] = np.zeros((0, 4), dtype=np.int64)
            self.counts[n] = len(self.vecs[n])
            log(f"n={n:>2} leaves (K={2*n-1:>2}): distinct new functions={len(self.vecs[n]):>10,}  total={len(seen):>10,}  [{time.time()-t0:.0f}s]")
        self.order = {n: np.argsort(self.hashes[n]) for n in self.hashes}
        self.sorted = {n: self.hashes[n][self.order[n]] for n in self.hashes}
    def H(self, V):
        return (np.round(np.sign(V) * np.log1p(np.abs(V)) * 1e7).astype(np.int64) * self.R).sum(axis=1)
    @staticmethod
    def _has(h, arr):
        if len(arr) == 0: return np.zeros(len(h), bool)
        pos = np.searchsorted(arr, h); pos[pos == len(arr)] = 0
        return arr[pos] == h
    def lookup(self, n, h):
        s = self.sorted[n]
        if len(s) == 0: return np.full(len(h), -1)
        pos = np.searchsorted(s, h); pos[pos == len(s)] = 0
        return np.where(s[pos] == h, self.order[n][pos], -1)
    def rpn(self, n, idx):
        if n == 1: return self.back[1][idx][0]
        i, ia, j, ib = self.back[n][idx]
        return self.rpn(int(i), int(ia)) + self.rpn(int(j), int(ib)) + 'E'
    def target(self, name):
        X, Y = self.X, self.Y
        return {'x-y': X - Y, 'x+y': X + Y, '-x': -X, 'x*y': X * Y, 'x/y': X / Y, '1/x': 1 / X, 'x^2': X ** 2,
                '2x': 2 * X, 'x/2': X / 2, '0': np.zeros(self.m), '-1': -np.ones(self.m), '2': 2 * np.ones(self.m)}[name]
    def find(self, name, maxn=None):
        """Return (leaves, rpn, how) of the shortest expression found, or (None, None, note)."""
        T = self.target(name); h = self.H(T[None, :]); maxn = maxn or 2 * self.nmax
        for n in range(1, self.nmax + 1):
            r = self.lookup(n, h)
            if r[0] >= 0: return n, self.rpn(n, r[0]), 'exhaustive'
        for n in range(self.nmax + 1, maxn + 1):
            for i in range(max(1, n - self.nmax), min(self.nmax, n - 1) + 1):
                j = n - i
                if len(self.vecs[i]) <= len(self.vecs[j]):
                    A = self.vecs[i]
                    with np.errstate(all='ignore'):
                        Bv = np.exp(np.exp(A) - T[None, :])
                    good = np.isfinite(np.exp(A)).all(axis=1) & np.isfinite(Bv).all(axis=1) & (Bv > 0).all(axis=1) & (np.abs(Bv).max(axis=1) < 1e250)
                    ia = np.nonzero(good)[0]
                    if len(ia) == 0: continue
                    r = self.lookup(j, self.H(Bv[ia])); hit = np.nonzero(r >= 0)[0]
                    if len(hit): return n, self.rpn(i, int(ia[hit[0]])) + self.rpn(j, int(r[hit[0]])) + 'E', 'meet-in-the-middle (balanced splits only; NOT exhaustive)'
                else:
                    B = self.vecs[j]; ib = np.nonzero((B > 0).all(axis=1))[0]
                    with np.errstate(all='ignore'):
                        arg = T[None, :] + np.log(B[ib])
                    g = (arg > 0).all(axis=1); ib = ib[g]; av = np.log(arg[g])
                    if len(ib) == 0: continue
                    r = self.lookup(i, self.H(av)); hit = np.nonzero(r >= 0)[0]
                    if len(hit): return n, self.rpn(i, int(r[hit[0]])) + self.rpn(j, int(ib[hit[0]])) + 'E', 'meet-in-the-middle (balanced splits only; NOT exhaustive)'
        return None, None, f'not found: none with <= {self.nmax} leaves (exhaustive); none via balanced splits up to {maxn} leaves (partial)'

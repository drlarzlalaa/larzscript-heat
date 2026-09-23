#!/usr/bin/env python3
"""Independent Python reference for heat.lz (provenance and cross-check).

1-D heat equation u_t = D u_xx on [-10, 10] (201 points, dx = 0.1, D = 1), started from a
single-cell spike of unit area. Exact solution for a delta start: a Gaussian of variance 2 D t.

    python3 tools/reference.py run ftcs 0.4 1
    python3 tools/reference.py stability
"""
import math, sys

N, DX, D = 201, 0.1, 1.0
XS = [(i - 100) * DX for i in range(N)]

def start():
    u = [0.0] * N
    u[100] = 1.0 / DX
    return u

def ftcs(u, r):
    n = [0.0] * N
    for i in range(1, N - 1):
        n[i] = u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1])
    return n

def cn(u, r):
    """Crank-Nicolson: solve the tridiagonal system with the Thomas algorithm (zero at both ends)."""
    m = N - 2
    a = -r / 2; b = 1 + r; c = -r / 2
    rhs = [r / 2 * u[i - 1] + (1 - r) * u[i] + r / 2 * u[i + 1] for i in range(1, N - 1)]
    cp, dp = [0.0] * m, [0.0] * m
    cp[0] = c / b; dp[0] = rhs[0] / b
    for i in range(1, m):
        den = b - a * cp[i - 1]
        cp[i] = c / den; dp[i] = (rhs[i] - a * dp[i - 1]) / den
    x = [0.0] * m
    x[-1] = dp[-1]
    for i in range(m - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return [0.0] + x + [0.0]

def simulate(scheme, r, t_end):
    dt = r * DX * DX / D
    steps = round(t_end / dt)
    u = start()
    step = ftcs if scheme == "ftcs" else cn
    for _ in range(steps):
        u = step(u, r)
        if max(abs(v) for v in u) > 1e6: break
    return u, steps * dt, steps

def exact(x, t):
    return math.exp(-x * x / (4 * D * t)) / math.sqrt(4 * math.pi * D * t)

def stats(u, t):
    mass = sum(u) * DX
    var = sum(v * x * x for v, x in zip(u, XS)) * DX / mass if mass else float("nan")
    err = max(abs(v - exact(x, t)) for v, x in zip(u, XS))
    return mass, var, err, max(abs(v) for v in u)

if __name__ == "__main__":
    if sys.argv[1] == "run":
        u, t, steps = simulate(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
        m, v, e, mx = stats(u, t)
        print("steps %d t %.4f mass %.6g variance %.6g (exact %.6g) max_err %.4g max %.4g" % (steps, t, m, v, 2 * D * t, e, mx))
        print(["%.5g" % u[100 + k * 10] for k in range(5)], ["%.5g" % exact(k * 1.0, t) for k in range(5)])
    else:
        for scheme, rs in (("ftcs", (0.1, 0.25, 0.4, 0.5, 0.51, 0.6, 1.0)), ("cn", (0.5, 1, 5, 25, 50))):
            for r in rs:
                u, t, steps = simulate(scheme, r, 1.0)
                m, v, e, mx = stats(u, t)
                print(scheme, r, steps, "%.6g" % m, "%.6g" % v, "%.4g" % e, "%.4g" % mx)

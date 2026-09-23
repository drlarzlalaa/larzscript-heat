# larzscript-heat

Heat diffusion, and when a simulation of it can be trusted, written entirely in [Larzscript](https://github.com/larz-scripter/larzscript). `heat.lz` is one file. Put a spike of heat in the middle of a rod and it spreads into a bell curve whose width grows as the square root of time. Simulating that on a computer is a classic first exercise, and a classic first trap: the obvious method blows up if you take too big a time step, and the "unconditionally stable" method can be stable and still wrong.

```
$ larzscript heat.lz run
ftcs, r = 0.4 (time step 0.004), 250 steps to t = 1
total heat 1, variance 2 (exact 2Dt = 2), largest error 0.000247, peak 0.2818
| x | simulated | exact     |
|---|-----------|-----------|
| 0 | 0.28185   | 0.28209   |
| 1 | 0.21968   | 0.2197    |
| 2 | 0.10393   | 0.10378   |
| 3 | 0.029765  | 0.029733  |
| 4 | 0.0051379 | 0.0051667 |
verdict: accurate

$ larzscript heat.lz stability
| Scheme | r    | Steps | Peak height | Largest error | Verdict               |
|--------|------|-------|-------------|---------------|-----------------------|
| ftcs   | 0.1  | 1000  | 0.282       | 7.07e-05      | accurate              |
| ftcs   | 0.25 | 400   | 0.282       | 8.81e-05      | accurate              |
| ftcs   | 0.4  | 250   | 0.282       | 0.000247      | accurate              |
| ftcs   | 0.5  | 200   | 0.563       | 0.281         | stable but inaccurate |
| ftcs   | 0.51 | 196   | 627         | 627           | blew up               |
| ftcs   | 0.6  | 43    | over 1000   | -             | blew up               |
| ftcs   | 1    | 13    | over 1000   | -             | blew up               |
| cn     | 0.5  | 200   | 0.282       | 0.000176      | accurate              |
| cn     | 1    | 100   | 0.282       | 0.000172      | accurate              |
| cn     | 5    | 20    | 0.328       | 0.046         | stable but inaccurate |
| cn     | 25   | 4     | 5.99        | 5.7           | stable but inaccurate |
| cn     | 50   | 2     | 8.03        | 7.75          | stable but inaccurate |
```

Here `r = D dt / dx^2` measures how big a time step is relative to the grid. Reading the table:

- **Explicit method (`ftcs`) is accurate up to r = 0.4 and unstable just past 1/2.** At r = 0.51 the peak has already grown to 627 (the true peak is 0.282); at r = 0.6 the values pass a million within 43 steps and the run is stopped. Heat spreading can never make a point hotter than its surroundings, so a growing peak is an unmistakable sign the scheme has gone wrong.
- **Exactly r = 0.5 is a curiosity.** The answer stays bounded, but each step averages the two neighbours, so the heat sits only on every *other* grid point: half the points read zero, and the error against the smooth curve is 0.28.
- **Crank-Nicolson (`cn`) never blows up, even at r = 50 - but it stops being right.** The starting spike is not smooth, and a large step lets the answer ring: at r = 5 the peak is 0.328 instead of 0.282, and at r = 50 (two steps!) it is 8.03. "Unconditionally stable" means bounded, not accurate.
- **The explicit scheme's variance is exactly 2Dt whenever it is stable,** and total heat stays 1: each step spreads the heat by exactly `2 D dt`, whatever r is. Crank-Nicolson's variance is 2Dt to within about 1e-5 (a little heat reaches the ends of the rod by t = 2, so `run --scheme=cn --r=1 --t=2` shows 3.99988 and 0.999999). These global quantities look fine even when the answer is wrong (the r = 50 run has variance 1.99998 and a peak of 8.03), which is why the *shape* (the error and the peak) is what tells you when a run has failed.

## Does it check out?

- **The program is right.** `tools/reference.py` is an independent Python implementation of both schemes (using `math.exp` where Larzscript, which has no `exp`, uses a series). The profile, total heat, variance, largest error and peak matched it in every row above, and in extra runs (`ftcs` at r = 0.6 to t = 0.2, `cn` at r = 1 to t = 2, `ftcs` at r = 0.25 to t = 0.5), before the tests were written.
- **The exact solution is the standard one.** From a spike of unit area, the heat becomes a Gaussian with variance 2Dt, and the explicit scheme's own variance grows by exactly that amount each step.

## Install

You need the [Larzscript](https://github.com/larz-scripter/larzscript) interpreter and the `cli`, `args` and `table` packages:

```
curl -fsSL https://raw.githubusercontent.com/larz-scripter/larzscript/main/install.sh | sh
larzscript pkg install cli
larzscript pkg install args
larzscript pkg install table
```

## Commands

| Command | What it does |
|---|---|
| `run [--scheme=ftcs\|cn] [--r=0.4] [--t=1]` | One simulation (D = 1, 201 points, dx = 0.1) against the exact Gaussian: steps, total heat, variance, largest error, peak, a five-point profile and a verdict. |
| `stability` | Both schemes over a range of r, all run to t = 1. |

A run that passes a value of a million is stopped early and reported as having blown up.

## Limits

- **One problem only:** a spike of heat in a 1-D rod with the ends held at zero. Real heat problems have material properties, boundaries and sources.
- **A deliberately harsh start.** A single-cell spike makes the schemes' weaknesses visible; a smooth starting profile would let Crank-Nicolson stay accurate at much larger steps.
- **Only two schemes.** Backward Euler (stable and smooth but only first-order) and higher-order methods are not included.
- **The rod is finite (x from -10 to 10),** which only matters for very long runs; the Gaussian is nowhere near the ends at t <= 10.
- **Accuracy figures depend on the grid** (dx = 0.1 is fixed), not only on r.

## Tests

```
sh tests/run_tests.sh
```

Set `LZ="larzscript /path/to/heat.lz"` to test another copy. CI runs the same suite on every push.

## Licence

MIT (`LICENSE`).

# Temporal HTTP client benchmark

Baseline: `25f3d2ed10bde088ddd2a62c22711bfdfbde695e`. PR source: `48eef0e2adaca911754e85c802b62a17733da225`.

| Scenario | p50 before → after, ms | p95 before → after, ms | Batch before → after, ms | Peak new Python allocations during warm batch, KiB | Warm RSS before → after, MiB | New connections per timed 100 calls |
| --- | --- | --- | --- | --- | --- | --- |
| serial | 9.93 → 1.47 | 23.07 → 3.92 | 1154.66 → 172.88 | 606.7 → 594.6 | 63.51 → 56.76 | 100 → 0 |
| concurrent8 | 52.98 → 16.69 | 90.40 → 38.66 | 1034.86 → 277.27 | 772.9 → 687.0 | 67.23 → 56.90 | 100 → 0 |
| server_close | 8.32 → 2.11 | 15.57 → 4.37 | 971.62 → 253.87 | 575.0 → 592.3 | 63.52 → 56.74 | 100 → 100 |
| https | 5.41 → 1.45 | 9.43 → 3.09 | 604.23 → 185.74 | 854.6 → 591.9 | 57.97 → 57.56 | 100 → 0 |
| model50ms | 60.29 → 51.76 | 75.15 → 53.99 | 6267.66 → 5311.76 | 606.8 → 594.5 | 63.52 → 56.76 | 100 → 0 |

Serial HTTP warm latency falls 85.2%. Even when the server closes each connection, client reuse saves 74.6%. With a simulated 50 ms model delay, total latency falls 14.1%. These are component measurements, not production inference or whole-API measurements.

New allocations during the warm serial batch change only about 2%; the server-close case increases about 3%. Warm serial process RSS falls about 6.8 MiB in this fixture. Native allocation retention and the combined server/client process affect RSS. The traced peaks exclude client allocations retained before tracing begins, so these figures do not establish a reduction in total Python heap size.

## Method

- Five fresh processes per variant and scenario; randomized with seed 705707. The actual baseline and PR `TemporalModelService.predict()` implementations run against the same real loopback HTTP/1.1 server, payload of 10 frame keys, ROI, bearer token, and versioned response. No remote service or database is contacted.
- One cold call plus eight warmup calls; 100 untraced timed calls and a separate 100-call tracemalloc batch per process. Total: 50 fresh processes, 5,000 timed predictions; 10,450 successful calls including warmup and allocation measurements.
- Each cell is the median of the five process summaries. Per-request timings exclude waiting for the concurrency semaphore; batch timings include it. The production validation worker calls serially; concurrency eight is a stress case.
- `server_close` sends Connection: close on every response. This tests loss of connection reuse, as can happen after idle expiry; it does not measure an actual 5-second pause. `model50ms` sleeps 50 ms per request. HTTPS verifies a local test certificate with the same explicitly supplied SSL context in both variants; it measures TLS connections but excludes rebuilding that verification context.
- Warmed connection counts: baseline opens 100 new connections; the PR uses its existing one/eight connections. The server-close case opens 100 in both variants.
- Python 3.11.15, httpx 0.28.1, Linux. The local client factory sets trust_env=False only for this isolated benchmark. Production proxy and TLS settings are preserved.
- RSS is read before tracemalloc, after the timed batch. The Python column measures new allocations after warmup; it includes the loopback server, task batch, and HTTP stack, but excludes retained client allocations. Process peak RSS in raw data includes the traced phase; it is not a pure production memory measurement.
- First-call speedup is not established: serial cold medians were 40.18 ms before / 68.09 ms after, with import/setup noise in fresh processes. The performance claim is restricted to warmed requests.

## Reproduce

See README.md and run_matrix.py in this artifact. The runner uses frozen source snapshots and writes new raw data and an aggregate together, without replacing the original recorded files.

## Validation

- 25 focused tests passed; temporal service statement coverage 100%. One new test verifies client reuse, closure and restart. An existing lifespan test checks shutdown cleanup.
- `lifecycle.py` ran the real application lifespan and local TCP server in three separate event loops; each run reused one connection, closed the client, and reset it before the next loop.
- Full repository ruff lint/format, application/client ty checks and all pre-push hooks passed. The type checker scope matches the repository Makefile; tests are outside that scope.
- A three-way merge tree check combined this branch with database #705, triangulation #706, then uploads #707 without conflicts. The new PR touches four different files.
- Production diff: +10 net lines. Total diff: 37 additions / 8 deletions (+29). Benchmark tools/results stay outside the PR diff.

All 23 GitHub check runs passed at the PR head, including full backend/client tests, end-to-end, builds, typing, lint, pre-commit, and Code Quality. Run: https://github.com/pyronear/pyro-api/actions/runs/37618218743 .

## Recorded peak RSS

Medians over five fresh processes, including the local server and the traced allocation phase.

| Scenario | Baseline MiB | PR MiB | Reduction |
| --- | ---: | ---: | ---: |
| serial | 63.99 | 57.36 | 10.4% |
| concurrent8 | 67.99 | 57.61 | 15.3% |
| server_close | 63.49 | 57.24 | 9.8% |
| https | 58.36 | 57.98 | 0.6% |
| model50ms | 63.99 | 57.36 | 10.4% |

These are component peaks, not full production API worker peaks. The HTTPS case supplies the same verification context in both variants.

## Adversarial review

Three independent reviewers found no correctness regressions. Real TCP probes verified disconnect, timeout, cancellation, invalid JSON, HTTP 503, token changes, and shutdown/restart across event loops. Two P3 improvements were accepted: describe allocation tracing as new allocations after warmup, and publish reproducible evidence. No feature code or extra tests were needed.

# Earlier GitHub Actions feedback

PR: https://github.com/pyronear/pyro-api/pull/712

The backend suite was the last job on 16 of 20 recent PR revisions. Their median complete-feedback time was 296.5 seconds. Two independent runners execute the same backend tests in parallel. Each has its own PostgreSQL and S3 stack. The existing required `pytest` check accepts success only when both shards pass.

## GitHub measurement

| Observed hosted-runner time | Before | After |
|---|---:|---:|
| Backend start to required `pytest` success | 279 s (4m39s) | 223 s (3m43s), 20.07% lower |
| pytest's reported suite time | 156.01 s | max(90.17 s, 79.86 s), 42.20% lower |

Baseline: [successful main run 37810410521](https://github.com/pyronear/pyro-api/actions/runs/37810410521), backend job 113425496752 at commit `9f4c75f2fddfd0d3e922c4d2066ff357fdc63b24`.

Candidate: [successful PR run 37861920091](https://github.com/pyronear/pyro-api/actions/runs/37861920091), shards 113599427379 / 113599427424 and gate 113600472385 at commit `70271fdbdd0aa99159f47569d053c7f120fddd05`. The candidate metric starts when both shard jobs start and ends when the required gate succeeds. It includes duplicated setup, Docker startup, full tests and coverage, cleanup, uploads, optional Telegram check and the gate's queue/runtime.

All 23 PR checks passed. Full feedback, from the earliest workflow creation to the last check completion, took 226 s (3m46s), versus the recent PR median of 296.5 s (4m56.5s). The median comparison is context, not a matched experiment. Both coverage uploads were queued successfully under the same backend flag. The unchanged optional live Telegram check passed its two tests on the remaining shard only.

This is one successful baseline run and one successful candidate run. Hosted-runner speed and queues vary. The candidate includes the subsequent unrelated Mako lockfile update from main; app/test source is identical. The main run at that updated parent had a pre-existing intermittent failure in `test_risk_gate_finish_keeps_due_when_frames_changed`, so the last successful full-suite run is used explicitly. `github-runs.json` contains raw job/step timings, candidate workflows, all checks and calculated comparisons.

## Local validation

| Test and coverage phase | Full suite | Two concurrent shards |
|---|---:|---:|
| Wall time | 133.543 s | 87.939 s (34.15% lower) |
| Passing tests | 680 | 288 + 392 |
| Optional skipped tests | 1 | 0 + 1 |
| Distinct test cases | 681 | 288 + 393 |
| Covered source lines | 2,671 | 2,671 |

Source baseline: `9f4c75f2fddfd0d3e922c4d2066ff357fdc63b24`. All application and test files are identical in the candidate. Its parent also includes the unrelated Mako dependency update `9eb5e8aa013e62070c047e11b7151294584bf9c6`.

Python 3.11.15, baseline locked dependencies, PostgreSQL 15, Moto 5.2.3, full pytest-cov coverage, identical SQL/pytest instrumentation. Both shards run concurrently on the same local host with separate PostgreSQL containers and Moto servers. Separate runners on GitHub also isolate these services.

`elapsed_seconds` measures `pytest.main`, including collection, tests, and coverage generation. It excludes interpreter imports, service startup and the external schema reset. The parallel orchestrator's whole subprocess wall time was 90.553 seconds. These are one baseline and one concurrent trial, not a statistical speed guarantee. Use the actual GitHub job durations for end-to-end feedback, including checkout, Docker startup, coverage uploads and the required gate.

`verify.py` confirms identical test IDs, a disjoint partition, no duplicate test calls, the same fixture hash, and exactly identical combined valid/covered source-line sets. Only the two isolated S3 ports inside parametrized IDs are normalized. New test files automatically join the remaining shard. The separate optional live Telegram check still runs once.

## Reproduction

Use a Python 3.11 environment with the baseline server/test groups installed. Start two disposable PostgreSQL 15 containers named `ci-feedback-postgres` and `ci-feedback-postgres-2`, with database/user `benchmark` and password `benchmark-only`, publishing localhost ports 55435 and 55436. Start Moto 5.2.3 servers on localhost ports 5567 and 5568. The profiler drops and recreates only the disposable benchmark database schema and resets only the selected Moto server before each run.

```sh
python profile.py /path/to/baseline baseline baseline.json
python parallel.py /path/to/candidate
python verify.py
```

Run these scripts from this directory. Both source trees must contain `src/app` and `src/tests`. `parallel.py` uses the active Python interpreter. The selected API files are detections, sequences, camera_proxy and temporal_validation; the other invocation runs `src/tests/` with exactly those files ignored.

Workflow validation: actionlint 1.7.12 over all workflows, dependency-sync check, and shell gate checks for success/failure/cancelled/skipped. No application changes or new repository tests. The feature diff is one workflow, 23 additions / 2 deletions. This uses more runner time to reduce feedback latency.

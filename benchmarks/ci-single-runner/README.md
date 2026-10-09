# Faster backend feedback with less runner usage

PR: https://github.com/pyronear/pyro-api/pull/712

Build the backend image once while PostgreSQL and S3 start. Run two test groups concurrently on that same runner, with separate databases, S3 bucket names and coverage files. Upload coverage while the stack stops. Keep the existing required `pytest` check and all other jobs.

## Hosted-runner measurement

| Backend metric | Original baseline | One runner, shared setup | Improvement |
|---|---:|---:|---:|
| Developer wait: job start to backend check success | 279 s (4m39s) | 193–213 s (3m13s–3m33s) | 66–86 s / 23.66–30.82% less |
| Runner usage: sum of backend job running times | 4.65 runner-min | 3.22–3.55 runner-min | 1.10–1.43 runner-min / 23.66–30.82% less |
| Billed Actions minutes in this public repository | 0 | 0 | Unchanged |

These measurements include checkout, image/service setup, tests, the live Telegram check, coverage upload and cleanup. Both versions use one backend job, so elapsed backend feedback time and summed backend runner time decrease together. Other CI jobs and asynchronous Codecov processing are outside this table. Queueing before the job starts is excluded. Runner minutes are unrounded runtime totals; private-repository quota consumption and charges depend on billing rules, runner prices and included allowances.

Baseline: successful [main run 37810410521](https://github.com/pyronear/pyro-api/actions/runs/37810410521), job `113425496752`, commit `9f4c75f2fddfd0d3e922c4d2066ff357fdc63b24`, 2026-10-08 16:38:47–16:43:26 UTC.

Candidate: successful [PR run 37939066818](https://github.com/pyronear/pyro-api/actions/runs/37939066818), job `113848467551`, commit `9a7bf68444dea7359e4c6694e9fca9dc5143aba6`, 2026-10-09 13:45:00–13:48:13 UTC. All 23 checks passed, including both Codecov checks. Codecov completed at 13:48:45 UTC, after the backend job; 193 seconds is the backend result time, not the time until every external status finishes.

The candidate starts S3/PostgreSQL in 70 seconds while its 50-second image build runs concurrently. Its test steps take 105 and 89 seconds concurrently. Pytest itself reports 97.23 and 82.29 seconds, with 288 and 392 passes plus one optional skip; the baseline reports 156.01 seconds, 680 passes and one skip. The separate live Telegram check passes its two tests in both runs. Raw job/step timestamps and checks are in `github-runs.json`.

A repeat at the exact same candidate commit, [run 37943091015](https://github.com/pyronear/pyro-api/actions/runs/37943091015), job `113862241792`, took 213 seconds on 2026-10-09 14:17:43–14:21:16 UTC. Its test steps took 130 and 111 seconds; all backend cases and both live Telegram tests passed again. All check names have successful conclusions. Raw repeat timestamps, checks and calculated comparisons are in `github-repeat.json`. The table includes both successful candidate measurements, not only the faster run.

Hosted-runner speed and queues vary. This is one successful baseline and two candidate runs, not a guaranteed runtime or a statistical estimate. The candidate parent is main `9eb5e8aa013e62070c047e11b7151294584bf9c6`, which adds an unrelated Mako lockfile update. Application and test source are identical to the successful baseline. The run at that newer parent had a pre-existing intermittent temporal-validation test failure, so the last successful baseline is named explicitly.

## Equivalent-test validation on one host

| Local test and coverage phase | Full suite | Two groups on the same host |
|---|---:|---:|
| Whole subprocess wall time | 240.716 s | 132.223 s (45.07% less) |
| Passing cases | 680 | 288 + 392 |
| Optional skipped cases | 1 | 0 + 1 |
| Distinct cases | 681 | 288 + 393 |
| Covered application lines | 2,944 | 2,944 |

Python 3.11.15, baseline locked server/test dependencies, one PostgreSQL 15 service with default durability settings, and one Moto 5.2.3 S3 service, on the same four-CPU host. The candidate uses separate databases and bucket-name prefixes, matching the isolation used on GitHub. Local Moto uses `eu-west-3` to satisfy its bucket-creation validation; actual GitHub CI retains its existing LocalStack 1.4 service and region. Local timing excludes service/image startup, cleanup and upload; use the hosted table for end-to-end backend feedback and runner consumption.

`verify.py` checks identical outcomes for every exact test ID, no missing/extra/duplicate cases, identical fixture hashes, and exactly equal combined valid and covered source-line sets. New test files automatically join the remaining group. The reporter does not import app modules before coverage starts. This is why its 2,944 covered lines should not be mixed with the earlier SQL-instrumented profiler's 2,671 lines.

## Reproduction

Use a Python 3.11 environment with the baseline locked server/test dependencies installed, and a checkout at `9a7bf68444dea7359e4c6694e9fca9dc5143aba6`. Start a fresh disposable PostgreSQL container and a separate Moto server:

```sh
docker run -d --name ci-feedback-shared-postgres -p 127.0.0.1:55435:5432 \
  -e POSTGRES_USER=benchmark -e POSTGRES_PASSWORD=benchmark-only \
  -e POSTGRES_DB=benchmark postgres:15-alpine
docker exec ci-feedback-shared-postgres pg_isready -U benchmark
uv tool run --from 'moto[s3,server]==5.2.3' moto_server -H 127.0.0.1 -p 5567
```

Once both services are ready, from this directory in another terminal:

```sh
python local.py /path/to/pyro-api
python verify.py
```

The harness resets only that disposable Moto server, creates fresh `baseline`, `api` and `remaining` databases in the named container, runs the full suite, then runs the two groups concurrently. Use a fresh container for each repeat. Profiles, coverage XML and whole-process timings are included here. Stop the owned services after use.

## Rejected experiments and workflow validation

Three test groups took 143.303 seconds locally versus 132.223 for two. Turning off PostgreSQL fsync took 149.602 seconds. Creating the schema once per session took 144.459 seconds locally and 198 seconds for the hosted job. None showed an additional benefit, so none is included in the PR. The earlier two-runner design is also superseded: it duplicated setup and increased runner consumption.

The final feature diff changes one workflow: 29 additions / 13 deletions, 16 net lines. No app, dependency, fixture or test changes. The existing Docker, client and end-to-end jobs still validate application startup and migrations. Session/database resets within the backend suite are unchanged.

GitHub accepted and executed the native `parallel` and `background` syntax successfully. Actionlint 1.7.12 predates that syntax; it passed on the expanded leaf steps in `leaf-steps.yml`, with only parallel wrappers/background keys removed. The dependency-sync check and `git diff --check` passed. Native control flow was validated by the real GitHub run, not by claiming unsupported syntax passed the old parser.

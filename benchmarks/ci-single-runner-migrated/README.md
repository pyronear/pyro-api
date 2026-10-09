# Faster backend feedback against migrated databases

PR: https://github.com/pyronear/pyro-api/pull/712

Build one backend image while PostgreSQL and S3 start, then run two isolated test groups concurrently on one runner. Each container runs `alembic upgrade head` and `python app/db.py` before pytest. Upload coverage while the services stop. Keep all existing required checks and other jobs.

## Hosted measurement

| Backend metric | Original baseline | Final candidate | Improvement |
|---|---:|---:|---:|
| Developer wait: job start through backend check success | 279 s (4m39s) | 203 s (3m23s) | 76 s / 27.24% less |
| Runner usage: sum of backend job running times | 4.65 runner-min | 3.38 runner-min | 1.27 runner-min / 27.24% less |
| Billed Actions minutes in this public repository | 0 | 0 | Unchanged |

These totals include checkout, service/image setup, migrations/bootstrap, pytest, the live Telegram check, coverage upload and cleanup. Both versions use one backend runner, so elapsed feedback and summed runner time decrease together. Other jobs, queueing before job start, and asynchronous Codecov processing are outside the table. Runner usage is unrounded runtime; private billing depends on applicable rules, runner prices and allowances.

Baseline: successful [main run 37810410521](https://github.com/pyronear/pyro-api/actions/runs/37810410521), job `113425496752`, commit `9f4c75f2fddfd0d3e922c4d2066ff357fdc63b24`, 2026-10-08 16:38:47–16:43:26 UTC.

Candidate: successful [PR run 37978737679](https://github.com/pyronear/pyro-api/actions/runs/37978737679), job `113983547254`, commit `cad7e979fbbe478e547d6e4e284eff8ccc51468e`, 2026-10-09 19:13:27–19:16:50 UTC. Both groups apply migrations through `e7a4b9c3d5f2`. Pytest reports 288 passes in 112.47 seconds and 392 passes plus one optional skip in 99.35 seconds. Both separate live Telegram tests pass in 2.03 seconds.

All 23 check names now have successful conclusions. The unchanged end-to-end job initially failed during organization cleanup because an alert still referenced the organization; only that job was rerun, and it passed. Raw initial/retry metadata is included. The retry is outside the backend table and makes the complete CI run longer; 203 seconds describes backend feedback, not the wait for every check in this particular run.

This is one successful baseline and one final candidate trial; hosted-runner speed and queues vary. Application and test source are unchanged. The candidate parent `9eb5e8aa013e62070c047e11b7151294584bf9c6` includes an unrelated Mako lockfile update. Its original main test run had a pre-existing intermittent temporal-validation failure, so the last successful baseline is named explicitly. Earlier measurements in `../ci-single-runner/` omitted migrations for the fresh test databases and are superseded for the final implementation.

## Adversarial review and fix

Three independent reviewers checked isolation, native workflow semantics and benchmark claims. Two found that the fresh shard databases used ORM `create_all` instead of migrations. The production migration adds `ck_sequences_validation_status` and SQL defaults absent from model metadata. Skipping it could let a regression write an invalid status without CI rejecting it.

Both test commands now run migrations and the original bootstrap in their own container before `exec` starts pytest. This preserves the shard database/hostname and forwards pytest arguments and exit status. Only two additional workflow lines were needed. No other actionable review finding remained.

Native parallel groups wait for every child and propagate failures. Background cleanup is awaited before job completion. Coverage files are in the source bind mount, with separate filenames, and survive service removal. Host Bash expands both file selections before they reach `sh -c`; one-off checks verified migration/bootstrap failure stops later commands and pytest's exit code is preserved. Removed runner-level superadmin/PostgreSQL variables were unused: Compose already sets explicit values.

## Equivalent-suite validation

| Local test and coverage phase | Full suite | Two groups on one host |
|---|---:|---:|
| Whole subprocess wall time | 152.573 s | 93.789 s (38.53% less) |
| Passing cases | 680 | 288 + 392 |
| Optional skipped cases | 1 | 0 + 1 |
| Distinct cases | 681 | 288 + 393 |
| Covered application lines | 2,944 | 2,944 |

All three databases are migrated and bootstrapped before timing pytest. Their schema dumps are identical; `verified-schemas.json` records matching hashes and migration heads, and `migrated-schema.sql` contains the schema. Only random pg_dump restrict/unrestrict tokens, if present, are removed for comparison. `verify.py` confirms the exact same per-case outcomes, a disjoint complete partition, no duplicate calls, identical fixture hashes, and exactly equal combined valid/covered source-line sets.

Python 3.11.15, PostgreSQL 15.19 with default durability settings, Moto 5.2.2, one four-CPU host, one shared PostgreSQL service and one shared S3 service. Separate databases and bucket prefixes provide isolation. The Python environment uses baseline locked server/test dependencies (Mako 1.3.12); hosted CI uses the current lock (Mako 1.4.2). Local Moto uses `eu-west-3`; GitHub retains the existing LocalStack 1.4 and region. Local timing covers test subprocesses and coverage only, excluding initialization/services, cleanup and uploads. Use the hosted table for end-to-end backend feedback and runner consumption.

## Reproduction

Use a Python 3.11 environment with the locked server/test groups installed and a checkout at the final candidate commit. Start fresh disposable services:

```sh
docker run -d --name ci-feedback-shared-postgres -p 127.0.0.1:55435:5432 \
  -e POSTGRES_USER=benchmark -e POSTGRES_PASSWORD=benchmark-only \
  -e POSTGRES_DB=benchmark postgres:15-alpine
docker exec ci-feedback-shared-postgres pg_isready -U benchmark
uv tool run --from 'moto[s3,server]==5.2.2' moto_server -H 127.0.0.1 -p 5567
```

Once the services are ready, run from this directory in another terminal:

```sh
python local.py /path/to/pyro-api
python verify.py
```

The harness resets only the disposable Moto server, creates fresh `baseline`, `api` and `remaining` databases, migrates/bootstraps all three, runs the full suite, then runs the two groups concurrently. Use a fresh PostgreSQL container for each repeat and stop owned services afterward. Raw profiles and coverage XML are included.

The feature diff is one workflow: 31 additions / 13 deletions, **18 net lines**. No application, dependency, fixture or test changes. GitHub validates the native `parallel`/`background` syntax. Actionlint 1.7.12 predates those keys; it passes on the equivalent expanded leaf steps in `leaf-steps.yml`. Dependency sync and `git diff --check` also pass.

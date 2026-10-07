# PR #708 benchmark evidence

Frozen source, original raw measurements, and a portable runner for
[pyronear/pyro-api#708](https://github.com/pyronear/pyro-api/pull/708).
The feature branch remains four files, +10 net production lines / +29 net total.

Read REPORT.md for the measurements and limits. These are local component
benchmarks, not production model inference or full API memory measurements.
Tracing starts after warmup, so the Python allocation column measures new
allocations during the batch, not total live Python memory. RSS includes native
allocations, the local server, and the traced batch.

To reproduce, clone the evidence branch and install the baseline dependencies:

```sh
git clone --branch codex/perf-temporal-benchmark-evidence https://github.com/pyronear/pyro-api.git pyro-api-benchmarks
cd pyro-api-benchmarks
uv sync --locked --python 3.11 --only-group server --only-group test
export PYRO_BENCH_REPO="$PWD"
cd benchmarks/temporal-client
openssl req -x509 -newkey rsa:2048 -nodes -keyout benchmark.key -out benchmark.crt -days 1 -subj /CN=127.0.0.1 -addext subjectAltName=IP:127.0.0.1
"$PYRO_BENCH_REPO/.venv/bin/python" run_matrix.py
```

The evidence branch uses the baseline application and frozen predictor snapshots.
It has no effect on the feature PR diff or its merge order.

The matrix runs 50 fresh processes and takes several minutes. It writes
reproduced_results.jsonl and reproduced_results.summary.json together. Existing
reproduced output is overwritten. The original_results.jsonl, original_summary.json
and original_provenance.json files remain the recorded evidence.

The predictor runner and both source snapshots are byte-identical to the
original benchmark. bootstrap.py changes only repository-path discovery. The
portable matrix uses relative file paths and also refreshes its summary.
Dummy settings and a mocked S3 startup probe keep this experiment local.

Baseline commit: 25f3d2ed10bde088ddd2a62c22711bfdfbde695e.
PR source commit: 48eef0e2adaca911754e85c802b62a17733da225.
Python 3.11.15, httpx 0.28.1. All code is under the repository's Apache-2.0 license.

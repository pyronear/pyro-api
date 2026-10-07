# Copyright (C) 2026, Pyronear.
# Licensed under the Apache License 2.0; see LICENSE.
"""Run one fresh-process comparison using the actual TemporalModelService."""

import argparse
import asyncio
import gc
import importlib.util
import json
import math
import resource
import ssl
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from unittest.mock import patch

import bootstrap  # noqa: F401 -- isolated app settings and startup probe
import httpx

from app.core.config import settings


def rss_kib():
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return 0


async def run(args):
    spec = importlib.util.spec_from_file_location("bench_temporal", args.source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    service = module.TemporalModelService()
    real_client = httpx.AsyncClient
    connections = 0
    requests = 0
    tasks = set()
    peers = set()
    delay = .05 if args.scenario == "model50ms" else 0
    concurrency = 8 if args.scenario == "concurrent8" else 1
    close = args.scenario == "server_close"
    tls = args.scenario == "https"
    server_ssl = client_ssl = None
    if tls:
        server_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ssl.load_cert_chain(args.cert, args.key)
        client_ssl = ssl.create_default_context(cafile=args.cert)
    body = json.dumps({"probability": .75, "version": {"api": "1.4.0", "model": "0.1.0"}}).encode()
    response = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)).encode()
    response += (b"\r\nConnection: close" if close else b"") + b"\r\n\r\n" + body

    async def serve(reader, writer):
        nonlocal connections, requests
        connections += 1
        task = asyncio.current_task()
        tasks.add(task)
        peers.add(writer)
        try:
            while True:
                header = await reader.readuntil(b"\r\n\r\n")
                length = next(int(line.split(b":", 1)[1]) for line in header.split(b"\r\n") if line.lower().startswith(b"content-length:"))
                payload = json.loads(await reader.readexactly(length))
                assert payload["bucket"] == "benchmark"
                assert len(payload["frames"]) == 10
                assert b"Authorization: Bearer benchmark-token" in header
                requests += 1
                if delay:
                    await asyncio.sleep(delay)
                writer.write(response)
                await writer.drain()
                if close:
                    break
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass
            peers.discard(writer)
            tasks.discard(task)

    server = await asyncio.start_server(serve, "127.0.0.1", 0, ssl=server_ssl)
    port = server.sockets[0].getsockname()[1]
    settings.TEMPORAL_API_URL = f"{'https' if tls else 'http'}://127.0.0.1:{port}"
    settings.TEMPORAL_API_TOKEN = "benchmark-token"
    frames = [f"camera/2026-10-07/{i:064x}.jpg" for i in range(10)]

    def local_client(**kwargs):
        # Keep proxy configuration out of this loopback experiment. TLS remains verified.
        if tls:
            kwargs["verify"] = client_ssl
        return real_client(trust_env=False, **kwargs)

    async def batch(count):
        sem = asyncio.Semaphore(concurrency)
        samples = []
        async def call():
            async with sem:
                start = time.perf_counter_ns()
                result = await service.predict("benchmark", frames, [.1, .2, .7, .8])
                elapsed = (time.perf_counter_ns() - start) / 1e6
                assert result == module.TemporalPrediction(.75, "0.1.0", "1.4.0")
                samples.append(elapsed)
        start = time.perf_counter_ns()
        await asyncio.gather(*(call() for _ in range(count)))
        return samples, (time.perf_counter_ns() - start) / 1e6

    try:
        with patch.object(module.httpx, "AsyncClient", new=local_client):
            cold, _ = await batch(1)
            await batch(max(8, concurrency))
            await asyncio.sleep(0)
            before_connections = connections
            samples, elapsed = await batch(args.count)
            timed_connections = connections - before_connections
            gc.collect()
            rss_before = rss_kib()
            tracemalloc.start()
            current, _ = tracemalloc.get_traced_memory()
            await batch(args.count)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rss_after = rss_kib()
        samples.sort()
        return {
            "variant": args.variant, "scenario": args.scenario, "count": args.count,
            "concurrency": concurrency, "cold_ms": cold[0], "p50_ms": statistics.median(samples),
            "p95_ms": samples[math.ceil(.95 * len(samples)) - 1], "batch_ms": elapsed,
            "timed_connections": timed_connections, "total_connections": connections,
            "python_peak_kib": (peak - current) / 1024, "rss_before_kib": rss_before,
            "rss_after_kib": rss_after, "process_peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "httpx": httpx.__version__, "python": sys.version.split()[0], "requests": requests,
        }
    finally:
        if hasattr(service, "aclose"):
            await service.aclose()
        server.close()
        await server.wait_closed()
        for writer in list(peers):
            writer.close()
        if tasks:
            await asyncio.gather(*list(tasks), return_exceptions=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--scenario", choices=["serial", "concurrent8", "server_close", "model50ms", "https"], required=True)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--cert")
    parser.add_argument("--key")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args))), flush=True)

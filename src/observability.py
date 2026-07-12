"""
observability.py

Thin tracing layer so every prediction and every LLM call can be inspected
later: how long it took, what went in, what came out, and for LLM calls how
much it cost. This is the kind of thing that separates a notebook from
something you would actually run in production.

It wraps Langfuse if it is installed and configured. If it is not, every call
becomes a no op so nothing breaks and the pipeline runs the same. You should
never have to write "if tracing_enabled" anywhere else in the code.

To turn it on, set these env vars (see .env.example):
    LANGFUSE_PUBLIC_KEY
    LANGFUSE_SECRET_KEY
    LANGFUSE_HOST          (optional, defaults to cloud)

Usage:
    from src.observability import get_tracer
    tracer = get_tracer()
    span = tracer.start("score_territory", {"territory_id": "TER_0048"})
    ... do work ...
    span.end({"retailers_scored": 8, "latency_ms": 142})
"""

import os
import time
import logging

log = logging.getLogger("kshetra.obs")


class _NoOpSpan:
    """Does nothing, returns sensible values, never throws."""
    def __init__(self, name):
        self.name = name
        self._t0 = time.time()

    def end(self, output=None):
        return time.time() - self._t0

    def score(self, name, value):
        pass


class _NoOpTracer:
    """Used when Langfuse is not available. Same interface, zero side effects."""
    enabled = False

    def start(self, name, metadata=None):
        return _NoOpSpan(name)

    def flush(self):
        pass


class _LangfuseSpan:
    def __init__(self, span):
        self._span = span
        self._t0 = time.time()

    def end(self, output=None):
        elapsed = time.time() - self._t0
        try:
            self._span.update(output=output, metadata={"latency_ms": round(elapsed * 1000, 1)})
            self._span.end()
        except Exception as exc:
            log.debug("span end failed: %s", exc)
        return elapsed

    def score(self, name, value):
        try:
            self._span.score(name=name, value=value)
        except Exception as exc:
            log.debug("span score failed: %s", exc)


class _LangfuseTracer:
    enabled = True

    def __init__(self, client):
        self._client = client

    def start(self, name, metadata=None):
        try:
            span = self._client.span(name=name, metadata=metadata or {})
            return _LangfuseSpan(span)
        except Exception as exc:
            log.debug("could not start span: %s", exc)
            return _NoOpSpan(name)

    def flush(self):
        try:
            self._client.flush()
        except Exception:
            pass


_tracer = None


def get_tracer():
    """
    Return a tracer. Langfuse backed if configured and importable, otherwise a
    no op. Cached so you get the same one every time.
    """
    global _tracer
    if _tracer is not None:
        return _tracer

    has_keys = os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")
    if not has_keys:
        log.info("Langfuse keys not set, tracing is a no op")
        _tracer = _NoOpTracer()
        return _tracer

    try:
        from langfuse import Langfuse
        client = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        )
        log.info("Langfuse tracing enabled")
        _tracer = _LangfuseTracer(client)
    except ImportError:
        log.info("langfuse not installed, tracing is a no op (pip install langfuse to enable)")
        _tracer = _NoOpTracer()
    except Exception as exc:
        log.warning("Langfuse init failed (%s), tracing is a no op", exc)
        _tracer = _NoOpTracer()
    return _tracer


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    t = get_tracer()
    print("tracer enabled:", t.enabled)
    s = t.start("demo_span", {"foo": "bar"})
    time.sleep(0.05)
    elapsed = s.end({"result": "ok"})
    print(f"span ran for {elapsed*1000:.1f} ms")
    t.flush()

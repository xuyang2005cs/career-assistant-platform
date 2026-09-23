# Issue Log

## 2026-09-24: Configured package mirror returned no FastAPI release

**Observed:** Installing `requirements.txt` through the machine's configured Tsinghua PyPI mirror failed with “No matching distribution found.”

**Diagnosis:** The mirror returned no available FastAPI versions; the requirement itself was valid.

**Resolution:** Retried the repository-local virtual environment installation with the official PyPI index for that command. Global pip configuration was left unchanged.

## 2026-09-24: Test client emitted an upstream deprecation warning

**Observed:** The first passing test used FastAPI's `TestClient`, and the installed Starlette release warned that its HTTPX compatibility path was deprecated.

**Resolution:** Replaced `TestClient` with HTTPX `ASGITransport` and `AsyncClient`, then reran the suite successfully with no warnings.

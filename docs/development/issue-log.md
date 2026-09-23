# Issue Log

## 2026-09-24: Configured package mirror returned no FastAPI release

**Observed:** Installing `requirements.txt` through the machine's configured Tsinghua PyPI mirror failed with “No matching distribution found.”

**Diagnosis:** The mirror returned no available FastAPI versions; the requirement itself was valid.

**Resolution:** Retried the repository-local virtual environment installation with the official PyPI index for that command. Global pip configuration was left unchanged.

## 2026-09-24: Test client emitted an upstream deprecation warning

**Observed:** The first passing test used FastAPI's `TestClient`, and the installed Starlette release warned that its HTTPX compatibility path was deprecated.

**Resolution:** Replaced `TestClient` with HTTPX `ASGITransport` and `AsyncClient`, then reran the suite successfully with no warnings.

## 2026-09-24: Custom validation body did not match generated OpenAPI

**Observed:** FastAPI initially generated its default `HTTPValidationError` component even though runtime validation failures used the project's custom error envelope.

**Cause:** Replacing the exception handler changes runtime behavior but does not automatically replace each route's documented `422` response model.

**Resolution:** Added explicit `ErrorDetail` and `ErrorResponse` schemas and configured the Job router's `422` response. OpenAPI was regenerated and verified to reference `ErrorResponse`.

## 2026-09-24: SQLite schema inspection command failed due to nested quoting

**Observed:** The first one-line Python command used to read SQLite DDL failed with a syntax error before opening or modifying the database.

**Cause:** PowerShell and Python string quoting were nested incorrectly.

**Resolution:** Reissued a simpler read-only command with PowerShell single-quoted command text and Python double-quoted SQL. The real table and index DDL were then captured successfully.

## 2026-09-24: Browser automation blocked a local `file:` diagram URL

**Observed:** Playwright refused to navigate directly to the local ER diagram HTML file.

**Cause:** The browser automation safety policy blocks the `file:` protocol.

**Resolution:** Served the static diagram temporarily on `127.0.0.1:8765`, captured the verified page, and stopped the temporary server. No schema data was uploaded externally.

## 2026-09-24: Demo acceptance produced a browser console error

**Observed:** The demo rendered and functioned, but the browser console reported a `404` for `/favicon.ico`.

**Cause:** Browsers request a favicon automatically even when a page does not declare one.

**Resolution:** Added a safe inline `data:` favicon to the demo and the reproducible test-evidence page, reran browser acceptance, and confirmed zero console errors and warnings.

## 2026-09-24: Test screenshot risked becoming manually curated evidence

**Observed:** A terminal screenshot would be difficult to reproduce at a stable size and could be mistaken for manually composed output.

**Resolution:** Ran pytest with JUnit XML output, added a small renderer that reads the real counts and duration, and captured that generated page in a real browser. The source XML remains a local ignored build artifact; the screenshot reports the verified 40-test run.

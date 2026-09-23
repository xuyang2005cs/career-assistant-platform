# Technical Decisions

## TD-001: Keep Phase 1 intentionally small

Only a health endpoint is implemented. Empty package boundaries communicate likely areas of responsibility without introducing unused frameworks or abstractions.

## TD-002: Test through ASGI

The health test uses HTTPX `ASGITransport` and `AsyncClient`. This verifies routing, serialization, and the HTTP contract without opening a network port during the test suite.

## TD-003: Use repository-local Git identity

The project uses repository-local author settings so unrelated global Git settings are not overwritten. The commit address is the GitHub-provided noreply form tied to the verified repository owner account.

## TD-004: Use compatible dependency ranges

Direct dependencies use bounded ranges in `requirements.txt`. This keeps Phase 1 simple while preventing accidental upgrades to a future major version. A lock strategy can be introduced when deployment environments are defined.

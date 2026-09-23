# Environment Setup

## Verified Baseline

- Windows development environment
- Python 3.13.14
- Git 2.53.0
- GitHub CLI 2.95.0
- Repository-local Git identity

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
python -m uvicorn app.main:app --reload
```

The `.venv` directory and local `.env` files are ignored by Git. Copy `.env.example` to `.env` only when local configuration is required; never commit the resulting file.

## Package Index Note

During Phase 1, the machine's configured Tsinghua PyPI mirror returned no FastAPI distributions. Installation succeeded without changing global configuration by using the official index for that command:

```powershell
python -m pip install --index-url https://pypi.org/simple -r requirements.txt
```

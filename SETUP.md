# Local Setup

## Python Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the local package with development tools:

```powershell
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Run checks:

```powershell
pytest
ruff check .
```


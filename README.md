
# 4D Rhino Visualization

A real-time visualization system for four-dimensional geometry
using Rhino 7.

## Architecture

- `src/fourd`: Independent 4D mathematical engine
- `rhino`: Rhino 7 integration and rendering
- `tests`: Unit tests
- `examples`: Example 4D geometries

## Development Environment

- Python 3.14
- pytest
- Rhino 7
- IronPython 2.7 (embedded in Rhino 7)

## Getting Started

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run tests:

```powershell
pytest
```

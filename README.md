
# 4D Rhino Visualization

A real-time visualization system for four-dimensional geometry
using Rhino 7.

## Architecture

- `src/fourd`: Independent 4D mathematical engine
- `rhino_app`: Rhino 7 integration and rendering
- `tests`: Unit tests
- `examples`: Example 4D geometries

## Development Environment

- Python 3.14
- pytest
- Rhino 7
- IronPython 2.7 (embedded in Rhino 7)

## Getting Started

### Linux

Set up the virtual environment (creates `.venv` and installs pytest):

```bash
bash scripts/setup_dev.sh
```

Run tests:

```bash
.venv/bin/python -m pytest
```

### Windows

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run tests:

```powershell
pytest
```

## Running in Rhino 7

Run scripts with the `_RunPythonScript` command (or open them in `_EditPythonScript`).
Replace `<repo>` with the path of this repository.

| Script | What it does |
|---|---|
| `<repo>\rhino_app\selfcheck.py` | Checks that the math engine works in Rhino's IronPython 2.7 |
| `<repo>\rhino_app\main.py` | Shows the rotating tesseract. Run again to pause; run once more to rebuild from `CONFIG` and resume |
| `<repo>\rhino_app\clear.py` | Stops the animation and removes the drawing |

Settings (projection, rotation plane, speed, colors, static frame, ...) go in the
`CONFIG` dict at the top of `rhino_app/main.py`. See `DEFAULT_CONFIG` in
`rhino_app/scene_config.py` for every option and its default.

The tesseract is drawn with a DisplayConduit, so no objects are added to the Rhino document.

# -*- coding: utf-8 -*-
"""
main.py가 그린 4D 장면을 멈추고 뷰포트에서 지운다.

실행:  _RunPythonScript <repo>/rhino_app/clear.py
"""
from __future__ import print_function

import os
import sys


def main():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        raise RuntimeError("Run this file as a script (e.g. _RunPythonScript) so __file__ is defined.")
    root = os.path.dirname(here)
    for path in (root, os.path.join(root, "src")):
        if path not in sys.path:
            sys.path.insert(0, path)

    from rhino_app import controller, renderer
    controller.stop_current()
    renderer.clear()
    print("fourd: cleared.")


if __name__ == "__main__":
    main()

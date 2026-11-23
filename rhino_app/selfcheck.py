# -*- coding: utf-8 -*-
"""
수학 엔진(fourd) 호환성 자체 점검.

Rhino 7 (IronPython 2.7)에서 실행:  _RunPythonScript <repo>/rhino_app/selfcheck.py
일반 Python에서도 실행 가능:       python rhino_app/selfcheck.py

pytest 없이 핵심 검증 항목을 직접 실행하고 결과를 출력한다.
"""
from __future__ import print_function

import math
import os
import sys
import traceback


def _setup_paths():
    # repo/src 와 repo 를 import 경로에 추가하고, 이전 실행에서 캐시된 모듈을 지운다
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        raise RuntimeError("Run this file as a script (e.g. _RunPythonScript) so __file__ is defined.")
    root = os.path.dirname(here)
    for path in (root, os.path.join(root, "src")):
        if path not in sys.path:
            sys.path.insert(0, path)
    for name in list(sys.modules):
        if name.split(".")[0] in ("fourd", "rhino_app"):
            del sys.modules[name]


def _close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def _check_tesseract_structure():
    from fourd.polytope import Tesseract
    t = Tesseract()
    assert t.vertex_count() == 16, "vertex count {}".format(t.vertex_count())
    assert t.edge_count() == 32, "edge count {}".format(t.edge_count())
    assert len(set(tuple(v.data) for v in t.vertices)) == 16, "duplicate vertices"
    for a, b in t.edge_segments():
        assert _close(a.distance_to(b), 2.0), "edge length"
    for i in range(16):
        assert len(t.neighbors(i)) == 4, "vertex degree"


def _check_rotation():
    from fourd.geometry import Point4D, Vector4D
    from fourd.matrix import Matrix4D
    from fourd.rotation import Rotation4D
    rotations = [Rotation4D.coordinate_plane(p, 0.7, -0.4) for p in ("xy", "xz", "xw", "yz", "yw", "zw")]
    rotations.append(Rotation4D(Vector4D([1, 2, 3, 4]), Vector4D([-2, 1, 0.5, 3]), 1.1, 0.3))
    identity = Matrix4D.identity()
    p, q = Point4D([1, -2, 0.5, 3]), Point4D([-1, 4, 2, 0])
    for r in rotations:
        m = r.get_rotation_matrix()
        product = m.transpose() * m
        for i in range(4):
            for j in range(4):
                assert _close(product.data[i][j], identity.data[i][j]), "not orthogonal"
        assert _close(m.determinant(), 1.0), "determinant"
        assert _close(r.rotate_point(p).distance_to(r.rotate_point(q)), p.distance_to(q)), "distance"
    full = Rotation4D.coordinate_plane("xw", 2 * math.pi).get_rotation_matrix()
    for i in range(4):
        for j in range(4):
            assert _close(full.data[i][j], identity.data[i][j]), "2*pi rotation"


def _check_projection():
    from fourd.geometry import Point4D
    from fourd.polytope import Polytope
    from fourd.projection import OrthographicProjection, PerspectiveProjection
    assert OrthographicProjection().project_point(Point4D([1, 2, 3, 4])) == (1.0, 2.0, 3.0), "orthographic"
    p = PerspectiveProjection(4).project_point(Point4D([1, 1, 1, 2]))
    assert all(_close(c, 2.0) for c in p), "perspective {}".format(p)
    edge = Polytope([Point4D([0, 0, 0, 0]), Point4D([4, 0, 0, 4])], [(0, 1)])
    s = PerspectiveProjection(4, near=1).project(edge).segments[0]
    assert all(_close(a, b) for a, b in zip(s.end, (12.0, 0.0, 0.0))), "clipping {}".format(s.end)
    assert s.end_clipped and s.end_w == 3.0, "clipping flags"


def _check_scene():
    from fourd.polytope import Tesseract
    from fourd.projection import PerspectiveProjection
    from fourd.scene import RotationMotion, Scene
    scene = Scene(Tesseract(), RotationMotion.coordinate_plane("xw", 0.5), scale=10)
    frame = scene.frame(1.0)
    assert len(frame.lines) == 32 and len(frame.points) == 16, repr(frame)
    scene.projection = PerspectiveProjection(2.5, near=0.05)
    for step in range(50):
        bounds = scene.frame(step * 0.1).bounds()
        assert all(abs(c) < 1e6 for c in bounds[0] + bounds[1]), "perspective bounds"


CHECKS = [
    ("tesseract: 16 vertices, 32 edges, equal edge lengths", _check_tesseract_structure),
    ("rotation: orthogonal, det +1, preserves distance, 2*pi restores", _check_rotation),
    ("projection: reference values and near-plane clipping", _check_projection),
    ("scene: prototype frame and perspective animation", _check_scene),
]


def run():
    print("fourd self-check")
    print("Python {} ({})".format(sys.version.split()[0], sys.platform))
    try:
        _setup_paths()
        import fourd
        print("fourd {} loaded from {}".format(fourd.__version__, os.path.dirname(fourd.__file__)))
    except Exception:
        print("FAIL  could not import fourd")
        traceback.print_exc()
        return False

    failures = 0
    for name, check in CHECKS:
        try:
            check()
            print("PASS  " + name)
        except Exception:
            failures += 1
            print("FAIL  " + name)
            traceback.print_exc()
    if failures:
        print("{} of {} checks FAILED".format(failures, len(CHECKS)))
    else:
        print("All {} checks passed".format(len(CHECKS)))
    return failures == 0


if __name__ == "__main__":
    run()

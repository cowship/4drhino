import math

import pytest

from fourd.geometry import Point4D, Vector4D
from fourd.polytope import Polytope, Tesseract
from fourd.projection import OrthographicProjection, PerspectiveProjection
from fourd.scene import FAR_COLOR, NEAR_COLOR, Frame, RotationMotion, Scene

# scene.py에 정의된 RotationMotion, Frame, Scene 클래스에 대한 테스트 케이스


# 회전 운동 (RotationMotion) 테스트

def test_motion_angle_grows_with_time():
    motion = RotationMotion.coordinate_plane("xw", 0.5, 0.2)
    rotation = motion.at(2.0)
    assert rotation.angle1 == pytest.approx(1.0)
    assert rotation.angle2 == pytest.approx(0.4)


def test_motion_coordinate_plane_matches_rotation():
    motion = RotationMotion.coordinate_plane("xw", 1.0)
    moved = motion.at(math.pi / 2).rotate_vector(Vector4D([1, 0, 0, 0]))
    assert moved.data == pytest.approx([0, 0, 0, 1])


def test_motion_copies_plane_vectors():
    v = Vector4D([1, 0, 0, 0])
    motion = RotationMotion(v, Vector4D([0, 1, 0, 0]), 1.0)
    v.data[0] = 5
    assert motion.plane_vector1.data == [1, 0, 0, 0]


def test_motion_invalid_arguments():
    with pytest.raises(ValueError):
        RotationMotion(Vector4D([1, 0, 0, 0]), Vector4D([2, 0, 0, 0]), 1.0)
    with pytest.raises(TypeError):
        RotationMotion(Vector4D([1, 0, 0, 0]), Vector4D([0, 1, 0, 0]), "1")
    with pytest.raises(ValueError):
        RotationMotion.coordinate_plane("xx", 1.0)
    with pytest.raises(TypeError):
        RotationMotion.coordinate_plane("xy", 1.0).at("1")


# 프레임 (Frame) 테스트

def test_frame_bounds():
    frame = Frame([((0, 0, 0), (1, -2, 3), (0, 0, 0))], [((-1, 5, 0), (0, 0, 0))])
    assert frame.bounds() == ((-1, -2, 0), (1, 5, 3))


def test_empty_frame_bounds():
    assert Frame([], []).bounds() is None


# 장면 (Scene) 테스트

# 첫 프로토타입: 테서랙트 + xw 회전 + 직교 투영 -> 모서리 32개, 꼭짓점 16개
def test_prototype_frame_counts():
    scene = Scene(Tesseract(), RotationMotion.coordinate_plane("xw", 0.5))
    frame = scene.frame(1.0)
    assert len(frame.lines) == 32
    assert len(frame.points) == 16


# 회전이 없으면 시간에 상관없이 같은 프레임
def test_static_scene():
    scene = Scene(Tesseract(), depth_coloring=False)
    assert scene.frame(0).lines == scene.frame(10).lines


# 프레임 좌표가 (중심 기준 회전 -> 투영 -> 배율)과 일치하는지 손계산으로 확인
# t = 1, 속도 pi/2 -> xw 평면 90도: (x, y, z, w) -> (-w, y, z, x) -> 직교 투영 (-w, y, z) -> 배율 10
def test_frame_coordinates_reference():
    scene = Scene(Tesseract(), RotationMotion.coordinate_plane("xw", math.pi / 2), scale=10)
    frame = scene.frame(1.0)
    expected = sorted((-10.0 * v.data[3], 10.0 * v.data[1], 10.0 * v.data[2]) for v in Tesseract().vertices)
    actual = sorted(tuple(round(c, 9) + 0.0 for c in p) for p, _ in frame.points)
    assert actual == expected


# 중심이 원점이 아니어도 제자리(무게중심 기준)에서 회전하는지
def test_rotation_about_centroid():
    center = Point4D([5, -3, 2, 1])
    scene = Scene(Tesseract(center=center), RotationMotion.coordinate_plane("xw", 0.8, 0.3))
    for t in (0.0, 0.7, 2.5):
        posed = scene.posed_polytope(t)
        assert posed.centroid().data == pytest.approx(center.data)
        for a, b in posed.edge_segments():
            assert a.distance_to(b) == pytest.approx(2.0)


# 배율이 모든 좌표에 곱해지는지
def test_scale():
    base = Scene(Tesseract()).frame()
    scaled = Scene(Tesseract(), scale=3).frame()
    for (a1, b1, _), (a2, b2, _) in zip(base.lines, scaled.lines):
        assert a2 == pytest.approx(tuple(3 * c for c in a1))
        assert b2 == pytest.approx(tuple(3 * c for c in b1))


# 깊이 색상: w가 가장 큰 꼭짓점은 NEAR_COLOR, 가장 작은 꼭짓점은 FAR_COLOR 쪽
def test_depth_colors_at_extremes():
    scene = Scene(Tesseract())
    # 테서랙트의 w 범위는 회전과 무관하게 무게중심 w +- 반지름(2) = [-2, 2]
    assert scene.color_at(2.0) == NEAR_COLOR
    assert scene.color_at(-2.0) == FAR_COLOR
    assert scene.color_at(10.0) == NEAR_COLOR   # 범위 밖은 끝값으로 고정
    middle = scene.color_at(0.0)
    for m, f, n in zip(middle, FAR_COLOR, NEAR_COLOR):
        assert m == int(round((f + n) / 2.0))


# 깊이 색상: 꼭짓점의 w가 클수록 NEAR_COLOR에 가깝다
def test_vertex_colors_follow_w():
    scene = Scene(Tesseract())
    colors = {}
    for (p, color), v in zip(scene.frame().points, Tesseract().vertices):
        colors.setdefault(v.data[3], set()).add(color)
    assert len(colors[1.0]) == 1 and len(colors[-1.0]) == 1
    red_index = 0
    assert list(colors[1.0])[0][red_index] > list(colors[-1.0])[0][red_index]


# 깊이 색상을 끄면 모두 단색
def test_depth_coloring_off():
    frame = Scene(Tesseract(), depth_coloring=False, base_color=(1, 2, 3)).frame()
    assert {c for _, _, c in frame.lines} == {(1, 2, 3)}
    assert {c for _, c in frame.points} == {(1, 2, 3)}


# 꼭짓점 표시를 끄면 점이 없다
def test_hide_vertices():
    assert Scene(Tesseract(), show_vertices=False).frame().points == []


# 원근 투영 장면: 근접 평면 뒤의 꼭짓점은 점으로 그리지 않는다
def test_perspective_scene_hides_vertices_behind_near_plane():
    scene = Scene(Tesseract(center=Point4D([0, 0, 0, 3])), projection=PerspectiveProjection(4, near=0.1))
    frame = scene.frame()
    assert len(frame.points) == 8
    assert len(frame.lines) == 20


# 회전하는 원근 장면에서 모든 프레임이 유한한 좌표를 내는지
def test_perspective_animation_is_finite():
    scene = Scene(Tesseract(), RotationMotion.coordinate_plane("xw", 0.9, 0.4),
                  PerspectiveProjection(2.5, near=0.05), scale=10)
    for step in range(100):
        bounds = scene.frame(step * 0.05).bounds()
        assert bounds is not None
        for c in bounds[0] + bounds[1]:
            assert abs(c) < 1e6


# 투영을 나중에 바꿀 수 있다
def test_switch_projection():
    scene = Scene(Tesseract())
    ortho = scene.frame().lines
    scene.projection = PerspectiveProjection(4)
    assert scene.frame().lines != ortho


def test_scene_invalid_arguments():
    with pytest.raises(TypeError):
        Scene("not a polytope")
    with pytest.raises(TypeError):
        Scene(Tesseract(), motion="xw")
    with pytest.raises(TypeError):
        Scene(Tesseract(), projection="ortho")
    with pytest.raises(ValueError):
        Scene(Tesseract(), scale=0)
    with pytest.raises(ValueError):
        Scene(Tesseract(), near_color=(256, 0, 0))
    with pytest.raises(ValueError):
        Scene(Tesseract(), far_color=(0, 0))


def test_empty_polytope_scene():
    frame = Scene(Polytope([], [])).frame()
    assert frame.lines == [] and frame.points == []

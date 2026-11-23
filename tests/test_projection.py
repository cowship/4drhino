import random

import pytest

from fourd.geometry import Point4D, Vector4D
from fourd.polytope import Polytope, Tesseract
from fourd.projection import OrthographicProjection, PerspectiveProjection, ProjectionResult
from fourd.rotation import Rotation4D

# projection.py에 정의된 투영 클래스에 대한 테스트 케이스
# 기준값은 손으로 계산한 값이다.


def segment(a, b):
    return Polytope([Point4D(a), Point4D(b)], [(0, 1)])


def cross3(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def sub3(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def assert_collinear(p, q, r):
    # p, q, r이 한 직선 위에 있는지 (외적이 0)
    for c in cross3(sub3(q, p), sub3(r, p)):
        assert c == pytest.approx(0.0, abs=1e-9)


# 직교 투영 (OrthographicProjection) 테스트

def test_orthographic_drops_w():
    assert OrthographicProjection().project_point(Point4D([1, 2, 3, 4])) == (1.0, 2.0, 3.0)


def test_orthographic_ignores_large_w():
    # 직교 투영은 클리핑이 없다
    assert OrthographicProjection().project_point(Point4D([1, 2, 3, 1000])) == (1.0, 2.0, 3.0)


def test_orthographic_tesseract():
    result = OrthographicProjection().project(Tesseract())
    assert result.segment_count() == 32
    # 투영된 꼭짓점은 3D 정육면체의 꼭짓점 8개로 겹친다
    points = set()
    for s in result.segments:
        points.add(s.start)
        points.add(s.end)
    assert len(points) == 8
    # w 방향 모서리 8개는 길이 0으로 겹친다
    assert sum(1 for s in result.segments if s.start == s.end) == 8


# 원근 투영 (PerspectiveProjection) 테스트

# 기준값: d = 4, (1, 1, 1, 2) -> 배율 4 / (4 - 2) = 2 -> (2, 2, 2)
def test_perspective_reference_point_in_front():
    p = PerspectiveProjection(eye_distance=4).project_point(Point4D([1, 1, 1, 2]))
    assert p == pytest.approx((2, 2, 2))


# 기준값: d = 4, (2, -4, 6, -4) -> 배율 4 / (4 + 4) = 0.5 -> (1, -2, 3)
def test_perspective_reference_point_behind_projection_plane():
    p = PerspectiveProjection(eye_distance=4).project_point(Point4D([2, -4, 6, -4]))
    assert p == pytest.approx((1, -2, 3))


# 기준값: d = 2, (3, 0, -1, 1.5) -> 배율 2 / 0.5 = 4 -> (12, 0, -4)
def test_perspective_reference_point_close_to_eye():
    p = PerspectiveProjection(eye_distance=2).project_point(Point4D([3, 0, -1, 1.5]))
    assert p == pytest.approx((12, 0, -4))


# w = 0 인 점은 직교 투영과 같다
def test_perspective_matches_orthographic_at_w_zero():
    point = Point4D([1.5, -2, 3, 0])
    assert PerspectiveProjection(5).project_point(point) == pytest.approx(
        OrthographicProjection().project_point(point))


# 눈에서 멀어질수록(w가 작을수록) 작게 보인다
def test_perspective_farther_is_smaller():
    proj = PerspectiveProjection(4)
    near = proj.project_point(Point4D([1, 0, 0, 1]))[0]
    middle = proj.project_point(Point4D([1, 0, 0, 0]))[0]
    far = proj.project_point(Point4D([1, 0, 0, -1]))[0]
    assert near > middle > far > 0


# 4D 직선은 원근 투영 후에도 직선이다(꼭짓점만 투영해도 되는 근거)
def test_perspective_preserves_straight_lines():
    proj = PerspectiveProjection(4)
    rng = random.Random(0)
    for _ in range(20):
        a = [rng.uniform(-2, 2) for _ in range(4)]
        b = [rng.uniform(-2, 2) for _ in range(4)]
        t = rng.uniform(0, 1)
        m = [a[k] + t * (b[k] - a[k]) for k in range(4)]
        pa, pb, pm = (proj.project_point(Point4D(x)) for x in (a, b, m))
        assert_collinear(pa, pb, pm)


# 원근 투영된 테서랙트: 깊이 정보와 모서리 수
def test_perspective_tesseract_fully_visible():
    result = PerspectiveProjection(4).project(Tesseract())
    assert result.segment_count() == 32
    assert result.w_range() == (-1.0, 1.0)
    assert not any(s.start_clipped or s.end_clipped for s in result.segments)
    # 안쪽 셀(w = -1)은 배율 0.8, 바깥쪽 셀(w = +1)은 배율 4/3
    for s in result.segments:
        for point, w in ((s.start, s.start_w), (s.end, s.end_w)):
            expected = 4.0 / (4.0 - w)
            assert [abs(c) for c in point] == pytest.approx([expected] * 3)


# 각 선분이 원본 모서리 번호를 유지한다
def test_segments_keep_edge_indices():
    t = Tesseract()
    result = PerspectiveProjection(4).project(t)
    assert [s.edge for s in result.segments] == t.edges


# 근접 평면 클리핑 테스트 (d = 4, near = 1 -> 근접 평면 w = 3)

# 기준값: (0,0,0,0)-(4,0,0,4) 는 t = 3/4 에서 잘려 (3,0,0,3), 투영 배율 4 -> (12,0,0)
def test_clipping_reference_values():
    result = PerspectiveProjection(4, near=1).project(segment([0, 0, 0, 0], [4, 0, 0, 4]))
    assert result.segment_count() == 1
    s = result.segments[0]
    assert s.start == pytest.approx((0, 0, 0))
    assert s.end == pytest.approx((12, 0, 0))
    assert s.start_w == 0
    assert s.end_w == 3.0
    assert (s.start_clipped, s.end_clipped) == (False, True)


# 끝점 순서가 반대여도 같은 결과
def test_clipping_reversed_segment():
    result = PerspectiveProjection(4, near=1).project(segment([4, 0, 0, 4], [0, 0, 0, 0]))
    s = result.segments[0]
    assert s.start == pytest.approx((12, 0, 0))
    assert s.end == pytest.approx((0, 0, 0))
    assert (s.start_clipped, s.end_clipped) == (True, False)
    assert s.start_w == 3.0


# 양 끝점이 모두 근접 평면 뒤에 있으면 그리지 않는다
def test_clipping_drops_segment_fully_behind():
    result = PerspectiveProjection(4, near=1).project(segment([0, 0, 0, 3.5], [1, 1, 1, 10]))
    assert result.segment_count() == 0
    assert result.w_range() is None


# 근접 평면 위의 점은 보인다(경계 포함)
def test_point_on_near_plane_is_visible():
    proj = PerspectiveProjection(4, near=1)
    assert proj.project_point(Point4D([1, 0, 0, 3])) == pytest.approx((4, 0, 0))
    result = proj.project(segment([0, 0, 0, 0], [1, 0, 0, 3]))
    assert not result.segments[0].end_clipped


# 근접 평면 뒤의 점을 직접 투영하면 오류
def test_project_point_behind_near_plane_raises():
    with pytest.raises(ValueError):
        PerspectiveProjection(4, near=1).project_point(Point4D([0, 0, 0, 3.5]))
    with pytest.raises(ValueError):
        PerspectiveProjection(4).project_point(Point4D([0, 0, 0, 4]))


# 잘린 끝점은 원래 직선 위에 있다(투영 후에도)
def test_clipped_endpoint_lies_on_original_line():
    proj = PerspectiveProjection(4, near=0.5)
    a, b = [1, -2, 0.5, -1], [3, 1, 2, 6]
    s = proj.project(segment(a, b)).segments[0]
    # 보이는 구간 안의 다른 점
    m = [a[k] + 0.3 * (b[k] - a[k]) for k in range(4)]
    assert_collinear(s.start, s.end, proj.project_point(Point4D(m)))


# 관찰자 쪽으로 밀어서 일부가 근접 평면을 넘은 테서랙트
# 중심 w = 3 -> 꼭짓점 w는 2 또는 4, 근접 평면 w = 3.9
#   w = 2 셀의 모서리 12개: 그대로
#   w = 4 셀의 모서리 12개: 제거
#   w 방향 모서리 8개: 잘림
def test_tesseract_partially_behind_near_plane():
    t = Tesseract(center=Point4D([0, 0, 0, 3]))
    result = PerspectiveProjection(4, near=0.1).project(t)
    assert result.segment_count() == 20
    clipped = [s for s in result.segments if s.end_clipped or s.start_clipped]
    assert len(clipped) == 8
    for s in clipped:
        w = s.end_w if s.end_clipped else s.start_w
        assert w == pytest.approx(3.9)
    assert result.w_range() == pytest.approx((2.0, 3.9))


# 회전하는 테서랙트에서 투영 좌표가 항상 유한한지
def test_rotating_tesseract_always_finite():
    proj = PerspectiveProjection(2, near=0.05)  # 테서랙트가 눈을 넘나드는 상황
    t = Tesseract()
    clipped_count = 0
    for step in range(60):
        rotation = Rotation4D(Vector4D([1, 0, 0, 1]), Vector4D([0, 1, 1, 0]), step * 0.1, step * 0.07)
        result = proj.project(t.transform(rotation.get_rotation_matrix()))
        for s in result.segments:
            assert s.start_w <= 1.95 + 1e-12 and s.end_w <= 1.95 + 1e-12
            for c in s.start + s.end:
                assert abs(c) < 1e6
            clipped_count += s.start_clipped or s.end_clipped
    # 실제로 클리핑이 일어나는 상황을 검사했는지 확인
    assert clipped_count > 0


# 입력 검증 테스트

def test_perspective_invalid_parameters():
    with pytest.raises(ValueError):
        PerspectiveProjection(0)
    with pytest.raises(ValueError):
        PerspectiveProjection(-1)
    with pytest.raises(ValueError):
        PerspectiveProjection(4, near=0)
    with pytest.raises(TypeError):
        PerspectiveProjection("4")
    with pytest.raises(TypeError):
        PerspectiveProjection(4, near=None)


def test_invalid_input_types():
    for proj in (OrthographicProjection(), PerspectiveProjection()):
        with pytest.raises(TypeError):
            proj.project_point(Vector4D([1, 2, 3, 4]))
        with pytest.raises(TypeError):
            proj.project([Point4D([1, 2, 3, 4])])


def test_result_repr():
    result = OrthographicProjection().project(Tesseract())
    assert isinstance(result, ProjectionResult)
    assert repr(result) == "ProjectionResult(32 segments)"


# 점의 투영 가능 여부 테스트
def test_is_visible():
    proj = PerspectiveProjection(4, near=1)
    assert proj.is_visible(Point4D([0, 0, 0, 3]))
    assert not proj.is_visible(Point4D([0, 0, 0, 3.01]))
    assert OrthographicProjection().is_visible(Point4D([0, 0, 0, 1000]))
    with pytest.raises(TypeError):
        proj.is_visible(Vector4D([0, 0, 0, 0]))

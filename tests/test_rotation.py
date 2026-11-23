import math
import random

import pytest

from fourd.geometry import Point4D, Vector4D
from fourd.matrix import Matrix4D
from fourd.rotation import Rotation4D

# rotation.py에 정의된 Rotation4D 클래스에 대한 테스트 케이스

PLANES = ["xy", "xz", "xw", "yz", "yw", "zw"]


def assert_matrix_close(actual, expected, tol=1e-9):
    for i in range(4):
        for j in range(4):
            assert actual.data[i][j] == pytest.approx(expected.data[i][j], abs=tol)


def assert_vector_close(actual, expected, tol=1e-9):
    for i in range(4):
        assert actual.data[i] == pytest.approx(expected[i], abs=tol)


def random_vector(rng):
    return Vector4D([rng.uniform(-5, 5) for _ in range(4)])


def sample_rotations():
    # 좌표 평면 6개 + 임의 평면, 단순/이중/등각 회전
    rotations = []
    for plane in PLANES:
        rotations.append(Rotation4D.coordinate_plane(plane, 0.7))
        rotations.append(Rotation4D.coordinate_plane(plane, 0.7, -1.3))
    rng = random.Random(0)
    for _ in range(10):
        a, b = random_vector(rng), random_vector(rng)
        rotations.append(Rotation4D(a, b, rng.uniform(-math.pi, math.pi), rng.uniform(-math.pi, math.pi)))
        rotations.append(Rotation4D(a, b, 0.4, 0.4))
    return rotations


# 회전 행렬의 직교성 (R^T R = I) 테스트
@pytest.mark.parametrize("rotation", sample_rotations())
def test_rotation_matrix_is_orthogonal(rotation):
    r = rotation.get_rotation_matrix()
    assert_matrix_close(r.transpose() * r, Matrix4D.identity())


# 회전 행렬의 행렬식이 +1인지 테스트 (반사가 아닌 회전)
@pytest.mark.parametrize("rotation", sample_rotations())
def test_rotation_matrix_determinant_is_one(rotation):
    assert rotation.get_rotation_matrix().determinant() == pytest.approx(1.0)


# 회전이 두 점 사이의 유클리드 거리를 보존하는지 테스트
@pytest.mark.parametrize("rotation", sample_rotations())
def test_rotation_preserves_distance(rotation):
    rng = random.Random(1)
    for _ in range(5):
        p = Point4D([rng.uniform(-5, 5) for _ in range(4)])
        q = Point4D([rng.uniform(-5, 5) for _ in range(4)])
        before = p.distance_to(q)
        after = rotation.rotate_point(p).distance_to(rotation.rotate_point(q))
        assert after == pytest.approx(before)


# 한 평면에서 2π 회전하면 원래 좌표로 돌아오는지 테스트
@pytest.mark.parametrize("plane", PLANES)
def test_full_turn_restores_original(plane):
    rotation = Rotation4D.coordinate_plane(plane, 2 * math.pi)
    assert_matrix_close(rotation.get_rotation_matrix(), Matrix4D.identity())


# 이중 회전에서 두 각도 모두 2π이면 항등 변환인지 테스트
def test_double_full_turn_restores_original():
    rotation = Rotation4D(Vector4D([1, 2, 3, 4]), Vector4D([-2, 1, 0.5, 3]), 2 * math.pi, -2 * math.pi)
    assert_matrix_close(rotation.get_rotation_matrix(), Matrix4D.identity())


# 각도가 0이면 항등 변환인지 테스트
def test_zero_angle_is_identity():
    rotation = Rotation4D(Vector4D([1, 2, 3, 4]), Vector4D([0, 1, 0, 0]), 0, 0)
    assert_matrix_close(rotation.get_rotation_matrix(), Matrix4D.identity())


# xw 평면 90도 회전: x -> w, w -> -x, y와 z는 고정
def test_xw_quarter_turn():
    rotation = Rotation4D.coordinate_plane("xw", math.pi / 2)
    assert_vector_close(rotation.rotate_vector(Vector4D([1, 0, 0, 0])), [0, 0, 0, 1])
    assert_vector_close(rotation.rotate_vector(Vector4D([0, 0, 0, 1])), [-1, 0, 0, 0])
    assert_vector_close(rotation.rotate_vector(Vector4D([0, 1, 0, 0])), [0, 1, 0, 0])
    assert_vector_close(rotation.rotate_vector(Vector4D([0, 0, 1, 0])), [0, 0, 1, 0])


# 좌표 평면 회전이 표준 2차원 회전 행렬과 일치하는지 테스트
@pytest.mark.parametrize("plane", PLANES)
def test_coordinate_plane_matches_textbook_matrix(plane):
    angle = 0.9
    i, j = "xyzw".index(plane[0]), "xyzw".index(plane[1])
    expected = Matrix4D.identity()
    expected.data[i][i] = math.cos(angle)
    expected.data[i][j] = -math.sin(angle)
    expected.data[j][i] = math.sin(angle)
    expected.data[j][j] = math.cos(angle)
    actual = Rotation4D.coordinate_plane(plane, angle).get_rotation_matrix()
    assert_matrix_close(actual, expected)


# 단순 회전에서는 orthogonal complement 위의 벡터가 고정되는지 테스트
def test_simple_rotation_fixes_complement():
    rotation = Rotation4D(Vector4D([1, 1, 0, 0]), Vector4D([0, 1, 1, 1]), 1.1)
    for v in (rotation.v1, rotation.v2):
        assert_vector_close(rotation.rotate_vector(v), v.data)


# 이중 회전: 두 평면이 각자의 각도만큼 회전하는지 테스트
def test_double_rotation_rotates_each_plane():
    angle1, angle2 = 0.5, -1.2
    rotation = Rotation4D(Vector4D([1, 2, 0, 1]), Vector4D([0, 1, 3, -1]), angle1, angle2)
    u1, u2, v1, v2 = rotation.u1, rotation.u2, rotation.v1, rotation.v2

    rotated_u1 = rotation.rotate_vector(u1)
    assert_vector_close(rotated_u1, (math.cos(angle1) * u1 + math.sin(angle1) * u2).data)

    rotated_v1 = rotation.rotate_vector(v1)
    assert_vector_close(rotated_v1, (math.cos(angle2) * v1 + math.sin(angle2) * v2).data)


# 등각 회전: 모든 벡터가 같은 각도만큼 회전하는지 테스트
def test_isoclinic_rotation_rotates_every_vector_by_same_angle():
    angle = 0.8
    rotation = Rotation4D(Vector4D([1, 0, 2, 0]), Vector4D([0, 1, 0, -1]), angle, angle)
    rng = random.Random(2)
    for _ in range(10):
        v = random_vector(rng)
        assert v.angle_to(rotation.rotate_vector(v)) == pytest.approx(angle)


# basis [u1 u2 v1 v2]가 오른손 방향의 orthonormal basis인지 테스트
def test_basis_is_right_handed_orthonormal():
    rng = random.Random(3)
    for _ in range(20):
        rotation = Rotation4D(random_vector(rng), random_vector(rng), 0.3)
        basis = [rotation.u1, rotation.u2, rotation.v1, rotation.v2]
        for i in range(4):
            for j in range(4):
                assert basis[i].dot(basis[j]) == pytest.approx(1.0 if i == j else 0.0, abs=1e-9)
        frame = Matrix4D([b.data for b in basis])
        assert frame.determinant() == pytest.approx(1.0)


# 회전 평면이 같으면 생성 벡터가 달라도 같은 회전인지 테스트
def test_same_plane_same_rotation():
    r1 = Rotation4D(Vector4D([1, 0, 0, 0]), Vector4D([0, 0, 0, 1]), 0.6, 0.2)
    r2 = Rotation4D(Vector4D([2, 0, 0, 0]), Vector4D([3, 0, 0, 5]), 0.6, 0.2)
    assert_matrix_close(r1.get_rotation_matrix(), r2.get_rotation_matrix())


# 반환된 행렬을 수정해도 회전 객체가 변하지 않는지 테스트
def test_get_rotation_matrix_returns_copy():
    rotation = Rotation4D.coordinate_plane("xy", 0.5)
    m = rotation.get_rotation_matrix()
    m.data[0][0] = 100
    assert rotation.get_rotation_matrix().data[0][0] == pytest.approx(math.cos(0.5))


# 회전된 점의 타입이 Point4D인지 테스트
def test_rotate_point_returns_point():
    rotation = Rotation4D.coordinate_plane("xw", 0.5)
    assert isinstance(rotation.rotate_point(Point4D([1, 2, 3, 4])), Point4D)


# 1차 종속인 평면 벡터에 대한 예외 처리 테스트
def test_dependent_plane_vectors_raise():
    with pytest.raises(ValueError):
        Rotation4D(Vector4D([1, 2, 3, 4]), Vector4D([2, 4, 6, 8]), 0.5)


# 0 벡터에 대한 예외 처리 테스트
def test_zero_plane_vector_raises():
    with pytest.raises(ValueError):
        Rotation4D(Vector4D([0, 0, 0, 0]), Vector4D([0, 1, 0, 0]), 0.5)


# 잘못된 타입에 대한 예외 처리 테스트
def test_invalid_types_raise():
    with pytest.raises(TypeError):
        Rotation4D([1, 0, 0, 0], Vector4D([0, 1, 0, 0]), 0.5)
    with pytest.raises(TypeError):
        Rotation4D(Vector4D([1, 0, 0, 0]), Vector4D([0, 1, 0, 0]), "0.5")
    rotation = Rotation4D.coordinate_plane("xy", 0.5)
    with pytest.raises(TypeError):
        rotation.rotate_vector(Point4D([1, 0, 0, 0]))
    with pytest.raises(TypeError):
        rotation.rotate_point(Vector4D([1, 0, 0, 0]))


# 잘못된 좌표 평면 이름에 대한 예외 처리 테스트
@pytest.mark.parametrize("plane", ["xx", "ab", "x", "xyz", ""])
def test_invalid_coordinate_plane_raises(plane):
    with pytest.raises(ValueError):
        Rotation4D.coordinate_plane(plane, 0.5)

import pytest
from fourd.geometry import Point4D, Vector4D

#geometry.py에 정의된 Point4D와 Vector4D 클래스에 대한 테스트 케이스

#점 (Point4D) 클래스 테스트

# 두 점 사이의 거리 계산 테스트
def test_point4d_distance_to():
    a= Point4D(0,0,0,0)
    b= Point4D(1,2,2,4)
    distance = a.distance_to(b)
    assert distance == pytest.approx(5)

# 서로 같은 점 사이의 거리 계산 테스트
def test_point4d_distance_to_same_point():
    a= Point4D(0,0,0,0)
    b= Point4D(0,0,0,0)
    distance = a.distance_to(b)
    assert distance == pytest.approx(0)

# 점과 벡터의 덧셈 테스트
def test_point4d_add_vector4d():
    p = Point4D(1, 2, 3, 4)
    v = Vector4D(2, 3, 4, 5)
    result = p + v
    assert isinstance(result, Point4D)
    assert result.x == 3
    assert result.y == 5
    assert result.z == 7
    assert result.w == 9

# 두 점 사이의 벡터 계산 테스트
def test_point4d_subtract_point4d():
    p1 = Point4D(5, 6, 7, 8)
    p2 = Point4D(1, 2, 3, 4)
    result = p1 - p2
    assert isinstance(result, Vector4D)
    assert result.x == 4
    assert result.y == 4
    assert result.z == 4
    assert result.w == 4

# 벡터 (Vector4D) 클래스 테스트

# 벡터의 크기 계산 테스트
def test_vector4d_magnitude():
    v = Vector4D(1,2,2,4)
    magnitude = v.magnitude()
    assert magnitude == pytest.approx(5)

# 벡터의 크기가 0인 경우 테스트
def test_vector4d_magnitude_zero():
    v = Vector4D(0,0,0,0)
    magnitude = v.magnitude()
    assert magnitude == pytest.approx(0)

# 벡터 정규화 테스트
def test_vector4d_normalize():
    v = Vector4D(0, 3, 0, 4)
    normalized = v.normalize()
    expected_magnitude = 5.0
    assert isinstance(normalized, Vector4D)
    assert normalized.x == pytest.approx(0 / expected_magnitude)
    assert normalized.y == pytest.approx(3 / expected_magnitude)
    assert normalized.z == pytest.approx(0 / expected_magnitude)
    assert normalized.w == pytest.approx(4 / expected_magnitude)

# 벡터 정규화 시 크기가 0인 벡터에 대한 예외 처리 테스트
def test_vector4d_normalize_zero_vector():
    v = Vector4D(0, 0, 0, 0)
    with pytest.raises(ValueError):
        v.normalize()

# 벡터 덧셈 테스트
def test_vector4d_addition():
    v1 = Vector4D(1, 2, 3, 4)
    v2 = Vector4D(4, 3, 2, 1)
    result = v1 + v2
    assert isinstance(result, Vector4D)
    assert result.x == 5
    assert result.y == 5
    assert result.z == 5
    assert result.w == 5

# 벡터 뺄셈 테스트
def test_vector4d_subtraction():
    v1 = Vector4D(4, 3, 2, 1)
    v2 = Vector4D(1, 1, 1, 1)
    result = v1 - v2
    assert isinstance(result, Vector4D)
    assert result.x == 3
    assert result.y == 2
    assert result.z == 1
    assert result.w == 0

# 벡터 스칼라 곱 테스트
def test_vector4d_scalar_multiplication():
    v = Vector4D(1, 2, 3, 4)
    scalar = 3
    result = scalar * v
    assert isinstance(result, Vector4D)
    assert result.x == 3
    assert result.y == 6
    assert result.z == 9
    assert result.w == 12

# 벡터 마이너스 데스트
def test_vector4d_negation():
    v = Vector4D(1, -2, 3, -4)
    result = -v
    assert isinstance(result, Vector4D)
    assert result.x == -1
    assert result.y == 2
    assert result.z == -3
    assert result.w == 4

# 벡터 내적 테스트
def test_vector4d_dot_product():
    v1 = Vector4D(1, 2, 3, 4)
    v2 = Vector4D(4, 3, 2, 1)
    dot_product = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z + v1.w * v2.w
    assert dot_product == 20

# 벡터 사이의 각도 계산 테스트
def test_vector4d_angle_to():
    v1 = Vector4D(1, 0, 0, 0)
    v2 = Vector4D(0, 1, 0, 0)
    angle = v1.angle_to(v2)
    assert angle == pytest.approx(90.0)

# 벡터 사이의 각도 계산 시 동일한 벡터에 대한 테스트
def test_vector4d_angle_to_same_vector():
    v1 = Vector4D(1, 0, 0, 0)
    v2 = Vector4D(1, 0, 0, 0)
    angle = v1.angle_to(v2)
    assert angle == pytest.approx(0.0)

# 벡터 사이의 각도 계산 시 반대 방향 벡터에 대한 테스트
def test_vector4d_angle_to_opposite_vector():
    v1 = Vector4D(1, 0, 0, 0)
    v2 = Vector4D(-1, 0, 0, 0)
    angle = v1.angle_to(v2)
    assert angle == pytest.approx(180.0)

# 벡터 사이의 각도 계산 시 0 벡터에 대한 테스트
def test_vector4d_angle_to_zero_vector():
    v1 = Vector4D(1, 0, 0, 0)
    v2 = Vector4D(0, 0, 0, 0)
    with pytest.raises(ValueError):
        v1.angle_to(v2)
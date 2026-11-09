import pytest
from typing import cast
from fourd.geometry import Vector4D
from fourd.matrix import Matrix4D

#matrix.py에 정의된 Matrix4D 클래스에 대한 테스트 케이스
# 행렬(Matrix4D) 클래스 테스트

# 4x4 행렬 생성 테스트
def test_matrix4d_creation():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    assert isinstance(m, Matrix4D)
    assert m.data == [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트
def test_matrix4d_creation_invalid_type():
    with pytest.raises(TypeError):
        Matrix4D([[1, 2, 3], [4, 5, 6], [7, 8, 9]])  # Not a 4x4 matrix

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트 (내부 원소가 숫자가 아닌 경우)
def test_matrix4d_creation_invalid_inner_type():
    with pytest.raises(TypeError):
        Matrix4D([[1, 2, 3, 4], [5, 6, 7, '8'], [9, 10, 11, 12], [13, 14, 15, 16]])  # Inner element is not a number

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트 (내부 원소가 리스트가 아닌 경우)
def test_matrix4d_creation_invalid_inner_list():
    with pytest.raises(TypeError):
        Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], 'not a list'])  # Inner element is not a list

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트 (내부 원소의 길이가 4가 아닌 경우)
def test_matrix4d_creation_invalid_inner_length():
    with pytest.raises(TypeError):
        Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11], [13, 14, 15, 16]])  # Inner list length is not 4

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트 (바깥 객체가 리스트가 아닌 경우)
def test_matrix4d_creation_invalid_outer_type():
    with pytest.raises(TypeError):
        Matrix4D("not a list")  # Outer object is not a list

# 4x4 행렬 생성 시 잘못된 데이터 타입에 대한 예외 처리 테스트 (바깥 객체의 길이가 4가 아닌 경우)
def test_matrix4d_creation_invalid_outer_length():
    with pytest.raises(TypeError):
        Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])  # Outer list length is not 4

# 항등행렬 생성
def test_matrix4d_identity():
    identity_matrix = Matrix4D.identity()
    expected_identity = Matrix4D([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    assert identity_matrix.data == expected_identity.data

# 4x4 행렬 전치 테스트
def test_matrix4d_transpose():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    transposed = m.transpose()
    expected_transpose = Matrix4D([[1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15], [4, 8, 12, 16]])
    assert transposed.data == expected_transpose.data

# 행렬의 덧셈 테스트
def test_matrix4d_addition():
    m1 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    m2 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    result = m1 + m2
    expected = Matrix4D([[17, 17, 17, 17], [17, 17, 17, 17], [17, 17, 17, 17], [17, 17, 17, 17]])
    assert result.data == expected.data

# 행렬의 뺄셈 테스트
def test_matrix4d_subtraction():
    m1 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    m2 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    result = m1 - m2
    expected = Matrix4D([[15, 13, 11, 9], [7, 5, 3, 1], [-1, -3, -5, -7], [-9, -11, -13, -15]])
    assert result.data == expected.data

# 행렬 곱셈 테스트
def test_matrix4d_multiplication():
    m1 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    m2 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    result = m1 * m2
    expected = Matrix4D([[80, 70, 60, 50], [240, 214, 188, 162], [400, 358, 316, 274], [560, 502, 444, 386]])
    assert result.data == expected.data

# 행렬과 벡터 곱셈 테스트
def test_matrix4d_vector_multiplication():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    v = Vector4D([1, 2, 3, 4])
    result = m * v
    expected = Vector4D([30, 70, 110, 150])
    assert result.data == expected.data

# 행렬 곱셈 시 다른 객체 타입에 대한 예외 처리 테스트
def test_matrix4d_multiplication_invalid_type():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    v = "not a Vector4D"
    with pytest.raises(TypeError):
        m * v

# 행렬 덧셈 시 다른 객체 타입에 대한 예외 처리 테스트
def test_matrix4d_addition_invalid_type():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    v = "not a Matrix4D"
    with pytest.raises(TypeError):
        m + v

# 행렬 뺄셈 시 다른 객체 타입에 대한 예외 처리 테스트
def test_matrix4d_subtraction_invalid_type():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    v = "not a Matrix4D"
    with pytest.raises(TypeError):
        m - v

# 행렬 스칼라 곱셈 시 다른 객체 타입에 대한 예외 처리 테스트
def test_matrix4d_scalar_multiplication_invalid_type():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    v = "not a scalar"
    with pytest.raises(TypeError):
        v * m

# 행렬 스칼라 곱셈 테스트
def test_matrix4d_scalar_multiplication():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    scalar = 2
    result = scalar * m
    expected = Matrix4D([[2, 4, 6, 8], [10, 12, 14, 16], [18, 20, 22, 24], [26, 28, 30, 32]])
    assert result.data == expected.data

# 항등행렬과의 곱셈 테스트
def test_matrix4d_identity_multiplication():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    identity = Matrix4D.identity()
    result = m * identity
    assert result.data == m.data

# 행렬의 곱셈 결합법칙 테스트
def test_matrix4d_associativity():
    m1 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    m2 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    m3 = Matrix4D([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    result1 = (m1 * m2) * m3
    result2 = m1 * (m2 * m3)
    assert result1.data == result2.data

# 행렬의 곱셈 분배법칙 테스트
def test_matrix4d_distributivity():
    m1 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    m2 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    m3 = Matrix4D([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    result1 = m1 * (m2 + m3)
    result2 = (m1 * m2) + (m1 * m3)
    assert result1.data == result2.data

# 행렬의 전치 두 번 테스트
def test_matrix4d_double_transpose():
    m = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    transposed_twice = m.transpose().transpose()
    assert transposed_twice.data == m.data

# 행렬곱의 전치 테스트
def test_matrix4d_transpose_multiplication():
    m1 = Matrix4D([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    m2 = Matrix4D([[16, 15, 14, 13], [12, 11, 10, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    transposed_product = cast(Matrix4D, m1 * m2).transpose()
    product_of_transposes = m2.transpose() * m1.transpose()
    assert transposed_product.data == product_of_transposes.data


# RREF 테스트

def test_rref_already_reduced():
    m = Matrix4D([
        [1, 0, 2, 0],
        [0, 1, 3, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    assert result.data == m.data


def test_rref_row_swap():
    m = Matrix4D([
        [0, 1, 2, 3],
        [1, 0, 0, 0],
        [0, 0, 1, 2],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    expected = [
        [1, 0, 0, 0],
        [0, 1, 0, -1],
        [0, 0, 1, 2],
        [0, 0, 0, 0]
    ]

    assert result.data == expected


def test_rref_zero_matrix():
    m = Matrix4D([
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    assert result.data == m.data


def test_rref_dependent_rows():
    m = Matrix4D([
        [1, 2, 3, 4],
        [2, 4, 6, 8],
        [3, 6, 9, 12],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    expected = [
        [1, 2, 3, 4],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    assert result.data == expected


def test_rref_skip_zero_column():
    m = Matrix4D([
        [0, 1, 2, 3],
        [0, 2, 4, 6],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    expected = [
        [0, 1, 2, 3],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    assert result.data == expected


def test_rref_float_values():
    m = Matrix4D([
        [0.1, 0.2, 0, 0],
        [0.3, 0.6, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0]
    ])

    result = m.rref()

    expected = [
        [1, 2, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    for i in range(4):
        for j in range(4):
            assert abs(result.data[i][j] - expected[i][j]) < 1e-10


def test_rref_preserves_original_matrix():
    m = Matrix4D([
        [1, 2, 3, 4],
        [2, 4, 6, 8],
        [0, 0, 1, 2],
        [0, 0, 0, 0]
    ])

    original = [row[:] for row in m.data]

    result = m.rref()

    assert m.data == original
    assert result is not m


def test_rref_integer_division():
    m = Matrix4D([
        [2, 1, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    result = m.rref()

    expected = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

    for i in range(4):
        for j in range(4):
            assert abs(result.data[i][j] - expected[i][j]) < 1e-10

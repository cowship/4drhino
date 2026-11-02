
from geometry import Vector4D
from copy import deepcopy

class Matrix4D:
    def __init__(self, data):
        if not self.is_4x4_nested_list(data):
            raise TypeError("Data must be a 4x4 nested list.")
        self.data = deepcopy(data)

    #4x4 중첩 리스트인지 확인하는 정적 메서드
    @staticmethod
    def is_4x4_nested_list(arr):
        # 1. 바깥 객체가 리스트이고 길이가 4인지 확인
        if not isinstance(arr, list) or len(arr) != 4:
            return False

        # 2. 각 내부 원소가 리스트이고 길이가 4인지 확인하고 각 내부 원소가 숫자인지 확인
        return all(isinstance(row, list) and len(row) == 4 and all(isinstance(num, (int, float)) for num in row) for row in arr)

    #4x4 행렬을 출력(디버그용)
    def __repr__(self):
        return "Matrix4D({})".format(self.data)

    #행렬의 덧셈, 뺄셈 연산을 정의
    def __add__(self, other):
        if isinstance(other, Matrix4D):
            return Matrix4D([[self.data[i][j] + other.data[i][j] for j in range(4)] for i in range(4)])
        else:
            raise TypeError("Can only add another Matrix4D")

    def __sub__(self, other):
        if isinstance(other, Matrix4D):
            return Matrix4D([[self.data[i][j] - other.data[i][j] for j in range(4)] for i in range(4)])
        else:
            raise TypeError("Can only subtract another Matrix4D")

    #행렬 곱셈 연산을 정의(행렬 * 행렬, 행렬 * 벡터)
    def __mul__(self, other):
        if isinstance(other, Matrix4D):
            result = [[0 for _ in range(4)] for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    result[i][j] = sum(self.data[i][k] * other.data[k][j] for k in range(4))
            return Matrix4D(result)
        elif isinstance(other, Vector4D):
            result = [0 for _ in range(4)]
            for i in range(4):
                result[i] = sum(self.data[i][j] * other.data[j] for j in range(4))
            return Vector4D(*result)
        else:
            raise TypeError("Can only multiply by another Matrix4D or a Vector4D")

    #스칼라 곱 연산을 정의(스칼라 * 행렬)
    def __rmul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Matrix4D([[scalar * self.data[i][j] for j in range(4)] for i in range(4)])
        else:
            raise TypeError("Can only multiply by a scalar (int or float)")

    #행렬 전치 연산을 정의
    def transpose(self):
        return Matrix4D([[self.data[j][i] for j in range(4)] for i in range(4)])

    #항등행렬을 생성하는 정적 메서드
    @staticmethod
    def identity():
        return Matrix4D([[1 if i == j else 0 for j in range(4)] for i in range(4)])
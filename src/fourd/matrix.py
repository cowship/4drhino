
from fourd.geometry import Vector4D
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
            return Vector4D(result)
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

    #항등행렬을 생성
    @staticmethod
    def identity():
        return Matrix4D([[1 if i == j else 0 for j in range(4)] for i in range(4)])

    # 기본행연산
    # 행 교환
    def row_swap(self, row1, row2):
        if not (0 <= row1 < 4) or not (0 <= row2 < 4):
            raise IndexError("Row indices must be between 0 and 3.")
        self.data[row1], self.data[row2] = self.data[row2], self.data[row1]

    # 행 정규화
    def row_normalize(self, row):
        if not (0 <= row < 4):
            raise IndexError("Row index must be between 0 and 3.")

        pivot = None
        for i in range(4):
            if self.data[row][i] != 0:
                pivot = i
                break

        if pivot is None:
            raise ValueError("Cannot normalize a zero row.")

        divisor = self.data[row][pivot]
        self.data[row] = [value / divisor for value in self.data[row]]

    # pivot 열의 모든 원소를 제거
    def row_eliminate(self, row):
        if not (0 <= row < 4):
            raise IndexError("Row indices must be between 0 and 3.")

        pivot = None
        for i in range(4):
            if self.data[row][i] != 0:
                pivot = i
                break

        if pivot is None:
            raise ValueError("Cannot normalize a zero row.")
        
        for target_row in range(4):
            if(target_row == row):
                continue
            factor = self.data[target_row][pivot] / self.data[row][pivot]
            self.data[target_row] = [self.data[target_row][j] - factor * self.data[row][j] for j in range(4)]

    # RREF 생성
    def rref(self):
        for i in range(4):
            self.row_normalize(i)
            self.row_eliminate(i)
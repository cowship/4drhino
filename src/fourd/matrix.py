
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
    def row_normalize(self, row, pivot_col=None, tolerance=1e-12):
        if not (0 <= row < 4):
            raise IndexError("Row index must be between 0 and 3.")

        if pivot_col is None:
            pivot_col = None
            for col in range(4):
                if abs(self.data[row][col]) > tolerance:
                    pivot_col = col
                    break

        if pivot_col is None:
            raise ValueError("Cannot normalize a zero row.")

        if not (0 <= pivot_col < 4):
            raise IndexError("Column index must be between 0 and 3.")

        divisor = self.data[row][pivot_col]

        if abs(divisor) <= tolerance:
            raise ValueError("Pivot is too close to zero.")

        self.data[row] = [
            float(value) / divisor for value in self.data[row]
        ]

        # 부동소수점 오차 제거
        for col in range(4):
            if abs(self.data[row][col]) <= tolerance:
                self.data[row][col] = 0.0

    # 지정한 pivot 열의 다른 행 원소 제거
    def row_eliminate(self, row, pivot_col=None, tolerance=1e-12):
        if not (0 <= row < 4):
            raise IndexError("Row index must be between 0 and 3.")

        if pivot_col is None:
            pivot_col = None
            for col in range(4):
                if abs(self.data[row][col]) > tolerance:
                    pivot_col = col
                    break

        if pivot_col is None:
            raise ValueError("Cannot eliminate using a zero row.")

        if not (0 <= pivot_col < 4):
            raise IndexError("Column index must be between 0 and 3.")

        pivot = self.data[row][pivot_col]

        if abs(pivot) <= tolerance:
            raise ValueError("Pivot is too close to zero.")

        for target_row in range(4):
            if target_row == row:
                continue

            factor = float(self.data[target_row][pivot_col]) / pivot

            if abs(factor) <= tolerance:
                self.data[target_row][pivot_col] = 0.0
                continue

            self.data[target_row] = [
                self.data[target_row][col] -
                factor * self.data[row][col]
                for col in range(4)
            ]

            # 계산 과정에서 발생한 작은 오차 제거
            for col in range(4):
                if abs(self.data[target_row][col]) <= tolerance:
                    self.data[target_row][col] = 0.0

    # Reduced Row Echelon Form 생성
    def rref(self, epsilon=1e-12):
        if not isinstance(epsilon, (int, float)) or epsilon < 0:
            raise ValueError("Epsilon must be a non-negative number.")

        # 원본 행렬 보존
        result = Matrix4D(self.data)

        # 행렬의 크기에 비례하는 허용 오차
        scale = max(
            abs(value)
            for row in result.data
            for value in row
        )
        tolerance = epsilon * scale

        pivot_row = 0

        # 열을 왼쪽에서 오른쪽으로 탐색
        for pivot_col in range(4):

            if pivot_row >= 4:
                break

            # 현재 열에서 가장 큰 절댓값을 가진 원소 탐색
            best_row = None
            best_value = 0.0

            for row in range(pivot_row, 4):
                value = abs(result.data[row][pivot_col])

                if value > best_value:
                    best_value = value
                    best_row = row

            # 현재 열에 유효한 pivot이 없으면 다음 열로 이동
            if best_row is None or best_value <= tolerance:
                continue

            # Pivot 행을 현재 위치로 이동
            result.row_swap(pivot_row, best_row)

            # Pivot을 1로 정규화
            result.row_normalize(
                pivot_row,
                pivot_col,
                tolerance
            )

            # Pivot 열의 나머지 원소 제거
            result.row_eliminate(
                pivot_row,
                pivot_col,
                tolerance
            )

            pivot_row += 1

        return result

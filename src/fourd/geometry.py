
import math
from copy import deepcopy

#4차원에서의 점
class Point4D:
    @staticmethod
    def is_4list(arr):
        # 리스트이고 길이가 4인지 확인
        if not isinstance(arr, list) or len(arr) != 4:
            return False
        # 각 내부 원소가 숫자인지 확인
        return all(isinstance(num, (int, float)) for num in arr)

    #4개의 숫자로 좌표를 생성
    def __init__(self, data):
        if not self.is_4list(data):
            raise TypeError("Data must be a 4-element list of numbers.")
        self.data = deepcopy(data)

    #4개의 좌표를 출력(디버그용)
    def __repr__(self):
        return "Point4D({})".format(self.data)
        
    #두 점 사이의 거리를 계산
    def distance_to(self, other):
        if not isinstance(other, Point4D):
            raise TypeError("The other object must be an instance of Point4D.")
        return ((self.data[0] - other.data[0]) ** 2 + 
                (self.data[1] - other.data[1]) ** 2 + 
                (self.data[2] - other.data[2]) ** 2 + 
                (self.data[3] - other.data[3]) ** 2) ** 0.5

    #점에 벡터를 더하여 새로운 점을 생성(점+벡터 순서)
    def __add__(self, vector):
        if not isinstance(vector, Vector4D):
            raise TypeError("The vector must be an instance of Vector4D.")
        return Point4D([self.data[0] + vector.data[0], self.data[1] + vector.data[1], self.data[2] + vector.data[2], self.data[3] + vector.data[3]])

    #두 점 사이의 벡터를 계산
    def __sub__(self, other):
        if not isinstance(other, Point4D):
            raise TypeError("The other object must be an instance of Point4D.")
        return Vector4D([self.data[0] - other.data[0], self.data[1] - other.data[1], self.data[2] - other.data[2], self.data[3] - other.data[3]])


#4차원에서의 벡터
class Vector4D:
    @staticmethod
    def is_4list(arr):
        # 리스트이고 길이가 4인지 확인
        if not isinstance(arr, list) or len(arr) != 4:
            return False
        # 각 내부 원소가 숫자인지 확인
        return all(isinstance(num, (int, float)) for num in arr)

    #4개의 숫자로 벡터를 생성
    def __init__(self, data):
        if not self.is_4list(data):
            raise TypeError("Data must be a 4-element list of numbers.")
        self.data = deepcopy(data)

    #4개의 성분을 출력(디버그용)
    def __repr__(self):
        return "Vector4D({})".format(self.data)
        
    #벡터의 크기를 계산
    def magnitude(self):
        return (self.data[0] ** 2 + self.data[1] ** 2 + self.data[2] ** 2 + self.data[3] ** 2) ** 0.5

    #벡터를 정규화하여 단위 벡터를 반환
    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector.")
        return Vector4D([self.data[0] / mag, self.data[1] / mag, self.data[2] / mag, self.data[3] / mag])

    #두 벡터를 더하거나 빼는 연산을 수행
    def __add__(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return Vector4D([self.data[0] + other.data[0], self.data[1] + other.data[1], self.data[2] + other.data[2], self.data[3] + other.data[3]])

    def __sub__(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return Vector4D([self.data[0] - other.data[0], self.data[1] - other.data[1], self.data[2] - other.data[2], self.data[3] - other.data[3]])

    #벡터의 스칼라 곱을 계산(스칼라*벡터 순서)
    def __rmul__(self, scalar):
        return Vector4D([self.data[0] * scalar, self.data[1] * scalar, self.data[2] * scalar, self.data[3] * scalar])

    #반대 방향 벡터
    def __neg__(self):
        return Vector4D([-self.data[0], -self.data[1], -self.data[2], -self.data[3]])

    #벡터의 내적
    def dot(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return self.data[0] * other.data[0] + self.data[1] * other.data[1] + self.data[2] * other.data[2] + self.data[3] * other.data[3]

    #두 벡터 사이의 각도를 계산(도 단위)
    def angle_to(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        dot_product = self.dot(other)
        mag_self = self.magnitude()
        mag_other = other.magnitude()
        if mag_self == 0 or mag_other == 0:
            raise ValueError("Cannot calculate the angle with a zero vector.")
        cos_theta = dot_product / (mag_self * mag_other)
        # Clamp the value to avoid numerical issues(부동소숫점 오차를 방지하기 위해 값 제한)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        return math.degrees(math.acos(cos_theta))
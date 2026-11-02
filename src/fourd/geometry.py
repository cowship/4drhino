
import math

#4차원에서의 점
class Point4D:
    #4개의 숫자로 좌표를 생성
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    #4개의 좌표를 출력(디버그용)
    def __repr__(self):
        return "Point4D({}, {}, {}, {})".format(
            self.x, self.y, self.z, self.w
        )
        
    #두 점 사이의 거리를 계산
    def distance_to(self, other):
        if not isinstance(other, Point4D):
            raise TypeError("The other object must be an instance of Point4D.")
        return ((self.x - other.x) ** 2 + 
                (self.y - other.y) ** 2 + 
                (self.z - other.z) ** 2 + 
                (self.w - other.w) ** 2) ** 0.5

    #점에 벡터를 더하여 새로운 점을 생성(점+벡터 순서)
    def __add__(self, vector):
        if not isinstance(vector, Vector4D):
            raise TypeError("The vector must be an instance of Vector4D.")
        return Point4D(self.x + vector.x, self.y + vector.y, self.z + vector.z, self.w + vector.w)

    #두 점 사이의 벡터를 계산
    def __sub__(self, other):
        if not isinstance(other, Point4D):
            raise TypeError("The other object must be an instance of Point4D.")
        return Vector4D(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)


#4차원에서의 벡터
class Vector4D:
    #4개의 숫자로 벡터를 생성
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    #4개의 성분을 출력(디버그용)
    def __repr__(self):
        return "Vector4D({}, {}, {}, {})".format(
            self.x, self.y, self.z, self.w
        )
        
    #벡터의 크기를 계산
    def magnitude(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2) ** 0.5

    #벡터를 정규화하여 단위 벡터를 반환
    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector.")
        return Vector4D(self.x / mag, self.y / mag, self.z / mag, self.w / mag)

    #두 벡터를 더하거나 빼는 연산을 수행
    def __add__(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return Vector4D(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return Vector4D(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    #벡터의 스칼라 곱을 계산(스칼라*벡터 순서)
    def __rmul__(self, scalar):
        return Vector4D(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)

    #반대 방향 벡터
    def __neg__(self):
        return Vector4D(-self.x, -self.y, -self.z, -self.w)

    #벡터의 내적
    def dot(self, other):
        if not isinstance(other, Vector4D):
            raise TypeError("The other object must be an instance of Vector4D.")
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

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
#4차원에서의 점
class Point4D:
    #4개의 숫자로 좌표를 생성
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    #4개의 좌표를 출력(디버그용이라함)
    def __repr__(self):
        return f"Point4D({self.x}, {self.y}, {self.z}, {self.w})"

    #두 점 사이의 거리를 계산
    def distance_to(self, other):
        if not isinstance(other, Point4D):
            raise ValueError("The other object must be an instance of Point4D.")
        return ((self.x - other.x) ** 2 + 
                (self.y - other.y) ** 2 + 
                (self.z - other.z) ** 2 + 
                (self.w - other.w) ** 2) ** 0.5

    #점에 벡터를 더하여 새로운 점을 생성
    def addVector(self, vector):
        if not isinstance(vector, Vector4D):
            raise ValueError("The vector must be an instance of Vector4D.")
        return Point4D(self.x + vector.x, self.y + vector.y, self.z + vector.z, self.w + vector.w)

    #두 점 사이의 벡터를 계산
    def makeVector(self, other):
        if not isinstance(other, Point4D):
            raise ValueError("The other object must be an instance of Point4D.")
        return Vector4D(other.x - self.x, other.y - self.y, other.z - self.z, other.w - self.w)


#4차원에서의 벡터
class Vector4D:
    #4개의 숫자로 벡터를 생성
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    #4개의 성분을 출력(디버그용이라함)
    def __repr__(self):
        return f"Vector4D({self.x}, {self.y}, {self.z}, {self.w})"

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
    def add(self, other):
        if not isinstance(other, Vector4D):
            raise ValueError("The other object must be an instance of Vector4D.")
        return Vector4D(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def subtract(self, other):
        if not isinstance(other, Vector4D):
            raise ValueError("The other object must be an instance of Vector4D.")
        return Vector4D(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    #벡터의 스칼라 곱을 계산
    def scale(self, scalar):
        return Vector4D(self.x * scalar, self.y * scalar, self.z * scalar, self.w * scalar)
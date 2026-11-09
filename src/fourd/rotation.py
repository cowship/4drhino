
from .matrix import Matrix4D
from .geometry import Vector4D
import math
from typing import cast

class Rotation4D:
    # rotation plane 1개와 rotationa angle 2개를 통해 임의의 4차원 회전 행렬을 생성
    def __init__(self, axis1, axis2, angle1, angle2):
        if axis1 == axis2:
            raise ValueError("Axes must be independent.")
        self.axis1 = axis1
        self.axis2 = axis2
        self.angle1 = angle1
        self.angle2 = angle2

    # vector 2개를 통해 rotation plane의 orthonormal basis를 생성
    @staticmethod
    def gram_schmidt(vector1, vector2):
        # vector1를 정규화
        u1 = vector1.normalize()

        # vector2를 u1에 직교하도록 정규화
        proj = vector2.dot(u1)
        u2 = Vector4D([vector2.data[i] - proj * u1.data[i] for i in range(4)]).normalize()
        return u1, u2

    # Gaussian elimination을 통해 rotation plane의 orthogonal complement의 orthonormal basis를 생성
    @staticmethod
    def orthogonal_complement(vector1, vector2):
        # u1과 u2를 행렬로 만들어서 Gaussian elimination을 수행
        matrix = Matrix4D([vector1.data, vector2.data, [0, 0, 0, 0], [0, 0, 0, 0]])

        # Gaussian elimination을 통해 orthogonal complement를 찾음
        matrix = matrix.rref()
        matrix = matrix.transpose()

        # 여기서는 간단히 예시로 두 벡터를 반환
        return Rotation4D.gram_schmidt(matrix.data[2], matrix.data[3])

    # 4D 회전 행렬을 반환
    def get_rotation_matrix(self):
        # rotation plane의 orthonormal basis를 생성
        u1, u2 = self.gram_schmidt(self.axis1, self.axis2)

        # orthogonal complement의 orthonormal basis를 생성
        v1, v2 = self.orthogonal_complement(u1, u2)

        # 좌표계 변환 행렬 생성
        orthonormal_basis = [u1.data, u2.data, v1.data, v2.data]
        orthonormal_matrix = Matrix4D(orthonormal_basis).transpose()

        # 4x4 identity matrix 생성
        rotation_matrix = Matrix4D.identity()

        # rotation plane에 대한 회전 행렬을 구성
        c1 = math.cos(self.angle1)
        s1 = math.sin(self.angle1)
        c2 = math.cos(self.angle2)
        s2 = math.sin(self.angle2)

        # rotation plane에 대한 회전 행렬을 구성
        rotation_data = cast(list[list[float]], rotation_matrix.data)
        rotation_data[0][0] = c1
        rotation_data[0][1] = -s1
        rotation_data[1][0] = s1
        rotation_data[1][1] = c1

        rotation_data[2][2] = c2
        rotation_data[2][3] = -s2
        rotation_data[3][2] = s2
        rotation_data[3][3] = c2

        # 좌표계 변환을 적용
        rotation_matrix = orthonormal_matrix * rotation_matrix * orthonormal_matrix.transpose()

        return rotation_matrix

    def rotate_vector(self, vector):
        if not isinstance(vector, Vector4D):
            raise TypeError("The input must be an instance of Vector4D.")
        rotation_matrix = self.get_rotation_matrix()
        return rotation_matrix * vector
# -*- coding: utf-8 -*-

import math

from .geometry import Point4D, Vector4D
from .matrix import Matrix4D

# 1차 독립 판정에 사용하는 허용 오차(입력 벡터 크기에 대한 상대값)
_INDEPENDENCE_TOLERANCE = 1e-10

# 좌표축 이름과 인덱스
_AXIS_INDEX = {"x": 0, "y": 1, "z": 2, "w": 3}


def _standard_basis(index):
    data = [0.0, 0.0, 0.0, 0.0]
    data[index] = 1.0
    return Vector4D(data)


def _reject(vector, basis):
    # vector에서 orthonormal basis 성분을 제거한 나머지(직교 성분)를 반환
    data = list(vector.data)
    for b in basis:
        proj = sum(data[i] * b.data[i] for i in range(4))
        data = [data[i] - proj * b.data[i] for i in range(4)]
    return Vector4D(data)


class Rotation4D(object):
    """
    4차원 일반 회전(double rotation).

    4차원에서 임의의 회전은 서로 직교하는 두 평면 P, Q에서의 2차원 회전의 합성이다.
      - P: plane_vector1, plane_vector2가 생성하는 회전 평면
      - Q: P의 orthogonal complement
    P에서 angle1만큼, Q에서 angle2만큼 동시에 회전한다.

      angle2 == 0          : 단순 회전(simple rotation, P 위에서만 회전하고 Q는 고정)
      angle2 == +-angle1   : 등각 회전(isoclinic rotation)

    P의 회전 방향은 u1 -> u2 (u1, u2는 plane_vector1, plane_vector2를 Gram-Schmidt한 것).
    Q의 basis (v1, v2)는 det[u1 u2 v1 v2] = +1이 되도록 잡으므로
    angle2의 부호는 4차원 공간의 방향(orientation)에 대해 일관되게 정의된다.

    각도 단위는 라디안이다.
    """

    def __init__(self, plane_vector1, plane_vector2, angle1, angle2=0.0):
        if not isinstance(plane_vector1, Vector4D) or not isinstance(plane_vector2, Vector4D):
            raise TypeError("Plane vectors must be instances of Vector4D.")
        if not isinstance(angle1, (int, float)) or not isinstance(angle2, (int, float)):
            raise TypeError("Angles must be numbers (radians).")

        # 회전 평면 P의 orthonormal basis
        self.u1, self.u2 = self.gram_schmidt(plane_vector1, plane_vector2)
        # P의 orthogonal complement Q의 orthonormal basis (오른손 방향)
        self.v1, self.v2 = self.orthogonal_complement(self.u1, self.u2)

        self.angle1 = float(angle1)
        self.angle2 = float(angle2)

        self._matrix = self._build_matrix()

    # 좌표 평면(xy, xz, xw, yz, yw, zw) 위에서의 회전을 생성
    # 예: Rotation4D.coordinate_plane("xw", math.pi / 4)
    @classmethod
    def coordinate_plane(cls, plane, angle1, angle2=0.0):
        if not isinstance(plane, str) or len(plane) != 2 \
                or plane[0] not in _AXIS_INDEX or plane[1] not in _AXIS_INDEX \
                or plane[0] == plane[1]:
            raise ValueError("Plane must be two different axes from 'xyzw', e.g. 'xw'.")
        return cls(_standard_basis(_AXIS_INDEX[plane[0]]),
                   _standard_basis(_AXIS_INDEX[plane[1]]),
                   angle1, angle2)

    # vector 2개를 통해 rotation plane의 orthonormal basis를 생성
    @staticmethod
    def gram_schmidt(vector1, vector2):
        if vector1.magnitude() == 0 or vector2.magnitude() == 0:
            raise ValueError("Plane vectors must be non-zero.")
        u1 = vector1.normalize()

        # vector2에서 u1 성분을 제거
        residual = _reject(vector2, [u1])
        if residual.magnitude() <= _INDEPENDENCE_TOLERANCE * vector2.magnitude():
            raise ValueError("Plane vectors must be linearly independent.")
        u2 = residual.normalize()
        return u1, u2

    # rotation plane의 orthogonal complement의 orthonormal basis를 생성
    @staticmethod
    def orthogonal_complement(u1, u2):
        # 표준 기저 e1..e4에서 이미 구한 basis 성분을 제거하고,
        # 남은 성분이 가장 큰 것을 골라 정규화한다.
        # (가장 큰 것을 고르면 수치적으로 안정적이다:
        #  첫 번째는 잔차 제곱합이 2이므로 크기가 최소 1/sqrt(2),
        #  두 번째는 잔차 제곱합이 1이므로 크기가 최소 1/2)
        basis = [u1, u2]
        for _ in range(2):
            candidates = [_reject(_standard_basis(i), basis) for i in range(4)]
            best = max(candidates, key=lambda v: v.magnitude())
            basis.append(best.normalize())
        v1, v2 = basis[2], basis[3]

        # det[u1 u2 v1 v2] = +1 이 되도록 v2의 방향을 맞춘다
        frame = Matrix4D([u1.data, u2.data, v1.data, v2.data])
        if frame.determinant() < 0:
            v2 = -v2
        return v1, v2

    # basis B = [u1 u2 v1 v2] (열벡터) 에 대해 R = B * D * B^T
    # D는 (u1,u2) 평면에서 angle1, (v1,v2) 평면에서 angle2 회전하는 블록 대각 행렬
    def _build_matrix(self):
        c1 = math.cos(self.angle1)
        s1 = math.sin(self.angle1)
        c2 = math.cos(self.angle2)
        s2 = math.sin(self.angle2)

        block = Matrix4D([
            [c1, -s1, 0.0, 0.0],
            [s1, c1, 0.0, 0.0],
            [0.0, 0.0, c2, -s2],
            [0.0, 0.0, s2, c2],
        ])
        basis = Matrix4D([self.u1.data, self.u2.data, self.v1.data, self.v2.data]).transpose()
        return basis * block * basis.transpose()

    # 4D 회전 행렬을 반환(내부 행렬의 복사본)
    def get_rotation_matrix(self):
        return Matrix4D(self._matrix.data)

    def rotate_vector(self, vector):
        if not isinstance(vector, Vector4D):
            raise TypeError("The input must be an instance of Vector4D.")
        return self._matrix * vector

    # 원점을 중심으로 점을 회전
    def rotate_point(self, point):
        if not isinstance(point, Point4D):
            raise TypeError("The input must be an instance of Point4D.")
        return self._matrix * point

# -*- coding: utf-8 -*-

from .geometry import Point4D, Vector4D
from .matrix import Matrix4D


class Polytope(object):
    """
    꼭짓점과 모서리로 이루어진 4차원 도형(wireframe).

    vertices: Point4D 리스트
    edges:    꼭짓점 인덱스 쌍 (i, j) 리스트. 내부적으로 i < j 로 정규화하여 저장한다.

    변환 메서드(transform, translate)는 원본을 바꾸지 않고 새 Polytope를 반환한다.
    애니메이션에서는 원본 도형을 그대로 두고 프레임마다 변환 결과만 새로 만들면 된다.
    """

    def __init__(self, vertices, edges):
        if not isinstance(vertices, list) or not all(isinstance(v, Point4D) for v in vertices):
            raise TypeError("Vertices must be a list of Point4D.")
        if not isinstance(edges, list):
            raise TypeError("Edges must be a list of index pairs.")

        count = len(vertices)
        normalized = []
        seen = set()
        for edge in edges:
            if not isinstance(edge, (list, tuple)) or len(edge) != 2 \
                    or not all(isinstance(i, int) and not isinstance(i, bool) for i in edge):
                raise TypeError("Each edge must be a pair of vertex indices.")
            i, j = edge
            if not (0 <= i < count) or not (0 <= j < count):
                raise IndexError("Edge {} refers to a missing vertex.".format(tuple(edge)))
            if i == j:
                raise ValueError("Edge {} connects a vertex to itself.".format(tuple(edge)))
            key = (min(i, j), max(i, j))
            if key in seen:
                raise ValueError("Duplicate edge {}.".format(key))
            seen.add(key)
            normalized.append(key)

        self.vertices = [Point4D(v.data) for v in vertices]
        self.edges = normalized

    def __repr__(self):
        return "{}({} vertices, {} edges)".format(
            type(self).__name__, len(self.vertices), len(self.edges))

    def vertex_count(self):
        return len(self.vertices)

    def edge_count(self):
        return len(self.edges)

    # 각 모서리를 양 끝점 (Point4D, Point4D) 쌍으로 반환(렌더러용)
    def edge_segments(self):
        return [(self.vertices[i], self.vertices[j]) for i, j in self.edges]

    # 꼭짓점 i에 연결된 꼭짓점 인덱스 목록
    def neighbors(self, index):
        if not (0 <= index < len(self.vertices)):
            raise IndexError("Vertex index out of range.")
        result = []
        for i, j in self.edges:
            if i == index:
                result.append(j)
            elif j == index:
                result.append(i)
        return sorted(result)

    # 꼭짓점들의 무게중심
    def centroid(self):
        if not self.vertices:
            raise ValueError("Cannot compute the centroid of an empty polytope.")
        n = float(len(self.vertices))
        return Point4D([sum(v.data[k] for v in self.vertices) / n for k in range(4)])

    # 모든 꼭짓점에 행렬을 적용한 새 도형(원점 기준 선형변환)
    # 예: polytope.transform(rotation.get_rotation_matrix())
    def transform(self, matrix):
        if not isinstance(matrix, Matrix4D):
            raise TypeError("The matrix must be an instance of Matrix4D.")
        return self._with_vertices([matrix * v for v in self.vertices])

    # 모든 꼭짓점을 벡터만큼 평행이동한 새 도형
    def translate(self, vector):
        if not isinstance(vector, Vector4D):
            raise TypeError("The vector must be an instance of Vector4D.")
        return self._with_vertices([v + vector for v in self.vertices])

    # 같은 모서리 구조에 꼭짓점만 바꾼 새 도형
    def _with_vertices(self, vertices):
        result = Polytope.__new__(Polytope)
        result.vertices = vertices
        result.edges = list(self.edges)
        return result


class Tesseract(Polytope):
    """
    4차원 초입방체(hypercube).

    size:   한 변의 길이 (기본값 2.0 -> 꼭짓점 좌표가 +-1)
    center: 중심점 (기본값 원점)

    꼭짓점 번호 i의 비트 k가 1이면 k번째 좌표(x, y, z, w 순)가 +size/2, 0이면 -size/2.
    좌표가 정확히 하나만 다른 두 꼭짓점(번호가 비트 하나만 다른 쌍)이 모서리로 연결된다.
    -> 꼭짓점 2^4 = 16개, 모서리 16 * 4 / 2 = 32개
    """

    def __init__(self, size=2.0, center=None):
        if not isinstance(size, (int, float)) or isinstance(size, bool):
            raise TypeError("Size must be a number.")
        if size <= 0:
            raise ValueError("Size must be positive.")
        if center is None:
            center = Point4D([0.0, 0.0, 0.0, 0.0])
        if not isinstance(center, Point4D):
            raise TypeError("Center must be an instance of Point4D.")

        half = size / 2.0
        vertices = []
        for i in range(16):
            vertices.append(Point4D([
                center.data[k] + (half if (i >> k) & 1 else -half) for k in range(4)
            ]))

        edges = []
        for i in range(16):
            for k in range(4):
                j = i ^ (1 << k)
                if i < j:
                    edges.append((i, j))

        Polytope.__init__(self, vertices, edges)
        self.size = float(size)
        self.center = Point4D(center.data)

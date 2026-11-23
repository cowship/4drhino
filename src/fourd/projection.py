# -*- coding: utf-8 -*-
"""
4D -> 3D 투영.

입력 좌표는 관찰자 좌표계 기준이다(관찰자 변환은 camera에서 처리).
관찰자는 항상 w축을 따라 바라보며, 투영은 w 성분을 제거한다.

  - OrthographicProjection: (x, y, z, w) -> (x, y, z)
  - PerspectiveProjection:  눈이 w = d 에 있고 -w 방향을 바라본다.
                            (x, y, z, w) -> (x, y, z) * d / (d - w)
                            w = 0 인 점은 직교 투영과 같은 크기로 보인다.

원근 투영에서 눈에 너무 가깝거나 눈 뒤에 있는 점(w > d - near)은 투영할 수 없으므로
근접 평면 w = d - near 에서 모서리를 잘라낸다(near-plane clipping).
4D 직선은 원근 투영 후에도 직선이므로 선분의 양 끝점만 투영하면 된다.
"""

from .geometry import Point4D
from .polytope import Polytope


class ProjectedSegment(object):
    """
    투영된 3차원 선분 하나.

    start, end:          투영된 3D 좌표 (x, y, z) 튜플
    start_w, end_w:      투영 전 w 좌표(깊이). 모서리 색 지정 등에 사용
    edge:                원본 Polytope의 모서리 (i, j)
    start_clipped,
    end_clipped:         해당 끝점이 근접 평면에서 잘려 새로 생긴 점인지 여부
    """

    def __init__(self, start, end, start_w, end_w, edge,
                 start_clipped=False, end_clipped=False):
        self.start = start
        self.end = end
        self.start_w = start_w
        self.end_w = end_w
        self.edge = edge
        self.start_clipped = start_clipped
        self.end_clipped = end_clipped

    def __repr__(self):
        return "ProjectedSegment({}, {}, edge={})".format(self.start, self.end, self.edge)


class ProjectionResult(object):
    """
    Polytope를 투영한 결과.

    segments: 화면에 그릴 ProjectedSegment 리스트.
              근접 평면 뒤로 완전히 넘어간 모서리는 포함되지 않는다.
    """

    def __init__(self, segments):
        self.segments = segments

    def __repr__(self):
        return "ProjectionResult({} segments)".format(len(self.segments))

    def segment_count(self):
        return len(self.segments)

    def w_range(self):
        # 결과에 포함된 깊이(w)의 최솟값, 최댓값 (색상 정규화용)
        if not self.segments:
            return None
        values = []
        for s in self.segments:
            values.append(s.start_w)
            values.append(s.end_w)
        return min(values), max(values)


class Projection(object):
    # 근접 평면의 w 값. None이면 클리핑하지 않는다.
    def _clip_limit(self):
        return None

    # 점이 투영 가능한 영역(근접 평면 앞쪽, 경계 포함)에 있는지
    def is_visible(self, point):
        if not isinstance(point, Point4D):
            raise TypeError("The point must be an instance of Point4D.")
        limit = self._clip_limit()
        return limit is None or point.data[3] <= limit

    # 하나의 점을 투영한 3D 좌표(튜플)
    def project_point(self, point):
        if not self.is_visible(point):
            raise ValueError("The point is behind the near plane and cannot be projected.")
        return self._project_coords(point.data)

    def _project_coords(self, data):
        raise NotImplementedError

    # Polytope의 모든 모서리를 투영(필요하면 근접 평면에서 잘라냄)
    def project(self, polytope):
        if not isinstance(polytope, Polytope):
            raise TypeError("The input must be an instance of Polytope.")
        limit = self._clip_limit()
        segments = []
        for (i, j) in polytope.edges:
            a = polytope.vertices[i].data
            b = polytope.vertices[j].data
            clipped = self._clip(a, b, limit)
            if clipped is None:
                continue
            a, b, a_clipped, b_clipped = clipped
            segments.append(ProjectedSegment(
                self._project_coords(a), self._project_coords(b),
                a[3], b[3], (i, j), a_clipped, b_clipped))
        return ProjectionResult(segments)

    # 선분 a-b 중 w <= limit 인 부분을 반환. 전부 넘어가면 None
    @staticmethod
    def _clip(a, b, limit):
        if limit is None:
            return a, b, False, False
        a_visible = a[3] <= limit
        b_visible = b[3] <= limit
        if a_visible and b_visible:
            return a, b, False, False
        if not a_visible and not b_visible:
            return None
        # 선분이 근접 평면과 만나는 점: a + t (b - a), w = limit
        t = (limit - a[3]) / float(b[3] - a[3])
        cut = [a[k] + t * (b[k] - a[k]) for k in range(4)]
        cut[3] = limit  # 부동소수점 오차 없이 정확히 평면 위에 놓는다
        if a_visible:
            return a, cut, False, True
        return cut, b, True, False


class OrthographicProjection(Projection):
    """w 성분을 버리는 직교 투영."""

    def _project_coords(self, data):
        return (float(data[0]), float(data[1]), float(data[2]))


class PerspectiveProjection(Projection):
    """
    원근 투영.

    eye_distance: 눈의 위치 w = d (d > 0). 투영면은 w = 0.
    near:         근접 평면까지의 거리. w > d - near 인 부분은 잘린다 (near > 0).
    """

    def __init__(self, eye_distance=4.0, near=0.1):
        for name, value in (("eye_distance", eye_distance), ("near", near)):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError("{} must be a number.".format(name))
            if value <= 0:
                raise ValueError("{} must be positive.".format(name))
        self.eye_distance = float(eye_distance)
        self.near = float(near)

    def _clip_limit(self):
        return self.eye_distance - self.near

    def _project_coords(self, data):
        scale = self.eye_distance / (self.eye_distance - data[3])
        return (data[0] * scale, data[1] * scale, data[2] * scale)

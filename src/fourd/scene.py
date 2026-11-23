# -*- coding: utf-8 -*-
"""
장면(Scene): 도형 + 회전 운동 + 투영 -> 한 프레임에 그릴 3D 선분과 점.

Rhino에 의존하지 않는다. 렌더러는 Scene.frame(t)이 돌려준 Frame을 그리기만 한다.

파이프라인:
    도형 --(중심 기준 회전, 시간 t)--> 월드 좌표
         --(관찰자 변환: Phase 4 camera 자리)--> 관찰자 좌표
         --(투영 4D -> 3D)--> 선분
         --(배율, w 깊이 색상)--> Frame
"""

from .geometry import Point4D, Vector4D
from .polytope import Polytope
from .projection import OrthographicProjection, Projection
from .rotation import Rotation4D

# 기본 색상 (R, G, B)
NEAR_COLOR = (230, 70, 40)     # 관찰자에 가까운 쪽(w 큼): 붉은색
FAR_COLOR = (40, 110, 230)     # 관찰자에서 먼 쪽(w 작음): 푸른색
BASE_COLOR = (20, 20, 20)      # 깊이 색상을 끌 때의 단색


def _check_color(name, color):
    if not isinstance(color, (list, tuple)) or len(color) != 3 or \
            not all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c <= 255 for c in color):
        raise ValueError("{} must be three integers between 0 and 255.".format(name))
    return tuple(color)


def _check_number(name, value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError("{} must be a number.".format(name))
    return float(value)


class RotationMotion(object):
    """
    시간에 따라 일정한 각속도로 도는 이중 회전.

    speed1: 회전 평면에서의 각속도 (rad/s)
    speed2: 그 직교 평면에서의 각속도 (rad/s, 기본값 0 -> 단순 회전)
    """

    def __init__(self, plane_vector1, plane_vector2, speed1, speed2=0.0):
        self.speed1 = _check_number("speed1", speed1)
        self.speed2 = _check_number("speed2", speed2)
        # 평면 벡터 검증은 Rotation4D에 맡긴다
        Rotation4D(plane_vector1, plane_vector2, 0.0, 0.0)
        self.plane_vector1 = Vector4D(plane_vector1.data)
        self.plane_vector2 = Vector4D(plane_vector2.data)

    @classmethod
    def coordinate_plane(cls, plane, speed1, speed2=0.0):
        base = Rotation4D.coordinate_plane(plane, 0.0)
        return cls(base.u1, base.u2, speed1, speed2)

    # 시각 t(초)에서의 회전
    def at(self, t):
        t = _check_number("t", t)
        return Rotation4D(self.plane_vector1, self.plane_vector2, self.speed1 * t, self.speed2 * t)


class Frame(object):
    """
    한 프레임에 그릴 내용.

    lines:  [((x, y, z), (x, y, z), (r, g, b)), ...]
    points: [((x, y, z), (r, g, b)), ...]
    """

    def __init__(self, lines, points):
        self.lines = lines
        self.points = points

    def __repr__(self):
        return "Frame({} lines, {} points)".format(len(self.lines), len(self.points))

    # 모든 좌표를 감싸는 축 정렬 상자 ((min x, y, z), (max x, y, z)). 비어 있으면 None
    def bounds(self):
        coords = []
        for start, end, _ in self.lines:
            coords.append(start)
            coords.append(end)
        for point, _ in self.points:
            coords.append(point)
        if not coords:
            return None
        lower = tuple(min(c[k] for c in coords) for k in range(3))
        upper = tuple(max(c[k] for c in coords) for k in range(3))
        return lower, upper


class Scene(object):
    """
    polytope:        그릴 도형
    motion:          RotationMotion (None이면 회전하지 않음). 도형의 무게중심을 기준으로 돈다
    projection:      OrthographicProjection 또는 PerspectiveProjection (기본: 직교)
    scale:           투영 결과에 곱할 배율 (Rhino 단위에 맞추기 위함)
    depth_coloring:  True이면 w 깊이에 따라 FAR_COLOR -> NEAR_COLOR로 색을 칠한다
    show_vertices:   True이면 꼭짓점도 점으로 그린다
    """

    def __init__(self, polytope, motion=None, projection=None, scale=1.0,
                 depth_coloring=True, show_vertices=True,
                 near_color=NEAR_COLOR, far_color=FAR_COLOR, base_color=BASE_COLOR):
        if not isinstance(polytope, Polytope):
            raise TypeError("The polytope must be an instance of Polytope.")
        if motion is not None and not isinstance(motion, RotationMotion):
            raise TypeError("The motion must be an instance of RotationMotion.")
        if projection is None:
            projection = OrthographicProjection()
        if not isinstance(projection, Projection):
            raise TypeError("The projection must be a projection instance.")
        self.scale = _check_number("scale", scale)
        if self.scale <= 0:
            raise ValueError("Scale must be positive.")

        self.polytope = polytope
        self.motion = motion
        self.projection = projection
        self.depth_coloring = bool(depth_coloring)
        self.show_vertices = bool(show_vertices)
        self.near_color = _check_color("near_color", near_color)
        self.far_color = _check_color("far_color", far_color)
        self.base_color = _check_color("base_color", base_color)

        # 회전 중심(무게중심)과, 회전해도 변하지 않는 w 범위(색상 기준)
        self.pivot = polytope.centroid() if polytope.vertices else Point4D([0, 0, 0, 0])
        radius = max([v.distance_to(self.pivot) for v in polytope.vertices] or [0.0])
        self._w_min = self.pivot.data[3] - radius
        self._w_max = self.pivot.data[3] + radius

    # 시각 t에서 회전한 도형(월드 좌표)
    def posed_polytope(self, t):
        if self.motion is None:
            return self.polytope
        to_origin = Vector4D([-c for c in self.pivot.data])
        back = Vector4D(list(self.pivot.data))
        matrix = self.motion.at(t).get_rotation_matrix()
        return self.polytope.translate(to_origin).transform(matrix).translate(back)

    # 월드 좌표 -> 관찰자 좌표. Phase 4에서 camera 변환이 들어갈 자리
    def to_view_space(self, polytope):
        return polytope

    # w 깊이에 따른 색
    def color_at(self, w):
        if not self.depth_coloring:
            return self.base_color
        span = self._w_max - self._w_min
        s = 0.5 if span <= 0 else (w - self._w_min) / span
        s = max(0.0, min(1.0, s))
        return tuple(int(round(f + (n - f) * s)) for f, n in zip(self.far_color, self.near_color))

    def _scaled(self, p):
        return (p[0] * self.scale, p[1] * self.scale, p[2] * self.scale)

    # 시각 t(초)의 프레임
    def frame(self, t=0.0):
        view = self.to_view_space(self.posed_polytope(t))
        result = self.projection.project(view)

        lines = []
        for s in result.segments:
            color = self.color_at((s.start_w + s.end_w) / 2.0)
            lines.append((self._scaled(s.start), self._scaled(s.end), color))

        points = []
        if self.show_vertices:
            for v in view.vertices:
                if self.projection.is_visible(v):
                    points.append((self._scaled(self.projection.project_point(v)), self.color_at(v.data[3])))
        return Frame(lines, points)

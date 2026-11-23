# -*- coding: utf-8 -*-
"""
Rhino 7 DisplayConduit 렌더러.

fourd.scene.Frame(3D 선분과 점, RGB 색)을 받아서 뷰포트에 그린다.
Rhino 문서에 객체를 추가하지 않으므로 매 프레임 갱신해도 문서/Undo 기록이 늘지 않는다.

conduit 인스턴스는 scriptcontext.sticky에 보관한다. 스크립트를 다시 실행해도
이전 conduit를 찾아 끌 수 있어서 화면에 여러 개가 겹쳐 그려지지 않는다.
"""
from __future__ import print_function

import Rhino
import scriptcontext as sc
import System.Drawing

STICKY_KEY = "fourd.conduit"

# Rhino 7의 둥근 점 스타일. 없는 버전이면 기본 점 스타일
POINT_STYLE = getattr(Rhino.Display.PointStyle, "RoundSimple", Rhino.Display.PointStyle.Simple)


def to_point3d(p):
    return Rhino.Geometry.Point3d(p[0], p[1], p[2])


def to_color(c):
    return System.Drawing.Color.FromArgb(c[0], c[1], c[2])


def to_bounding_box(bounds):
    # Frame.bounds() 결과 -> Rhino BoundingBox (비어 있으면 Empty)
    if bounds is None:
        return Rhino.Geometry.BoundingBox.Empty
    lower, upper = bounds
    return Rhino.Geometry.BoundingBox(to_point3d(lower), to_point3d(upper))


class FourDConduit(Rhino.Display.DisplayConduit):

    def __init__(self):
        # .NET 기반 클래스이므로 인자 없는 생성자만 사용하고 설정은 속성으로 한다
        self.lines = []          # [(Line, Color), ...]
        self.points = []         # [(Point3d, Color), ...]
        self.bbox = Rhino.Geometry.BoundingBox.Empty
        self.line_thickness = 2
        self.point_radius = 4
        self._error_reported = False

    def set_frame(self, frame):
        self.lines = [(Rhino.Geometry.Line(to_point3d(a), to_point3d(b)), to_color(c))
                      for a, b, c in frame.lines]
        self.points = [(to_point3d(p), to_color(c)) for p, c in frame.points]
        self.bbox = to_bounding_box(frame.bounds())

    # 도형이 뷰포트 클리핑 범위 안에 들어오도록 크기를 알린다
    def CalculateBoundingBox(self, e):
        if self.bbox.IsValid:
            e.IncludeBoundingBox(self.bbox)

    def PostDrawObjects(self, e):
        try:
            for line, color in self.lines:
                e.Display.DrawLine(line, color, self.line_thickness)
            for point, color in self.points:
                e.Display.DrawPoint(point, POINT_STYLE, self.point_radius, color)
        except Exception as ex:
            # 그리기 오류는 매 프레임 반복되므로 한 번만 출력하고 conduit를 끈다
            if not self._error_reported:
                self._error_reported = True
                print("fourd renderer error: {}".format(ex))
            self.Enabled = False


def show(frame, line_thickness=2, point_radius=4):
    # 이전 conduit를 끄고 새 conduit로 frame을 그린다. 새 conduit를 반환
    clear(refresh=False)
    conduit = FourDConduit()
    conduit.line_thickness = line_thickness
    conduit.point_radius = point_radius
    conduit.set_frame(frame)
    conduit.Enabled = True
    sc.sticky[STICKY_KEY] = conduit
    redraw()
    return conduit


def current():
    return sc.sticky.get(STICKY_KEY)


def clear(refresh=True):
    conduit = sc.sticky.pop(STICKY_KEY, None)
    if conduit is not None:
        conduit.Enabled = False
    if refresh:
        redraw()


def redraw():
    sc.doc.Views.Redraw()


def zoom_to(bbox):
    if not bbox.IsValid:
        return
    view = sc.doc.Views.ActiveView
    if view is None:
        return
    view.ActiveViewport.ZoomBoundingBox(bbox)
    view.Redraw()

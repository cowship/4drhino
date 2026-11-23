"""
rhino_app 테스트.

Rhino가 없는 환경에서 실행하므로 Rhino, System.Drawing, scriptcontext, Eto.Forms를
흉내 낸 가짜 모듈을 sys.modules에 넣고 main.py / clear.py의 흐름을 검증한다.
실제 Rhino 화면 확인은 Rhino 7에서 직접 해야 한다.
"""
import importlib
import sys
import types

import pytest


# ---------------------------------------------------------------- 가짜 모듈

class FakeEvent(object):
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, *args):
        for h in list(self.handlers):
            h(*args)


class FakePoint3d(object):
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = x, y, z


class FakeLine(object):
    def __init__(self, a, b):
        self.From, self.To = a, b


class FakeBoundingBox(object):
    def __init__(self, lower=None, upper=None):
        self.Min, self.Max = lower, upper

    @property
    def IsValid(self):
        return self.Min is not None


FakeBoundingBox.Empty = FakeBoundingBox()


class FakeConduit(object):
    def __init__(self):
        self.Enabled = False


class FakeUITimer(object):
    instances = []

    def __init__(self):
        self.Interval = None
        self.Elapsed = FakeEvent()
        self.started = False
        FakeUITimer.instances.append(self)

    def Start(self):
        self.started = True

    def Stop(self):
        self.started = False


class FakeDisplay(object):
    def __init__(self):
        self.lines = []
        self.points = []

    def DrawLine(self, line, color, thickness):
        self.lines.append((line, color, thickness))

    def DrawPoint(self, point, style, radius, color):
        self.points.append((point, style, radius, color))


class FakeDrawArgs(object):
    def __init__(self):
        self.Display = FakeDisplay()
        self.included = []

    def IncludeBoundingBox(self, bbox):
        self.included.append(bbox)


@pytest.fixture
def rhino(monkeypatch):
    """가짜 Rhino 환경을 설치하고, 테스트 후 모듈 캐시를 원래대로 되돌린다."""
    saved_modules = dict(sys.modules)
    saved_path = list(sys.path)

    state = types.SimpleNamespace(redraws=0, zooms=[])

    rhino_mod = types.ModuleType("Rhino")
    rhino_mod.Geometry = types.SimpleNamespace(Point3d=FakePoint3d, Line=FakeLine, BoundingBox=FakeBoundingBox)
    rhino_mod.Display = types.SimpleNamespace(
        DisplayConduit=FakeConduit,
        PointStyle=types.SimpleNamespace(Simple="Simple", RoundSimple="RoundSimple"))

    drawing = types.ModuleType("System.Drawing")
    drawing.Color = types.SimpleNamespace(FromArgb=lambda r, g, b: (r, g, b))
    system = types.ModuleType("System")
    system.Drawing = drawing

    viewport = types.SimpleNamespace(ZoomBoundingBox=lambda bbox: state.zooms.append(bbox))
    view = types.SimpleNamespace(ActiveViewport=viewport, Redraw=lambda: None)

    def redraw():
        state.redraws += 1

    sc = types.ModuleType("scriptcontext")
    sc.sticky = {}
    sc.doc = types.SimpleNamespace(Views=types.SimpleNamespace(Redraw=redraw, ActiveView=view))

    eto = types.ModuleType("Eto")
    eto_forms = types.ModuleType("Eto.Forms")
    eto_forms.UITimer = FakeUITimer
    eto.Forms = eto_forms
    FakeUITimer.instances = []

    for name, module in (("Rhino", rhino_mod), ("System", system), ("System.Drawing", drawing),
                         ("scriptcontext", sc), ("Eto", eto), ("Eto.Forms", eto_forms)):
        monkeypatch.setitem(sys.modules, name, module)

    state.sticky = sc.sticky
    yield state

    sys.modules.clear()
    sys.modules.update(saved_modules)
    sys.path[:] = saved_path


def load_script(name):
    module = importlib.import_module("rhino_app." + name)
    return importlib.reload(module)


def run_main(config=None):
    main = load_script("main")
    if config is not None:
        main.CONFIG = config
    main.main()
    return main


def tick(timer):
    timer.Elapsed.fire(timer, None)


# ---------------------------------------------------------------- scene_config (순수 Python)

def test_merged_config_rejects_unknown_keys():
    from rhino_app import scene_config
    assert scene_config.merged_config({"speed": 1.0})["speed"] == 1.0
    with pytest.raises(KeyError):
        scene_config.merged_config({"sped": 1.0})


def test_build_scene_projection_modes():
    from fourd.projection import OrthographicProjection, PerspectiveProjection
    from rhino_app import scene_config
    ortho = scene_config.build_scene(scene_config.merged_config())
    assert isinstance(ortho.projection, OrthographicProjection)
    persp = scene_config.build_scene(scene_config.merged_config({"projection": "perspective", "eye_distance": 5}))
    assert isinstance(persp.projection, PerspectiveProjection)
    assert persp.projection.eye_distance == 5
    with pytest.raises(ValueError):
        scene_config.build_scene(scene_config.merged_config({"projection": "fisheye"}))


def test_default_scene_is_the_prototype():
    from rhino_app import scene_config
    frame = scene_config.build_scene(scene_config.merged_config()).frame(0.5)
    assert len(frame.lines) == 32 and len(frame.points) == 16


def test_motion_bounds_cover_every_frame():
    from rhino_app import scene_config
    scene = scene_config.build_scene(scene_config.merged_config({"speed": 0.7, "speed2": 0.3}))
    lower, upper = scene_config.motion_bounds(scene)
    # 직교 투영에서 테서랙트(반지름 2, 배율 10)가 차지할 수 있는 범위를 넘지 않는다
    assert all(-20 - 1e-9 <= c <= 20 + 1e-9 for c in lower + upper)
    # 회전 중 가장 멀리 간 x는 정지 프레임보다 넓다
    still = scene.frame(0.0).bounds()
    assert upper[0] >= still[1][0]


def test_motion_bounds_without_rotation():
    from rhino_app import scene_config
    scene = scene_config.build_scene(scene_config.merged_config({"speed": 0.0}))
    assert scene_config.motion_bounds(scene) == scene.frame(0.0).bounds()


# ---------------------------------------------------------------- main.py / clear.py 흐름

def test_first_run_starts_animation(rhino):
    run_main()
    conduit = rhino.sticky["fourd.conduit"]
    animator = rhino.sticky["fourd.animator"]
    assert conduit.Enabled
    assert animator.running
    assert len(conduit.lines) == 32 and len(conduit.points) == 16
    assert len(rhino.zooms) == 1 and rhino.zooms[0].IsValid
    timer = FakeUITimer.instances[-1]
    assert timer.started and timer.Interval == pytest.approx(1 / 30.0)


def test_tick_advances_time_and_redraws(rhino, monkeypatch):
    run_main()
    animator = rhino.sticky["fourd.animator"]
    conduit = rhino.sticky["fourd.conduit"]
    before_lines = [(l.From.X, l.To.X) for l, _ in conduit.lines]
    before_redraws = rhino.redraws

    controller = sys.modules["rhino_app.controller"]
    clock = [animator._last]
    monkeypatch.setattr(controller.time, "time", lambda: clock[0])
    clock[0] += 0.05
    tick(FakeUITimer.instances[-1])

    assert animator.t == pytest.approx(0.55)
    assert rhino.redraws == before_redraws + 1
    assert [(l.From.X, l.To.X) for l, _ in conduit.lines] != before_lines

    # Rhino가 오래 멈췄다 돌아와도 한 프레임에 MAX_STEP 이상 진행하지 않는다
    clock[0] += 5.0
    tick(FakeUITimer.instances[-1])
    assert animator.t == pytest.approx(0.55 + controller.MAX_STEP)


def test_second_run_pauses_third_run_resumes(rhino):
    run_main()
    first = rhino.sticky["fourd.animator"]
    first.t = 3.0

    run_main()
    assert not first.running
    assert not FakeUITimer.instances[-1].started
    assert FakeUITimer.instances[-1].Elapsed.handlers == []

    run_main({"projection": "perspective"})
    resumed = rhino.sticky["fourd.animator"]
    assert resumed is not first
    assert resumed.running and resumed.t == pytest.approx(3.0)
    # 이전 conduit는 꺼지고 새 conduit 하나만 켜진다
    assert rhino.sticky["fourd.conduit"].Enabled
    # 화면 맞춤은 처음 한 번만
    assert len(rhino.zooms) == 1


def test_static_mode(rhino):
    run_main({"animate": False, "start_time": 1.25})
    animator = rhino.sticky["fourd.animator"]
    assert not animator.running
    assert animator.t == 1.25
    assert rhino.sticky["fourd.conduit"].Enabled
    # 정지 화면 모드에서는 다시 실행하면 설정한 시각으로 다시 그린다
    run_main({"animate": False, "start_time": 2.0})
    assert rhino.sticky["fourd.animator"].t == 2.0


def test_clear(rhino):
    run_main()
    conduit = rhino.sticky["fourd.conduit"]
    animator = rhino.sticky["fourd.animator"]
    load_script("clear").main()
    assert not conduit.Enabled
    assert not animator.running
    assert "fourd.conduit" not in rhino.sticky and "fourd.animator" not in rhino.sticky


def test_conduit_draws_frame(rhino):
    run_main({"line_thickness": 3, "point_radius": 6})
    conduit = rhino.sticky["fourd.conduit"]

    args = FakeDrawArgs()
    conduit.CalculateBoundingBox(args)
    assert len(args.included) == 1

    conduit.PostDrawObjects(args)
    assert len(args.Display.lines) == 32
    assert all(thickness == 3 for _, _, thickness in args.Display.lines)
    assert len(args.Display.points) == 16
    assert all(style == "RoundSimple" and radius == 6 for _, style, radius, _ in args.Display.points)


def test_conduit_disables_itself_on_draw_error(rhino, capsys):
    run_main()
    conduit = rhino.sticky["fourd.conduit"]

    class BrokenDisplay(object):
        def DrawLine(self, *args):
            raise RuntimeError("boom")

    args = FakeDrawArgs()
    args.Display = BrokenDisplay()
    conduit.PostDrawObjects(args)
    conduit.PostDrawObjects(args)
    assert not conduit.Enabled
    assert capsys.readouterr().out.count("fourd renderer error") == 1


def test_animation_stops_on_frame_error(rhino, capsys):
    run_main()
    animator = rhino.sticky["fourd.animator"]

    def broken(t):
        raise RuntimeError("bad frame")

    animator.scene.frame = broken
    tick(FakeUITimer.instances[-1])
    assert not animator.running
    assert "fourd animation stopped by error: bad frame" in capsys.readouterr().out


def test_invalid_config_does_not_leave_half_state(rhino):
    with pytest.raises(ValueError):
        run_main({"projection": "fisheye"})
    assert "fourd.conduit" not in rhino.sticky
    assert "fourd.animator" not in rhino.sticky


def test_invalid_config_keeps_paused_scene(rhino):
    run_main()
    run_main()  # 일시정지
    paused = rhino.sticky["fourd.animator"]
    conduit = rhino.sticky["fourd.conduit"]
    with pytest.raises(ValueError):
        run_main({"projection": "fisheye"})
    assert rhino.sticky["fourd.animator"] is paused
    assert rhino.sticky["fourd.conduit"] is conduit and conduit.Enabled

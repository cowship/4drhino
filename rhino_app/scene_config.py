# -*- coding: utf-8 -*-
"""
main.py 설정값(dict) -> fourd Scene 생성. Rhino에 의존하지 않는다.
"""

import math

from fourd.polytope import Tesseract
from fourd.projection import OrthographicProjection, PerspectiveProjection
from fourd.scene import RotationMotion, Scene

DEFAULT_CONFIG = {
    # 도형
    "size": 2.0,                     # 테서랙트 한 변의 길이

    # 회전 (각속도 단위: rad/s)
    "rotation_plane": "xw",          # xy, xz, xw, yz, yw, zw
    "speed": 0.6,                    # 회전 평면에서의 각속도
    "speed2": 0.0,                   # 직교 평면에서의 각속도 (0이면 단순 회전)

    # 투영
    "projection": "orthographic",    # "orthographic" 또는 "perspective"
    "eye_distance": 4.0,             # 원근 투영: 눈의 위치 w = d
    "near": 0.1,                     # 원근 투영: 근접 평면 거리

    # 표시
    "scale": 10.0,                   # Rhino 단위 배율
    "depth_coloring": True,          # w 깊이에 따른 색상
    "show_vertices": True,
    "line_thickness": 2,             # 픽셀
    "point_radius": 4,               # 픽셀

    # 재생
    "animate": True,                 # False이면 start_time 시점의 정지 화면
    "start_time": 0.5,               # 처음 그릴 시각(초)
    "fps": 30,
    "zoom_to_fit": True,             # 처음 그릴 때 화면을 도형에 맞춤
}


def merged_config(overrides=None):
    config = dict(DEFAULT_CONFIG)
    if overrides:
        unknown = set(overrides) - set(DEFAULT_CONFIG)
        if unknown:
            raise KeyError("Unknown config keys: {}".format(", ".join(sorted(unknown))))
        config.update(overrides)
    return config


def build_projection(config):
    mode = config["projection"]
    if mode == "orthographic":
        return OrthographicProjection()
    if mode == "perspective":
        return PerspectiveProjection(config["eye_distance"], config["near"])
    raise ValueError("projection must be 'orthographic' or 'perspective', not {!r}".format(mode))


def motion_bounds(scene, start_time=0.0, samples=48):
    # 회전하는 동안 도형이 차지하는 대략적인 범위 (화면 맞춤용)
    # 여러 시각의 프레임 범위를 합친다. 회전하지 않으면 한 프레임의 범위
    speeds = [abs(scene.motion.speed1), abs(scene.motion.speed2)] if scene.motion else [0.0]
    fastest = max(speeds)
    if fastest == 0:
        times = [start_time]
    else:
        period = 2 * math.pi / fastest
        times = [start_time + period * k / float(samples) for k in range(samples)]
    lower, upper = None, None
    for t in times:
        bounds = scene.frame(t).bounds()
        if bounds is None:
            continue
        if lower is None:
            lower, upper = bounds
        else:
            lower = tuple(min(a, b) for a, b in zip(lower, bounds[0]))
            upper = tuple(max(a, b) for a, b in zip(upper, bounds[1]))
    return None if lower is None else (lower, upper)


def build_scene(config):
    motion = RotationMotion.coordinate_plane(config["rotation_plane"], config["speed"], config["speed2"])
    return Scene(
        Tesseract(size=config["size"]),
        motion=motion,
        projection=build_projection(config),
        scale=config["scale"],
        depth_coloring=config["depth_coloring"],
        show_vertices=config["show_vertices"],
    )

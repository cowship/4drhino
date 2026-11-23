# -*- coding: utf-8 -*-
"""
4D 테서랙트를 Rhino 7 뷰포트에 표시한다.

실행:  _RunPythonScript <repo>/rhino_app/main.py

  - 처음 실행: 장면을 만들고 재생한다 (animate가 False이면 정지 화면)
  - 재생 중 다시 실행: 일시정지
  - 일시정지 상태에서 다시 실행: 아래 CONFIG를 다시 읽어 장면을 새로 만들고 이어서 재생
  - 지우기: _RunPythonScript <repo>/rhino_app/clear.py

설정은 아래 CONFIG에서 바꾼다. 바꿀 수 있는 항목과 기본값은 rhino_app/scene_config.py의
DEFAULT_CONFIG를 참고. 여기에 적은 항목만 기본값을 덮어쓴다.
"""
from __future__ import print_function

import os
import sys

CONFIG = {
    # 예시)
    # "projection": "perspective",
    # "rotation_plane": "xw",
    # "speed": 0.6,
    # "animate": False,
}


def _setup_paths():
    # repo/src 와 repo 를 import 경로에 추가하고, 이전 실행에서 캐시된 모듈을 지운다
    # (Rhino는 한 번 import한 모듈을 기억하므로, 지우지 않으면 코드 수정이 반영되지 않는다)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        raise RuntimeError("Run this file as a script (e.g. _RunPythonScript) so __file__ is defined.")
    root = os.path.dirname(here)
    for path in (root, os.path.join(root, "src")):
        if path not in sys.path:
            sys.path.insert(0, path)
    for name in list(sys.modules):
        if name.split(".")[0] in ("fourd", "rhino_app"):
            del sys.modules[name]


def main():
    _setup_paths()
    from rhino_app import controller, renderer, scene_config

    config = scene_config.merged_config(CONFIG)
    previous = controller.current()

    # 재생 중이면 일시정지
    if previous is not None and previous.running:
        previous.stop()
        print("fourd: paused at t = {:.2f} s (run again to resume, clear.py to remove)".format(previous.t))
        return

    # 재생 모드에서는 멈춘 시각부터 이어서, 정지 화면 모드에서는 설정한 시각으로
    if previous is not None and config["animate"]:
        start_time = previous.t
    else:
        start_time = config["start_time"]
    first_show = renderer.current() is None

    # 설정이 잘못되었으면 여기서 오류가 나고, 기존 화면은 그대로 남는다
    scene = scene_config.build_scene(config)
    frame = scene.frame(start_time)

    controller.stop_current()
    conduit = renderer.show(frame, config["line_thickness"], config["point_radius"])

    if config["zoom_to_fit"] and first_show:
        renderer.zoom_to(renderer.to_bounding_box(scene_config.motion_bounds(scene, start_time)))

    animator = controller.Animator(scene, conduit, config["fps"], start_time)
    controller.register(animator)

    description = "{} projection, {} plane".format(config["projection"], config["rotation_plane"])
    if config["animate"]:
        animator.start()
        print("fourd: playing ({}). Run again to pause.".format(description))
    else:
        print("fourd: static frame at t = {} s ({}).".format(start_time, description))


if __name__ == "__main__":
    main()

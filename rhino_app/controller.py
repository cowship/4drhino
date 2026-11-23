# -*- coding: utf-8 -*-
"""
애니메이션 컨트롤러.

Eto UITimer는 Rhino UI 스레드에서 일정 간격으로 호출되므로, 화면을 멈추지 않고
(while + sleep 반복 없이) 프레임마다 장면을 갱신할 수 있다.

Animator 인스턴스는 scriptcontext.sticky에 보관하여 main.py를 다시 실행할 때
재생/일시정지를 전환할 수 있게 한다.
"""
from __future__ import print_function

import time

import Eto.Forms
import scriptcontext as sc

from rhino_app import renderer

STICKY_KEY = "fourd.animator"

# 한 프레임에서 시간을 최대 얼마까지 진행할지(초). Rhino가 잠시 멈췄다가 돌아와도 튀지 않게 한다
MAX_STEP = 0.1


class Animator(object):

    def __init__(self, scene, conduit, fps=30, start_time=0.0):
        if fps <= 0:
            raise ValueError("fps must be positive.")
        self.scene = scene
        self.conduit = conduit
        self.interval = 1.0 / fps
        self.t = float(start_time)
        self._timer = None
        self._handler = self._on_tick   # += / -= 에 같은 객체를 쓰기 위해 보관
        self._last = None

    @property
    def running(self):
        return self._timer is not None

    def render(self):
        self.conduit.set_frame(self.scene.frame(self.t))
        renderer.redraw()

    def start(self):
        if self.running:
            return
        self._last = time.time()
        timer = Eto.Forms.UITimer()
        timer.Interval = self.interval
        timer.Elapsed += self._handler
        self._timer = timer
        timer.Start()

    def stop(self):
        timer = self._timer
        if timer is None:
            return
        self._timer = None
        timer.Stop()
        timer.Elapsed -= self._handler

    def _on_tick(self, sender, e):
        try:
            now = time.time()
            self.t += min(now - self._last, MAX_STEP)
            self._last = now
            self.render()
        except Exception as ex:
            # 타이머가 계속 같은 오류를 내지 않도록 멈춘다
            self.stop()
            print("fourd animation stopped by error: {}".format(ex))


def current():
    return sc.sticky.get(STICKY_KEY)


def register(animator):
    sc.sticky[STICKY_KEY] = animator


def stop_current():
    animator = sc.sticky.pop(STICKY_KEY, None)
    if animator is not None:
        animator.stop()
    return animator

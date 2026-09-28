"""Простой проигрыватель кадровой анимации.

Анимации бывают двух видов:
  - плоские: {"idle": [...], "walk": [...], "attack": [...]} — влево смотрят
    отражением кадра (плейсхолдеры);
  - по направлениям: {"walk_down": [...], "idle_left": [...], ...} — у каждой
    из четырёх сторон свои кадры (нарезанные спрайт-листы).
"""
import pygame

DIRECTIONS = ("down", "left", "right", "up")


class Animator:
    def __init__(self, frames_by_action, frame_ms=110):
        self.frames_by_action = frames_by_action
        self.frame_ms = frame_ms
        self.action = "idle"
        self.direction = "down"
        self.directional = "idle_down" in frames_by_action
        self.index = 0
        self.timer = 0.0

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.index = 0
            self.timer = 0.0

    def face(self, dx, dy):
        """Повернуться по направлению движения/взгляда (dx, dy)."""
        if dx == 0 and dy == 0:
            return
        if abs(dx) >= abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def frames(self):
        fb = self.frames_by_action
        return (fb.get(f"{self.action}_{self.direction}") or fb.get(self.action)
                or fb.get(f"idle_{self.direction}") or fb["idle"])

    def update(self, dt_ms):
        self.timer += dt_ms
        if self.timer >= self.frame_ms:
            self.timer = 0.0
            self.index = (self.index + 1) % len(self.frames())

    def is_finished_once(self):
        """Для атаки: True, когда цикл кадров прошёл один раз целиком."""
        return self.index == len(self.frames()) - 1

    def current_frame(self, flip=False):
        frames = self.frames()
        frame = frames[self.index % len(frames)]
        if flip and not self.directional:
            frame = pygame.transform.flip(frame, True, False)
        return frame

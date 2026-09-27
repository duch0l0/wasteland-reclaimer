"""Простой проигрыватель кадровой анимации."""


class Animator:
    def __init__(self, frames_by_action, frame_ms=110):
        self.frames_by_action = frames_by_action
        self.frame_ms = frame_ms
        self.action = "idle"
        self.index = 0
        self.timer = 0.0

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.index = 0
            self.timer = 0.0

    def update(self, dt_ms):
        frames = self.frames_by_action.get(self.action) or self.frames_by_action["idle"]
        self.timer += dt_ms
        if self.timer >= self.frame_ms:
            self.timer = 0.0
            self.index = (self.index + 1) % len(frames)

    def is_finished_once(self):
        """Для атаки: True, когда цикл кадров прошёл один раз целиком."""
        frames = self.frames_by_action.get(self.action) or []
        return self.index == len(frames) - 1

    def current_frame(self, flip=False):
        frames = self.frames_by_action.get(self.action) or self.frames_by_action["idle"]
        frame = frames[self.index % len(frames)]
        if flip:
            import pygame
            frame = pygame.transform.flip(frame, True, False)
        return frame

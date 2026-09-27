"""Многослойный скроллящийся фон (parallax): дальние слои едут медленнее."""
import pygame

from . import settings as S
from . import loader


LAYER_DEFS = [
    {"top_color": (32, 26, 30), "bottom_color": (58, 44, 40), "speed": 0.15, "baseline": 0.45},   # небо/дальние горы
    {"top_color": (54, 42, 34), "bottom_color": (78, 60, 44), "speed": 0.35, "baseline": 0.62},   # средние дюны
    {"top_color": (70, 55, 40), "bottom_color": (94, 74, 50), "speed": 0.6, "baseline": 0.80},    # ближние дюны/руины
]


class Parallax:
    def __init__(self):
        self.layers = loader.load_parallax_layers(S.BG_DIR, (S.SCREEN_W, S.SCREEN_H), LAYER_DEFS)

    def draw(self, surf, cam_x):
        for layer in self.layers:
            img = layer["surface"]
            w = img.get_width()
            offset = int(cam_x * layer["speed"]) % w
            surf.blit(img, (-offset, 0))
            if offset > 0:
                surf.blit(img, (w - offset, 0))

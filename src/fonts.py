"""
Шрифты игры — из assets/fonts/ (DejaVu, свободная лицензия, см. LICENSE-DejaVu.txt),
чтобы кириллица одинаково выглядела на любой системе, в том числе на Windows,
где DejaVu не установлен. Если файла нет — системный шрифт.
"""
import os

import pygame

FONT_DIR = os.path.join("assets", "fonts")
FILES = {
    ("dejavusans", False): "DejaVuSans.ttf",
    ("dejavusans", True): "DejaVuSans-Bold.ttf",
    ("dejavuserif", False): "DejaVuSerif.ttf",
    ("dejavuserif", True): "DejaVuSerif-Bold.ttf",
    ("dejavusansmono", False): "DejaVuSansMono.ttf",
    ("dejavusansmono", True): "DejaVuSansMono.ttf",
}
_CACHE = {}


def get(name="dejavusans", size=16, bold=False, italic=False):
    key = (name, size, bold, italic)
    if key not in _CACHE:
        if not pygame.font.get_init():
            pygame.font.init()
        path = os.path.join(FONT_DIR, FILES.get((name, bold), "DejaVuSans.ttf"))
        if os.path.isfile(path):
            f = pygame.font.Font(path, size)
            if bold and (name, True) not in FILES:
                f.set_bold(True)
        else:
            f = pygame.font.SysFont(name, size, bold=bold)
        if italic:
            f.set_italic(True)
        _CACHE[key] = f
    return _CACHE[key]

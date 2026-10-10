"""Меню действий по ПКМ (src/game/ctxmenu.py): рамка у курсора, пункты с цифрами."""
import pygame

from .. import settings as S
from .common import fonts, panel, hotspot, COLOR_TITLE, COLOR_HOVER, PANEL_H


def draw_ctx_menu(surf, game):
    menu = game.ctx_menu
    font, font_small = fonts()
    w = max(220, max(font_small.size(f"[{i + 1}] {label}")[0] for i, (label, _) in enumerate(menu["items"])) + 32,
            font_small.size(menu["title"])[0] + 32)
    h = 40 + 26 * len(menu["items"])
    x = min(menu["pos"][0] + 12, S.SCREEN_W - w - 8)
    y = min(menu["pos"][1] - 10, S.SCREEN_H - PANEL_H - h - 8)
    box = pygame.Rect(x, max(8, y), w, h)
    panel(surf, box, 240)
    surf.blit(font_small.render(menu["title"], True, COLOR_TITLE), (box.x + 14, box.y + 10))
    yy = box.y + 36
    for i, (label, _) in enumerate(menu["items"]):
        row = pygame.Rect(box.x + 6, yy - 3, box.w - 12, 24)
        pick = lambda i=i: game.ctx_choose(i)
        pick.ctx = True
        hover = hotspot(row, pick)
        if hover:
            pygame.draw.rect(surf, (70, 60, 40), row, border_radius=3)
        surf.blit(font_small.render(f"[{i + 1}] {label}", True, COLOR_HOVER if hover else (220, 210, 190)),
                  (box.x + 14, yy))
        yy += 26

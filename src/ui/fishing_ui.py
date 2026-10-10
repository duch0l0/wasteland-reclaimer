"""Окно рыбалки (src/game/fishing.py): шкала, зелёная зона, бегущий поплавок, подсказка."""
import pygame

from .. import settings as S
from .common import fonts, panel, hotspot, COLOR_TITLE, PANEL_H


def draw_fishing(surf, game):
    f = game.fishing
    font, font_small = fonts()
    box = pygame.Rect(S.SCREEN_W // 2 - 300, S.SCREEN_H - PANEL_H - 190, 600, 170)
    panel(surf, box, 235)
    hotspot(box, lambda: game.fishing_strike())          # клик по окну — подсечь
    surf.blit(font.render("Рыбалка у причала", True, COLOR_TITLE), (box.x + 16, box.y + 10))
    surf.blit(font_small.render(f"Наживка: {game.inventory.count('наживка')}", True, (200, 190, 170)),
              (box.right - 140, box.y + 14))
    bar = pygame.Rect(box.x + 30, box.y + 62, box.w - 60, 26)
    pygame.draw.rect(surf, (40, 60, 70), bar, border_radius=4)
    lo, hi = f["zone"]
    if f["state"] in ("bite", "done"):
        zone = pygame.Rect(bar.x + int(lo * bar.w), bar.y, int((hi - lo) * bar.w), bar.h)
        pygame.draw.rect(surf, (80, 170, 90), zone, border_radius=4)
    pygame.draw.rect(surf, (120, 140, 150), bar, 2, border_radius=4)
    x = bar.x + int(f["pos"] * bar.w)
    bob = 0 if f["state"] != "wait" else int(3 * ((pygame.time.get_ticks() // 300) % 2))
    pygame.draw.circle(surf, (230, 70, 50), (x, bar.centery + bob), 9)
    pygame.draw.circle(surf, (245, 240, 230), (x, bar.centery - 4 + bob), 4)
    surf.blit(font_small.render(f["msg"], True, (225, 215, 195)), (box.x + 20, box.y + 104))
    surf.blit(font_small.render("Space или клик — подсечь · Esc — смотать удочку", True, (160, 150, 135)),
              (box.x + 20, box.y + 134))

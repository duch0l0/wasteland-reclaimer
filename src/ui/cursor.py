"""Подсказка у курсора: клетка под мышью, путь с ценой в ОД (в бою), что будет по клику."""
import pygame

from .. import settings as S
from .common import fonts

T = S.TILE


def draw_cursor_hint(surf, hint, cam, text_surf=None):
    """Путь и клетка — на холсте мира (surf), подпись — у курсора на экране (text_surf)."""
    if not hint:
        return
    text, color, path, tile = hint
    surf_world, surf = surf, text_surf or surf
    if path:
        for i, (tx, ty) in enumerate(path):
            center = tuple(int(c) for c in cam.p(tx * T + T // 2, ty * T + T // 2))
            pygame.draw.circle(surf_world, (20, 16, 12), center, 5)
            pygame.draw.circle(surf_world, color, center, 3)
    if tile and getattr(cam, "iso", False):   # клетка — ромб
        x, y = tile
        pts = [cam.p(x * T, y * T), cam.p((x + 1) * T, y * T), cam.p((x + 1) * T, (y + 1) * T), cam.p(x * T, (y + 1) * T)]
        pygame.draw.polygon(surf_world, color or (230, 220, 190), pts, 1)
    elif tile:
        r = pygame.Rect(tile[0] * T - int(cam.x), tile[1] * T - int(cam.y), T, T)
        frame = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(frame, (*(color or (230, 220, 190)), 150), frame.get_rect(), 1, border_radius=4)
        surf_world.blit(frame, r)
    if text:
        _, font_small = fonts()
        mx, my = pygame.mouse.get_pos()
        txt = font_small.render(text, True, color)
        box = txt.get_rect(topleft=(mx + 16, my + 12)).inflate(10, 4)
        if box.right > S.SCREEN_W - 4:  # у правого края — подпись слева от курсора
            box.right = mx - 8
        bg = pygame.Surface(box.size, pygame.SRCALPHA)
        bg.fill((15, 12, 10, 200))
        surf.blit(bg, box)
        surf.blit(txt, txt.get_rect(center=box.center))

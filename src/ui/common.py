"""Общее для всего интерфейса: шрифты, перенос строк, подложка окон."""
import pygame

from .. import settings as S

pygame.font.init()
_FONTS = {}

COLOR_TITLE = (210, 190, 120)
COLOR_DIM = (170, 160, 145)
COLOR_OK = (140, 220, 140)
COLOR_BAD = (150, 130, 110)


def _font(size):
    if size not in _FONTS:
        try:
            _FONTS[size] = pygame.font.SysFont("dejavusans", size)
        except Exception:
            _FONTS[size] = pygame.font.Font(None, size + 2)
    return _FONTS[size]


def fonts():
    """(обычный, мелкий) — используются почти везде."""
    return _font(20), _font(16)


def font_tiny():
    return _font(13)


def wrap_text(font, text, max_w):
    """Разбивает текст на строки по словам так, чтобы каждая влезала в max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}" if cur else word
        if cur and font.size(trial)[0] > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def panel(surf, rect, alpha=240):
    """Полупрозрачная тёмная подложка окна с рамкой."""
    p = pygame.Surface(rect.size, pygame.SRCALPHA)
    p.fill((*S.COLOR_PANEL, alpha))
    pygame.draw.rect(p, S.COLOR_PANEL_BORDER, p.get_rect(), 2)
    surf.blit(p, rect.topleft)


def centered_box(w, h):
    return pygame.Rect(S.SCREEN_W // 2 - w // 2, S.SCREEN_H // 2 - h // 2, w, h)


def draw_rows(surf, rows, x, y, font, line_h=20, gap=8):
    """rows: (текст, цвет, отступ) или None (пустой промежуток). Возвращает y после последней строки."""
    for r in rows:
        if r is None:
            y += gap
            continue
        text, color, dx = r
        surf.blit(font.render(text, True, color), (x + dx, y))
        y += line_h
    return y


def rows_height(rows, line_h=20, gap=8):
    return sum(line_h if r else gap for r in rows)

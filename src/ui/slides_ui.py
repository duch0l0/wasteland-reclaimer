"""Показ слайдов: картинка в рамке диапроектора, год, заголовок, текст печатается машинкой."""
import pygame

from .. import settings as S
from .common import hotspot
from .slide_art import slide_image, W as ART_W, H as ART_H

AMBER = (240, 200, 120)
AMBER_DIM = (150, 115, 70)
TYPE_SPEED = 55  # символов в секунду
FADE_MS = 450

_F = {}


def _font(name, size, **kw):
    key = (name, size, tuple(sorted(kw.items())))
    if key not in _F:
        _F[key] = pygame.font.SysFont(name, size, **kw)
    return _F[key]


def _wrap(font, text, width):
    out = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = f"{cur} {w}" if cur else w
            if cur and font.size(t)[0] > width:
                out.append(cur)
                cur = w
            else:
                cur = t
        out.append(cur)
    return out


def slide_text(slide):
    return "\n\n".join(p["text"] for p in slide["parts"])


def typed_chars(show):
    return int(show["t"] * TYPE_SPEED / 1000)


def draw_slides(surf, game):
    show = game.slides
    slide = show["list"][show["i"]]
    surf.fill((12, 9, 7))
    art = slide_image(slide["art"], game)
    ax = (S.SCREEN_W - ART_W) // 2
    ay = 30
    pygame.draw.rect(surf, (40, 32, 24), (ax - 14, ay - 14, ART_W + 28, ART_H + 28), border_radius=6)
    pygame.draw.rect(surf, (90, 72, 50), (ax - 14, ay - 14, ART_W + 28, ART_H + 28), 2, border_radius=6)
    surf.blit(art, (ax, ay))

    y = ay + ART_H + 22
    title = _font("dejavuserif", 30, bold=True).render(slide["title"], True, AMBER)
    surf.blit(title, (ax, y))
    if slide.get("year"):  # год — справа от заголовка, на той же строке, мельче
        yr = _font("dejavusans", 20).render(slide["year"], True, AMBER_DIM)
        surf.blit(yr, (ax + ART_W - yr.get_width(), y + 8))
    y += 46
    body = _font("dejavuserif", 21)
    text = slide_text(slide)[:typed_chars(show)]
    for line in _wrap(body, text, ART_W)[:7]:
        surf.blit(body.render(line, True, (235, 220, 190)), (ax, y))
        y += 28
    # точки прогресса и подсказки
    n = len(show["list"])
    for i in range(n):
        c = AMBER if i == show["i"] else (70, 55, 40)
        pygame.draw.circle(surf, c, (S.SCREEN_W // 2 - n * 9 + i * 18, S.SCREEN_H - 22), 5)
    hint = _font("dejavusans", 15).render("Space/клик — дальше · Esc — пропустить", True, AMBER_DIM)
    surf.blit(hint, (S.SCREEN_W - hint.get_width() - 20, S.SCREEN_H - 30))
    hotspot(pygame.Rect(0, 0, S.SCREEN_W, S.SCREEN_H), game.slides_next)

    # затемнение в начале слайда
    if show["t"] < FADE_MS:
        fade = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * (1 - show["t"] / FADE_MS))))
        surf.blit(fade, (0, 0))

"""
Боевые анимации героя, дорисованные поверх нарезанных кадров (assets/sprites/player/<сторона>/1.png):

  melee/<сторона>/0..2.png — удар ломом: замах, удар с росчерком, доводка;
  shoot/<сторона>/0..2.png — выстрел: рука с пистолетом, вспышка и отдача, дымок.

Кадр шире и выше исходного (46×41 против 22×37): рука с оружием выходит за
силуэт. Герой стоит по центру, ноги на нижнем крае — игра рисует спрайт от
ног, так что при смене анимации он не прыгает. Для взгляда влево рисунок
поверх зеркалится с правой стороны, а сам герой берётся из своего левого кадра.

Попадание по герою и уворот рисуются для всех персонажей прямо в игре
(src/loader.py, make_reactions) — отдельных файлов не нужно.

Запуск из папки game_project (после tools/slice_sprites.py):
    .venv/bin/python tools/make_hero_anims.py
"""
import os
import sys

import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "sprites", "player")
CW, CH = 46, 41          # размер кадра анимации
BW, BH = 22, 37          # размер исходного кадра героя
BX, BY = (CW - BW) // 2, CH - BH   # где стоит герой в кадре без смещения

OUTLINE = (18, 16, 30)
SLEEVE = (70, 74, 70)
SLEEVE_HI = (120, 124, 110)
SKIN = (236, 190, 150)
ROD = (128, 48, 40)          # лом — ржавый красный
ROD_HI = (176, 84, 64)
GUN = (52, 54, 62)
GUN_HI = (96, 100, 110)
FLASH = (255, 236, 140)
FLASH_CORE = (255, 255, 235)


def px(s, x, y, c):
    if 0 <= x < CW and 0 <= y < CH:
        s.set_at((int(x), int(y)), c)


def line(s, a, b, c, width=1):
    pygame.draw.line(s, c, a, b, width)


def arm(s, shoulder, hand):
    """Рука: контур, рукав, светлый блик, кисть 2×2."""
    line(s, shoulder, hand, OUTLINE, 4)
    line(s, shoulder, hand, SLEEVE, 2)
    line(s, (shoulder[0], shoulder[1] - 1), (hand[0], hand[1] - 1), SLEEVE_HI, 1)
    pygame.draw.rect(s, OUTLINE, (hand[0] - 2, hand[1] - 2, 4, 4))
    pygame.draw.rect(s, SKIN, (hand[0] - 1, hand[1] - 1, 2, 2))


def crowbar(s, a, b):
    """Лом от кисти a до конца b, на конце — загнутый «клюв»."""
    line(s, a, b, OUTLINE, 4)
    line(s, a, b, ROD, 2)
    line(s, a, b, ROD_HI, 1)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = max(1, (dx * dx + dy * dy) ** 0.5)
    hook = (b[0] - dy / n * 3, b[1] + dx / n * 3)  # перпендикуляр к лому
    line(s, b, hook, OUTLINE, 3)
    line(s, b, hook, ROD, 1)


def streak(s, pts):
    """Росчерк удара — полупрозрачная дуга."""
    layer = pygame.Surface((CW, CH), pygame.SRCALPHA)
    pygame.draw.lines(layer, (255, 240, 200, 110), False, pts, 3)
    pygame.draw.lines(layer, (255, 255, 255, 170), False, pts, 1)
    s.blit(layer, (0, 0))


def pistol_side(s, hand, up=0):
    """Пистолет в профиль, ствол вправо. Возвращает точку дула."""
    x, y = hand[0], hand[1] - up
    pygame.draw.rect(s, OUTLINE, (x - 2, y - 3, 10, 5))
    pygame.draw.rect(s, GUN, (x - 1, y - 2, 8, 3))
    line(s, (x - 1, y - 2), (x + 6, y - 2), GUN_HI)
    pygame.draw.rect(s, OUTLINE, (x - 2, y, 4, 4))
    pygame.draw.rect(s, GUN, (x - 1, y, 2, 3))
    return (x + 8, y - 1)


def pistol_vertical(s, hand, down=True):
    """Пистолет стволом к зрителю (вниз) или от зрителя (вверх). Возвращает точку дула."""
    x, y = hand
    if down:
        pygame.draw.rect(s, OUTLINE, (x - 2, y - 1, 5, 7))
        pygame.draw.rect(s, GUN, (x - 1, y, 3, 5))
        return (x, y + 7)
    pygame.draw.rect(s, OUTLINE, (x - 2, y - 7, 5, 8))
    pygame.draw.rect(s, GUN, (x - 1, y - 6, 3, 6))
    return (x, y - 8)


def flash(s, p, size=3):
    x, y = p
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        line(s, (x, y), (x + dx * size, y + dy * size), FLASH, 1)
    pygame.draw.circle(s, FLASH, (x, y), 2)
    px(s, x, y, FLASH_CORE)


def smoke(s, p):
    layer = pygame.Surface((CW, CH), pygame.SRCALPHA)
    pygame.draw.circle(layer, (200, 200, 195, 120), (p[0] + 2, p[1] - 2), 3)
    pygame.draw.circle(layer, (220, 220, 215, 80), (p[0] + 5, p[1] - 4), 2)
    s.blit(layer, (0, 0))


# ---- кадры: (смещение героя dx, dy, функция рисования поверх(слой, ox, oy)) — для взгляда вправо
def _melee_right():
    def f0(s, ox, oy):   # замах: лом за спиной
        arm(s, (ox + 11, oy + 16), (ox + 8, oy + 7))
        crowbar(s, (ox + 8, oy + 7), (ox + 1, oy - 1))

    def f1(s, ox, oy):   # удар: лом вперёд, росчерк
        streak(s, [(ox + 2, oy + 0), (ox + 16, oy + 1), (ox + 28, oy + 8), (ox + 32, oy + 16)])
        arm(s, (ox + 12, oy + 16), (ox + 19, oy + 17))
        crowbar(s, (ox + 19, oy + 17), (ox + 32, oy + 14))

    def f2(s, ox, oy):   # доводка: лом вниз-вперёд
        arm(s, (ox + 12, oy + 17), (ox + 18, oy + 21))
        crowbar(s, (ox + 18, oy + 21), (ox + 27, oy + 31))
    return [(-1, 0, f0), (2, 0, f1), (1, 0, f2)]


def _shoot_right():
    def f0(s, ox, oy):
        arm(s, (ox + 12, oy + 17), (ox + 19, oy + 17))
        pistol_side(s, (ox + 20, oy + 17))

    def f1(s, ox, oy):   # выстрел: вспышка, отдача
        arm(s, (ox + 12, oy + 17), (ox + 19, oy + 16))
        flash(s, pistol_side(s, (ox + 20, oy + 16), up=1))

    def f2(s, ox, oy):
        arm(s, (ox + 12, oy + 17), (ox + 19, oy + 17))
        smoke(s, pistol_side(s, (ox + 20, oy + 17)))
    return [(0, 0, f0), (-1, 0, f1), (0, 0, f2)]


def _melee_down():
    def f0(s, ox, oy):
        arm(s, (ox + 17, oy + 16), (ox + 20, oy + 7))
        crowbar(s, (ox + 20, oy + 7), (ox + 26, oy - 2))

    def f1(s, ox, oy):
        streak(s, [(ox + 28, oy + 0), (ox + 22, oy + 18), (ox + 8, oy + 32)])
        arm(s, (ox + 17, oy + 17), (ox + 13, oy + 23))
        crowbar(s, (ox + 13, oy + 23), (ox + 3, oy + 34))

    def f2(s, ox, oy):
        arm(s, (ox + 17, oy + 17), (ox + 12, oy + 24))
        crowbar(s, (ox + 12, oy + 24), (ox + 7, oy + 37))
    return [(0, -1, f0), (0, 1, f1), (0, 1, f2)]


def _shoot_down():
    def f0(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 12, oy + 19))
        pistol_vertical(s, (ox + 12, oy + 20))

    def f1(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 12, oy + 18))
        flash(s, pistol_vertical(s, (ox + 12, oy + 19)))

    def f2(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 12, oy + 19))
        smoke(s, pistol_vertical(s, (ox + 12, oy + 20)))
    return [(0, 0, f0), (0, -1, f1), (0, 0, f2)]


def _melee_up():
    def f0(s, ox, oy):
        arm(s, (ox + 17, oy + 16), (ox + 20, oy + 8))
        crowbar(s, (ox + 20, oy + 8), (ox + 25, oy - 1))

    def f1(s, ox, oy):
        streak(s, [(ox + 26, oy + 2), (ox + 14, oy - 2), (ox + 2, oy + 4)])
        arm(s, (ox + 16, oy + 15), (ox + 13, oy + 7))
        crowbar(s, (ox + 13, oy + 7), (ox + 5, oy - 2))

    def f2(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 12, oy + 10))
        crowbar(s, (ox + 12, oy + 10), (ox + 4, oy + 6))
    return [(0, 1, f0), (0, -2, f1), (0, -1, f2)]


def _shoot_up():
    def f0(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 16, oy + 8))
        pistol_vertical(s, (ox + 16, oy + 8), down=False)

    def f1(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 16, oy + 9))
        flash(s, pistol_vertical(s, (ox + 16, oy + 9), down=False))

    def f2(s, ox, oy):
        arm(s, (ox + 16, oy + 16), (ox + 16, oy + 8))
        smoke(s, pistol_vertical(s, (ox + 16, oy + 8), down=False))
    return [(0, 0, f0), (0, 1, f1), (0, 0, f2)]


ACTIONS = {
    "melee": {"right": _melee_right(), "down": _melee_down(), "up": _melee_up()},
    "shoot": {"right": _shoot_right(), "down": _shoot_down(), "up": _shoot_up()},
}


def build(base, frames, mirror=False):
    """Кадры действия: герой со смещением + рисунок поверх. mirror — для взгляда влево."""
    out = []
    for dx, dy, draw in frames:
        layer = pygame.Surface((CW, CH), pygame.SRCALPHA)
        draw(layer, BX + dx, BY + dy)
        if mirror:
            layer = pygame.transform.flip(layer, True, False)
            dx = -dx
        s = pygame.Surface((CW, CH), pygame.SRCALPHA)
        # в профиль рука с оружием — перед корпусом; анфас и со спины — тоже поверх
        s.blit(base, (BX + dx, BY + dy))
        s.blit(layer, (0, 0))
        out.append(s)
    return out


def main():
    pygame.init()
    base = {d: pygame.image.load(os.path.join(SRC, d, "1.png")) for d in ("down", "left", "right", "up")}
    assert base["down"].get_size() == (BW, BH), "ожидался кадр героя 22×37 — сначала tools/slice_sprites.py"
    for action, by_dir in ACTIONS.items():
        for d in ("down", "left", "right", "up"):
            frames = build(base[d], by_dir["right"], mirror=True) if d == "left" else build(base[d], by_dir[d])
            folder = os.path.join(SRC, action, d)
            os.makedirs(folder, exist_ok=True)
            for i, f in enumerate(frames):
                pygame.image.save(f, os.path.join(folder, f"{i}.png"))
        print(f"{action}: 4 стороны × {len(by_dir['right'])} кадра -> assets/sprites/player/{action}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

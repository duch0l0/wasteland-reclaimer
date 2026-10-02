"""
Балахоны «Детей Единства», нарисованные кодом: культист (тёмно-красный) и брат Ансельм
(белый с золотом, с посохом). По образу старого листа npc/raw/cultist.png — глубокий
капюшон, вместо лица тьма с тусклыми огоньками глаз, — но в разрешении и пропорциях
остальных жителей.

Рисуем мелким пиксель-артом 22×38 (свет сверху слева, складки, подол колышется при ходьбе)
и увеличиваем вдвое без сглаживания. 4 стороны × 4 кадра шага (0 и 2 — шаг, 1 и 3 — стоит).
Результат: assets/sprites/cultist/, assets/sprites/anselm/ (кадры уже в игровом размере — файл native).

Запуск из папки game_project:  .venv/bin/python tools/make_robes.py
"""
import os
import shutil

import pygame

W, H = 22, 38
INK = (20, 12, 14)
PALETTES = {
    "cultist": {"base": (146, 30, 30), "light": (188, 52, 44), "dark": (96, 18, 20), "deep": (58, 10, 14),
                "belt": (176, 150, 100), "trim": None, "eyes": (230, 120, 40), "staff": False},
    "anselm": {"base": (212, 204, 184), "light": (242, 236, 218), "dark": (160, 150, 128), "deep": (104, 94, 80),
               "belt": (214, 170, 60), "trim": (214, 170, 60), "eyes": (250, 220, 150), "staff": True},
}


def px(s, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        s.set_at((int(x), int(y)), c)


def outline(s):
    m = pygame.mask.from_surface(s, 10)
    for y in range(H):
        for x in range(W):
            if not m.get_at((x, y)) and any(0 <= x + dx < W and 0 <= y + dy < H and m.get_at((x + dx, y + dy))
                                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                s.set_at((x, y), INK)


def robe(pal, d, frame):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    bob = 1 if frame in (1, 3) else 0          # стоя — на пиксель выше
    sway = {0: -1, 1: 0, 2: 1, 3: 0}[frame]    # подол качается при шаге
    top = 2 + bob
    side = d in ("left", "right")
    # посох (за фигурой, если смотрит вверх)
    if pal["staff"] and d == "up":
        _staff(s, pal, 18, top)
    # плащ: от плеч колоколом к подолу
    sh_l, sh_r = (5, 16) if not side else (6, 15)
    hem_l, hem_r = 2 + min(0, sway), 19 + max(0, sway)
    body = [(sh_l, top + 12), (sh_r, top + 12), (hem_r, H - 3), (hem_l, H - 3)]
    pygame.draw.polygon(s, pal["base"], body)
    for x in range(hem_l, hem_r + 1):       # тень справа, свет слева
        for y in range(top + 12, H - 2):
            if s.get_at((x, y)).a and x > (sh_r + hem_r) // 2 - 1:
                px(s, x, y, pal["dark"])
            elif s.get_at((x, y)).a and x < (sh_l + hem_l) // 2 + 2:
                px(s, x, y, pal["light"])
    for fx in (8, 11, 14):                  # складки
        for y in range(top + 17, H - 3):
            if s.get_at((fx + (sway if y > H - 9 else 0), y)).a:
                px(s, fx + (sway if y > H - 9 else 0), y, pal["dark"])
    # подол и ступни из-под него
    for x in range(hem_l, hem_r + 1):
        px(s, x, H - 3, pal["deep"])
    feet = (7 + sway, 13 - sway) if not side else ((9 + sway, 12 - sway))
    for fx in feet:
        px(s, fx, H - 2, (40, 30, 26))
        px(s, fx + 1, H - 2, (40, 30, 26))
    if pal["trim"]:                         # золотая кайма по подолу
        for x in range(hem_l + 1, hem_r):
            px(s, x, H - 4, pal["trim"])
    # рукава и пояс
    belt_y = top + 20
    for x in range(sh_l - 1, sh_r + 2):
        if s.get_at((x, belt_y)).a:
            px(s, x, belt_y, pal["belt"])
    if not side and d == "down":            # руки сложены в рукавах на груди
        pygame.draw.rect(s, pal["dark"], (7, top + 15, 8, 3))
        pygame.draw.rect(s, pal["light"], (7, top + 15, 8, 1))
        if pal["trim"]:                     # золотой круг «Единства» на груди
            pygame.draw.circle(s, pal["trim"], (11, top + 23), 2, 1)
    elif side:
        front = 15 if d == "right" else 4
        pygame.draw.rect(s, pal["dark"], (min(front, 11 if d == "right" else front), top + 15, 6, 3))
    # капюшон
    hood = pygame.Rect(5, top, 12, 14) if not side else pygame.Rect(5, top, 12, 14)
    pygame.draw.ellipse(s, pal["base"], hood)
    px(s, 11, top - 1, pal["base"])         # острый верх
    pygame.draw.ellipse(s, pal["light"], (6, top + 1, 5, 6))
    for y in range(top + 2, top + 13):     # тень капюшона справа
        px(s, 16, y, pal["dark"])
        px(s, 15, y + 1, pal["dark"]) if y > top + 6 else None
    if pal["trim"]:
        pygame.draw.arc(s, pal["trim"], hood.inflate(-1, -1), 3.6, 5.8, 1)
    # лицо — тьма, в ней тусклые огоньки глаз
    if d == "down":
        pygame.draw.ellipse(s, (14, 8, 10), (7, top + 4, 8, 9))
        px(s, 9, top + 8, pal["eyes"])
        px(s, 12, top + 8, pal["eyes"])
    elif side:
        x0 = 11 if d == "right" else 6
        pygame.draw.ellipse(s, (14, 8, 10), (x0, top + 4, 5, 8))
        px(s, x0 + (3 if d == "right" else 1), top + 8, pal["eyes"])
    else:                                    # со спины: шов капюшона
        for y in range(top + 3, top + 13):
            px(s, 11, y, pal["dark"])
    if pal["staff"] and d != "up":
        _staff(s, pal, 19 if d != "left" else 2, top)
    outline(s)
    if d == "left":
        pass
    return s


def _staff(s, pal, x, top):
    """Посох Ансельма: тёмное древко, сверху золотой круг."""
    for y in range(top + 2, H - 2):
        px(s, x, y, (90, 64, 40))
    pygame.draw.circle(s, pal["trim"], (x, top + 2), 2, 1)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    pygame.init()
    for sid, pal in PALETTES.items():
        dst = os.path.join("assets", "sprites", sid)
        shutil.rmtree(dst, ignore_errors=True)
        for d in ("down", "left", "right", "up"):
            os.makedirs(os.path.join(dst, d), exist_ok=True)
            for i in range(4):
                img = robe(pal, d, i)
                if d == "left":     # влево — зеркало правой стороны
                    img = pygame.transform.flip(robe(pal, "right", i), True, False)
                img = pygame.transform.scale(img, (W * 2, H * 2))
                pygame.image.save(img, os.path.join(dst, d, f"{i}.png"))
        with open(os.path.join(dst, "native"), "w") as fh:
            fh.write("кадры уже в игровом размере (tools/make_robes.py)\n")
        print("готово:", sid)


if __name__ == "__main__":
    main()

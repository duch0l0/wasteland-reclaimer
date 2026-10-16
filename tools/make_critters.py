"""
Спрайты городских животных (assets/sprites/<имя>/{down,left,right,up}/0..3.png + файл native — без увеличения):
  cat_orange cat_grey cat_black cat_white   кошки (рисуются здесь)
  chicken_white chicken_brown chicken_black курицы
  brahmin                                   двухголовая корова-брамин
  dog_dark dog_pale dog_grey                перекраски нашего пса (assets/sprites/dog)
Кадры: 0 и 2 — шаг, 1 и 3 — стоит (так их читает loader.load_directional_animations).

Запуск из папки game_project:  .venv/bin/python tools/make_critters.py
"""
import os
import shutil

import pygame

pygame.init()
pygame.display.set_mode((1, 1))
OUT = "assets/sprites"
OUTLINE = (24, 20, 18, 255)


def outline(img):
    w, h = img.get_size()
    src = img.copy()
    for y in range(h):
        for x in range(w):
            if src.get_at((x, y)).a == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src.get_at((nx, ny)).a > 150:
                        img.set_at((x, y), OUTLINE)
                        break
    return img


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


def save(name, frames):
    base = os.path.join(OUT, name)
    shutil.rmtree(base, ignore_errors=True)
    for d, imgs in frames.items():
        os.makedirs(os.path.join(base, d), exist_ok=True)
        for i, im in enumerate(imgs):
            pygame.image.save(im, os.path.join(base, d, f"{i}.png"))
    open(os.path.join(base, "native"), "w").close()


def flipped(imgs):
    return [pygame.transform.flip(i, True, False) for i in imgs]


# ------------------------------------------------------------------ кошка
def cat_frames(col, belly, patch=None):
    W, H = 28, 24
    side, front, back = [], [], []
    for f in range(4):
        step = f in (0, 2)
        lift = (1 if f == 0 else -1) if step else 0
        # --- вид сбоку (смотрит вправо)
        im = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (5, 9, 16, 9))                                  # туловище
        pygame.draw.ellipse(im, belly, (8, 14, 10, 4))
        pygame.draw.circle(im, col, (21, 8), 5)                                      # голова
        pygame.draw.polygon(im, col, [(17, 5), (18, 0), (21, 4)])                    # уши
        pygame.draw.polygon(im, col, [(22, 4), (25, 0), (26, 6)])
        im.set_at((23, 8), (30, 30, 30, 255))
        im.set_at((26, 9), (230, 130, 140, 255))                                     # нос
        pygame.draw.line(im, col, (6, 11), (2, 7 + (2 if f in (1, 3) else 0)), 2)    # хвост
        for lx, ph in ((7, 0), (10, 1), (17, 1), (20, 0)):                           # лапы
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(col, 0.85), (lx, 17 + max(0, yo), 3, 5 - max(0, yo)))
        if patch:
            pygame.draw.ellipse(im, patch, (9, 9, 6, 5))
        side.append(outline(im))
        # --- спереди
        im = pygame.Surface((20, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (3, 10, 14, 12))
        pygame.draw.ellipse(im, belly, (6, 15, 8, 6))
        pygame.draw.circle(im, col, (10, 8), 6)
        pygame.draw.polygon(im, col, [(4, 5), (5, 0), (8, 3)])
        pygame.draw.polygon(im, col, [(12, 3), (15, 0), (16, 5)])
        im.set_at((8, 8), (30, 30, 30, 255)); im.set_at((12, 8), (30, 30, 30, 255))
        im.set_at((10, 10), (230, 130, 140, 255))
        for lx, ph in ((5, 0), (11, 1)):
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(col, 0.85), (lx, 19 + max(0, yo), 4, 4 - max(0, yo)))
        front.append(outline(im))
        # --- сзади
        im = pygame.Surface((20, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (3, 8, 14, 13))
        pygame.draw.circle(im, col, (10, 6), 5)
        pygame.draw.polygon(im, col, [(5, 4), (6, 0), (9, 2)])
        pygame.draw.polygon(im, col, [(11, 2), (14, 0), (15, 4)])
        pygame.draw.line(im, col, (10, 18), (10 + (2 if f in (1, 3) else -2), 8), 2)
        for lx, ph in ((5, 0), (11, 1)):
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(col, 0.85), (lx, 19 + max(0, yo), 4, 4 - max(0, yo)))
        back.append(outline(im))
    return {"right": side, "left": flipped(side), "down": front, "up": back}


# ------------------------------------------------------------------ курица
def chicken_frames(col, comb=(210, 50, 44)):
    side, front, back = [], [], []
    for f in range(4):
        step = f in (0, 2)
        bob = 1 if f == 0 else 0
        im = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (4, 7 + bob, 15, 11))                          # тело
        pygame.draw.polygon(im, shade(col, 0.9), [(4, 9 + bob), (0, 6), (3, 13 + bob)])   # хвост
        pygame.draw.ellipse(im, shade(col, 0.88), (8, 10 + bob, 8, 6))              # крыло
        pygame.draw.circle(im, col, (18, 6 + bob), 4)                                # голова
        pygame.draw.rect(im, comb, (17, 1 + bob, 3, 3))                              # гребешок
        pygame.draw.polygon(im, (236, 180, 50), [(21, 6 + bob), (24, 7 + bob), (21, 8 + bob)])
        im.set_at((19, 5 + bob), (20, 20, 20, 255))
        pygame.draw.line(im, (230, 170, 60), (9, 18), (9 + (2 if step else 0), 22), 1)
        pygame.draw.line(im, (230, 170, 60), (14, 18), (14 - (2 if step else 0), 22), 1)
        side.append(outline(im))
        im = pygame.Surface((18, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (3, 8 + bob, 12, 11))
        pygame.draw.circle(im, col, (9, 6 + bob), 4)
        pygame.draw.rect(im, comb, (8, 1 + bob, 3, 3))
        pygame.draw.polygon(im, (236, 180, 50), [(8, 7 + bob), (10, 7 + bob), (9, 10 + bob)])
        im.set_at((7, 5 + bob), (20, 20, 20, 255)); im.set_at((11, 5 + bob), (20, 20, 20, 255))
        pygame.draw.line(im, (230, 170, 60), (6, 19), (6 + (1 if step else 0), 23), 1)
        pygame.draw.line(im, (230, 170, 60), (12, 19), (12 - (1 if step else 0), 23), 1)
        front.append(outline(im))
        im = pygame.Surface((18, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(im, col, (3, 7 + bob, 12, 12))
        pygame.draw.circle(im, col, (9, 5 + bob), 3)
        pygame.draw.rect(im, comb, (8, 1 + bob, 3, 3))
        pygame.draw.polygon(im, shade(col, 0.85), [(5, 12), (9, 4), (13, 12)])
        pygame.draw.line(im, (230, 170, 60), (6, 19), (6 + (1 if step else 0), 23), 1)
        pygame.draw.line(im, (230, 170, 60), (12, 19), (12 - (1 if step else 0), 23), 1)
        back.append(outline(im))
    return {"right": side, "left": flipped(side), "down": front, "up": back}


# ------------------------------------------------------------------ брамин
def brahmin_frames():
    hide, patch, horn, dark = (150, 104, 66, 255), (226, 214, 190, 255), (232, 226, 200, 255), (96, 64, 40, 255)
    side, front, back = [], [], []
    for f in range(4):
        step = f in (0, 2)
        lift = (2 if f == 0 else -2) if step else 0
        im = pygame.Surface((64, 46), pygame.SRCALPHA)
        pygame.draw.ellipse(im, hide, (8, 8, 38, 22))                                # туловище с горбом
        pygame.draw.ellipse(im, hide, (12, 3, 16, 12))
        pygame.draw.ellipse(im, patch, (24, 12, 14, 9))
        pygame.draw.ellipse(im, patch, (10, 17, 9, 7))
        for hx, hy, k in ((50, 14, 0), (46, 7, 1)):                                  # две головы
            pygame.draw.ellipse(im, hide, (hx - 8, hy, 16, 12))
            pygame.draw.rect(im, (44, 30, 22, 255), (hx + 4, hy + 6, 4, 4))
            pygame.draw.polygon(im, horn, [(hx - 5, hy + 1), (hx - 9, hy - 5), (hx - 2, hy)])
            im.set_at((hx + 1, hy + 4), (20, 20, 20, 255))
        pygame.draw.line(im, dark, (9, 14), (3, 24), 2)                              # хвост
        pygame.draw.circle(im, dark, (3, 25), 2)
        for lx, ph in ((12, 0), (18, 1), (34, 1), (40, 0)):
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(hide, 0.82), (lx, 28 + max(0, yo), 5, 17 - max(0, yo)))
            pygame.draw.rect(im, dark, (lx, 42, 5, 3))
        side.append(outline(im))
        im = pygame.Surface((40, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(im, hide, (4, 16, 32, 26))
        pygame.draw.ellipse(im, patch, (14, 24, 14, 10))
        for hx in (11, 29):
            pygame.draw.ellipse(im, hide, (hx - 8, 3, 16, 18))
            pygame.draw.polygon(im, horn, [(hx - 7, 6), (hx - 12, 0), (hx - 4, 4)])
            pygame.draw.polygon(im, horn, [(hx + 7, 6), (hx + 12, 0), (hx + 4, 4)])
            im.set_at((hx - 3, 10), (20, 20, 20, 255)); im.set_at((hx + 3, 10), (20, 20, 20, 255))
            pygame.draw.rect(im, (60, 42, 32, 255), (hx - 3, 15, 6, 4))
        for lx, ph in ((8, 0), (28, 1)):
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(hide, 0.82), (lx, 36 + max(0, yo), 6, 10 - max(0, yo)))
        front.append(outline(im))
        im = pygame.Surface((40, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(im, hide, (4, 8, 32, 30))
        pygame.draw.ellipse(im, patch, (10, 12, 12, 10))
        pygame.draw.line(im, dark, (20, 30), (20 + (4 if f in (1, 3) else -4), 44), 2)
        for lx, ph in ((8, 0), (28, 1)):
            yo = lift if ph else -lift
            pygame.draw.rect(im, shade(hide, 0.82), (lx, 34 + max(0, yo), 6, 10 - max(0, yo)))
        back.append(outline(im))
    return {"right": side, "left": flipped(side), "down": front, "up": back}


# ------------------------------------------------------------------ перекраски пса
def recolor_dog(name, fn):
    src = os.path.join(OUT, "dog")
    frames = {}
    for d in ("down", "left", "right", "up"):
        imgs = []
        for i in range(4):
            im = pygame.image.load(os.path.join(src, d, f"{i}.png")).convert_alpha()
            out = im.copy()
            for y in range(im.get_height()):
                for x in range(im.get_width()):
                    c = im.get_at((x, y))
                    if c.a:
                        out.set_at((x, y), fn(c))
            imgs.append(out)
        frames[d] = imgs
    save(name, frames)


def gray(c):
    return (c.r * 3 + c.g * 6 + c.b) // 10


if __name__ == "__main__":
    for nm, col, belly, patch in (("cat_orange", (226, 148, 70, 255), (246, 216, 170, 255), (244, 190, 120, 255)),
                                  ("cat_grey", (150, 154, 164, 255), (206, 208, 214, 255), None),
                                  ("cat_black", (52, 50, 58, 255), (84, 82, 92, 255), None),
                                  ("cat_white", (236, 232, 226, 255), (250, 246, 240, 255), (196, 150, 108, 255))):
        save(nm, cat_frames(col, belly, patch))
    for nm, col in (("chicken_white", (240, 236, 226, 255)), ("chicken_brown", (176, 112, 62, 255)),
                    ("chicken_black", (60, 58, 66, 255))):
        save(nm, chicken_frames(col))
    save("brahmin", brahmin_frames())
    recolor_dog("dog_dark", lambda c: (int(gray(c) * 0.42), int(gray(c) * 0.38), int(gray(c) * 0.36), c.a))
    recolor_dog("dog_pale", lambda c: (min(255, gray(c) + 70), min(255, gray(c) + 62), min(255, gray(c) + 44), c.a))
    recolor_dog("dog_grey", lambda c: (gray(c), gray(c), min(255, gray(c) + 8), c.a))
    print("нарисовано: 11 видов")
